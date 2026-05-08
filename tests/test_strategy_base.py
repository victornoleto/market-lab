"""Tests for the strategy base module (Strategy Protocol re-export + rebalance ABC).

Shape of the vocabulary:

* ``Strategy`` — Protocol already in ``engine.runner``; re-exported here for
  discoverability alongside strategy implementations.
* ``StrategyContext`` — typed wrapper over the Runner's per-backtest ``dict``
  context, carrying universe / params / logger.
* ``StrategyBase`` — ABC that turns ``on_bar`` into a "rebalance or hold"
  dispatcher. Subclasses override ``should_rebalance`` + ``on_rebalance``.
"""

from __future__ import annotations

import logging

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# StrategyContext
# ---------------------------------------------------------------------------


class TestStrategyContext:
    def test_defaults_are_empty(self):
        from market_lab.backtest.strategies.base import StrategyContext

        ctx = StrategyContext()
        assert ctx.universe == set()
        assert ctx.params == {}
        assert isinstance(ctx.logger, logging.Logger)

    def test_accepts_universe_and_params(self):
        from market_lab.backtest.strategies.base import StrategyContext

        ctx = StrategyContext(
            universe={"AAPL", "MSFT"},
            params={"risk_factor": 0.001, "top_pct": 0.20},
        )
        assert ctx.universe == {"AAPL", "MSFT"}
        assert ctx.params["risk_factor"] == 0.001

    def test_universe_is_mutable_on_instance(self):
        from market_lab.backtest.strategies.base import StrategyContext

        ctx = StrategyContext()
        ctx.universe.add("NVDA")
        assert ctx.universe == {"NVDA"}


# ---------------------------------------------------------------------------
# Strategy Protocol re-export
# ---------------------------------------------------------------------------


class TestStrategyReexport:
    def test_base_module_exposes_strategy_protocol(self):
        from market_lab.backtest.engine.runner import Strategy as RunnerStrategy
        from market_lab.backtest.strategies.base import Strategy

        # Same object — re-export, not reimplementation.
        assert Strategy is RunnerStrategy


# ---------------------------------------------------------------------------
# StrategyBase (rebalance-oriented ABC)
# ---------------------------------------------------------------------------


class _SpyStrategy:
    """Fixture strategy subclass: records rebalance calls, returns canned orders."""

    def __init__(self, rebalance_days: set[pd.Timestamp], canned_orders=None):
        self.rebalance_days = rebalance_days
        self.canned_orders = canned_orders or []
        self.rebalance_calls: list[pd.Timestamp] = []

    def should_rebalance(self, ts, bars):
        return ts in self.rebalance_days

    def on_rebalance(self, ts, bars, portfolio, context):
        self.rebalance_calls.append(ts)
        return list(self.canned_orders)


def _make_bar(symbol: str, ts: pd.Timestamp, close: float = 100.0):
    from market_lab.backtest.engine.execution import Bar

    return Bar(
        symbol=symbol,
        timestamp=ts,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1_000_000,
    )


class TestStrategyBase:
    def test_on_bar_returns_empty_when_not_rebalance(self):
        from market_lab.backtest.engine.portfolio import Portfolio
        from market_lab.backtest.strategies.base import StrategyBase

        t_hold = pd.Timestamp("2024-01-02")  # not in rebalance_days
        t_rebalance = pd.Timestamp("2024-01-03")

        class Spy(_SpyStrategy, StrategyBase):
            pass

        strat = Spy(rebalance_days={t_rebalance})
        bars = {"AAPL": _make_bar("AAPL", t_hold)}
        orders = strat.on_bar(bars, Portfolio(initial_cash=10_000.0), {})

        assert orders == []
        assert strat.rebalance_calls == []

    def test_on_bar_dispatches_to_on_rebalance_when_flagged(self):
        from market_lab.backtest.engine.execution import Order
        from market_lab.backtest.engine.portfolio import Portfolio
        from market_lab.backtest.strategies.base import StrategyBase

        t_rebalance = pd.Timestamp("2024-01-03")

        class Spy(_SpyStrategy, StrategyBase):
            pass

        canned = [Order("AAPL", side="buy", volume=5)]
        strat = Spy(rebalance_days={t_rebalance}, canned_orders=canned)
        bars = {"AAPL": _make_bar("AAPL", t_rebalance)}
        orders = strat.on_bar(bars, Portfolio(initial_cash=10_000.0), {})

        assert orders == canned
        assert strat.rebalance_calls == [t_rebalance]

    def test_on_bar_empty_bars_returns_empty_without_calling_rebalance(self):
        from market_lab.backtest.engine.portfolio import Portfolio
        from market_lab.backtest.strategies.base import StrategyBase

        class Spy(_SpyStrategy, StrategyBase):
            pass

        strat = Spy(rebalance_days=set())  # never rebalance anyway
        orders = strat.on_bar({}, Portfolio(initial_cash=10_000.0), {})
        assert orders == []

    def test_subclass_must_implement_abstract_methods(self):
        from market_lab.backtest.strategies.base import StrategyBase

        with pytest.raises(TypeError, match="abstract"):
            StrategyBase()  # type: ignore[abstract]
