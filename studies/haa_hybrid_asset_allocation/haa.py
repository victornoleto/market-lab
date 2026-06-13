"""Hybrid Asset Allocation (HAA) engine.

This module implements Wouter Keller and Jan Willem Keuning's HAA mechanics as
an auditable study helper, not as a live-trading system. The signal combines
cross-sectional and absolute momentum: rank the offensive universe by equal
weighted 1/3/6/12-month total returns, hold the top ``top_n`` assets only when
the TIP canary has positive momentum, and replace weak/risk-off slots with the
best defensive asset between BIL and IEF.

Decision citations:
  - 1/3/6/12 momentum as a cross-sectional/absolute momentum signal:
    [stocks_on_the_move, p.60]
  - Monthly review/rebalance cadence for momentum portfolios:
    [stocks_on_the_move, p.98-99]
  - Defensive cash/bond sleeve and turnover/tax awareness:
    [systematic_trading, p.185-188]
  - Anti-overfit validation expected downstream: [advances_fin_ml, p.208-211]

Primary external source for the exact HAA recipe: Keller & Keuning, "Dual and
Canary Momentum with Rising Yields/Inflation: Hybrid Asset Allocation", SSRN
4346906; public rule summaries from TrendXplorer, Allocate Smartly and
BestFolio. The external paper is cited in study docs; the book citations above
anchor the repo's indicator/parameter discipline.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as dt_date, timedelta
from pathlib import Path
from typing import Iterable

import pandas as pd

from market_lab.backtest.metrics.performance import (
    cagr,
    calmar,
    max_drawdown,
    sharpe,
    sortino,
    volatility,
)


TRADING_DAYS_PER_YEAR = 252
DEFAULT_START_VALUE = 10_000.0


@dataclass(frozen=True)
class HAAConfig:
    """Specification for one HAA variant.

    ``lookback_months=(1, 3, 6, 12)`` and ``top_n=4`` are the HAA recipe from
    Keller/Keuning. The parameters are explicit so the study can also run
    pre-registered robustness variants; any such grid must pay PBO/DSR trial
    costs [advances_fin_ml, p.208-211], [advances_fin_ml, p.273-275].
    """

    name: str
    offensive_assets: tuple[str, ...]
    canary_asset: str = "TIP"
    defensive_assets: tuple[str, str] = ("BIL", "IEF")
    top_n: int = 4
    lookback_months: tuple[int, int, int, int] = (1, 3, 6, 12)
    min_offensive_assets: int | None = None

    def __post_init__(self) -> None:
        if self.top_n <= 0:
            raise ValueError("top_n must be positive")
        if not self.offensive_assets:
            raise ValueError("offensive_assets cannot be empty")
        if len(self.defensive_assets) != 2:
            raise ValueError("HAA defensive universe should contain exactly two assets")
        if any(month <= 0 for month in self.lookback_months):
            raise ValueError("lookback_months must be positive")
        if len(set(self.lookback_months)) != len(self.lookback_months):
            raise ValueError("lookback_months must be unique")

    @property
    def required_assets(self) -> tuple[str, ...]:
        return tuple(
            sorted(set(self.offensive_assets) | {self.canary_asset} | set(self.defensive_assets))
        )

    @property
    def min_required_offensive_assets(self) -> int:
        return self.min_offensive_assets or self.top_n


HAA_BALANCED_G8_T4 = HAAConfig(
    name="haa_balanced_g8_t4",
    offensive_assets=("SPY", "IWM", "VEA", "VWO", "VNQ", "DBC", "IEF", "TLT"),
)

HAA_BALANCED_G8_T4_NO_VNQ = HAAConfig(
    name="haa_balanced_g8_t4_no_vnq_proxy",
    # Non-canonical fallback for Testfol.io: VNQSIM is not exposed in the user's
    # cache/API sample, so this keeps the HAA machinery runnable while clearly
    # paying the trial/documentation cost [advances_fin_ml, p.208-211].
    offensive_assets=("SPY", "IWM", "VEA", "VWO", "DBC", "IEF", "TLT"),
)

HAA_BESTFOLIO_NO_QQQ_SEED = HAAConfig(
    name="haa_bestfolio_no_qqq_seed",
    # BestFolio's rendered page says 9 offensive assets for the no-QQQ variant
    # but does not expose the exact list publicly. This seed extends the classic
    # G8/T4 with GLD as the ninth broad diversifier and is labelled non-canonical.
    offensive_assets=("SPY", "IWM", "VEA", "VWO", "VNQ", "DBC", "GLD", "IEF", "TLT"),
)


def canonicalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with uppercase ticker columns for stable matching."""
    out = frame.copy()
    out.columns = [str(col).upper() for col in out.columns]
    return out


