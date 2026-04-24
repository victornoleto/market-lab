"""Real-ETF variant of the EMA/SMA threshold sweep runner.

Loads signal prices + real ETF returns from the Tiingo parquet cache
and runs the same cartesian grid as the SPYSIM study, but using actual
UPRO/SSO/SPY (or QQQ/QLD/TQQQ) returns on the buy side. For the sell
side, since inverse LETFs are not in the Tiingo cache, short legs are
synthesized from the signal asset's real returns.

Design choices
--------------

* **Buy leg is fully real** — the main educational goal (real UPRO vs
  synth UPRO) is answered for any long-only config.
* **Sell leg < 0** uses ``_synth_leveraged_returns(signal_returns, L,
  fee)`` as a proxy for the absent SH/SDS/SPXU/SPXU/SPXS (or
  PSQ/QID/SQQQ). This is the same formula Gayed uses for synth LETF.
* **Effective start date** = the latest first-date across ALL tickers
  used in the grid. For the full SPY grid including UPRO, that's
  2009-06-25 (UPRO inception). For a cash-only grid, 2006-06-21 (SSO).

Citations
---------

* Synth LETF formula ``r = L · r − fee/252``:
  ``[leverage_for_the_long_run, p.16, footnote 22]``.
* Real UPRO vs synth 3x — expect 2-3pp/yr drag from daily re-leveraging
  tracking error: ``[leverage_for_the_long_run, p.21, Table 12]``.
* Honest alignment (no look-ahead):
  ``[advances_fin_ml, p.31-34]``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.grid.ema_sma_threshold_grid import (
    ConfigMetrics,
    GateFlags,
    compute_composite_scores,
    compute_config_metrics,
    evaluate_gates,
)
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    calmar as _calmar,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
    sortino as _sortino,
    volatility as _volatility,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    DEFAULT_FEE,
    EMASMAThresholdConfig,
    ThresholdResult,
    TRADING_DAYS_PER_YEAR,
    _synth_leveraged_returns,
    simulate_regime_threshold_with_legs,
)

DEFAULT_CACHE = Path("data/tiingo/daily/prices")


@dataclass(frozen=True)
class RealETFMarket:
    """Which tickers back this market's signal + buy legs.

    ``signal_ticker`` = used for MA regime filter (and signal returns
    when a synth inverse is needed on the sell side).
    ``buy_tickers`` maps integer leverage (1, 2, 3) to the real ETF
    symbol that provides that leverage.
    """

    name: str  # human label, e.g. "SPY (S&P 500)"
    signal_ticker: str
    buy_tickers: dict[int, str]  # {1: "SPY", 2: "SSO", 3: "UPRO"}
    label: str  # folder slug (e.g. "spy")


SPY_MARKET = RealETFMarket(
    name="SPY (S&P 500)",
    signal_ticker="SPY",
    buy_tickers={1: "SPY", 2: "SSO", 3: "UPRO"},
    label="spy",
)

NDX_MARKET = RealETFMarket(
    name="QQQ (NASDAQ-100)",
    signal_ticker="QQQ",
    buy_tickers={1: "QQQ", 2: "QLD", 3: "TQQQ"},
    label="ndx",
)


def load_etf_series(ticker: str, cache_dir: Path = DEFAULT_CACHE) -> pd.Series:
    """Load adjusted close price series for one ETF from Tiingo cache."""
    path = cache_dir / f"{ticker}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"ticker {ticker!r} not in {cache_dir}")
    df = pd.read_parquet(path)
    # Tiingo storage usually has 'adjClose' column — pick the clean price.
    col = None
    for c in ("adjClose", "adj_close", "close"):
        if c in df.columns:
            col = c
            break
    if col is None:
        raise ValueError(f"{ticker}: no price column found in {df.columns.tolist()}")
    s = df[col].astype(float).copy()
    s.index = pd.DatetimeIndex(df.index).tz_localize(None)
    s.name = ticker
    return s.sort_index()


def load_etf_returns(ticker: str, cache_dir: Path = DEFAULT_CACHE) -> pd.Series:
    s = load_etf_series(ticker, cache_dir)
    r = s.pct_change().dropna()
    r.name = ticker
    return r


def build_data_bundle(
    market: RealETFMarket,
    leverages_used: tuple[float, ...],
    cache_dir: Path = DEFAULT_CACHE,
) -> dict[str, pd.Series]:
    """Load signal prices + buy-leg returns for every leverage the grid needs.

    Returns a dict ``{"signal_prices": ..., "signal_returns": ...,
    "buy_L1": <returns>, "buy_L2": ..., "buy_L3": ...}``.

    Effective start date = max first-date across all loaded series.
    """
    signal_prices = load_etf_series(market.signal_ticker, cache_dir)
    signal_returns = signal_prices.pct_change().dropna()

    buy: dict[int, pd.Series] = {}
    for lev in sorted({int(x) for x in leverages_used if x > 0}):
        tkr = market.buy_tickers.get(lev)
        if tkr is None:
            raise ValueError(f"market {market.label}: no ticker for leverage {lev}")
        buy[lev] = load_etf_returns(tkr, cache_dir)

    # Intersect all indices to find effective start.
    first_dates = [signal_returns.index[0]] + [s.index[0] for s in buy.values()]
    start = max(first_dates)
    last_dates = [signal_returns.index[-1]] + [s.index[-1] for s in buy.values()]
    end = min(last_dates)

    # Align everything to a common index (signal returns intersection).
    common = signal_returns.loc[(signal_returns.index >= start) & (signal_returns.index <= end)].index
    bundle = {
        "signal_prices": signal_prices.reindex(common),
        "signal_returns": signal_returns.reindex(common),
    }
    for lev, r in buy.items():
        bundle[f"buy_L{lev}"] = r.reindex(common)

    # Data meta.
    bundle["_meta"] = pd.Series({
        "market": market.name,
        "signal_ticker": market.signal_ticker,
        "start": start,
        "end": end,
        "n_bars": len(common),
    })
    return bundle


def simulate_config_with_real_legs(
    cfg: EMASMAThresholdConfig,
    bundle: dict[str, pd.Series],
) -> ThresholdResult:
    """Run one config using real buy leg + synth sell leg.

    ``bundle`` must contain ``signal_prices``, ``signal_returns``, and
    ``buy_L{int(cfg.buy_leverage)}`` — see :func:`build_data_bundle`.
    """
    buy_key = f"buy_L{int(cfg.buy_leverage)}"
    buy_leg = bundle[buy_key]
    signal_prices = bundle["signal_prices"]
    signal_returns = bundle["signal_returns"]

    if cfg.sell_leverage == 0.0:
        cash_daily = cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
        sell_leg = pd.Series(cash_daily, index=signal_returns.index)
    else:
        # Synth inverse LETF from real signal returns.
        sell_leg = _synth_leveraged_returns(
            signal_returns, cfg.sell_leverage, cfg.fee
        )

    return simulate_regime_threshold_with_legs(
        signal_prices=signal_prices,
        buy_leg_returns=buy_leg,
        sell_leg_returns=sell_leg,
        cfg=cfg,
    )


def benchmark_signal_buy_hold(bundle: dict[str, pd.Series]) -> ConfigMetrics:
    """Buy-and-hold baseline of the SIGNAL ticker (e.g. SPY, QQQ)."""
    prices = bundle["signal_prices"].dropna()
    eq = prices / prices.iloc[0]
    rets = eq.pct_change().dropna()
    meta = bundle.get("_meta", pd.Series({"signal_ticker": "SIGNAL"}))
    label = f"BENCHMARK_{meta['signal_ticker']}_BH"
    # Cfg is a placeholder; only metrics are consumed downstream.
    placeholder = EMASMAThresholdConfig(
        filter="SMA", lookback=2, threshold_pct=0.0,
        buy_leverage=1.0, sell_leverage=0.0, fee=0.0,
    )
    return ConfigMetrics(
        cfg_id=label,
        cfg=placeholder,
        cagr=_cagr(eq, TRADING_DAYS_PER_YEAR),
        sharpe=_sharpe(rets, TRADING_DAYS_PER_YEAR),
        max_drawdown=_max_drawdown(eq),
        calmar=_calmar(eq, TRADING_DAYS_PER_YEAR),
        sortino=_sortino(rets, TRADING_DAYS_PER_YEAR),
        volatility=_volatility(rets, TRADING_DAYS_PER_YEAR),
        n_switches=0,
        cum_cost_pct=0.0,
    )
