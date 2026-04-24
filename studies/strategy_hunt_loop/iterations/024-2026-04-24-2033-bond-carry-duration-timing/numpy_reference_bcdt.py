"""Iter 024 — numpy-pure reference for bond-carry duration timing (G7 cross-lib).

Re-implements ``apply_bond_carry_duration_timing`` in raw numpy with
explicit Python-loop logic where pandas would vectorise. Goal is to
verify that the pandas engine and the numpy reference produce the
same equity curve to ≤ 3 pp CAGR per the AFML p.31-34 cross-lib
parity discipline.

Inputs are aligned numpy arrays; the caller is responsible for
having performed the inner-join + drop-NaN step that the pandas
engine does internally.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import numpy as np


def apply_bond_carry_duration_timing_np(
    r_eq: np.ndarray,
    r_tlt: np.ndarray,
    r_shv: np.ndarray,
    signal: np.ndarray,
    *,
    eq_w: float,
    bd_w: float,
    smoothing_days: int,
    lag_bars: int,
    ramp_max_bps: float,
    rebalance_bars: int,
    cost_bps_per_leg: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Numpy-pure reimplementation of ``apply_bond_carry_duration_timing``.

    All input arrays must have the same length and be NaN-free in the
    return columns. The signal column may contain NaNs only inside the
    smoothing warm-up region.

    Returns
    -------
    (net, positions, scale, alloc_tlt)
        positions : (N, 3) array with columns [EQ, TLT, SHV]
        scale : (N,) constant eq_w + bd_w
        alloc_tlt : (N,) bond-leg TLT fraction in [0, 1]
        Bars in the warm-up region (NaN alloc) are EXCLUDED from the
        returned arrays — same behaviour as the pandas engine.
    """
    if not (len(r_eq) == len(r_tlt) == len(r_shv) == len(signal)):
        raise ValueError(
            f"input length mismatch: eq={len(r_eq)} tlt={len(r_tlt)} "
            f"shv={len(r_shv)} sig={len(signal)}"
        )
    n = len(r_eq)

    # Convert signal from percent to bps and apply rolling SMA + lag.
    bps = signal.astype(float) * 100.0
    smoothed = np.full(n, np.nan)
    for t in range(smoothing_days - 1, n):
        window = bps[t - smoothing_days + 1: t + 1]
        if not np.any(np.isnan(window)):
            smoothed[t] = window.mean()

    lagged = np.full(n, np.nan)
    if lag_bars >= n:
        # Trivially all-NaN.
        return (
            np.array([], dtype=float),
            np.zeros((0, 3), dtype=float),
            np.array([], dtype=float),
            np.array([], dtype=float),
        )
    lagged[lag_bars:] = smoothed[: n - lag_bars]

    # Ramp.
    alloc_raw = np.clip(lagged / ramp_max_bps, 0.0, 1.0)

    # Drop warm-up NaNs.
    keep = ~np.isnan(alloc_raw)
    if not keep.any():
        return (
            np.array([], dtype=float),
            np.zeros((0, 3), dtype=float),
            np.array([], dtype=float),
            np.array([], dtype=float),
        )
    eq = r_eq[keep].astype(float)
    tlt = r_tlt[keep].astype(float)
    shv = r_shv[keep].astype(float)
    alloc = alloc_raw[keep]
    m = len(eq)

    # Monthly rebalance: hold alloc constant in chunks of rebalance_bars.
    held = np.empty(m, dtype=float)
    k = 0
    while k < m:
        end = min(k + rebalance_bars, m)
        held[k:end] = alloc[k]
        k = end

    pos_eq = np.full(m, eq_w, dtype=float)
    pos_tlt = bd_w * held
    pos_shv = bd_w * (1.0 - held)

    gross = pos_eq * eq + pos_tlt * tlt + pos_shv * shv

    dpos_eq = np.abs(np.diff(pos_eq, prepend=0.0))
    dpos_tlt = np.abs(np.diff(pos_tlt, prepend=0.0))
    dpos_shv = np.abs(np.diff(pos_shv, prepend=0.0))
    cost = (dpos_eq + dpos_tlt + dpos_shv) * cost_bps_per_leg

    net = gross - cost
    positions = np.column_stack([pos_eq, pos_tlt, pos_shv])
    scale = pos_eq + pos_tlt + pos_shv  # constant eq_w + bd_w
    return net, positions, scale, held
