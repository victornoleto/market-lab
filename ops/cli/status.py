"""`ops status` quick dashboard."""
from __future__ import annotations

import typer

from ops.core import reports


def main(strategy: str = typer.Option("plano_b", "--strategy")) -> None:
    """Show quick dashboard."""
    typer.echo(reports.render_status_dashboard(strategy=strategy))
