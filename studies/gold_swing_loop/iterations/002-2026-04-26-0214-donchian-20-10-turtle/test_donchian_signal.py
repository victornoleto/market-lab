"""TDD tests for the Donchian-20/10 channel breakout signal.

Run with::

    .venv/bin/python -m pytest studies/gold_swing_loop/iterations/002-*/test_donchian_signal.py -v

Validates:
* No look-ahead bias (entry/exit channels use t-1 reference via shift(1))
* Long entry fires once `close[t] > max(close[t-20..t-1])` (i.e., bar t≥20)
* Long exit fires when `close[t] < min(close[t-10..t-1])`
* Position is binary {-1, 0, +1}; flat between trades
* `long_only=True` clips short signals to 0
* No direct +1 → -1 flip in a single bar (state machine passes through 0)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))


@pytest.fixture
def trending_up_close():
    """50-bar monotone uptrend → long entry on bar 20, no exit thereafter."""
    n = 50
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    close = pd.Series(np.linspace(100.0, 200.0, n), index=idx, name="close")
    return pd.DataFrame({"close": close})


@pytest.fixture
def trending_down_close():
    """50-bar monotone downtrend → short entry on bar 20 (Track A)."""
    n = 50
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    close = pd.Series(np.linspace(200.0, 100.0, n), index=idx, name="close")
    return pd.DataFrame({"close": close})


@pytest.fixture
def reversing_uptrend():
    """30 bars up → 15 bars down. Long fires at bar 20, exits in downtrend."""
    n_up = 30
    n_down = 15
    idx = pd.date_range("2024-01-01", periods=n_up + n_down, freq="B")
    up = np.linspace(100.0, 200.0, n_up)
    down = np.linspace(200.0, 150.0, n_down)
    close = pd.Series(np.concatenate([up, down]), index=idx, name="close")
    return pd.DataFrame({"close": close})


@pytest.fixture
def flat_close():
    """30 bars flat → no breakout (strict >), position stays 0."""
    n = 30
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    close = pd.Series(100.0, index=idx, name="close")
    return pd.DataFrame({"close": close})


def test_donchian_long_entry_on_new_high(trending_up_close):
    """Long entry must fire on bar 20 (first bar with full prior 20-day window)."""
    from run_backtest import donchian_breakout_signal

    pos = donchian_breakout_signal(trending_up_close, entry_lookback=20,
                                    exit_lookback=10, long_only=False)
    assert (pos.iloc[:20] == 0).all(), "no entry before 20-day window forms (bars 0-19)"
    assert (pos.iloc[20:] == 1).all(), "long position throughout monotone uptrend (bars 20+)"


def test_donchian_short_entry_on_new_low(trending_down_close):
    """Short entry must fire on bar 20 in a monotone downtrend (Track A)."""
    from run_backtest import donchian_breakout_signal

    pos = donchian_breakout_signal(trending_down_close, entry_lookback=20,
                                    exit_lookback=10, long_only=False)
    assert (pos.iloc[:20] == 0).all(), "no entry before 20-day window forms"
    assert (pos.iloc[20:] == -1).all(), "short position throughout monotone downtrend"


def test_donchian_long_only_clips_shorts(trending_down_close):
    """`long_only=True` must drop short signals to flat."""
    from run_backtest import donchian_breakout_signal

    pos = donchian_breakout_signal(trending_down_close, entry_lookback=20,
                                    exit_lookback=10, long_only=True)
    assert (pos == 0).all(), "long-only must clip shorts to flat"


def test_donchian_no_lookahead_in_exit(reversing_uptrend):
    """The 10-day exit reference must use bars STRICTLY BEFORE current bar.

    Pattern (uptrend bars 0-29, downtrend bars 30-44):
        * bars 0-19 : 0  (no rolling window yet)
        * bars 20-?? : 1 (long entered at bar 20)
        * bar k (some k>=30): exit fires when close drops below 10-day low
        * post-exit: 0 or -1 (depending on 20-day low test)
    """
    from run_backtest import donchian_breakout_signal

    pos = donchian_breakout_signal(reversing_uptrend, entry_lookback=20,
                                    exit_lookback=10, long_only=False)
    # Long entered at bar 20 and held while uptrend extends.
    # We don't pin the exact exit bar, but it must happen during the
    # downtrend (bars 30+) — strategy MUST exit before the dataset ends.
    assert (pos.iloc[20:30] == 1).all(), "long held during uptrend extension (bars 20-29)"
    assert not (pos.iloc[30:] == 1).all(), "must exit long at some point during downtrend (bars 30+)"


def test_donchian_flat_close_no_signal(flat_close):
    """Flat prices → no breakout entry (strict > on entry channel)."""
    from run_backtest import donchian_breakout_signal

    pos = donchian_breakout_signal(flat_close, entry_lookback=20,
                                    exit_lookback=10, long_only=False)
    # Flat close[t] equals all values in the rolling window → strict > fails.
    # Strict < also fails. Position must stay 0 throughout.
    assert (pos == 0).all(), "flat close = no breakout, no entry"


def test_donchian_position_values_are_binary(reversing_uptrend):
    """Position must only take values in {-1, 0, +1}."""
    from run_backtest import donchian_breakout_signal

    pos = donchian_breakout_signal(reversing_uptrend, entry_lookback=20,
                                    exit_lookback=10, long_only=False)
    valid = {-1.0, 0.0, 1.0}
    assert set(pos.unique()).issubset(valid), f"unexpected pos values: {set(pos.unique())}"


def test_donchian_no_overlap_long_short(reversing_uptrend):
    """Cannot flip directly +1 → -1 (or -1 → +1) in one bar; must pass through 0.

    A direct flip would be a position diff of magnitude 2.
    """
    from run_backtest import donchian_breakout_signal

    pos = donchian_breakout_signal(reversing_uptrend, entry_lookback=20,
                                    exit_lookback=10, long_only=False)
    # fillna(0) on the first bar's diff (which is NaN by definition).
    diffs = pos.diff().fillna(0.0).abs()
    assert (diffs <= 1.0).all(), \
        f"state machine must pass through 0; max diff observed = {float(diffs.max())}"
