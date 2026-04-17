"""Tests for screener.hurst — structure-function Hurst estimator.

Citation: ``[algo_trading_chan, p.44-46, ch.2]``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.screener.hurst import HurstResult, hurst_exponent


def _gbm_prices(n: int = 1000, seed: int = 0) -> pd.Series:
    rng = np.random.default_rng(seed)
    log_ret = rng.normal(0.0, 0.01, size=n)
    log_p = np.cumsum(log_ret)
    return pd.Series(
        np.exp(log_p),
        index=pd.date_range("2020-01-01", periods=n, freq="B"),
    )


def _ar1_mean_reverting(n: int = 1000, phi: float = 0.5, seed: int = 1) -> pd.Series:
    """AR(1) on log-returns with negative auto-correlation → MR series."""
    rng = np.random.default_rng(seed)
    eps = rng.normal(0.0, 0.01, size=n)
    log_ret = np.empty(n)
    log_ret[0] = eps[0]
    for i in range(1, n):
        # negative phi on the prior return => mean-reverting log-prices
        log_ret[i] = -phi * log_ret[i - 1] + eps[i]
    log_p = np.cumsum(log_ret)
    return pd.Series(
        np.exp(log_p),
        index=pd.date_range("2020-01-01", periods=n, freq="B"),
    )


def _trending(n: int = 1000, drift: float = 0.001, seed: int = 2) -> pd.Series:
    """Strong drift with low noise → trending H > 0.5."""
    rng = np.random.default_rng(seed)
    log_ret = drift + rng.normal(0.0, 0.0005, size=n)
    log_p = np.cumsum(log_ret)
    return pd.Series(
        np.exp(log_p),
        index=pd.date_range("2020-01-01", periods=n, freq="B"),
    )


class TestHurstExponent:
    def test_geometric_brownian_motion_h_near_half(self):
        prices = _gbm_prices(n=2000, seed=0)
        result = hurst_exponent(prices)
        assert isinstance(result, HurstResult)
        # GBM ⇒ H ≈ 0.5 (Chan p.44-45)
        assert 0.4 <= result.h <= 0.6

    def test_mean_reverting_h_below_half(self):
        prices = _ar1_mean_reverting(n=2000, phi=0.6, seed=1)
        result = hurst_exponent(prices)
        assert result.h < 0.5

    def test_trending_h_above_half(self):
        prices = _trending(n=2000, drift=0.001, seed=2)
        result = hurst_exponent(prices)
        assert result.h > 0.5

    def test_r2_high_for_clean_signal(self):
        prices = _gbm_prices(n=2000, seed=0)
        result = hurst_exponent(prices)
        # Structure function on enough data should give R² > 0.85
        assert result.r2 > 0.85

    def test_n_obs_reflects_input(self):
        prices = _gbm_prices(n=500, seed=0)
        result = hurst_exponent(prices)
        assert result.n_obs == 500

    def test_dropna_and_min_obs(self):
        idx = pd.date_range("2020-01-01", periods=50, freq="B")
        prices = pd.Series([float("nan")] * 50, index=idx)
        with pytest.raises(ValueError, match="at least 100"):
            hurst_exponent(prices, min_obs=100)

    def test_negative_prices_rejected(self):
        idx = pd.date_range("2020-01-01", periods=200, freq="B")
        prices = pd.Series(np.linspace(-1, 100, 200), index=idx)
        with pytest.raises(ValueError, match="strictly positive"):
            hurst_exponent(prices)

    def test_non_series_rejected(self):
        with pytest.raises(TypeError, match="pd.Series"):
            hurst_exponent(np.arange(200, dtype=float))  # type: ignore[arg-type]

    def test_bootstrap_returns_ci(self):
        prices = _gbm_prices(n=1000, seed=0)
        result = hurst_exponent(prices, bootstrap=50, random_state=42)
        assert result.ci_low is not None and result.ci_high is not None
        assert result.ci_low <= result.h <= result.ci_high

    def test_bootstrap_zero_skips_ci(self):
        prices = _gbm_prices(n=1000, seed=0)
        result = hurst_exponent(prices, bootstrap=0)
        assert result.ci_low is None and result.ci_high is None

    def test_max_lag_clipped_to_n_minus_one(self):
        prices = _gbm_prices(n=300, seed=0)
        # Asking for a max_lag larger than n should not crash
        result = hurst_exponent(prices, max_lag=10_000)
        assert 0.0 <= result.h <= 1.0

    def test_n_lags_distinct(self):
        prices = _gbm_prices(n=500, seed=0)
        result = hurst_exponent(prices, n_lags=20)
        # n_lags is the *requested* count; the realised count after dedup
        # is reported on the result and must be >= 3
        assert result.n_lags >= 3
