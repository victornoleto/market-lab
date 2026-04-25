"""Iter 070 — Pure-numpy reference for the continuous T10Y3M inner-weight blend.

Purpose
-------

G7 cross-library parity check (`[advances_fin_ml, p.31-34]`): an
independent numpy implementation that shares no code with the pandas
engine. Used in the gate battery to confirm CAGR difference stays under
3 pp (we expect well under 1e-12 per bar in practice).

Algorithm
---------

Same semantics as ``t10y3m_cont_inner_weight.combine_with_t10y3m_cont_inner_weight``
but written end-to-end in numpy. Caller must pre-align ``term_spread``
to the same index as ``r_046`` and ``r_qqqt`` and pre-fill any NaN.
"""

from __future__ import annotations

import numpy as np


def _rolling_mean_std_lookback(
    x: np.ndarray, lookback: int
) -> tuple[np.ndarray, np.ndarray]:
    """Rolling mean and std (ddof=0) over a closed [t-lookback+1, t] window.

    Returns NaN for bars where the window is incomplete (t < lookback - 1).
    Pure numpy via cumulative sums; matches pandas' ``Series.rolling().mean()``
    and ``Series.rolling().std(ddof=0)`` to within 1e-12.
    """
    n = len(x)
    out_mean = np.full(n, np.nan, dtype=float)
    out_std = np.full(n, np.nan, dtype=float)
    if n == 0 or lookback < 1:
        return out_mean, out_std
    # Cumulative sums — element [i] = sum of x[0..i] inclusive.
    csum = np.cumsum(x.astype(float))
    csumsq = np.cumsum(x.astype(float) ** 2)
    for t in range(lookback - 1, n):
        if t == lookback - 1:
            s = csum[t]
            ssq = csumsq[t]
        else:
            s = csum[t] - csum[t - lookback]
            ssq = csumsq[t] - csumsq[t - lookback]
        m = s / lookback
        var = max(ssq / lookback - m * m, 0.0)
        out_mean[t] = m
        out_std[t] = np.sqrt(var)
    return out_mean, out_std


def combine_with_t10y3m_cont_inner_weight_np(
    r_046: np.ndarray,
    r_qqqt: np.ndarray,
    term_spread_aligned: np.ndarray,
    *,
    w_min: float = 0.05,
    w_max: float = 0.20,
    alpha: float = 0.25,
    lookback_z: int = 1260,
    cost_bps: float = 5.0,
) -> np.ndarray:
    """Pure-numpy reference for continuous T10Y3M inner-weight blend.

    Inputs assumed to be already aligned arrays of equal length, with
    ``term_spread_aligned`` NaN-free (caller mirrors the pandas engine's
    ``ffill().bfill()``).
    """
    n = len(r_046)
    if n < 2:
        raise ValueError(f"inputs must have ≥ 2 bars; got {n}")
    if len(r_qqqt) != n or len(term_spread_aligned) != n:
        raise ValueError("input arrays must have equal length")

    a = r_046.astype(float)
    b = r_qqqt.astype(float)
    s = term_spread_aligned.astype(float)

    # Strict no-peek: shift(1) on the spread (bar 0's lag = bar 0 itself).
    s_lag = np.empty(n)
    s_lag[0] = s[0]
    s_lag[1:] = s[:-1]

    # Rolling mean/std on the LAGGED series (BOTH shift(1) — never see bar t).
    rmean, rstd = _rolling_mean_std_lookback(s_lag, lookback_z)

    # z = (s_lag - rmean) / rstd; warmup → z=0; rstd=0 → z=0.
    valid = (~np.isnan(rmean)) & (~np.isnan(rstd)) & (rstd > 0.0)
    z = np.zeros(n, dtype=float)
    safe_std = np.where(rstd > 0.0, rstd, 1.0)
    raw = (s_lag - rmean) / safe_std
    z = np.where(valid, raw, 0.0)
    z = np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0)

    f = np.clip(0.5 - alpha * z, 0.0, 1.0)
    w_qqqt = w_min + (w_max - w_min) * f
    w_qqqt = np.clip(w_qqqt, w_min, w_max)
    w_046 = 1.0 - w_qqqt

    w_qqqt_prev = np.empty(n)
    w_qqqt_prev[0] = w_qqqt[0]
    w_qqqt_prev[1:] = w_qqqt[:-1]
    delta_w = np.abs(w_qqqt - w_qqqt_prev)
    cost = (cost_bps * 1e-4) * delta_w

    out = w_046 * a + w_qqqt * b - cost
    return out
