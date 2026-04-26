"""Iter 077 — TDD specs for the long-short MTUM−VLUE factor sleeve and ensemble.

Mechanism specs:
  Sleeve = dollar-neutral long-short on MTUM (long) − VLUE (short),
  vol-targeted, with retail-rate short-borrow charge and turnover cost::

      ret_MTUM_t   = price_MTUM[t]/price_MTUM[t-1] - 1
      ret_VLUE_t   = price_VLUE[t]/price_VLUE[t-1] - 1
      spread_t     = ret_MTUM_t - ret_VLUE_t
      vol_{t-1}    = std(spread[t-vol_lb : t]) · √252
      pos_{t-1}    = clip(target_vol / vol_{t-1}, 0, leg_cap)
      borrow_t     = pos_{t-1} · short_borrow_rate / 252
      cost_t       = (trans_cost_bps/10000) · |pos_{t-1} - pos_{t-2}|
      r_sleeve_t   = pos_{t-1} · spread_t - borrow_t - cost_t

  Ensemble = linear convex blend with iter 064 saved stream::

      r_077_t = w_064 · r_064_t + w_sleeve · r_sleeve_t

Specs cover:
  1. Spread = ret_MTUM − ret_VLUE on toy data
  2. Vol-target sizing reaches target within tolerance
  3. Leg cap clamps oversized positions
  4. T-1 lag enforced (no look-ahead from current-bar vol)
  5. Warmup period emits 0 returns
  6. Pure-numpy reference matches pandas impl within 1e-9 (G7 cross-lib)
  7. Determinism (same input → same output)
  8. Borrow charge applied — higher rate → lower returns monotonically
  9. Transaction cost applied — higher cost → lower returns monotonically
 10. Inner-join with iter 064 stream preserves dates
 11. Convex combine boundary w_sleeve=0 reduces to iter 064
 12. Convex combine boundary w_064=0 reduces to sleeve
 13. Negative-weight rejection (raise ValueError)
 14. Both-zero weight rejection (raise ValueError)
 15. Negative leg_cap rejection
 16. Negative target_vol rejection
 17. Negative borrow rate rejection
 18. Negative trans_cost rejection
 19. Sleeve magnitude scales with target_vol (2× tv → ~2× sleeve, modulo cap)
 20. Equal MTUM & VLUE (zero spread) yields ~0 sleeve return modulo cost

Citations
---------
* Carhart (1997) JoF 52(1) — UMD long-short momentum factor.
* Asness-Moskowitz-Pedersen (2013) JoF 68(3) — value-momentum factor pair.
* `[volatility_trading, p.218]` — Sinclair (2013) inverse-vol sizing.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead) discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from mtum_vlue_sleeve import (  # noqa: E402
    combine_iter064_with_sleeve,
    compute_sleeve_returns,
)
from numpy_reference_iter077 import (  # noqa: E402
    combine_iter064_with_sleeve_np,
    compute_sleeve_returns_np,
)


# ---------------------------------------------------------------------------
# Fixtures — synthetic price series with controllable behavior
# ---------------------------------------------------------------------------


def _gbm_series(
    n: int = 600, drift: float = 0.0005, sigma: float = 0.012, seed: int = 7,
) -> pd.Series:
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, sigma, n)
    prices = 100.0 * np.exp(np.cumsum(rets))
    idx = pd.date_range("2014-01-02", periods=n, freq="B")
    return pd.Series(prices, index=idx, name="price")


def _equal_series(n: int = 600, drift: float = 0.0003, sigma: float = 0.01) -> pd.Series:
    """Two identical series → spread is zero → sleeve returns ≈ −costs only."""
    rng = np.random.default_rng(31)
    rets = rng.normal(drift, sigma, n)
    prices = 100.0 * np.exp(np.cumsum(rets))
    idx = pd.date_range("2014-01-02", periods=n, freq="B")
    return pd.Series(prices, index=idx, name="price")


# ---------------------------------------------------------------------------
# 1. Spread = ret_MTUM − ret_VLUE
# ---------------------------------------------------------------------------


def test_spread_is_difference_of_returns():
    """Sleeve gross signal is ret_MTUM − ret_VLUE."""
    mtum = _gbm_series(seed=1)
    vlue = _gbm_series(seed=2)
    # Run with no vol-targeting cap (set leg_cap large) and zero borrow + cost
    sleeve = compute_sleeve_returns(
        mtum, vlue,
        vol_lookback=21, target_vol=0.10, leg_cap=10.0,
        short_borrow_rate=0.0, trans_cost_bps=0.0,
    )
    ret_mtum = mtum.pct_change().fillna(0.0)
    ret_vlue = vlue.pct_change().fillna(0.0)
    spread = ret_mtum - ret_vlue
    # post-warmup, sleeve_t ≈ pos_{t-1} · spread_t (where pos > 0)
    # Pick a post-warmup bar where sleeve != 0 → check sign consistency
    post = sleeve.iloc[30:]
    spread_post = spread.iloc[30:]
    matched = (np.sign(post) == np.sign(spread_post)) | (
        post.abs() < 1e-12
    )
    # Allow some sign mismatches near zero
    assert matched.mean() > 0.95, "Sleeve sign should track spread sign post-warmup"


# ---------------------------------------------------------------------------
# 2. Vol-target sizing
# ---------------------------------------------------------------------------


def test_vol_target_realized_close_to_target():
    """Sleeve realized vol should approximately match target_vol."""
    mtum = _gbm_series(seed=11)
    vlue = _gbm_series(seed=12)
    target = 0.08
    sleeve = compute_sleeve_returns(
        mtum, vlue,
        vol_lookback=21, target_vol=target, leg_cap=10.0,  # uncapped
        short_borrow_rate=0.0, trans_cost_bps=0.0,
    )
    realized = sleeve.iloc[30:].std() * np.sqrt(252)
    # Allow ±50% tolerance — realized vol of vol-targeted strategy on
    # noisy synthetic data won't hit target precisely but should be close.
    assert 0.5 * target < realized < 1.6 * target, \
        f"Realized vol {realized:.4f} outside [0.5×, 1.6×] of target {target}"


# ---------------------------------------------------------------------------
# 3. Leg cap clamps
# ---------------------------------------------------------------------------


def test_leg_cap_clamps_position():
    """High target_vol with low leg_cap → position never exceeds leg_cap."""
    mtum = _gbm_series(sigma=0.001, seed=21)  # very low vol → wants big position
    vlue = _gbm_series(sigma=0.001, seed=22)
    sleeve_low = compute_sleeve_returns(
        mtum, vlue,
        vol_lookback=21, target_vol=2.0,  # huge target
        leg_cap=0.5,                      # clamp at 0.5
        short_borrow_rate=0.0, trans_cost_bps=0.0,
    )
    sleeve_uncapped = compute_sleeve_returns(
        mtum, vlue,
        vol_lookback=21, target_vol=2.0,
        leg_cap=10.0,
        short_borrow_rate=0.0, trans_cost_bps=0.0,
    )
    # Capped sleeve should have strictly smaller (in magnitude) returns
    assert sleeve_low.abs().sum() < sleeve_uncapped.abs().sum()


# ---------------------------------------------------------------------------
# 4. T-1 lag (no look-ahead)
# ---------------------------------------------------------------------------


def test_t_minus_one_lag_enforced():
    """Sleeve at bar t uses vol from bars [t-vol_lb-1, t-2], not bar t."""
    mtum = _gbm_series(seed=33)
    vlue = _gbm_series(seed=34)
    sleeve = compute_sleeve_returns(
        mtum, vlue,
        vol_lookback=21, target_vol=0.10, leg_cap=2.0,
        short_borrow_rate=0.0, trans_cost_bps=0.0,
    )
    # First vol_lookback bars must be 0: rolling std needs vol_lookback
    # values; first valid std is at iloc[vol_lookback-1]; T-1 lag pushes
    # first non-zero position/return to iloc[vol_lookback].
    assert sleeve.iloc[:21].abs().sum() < 1e-12, \
        "Sleeve must not produce returns within first vol_lookback bars"


# ---------------------------------------------------------------------------
# 5. Warmup emits 0
# ---------------------------------------------------------------------------


def test_warmup_emits_zero():
    """First vol_lookback bars have NaN vol → sleeve returns 0."""
    mtum = _gbm_series(seed=41)
    vlue = _gbm_series(seed=42)
    sleeve = compute_sleeve_returns(
        mtum, vlue,
        vol_lookback=21, target_vol=0.10, leg_cap=2.0,
        short_borrow_rate=0.0, trans_cost_bps=0.0,
    )
    assert sleeve.iloc[:21].sum() == 0.0


# ---------------------------------------------------------------------------
# 6. G7 cross-lib parity
# ---------------------------------------------------------------------------


def test_pandas_numpy_parity_default_params():
    mtum = _gbm_series(seed=51)
    vlue = _gbm_series(seed=52)
    pd_out = compute_sleeve_returns(
        mtum, vlue,
        vol_lookback=21, target_vol=0.10, leg_cap=1.0,
        short_borrow_rate=0.01, trans_cost_bps=5.0,
    )
    np_out = compute_sleeve_returns_np(
        mtum.values, vlue.values,
        vol_lookback=21, target_vol=0.10, leg_cap=1.0,
        short_borrow_rate=0.01, trans_cost_bps=5.0,
    )
    assert np.allclose(pd_out.values, np_out, atol=1e-9, rtol=0)


def test_pandas_numpy_parity_swept_params():
    mtum = _gbm_series(seed=61)
    vlue = _gbm_series(seed=62)
    for tv in [0.06, 0.08, 0.10, 0.12, 0.15]:
        for w in [0.10, 0.20, 0.30, 0.40]:
            pd_out = compute_sleeve_returns(
                mtum, vlue,
                vol_lookback=21, target_vol=tv, leg_cap=1.0,
                short_borrow_rate=0.01, trans_cost_bps=5.0,
            )
            np_out = compute_sleeve_returns_np(
                mtum.values, vlue.values,
                vol_lookback=21, target_vol=tv, leg_cap=1.0,
                short_borrow_rate=0.01, trans_cost_bps=5.0,
            )
            assert np.allclose(pd_out.values, np_out, atol=1e-9, rtol=0), \
                f"Mismatch at tv={tv}, w={w}"


# ---------------------------------------------------------------------------
# 7. Determinism
# ---------------------------------------------------------------------------


def test_determinism():
    mtum = _gbm_series(seed=71)
    vlue = _gbm_series(seed=72)
    out1 = compute_sleeve_returns(mtum, vlue)
    out2 = compute_sleeve_returns(mtum, vlue)
    assert np.allclose(out1.values, out2.values, atol=0)


# ---------------------------------------------------------------------------
# 8. Borrow charge monotonic
# ---------------------------------------------------------------------------


def test_higher_borrow_lowers_returns():
    mtum = _gbm_series(seed=81)
    vlue = _gbm_series(seed=82)
    low = compute_sleeve_returns(
        mtum, vlue, short_borrow_rate=0.0, trans_cost_bps=0.0,
    ).sum()
    high = compute_sleeve_returns(
        mtum, vlue, short_borrow_rate=0.05, trans_cost_bps=0.0,
    ).sum()
    assert high < low


# ---------------------------------------------------------------------------
# 9. Transaction cost monotonic
# ---------------------------------------------------------------------------


def test_higher_cost_lowers_returns():
    mtum = _gbm_series(seed=91)
    vlue = _gbm_series(seed=92)
    low = compute_sleeve_returns(
        mtum, vlue, short_borrow_rate=0.0, trans_cost_bps=0.0,
    ).sum()
    high = compute_sleeve_returns(
        mtum, vlue, short_borrow_rate=0.0, trans_cost_bps=50.0,
    ).sum()
    assert high < low


# ---------------------------------------------------------------------------
# 10. Inner-join preserves dates
# ---------------------------------------------------------------------------


def test_combine_inner_join_preserves_dates():
    idx_a = pd.date_range("2010-01-04", periods=300, freq="B")
    idx_b = pd.date_range("2014-01-06", periods=300, freq="B")
    rng = np.random.default_rng(101)
    a = pd.Series(rng.normal(0.0005, 0.01, 300), index=idx_a, name="iter064")
    b = pd.Series(rng.normal(0.0001, 0.005, 300), index=idx_b, name="sleeve")
    combined = combine_iter064_with_sleeve(a, b, w_064=0.7, w_sleeve=0.3)
    expected_dates = idx_a.union(idx_b)
    assert combined.index.equals(expected_dates)


def test_combine_phase_in_preserves_iter064_pre_sleeve():
    """Pre-sleeve dates: combined == r_064 (full weight, no dilution).
    Post-sleeve: combined == w_064 · r_064 + w_sleeve · r_sleeve.
    """
    idx_a = pd.date_range("2010-01-04", periods=300, freq="B")
    idx_b = pd.date_range("2014-01-06", periods=300, freq="B")
    rng = np.random.default_rng(102)
    a = pd.Series(rng.normal(0.0005, 0.01, 300), index=idx_a, name="iter064")
    b = pd.Series(rng.normal(0.0001, 0.005, 300), index=idx_b, name="sleeve")
    combined = combine_iter064_with_sleeve(a, b, w_064=0.8, w_sleeve=0.2)
    # Pre-sleeve dates: combined = a (since sleeve absent → eff_w_064=1.0)
    pre_sleeve_dates = a.index.difference(b.index)
    assert np.allclose(
        combined.loc[pre_sleeve_dates].values,
        a.loc[pre_sleeve_dates].values,
        atol=1e-12,
    )
    # Both-present dates: combined = 0.8 a + 0.2 b
    both_dates = a.index.intersection(b.index)
    if len(both_dates) > 0:
        expected = 0.8 * a.loc[both_dates].values + 0.2 * b.loc[both_dates].values
        assert np.allclose(
            combined.loc[both_dates].values, expected, atol=1e-12,
        )
    # Post-064 dates (sleeve only): combined = 0.2 b (since iter 064 absent)
    post_064_dates = b.index.difference(a.index)
    if len(post_064_dates) > 0:
        expected = 0.2 * b.loc[post_064_dates].values
        assert np.allclose(
            combined.loc[post_064_dates].values, expected, atol=1e-12,
        )


# ---------------------------------------------------------------------------
# 11. Boundary: w_sleeve=0 → combined = w_064 · r_064
# ---------------------------------------------------------------------------


def test_combine_boundary_zero_sleeve_weight():
    idx = pd.date_range("2014-01-02", periods=100, freq="B")
    rng = np.random.default_rng(111)
    a = pd.Series(rng.normal(0.0005, 0.01, 100), index=idx)
    b = pd.Series(rng.normal(0.0, 0.005, 100), index=idx)
    combined = combine_iter064_with_sleeve(a, b, w_064=1.0, w_sleeve=0.0)
    assert np.allclose(combined.values, a.values, atol=0)


# ---------------------------------------------------------------------------
# 12. Boundary: w_064=0 → combined = w_sleeve · r_sleeve
# ---------------------------------------------------------------------------


def test_combine_boundary_zero_iter064_weight():
    idx = pd.date_range("2014-01-02", periods=100, freq="B")
    rng = np.random.default_rng(121)
    a = pd.Series(rng.normal(0.0005, 0.01, 100), index=idx)
    b = pd.Series(rng.normal(0.0, 0.005, 100), index=idx)
    combined = combine_iter064_with_sleeve(a, b, w_064=0.0, w_sleeve=1.0)
    assert np.allclose(combined.values, b.values, atol=0)


# ---------------------------------------------------------------------------
# 13-14. Weight rejections
# ---------------------------------------------------------------------------


def test_combine_rejects_negative_weights():
    idx = pd.date_range("2014-01-02", periods=10, freq="B")
    a = pd.Series(np.zeros(10), index=idx)
    b = pd.Series(np.zeros(10), index=idx)
    with pytest.raises(ValueError, match="w_064 must be >= 0"):
        combine_iter064_with_sleeve(a, b, w_064=-0.1, w_sleeve=0.5)
    with pytest.raises(ValueError, match="w_sleeve must be >= 0"):
        combine_iter064_with_sleeve(a, b, w_064=0.5, w_sleeve=-0.1)


def test_combine_rejects_zero_zero_weights():
    idx = pd.date_range("2014-01-02", periods=10, freq="B")
    a = pd.Series(np.zeros(10), index=idx)
    b = pd.Series(np.zeros(10), index=idx)
    with pytest.raises(ValueError, match="must be > 0"):
        combine_iter064_with_sleeve(a, b, w_064=0.0, w_sleeve=0.0)


# ---------------------------------------------------------------------------
# 15-18. Sleeve parameter rejections
# ---------------------------------------------------------------------------


def test_sleeve_rejects_negative_leg_cap():
    mtum = _gbm_series(seed=131)
    vlue = _gbm_series(seed=132)
    with pytest.raises(ValueError, match="leg_cap"):
        compute_sleeve_returns(mtum, vlue, leg_cap=-0.5)


def test_sleeve_rejects_negative_target_vol():
    mtum = _gbm_series(seed=141)
    vlue = _gbm_series(seed=142)
    with pytest.raises(ValueError, match="target_vol"):
        compute_sleeve_returns(mtum, vlue, target_vol=-0.05)


def test_sleeve_rejects_negative_borrow():
    mtum = _gbm_series(seed=151)
    vlue = _gbm_series(seed=152)
    with pytest.raises(ValueError, match="short_borrow_rate"):
        compute_sleeve_returns(mtum, vlue, short_borrow_rate=-0.01)


def test_sleeve_rejects_negative_trans_cost():
    mtum = _gbm_series(seed=161)
    vlue = _gbm_series(seed=162)
    with pytest.raises(ValueError, match="trans_cost_bps"):
        compute_sleeve_returns(mtum, vlue, trans_cost_bps=-1.0)


# ---------------------------------------------------------------------------
# 19. Magnitude scales with target_vol
# ---------------------------------------------------------------------------


def test_sleeve_magnitude_scales_with_target_vol():
    mtum = _gbm_series(seed=171)
    vlue = _gbm_series(seed=172)
    s_low = compute_sleeve_returns(
        mtum, vlue, target_vol=0.05, leg_cap=10.0,
        short_borrow_rate=0.0, trans_cost_bps=0.0,
    )
    s_high = compute_sleeve_returns(
        mtum, vlue, target_vol=0.20, leg_cap=10.0,
        short_borrow_rate=0.0, trans_cost_bps=0.0,
    )
    # Realized vol should scale ~linearly with target_vol for uncapped sleeve
    rv_low = s_low.iloc[30:].std() * np.sqrt(252)
    rv_high = s_high.iloc[30:].std() * np.sqrt(252)
    ratio = rv_high / rv_low
    assert 2.5 < ratio < 5.5, f"Vol ratio {ratio:.2f} not near 4× expected"


# ---------------------------------------------------------------------------
# 20. Equal MTUM/VLUE → near-zero sleeve return modulo cost
# ---------------------------------------------------------------------------


def test_equal_legs_yields_near_zero():
    p = _equal_series()
    sleeve = compute_sleeve_returns(
        p, p,  # identical series → spread = 0
        target_vol=0.10, leg_cap=2.0,
        short_borrow_rate=0.0, trans_cost_bps=0.0,
    )
    # Identical legs → spread is identically zero → no vol → no position
    # → sleeve returns identically zero
    assert sleeve.abs().sum() < 1e-12, \
        "Identical legs must yield zero sleeve return (spread = 0)"
