"""Strategy building blocks: Protocol re-export, typed context, rebalance ABC.

The engine's :class:`Runner` only requires a callable with ``on_bar(bars,
portfolio, context) → list[Order]`` — that's the :class:`Strategy` Protocol.
This module adds two conveniences on top:

* :class:`StrategyContext` — a typed dataclass strategies can populate to hold
  the active universe, immutable parameters, and a logger. The Runner itself
  passes a plain ``dict`` to ``on_bar``, so strategies that need typed access
  can stash a StrategyContext under a known key (``context["strategy_ctx"]``)
  or just use the dict directly.

* :class:`StrategyBase` — an ABC for the common case where a strategy does
  nothing on most bars and only acts on rebalance days. Subclasses override
  ``should_rebalance(ts, bars)`` and ``on_rebalance(ts, bars, portfolio,
  context)``. Keeps the no-op path cheap.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd

from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.engine.runner import Strategy

__all__ = ["Strategy", "StrategyBase", "StrategyContext"]


@dataclass
class StrategyContext:
    """Typed container for per-run strategy state.

    Attributes
    ----------
    universe
        Current tradable symbols. Strategies that trade a dynamic universe
        (e.g., point-in-time SPX 500) update this on each rebalance.
    params
        Immutable configuration: thresholds, lookbacks, risk factors. Kept
        separate from :class:`StrategyBase` instance attributes so strategies
        can be cloned with modified params for walk-forward / CPCV.
    logger
        Per-strategy logger. Defaults to ``ai_trade.strategy``.
    """

    universe: set[str] = field(default_factory=set)
    params: dict = field(default_factory=dict)
    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy")
    )


class StrategyBase(ABC):
    """ABC for strategies that only act on rebalance days.

    Subclasses implement :meth:`should_rebalance` (fast, pure) and
    :meth:`on_rebalance` (the actual order logic). ``on_bar`` is a dispatcher:
    no-op when not rebalancing, otherwise delegates to ``on_rebalance``.
    """

    @abstractmethod
    def should_rebalance(
        self, ts: pd.Timestamp, bars: dict[str, Bar]
    ) -> bool:
        """Return True iff ``ts`` is a rebalance day for this strategy."""

    @abstractmethod
    def on_rebalance(
        self,
        ts: pd.Timestamp,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        """Emit orders for this rebalance. Called only when ``should_rebalance``."""

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        if not bars:
            return []
        ts = next(iter(bars.values())).timestamp
        if not self.should_rebalance(ts, bars):
            return []
        return self.on_rebalance(ts, bars, portfolio, context)
