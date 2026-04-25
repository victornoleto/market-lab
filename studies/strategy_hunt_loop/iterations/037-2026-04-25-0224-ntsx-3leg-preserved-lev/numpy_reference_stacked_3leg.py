"""Iter 034 — Pure-numpy hand-rolled reference for 3-leg static stack.

Independent re-implementation of `apply_static_stack_3leg` used by G7
cross-library parity (`[advances_fin_ml, p.31-34]`). Must NOT call into
the pandas engine — the whole point is to detect engine bugs by
computing the same answer through a different code path.
"""

from __future__ import annotations

import numpy as np


def apply_static_stack_3leg_np(
    r_eq: np.ndarray,
    r_bd_short: np.ndarray,
    r_bd_long: np.ndarray,
    *,
    eq_w: float = 0.9,
    bd_short_w: float = 0.4,
    bd_long_w: float = 0.2,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """3-leg static return-stack — pure numpy, no pandas.

    Returns
    -------
    (net, positions, scale)
        ``net`` : (n,) array of net daily returns.
        ``positions`` : (n, 3) array, columns [EQ, BD_S, BD_L].
        ``scale`` : (n,) array of total gross exposure.
    """
    a = np.asarray(r_eq, dtype=float)
    b = np.asarray(r_bd_short, dtype=float)
    c = np.asarray(r_bd_long, dtype=float)
    if not (a.shape == b.shape == c.shape):
        raise ValueError(f"shape mismatch: eq={a.shape}, bd_s={b.shape}, bd_l={c.shape}")
    n = a.shape[0]
    if n == 0:
        raise ValueError("empty input arrays")

    pos_eq = np.full(n, eq_w, dtype=float)
    pos_s = np.full(n, bd_short_w, dtype=float)
    pos_l = np.full(n, bd_long_w, dtype=float)
    scale = pos_eq + pos_s + pos_l

    gross = pos_eq * a + pos_s * b + pos_l * c

    # |∆pos| with t=0 baseline at zero (initial setup cost).
    dpos_eq = np.empty(n, dtype=float)
    dpos_s = np.empty(n, dtype=float)
    dpos_l = np.empty(n, dtype=float)
    dpos_eq[0] = pos_eq[0]
    dpos_s[0] = pos_s[0]
    dpos_l[0] = pos_l[0]
    if n > 1:
        dpos_eq[1:] = np.abs(np.diff(pos_eq))
        dpos_s[1:] = np.abs(np.diff(pos_s))
        dpos_l[1:] = np.abs(np.diff(pos_l))
    cost = (dpos_eq + dpos_s + dpos_l) * cost_bps_per_leg

    net = gross - cost

    positions = np.column_stack([pos_eq, pos_s, pos_l])
    return net, positions, scale


def cagr_np(net: np.ndarray, periods_per_year: int = 252) -> float:
    """Compute CAGR from a net-returns array (compounded growth).

    Identical to iter 015's helper — duplicated here to keep the iter 034
    G7 reference truly self-contained.
    """
    eq = np.cumprod(1.0 + np.asarray(net, dtype=float))
    n = len(eq)
    if n == 0:
        return 0.0
    final = float(eq[-1])
    if final <= 0:
        return -1.0
    return final ** (periods_per_year / n) - 1.0
