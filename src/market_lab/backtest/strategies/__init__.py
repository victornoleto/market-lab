"""market_lab.backtest.strategies — concrete strategy implementations.

After the 2026-04-24 cleanup consolidated the project into MAINTENANCE
mode (100% Plano C passive; all active hunts FAIL 113/113), only the ABC
+ educational/research modules remain. Historical strategies (Plano A
V2, Plano B LETF rotation, Phase 3.6/3.7/3.8 families, Strategy D BR
ranking, etc.) are recoverable via
``git checkout pre-cleanup-2026-04-24 -- src/market_lab/backtest/strategies/``.

Public surface:

* :class:`Strategy` — Protocol from ``engine.runner`` (re-exported).
* :class:`StrategyBase` — ABC with a rebalance dispatcher; subclasses override
  ``should_rebalance`` + ``on_rebalance`` instead of ``on_bar``.
* :class:`StrategyContext` — typed wrapper over the Runner's per-run context dict.
"""

from market_lab.backtest.strategies.base import (
    Strategy,
    StrategyBase,
    StrategyContext,
)

__all__ = [
    "Strategy",
    "StrategyBase",
    "StrategyContext",
]
