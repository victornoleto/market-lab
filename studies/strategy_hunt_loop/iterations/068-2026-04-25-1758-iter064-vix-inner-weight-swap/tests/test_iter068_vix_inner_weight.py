"""TDD for iter 068 — VIX-conditional inner-weight swap.

Tests the contract of `combine_with_vix_inner_weight` and its numpy
reference. Mirrors the shape/behaviour conventions used in iter 065's
`apply_vix_lev_gate` test suite.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ITER_DIR))

from vix_inner_weight import combine_with_vix_inner_weight  # noqa: E402
from numpy_reference_iter068 import combine_with_vix_inner_weight_np  # noqa: E402


def _make_index(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2020-01-02", periods=n)


def test_shape_parity():
    idx = _make_index(50)
    r_046 = pd.Series(np.full(50, 0.001), index=idx)
    r_qqqt = pd.Series(np.full(50, 0.002), index=idx)
    vix = pd.Series(np.full(50, 15.0), index=idx)
    out = combine_with_vix_inner_weight(r_046, r_qqqt, vix)
    assert len(out) == 50
    assert out.index.equals(idx)


def test_constant_calm_vix_equals_static_blend():
    """When VIX < threshold always, output = w_calm convex combo (minus
    the single seed-bar flip cost from bar 0's bfill seed)."""
    idx = _make_index(30)
    r_046 = pd.Series(np.full(30, 0.001), index=idx)
    r_qqqt = pd.Series(np.full(30, 0.002), index=idx)
    vix = pd.Series(np.full(30, 10.0), index=idx)  # always calm
    out = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=0.20, w_qqqt_stress=0.05, vix_threshold=20.0,
        cost_bps=0.0,  # zero cost to isolate weight check
    )
    expected_per_bar = 0.80 * 0.001 + 0.20 * 0.002
    assert np.allclose(out.values, expected_per_bar, atol=1e-12)


def test_constant_stress_vix_equals_static_blend():
    idx = _make_index(30)
    r_046 = pd.Series(np.full(30, 0.001), index=idx)
    r_qqqt = pd.Series(np.full(30, 0.002), index=idx)
    vix = pd.Series(np.full(30, 30.0), index=idx)  # always stress
    out = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=0.20, w_qqqt_stress=0.05, vix_threshold=20.0,
        cost_bps=0.0,
    )
    expected_per_bar = 0.95 * 0.001 + 0.05 * 0.002
    assert np.allclose(out.values, expected_per_bar, atol=1e-12)


def test_no_lookahead_uses_vix_t_minus_1():
    """If we engineer VIX so bar t-1 is calm and bar t is stress, the
    weight at bar t should still reflect calm (uses VIX[t-1])."""
    idx = _make_index(10)
    r_046 = pd.Series(np.full(10, 0.001), index=idx)
    r_qqqt = pd.Series(np.full(10, 0.010), index=idx)
    # VIX: bar 0 calm, bar 1 stress, rest stress
    vix_vals = np.array([10.0, 30.0, 30.0, 30.0, 30.0,
                         30.0, 30.0, 30.0, 30.0, 30.0])
    vix = pd.Series(vix_vals, index=idx)
    out = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=0.20, w_qqqt_stress=0.05, vix_threshold=20.0,
        cost_bps=0.0,
    )
    # Bar 0: VIX[t-1] is bfilled to bar 0's value (10) → calm → 0.20
    # Bar 1: VIX[t-1] = 10 (bar 0) → calm → 0.20
    # Bar 2: VIX[t-1] = 30 (bar 1) → stress → 0.05
    expected = np.array([
        0.80 * 0.001 + 0.20 * 0.010,  # bar 0: calm seed
        0.80 * 0.001 + 0.20 * 0.010,  # bar 1: calm (uses VIX[0]=10)
        0.95 * 0.001 + 0.05 * 0.010,  # bar 2: stress (uses VIX[1]=30)
    ])
    assert np.allclose(out.values[:3], expected, atol=1e-12)


def test_total_exposure_strictly_one():
    """Sum of inner weights at every bar equals 1.0 within fp tolerance."""
    rng = np.random.default_rng(42)
    n = 200
    idx = _make_index(n)
    r_046 = pd.Series(rng.normal(0, 0.01, n), index=idx)
    r_qqqt = pd.Series(rng.normal(0, 0.012, n), index=idx)
    vix = pd.Series(rng.uniform(10, 35, n), index=idx)
    out = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=0.20, w_qqqt_stress=0.05, vix_threshold=20.0,
        cost_bps=0.0,
        return_diagnostics=True,
    )
    diag = out.attrs["diagnostics"]
    w_046 = diag["w_046"]
    w_qqqt = diag["w_qqqt"]
    total = w_046 + w_qqqt
    assert np.allclose(total, 1.0, atol=1e-12)


