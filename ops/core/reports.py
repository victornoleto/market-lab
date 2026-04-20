"""Markdown renderers for benchmark reports + status dashboard."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from io import StringIO

import pandas as pd

from ops.core import benchmarks, positions, storage

ENABLED_SERIES = ("spy_usd", "ivvb11_brl", "ibov_brl", "ipca_pct_monthly",
                  "selic_daily_pct")


def _strategy_equity_curve(strategy: str, inception: date, end: date,
                           base: Decimal) -> pd.DataFrame:
    """Simple strategy equity: cumulative realized_gain_brl starting at base."""
    trades = sorted(
        [t for t in storage.read_trades() if t.strategy == strategy
         and inception <= t.date <= end],
        key=lambda t: t.date,
    )
    rows = []
    equity = float(base)
    current_date = inception
    for t in trades:
        if t.date > current_date:
            rows.append({"date": current_date, "value": equity})
            current_date = t.date
        if t.side == "sell":
            equity += float(t.realized_gain_brl)
    rows.append({"date": end, "value": equity})
    return pd.DataFrame(rows)


def render_monthly_benchmark_report(year: int, month: int,
                                    strategy: str = "plano_b",
                                    base_value_brl: Decimal = Decimal("100000")
                                    ) -> str:
    """Build a full markdown report for the given year-month."""
    import calendar
    _, last = calendar.monthrange(year, month)
    period_end = date(year, month, last)

    strategy_trades = [t for t in storage.read_trades() if t.strategy == strategy]
    if not strategy_trades:
        return f"# Benchmark report {year}-{month:02d}\n\nNo {strategy} trades yet.\n"
    inception = min(t.date for t in strategy_trades)

    buf = StringIO()
    buf.write(f"# Benchmark report — {strategy} — {year}-{month:02d}\n\n")
    buf.write(f"Inception: {inception}\n")
    buf.write(f"Period end: {period_end}\n\n")
    buf.write("## Equity vs benchmarks (rebased 100 at inception)\n\n")
    buf.write("| Series | Value @ period_end | Return since inception |\n")
    buf.write("|---|---|---|\n")

    strat_curve = _strategy_equity_curve(strategy, inception, period_end,
                                         base_value_brl)
    if not strat_curve.empty:
        strat_final = strat_curve.iloc[-1]["value"]
        strat_ret = (strat_final / float(base_value_brl) - 1) * 100
        buf.write(f"| **{strategy}** | R$ {strat_final:,.2f} | {strat_ret:+.2f}% |\n")

    for series_id in ENABLED_SERIES:
        curve = benchmarks.equity_curve_brl(series_id, inception, period_end,
                                            base_value_brl)
        if curve.empty:
            buf.write(f"| {series_id} | (no data) | — |\n")
            continue
        final = curve.iloc[-1]["value"]
        ret = (final / float(base_value_brl) - 1) * 100
        buf.write(f"| {series_id} | R$ {final:,.2f} | {ret:+.2f}% |\n")

    return buf.getvalue()


def render_status_dashboard(strategy: str = "plano_b") -> str:
    """Compact CLI dashboard."""
    pos = positions.current_positions()
    strategy_trades = [t for t in storage.read_trades() if t.strategy == strategy]
    unpaid_darfs = [e for e in storage.read_darf_history() if e.paid_at is None]
    carry = storage.read_carryforward()

    buf = StringIO()
    buf.write(f"=== ops status ({strategy}) ===\n")
    if strategy_trades:
        first = min(t.date for t in strategy_trades)
        last = max(t.date for t in strategy_trades)
        buf.write(f"Window: {first} -> {last}  ({len(strategy_trades)} trades)\n")
    else:
        buf.write("Window: (no trades yet)\n")

    buf.write("\nCurrent positions:\n")
    if not pos:
        buf.write("  (none)\n")
    for p in pos:
        buf.write(f"  {p.broker}/{p.account_id}  {p.ticker:<6}  "
                  f"qty={p.qty}  avg_cost_brl={p.avg_cost_brl:.2f}\n")

    buf.write(f"\nDARFs pendentes: {len(unpaid_darfs)}\n")
    for e in unpaid_darfs:
        buf.write(f"  {e.darf_id}  due {e.due_date}  "
                  f"R$ {e.tax_due_brl:.2f}  [{e.regime}]\n")

    if carry:
        buf.write("\nCarryforward balances (latest per stream):\n")
        latest: dict = {}
        for b in carry:
            key = (b.regime, b.stream)
            if key not in latest or b.period > latest[key].period:
                latest[key] = b
        for (regime, stream), b in sorted(latest.items()):
            buf.write(f"  {regime}/{stream:<12}  {b.period}  "
                      f"R$ {b.balance_out:.2f}\n")

    return buf.getvalue()
