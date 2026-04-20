"""`ops trade ...` subcommand group."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

import typer

from ops.cli._common import die, fmt_brl, fmt_qty
from ops.core import fx, storage
from ops.core.models import Trade

app = typer.Typer(help="Trade journal — add, list, show, delete, edit.")


def _next_trade_id(d: date) -> str:
    existing = storage.read_trades()
    prefix = f"T-{d.strftime('%Y%m%d')}"
    count = sum(1 for t in existing if t.trade_id.startswith(prefix))
    return f"{prefix}-{count + 1:03d}"


@app.command()
def add(
    ticker: str = typer.Option(..., "--ticker", "-t"),
    side: str = typer.Option(..., "--side", "-s", help="buy|sell"),
    qty: str = typer.Option(..., "--qty", "-q"),
    price_native: str = typer.Option(..., "--price", "-p"),
    currency: str = typer.Option("USD", "--currency"),
    fees_native: str = typer.Option("0", "--fees"),
    d: str = typer.Option(None, "--date", help="YYYY-MM-DD, default today"),
    broker: str = typer.Option("inter_global", "--broker"),
    account_id: str = typer.Option("inter_global_placeholder", "--account"),
    strategy: str = typer.Option("plano_b", "--strategy"),
    instrument_type: str = typer.Option("etf", "--instrument-type"),
    instrument_domicile: str = typer.Option("us", "--domicile"),
    ptax: Optional[str] = typer.Option(None, "--ptax",
        help="Override PTAX; default auto-fetch from BCB"),
    trade_type: str = typer.Option("swing", "--type"),
    notes: str = typer.Option("", "--notes"),
) -> None:
    """Add a new trade. PTAX auto-fetched unless --ptax given."""
    # Convert string inputs to Decimal after CLI parsing (Typer doesn't support Decimal natively)
    qty_d = Decimal(qty)
    price_native_d = Decimal(price_native)
    fees_native_d = Decimal(fees_native)
    ptax_d: Optional[Decimal] = Decimal(ptax) if ptax is not None else None

    if side not in ("buy", "sell"):
        die(f"side must be buy|sell, got {side!r}")
    trade_date = date.fromisoformat(d) if d else date.today()
    ptax_venda = ptax_d if ptax_d is not None else (
        Decimal("1") if currency == "BRL" else fx.get_ptax(trade_date)
    )

    # Compute BRL values
    gross_native = qty_d * price_native_d
    gross_brl = gross_native * ptax_venda
    fees_brl = fees_native_d * ptax_venda
    cost_basis_brl = gross_brl + fees_brl if side == "buy" else Decimal("0")

    realized_gain_brl = Decimal("0")
    if side == "sell":
        from ops.core.positions import positions_from_trades
        existing = storage.read_trades()
        ticker_lots = []
        for p in positions_from_trades(existing):
            if (p.broker == broker and p.account_id == account_id
                and p.ticker == ticker):
                ticker_lots = list(p.open_lots)
                break
        remaining = qty_d
        consumed_basis = Decimal("0")
        for lot in ticker_lots:
            if remaining <= 0:
                break
            take = min(lot.qty, remaining)
            fraction = take / lot.qty
            consumed_basis += lot.cost_basis_brl * fraction
            remaining -= take
        if remaining > 0:
            die(f"Insufficient FIFO qty: need {qty_d}, available "
                f"{qty_d - remaining}. Backfill buys first.")
        realized_gain_brl = gross_brl - fees_brl - consumed_basis

    trade_id = _next_trade_id(trade_date)
    trade = Trade(
        trade_id=trade_id, date=trade_date, broker=broker, account_id=account_id,
        strategy=strategy, ticker=ticker, instrument_type=instrument_type,
        instrument_domicile=instrument_domicile, side=side, qty=qty_d,
        price_native=price_native_d, currency=currency, fees_native=fees_native_d,
        ptax_venda=ptax_venda, cost_basis_brl=cost_basis_brl, gross_brl=gross_brl,
        realized_gain_brl=realized_gain_brl, trade_type=trade_type, notes=notes,
    )
    with storage.lock():
        storage.append_trade(trade)
    typer.secho(f"[OK] Trade {trade_id} registrado.", fg=typer.colors.GREEN)
    typer.echo(f"  Date      : {trade_date.isoformat()}")
    typer.echo(f"  {side.upper():4} {fmt_qty(qty_d)} {ticker} @ {price_native_d} {currency}")
    typer.echo(f"  PTAX      : {ptax_venda}")
    typer.echo(f"  Gross BRL : {fmt_brl(gross_brl)}")
    if side == "buy":
        typer.echo(f"  Cost basis: {fmt_brl(cost_basis_brl)}")
    else:
        typer.echo(f"  Realized  : {fmt_brl(realized_gain_brl)}")


@app.command("list")
def list_trades(
    strategy: Optional[str] = typer.Option(None, "--strategy"),
    ticker: Optional[str] = typer.Option(None, "--ticker"),
    broker: Optional[str] = typer.Option(None, "--broker"),
    side: Optional[str] = typer.Option(None, "--side"),
    since: Optional[str] = typer.Option(None, "--since"),
    until: Optional[str] = typer.Option(None, "--until"),
) -> None:
    """List trades with filters."""
    trades = storage.read_trades()
    if strategy:
        trades = [t for t in trades if t.strategy == strategy]
    if ticker:
        trades = [t for t in trades if t.ticker == ticker]
    if broker:
        trades = [t for t in trades if t.broker == broker]
    if side:
        trades = [t for t in trades if t.side == side]
    if since:
        d = date.fromisoformat(since)
        trades = [t for t in trades if t.date >= d]
    if until:
        d = date.fromisoformat(until)
        trades = [t for t in trades if t.date <= d]

    if not trades:
        typer.echo("(no trades)")
        return
    for t in sorted(trades, key=lambda t: (t.date, t.trade_id)):
        typer.echo(
            f"{t.trade_id}  {t.date.isoformat()}  {t.side:4}  "
            f"{fmt_qty(t.qty):>8} {t.ticker:<6}  @ {t.price_native} {t.currency}  "
            f"PTAX {t.ptax_venda}  "
            f"gain={fmt_brl(t.realized_gain_brl):>14}  [{t.strategy}]"
        )


@app.command()
def show(trade_id: str) -> None:
    """Show detail of one trade."""
    trades = storage.read_trades()
    match = [t for t in trades if t.trade_id == trade_id]
    if not match:
        die(f"Trade {trade_id} not found")
    t = match[0]
    for field_name in t.__dataclass_fields__:
        value = getattr(t, field_name)
        typer.echo(f"  {field_name:22}: {value}")
