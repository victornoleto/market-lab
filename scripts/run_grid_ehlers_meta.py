#!/usr/bin/env python3
"""Run the Ehlers BP Swing + AFML meta-label grid (Phase 2.5 Run 4 Step 1).

End-to-end pipeline for the AFML rescue attempt on the Ehlers swing
trader:

1. Fetch daily OHLCV for the target symbol (Tiingo or yfinance).
2. Build 48 ``EhlersMetaGridConfig`` configs
   (2 × 2 × 3 × 2 × 2 = hp × lp × pct × stop × p_act_threshold).
3. Execute the grid via :class:`GridRunner` with checkpoint resume.
   Each trial fits a RandomForest on the first 50% of primary events
   then backtests with the secondary filter active on the remainder
   [advances_fin_ml, §3.6, p.50-54].
4. Walk-forward per config (8 windows).
5. Evaluate the 3 gates: PBO < 0.5, DSR p < 0.05, walk-forward ≥ 6/8.
6. Emit report (PASS) or diagnostic (FAIL).

Typical invocation:

    .venv/bin/python scripts/run_grid_ehlers_meta.py \\
        --data-source tiingo --symbol SPY \\
        --start 2015-01-01 --end 2023-12-31 \\
        --cash 100000 --n-jobs 4 --output-dir reports/

Dry run (smoke test, 3 configs):

    .venv/bin/python scripts/run_grid_ehlers_meta.py --dry-run \\
        --start 2022-01-01 --end 2023-12-31 \\
        --output-dir /tmp/grid_meta_smoke

Logs: unified append-only at ``logs/grid.log`` (shared with every other
grid run, present and future).
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from tqdm import tqdm


log = logging.getLogger("ai_trade.grid.ehlers_meta")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Ehlers BP Swing + AFML meta-label grid with active anti-overfit gates."
        ),
    )
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument(
        "--run-id",
        default=None,
        help="Defaults to grid_ehlers_meta_<YYYYMMDD-HHMM>. Resume a prior run "
        "by reusing its run_id.",
    )
    ap.add_argument(
        "--n-jobs", type=int, default=-1,
        help="-1 = all cores (default); 1 = sequential.",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Limit grid to first 3 configs for smoke testing.",
    )
    ap.add_argument(
        "--symbol", default=None,
        help="Ticker to trade. Defaults: ^GSPC (yfinance) / SPY (tiingo).",
    )
    ap.add_argument(
        "--asset-class", default="equity",
        choices=["equity", "etf", "index", "crypto", "forex"],
    )
    ap.add_argument(
        "--warmup-days", type=int, default=500,
        help="Calendar days of history before --start (default: 500).",
    )
    ap.add_argument(
        "--data-source",
        choices=["yfinance", "tiingo"],
        default="tiingo",
    )
    ap.add_argument(
        "--storage-root", type=Path, default=Path("data/tiingo"),
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
        EhlersMetaGridConfig,
        GateEvaluator,
        GridReportGenerator,
        GridRunner,
        JsonlTrialObserver,
        StatusFileObserver,
        compose_observers,
        ehlers_meta_grid_configs,
        setup_grid_logging,
        wf_for_grid,
    )
    from ai_trade.backtest.strategies.ehlers_meta import EhlersMetaStrategy

    args = _parse_args(argv)
    if args.symbol is None:
        args.symbol = "^GSPC" if args.data_source == "yfinance" else "SPY"
    run_id = (
        args.run_id or f"grid_ehlers_meta_{datetime.now().strftime('%Y%m%d-%H%M')}"
    )
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
        "start=%s end=%s cash=$%.0f n_jobs=%d dry_run=%s symbol=%s data_source=%s",
        args.start, args.end, args.cash, args.n_jobs, args.dry_run,
        args.symbol, args.data_source,
    )

    configs = ehlers_meta_grid_configs()
    if args.dry_run:
        configs = configs[:3]
        log.info("DRY RUN: limited to %d configs", len(configs))

    fetch_start = args.start - timedelta(days=args.warmup_days)
    log.info("Fetching %s %s → %s via %s",
             args.symbol, fetch_start, args.end, args.data_source)
    src = _build_source(args.data_source, args.storage_root)
    fetch_kwargs = (
        {"asset_class": args.asset_class} if args.data_source == "tiingo" else {}
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
        args.start,
        args.end,
    )

    def trial_fn(cfg: EhlersMetaGridConfig):
        """Build the meta strategy for this trial and run it.

        Strategy fits the RandomForest on the first 50% of primary events
        (within the full ``data`` frame including warmup), then runs the
        Runner on the bounded ``[start, end]`` slice with the filter
        active after the training cutoff.
        """
        strategy = EhlersMetaStrategy(
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
            p_act_threshold=cfg.p_act_threshold,
            train_fraction=cfg.train_fraction,
            pt=cfg.pt,
            sl=cfg.sl,
            vertical_bars=cfg.vertical_bars,
            atr_window=cfg.atr_window,
            sma_regime_window=cfg.sma_regime_window,
            n_estimators=cfg.n_estimators,
            max_depth=cfg.max_depth,
            min_train_events=cfg.min_train_events,
            random_state=cfg.random_state,
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
        config_cls=EhlersMetaGridConfig,
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
