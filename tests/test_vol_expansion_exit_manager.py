"""Tests for ExitManager [trading_systems_methods, p.353; systematic_trading, p.212]."""
from __future__ import annotations
import math
from datetime import datetime, timedelta
import pandas as pd
import pytest
from ai_trade.backtest.strategies.vol_expansion_breakout import (
    BreakoutDirection, ExitManager, ExitReason, PositionState,
)


def _ohlc(highs, lows, closes) -> pd.DataFrame:
    return pd.DataFrame({"open": list(closes), "high": list(highs), "low": list(lows), "close": list(closes)})


def _pos(
    direction: BreakoutDirection,
    entry_price: float = 500.0,
    entry_ts: datetime = datetime(2024, 1, 1, 9, 30),
    sigma_yz_annual: float = 0.20,
    bars_per_year: int = 1638,
) -> PositionState:
    return PositionState(
        direction=direction,
        entry_price=entry_price,
        entry_timestamp=entry_ts,
        sigma_yz_at_entry_annual=sigma_yz_annual,
        bars_per_year_at_entry=bars_per_year,
    )


def test_opposite_channel_exit_long() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0, disaster_n_sigma=4, ref_hold_bars=24)
    closes = [100.0] * 10 + [95.0]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    lows[-2] = 99.5
    pos = _pos(BreakoutDirection.LONG, entry_price=100.0)
    assert em.should_exit(_ohlc(highs, lows, closes), pos, datetime(2024, 1, 1, 10, 30)) == ExitReason.OPPOSITE_CHANNEL


def test_opposite_channel_exit_short() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0, disaster_n_sigma=4, ref_hold_bars=24)
    closes = [100.0] * 10 + [110.0]
    highs = [c + 0.5 for c in closes]
    highs[-2] = 100.5
    lows = [c - 0.5 for c in closes]
    pos = _pos(BreakoutDirection.SHORT, entry_price=100.0)
    assert em.should_exit(_ohlc(highs, lows, closes), pos, datetime(2024, 1, 1, 10, 30)) == ExitReason.OPPOSITE_CHANNEL


def test_time_stop_at_48h() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0, disaster_n_sigma=4, ref_hold_bars=24)
    closes = [100.0] * 11
    df = _ohlc([c + 0.5 for c in closes], [c - 0.5 for c in closes], closes)
    pos = _pos(BreakoutDirection.LONG, entry_ts=datetime(2024, 1, 1, 0, 0))
    assert em.should_exit(df, pos, datetime(2024, 1, 3, 0, 0)) == ExitReason.TIME_STOP


def test_disaster_stop_long_triggers() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0, disaster_n_sigma=4, ref_hold_bars=24)
    pos = _pos(BreakoutDirection.LONG, entry_price=500.0, sigma_yz_annual=0.20, bars_per_year=1638)
    # threshold ~ $48.40. Close at $451 triggers; $452 doesn't.
    # Window closes at 450 so lows (449.9) stay below the trigger close (451),
    # ensuring the opposite-channel check does not fire before the disaster check.
    closes_trigger = [450.0] * 10 + [451.0]
    df1 = _ohlc([c + 0.1 for c in closes_trigger], [c - 0.1 for c in closes_trigger], closes_trigger)
    assert em.should_exit(df1, pos, datetime(2024, 1, 1, 10, 30)) == ExitReason.DISASTER_STOP

    closes_safe = [450.0] * 10 + [452.0]
    df2 = _ohlc([c + 0.1 for c in closes_safe], [c - 0.1 for c in closes_safe], closes_safe)
    assert em.should_exit(df2, pos, datetime(2024, 1, 1, 10, 30)) != ExitReason.DISASTER_STOP


def test_disaster_stop_short_triggers() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0, disaster_n_sigma=4, ref_hold_bars=24)
    pos = _pos(BreakoutDirection.SHORT, entry_price=500.0, sigma_yz_annual=0.20, bars_per_year=1638)
    # Window closes at 550 so highs (550.1) stay above the trigger close (549),
    # ensuring the opposite-channel check does not fire before the disaster check.
    closes = [550.0] * 10 + [549.0]
    df = _ohlc([c + 0.1 for c in closes], [c - 0.1 for c in closes], closes)
    assert em.should_exit(df, pos, datetime(2024, 1, 1, 10, 30)) == ExitReason.DISASTER_STOP


def test_exit_priority_opposite_channel_first() -> None:
    em = ExitManager(n_exit=10, max_hold_hours=48.0, disaster_n_sigma=4, ref_hold_bars=24)
    pos = _pos(BreakoutDirection.LONG, entry_price=500.0, sigma_yz_annual=0.20, bars_per_year=1638)
    closes = [500.0] * 10 + [400.0]  # triggers both channel exit and disaster
    df = _ohlc([c + 0.1 for c in closes], [c - 0.1 for c in closes], closes)
    assert em.should_exit(df, pos, datetime(2024, 1, 1, 10, 30)) == ExitReason.OPPOSITE_CHANNEL
