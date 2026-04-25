"""TDD specs for iter 060 leverage transform on iter 058 stream.

Pin down the leverage mechanics independent of iter 058's combined
stream, verify pandas/numpy parity, and confirm the Sharpe identity
at b = rf (zero-drag case justifying the 2.5% futures-borrow path).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from levered_iter058 import (  # noqa: E402
    apply_leverage_np,
    apply_leverage_pd,
    daily_borrow_from_annual,
)


# ---------------------------------------------------------------------------
# daily_borrow_from_annual
# ---------------------------------------------------------------------------


def test_daily_borrow_zero_returns_zero():
    assert daily_borrow_from_annual(0.0) == pytest.approx(0.0, abs=1e-12)


def test_daily_borrow_2pct_matches_compounded():
    # (1.02)^(1/252) - 1
    expected = (1.02) ** (1.0 / 252.0) - 1.0
    assert daily_borrow_from_annual(0.02) == pytest.approx(expected, abs=1e-12)


def test_daily_borrow_2pt5pct_matches_compounded():
    # 2.5% futures-implied financing rate
    expected = (1.025) ** (1.0 / 252.0) - 1.0
    assert daily_borrow_from_annual(0.025) == pytest.approx(expected, abs=1e-12)


def test_daily_borrow_negative_raises():
    with pytest.raises(ValueError, match="must be >= 0"):
        daily_borrow_from_annual(-0.001)


# ---------------------------------------------------------------------------
# apply_leverage_pd / apply_leverage_np — invariants
# ---------------------------------------------------------------------------


def _make_returns(n: int = 100, seed: int = 42) -> pd.Series:
    rng = np.random.default_rng(seed)
    raw = rng.normal(loc=0.0003, scale=0.005, size=n)
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.Series(raw, index=idx, name="r_058")


def test_lev_one_is_identity_pd():
    """lev=1.0 returns the input unchanged regardless of borrow rate."""
    r = _make_returns()
    out = apply_leverage_pd(r, lev=1.0, borrow_rate_annual=0.025)
    pd.testing.assert_series_equal(
        out, r.rename("r_058_levered"), check_names=True,
    )


def test_lev_one_is_identity_np():
    r = _make_returns().values
    out = apply_leverage_np(r, lev=1.0, borrow_rate_annual=0.10)
    np.testing.assert_array_almost_equal(out, r, decimal=15)


def test_lev_two_zero_borrow_doubles_returns():
    """lev=2.0, b=0 → exactly 2.0 × r (no drag)."""
    r = _make_returns().values
    out = apply_leverage_np(r, lev=2.0, borrow_rate_annual=0.0)
    np.testing.assert_array_almost_equal(out, 2.0 * r, decimal=15)


def test_borrow_drag_constant_per_bar():
    """At lev>1, borrow drag is constant (not return-dependent)."""
    r = _make_returns()
    lev, b = 1.5, 0.025
    out = apply_leverage_pd(r, lev=lev, borrow_rate_annual=b)
    diff = out - lev * r
    daily_borrow = daily_borrow_from_annual(b)
    expected_drag = -(lev - 1.0) * daily_borrow
    # All elements equal the expected drag (constant per bar).
    np.testing.assert_array_almost_equal(
        diff.values, np.full(len(r), expected_drag), decimal=15,
    )


def test_pandas_numpy_parity():
    """Pandas and numpy implementations must match to 1e-12."""
    r = _make_returns(n=500, seed=7)
    out_pd = apply_leverage_pd(r, lev=1.5, borrow_rate_annual=0.025)
    out_np = apply_leverage_np(r.values, lev=1.5, borrow_rate_annual=0.025)
    np.testing.assert_array_almost_equal(out_pd.values, out_np, decimal=12)


# ---------------------------------------------------------------------------
# Sharpe identity at b = rf — the core thesis of iter 060
# ---------------------------------------------------------------------------


def _annualized_sharpe(returns: np.ndarray, *, rf: float = 0.0) -> float:
    """Annualized Sharpe from daily simple returns, no rf adjustment."""
    excess = returns - rf / 252.0
    mu = float(np.mean(excess))
    sigma = float(np.std(excess, ddof=0))
    if sigma <= 1e-18:
        return 0.0
    return mu / sigma * np.sqrt(252.0)


def test_sharpe_preserved_when_borrow_equals_rf():
    """When borrow_rate_annual == rf, Sharpe is preserved (compound-error only).

    This is the core empirical thesis of iter 060: futures-implied
    financing at ~T-bill rate adds no Sharpe drag, leaving the
    leverage transform Sharpe-neutral. The preservation is exact in
    the simple-rate sense (rf/252) but our daily_borrow_from_annual
    uses compound rate ((1+rf)^(1/252)-1), so a tiny residual drag of
    order rf²/252² per bar remains. Real-world futures financing is
    T-bill + 30-50bps (not exactly rf), but the limit case proves the
    mechanism.
    """
    rng = np.random.default_rng(11)
    raw = rng.normal(loc=0.0004, scale=0.005, size=2000)  # ~10% annual
    rf = 0.02
    sharpe_unlev = _annualized_sharpe(raw, rf=rf)

    # Apply leverage to TOTAL returns at b=rf, then compute Sharpe of
    # the levered total (subtracting rf/252 inside _annualized_sharpe).
    levered_total = apply_leverage_np(
        raw, lev=1.5, borrow_rate_annual=rf,
    )
    sharpe_lev = _annualized_sharpe(levered_total, rf=rf)
    # At b = rf with compound daily_borrow, Sharpe is preserved to
    # within ~1e-3 (compound-vs-simple residual is order rf²/n²).
    assert sharpe_lev == pytest.approx(sharpe_unlev, abs=2e-3)


def test_sharpe_drag_at_2pt5pct_borrow_matches_formula():
    """At b > rf, Sharpe drag matches (lev-1)*(b-rf)/(lev*sigma_annual).

    iter 060 hypothesis: at lev=1.5, b=0.025, rf=0.02, sigma_annual~0.055,
    drag ≈ 0.5 × 0.005 / (1.5 × 0.055) ≈ 0.030.
    """
    rng = np.random.default_rng(13)
    n = 5000
    sigma_annual = 0.055
    sigma_daily = sigma_annual / np.sqrt(252.0)
    mu_daily = 0.001  # arbitrary
    raw = rng.normal(loc=mu_daily, scale=sigma_daily, size=n)
    rf = 0.02
    b = 0.025
    lev = 1.5

    sharpe_unlev = _annualized_sharpe(raw, rf=rf)
    # Apply leverage with proper borrow accounting:
    #   r_total_lev = lev * (r - rf_d) + rf_d - (lev-1) * (daily_borrow - rf_d)
    # Simplification: r_lev_total = lev * r - (lev-1) * daily_borrow.
    lev_returns = apply_leverage_np(raw, lev=lev, borrow_rate_annual=b)
    sharpe_lev = _annualized_sharpe(lev_returns, rf=rf)

    drag_observed = sharpe_unlev - sharpe_lev
    # Predicted drag using daily-form (compound) borrow rates:
    #   drag = sqrt(252) * (lev-1) * (daily_borrow_b - rf/252) / (lev * sigma_daily)
    daily_borrow_b = (1.0 + b) ** (1.0 / 252.0) - 1.0
    sigma_daily = sigma_annual / np.sqrt(252.0)
    drag_predicted = (
        np.sqrt(252.0) * (lev - 1.0) * (daily_borrow_b - rf / 252.0)
        / (lev * sigma_daily)
    )
    # Daily-form formula matches observed drag to within 5% at n=5000.
    # The simple-form formula (lev-1)*(b-rf)/(lev*sigma_annual) over-
    # predicts by ~7% (compound vs simple).
    assert drag_observed == pytest.approx(drag_predicted, rel=0.05)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_validation_lev_zero_raises():
    with pytest.raises(ValueError, match="lev must be > 0"):
        apply_leverage_pd(_make_returns(), lev=0.0, borrow_rate_annual=0.025)


def test_validation_lev_negative_raises():
    with pytest.raises(ValueError, match="lev must be > 0"):
        apply_leverage_np(
            _make_returns().values, lev=-0.5, borrow_rate_annual=0.025,
        )


def test_validation_borrow_negative_raises():
    with pytest.raises(ValueError, match="must be >= 0"):
        apply_leverage_pd(_make_returns(), lev=1.5, borrow_rate_annual=-0.001)


def test_levered_series_has_same_index_as_input():
    r = _make_returns(n=200, seed=99)
    out = apply_leverage_pd(r, lev=1.5, borrow_rate_annual=0.025)
    pd.testing.assert_index_equal(out.index, r.index)
