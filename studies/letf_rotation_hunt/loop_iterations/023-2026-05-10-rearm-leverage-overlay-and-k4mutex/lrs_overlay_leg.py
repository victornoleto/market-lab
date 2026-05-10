"""Iter 023 — LRS-during-rearm overlay helper (slots 5 + 6).

Phase 4 — iter 017 focused validation/refinement. Iter-local helper that
applies a multiplicative leverage scalar to on-leg returns ONLY on days
where the rearm gate is active (lagged 1 day, matching the
`build_single_asset_on_leg` shift convention).

Used by:
- Slot 5: rearm-only T40D60 base + LRS1.15× during rearm
- Slot 6: K4_AND_lv25 OR rearm T40D60 base + LRS1.15× during rearm

The same `apply_lrs_during_rearm_overlay` powers both; the slots differ
only in the upstream base upgrade gate composition.

Iter-local helper (`loop_iterations/023-.../`); does NOT modify shared
modules per LOOP_PROTOCOL §"Scope limits".

Citations
---------
- [leverage_for_the_long_run, ch.4-5, p.40-60]: PRIMARY LRS Husson-
  Trifoni leverage scaling in streak windows.
- [leverage_for_the_long_run, p.6-7, ch.3]: Husson-Trifoni MA-streak
  window onset (rearm primitive motivation).
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking (slot 6
  additive K4-base + LRS-overlay composition).
- [advances_fin_ml, p.208-211]: PBO via CSCV (mechanism-mix diversity).
"""
from __future__ import annotations

import pandas as pd


def apply_lrs_during_rearm_overlay(
    on_leg_returns: pd.Series,
    rearm_gate: pd.Series,
    lrs_factor: float,
) -> pd.Series:
    """Scale on-leg returns by lrs_factor on rearm-active days only.

    On days where rearm_gate (lagged 1 day) == 1: returns *= lrs_factor.
    On days where rearm_gate (lagged 1 day) == 0 (or NaN): returns *= 1.0.

    The lag matches iter 014's build_single_asset_on_leg shift convention:
    rearm gate computed on day t-1's information is applied at open of day t.

    For lrs_factor=1.0 this reduces to on_leg_returns unchanged
    (calibration anchor — must match slot 4 bit-exactly when LRS off).

    Parameters
    ----------
    on_leg_returns : pd.Series
        Daily on-leg returns from build_single_asset_on_leg (or basket3).
    rearm_gate : pd.Series
        0/1 daily series marking rearm window days (NaN = no information).
    lrs_factor : float
        Multiplicative leverage scalar. 1.0 = no overlay. >1.0 = boost.

    Returns
    -------
    pd.Series
        Aligned to on_leg_returns.index. Values: r_t * (1 + (lrs_factor-1) * rearm_lag).

    Notes
    -----
    Gross-return approximation: does NOT model the daily compounding-vol-drag
    asymmetry of a true synthetic LETF at the implied effective leverage
    (e.g., 1.15 × TQQQ daily ≈ effective ~3.45× of QQQ but misses
    rebalance-cost diverge). For modest scaling (<=1.30) over short windows
    (~60 trading days) this approximation is reasonable; documented for
    future refinement.
    """
    if lrs_factor == 1.0:
        return on_leg_returns

    rearm_lag = rearm_gate.shift(1).reindex(on_leg_returns.index).fillna(0.0)
    scaler = 1.0 + (lrs_factor - 1.0) * rearm_lag
    return on_leg_returns * scaler
