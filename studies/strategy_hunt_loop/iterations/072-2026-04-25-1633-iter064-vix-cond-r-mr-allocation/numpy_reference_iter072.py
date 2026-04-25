"""Iter 072 — Pure-numpy reference for the regime-conditional 3-leg combiner.

Purpose
-------

G7 cross-library parity check (`[advances_fin_ml, p.31-34]`): an
independent numpy implementation that shares NO code with the pandas
engine. Caller is responsible for pre-aligning all 4 input arrays
(r_046, r_qqqt, r_mr, VIX) to identical length, with VIX NaN already
filled (the pandas engine does ffill().bfill()).

Algorithm
---------

Same as ``regime_conditional_3leg.combine_regime_cond_3leg``, but
written end-to-end in numpy. No pandas index ops; aligned inputs only.
"""

from __future__ import annotations

import numpy as np


def combine_regime_cond_3leg_np(
    r_046: np.ndarray,
    r_qqqt: np.ndarray,
    r_mr: np.ndarray,
    vix_aligned: np.ndarray,
    *,
    w_mr_calm: float,
    w_mr_stress: float,
    vix_threshold: float = 20.0,
    cost_bps: float = 5.0,
) -> np.ndarray:
    """Pure-numpy reference for the iter 072 regime-conditional 3-leg combiner.

    Inputs assumed to be ALREADY ALIGNED arrays of equal length. VIX
    NaNs assumed pre-filled (the pandas engine does ffill().bfill();
    callers of this reference must mirror that).
    """
    n = len(r_046)
    if n < 2:
        raise ValueError(f"inputs must have ≥ 2 bars; got {n}")
    if len(r_qqqt) != n or len(r_mr) != n or len(vix_aligned) != n:
        raise ValueError("input arrays must have equal length")

    a = r_046.astype(float)
    b = r_qqqt.astype(float)
    c = r_mr.astype(float)
    v = vix_aligned.astype(float)

    # No-lookahead shift(1); bar 0 lag is bfilled to bar 0 itself.
    v_lag = np.empty(n)
    v_lag[0] = v[0]
    v_lag[1:] = v[:-1]

    is_stress = (v_lag >= vix_threshold)
    w_mr = np.where(is_stress, w_mr_stress, w_mr_calm).astype(float)
    w_base = 1.0 - w_mr
    w_046 = w_base * 0.90
    w_qqqt = w_base * 0.10

    w_mr_prev = np.empty(n)
    w_mr_prev[0] = w_mr[0]
    w_mr_prev[1:] = w_mr[:-1]
    delta_w_mr = np.abs(w_mr - w_mr_prev)
    cost = (cost_bps * 1e-4) * delta_w_mr

    out = w_046 * a + w_qqqt * b + w_mr * c - cost
    return out
