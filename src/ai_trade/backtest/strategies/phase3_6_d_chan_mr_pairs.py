"""Phase 3.6 Family D — Chan-style cointegrated MR pairs (NON-Kalman).

Rolling-window cointegration pair-trading on liquid ETF pairs, using
static-per-window OLS hedge-ratio estimation (explicitly NOT Kalman).
Entry/exit by z-score of the residual spread. Return-series engine
(no bar-level positions).

This family deliberately avoids the Kalman variant that was tested as
V2-L5 (phase 3.5f) and FAILED structurally (0/6 pairs passed ADF).
Instead this implementation:

  * Uses the Engle-Granger test `statsmodels.tsa.stattools.coint` on a
    rolling lookback window to gate each pair's tradability per day.
    Pair trades only when the EG p-value ≤ ``coint_pvalue_gate`` over
    the lookback. `[algo_trading_chan, p.51-54]`
  * Recomputes the hedge ratio β via OLS on log-prices each day using
    the trailing lookback window (static-per-day, updated as the window
    rolls). This is the canonical "rolling OLS pair trader" variant
    described by Chan in ch.3 where he contrasts it to the Kalman
    filter. `[algo_trading_chan, ch.3 p.65-75]`
  * Computes the residual spread ``s_t = log(y_t) - α - β · log(x_t)``
    using ONLY the lookback window for (α, β) — no look-ahead.
    `[advances_fin_ml, p.31-34]`
  * Z-scores the residual using the same lookback-window mean and std,
    shifted by one bar so that today's entry signal uses yesterday's
    z-score. `[advances_fin_ml, p.31-34]`
  * Exits on z crossing ``exit_z`` (0.0 canonical: mean-cross) or on
    the stop at |z| > ``stop_z`` (no fail-safe in Chan but prudent for
    regime-break insurance). `[algo_trading_chan, p.71-73, p.183-184]`

Broker model
------------

Pepperstone Razor CFD for pairs (plan §3.1) — per-leg spread ~0.05%,
commission $0.35 per 100k notional per side, swap −0.02% per night on
levered notional. Pairs are typically net-flat so swap impact is
modest; we still apply it per leg.

Citations glossary
------------------

* Pair-selection principle (sector peers + cointegration test):
  `[algo_trading_chan, p.51-54, p.88-89]`.
* Engle-Granger cointegration test:
  `[algo_trading_chan, p.51-54, p.42-43]`.
* Rolling OLS hedge ratio vs Kalman:
  `[algo_trading_chan, ch.3 p.65-80]` (rolls vs Kalman comparison).
* Z-score entry/exit bands (Bollinger-pairs):
  `[algo_trading_chan, p.71-73, p.94]`.
* Half-life lookback sizing:
  `[algo_trading_chan, p.47-48]`.
* Stops only above backtest max DD:
  `[algo_trading_chan, p.183-184]`.
* Look-ahead timing convention:
  `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint

log = logging.getLogger(__name__)

__all__ = [
    "ChanPairsConfig",
    "ChanPairsResult",
    "simulate_chan_pairs",
    "PairSpec",
    "DEFAULT_PAIRS",
]


@dataclass(frozen=True)
class PairSpec:
    """One (y, x) pair with its own IS start date (inception-aware).

    The pair trades ``y`` as the dependent variable and ``x`` as the
    independent, with hedge ratio β regressing log(y) on log(x).
    Chan's RULE [p.54, ch.2] — try both orderings and pick the one
    with the more negative t-statistic — is deferred; the primary
    orientation is chosen per sector convention (larger-notional or
    broader-index goes in y).
    """

    y: str
    x: str
    label: str = ""

    def __post_init__(self) -> None:
        if not self.label:
            object.__setattr__(self, "label", f"{self.y}_{self.x}")


# Default pair list: sector-peer ETFs with long IS coverage (both legs
# inception ≤ 2007 in Tiingo bulk). Deliberately avoids the KRE/KBE/OIH
# suggestions from the brief (not in Tiingo bulk). All 5 pairs have
# defensible economic cointegration rationale (same risk factor).
#
# Economic rationale per pair:
#   XLE/USO   energy equity vs oil futures beta — commodity exposure
#             [algo_trading_chan, p.116-120]
#   TLT/IEF   20y vs 10y Treasuries — same duration factor
#             [algo_trading_chan, p.52-53]
#   HYG/LQD   high-yield vs investment-grade credit — same rate factor
#             [quant_trading_chan, ch.3]
#   GLD/SLV   gold vs silver — shared precious-metals risk premium
#             [algo_trading_chan, p.52]
#   XLU/XLP   utilities vs consumer staples — defensive-equity factor
#             [algo_trading_chan, p.88-89]
DEFAULT_PAIRS: tuple[PairSpec, ...] = (
    PairSpec(y="XLE", x="USO", label="energy_xle_uso"),
    PairSpec(y="TLT", x="IEF", label="bonds_tlt_ief"),
    PairSpec(y="HYG", x="LQD", label="credit_hyg_lqd"),
    PairSpec(y="GLD", x="SLV", label="metals_gld_slv"),
    PairSpec(y="XLU", x="XLP", label="defensives_xlu_xlp"),
)


@dataclass(frozen=True)
class ChanPairsConfig:
    """Immutable configuration for a Chan pairs run.

    Parameters
    ----------
    lookback
        Rolling window used for both OLS hedge-ratio estimation and
        residual z-score statistics, in trading days. Chan recommends a
        small multiple of the half-life `[algo_trading_chan, p.47]`.
        Grid values {60, 126, 252} span ~3mo/~6mo/~1y.
    entry_z
        |z| threshold for entry. Canonical {1.5, 2.0, 2.5} — Chan uses
        1.0 in his Bollinger-pairs example `[algo_trading_chan, p.71-72]`
        but notes it's a free parameter optimized in training. We use
        wider entries to filter noise.
    exit_z
        |z| threshold for exit. Mean-cross exit = 0.0; partial exit = 0.5.
        Canonical `[algo_trading_chan, p.71-72]`.
    stop_z
        Hard stop at |z| > stop_z. Chan NEVER rule `[p.183-184, ch.8]`
        says stops should be above backtest max DD; 3.5-4.0 is beyond
        typical spread excursion so it only fires on regime break.
    coint_pvalue_gate
        Engle-Granger p-value threshold to ALLOW the pair to trade in a
        given rolling window. 0.10 is Chan's pragmatic threshold
        `[algo_trading_chan, p.54]` (looser than 0.05 because EG power
        on 252 bars is modest). Set to 1.0 to disable the gate.
    per_pair_gross_pct
        Fraction of equity put on one leg at entry (matched on the other).
        5% per pair × 5 pairs × 2 legs = 50% gross when all are active
        — well within 100% cap.
    spread_one_way_pct
        Spread cost per leg per entry/exit. 0.0005 (5 bps) ~ sector ETF
        typical. `[plan §3.1]`.
    commission_per_trade_pct
        Commission per leg per entry/exit in fraction of notional.
        Pepperstone Razor: $0.35 per $100k = 0.000035 per $1.
    swap_per_night_pct
        Overnight swap on levered notional per leg per night. −0.02%
        per night per leg (−0.04% total per pair-night) is the Razor
        Oct-2024 reference `[plan §3.1]`.
    tax_rate
        BR capital-gains tax on realized gains. Pepperstone is
        non-BR-source so tax_rate=0.0 is the default. `[mandate §1]`.
    min_obs_for_coint
        Minimum bars needed before running the EG test. We require ≥30.
    """

    lookback: int = 126
    entry_z: float = 2.0
    exit_z: float = 0.0
    stop_z: float = 4.0
    coint_pvalue_gate: float = 0.10
    per_pair_gross_pct: float = 0.05
    spread_one_way_pct: float = 0.0005
    commission_per_trade_pct: float = 0.000035
    swap_per_night_pct: float = 0.0002  # 0.02% per night per leg
    tax_rate: float = 0.0
    min_obs_for_coint: int = 30

    def __post_init__(self) -> None:
        if self.lookback < 30:
            raise ValueError(f"lookback must be >= 30, got {self.lookback}")
        if self.entry_z <= 0:
            raise ValueError(f"entry_z must be > 0, got {self.entry_z}")
        if self.exit_z < 0 or self.exit_z >= self.entry_z:
            raise ValueError(
                f"exit_z must be in [0, entry_z), got exit={self.exit_z} entry={self.entry_z}"
            )
        if self.stop_z <= self.entry_z:
            raise ValueError(
                f"stop_z must be > entry_z, got stop={self.stop_z} entry={self.entry_z}"
            )
        if not 0 < self.per_pair_gross_pct <= 0.5:
            raise ValueError(
                f"per_pair_gross_pct must be in (0, 0.5], got {self.per_pair_gross_pct}"
            )
        if not 0.0 <= self.coint_pvalue_gate <= 1.0:
            raise ValueError(
                f"coint_pvalue_gate must be in [0, 1], got {self.coint_pvalue_gate}"
            )


@dataclass
class ChanPairsResult:
    """Output of a Chan pairs simulation."""

    daily_returns: pd.Series
    per_pair_returns: pd.DataFrame  # column per pair
    positions: pd.DataFrame  # long/short/flat per pair per day
    hold_lengths: list[int] = field(default_factory=list)
    n_trades_per_pair: dict[str, int] = field(default_factory=dict)
    n_coint_bars_per_pair: dict[str, int] = field(default_factory=dict)
    total_bars_per_pair: dict[str, int] = field(default_factory=dict)
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = 252) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        if sd == 0.0:
            return 0.0
        return float(r.mean() / sd * np.sqrt(periods_per_year))

    def median_hold_days(self) -> float:
        if not self.hold_lengths:
            return float("nan")
        return float(np.median(self.hold_lengths))


def _rolling_ols_beta(
    log_y: pd.Series, log_x: pd.Series, lookback: int
) -> tuple[pd.Series, pd.Series]:
    """Rolling OLS regressing log_y on log_x over trailing ``lookback`` bars.

    Returns (alpha, beta) series. Both are NaN in the first
    ``lookback-1`` positions. Values at index ``t`` use bars
    ``[t-lookback+1, t]`` inclusive (anchored on today's close), so
    downstream must shift by 1 before acting on them to avoid look-ahead.

    Closed-form OLS: β = cov(x, y) / var(x); α = mean(y) - β·mean(x).
    Uses pandas rolling for speed instead of iterating.
    """
    # cov(x, y) and var(x) via rolling; pandas uses Bessel-corrected by
    # default which is fine — β is invariant to that normalization.
    rolled_x = log_x.rolling(window=lookback, min_periods=lookback)
    rolled_y = log_y.rolling(window=lookback, min_periods=lookback)
    mean_x = rolled_x.mean()
    mean_y = rolled_y.mean()
    var_x = rolled_x.var()
    # cov(x,y) via E[xy] - E[x]E[y]
    mean_xy = (log_x * log_y).rolling(window=lookback, min_periods=lookback).mean()
    cov_xy = mean_xy - mean_x * mean_y
    beta = cov_xy / var_x.replace(0.0, np.nan)
    alpha = mean_y - beta * mean_x
    return alpha, beta


def _residual_zscore(
    log_y: pd.Series, log_x: pd.Series, alpha: pd.Series, beta: pd.Series, lookback: int
) -> pd.Series:
    """Compute z-score of residual s_t = log_y - α_t - β_t · log_x.

    The z-score uses a rolling mean/std of the residual OVER the same
    lookback window. To avoid look-ahead, we:

      1. Compute residual at each t using (α_t, β_t) from the same
         trailing window (definition above).
      2. Z-score with trailing (mean, std) of the residual — again
         ending at t.
      3. Caller shifts the output series by 1 before consuming.
    """
    residual = log_y - alpha - beta * log_x
    r_mean = residual.rolling(window=lookback, min_periods=lookback).mean()
    r_std = residual.rolling(window=lookback, min_periods=lookback).std()
    z = (residual - r_mean) / r_std.replace(0.0, np.nan)
    return z


def _rolling_coint_pvalue(
    y: pd.Series, x: pd.Series, lookback: int, stride: int = 21
) -> pd.Series:
    """Engle-Granger p-value computed on rolling windows, stride-sampled.

    statsmodels.tsa.stattools.coint is slow; evaluating every bar on
    252-bar windows takes minutes per pair. We evaluate every ``stride``
    bars (default 21 = ~monthly) and forward-fill between evaluations.
    The p-value gate is a slow-moving filter so monthly refresh is
    faithful to Chan's practice [p.54].

    Returns a Series aligned to y/x.index with NaN in warmup. The first
    ``lookback-1`` bars are NaN; after that we have a valid p-value.
    """
    idx = y.index
    out = pd.Series(np.nan, index=idx, dtype=float)
    n = len(idx)
    if n < lookback:
        return out

    # Evaluation points: every `stride` from lookback-1 to n-1
    eval_points = list(range(lookback - 1, n, stride))
    if eval_points[-1] != n - 1:
        eval_points.append(n - 1)

    y_vals = y.values
    x_vals = x.values
    for ep in eval_points:
        lo = ep - lookback + 1
        y_win = y_vals[lo : ep + 1]
        x_win = x_vals[lo : ep + 1]
        if np.any(np.isnan(y_win)) or np.any(np.isnan(x_win)):
            continue
        # Guard against degenerate windows (zero variance on either leg).
        if np.std(y_win) == 0 or np.std(x_win) == 0:
            continue
        try:
            _, pval, _ = coint(y_win, x_win, autolag="BIC")
        except Exception:
            continue
        out.iloc[ep] = pval
    # Forward-fill so the gate stays valid between evaluations.
    return out.ffill()


def _simulate_one_pair(
    prices_y: pd.Series,
    prices_x: pd.Series,
    ret_y: pd.Series,
    ret_x: pd.Series,
    config: ChanPairsConfig,
    pair_label: str,
) -> tuple[pd.Series, pd.Series, list[int], int, int, int, float]:
    """Simulate one pair and return its daily return contribution.

    Return computation convention
    -----------------------------

    For a single pair, if we're long the spread at day t-1 (long y, short
    β·x in log-notional), the day-t return of the spread is::

        r_spread_t = r_y_t - β_{t-1} · r_x_t

    Because we shift signals by one bar, β used for today's return is the
    β at close of t-1. Per-pair gross notional is ``per_pair_gross_pct``
    (applied as a weight into the portfolio), so the pair contributes::

        w_t · sign_{t-1} · r_spread_t

    where sign ∈ {+1, -1, 0} (long-spread / short-spread / flat).

    Costs (spread + commission) are applied on position changes. Swap
    cost is applied per night when the pair holds any position (both
    legs incur swap).
    """
    log_y = np.log(prices_y.astype(float))
    log_x = np.log(prices_x.astype(float))
    # 1. Rolling OLS α, β
    alpha, beta = _rolling_ols_beta(log_y, log_x, config.lookback)
    # 2. Residual z-score (trailing stats, anchored at t)
    z_t = _residual_zscore(log_y, log_x, alpha, beta, config.lookback)
    # 3. Rolling EG p-value gate (stride=21d monthly refresh)
    pval = _rolling_coint_pvalue(
        log_y, log_x, config.lookback, stride=max(21, config.lookback // 12)
    )

    # Shift all signals by 1 bar: today's position uses yesterday's
    # signals. `[advances_fin_ml, p.31-34]`
    z_lag = z_t.shift(1)
    beta_lag = beta.shift(1)
    pval_lag = pval.shift(1)

    # Position logic: +1 = long spread (long y short x), -1 = short, 0 = flat.
    # Entry triggers and exit triggers with hysteresis.
    idx = prices_y.index
    position = pd.Series(0.0, index=idx)
    prev_pos = 0.0
    hold_lengths: list[int] = []
    cur_hold = 0
    n_coint_bars = 0
    n_trades = 0

    for i, ts in enumerate(idx):
        z = z_lag.iloc[i]
        p = pval_lag.iloc[i]
        if np.isnan(z) or np.isnan(p):
            position.iloc[i] = 0.0
            if prev_pos != 0.0:
                hold_lengths.append(cur_hold)
            prev_pos = 0.0
            cur_hold = 0
            continue
        coint_ok = p <= config.coint_pvalue_gate
        if coint_ok:
            n_coint_bars += 1

        # Stop-loss: flat out if |z| > stop_z regardless of coint status
        if abs(z) > config.stop_z:
            new_pos = 0.0
        elif coint_ok:
            if prev_pos == 0.0:
                # entry conditions
                if z < -config.entry_z:
                    new_pos = 1.0  # long spread (y cheap vs x)
                elif z > config.entry_z:
                    new_pos = -1.0  # short spread (y rich vs x)
                else:
                    new_pos = 0.0
            elif prev_pos > 0:
                # long — exit when z crosses above -exit_z (toward mean)
                if z >= -config.exit_z:
                    new_pos = 0.0
                else:
                    new_pos = 1.0
            else:  # prev_pos < 0
                # short — exit when z crosses below +exit_z
                if z <= config.exit_z:
                    new_pos = 0.0
                else:
                    new_pos = -1.0
        else:
            # Cointegration gate OFF — unwind existing pos.
            new_pos = 0.0

        position.iloc[i] = new_pos
        if new_pos == prev_pos and new_pos != 0.0:
            cur_hold += 1
        else:
            if prev_pos != 0.0:
                hold_lengths.append(cur_hold)
            cur_hold = 1 if new_pos != 0.0 else 0
            if new_pos != 0.0 and new_pos != prev_pos:
                n_trades += 1
        prev_pos = new_pos
    # Flush trailing hold
    if prev_pos != 0.0 and cur_hold > 0:
        hold_lengths.append(cur_hold)

    # Daily return of the pair's spread (unit gross, per leg):
    # r_spread = r_y - β_lag · r_x
    ret_y_aligned = ret_y.reindex(idx).fillna(0.0)
    ret_x_aligned = ret_x.reindex(idx).fillna(0.0)
    beta_for_ret = beta_lag.reindex(idx).fillna(0.0)
    # Cap |β| at 5 to guard against degenerate OLS near no-variance (a
    # structural safety — Chan never sees |β| > 2 on sector peers).
    beta_for_ret = beta_for_ret.clip(lower=-5.0, upper=5.0)
    spread_ret = ret_y_aligned - beta_for_ret * ret_x_aligned

    # Per-pair weighted return BEFORE costs
    pos_lag_for_ret = position.shift(1).fillna(0.0)  # apply position from t-1 to t's return
    pair_ret_gross = pos_lag_for_ret * spread_ret * config.per_pair_gross_pct

    # Cost side: every position change incurs 2× spread + 2× commission
    # (one for y leg, one for x leg), scaled by 2 × per_pair_gross (both
    # legs). Entry and exit each trigger costs.
    pos_change = (position - position.shift(1)).abs().fillna(0.0)
    # Each unit of pos_change means one leg's full notional turned over
    # twice (close old pos + open new pos). We apply spread+comm per leg
    # per side, two legs, so 2 × (spread + commission).
    per_change_cost = (
        2.0 * (config.spread_one_way_pct + config.commission_per_trade_pct)
    )
    cost_impact = pos_change * per_change_cost * config.per_pair_gross_pct

    # Swap: applied each night the pair has a non-zero position. Both
    # legs incur swap → 2× swap_per_night_pct on per_pair_gross notional.
    swap_impact = (
        position.abs() * 2.0 * config.swap_per_night_pct * config.per_pair_gross_pct
    )

    pair_ret_net = pair_ret_gross - cost_impact - swap_impact

    total_cost = float(cost_impact.sum() + swap_impact.sum())
    return (
        pair_ret_net,
        position,
        hold_lengths,
        n_trades,
        n_coint_bars,
        len(idx),
        total_cost,
    )


def simulate_chan_pairs(
    prices: dict[str, pd.Series],
    returns: dict[str, pd.Series],
    config: ChanPairsConfig,
    pairs: Sequence[PairSpec] = DEFAULT_PAIRS,
) -> ChanPairsResult:
    """Simulate a multi-pair Chan MR-pairs basket.

    Parameters
    ----------
    prices
        Dict {ticker → adjusted close Series}. All tickers referenced in
        ``pairs`` must be present. Series should share a common date
        index or be aligned-at-callsite.
    returns
        Dict {ticker → daily total returns (pct_change of adj_close)}.
    config
        Strategy configuration.
    pairs
        Sequence of :class:`PairSpec` describing (y, x) pair orientations.

    Returns
    -------
    ChanPairsResult
        Portfolio-level daily returns (sum over all pairs), per-pair
        positions & hold distribution, and aggregate cost/tax counters.

    Notes
    -----
    Tax is intentionally applied at portfolio level post-hoc: we apply
    ``tax_rate`` on aggregate monthly-positive net-profit months. For the
    default Pepperstone path (``tax_rate=0.0``) this is a no-op.
    """
    # Build master index = intersection of all referenced tickers
    tickers = set()
    for p in pairs:
        tickers.add(p.y)
        tickers.add(p.x)
    missing = [t for t in tickers if t not in prices or t not in returns]
    if missing:
        raise KeyError(f"Missing ticker(s) in prices/returns: {missing}")

    idx = None
    for t in tickers:
        idx_t = prices[t].dropna().index
        idx = idx_t if idx is None else idx.intersection(idx_t)
    assert idx is not None and len(idx) > 0

    per_pair_ret: dict[str, pd.Series] = {}
    positions: dict[str, pd.Series] = {}
    all_holds: list[int] = []
    trades_map: dict[str, int] = {}
    coint_bars_map: dict[str, int] = {}
    total_bars_map: dict[str, int] = {}
    total_cost = 0.0

    for p in pairs:
        py = prices[p.y].reindex(idx).astype(float)
        px = prices[p.x].reindex(idx).astype(float)
        ry = returns[p.y].reindex(idx).astype(float)
        rx = returns[p.x].reindex(idx).astype(float)
        ret_p, pos_p, holds_p, n_tr, n_cb, n_tot, cost_p = _simulate_one_pair(
            py, px, ry, rx, config, p.label
        )
        per_pair_ret[p.label] = ret_p
        positions[p.label] = pos_p
        all_holds.extend(holds_p)
        trades_map[p.label] = n_tr
        coint_bars_map[p.label] = n_cb
        total_bars_map[p.label] = n_tot
        total_cost += cost_p

    ppr_df = pd.concat(per_pair_ret, axis=1).reindex(idx).fillna(0.0)
    pos_df = pd.concat(positions, axis=1).reindex(idx).fillna(0.0)

    # Portfolio daily return = sum across pairs (each already scaled by
    # per_pair_gross_pct). With 5 pairs × 5% = 25% gross max per side,
    # well within 100% cap.
    daily_ret = ppr_df.sum(axis=1)

    # Optional BR-tax (applied at portfolio level on monthly buckets of
    # realized net gain). Pepperstone default has tax_rate=0.0 so this
    # is a no-op by default.
    cum_tax = 0.0
    if config.tax_rate > 0.0:
        # Monthly bucket realization: apply tax once per positive month
        month_key = daily_ret.index.to_period("M")
        by_month = daily_ret.groupby(month_key).sum()
        # Build a daily factor series that subtracts tax only at month-end
        tax_on_last_day = pd.Series(0.0, index=daily_ret.index)
        for m, g in by_month.items():
            if g > 0:
                tax = g * config.tax_rate
                mask = month_key == m
                last_day = daily_ret.index[mask][-1]
                tax_on_last_day.loc[last_day] -= tax
                cum_tax += tax
        daily_ret = daily_ret + tax_on_last_day

    return ChanPairsResult(
        daily_returns=daily_ret,
        per_pair_returns=ppr_df,
        positions=pos_df,
        hold_lengths=all_holds,
        n_trades_per_pair=trades_map,
        n_coint_bars_per_pair=coint_bars_map,
        total_bars_per_pair=total_bars_map,
        cum_cost_pct=total_cost,
        cum_tax_pct=cum_tax,
    )
