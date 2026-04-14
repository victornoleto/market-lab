"""Probability of Backtest Overfitting via CSCV.

References
----------
* AFML ch.11 p.208-211 — CSCV algorithm and PBO definition.
* Masters ``books/code/masters-testing-tuning/CSCV_MKT/CSCV_CORE.CPP`` — the
  canonical C reference used as cross-check for the Python translation.

Gate
----
``pbo >= 0.5`` → **reject** the strategy family: the IS-best is as likely to
underperform OOS as to outperform, i.e. we are selecting lucky noise.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np


@dataclass
class PBOResult:
    pbo: float
    logits: np.ndarray
    n_blocks: int
    n_combinations: int


def _sharpe_columns(matrix: np.ndarray) -> np.ndarray:
    """Per-column Sharpe (mean/std, ddof=0). Columns with σ ≈ 0 get score 0."""
    mu = matrix.mean(axis=0)
    sigma = matrix.std(axis=0, ddof=0)
    out = np.zeros_like(mu)
    mask = sigma > 1e-12
    out[mask] = mu[mask] / sigma[mask]
    return out


def pbo(returns: np.ndarray, n_blocks: int = 10) -> PBOResult:
    """Probability of Backtest Overfitting via CSCV [AFML p.208-211].

    Parameters
    ----------
    returns
        ``(T, N)`` matrix — rows are time periods, columns are strategy
        configurations. Each column's Sharpe-in-sample vs Sharpe-out-of-sample
        relationship is what CSCV probes.
    n_blocks
        Number of contiguous blocks to partition the rows into. Must be even;
        odd values are rounded **down** per Masters' convention (line 40 of
        ``CSCV_CORE.CPP``).

    Notes
    -----
    For every balanced IS/OOS split (``C(S, S/2)`` of them), we find the
    strategy that ranks best under the IS Sharpe, then compute its OOS
    relative rank ``(number of OOS Sharpes ≤ this one) / (N + 1)``. The
    relative rank is mapped to a logit for interpretation, and PBO is the
    fraction of splits where the relative rank falls at or below the OOS
    median (``rel_rank ≤ 0.5``) — i.e. IS-best lost half or more of its OOS
    peers.
    """
    returns = np.asarray(returns, dtype=float)
    if returns.ndim != 2:
        raise ValueError(f"returns must be 2D (T, N), got shape {returns.shape}")
    T, N = returns.shape
    if N < 2:
        raise ValueError("PBO requires at least 2 strategies (N >= 2)")
    n_blocks = n_blocks - (n_blocks % 2)
    if n_blocks < 2:
        raise ValueError("n_blocks must round down to an even integer >= 2")

    blocks = np.array_split(np.arange(T), n_blocks)
    half = n_blocks // 2

    logits: list[float] = []
    n_below = 0
    n_total = 0
    eps = 1e-10

    for is_combo in combinations(range(n_blocks), half):
        is_set = set(is_combo)
        is_rows = np.concatenate([blocks[b] for b in range(n_blocks) if b in is_set])
        oos_rows = np.concatenate([blocks[b] for b in range(n_blocks) if b not in is_set])

        is_crits = _sharpe_columns(returns[is_rows])
        oos_crits = _sharpe_columns(returns[oos_rows])

        ibest = int(np.argmax(is_crits))
        best_oos = oos_crits[ibest]
        # Count includes IS-best itself (Masters insurance clause, line 114).
        n_leq = int(np.sum(oos_crits <= best_oos))
        rel_rank = n_leq / (N + 1)

        rr = min(max(rel_rank, eps), 1 - eps)
        logits.append(float(np.log(rr / (1 - rr))))

        if rel_rank <= 0.5:
            n_below += 1
        n_total += 1

    return PBOResult(
        pbo=n_below / n_total,
        logits=np.array(logits),
        n_blocks=n_blocks,
        n_combinations=n_total,
    )


def pbo_gate(pbo_value: float, threshold: float = 0.5) -> str:
    """Binary gate: ``pass`` if ``pbo_value < threshold``, else ``reject``.

    Default threshold 0.5 comes from AFML p.208-211. Equality is treated as
    rejection because a coin toss of correctness is not a useful gate.
    """
    return "reject" if pbo_value >= threshold else "pass"
