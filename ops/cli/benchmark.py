"""`ops benchmark ...` subcommand group."""
from __future__ import annotations

from pathlib import Path

import typer

from ops.core import benchmarks, reports

app = typer.Typer(help="Benchmarks — fetch, report.")


@app.command()
def fetch(
    series: str = typer.Option("all", "--series",
        help="Comma-separated list or 'all'."),
) -> None:
    """Refresh benchmark series caches."""
    if series == "all":
        benchmarks.fetch_all()
    else:
        for s in series.split(","):
            fn = getattr(benchmarks, f"fetch_{s.strip()}", None)
            if fn is None:
                typer.echo(f"[WARN] unknown series {s!r}, skipping")
                continue
            fn()
    typer.secho("[OK] benchmark fetch done.", fg=typer.colors.GREEN)


@app.command()
def report(
    year: int = typer.Option(..., "--year"),
    month: int = typer.Option(..., "--month"),
    strategy: str = typer.Option("plano_b", "--strategy"),
    out: str = typer.Option(None, "--out", help="Write to file; default stdout"),
) -> None:
    """Generate monthly benchmark comparison report (markdown)."""
    md = reports.render_monthly_benchmark_report(year, month, strategy=strategy)
    if out:
        Path(out).write_text(md, encoding="utf-8")
        typer.echo(f"[OK] Report written to {out}")
    else:
        typer.echo(md)
