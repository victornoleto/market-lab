"""Tests for the SessionStrategy (Phase 3.5a Lead T4).

Covers:
- Validation of range_type, signal/exit windows, and entry_band_pct.
- ORB mode: breakout only during signal_hours, range drawn from
  in-window bars, leakage-free (boundary ffill).
- MR mode: fade rolling-bar-window extreme with band.
- Forced exit via exit_hours_utc closes position regardless of P&L.

All tests use synthetic OHLCV — no network, no Tiingo cache.
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


def _run(strategy, data, cash: float = 100_000.0):
    from ai_trade.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
    from ai_trade.backtest.engine.runner import Runner

    executor = ExecutionSimulator(ExecutionConfig())
    runner = Runner(executor=executor)
    return runner.run(strategy, data, initial_cash=cash)


class TestValidation:
    def test_orb_rejects_nonzero_band(self):
        from ai_trade.backtest.strategies.session_based import SessionStrategy

        idx = pd.date_range("2021-01-01", periods=100, freq="h")
        df = _ohlcv_from_close(pd.Series(np.full(100, 100.0), index=idx))
        with pytest.raises(ValueError, match="entry_band_pct"):
            SessionStrategy(
                data={"EURUSD": df},
                symbol="EURUSD",
                mode="orb",
                range_type="hours",
                range_hours_utc=(0, 7),
                signal_hours_utc=(7, 21),
                entry_band_pct=0.1,
            )

    def test_hours_requires_range_hours(self):
        from ai_trade.backtest.strategies.session_based import SessionStrategy

        idx = pd.date_range("2021-01-01", periods=100, freq="h")
        df = _ohlcv_from_close(pd.Series(np.full(100, 100.0), index=idx))
        with pytest.raises(ValueError, match="range_hours_utc"):
            SessionStrategy(
                data={"EURUSD": df},
                symbol="EURUSD",
                mode="orb",
                range_type="hours",
                signal_hours_utc=(7, 21),
            )

    def test_bars_requires_window(self):
        from ai_trade.backtest.strategies.session_based import SessionStrategy

        idx = pd.date_range("2021-01-01", periods=100, freq="h")
        df = _ohlcv_from_close(pd.Series(np.full(100, 100.0), index=idx))
        with pytest.raises(ValueError, match="range_window_bars"):
            SessionStrategy(
                data={"EURUSD": df},
                symbol="EURUSD",
                mode="mr",
                range_type="bars",
                signal_hours_utc=(20, 21),
            )


class TestOrbMode:
    def _series_with_daily_asian_break(self, n_days: int = 20) -> pd.Series:
        """Each day: flat 00-07 (base 100), then +2% spike at 08-12, then flat.

        A long ORB (Asian range 0-7, London 7-21, breakout close > range high)
        should trigger on the 08 UTC bar when price jumps.
        """
        values = []
        idx = []
        start = pd.Timestamp("2021-01-01 00:00", tz=None)
        for d in range(n_days):
            for h in range(24):
                ts = start + pd.Timedelta(days=d, hours=h)
                if h < 7:
                    px = 100.0  # Asian flat
                elif 7 <= h < 12:
                    px = 102.0  # London breakout
                else:
                    px = 102.0  # hold
                values.append(px)
                idx.append(ts)
        return pd.Series(values, index=pd.DatetimeIndex(idx))

    def test_entry_only_in_signal_window(self):
        from ai_trade.backtest.strategies.session_based import SessionStrategy

        close = self._series_with_daily_asian_break(n_days=15)
        df = _ohlcv_from_close(close, spread_bps=0.1)
        strat = SessionStrategy(
            data={"EURUSD": df},
            symbol="EURUSD",
            mode="orb",
            range_type="hours",
            range_hours_utc=(0, 7),
            signal_hours_utc=(7, 21),
            exit_hours_utc=(21, 22),  # force exit at 21:00 so we don't flag next day
            direction="both",
            atr_stop_mult=0.0,  # disable ATR stop for clean unit test
            atr_window=14,
            max_hold=24,
            risk_pct_of_equity=0.5,
        )
        result = _run(strat, {"EURUSD": df})
        assert len(result.trades) > 0, "ORB should fire on Asian-range breakout"
        for tr in result.trades:
            entry_hour = pd.Timestamp(tr.entry_time).hour
            assert 7 <= entry_hour < 21, (
                f"entry at {entry_hour}h outside signal window"
            )

    def test_orb_no_entries_when_signal_window_empty(self):
        from ai_trade.backtest.strategies.session_based import SessionStrategy

        close = self._series_with_daily_asian_break(n_days=10)
        df = _ohlcv_from_close(close, spread_bps=0.1)
        strat = SessionStrategy(
            data={"EURUSD": df},
            symbol="EURUSD",
            mode="orb",
            range_type="hours",
            range_hours_utc=(0, 7),
            signal_hours_utc=(0, 6),  # Signal window inside Asian (no breakout)
            direction="both",
            atr_stop_mult=0.0,
            max_hold=12,
            risk_pct_of_equity=0.5,
        )
        result = _run(strat, {"EURUSD": df})
        # The Asian range is being built but never broken during 0-6h
        # since prices are flat 100.0 inside the range period itself.
        assert len(result.trades) == 0


class TestMrMode:
    def _series_with_spike_at_hour(self, hour: int, n_days: int = 30) -> pd.Series:
        """Flat 100.0 everywhere except a +3% spike at `hour` each day."""
        values = []
        idx = []
        start = pd.Timestamp("2021-01-01 00:00")
        for d in range(n_days):
            for h in range(24):
                ts = start + pd.Timedelta(days=d, hours=h)
                px = 103.0 if h == hour else 100.0
                values.append(px)
                idx.append(ts)
        return pd.Series(values, index=pd.DatetimeIndex(idx))

    def test_mr_fades_spike_into_short(self):
        from ai_trade.backtest.strategies.session_based import SessionStrategy

        close = self._series_with_spike_at_hour(hour=20, n_days=15)
        df = _ohlcv_from_close(close, spread_bps=0.1)
        strat = SessionStrategy(
            data={"EURUSD": df},
            symbol="EURUSD",
            mode="mr",
            range_type="bars",
            # 12-bar window keeps the rolling max inside the same-day
            # flat 08-19 hours, so the 20h spike is a genuine out-of-range
            # event not carried over from the prior day's spike.
            range_window_bars=12,
            signal_hours_utc=(20, 21),
            exit_hours_utc=(7, 8),
            direction="both",
            entry_band_pct=0.002,  # 0.2% beyond range
            atr_stop_mult=0.0,  # disable ATR stop for clean test
            max_hold=48,
            risk_pct_of_equity=0.5,
        )
        result = _run(strat, {"EURUSD": df})
        assert len(result.trades) > 0, "MR should fade the 20h spike"
        # All entries must be shorts (price 3% above rolling range => fade short)
        # and must happen strictly at hour=20.
        for tr in result.trades:
            entry_hour = pd.Timestamp(tr.entry_time).hour
            assert entry_hour == 20
            assert tr.side == "short"


class TestForcedExit:
    def test_exit_hours_closes_position(self):
        from ai_trade.backtest.strategies.session_based import SessionStrategy

        # Design: flat 100 for 48h → +2% step at 07:00 on day 2 → hold.
        # ORB long triggers at 07:00; exit_hours (21, 22) forces flat.
        idx = pd.date_range("2021-01-01", periods=24 * 10, freq="h")
        close = pd.Series(np.full(len(idx), 100.0), index=idx)
        # From day 2 onwards, every London open (07:00) spikes +2%, then holds.
        for i, ts in enumerate(idx):
            if ts.date() >= pd.Timestamp("2021-01-02").date() and ts.hour >= 7:
                close.iloc[i] = 102.0
        df = _ohlcv_from_close(close, spread_bps=0.1)
        strat = SessionStrategy(
            data={"EURUSD": df},
            symbol="EURUSD",
            mode="orb",
            range_type="hours",
            range_hours_utc=(0, 7),
            signal_hours_utc=(7, 21),
            exit_hours_utc=(21, 22),
            direction="long",
            atr_stop_mult=0.0,
            max_hold=48,
            risk_pct_of_equity=0.5,
        )
        result = _run(strat, {"EURUSD": df})
        assert len(result.trades) > 0
        # Every trade must exit at 21:00 (forced-exit window).
        for tr in result.trades:
            exit_hour = pd.Timestamp(tr.exit_time).hour
            assert exit_hour == 21, f"expected forced exit at 21h, got {exit_hour}h"
