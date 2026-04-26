"""Iter 076 — TDD specs for the LEVERED GLD/TLT trend sleeve and ensemble.

Inherits all iter 075 sleeve mechanics PLUS the new leg-level borrow
drag primitive::

    pos_{t-1}   = min(target_vol / vol_{t-1} · trend_{t-1}, leg_cap)
    excess      = max(pos_{t-1} - 1, 0)
    daily_borrow = (1 + borrow_rate_annual) ** (1/252) - 1
    r_leg_t     = pos_{t-1} · raw_t - excess · daily_borrow

Specs cover (≥ 14 tests):
  Original iter-075-class invariants:
   1. Sleeve trend-filter behavior (long when above SMA, flat when below)
   2. Vol-target scales position inversely with realized vol
   3. Leg cap enforced (no per-leg position above leg_cap)
   4. T-1 lag enforced (no look-ahead)
   5. Warmup period emits 0 returns
   6. Equal-weight 50/50 GLD/TLT blending
   7. Determinism (same input → same output)
   8. Pure-numpy reference matches pandas impl within 1e-9 (G7 cross-lib)

  New iter-076 borrow-drag specs:
   9. ``daily_borrow_from_annual(0.045)`` ≈ 1.745e-4 (sanity)
  10. ``borrow_rate_annual = 0`` ⇒ output identical to no-drag iter-075-style
  11. At ``leg_cap = 1.0``, drag is identically 0.0 regardless of target_vol
  12. At ``leg_cap = 3.0`` with high target_vol, drag is strictly > 0 on
      bars where trend is on AND realized vol is low enough to lever
  13. Drag is non-negative on every bar (cannot subsidize)
  14. iter-075 baseline (target_vol=0.10, leg_cap=1.0, borrow=0) reproduces
      iter 075's legs bit-for-bit on synthetic data
  15. Sleeve at target_vol=0.20 with leg_cap=3.0, borrow=0 has roughly
      double the magnitude of iter-075-style at target_vol=0.10
      (linear-leverage scaling sanity, ±50% tolerance for cap binding)

  Ensemble combine specs (mirror iter 075):
  16. Combine at w_sleeve=0 reduces to r_064 only
  17. Combine at w_064=0 reduces to r_sleeve only
  18. Combine at w=0.5/0.5 is arithmetic mean
  19. Negative weights raise ValueError
  20. Both-zero weights raise ValueError
  21. Combine matches numpy reference

Citations
---------
* Faber (2007) SSRN 962461 — SMA-200 long-only trend filter.
* `[volatility_trading, p.218]` — Sinclair (2013) inverse-vol sizing.
* `[risk_parity, ch.5]` — equal-weight risk parity rationale.
* `[leverage_for_the_long_run, ch.5]` — borrow drag primitive.
* Frazzini-Pedersen (2014) JFE 111(1) — borrow frictions on levered low-vol.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from iter076_sleeve import (  # noqa: E402
    _single_leg_returns,
    combine_iter064_with_sleeve,
    compute_sleeve_returns,
    daily_borrow_from_annual,
)
from numpy_reference_iter076 import (  # noqa: E402
    _single_leg_returns_np,
    combine_iter064_with_sleeve_np,
    compute_sleeve_returns_np,
)


# ---------------------------------------------------------------------------
# Synthetic price fixtures (controllable behavior)
# ---------------------------------------------------------------------------


def _trending_up_series(n: int = 600, drift: float = 0.0008,
                       sigma: float = 0.01, seed: int = 7) -> pd.Series:
    """Synthetic GBM-ish series with positive drift (mostly above SMA200)."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, sigma, n)
    prices = 100.0 * np.exp(np.cumsum(rets))
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    return pd.Series(prices, index=idx, name="price")


