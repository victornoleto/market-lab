"""Iter 075 — pure-numpy reference for the sleeve + ensemble (G7 parity).

Hand-rolled implementation that does NOT use pandas. Used to verify
the cross-library parity discipline `[advances_fin_ml, p.31-34]`:
the main pandas implementation must agree with this reference within
±3 pp CAGR (and within 1e-9 element-wise on toy tests).
"""

from __future__ import annotations

import numpy as np

ANNUALIZATION = 252


def _rolling_mean(arr: np.ndarray, window: int) -> np.ndarray:
    """NaN-safe rolling mean. Returns NaN for first (window-1) bars."""
    out = np.full_like(arr, np.nan, dtype=float)
    if len(arr) < window:
        return out
    cumsum = np.cumsum(np.insert(arr, 0, 0.0))
    out[window - 1:] = (cumsum[window:] - cumsum[:-window]) / window
    return out


def _rolling_std(arr: np.ndarray, window: int) -> np.ndarray:
    """NaN-safe rolling std (ddof=1, matches pandas default)."""
    out = np.full_like(arr, np.nan, dtype=float)
    n = len(arr)
    if n < window:
        return out
    for i in range(window - 1, n):
        out[i] = np.std(arr[i - window + 1:i + 1], ddof=1)
    return out


def _single_leg_returns_np(
    prices: np.ndarray,
    *,
    sma_lookback: int,
    vol_lookback: int,
    target_vol: float,
    leg_cap: float,
) -> np.ndarray:
    n = len(prices)
    raw = np.zeros(n)
    raw[1:] = prices[1:] / prices[:-1] - 1.0
    sma = _rolling_mean(prices, sma_lookback)
    # Trend at T-1: (price > sma) at index t-1
    trend_now = np.where(prices > sma, 1.0, 0.0)
    trend_now[~np.isfinite(sma)] = 0.0
    trend_lag = np.zeros(n)
    trend_lag[1:] = trend_now[:-1]
    # Realized vol (annualized) at T-1
    vol_daily = _rolling_std(raw, vol_lookback)
    vol_ann = vol_daily * np.sqrt(ANNUALIZATION)
    vol_ann_lag = np.zeros(n)
    vol_ann_lag[1:] = vol_ann[:-1]
    # Size: target_vol / vol_ann_lag, capped at leg_cap, gated by trend
    size = np.zeros(n)
    valid = (vol_ann_lag > 0) & np.isfinite(vol_ann_lag)
    size[valid] = target_vol / vol_ann_lag[valid]
    size = np.minimum(size, leg_cap)
    pos = size * trend_lag
    pos = np.nan_to_num(pos, nan=0.0, posinf=0.0, neginf=0.0)
    leg_ret = pos * raw
    leg_ret = np.nan_to_num(leg_ret, nan=0.0, posinf=0.0, neginf=0.0)
    return leg_ret


def compute_sleeve_returns_np(
    prices_gld: np.ndarray,
    prices_tlt: np.ndarray,
    *,
    sma_lookback: int = 200,
    vol_lookback: int = 21,
    target_vol: float = 0.10,
    leg_cap: float = 1.0,
) -> np.ndarray:
    if len(prices_gld) != len(prices_tlt):
        raise ValueError("prices_gld and prices_tlt must have same length")
    r_gld = _single_leg_returns_np(
        np.asarray(prices_gld, dtype=float),
        sma_lookback=sma_lookback, vol_lookback=vol_lookback,
        target_vol=target_vol, leg_cap=leg_cap,
    )
    r_tlt = _single_leg_returns_np(
        np.asarray(prices_tlt, dtype=float),
        sma_lookback=sma_lookback, vol_lookback=vol_lookback,
        target_vol=target_vol, leg_cap=leg_cap,
    )
    return 0.5 * r_gld + 0.5 * r_tlt


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
