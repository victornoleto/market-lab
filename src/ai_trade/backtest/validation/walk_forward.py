"""Walk-forward validation: rolling in-sample / out-of-sample splits.

References
----------
* Pardo (2008) *The Evaluation and Optimization of Trading Strategies* ch.10-11.
* Kaufman (2020) *Trading Systems and Methods* ch.21 — Testing.
* Masters (2018) *Testing and Tuning Market Trading Systems* ch.2-4.

Gate (ai-trade inviolable rule #5)
---------------------------------
A strategy passes the walk-forward gate when:

1. ``n_windows ≥ 8`` — enough OOS windows for robust evaluation.
2. ``n_profitable_windows ≥ 6 / 8`` — consistent performance across regimes
   (scales proportionally: ≥ 75% of ``n_windows`` must be profitable).
3. ``max_drawdown ≤ 25%`` in every window.
"""

from __future__ import annotations

from typing import Iterator, Sequence


def walk_forward_splits(
    n_obs: int,
    is_size: int,
    oos_size: int,
    step: int,
) -> Iterator[tuple[range, range]]:
    """Yield ``(train_range, test_range)`` for each sliding window.

    Parameters
    ----------
    n_obs
        Total observations in the backtest period.
    is_size
        In-sample window size (training).
    oos_size
        Out-of-sample window size (evaluation).
    step
        Stride between successive windows.

    Each train range is ``[start, start + is_size)`` and the immediately
    following test range is ``[start + is_size, start + is_size + oos_size)``.
    Windows advance by ``step`` until the test range would exceed ``n_obs``.
    """
    if step <= 0:
        raise ValueError(f"step must be positive, got {step}")
    if is_size <= 0 or oos_size <= 0:
        raise ValueError("is_size and oos_size must be positive")
    if n_obs < is_size + oos_size:
        raise ValueError(
            f"n_obs={n_obs} is less than at least one window's is+oos = "
            f"{is_size + oos_size}"
        )

    start = 0
    while start + is_size + oos_size <= n_obs:
        train = range(start, start + is_size)
        test = range(start + is_size, start + is_size + oos_size)
        yield train, test
        start += step


def walk_forward_gate(
    oos_returns_per_window: Sequence[float],
    drawdowns_per_window: Sequence[float],
    *,
    min_windows: int = 8,
    min_profitable_ratio: float = 6 / 8,
    max_drawdown: float = 0.25,
) -> str:
    """Gate verdict from rule #5 above.

    ``oos_returns_per_window[i]`` is the total OOS return in window *i*;
    ``drawdowns_per_window[i]`` is the max OOS drawdown (positive magnitude)
    in that window. Returns ``"pass"`` or ``"reject"``.
    """
    n = len(oos_returns_per_window)
    if n != len(drawdowns_per_window):
        raise ValueError("returns and drawdowns must have the same length")
    if n < min_windows:
        return "reject"
    if any(dd > max_drawdown for dd in drawdowns_per_window):
        return "reject"
    n_profitable = sum(1 for r in oos_returns_per_window if r > 0)
    if n_profitable < min_profitable_ratio * n:
        return "reject"
    return "pass"
