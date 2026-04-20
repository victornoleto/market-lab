"""`ops dividend ...` subcommand group."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

import typer

from ops.cli._common import die, fmt_brl, parse_date, parse_decimal
from ops.core import fx, storage
from ops.core.models import Dividend

app = typer.Typer(help="Dividend journal (Plano B ETFs distribute; Lei 14.754 unifies).")


def _next_div_id(d: date) -> str:
    existing = storage.read_dividends()
    prefix = f"D-{d.strftime('%Y%m%d')}"
    count = sum(1 for x in existing if x.dividend_id.startswith(prefix))
    return f"{prefix}-{count + 1:03d}"


@app.command()
def add(
    ticker: str = typer.Option(..., "--ticker", "-t"),
    gross_usd: str = typer.Option(..., "--gross-usd"),
    withheld_usd: str = typer.Option("0", "--withheld-usd"),
    d: Optional[str] = typer.Option(None, "--date", help="Payment date YYYY-MM-DD"),
    broker: str = typer.Option("inter_global", "--broker"),
    account_id: str = typer.Option("inter_global_placeholder", "--account"),
    ptax: Optional[str] = typer.Option(None, "--ptax"),
    notes: str = typer.Option("", "--notes"),
) -> None:
    """Register a dividend payment. PTAX auto-fetched unless --ptax given."""
    gross_d = parse_decimal(gross_usd, "--gross-usd")
    withheld_d = parse_decimal(withheld_usd, "--withheld-usd")
    payment_date = parse_date(d, "--date") if d else date.today()
    ptax_venda = parse_decimal(ptax, "--ptax") if ptax is not None else fx.get_ptax(payment_date)
    net_usd = gross_d - withheld_d
    with storage.lock():
        div_id = _next_div_id(payment_date)
        div = Dividend(
            dividend_id=div_id,
            payment_date=payment_date, broker=broker, account_id=account_id,
            ticker=ticker, gross_usd=gross_d, withheld_us_tax_usd=withheld_d,
            net_usd=net_usd, ptax_venda=ptax_venda,
            gross_brl=gross_d * ptax_venda,
            withheld_us_tax_brl=withheld_d * ptax_venda,
            net_brl=net_usd * ptax_venda, notes=notes,
        )
        storage.append_dividend(div)
    typer.secho(f"[OK] Dividend {div.dividend_id} registrado.", fg=typer.colors.GREEN)
    typer.echo(f"  Gross BRL: {fmt_brl(div.gross_brl)}  (withheld {fmt_brl(div.withheld_us_tax_brl)})")
    typer.secho(
        "[ALERT] Regime annual_14754: este valor entra no bucket rendimentos anual.\n"
        "[ALERT] Regime monthly_6015: lembrar de declarar Carne-Leao (codigo 0190) "
        "ate ultimo dia util do mes seguinte.",
        fg=typer.colors.YELLOW,
    )


@app.command("list")
def list_dividends(
    ticker: Optional[str] = typer.Option(None, "--ticker"),
    since: Optional[str] = typer.Option(None, "--since"),
    until: Optional[str] = typer.Option(None, "--until"),
) -> None:
    """List dividends with filters."""
    divs = storage.read_dividends()
    if ticker:
        divs = [d for d in divs if d.ticker == ticker]
    if since:
        s = parse_date(since, "--since")
        divs = [d for d in divs if d.payment_date >= s]
    if until:
        u = parse_date(until, "--until")
        divs = [d for d in divs if d.payment_date <= u]
    if not divs:
        typer.echo("(no dividends)")
        return
    for d in sorted(divs, key=lambda x: x.payment_date):
        typer.echo(
            f"{d.dividend_id}  {d.payment_date.isoformat()}  {d.ticker:<6}  "
            f"gross={fmt_brl(d.gross_brl):>12}  net={fmt_brl(d.net_brl):>12}"
        )
