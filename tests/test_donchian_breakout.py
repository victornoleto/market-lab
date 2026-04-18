"""Tests for the Donchian channel breakout strategy.

Strategy rules from [trading_systems_methods, p.353]:

1. Pre-compute rolling max(high) and min(low) over entry_lookback bars,
   excluding the current bar (shift 1) — leakage-free.
2. Long entry when close > prior entry_high.
3. Long exit when close < prior exit_low (M < N), OR ATR-stop, OR time-stop.
4. Symmetric for short.

All tests use synthetic OHLCV; no network.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _ohlcv_from_close(close: pd.Series, spread_bps: float = 1.0) -> pd.DataFrame:
    close = close.astype(float)
    half = close * spread_bps * 1e-4
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame(
        {
            "open": open_,
            "high": close + half,
            "low": close - half,
            "close": close,
            "volume": 1_000_000.0,
        },
        index=close.index,
    )


def _flat_then_breakout(
    n_flat: int = 80,
    n_break: int = 40,
    baseline: float = 100.0,
    breakout_amp: float = 10.0,
    freq: str = "h",
) -> pd.Series:
    """Flat baseline → upward breakout → hold high."""
    flat = np.full(n_flat, baseline)
    ramp = np.linspace(baseline, baseline + breakout_amp, n_break)
    values = np.concatenate([flat, ramp])
    idx = pd.date_range("2021-01-01", periods=len(values), freq=freq)
    return pd.Series(values, index=idx)


def _flat_breakout_reverse(
    n_flat: int = 80, n_break: int = 30, n_revert: int = 30,
    baseline: float = 100.0, breakout_amp: float = 10.0,
    freq: str = "h",
) -> pd.Series:
    """Flat → upward breakout → mean revert below baseline (triggers exit)."""
    flat = np.full(n_flat, baseline)
    up = np.linspace(baseline, baseline + breakout_amp, n_break)
    down = np.linspace(baseline + breakout_amp, baseline - breakout_amp, n_revert)
    values = np.concatenate([flat, up, down])
    idx = pd.date_range("2021-01-01", periods=len(values), freq=freq)
    return pd.Series(values, index=idx)


def _run_strategy(strategy, data, cash: float = 100_000.0):
    from ai_trade.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
    from ai_trade.backtest.engine.runner import Runner

    executor = ExecutionSimulator(ExecutionConfig())
    runner = Runner(executor=executor)
    return runner.run(strategy, data, initial_cash=cash)


class TestConstruction:
    def test_precomputes_channels(self):
        from ai_trade.backtest.strategies.donchian_breakout import (
            DonchianBreakoutStrategy,
        )

        close = pd.Series(
            np.linspace(100, 110, 200),
            index=pd.date_range("2021-01-01", periods=200, freq="h"),
        )
        data = {"X": _ohlcv_from_close(close)}
        strat = DonchianBreakoutStrategy(
            data=data, symbol="X", entry_lookback=20, exit_lookback=10,
        )
        ind = strat._indicators["X"]

        assert {"entry_high", "entry_low", "exit_low", "exit_high", "atr"} <= set(
            ind.columns
        )
        # First entry_lookback bars must be NaN (warmup, channels exclude current).
        assert ind["entry_high"].iloc[:20].isna().all()
        # By bar 25, channels are populated.
        assert not pd.isna(ind["entry_high"].iloc[25])

    def test_invalid_params_rejected(self):
        from ai_trade.backtest.strategies.donchian_breakout import (
            DonchianBreakoutStrategy,
        )

        close = pd.Series(
            np.linspace(100, 110, 200),
            index=pd.date_range("2021-01-01", periods=200, freq="h"),
        )
        data = {"X": _ohlcv_from_close(close)}

        with pytest.raises(ValueError, match="entry_lookback"):
            DonchianBreakoutStrategy(data=data, symbol="X", entry_lookback=1)
        with pytest.raises(ValueError, match="exit_lookback.*entry_lookback"):
            DonchianBreakoutStrategy(
                data=data, symbol="X", entry_lookback=10, exit_lookback=10,
            )
        with pytest.raises(ValueError, match="direction"):
            DonchianBreakoutStrategy(
                data=data, symbol="X", direction="badbad",  # type: ignore[arg-type]
            )
        with pytest.raises(KeyError):
            DonchianBreakoutStrategy(data=data, symbol="ZZZ")


class TestSignals:
    def test_long_entry_on_breakout(self):
        from ai_trade.backtest.strategies.donchian_breakout import (
            DonchianBreakoutStrategy,
        )

        close = _flat_then_breakout(n_flat=80, n_break=60, breakout_amp=15.0)
        data = {"X": _ohlcv_from_close(close)}
        strat = DonchianBreakoutStrategy(
            data=data, symbol="X", entry_lookback=20, exit_lookback=10,
            atr_stop_mult=0.0, max_hold=15, direction="long",
        )
        result = _run_strategy(strat, data)

        # Open + close on time-stop produces at least one full trade.
        assert len(result.fills) >= 1
        # Entry fill price above baseline (breakout took us above 100).
        entry_fill = result.fills[0]
        assert entry_fill.fill_price > 100.0

    def test_long_exit_on_donchian_low_break(self):
        from ai_trade.backtest.strategies.donchian_breakout import (
            DonchianBreakoutStrategy,
        )

        close = _flat_breakout_reverse(
            n_flat=80, n_break=30, n_revert=80,
            baseline=100.0, breakout_amp=15.0,
        )
        data = {"X": _ohlcv_from_close(close)}
        strat = DonchianBreakoutStrategy(
            data=data, symbol="X", entry_lookback=20, exit_lookback=10,
            atr_stop_mult=0.0, max_hold=300, direction="long",
        )
        result = _run_strategy(strat, data)

        # Entered on breakout, exited on exit-low channel breakdown.
        assert len(result.trades) >= 1
        # Exit timestamp must precede the bottom (revert finishes after exit).
        assert result.trades[0].exit_time < close.index[-1]

    def test_time_stop_caps_hold(self):
        from ai_trade.backtest.strategies.donchian_breakout import (
            DonchianBreakoutStrategy,
        )

        close = _flat_then_breakout(n_flat=80, n_break=200, breakout_amp=20.0)
        data = {"X": _ohlcv_from_close(close)}
        strat = DonchianBreakoutStrategy(
            data=data, symbol="X", entry_lookback=20, exit_lookback=10,
            atr_stop_mult=0.0, max_hold=15, direction="long",
        )
        result = _run_strategy(strat, data)

        assert len(result.trades) >= 1
        # Trend never breaks the exit channel; only time-stop can close.
        first = result.trades[0]
        entry_loc = close.index.get_loc(first.entry_time)
        exit_loc = close.index.get_loc(first.exit_time)
        bars_held = exit_loc - entry_loc
        assert bars_held <= 16  # max_hold + 1 tolerance for execution timing

    def test_short_entry_on_breakdown(self):
        from ai_trade.backtest.strategies.donchian_breakout import (
            DonchianBreakoutStrategy,
        )

        # Flat baseline → downward breakout.
        n_flat = 80
        n_break = 60
        flat = np.full(n_flat, 100.0)
        down = np.linspace(100.0, 85.0, n_break)
        values = np.concatenate([flat, down])
        idx = pd.date_range("2021-01-01", periods=len(values), freq="h")
        close = pd.Series(values, index=idx)
        data = {"X": _ohlcv_from_close(close)}
        strat = DonchianBreakoutStrategy(
            data=data, symbol="X", entry_lookback=20, exit_lookback=10,
            atr_stop_mult=0.0, max_hold=15, direction="short",
        )
        result = _run_strategy(strat, data)

        assert len(result.fills) >= 1
        entry_fill = result.fills[0]
        # Short entry fill price below baseline (breakdown took us under 100).
        assert entry_fill.fill_price < 100.0

    def test_no_signal_on_flat_data(self):
        from ai_trade.backtest.strategies.donchian_breakout import (
            DonchianBreakoutStrategy,
        )

        idx = pd.date_range("2021-01-01", periods=300, freq="h")
        close = pd.Series(100.0, index=idx)
        data = {"X": _ohlcv_from_close(close, spread_bps=0.0)}
        strat = DonchianBreakoutStrategy(
            data=data, symbol="X", entry_lookback=20, exit_lookback=10,
            atr_stop_mult=0.0, max_hold=120, direction="both",
        )
        result = _run_strategy(strat, data)

        # Channels degenerate to a flat line; equality should not trigger entry.
        assert len(result.trades) == 0
