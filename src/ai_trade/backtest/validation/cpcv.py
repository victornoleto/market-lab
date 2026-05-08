"""Purged K-Fold and Combinatorial Purged Cross-Validation.

References
----------
* AFML ch.7 p.149-154 — Purged K-Fold (with embargo).
* AFML ch.12 p.219-222 — CPCV, number of paths φ[N,k] = C(N,k)·k/N.

Contract for ``times`` argument
-------------------------------
A ``pd.Series`` where the **index** is ``t0`` (label start timestamp) and
**values** are ``t1`` (label end timestamp). For single-horizon labels
(``t0 == t1``), pass ``pd.Series(idx, index=idx)``.

Train observation *i* is kept for a given test set iff its label
``(t0_i, t1_i)`` does not overlap the test range **and** *i* does not fall
inside the positional embargo window that follows the test block. Embargo
size is ``int(embargo_pct · len(times))`` observations per AFML p.151.
"""

from __future__ import annotations

from itertools import combinations
from math import comb
from typing import Iterator

import numpy as np
import pandas as pd


def _purge(
    times: pd.Series,
    train_idx: np.ndarray,
    test_t0_min: pd.Timestamp,
    test_t1_max: pd.Timestamp,
) -> np.ndarray:
    """Keep train obs whose label ``(t0_i, t1_i)`` sits fully before or after the test span."""
    t0 = times.index[train_idx]
    t1 = times.iloc[train_idx].values
    keep = (t1 < test_t0_min) | (t0 > test_t1_max)
    return train_idx[keep]


def _embargo(
    train_idx: np.ndarray, test_last_pos: int, embargo_n: int, n_total: int
) -> np.ndarray:
    """Remove train obs at positions ``(test_last_pos, test_last_pos + embargo_n]``."""
    if embargo_n <= 0:
        return train_idx
    end = min(test_last_pos + embargo_n, n_total - 1)
    keep = (train_idx <= test_last_pos) | (train_idx > end)
    return train_idx[keep]


def purged_kfold_splits(
    times: pd.Series,
    n_splits: int,
    embargo_pct: float = 0.0,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """Yield ``(train_idx, test_idx)`` pairs for purged K-fold CV [AFML p.149-154]."""
    if n_splits < 2:
        raise ValueError(f"n_splits must be >= 2, got {n_splits}")
    n = len(times)
    embargo_n = int(embargo_pct * n)

    indices = np.arange(n)
    groups = np.array_split(indices, n_splits)

    for test_idx in groups:
        test_first = int(test_idx[0])
        test_last = int(test_idx[-1])
        test_t0_min = times.index[test_first]
        test_t1_max = times.iloc[test_first : test_last + 1].max()

        train = np.setdiff1d(indices, test_idx, assume_unique=True)
        train = _purge(times, train, test_t0_min, test_t1_max)
        train = _embargo(train, test_last, embargo_n, n)
        yield train, test_idx


def cpcv_path_count(n_groups: int, n_test_groups: int) -> int:
    """Number of distinct CPCV backtest paths ``φ[N,k] = C(N,k) · k / N`` [AFML p.219-220]."""
    if not 1 <= n_test_groups < n_groups:
        raise ValueError(
            f"need 1 <= n_test_groups < n_groups, got n_test_groups={n_test_groups}, "
            f"n_groups={n_groups}"
        )
    return comb(n_groups, n_test_groups) * n_test_groups // n_groups


def cpcv_splits(
    times: pd.Series,
    n_groups: int,
    n_test_groups: int,
    embargo_pct: float = 0.0,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """Yield ``(train_idx, test_idx)`` for every combination of ``k`` test groups [AFML p.219-222].

    Purge and embargo are applied **per test block** inside the combination, so
    a combination like ``(group 0, group 5)`` purges train observations that
    overlap *either* block and embargoes train positions that follow *either*
    block's last observation.
    """
    if not 1 <= n_test_groups < n_groups:
        raise ValueError(
            f"need 1 <= n_test_groups < n_groups, got n_test_groups={n_test_groups}, "
            f"n_groups={n_groups}"
        )
    n = len(times)
    embargo_n = int(embargo_pct * n)

    indices = np.arange(n)
    groups = np.array_split(indices, n_groups)

    for combo in combinations(range(n_groups), n_test_groups):
        test_idx = np.sort(np.concatenate([groups[g] for g in combo]))
        train = np.setdiff1d(indices, test_idx, assume_unique=True)

        for g in combo:
            block = groups[g]
            block_first = int(block[0])
            block_last = int(block[-1])
            block_t0_min = times.index[block_first]
            block_t1_max = times.iloc[block_first : block_last + 1].max()
            train = _purge(times, train, block_t0_min, block_t1_max)
            train = _embargo(train, block_last, embargo_n, n)

        yield train, test_idx
