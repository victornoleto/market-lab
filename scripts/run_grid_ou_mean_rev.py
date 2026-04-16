#!/usr/bin/env python3
"""Run the OU Mean-Reversion grid with active gates.

Orchestrates the end-to-end pipeline for a single-instrument OU
mean-reversion grid:

1. Fetch OHLCV from Tiingo (1h or daily).
2. Build 4 OU MR configs (2 × 2: lookback × z_entry).
3. Execute the grid in parallel via :class:`GridRunner`.
4. Run walk-forward per config.
5. Apply :class:`GateEvaluator` (PBO < 0.5, DSR p < 0.05, WF ≥ 6/8).
6. Write pass or fail report.

Typical invocation (1h SPY, 5 years):

    .venv/bin/python scripts/run_grid_ou_mean_rev.py \\
        --data-source tiingo --symbol SPY --asset-class etf \\
        --storage-root data/tiingo --start 2021-01-01 --end 2025-12-31 \\
        --frequency 1hour --output-dir reports/ --n-jobs 4

Strategy citations:
- [algo_trading_chan, p.47-48, ch.2] — OU process, half-life formula.
- [machine_trading, p.60-65, ch.3] — AR(1) model foundation.
- [quant_trading_chan, p.140-142] — z-score mean-reversion entries.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from tqdm import tqdm

log = logging.getLogger("ai_trade.grid.ou_mean_rev")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="OU MR grid with active anti-overfit gates.",
    )
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--n-jobs", type=int, default=-1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--symbol", default="SPY")
    ap.add_argument(
        "--asset-class", default="etf",
        choices=["equity", "etf", "index", "crypto", "forex"],
    )
    ap.add_argument("--warmup-days", type=int, default=100)
    ap.add_argument(
        "--data-source", choices=["yfinance", "tiingo"], default="tiingo",
    )
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument(
        "--frequency", default="1hour", choices=["daily", "1hour"],
    )
    ap.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


def _build_source(name: str, storage_root: Path):
    if name == "yfinance":
        from ai_trade.backtest.data.yfinance_source import YFinanceSource
        return YFinanceSource()
    if name == "tiingo":
        from ai_trade.backtest.data.tiingo_source import TiingoSource
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage
        return TiingoSource(storage=TiingoStorage(root=storage_root))
    raise ValueError(f"unknown data_source: {name!r}")


def main(argv: list[str] | None = None) -> int:
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
        setup_grid_logging,
        wf_for_grid,
    )
    from ai_trade.backtest.grid.ou_mean_rev_config import (
        OUMeanRevGridConfig,
        ou_mean_rev_grid_configs,
    )
    from ai_trade.backtest.strategies.ou_mean_rev import OUMeanRevStrategy

    args = _parse_args(argv)
    if args.frequency == "1hour" and args.data_source != "tiingo":
        log.error("--frequency=1hour requires --data-source=tiingo")
        return 1
    run_id = args.run_id or f"grid_ou_mean_rev_{datetime.now().strftime('%Y%m%d-%H%M')}"
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
        "start=%s end=%s cash=$%.0f n_jobs=%d symbol=%s "
        "data_source=%s frequency=%s",
        args.start, args.end, args.cash, args.n_jobs,
        args.symbol, args.data_source, args.frequency,
    )

    configs = ou_mean_rev_grid_configs()
    if args.dry_run:
        configs = configs[:2]
        log.info("DRY RUN: limited to %d configs", len(configs))
    log.info("Grid size: %d configs (N=%d for DSR)", len(configs), len(configs))

    fetch_start = args.start - timedelta(days=args.warmup_days)
    log.info("Fetching %s %s → %s via %s (freq=%s)",
             args.symbol, fetch_start, args.end, args.data_source, args.frequency)
    src = _build_source(args.data_source, args.storage_root)
    fetch_kwargs = (
        {"asset_class": args.asset_class, "frequency": args.frequency}
        if args.data_source == "tiingo" else {}
    )
    raw = src.fetch_many([args.symbol], fetch_start, args.end, **fetch_kwargs)
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
        args.start, args.end,
    )

    periods_per_year = 252 * 7 if args.frequency == "1hour" else 252

    def trial_fn(cfg: OUMeanRevGridConfig):
        strategy = OUMeanRevStrategy(
            data=data,
            symbol=args.symbol,
            lookback=cfg.lookback,
            z_entry=cfg.z_entry,
            z_exit=cfg.z_exit,
            stop_pct=cfg.stop_pct,
            max_hold=cfg.max_hold,
            risk_pct_of_equity=cfg.risk_pct_of_equity,
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
        config_cls=OUMeanRevGridConfig,
        periods_per_year=periods_per_year,
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
            output_dir=output_dir, data_source=args.data_source,
        )
        log.info("PASS report: %s", path)
    else:
        diagnostic = DiagnosticAnalyzer().analyze(
            grid=grid, verdict=verdict, wf_results=wf_results,
        )
        path = report_gen.write_fail_report(
            grid=grid, verdict=verdict, wf_results=wf_results,
            diagnostic=diagnostic,
            output_dir=output_dir, data_source=args.data_source,
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
