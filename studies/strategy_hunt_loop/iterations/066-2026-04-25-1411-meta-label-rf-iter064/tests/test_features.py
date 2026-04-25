"""Iter 066 — Feature engineering invariants."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from feature_engineering import (  # noqa: E402
    FEATURE_COLS,
    build_feature_matrix,
    label_positive_return,
    rolling_mdd,
    rolling_sharpe,
    sma_distance,
    warmup_drop,
)


@pytest.fixture
def synth_returns() -> pd.Series:
    rng = np.random.default_rng(0)
    n = 500
    idx = pd.date_range("2010-01-01", periods=n, freq="B")
    r = pd.Series(rng.normal(0.0005, 0.01, n), index=idx)
    return r


@pytest.fixture
def synth_prices() -> pd.Series:
    rng = np.random.default_rng(1)
    n = 500
    idx = pd.date_range("2010-01-01", periods=n, freq="B")
    rets = rng.normal(0.0005, 0.01, n)
    eq = (1.0 + rets).cumprod() * 100.0
    return pd.Series(eq, index=idx)


def test_rolling_sharpe_window_warmup_nan(synth_returns):
    rs = rolling_sharpe(synth_returns, window=21)
    assert rs.iloc[:20].isna().all(), "warmup bars must be NaN"
    assert rs.iloc[20:].abs().max() < 100.0  # sanity


def test_rolling_mdd_warmup_nan(synth_returns):
    mdd = rolling_mdd(synth_returns, window=63)
    assert mdd.iloc[:62].isna().all()
    assert mdd.iloc[62:].min() >= 0.0  # mdd is non-negative magnitude


def test_sma_distance_known_value():
    """SMA200 distance: when price = SMA, distance = 0."""
    prices = pd.Series(np.full(250, 100.0), index=pd.date_range("2010", periods=250))
    d = sma_distance(prices, window=200)
    # SMA = 100 from bar 199 onward, distance = 0
    assert abs(d.iloc[200]) < 1e-12


def test_build_feature_matrix_shifts_one_bar(synth_returns, synth_prices):
    vix = pd.Series(np.full(500, 20.0), index=synth_returns.index)
    t10y3m = pd.Series(np.full(500, 1.5), index=synth_returns.index)
    X = build_feature_matrix(synth_returns, synth_prices, vix, t10y3m)
    # All features shifted +1: row 0 must be all NaN.
    assert X.iloc[0].isna().all(), "shift(1) must NaN-fill row 0"
    assert list(X.columns) == list(FEATURE_COLS)


def test_label_positive_return_binary(synth_returns):
    y = label_positive_return(synth_returns)
    assert set(y.unique()).issubset({0, 1})
    assert (y == (synth_returns > 0).astype(int)).all()


def test_warmup_drop_removes_nan_rows(synth_returns, synth_prices):
    vix = pd.Series(np.full(500, 20.0), index=synth_returns.index)
    t10y3m = pd.Series(np.full(500, 1.5), index=synth_returns.index)
    X = build_feature_matrix(synth_returns, synth_prices, vix, t10y3m)
    y = label_positive_return(synth_returns)
    Xc, yc = warmup_drop(X, y)
    assert Xc.notna().all().all(), "all features must be non-NaN after warmup drop"
    assert len(Xc) == len(yc)
    # warmup ≥ max(21,63,200) due to SMA-200 / MDD-63 / Sharpe-21 + 1 shift.
    assert len(synth_returns) - len(Xc) >= 200


def test_no_peek_via_shifted_value(synth_returns, synth_prices):
    """build_feature_matrix(t).vix == vix(t-1) (after fillna for VIX gaps)."""
    n = len(synth_returns)
    vix = pd.Series(np.arange(n, dtype=float), index=synth_returns.index, name="vix")
    t10y3m = pd.Series(np.full(n, 1.5), index=synth_returns.index)
    X = build_feature_matrix(synth_returns, synth_prices, vix, t10y3m)
    # Bar i (i ≥ 1) must see vix value (i-1)
    assert X["vix"].iloc[5] == 4.0
    assert X["vix"].iloc[100] == 99.0
