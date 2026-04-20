"""`ops darf ...` subcommand group."""
from __future__ import annotations

from dataclasses import replace as dataclass_replace
from datetime import date
from decimal import Decimal
from typing import Optional

import typer

from ops.cli._common import die, fmt_brl, parse_date
from ops.core import storage
from ops.core.models import CarryforwardBalance, Stream
from ops.core.tax import get_regime

app = typer.Typer(help="DARF calculator — preview, close, list, carryforward, paid.")

DEFAULT_REGIME = "annual_14754"  # Configurable via config.yaml in future.


def _current_carryforward(regime_name: str, stream: Stream) -> Decimal:
    """Latest balance_out for (regime, stream). Zero if none."""
    balances = storage.read_carryforward()
    matching = [b for b in balances if b.regime == regime_name and b.stream == stream]
    if not matching:
        return Decimal("0")
    latest = max(matching, key=lambda b: b.period)
    return latest.balance_out


@app.command()
def preview(
    regime: str = typer.Option(DEFAULT_REGIME, "--regime"),
    d: Optional[str] = typer.Option(None, "--date", help="Any date inside the period"),
) -> None:
    """Compute DARFs for the period containing --date (or today) without committing."""
    r = get_regime(regime)
    ref = parse_date(d, "--date") if d else date.today()
    period_start, period_end = r.period_for(ref)

    trades = [t for t in storage.read_trades() if period_start <= t.date <= period_end]
    divs = [x for x in storage.read_dividends() if period_start <= x.payment_date <= period_end]
    carry_in = {s: _current_carryforward(regime, s) for s in r.streams}

    events = r.compute(trades, divs, carry_in, period_start, period_end)
    if not events:
        typer.echo(f"[PREVIEW] {regime} {r.period_key(period_end)}: nenhum DARF "
                   f"(sem ganho liquido positivo apos carryforward).")
        return
    for e in events:
        typer.echo(f"--- {e.darf_id} ({e.stream}, code {e.code}) ---")
        typer.echo(f"  Period          : {e.period_start} -> {e.period_end}")
        typer.echo(f"  Due date        : {e.due_date}")
        typer.echo(f"  Gross gain      : {fmt_brl(e.gross_gain_brl)}")
        typer.echo(f"  Dividends       : {fmt_brl(e.dividends_brl)}")
        typer.echo(f"  Carryforward in : {fmt_brl(carry_in.get(e.stream, Decimal('0')))}")
        typer.echo(f"  Loss offset     : {fmt_brl(e.loss_offset_brl)}")
        typer.echo(f"  Net taxable     : {fmt_brl(e.net_taxable_brl)}")
        typer.echo(f"  Tax rate        : {e.tax_rate_applied * 100}%")
        typer.secho(f"  Tax due         : {fmt_brl(e.tax_due_brl)}",
                    fg=typer.colors.YELLOW, bold=True)


