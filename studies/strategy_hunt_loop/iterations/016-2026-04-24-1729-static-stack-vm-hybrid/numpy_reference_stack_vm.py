"""Iter 016 — Hand-rolled numpy reference for cross-library parity (G7).

Independent re-implementation of ``apply_static_stack_vol_managed`` in
pure numpy (no pandas). Required by gate G7: the two implementations
must agree to ≤ 3 pp CAGR (typically ≤ 1e-10 absolute on returns).

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import numpy as np


def _rolling_var_np(x: np.ndarray, window: int) -> np.ndarray:
    """Rolling population (ddof=0) variance. NaN for bars < window."""
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    if n < window:
        return out
    for i in range(window - 1, n):
        w = x[i - window + 1 : i + 1]
        out[i] = float(np.var(w, ddof=0))
    return out


def _rolling_cov_np(x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
    """Rolling population (ddof=0) covariance. NaN for bars < window."""
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    if n < window:
        return out
    for i in range(window - 1, n):
        xw = x[i - window + 1 : i + 1]
        yw = y[i - window + 1 : i + 1]
        out[i] = float(
            np.mean((xw - xw.mean()) * (yw - yw.mean()))
        )
    return out


def apply_static_stack_vm_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Numpy-pure re-implementation of ``apply_static_stack_vol_managed``.

    Inputs and outputs are numpy arrays (shape (N,)). The returned arrays
    are ALIGNED on the full input grid — the first ``lookback + 1`` bars
    have NaN (because σ̂²_{t-1} needs one prior bar beyond the lookback
    window). The pandas version drops these; callers can compare with
    ``np.testing.assert_allclose(pd.dropna().values, np_arr[~np.isnan(np_arr)])``
    or mask by the finite-scale mask.

    This version purposely uses the same shape convention as the pandas
    version's ``.dropna()`` output — i.e., returns arrays truncated to
    bars where scale is valid. See test in ``tests/test_static_stack_vm.py``.
    """
    if eq_weight < 0 or bd_weight < 0:
        raise ValueError("weights must be non-negative")
    total_w = eq_weight + bd_weight
    if total_w <= 0:
        raise ValueError("eq+bd weights must sum to > 0")
    if target_vol <= 0:
        raise ValueError("target_vol must be > 0")
    if lookback < 2:
        raise ValueError("lookback must be ≥ 2")
    if max_leverage <= 0:
        raise ValueError("max_leverage must be > 0")

    n = len(r_eq)
    if len(r_bd) != n:
        raise ValueError("r_eq and r_bd must have the same length")

    w_eq = eq_weight / total_w
    w_bd = bd_weight / total_w

    # Rolling variances / covariance at each bar t, using returns [t-lookback+1 .. t].
    var_eq = _rolling_var_np(r_eq, lookback) * periods_per_year
    var_bd = _rolling_var_np(r_bd, lookback) * periods_per_year
    cov = _rolling_cov_np(r_eq, r_bd, lookback) * periods_per_year

    # Shift by 1 bar to get σ̂²_{t-1}.
    shifted_var_eq = np.empty(n, dtype=float)
    shifted_var_bd = np.empty(n, dtype=float)
    shifted_cov = np.empty(n, dtype=float)
    shifted_var_eq[0] = np.nan
    shifted_var_bd[0] = np.nan
    shifted_cov[0] = np.nan
    shifted_var_eq[1:] = var_eq[:-1]
    shifted_var_bd[1:] = var_bd[:-1]
    shifted_cov[1:] = cov[:-1]

    ann_var_port = (
        w_eq ** 2 * shifted_var_eq
        + w_bd ** 2 * shifted_var_bd
        + 2.0 * w_eq * w_bd * shifted_cov
    )
    # Guard against fp negatives.
    ann_var_port = np.where(ann_var_port < 0, 0.0, ann_var_port)

    target_var = target_vol ** 2
    scale_full = np.full(n, np.nan, dtype=float)
    mask_valid = ~np.isnan(ann_var_port)
    pos_mask = mask_valid & (ann_var_port > 0)
    zero_mask = mask_valid & (ann_var_port == 0)
    scale_full[pos_mask] = target_var / ann_var_port[pos_mask]
    scale_full[zero_mask] = max_leverage
    scale_full = np.clip(scale_full, 0.0, max_leverage)

    # Drop NaN-lead (first lookback bars).
    keep = ~np.isnan(scale_full)
    idx_keep = np.where(keep)[0]
    scale = scale_full[idx_keep]
    pos_eq = w_eq * scale
    pos_bd = w_bd * scale

    r_eq_v = r_eq[idx_keep]
    r_bd_v = r_bd[idx_keep]
    gross = pos_eq * r_eq_v + pos_bd * r_bd_v

    # dpos with first-bar diff vs zero (matches pandas .diff().fillna(first))
    dpos_eq = np.empty_like(pos_eq)
    dpos_bd = np.empty_like(pos_bd)
    dpos_eq[0] = pos_eq[0]
    dpos_bd[0] = pos_bd[0]
    dpos_eq[1:] = np.abs(np.diff(pos_eq))
    dpos_bd[1:] = np.abs(np.diff(pos_bd))
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg

    net = gross - cost
    return net, pos_eq, pos_bd, scale
