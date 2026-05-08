"""ai_trade.backtest.engine — portfolio accounting, execution, bar runner.

Public API is kept small on purpose: strategies depend on the :class:`Portfolio`
and the :class:`Runner`, not on implementation details of fills or swap
accounting. The ``Bar``/``Order``/``Fill``/``Trade`` dataclasses form the
vocabulary used between the components.
"""

from ai_trade.backtest.engine.execution import (
    Bar,
    ExecutionConfig,
    ExecutionSimulator,
    Fill,
    Order,
    SwapModel,
)
from ai_trade.backtest.engine.portfolio import Portfolio, Position, Trade
from ai_trade.backtest.engine.runner import BacktestResult, Runner, Strategy

__all__ = [
    "Bar",
    "BacktestResult",
    "ExecutionConfig",
    "ExecutionSimulator",
    "Fill",
    "Order",
    "Portfolio",
    "Position",
    "Runner",
    "Strategy",
    "SwapModel",
    "Trade",
]
