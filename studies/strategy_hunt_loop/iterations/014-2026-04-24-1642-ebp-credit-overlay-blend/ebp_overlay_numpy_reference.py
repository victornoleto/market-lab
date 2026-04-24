"""Iter 014 — Numpy reference for cross-library parity (G7) on EBP overlay.

Hand-rolled numpy mirror of ``ebp_credit_overlay.apply_blend_with_credit_overlay``
and ``compute_ebp_zscore``. Used only by tests + G7 gate. See
`[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ITER006_DIR = Path(__file__).resolve().parents[1] / "006-2026-04-24-1027-vol-managed-60-40"
sys.path.insert(0, str(ITER006_DIR))
from numpy_reference import apply_blend_variance_target_np  # noqa: E402


def ebp_zscore_np(x: np.ndarray, *, window: int = 252) -> np.ndarray:
    """Rolling trailing-window z-score (sample mean/std, ddof=0).

    z[t] uses indices [t-window+1, t] inclusive. Bars without enough
    history are NaN.
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    z = np.full(n, np.nan)
    for t in range(window - 1, n):
        w = x[t - window + 1 : t + 1]
        # If any NaN in the window, leave NaN (pandas default behaviour).
        if np.isnan(w).any():
            continue
        mu = w.mean()
        sigma = w.std(ddof=0)
        if sigma <= 0:
            continue
        z[t] = (x[t] - mu) / sigma
    return z


def apply_blend_with_credit_overlay_np(
    r_spy: np.ndarray,
    r_tlt: np.ndarray,
    *,
    ebp_z: np.ndarray,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    threshold: float,
    haircut: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Pure-numpy blend + asymmetric EBP credit overlay.

    Returns (net, pos_spy_gated, pos_tlt_ungated, scale) — all dropped
    first ``lookback`` bars to match the pandas path.
    """
    _, pos_spy_base, pos_tlt_base, scale = apply_blend_variance_target_np(
        r_spy, r_tlt,
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=0.0,  # ungated costs; we'll re-compute below
    )
    # Align EBP-z to the blend's valid window: pandas path drops the first
    # ``lookback`` bars, so numpy path too. Use the same slice.
    ebp_z_arr = np.asarray(ebp_z, dtype=float)
    mask = ~(np.isnan(r_spy) | np.isnan(r_tlt))
    r_spy_f = np.asarray(r_spy, dtype=float)[mask]
    r_tlt_f = np.asarray(r_tlt, dtype=float)[mask]
    ebp_z_f = ebp_z_arr[mask]
    n = len(r_spy_f)
    # Blend drops first ``lookback`` bars → valid = [lookback, n)
    ebp_z_valid = ebp_z_f[lookback:n]
    r_spy_valid = r_spy_f[lookback:n]
    r_tlt_valid = r_tlt_f[lookback:n]

    gate = np.ones_like(ebp_z_valid)
    gate[~np.isnan(ebp_z_valid) & (ebp_z_valid >= threshold)] = haircut

    pos_spy_g = pos_spy_base * gate
    pos_tlt_g = pos_tlt_base  # unchanged

    gross = pos_spy_g * r_spy_valid + pos_tlt_g * r_tlt_valid

    dpos_spy = np.empty_like(pos_spy_g)
    dpos_tlt = np.empty_like(pos_tlt_g)
    dpos_spy[0] = abs(pos_spy_g[0])
    dpos_tlt[0] = abs(pos_tlt_g[0])
    dpos_spy[1:] = np.abs(np.diff(pos_spy_g))
    dpos_tlt[1:] = np.abs(np.diff(pos_tlt_g))
    cost = (dpos_spy + dpos_tlt) * cost_bps_per_leg
    net = gross - cost
    return net, pos_spy_g, pos_tlt_g, scale


__all__ = [
    "apply_blend_with_credit_overlay_np",
    "ebp_zscore_np",
]
