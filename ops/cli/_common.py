"""Shared CLI utilities: pretty tables, confirmations, error formatting."""
from __future__ import annotations

from decimal import Decimal

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
