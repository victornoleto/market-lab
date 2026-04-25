"""Iter 068 — Pure-numpy reference for the VIX-conditional inner-weight blend.

Purpose
-------

G7 cross-library parity check (`[advances_fin_ml, p.31-34]`): an
independent numpy implementation that shares NO code with the pandas
engine. Used in the gate battery to confirm that any difference in
CAGR between engines stays under 3 pp.

Algorithm
---------

Same as ``vix_inner_weight.combine_with_vix_inner_weight``, but
written end-to-end in numpy. VIX alignment is the caller's
responsibility (must be pre-aligned to the same index as r_046 and
r_qqqt, with NaN already filled).
"""

from __future__ import annotations

import numpy as np


def combine_with_vix_inner_weight_np(
    r_046: np.ndarray,
    r_qqqt: np.ndarray,
    vix_aligned: np.ndarray,
    *,
    w_qqqt_calm: float = 0.20,
    w_qqqt_stress: float = 0.05,
    vix_threshold: float = 20.0,
    cost_bps: float = 5.0,
) -> np.ndarray:
    """Pure-numpy reference for VIX-conditional inner-weight blend.

    Inputs assumed to be ALREADY ALIGNED arrays of equal length. VIX
    NaNs assumed pre-filled (the pandas engine does ffill().bfill();
    the caller of this reference must mirror that).
    """
    n = len(r_046)
    if n < 2:
        raise ValueError(f"inputs must have ≥ 2 bars; got {n}")
    if len(r_qqqt) != n or len(vix_aligned) != n:
        raise ValueError("input arrays must have equal length")

    a = r_046.astype(float)
    b = r_qqqt.astype(float)
    v = vix_aligned.astype(float)

    # No-lookahead: shift(1) — bar 0 lag is bfilled to bar 0 itself.
    v_lag = np.empty(n)
    v_lag[0] = v[0]
    v_lag[1:] = v[:-1]

    is_stress = (v_lag >= vix_threshold)
    w_qqqt = np.where(is_stress, w_qqqt_stress, w_qqqt_calm).astype(float)
    w_046 = 1.0 - w_qqqt

    w_qqqt_prev = np.empty(n)
    w_qqqt_prev[0] = w_qqqt[0]
    w_qqqt_prev[1:] = w_qqqt[:-1]
    delta_w = np.abs(w_qqqt - w_qqqt_prev)
    cost = (cost_bps * 1e-4) * delta_w

    out = w_046 * a + w_qqqt * b - cost
    return out
