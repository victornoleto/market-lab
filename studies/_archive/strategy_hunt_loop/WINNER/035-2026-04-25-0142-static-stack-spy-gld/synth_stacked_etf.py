"""Iter 015 — Synthetic NTSX (90/60 SPY+IEF stack) static return-stacking.

Mechanism (deliberately the simplest possible primitive):

    pos_eq[t] = eq_w   (constant)
    pos_bd[t] = bd_w   (constant)
    scale[t]  = eq_w + bd_w == 1.5  (constant; not vol-managed)

    gross[t] = pos_eq · r_eq[t] + pos_bd · r_bd[t]
    cost[t]  = (|∆pos_eq[t]| + |∆pos_bd[t]|) · cost_bps_per_leg
              ≈ 0 except at t=0 (initial setup)
    net[t]   = gross[t] − cost[t]

Funding cost (futures-stacking implicit borrow on the 50% additional
notional) is NOT modeled. The synthetic version overestimates the real
NTSX product's return by ~50-100 bps annually depending on rate regime.
The final report's sensitivity section quantifies this.

Citations
---------
* `[risk_parity, p.5, p.10-11, ch.1]` — Asness-Frazzini-Pedersen (2012)
  risk-parity argument: lever a diversified base for higher Sharpe per
  unit of total risk.
* `[leverage_for_the_long_run, p.19-20]` — leverage on a diversified
  base captures duration risk-premium without market-timing.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (vacuous for
  static weights but enforced structurally by the constant-weight design).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_static_stack(
    r_eq: pd.Series,
    r_bd: pd.Series,
    *,
    eq_w: float = 0.9,
    bd_w: float = 0.6,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series]:
    """Two-leg static return-stack with daily-rebalanced fixed weights.

    Parameters
    ----------
    r_eq, r_bd : pd.Series
        Aligned daily simple-return streams for equity and bond legs.
        Must share the same DatetimeIndex.
    eq_w, bd_w : float
        Per-leg fixed weights. Defaults: 0.9 / 0.6 (NTSX prospectus).
    cost_bps_per_leg : float
        Linear cost per unit of per-leg position change. Default 2 bps.

    Returns
    -------
    (net_returns, positions_df, scale)
        ``net_returns`` : pd.Series of net daily returns (after cost).
        ``positions_df`` : pd.DataFrame with columns ["EQ", "BD"].
        ``scale`` : pd.Series of total gross exposure (constant eq_w+bd_w).

    Raises
    ------
    ValueError
        If indices are not strictly equal.
    """
    if eq_w < 0 or bd_w < 0:
        raise ValueError(f"weights must be non-negative; got eq={eq_w} bd={bd_w}")
    if not r_eq.index.equals(r_bd.index):
        raise ValueError(
            "r_eq and r_bd must share identical indices "
            f"(eq has {len(r_eq)} bars, bd has {len(r_bd)} bars)"
        )

    a = r_eq.astype(float)
    b = r_bd.astype(float)
    mask = a.notna() & b.notna()
    a = a.loc[mask]
    b = b.loc[mask]
    if len(a) == 0:
        raise ValueError("no overlapping non-NaN bars between r_eq and r_bd")

    idx = a.index
    pos_eq = pd.Series(eq_w, index=idx, dtype=float)
    pos_bd = pd.Series(bd_w, index=idx, dtype=float)
    scale = pos_eq + pos_bd
    scale.name = "scale"

    gross = pos_eq * a + pos_bd * b

    # Cost: |∆pos| × bps × 2 legs. With static weights, ∆ = 0 for t > 0.
    # The t=0 bar's ∆ is measured against zero (initial setup).
    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_bd = pos_bd.diff().abs().fillna(pos_bd.iloc[0])
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg

    net = (gross - cost).astype(float)
    net.name = "net"

    positions = pd.DataFrame({"EQ": pos_eq, "BD": pos_bd}, index=idx)
    return net, positions, scale
