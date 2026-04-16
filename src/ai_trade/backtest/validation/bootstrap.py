"""Stationary bootstrap for time-series resampling — Politis & Romano (1994).

Used to estimate confidence intervals on Sharpe / CAGR / MaxDD when trade
returns are serially correlated. Cited as the appropriate method for
trade-sequence inference in `[advances_fin_ml, p.196-202, ch.11]`.

Algorithm (Politis & Romano, 1994):
  - For each resample, sample blocks of trades whose lengths follow a
    geometric distribution with mean ``block_mean``. Block restarts happen
    with probability ``p = 1 / block_mean`` at each step. Within a block,
    the next index is the previous index + 1 (mod n) — preserving any
    short-range serial dependence.
  - The full resample matches the original length so realised
    trade-rate statistics carry over to annualisation.
"""
from __future__ import annotations

import numpy as np


def stationary_bootstrap_trades(
    trades: np.ndarray,
    block_mean: int = 5,
    n_resamples: int = 10000,
    seed: int = 42,
) -> np.ndarray:
    """Politis-Romano stationary bootstrap on a 1-D trade sequence.

    Parameters
    ----------
    trades
        1-D array of per-trade metrics (typically PnL or per-trade returns).
    block_mean
        Mean block length L of the geometric distribution; restart
        probability p = 1/L. Lower L → closer to IID; higher L preserves
        more serial structure. Default 5 is the spec default for Sharpe CI
        when autocorrelation is mild (`[advances_fin_ml, p.196-202]`).
    n_resamples
        Number of bootstrap replicates.
    seed
        RNG seed for reproducibility.

    Returns
    -------
    np.ndarray of shape (n_resamples, len(trades)) — each row a resampled
    trade sequence.
    """
    if trades.ndim != 1:
        raise ValueError(f"trades must be 1-D, got shape {trades.shape}")
    if len(trades) == 0:
        raise ValueError("trades must be non-empty")
    if block_mean < 1:
        raise ValueError(f"block_mean must be >= 1, got {block_mean}")
    if n_resamples < 1:
        raise ValueError(f"n_resamples must be >= 1, got {n_resamples}")

    n = len(trades)
    p = 1.0 / block_mean
    rng = np.random.default_rng(seed)

    restarts = rng.random((n_resamples, n)) < p
    restarts[:, 0] = True
    fresh_indices = rng.integers(0, n, size=(n_resamples, n))

    indices = np.empty((n_resamples, n), dtype=np.int64)
    for r in range(n_resamples):
        cur = 0
        for t in range(n):
            if restarts[r, t]:
                cur = int(fresh_indices[r, t])
            else:
                cur = (cur + 1) % n
            indices[r, t] = cur

    return trades[indices]
