#!/usr/bin/env python3
"""Run the Ehlers Band-Pass Swing grid (Fase 2.5 Execução 2) with active gates.

Orchestrates the end-to-end pipeline for a single-instrument Ehlers
swing-trader grid on ``^GSPC`` (index price):

1. Fetch ``^GSPC`` OHLCV from yfinance (cached on first cold run).
2. Build 24 Ehlers configs (2 × 2 × 3 × 2 cartesian product of
   hp_period, lp_period, pct_of_dcp, stop_pct). ``--dry-run`` restricts
   to the first 3 for smoke testing.
3. Execute the grid in parallel via :class:`GridRunner` with checkpoint
   resume (mid-run crash → re-run picks up where it stopped).
4. Run walk-forward per config (8 windows each).
5. Apply :class:`GateEvaluator` against the 3 rules (PBO < 0.5 &
   DSR p-value < 0.05 & walk-forward ≥ 6/8).
6. If gates pass: :meth:`write_pass_report`. Otherwise: analyze failure
   mode via :class:`DiagnosticAnalyzer` and :meth:`write_fail_report`.

Typical invocation (production run, 9 years):

    .venv/bin/python scripts/run_grid_ehlers.py \\
        --start 2015-01-01 --end 2023-12-31 \\
        --cash 100000 \\
        --output-dir reports/

Dry-run (fast smoke):

    .venv/bin/python scripts/run_grid_ehlers.py \\
        --start 2022-01-01 --end 2023-12-31 \\
        --dry-run --output-dir /tmp/grid_smoke

Logs: unified append-only log at ``logs/grid.log`` (single ``tail -f``
for every run, past and future — shared with Clenow Execução 1 for
cross-strategy comparison). Per-run detail under
``.cache/grid_runs/{run_id}/``.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from tqdm import tqdm


log = logging.getLogger("ai_trade.grid.ehlers")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Ehlers Band-Pass Swing grid with active anti-overfit gates.",
    )
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument(
        "--run-id",
        default=None,
        help="Defaults to grid_ehlers_<YYYYMMDD-HHMM>. Resume a prior run by "
        "reusing its run_id.",
    )
    ap.add_argument(
        "--n-jobs", type=int, default=-1,
        help="-1 = all cores (default); 1 = sequential",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Limit grid to first 3 configs for smoke testing.",
    )
    ap.add_argument(
        "--symbol", default="^GSPC",
        help="Yahoo ticker to trade (default: ^GSPC).",
    )
    ap.add_argument(
        "--warmup-days", type=int, default=500,
        help="Calendar days of history before --start (default: 500).",
    )
    ap.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.yfinance_source import YFinanceSource
    from ai_trade.backtest.engine import (
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.grid import (
        DiagnosticAnalyzer,
        EhlersGridConfig,
        GateEvaluator,
        GridReportGenerator,
        GridRunner,
        JsonlTrialObserver,
        StatusFileObserver,
        compose_observers,
        ehlers_grid_configs,
        setup_grid_logging,
        wf_for_grid,
    )
    from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

    args = _parse_args(argv)
    run_id = args.run_id or f"grid_ehlers_{datetime.now().strftime('%Y%m%d-%H%M')}"
    output_dir = args.output_dir / run_id
    checkpoint_dir = Path(".cache/grid_runs")
    run_checkpoint_dir = checkpoint_dir / run_id
    run_checkpoint_dir.mkdir(parents=True, exist_ok=True)
    unified_log_path = Path("logs/grid.log")

    level = getattr(logging, args.log_level)
    setup_grid_logging(
        run_id=run_id,
        run_dir=run_checkpoint_dir,
        unified_log_path=unified_log_path,
        level=level,
    )

    log.info("=== grid run %s ===", run_id)
    log.info(
        "start=%s end=%s cash=$%.0f n_jobs=%d dry_run=%s symbol=%s",
        args.start, args.end, args.cash, args.n_jobs, args.dry_run, args.symbol,
    )

    configs = ehlers_grid_configs()
    if args.dry_run:
        configs = configs[:3]
        log.info("DRY RUN: limited to %d configs", len(configs))

    fetch_start = args.start - timedelta(days=args.warmup_days)
    log.info("Fetching %s %s → %s", args.symbol, fetch_start, args.end)
    src = YFinanceSource()
    raw = src.fetch_many([args.symbol], fetch_start, args.end)
    if args.symbol not in raw or raw[args.symbol].empty:
        log.error("No data for %s — abort", args.symbol)
        return 1
    data = {args.symbol: raw[args.symbol]}

    data_bounded = {
        args.symbol: data[args.symbol].loc[
            pd.Timestamp(args.start) : pd.Timestamp(args.end)
        ]
    }
    if data_bounded[args.symbol].empty:
        log.error("Bounded range [%s, %s] is empty", args.start, args.end)
        return 1
    log.info(
        "Data ready: %d bars in [%s, %s]",
        len(data_bounded[args.symbol]),
        args.start,
        args.end,
    )

    def trial_fn(cfg: EhlersGridConfig):
        """Build an Ehlers strategy with the grid config; run through Runner.

        The strategy precomputes indicators over the full ``data`` series
        (which includes the --warmup-days lead-in), then the Runner iterates
        only the bounded slice [start, end].
        """
        strategy = EhlersBPSwingStrategy(
            data=data,
            symbol=args.symbol,
            hp_period=cfg.hp_period,
            lp_period=cfg.lp_period,
            pct_of_dcp=cfg.pct_of_dcp,
            stop_pct=cfg.stop_pct,
            upper_threshold=cfg.upper_threshold,
            lower_threshold=cfg.lower_threshold,
            agc_decay=cfg.agc_decay,
            risk_pct_of_equity=cfg.risk_pct_of_equity,
            period_min=cfg.period_min,
            period_max=cfg.period_max,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        return runner.run(
            strategy=strategy, data=data_bounded, initial_cash=args.cash,
        )

    pbar = tqdm(total=len(configs), desc=f"grid {run_id}", unit="cfg")

    def tqdm_observer(completed: int, total: int, trial) -> None:
        pbar.update(1)
        pbar.set_postfix({
            "cfg_id": trial.config_id,
            "status": trial.status,
            "sharpe": (
                f"{trial.sharpe:.2f}" if trial.status == "ok" else "—"
            ),
        })

    observer = compose_observers(
        JsonlTrialObserver(
            path=run_checkpoint_dir / "trials.jsonl", run_id=run_id,
        ),
        StatusFileObserver(
            path=run_checkpoint_dir / "status.md", run_id=run_id,
        ),
        StatusFileObserver(
            path=Path("logs/grid_latest_status.md"), run_id=run_id,
        ),
        tqdm_observer,
    )

    grid = GridRunner(
        checkpoint_dir=checkpoint_dir,
        n_jobs=args.n_jobs,
        config_cls=EhlersGridConfig,
    ).run(
        configs=configs, trial_fn=trial_fn, run_id=run_id,
        progress_cb=observer,
    )
    pbar.close()

    log.info(
        "Grid complete: %d/%d OK (%d errors)",
        len(grid.ok_trials), len(grid.trials),
        len(grid.trials) - len(grid.ok_trials),
    )

    log.info("Running walk-forward per config (n_windows=8)")
    wf_results = wf_for_grid(grid, n_windows=8, n_jobs=args.n_jobs)

    log.info("Evaluating gates (PBO, DSR, walk-forward)")
    verdict = GateEvaluator().evaluate(
        grid=grid,
        wf_verdicts={cid: wf.verdict for cid, wf in wf_results.items()},
    )
    pbo_val = (
        float(verdict.pbo_result.pbo) if verdict.pbo_result else float("nan")
    )
    log.info(
        "Gate verdict: overall_pass=%s best_config_id=%s "
        "pbo=%.3f dsr_pass=%d/%d wf_pass=%d/%d",
        verdict.overall_pass, verdict.best_config_id,
        pbo_val,
        len(verdict.dsr_pass_ids), len(verdict.dsr_results),
        len(verdict.wf_pass_ids), len(verdict.wf_verdicts),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    report_gen = GridReportGenerator()

    if verdict.overall_pass:
        path = report_gen.write_pass_report(
            grid=grid, verdict=verdict, wf_results=wf_results,
            output_dir=output_dir, data_source="yfinance",
        )
        log.info("PASS report: %s", path)
    else:
        diagnostic = DiagnosticAnalyzer().analyze(
            grid=grid, verdict=verdict, wf_results=wf_results,
        )
        path = report_gen.write_fail_report(
            grid=grid, verdict=verdict, wf_results=wf_results,
            diagnostic=diagnostic,
            output_dir=output_dir, data_source="yfinance",
        )
        log.info("FAIL diagnostic report: %s", path)
        log.info(
            "Failure modes: %s",
            [m.label for m in diagnostic.failure_modes],
        )

    log.info("=== grid run %s done ===", run_id)
    return 0 if verdict.overall_pass else 2


if __name__ == "__main__":
    sys.exit(main())
