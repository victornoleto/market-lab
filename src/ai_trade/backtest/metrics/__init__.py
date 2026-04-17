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
from ai_trade.backtest.metrics.standard_report import (
    SpyBenchmark,
    SpyComparison,
    StandardReport,
    Trade,
    build_spy_benchmark,
    build_standard_report,
    compare_vs_spy,
    drawdown_periods,
    load_spy_series,
    render_markdown,
    render_trade_log,
)

__all__ = [
    "SpyBenchmark",
    "SpyComparison",
    "StandardReport",
    "Trade",
    "build_spy_benchmark",
    "build_standard_report",
    "cagr",
    "calmar",
    "compare_vs_spy",
    "drawdown_periods",
    "generate_report",
    "load_spy_series",
    "max_drawdown",
    "render_markdown",
    "render_trade_log",
    "returns_from_equity",
    "sharpe",
    "sortino",
    "var",
    "volatility",
]
