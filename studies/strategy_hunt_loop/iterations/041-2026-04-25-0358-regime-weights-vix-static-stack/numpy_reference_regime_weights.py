"""Iter 041 — Pure-numpy reference for regime-weighted 3-leg stack.

Independent re-implementation of `apply_regime_weights_3leg` for G7
cross-library parity (`[advances_fin_ml, p.31-34]`). Must NOT call the
pandas engine — different code path detects engine bugs.

Inputs are arrays already aligned on the return index, with the VIX
lag applied externally (so this reference depends only on integer
regime labels).
"""

from __future__ import annotations

from typing import Mapping

import numpy as np


def apply_regime_weights_3leg_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    r_gld: np.ndarray,
    regime: np.ndarray,
    *,
    calm_weights: Mapping[str, float],
    stress_weights: Mapping[str, float],
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Three-leg regime-weighted static stack — pure numpy, no pandas.

    Parameters
    ----------
    r_eq, r_bd, r_gld : (n,) ndarrays
        Aligned daily simple-return streams.
    regime : (n,) ndarray of int
        1 = calm regime (calm_weights apply); 0 = stress (stress_weights).
    calm_weights, stress_weights : mapping with keys "eq_w", "bd_w",
        "gld_w".
    cost_bps_per_leg : float
        Linear cost per unit per-leg ∆position.

    Returns
    -------
    (net, positions, scale)
        ``net`` : (n,) net returns.
        ``positions`` : (n, 3) array, columns [EQ, BD, GLD].
        ``scale`` : (n,) total gross exposure.
    """
    a = np.asarray(r_eq, dtype=float)
    b = np.asarray(r_bd, dtype=float)
    c = np.asarray(r_gld, dtype=float)
    reg = np.asarray(regime, dtype=int)
    if not (a.shape == b.shape == c.shape == reg.shape):
        raise ValueError(
            f"shape mismatch: eq={a.shape}, bd={b.shape}, gld={c.shape}, regime={reg.shape}"
        )
    n = a.shape[0]
    if n == 0:
        raise ValueError("empty input arrays")

    cw = (calm_weights["eq_w"], calm_weights["bd_w"], calm_weights["gld_w"])
    sw = (stress_weights["eq_w"], stress_weights["bd_w"], stress_weights["gld_w"])
    for w in (*cw, *sw):
        if w < 0:
            raise ValueError(f"weights must be non-negative; got {w}")

    pos_eq = np.where(reg == 1, cw[0], sw[0]).astype(float)
    pos_bd = np.where(reg == 1, cw[1], sw[1]).astype(float)
    pos_gld = np.where(reg == 1, cw[2], sw[2]).astype(float)
    scale = pos_eq + pos_bd + pos_gld

    gross = pos_eq * a + pos_bd * b + pos_gld * c

    dpos_eq = np.empty(n, dtype=float)
    dpos_bd = np.empty(n, dtype=float)
    dpos_gld = np.empty(n, dtype=float)
    dpos_eq[0] = pos_eq[0]
    dpos_bd[0] = pos_bd[0]
    dpos_gld[0] = pos_gld[0]
    if n > 1:
        dpos_eq[1:] = np.abs(np.diff(pos_eq))
        dpos_bd[1:] = np.abs(np.diff(pos_bd))
        dpos_gld[1:] = np.abs(np.diff(pos_gld))
    cost = (dpos_eq + dpos_bd + dpos_gld) * cost_bps_per_leg

    net = gross - cost
    positions = np.column_stack([pos_eq, pos_bd, pos_gld])
    return net, positions, scale


def cagr_np(net: np.ndarray, periods_per_year: int = 252) -> float:
    eq = np.cumprod(1.0 + np.asarray(net, dtype=float))
    n = len(eq)
    if n == 0:
        return 0.0
    final = float(eq[-1])
    if final <= 0:
        return -1.0
    return final ** (periods_per_year / n) - 1.0
