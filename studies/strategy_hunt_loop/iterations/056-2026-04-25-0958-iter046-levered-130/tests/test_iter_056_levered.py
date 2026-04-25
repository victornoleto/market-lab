"""TDD specs for the iter 056 leverage transform on iter 046.

These tests pin down the leverage mechanics independent of iter 046's
combined return stream, then verify pandas/numpy parity.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from levered_iter046 import (  # noqa: E402
    apply_leverage_np,
    apply_leverage_pd,
    daily_borrow_from_annual,
)


# ---------------------------------------------------------------------------
# Leverage transform — pure unit tests
# ---------------------------------------------------------------------------


def test_lev_one_returns_input_unchanged_pandas():
    rng = np.random.default_rng(1)
    series = pd.Series(rng.normal(0.0005, 0.01, size=20),
                       index=pd.date_range("2020-01-01", periods=20, freq="B"))
    out = apply_leverage_pd(series, lev=1.0, borrow_rate_annual=0.035)
    pd.testing.assert_series_equal(
        out.rename(series.name), series, check_names=False,
    )


def test_lev_one_returns_input_unchanged_numpy():
    rng = np.random.default_rng(2)
    arr = rng.normal(0.0005, 0.01, size=20)
    out = apply_leverage_np(arr, lev=1.0, borrow_rate_annual=0.99)
    np.testing.assert_allclose(out, arr, rtol=0, atol=1e-15)


def test_lev_two_zero_borrow_doubles_returns():
    arr = np.array([0.01, -0.005, 0.0, 0.02])
    out = apply_leverage_np(arr, lev=2.0, borrow_rate_annual=0.0)
    np.testing.assert_allclose(out, 2 * arr, rtol=0, atol=1e-15)


def test_borrow_drag_constant_per_bar_at_lev_above_one():
    arr = np.array([0.01, -0.005, 0.0, 0.02])
    daily_b = daily_borrow_from_annual(0.035)
    out_lev_13 = apply_leverage_np(arr, lev=1.3, borrow_rate_annual=0.035)
    expected = 1.3 * arr - 0.3 * daily_b
    np.testing.assert_allclose(out_lev_13, expected, rtol=0, atol=1e-15)


def test_daily_borrow_from_annual_matches_compounding_identity():
    annual = 0.035
    daily = daily_borrow_from_annual(annual)
    # Compounding 252 days reproduces the annual rate.
    np.testing.assert_allclose((1 + daily) ** 252 - 1, annual, rtol=1e-12, atol=0)


def test_daily_borrow_zero_at_zero_rate():
    assert daily_borrow_from_annual(0.0) == 0.0


def test_lev_le_zero_raises():
    with pytest.raises(ValueError, match="lev must be > 0"):
        apply_leverage_np(np.array([0.0]), lev=0.0, borrow_rate_annual=0.035)
    with pytest.raises(ValueError, match="lev must be > 0"):
        apply_leverage_pd(pd.Series([0.0]), lev=-0.5, borrow_rate_annual=0.035)


def test_negative_borrow_rate_raises():
    with pytest.raises(ValueError, match="borrow_rate_annual must be >= 0"):
        apply_leverage_np(np.array([0.0]), lev=1.3, borrow_rate_annual=-0.01)
    with pytest.raises(ValueError, match="borrow_rate_annual must be >= 0"):
        daily_borrow_from_annual(-1e-6)


# ---------------------------------------------------------------------------
# Pandas/numpy parity on identical input
# ---------------------------------------------------------------------------


def test_pandas_numpy_parity_on_identical_returns():
    rng = np.random.default_rng(3)
    arr = rng.normal(0.0005, 0.01, size=200)
    series = pd.Series(arr, index=pd.date_range("2020-01-01", periods=200, freq="B"))
    pd_out = apply_leverage_pd(series, lev=1.3, borrow_rate_annual=0.035)
    np_out = apply_leverage_np(arr, lev=1.3, borrow_rate_annual=0.035)
    np.testing.assert_allclose(pd_out.values, np_out, rtol=1e-15, atol=1e-15)


# ---------------------------------------------------------------------------
# Sharpe preservation under pure leverage (no borrow)
# ---------------------------------------------------------------------------


def test_sharpe_preserved_under_pure_leverage_no_borrow():
    """Sharpe = mean/std × √252; under r_lev = lev × r both scale by lev → ratio invariant."""
    rng = np.random.default_rng(4)
    arr = rng.normal(0.0008, 0.01, size=2000)
    out = apply_leverage_np(arr, lev=1.7, borrow_rate_annual=0.0)
    sharpe_in = arr.mean() / arr.std(ddof=0) * np.sqrt(252)
    sharpe_out = out.mean() / out.std(ddof=0) * np.sqrt(252)
    np.testing.assert_allclose(sharpe_out, sharpe_in, rtol=1e-12, atol=0)


def test_sharpe_drag_under_borrow_within_analytic_bound():
    """Drag ≈ (lev-1) * daily_borrow / (lev × σ); compare numerical vs formula."""
    rng = np.random.default_rng(5)
    arr = rng.normal(0.0008, 0.01, size=5000)
    lev = 1.3
    annual_borrow = 0.035
    daily_b = daily_borrow_from_annual(annual_borrow)
    out = apply_leverage_np(arr, lev=lev, borrow_rate_annual=annual_borrow)
    sigma = arr.std(ddof=0)
    sharpe_in = arr.mean() / sigma * np.sqrt(252)
    sharpe_out = out.mean() / out.std(ddof=0) * np.sqrt(252)
    expected_drag = (lev - 1) * daily_b * np.sqrt(252) / (lev * sigma)
    actual_drag = sharpe_in - sharpe_out
    np.testing.assert_allclose(actual_drag, expected_drag, rtol=1e-10, atol=1e-12)


# ---------------------------------------------------------------------------
# CAGR scaling
# ---------------------------------------------------------------------------


def test_cagr_scales_with_lev_minus_geometric_drag_minus_borrow():
    """G_lev = lev × G_strat - lev(lev-1) × σ²/2 - (lev-1) × borrow.

    Verified numerically up to discretization noise on a generated series.
    """
    rng = np.random.default_rng(6)
    n = 252 * 10  # 10-year simulation
    arr = rng.normal(0.0008, 0.01, size=n)
    lev = 1.5
    annual_borrow = 0.04
    daily_b = daily_borrow_from_annual(annual_borrow)
    out = apply_leverage_np(arr, lev=lev, borrow_rate_annual=annual_borrow)

    eq_in = np.cumprod(1 + arr)
    eq_out = np.cumprod(1 + out)
    cagr_in = float(eq_in[-1]) ** (252 / n) - 1
    cagr_out = float(eq_out[-1]) ** (252 / n) - 1

    sigma = arr.std(ddof=0) * np.sqrt(252)
    analytic_drag_geom = lev * (lev - 1) * sigma**2 / 2
    analytic_drag_borrow = (lev - 1) * annual_borrow
    expected_cagr_out = lev * cagr_in - analytic_drag_geom - analytic_drag_borrow

    # Analytic identity holds in continuous time; daily compounding plus
    # non-zero higher central moments add ~1-2pp error at lev=1.5.
    # Tolerance pinned at 2pp (sanity check on direction + magnitude).
    np.testing.assert_allclose(cagr_out, expected_cagr_out, atol=0.02)
