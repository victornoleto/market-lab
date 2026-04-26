"""TDD tests for iter 023 multi-asset gold_complex basket strategy.

Verifies:
1. Per-asset signal is byte-equivalent to iter 003's signal (no drift).
2. Basket position aggregation is correct (weighted sum ∈ [0, 1]).
3. Cost model applied PER LEG (not on portfolio sum) so per-asset spread
   tiers (8 bps gold / 20 bps silver) are honored.
4. Buy-hold benchmark = continuous-rebalance 60/40 returns.
5. IC-6 rolling correlation diagnostic returns valid exceed-fraction.
6. Mean-hold-time computation handles weighted (non-binary) positions.

Run: ``cd /tmp/ai-trade-gold-swing && uv run pytest studies/gold_swing_loop/iterations/023-2026-04-26-1900-multi-asset-gld-slv-basket/test_basket_signal.py -v``
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent
LOOP_DIR = ITER_DIR.parents[1]
sys.path.insert(0, str(LOOP_DIR))
sys.path.insert(0, str(ITER_DIR))

from cost_models import apply_pepperstone_costs  # noqa: E402


def _make_synth_close(n: int = 600, seed: int = 7, drift: float = 0.0003) -> pd.Series:
    """Synthetic geometric-walk close series of length n (daily index)."""
    rng = np.random.default_rng(seed)
    daily_ret = rng.normal(loc=drift, scale=0.012, size=n)
    eq = np.cumprod(1.0 + daily_ret) * 100.0
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    return pd.Series(eq, index=idx, name="close")


# ---------------------------------------------------------------------------
# 1. Per-asset signal byte-equivalent to iter 003 implementation
# ---------------------------------------------------------------------------


def test_per_asset_signal_matches_iter003_implementation():
    """Iter 023 signal must be the same RSI(2)<5 + SMA(200) state machine
    as iter 003 — we reuse iter 003's helper directly."""
    from run_backtest import connors_rsi2_signal_with_trend_filter

    close = _make_synth_close(n=400)
    df = pd.DataFrame({"close": close})

    pos = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5, sma_trend_period=200
    )
    assert len(pos) == 400
    assert set(pos.unique()).issubset({0.0, 1.0})
    # First 200 bars: SMA(200) is NaN warmup → no entries possible
    assert pos.iloc[:200].sum() == 0.0


# ---------------------------------------------------------------------------
# 2. Basket aggregation: weighted sum is correct, ∈ [0, 1]
# ---------------------------------------------------------------------------


def test_basket_position_is_weighted_sum_in_unit_interval():
    """pos_basket = w_gold * sig_gold + w_silver * sig_silver must be in [0,1]."""
    from run_backtest import build_basket_position

    idx = pd.date_range("2010-01-04", periods=10, freq="B")
    sig_gold = pd.Series([0, 1, 1, 0, 1, 0, 1, 1, 0, 0], dtype=float, index=idx)
    sig_silver = pd.Series([1, 1, 0, 1, 0, 0, 1, 1, 1, 0], dtype=float, index=idx)
    weights = {"gold": 0.6, "silver": 0.4}

    basket = build_basket_position({"gold": sig_gold, "silver": sig_silver}, weights)
    expected = 0.6 * sig_gold + 0.4 * sig_silver
    pd.testing.assert_series_equal(basket, expected, check_names=False)
    assert basket.min() >= 0.0
    assert basket.max() <= 1.0


def test_basket_weights_must_sum_to_one_and_match_keys():
    """Weight validation: sum to 1 ± 1e-9 and match signal keys."""
    from run_backtest import build_basket_position

    idx = pd.date_range("2010-01-04", periods=4, freq="B")
    sig = pd.Series([0, 1, 0, 1], dtype=float, index=idx)
    sigs = {"gold": sig, "silver": sig}

    with pytest.raises(ValueError, match=r"sum"):
        build_basket_position(sigs, {"gold": 0.3, "silver": 0.3})

    with pytest.raises(ValueError, match=r"keys|missing"):
        build_basket_position(sigs, {"gold": 0.6, "platinum": 0.4})


# ---------------------------------------------------------------------------
# 3. Per-leg cost model: spread is computed on per-asset position diffs,
#    NOT on the aggregated portfolio position
# ---------------------------------------------------------------------------


