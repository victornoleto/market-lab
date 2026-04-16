"""Tests for DonchianBreakout [trading_systems_methods, p.353]."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from ai_trade.backtest.strategies.vol_expansion_breakout import (
    BreakoutDirection, DonchianBreakout,
)


def _ohlc(highs, lows, closes) -> pd.DataFrame:
    return pd.DataFrame({"open": list(closes), "high": list(highs), "low": list(lows), "close": list(closes)})


def test_long_fire_when_close_breaks_above_window_high() -> None:
    sig = DonchianBreakout(n_entry=20)
    closes = list(np.linspace(100, 105, 21)) + [110.0]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    assert sig.fire(_ohlc(highs, lows, closes)) == BreakoutDirection.LONG


def test_short_fire_when_close_breaks_below_window_low() -> None:
    sig = DonchianBreakout(n_entry=20)
    closes = list(np.linspace(100, 95, 21)) + [80.0]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    assert sig.fire(_ohlc(highs, lows, closes)) == BreakoutDirection.SHORT


def test_no_fire_when_close_inside_channel() -> None:
    sig = DonchianBreakout(n_entry=20)
    closes = list(np.full(22, 100.0))
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    assert sig.fire(_ohlc(highs, lows, closes)) is None


def test_no_fire_at_exact_boundary() -> None:
    sig = DonchianBreakout(n_entry=20)
    highs = [101.0] * 22
    lows = [99.0] * 22
    closes = [100.0] * 21 + [101.0]  # equals window high
    assert sig.fire(_ohlc(highs, lows, closes)) is None


def test_returns_none_when_buffer_too_small() -> None:
    sig = DonchianBreakout(n_entry=20)
    assert sig.fire(_ohlc([100.0]*5, [99.0]*5, [99.5]*5)) is None
