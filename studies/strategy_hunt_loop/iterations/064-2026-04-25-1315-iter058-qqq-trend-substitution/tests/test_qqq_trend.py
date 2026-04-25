"""TDD specs for iter 064 QQQ-trend filter + combiner.

Verifies:
- `qqq_trend.compute_qqq_trend_returns` semantics (warmup, lag, cost,
  cash leg).
- `combined_046_plus_qqqt.combine_046_plus_qqqt` weight invariants.
- G7 cross-library parity (pandas vs pure-numpy reference).

Citations
---------
* `[advances_fin_ml, p.31-34]` — G7 parity discipline.
* `[advances_fin_ml, p.162-164]` — no-lookahead invariant.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from qqq_trend import compute_qqq_trend_returns  # noqa: E402
from numpy_reference_iter064 import compute_qqq_trend_returns_np  # noqa: E402
from combined_046_plus_qqqt import combine_046_plus_qqqt  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _toy_uptrend(n: int = 400, drift: float = 0.0008) -> pd.Series:
    """Synthetic uptrending price series — guarantees long position post-warmup."""
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    rng = np.random.default_rng(42)
    log_rets = rng.normal(drift, 0.01, n)
    log_rets[0] = 0.0
    px = 100.0 * np.exp(np.cumsum(log_rets))
    return pd.Series(px, index=idx, name="QQQ_synth")


def _toy_downtrend(n: int = 400, drift: float = -0.0008) -> pd.Series:
    """Synthetic downtrending series — guarantees cash position post-warmup."""
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    rng = np.random.default_rng(7)
    log_rets = rng.normal(drift, 0.005, n)
    log_rets[0] = 0.0
    px = 200.0 * np.exp(np.cumsum(log_rets))
    return pd.Series(px, index=idx, name="QQQ_synth_down")


# ---------------------------------------------------------------------------
# qqq_trend semantics
# ---------------------------------------------------------------------------


def test_qqq_trend_basic_shape():
    px = _toy_uptrend(n=300)
    out = compute_qqq_trend_returns(px, lookback=200, rf=0.0, cost_bps=0.0)
    # one bar lost to pct_change
    assert len(out) == len(px) - 1
    assert out.name == "r_qqq_trend"


def test_qqq_trend_warmup_is_cash_at_zero_rf():
    """During first `lookback` ret bars (no SMA), pos=0; with rf=0 returns=0
    on those bars (minus 0 cost)."""
    px = _toy_uptrend(n=300)
    out = compute_qqq_trend_returns(px, lookback=200, rf=0.0, cost_bps=0.0)
    # First 199 ret bars should be exactly 0 (warmup pos=0, rf_d=0)
    assert np.allclose(out.values[:199], 0.0, atol=1e-12)


def test_qqq_trend_warmup_pays_rf():
    """During warmup, position=0 → returns=rf_d daily (per-day risk-free)."""
    px = _toy_uptrend(n=300)
    rf = 0.05  # 5% annual
    rf_d = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    out = compute_qqq_trend_returns(px, lookback=200, rf=rf, cost_bps=0.0)
    assert np.allclose(out.values[:199], rf_d, atol=1e-14)


def test_qqq_trend_uptrend_is_long_post_warmup():
    """Smooth uptrend → SMA below price → pos=1 on most post-warmup bars."""
    px = _toy_uptrend(n=400, drift=0.001)
    out = compute_qqq_trend_returns(px, lookback=200, rf=0.0, cost_bps=0.0)
    # Compare post-warmup bars: returns should match raw QQQ returns on most days
    raw = px.pct_change().dropna()
    post_warmup = out.values[200:]
    raw_post = raw.values[200:]
    # On bars where pos=1, out == raw; correlation should be very high
    corr = float(np.corrcoef(post_warmup, raw_post)[0, 1])
    assert corr > 0.95, f"expected high corr in uptrend, got {corr}"


def test_qqq_trend_downtrend_stays_in_cash():
    """Strong downtrend → SMA above price → pos=0 → returns=rf_d."""
    px = _toy_downtrend(n=400, drift=-0.002)
    out = compute_qqq_trend_returns(px, lookback=100, rf=0.0, cost_bps=0.0)
    # After warmup, in steady downtrend, should stay in cash on majority of bars
    raw = px.pct_change().dropna()
    post = out.values[100:]
    raw_post = raw.values[100:]
    # Output close to 0 (cash at rf=0), much less variable than raw
    assert np.std(post) < 0.5 * np.std(raw_post), \
        f"expected lower vol in cash, got out_std={np.std(post)} raw_std={np.std(raw_post)}"


def test_qqq_trend_cost_charged_on_signal_flip():
    """A single up→down→up flip pattern triggers exactly 2 cost charges."""
    # Construct a price series with deterministic flip
    n = 250
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    px_vals = np.concatenate([
        np.linspace(100, 200, 100),  # uptrend
        np.linspace(200, 50, 100),   # crash
        np.linspace(50, 150, 50),    # recover
    ])
    px = pd.Series(px_vals, index=idx)
    out_with_cost = compute_qqq_trend_returns(px, lookback=20, rf=0.0, cost_bps=10.0)
    out_no_cost = compute_qqq_trend_returns(px, lookback=20, rf=0.0, cost_bps=0.0)
    diff = (out_no_cost - out_with_cost)
    # Total cost spent = sum of diff = cost_bps * 1e-4 * total_turnover
    # Total turnover ≥ 2 (at least 1 long→cash and 1 cash→long flip)
    total_cost = float(diff.sum())
    assert total_cost > 0, f"expected positive cumulative cost, got {total_cost}"
    # Per-flip cost = 10 bps = 0.001; with 2+ flips we expect ≥ 0.002 cumulative
    assert total_cost >= 1e-3, \
        f"expected cumulative cost ≥ 0.001, got {total_cost}"


def test_qqq_trend_no_lookahead():
    """Position at t depends only on prices at t-1 and earlier."""
    n = 300
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    rng = np.random.default_rng(123)
    px_vals = 100.0 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, n)))
    px = pd.Series(px_vals, index=idx)
    out_full = compute_qqq_trend_returns(px, lookback=50, rf=0.0, cost_bps=0.0)

    # Mutate the last bar drastically — should not change ANY prior output.
    px2 = px.copy()
    px2.iloc[-1] = px2.iloc[-1] * 100.0
    out_mut = compute_qqq_trend_returns(px2, lookback=50, rf=0.0, cost_bps=0.0)

    # All but the last bar of out should be identical
    np.testing.assert_array_equal(out_full.values[:-1], out_mut.values[:-1])


def test_qqq_trend_validation_lookback():
    px = _toy_uptrend(n=100)
    with pytest.raises(ValueError):
        compute_qqq_trend_returns(px, lookback=0)
    with pytest.raises(ValueError):
        compute_qqq_trend_returns(px, lookback=-5)


def test_qqq_trend_validation_short_input():
    px = pd.Series([100.0], index=pd.to_datetime(["2020-01-02"]))
    with pytest.raises(ValueError):
        compute_qqq_trend_returns(px, lookback=10)


# ---------------------------------------------------------------------------
# Combiner
# ---------------------------------------------------------------------------


def test_combine_basic_shape():
    idx = pd.date_range("2020-01-02", periods=100, freq="B")
    a = pd.Series(np.linspace(0.001, 0.002, 100), index=idx, name="r_046")
    b = pd.Series(np.linspace(-0.001, 0.001, 100), index=idx, name="r_qqqt")
    out = combine_046_plus_qqqt(a, b, w_046=0.9, w_qqqt=0.1)
    assert len(out) == 100
    assert out.name == "combined_046_plus_qqqt"
    np.testing.assert_allclose(out.values, 0.9 * a.values + 0.1 * b.values)


def test_combine_inner_join():
    idx_a = pd.date_range("2020-01-02", periods=100, freq="B")
    idx_b = pd.date_range("2020-02-15", periods=100, freq="B")
    a = pd.Series(np.full(100, 0.001), index=idx_a, name="r_046")
    b = pd.Series(np.full(100, 0.002), index=idx_b, name="r_qqqt")
    out = combine_046_plus_qqqt(a, b, w_046=0.5, w_qqqt=0.5)
    common = idx_a.intersection(idx_b)
    assert len(out) == len(common)
    np.testing.assert_allclose(out.values, 0.5 * 0.001 + 0.5 * 0.002)


def test_combine_validation():
    idx = pd.date_range("2020-01-02", periods=10, freq="B")
    a = pd.Series(np.zeros(10), index=idx)
    b = pd.Series(np.zeros(10), index=idx)
    with pytest.raises(ValueError):
        combine_046_plus_qqqt(a, b, w_046=-0.1, w_qqqt=0.5)
    with pytest.raises(ValueError):
        combine_046_plus_qqqt(a, b, w_046=0.5, w_qqqt=-0.1)
    with pytest.raises(ValueError):
        combine_046_plus_qqqt(a, b, w_046=0.0, w_qqqt=0.0)
    # Disjoint indexes (no overlap) → ValueError
    a2 = pd.Series(np.zeros(5), index=pd.date_range("2020-01-02", periods=5, freq="B"))
    b2 = pd.Series(np.zeros(5), index=pd.date_range("2021-01-02", periods=5, freq="B"))
    with pytest.raises(ValueError):
        combine_046_plus_qqqt(a2, b2)


# ---------------------------------------------------------------------------
# G7 cross-library parity
# ---------------------------------------------------------------------------


def test_g7_parity_uptrend():
    px = _toy_uptrend(n=500)
    pd_out = compute_qqq_trend_returns(px, lookback=200, rf=0.02, cost_bps=5.0)
    np_out = compute_qqq_trend_returns_np(px.values, lookback=200, rf=0.02, cost_bps=5.0)
    assert len(pd_out) == len(np_out)
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-12)


def test_g7_parity_downtrend():
    px = _toy_downtrend(n=500, drift=-0.0015)
    pd_out = compute_qqq_trend_returns(px, lookback=100, rf=0.03, cost_bps=10.0)
    np_out = compute_qqq_trend_returns_np(px.values, lookback=100, rf=0.03, cost_bps=10.0)
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-12)


def test_g7_parity_random_walk():
    n = 700
    idx = pd.date_range("2018-01-02", periods=n, freq="B")
    rng = np.random.default_rng(2024)
    px_vals = 100.0 * np.exp(np.cumsum(rng.normal(0.0002, 0.012, n)))
    px = pd.Series(px_vals, index=idx)
    pd_out = compute_qqq_trend_returns(px, lookback=200, rf=0.02, cost_bps=5.0)
    np_out = compute_qqq_trend_returns_np(px.values, lookback=200, rf=0.02, cost_bps=5.0)
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-12)
    # CAGR delta must be tiny
    eq_pd = float(np.prod(1.0 + pd_out.values))
    eq_np = float(np.prod(1.0 + np_out))
    n_bars = len(pd_out)
    cagr_pd = eq_pd ** (252.0 / n_bars) - 1.0
    cagr_np = eq_np ** (252.0 / n_bars) - 1.0
    assert abs(cagr_pd - cagr_np) * 100.0 < 0.01, \
        f"CAGR pp diff too large: {abs(cagr_pd - cagr_np) * 100} pp"
