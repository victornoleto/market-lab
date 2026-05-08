"""Execution simulator: converts :class:`Order` + :class:`Bar` into :class:`Fill`.

Design (intentionally CFD-agnostic at the price-unit level):

* ``half_spread`` and ``slippage`` are in **absolute price units**, not pips —
  the caller is responsible for any pip/bps → price conversion. This keeps
  the simulator equity-friendly and forex-friendly without a symbol-aware
  conversion layer. A 2-pip EURUSD spread becomes ``half_spread=0.0001``;
  a 1¢ AAPL spread is just ``half_spread=0.005``.
* Mid is taken as ``bar.close`` (close-to-close fills for daily data; the
  Runner can swap bars per-timestamp if it wants next-open execution).
* Fill price on buy = ``close + half_spread + slippage``; on sell it subtracts.
* ``commission_per_unit`` is $ per share/lot (multiplied by ``order.volume``).
* Swap accounting is a separate concern — see :class:`SwapModel`.

Etapa 2 (cTrader calibration) will wrap this with per-symbol ``ExecutionConfig``
derived from measured spreads on the Pepperstone demo account — no shape
change to this interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

OrderSide = Literal["buy", "sell"]


@dataclass
class Bar:
    """Single-bar OHLCV snapshot for one symbol at one timestamp."""

    symbol: str
    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Order:
    """Market order. Extensible later to limit/stop by adding ``kind`` variants."""

    symbol: str
    side: OrderSide
    volume: float
    kind: Literal["market"] = "market"


@dataclass
class Fill:
    """Outcome of an executed :class:`Order` against a :class:`Bar`."""

    order: Order
    fill_price: float
    fill_time: pd.Timestamp
    commission: float
    slippage_cost: float  # total premium over mid (half_spread + slippage) × volume


@dataclass
class ExecutionConfig:
    """All costs in absolute price units (not pips / not bps)."""

    half_spread: float = 0.0
    slippage: float = 0.0
    commission_per_unit: float = 0.0


@dataclass
class ExecutionSimulator:
    config: ExecutionConfig

    def simulate_fill(self, order: Order, bar: Bar) -> Fill:
        """Produce the Fill that results from crossing ``order`` against ``bar``.

        Raises ``ValueError`` for non-positive volume — the Runner should never
        emit those; raising is louder than silently no-op'ing.
        """
        if order.volume <= 0:
            raise ValueError(f"order volume must be > 0, got {order.volume}")

        premium = self.config.half_spread + self.config.slippage
        fill_price = bar.close + premium if order.side == "buy" else bar.close - premium
        commission = self.config.commission_per_unit * order.volume
        slippage_cost = premium * order.volume

        return Fill(
            order=order,
            fill_price=fill_price,
            fill_time=bar.timestamp,
            commission=commission,
            slippage_cost=slippage_cost,
        )


@dataclass
class SwapModel:
    """Daily overnight financing. Called once per bar at the Runner's discretion.

    Rate semantics: ``rate × notional`` per day is **subtracted** from cash. A
    positive rate is a cost to the trader; a negative rate (rare — only for
    carry-favorable pairs) credits the trader.
    """

    long_rate_per_day: float = 0.0
    short_rate_per_day: float = 0.0

    def charge(self, portfolio, timestamp: pd.Timestamp) -> None:
        del timestamp  # reserved for calendar-aware rollover logic
        for pos in portfolio.positions.values():
            rate = self.long_rate_per_day if pos.side == "long" else self.short_rate_per_day
            if rate == 0.0:
                continue
            notional = pos.volume * pos.mark_price
            portfolio.apply_cash_flow(-rate * notional, reason=f"swap_{pos.symbol}")
