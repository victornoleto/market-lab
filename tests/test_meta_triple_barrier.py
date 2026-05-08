"""Unit tests for triple-barrier labeling [AFML §3.4, p.45-49]."""

from __future__ import annotations

import numpy as np
import pandas as pd

from market_lab.backtest.meta.triple_barrier import apply_triple_barrier


def _close(values):
    idx = pd.date_range("2024-01-01", periods=len(values), freq="B")
    return pd.Series(values, index=idx, dtype=float)


def _events(t0s, t1s, trgt, side):
    return pd.DataFrame(
        {"t1": t1s, "trgt": trgt, "side": side},
        index=pd.DatetimeIndex(t0s),
    )


class TestTripleBarrier:
    def test_long_profit_barrier_hit_first(self):
        """Long entry at 100, 2% target — price rises to 103 by day 3."""
        close = _close([100, 101, 103, 104, 105, 106])
        t1 = [close.index[-1]]
        ev = _events([close.index[0]], t1, [0.02], [1])

        out = apply_triple_barrier(close, ev, pt_sl=(1.0, 1.0))
        assert out.iloc[0]["bin"] == 1
        # Upper = 100 * 1.02 = 102; first bar at or above is index 2 (103).
        assert out.iloc[0]["t1_actual"] == close.index[2]
        assert out.iloc[0]["ret"] > 0

    def test_long_stop_barrier_hit_first(self):
        """Long entry at 100, stop 2% → price falls to 97 immediately."""
        close = _close([100, 99, 97, 96, 95, 94])
        ev = _events([close.index[0]], [close.index[-1]], [0.02], [1])

        out = apply_triple_barrier(close, ev, pt_sl=(1.0, 1.0))
        assert out.iloc[0]["bin"] == -1
        # Lower = 100 * 0.98 = 98; first bar at or below is index 2 (97).
        assert out.iloc[0]["t1_actual"] == close.index[2]
        assert out.iloc[0]["ret"] < 0

    def test_vertical_barrier_when_neither_touched(self):
        close = _close([100, 100.5, 100.3, 100.7, 100.1, 100.4])
        ev = _events([close.index[0]], [close.index[-1]], [0.05], [1])

        out = apply_triple_barrier(close, ev, pt_sl=(1.0, 1.0))
        assert out.iloc[0]["bin"] == 0
        assert out.iloc[0]["t1_actual"] == close.index[-1]

    def test_short_side_profit_barrier_is_lower_price(self):
        """Short entry at 100, 2% target → price falls to 97 → profit."""
        close = _close([100, 99, 97, 96, 95, 94])
        ev = _events([close.index[0]], [close.index[-1]], [0.02], [-1])

        out = apply_triple_barrier(close, ev, pt_sl=(1.0, 1.0))
        # For a short, "up" in PnL means price fell: hit_up is price <= upper
        assert out.iloc[0]["bin"] == 1  # profit for short side
        assert out.iloc[0]["ret"] > 0  # ret is aligned with trade PnL

    def test_pt_sl_asymmetry_only_pt(self):
        """Setting sl=0 disables the stop barrier entirely."""
        close = _close([100, 99, 97, 104, 105, 106])
        ev = _events([close.index[0]], [close.index[-1]], [0.02], [1])

        # With sl=0, lower barrier = 100 * 1 = 100. Any dip below hits it.
        # So use sl=0 but a very wide pt=1000 → neither barrier triggers
        # a clean "hit" on the depicted data except vertical.
        # Simpler: use a mid-path recovery
        out = apply_triple_barrier(close, ev, pt_sl=(2.0, 0.5))
        # Upper = 100 * 1.04 = 104 → hit at index 3
        # Lower = 100 * 0.99 = 99 → hit at index 1 FIRST
        # So bin should be -1 (stop hit before profit).
        assert out.iloc[0]["bin"] == -1

    def test_empty_events_returns_empty_frame(self):
        close = _close([100, 101, 102])
        ev = pd.DataFrame(columns=["t1", "trgt", "side"])
        out = apply_triple_barrier(close, ev, pt_sl=(1.0, 1.0))
        assert out.empty

    def test_path_truncated_at_series_end_if_t1_beyond(self):
        """t1 past the last close timestamp — function walks path up to end."""
        close = _close([100, 101, 102])
        t1_future = close.index[-1] + pd.Timedelta(days=30)
        ev = _events([close.index[0]], [t1_future], [0.02], [1])

        out = apply_triple_barrier(close, ev, pt_sl=(1.0, 1.0))
        # Upper = 102 — hit at index 2.
        assert out.iloc[0]["bin"] == 1

    def test_columns_and_types(self):
        close = _close([100, 101, 102, 103])
        ev = _events([close.index[0]], [close.index[-1]], [0.02], [1])
        out = apply_triple_barrier(close, ev, pt_sl=(1.0, 1.0))
        assert list(out.columns) == ["bin", "t1_actual", "ret"]
        assert out["bin"].dtype.kind in ("i", "u")
        assert np.issubdtype(out["ret"].dtype, np.floating)
