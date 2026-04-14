#!/usr/bin/env python3
"""Run the Clenow momentum grid (Fase 2.5 / 3) with active gates.

Orchestrates the end-to-end pipeline:

1. Fetch SPX 500 OHLCV (yfinance) + point-in-time Wikipedia constituents.
   Cached on first cold run (~40 min first time, ~10 s warm).
2. Build 30 Clenow configs (cartesian product of lookback_regression,
   top_pct, risk_factor). ``--dry-run`` restricts to 3 for smoke testing.
3. Execute the grid in parallel via :class:`GridRunner` with checkpoint
   resume (mid-run crash → re-run picks up where it stopped).
4. Run walk-forward per config (8 windows each).
5. Apply :class:`GateEvaluator` against the 3 rules (PBO < 0.5 &
   DSR p-value < 0.05 & walk-forward ≥ 6/8).
6. If gates pass: :meth:`write_pass_report`. Otherwise: analyze failure
   mode via :class:`DiagnosticAnalyzer` and :meth:`write_fail_report`.

Typical invocation (production run, 9 years):

    .venv/bin/python scripts/run_grid_clenow.py \\
        --start 2015-01-01 --end 2023-12-31 \\
        --cash 100000 \\
        --output-dir reports/

Dry-run (fast smoke):

    .venv/bin/python scripts/run_grid_clenow.py \\
        --start 2022-01-01 --end 2023-12-31 \\
        --dry-run --output-dir /tmp/grid_smoke

Logs: unified append-only log at ``logs/grid.log`` (single ``tail -f`` for
every run, past and future). Per-run detail under
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


log = logging.getLogger("ai_trade.grid")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Clenow momentum grid with active anti-overfit gates.",
    )
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument(
        "--run-id",
        default=None,
        help="Defaults to grid_<YYYYMMDD-HHMM>. Resume a prior run by reusing "
        "its run_id.",
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
        "--index-symbol", default="^GSPC",
        help="Yahoo ticker for the regime filter (default: ^GSPC).",
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
    from ai_trade.backtest.data.wikipedia_spx import WikipediaSPX
    from ai_trade.backtest.data.yfinance_source import YFinanceSource
    from ai_trade.backtest.engine import (
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.grid import (
        DiagnosticAnalyzer,
        GateEvaluator,
        GridReportGenerator,
        GridRunner,
        JsonlTrialObserver,
        StatusFileObserver,
        compose_observers,
        grid_configs,
        setup_grid_logging,
        wf_for_grid,
    )
    from ai_trade.backtest.strategies.clenow_momentum import (
        ClenowMomentumStrategy,
    )

    args = _parse_args(argv)
    run_id = args.run_id or f"grid_{datetime.now().strftime('%Y%m%d-%H%M')}"
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
    log.info("start=%s end=%s cash=$%.0f n_jobs=%d dry_run=%s",
             args.start, args.end, args.cash, args.n_jobs, args.dry_run)

    configs = grid_configs()
    if args.dry_run:
        configs = configs[:3]
        log.info("DRY RUN: limited to %d configs", len(configs))

    log.info("Loading Wikipedia SPX")
    wiki = WikipediaSPX()
    universe_at_start = wiki.constituents_on(args.start)
    log.info("Point-in-time universe on %s: %d tickers",
             args.start, len(universe_at_start))

    tickers = sorted(universe_at_start)
    if args.index_symbol not in tickers:
        tickers.append(args.index_symbol)

    fetch_start = args.start - timedelta(days=args.warmup_days)
    log.info("Fetching %d tickers %s → %s (cold run: ~40 min)",
             len(tickers), fetch_start, args.end)
    src = YFinanceSource()
    raw = src.fetch_many(tickers, fetch_start, args.end)
    data = {t: df for t, df in raw.items() if not df.empty}
    dropped = len(raw) - len(data)
    if dropped:
        log.warning("yfinance returned no data for %d tickers "
                    "(survivorship materialized)", dropped)
    if args.index_symbol not in data:
        log.error("No data for index %s — abort", args.index_symbol)
        return 1

    available = set(data.keys())

    def constituents_on(d: date) -> set[str]:
        return wiki.constituents_on(d) & available

    data_bounded = {
        t: df.loc[pd.Timestamp(args.start):pd.Timestamp(args.end)]
        for t, df in data.items()
    }
    data_bounded = {t: df for t, df in data_bounded.items() if not df.empty}
    log.info("Data ready: %d tickers with bars in [%s, %s]",
             len(data_bounded), args.start, args.end)

    def trial_fn(cfg):
        """Build Clenow strategy with the grid config; run through Runner.

        Strategy receives the full ``data`` (for warmup lookups); Runner
        iterates only the bounded slice.
        """
        strategy = ClenowMomentumStrategy(
            data=data,
            constituents_provider=constituents_on,
            index_symbol=args.index_symbol,
            lookback_regression=cfg.lookback_regression,
            top_pct=cfg.top_pct,
            risk_factor=cfg.risk_factor,
            rebalance_weekday=cfg.rebalance_weekday,
            lookback_trend=cfg.lookback_trend,
            lookback_index_trend=cfg.lookback_index_trend,
            lookback_atr=cfg.lookback_atr,
            lookback_gap=cfg.lookback_gap,
            gap_threshold=cfg.gap_threshold,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        return runner.run(
            strategy=strategy, data=data_bounded, initial_cash=args.cash,
        )

    # tqdm progress bar wrapping the grid run.
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
        checkpoint_dir=checkpoint_dir, n_jobs=args.n_jobs,
    ).run(
        configs=configs, trial_fn=trial_fn, run_id=run_id,
        progress_cb=observer,
    )
    pbar.close()

    log.info("Grid complete: %d/%d OK (%d errors)",
             len(grid.ok_trials), len(grid.trials),
             len(grid.trials) - len(grid.ok_trials))

    log.info("Running walk-forward per config (n_windows=8)")
    wf_results = wf_for_grid(grid, n_windows=8, n_jobs=args.n_jobs)

    log.info("Evaluating gates (PBO, DSR, walk-forward)")
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts={
        cid: wf.verdict for cid, wf in wf_results.items()
    })
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
        log.info("Failure modes: %s",
                 [m.label for m in diagnostic.failure_modes])

    log.info("=== grid run %s done ===", run_id)
    return 0 if verdict.overall_pass else 2


if __name__ == "__main__":
    sys.exit(main())
