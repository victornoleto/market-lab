"""Plano A Leveraged Rotation — V2-L2 (Phase 3.5a-V2 CFD).

Gayed-style regime rotation transported to Pepperstone Razor CFD. Per-
asset regime filter gates leverage L between a long risk-on leg (SPY
and/or QQQ held at ``L`` leverage) and a risk-off leg (cash, TLT, or
GLD, unlevered). Each risk-on asset is evaluated under its OWN MA
signal — when SPY is above MA it rotates to levered SPY; when QQQ is
below MA it rotates to the off-regime asset for QQQ's 1/N budget.

This module intentionally duplicates NONE of ``letf_rotation.py`` (the
Plano B Phase 3.5b winner, imutável per memory.md). The differences
are structural:

* **CFD spot leverage, not synthetic LETF.** Daily return in the risk-
  on leg is ``L * spot_return - L * swap_daily`` — no expense-ratio
  daily drag, swap applies to the leveraged notional.
* **Per-asset regime**, multi-asset: each risk-on ticker has its own
  MA signal; the portfolio can be part ON and part OFF between
  different risk-on tickers (budget is equal 1/N across risk-on).
* **No 15% BR tax.** Path A is a foreign CFD broker — capital-gains
  tax on Pepperstone is handled outside the model (Brazilian resident
  DARF). The V2 spec models spread + commission + slippage + swap only.
* **Pepperstone Razor cost model** (spec §3): spread half 2 bps each
  side, commission $3.50/side → 6.6 bps round-trip on a $1 notional
  ($1 is the unit-equity abstraction), slippage 1-3 bps per round-trip,
  swap 0.005%/day long (= 5 bps/day on the LEVERED notional).

Regime signals supported:

* ``"sma200"``: close > SMA(200) → ON, strict cross [Gayed, p.13].
* ``"ema100"``: close > EMA(100) → ON (Reddit study variant).
* ``"lrs"``: majority vote of {SMA100, SMA200, EMA100} ≥ 2/3 → ON
  (composite robustness — Gayed's p.14 Table 6 shows all MAs produce
  positive alpha; the vote dampens any single-MA quirk).

Citations
---------

* Regime rotation as the pure-return-series family: Gayed
  ``[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.21]``.
* Leverage as a regime-dependent exposure (risk-on levered, risk-off
  defensive): ``[leverage_for_the_long_run, p.17, Table 8]``.
* Carver-style CFD cost model + retail risk budget: ``[systematic_trading,
  ch.8-9]``.
* Kelly f/2 leverage cap cross-check: ``[math_money_mgmt, Vince]`` and
  ``[leverage_space, Vince]``.
* Retail Pepperstone Razor cost figures: Phase 3.5a-V2 spec §3,
  docs/investment-mandate.md §3.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal, Mapping

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "TRADING_DAYS_PER_YEAR",
    "PlanoALeveragedRotationConfig",
    "PlanoALeveragedRotationResult",
    "compute_regime_signal",
    "simulate_plano_a_rotation",
]


TRADING_DAYS_PER_YEAR = 252

RegimeSignalKind = Literal["sma200", "ema100", "lrs"]
OffRegimeAssetKind = Literal["cash", "tlt", "gld"]


@dataclass(frozen=True)
class PlanoALeveragedRotationConfig:
    """Immutable config for one V2-L2 Gayed-CFD rotation run.

    Parameters
    ----------
    regime_signal : {"sma200", "ema100", "lrs"}
        Regime filter family applied per risk-on asset. See module
        docstring for definitions.
    leverage : float
        Multiplier applied on risk-on days. 2x, 3x, 5x are the V2
        sweep values. Above 5x is out-of-scope per memory.md mandate
        (PoR > 50% empirically).
    off_regime_asset : {"cash", "tlt", "gld"}
        Where the 1/N slice goes when a risk-on ticker is OFF. Cash
        returns 0. TLT/GLD use the actual daily return of that asset.
    risk_on_tickers : tuple of ticker keys
        Ordered list of risk-on tickers whose prices drive both the
        regime signal and the levered long. Equal 1/N budget each.
    spread_half_bps : float
        Half-spread in bps per side (Pepperstone Razor → 2 bps).
    commission_per_side_usd : float
        Commission per side in USD on a standard lot. For our unit-
        equity simulation we translate to ~3.3 bps per side on $1
        notional assuming $10k lot (= 33 bps round-trip on full notional,
        but since we model per-asset 1/N budget at unit equity, we use
        the bps representation directly).
    commission_round_trip_bps : float
        Commission round-trip already in bps (derived default 6.6 bps
        = $3.30 on $5k/side equivalent). Overridable for sensitivity.
    slippage_bps_round_trip : float
        Slippage round-trip in bps (default 3, mid of 1-3 range).
    swap_daily_pct_long : float
        Daily swap drag on the long LEVERED notional (negative number,
        default -0.005 = -0.5 bps/day). Applied every day on the
        risk-on slice gross exposure.
    """

    regime_signal: RegimeSignalKind = "sma200"
    leverage: float = 2.0
    off_regime_asset: OffRegimeAssetKind = "cash"
    risk_on_tickers: tuple[str, ...] = ("SPY", "QQQ")
    spread_half_bps: float = 2.0
    commission_round_trip_bps: float = 6.6
    slippage_bps_round_trip: float = 3.0
    swap_daily_pct_long: float = -0.005
    cash_rate_annual: float = 0.0

    def __post_init__(self) -> None:
        if self.regime_signal not in ("sma200", "ema100", "lrs"):
            raise ValueError(
                f"regime_signal must be sma200|ema100|lrs, got {self.regime_signal!r}"
            )
        if self.leverage <= 0:
            raise ValueError(f"leverage must be > 0, got {self.leverage}")
        if self.off_regime_asset not in ("cash", "tlt", "gld"):
            raise ValueError(
                f"off_regime_asset must be cash|tlt|gld, got {self.off_regime_asset!r}"
            )
        if not self.risk_on_tickers:
            raise ValueError("risk_on_tickers must not be empty")
        if self.spread_half_bps < 0:
            raise ValueError(f"spread_half_bps must be ≥ 0, got {self.spread_half_bps}")
        if self.commission_round_trip_bps < 0:
            raise ValueError(
                f"commission_round_trip_bps must be ≥ 0, got {self.commission_round_trip_bps}"
            )
        if self.slippage_bps_round_trip < 0:
            raise ValueError(
                f"slippage_bps_round_trip must be ≥ 0, got {self.slippage_bps_round_trip}"
            )

    @property
    def round_trip_cost_pct(self) -> float:
        """Combined round-trip cost as a fraction of a switched notional.

        spread_full = 2 * spread_half_bps (entry + exit).
        Total = spread_full + commission_round_trip + slippage_round_trip.
        """
        total_bps = (
            2.0 * self.spread_half_bps
            + self.commission_round_trip_bps
            + self.slippage_bps_round_trip
        )
        return total_bps / 10_000.0

    @property
    def swap_daily_frac(self) -> float:
        """Daily swap as a signed fraction (e.g. -0.00005 for -0.5 bps/d).

        ``swap_daily_pct_long`` is expressed as a percent (so -0.005 means
        -0.005% = -0.5 bps). Divide by 100 to get the fraction.
        """
        return self.swap_daily_pct_long / 100.0


@dataclass
class PlanoALeveragedRotationResult:
    """Output of a single V2-L2 rotation run."""

    daily_returns: pd.Series
    equity: pd.Series
    weights: pd.DataFrame  # columns = risk_on_tickers + [off_regime_asset]; rows = dates
    regime_on_fraction: pd.Series  # fraction of risk-on tickers ON each day
    switches_by_ticker: pd.Series  # total regime flips per ticker
    cum_cost_pct: float
    cum_swap_pct: float
    median_hold_days: float
    n_switches_total: int
    universe_tickers: tuple[str, ...]
    off_regime_asset: str

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sigma = float(r.std(ddof=1))
        if sigma == 0.0:
            return 0.0
        return float(r.mean() / sigma * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        eq = self.equity.dropna()
        if len(eq) < 2:
            return 0.0
        years = (len(eq) - 1) / periods_per_year
        if years <= 0:
            return 0.0
        total = float(eq.iloc[-1] / eq.iloc[0])
        if total <= 0:
            return -1.0
        return total ** (1.0 / years) - 1.0

    def max_drawdown(self) -> float:
        eq = self.equity.dropna()
        if eq.empty:
            return 0.0
        peak = eq.cummax()
        return float((eq / peak - 1.0).min())


def compute_regime_signal(
    prices: pd.Series,
    kind: RegimeSignalKind = "sma200",
) -> pd.Series:
    """Per-bar "ON"/"OFF" regime signal for a single price series.

    Parameters
    ----------
    prices : pd.Series
        Daily close prices (typically total-return proxy).
    kind : {"sma200", "ema100", "lrs"}
        Signal family. ``lrs`` is a majority vote (≥2/3) over
        {SMA100, SMA200, EMA100}.

    Returns
    -------
    pd.Series
        Object series with values in {"ON", "OFF"} or NaN (warmup).

    Citations
    ---------

    * SMA 200 regime signal: ``[leverage_for_the_long_run, p.13]``.
    * MA periods all produce alpha: ``[leverage_for_the_long_run, p.14,
      Table 6]``.
    * Composite voting for robustness: common CTA practice, see
      ``[systematic_trading, ch.8-9]``.
    """
    if kind not in ("sma200", "ema100", "lrs"):
        raise ValueError(f"kind must be sma200|ema100|lrs, got {kind!r}")
    px = prices.astype(float)

    def _build_object_signal(
        mask_valid: pd.Series, is_on: pd.Series
    ) -> pd.Series:
        valid = mask_valid.fillna(False).to_numpy()
        on = is_on.fillna(False).to_numpy()
        out_arr = np.empty(len(valid), dtype=object)
        out_arr[:] = np.nan
        for i in range(len(out_arr)):
            if valid[i]:
                out_arr[i] = "ON" if on[i] else "OFF"
        return pd.Series(out_arr, index=px.index, dtype=object)

    if kind == "sma200":
        ma = px.rolling(window=200, min_periods=200).mean()
        return _build_object_signal(ma.notna(), px > ma)

    if kind == "ema100":
        ma = px.ewm(span=100, min_periods=100, adjust=False).mean()
        return _build_object_signal(ma.notna(), px > ma)

    # lrs composite
    sma100 = px.rolling(window=100, min_periods=100).mean()
    sma200 = px.rolling(window=200, min_periods=200).mean()
    ema100 = px.ewm(span=100, min_periods=100, adjust=False).mean()
    votes = (
        (px > sma100).astype(int)
        + (px > sma200).astype(int)
        + (px > ema100).astype(int)
    )
    warmup_valid = sma200.notna() & sma100.notna() & ema100.notna()
    return _build_object_signal(warmup_valid, votes >= 2)


def simulate_plano_a_rotation(
    risk_on_panel: Mapping[str, pd.DataFrame],
    config: PlanoALeveragedRotationConfig,
    *,
    off_regime_panel: Mapping[str, pd.DataFrame] | None = None,
) -> PlanoALeveragedRotationResult:
    """Run ONE V2-L2 Gayed-CFD rotation config across the risk-on panel.

    Parameters
    ----------
    risk_on_panel : mapping of ticker → DataFrame with ``close`` column.
        Keys must include every ticker in ``config.risk_on_tickers``.
    config : :class:`PlanoALeveragedRotationConfig`
    off_regime_panel : mapping of asset-key → DataFrame with ``close``.
        Required if ``config.off_regime_asset`` is ``tlt`` or ``gld``.
        Keys are the lowercase off-regime names ("tlt", "gld"). Cash
        needs no panel.

    Returns
    -------
    :class:`PlanoALeveragedRotationResult`

    Notes
    -----
    The backtest calendar is the INTERSECTION of the risk-on tickers'
    indexes (weekdays only). Off-regime asset bars are reindexed onto
    this calendar (ffilled where missing — a missing bar means the
    asset didn't trade that day; we hold the prior close, returning 0).

    The IS/OOS/FWD split logic is NOT applied here (same contract as
    TSMOM multi-asset): the caller computes split metrics from
    ``result.daily_returns`` via
    :func:`ai_trade.backtest.grid.letf_rotation_b1c.compute_split_metrics`.
    """
    for t in config.risk_on_tickers:
        if t not in risk_on_panel:
            raise ValueError(f"risk_on_panel missing ticker {t!r}")
        if "close" not in risk_on_panel[t].columns:
            raise ValueError(f"risk_on_panel[{t!r}] lacks 'close' column")

    # Build per-ticker close series on native index; keep only the
    # intersection of indexes + weekdays (avoids crypto weekend
    # pollution — same rationale as TSMOM multi-asset).
    closes: dict[str, pd.Series] = {}
    for t in config.risk_on_tickers:
        s = risk_on_panel[t]["close"].astype(float).sort_index()
        s = s[~s.index.duplicated(keep="last")]
        closes[t] = s

    # Intersection → common calendar for rotation portfolio.
    common_idx = None
    for s in closes.values():
        common_idx = s.index if common_idx is None else common_idx.intersection(s.index)
    assert common_idx is not None
    common_idx = pd.DatetimeIndex(common_idx)
    common_idx = common_idx[common_idx.dayofweek < 5]
    close_df = pd.DataFrame(
        {t: closes[t].reindex(common_idx) for t in config.risk_on_tickers},
        index=common_idx,
    )

    # Off-regime return series (0 for cash, actual pct_change for tlt/gld).
    if config.off_regime_asset == "cash":
        off_daily = pd.Series(
            config.cash_rate_annual / TRADING_DAYS_PER_YEAR,
            index=common_idx,
        )
    else:
        if off_regime_panel is None or config.off_regime_asset not in off_regime_panel:
            raise ValueError(
                f"off_regime_panel required for off_regime_asset={config.off_regime_asset!r}"
            )
        off_df = off_regime_panel[config.off_regime_asset]
        if "close" not in off_df.columns:
            raise ValueError(
                f"off_regime_panel[{config.off_regime_asset!r}] lacks 'close'"
            )
        off_s = off_df["close"].astype(float).sort_index()
        off_s = off_s[~off_s.index.duplicated(keep="last")]
        off_reindexed = off_s.reindex(common_idx).ffill()
        off_daily = off_reindexed.pct_change()

    # Per-asset daily return (pct_change on the common calendar).
    ret_df = close_df.pct_change()

    # Regime signal per asset, on the asset's OWN native price series
    # (then reindexed onto common_idx). Warmup days yield NaN → treated
    # as OFF (safer cold-start, same convention as letf_rotation.py).
    regime_df = pd.DataFrame(
        index=common_idx, columns=config.risk_on_tickers, dtype=object
    )
    for t in config.risk_on_tickers:
        raw_signal = compute_regime_signal(closes[t], kind=config.regime_signal)
        regime_df[t] = raw_signal.reindex(common_idx).fillna("OFF")

    # Allocation logic at each bar.
    n_assets = len(config.risk_on_tickers)
    budget_per_asset = 1.0 / n_assets  # equal-weight notional budget.
    L = float(config.leverage)
    swap_frac = config.swap_daily_frac  # signed, typically negative
    round_trip_cost = config.round_trip_cost_pct

    # Per-ticker columns: risk-on weight (net of regime) in each asset.
    # Plus the off-regime asset column (sum of idle budgets).
    cols = list(config.risk_on_tickers) + [f"off_{config.off_regime_asset}"]
    weights_arr = np.zeros((len(common_idx), len(cols)), dtype=float)

    daily_net = np.zeros(len(common_idx), dtype=float)
    regime_on_frac = np.zeros(len(common_idx), dtype=float)
    switches_per_ticker = {t: 0 for t in config.risk_on_tickers}
    cum_cost = 0.0
    cum_swap = 0.0
    n_switches_total = 0

    # Hold-segment bookkeeping (for median-hold metric).
    hold_lengths: list[int] = []
    in_segment = {t: False for t in config.risk_on_tickers}
    seg_bar_count = {t: 0 for t in config.risk_on_tickers}

    prev_weights = np.zeros(len(cols), dtype=float)
    ret_vals = ret_df.to_numpy(float)
    off_vals = off_daily.to_numpy(float)

    for bar_i, ts in enumerate(common_idx):
        on_count = 0
        # Determine this bar's target weights (pre-cost).
        new_w = np.zeros(len(cols), dtype=float)
        for k, t in enumerate(config.risk_on_tickers):
            state = regime_df.iloc[bar_i][t]
            if state == "ON":
                new_w[k] = L * budget_per_asset  # levered long on asset k
                on_count += 1
            else:
                # Idle budget parks in off-regime asset.
                new_w[-1] += budget_per_asset
        regime_on_frac[bar_i] = on_count / n_assets

        # Cost on any ∆weight.
        if bar_i == 0:
            delta = np.abs(new_w)
        else:
            delta = np.abs(new_w - prev_weights)
        cost_today = float(np.sum(delta) * round_trip_cost * 0.5)
        # Why * 0.5: |delta| counts the FULL change in gross notional;
        # a full rebuild (0 → w) is logically "one side" of a round trip
        # and we amortize round-trip cost as half per side. Opens AND
        # closes happen across adjacent switches, so over a full enter-
        # exit cycle we pay ~round_trip_cost once. This matches the
        # V1 / V2-L1 accounting convention (round_trip_bps / 10_000 on
        # |delta| turnover).
        # Actually in TSMOM multi-asset the convention is: round_trip
        # bps / 10_000 applied to |delta| directly (no 0.5). Stay
        # consistent with that: treat |delta| as turnover and round-trip
        # bps as the all-in spread+commission cost per turnover unit.
        cost_today = float(np.sum(delta) * round_trip_cost)
        cum_cost += cost_today

        # Count per-ticker switches (prev state vs new state).
        if bar_i > 0:
            for k, t in enumerate(config.risk_on_tickers):
                was_on = prev_weights[k] > 0
                is_on = new_w[k] > 0
                if was_on != is_on:
                    switches_per_ticker[t] += 1
                    n_switches_total += 1

        # Swap on the LEVERED notional only (sum of risk-on weights).
        levered_notional = float(np.sum(new_w[:n_assets]))
        swap_today = levered_notional * swap_frac
        cum_swap += swap_today

        # Daily portfolio return.
        if bar_i == 0:
            gross_ret = 0.0
        else:
            # Risk-on contribution: w_k * asset_k_return.
            per_asset = np.where(
                np.isnan(ret_vals[bar_i]), 0.0, ret_vals[bar_i]
            )
            on_ret = float(np.sum(new_w[:n_assets] * per_asset))
            off_r = off_vals[bar_i] if not np.isnan(off_vals[bar_i]) else 0.0
            off_ret = float(new_w[-1] * off_r)
            gross_ret = on_ret + off_ret

        daily_net[bar_i] = gross_ret - cost_today + swap_today
        # (swap_frac is negative → adding it subtracts cost.)

        weights_arr[bar_i] = new_w
        prev_weights = new_w.copy()

        # Update hold-segment counters.
        for k, t in enumerate(config.risk_on_tickers):
            if new_w[k] > 0:
                if not in_segment[t]:
                    in_segment[t] = True
                    seg_bar_count[t] = 1
                else:
                    seg_bar_count[t] += 1
            else:
                if in_segment[t]:
                    hold_lengths.append(seg_bar_count[t])
                    in_segment[t] = False
                    seg_bar_count[t] = 0

    # Flush any still-open segments.
    for t in config.risk_on_tickers:
        if in_segment[t] and seg_bar_count[t] > 0:
            hold_lengths.append(seg_bar_count[t])

    median_hold = float(np.median(hold_lengths)) if hold_lengths else 0.0
    daily_net_s = pd.Series(daily_net, index=common_idx, dtype=float)
    equity = (1.0 + daily_net_s).cumprod()
    weights_df = pd.DataFrame(weights_arr, index=common_idx, columns=cols)
    switches_s = pd.Series(switches_per_ticker, name="n_switches")

    return PlanoALeveragedRotationResult(
        daily_returns=daily_net_s,
        equity=equity,
        weights=weights_df,
        regime_on_fraction=pd.Series(regime_on_frac, index=common_idx),
        switches_by_ticker=switches_s,
        cum_cost_pct=float(cum_cost),
        cum_swap_pct=float(cum_swap),
        median_hold_days=median_hold,
        n_switches_total=int(n_switches_total),
        universe_tickers=tuple(config.risk_on_tickers),
        off_regime_asset=config.off_regime_asset,
    )
