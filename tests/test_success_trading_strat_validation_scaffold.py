from __future__ import annotations

import numpy as np

from studies.success_trading_strat.scripts.validation_scaffold import (
    annualized_sharpe,
    mcpt_on_strategy_returns,
    permute_after_initial_train,
    price_returns,
    walk_forward_mcpt,
    walk_forward_strategy_returns,
    walk_forward_windows,
)


def _buy_hold_returns(prices: np.ndarray) -> np.ndarray:
    return price_returns(prices)


def _wf_buy_hold_returns(train_prices: np.ndarray, test_prices: np.ndarray) -> np.ndarray:
    del train_prices
    return price_returns(test_prices)


def test_walk_forward_windows_do_not_overlap() -> None:
    windows = walk_forward_windows(100, train_size=40, test_size=10, step_size=10)

    assert len(windows) == 6
    assert all(w.train_end == w.test_start for w in windows)
    assert windows[-1].test_end == 100


def test_permute_after_initial_train_preserves_prefix_and_endpoint() -> None:
    steps = np.linspace(0.2, 1.8, 49)
    prices = np.concatenate([[100.0], 100.0 + np.cumsum(steps)])
    rng = np.random.default_rng(7)

    permuted = permute_after_initial_train(prices, 20, rng)

    np.testing.assert_allclose(permuted[:20], prices[:20])
    assert permuted[-1] == prices[-1]
    assert not np.allclose(permuted[20:-1], prices[20:-1])


def test_mcpt_on_strategy_returns_is_deterministic_with_seed() -> None:
    rng = np.random.default_rng(1)
    prices = 100.0 * np.cumprod(1.0 + rng.normal(0.0005, 0.01, 300))

    a = mcpt_on_strategy_returns(
        prices,
        _buy_hold_returns,
        n_permutations=25,
        seed=11,
    )
    b = mcpt_on_strategy_returns(
        prices,
        _buy_hold_returns,
        n_permutations=25,
        seed=11,
    )

    assert 0.0 <= a.p_value <= 1.0
    assert a.observed == b.observed
    np.testing.assert_allclose(a.permuted_statistics, b.permuted_statistics)


def test_walk_forward_strategy_returns_concatenates_oos_only() -> None:
    prices = np.linspace(100.0, 200.0, 101)

    returns = walk_forward_strategy_returns(
        prices,
        _wf_buy_hold_returns,
        train_size=40,
        test_size=11,
        step_size=10,
    )

    assert returns.ndim == 1
    assert returns.size == 60


def test_walk_forward_mcpt_returns_window_count_and_unit_p_value() -> None:
    rng = np.random.default_rng(2)
    prices = 100.0 * np.cumprod(1.0 + rng.normal(0.0003, 0.01, 260))

    result = walk_forward_mcpt(
        prices,
        _wf_buy_hold_returns,
        train_size=80,
        test_size=30,
        step_size=30,
        n_permutations=20,
        seed=13,
    )

    assert result.n_windows == 6
    assert result.observed_returns.size == 174
    assert 0.0 <= result.mcpt.p_value <= 1.0
    assert np.isfinite(annualized_sharpe(result.observed_returns))
