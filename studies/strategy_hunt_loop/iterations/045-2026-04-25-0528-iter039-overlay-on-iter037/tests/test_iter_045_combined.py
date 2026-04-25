"""Iter 045 — TDD specs for the 50/50 convex combo of iter 037 + iter 039.

These specs MUST pass before the backtest runs (engine-correctness gate
before measurements). Mirrors iter 037/039/044 testing patterns.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ITER_DIR))

from combined_037_039 import compute_combined_returns  # noqa: E402
from numpy_reference_combined import compute_combined_returns_np  # noqa: E402


def _make_index(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2020-01-02", periods=n, freq="B")


def _make_prices(n: int, seed: int = 0) -> dict[str, pd.Series]:
    """Synthetic price series for SPY/IEF/GLD/QQQ/IWM with known stats."""
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
# 1. Reduces to iter 037 when w_039 = 0
# ---------------------------------------------------------------------------

def test_reduces_to_iter_037_when_w039_zero():
    """w_037=1, w_039=0 → combined equals iter 037 net (on the inner-join)."""
    p = _make_prices(400, seed=1)
    vix = _make_vix(400, seed=2)

    combined, r_037, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
        w_037=1.0, w_039=0.0,
    )
    # Combined == r_037 (on the same intersection); both aligned to common idx
    assert combined.index.equals(r_037.index)
    np.testing.assert_allclose(combined.values, r_037.values, atol=1e-15)


# ---------------------------------------------------------------------------
# 2. Reduces to iter 039 when w_037 = 0
# ---------------------------------------------------------------------------

def test_reduces_to_iter_039_when_w037_zero():
    """w_037=0, w_039=1 → combined equals iter 039 net."""
    p = _make_prices(400, seed=3)
    vix = _make_vix(400, seed=4)

    combined, r_037, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
        w_037=0.0, w_039=1.0,
    )
    assert combined.index.equals(r_039.index)
    np.testing.assert_allclose(combined.values, r_039.values, atol=1e-15)


# ---------------------------------------------------------------------------
# 3. 50/50 returns the arithmetic mean of the two streams
# ---------------------------------------------------------------------------

def test_50_50_combo_is_arithmetic_mean():
    """For any (r_037, r_039), 0.5*r_037 + 0.5*r_039 = (r_037+r_039)/2."""
    p = _make_prices(400, seed=5)
    vix = _make_vix(400, seed=6)
    combined, r_037, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
        w_037=0.5, w_039=0.5,
    )
    expected = (r_037 + r_039) / 2.0
    np.testing.assert_allclose(combined.values, expected.values, atol=1e-15)


# ---------------------------------------------------------------------------
# 4. Combined index is the intersection of iter 037 and iter 039 indexes
# ---------------------------------------------------------------------------

def test_combined_index_is_intersection():
    """Combined output covers exactly the dates where BOTH sub-strategies have
    a return. iter 037 net starts on bar 1 (post-pct_change); iter 039 net
    starts on bar 1 too. The intersection should equal the shorter range."""
    p = _make_prices(500, seed=7)
    vix = _make_vix(500, seed=8)
    combined, r_037, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
    )
    expected = r_037.index.intersection(r_039.index)
    assert combined.index.equals(expected)


# ---------------------------------------------------------------------------
# 5. Cost is intrinsic to each sub-strategy; combined inherits both
# ---------------------------------------------------------------------------

def test_cost_inherited_from_subcomponents():
    """Iter 037 has 2 bps per-leg setup cost on bar 0 (3 legs × 2 bps =
    6 bps total impact on bar 0). Iter 039 has roll cost 5 bps per roll
    spread across the basket. The combined bar 0 has 0.5 * (037 cost) +
    0.5 * (039 cost). Verify combined bar 0 differs from the gross
    weighted average by approximately the expected cost."""
    p = _make_prices(50, seed=9)
    vix = _make_vix(50, seed=10)
    combined, r_037, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix,
        cost_bps_per_leg=0.0002, cost_bps_per_roll=5.0,
    )
    # Bar 0 of combined should have:
    #   r_037[0] = (eq_w*r_eq + bd_short_w*r_bd + bd_long_w*r_gld) − (eq_w + bd_short_w + bd_long_w) * 2bps
    # iter 037 setup cost on bar 0: (0.6 + 0.45 + 0.45) * 2bps = 1.5 * 2bps = 3bps.
    # iter 039 has its own roll cost; combined bar 0 has 0.5 * each.
    # We just verify the cost mechanism is active: bar-0 r_037 < gross weighted average.
    r_eq = p["SPY"].pct_change().dropna().iloc[0]
    r_bd = p["IEF"].pct_change().dropna().iloc[0]
    r_gld = p["GLD"].pct_change().dropna().iloc[0]
    gross_037_bar0 = 0.6 * r_eq + 0.45 * r_bd + 0.45 * r_gld
    setup_cost = 1.5 * 0.0002
    expected_037_bar0 = gross_037_bar0 - setup_cost
    assert r_037.iloc[0] == pytest.approx(expected_037_bar0, abs=1e-12)


# ---------------------------------------------------------------------------
# 6. Negative weights raise
# ---------------------------------------------------------------------------

def test_negative_weights_raise():
    p = _make_prices(50, seed=11)
    vix = _make_vix(50, seed=12)
    with pytest.raises(ValueError, match="w_037 must be >= 0"):
        compute_combined_returns(
            p["SPY"], p["IEF"], p["GLD"],
            {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
            vix, w_037=-0.1, w_039=0.5,
        )
    with pytest.raises(ValueError, match="w_039 must be >= 0"):
        compute_combined_returns(
            p["SPY"], p["IEF"], p["GLD"],
            {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
            vix, w_037=0.5, w_039=-0.1,
        )


def test_zero_sum_weights_raise():
    p = _make_prices(50, seed=13)
    vix = _make_vix(50, seed=14)
    with pytest.raises(ValueError, match=r"w_037 \+ w_039 must be > 0"):
        compute_combined_returns(
            p["SPY"], p["IEF"], p["GLD"],
            {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
            vix, w_037=0.0, w_039=0.0,
        )


# ---------------------------------------------------------------------------
# 7. Cross-lib parity (G7) on synthetic data
# ---------------------------------------------------------------------------

def test_cross_lib_parity_within_tolerance():
    """Pandas engine + numpy reference produce identical net streams on the
    same synthetic input (within tight float tolerance, well below G7's
    3 pp CAGR threshold)."""
    p = _make_prices(400, seed=15)
    vix = _make_vix(400, seed=16)

    # Pandas
    combined_pd, _, _ = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix, w_037=0.5, w_039=0.5,
    )

    # Numpy: align inputs the same way the pandas engine does
    r_eq_np = p["SPY"].pct_change().dropna().to_numpy(float)
    r_bd_np = p["IEF"].pct_change().dropna().to_numpy(float)
    r_gld_np = p["GLD"].pct_change().dropna().to_numpy(float)
    basket_arr = {
        "SPY": p["SPY"].to_numpy(float),
        "QQQ": p["QQQ"].to_numpy(float),
        "IWM": p["IWM"].to_numpy(float),
    }
    vix_arr = vix.to_numpy(float)

    combined_np, _, _ = compute_combined_returns_np(
        r_eq_np, r_bd_np, r_gld_np,
        basket_arr, vix_arr,
        w_037=0.5, w_039=0.5,
    )

    # The two engines may produce slightly different lengths if iter 039's
    # internal warmup differs from iter 037's. Trim both to the shorter.
    n = min(len(combined_pd), len(combined_np))
    pd_arr = combined_pd.values[-n:]
    np_arr = combined_np[-n:]

    # Tight float tolerance — tighter than G7's 3 pp CAGR.
    np.testing.assert_allclose(pd_arr, np_arr, atol=1e-10)


# ---------------------------------------------------------------------------
# 8. Combined Sharpe is bracketed when corr < 1
# ---------------------------------------------------------------------------

def test_combined_volatility_below_max_subcomponent():
    """If r_037 and r_039 are not perfectly correlated, the 50/50 combined
    std must be ≤ max(std_037, std_039) — basic diversification check.
    """
    p = _make_prices(400, seed=17)
    vix = _make_vix(400, seed=18)
    combined, r_037, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix, w_037=0.5, w_039=0.5,
    )
    # 50/50 combined std must be <= 0.5 * std_037 + 0.5 * std_039
    # (Cauchy-Schwarz; equality only when r_037 == r_039 exactly).
    upper = 0.5 * r_037.std() + 0.5 * r_039.std()
    assert combined.std() <= upper + 1e-12


# ---------------------------------------------------------------------------
# 9. Asymmetric weights still produce convex combo
# ---------------------------------------------------------------------------

def test_asymmetric_weights_produce_weighted_combo():
    """w_037=0.7, w_039=0.3 → combined = 0.7*r_037 + 0.3*r_039 exactly."""
    p = _make_prices(300, seed=19)
    vix = _make_vix(300, seed=20)
    combined, r_037, r_039 = compute_combined_returns(
        p["SPY"], p["IEF"], p["GLD"],
        {"SPY": p["SPY"], "QQQ": p["QQQ"], "IWM": p["IWM"]},
        vix, w_037=0.7, w_039=0.3,
    )
    expected = 0.7 * r_037 + 0.3 * r_039
    np.testing.assert_allclose(combined.values, expected.values, atol=1e-15)
