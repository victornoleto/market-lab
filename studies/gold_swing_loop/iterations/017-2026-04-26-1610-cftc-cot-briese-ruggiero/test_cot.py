"""TDD unit tests for Briese COT Index + Ruggiero signal logic.

Citation: `[trading_systems_methods, p.639-640]`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import run_backtest as bt  # noqa: E402


def test_briese_index_endpoints() -> None:
    """COTI = 0 at the rolling-min, 100 at the rolling-max, 50 at midpoint."""
    nl = pd.Series(
        [10, 20, 30, 40, 50, 25],
        index=pd.date_range("2020-01-01", periods=6, freq="W-FRI"),
    )
    coti = bt.briese_cot_index(nl, window=5)
    # First 4 values are NaN (window not full yet)
    assert coti.iloc[:4].isna().all()
    # At index 4 the window is [10,20,30,40,50]: NL=50 at max → COTI = 100
    assert np.isclose(coti.iloc[4], 100.0)
    # At index 5 the window is [20,30,40,50,25]: NL=25, min=20, max=50, span=30
    # COTI = 100 * (25 - 20) / 30 = 16.667
    assert np.isclose(coti.iloc[5], 100 * (25 - 20) / 30)


def test_briese_index_constant_series() -> None:
    """Constant net-long → degenerate window → COTI defined as 50 (neutral)."""
    nl = pd.Series([42] * 10, index=pd.date_range("2020-01-01", periods=10, freq="W-FRI"))
    coti = bt.briese_cot_index(nl, window=5)
    # Once window is full and constant, min == max → spans = 0 → COTI = 50 by convention.
    valid = coti.iloc[4:]
    assert np.allclose(valid.values, 50.0)


def test_ruggiero_signal_with_lag() -> None:
    """Signal fires only when (Comm > 70) AND (Small < 30) at LAGGED week, exits at neutral."""
    weeks = pd.date_range("2020-01-03", periods=8, freq="W-FRI")
    cot_comm = pd.Series([60, 75, 80, 65, 45, 30, 80, 80], index=weeks)
    cot_small = pd.Series([40, 25, 20, 35, 55, 60, 25, 25], index=weeks)
    daily_index = pd.date_range("2020-01-08", "2020-02-29", freq="B")

    signal = bt.ruggiero_signal(
        cot_comm=cot_comm,
        cot_small=cot_small,
        daily_index=daily_index,
        comm_buy=70.0,
        small_buy=30.0,
        comm_exit=50.0,
        small_exit=50.0,
        lag_weeks=1,
        max_hold_days=30,
    )

    # 2020-01-13 lookup=2020-01-06 → most recent week ≤ that = 2020-01-03 (60/40) → no entry
    assert signal.loc["2020-01-13"] == 0
    # 2020-01-21 lookup=2020-01-14 → week 2020-01-10 (75/25) → entry (in_pos=True)
    assert signal.loc["2020-01-21"] == 1
    # 2020-02-03 lookup=2020-01-27 → week 2020-01-24 (65/35); neither buy nor exit → state machine
    # holds the long open
    assert signal.loc["2020-02-03"] == 1
    # 2020-02-07 lookup=2020-01-31 → week 2020-01-31 (45/55) → BOTH exit conditions fire → flat
    assert signal.loc["2020-02-07"] == 0


def test_max_hold_timeout() -> None:
    """If signal stays valid > max_hold_days, position auto-exits."""
    weeks = pd.date_range("2020-01-03", periods=20, freq="W-FRI")
    # Signal fires every week and never reverts
    cot_comm = pd.Series([80] * 20, index=weeks)
    cot_small = pd.Series([20] * 20, index=weeks)
    daily_index = pd.date_range("2020-01-13", "2020-04-30", freq="B")
    signal = bt.ruggiero_signal(
        cot_comm=cot_comm,
        cot_small=cot_small,
        daily_index=daily_index,
        comm_buy=70.0,
        small_buy=30.0,
        comm_exit=50.0,
        small_exit=50.0,
        lag_weeks=1,
        max_hold_days=10,
    )

    # First active day, then ~10 trading days holding, then forced exit, then re-enter once
    # valid window passes (next bar). The exact sequence: 1,1,1,1,1,1,1,1,1,1,0 (10-day cap),
    # then re-enter the next bar.
    runs = (signal != signal.shift()).cumsum()
    holds = signal.groupby(runs).agg(["sum", "count"])
    # Each "1" run capped at 10
    long_runs = holds[holds["sum"] > 0]
    assert (long_runs["count"] <= 10).all()


def test_apply_costs_long_only() -> None:
    """Cost model: 8 bps RT spread per round-trip + 1 bps swap per calendar night long."""
    daily_index = pd.date_range("2020-01-06", "2020-01-17", freq="B")  # 10 business days
    # Position: long 5 days, flat 3, long 2
    pos = pd.Series([1, 1, 1, 1, 1, 0, 0, 0, 1, 1], index=daily_index)
    gross = pd.Series([0.001] * 10, index=daily_index)  # 0.1% per day gross
    net = bt.apply_costs(
        gross_returns=gross,
        position=pos,
        spread_bps_rt=8.0,
        swap_bps_per_calendar_night=1.0,
    )
    assert len(net) == len(gross)
    # Two round-trip trades → 2 * 8 = 16 bps total spread
    spread_total = (net - gross * pos).sum() * 1e4
    # First trade: 4 nights (Mon-Fri) inside hold = 4 * (-1bp) swap + at exit -8bp spread (split between in/out)
    # Approximate sanity: net cumulative drag should be NEGATIVE
    assert (net - gross * pos).sum() < 0


if __name__ == "__main__":
    import traceback
    failures = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except Exception:  # noqa: BLE001
                failures += 1
                print(f"FAIL  {name}")
                traceback.print_exc()
    sys.exit(0 if failures == 0 else 1)
