"""Iter 024 — Unconditional LRS overlay helper (slots 3 + 6).

Phase 4 — iter 017 focused validation/refinement. Iter-local helper that
applies a multiplicative leverage scalar to on-leg returns on EVERY ON day
(not gated to the rearm window). Distinct from iter 023's
`apply_lrs_during_rearm_overlay` which gated LRS application to the rearm
window only.

Mechanism: on `on_signal_t-1 = 1` (RISK_ON state, strategy holds the on-leg),
on-leg return is scaled by `lrs_factor`. On `on_signal_t-1 = 0` (RISK_OFF
state), no scaling is applied (the strategy holds the off-leg, which is not
touched by LRS — preserves Husson-Trifoni `[p.13]` "leverage only when above MA"
convention).

Used by:
- Slot 3: K4_AND_lv25 base + LRS1.05× unconditional during ON
- Slot 6: rearm-only T40D60 base + LRS1.05× unconditional during ON

Both slots share the same `apply_unconditional_lrs_overlay` mechanism; they
differ only in the upstream upgrade-gate composition (K4_AND_lv25 vs rearm-only).
This places the LRS axis on 2 distinct base mechanism families, decoupling LRS
from the rearm scaffolding that caused iter 023's G1 PBO 0.6548 blowup.

Iter-local helper (`runs/post_close/024-.../`); does NOT modify shared modules
per LOOP_PROTOCOL §"Scope limits".

Citations
---------
- [leverage_for_the_long_run, p.13, ch.3]: PRIMARY canonical LRS rule —
  RISK_ON: leveraged S&P 500 daily; RISK_OFF: T-bills.
- [leverage_for_the_long_run, ch.4-5, p.40-60]: Husson-Trifoni LRS leverage
  scaling at 1.25x/2x/3x — modest scaling preserves vol-drag-vs-expected-
  return positive expected value (1.05x sits well within sweet spot).
- [leverage_for_the_long_run, p.5-6]: ann vol < 40% sweet spot for leverage.
- [advances_fin_ml, p.208-211]: CSCV PBO mechanism-mix diversity (motivates
  decoupling LRS from rearm scaffolding).
"""
from __future__ import annotations

import pandas as pd


def apply_unconditional_lrs_overlay(
    on_leg_returns: pd.Series,
    on_signal: pd.Series,
    lrs_factor: float,
) -> pd.Series:
    """Scale on-leg returns by lrs_factor on every ON day (RISK_ON state).

    On days where on_signal (lagged 1 day) == 1: returns *= lrs_factor.
    On days where on_signal (lagged 1 day) == 0 (or NaN): returns *= 1.0.

    The lag matches iter 014's build_single_asset_on_leg shift convention:
    on_signal computed on day t-1's information is applied at open of day t.

    For lrs_factor=1.0 this reduces to on_leg_returns unchanged (calibration
    anchor — slot 3 must collapse to slot 2 bit-exactly when LRS off).

    Distinct from iter 023's apply_lrs_during_rearm_overlay (which gates LRS
    to rearm-window days only — ~9.7% of trading days). This helper applies
    LRS on every ON day (~70-80% of trading days), spreading the LRS effect
    temporally and structurally orthogonalizing it from the rearm scaffolding.

    Parameters
    ----------
    on_leg_returns : pd.Series
        Daily on-leg returns from build_single_asset_on_leg.
    on_signal : pd.Series
        0/1 daily series marking ON state (vote-K=2 entry signal).
    lrs_factor : float
        Multiplicative leverage scalar. 1.0 = no overlay. >1.0 = boost.
        Conservative midpoint between iter 023's 1.15x (PBO-blowup) and
        1.00x (no overlay) is 1.05x — within Husson-Trifoni vol-regime
        sweet spot (ann vol < 40%) on 2x QLD on-leg (effective 2.1x).

    Returns
    -------
    pd.Series
        Aligned to on_leg_returns.index. Values: r_t * (1 + (lrs_factor-1) * on_lag).

    Notes
    -----
    Gross-return approximation: does NOT model the daily compounding-vol-drag
    asymmetry of a true synthetic LETF at the implied effective leverage
    (e.g., 1.05 x QLD ≈ effective ~2.1x of QQQ; 1.05 x TQQQ ≈ effective
    ~3.15x of QQQ — both miss daily-rebalance-cost divergence). At 1.05x
    over multi-decade horizons this approximation is reasonable; documented
    for future refinement.
    """
    if lrs_factor == 1.0:
        return on_leg_returns

    on_lag = on_signal.shift(1).reindex(on_leg_returns.index).fillna(0.0)
    scaler = 1.0 + (lrs_factor - 1.0) * on_lag
    return on_leg_returns * scaler
