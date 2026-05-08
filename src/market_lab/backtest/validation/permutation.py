"""Monte Carlo Permutation Test (MCPT) for trading strategies.

References
----------
* Masters (2018) *Testing and Tuning Market Trading Systems* ch.2-3.
* Masters ``books/code/masters-testing-tuning/MCPT_TRN/MCPT_TRN.CPP`` —
  canonical C reference implementing shuffle-of-changes with endpoints fixed
  (``prepare_permute`` + ``do_permute``).
* Masters ``MCPT_BARS/MCPT_BARS.CPP`` — permutation at the raw-bar level.

Null hypothesis
---------------
The observed strategy performance is indistinguishable from what would be
obtained applying the same rules to a reshuffled series that preserves the
marginal distribution of bar-to-bar changes but destroys serial structure.
A low p-value rejects the null in favor of genuine time-series signal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass
class MCPTResult:
    observed: float
    p_value: float
    permuted_statistics: np.ndarray
    n_permutations: int


def permute_prices(prices: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Return a new price path with shuffled interior changes.

    Replicates Masters' ``prepare_permute`` + ``do_permute`` (MCPT_TRN.CPP
    lines 174-213): the first price is the basis; the ``n-1`` bar-to-bar
    changes are shuffled uniformly at random; the path is rebuilt. First and
    last prices are preserved — the sum of changes is an invariant of the
    permutation.
    """
    prices = np.asarray(prices, dtype=float)
    if prices.size < 3:
        return prices.copy()
    changes = np.diff(prices)
    rng.shuffle(changes)
    out = np.empty_like(prices)
    out[0] = prices[0]
    out[1:] = prices[0] + np.cumsum(changes)
    # Re-pin the last price to erase any floating-point drift from cumsum.
    out[-1] = prices[-1]
    return out


def monte_carlo_permutation_test(
    prices: np.ndarray,
    statistic: Callable[[np.ndarray], float],
    n_permutations: int,
    rng: np.random.Generator | None = None,
) -> MCPTResult:
    """Masters-style MCPT on a price series.

    Parameters
    ----------
    prices
        Baseline price or log-price path.
    statistic
        Callable that takes a price path and returns a scalar performance
        measure (higher is "better"). Examples: total return, Sharpe,
        lag-1 autocorrelation of returns.
    n_permutations
        Number of shuffled realizations to evaluate.
    rng
        ``np.random.Generator`` for reproducibility; defaults to a fresh
        unseeded generator.

    Returns
    -------
    MCPTResult
        ``p_value`` is the proportion of permutations whose statistic meets
        or exceeds the observed statistic. Small values (< 0.05) reject the
        null hypothesis of no serial signal.
    """
    if rng is None:
        rng = np.random.default_rng()
    prices = np.asarray(prices, dtype=float)
    observed = float(statistic(prices))

    stats = np.empty(n_permutations, dtype=float)
    for i in range(n_permutations):
        stats[i] = float(statistic(permute_prices(prices, rng)))

    # Masters counts "how many permutations matched or beat the observed",
    # and divides by n_permutations (the original run is NOT re-counted
    # because it's held out as the reference).
    n_ge = int(np.sum(stats >= observed))
    p_value = n_ge / n_permutations

    return MCPTResult(
        observed=observed,
        p_value=p_value,
        permuted_statistics=stats,
        n_permutations=n_permutations,
    )
