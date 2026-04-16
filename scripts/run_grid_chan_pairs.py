#!/usr/bin/env python3
"""Run the Chan Bollinger Pairs grid (Phase 2.5 first intraday entry).

End-to-end pipeline:

1. Fetch 1h OHLCV for ``long_symbol`` and ``short_symbol`` via
   :class:`TiingoSource` (requires ``tiingo_service`` infra).
2. Build the 4 ``ChanPairsGridConfig`` configs.
3. Execute the grid via :class:`GridRunner` with checkpoint resume.
4. Walk-forward per config (8 windows), with β + half-life **refit**
   at the start of each window (true OOS per Chan [p.8, ch.1]).
5. Evaluate gates: PBO < 0.5, DSR p < 0.05, walk-forward ≥ 6/8.
6. Emit report (PASS) or diagnostic (FAIL).

Typical invocation:

    .venv/bin/python scripts/run_grid_chan_pairs.py \\
        --long-symbol GLD --short-symbol SLV \\
        --start 2022-01-01 --end 2026-04-15 \\
        --cash 100000 --n-jobs 4 --output-dir reports/

Dry run (smoke, 1 config):

    .venv/bin/python scripts/run_grid_chan_pairs.py --dry-run \\
        --long-symbol GLD --short-symbol SLV \\
        --start 2023-01-01 --end 2024-12-31 \\
        --output-dir /tmp/grid_chan_pairs_smoke
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from tqdm import tqdm


log = logging.getLogger("ai_trade.grid.chan_pairs")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Chan Bollinger Pairs 1h grid with anti-overfit gates.",
    )
    ap.add_argument("--long-symbol", default="GLD")
    ap.add_argument("--short-symbol", default="SLV")
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--n-jobs", type=int, default=-1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--asset-class", default="etf",
        choices=["equity", "etf", "index", "crypto", "forex"],
    )
    ap.add_argument("--warmup-days", type=int, default=365)
    ap.add_argument(
        "--storage-root", type=Path, default=Path("data/tiingo"),
    )
    ap.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import (
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.grid import (
        ChanPairsGridConfig,
        DiagnosticAnalyzer,
        GateEvaluator,
        GridReportGenerator,
        GridRunner,
        JsonlTrialObserver,
        StatusFileObserver,
        chan_pairs_grid_configs,
        compose_observers,
        setup_grid_logging,
        wf_for_grid,
    )
    from ai_trade.backtest.strategies.chan_bollinger_pairs import (
        ChanBollingerPairsStrategy,
    )

    args = _parse_args(argv)
    run_id = (
        args.run_id or f"grid_chan_pairs_{datetime.now().strftime('%Y%m%d-%H%M')}"
    )
    output_dir = args.output_dir / run_id
    checkpoint_dir = Path(".cache/grid_runs")
    run_checkpoint_dir = checkpoint_dir / run_id
    run_checkpoint_dir.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, args.log_level)
    setup_grid_logging(
        run_id=run_id, run_dir=run_checkpoint_dir,
        unified_log_path=Path("logs/grid.log"), level=level,
    )

    log.info("=== grid run %s ===", run_id)
    log.info(
        "long=%s short=%s start=%s end=%s cash=$%.0f n_jobs=%d dry_run=%s",
        args.long_symbol, args.short_symbol, args.start, args.end,
        args.cash, args.n_jobs, args.dry_run,
    )

    configs = chan_pairs_grid_configs()
    if args.dry_run:
        configs = configs[:1]
        log.info("DRY RUN: limited to 1 config")

    fetch_start = args.start - timedelta(days=args.warmup_days)
    log.info(
        "Fetching %s + %s 1h from %s → %s",
        args.long_symbol, args.short_symbol, fetch_start, args.end,
    )
    src = TiingoSource(storage=TiingoStorage(root=args.storage_root))
    raw = {}
    for sym in (args.long_symbol, args.short_symbol):
        df = src.fetch(
            sym, fetch_start, args.end,
            frequency="1hour", asset_class=args.asset_class,
        )
        if df.empty:
            log.error("No data for %s — abort", sym)
            return 1
        raw[sym] = df

    # Align indices by inner-join on timestamps (handles minor gaps/halts)
    common_idx = raw[args.long_symbol].index.intersection(
        raw[args.short_symbol].index
    )
    if len(common_idx) == 0:
        log.error("No overlapping timestamps between %s and %s",
                  args.long_symbol, args.short_symbol)
        return 1
    data_full = {sym: raw[sym].loc[common_idx] for sym in raw}

    data_bounded = {
        sym: data_full[sym].loc[
            pd.Timestamp(args.start) : pd.Timestamp(args.end)
        ]
        for sym in data_full
    }
    if any(df.empty for df in data_bounded.values()):
        log.error("Bounded range [%s, %s] is empty", args.start, args.end)
        return 1
    log.info(
        "Data ready: %d bars in [%s, %s]",
        len(data_bounded[args.long_symbol]), args.start, args.end,
    )

    def trial_fn(cfg: ChanPairsGridConfig):
        """Build the pair strategy for one trial and run it."""
        strategy = ChanBollingerPairsStrategy(
            data=data_full,
            long_symbol=args.long_symbol,
            short_symbol=args.short_symbol,
            lookback_multiplier=cfg.lookback_multiplier,
            entry_z=cfg.entry_z,
            exit_z=cfg.exit_z,
            spread_stop_z=cfg.spread_stop_z,
            train_bars=cfg.train_bars,
            half_life_min=cfg.half_life_min,
            half_life_max=cfg.half_life_max,
            risk_pct_of_equity=cfg.risk_pct_of_equity,
            max_hold_hours=cfg.max_hold_hours,
            entry_hour_cutoff=cfg.entry_hour_cutoff,
            friday_flat_hour=cfg.friday_flat_hour,
            friday_no_entry_hour=cfg.friday_no_entry_hour,
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
        config_cls=ChanPairsGridConfig,
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
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("PASS report: %s", path)
    else:
        diagnostic = DiagnosticAnalyzer().analyze(
            grid=grid, verdict=verdict, wf_results=wf_results,
        )
        path = report_gen.write_fail_report(
            grid=grid, verdict=verdict, wf_results=wf_results,
            diagnostic=diagnostic,
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("FAIL diagnostic report: %s", path)

    log.info("=== grid run %s done ===", run_id)
    return 0 if verdict.overall_pass else 2


if __name__ == "__main__":
    sys.exit(main())