def momentum_13612u(
    monthly_prices: pd.DataFrame,
    assets: Iterable[str],
    lookback_months: tuple[int, ...] = (1, 3, 6, 12),
) -> pd.DataFrame:
    """Equal-weighted 1/3/6/12-month return momentum.

    HAA uses an unweighted 13612 score, not the VAA/DAA/BAA 13612W weighting.
    Full lookback availability is required for a finite score; this enforces the
    13-month minimum-history convention and avoids implicitly favoring younger
    assets [stocks_on_the_move, p.60].
    """
    assets_tuple = tuple(str(asset).upper() for asset in assets)
    prices = canonicalize_columns(monthly_prices)
    scores = pd.DataFrame(index=prices.index, columns=assets_tuple, dtype=float)
    for asset in assets_tuple:
        if asset not in prices.columns:
            continue
        p = prices[asset].astype(float)
        components = [p / p.shift(months) - 1.0 for months in lookback_months]
        component_frame = pd.concat(components, axis=1)
        scores[asset] = component_frame.mean(axis=1, skipna=False)
    return scores


def best_defensive_asset(
    defensive_momentum: pd.Series, defensive_assets: tuple[str, str]
) -> str | None:
    """Pick the best defensive asset by the same 13612U momentum score."""
    row = defensive_momentum.reindex([asset.upper() for asset in defensive_assets]).dropna()
    if row.empty:
        return None
    return str(row.sort_values(ascending=False).index[0])


def haa_monthly_weights(prices: pd.DataFrame, config: HAAConfig) -> pd.DataFrame:
    """Build month-end HAA target weights.

    The target is computed on month-end prices. Applying these weights through
    ``simulate_haa_gross`` uses ``weights.shift(1) * returns`` so the signal at
    the close of a month can affect only subsequent returns, preventing the
    look-ahead bug class documented elsewhere in this repo [advances_fin_ml,
    p.31-34].
    """
    daily = canonicalize_columns(prices).sort_index()
    missing = [asset for asset in config.required_assets if asset not in daily.columns]
    if missing:
        raise KeyError(f"missing required HAA assets for {config.name}: {missing}")

    monthly = daily[list(config.required_assets)].resample("ME").last()
    offensive_mom = momentum_13612u(monthly, config.offensive_assets, config.lookback_months)
    defensive_mom = momentum_13612u(monthly, config.defensive_assets, config.lookback_months)
    canary_mom = momentum_13612u(monthly, (config.canary_asset,), config.lookback_months)[
        config.canary_asset.upper()
    ]

    columns = tuple(sorted(set(config.offensive_assets) | set(config.defensive_assets)))
    weights = pd.DataFrame(0.0, index=monthly.index, columns=columns)

    for rebalance_date in monthly.index:
        canary_value = canary_mom.loc[rebalance_date]
        defensive_asset = best_defensive_asset(
            defensive_mom.loc[rebalance_date], config.defensive_assets
        )
        if defensive_asset is None or pd.isna(canary_value):
            continue

        if float(canary_value) <= 0.0:
            weights.loc[rebalance_date, defensive_asset] = 1.0
            continue

        row = offensive_mom.loc[rebalance_date].dropna().sort_values(ascending=False)
        if len(row) < config.min_required_offensive_assets:
            weights.loc[rebalance_date, defensive_asset] = 1.0
            continue

        chosen = row.head(config.top_n)
        slot_weight = 1.0 / config.top_n
        for asset, score in chosen.items():
            target = str(asset) if float(score) > 0.0 else defensive_asset
            weights.loc[rebalance_date, target] += slot_weight

    return weights


def daily_weights_from_monthly(
    prices: pd.DataFrame, monthly_weights: pd.DataFrame
) -> pd.DataFrame:
    """Forward-fill month-end target weights onto the daily price index."""
    daily_index = pd.DatetimeIndex(prices.index)
    weights = monthly_weights.reindex(daily_index, method="ffill").fillna(0.0)
    return weights.reindex(columns=monthly_weights.columns, fill_value=0.0)


def simulate_haa_gross(
    prices: pd.DataFrame, config: HAAConfig
) -> tuple[pd.Series, pd.DataFrame]:
    """Simulate gross daily HAA returns using previous weights times current returns."""
    daily = canonicalize_columns(prices).sort_index()
    monthly_weights = haa_monthly_weights(daily, config)
    daily_weights = daily_weights_from_monthly(daily, monthly_weights)
    returns = daily[daily_weights.columns].pct_change()
    gross = (daily_weights.shift(1) * returns).sum(axis=1).dropna()
    active = daily_weights.sum(axis=1) > 0.0
    if not active.any():
        return gross.iloc[0:0].rename(config.name), daily_weights
    first_signal = active[active].index[0]
    gross = gross[gross.index >= first_signal]
    gross.name = config.name
    return gross, daily_weights


