"""Markdown report generator for a backtest run.

Input: a :class:`BacktestResult` plus the outputs of the validation framework
(PBO, DSR, walk-forward, CPCV). Output: a Markdown file in ``output_dir``
named ``<strategy>_<YYYYMMDD-HHMM>.md`` and a companion PNG chart under
``<output_dir>/assets/``.

Sections (in order):

1. **Header** — strategy name, run timestamp, data source.
2. **Survivorship disclaimer** — emitted for sources marked as biased
   (``yfinance``, ``wikipedia``). Skipped for survivorship-free sources
   (tag containing ``_sf`` or an explicit whitelist). ROADMAP rule: *every*
   biased report must carry the disclaimer.
3. **Performance** — CAGR, Sharpe, Sortino, Calmar, max DD, volatility, VaR.
4. **CPCV** — distribution of Sharpes across paths.
5. **PBO** — value + pass/reject verdict.
6. **DSR** — value, p-value, verdict vs α = 0.05 (rule #4).
7. **Walk-forward** — window counts + max DD + verdict.
8. **Equity curve + drawdown chart** — PNG embedded via Markdown image.
9. **Trades** — top 10 winners and top 10 losers.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from ai_trade.backtest.engine.runner import BacktestResult
from ai_trade.backtest.metrics._fmt import (
    _dataframe_to_markdown,
    _fmt_num,
    _fmt_pct,
)
from ai_trade.backtest.metrics.performance import (
    cagr,
    calmar,
    max_drawdown,
    returns_from_equity,
    sharpe,
    sortino,
    var,
    volatility,
)

_BIASED_SOURCES = {"yfinance", "wikipedia", "yahoo"}


def _needs_disclaimer(source: str) -> bool:
    s = source.lower()
    if s in _BIASED_SOURCES:
        return True
    # Any source not explicitly marked survivorship-free that has a known
    # biased substring. Pepperstone/cTrader historical IS biased (broker
    # lists only what it still offers) but calibration-stage reports will
    # mark that separately.
    return any(tag in s for tag in ("yfinance", "wikipedia", "yahoo"))


def _plot_equity_and_drawdown(equity: pd.Series, png_path: Path) -> None:
    """Two-panel chart: equity curve on top, underwater drawdown on bottom."""
    import matplotlib

    matplotlib.use("Agg")  # non-interactive backend for CI / headless VPS
    import matplotlib.pyplot as plt

    peak = equity.cummax()
    dd = (peak - equity) / peak

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(equity.index, equity.values, linewidth=1.2)
    ax1.set_ylabel("Equity")
    ax1.grid(True, alpha=0.3)

    ax2.fill_between(equity.index, -dd.values * 100, 0, alpha=0.5)
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_xlabel("Date")
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=120)
    plt.close(fig)


def _performance_table(equity: pd.Series, periods_per_year: int) -> str:
    if len(equity) < 2:
        return "| Metric | Value |\n|---|---|\n| (not enough data) | — |\n"
    rets = returns_from_equity(equity)
    rows = [
        ("CAGR", _fmt_pct(cagr(equity, periods_per_year))),
        ("Sharpe (annualized)", _fmt_num(sharpe(rets, periods_per_year), 3)),
        ("Sortino (annualized)", _fmt_num(sortino(rets, periods_per_year), 3)),
        ("Calmar", _fmt_num(calmar(equity, periods_per_year), 3)),
        ("Max drawdown", _fmt_pct(max_drawdown(equity))),
        ("Volatility (annualized)", _fmt_pct(volatility(rets, periods_per_year))),
        ("VaR (95%, historical)", _fmt_pct(var(rets, alpha=0.05))),
    ]
    lines = ["| Metric | Value |", "|---|---|"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    return "\n".join(lines) + "\n"


def _cpcv_section(cpcv: dict[str, Any] | None) -> str:
    if cpcv is None:
        return "_CPCV not run._\n"
    parts = ["| Statistic | Value |", "|---|---|"]
    for key, label, fmt in (
        ("mean_sharpe", "Mean Sharpe", lambda v: _fmt_num(v, 3)),
        ("std_sharpe", "Std Sharpe", lambda v: _fmt_num(v, 3)),
        ("min_sharpe", "Min Sharpe", lambda v: _fmt_num(v, 3)),
        ("max_sharpe", "Max Sharpe", lambda v: _fmt_num(v, 3)),
    ):
        if key in cpcv:
            parts.append(f"| {label} | {fmt(float(cpcv[key]))} |")
    paths = cpcv.get("path_sharpes")
    if paths is not None:
        parts.append(f"| N paths | {len(paths)} |")
    return "\n".join(parts) + "\n"


def _pbo_section(pbo_res: Any) -> str:
    if pbo_res is None:
        return "_PBO not run._\n"
    from ai_trade.backtest.validation.pbo import pbo_gate

    value = float(pbo_res.pbo)
    verdict = pbo_gate(value)
    return (
        f"- **PBO:** {_fmt_num(value, 3)}\n"
        f"- **Verdict:** `{verdict}` (gate: reject when PBO ≥ 0.5)\n"
        f"- **Combinations:** {pbo_res.n_combinations} across "
        f"{pbo_res.n_blocks} blocks\n"
    )


def _dsr_section(dsr_res: Any, alpha: float = 0.05) -> str:
    if dsr_res is None:
        return "_DSR not run._\n"
    p = float(dsr_res.p_value)
    verdict = "pass" if p < alpha else "reject"
    return (
        f"- **Observed Sharpe (periodic):** {_fmt_num(dsr_res.observed_sharpe, 4)}\n"
        f"- **Benchmark E[SR_max] over {dsr_res.n_trials} trials:** "
        f"{_fmt_num(dsr_res.benchmark_sharpe, 4)}\n"
        f"- **DSR:** {_fmt_num(dsr_res.dsr, 4)}\n"
        f"- **p-value:** {_fmt_num(p, 4)}\n"
        f"- **Verdict:** `{verdict}` (α = {alpha})\n"
    )


def _walk_forward_section(wf: dict[str, Any] | None) -> str:
    if wf is None:
        return "_Walk-forward not run._\n"
    rows = [
        ("Windows", str(wf.get("n_windows", "—"))),
        ("Profitable", str(wf.get("n_profitable", "—"))),
        ("Max drawdown (worst window)", _fmt_pct(float(wf["max_drawdown"]))
            if "max_drawdown" in wf else "—"),
        ("Verdict", f"`{wf.get('verdict', '—')}`"),
    ]
    lines = ["| Metric | Value |", "|---|---|"]
    lines.extend(f"| {k} | {v} |" for k, v in rows)
    return "\n".join(lines) + "\n"


def _trades_section(trades: list) -> str:
    if not trades:
        return "_No closed trades._\n"
    df = pd.DataFrame(
        [
            {
                "symbol": t.symbol,
                "side": t.side,
                "volume": t.volume,
                "entry_time": t.entry_time,
                "exit_time": t.exit_time,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "pnl": t.pnl,
            }
            for t in trades
        ]
    )
    df_sorted = df.sort_values("pnl", ascending=False)
    winners = df_sorted.head(10)
    losers = df_sorted.tail(10).iloc[::-1]  # most negative first

    def _fmt_table(frame: pd.DataFrame) -> str:
        if frame.empty:
            return "_(none)_\n"
        frame = frame.copy()
        frame["pnl"] = frame["pnl"].map(lambda x: f"{x:,.2f}")
        frame["entry_price"] = frame["entry_price"].map(lambda x: f"{x:,.2f}")
        frame["exit_price"] = frame["exit_price"].map(lambda x: f"{x:,.2f}")
        return _dataframe_to_markdown(frame) + "\n"

    return (
        "### Top 10 Winners\n\n"
        + _fmt_table(winners)
        + "\n### Top 10 Losers\n\n"
        + _fmt_table(losers)
    )


def generate_report(
    *,
    result: BacktestResult,
    validation: dict[str, Any],
    strategy_name: str,
    output_dir: Path | str,
    data_source: str,
    periods_per_year: int = 252,
    run_time: datetime | None = None,
) -> Path:
    """Render a full backtest report; return the path to the Markdown file.

    ``validation`` is a dict that may carry any of: ``"pbo"`` (PBOResult),
    ``"dsr"`` (DSRResult), ``"walk_forward"`` (dict with keys ``n_windows``,
    ``n_profitable``, ``max_drawdown``, ``verdict``), ``"cpcv"`` (dict with
    path Sharpe summary stats). Missing keys are rendered as "not run".
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "assets").mkdir(exist_ok=True)

    run_time = run_time or datetime.now()
    stamp = run_time.strftime("%Y%m%d-%H%M")
    md_path = output_dir / f"{strategy_name}_{stamp}.md"
    png_path = output_dir / "assets" / f"{strategy_name}_{stamp}.png"

    _plot_equity_and_drawdown(result.equity_curve, png_path)

    header = (
        f"# Backtest Report — `{strategy_name}`\n\n"
        f"- **Run:** {run_time.isoformat(timespec='minutes')}\n"
        f"- **Data source:** `{data_source}`\n"
        f"- **Initial cash:** ${result.initial_cash:,.2f}\n"
        f"- **Final equity:** ${result.final_equity:,.2f}\n"
        f"- **Periods/year:** {periods_per_year}\n"
    )

    disclaimer = ""
    if _needs_disclaimer(data_source):
        disclaimer = (
            "\n> ⚠️ **Survivorship bias warning.** This backtest uses a data "
            "source (`" + data_source + "`) that contains survivorship bias: "
            "companies delisted or bankrupted during the test period are not "
            "represented. Reported returns are systematically **overstated**. "
            "See ROADMAP §\"Deferred decisions — Data source\". Move to a "
            "survivorship-free source (Tiingo SF, Norgate, EOD) before "
            "trusting any gate decision based on this report.\n"
        )

    pbo_res = validation.get("pbo")
    dsr_res = validation.get("dsr")
    wf_res = validation.get("walk_forward")
    cpcv_res = validation.get("cpcv")

    sections = [
        header,
        disclaimer,
        "## Performance summary\n\n" + _performance_table(result.equity_curve, periods_per_year),
        "## Equity curve + drawdown\n\n"
        f"![equity and drawdown](assets/{png_path.name})\n",
        "## CPCV path distribution\n\n" + _cpcv_section(cpcv_res),
        "## PBO (Probability of Backtest Overfitting)\n\n" + _pbo_section(pbo_res),
        "## DSR (Deflated Sharpe Ratio)\n\n" + _dsr_section(dsr_res),
        "## Walk-forward\n\n" + _walk_forward_section(wf_res),
        "## Trades\n\n" + _trades_section(result.trades),
    ]
    md_path.write_text("\n".join(sections))
    return md_path
