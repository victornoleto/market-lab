"""Bar-by-bar event loop that drives a :class:`Strategy` against OHLCV data.

Execution convention (daily bars):

1. At each timestamp, build a :class:`Bar` for every symbol that has data.
2. Mark held positions to today's close (so ``portfolio.equity`` is fresh
   before the strategy reads it).
3. Call ``strategy.on_bar(bars, portfolio, context)`` — the strategy returns
   a list of :class:`Order` objects.
4. Execute each order against its symbol's bar via the :class:`ExecutionSimulator`;
   route buys/sells into ``open_position``/``close_position`` based on the
   current position's side.
5. Re-mark positions to close (removes any spread premium embedded in the
   fresh fill price from the mark).
6. Apply overnight swap (if a :class:`SwapModel` is configured).
7. Record equity.

This is close-to-close MOC execution — the standard backtest simplification
for daily OHLCV. Intraday or next-open-fill variants can replace this logic
later without touching the strategy/portfolio interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from market_lab.backtest.engine.execution import (
    Bar,
    ExecutionSimulator,
    Fill,
    Order,
    SwapModel,
)
from market_lab.backtest.engine.portfolio import Portfolio, Trade


class Strategy(Protocol):
    """Strategies are anything callable as ``on_bar(bars, portfolio, context)``.

    * ``bars`` is a dict of ``{symbol: Bar}`` for symbols present at this ts.
    * ``portfolio`` is mutable — positions are already marked to today's close.
    * ``context`` is a dict the Runner creates once and hands back every bar;
      strategies use it for state that must persist across calls (counters,
      rolling-window caches, rebalance calendars).
    """

    def on_bar(
        self, bars: dict[str, Bar], portfolio: Portfolio, context: dict
    ) -> list[Order]: ...


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: list[Trade]
    fills: list[Fill]
    initial_cash: float
    final_equity: float


def _union_timestamps(data: dict[str, pd.DataFrame]) -> list[pd.Timestamp]:
    """Sorted union of every DataFrame's DatetimeIndex."""
    stamps: set[pd.Timestamp] = set()
    for df in data.values():
        stamps.update(df.index)
    return sorted(stamps)


def _bars_at(ts: pd.Timestamp, data: dict[str, pd.DataFrame]) -> dict[str, Bar]:
    bars: dict[str, Bar] = {}
    for symbol, df in data.items():
        if ts not in df.index:
            continue
        row = df.loc[ts]
        bars[symbol] = Bar(
            symbol=symbol,
            timestamp=ts,
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
        )
    return bars


@dataclass
class Runner:
    executor: ExecutionSimulator
    swap_model: SwapModel | None = None

    def run(
        self,
        strategy: Strategy,
        data: dict[str, pd.DataFrame],
        initial_cash: float,
    ) -> BacktestResult:
        portfolio = Portfolio(initial_cash=initial_cash)
        fills: list[Fill] = []
        context: dict = {}

        for ts in _union_timestamps(data):
            bars = _bars_at(ts, data)
            if not bars:
                continue

            # Freshen marks before handing control to the strategy.
            self._mark_to_close(bars, portfolio)

            orders = strategy.on_bar(bars, portfolio, context)
            for order in orders:
                if order.symbol not in bars:
                    raise ValueError(
                        f"order for {order.symbol} at {ts} but no bar this timestamp"
                    )
                fill = self.executor.simulate_fill(order, bars[order.symbol])
                self._apply_fill(fill, portfolio)
                fills.append(fill)

            # Fills overwrite mark_price with fill_price; re-mark to close so
            # equity reflects today's mid, not the spread-padded entry.
            self._mark_to_close(bars, portfolio)

            if self.swap_model is not None:
                self.swap_model.charge(portfolio, ts)

            portfolio.record_equity(ts)

        return BacktestResult(
            equity_curve=portfolio.equity_curve,
            trades=list(portfolio.closed_trades),
            fills=fills,
            initial_cash=initial_cash,
            final_equity=portfolio.equity,
        )

    @staticmethod
    def _mark_to_close(bars: dict[str, Bar], portfolio: Portfolio) -> None:
        for symbol, bar in bars.items():
            portfolio.update_mark(symbol, bar.close)

    @staticmethod
    def _apply_fill(fill: Fill, portfolio: Portfolio) -> None:
        order = fill.order
        pos = portfolio.positions.get(order.symbol)

        if order.side == "buy":
            if pos is not None and pos.side == "short":
                portfolio.close_position(
                    order.symbol, order.volume, fill.fill_price, fill.fill_time
                )
            else:
                portfolio.open_position(
                    order.symbol, "long", order.volume, fill.fill_price, fill.fill_time
                )
        else:  # sell
            if pos is not None and pos.side == "long":
                portfolio.close_position(
                    order.symbol, order.volume, fill.fill_price, fill.fill_time
                )
            else:
                portfolio.open_position(
                    order.symbol, "short", order.volume, fill.fill_price, fill.fill_time
                )

        if fill.commission != 0.0:
            portfolio.apply_cash_flow(-fill.commission, reason="commission")
