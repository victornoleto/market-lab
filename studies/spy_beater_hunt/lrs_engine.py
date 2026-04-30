"""Gayed Leveraged Rotation Strategy (LRS) engine — 200d SMA regime gate.

The 200d-SMA gate produces a boolean ON/OFF signal: when the underlying's
price is above its 200-day moving average we hold leveraged equity (e.g.
UPRO, TQQQ); when below we hold a defensive sleeve (IEF, CASHX, KMLM).
T+1 execution lag avoids peek-ahead.

Citation: [leverage_for_the_long_run, ch.3-4, p.40-60] — Gayed shows the
200d-SMA gate dramatically reduces LETF volatility decay by sidestepping
prolonged drawdowns where daily-reset compounding is most punishing.
"""
from __future__ import annotations

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