def test_per_leg_cost_applied_separately_with_distinct_spreads():
    """Per-leg spread tiers must be distinct: gold 8 bps, silver 20 bps.
    Total spread cost should be sum of two separate calls, not one call
    on the aggregate position."""
    from run_backtest import compute_basket_pnl

    idx = pd.date_range("2010-01-04", periods=20, freq="B")
    rng = np.random.default_rng(0)
    gld_ret = pd.Series(rng.normal(0.0, 0.01, 20), index=idx)
    slv_ret = pd.Series(rng.normal(0.0, 0.015, 20), index=idx)

    sig_gold = pd.Series([0]*5 + [1]*10 + [0]*5, dtype=float, index=idx)
    sig_silver = pd.Series([0]*8 + [1]*7 + [0]*5, dtype=float, index=idx)

    weights = {"gold": 0.6, "silver": 0.4}
    sigs = {"gold": sig_gold, "silver": sig_silver}
    rets = {"gold": gld_ret, "silver": slv_ret}
    spreads_rt = {"gold": 8.0, "silver": 20.0}

    out = compute_basket_pnl(rets, sigs, weights, spreads_rt)

    # Per-leg breakdown matches direct call
    pos_gold_full = sig_gold * weights["gold"]
    pos_silver_full = sig_silver * weights["silver"]
    br_gold = apply_pepperstone_costs(
        gld_ret, pos_gold_full, spread_rt_bps=8.0, intraday_close=False,
    )
    br_silver = apply_pepperstone_costs(
        slv_ret, pos_silver_full, spread_rt_bps=20.0, intraday_close=False,
    )
    expected_net = (br_gold.net_pnl + br_silver.net_pnl)
    pd.testing.assert_series_equal(
        out["net_pnl"], expected_net, check_names=False, atol=1e-12,
    )
    assert out["spread_total_bps"]["gold"] != out["spread_total_bps"]["silver"]


# ---------------------------------------------------------------------------
# 4. Buy-hold benchmark is continuous-rebalance 60/40 returns
# ---------------------------------------------------------------------------


def test_basket_buyhold_benchmark_is_weighted_returns():
    """Benchmark = w_gold × gld_ret + w_silver × slv_ret (continuous rebalance)."""
    from run_backtest import basket_buyhold_returns

    idx = pd.date_range("2010-01-04", periods=10, freq="B")
    gld = pd.Series(np.linspace(100, 110, 10), index=idx)
    slv = pd.Series(np.linspace(20, 25, 10), index=idx)
    weights = {"gold": 0.6, "silver": 0.4}

    bh = basket_buyhold_returns({"gold": gld, "silver": slv}, weights)
    expected = 0.6 * gld.pct_change().fillna(0.0) + 0.4 * slv.pct_change().fillna(0.0)
    pd.testing.assert_series_equal(bh, expected, check_names=False, atol=1e-12)


# ---------------------------------------------------------------------------
# 5. IC-6 rolling-correlation diagnostic
# ---------------------------------------------------------------------------


def test_ic6_correlation_diagnostic_returns_exceed_fraction():
    """IC-6 helper computes rolling-60d |ρ| and returns exceed-fraction
    at threshold τ. Self-correlation should give exceed_frac ~ 1.0."""
    from run_backtest import ic6_rolling_correlation_diagnostic

    idx = pd.date_range("2010-01-04", periods=300, freq="B")
    rng = np.random.default_rng(42)
    a = pd.Series(rng.normal(0.0, 0.01, 300), index=idx)
    diag = ic6_rolling_correlation_diagnostic(a, a, window=60, threshold=0.30)

    # Self-correlation should exceed 0.30 on essentially every valid window
    assert diag["exceed_frac"] > 0.95
    assert diag["window"] == 60
    assert diag["threshold"] == 0.30
    assert "static_rho" in diag
    assert abs(diag["static_rho"] - 1.0) < 1e-9

    # Independent series should have exceed_frac near 0
    b = pd.Series(rng.normal(0.0, 0.01, 300), index=idx)
    diag2 = ic6_rolling_correlation_diagnostic(a, b, window=60, threshold=0.30)
    assert diag2["exceed_frac"] < 0.30  # noisy but should not be high


# ---------------------------------------------------------------------------
# 6. Mean-hold-time on weighted (non-binary) basket positions
# ---------------------------------------------------------------------------


def test_mean_hold_time_for_weighted_basket():
    """For weighted basket positions ∈ [0, 1], mean hold = mean trade
    duration where in_trade ⇔ position > 0 (any nonzero exposure)."""
    from run_backtest import compute_basket_mean_hold

    idx = pd.date_range("2010-01-04", periods=20, freq="B")
    # Trade 1: bars 2-5 (4 bars hold), Trade 2: bars 8-13 (6 bars), Trade 3: bars 16-19 (4)
    pos = pd.Series(
        [0, 0, 0.6, 1.0, 0.4, 0.6, 0, 0, 0.4, 0.6, 1.0, 1.0, 0.6, 0.4, 0, 0, 0.6, 0.4, 0.6, 1.0],
        dtype=float, index=idx,
    )
    mean_hold, n_trades = compute_basket_mean_hold(pos)
    assert n_trades == 3
    # Hold lengths: 4, 6, 4 → mean = 14/3 ≈ 4.667
    assert abs(mean_hold - 14.0 / 3.0) < 1e-9
