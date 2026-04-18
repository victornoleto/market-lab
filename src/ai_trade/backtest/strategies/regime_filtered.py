"""Regime-filtered strategy wrapper.

Wraps an inner strategy instance and gates its **entry** orders through
an external boolean mask (e.g. SMA-trend, realized-volatility regime).
Exit orders (those returned while a position is open) always pass
through, so stop-loss / time-stop / mean-reversion-target behavior is
preserved regardless of regime.

Used by Phase 3.5a Lead T5 to test regime overlays on the BollingerMR
seed without modifying the seed itself (CLAUDE.md §3.5a: BollingerMR
seed is IMUTÁVEL).

Citations
---------
- Regime-aware features / meta-labeling: ``[advances_fin_ml, ch.17]``.
- SMA trend regime filter: ``[stocks_on_the_move, p.110]``.
- Realized-volatility regime (VIX-proxy): ``[volatility_trading]``.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio


@dataclass
class RegimeFilteredStrategy:
    """Wraps ``inner`` and drops entry orders where ``regime_mask`` is False.

    ``regime_mask`` is a boolean pd.Series indexed by the same bar
    timestamps used by the inner strategy. Lookups are by exact
    timestamp; missing timestamps are treated as False (blocked).

    Only entry orders are gated — orders emitted while a position
    already exists (i.e. exits) always pass through. This preserves
    risk-management behavior of the inner strategy regardless of regime.
    """

    inner: object
    regime_mask: pd.Series

    def __post_init__(self) -> None:
        if not hasattr(self.inner, "on_bar"):
            raise TypeError("inner must expose .on_bar(bars, portfolio, context)")
        if not hasattr(self.inner, "symbol"):
            raise TypeError("inner must expose .symbol (str)")
        if not isinstance(self.regime_mask, pd.Series):
            raise TypeError("regime_mask must be a pd.Series")
        if self.regime_mask.dtype != bool:
            self.regime_mask = self.regime_mask.astype(bool)

    @property
    def symbol(self) -> str:
        return self.inner.symbol

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        orders = self.inner.on_bar(bars, portfolio, context)
        if not orders:
            return orders
        symbol = self.inner.symbol
        if symbol not in bars:
            return orders
        if portfolio.positions.get(symbol) is not None:
            return orders
        ts = bars[symbol].timestamp
        try:
            allow = bool(self.regime_mask.loc[ts])
        except KeyError:
            allow = False
        return orders if allow else []
