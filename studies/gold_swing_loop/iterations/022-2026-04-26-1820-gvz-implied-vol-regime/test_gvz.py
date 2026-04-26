"""TDD tests for iter 022 GVZ z-score signal + cost model parity.

These tests are deliberately minimal: confirm correctness of the
mechanics (rolling z-score, no-lookahead state machine, cost-model parity
vs iter 021) without coupling to gold-specific data values.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from run_backtest import (  # noqa: E402
    apply_costs,
    gvz_zscore_signal_long_when_z_below,
    rolling_zscore,
)


def test_rolling_zscore_constant_series_returns_zero():
    """Constant series → std=0 → z forced to 0 (no NaN explosion)."""
    s = pd.Series([5.0] * 300, index=pd.date_range("2010-01-01", periods=300, freq="D"))
    z = rolling_zscore(s, window=252)
    valid = z.dropna()
    assert (valid == 0.0).all()


def test_rolling_zscore_known_mean_std():
    """Known synthetic ramp + constant shift → z-score is signed."""
    rng = np.random.default_rng(0)
    base = pd.Series(rng.normal(0, 1, 500), index=pd.date_range("2010-01-01", periods=500, freq="D"))
    s = base.copy()
    s.iloc[-1] = 10.0  # huge spike at end
    z = rolling_zscore(s, window=252)
    # last value should be > +3σ in z-space
    assert z.iloc[-1] > 3.0


def test_signal_no_lookahead_lag1():
    """Position at day t depends only on z at day (t - lag_days), not z at t."""
    # Construct GVZ where z<-1 ONLY at day t=300, all else z≈0.
    # With lag=1, position should fire at day t=301, NOT t=300.
    n = 500
    idx = pd.date_range("2010-01-01", periods=n, freq="D")
    rng = np.random.default_rng(0)
    g = pd.Series(rng.normal(20, 0.1, n), index=idx)
    g.iloc[300] = 5.0  # extreme low spike → z very negative on this day
    pos = gvz_zscore_signal_long_when_z_below(
        gvz_daily=g, daily_index=idx, window_days=252,
        z_entry=-1.0, z_exit=0.0, lag_days=1, max_hold_days=30,
    )
    # day 300: z(300) is extreme but lagged, so we use z(299) which is ~0 → no entry
    assert int(pos.iloc[300]) == 0, "lag=1 violated — entered on same-bar z extreme"
    # day 301: z(300) [the extreme] is now visible → should enter
    assert int(pos.iloc[301]) == 1


def test_signal_state_machine_max_hold_caps_position():
    """When z stays below entry indefinitely, state-machine releases at max_hold."""
    n = 400
    idx = pd.date_range("2010-01-01", periods=n, freq="D")
    # GVZ permanently low (after warmup) → z≈0 within window though.
    # Build a series whose rolling-252 z is always < -1 in second half:
    g = pd.Series([20.0] * n, index=idx, dtype=float)
    g.iloc[252:] = 5.0  # second half: drops abruptly. After window rolls, z deeply negative.
    pos = gvz_zscore_signal_long_when_z_below(
        gvz_daily=g, daily_index=idx, window_days=252,
        z_entry=-1.0, z_exit=0.0, lag_days=1, max_hold_days=30,
    )
    # Eventually the position vector contains long stretches; verify one trade is capped at 30 bars.
    pos_arr = pos.values
    runs = []
    cur = 0
    for v in pos_arr:
        if v == 1:
            cur += 1
        elif cur > 0:
            runs.append(cur)
            cur = 0
    if cur > 0:
        runs.append(cur)
    # At least one run; max run should be <= max_hold_days = 30
    assert len(runs) > 0
    assert max(runs) <= 30


def test_apply_costs_zero_position_zero_cost():
    """All-flat position incurs zero cost regardless of returns."""
    idx = pd.date_range("2010-01-01", periods=100, freq="D")
    g = pd.Series(np.random.default_rng(0).normal(0, 0.01, 100), index=idx)
    p = pd.Series([0] * 100, index=idx, dtype=int)
    net = apply_costs(g, p, spread_bps_rt=8.0, swap_bps_per_calendar_night=1.0)
    assert (net == 0.0).all()


def test_apply_costs_single_trade_round_trip():
    """One round trip = 8 bps spread + 1 swap night for 1-night hold."""
    idx = pd.date_range("2010-01-01", periods=10, freq="D")
    g = pd.Series([0.0] * 10, index=idx)  # zero gross returns → only costs
    p = pd.Series([0, 0, 0, 1, 0, 0, 0, 0, 0, 0], index=idx, dtype=int)  # 1-day long
    net = apply_costs(g, p, spread_bps_rt=8.0, swap_bps_per_calendar_night=1.0)
    total_cost = -net.sum()
    # entry (4 bps) + exit (4 bps) + 1 swap night (1 bps) ~= 9 bps total
    expected = 9 * 1e-4
    assert abs(total_cost - expected) < 1e-6, f"got {total_cost} expected ~{expected}"


def test_signal_position_dtype_int():
    """Position vector is int (0/1), no nan/float surprises."""
    n = 500
    idx = pd.date_range("2010-01-01", periods=n, freq="D")
    g = pd.Series(np.random.default_rng(0).normal(20, 1, n), index=idx)
    pos = gvz_zscore_signal_long_when_z_below(
        gvz_daily=g, daily_index=idx, window_days=252,
        z_entry=-1.0, z_exit=0.0, lag_days=1, max_hold_days=30,
    )
    assert pos.dtype.kind in ("i", "u")
    assert pos.isin([0, 1]).all()
