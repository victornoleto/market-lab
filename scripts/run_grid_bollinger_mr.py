#!/usr/bin/env python3
"""Run the Bollinger Mean-Reversion grid with active gates.

Orchestrates the end-to-end pipeline for a single-instrument Bollinger
mean-reversion grid:

1. Fetch OHLCV from Tiingo (1h or daily).
2. Build 4 Bollinger MR configs (2 × 2: window × std_mult).
3. Execute the grid in parallel via :class:`GridRunner`.
4. Run walk-forward per config.
5. Apply :class:`GateEvaluator` (PBO < 0.5, DSR p < 0.05, WF ≥ 6/8).
6. Write pass or fail report.

Typical invocation (1h SPY, 5 years):

    .venv/bin/python scripts/run_grid_bollinger_mr.py \\
        --data-source tiingo --symbol SPY --asset-class etf \\
        --storage-root data/tiingo --start 2021-01-01 --end 2025-12-31 \\
        --frequency 1hour --output-dir reports/ --n-jobs 4

Strategy citations:
- [algo_trading_chan, p.28-30, ch.2] — Bollinger band mean-reversion.
- [machine_trading, p.204-205, ch.7] — short-term Bollinger scalping.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from tqdm import tqdm

log = logging.getLogger("ai_trade.grid.bollinger_mr")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Bollinger MR grid with active anti-overfit gates.",
    )
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--n-jobs", type=int, default=-1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--symbol", default=None)
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
        "--direction", default="long",
        choices=["long", "short", "both"],
        help="Entry direction: long (default), short, or both.",
    )
    ap.add_argument(
        "--garch-lambda", type=float, default=0.0,
        help="EWMA-GARCH vol sizing lambda (0=disabled, 0.94=RiskMetrics). "
             "[machine_trading, p.126-127, ch.4]",
    )
    ap.add_argument(
        "--canonical-only", action="store_true",
        help="Run only the canonical (20,2) Bollinger config (N=1, no "
             "multiple-test deflation). Use when config is pre-specified "
             "by literature. [machine_trading, p.204-205, ch.7]",
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
    from ai_trade.backtest.grid.bollinger_mr_config import (
        BollingerMRGridConfig,
        bollinger_mr_canonical_configs,
        bollinger_mr_grid_configs,
    )
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    args = _parse_args(argv)
    if args.symbol is None:
        args.symbol = "SPY"
    if args.frequency == "1hour" and args.data_source != "tiingo":
        log.error("--frequency=1hour requires --data-source=tiingo")
        return 1
    run_id = args.run_id or f"grid_bollinger_mr_{datetime.now().strftime('%Y%m%d-%H%M')}"
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
        "data_source=%s frequency=%s direction=%s garch_lambda=%.2f",
        args.start, args.end, args.cash, args.n_jobs,
        args.symbol, args.data_source, args.frequency,
        args.direction, args.garch_lambda,
    )

    if args.canonical_only:
        configs = bollinger_mr_canonical_configs()
        log.info("CANONICAL mode: N=1 pre-specified config (20,2) [machine_trading, p.204-205]")
    else:
        configs = bollinger_mr_grid_configs()
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

    # Determine periods_per_year for Sharpe/CAGR annualization.
    periods_per_year = 252 * 7 if args.frequency == "1hour" else 252

    def trial_fn(cfg: BollingerMRGridConfig):
        strategy = BollingerMRStrategy(
            data=data,
            symbol=args.symbol,
            window=cfg.window,
            std_mult=cfg.std_mult,
            stop_pct=cfg.stop_pct,
            max_hold=cfg.max_hold,
            risk_pct_of_equity=cfg.risk_pct_of_equity,
            direction=args.direction,
            garch_lambda=args.garch_lambda,
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
        config_cls=BollingerMRGridConfig,
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
