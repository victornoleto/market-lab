"""Threshold-buffered signal variants for the threshold_sweep sub-study.

Per spec §4.2-§4.3:
  - sma_gate_with_buffer: stateful hysteresis (symmetric or asymmetric).
  - ar1_gate_with_buffer: stateless threshold (just `> threshold`).

Citations:
  - [trading_systems_methods, Kaufman ch.6] hysteresis mechanism.
  - [systematic_trading, Carver p.174] asymmetric exit for leveraged.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.signals import ar1_coefficient


def sma_gate_with_buffer(
    prices: pd.Series,
    period: int = 200,
    on_threshold: float = 0.0,
    off_threshold: float = 0.0,
) -> pd.Series:
    """Stateful SMA gate with hysteresis buffer.

    State machine:
      - State 0 (OFF) → State 1 (ON) when price/SMA > 1 + on_threshold.
      - State 1 (ON) → State 0 (OFF) when price/SMA < 1 - off_threshold.
      - Otherwise: hold previous state.

    Symmetric:    on_threshold == off_threshold (e.g., 0.02 → ±2% band).
    Asymmetric:   on_threshold > off_threshold (faster off, slower on).
    Plain crossover: both = 0.0 (matches signals.sma_gate).

    Initial state (first valid post-warmup bar): 1 if price > SMA, else 0.

    Parameters
    ----------
    prices : pd.Series
        Daily close prices.
    period : int
        SMA lookback period.
    on_threshold : float
        Buffer required (as fraction) to flip OFF→ON. Must be ≥ 0.
    off_threshold : float
        Buffer required (as fraction) to flip ON→OFF. Must be ≥ 0.

    Returns
    -------
    pd.Series
        {0.0, 1.0, NaN}. NaN during warmup (first `period - 1` bars).
    """
    if on_threshold < 0 or off_threshold < 0:
        raise ValueError("on_threshold and off_threshold must be >= 0")

    sma = prices.rolling(window=period, min_periods=period).mean()
    state_arr = np.full(len(prices), np.nan)
    current = np.nan

    price_arr = prices.values
    sma_arr = sma.values

    for t in range(len(prices)):
        if np.isnan(sma_arr[t]):
            continue
        ratio = price_arr[t] / sma_arr[t]
        if np.isnan(current):
            # First valid bar: initialise from ratio
            current = 1.0 if ratio > 1.0 else 0.0
        elif current == 0.0 and ratio > 1.0 + on_threshold:
            current = 1.0
        elif current == 1.0 and ratio < 1.0 - off_threshold:
            current = 0.0
        # else: hold

        state_arr[t] = current

    return pd.Series(state_arr, index=prices.index)


def ar1_gate_with_buffer(
    returns: pd.Series, window: int = 30, threshold: float = 0.0,
) -> pd.Series:
    """Stateless AR(1) gate with threshold buffer.

    Returns 1 if AR(1)_window > threshold, else 0. NaN during warmup.

    threshold = 0 (default) matches the canonical `(ar1 > 0)` gate.
    threshold > 0 requires stronger momentum confirmation.

    Citations:
      - [paper.hsieh_2025_letf_compounding] AR(1) regime for LETFs.
      - [trading_systems_methods, Kaufman ch.21] regime-sensitivity testing.
    """
    ar1 = ar1_coefficient(returns, window=window)
    gate = (ar1 > threshold).astype(float)
    gate[ar1.isna()] = np.nan
    return gate
