"""Tests for the DFII10 macro stream signal (gold swing iter 014).

The signal is binary: ``1`` when DFII10 is *falling* on a 60-day rolling
window (today's close < close 60 trading-days ago), else ``0``. The
signal is computed on FRED's DFII10 daily series and forward-filled to
align with each gold dataset's bar index.

Citations
---------
* `[trading_systems_methods, p.13]` — metals are low-noise → trend-following with macro driver
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.strategies.macro_dfii10_gold import (
    dfii10_falling_flag,
    dfii10_falling_flag_numpy,
    align_signal_to_index,
)


# ---------------------------------------------------------------------------
# dfii10_falling_flag — pandas reference
# ---------------------------------------------------------------------------


def test_falling_flag_basic_descending():
    """Strictly descending series → flag = 1 once warmup is past."""
    idx = pd.date_range("2020-01-02", periods=120, freq="B")
    series = pd.Series(np.linspace(2.0, 1.0, 120), index=idx)  # falling
    flag = dfii10_falling_flag(series, lookback=60)
    assert flag.iloc[:60].sum() == 0  # warmup
    assert flag.iloc[60:].sum() == 60  # all 1 (strictly falling on 60-day window)
    assert flag.dtype == np.int64 or flag.dtype == int


def test_falling_flag_basic_ascending():
    """Strictly ascending series → flag = 0 always."""
    idx = pd.date_range("2020-01-02", periods=120, freq="B")
    series = pd.Series(np.linspace(1.0, 2.0, 120), index=idx)
    flag = dfii10_falling_flag(series, lookback=60)
    assert flag.sum() == 0


def test_falling_flag_warmup_zero():
    """First ``lookback`` bars must be flag=0 (cannot compute lag yet)."""
    idx = pd.date_range("2020-01-02", periods=200, freq="B")
    series = pd.Series(np.random.RandomState(42).randn(200).cumsum() + 2.0, index=idx)
    flag = dfii10_falling_flag(series, lookback=60)
    assert (flag.iloc[:60] == 0).all()


def test_falling_flag_strict_inequality():
    """Equal values today vs 60d ago → flag = 0 (strict less-than)."""
    idx = pd.date_range("2020-01-02", periods=120, freq="B")
    series = pd.Series(np.full(120, 1.5), index=idx)  # constant
    flag = dfii10_falling_flag(series, lookback=60)
    assert (flag == 0).all()


def test_falling_flag_index_preserved():
    idx = pd.date_range("2020-01-02", periods=120, freq="B")
    series = pd.Series(np.linspace(2.0, 1.0, 120), index=idx)
    flag = dfii10_falling_flag(series, lookback=60)
    pd.testing.assert_index_equal(flag.index, series.index)


# ---------------------------------------------------------------------------
# Cross-lib parity (pandas vs hand-rolled numpy) — G7 gate
# ---------------------------------------------------------------------------


def test_falling_flag_numpy_parity_random():
    rng = np.random.RandomState(7)
    n = 500
    arr = (rng.randn(n).cumsum() * 0.05 + 1.5).clip(min=-1.0)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    series = pd.Series(arr, index=idx)

    flag_pd = dfii10_falling_flag(series, lookback=60).values
    flag_np = dfii10_falling_flag_numpy(arr, lookback=60)

    assert flag_pd.dtype.kind == "i"
    assert flag_np.dtype.kind == "i"
    np.testing.assert_array_equal(flag_pd, flag_np)


def test_falling_flag_numpy_parity_descending():
    arr = np.linspace(2.5, 0.5, 300)
    flag_np = dfii10_falling_flag_numpy(arr, lookback=60)
    # 300 bars; first 60 are warmup → 0, remaining 240 → 1
    assert flag_np[:60].sum() == 0
    assert flag_np[60:].sum() == 240


# ---------------------------------------------------------------------------
# align_signal_to_index — daily DFII10 → asset bar index
# ---------------------------------------------------------------------------


def test_align_signal_to_daily_index():
    """DFII10 (daily) → daily gold index. Should ffill across asset's bars."""
    dfii10_idx = pd.date_range("2020-01-02", periods=10, freq="B")
    flag = pd.Series([0, 0, 1, 1, 1, 0, 0, 1, 1, 1], index=dfii10_idx, dtype=int)
    asset_idx = pd.date_range("2020-01-03", periods=10, freq="B")
    aligned = align_signal_to_index(flag, asset_idx)
    assert len(aligned) == 10
    pd.testing.assert_index_equal(aligned.index, asset_idx)
    # No look-ahead — aligned[t] should equal flag at the bar with date ≤ t
    # 2020-01-03 corresponds to flag at 2020-01-03 → 0
    assert aligned.iloc[0] == 0


def test_align_signal_to_intraday_index():
    """DFII10 (daily) → 1h gold index. Daily flag should propagate across intraday bars."""
    dfii10_idx = pd.date_range("2020-01-02", periods=5, freq="B")
    flag = pd.Series([0, 1, 1, 0, 1], index=dfii10_idx, dtype=int)
    # Build 24 intraday bars per day for 5 business days
    asset_idx = pd.date_range("2020-01-02 00:00", "2020-01-08 23:00", freq="1h")
    aligned = align_signal_to_index(flag, asset_idx)
    assert len(aligned) == len(asset_idx)
    # Within day d, aligned should be flag at d (forward-fill from prior bar's signal)
    # 2020-01-02 bars → flag[0]=0
    mask_jan02 = (asset_idx.date == pd.Timestamp("2020-01-02").date())
    assert (aligned[mask_jan02] == 0).all()
    mask_jan06 = (asset_idx.date == pd.Timestamp("2020-01-06").date())
    # On Mon 2020-01-06, prior business day flag (Fri 2020-01-03=1) ffilled
    assert (aligned[mask_jan06] == 1).all()


def test_align_handles_missing_days():
    """If asset has bars on days where DFII10 has no value (FRED holiday),
    ffill should carry the prior signal."""
    dfii10_idx = pd.DatetimeIndex(["2020-01-02", "2020-01-03", "2020-01-07"])
    flag = pd.Series([1, 0, 1], index=dfii10_idx, dtype=int)
    asset_idx = pd.DatetimeIndex(["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"])
    aligned = align_signal_to_index(flag, asset_idx)
    # 2020-01-06: DFII10 has no row (MLK holiday gap) → ffill from Jan 3 = 0
    assert aligned.loc["2020-01-06"] == 0
    assert aligned.loc["2020-01-07"] == 1


def test_align_pre_signal_data_zero():
    """Asset bars BEFORE first DFII10 bar should get 0 (no signal yet)."""
    dfii10_idx = pd.DatetimeIndex(["2020-01-10", "2020-01-13"])
    flag = pd.Series([1, 1], index=dfii10_idx, dtype=int)
    asset_idx = pd.DatetimeIndex(["2020-01-02", "2020-01-03", "2020-01-10", "2020-01-13"])
    aligned = align_signal_to_index(flag, asset_idx)
    assert aligned.loc["2020-01-02"] == 0
    assert aligned.loc["2020-01-03"] == 0
    assert aligned.loc["2020-01-10"] == 1
    assert aligned.loc["2020-01-13"] == 1
