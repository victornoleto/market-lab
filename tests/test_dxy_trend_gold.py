"""Tests for the DXY trend-slope gate signal (gold swing iter 015).

The signal is binary: ``1`` when the 200-day SMA of DXY (FRED DTWEXBGS)
is *falling* on a 20-trading-day rolling window (SMA_200(t) <
SMA_200(t - 20)), else ``0``. Long gold when DXY's smoothed level is in
sustained falling regime.

This grammar is **slope-based**, structurally distinct from GS-5's
closures (z-score MR; level-vs-MA on cached FX). FRED DTWEXBGS provides
~20 years of long-history data (2006-01-02 → present), avoiding the
2020+ window constraint that GS-5 relied on.

Citations
---------
* `[stocks_on_the_move, p.100]` — 200-day SMA canonical trend filter
* `[trading_systems_methods, p.13-14]` — gold/USD inverse coupling
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from market_lab.backtest.strategies.dxy_trend_gold import (
    align_signal_to_index,
    dxy_sma_falling_flag,
    dxy_sma_falling_flag_numpy,
)


# ---------------------------------------------------------------------------
# dxy_sma_falling_flag — pandas reference
# ---------------------------------------------------------------------------


def test_falling_flag_basic_descending():
    """Strictly descending series → 200d SMA falls → flag = 1 once warmed."""
    n = 400
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    series = pd.Series(np.linspace(120.0, 90.0, n), index=idx)  # falling
    flag = dxy_sma_falling_flag(series, sma_window=200, slope_lookback=20)
    # First (200 + 20 - 1) bars must be warmup → 0
    assert flag.iloc[:219].sum() == 0
    # Past warmup, every SMA(t) is strictly less than SMA(t-20) → 1
    assert flag.iloc[219:].sum() == n - 219
    assert flag.dtype == np.int64 or flag.dtype == int


def test_falling_flag_basic_ascending():
    """Strictly ascending series → SMA rises → flag = 0 always."""
    n = 400
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    series = pd.Series(np.linspace(90.0, 120.0, n), index=idx)
    flag = dxy_sma_falling_flag(series, sma_window=200, slope_lookback=20)
    assert flag.sum() == 0


def test_falling_flag_warmup_zero():
    """First (sma_window + slope_lookback - 1) bars must be 0."""
    rng = np.random.RandomState(42)
    n = 500
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    series = pd.Series(rng.randn(n).cumsum() + 100.0, index=idx)
    flag = dxy_sma_falling_flag(series, sma_window=200, slope_lookback=20)
    assert (flag.iloc[:219] == 0).all()


def test_falling_flag_strict_inequality():
    """Constant series → SMA is constant → slope = 0 → flag = 0 (strict <)."""
    n = 400
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    series = pd.Series(np.full(n, 100.0), index=idx)
    flag = dxy_sma_falling_flag(series, sma_window=200, slope_lookback=20)
    assert (flag == 0).all()


def test_falling_flag_index_preserved():
    n = 300
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    series = pd.Series(np.linspace(120.0, 100.0, n), index=idx)
    flag = dxy_sma_falling_flag(series, sma_window=200, slope_lookback=20)
    pd.testing.assert_index_equal(flag.index, series.index)


def test_falling_flag_v_shape():
    """V-shaped DXY (down then up): flag fires during MA falling, then turns off."""
    n = 600
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    half = n // 2
    down = np.linspace(120.0, 90.0, half)
    up = np.linspace(90.0, 120.0, n - half)
    series = pd.Series(np.concatenate([down, up]), index=idx)
    flag = dxy_sma_falling_flag(series, sma_window=200, slope_lookback=20)
    # SMA still falling well past mid-point because MA lags → some 1s in
    # second half early; eventually settles to 0 once MA inflects
    assert flag.iloc[300:350].sum() > 0  # MA still falling early
    assert flag.iloc[-50:].sum() == 0    # MA rising at end


# ---------------------------------------------------------------------------
# Cross-lib parity (pandas vs hand-rolled numpy) — G7 gate
# ---------------------------------------------------------------------------


def test_falling_flag_numpy_parity_random():
    rng = np.random.RandomState(7)
    n = 600
    arr = (rng.randn(n).cumsum() * 0.3 + 100.0).clip(min=50.0)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    series = pd.Series(arr, index=idx)

    flag_pd = dxy_sma_falling_flag(series, sma_window=200, slope_lookback=20).values
    flag_np = dxy_sma_falling_flag_numpy(arr, sma_window=200, slope_lookback=20)

    assert flag_pd.dtype.kind == "i"
    assert flag_np.dtype.kind == "i"
    np.testing.assert_array_equal(flag_pd, flag_np)


def test_falling_flag_numpy_parity_descending():
    arr = np.linspace(125.0, 85.0, 500)
    flag_np = dxy_sma_falling_flag_numpy(arr, sma_window=200, slope_lookback=20)
    # warmup is sma_window + slope_lookback - 1 = 219
    assert flag_np[:219].sum() == 0
    assert flag_np[219:].sum() == 500 - 219


# ---------------------------------------------------------------------------
# align_signal_to_index — daily DXY → asset bar index
# ---------------------------------------------------------------------------


def test_align_signal_to_daily_index():
    """DXY (daily) → daily gold index. Should ffill across asset's bars."""
    dxy_idx = pd.date_range("2020-01-02", periods=10, freq="B")
    flag = pd.Series([0, 0, 1, 1, 1, 0, 0, 1, 1, 1], index=dxy_idx, dtype=int)
    asset_idx = pd.date_range("2020-01-03", periods=10, freq="B")
    aligned = align_signal_to_index(flag, asset_idx)
    assert len(aligned) == 10
    pd.testing.assert_index_equal(aligned.index, asset_idx)


def test_align_signal_to_intraday_index():
    """Daily DXY signal → 1h gold index propagates within each business day."""
    dxy_idx = pd.date_range("2020-01-02", periods=5, freq="B")
    flag = pd.Series([0, 1, 1, 0, 1], index=dxy_idx, dtype=int)
    asset_idx = pd.date_range("2020-01-02 00:00", "2020-01-08 23:00", freq="1h")
    aligned = align_signal_to_index(flag, asset_idx)
    assert len(aligned) == len(asset_idx)
    mask_jan02 = (asset_idx.date == pd.Timestamp("2020-01-02").date())
    assert (aligned[mask_jan02] == 0).all()
    mask_jan06 = (asset_idx.date == pd.Timestamp("2020-01-06").date())
    # Mon Jan 6: prior business day (Fri Jan 3 = 1) ffilled
    assert (aligned[mask_jan06] == 1).all()


def test_align_pre_signal_data_zero():
    """Asset bars BEFORE first DXY bar should get 0 (no signal yet)."""
    dxy_idx = pd.DatetimeIndex(["2020-01-10", "2020-01-13"])
    flag = pd.Series([1, 1], index=dxy_idx, dtype=int)
    asset_idx = pd.DatetimeIndex(["2020-01-02", "2020-01-03", "2020-01-10", "2020-01-13"])
    aligned = align_signal_to_index(flag, asset_idx)
    assert aligned.loc["2020-01-02"] == 0
    assert aligned.loc["2020-01-03"] == 0
    assert aligned.loc["2020-01-10"] == 1
    assert aligned.loc["2020-01-13"] == 1
