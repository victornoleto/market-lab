"""Gayed-style Leveraged Rotation Strategy (LRS) regime-gate engines.

Three gate families, all returning a boolean ON/OFF Series with T+1
execution lag (no peek-ahead):

  - ``gayed_200d_sma_gate``  — classical SMA cross. Single trigger.
  - ``ema_gate``             — EMA cross (faster reaction, lower lag).
  - ``threshold_band_gate``  — hysteresis band around SMA/EMA. Turn ON
    when price > MA × (1 + buffer); turn OFF when price < MA × (1 - buffer);
    HOLD state otherwise. Reduces whipsaw cost in choppy markets.

Citations:
  - [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed — 200d SMA on LETFs
  - studies/_archive/ema_sma_threshold_nasdaq_real (prior project sweep,
    2010-2024 NDX): SMA/EMA × N{100,150,200} × threshold{0,2,5}% sweep,
    SMA_N150_th0_bL2 best (CAGR 25.32%, MDD 40.53%, 5/7 gates) on QQQ.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def gayed_200d_sma_gate(
    signal_prices: pd.Series,
    window: int = 200,
    lag_days: int = 1,
) -> pd.Series:
    """Boolean ON/OFF series from a price > SMA(window) regime check.

    Args:
        signal_prices: equity-curve series (e.g. SPYSIM cache prices).
        window: SMA lookback in trading days (default 200 per Gayed).
        lag_days: execution lag (default 1) — gate at time t reflects
            the signal computed from prices at time t-1, ensuring no
            peek-ahead. T+0 (lag=0) would peek; T+1 mirrors live trading.

    Returns:
        Boolean Series indexed identically to ``signal_prices`` where
        True = bullish regime (allocate to leveraged equity), False =
        bearish regime (allocate to defensive sleeve). Pre-window days
        and the first ``lag_days`` rows fill False (no signal yet).
    """
    sma = signal_prices.rolling(window=window, min_periods=window).mean()
    on_off = signal_prices > sma
    return on_off.shift(lag_days).fillna(False)


def ema_gate(
    signal_prices: pd.Series,
    window: int = 200,
    lag_days: int = 1,
) -> pd.Series:
    """Boolean ON/OFF series from a price > EMA(span=window) regime check.

    EMA reacts faster than SMA to recent price moves; in trending markets
    this catches regime shifts earlier (less lag, less peak drawdown
    capture during crashes), at the cost of slightly more whipsaw in
    sideways markets.

    Args:
        signal_prices: equity-curve series.
        window: EMA span in trading days.
        lag_days: T+1 execution lag (default 1).

    Returns:
        Boolean Series, True = price > EMA.
    """
    ema = signal_prices.ewm(span=window, adjust=False, min_periods=window).mean()
    on_off = signal_prices > ema
    return on_off.shift(lag_days).fillna(False)


def threshold_band_gate(
    signal_prices: pd.Series,
    window: int = 200,
    buffer_pct: float = 0.02,
    lag_days: int = 1,
    filter_type: str = "sma",
) -> pd.Series:
    """Hysteresis-banded regime gate to reduce whipsaw cost.

    State transitions (computed sequentially):
      - OFF → ON  when price > MA × (1 + buffer_pct)
      - ON  → OFF when price < MA × (1 - buffer_pct)
      - else: HOLD current state

    The buffer creates a "zone of indifference" around the moving
    average where the gate doesn't flip — analogous to a Schmitt trigger.
    Larger buffer = fewer flips = lower trading frequency but slower
    response to genuine regime shifts.

    Args:
        signal_prices: equity-curve series.
        window: MA window (SMA window or EMA span).
        buffer_pct: half-width of the hysteresis band as a fraction
            (e.g. 0.02 = 2% above and below MA).
        lag_days: T+1 execution lag.
        filter_type: ``"sma"`` (rolling mean) or ``"ema"`` (exponential).

    Returns:
        Boolean Series, True = bullish regime per hysteresis state.
    """
    if filter_type == "sma":
        ma = signal_prices.rolling(window=window, min_periods=window).mean()
    elif filter_type == "ema":
        ma = signal_prices.ewm(
            span=window, adjust=False, min_periods=window
        ).mean()
    else:
        raise ValueError(
            f"unknown filter_type {filter_type!r}; choose 'sma' or 'ema'"
        )

    upper = ma * (1.0 + buffer_pct)
    lower = ma * (1.0 - buffer_pct)

    above = (signal_prices > upper).fillna(False).to_numpy(dtype=bool)
    below = (signal_prices < lower).fillna(False).to_numpy(dtype=bool)
    valid = ma.notna().to_numpy(dtype=bool)

    state = np.zeros(len(signal_prices), dtype=bool)
    current = False
    for i in range(len(signal_prices)):
        if not valid[i]:
            current = False
        elif above[i]:
            current = True
        elif below[i]:
            current = False
        # else: hold
        state[i] = current

    out = pd.Series(state, index=signal_prices.index)
    return out.shift(lag_days).fillna(False).astype(bool)


def lrs_strategy_returns(
    on_returns: pd.Series,
    off_returns: pd.Series,
    gate: pd.Series,
) -> pd.Series:
    """Daily strategy returns alternating between on/off based on the gate.

    Args:
        on_returns: leveraged-equity daily returns (e.g. UPRO synth).
        off_returns: defensive sleeve daily returns (e.g. IEF synth).
        gate: boolean Series from ``gayed_200d_sma_gate``.

    Returns:
        Daily returns Series on the intersection of all three indices
        (pd.concat + dropna). Returns ``on_returns[t]`` when ``gate[t]``
        is True, else ``off_returns[t]``.
    """
    aligned = pd.concat(
        {"on": on_returns, "off": off_returns, "gate": gate},
        axis=1,
        sort=True,
    ).dropna()
    return aligned["on"].where(aligned["gate"].astype(bool), aligned["off"])
