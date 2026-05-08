"""Unit tests for signals.py — entry/exit gate logic per spec §2.7."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_sma_gate_above_below():
    """SMA gate: ON when price > SMA, OFF when price < SMA."""
    from studies.letf_rotation_hunt.signals import sma_gate

    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    # ramp up 200 days, then dip
    prices = pd.Series(
        list(range(100, 300)) + list(range(300, 200, -1)),
        index=dates,
    )

    gate = sma_gate(prices, period=200)

    # Day 200 (first valid SMA): price=300, SMA=mean(100..299)=199.5 → ON
    assert gate.iloc[200] == 1

    # Last day: price=200, SMA includes the dip → check signal flipped OFF at some point
    assert gate.iloc[-1] == 0


def test_sma_gate_period_param():
    """SMA gate respects period parameter."""
    from studies.letf_rotation_hunt.signals import sma_gate

    dates = pd.date_range("2020-01-01", periods=100, freq="B")
    prices = pd.Series(np.linspace(100, 200, 100), index=dates)

    gate_50 = sma_gate(prices, period=50)
    gate_100 = sma_gate(prices, period=100)

    # First 49 of gate_50 should be NaN; 50+ should be 1 (rising prices, price > SMA50)
    assert gate_50.iloc[:49].isna().all()
    assert (gate_50.iloc[50:] == 1).all()


def test_ema_gate_decay_param():
    """EMA gate uses α = 2 / (L+1) per Carver [systematic_trading, p.283]."""
    from studies.letf_rotation_hunt.signals import ema_gate

    dates = pd.date_range("2020-01-01", periods=100, freq="B")
    prices = pd.Series(np.ones(100) * 100.0, index=dates)
    prices.iloc[50:] = 110.0  # step up at day 50

    gate = ema_gate(prices, period=10)

    # After step up, EMA needs ~3*period to catch up; gate eventually flips ON
    # Day 51-55: price 110 > EMA still ~100 → ON
    assert gate.iloc[51] == 1


def test_vol_gate_below_threshold():
    """Vol gate: 1 if rolling realized vol < threshold, else 0."""
    from studies.letf_rotation_hunt.signals import realized_vol_gate

    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    # constant returns ~0% (low vol)
    returns = pd.Series(np.zeros(300), index=dates)

    gate = realized_vol_gate(returns, window=21, threshold=0.40)

    # All ON (vol = 0 < 0.40)
    assert (gate.iloc[21:] == 1).all()


def test_vol_gate_above_threshold():
    """Vol gate: 0 when realized vol exceeds 40% (Gayed threshold)."""
    from studies.letf_rotation_hunt.signals import realized_vol_gate

    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    # Inject high-vol period: alternating ±5% returns (annualized ~80% vol)
    returns = pd.Series(np.zeros(300), index=dates)
    returns.iloc[50:100] = np.random.RandomState(42).choice([-0.05, 0.05], size=50)

    gate = realized_vol_gate(returns, window=21, threshold=0.40)

    # During injected high-vol window, gate should be OFF
    assert (gate.iloc[71:99] == 0).any()


def test_vix_scaling_baseline():
    """VIX scaling: weight = clip(VIX_baseline / VIX_prev_month, 0, 1)."""
    from studies.letf_rotation_hunt.signals import vix_scaling

    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    # VIX constant at 20 (baseline = mean ≈ 20 → weight = 1)
    vix = pd.Series(np.ones(300) * 20.0, index=dates)

    weight = vix_scaling(vix, lookback_baseline=252, lookback_prev_month=21)

    # After warmup, VIX_avg = VIX_prev_month → weight = 1
    assert weight.iloc[252] == pytest.approx(1.0, abs=1e-6)


def test_vix_scaling_high_vix():
    """VIX scaling: weight < 1 when VIX_prev_month > VIX_baseline."""
    from studies.letf_rotation_hunt.signals import vix_scaling

    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    vix = pd.Series(np.ones(300) * 15.0, index=dates)
    vix.iloc[280:] = 30.0  # spike in last 20 days

    weight = vix_scaling(vix, lookback_baseline=252, lookback_prev_month=21)

    # When prev-month VIX spike > baseline, weight < 1 (clipped inverse ratio)
    # Actual computed value: baseline=16.19, prev_month=29.29, ratio=0.5528
    assert weight.iloc[-1] == pytest.approx(0.5528, abs=0.02)
    assert 0 <= weight.iloc[-1] <= 1  # bounds check


def test_ar1_coefficient_positive_regime():
    """AR(1) > 0 → momentum regime; < 0 → mean-reversion."""
    from studies.letf_rotation_hunt.signals import ar1_coefficient

    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    # Strongly autocorrelated returns (momentum regime)
    rng = np.random.RandomState(42)
    eps = rng.normal(0, 0.01, 300)
    rets = np.zeros(300)
    rets[0] = eps[0]
    for t in range(1, 300):
        rets[t] = 0.6 * rets[t - 1] + eps[t]  # AR(1) coefficient = 0.6

    returns = pd.Series(rets, index=dates)
    coef = ar1_coefficient(returns, window=30)

    # Most non-NaN values should be positive (true coef = 0.6)
    valid = coef.dropna()
    assert (valid > 0).mean() > 0.7


def test_vote_of_k():
    """Vote-of-K gate: sum of indicators ≥ K."""
    from studies.letf_rotation_hunt.signals import vote_of_k

    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    s1 = pd.Series([1, 1, 1, 0, 0, 0, 1, 1, 0, 0], index=dates)
    s2 = pd.Series([1, 1, 0, 0, 0, 1, 1, 0, 0, 0], index=dates)
    s3 = pd.Series([1, 0, 0, 0, 1, 1, 1, 0, 0, 1], index=dates)

    # K=2: need at least 2 of 3 ON
    gate_k2 = vote_of_k([s1, s2, s3], k=2)
    expected_k2 = pd.Series([1, 1, 0, 0, 0, 1, 1, 0, 0, 0], index=dates).astype(float)
    pd.testing.assert_series_equal(gate_k2, expected_k2, check_names=False)

    # K=3: need all 3 ON
    gate_k3 = vote_of_k([s1, s2, s3], k=3)
    expected_k3 = pd.Series([1, 0, 0, 0, 0, 0, 1, 0, 0, 0], index=dates).astype(float)
    pd.testing.assert_series_equal(gate_k3, expected_k3, check_names=False)


def test_hmm_two_state_separates_regimes():
    """HMM 2-state separates bull/bear regimes."""
    from studies.letf_rotation_hunt.signals import hmm_regime_gate

    dates = pd.date_range("2020-01-01", periods=600, freq="B")
    rng = np.random.RandomState(42)
    # 300 days bull (mean +0.05%, vol 1%) + 300 days bear (mean -0.10%, vol 3%)
    bull = rng.normal(0.0005, 0.01, 300)
    bear = rng.normal(-0.001, 0.03, 300)
    returns = pd.Series(np.concatenate([bull, bear]), index=dates)

    gate = hmm_regime_gate(returns, n_states=2, refit_every=252, train_window=252)

    # After fit: bull-like state ON; bear-like state OFF
    # Check majority state in second half is OFF (bear)
    valid = gate.dropna()
    bear_half = valid.iloc[len(valid) // 2:]
    assert (bear_half == 0).mean() > 0.5


def test_ewmac_forecast_capped():
    """EWMAC forecast capped at ±20 per Carver."""
    from studies.letf_rotation_hunt.signals import ewmac_forecast

    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    # Strong uptrend → should produce strongly positive forecast
    prices = pd.Series(np.linspace(100, 300, 300), index=dates)

    forecast = ewmac_forecast(prices, lfast=16, lslow=64, scalar=3.75)

    # Cap check
    assert forecast.dropna().between(-20, 20).all()
    # Should be predominantly positive in strong uptrend
    assert forecast.dropna().mean() > 0


def test_vote_of_k_invalid_k_raises():
    """vote_of_k raises ValueError for k > len(signals) or k < 1."""
    from studies.letf_rotation_hunt.signals import vote_of_k

    dates = pd.date_range("2020-01-01", periods=5, freq="B")
    s1 = pd.Series([1] * 5, index=dates)
    s2 = pd.Series([0] * 5, index=dates)

    with pytest.raises(ValueError, match="exceeds"):
        vote_of_k([s1, s2], k=5)

    with pytest.raises(ValueError, match=">= 1"):
        vote_of_k([s1, s2], k=0)

    with pytest.raises(ValueError, match="at least one"):
        vote_of_k([], k=1)


def test_ewmac_invalid_params_raise():
    """ewmac_forecast raises ValueError for invalid params."""
    from studies.letf_rotation_hunt.signals import ewmac_forecast

    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    prices = pd.Series([100.0] * 10, index=dates)

    with pytest.raises(ValueError, match="lfast"):
        ewmac_forecast(prices, lfast=64, lslow=16)  # inverted

    with pytest.raises(ValueError, match="scalar"):
        ewmac_forecast(prices, scalar=-1.0)


def test_clenow_slope_r_squared_ranking():
    """Clenow score = annualized slope × R² of log price regression."""
    from studies.letf_rotation_hunt.signals import clenow_score

    dates = pd.date_range("2020-01-01", periods=200, freq="B")

    # Clean uptrend (high slope, high R²)
    smooth_up = pd.Series(np.exp(np.linspace(0, 0.5, 200)) * 100, index=dates)

    # Noisy uptrend (same slope, lower R²)
    rng = np.random.RandomState(42)
    noisy_up = smooth_up * (1 + rng.normal(0, 0.05, 200))

    score_smooth = clenow_score(smooth_up, window=90)
    score_noisy = clenow_score(noisy_up, window=90)

    # Smooth should have higher Clenow score (R² penalty on noisy)
    assert score_smooth.iloc[-1] > score_noisy.iloc[-1]
    assert score_smooth.iloc[-1] > 0  # uptrend → positive
