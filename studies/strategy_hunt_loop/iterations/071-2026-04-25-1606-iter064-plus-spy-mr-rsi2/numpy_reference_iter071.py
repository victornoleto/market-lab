"""Iter 071 — Pure-numpy reference implementation for G7 cross-lib parity.

Mirrors `spy_mr.compute_spy_mr_returns` semantics with no pandas, so
the engine can be cross-validated to ±3pp CAGR (target ≤ 1e-9 max
return diff). See `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import numpy as np


def wilder_rsi_np(prices: np.ndarray, period: int = 2) -> np.ndarray:
    """Wilder's RSI on a 1D numpy array.

    Same recursive smoothing as `spy_mr.wilder_rsi`. The first
    `period` entries are NaN (warmup).
    """
    if period <= 0:
        raise ValueError(f"period must be > 0; got {period}")
    n = len(prices)
    rsi = np.full(n, np.nan, dtype=float)
    if n < 2:
        return rsi

    delta = np.diff(prices)  # length n-1
    gains = np.where(delta > 0, delta, 0.0)
    losses = np.where(delta < 0, -delta, 0.0)

    avg_gain = np.zeros(n - 1, dtype=float)
    avg_loss = np.zeros(n - 1, dtype=float)
    alpha = 1.0 / period
    # Pandas ewm with min_periods=period and adjust=False produces NaN until
    # index `period - 1` of the deltas (the period-th bar). We mirror that
    # by leaving the first (period - 1) entries undefined and seeding at
    # index period-1 with the simple mean of the first `period` entries.
    if n - 1 < period:
        # Not enough data to seed Wilder smoothing.
        return rsi
    avg_gain[period - 1] = np.mean(gains[:period])
    avg_loss[period - 1] = np.mean(losses[:period])
    for i in range(period, n - 1):
        avg_gain[i] = (1.0 - alpha) * avg_gain[i - 1] + alpha * gains[i]
        avg_loss[i] = (1.0 - alpha) * avg_loss[i - 1] + alpha * losses[i]

    # Compute RSI on indices ≥ period-1 of the delta array → these correspond
    # to price index ≥ period in the price array (deltas index t-1 = price t).
    for i in range(period - 1, n - 1):
        ag = avg_gain[i]
        al = avg_loss[i]
        if al == 0.0 and ag == 0.0:
            rsi[i + 1] = 50.0
        elif al == 0.0:
            rsi[i + 1] = 100.0
        else:
            rs = ag / al
            rsi[i + 1] = 100.0 - 100.0 / (1.0 + rs)
    return rsi


def _rolling_mean_np(arr: np.ndarray, window: int) -> np.ndarray:
    """Trailing rolling mean; the first (window-1) bars are NaN."""
    n = len(arr)
    out = np.full(n, np.nan, dtype=float)
    if n < window:
        return out
    csum = np.cumsum(arr, dtype=float)
    csum = np.concatenate([[0.0], csum])  # length n+1
    out[window - 1:] = (csum[window:] - csum[:n - window + 1]) / window
    return out


def compute_spy_mr_returns_np(
    prices: np.ndarray,
    *,
    rsi_period: int = 2,
    rsi_threshold: float = 5.0,
    sma_filter: int = 200,
    exit_sma: int = 5,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> np.ndarray:
    """Pure-numpy mirror of `spy_mr.compute_spy_mr_returns`.

    Returns an array of length `len(prices) - 1` (one bar lost to
    pct_change), aligned to prices[1:].
    """
    if rsi_period <= 0:
        raise ValueError("rsi_period must be > 0")
    if not (0.0 <= rsi_threshold <= 100.0):
        raise ValueError("rsi_threshold must be in [0, 100]")
    if sma_filter <= 0:
        raise ValueError("sma_filter must be > 0")
    if exit_sma <= 0:
        raise ValueError("exit_sma must be > 0")
    if cost_bps < 0:
        raise ValueError("cost_bps must be >= 0")
    if len(prices) < 2:
        raise ValueError("prices must have >= 2 points")

    rf_d = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    n = len(prices)
    rsi = wilder_rsi_np(prices, period=rsi_period)
    sma_long = _rolling_mean_np(prices, sma_filter)
    sma_short = _rolling_mean_np(prices, exit_sma)

    # Shift everything by +1 to align "yesterday's signal applied today"
    rsi_prev = np.concatenate([[np.nan], rsi[:-1]])
    px_prev = np.concatenate([[np.nan], prices[:-1]])
    sma_long_prev = np.concatenate([[np.nan], sma_long[:-1]])
    sma_short_prev = np.concatenate([[np.nan], sma_short[:-1]])

    pos = np.zeros(n, dtype=float)
    for t in range(1, n):
        prev_pos = pos[t - 1]
        if (
            np.isnan(rsi_prev[t]) or np.isnan(px_prev[t])
            or np.isnan(sma_long_prev[t]) or np.isnan(sma_short_prev[t])
        ):
            pos[t] = 0.0
            continue
        gate = px_prev[t] > sma_long_prev[t]
        if prev_pos == 0.0:
            pos[t] = 1.0 if (gate and rsi_prev[t] < rsi_threshold) else 0.0
        else:
            pos[t] = 0.0 if (px_prev[t] > sma_short_prev[t]) else 1.0

    pos_prev_arr = np.concatenate([[0.0], pos[:-1]])
    turnover = np.abs(pos - pos_prev_arr)
    cost = (cost_bps * 1e-4) * turnover

    rets = np.zeros(n, dtype=float)
    rets[1:] = (prices[1:] - prices[:-1]) / prices[:-1]

    net_full = pos * rets + (1.0 - pos) * rf_d - cost
    return net_full[1:]
