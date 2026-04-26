"""Iter 077 — pure-numpy reference for long-short MTUM/VLUE sleeve (G7 parity).

Hand-rolled implementation that does NOT use pandas. Used to verify
the cross-library parity discipline `[advances_fin_ml, p.31-34]`:
the main pandas implementation must agree with this reference within
±3 pp CAGR (and within 1e-9 element-wise on toy tests).
"""

from __future__ import annotations

import numpy as np

ANNUALIZATION = 252


def _rolling_std_ddof1(arr: np.ndarray, window: int) -> np.ndarray:
    """NaN-safe rolling std (ddof=1, matches pandas default)."""
    out = np.full_like(arr, np.nan, dtype=float)
    n = len(arr)
    if n < window:
        return out
    for i in range(window - 1, n):
        out[i] = np.std(arr[i - window + 1:i + 1], ddof=1)
    return out


def compute_sleeve_returns_np(
    prices_mtum: np.ndarray,
    prices_vlue: np.ndarray,
    *,
    vol_lookback: int = 21,
    target_vol: float = 0.10,
    leg_cap: float = 1.0,
    short_borrow_rate: float = 0.01,
    trans_cost_bps: float = 5.0,
) -> np.ndarray:
    if len(prices_mtum) != len(prices_vlue):
        raise ValueError("prices_mtum and prices_vlue must have same length")
    if leg_cap < 0:
        raise ValueError(f"leg_cap must be >= 0; got {leg_cap}")
    mtum = np.asarray(prices_mtum, dtype=float)
    vlue = np.asarray(prices_vlue, dtype=float)
    n = len(mtum)
    ret_mtum = np.zeros(n)
    ret_vlue = np.zeros(n)
    ret_mtum[1:] = mtum[1:] / mtum[:-1] - 1.0
    ret_vlue[1:] = vlue[1:] / vlue[:-1] - 1.0
    spread = ret_mtum - ret_vlue

    vol_daily = _rolling_std_ddof1(spread, vol_lookback)
    vol_ann = vol_daily * np.sqrt(ANNUALIZATION)
    vol_ann_lag = np.zeros(n)
    vol_ann_lag[1:] = vol_ann[:-1]

    size = np.zeros(n)
    valid = (vol_ann_lag > 0) & np.isfinite(vol_ann_lag)
    size[valid] = target_vol / vol_ann_lag[valid]
    pos = np.minimum(np.maximum(size, 0.0), leg_cap)
    pos = np.nan_to_num(pos, nan=0.0, posinf=0.0, neginf=0.0)

    daily_borrow = pos * (short_borrow_rate / ANNUALIZATION)
    pos_diff = np.zeros(n)
    pos_diff[1:] = np.abs(pos[1:] - pos[:-1])
    pos_diff[0] = abs(pos[0])
    cost = pos_diff * (trans_cost_bps / 10000.0)

    sleeve = pos * spread - daily_borrow - cost
    return np.nan_to_num(sleeve, nan=0.0, posinf=0.0, neginf=0.0)


def combine_iter064_with_sleeve_np(
    r_064: np.ndarray,
    r_sleeve: np.ndarray,
    *,
    w_064: float,
    w_sleeve: float,
) -> np.ndarray:
    if w_064 < 0 or w_sleeve < 0:
        raise ValueError("weights must be ≥ 0")
    if (w_064 + w_sleeve) <= 0:
        raise ValueError("weights must not both be 0")
    if len(r_064) != len(r_sleeve):
        raise ValueError("r_064 and r_sleeve must have same length")
    return w_064 * np.asarray(r_064, dtype=float) + \
        w_sleeve * np.asarray(r_sleeve, dtype=float)
