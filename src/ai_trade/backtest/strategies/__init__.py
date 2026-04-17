"""ai_trade.backtest.strategies — concrete strategy implementations.

After the 2026-04-16 post-winners cleanup only the 2 production winners
remain here. Discarded strategies (Clenow / Ehlers / Kalman / Chan /
VolExpansion / OUMeanRev) were removed; the F3.D portfolio module that
combined them is gone too. Pure helper functions previously in
``clenow_momentum`` (``adjusted_slope``, ``atr``, ``max_gap``) live in
``ai_trade.backtest.helpers.momentum``.

Public surface:

* :class:`Strategy` — Protocol from ``engine.runner`` (re-exported).
* :class:`StrategyBase` — ABC with a rebalance dispatcher; subclasses override
  ``should_rebalance`` + ``on_rebalance`` instead of ``on_bar``.
* :class:`StrategyContext` — typed wrapper over the Runner's per-run context dict.
* :class:`BollingerMRStrategy` — Path A winner (short-hold CFD, SPY 1h).
* :class:`ETFRotationStrategy` — Path B winner (swing broker, monthly).
"""

from ai_trade.backtest.strategies.base import (
    Strategy,
    StrategyBase,
    StrategyContext,
)
from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy
from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy

__all__ = [
    "BollingerMRStrategy",
    "ETFRotationStrategy",
    "Strategy",
    "StrategyBase",
    "StrategyContext",
]
