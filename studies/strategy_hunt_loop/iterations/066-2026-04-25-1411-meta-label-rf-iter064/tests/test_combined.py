"""Iter 066 — Combined gate (deterministic post-prediction transform)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from combined_iter064_meta import (  # noqa: E402
    gate_iter064_with_meta,
    gate_iter064_with_meta_np,
)


def test_gate_passthrough_on_full_long():
    n = 100
    idx = pd.date_range("2010", periods=n, freq="B")
    r = pd.Series(np.full(n, 0.001), index=idx)
    pred = pd.Series(np.ones(n, dtype=int), index=idx)
    out = gate_iter064_with_meta(r, pred, cost_per_flip=0.0)
    # First bar pred[t-1]=0 → cash; rest = r[t]
    np.testing.assert_almost_equal(out.iloc[0], 0.0)
    np.testing.assert_array_almost_equal(out.iloc[1:].values, r.iloc[1:].values)


def test_gate_zero_on_full_cash():
    n = 50
    idx = pd.date_range("2010", periods=n, freq="B")
    r = pd.Series(np.full(n, 0.001), index=idx)
    pred = pd.Series(np.zeros(n, dtype=int), index=idx)
    out = gate_iter064_with_meta(r, pred, cost_per_flip=5e-4)
    assert (out == 0.0).all()


def test_gate_cost_on_flip():
    """One flip on/off costs 1 × cost_per_flip per direction."""
    n = 5
    idx = pd.date_range("2010", periods=n, freq="B")
    r = pd.Series(np.zeros(n), index=idx)
    # pred sequence: 0 1 1 0 0
    pred = pd.Series([0, 1, 1, 0, 0], index=idx)
    out = gate_iter064_with_meta(r, pred, cost_per_flip=1e-3)
    # flips at t=1 (0→1) and t=3 (1→0): each costs 1e-3.
    assert abs(out.iloc[1] - (-1e-3)) < 1e-12
    assert abs(out.iloc[3] - (-1e-3)) < 1e-12
    # No flip on bars 0,2,4 → 0.
    assert out.iloc[0] == 0.0
    assert out.iloc[2] == 0.0
    assert out.iloc[4] == 0.0


def test_gate_signal_lag_one_bar():
    """pred[t-1] applies to r[t], not pred[t]."""
    idx = pd.date_range("2010", periods=4, freq="B")
    r = pd.Series([0.01, 0.02, 0.03, -0.01], index=idx)
    pred = pd.Series([0, 1, 0, 1], index=idx)
    out = gate_iter064_with_meta(r, pred, cost_per_flip=0.0)
    # bar 0: pred[t-1] = 0 (init) → 0
    # bar 1: pred[t-1] = 0 → 0
    # bar 2: pred[t-1] = 1 → r[2] = 0.03
    # bar 3: pred[t-1] = 0 → 0
    np.testing.assert_array_almost_equal(out.values, [0.0, 0.0, 0.03, 0.0])


def test_g7_numpy_parity():
    rng = np.random.default_rng(42)
    n = 1000
    idx = pd.date_range("2010", periods=n, freq="B")
    r_arr = rng.normal(0.0005, 0.01, n)
    pred_arr = rng.integers(0, 2, n)
    r_pd = pd.Series(r_arr, index=idx)
    pred_pd = pd.Series(pred_arr, index=idx)
    out_pd = gate_iter064_with_meta(r_pd, pred_pd, cost_per_flip=5e-4)
    out_np = gate_iter064_with_meta_np(r_arr, pred_arr, cost_per_flip=5e-4)
    max_diff = np.max(np.abs(out_pd.values - out_np))
    assert max_diff < 1e-12, f"pandas-numpy parity violated: {max_diff}"


def test_gate_handles_nan_predictions_as_cash():
    n = 5
    idx = pd.date_range("2010", periods=n, freq="B")
    r = pd.Series([0.01, 0.01, 0.01, 0.01, 0.01], index=idx)
    pred = pd.Series([np.nan, 1.0, 1.0, np.nan, 1.0], index=idx)
    out = gate_iter064_with_meta(r, pred, cost_per_flip=0.0)
    # NaN treated as cash (0). pred sequence: 0 1 1 0 1
    # Lagged: 0 0 1 1 0 → returns: 0 0 0.01 0.01 0
    np.testing.assert_array_almost_equal(out.values, [0.0, 0.0, 0.01, 0.01, 0.0])