def test_cost_proportional_to_weight_flip():
    """One flip from calm → stress should subtract cost_bps × |Δw_qqqt|
    on the bar where the flip happens."""
    idx = _make_index(5)
    r_046 = pd.Series(np.zeros(5), index=idx)  # zero return isolates cost
    r_qqqt = pd.Series(np.zeros(5), index=idx)
    vix_vals = np.array([10.0, 10.0, 30.0, 30.0, 30.0])
    vix = pd.Series(vix_vals, index=idx)
    out = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=0.20, w_qqqt_stress=0.05, vix_threshold=20.0,
        cost_bps=5.0,
    )
    # Expected weights (using VIX[t-1] with bfill for bar 0):
    # bar 0: VIX[-1]=NaN → bfilled to VIX[0]=10 → calm → w_qqqt=0.20
    # bar 1: VIX[0]=10 → calm → 0.20
    # bar 2: VIX[1]=10 → calm → 0.20
    # bar 3: VIX[2]=30 → stress → 0.05  (← FLIP HERE)
    # bar 4: VIX[3]=30 → stress → 0.05
    # cost only on bar 3: |0.05 - 0.20| × 5 bps = 0.15 × 0.0005 = 0.000075
    expected = np.array([0.0, 0.0, 0.0, -0.000075, 0.0])
    assert np.allclose(out.values, expected, atol=1e-15)


def test_pandas_vs_numpy_parity():
    """Cross-library reference matches the pandas engine to fp tolerance."""
    rng = np.random.default_rng(7)
    n = 500
    idx = _make_index(n)
    r_046 = pd.Series(rng.normal(0.0005, 0.008, n), index=idx)
    r_qqqt = pd.Series(rng.normal(0.0008, 0.012, n), index=idx)
    vix = pd.Series(rng.uniform(8, 40, n), index=idx)

    out_pd = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=0.20, w_qqqt_stress=0.05, vix_threshold=20.0,
        cost_bps=5.0,
    )
    out_np = combine_with_vix_inner_weight_np(
        r_046.to_numpy(), r_qqqt.to_numpy(), vix.to_numpy(),
        w_qqqt_calm=0.20, w_qqqt_stress=0.05, vix_threshold=20.0,
        cost_bps=5.0,
    )
    max_abs_diff = np.max(np.abs(out_pd.to_numpy() - out_np))
    assert max_abs_diff < 1e-12, f"max_abs_diff={max_abs_diff}"


def test_vix_reindex_with_ffill():
    """VIX gaps (e.g., holiday) should ffill before being used."""
    idx = _make_index(10)
    r_046 = pd.Series(np.full(10, 0.001), index=idx)
    r_qqqt = pd.Series(np.full(10, 0.005), index=idx)
    # VIX missing at index[3] and index[7]; should ffill from prior values
    vix_vals = np.array([15.0, 15.0, 15.0, np.nan, 15.0,
                         15.0, 15.0, np.nan, 15.0, 15.0])
    vix = pd.Series(vix_vals, index=idx)
    out = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=0.20, w_qqqt_stress=0.05, vix_threshold=20.0,
        cost_bps=0.0,
    )
    # All should be calm → constant blend, NO NaN
    expected_per_bar = 0.80 * 0.001 + 0.20 * 0.005
    assert not np.any(np.isnan(out.values))
    assert np.allclose(out.values, expected_per_bar, atol=1e-12)


def test_negative_weights_rejected():
    idx = _make_index(20)
    r_046 = pd.Series(np.full(20, 0.001), index=idx)
    r_qqqt = pd.Series(np.full(20, 0.001), index=idx)
    vix = pd.Series(np.full(20, 15.0), index=idx)
    with pytest.raises(ValueError, match="w_qqqt_calm must be in"):
        combine_with_vix_inner_weight(
            r_046, r_qqqt, vix, w_qqqt_calm=-0.1,
        )
    with pytest.raises(ValueError, match="w_qqqt_stress must be in"):
        combine_with_vix_inner_weight(
            r_046, r_qqqt, vix, w_qqqt_stress=1.5,
        )


def test_negative_cost_bps_rejected():
    idx = _make_index(20)
    r_046 = pd.Series(np.full(20, 0.001), index=idx)
    r_qqqt = pd.Series(np.full(20, 0.001), index=idx)
    vix = pd.Series(np.full(20, 15.0), index=idx)
    with pytest.raises(ValueError, match="cost_bps must be"):
        combine_with_vix_inner_weight(
            r_046, r_qqqt, vix, cost_bps=-1.0,
        )


def test_negative_vix_threshold_rejected():
    idx = _make_index(20)
    r_046 = pd.Series(np.full(20, 0.001), index=idx)
    r_qqqt = pd.Series(np.full(20, 0.001), index=idx)
    vix = pd.Series(np.full(20, 15.0), index=idx)
    with pytest.raises(ValueError, match="vix_threshold must be"):
        combine_with_vix_inner_weight(
            r_046, r_qqqt, vix, vix_threshold=-5.0,
        )


def test_too_short_input_rejected():
    idx = _make_index(1)
    r_046 = pd.Series([0.001], index=idx)
    r_qqqt = pd.Series([0.001], index=idx)
    vix = pd.Series([15.0], index=idx)
    with pytest.raises(ValueError, match="must have"):
        combine_with_vix_inner_weight(r_046, r_qqqt, vix)


def test_no_overlap_rejected():
    idx_a = pd.bdate_range("2020-01-02", periods=20)
    idx_b = pd.bdate_range("2025-01-02", periods=20)
    r_046 = pd.Series(np.full(20, 0.001), index=idx_a)
    r_qqqt = pd.Series(np.full(20, 0.001), index=idx_b)
    vix = pd.Series(np.full(20, 15.0), index=idx_a)
    with pytest.raises(ValueError, match="overlap"):
        combine_with_vix_inner_weight(r_046, r_qqqt, vix)
