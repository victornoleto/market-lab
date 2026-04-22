"""Phase D-MVP orchestrator — iterate the D1+D4 grid, compute gates, decide.

Runs the full MVP grid (24 D1 + 18 D4 = 42 configs), each over IS/OOS/FWD
splits, applying the BR cost + R$20k-conditional tax model. Computes the
**MVP gates** (not the full 13 Fase D-gate set):

* PBO via CSCV on the per-config daily returns matrix (OOS window).
  ``[advances_fin_ml, p.208-211]``.
* DSR with ``N_trials`` = total grid size = 42. ``[advances_fin_ml, p.275]``.
* OOS Sharpe, CAGR, MDD per config (tier classification per mandate
  §2.2 / §2.3).

Emits ``reports/phase_d_mvp/SUMMARY.md`` with:

* Per-config table (lead, config params, OOS Sharpe/CAGR/MDD, DSR p-value,
  tier classifications).
* Aggregate PBO value and pass/fail.
* Early-abort flag: ``TRUE`` when **zero configs** satisfy
  ``PBO < 0.5 AND DSR p < 0.1`` — signals that Fase D-ampliada (Fundamentus
  scrape + D2/D3/combos) is not worth pursuing under this OHLCV-only grid.

Usage
-----
::

    .venv/bin/python -m scripts.phase_d_mvp.orchestrator \
        [--initial-cash 50000] [--skip-existing]

The orchestrator iterates sequentially on a single process (the Runner's
hot loop is CPU-bound but each config is ~1-3 min on a modern laptop; 42
× 3 splits ≈ 2-3 hours total). Use ``--skip-existing`` to resume after a
partial run.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ai_trade.backtest.metrics.performance import returns_from_equity
from ai_trade.backtest.validation.dsr import dsr
from ai_trade.backtest.validation.pbo import pbo as pbo_cscv

from scripts.phase_d_mvp.run_single import (
    SPLITS,
    SplitMetrics,
    _config_slug,
    load_ohlcv,
    run_split,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_REPORTS_DIR = _PROJECT_ROOT / "reports" / "phase_d_mvp"

log = logging.getLogger("phase_d_mvp.orchestrator")


# ---------------------------------------------------------------------------
# Grid definitions (42 configs total)
# ---------------------------------------------------------------------------
def d1_grid() -> list[dict]:
    """D1 Clenow momentum grid: lookback × n_top × sector_cap = 2×4×3 = 24."""
    configs = []
    for lookback, n_top, cap in product(
        [90, 180],
        [15, 20, 25, 30],
        [0.20, 0.25, 0.30],
    ):
        configs.append({
            "lookback": lookback,
            "n_top": n_top,
            "sector_cap_pct": cap,
        })
    return configs


def d4_grid() -> list[dict]:
    """D4 Low-vol + Mom grid: pre_n × n_top × vol_lookback = 3×3×2 = 18."""
    configs = []
    for pre_n, n_top, vol_lk in product(
        [30, 40, 50],
        [15, 20, 25],
        [60, 90],
    ):
        if n_top > pre_n:  # nonsense — skip
            continue
        configs.append({
            "pre_n": pre_n,
            "n_top": n_top,
            "vol_lookback": vol_lk,
        })
    return configs


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
@dataclass
class GridRecord:
    lead: str
    config: dict
    slug: str
    is_metrics: SplitMetrics | None
    oos_metrics: SplitMetrics | None
    fwd_metrics: SplitMetrics | None
    oos_daily_returns: np.ndarray | None  # for PBO matrix

    @property
    def config_str(self) -> str:
        return ", ".join(f"{k}={v}" for k, v in sorted(self.config.items()))


def _run_one_config(
    lead: str,
    config: dict,
    initial_cash: float,
    skip_existing: bool,
    output_dir: Path,
) -> GridRecord:
    slug = f"{lead.lower()}_{_config_slug(config)}"
    out_dir = output_dir / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    def _get_split(split: str) -> SplitMetrics | None:
        json_path = out_dir / f"{split}.json"
        equity_path = out_dir / f"{split}_equity.parquet"
        if skip_existing and json_path.exists() and equity_path.exists():
            log.info("skip-existing hit: %s", json_path)
            with open(json_path) as f:
                return SplitMetrics(**json.load(f))
        try:
            metrics = run_split(
                lead, dict(config), split, initial_cash,
                persist_equity_to=equity_path,
            )
        except Exception:
            log.exception("run_split failed for %s %s %s", lead, slug, split)
            return None
        with open(json_path, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2, default=str)
        return metrics

    is_m = _get_split("IS")
    oos_m = _get_split("OOS")
    fwd_m = _get_split("FWD")

    # Capture OOS daily returns for PBO matrix
    oos_rets: np.ndarray | None = None
    oos_equity_path = out_dir / "OOS_equity.parquet"
    if oos_m is not None and oos_equity_path.exists():
        eq = pd.read_parquet(oos_equity_path)["equity"]
        oos_rets = returns_from_equity(eq).to_numpy()

    return GridRecord(
        lead=lead,
        config=config,
        slug=slug,
        is_metrics=is_m,
        oos_metrics=oos_m,
        fwd_metrics=fwd_m,
        oos_daily_returns=oos_rets,
    )


def _collect_oos_matrix(records: list[GridRecord]) -> tuple[np.ndarray | None, list[str]]:
    """Build ``(T, N)`` matrix of aligned OOS daily returns across configs.

    Returns ``(None, [])`` if no common alignment is possible (missing data).
    """
    valid = [r for r in records if r.oos_daily_returns is not None and r.oos_daily_returns.size > 0]
    if not valid:
        return None, []

    # All configs share the same OOS window and same data — equity curves
    # should have the same length. If not, truncate to the shortest.
    lengths = [r.oos_daily_returns.size for r in valid]
    T = min(lengths)
    matrix = np.column_stack([r.oos_daily_returns[:T] for r in valid])
    return matrix, [r.slug for r in valid]


def _classify_cagr_b(cagr_value: float) -> str:
    """Strategy D tier classification (same as B, mandate §2.2)."""
    if cagr_value < 0.11:
        return "Folclore"
    if cagr_value < 0.17:
        return "Marginal"
    if cagr_value < 0.25:
        return "Válido"
    if cagr_value < 0.40:
        return "Forte"
    return "Extraordinário"


def _classify_mdd_b(mdd_value: float) -> str:
    """Strategy D tier for MDD (same shape as B, mandate §2.3)."""
    if mdd_value <= 0.15:
        return "Excelente"
    if mdd_value <= 0.25:
        return "Válido"
    if mdd_value <= 0.35:
        return "Marginal"
    if mdd_value <= 0.50:
        return "Forte warning"
    return "Reject"


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------
def write_summary(
    records: list[GridRecord],
    pbo_result: Any,
    dsr_results: dict[str, Any],
    output_path: Path,
    initial_cash: float,
    early_abort: bool,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"# Phase D-MVP — Strategy D grid report ({ts})\n")
    lines.append("")
    lines.append(f"Initial cash: R${initial_cash:,.0f}\n")
    lines.append(f"Configs run: {len(records)} "
                 f"({sum(1 for r in records if r.lead == 'D1')} D1 + "
                 f"{sum(1 for r in records if r.lead == 'D4')} D4)\n")
    lines.append(f"OOS window: {SPLITS['OOS'][0]} → {SPLITS['OOS'][1]}\n\n")

    # Aggregate PBO
    if pbo_result is not None:
        lines.append("## Aggregate PBO (OOS daily returns, CSCV)\n")
        lines.append(f"- **PBO = {pbo_result.pbo:.3f}** "
                     f"(threshold < 0.5 per `[advances_fin_ml, p.208-211]`)")
        lines.append(f"- n_blocks = {pbo_result.n_blocks}, "
                     f"n_combinations = {pbo_result.n_combinations}")
        verdict = "**PASS**" if pbo_result.pbo < 0.5 else "**FAIL**"
        lines.append(f"- Verdict: {verdict}\n\n")
    else:
        lines.append("## Aggregate PBO\n- N/A — insufficient OOS data for CSCV\n\n")

    # Early abort flag
    lines.append("## Early-abort decision\n")
    if early_abort:
        lines.append("🛑 **ABORT Fase D-ampliada.** Zero configs satisfy "
                     "`PBO<0.5 AND DSR p<0.1`. No justification for investing "
                     "in Fundamentus scraping or implementing D2/D3/combos.")
        lines.append("")
        lines.append("Recommended next: write "
                     "`reports/phase_d_mvp/BREADTH_NO_WINNER_D.md` with root cause "
                     "analysis (similar to Phase 3.6/3.7-3/3.8-1 closures) and "
                     "escalate to user for pivot (R1-R5 style).\n\n")
    else:
        n_pass = sum(
            1 for r in records
            if r.oos_metrics is not None
            and dsr_results.get(r.slug, {}).get("p_value", 1.0) < 0.1
            and pbo_result is not None
            and pbo_result.pbo < 0.5
        )
        lines.append(f"✅ **Proceed to Fase D-ampliada.** {n_pass} config(s) "
                     f"satisfy the minimum (PBO < 0.5 and DSR p < 0.1).\n\n")

    # Per-config table
    lines.append("## Per-config results (OOS)\n\n")
    lines.append("| Lead | Config | Sharpe | CAGR | MDD | Tier CAGR | Tier MDD | DSR p | n trades | Tax hits |")
    lines.append("|------|--------|--------|------|-----|-----------|----------|-------|----------|----------|")
    for r in records:
        m = r.oos_metrics
        if m is None:
            lines.append(f"| {r.lead} | {r.config_str} | ERR | — | — | — | — | — | — | — |")
            continue
        dsr_p = dsr_results.get(r.slug, {}).get("p_value", float("nan"))
        lines.append(
            f"| {r.lead} | {r.config_str} | "
            f"{m.sharpe_net:.3f} | {m.cagr_net:.2%} | {m.mdd_net:.2%} | "
            f"{_classify_cagr_b(m.cagr_net)} | {_classify_mdd_b(m.mdd_net)} | "
            f"{dsr_p:.3f} | {m.n_trades} | {m.monthly_tax_hits} |"
        )
    lines.append("")

    # Citations footer
    lines.append("\n## Citations\n")
    lines.append("- PBO < 0.5 (CSCV): `[advances_fin_ml, p.208-211]`")
    lines.append("- DSR deflator: `[advances_fin_ml, p.275]`")
    lines.append("- D1 Clenow adjusted slope, SMA100, gap 15%: "
                 "`[stocks_on_the_move, p.76-77, p.81-82, p.82]`")
    lines.append("- Position inertia 10%: `[systematic_trading, p.174]`")
    lines.append("- Tier framework (warning-only): "
                 "`docs/investment-mandate.md §2.2, §2.3, §4b`")
    lines.append("")

    output_path.write_text("\n".join(lines))
    log.info("summary written: %s", output_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initial-cash", type=float, default=50_000.0)
    parser.add_argument("--skip-existing", action="store_true",
                        help="Reuse existing JSON per-split reports from disk.")
    parser.add_argument("--output-dir", type=Path, default=_REPORTS_DIR)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the grid and exit; don't run backtests.")
    parser.add_argument("--leads", nargs="*", default=["D1", "D4"],
                        choices=["D1", "D4"],
                        help="Restrict to a subset of leads.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )

    grid: list[tuple[str, dict]] = []
    if "D1" in args.leads:
        grid.extend(("D1", c) for c in d1_grid())
    if "D4" in args.leads:
        grid.extend(("D4", c) for c in d4_grid())

    log.info("grid size: %d configs (leads=%s)", len(grid), args.leads)
    if args.dry_run:
        for lead, config in grid:
            print(f"{lead}: {config}")
        return 0

    records: list[GridRecord] = []
    for i, (lead, config) in enumerate(grid, start=1):
        log.info("=" * 72)
        log.info("[%d/%d] %s %s", i, len(grid), lead, config)
        record = _run_one_config(
            lead, config, args.initial_cash, args.skip_existing, args.output_dir
        )
        records.append(record)

    # PBO on OOS daily returns
    matrix, slugs = _collect_oos_matrix(records)
    pbo_result = None
    if matrix is not None and matrix.shape[1] >= 4:
        try:
            pbo_result = pbo_cscv(matrix, n_blocks=10)
            log.info("PBO (OOS) = %.3f over %d configs",
                     pbo_result.pbo, matrix.shape[1])
        except Exception:
            log.exception("PBO computation failed")

    # DSR per-config (N_trials = total grid size, Bonferroni-like deflator)
    dsr_results: dict[str, dict] = {}
    n_trials = len(records)
    for record in records:
        if record.oos_daily_returns is None or record.oos_daily_returns.size < 30:
            continue
        try:
            result = dsr(record.oos_daily_returns, n_trials=n_trials)
            dsr_results[record.slug] = {
                "dsr": float(result.dsr),
                "p_value": float(result.p_value),
                "observed_sharpe": float(result.observed_sharpe),
                "benchmark_sharpe": float(result.benchmark_sharpe),
                "n_trials": int(result.n_trials),
            }
        except Exception:
            log.exception("DSR failed for %s", record.slug)

    # Early abort decision
    early_abort = True
    if pbo_result is not None and pbo_result.pbo < 0.5:
        for record in records:
            p = dsr_results.get(record.slug, {}).get("p_value", 1.0)
            if p < 0.1:
                early_abort = False
                break

    # Write summary
    summary_path = args.output_dir / "SUMMARY.md"
    write_summary(records, pbo_result, dsr_results, summary_path,
                  args.initial_cash, early_abort)

    # Persist PBO matrix + DSR for downstream analysis
    if matrix is not None:
        np.savez(
            args.output_dir / "oos_returns_matrix.npz",
            matrix=matrix, slugs=np.array(slugs),
        )
    with open(args.output_dir / "dsr_results.json", "w") as f:
        json.dump(dsr_results, f, indent=2)

    log.info("orchestrator done (early_abort=%s)", early_abort)
    return 2 if early_abort else 0


if __name__ == "__main__":
    raise SystemExit(main())
