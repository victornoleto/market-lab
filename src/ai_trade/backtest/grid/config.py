"""Clenow momentum parameter grid definition.

The grid varies three Clenow parameters that are defensible per
``[stocks_on_the_move, p.73, p.95, p.88]`` — lookback of the exponential
regression, top-rank cutoff, and the ATR risk budget. Fixed Clenow params
(rebalance weekday, stock/index trend windows, ATR/gap windows) mirror the
book defaults and stay constant across the grid.

Respects ``knowledge/SKILL.md`` Rule #2 (≤ 4 params varied per strategy):
3 dimensions × 5 × 3 × 2 = 30 unique configs.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


LOOKBACK_REGRESSION = (60, 75, 90, 105, 120)
TOP_PCT = (0.10, 0.20, 0.30)
RISK_FACTOR = (0.001, 0.002)


@dataclass(frozen=True)
class ClenowGridConfig:
    """Parameter bundle for one Clenow trial.

    The three grid dimensions are the leading fields (positional); the rest
    are fixed defaults taken from ``[stocks_on_the_move]``.
    """

    lookback_regression: int
    top_pct: float
    risk_factor: float

    rebalance_weekday: int = 2        # Wednesday [p.99]
    lookback_trend: int = 100          # 100d MA filter on individual stocks
    lookback_index_trend: int = 200    # SPX 200d MA regime [p.66-67]
    lookback_atr: int = 20             # ATR20 [p.82]
    lookback_gap: int = 90             # 90-day gap filter
    gap_threshold: float = 0.15        # 15% max gap


def grid_configs() -> list[ClenowGridConfig]:
    """Return the 30 grid configs in cartesian-product iteration order.

    Order is: ``(lookback_regression, top_pct, risk_factor)`` — outer-most
    first. Callers can rely on this being stable across invocations so that
    ``config_id = i`` is a deterministic key for checkpoint/resume.
    """
    return [
        ClenowGridConfig(
            lookback_regression=lb,
            top_pct=tp,
            risk_factor=rf,
        )
        for lb, tp, rf in itertools.product(LOOKBACK_REGRESSION, TOP_PCT, RISK_FACTOR)
    ]