def simulate_haa_holdings_loop(prices: pd.DataFrame, config: HAAConfig) -> pd.Series:
    """Independent holdings-loop gross-return reference for cross-checks.

    This intentionally avoids the vectorized ``weights.shift(1) * returns`` path
    used by ``simulate_haa_gross``. Agreement within rounding noise is the study's
    lightweight cross-implementation guard [advances_fin_ml, p.31-34].
    """
    daily = canonicalize_columns(prices).sort_index()
    monthly_weights = haa_monthly_weights(daily, config)
    daily_weights = daily_weights_from_monthly(daily, monthly_weights)
    asset_returns = daily[daily_weights.columns].pct_change().fillna(0.0)

    current_weights = pd.Series(0.0, index=daily_weights.columns)
    returns: list[float] = []
    dates: list[pd.Timestamp] = []
    active_seen = False
    for current_date in daily.index:
        row_ret = asset_returns.loc[current_date]
        daily_return = float((current_weights * row_ret).sum())
        if active_seen:
            returns.append(daily_return)
            dates.append(pd.Timestamp(current_date))

        target = daily_weights.loc[current_date]
        if target.sum() > 0.0:
            active_seen = True
            current_weights = target.astype(float)
        elif active_seen:
            current_weights = target.astype(float)

    out = pd.Series(returns, index=pd.DatetimeIndex(dates), name=config.name)
    return out


def equity_from_returns(returns: pd.Series, start_value: float = DEFAULT_START_VALUE) -> pd.Series:
    """Compounded equity curve from daily returns."""
    if returns.empty:
        return pd.Series(dtype=float, name="equity")
    start = pd.Series([start_value], index=[returns.index[0] - pd.Timedelta(days=1)])
    compounded = (1.0 + returns).cumprod() * start_value
    equity = pd.concat([start, compounded])
    equity.name = "equity"
    return equity


def metrics_from_returns(
    returns: pd.Series, periods_per_year: int = TRADING_DAYS_PER_YEAR
) -> dict[str, float | str]:
    """Standard performance metrics for a daily-return series."""
    clean = returns.dropna().astype(float)
    if clean.empty:
        return {
            "start": "n/a",
            "end": "n/a",
            "n_obs": 0,
            "years": 0.0,
            "cagr": 0.0,
            "mdd": 0.0,
            "vol": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "calmar": 0.0,
            "terminal": 1.0,
        }
    equity = equity_from_returns(clean, start_value=1.0)
    years = len(clean) / periods_per_year
    return {
        "start": str(clean.index[0].date()),
        "end": str(clean.index[-1].date()),
        "n_obs": int(len(clean)),
        "years": float(years),
        "cagr": float(cagr(equity, periods_per_year)),
        "mdd": -float(max_drawdown(equity)),
        "vol": float(volatility(clean, periods_per_year)),
        "sharpe": float(sharpe(clean, periods_per_year)),
        "sortino": float(sortino(clean, periods_per_year)),
        "calmar": float(calmar(equity, periods_per_year)),
        "terminal": float(equity.iloc[-1]),
    }


