"""Portfolio accounting: positions, cash flow, realized/unrealized P&L, equity curve.

Accounting model (single base currency, USD for now):

* ``cash`` reflects every settled flow: entry debits, exit credits, commissions,
  swaps, deposits/withdrawals.
* ``realized_pnl`` tracks closed-trade P&L as a standalone accumulator — it is
  **not** added to ``cash`` (cash already includes it via the exit credit).
  Keeping it separate is useful for reports and sanity checks.
* ``equity = cash + Σ unrealized_pnl``. At flat state, equity == cash.

Multi-currency CFD accounting (per-symbol quote currency, funding charges in
the home currency) is deferred until the cTrader adapter arrives (ROADMAP
§"Backtest em duas etapas"). The engine interface doesn't change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd

Side = Literal["long", "short"]


@dataclass
class Position:
    """An open position in a single symbol.

    ``avg_entry_price`` is volume-weighted across same-side opens.
    ``mark_price`` is the most recent price the Runner has fed back — it drives
    ``unrealized_pnl``. Defaults to ``avg_entry_price`` right after opening.
    """

    symbol: str
    side: Side
    volume: float
    avg_entry_price: float
    mark_price: float

    @property
    def unrealized_pnl(self) -> float:
        sign = 1.0 if self.side == "long" else -1.0
        return sign * self.volume * (self.mark_price - self.avg_entry_price)


@dataclass
class Trade:
    """A round-trip: one open, one (partial or full) close.

    Emitted by :meth:`Portfolio.close_position`; the Runner collects these into
    :class:`BacktestResult` for reporting.
    """

    symbol: str
    side: Side
    volume: float
    entry_price: float
    exit_price: float
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    pnl: float


@dataclass
class Portfolio:
    initial_cash: float
    cash: float = field(init=False)
    positions: dict[str, Position] = field(init=False, default_factory=dict)
    realized_pnl: float = field(init=False, default=0.0)
    closed_trades: list[Trade] = field(init=False, default_factory=list)
    _equity_points: dict[pd.Timestamp, float] = field(init=False, default_factory=dict)
    _entry_times: dict[str, pd.Timestamp] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self.cash = self.initial_cash

    # -- positions ---------------------------------------------------------

    def open_position(
        self,
        symbol: str,
        side: Side,
        volume: float,
        price: float,
        timestamp: pd.Timestamp,
    ) -> None:
        """Open or add to a position. Raises if an opposite-side position is live."""
        if volume <= 0:
            raise ValueError(f"volume must be > 0, got {volume}")

        existing = self.positions.get(symbol)
        if existing is not None and existing.side != side:
            raise ValueError(
                f"cannot open {side} on {symbol}: opposite side position still open"
            )

        notional = volume * price
        # Long buys debit cash; short sells credit cash (proceeds).
        self.cash += -notional if side == "long" else notional

        if existing is None:
            self.positions[symbol] = Position(
                symbol=symbol,
                side=side,
                volume=volume,
                avg_entry_price=price,
                mark_price=price,
            )
            self._entry_times[symbol] = timestamp
        else:
            new_vol = existing.volume + volume
            existing.avg_entry_price = (
                existing.avg_entry_price * existing.volume + price * volume
            ) / new_vol
            existing.volume = new_vol
            existing.mark_price = price  # most recent trade is the freshest mark

    def close_position(
        self,
        symbol: str,
        volume: float,
        price: float,
        timestamp: pd.Timestamp,
    ) -> Trade:
        """Close (fully or partially) an open position; return the resulting :class:`Trade`."""
        if volume <= 0:
            raise ValueError(f"volume must be > 0, got {volume}")
        pos = self.positions.get(symbol)
        if pos is None:
            raise ValueError(f"no open position on {symbol}")
        if volume > pos.volume:
            raise ValueError(
                f"close volume {volume} exceeds open volume {pos.volume} on {symbol}"
            )

        sign = 1.0 if pos.side == "long" else -1.0
        pnl = sign * volume * (price - pos.avg_entry_price)
        notional = volume * price
        # Closing a long credits cash; closing a short debits cash.
        self.cash += notional if pos.side == "long" else -notional
        self.realized_pnl += pnl

        trade = Trade(
            symbol=symbol,
            side=pos.side,
            volume=volume,
            entry_price=pos.avg_entry_price,
            exit_price=price,
            entry_time=self._entry_times[symbol],
            exit_time=timestamp,
            pnl=pnl,
        )
        self.closed_trades.append(trade)

        if volume == pos.volume:
            del self.positions[symbol]
            del self._entry_times[symbol]
        else:
            pos.volume -= volume  # avg_entry_price unchanged (FIFO against avg)
            pos.mark_price = price

        return trade

    def update_mark(self, symbol: str, price: float) -> None:
        """Update the last known price for a held symbol (drives unrealized P&L)."""
        pos = self.positions.get(symbol)
        if pos is None:
            return  # ignore marks for symbols we don't hold — Runner is spammy
        pos.mark_price = price

    # -- cash / equity -----------------------------------------------------

    def apply_cash_flow(self, amount: float, reason: str) -> None:
        """Adjust ``cash`` by ``amount`` (sign-carrying). Reasons: commission, swap, deposit."""
        del reason  # reserved for future logging/audit; not used in accounting
        self.cash += amount

    @property
    def equity(self) -> float:
        """Net worth: cash plus the signed market value of every open position.

        For a long, position value = ``+volume × mark``; for a short,
        ``-volume × mark`` (a short is a liability to cover). Equivalently,
        ``equity == initial_cash + realized_pnl + Σ unrealized_pnl`` minus any
        commissions/swaps — but phrased here directly against cash because
        ``cash`` already absorbs those.
        """
        return self.cash + sum(
            (p.volume if p.side == "long" else -p.volume) * p.mark_price
            for p in self.positions.values()
        )

    def record_equity(self, timestamp: pd.Timestamp) -> None:
        """Snapshot current equity at ``timestamp``; later fetched via ``equity_curve``."""
        self._equity_points[timestamp] = self.equity

    @property
    def equity_curve(self) -> pd.Series:
        """Equity history as a ``pd.Series`` indexed by timestamp."""
        if not self._equity_points:
            return pd.Series(dtype=float, name="equity")
        items = sorted(self._equity_points.items())
        idx = pd.DatetimeIndex([ts for ts, _ in items], name="date")
        return pd.Series([v for _, v in items], index=idx, name="equity")
