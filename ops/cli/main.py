"""Entry point: `ops` typer app. Wire subcommand groups."""
from __future__ import annotations

import typer

from ops.cli import trade

app = typer.Typer(
    help="ops — Plano B operational platform (trades, DARFs, benchmarks).",
    no_args_is_help=True,
)

app.add_typer(trade.app, name="trade", help="Manage trade log.")


@app.command()
def version() -> None:
    """Print version + schema_version."""
    from ops.core.storage import SCHEMA_VERSION
    typer.echo(f"ops 0.1.0 (schema_version {SCHEMA_VERSION})")


if __name__ == "__main__":
    app()