def load_tiingo_price_frame(
    tickers: Iterable[str],
    root: Path = Path("data/tiingo"),
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """Load adjusted-close prices from the local Tiingo parquet cache.

    The function is storage-only by design. It never calls the Tiingo API, because
    this study is meant to preserve and reuse the previously downloaded cache.
    Tiingo adjusted close is the correct return input for total-return-ish equity
    and ETF momentum work when cash distributions matter [stocks_on_the_move,
    p.60].
    """
    root = Path(root)
    prices_dir = root / "daily" / "prices"
    if not prices_dir.exists():
        raise FileNotFoundError(
            f"Tiingo price directory not found: {prices_dir}. Restore the cached parquets "
            "downloaded during the Tiingo subscription before running this study."
        )

    frames: dict[str, pd.Series] = {}
    missing: list[str] = []
    for ticker in sorted({str(t).upper() for t in tickers}):
        path = prices_dir / f"{ticker}.parquet"
        if not path.exists():
            missing.append(ticker)
            continue
        df = pd.read_parquet(path)
        if "adj_close" in df.columns:
            series = df["adj_close"]
        elif "adjClose" in df.columns:
            series = df["adjClose"]
        elif "close" in df.columns:
            series = df["close"]
        else:
            raise KeyError(f"{path} has no adj_close/adjClose/close column")
        series = series.astype(float).sort_index()
        series.index = pd.DatetimeIndex(series.index).tz_localize(None)
        frames[ticker] = series.rename(ticker)

    if missing:
        suffix = "..." if len(missing) > 25 else ""
        raise FileNotFoundError(f"Missing Tiingo parquet files for: {missing[:25]}{suffix}")
    if not frames:
        raise FileNotFoundError(f"No Tiingo parquets loaded from {prices_dir}")

    out = pd.DataFrame(frames).sort_index()
    if start is not None:
        out = out.loc[pd.Timestamp(start):]
    if end is not None:
        out = out.loc[:pd.Timestamp(end)]
    return out


def load_testfolio_price_frame(
    tickers: Iterable[str],
    path: Path = Path("data/testfolio/cache/history.parquet"),
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """Load synthetic ETF equity curves from the local Testfol.io cache."""
    from market_lab.backtest.data.testfolio_loader import load_testfolio_frame

    aliases = {
        "BIL": "CASHX",
        "SPY": "SPYSIM",
        "IWM": "IWMSIM",
        "IEF": "IEFSIM",
        "GLD": "GLDSIM",
        "CASH": "CASHX",
    }
    raw = load_testfolio_frame(path)
    columns: dict[str, pd.Series] = {}
    missing: list[str] = []
    for ticker in sorted({str(t).upper() for t in tickers}):
        source = aliases.get(ticker, f"{ticker}SIM")
        if ticker in raw.columns:
            source = ticker
        if source not in raw.columns:
            missing.append(f"{ticker}->{source}")
            continue
        columns[ticker] = raw[source].astype(float).rename(ticker)
    if missing:
        raise KeyError(f"Missing Testfol.io cached columns: {missing}")
    out = pd.DataFrame(columns).sort_index()
    if start is not None:
        out = out.loc[pd.Timestamp(start):]
    if end is not None:
        out = out.loc[:pd.Timestamp(end)]
    return out


def load_yfinance_price_frame(
    tickers: Iterable[str],
    start: str | None = None,
    end: str | None = None,
    allow_missing: bool = False,
) -> pd.DataFrame:
    """Load adjusted-close prices from yfinance for an explicitly biased screen.

    This loader exists only because the local Tiingo cache was lost. It is never
    used as an automatic fallback: stock or mixed-universe results from a current
    yfinance universe are survivorship-biased and cannot be promoted without a
    delisted/PIT source [advances_fin_ml, p.208-211].
    """
    from market_lab.backtest.data.yfinance_source import YFinanceSource

    fetcher = YFinanceSource()
    start_date = pd.Timestamp(start).date() if start else dt_date(1927, 1, 1)
    end_date = (
        pd.Timestamp(end).date() + timedelta(days=1)
        if end
        else dt_date.today() + timedelta(days=1)
    )

    frames: dict[str, pd.Series] = {}
    missing: list[str] = []
    for ticker in sorted({str(t).upper() for t in tickers}):
        df = fetcher.fetch(ticker, start=start_date, end=end_date, use_cache=True)
        if df.empty:
            missing.append(ticker)
            continue
        series = df["adj_close"].astype(float).sort_index()
        series.index = pd.DatetimeIndex(series.index).tz_localize(None)
        frames[ticker] = series.rename(ticker)

    if missing and not allow_missing:
        suffix = "..." if len(missing) > 25 else ""
        raise FileNotFoundError(f"yfinance returned no data for: {missing[:25]}{suffix}")
    if not frames:
        raise FileNotFoundError("No yfinance prices loaded")

    out = pd.DataFrame(frames).sort_index()
    out.attrs["missing_tickers"] = sorted(missing)
    if start is not None:
        out = out.loc[pd.Timestamp(start):]
    if end is not None:
        out = out.loc[:pd.Timestamp(end)]
    return out


def manifest_tickers_by_asset_class(root: Path = Path("data/tiingo")) -> dict[str, list[str]]:
    """Read Tiingo manifest and group tickers by asset class."""
    import json

    manifest_path = Path(root) / "manifest.json"
    if not manifest_path.exists():
        return {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    grouped: dict[str, list[str]] = {}
    for ticker, entries in manifest.items():
        daily = entries.get("daily", {}) if isinstance(entries, dict) else {}
        asset_class = daily.get("asset_class")
        if asset_class:
            grouped.setdefault(str(asset_class), []).append(str(ticker).upper())
    return {key: sorted(set(values)) for key, values in grouped.items()}
