"""Tests for ``market_lab.backtest.validation.bootstrap``.

Stationary bootstrap (Politis & Romano, 1994) on trade sequences.
Cited in [advances_fin_ml, p.196-202, ch.11] for Sharpe-CI estimation
when trade returns are serially correlated.
"""
from __future__ import annotations

import numpy as np
import pytest


def test_output_shape_matches_n_resamples_x_n_trades():
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    rng = np.random.default_rng(0)
    trades = rng.normal(0, 1, 100)
    out = stationary_bootstrap_trades(trades, n_resamples=50, seed=42)
    assert out.shape == (50, 100)


def test_reproducible_with_same_seed():
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    trades = np.arange(20, dtype=float)
    a = stationary_bootstrap_trades(trades, n_resamples=10, seed=42)
    b = stationary_bootstrap_trades(trades, n_resamples=10, seed=42)
    np.testing.assert_array_equal(a, b)


def test_different_seeds_produce_different_resamples():
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    trades = np.arange(50, dtype=float)
    a = stationary_bootstrap_trades(trades, n_resamples=10, seed=1)
    b = stationary_bootstrap_trades(trades, n_resamples=10, seed=2)
    assert not np.array_equal(a, b)


def test_resamples_use_only_original_values():
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    trades = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    out = stationary_bootstrap_trades(trades, n_resamples=100, seed=42)
    assert np.all(np.isin(out.flatten(), trades))


def test_block_mean_1_breaks_serial_adjacency():
    """block_mean=1 ⇒ p=1.0 ⇒ every step is a fresh random index (IID)."""
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    trades = np.arange(100, dtype=float)
    out = stationary_bootstrap_trades(trades, block_mean=1, n_resamples=200, seed=42)
    # Probability of "next index == current+1" under IID ≈ 1/n = 0.01.
    consecutive_adj = ((out[:, 1:] - out[:, :-1]) == 1).mean()
    assert consecutive_adj < 0.05, (
        f"IID resampling should rarely hit adjacent indices; got rate {consecutive_adj}"
    )


def test_large_block_mean_preserves_serial_adjacency():
    """block_mean ≫ n ⇒ very few restarts ⇒ blocks are long ⇒ adjacency preserved."""
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    trades = np.arange(20, dtype=float)
    out = stationary_bootstrap_trades(trades, block_mean=100, n_resamples=200, seed=42)
    # p = 0.01 ⇒ ~1 restart in 20 steps on average ⇒ most pairs preserve +1 adjacency.
    consecutive_adj = ((out[:, 1:] - out[:, :-1]) == 1).mean()
    assert consecutive_adj > 0.80, (
        f"Long blocks should preserve adjacency; got rate {consecutive_adj}"
    )


def test_bootstrap_mean_is_unbiased_for_population_mean():
    """Mean of bootstrap-sample means converges to original mean."""
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    rng = np.random.default_rng(0)
    trades = rng.normal(loc=2.0, scale=1.0, size=200)
    out = stationary_bootstrap_trades(trades, n_resamples=2000, seed=42)
    bootstrap_means = out.mean(axis=1)
    se = trades.std() / np.sqrt(len(trades))
    assert abs(bootstrap_means.mean() - trades.mean()) < 3 * se


def test_rejects_empty_trades():
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    with pytest.raises(ValueError, match="non-empty"):
        stationary_bootstrap_trades(np.array([], dtype=float))


def test_rejects_non_1d_trades():
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    with pytest.raises(ValueError, match="1-D"):
        stationary_bootstrap_trades(np.zeros((5, 5)))


def test_rejects_invalid_block_mean():
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    with pytest.raises(ValueError, match="block_mean"):
        stationary_bootstrap_trades(np.arange(10.0), block_mean=0)


def test_rejects_invalid_n_resamples():
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    with pytest.raises(ValueError, match="n_resamples"):
        stationary_bootstrap_trades(np.arange(10.0), n_resamples=0)


def test_handles_single_trade():
    """n=1 input: every resample is [trade] × 1 = the single value."""
    from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

    trades = np.array([42.0])
    out = stationary_bootstrap_trades(trades, n_resamples=5, seed=42)
    assert out.shape == (5, 1)
    assert np.all(out == 42.0)
