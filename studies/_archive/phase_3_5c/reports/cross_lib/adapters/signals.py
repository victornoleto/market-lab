"""Canonical signal implementations referenced by all adapter tests.

These are *our definition* of the signals. Each lib adapter must reproduce
these values (tolerance ±0 at sample dates) for its unit tests to pass.

Citations
---------
- EMA100 regime: `[leverage_for_the_long_run, p.13]`
- Donchian canonical: `[trading_systems_methods, p.353]`
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema_regime(prices: pd.Series, lookback: int) -> pd.Series:
    """Return boolean Series: True when close > EMA(lookback).

    EMA uses pandas ewm with span=lookback, adjust=False (industry standard).
    """
    ema = prices.ewm(span=lookback, adjust=False).mean()
    return (prices > ema).astype(bool)


def always_on(prices: pd.Series) -> pd.Series:
    """Return constant-True state Series — buy-and-hold baseline (Lead D1).

    Used by Phase 3.5d as the defensive floor against which regime-filter
    strategies must prove they add value. `[leverage_for_the_long_run, p.16]`.
    """
    return pd.Series(True, index=prices.index, dtype=bool)


def donchian_signal(prices: pd.Series, entry: int, exit_: int) -> pd.Series:
    """Return state Series: 1 when LONG, 0 when FLAT.

    LONG triggered on close breaking above prior `entry`-day high.
    FLAT triggered on close breaking below prior `exit_`-day low.
    Hysteresis: state persists between transitions.
    """
    prior_high = prices.rolling(entry, min_periods=entry).max().shift(1)
    prior_low = prices.rolling(exit_, min_periods=exit_).min().shift(1)

    state = pd.Series(0, index=prices.index, dtype=int)
    current = 0
    for t in range(len(prices)):
        close = prices.iloc[t]
        if current == 0 and pd.notna(prior_high.iloc[t]) and close > prior_high.iloc[t]:
            current = 1
        elif current == 1 and pd.notna(prior_low.iloc[t]) and close < prior_low.iloc[t]:
            current = 0
        state.iloc[t] = current
    return state
