"""ai_trade.backtest.strategies — concrete strategy implementations.

Public surface:

* :class:`Strategy` — Protocol from ``engine.runner`` (re-exported).
* :class:`StrategyBase` — ABC with a rebalance dispatcher; subclasses override
  ``should_rebalance`` + ``on_rebalance`` instead of ``on_bar``.
* :class:`StrategyContext` — typed wrapper over the Runner's per-run context dict.
* :class:`ClenowMomentumStrategy` — replication of Clenow's
  ``stocks_on_the_move`` (citations inline in the class docstring).
"""

from ai_trade.backtest.strategies.base import (
    Strategy,
    StrategyBase,
    StrategyContext,
)
from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy
from ai_trade.backtest.strategies.chan_bollinger_pairs import ChanBollingerPairsStrategy
from ai_trade.backtest.strategies.clenow_momentum import ClenowMomentumStrategy
from ai_trade.backtest.strategies.vol_expansion_breakout import (
    RegimeReading,
    VolExpansionBreakoutStrategy,
    YangZhangCone,
)

__all__ = [
    "BollingerMRStrategy",
    "ChanBollingerPairsStrategy",
    "ClenowMomentumStrategy",
    "RegimeReading",
    "Strategy",
    "StrategyBase",
    "StrategyContext",
    "VolExpansionBreakoutStrategy",
    "YangZhangCone",
]
