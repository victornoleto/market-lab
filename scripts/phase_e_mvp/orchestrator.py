"""Strategy E orchestrator — preloaded data + grid × splits loop.

Key optimization vs Phase D: :func:`load_data_once` reads the multi-market
OHLCV from yfinance cache **once** at the start. Every config run then
consumes the in-memory dict — zero disk reads in the hot loop.

Same 42 configs (24 D1 + 18 D4), same 3 splits (IS/OOS/FWD). Writes
per-config JSONs + equity parquets under ``reports/phase_e_mvp/<slug>/``.
Aggregates PBO + DSR (N_trials=42) + SUMMARY.md with tier classifications.
Early-abort when zero configs satisfy ``PBO < 0.5 AND DSR p < 0.1``.

Usage::

    .venv/bin/python -m scripts.phase_e_mvp.orchestrator \
        [--initial-cash 50000] [--skip-existing] [--leads D1] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ai_trade.backtest.data.yfinance_source import YFinanceSource
from ai_trade.backtest.metrics.performance import returns_from_equity
from ai_trade.backtest.validation.dsr import dsr
from ai_trade.backtest.validation.pbo import pbo as pbo_cscv

from scripts.phase_e_mvp.run_engine import (
    SPLITS,
    SplitMetricsE,
    run_config_split,
)
from scripts.phase_e_mvp.universe import MULTIMARKET_TICKERS, market_of

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_REPORTS_DIR = _PROJECT_ROOT / "reports" / "phase_e_mvp"

log = logging.getLogger("phase_e_mvp.orchestrator")


# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------
def d1_grid() -> list[dict]:
    return [
        {"lookback": lb, "n_top": n, "sector_cap_pct": cap}
        for lb, n, cap in product([90, 180], [15, 20, 25, 30], [0.20, 0.25, 0.30])
    ]


def d4_grid() -> list[dict]:
    return [
        {"pre_n": p, "n_top": n, "vol_lookback": v}
        for p, n, v in product([30, 40, 50], [15, 20, 25], [60, 90])
        if n <= p
    ]


# ---------------------------------------------------------------------------
# Pre-load data once
# ---------------------------------------------------------------------------
def load_data_once(
    start: date, end: date, warmup_days: int = 240,
    tickers: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """Read OHLCV for the multi-market universe into memory.

    Called once per orchestrator invocation. The returned dict is passed
    by reference to every config; each strategy reads but does not
    mutate, so sharing is safe.
    """
    src = YFinanceSource()
    load_start = pd.Timestamp(start) - pd.Timedelta(days=warmup_days * 2)
    out: dict[str, pd.DataFrame] = {}
    tickers = tickers or MULTIMARKET_TICKERS
    for ticker in tickers:
        try:
            df = src.fetch(ticker, load_start.date(), end)
        except Exception:
            continue
        if df.empty or "close" not in df.columns:
            continue
        out[ticker] = df
    us_n = sum(1 for t in out if market_of(t) == "US")
    br_n = sum(1 for t in out if market_of(t) == "BR")
    log.info("loaded %d tickers into memory (US=%d BR=%d)", len(out), us_n, br_n)
    return out


# ---------------------------------------------------------------------------
# Config slug + record
# ---------------------------------------------------------------------------
def _config_slug(config: dict) -> str:
    parts = [f"{k}{v}" for k, v in sorted(config.items())]
    return "_".join(parts).replace(".", "p").replace("=", "").replace(",", "")


@dataclass
class GridRecordE:
    lead: str
    config: dict
    slug: str
    is_metrics: SplitMetricsE | None
    oos_metrics: SplitMetricsE | None
    fwd_metrics: SplitMetricsE | None
    oos_daily_returns: np.ndarray | None


def _run_one_config(
    lead: str, config: dict, data: dict[str, pd.DataFrame],
    initial_cash: float, skip_existing: bool, output_dir: Path,
) -> GridRecordE:
    slug = f"{lead.lower()}_{_config_slug(config)}"
    out_dir = output_dir / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    def _get_split(split: str) -> SplitMetricsE | None:
        json_path = out_dir / f"{split}.json"
        equity_path = out_dir / f"{split}_equity.parquet"
        if skip_existing and json_path.exists() and equity_path.exists():
            log.info("skip-existing hit: %s", json_path)
            with open(json_path) as f:
                return SplitMetricsE(**json.load(f))
        try:
            metrics = run_config_split(
                lead, config, split, data, initial_cash,
                persist_equity_to=equity_path,
            )
        except Exception:
            log.exception("run_config_split failed: %s %s %s", lead, slug, split)
            return None
        with open(json_path, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2, default=str)
        return metrics

    is_m = _get_split("IS")
    oos_m = _get_split("OOS")
    fwd_m = _get_split("FWD")

    oos_rets: np.ndarray | None = None
    oos_equity_path = out_dir / "OOS_equity.parquet"
    if oos_m is not None and oos_equity_path.exists():
        eq = pd.read_parquet(oos_equity_path)["equity"]
        oos_rets = returns_from_equity(eq).to_numpy()

    return GridRecordE(
        lead=lead, config=config, slug=slug,
        is_metrics=is_m, oos_metrics=oos_m, fwd_metrics=fwd_m,
        oos_daily_returns=oos_rets,
    )


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------
def _collect_oos_matrix(records: list[GridRecordE]):
    valid = [r for r in records if r.oos_daily_returns is not None and r.oos_daily_returns.size > 0]
    if not valid:
        return None, []
    T = min(r.oos_daily_returns.size for r in valid)
    matrix = np.column_stack([r.oos_daily_returns[:T] for r in valid])
    return matrix, [r.slug for r in valid]


def _classify_cagr(cagr_v: float) -> str:
    if cagr_v < 0.11: return "Folclore"
    if cagr_v < 0.17: return "Marginal"
    if cagr_v < 0.25: return "Válido"
    if cagr_v < 0.40: return "Forte"
    return "Extraordinário"


def _classify_mdd(mdd_v: float) -> str:
    if mdd_v <= 0.15: return "Excelente"
    if mdd_v <= 0.25: return "Válido"
    if mdd_v <= 0.35: return "Marginal"
    if mdd_v <= 0.50: return "Forte warning"
    return "Reject"


def write_summary(
    records: list[GridRecordE], pbo_result: Any,
    dsr_results: dict[str, Any], output_path: Path,
    initial_cash: float, early_abort: bool,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Phase E-MVP — Strategy E (multi-market) grid report ({ts})",
        "",
        f"Initial cash: R${initial_cash:,.0f}",
        f"Configs run: {len(records)} "
        f"({sum(1 for r in records if r.lead == 'D1')} D1 + "
        f"{sum(1 for r in records if r.lead == 'D4')} D4)",
        f"OOS window: {SPLITS['OOS'][0]} → {SPLITS['OOS'][1]}",
        f"Universe: SP500 top-200 + IBrX-100 (~300 tickers combined)",
        "",
    ]

    if pbo_result is not None:
        verdict = "**PASS**" if pbo_result.pbo < 0.5 else "**FAIL**"
        lines.append(
            f"## Aggregate PBO: {pbo_result.pbo:.3f} "
            f"(threshold < 0.5 per `[advances_fin_ml, p.208-211]`) → {verdict}"
        )
        lines.append(
            f"- n_blocks={pbo_result.n_blocks}, "
            f"n_combinations={pbo_result.n_combinations}"
        )
    else:
        lines.append("## Aggregate PBO: N/A")
    lines.append("")

    lines.append("## Early-abort decision")
    if early_abort:
        lines.extend([
            "🛑 **ABORT.** Zero configs satisfy `PBO<0.5 AND DSR p<0.1`.",
            "See `jornada/YYYY-MM-DD-phase-e-mvp-no-winner.md` for R1-R5.",
            "",
        ])
    else:
        n_pass = sum(
            1 for r in records
            if r.oos_metrics is not None
            and dsr_results.get(r.slug, {}).get("p_value", 1.0) < 0.1
            and pbo_result is not None and pbo_result.pbo < 0.5
        )
        lines.extend([
            f"✅ **Proceed.** {n_pass} config(s) pass the joint minimum "
            "(PBO<0.5, DSR p<0.1).",
            "",
        ])

    lines.extend([
        "## Per-config results (OOS, sorted by Sharpe)",
        "",
        "| Lead | Config | OOS Sharpe | OOS CAGR | OOS MDD | Tier CAGR | "
        "Tier MDD | DSR p | Trades (BR/US) | Tax R$ |",
        "|------|--------|------------|----------|---------|-----------|"
        "----------|-------|----------------|--------|",
    ])
    sorted_records = sorted(
        records,
        key=lambda r: r.oos_metrics.sharpe_net if r.oos_metrics else -99,
        reverse=True,
    )
    for r in sorted_records:
        m = r.oos_metrics
        cfg = ", ".join(f"{k}={v}" for k, v in sorted(r.config.items()))
        if m is None:
            lines.append(f"| {r.lead} | {cfg} | ERR | — | — | — | — | — | — | — |")
            continue
        dsr_p = dsr_results.get(r.slug, {}).get("p_value", float("nan"))
        lines.append(
            f"| {r.lead} | {cfg} | "
            f"{m.sharpe_net:+.3f} | {m.cagr_net:+.2%} | {m.mdd_net:.2%} | "
            f"{_classify_cagr(m.cagr_net)} | {_classify_mdd(m.mdd_net)} | "
            f"{dsr_p:.3f} | {m.n_trades} ({m.n_trades_br}/{m.n_trades_us}) | "
            f"R${m.tax_total_brl:,.0f} |"
        )
    lines.extend([
        "",
        "## Citations",
        "- PBO: `[advances_fin_ml, p.208-211]`",
        "- DSR deflator: `[advances_fin_ml, p.275]`",
        "- Clenow: `[stocks_on_the_move, p.76-77]`",
        "- Mandate: `docs/investment-mandate.md §4b` + "
        "`docs/mandate_overrides/2026-04-23-strategy-e-multimarket.md`",
        "",
    ])
    output_path.write_text("\n".join(lines))
    log.info("summary written: %s", output_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initial-cash", type=float, default=50_000.0)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=_REPORTS_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--leads", nargs="*", default=["D1", "D4"],
                        choices=["D1", "D4"])
    parser.add_argument("--data-start", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                        default=date(2010, 1, 1))
    parser.add_argument("--data-end", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                        default=date(2026, 4, 15))
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO, stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
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

    # Pre-load data ONCE — this is the key optimization.
    log.info("preloading OHLCV for %d tickers...", len(MULTIMARKET_TICKERS))
    data = load_data_once(args.data_start, args.data_end)
    if len(data) < 100:
        log.error("only %d tickers loaded; aborting", len(data))
        return 1

    records: list[GridRecordE] = []
    for i, (lead, config) in enumerate(grid, start=1):
        log.info("=" * 72)
        log.info("[%d/%d] %s %s", i, len(grid), lead, config)
        rec = _run_one_config(
            lead, config, data, args.initial_cash,
            args.skip_existing, args.output_dir,
        )
        records.append(rec)

    # Gates
    matrix, slugs = _collect_oos_matrix(records)
    pbo_result = None
    if matrix is not None and matrix.shape[1] >= 4:
        try:
            pbo_result = pbo_cscv(matrix, n_blocks=10)
            log.info("PBO (OOS) = %.3f over %d configs",
                     pbo_result.pbo, matrix.shape[1])
        except Exception:
            log.exception("PBO failed")

    dsr_results: dict[str, dict] = {}
    n_trials = len(records)
    for rec in records:
        if rec.oos_daily_returns is None or rec.oos_daily_returns.size < 30:
            continue
        try:
            r = dsr(rec.oos_daily_returns, n_trials=n_trials)
            dsr_results[rec.slug] = {
                "dsr": float(r.dsr), "p_value": float(r.p_value),
                "observed_sharpe": float(r.observed_sharpe),
                "benchmark_sharpe": float(r.benchmark_sharpe),
                "n_trials": int(r.n_trials),
            }
        except Exception:
            log.exception("DSR failed for %s", rec.slug)

    early_abort = True
    if pbo_result is not None and pbo_result.pbo < 0.5:
        for rec in records:
            if dsr_results.get(rec.slug, {}).get("p_value", 1.0) < 0.1:
                early_abort = False
                break

    summary_path = args.output_dir / "SUMMARY.md"
    write_summary(records, pbo_result, dsr_results, summary_path,
                  args.initial_cash, early_abort)

    if matrix is not None:
        np.savez(args.output_dir / "oos_returns_matrix.npz",
                 matrix=matrix, slugs=np.array(slugs))
    with open(args.output_dir / "dsr_results.json", "w") as f:
        json.dump(dsr_results, f, indent=2)

    log.info("orchestrator done (early_abort=%s)", early_abort)
    return 2 if early_abort else 0


if __name__ == "__main__":
    raise SystemExit(main())
