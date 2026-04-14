"""ai_trade.backtest.metrics — performance metrics and markdown report generation.

Two pieces:

* :mod:`performance` — pure functions (Sharpe, Sortino, Calmar, CAGR,
  max drawdown, volatility, VaR). Consumed by strategies for reporting and
  by the report module for the Performance table.
* :mod:`report` — consumes a :class:`BacktestResult` plus the outputs of the
  validation framework (CPCV, PBO, DSR, walk-forward) and emits a Markdown
  report with an equity/drawdown PNG chart. Enforces the survivorship
  disclaimer (ROADMAP inviolable rule) when the data source is biased.
"""

from ai_trade.backtest.metrics.performance import (
    cagr,
    calmar,
    max_drawdown,
    returns_from_equity,
    sharpe,
    sortino,
    var,
    volatility,
)
from ai_trade.backtest.metrics.report import generate_report

__all__ = [
    "cagr",
    "calmar",
    "generate_report",
    "max_drawdown",
    "returns_from_equity",
    "sharpe",
    "sortino",
    "var",
    "volatility",
]
