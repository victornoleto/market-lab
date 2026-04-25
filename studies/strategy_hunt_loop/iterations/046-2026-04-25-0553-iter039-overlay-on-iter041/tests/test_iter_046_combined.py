"""Iter 046 — TDD specs for the 50/50 convex combo of iter 041 + iter 039.

These specs MUST pass before the backtest runs (engine-correctness gate
before measurements). Mirrors iter 045's specs with iter 037 → iter 041
substitution; adds an extra spec for the regime-gate identity reduction
(``calm_weights == stress_weights`` collapses to the un-gated baseline).

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ITER_DIR))

from combined_041_039 import compute_combined_returns  # noqa: E402
from numpy_reference_combined_046 import (  # noqa: E402
    build_regime_array,
    compute_combined_returns_np,
)


def _make_index(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2020-01-02", periods=n, freq="B")


def _make_prices(n: int, seed: int = 0) -> dict[str, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = _make_index(n)
    series = {}
    for ticker, drift, vol in [
        ("SPY", 0.0006, 0.011),
        ("IEF", 0.00015, 0.004),
        ("GLD", 0.00025, 0.009),
        ("QQQ", 0.0008, 0.014),
        ("IWM", 0.0005, 0.013),
    ]:
        rets = rng.normal(drift, vol, n)
        prices = 100.0 * np.cumprod(1.0 + rets)
        series[ticker] = pd.Series(prices, index=idx, name=ticker)
    return series


def _make_vix(n: int, seed: int = 99) -> pd.Series:
    rng = np.random.default_rng(seed)
    raw = 18.0 + rng.standard_normal(n) * 4.0
    return pd.Series(np.clip(raw, 8.0, 80.0), index=_make_index(n), name="VIX")


# ---------------------------------------------------------------------------
# 1. Reduces to iter 041 when w_039 = 0
# ---------------------------------------------------------------------------

def test_reduces_to_iter_041_when_w039_zero():
    """w_041=1, w_039=0 → combined equals iter 041 net (on the inner-join)."""
    p = _make_prices(400, seed=1)
    vix = _make_vix(400, seed=2)

    combined, r_041, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
        w_041=1.0, w_039=0.0,
    )
    assert combined.index.equals(r_041.index)
    np.testing.assert_allclose(combined.values, r_041.values, atol=1e-15)


# ---------------------------------------------------------------------------
# 2. Reduces to iter 039 when w_041 = 0
# ---------------------------------------------------------------------------

def test_reduces_to_iter_039_when_w041_zero():
    """w_041=0, w_039=1 → combined equals iter 039 net."""
    p = _make_prices(400, seed=3)
    vix = _make_vix(400, seed=4)

    combined, r_041, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
        w_041=0.0, w_039=1.0,
    )
    assert combined.index.equals(r_039.index)
    np.testing.assert_allclose(combined.values, r_039.values, atol=1e-15)


# ---------------------------------------------------------------------------
# 3. 50/50 returns the arithmetic mean of the two streams
# ---------------------------------------------------------------------------

def test_50_50_combo_is_arithmetic_mean():
    p = _make_prices(400, seed=5)
    vix = _make_vix(400, seed=6)
    combined, r_041, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
        w_041=0.5, w_039=0.5,
    )
    expected = (r_041 + r_039) / 2.0
    np.testing.assert_allclose(combined.values, expected.values, atol=1e-15)


# ---------------------------------------------------------------------------
# 4. Combined index is the intersection of iter 041 and iter 039 indexes
# ---------------------------------------------------------------------------

def test_combined_index_is_intersection():
    p = _make_prices(500, seed=7)
    vix = _make_vix(500, seed=8)
    combined, r_041, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
    )
    expected = r_041.index.intersection(r_039.index)
    assert combined.index.equals(expected)


# ---------------------------------------------------------------------------
# 5. Cost is intrinsic; combined inherits both. Use controlled calm-only
# regime by forcing VIX < 20 always (so weights = calm_weights throughout).
# ---------------------------------------------------------------------------

def test_cost_inherited_from_subcomponents_calm_regime():
    """With calm-only VIX (< 20 always), iter 041 reduces to a static
    stack at calm_weights {0.70, 0.40, 0.40} → scale 1.50× → bar-0
    setup cost = 1.50 * 2 bps = 3 bps.
    """
    p = _make_prices(50, seed=9)
    n = len(p["SPY"])
    # Force a calm-only regime: VIX clipped < 20 throughout.
    vix = pd.Series(np.full(n, 12.0), index=_make_index(n), name="VIX")
    combined, r_041, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
        cost_bps_per_leg=0.0002, cost_bps_per_roll=5.0,
    )
    r_eq = p["SPY"].pct_change().dropna().iloc[0]
    r_bd = p["IEF"].pct_change().dropna().iloc[0]
    r_gld = p["GLD"].pct_change().dropna().iloc[0]
    # iter 041 calm weights
    eq_w, bd_w, gld_w = 0.70, 0.40, 0.40
    gross_041_bar0 = eq_w * r_eq + bd_w * r_bd + gld_w * r_gld
    setup_cost = (eq_w + bd_w + gld_w) * 0.0002
    expected_041_bar0 = gross_041_bar0 - setup_cost
    assert r_041.iloc[0] == pytest.approx(expected_041_bar0, abs=1e-12)


# ---------------------------------------------------------------------------
# 6. calm_weights == stress_weights collapses iter 041 to a static stack
# (regime layer becomes a no-op; engine reduces to the un-gated 3-leg).
# ---------------------------------------------------------------------------

def test_identity_when_calm_equals_stress_static_baseline():
    """When calm_weights == stress_weights, regime modulation has no
    effect — iter 041 net should equal the same static stack at those
    weights, regardless of VIX."""
    p = _make_prices(300, seed=21)
    vix_calm = pd.Series(np.full(300, 12.0), index=_make_index(300), name="VIX")
    vix_stress = pd.Series(np.full(300, 28.0), index=_make_index(300), name="VIX")

    fixed = {"eq_w": 0.65, "bd_w": 0.42, "gld_w": 0.42}

    combined_calm, r_041_calm, _ = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix_calm,
        calm_weights=fixed, stress_weights=fixed,
        w_041=1.0, w_039=0.0,
    )
    combined_stress, r_041_stress, _ = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix_stress,
        calm_weights=fixed, stress_weights=fixed,
        w_041=1.0, w_039=0.0,
    )
    # When weights coincide, the regime layer is a no-op → the two runs
    # must agree exactly bar-for-bar despite VIX differing massively.
    np.testing.assert_allclose(
        r_041_calm.values, r_041_stress.values, atol=1e-15,
    )


# ---------------------------------------------------------------------------
# 7. Negative weights raise
# ---------------------------------------------------------------------------

def test_negative_weights_raise():
    p = _make_prices(50, seed=11)
    vix = _make_vix(50, seed=12)
    with pytest.raises(ValueError, match="w_041 must be >= 0"):
        compute_combined_returns(
            p["SPY"], p["IEF"], p["GLD"],
            {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
            vix, w_041=-0.1, w_039=0.5,
        )
    with pytest.raises(ValueError, match="w_039 must be >= 0"):
        compute_combined_returns(
            p["SPY"], p["IEF"], p["GLD"],
            {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
            vix, w_041=0.5, w_039=-0.1,
        )


def test_zero_sum_weights_raise():
    p = _make_prices(50, seed=13)
    vix = _make_vix(50, seed=14)
    with pytest.raises(ValueError, match=r"w_041 \+ w_039 must be > 0"):
        compute_combined_returns(
            p["SPY"], p["IEF"], p["GLD"],
            {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
            vix, w_041=0.0, w_039=0.0,
        )


# ---------------------------------------------------------------------------
# 8. Cross-lib parity (G7) on synthetic data
# ---------------------------------------------------------------------------

def test_cross_lib_parity_within_tolerance():
    """Pandas + numpy reference produce identical net streams within tight
    float tolerance (well below G7's 3 pp CAGR)."""
    p = _make_prices(400, seed=15)
    vix = _make_vix(400, seed=16)

    combined_pd, _, _ = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix, w_041=0.5, w_039=0.5,
    )

    # numpy: align inputs as the pandas engine does. r_eq/bd/gld is post
    # pct_change (length n-1); basket prices are full level (length n);
    # vix_for_regime is aligned to the **return** index (length n-1).
    r_eq_np = p["SPY"].pct_change().dropna().to_numpy(float)
    r_bd_np = p["IEF"].pct_change().dropna().to_numpy(float)
    r_gld_np = p["GLD"].pct_change().dropna().to_numpy(float)
    basket_arr = {
        "SPY": p["SPY"].to_numpy(float),
        "QQQ": p["QQQ"].to_numpy(float),
        "IWM": p["IWM"].to_numpy(float),
    }
    # vix on returns index = vix.iloc[1:] (skip the price-only first bar).
    vix_for_regime = vix.iloc[1:].to_numpy(float)
    vix_full = vix.to_numpy(float)

    combined_np, _, _ = compute_combined_returns_np(
        r_eq_np, r_bd_np, r_gld_np,
        vix_for_regime,
        basket_arr, vix_full,
        w_041=0.5, w_039=0.5,
    )

    n = min(len(combined_pd), len(combined_np))
    pd_arr = combined_pd.values[-n:]
    np_arr = combined_np[-n:]
    np.testing.assert_allclose(pd_arr, np_arr, atol=1e-10)


