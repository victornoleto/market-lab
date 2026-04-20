"""Shared CLI utilities: pretty tables, confirmations, error formatting."""
from __future__ import annotations

from datetime import date as _date
from decimal import Decimal, InvalidOperation

import typer


def fmt_brl(v: Decimal) -> str:
    sign = "-" if v < 0 else ""
    abs_v = abs(v)
    return f"{sign}R$ {abs_v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_qty(v: Decimal) -> str:
    s = str(v.normalize())
    return s if "." in s else s + ".0"


def confirm(prompt: str) -> bool:
    return typer.confirm(prompt, default=False, abort=False)


def die(msg: str, code: int = 1) -> None:
    typer.secho(f"[ERROR] {msg}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code)


def parse_decimal(s: str, flag: str) -> Decimal:
    """Parse string to Decimal, die() with friendly error on bad input."""
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        die(f"{flag} must be a number, got {s!r}")


def parse_date(s: str, flag: str) -> _date:
    """Parse ISO date string, die() with friendly error on bad input."""
    try:
        return _date.fromisoformat(s)
    except (ValueError, TypeError):
        die(f"{flag} must be YYYY-MM-DD, got {s!r}")
