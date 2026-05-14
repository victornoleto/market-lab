"""Reusable MCPT and WF-MCPT scaffolding for success_trading_strat.

This module intentionally contains validation plumbing, not a strategy family.
The workflow follows Masters' MCPT and walk-forward discipline: first measure
the real strategy path, then compare it against permuted paths that preserve the
one-bar change distribution while destroying serial ordering
`[testing_tuning, p.148-150]`, `[testing_tuning, p.318-320]`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from market_lab.backtest.validation.permutation import MCPTResult, permute_prices


StrategyReturnsFn = Callable[[np.ndarray], np.ndarray]
WalkForwardStrategyFn = Callable[[np.ndarray, np.ndarray], np.ndarray]
MetricFn = Callable[[np.ndarray], float]


@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


@dataclass(frozen=True)
class WalkForwardMCPTResult:
    mcpt: MCPTResult
    n_windows: int
    observed_returns: np.ndarray


def annualized_sharpe(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """Return annualized Sharpe with zero risk-free rate.

    Sharpe is used only as a scalar validation metric here; candidate promotion
    still requires DSR/PBO accounting separately `[advances_fin_ml, p.222-223]`.
    """
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 2:
        return 0.0
    std = float(np.std(r, ddof=1))
    if std == 0.0:
        return 0.0
    return float(np.mean(r) / std * np.sqrt(periods_per_year))


def price_returns(prices: np.ndarray) -> np.ndarray:
    """Convert a positive price path to simple returns."""
    p = np.asarray(prices, dtype=float)
    if p.size < 2:
        return np.array([], dtype=float)
    if np.any(p <= 0.0):
        raise ValueError("prices must be strictly positive")
    return p[1:] / p[:-1] - 1.0


def mcpt_on_strategy_returns(
    prices: np.ndarray,
    strategy_returns: StrategyReturnsFn,
    *,
    n_permutations: int,
    seed: int,
    metric: MetricFn = annualized_sharpe,
) -> MCPTResult:
    """Run IS MCPT by re-evaluating a fixed strategy on permuted prices.

    The callable must implement the already pre-registered rule. Optimizing
    inside this callable would contaminate trial accounting and must be counted
    separately `[testing_tuning, p.327-335]`.
    """
    if n_permutations <= 0:
        raise ValueError("n_permutations must be positive")

    prices = _as_positive_prices(prices)
    rng = np.random.default_rng(seed)

    def statistic(path: np.ndarray) -> float:
        return float(metric(strategy_returns(path)))

    observed = statistic(prices)
    stats = np.empty(n_permutations, dtype=float)
    for i in range(n_permutations):
        stats[i] = statistic(permute_prices(prices, rng))
    p_value = float(np.sum(stats >= observed) / n_permutations)
    return MCPTResult(observed, p_value, stats, n_permutations)


def walk_forward_windows(
    n_obs: int,
    *,
    train_size: int,
    test_size: int,
    step_size: int,
) -> list[WalkForwardWindow]:
    """Return rolling train/test windows with no train-test overlap."""
    if min(n_obs, train_size, test_size, step_size) <= 0:
        raise ValueError("n_obs, train_size, test_size and step_size must be positive")
    windows: list[WalkForwardWindow] = []
    train_start = 0
    while True:
        train_end = train_start + train_size
        test_start = train_end
        test_end = test_start + test_size
        if test_end > n_obs:
            break
        windows.append(WalkForwardWindow(train_start, train_end, test_start, test_end))
        train_start += step_size
    if not windows:
        raise ValueError("not enough observations for one walk-forward window")
    return windows


def walk_forward_strategy_returns(
    prices: np.ndarray,
    fit_predict_returns: WalkForwardStrategyFn,
    *,
    train_size: int,
    test_size: int,
    step_size: int,
) -> np.ndarray:
    """Concatenate out-of-sample returns from rolling walk-forward windows."""
    prices = _as_positive_prices(prices)
    out: list[np.ndarray] = []
    for window in walk_forward_windows(
        prices.size,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
    ):
        train_prices = prices[window.train_start:window.train_end]
        test_prices = prices[window.test_start:window.test_end]
        test_returns = np.asarray(fit_predict_returns(train_prices, test_prices), dtype=float)
        if test_returns.ndim != 1:
            raise ValueError("fit_predict_returns must return a 1D return array")
        out.append(test_returns[np.isfinite(test_returns)])
    if not out:
        return np.array([], dtype=float)
    return np.concatenate(out)


def walk_forward_mcpt(
    prices: np.ndarray,
    fit_predict_returns: WalkForwardStrategyFn,
    *,
    train_size: int,
    test_size: int,
    step_size: int,
    n_permutations: int,
    seed: int,
    metric: MetricFn = annualized_sharpe,
) -> WalkForwardMCPTResult:
    """Run WF-MCPT by permuting only data after the first train window.

    The first training window is held fixed so the null distribution attacks the
    walk-forward/OOS sequence rather than rewriting the bootstrap training base
    `[testing_tuning, p.318-320]`.
    """
    if n_permutations <= 0:
        raise ValueError("n_permutations must be positive")

    prices = _as_positive_prices(prices)
    observed_returns = walk_forward_strategy_returns(
        prices,
        fit_predict_returns,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
    )
    observed = float(metric(observed_returns))
    rng = np.random.default_rng(seed)
    stats = np.empty(n_permutations, dtype=float)
    for i in range(n_permutations):
        permuted = permute_after_initial_train(prices, train_size, rng)
        stats[i] = float(metric(walk_forward_strategy_returns(
            permuted,
            fit_predict_returns,
            train_size=train_size,
            test_size=test_size,
            step_size=step_size,
        )))
    p_value = float(np.sum(stats >= observed) / n_permutations)
    mcpt = MCPTResult(observed, p_value, stats, n_permutations)
    n_windows = len(walk_forward_windows(
        prices.size,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
    ))
    return WalkForwardMCPTResult(mcpt, n_windows, observed_returns)


def permute_after_initial_train(
    prices: np.ndarray,
    initial_train_size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Shuffle price changes after the first train window, preserving the prefix."""
    prices = _as_positive_prices(prices)
    if initial_train_size < 2 or initial_train_size >= prices.size - 1:
        raise ValueError("initial_train_size must leave a non-empty permuted tail")
    out = prices.copy()
    tail = prices[initial_train_size - 1:].copy()
    out[initial_train_size - 1:] = permute_prices(tail, rng)
    return out


def _as_positive_prices(prices: np.ndarray) -> np.ndarray:
    arr = np.asarray(prices, dtype=float)
    if arr.ndim != 1:
        raise ValueError("prices must be a 1D array")
    if arr.size < 3:
        raise ValueError("prices must contain at least 3 observations")
    if not np.all(np.isfinite(arr)):
        raise ValueError("prices must be finite")
    if np.any(arr <= 0.0):
        raise ValueError("prices must be strictly positive")
    return arr
