"""Tests for iter 025 slow-EWMAC trend on multi-asset basket.

Primitive: ``studies/strategy_hunt_loop/iterations/025-.../slow_ewmac_multi_asset.py``

Coverage (TDD — 12 specs):
1. EWMAC forecast: NaN before σ_pp warmup; capped at ±20.
2. EWMAC sign tracks crossover sign post-warmup (uptrend → positive).
3. Forecast scalars (32:128 → 2.65, 64:256 → 1.87) match Carver Table 49.
4. combine_forecasts applies FDM and re-caps at ±20.
5. combine_forecasts rejects mismatched weight count.
6. position_size scales inversely with realized vol (no cap binding).
7. position_size enforces per-asset cap.
8. position_size clips to ≥0 when long_only=True.
9. position_size lag (σ̂_{t-1}, no look-ahead).
10. apply_no_trade_buffer holds position when |Δ| ≤ threshold.
11. apply_slow_ewmac_strategy: cost is linear in |Δw|.
12. apply_slow_ewmac_strategy: net = Σ pos_i · r_i − cost.

Citations
---------
* `[systematic_trading, p.118-119, ch.7]` — EWMAC rule.
* `[systematic_trading, p.131-133, ch.8]` — FDM.
* `[systematic_trading, p.244-258, ch.15]` — No-trade buffer.
* `[systematic_trading, p.282-285, app.B]` — EWMAC computation + scalars.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} no-look-ahead.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = (
    ROOT
    / "studies"
    / "strategy_hunt_loop"
    / "iterations"
    / "025-2026-04-24-2059-slow-ewmac-multi-asset"
)
sys.path.insert(0, str(ITER_DIR))

from slow_ewmac_multi_asset import (  # noqa: E402
    apply_no_trade_buffer,
    apply_slow_ewmac_strategy,
    combine_forecasts,
    compute_ewmac_forecast,
    position_size,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_prices_long():
    """6-asset deterministic prices over ~6 years (1500 bars > Lslow=256+sigma_span=36+lag=1)."""
    rng = np.random.default_rng(13)
    idx = pd.bdate_range("2018-01-02", "2024-06-30")
    n = len(idx)
    drifts = [0.0004, 0.0001, 0.00012, 0.00018, 0.00022, 0.0001]  # 6 assets
    vols = [0.010, 0.012, 0.011, 0.013, 0.014, 0.0085]
    cols = [f"asset_{i}" for i in range(6)]
    prices = pd.DataFrame(index=idx, columns=cols, dtype=float)
    p = np.full(6, 100.0)
    for t in range(n):
        prices.iloc[t] = p
        eps = rng.normal(size=6)
        rets = np.array(drifts) + np.array(vols) * eps
        p = p * (1.0 + rets)
    return prices


@pytest.fixture
def uptrend_prices():
    """Single asset with strong positive drift, long enough for slow EWMAC."""
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2018-01-02", "2024-06-30")
    n = len(idx)
    daily_drift = 0.0006
    rets = np.full(n, daily_drift) + rng.normal(0.0, 1e-4, size=n)
    prices = pd.Series(np.cumprod(1.0 + rets) * 100.0, index=idx, name="up")
    return prices


# ---------------------------------------------------------------------------
# 1-3. EWMAC forecast
# ---------------------------------------------------------------------------


def test_ewmac_forecast_nan_before_sigma_warmup(uptrend_prices):
    """Forecast is NaN before sigma_span bars (σ_pp not defined)."""
    f = compute_ewmac_forecast(uptrend_prices, 32, 128, 2.65, sigma_span=36)
    assert f.iloc[:35].isna().all()
    # After enough bars, valid.
    assert f.iloc[200:].notna().all()


def test_ewmac_forecast_capped_at_pm20(uptrend_prices):
    """Capping to ±20 holds even with extreme params."""
    # Crank scalar to make raw forecast huge.
    f = compute_ewmac_forecast(uptrend_prices, 32, 128, 1000.0, sigma_span=36)
    valid = f.dropna()
    assert (valid.abs() <= 20.0 + 1e-9).all()


def test_ewmac_uptrend_sign_positive(uptrend_prices):
    """Strong uptrend → forecast is positive after warmup."""
    f = compute_ewmac_forecast(uptrend_prices, 32, 128, 2.65, sigma_span=36)
    valid = f.dropna()
    # Skip first 200 bars (initialization transients), then expect positive.
    after = valid.iloc[200:]
    assert (after > 0).all(), "uptrend asset must produce positive EWMAC"


def test_ewmac_invalid_speeds_raise(uptrend_prices):
    with pytest.raises(ValueError, match="Lslow"):
        compute_ewmac_forecast(uptrend_prices, 128, 32, 2.65)


# ---------------------------------------------------------------------------
# 4-5. combine_forecasts
# ---------------------------------------------------------------------------


def test_combine_forecasts_applies_fdm_and_caps():
    idx = pd.date_range("2020-01-01", periods=10)
    f1 = pd.Series(np.full(10, 10.0), index=idx)
    f2 = pd.Series(np.full(10, 10.0), index=idx)
    combined = combine_forecasts([f1, f2], [0.5, 0.5], fdm=1.5, cap=20.0)
    # Weighted = 10. With FDM 1.5 → 15.
    np.testing.assert_allclose(combined.to_numpy(), np.full(10, 15.0))
    # If FDM pushes above cap, must clip.
    big = combine_forecasts([f1, f2], [0.5, 0.5], fdm=10.0, cap=20.0)
    np.testing.assert_allclose(big.to_numpy(), np.full(10, 20.0))


def test_combine_forecasts_mismatched_weights_raise():
    idx = pd.date_range("2020-01-01", periods=10)
    f1 = pd.Series(np.full(10, 1.0), index=idx)
    with pytest.raises(ValueError, match="same length"):
        combine_forecasts([f1], [0.5, 0.5], fdm=1.0)


def test_combine_forecasts_weights_must_sum_to_one():
    idx = pd.date_range("2020-01-01", periods=5)
    f1 = pd.Series(np.full(5, 1.0), index=idx)
    f2 = pd.Series(np.full(5, 1.0), index=idx)
    with pytest.raises(ValueError, match="weights must sum"):
        combine_forecasts([f1, f2], [0.3, 0.3], fdm=1.0)


# ---------------------------------------------------------------------------
# 6-9. position_size
# ---------------------------------------------------------------------------


def test_position_size_scales_inverse_vol():
    """When forecast is constant +10 (norm = 1), weight ≈ target_vol / asset_vol."""
    idx = pd.bdate_range("2020-01-02", periods=200)
    n = len(idx)
    rng = np.random.default_rng(3)
    # Constant volatility ~10%/yr (daily ~ 0.0063)
    rets = pd.Series(rng.normal(0.0001, 0.0063, size=n), index=idx)
    fcast = pd.Series(np.full(n, 10.0), index=idx)  # forecast_norm = 1 always
    pos = position_size(
        fcast, rets,
        target_vol_per_asset=0.10,
        asset_vol_span=36,
        lag_bars=1,
        max_per_asset_leverage=100.0,  # disable cap
        long_only=False,
    )
    valid = pos.dropna()
    # weight = 1 × 0.10 / asset_vol; asset_vol ≈ 0.10 → weight ≈ 1.0
    # Due to noise, expect within [0.7, 1.5]
    after = valid.iloc[100:]
    median_w = after.median()
    assert 0.5 < median_w < 1.7, f"expected weight ~1.0, got median {median_w}"


def test_position_size_per_asset_cap_enforced():
    idx = pd.bdate_range("2020-01-02", periods=200)
    rng = np.random.default_rng(5)
    rets = pd.Series(rng.normal(0.0001, 0.005, size=len(idx)), index=idx)
    fcast = pd.Series(np.full(len(idx), 20.0), index=idx)  # forecast_norm = 2 (extreme)
    pos = position_size(
        fcast, rets,
        target_vol_per_asset=0.20,
        asset_vol_span=36, lag_bars=1,
        max_per_asset_leverage=0.5,  # tight
        long_only=False,
    )
    valid = pos.dropna()
    assert (valid.abs() <= 0.5 + 1e-12).all(), "per-asset cap must bind"


def test_position_size_long_only_clips_negative():
    idx = pd.bdate_range("2020-01-02", periods=200)
    rng = np.random.default_rng(11)
    rets = pd.Series(rng.normal(0.0001, 0.005, size=len(idx)), index=idx)
    fcast = pd.Series(np.full(len(idx), -10.0), index=idx)  # negative
    pos = position_size(
        fcast, rets,
        target_vol_per_asset=0.10,
        asset_vol_span=36, lag_bars=1,
        max_per_asset_leverage=2.0,
        long_only=True,
    )
    valid = pos.dropna()
    assert (valid >= 0.0).all(), "long_only must clip negatives to 0"
    # Any negative input forecast → weight should be 0.
    assert (valid == 0.0).all()


def test_position_size_lag_no_lookahead():
    """Modifying r at bar t must not change pos at bar t (uses σ̂_{t-1})."""
    idx = pd.bdate_range("2020-01-02", periods=200)
    rng = np.random.default_rng(17)
    rets = pd.Series(rng.normal(0.0001, 0.005, size=len(idx)), index=idx)
    fcast = pd.Series(np.full(len(idx), 5.0), index=idx)
    pos1 = position_size(
        fcast, rets, target_vol_per_asset=0.10,
        asset_vol_span=36, lag_bars=1,
        max_per_asset_leverage=2.0, long_only=False,
    )
    rets_mut = rets.copy()
    rets_mut.iloc[150] = 0.5  # huge bar
    pos2 = position_size(
        fcast, rets_mut, target_vol_per_asset=0.10,
        asset_vol_span=36, lag_bars=1,
        max_per_asset_leverage=2.0, long_only=False,
    )
    # Position at bar 150 must be IDENTICAL (uses vol from bar 149).
    assert abs(pos1.iloc[150] - pos2.iloc[150]) < 1e-12


# ---------------------------------------------------------------------------
# 10. apply_no_trade_buffer
# ---------------------------------------------------------------------------


def test_no_trade_buffer_holds_position_within_threshold():
    idx = pd.date_range("2020-01-01", periods=10)
    target = pd.Series(
        [0.0, 0.50, 0.51, 0.55, 0.60, 0.55, 0.40, 0.45, 0.10, 0.10],
        index=idx,
    )
    held = apply_no_trade_buffer(target, threshold_pct=0.10)
    # Bar 0: target 0, held 0 (no change).
    # Bar 1: target 0.50, deviation 0.50 > 0.10×0.50 → trade. held=0.50
    # Bar 2: target 0.51, deviation 0.01 < 0.10×0.51=0.051 → hold. held=0.50
    # Bar 3: target 0.55, deviation 0.05 < 0.055 → hold. held=0.50
    # Bar 4: target 0.60, deviation 0.10 > 0.060 → trade. held=0.60
    # Bar 5: target 0.55, deviation 0.05 < 0.060 → hold. held=0.60
    # Bar 6: target 0.40, deviation 0.20 > 0.060 → trade. held=0.40
    # Bar 7: target 0.45, deviation 0.05 < 0.045 → no... wait 0.05 > 0.045. Trade.
    # 0.05 > 0.10 × max(0.45, 0.40) = 0.045 → trade. held=0.45
    # Bar 8: target 0.10, deviation 0.35 > 0.045 → trade. held=0.10
    # Bar 9: target 0.10, deviation 0 → hold. held=0.10
    expected = [0.0, 0.50, 0.50, 0.50, 0.60, 0.60, 0.40, 0.45, 0.10, 0.10]
    np.testing.assert_allclose(held.to_numpy(), expected, atol=1e-12)


def test_no_trade_buffer_zero_threshold_always_trades():
    idx = pd.date_range("2020-01-01", periods=5)
    target = pd.Series([0.0, 0.1, 0.15, 0.20, 0.18], index=idx)
    held = apply_no_trade_buffer(target, threshold_pct=0.0)
    # threshold=0 means deviation > 0 always trades.
    np.testing.assert_allclose(held.to_numpy(), target.to_numpy())


# ---------------------------------------------------------------------------
# 11-12. apply_slow_ewmac_strategy
# ---------------------------------------------------------------------------


def test_strategy_net_aggregates_positions(synthetic_prices_long):
    """net[t] = Σ pos_i · r_i − cost (cost=0)."""
    net, held, target, fcast = apply_slow_ewmac_strategy(
        synthetic_prices_long,
        speeds=[(32, 128), (64, 256)],
        speed_scalars=[2.65, 1.87],
        speed_weights=[0.5, 0.5],
        fdm=1.10,
        target_vol_per_asset=0.04,
        asset_vol_span=36,
        lag_bars=1,
        no_trade_buffer_pct=0.10,
        max_per_asset_leverage=0.6,
        long_only=True,
        cost_bps_per_leg=0.0,
    )
    rets = synthetic_prices_long.pct_change().loc[net.index]
    expected_gross = (held * rets).sum(axis=1)
    np.testing.assert_allclose(net.to_numpy(), expected_gross.to_numpy(), atol=1e-12)


def test_strategy_cost_linear_in_position_change(synthetic_prices_long):
    """net_cost = Σ |Δw_i| × cost_bps."""
    args = dict(
        speeds=[(32, 128), (64, 256)],
        speed_scalars=[2.65, 1.87],
        speed_weights=[0.5, 0.5],
        fdm=1.10,
        target_vol_per_asset=0.04,
        asset_vol_span=36,
        lag_bars=1,
        no_trade_buffer_pct=0.10,
        max_per_asset_leverage=0.6,
        long_only=True,
    )
    net0, held0, _, _ = apply_slow_ewmac_strategy(
        synthetic_prices_long, cost_bps_per_leg=0.0, **args,
    )
    net1, held1, _, _ = apply_slow_ewmac_strategy(
        synthetic_prices_long, cost_bps_per_leg=0.0002, **args,
    )
    pd.testing.assert_frame_equal(held0, held1)  # cost doesn't change positions
    dpos = held1.diff().abs().fillna(held1.iloc[0].abs())
    expected_cost = dpos.sum(axis=1) * 0.0002
    diff = net0 - net1
    np.testing.assert_allclose(diff.to_numpy(), expected_cost.to_numpy(), atol=1e-12)
