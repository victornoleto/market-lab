"""Iter 067 — pure-numpy reference for σ⁻² variance-target overlay (G7).

Mirrors `variance_target_overlay.apply_variance_target_overlay` using
only numpy primitives. Used by the cross-library parity test `[advances_fin_ml,
p.31-34]`.

For input length N and lookback L, the output arrays have length N - L
(one bar dropped from rolling, one from shift(1) — but pandas with
shift(1) has length N − L since the shift just moves NaNs forward and
they get dropped together with the rolling NaNs at the head).

Strict definition:

    valid bars: indices L, L+1, ..., N-1 in the source (size N - L).
    σ̂²[t] = var(r[t-L : t]) × periods_per_year   for t in [L, N).
    scale[t] = clip(σ_target² / σ̂²[t], 0, cap)
    Δscale[L] = scale[L]      (build-up cost on first valid bar)
    Δscale[t] = |scale[t] - scale[t-1]| for t > L
    cost[t] = Δscale[t] × cost_bps × 1e-4
    net[t] = scale[t] × r[t] - cost[t]

Note pandas `.shift(1)` gives σ̂[t-1] usable at bar t. The pandas
implementation uses `.shift(1)` so the rolling window ENDING at t-1
indexes scale[t]. Equivalently, in numpy, we use the rolling window
ending at t-1 (i.e., indices t-L .. t-1) for scale[t].

So actually scale[t] uses var(r[t-L : t-1+1]) = var(r[t-L : t]).
And first valid t with a complete window (and prior σ̂) is t = L
(window r[0..L-1] of size L).

Hence the FIRST valid bar in numpy aligned to pandas-with-shift(1) is
t = L (the bar AFTER the first L-bar window).
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def apply_variance_target_overlay_np(
    r: np.ndarray,
    *,
    sigma_target: Optional[float],
    lookback: int,
    cap: float,
    cost_bps: float,
    periods_per_year: int = 252,
) -> tuple[np.ndarray, np.ndarray]:
    """Pure-numpy reference. Returns (net, scale), both length len(r) - lookback."""
    if sigma_target is not None and sigma_target < 0:
        raise ValueError(f"sigma_target must be ≥ 0, got {sigma_target}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if cap <= 0:
        raise ValueError(f"cap must be > 0, got {cap}")
    if cost_bps < 0:
        raise ValueError(f"cost_bps must be ≥ 0, got {cost_bps}")
    n = len(r)
    if n <= lookback:
        raise ValueError(f"need > {lookback} bars, got {n}")

    r_arr = np.asarray(r, dtype=float)

    if sigma_target is None:
        sigma_target = float(np.std(r_arr, ddof=0)) * float(np.sqrt(periods_per_year))

    target_var = sigma_target * sigma_target

    # Output indices: t = lookback, lookback+1, ..., n-1   (size n - lookback).
    # σ̂²[t] uses r[t-lookback : t]  (window ending at t-1, size lookback).
    out_len = n - lookback
    sigma2 = np.empty(out_len, dtype=float)
    for i in range(out_len):
        t = i + lookback
        window = r_arr[t - lookback : t]
        sigma2[i] = float(np.var(window, ddof=0)) * float(periods_per_year)

    scale = np.empty(out_len, dtype=float)
    for i in range(out_len):
        if sigma2[i] > 0:
            s = target_var / sigma2[i]
        else:
            s = cap  # σ̂² = 0 ⇒ saturate
        scale[i] = max(0.0, min(cap, s))

    r_valid = r_arr[lookback:]  # aligned with scale (length out_len)

    delta = np.empty(out_len, dtype=float)
    delta[0] = scale[0]
    for i in range(1, out_len):
        delta[i] = abs(scale[i] - scale[i - 1])
    cost = delta * (cost_bps * 1e-4)

    net = scale * r_valid - cost

    return net, scale