# ---------------------------------------------------------------------------
# 9. Combined volatility ≤ weighted std bound (Cauchy-Schwarz)
# ---------------------------------------------------------------------------

def test_combined_volatility_below_weighted_bound():
    p = _make_prices(400, seed=17)
    vix = _make_vix(400, seed=18)
    combined, r_041, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix, w_041=0.5, w_039=0.5,
    )
    upper = 0.5 * r_041.std() + 0.5 * r_039.std()
    assert combined.std() <= upper + 1e-12


# ---------------------------------------------------------------------------
# 10. Asymmetric weights still produce convex combo
# ---------------------------------------------------------------------------

def test_asymmetric_weights_produce_weighted_combo():
    p = _make_prices(300, seed=19)
    vix = _make_vix(300, seed=20)
    combined, r_041, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix, w_041=0.7, w_039=0.3,
    )
    expected = 0.7 * r_041 + 0.3 * r_039
    np.testing.assert_allclose(combined.values, expected.values, atol=1e-15)


# ---------------------------------------------------------------------------
# 11. build_regime_array applies a 1-day VIX lag (no-lookahead)
# ---------------------------------------------------------------------------

def test_build_regime_array_applies_one_day_lag():
    """Regime[t] = 1 if VIX[t-1] < threshold else 0; bar 0 falls back to
    VIX[0]. Verifies the no-lookahead convention matches iter 041's
    pandas engine."""
    vix = np.array([15.0, 25.0, 18.0, 22.0, 10.0], dtype=float)
    regime = build_regime_array(vix, vix_threshold=20.0)
    # Bar 0 fallback: VIX[0]=15 < 20 → calm (1)
    # Bar 1: VIX[0]=15 < 20 → calm (1)
    # Bar 2: VIX[1]=25 ≥ 20 → stress (0)
    # Bar 3: VIX[2]=18 < 20 → calm (1)
    # Bar 4: VIX[3]=22 ≥ 20 → stress (0)
    expected = np.array([1, 1, 0, 1, 0], dtype=int)
    np.testing.assert_array_equal(regime, expected)
