"""Tests for RegimeFilteredStrategy wrapper (Phase 3.5a Lead T5).

Verifies that:
  1. Entry orders are dropped when regime_mask is False at the bar ts.
  2. Entry orders are passed through when regime_mask is True.
  3. Exit orders (with open position) always pass through.
  4. Missing timestamps in mask are treated as blocked (False).
  5. The .symbol property delegates to the inner strategy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.strategies.regime_filtered import RegimeFilteredStrategy


class _FakeInner:
    """Minimal inner strategy stub that always emits a buy order."""

    def __init__(self, symbol: str = "QQQ"):
        self.symbol = symbol

    def on_bar(self, bars, portfolio, context):
        if self.symbol not in bars:
            return []
        bar = bars[self.symbol]
        return [Order(symbol=self.symbol, side="buy", volume=1.0)]


def _bar(ts: pd.Timestamp, price: float = 100.0) -> Bar:
    return Bar(symbol="QQQ", timestamp=ts, open=price, high=price,
               low=price, close=price, volume=1000.0)


def _portfolio(cash: float = 10_000.0) -> Portfolio:
    return Portfolio(initial_cash=cash)


class TestRegimeFilter:
    def test_entry_blocked_when_mask_false(self):
        ts = pd.Timestamp("2024-01-01 10:00:00")
        mask = pd.Series([False], index=[ts])
        strat = RegimeFilteredStrategy(inner=_FakeInner(), regime_mask=mask)
        out = strat.on_bar({"QQQ": _bar(ts)}, _portfolio(), {})
        assert out == []

    def test_entry_allowed_when_mask_true(self):
        ts = pd.Timestamp("2024-01-01 10:00:00")
        mask = pd.Series([True], index=[ts])
        strat = RegimeFilteredStrategy(inner=_FakeInner(), regime_mask=mask)
        out = strat.on_bar({"QQQ": _bar(ts)}, _portfolio(), {})
        assert len(out) == 1
        assert out[0].side == "buy"

    def test_missing_timestamp_is_blocked(self):
        ts = pd.Timestamp("2024-01-01 10:00:00")
        other = pd.Timestamp("2024-01-02 10:00:00")
        mask = pd.Series([True], index=[other])
        strat = RegimeFilteredStrategy(inner=_FakeInner(), regime_mask=mask)
        out = strat.on_bar({"QQQ": _bar(ts)}, _portfolio(), {})
        assert out == []

    def test_exit_always_passes_through(self):
        """When a position is open, orders are exits and must not be gated."""
        ts = pd.Timestamp("2024-01-01 10:00:00")
        mask = pd.Series([False], index=[ts])
        strat = RegimeFilteredStrategy(inner=_FakeInner(), regime_mask=mask)

        portfolio = _portfolio()
        portfolio.open_position(
            symbol="QQQ", side="long", volume=1.0, price=100.0, timestamp=ts,
        )
        assert portfolio.positions.get("QQQ") is not None

        out = strat.on_bar({"QQQ": _bar(ts)}, portfolio, {})
        # Inner would return a buy, but since pos is open, wrapper passes
        # through (treated as exit context) even with False mask.
        assert len(out) == 1

    def test_symbol_property_delegates(self):
        mask = pd.Series([], dtype=bool)
        strat = RegimeFilteredStrategy(inner=_FakeInner("SPY"), regime_mask=mask)
        assert strat.symbol == "SPY"

    def test_type_errors_on_bad_inner(self):
        mask = pd.Series([], dtype=bool)
        with pytest.raises(TypeError):
            RegimeFilteredStrategy(inner=object(), regime_mask=mask)

    def test_type_error_on_non_series_mask(self):
        with pytest.raises(TypeError):
            RegimeFilteredStrategy(inner=_FakeInner(), regime_mask=[True, False])

    def test_non_bool_mask_is_coerced(self):
        ts = pd.Timestamp("2024-01-01 10:00:00")
        mask = pd.Series([1], index=[ts])  # int, not bool
        strat = RegimeFilteredStrategy(inner=_FakeInner(), regime_mask=mask)
        assert strat.regime_mask.dtype == bool
        out = strat.on_bar({"QQQ": _bar(ts)}, _portfolio(), {})
        assert len(out) == 1
