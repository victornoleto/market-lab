"""Iter 063 — Pure-numpy reference implementations for G7 parity check.

Provides numpy mirrors of:

1. ``synth_letf_returns_np`` — synth UPRO formula r = leverage·r_spy −
   expense/252 (vendored from iter 062's numpy reference).
2. ``apply_regime_weights_3leg_np`` — iter 041's regime-weighted
   3-leg static stack with prior-bar VIX gate, no-cost-on-bar-0
   convention (vendored from iter 041's numpy reference).
3. ``combine_two_streams_np`` — convex combination of two streams.
4. ``combine_three_streams_np`` — nested convex combination
   (0.90 · (0.5·A + 0.5·B) + 0.10·C) used for the iter 063 composite.

The numpy reference operates on raw numpy arrays aligned beforehand.
The caller is responsible for inner-joining indexes; this module
verifies parity given the same aligned inputs.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
"""

from __future__ import annotations

import numpy as np


def synth_letf_returns_np(
    r_spy: np.ndarray,
    *,
    leverage: float = 3.0,
    expense_ratio: float = 0.0091,
) -> np.ndarray:
    """Numpy mirror of ``synth_upro_returns`` from iter 062."""
    r_spy = np.asarray(r_spy, dtype=float)
    daily_expense = expense_ratio / 252.0
    return leverage * r_spy - daily_expense


def apply_regime_weights_3leg_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    r_gld: np.ndarray,
    vix: np.ndarray,
    *,
    calm_weights: dict[str, float],
    stress_weights: dict[str, float],
    vix_threshold: float = 20.0,
    cost_bps_per_leg: float = 0.0002,
) -> np.ndarray:
    """Numpy mirror of ``apply_regime_weights_3leg``.

    Assumes inputs are already aligned (same length, same time order).
    VIX[0] is reused for the "previous-bar" lookup at index 0 (matches
    pandas implementation's `vix_lag.iloc[0] = vix_aligned.iloc[0]`).
    """
    r_eq = np.asarray(r_eq, dtype=float)
    r_bd = np.asarray(r_bd, dtype=float)
    r_gld = np.asarray(r_gld, dtype=float)
    vix = np.asarray(vix, dtype=float)
    n = len(r_eq)
    if not (len(r_bd) == n and len(r_gld) == n and len(vix) == n):
        raise ValueError(
            f"length mismatch: eq={n}, bd={len(r_bd)}, gld={len(r_gld)}, "
            f"vix={len(vix)}"
        )

    vix_lag = np.empty(n, dtype=float)
    vix_lag[0] = vix[0]
    vix_lag[1:] = vix[:-1]
    regime = (vix_lag < vix_threshold).astype(int)

    pos_eq = np.where(regime == 1, calm_weights["eq_w"], stress_weights["eq_w"])
    pos_bd = np.where(regime == 1, calm_weights["bd_w"], stress_weights["bd_w"])
    pos_gld = np.where(regime == 1, calm_weights["gld_w"], stress_weights["gld_w"])

    gross = pos_eq * r_eq + pos_bd * r_bd + pos_gld * r_gld

    dpos_eq = np.empty(n)
    dpos_bd = np.empty(n)
    dpos_gld = np.empty(n)
    dpos_eq[0] = pos_eq[0]
    dpos_bd[0] = pos_bd[0]
    dpos_gld[0] = pos_gld[0]
    dpos_eq[1:] = np.abs(np.diff(pos_eq))
    dpos_bd[1:] = np.abs(np.diff(pos_bd))
    dpos_gld[1:] = np.abs(np.diff(pos_gld))
    cost = (dpos_eq + dpos_bd + dpos_gld) * cost_bps_per_leg

    return gross - cost


def combine_two_streams_np(
    a: np.ndarray, b: np.ndarray, *, w_a: float, w_b: float,
) -> np.ndarray:
    """Convex combo of two pre-aligned numpy arrays."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) != len(b):
        raise ValueError(f"length mismatch: a={len(a)}, b={len(b)}")
    return w_a * a + w_b * b


def combine_three_streams_np(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    *,
    w_a: float,
    w_b: float,
    w_outer_ab: float,
    w_outer_c: float,
) -> np.ndarray:
    """Nested convex combo: outer * (w_a·a + w_b·b) + outer_c·c.

    Used by iter 063 for:
        iter_058_letf = 0.90 · (0.5·iter_041_letf + 0.5·iter_039)
                      + 0.10 · HYG_TSM
    """
    inner = combine_two_streams_np(a, b, w_a=w_a, w_b=w_b)
    if len(inner) != len(c):
        raise ValueError(
            f"length mismatch: inner={len(inner)}, c={len(c)}"
        )
    return w_outer_ab * inner + w_outer_c * np.asarray(c, dtype=float)