def _flat_low_vol_series(n: int = 600, sigma: float = 0.003,
                         drift: float = 0.0005, seed: int = 11) -> pd.Series:
    """Low-vol trending series — forces target_vol/realized_vol > 1 → leverage."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, sigma, n)
    prices = 100.0 * np.exp(np.cumsum(rets))
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    return pd.Series(prices, index=idx, name="price")


# ---------------------------------------------------------------------------
# 1-8: Inherited iter-075-class invariants
# ---------------------------------------------------------------------------


def test_sleeve_returns_zero_during_warmup() -> None:
    gld = _trending_up_series(seed=1)
    tlt = _trending_up_series(seed=2)
    out = compute_sleeve_returns(
        gld, tlt, sma_lookback=200, vol_lookback=21,
        target_vol=0.10, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    assert (out.iloc[:200] == 0.0).all(), \
        "first 200 bars must be 0 (SMA-200 warmup)"


def test_sleeve_long_only_when_above_sma_with_leverage() -> None:
    """Trending-up series at high target_vol → mostly long with leverage →
    mostly positive returns when raw is positive (sanity)."""
    gld = _trending_up_series(seed=3)
    tlt = _trending_up_series(seed=4)
    out = compute_sleeve_returns(
        gld, tlt, sma_lookback=50, vol_lookback=21,
        target_vol=0.25, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    post_warmup = out.iloc[60:]
    assert post_warmup.std() > 0.0
    assert post_warmup.mean() > 0.0, \
        "trending-up levered sleeve should have positive mean (drift > borrow drag)"


def test_sleeve_zero_below_sma_levered() -> None:
    """Always-below-SMA crash + zero-vol flat → trend filter zeros pos →
    drag is also zero (no leverage applied → no borrow charge)."""
    n = 400
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    crash = pd.Series(100.0 * np.exp(np.linspace(0, -1.5, n)), index=idx)
    flat = pd.Series(100.0 * np.ones(n), index=idx)
    out = compute_sleeve_returns(
        crash, flat, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    assert np.allclose(out.iloc[60:].values, 0.0), \
        "always-below-SMA crash + zero-vol flat → r=0 always (no drag without trend)"


def test_sleeve_vol_target_scales_inversely_with_vol() -> None:
    gld_lo = _trending_up_series(seed=5, sigma=0.005)
    tlt_lo = _trending_up_series(seed=6, sigma=0.005)
    gld_hi = _trending_up_series(seed=5, sigma=0.020)
    tlt_hi = _trending_up_series(seed=6, sigma=0.020)
    r_lo = compute_sleeve_returns(
        gld_lo, tlt_lo, sma_lookback=100, vol_lookback=21,
        target_vol=0.10, leg_cap=10.0, borrow_rate_annual=0.0,  # borrow=0 to isolate
    )
    r_hi = compute_sleeve_returns(
        gld_hi, tlt_hi, sma_lookback=100, vol_lookback=21,
        target_vol=0.10, leg_cap=10.0, borrow_rate_annual=0.0,
    )
    abs_lo = r_lo.iloc[120:].abs().mean()
    abs_hi = r_hi.iloc[120:].abs().mean()
    assert 0.25 < abs_lo / abs_hi < 4.0, \
        f"vol-target should equalize ret magnitudes; ratio={abs_lo/abs_hi:.2f}"


def test_sleeve_leg_cap_enforced_levered() -> None:
    """Low-vol trending → would lever way above 1; leg_cap=2.0 must clip."""
    p = _flat_low_vol_series(seed=15, sigma=0.003)
    # Build a leg directly to inspect pos
    leg_capped = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=2.0, borrow_rate_annual=0.0,
    )
    leg_uncapped = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=20.0, borrow_rate_annual=0.0,
    )
    cap_mag = leg_capped.iloc[60:].abs().mean()
    uncap_mag = leg_uncapped.iloc[60:].abs().mean()
    assert cap_mag <= uncap_mag + 1e-12, \
        f"capped magnitude {cap_mag} should be ≤ uncapped {uncap_mag}"


def test_sleeve_t_minus_1_lag_no_look_ahead_levered() -> None:
    gld = _trending_up_series(seed=42)
    tlt = _trending_up_series(seed=43)
    r_orig = compute_sleeve_returns(
        gld, tlt, sma_lookback=50, vol_lookback=21,
        target_vol=0.20, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    gld_mod = gld.copy()
    gld_mod.iloc[300:] = gld_mod.iloc[300:] * 1.05
    r_mod = compute_sleeve_returns(
        gld_mod, tlt, sma_lookback=50, vol_lookback=21,
        target_vol=0.20, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    pd.testing.assert_series_equal(
        r_orig.iloc[:299], r_mod.iloc[:299], check_names=False,
    )


def test_sleeve_determinism_levered() -> None:
    gld = _trending_up_series(seed=99)
    tlt = _trending_up_series(seed=100)
    r1 = compute_sleeve_returns(
        gld, tlt, sma_lookback=50, vol_lookback=21,
        target_vol=0.25, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    r2 = compute_sleeve_returns(
        gld, tlt, sma_lookback=50, vol_lookback=21,
        target_vol=0.25, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    pd.testing.assert_series_equal(r1, r2)


def test_sleeve_matches_numpy_reference_levered() -> None:
    """Pandas impl == pure-numpy reference within 1e-9 across non-trivial cfg."""
    gld = _trending_up_series(seed=77)
    tlt = _trending_up_series(seed=78)
    r_pd = compute_sleeve_returns(
        gld, tlt, sma_lookback=200, vol_lookback=21,
        target_vol=0.25, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    r_np = compute_sleeve_returns_np(
        gld.values, tlt.values,
        sma_lookback=200, vol_lookback=21,
        target_vol=0.25, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    assert r_pd.shape[0] == r_np.shape[0]
    np.testing.assert_allclose(r_pd.values, r_np, atol=1e-9, rtol=1e-9)


# ---------------------------------------------------------------------------
# 9-15: New borrow-drag specs
# ---------------------------------------------------------------------------


def test_daily_borrow_from_annual_sanity() -> None:
    """daily_borrow(0.045) ≈ 1.745e-4 (compounded)."""
    db = daily_borrow_from_annual(0.045)
    assert abs(db - 1.745e-4) < 1e-6, f"got {db}"


def test_daily_borrow_from_annual_negative_raises() -> None:
    with pytest.raises(ValueError):
        daily_borrow_from_annual(-0.01)


def test_zero_borrow_rate_no_drag() -> None:
    """borrow_rate_annual=0 ⇒ no drag regardless of leverage."""
    p = _flat_low_vol_series(seed=20, sigma=0.003)
    r_no_borrow = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=3.0, borrow_rate_annual=0.0,
    )
    # Manual computation without drag should equal the leg
    raw = p.pct_change().fillna(0.0)
    sma = p.rolling(50, min_periods=50).mean()
    trend = (p > sma).astype(float).shift(1).fillna(0.0)
    vol_ann_lag = (raw.rolling(21, min_periods=21).std() * np.sqrt(252)).shift(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        size = np.where((vol_ann_lag > 0) & np.isfinite(vol_ann_lag),
                        0.30 / vol_ann_lag, 0.0)
    size = np.minimum(size, 3.0)
    pos = pd.Series(size, index=p.index) * trend
    pos = pos.fillna(0.0)
    expected = (pos * raw).fillna(0.0)
    np.testing.assert_allclose(r_no_borrow.values, expected.values, atol=1e-12)


def test_leg_cap_one_implies_zero_drag() -> None:
    """leg_cap=1.0 ⇒ pos never exceeds 1.0 ⇒ excess=0 ⇒ drag=0 always."""
    p = _flat_low_vol_series(seed=21, sigma=0.003)
    r_with_borrow = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=1.0, borrow_rate_annual=0.10,
    )
    r_no_borrow = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=1.0, borrow_rate_annual=0.0,
    )
    np.testing.assert_allclose(r_with_borrow.values, r_no_borrow.values, atol=1e-12)


def test_leverage_above_one_produces_positive_drag() -> None:
    """At leg_cap=3 with low-vol prices, pos should exceed 1 on many bars,
    and the levered+borrow-charged leg should differ from the no-borrow leg."""
    p = _flat_low_vol_series(seed=22, sigma=0.003)
    r_with_borrow = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=3.0, borrow_rate_annual=0.10,
    )
    r_no_borrow = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=3.0, borrow_rate_annual=0.0,
    )
    # The borrow-charged version must be strictly less in cumulative sum
    # (there's positive drag on at least some bars where pos > 1)
    cum_borrow = float(r_with_borrow.iloc[60:].sum())
    cum_no_borrow = float(r_no_borrow.iloc[60:].sum())
    assert cum_borrow < cum_no_borrow, \
        f"borrow drag should reduce cumulative return: with_borrow={cum_borrow}, " \
        f"no_borrow={cum_no_borrow}"


def test_drag_is_non_negative_per_bar() -> None:
    """The borrow drag itself must never subsidize: bar-level
    diff (no_borrow - with_borrow) is element-wise ≥ 0."""
    p = _flat_low_vol_series(seed=24, sigma=0.003)
    r_with_borrow = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    r_no_borrow = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=3.0, borrow_rate_annual=0.0,
    )
    diff = (r_no_borrow - r_with_borrow).values
    assert np.all(diff >= -1e-12), \
        f"drag must be non-negative per bar; min diff={diff.min()}"


def test_iter075_baseline_reproduction() -> None:
    """At target_vol=0.10, leg_cap=1.0, borrow=0 ⇒ output matches the
    iter-075-style sleeve construction (no leverage, no drag) bit-for-bit."""
    p = _trending_up_series(seed=33, sigma=0.012)
    r_iter076_baseline = _single_leg_returns(
        p, sma_lookback=200, vol_lookback=21,
        target_vol=0.10, leg_cap=1.0, borrow_rate_annual=0.0,
    )
    # Hand-computed iter-075-style equivalent (no drag term):
    raw = p.pct_change().fillna(0.0)
    sma = p.rolling(200, min_periods=200).mean()
    trend = (p > sma).astype(float).shift(1).fillna(0.0)
    vol_ann_lag = (raw.rolling(21, min_periods=21).std() * np.sqrt(252)).shift(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        size = np.where((vol_ann_lag > 0) & np.isfinite(vol_ann_lag),
                        0.10 / vol_ann_lag, 0.0)
    size = np.minimum(size, 1.0)
    pos = pd.Series(size, index=p.index) * trend
    pos = pos.fillna(0.0)
    iter075_equivalent = (pos * raw).fillna(0.0)
    np.testing.assert_allclose(
        r_iter076_baseline.values, iter075_equivalent.values, atol=1e-12,
    )


def test_linear_leverage_scaling_at_zero_borrow() -> None:
    """At borrow=0 and leg_cap=large: target_vol=0.20 sleeve has roughly
    2× the abs return magnitude of target_vol=0.10 sleeve."""
    gld = _trending_up_series(seed=51, sigma=0.012)
    tlt = _trending_up_series(seed=52, sigma=0.012)
    r10 = compute_sleeve_returns(
        gld, tlt, sma_lookback=50, vol_lookback=21,
        target_vol=0.10, leg_cap=10.0, borrow_rate_annual=0.0,
    )
    r20 = compute_sleeve_returns(
        gld, tlt, sma_lookback=50, vol_lookback=21,
        target_vol=0.20, leg_cap=10.0, borrow_rate_annual=0.0,
    )
    mag10 = r10.iloc[60:].abs().mean()
    mag20 = r20.iloc[60:].abs().mean()
    ratio = mag20 / mag10
    assert 1.5 < ratio < 2.5, \
        f"target_vol=0.20 should give ~2× magnitude of target_vol=0.10; ratio={ratio:.3f}"


# ---------------------------------------------------------------------------
# 16-21: Ensemble combine specs (mirror iter 075)
# ---------------------------------------------------------------------------


def _saved_streams() -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(13)
    idx = pd.date_range("2010-01-04", periods=20, freq="B")
    r_064 = pd.Series(rng.normal(0.001, 0.011, 20), index=idx, name="r_064")
    r_sleeve = pd.Series(rng.normal(0.0005, 0.008, 20), index=idx, name="r_sleeve")
    return r_064, r_sleeve


def test_combine_w_sleeve_zero_reduces_to_r064() -> None:
    r_064, r_sleeve = _saved_streams()
    out = combine_iter064_with_sleeve(r_064, r_sleeve, w_064=1.0, w_sleeve=0.0)
    pd.testing.assert_series_equal(
        out, r_064.loc[r_064.index.intersection(r_sleeve.index)],
        check_names=False,
    )


def test_combine_w_064_zero_reduces_to_r_sleeve() -> None:
    r_064, r_sleeve = _saved_streams()
    out = combine_iter064_with_sleeve(r_064, r_sleeve, w_064=0.0, w_sleeve=1.0)
    pd.testing.assert_series_equal(
        out, r_sleeve.loc[r_064.index.intersection(r_sleeve.index)],
        check_names=False,
    )


def test_combine_arithmetic_mean_at_50_50() -> None:
    r_064, r_sleeve = _saved_streams()
    out = combine_iter064_with_sleeve(r_064, r_sleeve, w_064=0.5, w_sleeve=0.5)
    common = r_064.index.intersection(r_sleeve.index)
    expected = 0.5 * r_064.loc[common] + 0.5 * r_sleeve.loc[common]
    np.testing.assert_allclose(out.values, expected.values, atol=1e-12)


def test_combine_negative_weight_raises() -> None:
    r_064, r_sleeve = _saved_streams()
    with pytest.raises(ValueError):
        combine_iter064_with_sleeve(r_064, r_sleeve, w_064=-0.1, w_sleeve=0.5)
    with pytest.raises(ValueError):
        combine_iter064_with_sleeve(r_064, r_sleeve, w_064=0.5, w_sleeve=-0.1)


def test_combine_both_zero_raises() -> None:
    r_064, r_sleeve = _saved_streams()
    with pytest.raises(ValueError):
        combine_iter064_with_sleeve(r_064, r_sleeve, w_064=0.0, w_sleeve=0.0)


def test_combine_matches_numpy_reference() -> None:
    r_064, r_sleeve = _saved_streams()
    out_pd = combine_iter064_with_sleeve(r_064, r_sleeve, w_064=0.7, w_sleeve=0.3)
    out_np = combine_iter064_with_sleeve_np(
        r_064.values, r_sleeve.values, w_064=0.7, w_sleeve=0.3,
    )
    np.testing.assert_allclose(out_pd.values, out_np, atol=1e-12)


def test_single_leg_np_matches_pd_at_high_target_vol() -> None:
    """Direct leg-level cross-lib parity at target_vol=0.30, leg_cap=3.0."""
    p = _flat_low_vol_series(seed=88, sigma=0.004)
    r_pd = _single_leg_returns(
        p, sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    r_np = _single_leg_returns_np(
        p.values,
        sma_lookback=50, vol_lookback=21,
        target_vol=0.30, leg_cap=3.0, borrow_rate_annual=0.045,
    )
    np.testing.assert_allclose(r_pd.values, r_np, atol=1e-9)
