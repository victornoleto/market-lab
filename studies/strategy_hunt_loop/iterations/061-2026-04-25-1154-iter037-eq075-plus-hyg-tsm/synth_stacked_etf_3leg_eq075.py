"""Iter 061 — 3-leg static return-stack (vendored verbatim from iter 037).

Same `apply_static_stack_3leg` mechanism as iter 037; iter 061 calls
it with **equity-overweight weights 0.75 / 0.40 / 0.40** instead of
iter 037's canonical 0.60 / 0.45 / 0.45. Total notional 1.55× (vs
iter 037's 1.50×), preserving the AFP risk-parity / Hsiao-Williams
preserved-leverage zone.

The function itself is asset-agnostic and weight-agnostic; only the
caller's choice of weights distinguishes iter 061 from iter 037.

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 multi-leg
  risk-parity decomposition; equity-vs-diversifier weight trade-off
  governed by bond/gold weights.
* `[risk_parity, p.5, p.10-11, ch.1]` — AFP 2012 SSRN 1728082.
* `[leverage_for_the_long_run, p.19-20]` — Hsiao & Williams 2017,
  preserved-leverage zone (1.5-1.6× total) for diversified base.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (vacuous for
  static weights but enforced structurally).
"""

from __future__ import annotations

import pandas as pd


def apply_static_stack_3leg(
    r_eq: pd.Series,
    r_bd_short: pd.Series,
    r_bd_long: pd.Series,
    *,
    eq_w: float = 0.75,
    bd_short_w: float = 0.40,
    bd_long_w: float = 0.40,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series]:
    """Three-leg static return-stack with daily-rebalanced fixed weights.

    Parameters
    ----------
    r_eq, r_bd_short, r_bd_long : pd.Series
        Aligned daily simple-return streams. Must share identical
        DatetimeIndex.
    eq_w, bd_short_w, bd_long_w : float
        Per-leg fixed weights. Defaults to iter 061's equity-overweight
        choice **0.75 / 0.40 / 0.40** (total 1.55×).
    cost_bps_per_leg : float
        Linear cost per unit of per-leg position change. Default 2 bps
        (matches iter 015/033/034/035/036/037).

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
