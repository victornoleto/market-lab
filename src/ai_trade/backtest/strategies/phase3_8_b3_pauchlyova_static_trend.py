"""Phase 3.8 B3 — Pauchlyova 2025 static+trend multi-asset allocation (rota B Inter).

Implements a **diversified static base allocation with per-component
trend overlay**, as described in Pauchlyova / Quantpedia 2025 "Leveraged
ETFs in Asset Allocation: Opportunity or Trap?" (`docs/research/
2026-04-23-phase3.7-literature-sprint.md §T1, paper 3`). This is a
fundamentally different paradigm from B1/B2 (on/off SMA regime): instead
of binary exposure to a single leveraged leg, we hold a 5-asset
portfolio always, but each component is flipped to cash (SHV) whenever
its own price falls below its own SMA-200. Monthly rebalance restores
the base allocation subject to the active trend overlays.

Thesis (literal Pauchlyova 2025 + Gayed anchor)
-----------------------------------------------

* ``[phase3_7_literature_sprint, §T1 paper 3]`` — "20% LETF equity + 40%
  bonds + 20% normal equity + 10% gold + 10% cash, trend-filtered per
  leg, maintains comparable volatility with BETTER returns and
  controlled drawdown" (Pauchlyova 2025). Simulation period 1926-2025
  in the Quantpedia article (with synthetic 2x before LETFs existed).
  We restrict our honest window to the post-GLD (2004-11-18) era
  because the Pauchlyova portfolio is **multi-asset** and the weakest
  component (GLD) governs the IS start. See "Data caveats" below.
* ``[leverage_for_the_long_run, p.7-8, p.11]`` — Gayed's SMA is a
  volatility-regime signal, not a price trend. Pauchlyova's overlay
  applies the same logic per-component: each component's price-above-SMA
  is used as a vol-regime filter, moving that leg to cash when its own
  regime turns hostile.
* ``[advances_fin_ml, p.31-34]`` — F2-alignment ``prev_weight × ret``
  for all 5 legs. The trend signal for bar ``t`` uses only data
  through ``t-1`` (strict shift).
* ``docs/investment-mandate.md §4.6`` — rota B Inter cost model
  (DARF 15% year-end on net realized gain, conservative no-loss-carry).

Base allocation (Pauchlyova Quantpedia table)
---------------------------------------------

    LETF (UPRO or SSO):  20%
    TLT                  40%
    SPY                  20%
    GLD                  10%
    SHV                  10%
    ───────────────────────
    Total                100%

**Trend overlay** — for each "risk" component ``c ∈ {LETF, TLT, SPY,
GLD}``::

    sma200_c_{t-1}  = SMA(c_close, 200).shift(1)
    if c_close_{t-1} < sma200_c_{t-1}:
        redirect c's weight → SHV (until trend reverts)

SHV itself is always 100% cash; no trend filter on SHV.

**Rebalance cadence:** monthly (first trading day of each month).
Between rebal days, weights drift with component returns (pure
buy-and-hold within the month). A trend flip detected on day ``t``
applies the overlay at bar ``t`` via the same shift-1 convention —
we DO NOT wait for the next monthly rebal to act on a flip. The only
intra-month action is moving the flipping component's current weight
to SHV (or restoring it if the trend reverts).

Signal look-ahead audit
-----------------------

For each trading day ``t``:

* ``close_{t-1}`` and ``SMA(200)_{t-1}`` for **every** component are
  the inputs to ``overlay_t`` — ``regime_c_t = (close_c > SMA_c).shift(1)``.
  Nothing from ``t`` influences the weight we carry into bar ``t``.
* Monthly rebal snapshots the base allocation on the first trading day
  of each month; weights applied on that day are built from
  ``signal_{t-1}`` (same shift convention).
* Daily portfolio return at ``t`` is ``Σ_i prev_w_i_t × r_i_t`` —
  standard F2 alignment. The ``prev_weights`` are what we carried from
  ``t-1`` after any trend flips or monthly rebals up to ``t``.
* Year-end DARF realization uses only equity through the year-end day
  — no next-year information.
* LETF synth uses FFR at ``t`` (public at open) — same convention as B1.

Citations sweep
---------------

* Base allocation + trend overlay:
  ``[phase3_7_literature_sprint, §T1 paper 3]`` (Pauchlyova 2025 Quantpedia).
* Gayed SMA-200 canonical trend filter:
  ``[leverage_for_the_long_run, p.13-17, p.16]``.
* F2 alignment:
  ``[advances_fin_ml, p.31-34]``.
* Rota B Inter cost model (DARF 15% year-end):
  ``docs/investment-mandate.md §4.6``.
* PBO/DSR:
  ``[advances_fin_ml, p.208-211, p.275]``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal, Mapping

import numpy as np
import pandas as pd

# Import year-end DARF helper + inception dates from B1 (reuse mandate).
from ai_trade.backtest.strategies.phase3_8_b1_gayed_canonical import (
    SSO_REAL_START,
    UPRO_REAL_START,
    apply_darf_year_end,
)

log = logging.getLogger(__name__)

__all__ = [
    "B3Config",
    "B3Result",
    "BASE_ALLOCATION_UPRO",
    "BASE_ALLOCATION_SSO",
    "DEFAULT_TREND_COMPONENTS",
    "compute_per_component_trend",
    "simulate_b3",
]


LETFKind = Literal["UPRO", "SSO"]
RebalCadence = Literal["monthly", "quarterly"]

#: Base allocation using UPRO-3x as the LETF sleeve.
BASE_ALLOCATION_UPRO: Mapping[str, float] = {
    "LETF": 0.20,  # UPRO (3x SPX)
    "TLT": 0.40,
    "SPY": 0.20,
    "GLD": 0.10,
    "SHV": 0.10,
}

#: Base allocation using SSO-2x as the LETF sleeve.
BASE_ALLOCATION_SSO: Mapping[str, float] = {
    "LETF": 0.20,  # SSO (2x SPX)
    "TLT": 0.40,
    "SPY": 0.20,
    "GLD": 0.10,
    "SHV": 0.10,
}

#: Components that receive a trend filter. SHV (cash) does not.
DEFAULT_TREND_COMPONENTS: tuple[str, ...] = ("LETF", "TLT", "SPY", "GLD")


@dataclass(frozen=True)
class B3Config:
    """Immutable config for one B3 run.

    Parameters
    ----------
    letf_kind : {"UPRO", "SSO"}
        Which real LETF fills the 20% LETF sleeve. Synth is used pre-
        inception of the real ETF (``UPRO_REAL_START`` or
        ``SSO_REAL_START``) when the data overlap permits — our honest
        window restriction starts at 2004-11-18 (GLD inception), which
        is pre-UPRO (2009-06-25) but post-SSO (2006-06-21). For UPRO we
        stitch synth → real at 2009-06-25; for SSO post-2006 we use
        real throughout.
    sma_period : int
        Trend filter lookback. **Always 200** (Gayed canonical, not
        swept — B3 is about the multi-asset paradigm, not MA grid).
    trend_filter_on : bool
        If True, apply per-component trend overlay. If False, run the
        static Pauchlyova base allocation straight (used as the PBO-
        grid ablation — pure-static is a distinct design cell).
    rebal_cadence : {"monthly", "quarterly"}
        Rebalance frequency. Monthly is the Pauchlyova default
        (~12 rebals/yr + trend flips = ~12-15/yr total).
    trend_components : tuple[str, ...]
        Which base components receive the trend filter. Always
        ``DEFAULT_TREND_COMPONENTS`` in canonical runs; exposed for
        testability. Must be a subset of the base allocation keys and
        must NOT include ``"SHV"``.
    base_allocation : Mapping[str, float]
        Static base weights. Defaults to ``BASE_ALLOCATION_UPRO`` when
        ``letf_kind="UPRO"`` (resolved in ``__post_init__`` if None).
    expense_ratio_letf : float
        Annualized LETF ER for the synth pre-inception leg. 0.0095 per
        Gayed footnote 23.
    cash_rate_annual : float
        Flat annualized cash rate proxy for SHV pre-2007-01-11 (where
        SHV data begins). 0.04 by default (mandate §4.6 long-run 3-mo
        T-bill proxy — same convention as B1).
    commission_bps : float
        Per-rebalance-turnover commission in bps. Inter zero (0.0).
    spread_bps : float
        Per-rebalance-turnover half-spread in bps (each unit of
        turnover costs this much; round-trip cost = 2×spread_bps).
        5 bps default — matches B1.
    tax_rate : float
        Year-end DARF on net realized gain. 0.15 (rota B). 0.0 to
        disable.
    """

    letf_kind: LETFKind = "UPRO"
    sma_period: int = 200
    trend_filter_on: bool = True
    rebal_cadence: RebalCadence = "monthly"
    trend_components: tuple[str, ...] = DEFAULT_TREND_COMPONENTS
    base_allocation: Mapping[str, float] | None = None
    expense_ratio_letf: float = 0.0095
    cash_rate_annual: float = 0.04
    commission_bps: float = 0.0
    spread_bps: float = 5.0
    tax_rate: float = 0.15

    def __post_init__(self) -> None:
        if self.letf_kind not in ("UPRO", "SSO"):
            raise ValueError(
                f"letf_kind must be UPRO or SSO, got {self.letf_kind!r}"
            )
        if self.sma_period <= 1:
            raise ValueError(f"sma_period must be > 1, got {self.sma_period}")
        if self.rebal_cadence not in ("monthly", "quarterly"):
            raise ValueError(
                f"rebal_cadence must be monthly or quarterly, got "
                f"{self.rebal_cadence!r}"
            )
        # Default base allocation based on letf_kind.
        if self.base_allocation is None:
            default = (
                BASE_ALLOCATION_UPRO
                if self.letf_kind == "UPRO"
                else BASE_ALLOCATION_SSO
            )
            # Use object.__setattr__ to bypass frozen.
            object.__setattr__(self, "base_allocation", default)
        # Validate base allocation.
        total = float(sum(self.base_allocation.values()))
        if not 0.999 <= total <= 1.001:
            raise ValueError(
                f"base_allocation must sum to 1.0, got {total:.6f}: "
                f"{dict(self.base_allocation)}"
            )
        if "SHV" not in self.base_allocation:
            raise ValueError("base_allocation must include SHV sleeve")
        # Validate trend components.
        bad = [c for c in self.trend_components if c not in self.base_allocation]
        if bad:
            raise ValueError(
                f"trend_components {bad} not in base_allocation keys "
                f"{list(self.base_allocation.keys())}"
            )
        if "SHV" in self.trend_components:
            raise ValueError("SHV cannot have trend filter (it IS cash)")

    @property
    def real_letf_start(self) -> pd.Timestamp:
        """Inception of the real LETF being used for the 20% sleeve."""
        return UPRO_REAL_START if self.letf_kind == "UPRO" else SSO_REAL_START

    @property
    def leverage(self) -> float:
        """Leverage of the LETF sleeve (3x UPRO, 2x SSO)."""
        return 3.0 if self.letf_kind == "UPRO" else 2.0


@dataclass
class B3Result:
    """Output of :func:`simulate_b3`."""

    equity: pd.Series  # post-tax daily equity, starting at 1.0
    daily_returns: pd.Series  # net-of-tax daily pct_change
    weights: pd.DataFrame  # cols = components, rows = trading days
    regime: pd.DataFrame  # per-component 0/1 trend flag (t-1 shifted)
    rebalance_dates: pd.DatetimeIndex
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

    def cagr(self, periods_per_year: int = 252) -> float:
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


def compute_per_component_trend(
    prices: pd.DataFrame,
    sma_period: int = 200,
) -> pd.DataFrame:
    """Per-component trend signal, **t-1 shifted** (F2-alignment).

    For each column ``c`` in ``prices``, returns a 0/1 integer series
    where ``1`` iff ``close_c_{t-1} > SMA(n)_c_{t-1}`` — i.e. the
    component is in a friendly trend regime going into bar ``t``.

    Parameters
    ----------
    prices : pd.DataFrame
        Daily price DataFrame with one column per component (close or
        adj_close). Index must be a DatetimeIndex sorted asc.
    sma_period : int
        Moving average lookback. 200 for Gayed canonical.

    Returns
    -------
    pd.DataFrame
        Same shape/index as ``prices``; 0/1 int per cell.
    """
    if sma_period <= 1:
        raise ValueError(f"sma_period must be > 1, got {sma_period}")
    px = prices.astype(float)
    sma = px.rolling(window=sma_period, min_periods=sma_period).mean()
    raw = (px > sma).astype(float)
    return raw.shift(1).fillna(0.0).astype(int)


def _rebal_day_mask(
    index: pd.DatetimeIndex, cadence: RebalCadence
) -> np.ndarray:
    """Boolean mask: True on the first trading day of each month/quarter.

    Monthly: first trading day of every calendar month.
    Quarterly: first trading day of every calendar quarter.
    """
    n = len(index)
    if n == 0:
        return np.zeros(0, dtype=bool)
    out = np.zeros(n, dtype=bool)
    if cadence == "monthly":
        out[0] = True
        for i in range(1, n):
            if (
                index[i].year != index[i - 1].year
                or index[i].month != index[i - 1].month
            ):
                out[i] = True
    elif cadence == "quarterly":
        out[0] = True
        for i in range(1, n):
            prev = index[i - 1]
            cur = index[i]
            prev_q = (prev.month - 1) // 3
            cur_q = (cur.month - 1) // 3
            if cur.year != prev.year or cur_q != prev_q:
                out[i] = True
    else:
        raise ValueError(f"unknown cadence: {cadence!r}")
    return out


def simulate_b3(
    returns: pd.DataFrame,
    prices: pd.DataFrame,
    config: B3Config,
) -> B3Result:
    """Run one B3 canonical config end-to-end.

    Pipeline
    --------

    1. Compute per-component trend signal ``regime`` (t-1 shifted).
    2. Build ``target_w_t`` at each bar: start from ``base_allocation``,
       and for each ``c ∈ trend_components`` with ``regime_c_t == 0``,
       move ``base_allocation[c]`` to ``SHV``. If
       ``config.trend_filter_on=False``, skip this step (static base).
    3. Held weights:
       * On rebal days: ``held_t = target_w_t``.
       * Otherwise: ``held_t = drift(held_{t-1}, r_{t-1})`` EXCEPT for
         trend-triggered flips — if any component's regime changed
         today, we re-execute the target on that bar too (treat as
         mini-rebal for consistency with the spec's "intra-month rebal
         only for the flipping component" rule).
    4. Daily portfolio return:
       ``r_p_t = Σ_i held_w_i_t × r_i_t − turnover_t × cost_bps/2``
       where ``turnover_t = Σ_i |target - prior_held|`` only on rebal /
       flip days.
    5. Apply year-end DARF on the compounded gross → post-tax equity
       via :func:`apply_darf_year_end` (reused from B1).

    Parameters
    ----------
    returns : pd.DataFrame
        Daily simple returns per component. Columns must be a superset
        of ``config.base_allocation.keys()``. All NaNs must be filled
        (by caller — typically 0 for missing warm-up bars).
    prices : pd.DataFrame
        Daily close/adj_close per component. Same columns as
        ``returns``. Index must share ``returns.index``.
    config : B3Config

    Returns
    -------
    B3Result

    Raises
    ------
    ValueError
        If the two inputs are not index-aligned or do not contain all
        required components.
    """
    components = list(config.base_allocation.keys())
    missing_r = [c for c in components if c not in returns.columns]
    missing_p = [c for c in components if c not in prices.columns]
    if missing_r:
        raise ValueError(f"returns missing components: {missing_r}")
    if missing_p:
        raise ValueError(f"prices missing components: {missing_p}")
    if not returns.index.equals(prices.index):
        raise ValueError("returns and prices must share index")

    rets = returns[components].astype(float).copy()
    pxs = prices[components].astype(float).copy()
    idx = rets.index
    n = len(idx)

    # Per-component trend signal (0/1), t-1 shifted. SHV gets a signal
    # too but we ignore it (SHV has no trend filter). Components that
    # are not in config.trend_components get a constant 1 (always on).
    if config.trend_filter_on:
        trend_pxs_full = compute_per_component_trend(
            pxs[list(config.trend_components)], sma_period=config.sma_period
        )
    # Build a full regime DataFrame with 1s for non-trend-filtered legs.
    regime = pd.DataFrame(1, index=idx, columns=components, dtype=int)
    if config.trend_filter_on:
        for c in config.trend_components:
            regime[c] = trend_pxs_full[c].astype(int)
    # SHV is always "on" (always cash). No override needed; default is 1.

    base = np.array(
        [float(config.base_allocation[c]) for c in components], dtype=float
    )
    shv_idx = components.index("SHV")

    rebal_mask = _rebal_day_mask(idx, config.rebal_cadence)

    # Pre-compute the target weights per bar: start from base, and for
    # each OFF-regime component redirect its weight to SHV.
    regime_arr = regime[components].to_numpy()
    target = np.zeros((n, len(components)), dtype=float)
    for t in range(n):
        w = base.copy()
        if config.trend_filter_on:
            off_mass = 0.0
            for i, c in enumerate(components):
                if c in config.trend_components and regime_arr[t, i] == 0:
                    off_mass += w[i]
                    w[i] = 0.0
            w[shv_idx] += off_mass
        target[t] = w

    # Flip detection — row ``t`` flips when target_t != target_{t-1}.
    flip_mask = np.zeros(n, dtype=bool)
    if n > 0:
        flip_mask[0] = True
        for t in range(1, n):
            if not np.allclose(target[t], target[t - 1], atol=1e-12):
                flip_mask[t] = True

    act_mask = rebal_mask | flip_mask  # days where held → target

    rets_arr = rets.to_numpy(dtype=float, copy=False)
    np.nan_to_num(rets_arr, copy=False)  # ensure no NaN leaking into pnl

    held = np.zeros((n, len(components)), dtype=float)
    gross = np.zeros(n, dtype=float)
    turnover_cost = np.zeros(n, dtype=float)

    prev_w = np.zeros(len(components), dtype=float)
    cost_bps = config.commission_bps + config.spread_bps  # per unit turnover
    cost_frac = cost_bps / 10_000.0
    rebal_dates_actual: list[pd.Timestamp] = []

    for t in range(n):
        if act_mask[t]:
            new_w = target[t]
            # Turnover = sum |Δw|; cost absorbed on this bar.
            delta = float(np.abs(new_w - prev_w).sum())
            turnover_cost[t] = delta * cost_frac
            held[t] = new_w
            rebal_dates_actual.append(idx[t])
        else:
            # Drift: held_t = prev_w * (1 + r_t); renormalize is NOT
            # done — weights drift naturally. But for portfolio return
            # calc we use prev_w * r_t (F2) then update w.
            held[t] = prev_w

        # Portfolio return — F2: prev_w × r_t (we treat held[t] AS the
        # weight carried INTO bar t, so prev_w above is held[t]).
        pnl = float(np.dot(held[t], rets_arr[t]))
        gross[t] = pnl - turnover_cost[t]

        # Update prev_w with post-return drift (for next bar). If we
        # rebalanced/flipped today, held[t] is the new target. Drift
        # under single-day return: new_w' = w*(1+r) / Σ(w*(1+r))
        # (but unnormalized drift keeps the economically-correct
        # exposure — we choose to NOT renormalize, mirroring B1's
        # exposure semantics).
        drifted = held[t] * (1.0 + rets_arr[t])
        prev_w = drifted

    cum_cost = float(turnover_cost.sum())

    gross_series = pd.Series(gross, index=idx, name="daily_b3_gross")
    equity, daily_net, cum_tax = apply_darf_year_end(
        gross_series, tax_rate=config.tax_rate
    )

    weights_df = pd.DataFrame(held, index=idx, columns=components)

    return B3Result(
        equity=equity,
        daily_returns=daily_net,
        weights=weights_df,
        regime=regime,
        rebalance_dates=pd.DatetimeIndex(rebal_dates_actual),
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
