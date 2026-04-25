"""Iter 038 — Pure-numpy reference for VIX-regime-gated 3-leg stack.

Independent re-implementation of `apply_regime_lev_stack_3leg` used by
G7 cross-library parity (`[advances_fin_ml, p.31-34]`). Must NOT call
the pandas engine — different code path detects engine bugs.

Inputs are arrays already aligned on the return index, with the VIX
lag applied externally (so this reference depends only on integer
regime labels).
"""

from __future__ import annotations

import numpy as np


def apply_regime_lev_stack_3leg_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    r_gld: np.ndarray,
    regime: np.ndarray,
    *,
    lev_lo: float = 1.70,
    lev_hi: float = 1.00,
    lev_neutral: float | None = None,
    base_weights: tuple[float, float, float] = (0.60, 0.45, 0.45),
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Three-leg regime-gated static stack — pure numpy, no pandas.

    Parameters
    ----------
    r_eq, r_bd, r_gld : (n,) ndarrays
        Aligned daily simple-return streams.
    regime : (n,) ndarray of int
        1 = low-vol regime (apply lev_lo); 0 = high-vol (apply lev_hi).
        First-bar sentinel can be encoded as 1 (matching the pandas
        primitive's neutral-fill convention) since `lev_neutral` is
        applied via the explicit override path described below.
    lev_neutral : float, optional
        If provided, used at any bar where ``regime == -1`` (the pandas
        engine's first-bar sentinel). When omitted, defaults to the
        midpoint ``0.5*(lev_lo + lev_hi)``.

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

    if lev_neutral is None:
        lev_neutral = 0.5 * (lev_lo + lev_hi)

    base_sum = sum(base_weights)
    if base_sum <= 0:
        raise ValueError("sum(base_weights) must be > 0")

    lev_per_bar = np.empty(n, dtype=float)
    lev_per_bar[reg == 1] = lev_lo
    lev_per_bar[reg == 0] = lev_hi
    lev_per_bar[reg == -1] = lev_neutral
    weight_scale = lev_per_bar / base_sum

    eq_base, bd_base, gld_base = base_weights
    pos_eq = eq_base * weight_scale
    pos_bd = bd_base * weight_scale
    pos_gld = gld_base * weight_scale
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
