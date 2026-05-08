"""Iter 015 — Pure-numpy hand-rolled reference for synthetic NTSX.

Independent re-implementation of `synth_stacked_etf.apply_static_stack`
used by G7 cross-library parity (`[advances_fin_ml, p.31-34]`). Must
NOT call into the pandas engine — the whole point is to detect engine
bugs by computing the same answer through a different code path.
"""

from __future__ import annotations

import numpy as np


def apply_static_stack_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    *,
    eq_w: float = 0.9,
    bd_w: float = 0.6,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Static return-stack — pure numpy, no pandas.

    Returns
    -------
    (net, positions, scale)
        ``net`` : (n,) array of net daily returns.
        ``positions`` : (n, 2) array, columns [EQ, BD].
        ``scale`` : (n,) array of total gross exposure.
    """
    a = np.asarray(r_eq, dtype=float)
    b = np.asarray(r_bd, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: eq={a.shape}, bd={b.shape}")
    n = a.shape[0]
    if n == 0:
        raise ValueError("empty input arrays")

    pos_eq = np.full(n, eq_w, dtype=float)
    pos_bd = np.full(n, bd_w, dtype=float)
    scale = pos_eq + pos_bd

    gross = pos_eq * a + pos_bd * b

    # |∆pos| with t=0 baseline at zero (initial setup cost).
    dpos_eq = np.empty(n, dtype=float)
    dpos_bd = np.empty(n, dtype=float)
    dpos_eq[0] = pos_eq[0]
    dpos_bd[0] = pos_bd[0]
    if n > 1:
        dpos_eq[1:] = np.abs(np.diff(pos_eq))
        dpos_bd[1:] = np.abs(np.diff(pos_bd))
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg

    net = gross - cost

    positions = np.column_stack([pos_eq, pos_bd])
    return net, positions, scale


def cagr_np(net: np.ndarray, periods_per_year: int = 252) -> float:
    """Compute CAGR from a net-returns array (compounded growth)."""
    eq = np.cumprod(1.0 + np.asarray(net, dtype=float))
    n = len(eq)
    if n == 0:
        return 0.0
    final = float(eq[-1])
    if final <= 0:
        return -1.0
    return final ** (periods_per_year / n) - 1.0
