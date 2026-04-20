"""Entry point: `ops` typer app."""
from __future__ import annotations

import typer

from ops.cli import darf, dividend, trade

app = typer.Typer(
    help="ops — Plano B operational platform (trades, DARFs, benchmarks).",
    no_args_is_help=True,
)

app.add_typer(trade.app, name="trade", help="Manage trade log.")
app.add_typer(dividend.app, name="dividend", help="Manage dividend log.")
app.add_typer(darf.app, name="darf", help="DARF calculator.")


@app.command()
def version() -> None:
    from ops.core.storage import SCHEMA_VERSION
    typer.echo(f"ops 0.1.0 (schema_version {SCHEMA_VERSION})")


if __name__ == "__main__":
    app()