@app.command()
def close(
    regime: str = typer.Option(DEFAULT_REGIME, "--regime"),
    period: Optional[str] = typer.Option(None, "--period",
        help="YYYY-MM (monthly) or YYYY (annual). Defaults to period containing today."),
) -> None:
    """Compute + commit DARFs + update carryforward."""
    r = get_regime(regime)
    if period:
        if len(period) == 7:
            try:
                y, m = int(period[:4]), int(period[5:7])
                ref = date(y, m, 15)
            except ValueError:
                die(f"Invalid --period {period!r}")
        elif len(period) == 4:
            try:
                ref = date(int(period), 6, 15)
            except ValueError:
                die(f"Invalid --period {period!r}")
        else:
            die(f"Invalid --period {period!r}")
    else:
        ref = date.today()
    period_start, period_end = r.period_for(ref)
    period_key = r.period_key(period_end)

    with storage.lock():
        # Idempotency check (must be inside lock)
        existing = [e for e in storage.read_darf_history()
                    if e.regime == regime
                    and e.period_start == period_start
                    and e.period_end == period_end]
        if existing:
            die(f"DARF for {regime} {period_key} already exists. "
                f"Use `ops darf recompute --confirm`.")

        trades = [t for t in storage.read_trades() if period_start <= t.date <= period_end]
        divs = [x for x in storage.read_dividends() if period_start <= x.payment_date <= period_end]
        carry_in = {s: _current_carryforward(regime, s) for s in r.streams}

        events = r.compute(trades, divs, carry_in, period_start, period_end)

        # Build new carryforward balances (one row per stream, regardless of events emitted).
        new_balances = []
        for stream in r.streams:
            if stream in ("swing", "daytrade"):
                stream_sells = [t for t in trades
                                if t.side == "sell" and t.trade_type == stream]
            else:  # rendimentos — annual regime, all sells count
                stream_sells = [t for t in trades if t.side == "sell"]
            # Accrue: negative gains flip sign and contribute to carryforward pool
            accrued = sum(
                (-t.realized_gain_brl for t in stream_sells if t.realized_gain_brl < 0),
                start=Decimal("0"),
            )
            consumed = sum(
                (e.loss_offset_brl for e in events if e.stream == stream),
                start=Decimal("0"),
            )
            balance_in = carry_in.get(stream, Decimal("0"))
            balance_out = balance_in + accrued - consumed
            if balance_out < 0:
                die(f"Carryforward invariant violated: balance_out={balance_out} "
                    f"for {regime}/{stream} in {period_key}")
            new_balances.append(CarryforwardBalance(
                regime=regime, stream=stream, period=period_key,
                balance_in=balance_in, accrued_this_period=accrued,
                consumed_this_period=consumed, balance_out=balance_out,
            ))

        for e in events:
            storage.append_darf_event(e)
        all_balances = storage.read_carryforward()
        all_balances = [
            b for b in all_balances
            if not (b.regime == regime and b.period == period_key)
        ] + new_balances
        storage.write_carryforward(all_balances)

    # Print results AFTER releasing lock
    if not events:
        typer.echo(f"[OK] {regime} {period_key}: sem DARF (sem ganho tributavel). "
                   f"Carryforward atualizado.")
    else:
        for e in events:
            typer.secho(f"[OK] {e.darf_id} criado: "
                        f"{fmt_brl(e.tax_due_brl)} vence {e.due_date}.",
                        fg=typer.colors.GREEN)
    typer.echo(f"Carryforward saldos pos-periodo ({period_key}):")
    for b in new_balances:
        typer.echo(f"  {b.stream:<12}: balance_out = {fmt_brl(b.balance_out)}")


@app.command("list")
def list_darfs(
    unpaid: bool = typer.Option(False, "--unpaid"),
) -> None:
    """List DARFs. --unpaid filters pending."""
    events = storage.read_darf_history()
    if unpaid:
        events = [e for e in events if e.paid_at is None]
    if not events:
        typer.echo("(no DARFs)")
        return
    for e in sorted(events, key=lambda x: x.due_date):
        status = "PAID" if e.paid_at else "PENDING"
        typer.echo(f"{e.darf_id}  {status:<7}  due {e.due_date}  "
                   f"{fmt_brl(e.tax_due_brl):>14}  [{e.regime}/{e.stream}]")


@app.command()
def carryforward() -> None:
    """Show current carryforward balances per (regime, stream)."""
    balances = storage.read_carryforward()
    if not balances:
        typer.echo("(no carryforward data)")
        return
    latest: dict[tuple[str, str], CarryforwardBalance] = {}
    for b in balances:
        key = (b.regime, b.stream)
        if key not in latest or b.period > latest[key].period:
            latest[key] = b
    for (regime, stream), b in sorted(latest.items()):
        typer.echo(f"{regime}/{stream:<12}  period {b.period}  "
                   f"balance = {fmt_brl(b.balance_out)}")


@app.command()
def paid(
    darf_id: str,
    d: Optional[str] = typer.Option(None, "--date", help="Payment date YYYY-MM-DD"),
    proof: str = typer.Option("", "--proof", help="Path to receipt PDF"),
) -> None:
    """Mark a DARF as paid."""
    events = storage.read_darf_history()
    match_idx = next((i for i, e in enumerate(events) if e.darf_id == darf_id), None)
    if match_idx is None:
        die(f"DARF {darf_id} not found")
    paid_date = parse_date(d, "--date") if d else date.today()
    events[match_idx] = dataclass_replace(events[match_idx], paid_at=paid_date, paid_proof_path=proof)
    with storage.lock():
        storage.write_darf_history(events)
    typer.secho(f"[OK] {darf_id} marked paid on {paid_date}.", fg=typer.colors.GREEN)
