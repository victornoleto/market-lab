"""FIFO lot matching + current positions derived from trade log.

Fiscal compliance: FIFO per IN RFB 1.585/2015 Art. 58.
Positions are *derived* from trades.csv (source of truth); never stored
separately.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from ops.core import storage
from ops.core.models import Lot, Position, Trade


class InsufficientQty(Exception):
    pass


def _group_key(t: Trade) -> tuple[str, str, str]:
    return (t.broker, t.account_id, t.ticker)


def current_positions() -> list[Position]:
    """Reconstruct current positions from the full trade log."""
    trades = sorted(storage.read_trades(), key=lambda t: (t.date, t.trade_id))
    return positions_from_trades(trades)


def positions_from_trades(trades: list[Trade]) -> list[Position]:
    """Apply FIFO lot matching to a chronologically sorted list of trades."""
    open_lots: dict[tuple[str, str, str], list[Lot]] = defaultdict(list)

    for t in trades:
        key = _group_key(t)
        if t.side == "buy":
            open_lots[key].append(
                Lot(trade_id=t.trade_id, date=t.date, ticker=t.ticker,
                    qty=t.qty, cost_basis_brl=t.cost_basis_brl)
            )
        else:  # sell — consume FIFO
            remaining = t.qty
            while remaining > Decimal("0"):
                if not open_lots[key]:
                    raise InsufficientQty(
                        f"Sell {t.trade_id} of {remaining} {t.ticker} but no open lots"
                    )
                lot = open_lots[key][0]
                if lot.qty <= remaining:
                    remaining -= lot.qty
                    open_lots[key].pop(0)
                else:
                    # Partial consume: keep the lot but shrink qty + proportional basis
                    fraction = remaining / lot.qty
                    new_qty = lot.qty - remaining
                    new_basis = lot.cost_basis_brl * (Decimal("1") - fraction)
                    open_lots[key][0] = Lot(
                        trade_id=lot.trade_id, date=lot.date, ticker=lot.ticker,
                        qty=new_qty, cost_basis_brl=new_basis,
                    )
                    remaining = Decimal("0")

    result: list[Position] = []
    for (broker, account_id, ticker), lots in open_lots.items():
        if not lots:
            continue
        total_qty = sum((l.qty for l in lots), start=Decimal("0"))
        total_basis = sum((l.cost_basis_brl for l in lots), start=Decimal("0"))
        avg_cost = total_basis / total_qty if total_qty > 0 else Decimal("0")
        result.append(
            Position(
                broker=broker, account_id=account_id, ticker=ticker,
                qty=total_qty, avg_cost_brl=avg_cost,
                open_lots=tuple(lots),
            )
        )
    return result


def drift_vs_target(strategy: str, target: dict[str, Decimal]) -> dict[str, Decimal]:
    """Realized weight per ticker within strategy minus target.

    Uses avg_cost_brl as value proxy (not mark-to-market) — MVP level.
    MTM will require benchmarks data (Task 9+).
    """
    trades = [t for t in storage.read_trades() if t.strategy == strategy]
    pos = positions_from_trades(trades)
    total = sum((p.qty * p.avg_cost_brl for p in pos), start=Decimal("0"))
    if total == 0:
        return {ticker: -target.get(ticker, Decimal("0")) for ticker in target}
    actual = {p.ticker: (p.qty * p.avg_cost_brl) / total for p in pos}
    return {
        ticker: actual.get(ticker, Decimal("0")) - target.get(ticker, Decimal("0"))
        for ticker in set(list(target) + list(actual))
    }
