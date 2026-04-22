"""Phase 3.7 — H2.a: Božović 2024 VIX-managed portfolio (pure VIX-scaling on SPY/cash).

**Literal replication** of Božović (2024) "VIX-managed portfolios", *International
Review of Financial Analysis* v95 Part A, applied to the SPY / cash (SHV) pair
with a daily rebalance. The signal is a **forward-looking** vol-scaling rule:

    exposure_t = clip(vix_baseline / VIX_prior_month_mean_{t-1}, 0.0, 1.0)

where ``VIX_prior_month_mean_{t-1}`` is the trailing 21-trading-day mean of
VIXCLS close through bar ``t-1`` (strictly no peek into day ``t``), and
``vix_baseline = 20`` is the paper's canonical anchor (the long-run unconditional
VIX mean 1990-2023). On bar ``t`` the allocation is

    w_SPY[t] = exposure_t
    w_SHV[t] = 1 - exposure_t

and the earned daily return (F2-patched alignment) is

    r_port[t] = w_SPY[t-1] * r_SPY[t] + w_SHV[t-1] * r_SHV[t]

Weights are computed from data through ``t-1``; the position earns return on
``t+1`` via ``prev_weights = weights.shift(1).fillna(0.0)``. This is the same
lookahead convention used across Phase 3.6 Family K and Phase 3.7 H1 modules
(``[advances_fin_ml, p.31-34]``).

Path B (Banco Inter Strategy B) cost model
------------------------------------------
* **Commission: zero** — Inter&Co Securities (FINRA) is commission-free for
  US equity ETFs.
* **FX spread: 1.20% per conversion** (midpoint of the 0.99%–1.50% range
  documented in feedback memory ``project_plano_b_broker_inter.md``). This
  applies on deposit/withdrawal only; inside a USD sub-account trading USD
  instruments (SPY/SHV) there is no per-trade FX conversion cost.
  **Effectively zero intra-strategy cost.**
* **15% DARF on realized capital gains** — BR swing capital-gains tax per
  mandate §4 (Strategy B rota B). Implemented as a **year-end realization
  event**: at the close of each calendar year, simulate a single liquidation
  of the net rebalance gain and tax it at 15%; intra-year losses carry forward
  within the year only (no cross-year loss netting — conservative
  interpretation of BR CG regime).
* **T+1 settlement:** daily rebal at close → next-day trade settles before
  next rebal, no conflict.
* **Cost×2 sensitivity (gate 13):** tax_rate ×2 = 30% and spread bps ×2.
  Under Inter rota B the intra-strategy spread is already ~0 so the cost×2
  stress is dominated by the tax doubling.

Citations
---------
* **Signal spec:** Božović (2024) "VIX-managed portfolios", *International
  Review of Financial Analysis* v95 Part A — ``[bozovic_2024_irfa]`` (indexed
  in ``docs/research/2026-04-23-phase3.7-literature-sprint.md §T2.Paper1``).
* **Prior-month VIX mean as scaling input:** ``[bozovic_2024_irfa, §2.2]``
  (paper methodology section; literature-sprint §T2 para 1-2).
* **Lookahead timing (prev_weight × ret):** ``[advances_fin_ml, p.31-34]``.
* **15% BR swing CG tax on Inter rota B:** ``docs/investment-mandate.md §4``;
  memory ``feedback_pepperstone_staging_and_darf.md``.
* **13-gate validation:** ``docs/investment-mandate.md §2.4`` + Phase 3.7-3
  hunt prompt (2026-04-23).

Look-ahead audit
----------------
For each trading day ``t``:

* ``vix_ma_21[t-1]`` = rolling 21-day mean of VIXCLS close over days
  ``[t-21, t-1]`` — **shifted by 1** (``.shift(1)``) so day ``t`` does not
  peek into its own VIXCLS reading. Warmup: the first 21 days yield NaN →
  ``exposure`` is forced to 0 (all-cash) until the MA is defined.
* ``exposure_t = clip(20 / vix_ma_21[t-1], 0, 1)``. Deterministic in
  ``vix_ma_21[t-1]``.
* ``weights[t] = (exposure_t, 1 - exposure_t)`` is known on day ``t`` from
  strictly-prior VIXCLS, so the F2-patched alignment ``prev_weights =
  weights.shift(1).fillna(0.0)`` then earns the correct return on day ``t+1``
  without any lookahead.

Design choices (trimmed to baseline)
------------------------------------
This module implements the **literal Božović baseline** only. Design knobs
held fixed at paper values:

* ``vix_baseline = 20.0`` (paper anchor).
* ``vix_ma_days = 21`` (prior-month trailing average).
* ``exposure_cap = 1.0``, ``exposure_floor = 0.0`` (no leverage baseline;
  H2.b is where leverage is added).
* Daily rebalance at close (paper-mandated cadence).
* Cash proxy = SHV daily return (short-dated Treasury ETF, close-to-close).
* Year-end tax realization (simple, documented).

No parameter sweep in H2.a — the sensitivity grid is a SHIFT of
``vix_ma_days`` (21 → {10, 14, 21, 42, 63}) and ``vix_baseline`` (20 → {15,
20, 25}) used **only** for PBO/DSR, not for winner selection.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "H2BozovicVixScalingConfig",
    "H2BozovicVixScalingResult",
    "compute_vix_exposure",
    "simulate_h2_bozovic_vix_scaling",
]


TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class H2BozovicVixScalingConfig:
    """Immutable Božović 2024 VIX-scaling config.

    Parameters
    ----------
    vix_baseline : float
        Long-run VIX anchor in points. Paper canonical = 20.0 (approx
        unconditional VIX mean 1990-2023). [bozovic_2024_irfa, §2.2]
    vix_ma_days : int
        Trailing-window length in trading days for the prior-month VIX
        mean. Paper canonical = 21 (≈ 1 calendar month of trading days).
        [bozovic_2024_irfa, §2.2]
    exposure_floor : float
        Lower bound on ``exposure_t``. Paper baseline = 0.0 (fully cash in
        high-VIX regimes is allowed).
    exposure_cap : float
        Upper bound on ``exposure_t``. Paper baseline = 1.0 (unleveraged).
        H2.b explores > 1.0 as the leverage variant.
    tax_rate : float
        Year-end CG tax on realized annual net return. 0.15 per mandate §4
        (BR swing rate on Inter rota B). Cost×2 sensitivity uses 0.30.
    fx_spread : float
        Per-conversion FX cost as fraction. Inter rota B: 0.012 (1.2%).
        **Applied to deposit/withdrawal only, NOT per trade** — inside a USD
        sub-account it is structurally zero. Kept as a parameter so the
        cost×2 sensitivity can sanity-check boundary conversion impact.
    apply_fx_on_rebalance : bool
        If True, charge ``fx_spread`` on every rebalance turnover. Default
        False (Inter USD sub-account model). Set True to stress-test a
        hypothetical BRL-settled sub-account.
    rebalance_threshold : float
        Minimum absolute change in ``exposure_t`` required to trigger an
        actual rebalance on day ``t``. Default 0.0 (rebalance every bar —
        matches paper). Kept for a turnover-sensitivity variant.
    """

    vix_baseline: float = 20.0
    vix_ma_days: int = 21
    exposure_floor: float = 0.0
    exposure_cap: float = 1.0
    tax_rate: float = 0.15
    fx_spread: float = 0.012
    apply_fx_on_rebalance: bool = False
    rebalance_threshold: float = 0.0

    def __post_init__(self) -> None:
        if self.vix_baseline <= 0:
            raise ValueError(f"vix_baseline must be > 0, got {self.vix_baseline}")
        if self.vix_ma_days < 2:
            raise ValueError(f"vix_ma_days must be >= 2, got {self.vix_ma_days}")
        if self.exposure_floor < 0:
            raise ValueError(
                f"exposure_floor must be >= 0, got {self.exposure_floor}"
            )
        if self.exposure_cap <= self.exposure_floor:
            raise ValueError(
                f"exposure_cap ({self.exposure_cap}) must be > exposure_floor "
                f"({self.exposure_floor})"
            )
        if not 0.0 <= self.tax_rate <= 1.0:
            raise ValueError(f"tax_rate must be in [0, 1], got {self.tax_rate}")
        if self.fx_spread < 0:
            raise ValueError(f"fx_spread must be >= 0, got {self.fx_spread}")
        if self.rebalance_threshold < 0:
            raise ValueError(
                f"rebalance_threshold must be >= 0, got {self.rebalance_threshold}"
            )


@dataclass
class H2BozovicVixScalingResult:
    """Simulation output (daily bar granularity).

    Attributes
    ----------
    daily_returns : pd.Series
        Net daily return after year-end tax and any FX-on-rebalance cost.
    gross_returns : pd.Series
        Pre-tax / pre-cost daily return (just ``prev_w × r``).
    exposure : pd.Series
        Daily SPY exposure ∈ [exposure_floor, exposure_cap]. NaN during
        warmup (first ``vix_ma_days`` bars).
    weights : pd.DataFrame
        Columns ``['SPY', 'SHV']``; rows are aligned to the common index.
    equity : pd.Series
        Compound equity curve starting at 1.0, after all costs/tax.
    tax_events : list[tuple[pd.Timestamp, float]]
        (year-end date, tax paid as fraction of year-start equity).
    cum_tax_pct : float
        Total tax paid as fraction of starting equity (cumulative drag).
    cum_fx_pct : float
        Total FX-on-rebalance drag, if enabled.
    n_rebalances : int
        Number of days where actual rebalance exceeded
        ``rebalance_threshold``.
    turnover : float
        Mean daily absolute change in SPY exposure — a paper-style measure
        of rebalance intensity.
    """

    daily_returns: pd.Series
    gross_returns: pd.Series
    exposure: pd.Series
    weights: pd.DataFrame
    equity: pd.Series
    tax_events: list[tuple[pd.Timestamp, float]]
    cum_tax_pct: float
    cum_fx_pct: float
    n_rebalances: int
    turnover: float

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        """Annualized Sharpe of net daily returns (ddof=1)."""
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sigma = float(r.std(ddof=1))
        if sigma <= 0:
            return 0.0
        return float(r.mean() / sigma * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        """Annualized CAGR from the equity curve."""
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
        """Max drawdown as negative fraction (e.g. -0.35 = -35%)."""
        eq = self.equity.dropna()
        if eq.empty:
            return 0.0
        peak = eq.cummax()
        return float((eq / peak - 1.0).min())


def compute_vix_exposure(
    vix_close: pd.Series,
    config: H2BozovicVixScalingConfig,
) -> pd.Series:
    """Compute the Božović VIX-scaled SPY exposure series.

    ``exposure_t = clip(vix_baseline / VIX_ma_{t-1}, exposure_floor, exposure_cap)``

    The trailing MA is shifted by 1 bar so that day ``t`` does not peek into
    its own VIXCLS close.

    Parameters
    ----------
    vix_close : pd.Series
        VIXCLS daily close series (DatetimeIndex, ascending, no NaN).
    config : H2BozovicVixScalingConfig
        Signal parameters.

    Returns
    -------
    pd.Series
        Float series on ``vix_close.index``. First ``vix_ma_days`` entries
        are NaN (warmup). Subsequent entries ∈ [exposure_floor, exposure_cap].
    """
    if vix_close.empty:
        return pd.Series(dtype=float, index=vix_close.index)
    vix = vix_close.astype(float)
    # Paper: prior-month mean VIX. Use rolling(21).mean().shift(1) —
    # day t uses days [t-21, t-1] only (strict no-peek).
    ma = (
        vix.rolling(window=config.vix_ma_days, min_periods=config.vix_ma_days)
        .mean()
        .shift(1)
    )
    raw = config.vix_baseline / ma
    exposure = raw.clip(lower=config.exposure_floor, upper=config.exposure_cap)
    return exposure


def simulate_h2_bozovic_vix_scaling(
    spy_returns: pd.Series,
    shv_returns: pd.Series,
    vix_close: pd.Series,
    config: H2BozovicVixScalingConfig,
) -> H2BozovicVixScalingResult:
    """Run Božović VIX-scaled SPY/cash daily rebalance end-to-end.

    Parameters
    ----------
    spy_returns : pd.Series
        Daily SPY total-return (decimal). Must share its DatetimeIndex with
        ``shv_returns`` at the intersection or be reindex-compatible.
    shv_returns : pd.Series
        Daily SHV total-return (cash proxy, decimal). Pre-2007 the caller
        should synthesize this (e.g. constant 3%/yr daily = ~0.00012) or
        use T-bill series; NaN fills with 0.0 are handled defensively.
    vix_close : pd.Series
        VIXCLS daily close series.
    config : H2BozovicVixScalingConfig

    Returns
    -------
    H2BozovicVixScalingResult

    Raises
    ------
    ValueError
        If input series have empty/nonexistent overlap.

    Notes
    -----
    * The common trading index = intersection(spy_returns, shv_returns,
      vix_close). If any side has calendar drift, we inner-join.
    * Year-end tax is applied at the LAST trading day of each calendar
      year. If the cumulative year-to-date net return is positive, we
      deduct ``tax_rate × (YTD equity gain)`` from equity and record the
      event. If negative, no tax is levied and no loss is carried forward
      across years (conservative BR CG interpretation).
    * FX-on-rebalance (opt-in via ``apply_fx_on_rebalance=True``) charges
      ``fx_spread × |Δexposure|`` on each rebalance day.
    """
    if spy_returns.empty or shv_returns.empty or vix_close.empty:
        raise ValueError("spy_returns, shv_returns, vix_close must be non-empty")

    # Align to intersection.
    idx = (
        spy_returns.index.intersection(shv_returns.index).intersection(vix_close.index)
    )
    if len(idx) < config.vix_ma_days + 10:
        raise ValueError(
            f"insufficient overlap: {len(idx)} days < vix_ma_days + 10 = "
            f"{config.vix_ma_days + 10}"
        )
    idx = idx.sort_values()
    spy = spy_returns.reindex(idx).astype(float).fillna(0.0)
    shv = shv_returns.reindex(idx).astype(float).fillna(0.0)
    vix = vix_close.reindex(idx).astype(float)

    # Exposure signal (F2-patched: already uses shift(1) internally).
    exposure = compute_vix_exposure(vix, config)
    # During warmup (NaN exposure), hold 100% cash (no SPY).
    exposure_eff = exposure.fillna(0.0)

    # Optional rebalance threshold: if abs change < threshold, hold previous
    # effective exposure. This is a turnover knob (paper baseline = 0).
    if config.rebalance_threshold > 0:
        out = np.full(len(exposure_eff), np.nan)
        prev = 0.0
        for i, e in enumerate(exposure_eff.to_numpy()):
            if i == 0 or abs(e - prev) >= config.rebalance_threshold:
                prev = float(e)
            out[i] = prev
        exposure_eff = pd.Series(out, index=idx)

    # Weights matrix: SPY + SHV = 1 at all times.
    weights = pd.DataFrame(
        {
            "SPY": exposure_eff.values,
            "SHV": 1.0 - exposure_eff.values,
        },
        index=idx,
    )

    # F2-patched alignment — prev_weight × ret.
    prev_w = weights.shift(1).fillna(0.0)
    ret_df = pd.DataFrame({"SPY": spy, "SHV": shv}, index=idx)
    gross_ret = (prev_w * ret_df).sum(axis=1)

    # FX-on-rebalance drag (opt-in).
    weight_changes = (weights - weights.shift(1).fillna(0.0)).abs().sum(axis=1) / 2.0
    # /2 because a shift from (1, 0) to (0, 1) sums to |ΔSPY| + |ΔSHV| = 2 ·
    # |ΔSPY|. We want turnover as fraction of equity rebalanced ≈ |Δexposure|.
    rebal_flag = weight_changes > config.rebalance_threshold
    if config.apply_fx_on_rebalance and config.fx_spread > 0:
        fx_drag = weight_changes * config.fx_spread
    else:
        fx_drag = pd.Series(0.0, index=idx)

    net_ret_before_tax = gross_ret - fx_drag

    # Compound equity with year-end tax realization.
    equity = 1.0
    equity_curve: list[float] = []
    daily_net: list[float] = []
    tax_events: list[tuple[pd.Timestamp, float]] = []
    cum_tax = 0.0

    # Year-end detection: last trading day of each calendar year.
    year = idx.year
    is_year_end = np.zeros(len(idx), dtype=bool)
    for i in range(len(idx)):
        if i == len(idx) - 1 or year[i + 1] != year[i]:
            is_year_end[i] = True
    year_start_equity = 1.0

    for i, ts in enumerate(idx):
        r_gross = float(net_ret_before_tax.iloc[i])
        new_eq_pre_tax = equity * (1.0 + r_gross)

        tax_this_bar = 0.0
        if is_year_end[i] and config.tax_rate > 0:
            # YTD gain = new_eq_pre_tax - year_start_equity.
            ytd_gain = new_eq_pre_tax - year_start_equity
            if ytd_gain > 0:
                tax_this_bar = config.tax_rate * ytd_gain
                new_eq = new_eq_pre_tax - tax_this_bar
                cum_tax += tax_this_bar
                tax_events.append((pd.Timestamp(ts), tax_this_bar))
            else:
                new_eq = new_eq_pre_tax
            # Reset year-start anchor for next calendar year.
            year_start_equity = new_eq
        else:
            new_eq = new_eq_pre_tax

        # Net return attributed to this bar (post tax/costs, relative to
        # previous equity).
        if equity > 0:
            daily_net.append(new_eq / equity - 1.0)
        else:
            daily_net.append(0.0)
        equity = new_eq
        equity_curve.append(equity)

    equity_series = pd.Series(equity_curve, index=idx, name="equity")
    daily_net_series = pd.Series(daily_net, index=idx, name="daily_net_return")

    # Turnover: mean absolute daily exposure change (excluding first bar).
    delta_exp = exposure_eff.diff().abs().fillna(0.0)
    turnover = float(delta_exp.mean())

    return H2BozovicVixScalingResult(
        daily_returns=daily_net_series,
        gross_returns=gross_ret,
        exposure=exposure,
        weights=weights,
        equity=equity_series,
        tax_events=tax_events,
        cum_tax_pct=cum_tax,
        cum_fx_pct=float(fx_drag.sum()),
        n_rebalances=int(rebal_flag.sum()),
        turnover=turnover,
    )
