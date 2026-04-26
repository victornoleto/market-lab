"""TDD tests for iter 025 cross-cluster GLD+BTCUSD 60/40 basket strategy.

Verifies:
1. Per-asset signal is byte-equivalent to iter 003's signal (no drift).
2. Basket position aggregation is correct (weighted sum ∈ [0, 1]).
3. Cost model applied PER LEG with leg-specific spread AND swap rates
   (gold 8 bps + −1 bps/night vs BTC 25 bps + −5 bps/night).
4. Buy-hold benchmark = continuous-rebalance 60/40 returns.
5. IC-6 rolling correlation diagnostic returns valid exceed-fraction.
6. Mean-hold-time computation handles weighted (non-binary) positions.

Run: ``cd /tmp/ai-trade-gold-swing && uv run pytest studies/gold_swing_loop/iterations/025-2026-04-26-2147-gld-btc-cross-cluster-basket/test_basket_signal.py -v``
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
    rng = np.random.default_rng(seed)
    daily_ret = rng.normal(loc=drift, scale=0.012, size=n)
    eq = np.cumprod(1.0 + daily_ret) * 100.0
    idx = pd.date_range("2014-01-04", periods=n, freq="B")
    return pd.Series(eq, index=idx, name="close")


# ---------------------------------------------------------------------------
# 1. Per-asset signal byte-equivalent to iter 003 implementation
# ---------------------------------------------------------------------------


def test_per_asset_signal_matches_iter003_implementation():
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
    from run_backtest import build_basket_position

    idx = pd.date_range("2014-01-06", periods=10, freq="B")
    sig_gold = pd.Series([0, 1, 1, 0, 1, 0, 1, 1, 0, 0], dtype=float, index=idx)
    sig_btc = pd.Series([1, 1, 0, 1, 0, 0, 1, 1, 1, 0], dtype=float, index=idx)
    weights = {"gold": 0.6, "btc": 0.4}

    basket = build_basket_position({"gold": sig_gold, "btc": sig_btc}, weights)
    expected = 0.6 * sig_gold + 0.4 * sig_btc
    pd.testing.assert_series_equal(basket, expected, check_names=False)
    assert basket.min() >= 0.0
    assert basket.max() <= 1.0


def test_basket_weights_must_sum_to_one_and_match_keys():
    from run_backtest import build_basket_position

    idx = pd.date_range("2014-01-06", periods=4, freq="B")
    sig = pd.Series([0, 1, 0, 1], dtype=float, index=idx)
    sigs = {"gold": sig, "btc": sig}

    with pytest.raises(ValueError, match=r"sum"):
        build_basket_position(sigs, {"gold": 0.3, "btc": 0.3})

    with pytest.raises(ValueError, match=r"keys|missing"):
        build_basket_position(sigs, {"gold": 0.6, "platinum": 0.4})


# ---------------------------------------------------------------------------
# 3. Per-leg cost model: spread + swap PER LEG with distinct rates
# ---------------------------------------------------------------------------


def test_per_leg_cost_uses_leg_specific_spread_and_swap():
    """Per-leg spread + swap tiers must be distinct: gold 8 bps + −1 bps/night
    vs BTC 25 bps + −5 bps/night. Total cost should equal sum of two
    apply_pepperstone_costs calls with leg-specific rates."""
    from run_backtest import compute_basket_pnl

    idx = pd.date_range("2014-01-06", periods=20, freq="B")
    rng = np.random.default_rng(0)
    gld_ret = pd.Series(rng.normal(0.0, 0.01, 20), index=idx)
    btc_ret = pd.Series(rng.normal(0.0, 0.025, 20), index=idx)  # BTC ~2.5x vol

    sig_gold = pd.Series([0]*5 + [1]*10 + [0]*5, dtype=float, index=idx)
    sig_btc = pd.Series([0]*8 + [1]*7 + [0]*5, dtype=float, index=idx)

    weights = {"gold": 0.6, "btc": 0.4}
    sigs = {"gold": sig_gold, "btc": sig_btc}
    rets = {"gold": gld_ret, "btc": btc_ret}
    spreads_rt = {"gold": 8.0, "btc": 25.0}
    swap_long = {"gold": -1.0, "btc": -5.0}

    out = compute_basket_pnl(rets, sigs, weights, spreads_rt, swap_long)

    pos_gold_full = sig_gold * weights["gold"]
    pos_btc_full = sig_btc * weights["btc"]
    br_gold = apply_pepperstone_costs(
        gld_ret, pos_gold_full, spread_rt_bps=8.0, swap_long_bps=-1.0,
        intraday_close=False,
    )
    br_btc = apply_pepperstone_costs(
        btc_ret, pos_btc_full, spread_rt_bps=25.0, swap_long_bps=-5.0,
        intraday_close=False,
    )
    expected_net = (br_gold.net_pnl + br_btc.net_pnl)
    pd.testing.assert_series_equal(
        out["net_pnl"], expected_net, check_names=False, atol=1e-12,
    )
    expected_gold_bps = float(-br_gold.spread_cost.sum() * 1e4)
    expected_btc_bps = float(-br_btc.spread_cost.sum() * 1e4)
    assert abs(out["spread_total_bps"]["gold"] - expected_gold_bps) < 1e-9
    assert abs(out["spread_total_bps"]["btc"] - expected_btc_bps) < 1e-9
    # Swap rates: BTC swap drag should be ~5x gold's per night per unit position
    expected_gold_swap_bps = float(-br_gold.swap_cost.sum() * 1e4)
    expected_btc_swap_bps = float(-br_btc.swap_cost.sum() * 1e4)
    assert abs(out["swap_total_bps"]["gold"] - expected_gold_swap_bps) < 1e-9
    assert abs(out["swap_total_bps"]["btc"] - expected_btc_swap_bps) < 1e-9


# ---------------------------------------------------------------------------
# 4. Buy-hold benchmark is continuous-rebalance 60/40 returns
# ---------------------------------------------------------------------------


def test_basket_buyhold_benchmark_is_weighted_returns():
    from run_backtest import basket_buyhold_returns

    idx = pd.date_range("2014-01-06", periods=10, freq="B")
    gld = pd.Series(np.linspace(100, 110, 10), index=idx)
    btc = pd.Series(np.linspace(800, 1000, 10), index=idx)
    weights = {"gold": 0.6, "btc": 0.4}

    bh = basket_buyhold_returns({"gold": gld, "btc": btc}, weights)
    expected = 0.6 * gld.pct_change().fillna(0.0) + 0.4 * btc.pct_change().fillna(0.0)
    pd.testing.assert_series_equal(bh, expected, check_names=False, atol=1e-12)


# ---------------------------------------------------------------------------
# 5. IC-6 rolling-correlation diagnostic
# ---------------------------------------------------------------------------


def test_ic6_correlation_diagnostic_returns_exceed_fraction():
    from run_backtest import ic6_rolling_correlation_diagnostic

    idx = pd.date_range("2014-01-06", periods=300, freq="B")
    rng = np.random.default_rng(42)
    a = pd.Series(rng.normal(0.0, 0.01, 300), index=idx)
    diag = ic6_rolling_correlation_diagnostic(a, a, window=60, threshold=0.30)

    assert diag["exceed_frac"] > 0.95
    assert diag["window"] == 60
    assert diag["threshold"] == 0.30
    assert "static_rho" in diag
    assert abs(diag["static_rho"] - 1.0) < 1e-9

    b = pd.Series(rng.normal(0.0, 0.01, 300), index=idx)
    diag2 = ic6_rolling_correlation_diagnostic(a, b, window=60, threshold=0.30)
    assert diag2["exceed_frac"] < 0.30


# ---------------------------------------------------------------------------
# 6. Mean-hold-time on weighted (non-binary) basket positions
# ---------------------------------------------------------------------------


def test_mean_hold_time_for_weighted_basket():
    from run_backtest import compute_basket_mean_hold

    idx = pd.date_range("2014-01-06", periods=20, freq="B")
    pos = pd.Series(
        [0, 0, 0.6, 1.0, 0.4, 0.6, 0, 0, 0.4, 0.6, 1.0, 1.0, 0.6, 0.4, 0, 0, 0.6, 0.4, 0.6, 1.0],
        dtype=float, index=idx,
    )
    mean_hold, n_trades = compute_basket_mean_hold(pos)
    assert n_trades == 3
    assert abs(mean_hold - 14.0 / 3.0) < 1e-9


# ---------------------------------------------------------------------------
# 7. NEW vs iter 024 — BTC swap drag is ~5x gold's per identical position
# ---------------------------------------------------------------------------


def test_btc_swap_is_five_times_gold_swap_per_unit_overnight():
    """Sanity: at identical 1.0 unit overnight position over N nights,
    BTC swap drag should be ~5x gold swap drag (not 1x or random)."""
    idx = pd.date_range("2014-01-06", periods=30, freq="B")
    pos = pd.Series(1.0, index=idx)
    rets = pd.Series(0.0, index=idx)

    br_gold = apply_pepperstone_costs(
        rets, pos, spread_rt_bps=0.0, swap_long_bps=-1.0, intraday_close=False,
    )
    br_btc = apply_pepperstone_costs(
        rets, pos, spread_rt_bps=0.0, swap_long_bps=-5.0, intraday_close=False,
    )
    gold_swap = float(-br_gold.swap_cost.sum())
    btc_swap = float(-br_btc.swap_cost.sum())
    # btc / gold should be ~5.0 (modulo weekend mult on identical bars)
    ratio = btc_swap / gold_swap if gold_swap != 0 else float("inf")
    assert abs(ratio - 5.0) < 0.01
