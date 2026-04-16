"""Tests for KalmanPairsStrategy [algo_trading_chan, p.76-80, ch.3]."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.kalman_pairs import KalmanPairsStrategy


def _pair_ohlcv(
    n: int = 2000, beta: float = 2.5, seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Synthesize cointegrated pair y = α + β·x + OU-noise with hl≈20."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = beta * x + eps
    df_y = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_x = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    return df_y, df_x


def test_instantiation_with_both_symbols_succeeds():
    df_y, df_x = _pair_ohlcv()
    strat = KalmanPairsStrategy(
        data={"SPY": df_y, "IWM": df_x},
        long_symbol="SPY",
        short_symbol="IWM",
    )
    assert strat.long_symbol == "SPY"
    assert strat.short_symbol == "IWM"


def test_missing_long_symbol_raises_keyerror():
    df_y, df_x = _pair_ohlcv()
    with pytest.raises(KeyError, match="SPY"):
        KalmanPairsStrategy(
            data={"IWM": df_x}, long_symbol="SPY", short_symbol="IWM",
        )


def test_missing_short_symbol_raises_keyerror():
    df_y, df_x = _pair_ohlcv()
    with pytest.raises(KeyError, match="IWM"):
        KalmanPairsStrategy(
            data={"SPY": df_y}, long_symbol="SPY", short_symbol="IWM",
        )


def test_invalid_delta_raises_valueerror():
    df_y, df_x = _pair_ohlcv()
    with pytest.raises(ValueError, match="delta"):
        KalmanPairsStrategy(
            data={"SPY": df_y, "IWM": df_x},
            long_symbol="SPY", short_symbol="IWM", delta=0.0,
        )


def test_invalid_entry_z_raises_valueerror():
    df_y, df_x = _pair_ohlcv()
    with pytest.raises(ValueError, match="entry_z"):
        KalmanPairsStrategy(
            data={"SPY": df_y, "IWM": df_x},
            long_symbol="SPY", short_symbol="IWM", entry_z=-0.5,
        )


def test_misaligned_indices_raises_valueerror():
    df_y, df_x = _pair_ohlcv(n=2000)
    df_x_short = df_x.iloc[:-10]
    with pytest.raises(ValueError, match="aligned"):
        KalmanPairsStrategy(
            data={"SPY": df_y, "IWM": df_x_short},
            long_symbol="SPY", short_symbol="IWM",
        )


def test_beta_recovers_true_value_within_tolerance():
    """After enough bars, the Kalman β should converge near the true β."""
    true_beta = 2.5
    df_y, df_x = _pair_ohlcv(n=2000, beta=true_beta, seed=7)
    strat = KalmanPairsStrategy(
        data={"SPY": df_y, "IWM": df_x},
        long_symbol="SPY", short_symbol="IWM",
        delta=1e-4, init_train_bars=500,
    )
    beta_series = strat._indicators["beta"].dropna()
    beta_final = beta_series.iloc[-1]
    assert abs(beta_final - true_beta) < 0.15, (
        f"β={beta_final:.3f} too far from true {true_beta}"
    )


def test_zscore_is_standardized():
    """Standardized innovation should have ~unit variance after warmup."""
    df_y, df_x = _pair_ohlcv(n=2500, seed=11)
    strat = KalmanPairsStrategy(
        data={"SPY": df_y, "IWM": df_x},
        long_symbol="SPY", short_symbol="IWM",
        delta=1e-4, init_train_bars=500,
    )
    z = strat._indicators["zscore"].dropna()
    # Post-burn-in sample should have std on order of 1.
    z_post = z.iloc[200:]
    # Broad sanity check — R=1 vs. σ_obs=0.3 keeps z std ~ 0.1–3.0.
    assert 0.05 < z_post.std() < 3.0, f"z std={z_post.std():.2f} off scale"


def test_grid_configs_four_returns_and_unique():
    from ai_trade.backtest.grid import (
        KalmanPairsGridConfig,
        kalman_pairs_grid_configs,
    )
    cfgs = kalman_pairs_grid_configs()
    assert len(cfgs) == 4
    seen = set()
    for c in cfgs:
        assert isinstance(c, KalmanPairsGridConfig)
        key = (c.delta, c.entry_z)
        assert key not in seen
        seen.add(key)
