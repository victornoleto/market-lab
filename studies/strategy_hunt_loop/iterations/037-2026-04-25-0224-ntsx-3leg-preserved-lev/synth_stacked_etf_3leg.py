"""Iter 034 — 3-leg static return-stack with bond-carry sleeve.

Generalisation of iter 015's `apply_static_stack` to support a third
leg (long-duration bond) at preserved total bond notional.

Mechanism::

    pos_eq[t]       = eq_w
    pos_bd_short[t] = bd_short_w   (e.g., 0.4 IEF)
    pos_bd_long[t]  = bd_long_w    (e.g., 0.2 TLT)

    bond_notional   = bd_short_w + bd_long_w   (e.g., 0.6, matches iter 015)
    total_leverage  = eq_w + bd_short_w + bd_long_w   (e.g., 1.5)

    gross[t] = pos_eq * r_eq + pos_bd_short * r_bd_short + pos_bd_long * r_bd_long
    cost[t]  = (|∆pos_eq| + |∆pos_bd_short| + |∆pos_bd_long|) * cost_bps_per_leg
    net[t]   = gross[t] − cost[t]

When ``bd_long_w == 0`` the function reduces exactly to iter 015's
two-leg case (verified by `test_3leg_stack_returns_match_2leg_when_alpha_zero`).

The "carry sleeve" framing — `bd_long_w` of TLT replaces an equal
notional of IEF inside the bond sleeve — is algebraically identical to
adding a zero-net-notional spread `bd_long_w · (r_TLT − r_IEF)` on top
of iter 015's portfolio. The function does not enforce a particular
short/long ticker pairing; it just stacks three return streams at fixed
weights.

Citations
---------
* `[risk_parity, ch.5]` — bond term-premium decomposition for the
  diversifying leg of a levered stack; choice of duration determines
  how much term premium the levered base harvests.
* `[risk_parity, p.5, p.10-11, ch.1]` — Asness-Frazzini-Pedersen (2012)
  risk-parity argument (preserved from iter 015).
* `[leverage_for_the_long_run, p.19-20]` — leverage on a diversified
  base captures duration risk-premium without market-timing.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (vacuous for
  static weights but enforced structurally by the constant-weight design).
* Koijen-Moskowitz-Pedersen-Vrugt (2018), JFE 127(2) — cross-sectional
  bond carry premium; spread (TLT − IEF) is the natural
  zero-net-notional way to harvest term-premium curvature.
"""

from __future__ import annotations

import pandas as pd


def apply_static_stack_3leg(
    r_eq: pd.Series,
    r_bd_short: pd.Series,
    r_bd_long: pd.Series,
    *,
    eq_w: float = 0.9,
    bd_short_w: float = 0.4,
    bd_long_w: float = 0.2,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series]:
    """Three-leg static return-stack with daily-rebalanced fixed weights.

    Parameters
    ----------
    r_eq, r_bd_short, r_bd_long : pd.Series
        Aligned daily simple-return streams. Must share identical
        DatetimeIndex.
    eq_w, bd_short_w, bd_long_w : float
        Per-leg fixed weights. Defaults: 0.9 / 0.4 / 0.2 (iter 034).
        ``bd_long_w == 0`` reduces to iter 015's 2-leg case.
    cost_bps_per_leg : float
        Linear cost per unit of per-leg position change. Default 2 bps.

    Returns
    -------
    (net_returns, positions_df, scale)
        ``net_returns`` : pd.Series of net daily returns (after cost).
        ``positions_df`` : pd.DataFrame with columns ["EQ", "BD_S", "BD_L"].
        ``scale`` : pd.Series of total gross exposure (sum of weights).

    Raises
    ------
    ValueError
        If indices are not strictly equal or any weight is negative.
    """
    if eq_w < 0 or bd_short_w < 0 or bd_long_w < 0:
        raise ValueError(
            f"weights must be non-negative; got eq={eq_w} bd_s={bd_short_w} bd_l={bd_long_w}"
        )
    if not (r_eq.index.equals(r_bd_short.index) and r_eq.index.equals(r_bd_long.index)):
        raise ValueError(
            "r_eq, r_bd_short, r_bd_long must share identical indices "
            f"(eq={len(r_eq)}, bd_s={len(r_bd_short)}, bd_l={len(r_bd_long)})"
        )

    a = r_eq.astype(float)
    b = r_bd_short.astype(float)
    c = r_bd_long.astype(float)
    mask = a.notna() & b.notna() & c.notna()
    a = a.loc[mask]
    b = b.loc[mask]
    c = c.loc[mask]
    if len(a) == 0:
        raise ValueError("no overlapping non-NaN bars across the three return streams")

    idx = a.index
    pos_eq = pd.Series(eq_w, index=idx, dtype=float)
    pos_bd_s = pd.Series(bd_short_w, index=idx, dtype=float)
    pos_bd_l = pd.Series(bd_long_w, index=idx, dtype=float)
    scale = pos_eq + pos_bd_s + pos_bd_l
    scale.name = "scale"

    gross = pos_eq * a + pos_bd_s * b + pos_bd_l * c

    # Cost: |∆pos| × bps per leg. With static weights, ∆ = 0 for t > 0.
    # The t=0 bar's ∆ is measured against zero (initial setup).
    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_s = pos_bd_s.diff().abs().fillna(pos_bd_s.iloc[0])
    dpos_l = pos_bd_l.diff().abs().fillna(pos_bd_l.iloc[0])
    cost = (dpos_eq + dpos_s + dpos_l) * cost_bps_per_leg

    net = (gross - cost).astype(float)
    net.name = "net"

    positions = pd.DataFrame(
        {"EQ": pos_eq, "BD_S": pos_bd_s, "BD_L": pos_bd_l}, index=idx,
    )
    return net, positions, scale
