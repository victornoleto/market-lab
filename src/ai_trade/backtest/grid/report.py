"""GridReportGenerator — Markdown + PNG reports for a grid run.

Two entry points:

* :meth:`GridReportGenerator.write_pass_report` when ``overall_pass=True``.
  Tells the user "a config survived, here's the verdict, here are the
  numbers, next step is paid-data ablation + 2nd strategy."
* :meth:`GridReportGenerator.write_fail_report` when the grid failed. Hands
  over a :class:`DiagnosticReport` rendered as narrative + data — the user
  decides the next move.

Both reports emit the survivorship disclaimer for biased sources (same
contract as :mod:`ai_trade.backtest.metrics.report`).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai_trade.backtest.grid.diagnostic import DiagnosticReport  # noqa: E402
from ai_trade.backtest.grid.gates import GateVerdict  # noqa: E402
from ai_trade.backtest.grid.result import GridResult  # noqa: E402
from ai_trade.backtest.grid.walk_forward import WFResult  # noqa: E402
from ai_trade.backtest.metrics._fmt import (  # noqa: E402
    _dataframe_to_markdown,
    _fmt_num,
    _fmt_pct,
)


_log = logging.getLogger("ai_trade.grid.report")


_BIASED_MARKERS = ("yfinance", "wikipedia", "yahoo")
_SURVIVORSHIP_FREE_MARKERS = ("_sf", "norgate", "tiingo_sf", "eod_sf")


def _needs_disclaimer(source: str) -> bool:
    s = source.lower()
    if any(m in s for m in _SURVIVORSHIP_FREE_MARKERS):
        return False
    return any(m in s for m in _BIASED_MARKERS) or True


_SURVIVORSHIP_TEXT = (
    "\n> ⚠️ **Survivorship bias warning.** This grid uses a data source "
    "that contains survivorship bias: companies delisted or bankrupted "
    "during the test period are not represented. Reported returns are "
    "systematically **overstated**. See ROADMAP §\"Decisões adiadas — "
    "Fonte de dados\". Migrating to a survivorship-free source "
    "(Tiingo SF, Norgate, EOD) is the ROADMAP gate for trusting any "
    "verdict from this report.\n"
)


@dataclass
class GridReportGenerator:
    periods_per_year: int = 252

    def write_pass_report(
        self,
        *,
        grid: GridResult,
        verdict: GateVerdict,
        wf_results: dict[int, WFResult],
        output_dir: Path,
        data_source: str,
        run_time: datetime | None = None,
    ) -> Path:
        output_dir = Path(output_dir)
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        run_time = run_time or datetime.now()
        heatmap_path = assets_dir / "heatmap_sharpe.png"
        _write_sharpe_heatmap(grid, heatmap_path)

        best_config_id = verdict.best_config_id
        best_equity_path = None
        if best_config_id is not None:
            best_trial = next(
                (t for t in grid.trials if t.config_id == best_config_id), None,
            )
            if best_trial is not None and best_trial.result is not None:
                best_equity_path = assets_dir / f"equity_best_{best_config_id}.png"
                _write_equity_chart(best_trial.result.equity_curve, best_equity_path)

        sections = [
            _header(grid, run_time, data_source, verdict_pass=True),
            _SURVIVORSHIP_TEXT if _needs_disclaimer(data_source) else "",
            "## Gate verdict — PASS\n\n" + _gate_summary_table(verdict),
            "## Best config\n\n"
            + _best_config_section(grid, verdict, wf_results),
            "## Equity curve — best config\n\n"
            + (
                f"![equity](assets/{best_equity_path.name})\n"
                if best_equity_path is not None
                else "_not available_\n"
            ),
            "## Sharpe heatmap (lookback × top_pct × risk_factor)\n\n"
            + f"![sharpe heatmap](assets/{heatmap_path.name})\n",
            "## Per-config metrics\n\n" + _per_config_table(grid, verdict, wf_results),
            "## Next step\n\n"
            + (
                "- A config passed all 3 anti-overfit gates (PBO < 0.5, "
                "DSR p < 0.05, walk-forward ≥ 6/8 profitable).\n"
                "- Validate on a survivorship-free paid-data source as the "
                "first ablation study (ROADMAP §\"Decisões adiadas\").\n"
                "- Proceed to the second strategy (Ehlers DSP / AFML meta-"
                "label / Chan mean-reversion) once the survivorship "
                "ablation succeeds.\n"
            ),
        ]
        md_path = output_dir / "summary.md"
        md_path.write_text("\n\n".join(s for s in sections if s))
        return md_path

    def write_fail_report(
        self,
        *,
        grid: GridResult,
        verdict: GateVerdict,
        wf_results: dict[int, WFResult],
        diagnostic: DiagnosticReport,
        output_dir: Path,
        data_source: str,
        run_time: datetime | None = None,
    ) -> Path:
        output_dir = Path(output_dir)
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        run_time = run_time or datetime.now()
        heatmap_path = assets_dir / "heatmap_sharpe.png"
        _write_sharpe_heatmap(grid, heatmap_path)

        sections = [
            _header(grid, run_time, data_source, verdict_pass=False),
            _SURVIVORSHIP_TEXT if _needs_disclaimer(data_source) else "",
            "## Gate verdict — FAIL\n\n" + _gate_summary_table(verdict),
            "## Failure modes\n\n" + _failure_modes_section(diagnostic),
            "## Best config so far (ignoring gates)\n\n"
            + _best_config_section_from_diag(diagnostic, wf_results),
            "## PBO logit distribution\n\n" + diagnostic.pbo_logit_distribution + "\n",
            "## Per-config metrics\n\n"
            + _diagnostic_per_config_table(diagnostic.per_config_metrics),
            "## Walk-forward breakdown\n\n"
            + _wf_breakdown_section(diagnostic.wf_window_breakdown),
            "## Sharpe heatmap\n\n"
            + f"![sharpe heatmap](assets/{heatmap_path.name})\n",
            "## Recommendation\n\n" + diagnostic.recommendation + "\n",
        ]
        md_path = output_dir / "diagnostic.md"
        md_path.write_text("\n\n".join(s for s in sections if s))
        return md_path


def _header(
    grid: GridResult, run_time: datetime, data_source: str, verdict_pass: bool,
) -> str:
    tag = "PASS" if verdict_pass else "FAIL"
    n_trials = len(grid.trials)
    n_ok = len(grid.ok_trials)
    return (
        f"# Grid Report — `{grid.run_id}` ({tag})\n\n"
        f"- **Run:** {run_time.isoformat(timespec='minutes')}\n"
        f"- **Data source:** `{data_source}`\n"
        f"- **Total trials:** {n_trials} (ok: {n_ok}, error: {n_trials - n_ok})\n"
    )


def _gate_summary_table(verdict: GateVerdict) -> str:
    pbo_str = (
        _fmt_num(float(verdict.pbo_result.pbo), 3)
        if verdict.pbo_result is not None
        else "—"
    )
    pbo_gate_str = "pass" if verdict.pbo_pass else "reject"
    dsr_pass_count = len(verdict.dsr_pass_ids)
    wf_pass_count = len(verdict.wf_pass_ids)
    lines = [
        "| Gate | Value | Verdict |",
        "|---|---|---|",
        f"| PBO | {pbo_str} | `{pbo_gate_str}` (gate: < 0.5) |",
        f"| DSR | {dsr_pass_count}/{len(verdict.dsr_results)} configs with p < 0.05 | "
        f"`{'pass' if dsr_pass_count > 0 else 'reject'}` |",
        f"| Walk-forward | {wf_pass_count}/{len(verdict.wf_verdicts)} configs pass | "
        f"`{'pass' if wf_pass_count > 0 else 'reject'}` |",
    ]
    return "\n".join(lines) + "\n"


def _best_config_section(
    grid: GridResult, verdict: GateVerdict, wf_results: dict[int, WFResult],
) -> str:
    if verdict.best_config_id is None:
        return "_No config passed all gates._\n"
    trial = next(
        (t for t in grid.trials if t.config_id == verdict.best_config_id), None,
    )
    if trial is None or trial.result is None:
        return "_Best config unavailable._\n"
    cfg = trial.config
    wf = wf_results.get(trial.config_id)
    rows = [
        ("config_id", str(trial.config_id)),
        ("lookback_regression", str(cfg.lookback_regression)),
        ("top_pct", _fmt_pct(cfg.top_pct)),
        ("risk_factor", _fmt_num(cfg.risk_factor, 4)),
        ("Sharpe (annualized)", _fmt_num(trial.sharpe, 3)),
        ("CAGR", _fmt_pct(trial.cagr)),
        ("Max drawdown", _fmt_pct(trial.max_drawdown)),
        ("Final equity", f"${trial.result.final_equity:,.2f}"),
    ]
    if trial.config_id in verdict.dsr_results:
        dr = verdict.dsr_results[trial.config_id]
        rows.append(("DSR p-value", _fmt_num(float(dr.p_value), 4)))
    if wf is not None:
        rows.append(("Walk-forward", f"{wf.n_profitable}/{wf.n_windows} profitable"))
    md = "| Field | Value |\n|---|---|\n" + "\n".join(
        f"| {k} | {v} |" for k, v in rows
    )
    return md + "\n"


def _best_config_section_from_diag(
    diagnostic: DiagnosticReport, wf_results: dict[int, WFResult],
) -> str:
    trial = diagnostic.best_config
    if trial.result is None:
        return "_Best config unavailable (all trials errored)._\n"
    cfg = trial.config
    wf = wf_results.get(trial.config_id)
    rows = [
        ("config_id", str(trial.config_id)),
        ("lookback_regression", str(cfg.lookback_regression)),
        ("top_pct", _fmt_pct(cfg.top_pct)),
        ("risk_factor", _fmt_num(cfg.risk_factor, 4)),
        ("Sharpe (annualized)", _fmt_num(trial.sharpe, 3)),
        ("CAGR", _fmt_pct(trial.cagr)),
        ("Max drawdown", _fmt_pct(trial.max_drawdown)),
    ]
    if wf is not None:
        rows.append(("Walk-forward", f"{wf.n_profitable}/{wf.n_windows} profitable"))
    md = "| Field | Value |\n|---|---|\n" + "\n".join(
        f"| {k} | {v} |" for k, v in rows
    )
    return md + "\n"


def _failure_modes_section(diagnostic: DiagnosticReport) -> str:
    if not diagnostic.failure_modes:
        return "_No failure modes identified._\n"
    lines = []
    for mode in diagnostic.failure_modes:
        lines.append(
            f"### `{mode.label}` ({mode.severity})\n\n{mode.description}\n"
        )
    return "\n".join(lines)


def _per_config_table(
    grid: GridResult, verdict: GateVerdict, wf_results: dict[int, WFResult],
) -> str:
    rows = []
    for trial in grid.trials:
        dsr_p = (
            float(verdict.dsr_results[trial.config_id].p_value)
            if trial.config_id in verdict.dsr_results
            else float("nan")
        )
        wf = wf_results.get(trial.config_id)
        rows.append({
            "config_id": trial.config_id,
            "lookback": trial.config.lookback_regression,
            "top_pct": _fmt_pct(trial.config.top_pct),
            "risk": _fmt_num(trial.config.risk_factor, 4),
            "Sharpe": _fmt_num(trial.sharpe, 3) if trial.status == "ok" else "—",
            "CAGR": _fmt_pct(trial.cagr) if trial.status == "ok" else "—",
            "DD": _fmt_pct(trial.max_drawdown) if trial.status == "ok" else "—",
            "DSR_p": _fmt_num(dsr_p, 4) if np.isfinite(dsr_p) else "—",
            "WF": wf.verdict if wf is not None else "—",
            "status": trial.status,
        })
    df = pd.DataFrame(rows)
    return _dataframe_to_markdown(df) + "\n"


def _diagnostic_per_config_table(df: pd.DataFrame) -> str:
    """Format the DiagnosticReport.per_config_metrics DataFrame."""
    if df.empty:
        return "_(no configs)_\n"
    display = df.copy()
    for col in ("sharpe", "cagr", "max_drawdown", "dsr_pvalue"):
        if col in display.columns:
            display[col] = display[col].map(
                lambda x: _fmt_num(float(x), 3) if pd.notna(x) else "—",
            )
    return _dataframe_to_markdown(display) + "\n"


def _wf_breakdown_section(wf_results: dict[int, WFResult]) -> str:
    if not wf_results:
        return "_No walk-forward results._\n"
    rows = []
    for cid in sorted(wf_results):
        wf = wf_results[cid]
        rows.append({
            "config_id": cid,
            "n_windows": wf.n_windows,
            "n_profitable": wf.n_profitable,
            "max_dd": _fmt_pct(wf.max_drawdown),
            "verdict": wf.verdict,
        })
    return _dataframe_to_markdown(pd.DataFrame(rows)) + "\n"


def _write_sharpe_heatmap(grid: GridResult, path: Path) -> None:
    """2D heatmap: Sharpe over (lookback_regression × top_pct), risk_factor
    aggregated by max (takes the best risk_factor per cell).
    """
    rows = []
    for trial in grid.ok_trials:
        rows.append({
            "lookback": trial.config.lookback_regression,
            "top_pct": trial.config.top_pct,
            "risk": trial.config.risk_factor,
            "sharpe": trial.sharpe,
        })
    if not rows:
        # Empty placeholder so downstream ``![...](path)`` links still resolve
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.text(0.5, 0.5, "no OK trials", ha="center", va="center")
        ax.axis("off")
        fig.savefig(path, dpi=100)
        plt.close(fig)
        return

    df = pd.DataFrame(rows)
    pivot = df.pivot_table(
        index="lookback", columns="top_pct", values="sharpe", aggfunc="max",
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    im = ax.imshow(pivot.values, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{c:.2f}" for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([str(i) for i in pivot.index])
    ax.set_xlabel("top_pct")
    ax.set_ylabel("lookback_regression")
    ax.set_title("Max Sharpe across risk_factor")
    fig.colorbar(im, ax=ax, label="Sharpe")
    for i, lb in enumerate(pivot.index):
        for j, tp in enumerate(pivot.columns):
            val = pivot.values[i, j]
            if np.isfinite(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="white")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _write_equity_chart(equity: pd.Series, path: Path) -> None:
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
    fig.savefig(path, dpi=120)
    plt.close(fig)
