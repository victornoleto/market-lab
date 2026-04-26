"""TDD tests for COT z-score signal generator.

Citation: `[trading_systems_methods, p.639-640]` (Briese/Ruggiero on COT;
z-score variant noted as canonical alternative when stochastic clips
recent extremes against historical tails) + de Roon-Nijman-Veld 2000
*J Finance* (z-score of commercial net positioning).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import run_backtest as bt  # noqa: E402


def test_rolling_zscore_endpoints() -> None:
    """Rolling z-score of a constant series → 0 (or NaN by convention)."""
    s = pd.Series([42.0] * 10, index=pd.date_range("2020-01-01", periods=10, freq="W-FRI"))
    z = bt.rolling_zscore(s, window=5)
    # Window not full → NaN
    assert z.iloc[:4].isna().all()
    # Constant window → std=0; convention: 0.0 (neutral)
    valid = z.iloc[4:]
    assert np.allclose(valid.values, 0.0)


def test_rolling_zscore_known_values() -> None:
    """z = (x - mean) / std on the trailing window."""
    s = pd.Series(
        [10.0, 20.0, 30.0, 40.0, 50.0, 100.0],
        index=pd.date_range("2020-01-01", periods=6, freq="W-FRI"),
    )
    z = bt.rolling_zscore(s, window=5)
    # At index 4: window=[10,20,30,40,50], mean=30, std=sqrt(((-20)^2+(-10)^2+0+10^2+20^2)/4)
    #   = sqrt(1000/4)=15.811; z = (50-30)/15.811 = 1.265
    assert np.isclose(z.iloc[4], (50.0 - 30.0) / np.std([10, 20, 30, 40, 50], ddof=1))
    # At index 5: window=[20,30,40,50,100], mean=48, std=ddof1; z = (100-48)/std
    expected = (100.0 - 48.0) / np.std([20, 30, 40, 50, 100], ddof=1)
    assert np.isclose(z.iloc[5], expected)


def test_zscore_signal_entry_exit_timeout() -> None:
    """State machine: enter long when z>+1.0, exit when z<0 OR timeout."""
    # Synthetic: NL_diff = 8 weeks of pure cycle so z gets > +1 then < 0
    weeks = pd.date_range("2020-01-03", periods=8, freq="W-FRI")
    # window=5; first valid bar = idx 4
    # Construct: weeks 0-4 are mild (mean ~ 0), week 5 is huge positive,
    # week 6 mild, week 7 negative
    nl_diff = pd.Series(
        [0.0, 1.0, -1.0, 0.5, -0.5, 100.0, 1.0, -50.0],
        index=weeks,
    )

    daily_index = pd.date_range("2020-02-01", "2020-04-30", freq="B")
    signal = bt.zscore_signal(
        nl_diff_weekly=nl_diff,
        daily_index=daily_index,
        window_weeks=5,
        z_entry=1.0,
        z_exit=0.0,
        lag_weeks=1,
        max_hold_days=30,
    )

    # 2020-02-10 (Mon) lookup = 2020-02-03 (1w lag) → most recent week ≤ that = 2020-01-31 (week idx 4)
    # At week 4 z is computed on window [0,1,-1,0.5,-0.5] → mean=0, std≈0.79; z(-0.5)=−0.633 → no entry
    assert signal.loc["2020-02-10"] == 0
    # 2020-02-17 lookup=2020-02-10 → most recent week ≤ that = 2020-02-07 (week idx 5, z huge positive)
    # Window [1,-1,0.5,-0.5,100] mean=20, std=44.6; z(100)=(100-20)/44.6=1.79 > 1.0 → entry
    assert signal.loc["2020-02-17"] == 1
    # 2020-03-02 lookup = 2020-02-24 → week 2020-02-21 (idx 7) z very negative → exit
    assert signal.loc["2020-03-02"] == 0


def test_zscore_signal_max_hold_timeout() -> None:
    """Position auto-exits at max_hold_days even if signal never reverts."""
    weeks = pd.date_range("2020-01-03", periods=20, freq="W-FRI")
    # Every week the latest sample is huge positive → z always > +1 once warmed up
    vals = [0.0, 0.0, 0.0, 0.0]
    vals.extend([100.0 * (i + 1) for i in range(16)])  # increasing → z > 0 every step
    nl_diff = pd.Series(vals, index=weeks)
    daily_index = pd.date_range("2020-02-15", "2020-08-30", freq="B")
    signal = bt.zscore_signal(
        nl_diff_weekly=nl_diff,
        daily_index=daily_index,
        window_weeks=4,
        z_entry=0.5,
        z_exit=-10.0,  # never naturally exits via z
        lag_weeks=1,
        max_hold_days=10,
    )
    runs = (signal != signal.shift()).cumsum()
    holds = signal.groupby(runs).agg(["sum", "count"])
    long_runs = holds[holds["sum"] > 0]
    # Each long run capped at exactly 10 trading days (max_hold)
    assert (long_runs["count"] <= 10).all()
    # And we have multiple long runs (auto-re-entry after timeout when signal still valid)
    assert len(long_runs) >= 2


def test_zscore_signal_directionality() -> None:
    """Smart-money sign: z>+1 = commercials more bullish than small → LONG.
    Negative z = small traders more bullish than commercials → no LONG entry.
    """
    weeks = pd.date_range("2020-01-03", periods=10, freq="W-FRI")
    # Synthetic monotonically decreasing diff → z always negative once warmed
    nl_diff = pd.Series([0.0, 0.0, 0.0, 0.0, 0.0, -10.0, -20.0, -30.0, -40.0, -50.0], index=weeks)
    daily_index = pd.date_range("2020-02-15", "2020-04-15", freq="B")
    signal = bt.zscore_signal(
        nl_diff_weekly=nl_diff,
        daily_index=daily_index,
        window_weeks=5,
        z_entry=1.0,
        z_exit=0.0,
        lag_weeks=1,
        max_hold_days=30,
    )
    # Should never enter long (z is always ≤ 0 once warmed)
    assert signal.sum() == 0


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
