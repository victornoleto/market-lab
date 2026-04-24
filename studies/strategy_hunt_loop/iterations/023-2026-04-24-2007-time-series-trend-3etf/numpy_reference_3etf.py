"""Iter 023 — Hand-rolled numpy reference for G7 cross-lib parity.

Reproduces the pandas ``apply_trend_3etf`` semantics with a bar-by-bar
numpy loop. CAGR must agree with the pandas version to within 3 pp
(`[advances_fin_ml, p.31-34]`).

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity gate motivation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def trend_3etf_numpy(
    returns_arr: np.ndarray,
    *,
    index: pd.DatetimeIndex,
    signal_lookback: int = 252,
    signal_skip: int = 21,
    vol_lookback: int = 21,
    target_vol_per_asset: float = 0.10,
    max_leverage: float = 2.0,
    cost_bps_per_leg: float = 0.0002,
    periods_per_year: int = 252,
) -> np.ndarray:
    """Numpy-pure reference producing net returns aligned to the valid bars.

    Parameters
    ----------
    returns_arr : np.ndarray shape (T, 3)
        Simple daily returns for three assets.
    index : pd.DatetimeIndex
        Original index (used to derive the valid-bar slice consistent
        with the pandas version). Length must equal T.

    Returns
    -------
    np.ndarray shape (T - warmup,)
        Net daily returns aligned to the pandas valid-bar slice.
    """
    if returns_arr.ndim != 2 or returns_arr.shape[1] != 3:
        raise ValueError(
            f"returns_arr must be shape (T, 3); got {returns_arr.shape}"
        )
    T, K = returns_arr.shape
    if len(index) != T:
        raise ValueError(f"index length {len(index)} != T {T}")

    required = signal_lookback + signal_skip + 1
    if T <= required:
        raise ValueError(f"need > {required} bars; got {T}")

    # --- log returns + cumulative sum --------------------------------------
    log_r = np.log1p(returns_arr)

    # --- rolling std (annualised), shifted by 1 (σ̂_{t-1}) -----------------
    ann_sigma = np.full((T, K), np.nan, dtype=float)
    for t in range(vol_lookback, T):
        window = returns_arr[t - vol_lookback : t, :]  # bars [t-L, t-1]
        ann_sigma[t, :] = window.std(axis=0, ddof=0) * np.sqrt(periods_per_year)

    # --- trend feature = rolling sum of log_r over [t-L+1, t], shifted -----
    feature = np.full((T, K), np.nan, dtype=float)
    for t in range(signal_lookback - 1, T):
        window = log_r[t - signal_lookback + 1 : t + 1, :]
        feature[t, :] = window.sum(axis=0)
    # Shift by signal_skip: value at t is the feature computed at (t - skip).
    shifted_feature = np.full((T, K), np.nan, dtype=float)
    if signal_skip > 0:
        shifted_feature[signal_skip:, :] = feature[:-signal_skip, :]
    else:
        shifted_feature = feature.copy()

    # --- signal in {-1, 0, +1} --------------------------------------------
    # np.sign of NaN is NaN; safe.
    signals = np.sign(shifted_feature)

    # --- raw positions ----------------------------------------------------
    raw_pos = np.full((T, K), np.nan, dtype=float)
    for k in range(K):
        sigma_k = ann_sigma[:, k]
        sig_k = signals[:, k]
        # Avoid div-by-zero; where σ=0 leave raw_pos = NaN.
        with np.errstate(invalid="ignore", divide="ignore"):
            raw_pos[:, k] = np.where(
                (sigma_k > 0) & np.isfinite(sig_k),
                sig_k * target_vol_per_asset / sigma_k,
                np.nan,
            )

    # --- valid bars: rows where every leg is finite -----------------------
    valid_mask = np.all(np.isfinite(raw_pos), axis=1)
    valid_idx = np.where(valid_mask)[0]
    if len(valid_idx) == 0:
        raise ValueError("no valid bars after warmup")

    raw_pos_v = raw_pos[valid_idx, :]
    r_v = returns_arr[valid_idx, :]

    # --- leverage cap via proportional shrink -----------------------------
    gross_raw = np.abs(raw_pos_v).sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        shrink = np.where(gross_raw > 0.0, max_leverage / gross_raw, 1.0)
    shrink = np.minimum(shrink, 1.0)
    positions = raw_pos_v * shrink[:, None]

    # --- gross return + cost ---------------------------------------------
    gross_ret = (positions * r_v).sum(axis=1)
    # Δpos with initial bar treated as built from zero.
    dpos = np.diff(positions, axis=0, prepend=0.0)
    # The prepend=0.0 trick: np.diff prepends a row of zeros, so row 0 ends up
    # being positions[0] - 0 = positions[0]. That matches the pandas path
    # (fillna with |positions.iloc[0]|) in absolute value.
    cost = np.abs(dpos).sum(axis=1) * cost_bps_per_leg
    net = gross_ret - cost

    return net
