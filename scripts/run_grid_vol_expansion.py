#!/usr/bin/env python3
"""Run the Vol-Expansion Breakout grid (Phase 2.5, Bundle γ: SPY, GLD, TLT).

End-to-end pipeline:

1. Fetch 1h OHLCV for each symbol via :class:`TiingoSource`
   (requires ``tiingo_service`` infra).
2. Build the 4 ``VolExpansionGridConfig`` configs × N symbols = N×4 trials.
3. Execute the grid via :class:`GridRunner` with checkpoint resume.
4. Walk-forward per config (8 windows), with regime pre-cache refit per window.
5. Evaluate gates: PBO < 0.5, DSR p < 0.05, walk-forward ≥ 6/8.
6. Emit report (PASS) or diagnostic (FAIL).

Typical invocation (Bundle γ):

    .venv/bin/python scripts/run_grid_vol_expansion.py \\
        --symbol SPY --asset-class etf --bars-per-year 1638 \\
        --symbol GLD --asset-class etf --bars-per-year 1638 \\
        --symbol TLT --asset-class etf --bars-per-year 1638 \\
        --start 2022-01-01 --end 2026-04-15 \\
        --cash 100000 --n-jobs 4 --output-dir reports/

Dry run (smoke, 1 config, 1 symbol):

    .venv/bin/python scripts/run_grid_vol_expansion.py --dry-run \\
        --symbol SPY --asset-class etf --bars-per-year 1638 \\
        --start 2024-01-01 --end 2024-06-30 \\
        --output-dir /tmp/grid_vol_expansion_smoke
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from tqdm import tqdm


log = logging.getLogger("ai_trade.grid.vol_expansion")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Vol-Expansion Breakout 1h grid with anti-overfit gates.",
    )
    ap.add_argument(
        "--symbol", dest="symbols", action="append", default=[],
        metavar="SYMBOL",
        help="Ticker symbol (repeat for multiple, e.g. --symbol SPY --symbol GLD).",
    )
    ap.add_argument(
        "--asset-class", dest="asset_classes", action="append", default=[],
        metavar="ASSET_CLASS",
        choices=["equity", "etf", "index", "crypto", "forex"],
        help="Asset class per symbol (same order as --symbol).",
    )
    ap.add_argument(
        "--bars-per-year", dest="bars_per_year", action="append", default=[],
        type=int,
        metavar="BARS",
        help="Trading bars per year per symbol (same order as --symbol). e.g. 1638 for ETF 1h.",
    )
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--n-jobs", type=int, default=-1)
    ap.add_argument("--dry-run", action="store_true")
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
        DiagnosticAnalyzer,
        GateEvaluator,
        GridReportGenerator,
        GridRunner,
        JsonlTrialObserver,
        StatusFileObserver,
        VolExpansionGridConfig,
        compose_observers,
        setup_grid_logging,
        vol_expansion_grid_configs,
        wf_for_grid,
    )
    from ai_trade.backtest.strategies.vol_expansion_breakout import (
        VolExpansionBreakoutStrategy,
    )

    args = _parse_args(argv)

    # --- Validate symbol / asset-class / bars-per-year alignment ---
    symbols = args.symbols
    asset_classes = args.asset_classes
    bars_per_year_list = args.bars_per_year

    if not symbols:
        log.error("At least one --symbol is required.")
        return 1

    # Fill defaults if user didn't provide per-symbol asset-class / bars-per-year
    if not asset_classes:
        asset_classes = ["etf"] * len(symbols)
    if not bars_per_year_list:
        bars_per_year_list = [1638] * len(symbols)

    if len(asset_classes) != len(symbols):
        log.error(
            "--asset-class count (%d) does not match --symbol count (%d)",
            len(asset_classes), len(symbols),
        )
        return 1
    if len(bars_per_year_list) != len(symbols):
        log.error(
            "--bars-per-year count (%d) does not match --symbol count (%d)",
            len(bars_per_year_list), len(symbols),
        )
        return 1

    symbol_specs: dict[str, dict] = {
        sym: {"bars_per_year": bpy, "asset_class": ac}
        for sym, bpy, ac in zip(symbols, bars_per_year_list, asset_classes)
    }

    run_id = (
        args.run_id or f"grid_vol_expansion_{datetime.now().strftime('%Y%m%d-%H%M')}"
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
        "symbols=%s start=%s end=%s cash=$%.0f n_jobs=%d dry_run=%s",
        symbols, args.start, args.end, args.cash, args.n_jobs, args.dry_run,
    )

    base_configs = vol_expansion_grid_configs()
    if args.dry_run:
        base_configs = base_configs[:1]
        dry_symbols = symbols[:1]
        log.info("DRY RUN: limited to 1 config × 1 symbol")
    else:
        dry_symbols = symbols

    fetch_start = args.start - timedelta(days=args.warmup_days)
    log.info(
        "Fetching %s 1h from %s → %s",
        dry_symbols, fetch_start, args.end,
    )
    src = TiingoSource(storage=TiingoStorage(root=args.storage_root))
    raw: dict[str, pd.DataFrame] = {}
    for sym in dry_symbols:
        ac = symbol_specs[sym]["asset_class"]
        df = src.fetch(
            sym, fetch_start, args.end,
            frequency="1hour", asset_class=ac,
        )
        if df.empty:
            log.error("No data for %s — abort", sym)
            return 1
        raw[sym] = df
        log.info("  %s: %d bars loaded", sym, len(df))

    # Bound the data to the backtest window (full window used for warmup)
    data_full: dict[str, pd.DataFrame] = raw
    data_bounded: dict[str, pd.DataFrame] = {
        sym: df.loc[pd.Timestamp(args.start): pd.Timestamp(args.end)]
        for sym, df in raw.items()
    }
    if any(df.empty for df in data_bounded.values()):
        log.error("Bounded range [%s, %s] is empty for some symbol", args.start, args.end)
        return 1
    for sym, df in data_bounded.items():
        log.info("  %s: %d bars in backtest window", sym, len(df))

    # Build trials: (config, symbol) pairs
    # Each trial is a single-symbol backtest for one config
    trial_specs: list[tuple[VolExpansionGridConfig, str]] = [
        (cfg, sym)
        for cfg in base_configs
        for sym in dry_symbols
    ]
    log.info(
        "%d configs × %d symbols = %d trials",
        len(base_configs), len(dry_symbols), len(trial_specs),
    )

    # GridRunner expects a list of config objects; we extend VolExpansionGridConfig
    # by wrapping (config, symbol) into a namedtuple-like frozen dataclass so
    # config_id is deterministic and checkpoint-resumable.
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class VolExpansionTrial:
        """Wrapper that pairs a grid config with one symbol for GridRunner."""
        n_entry: int
        n_exit: int
        k_filter: float
        target_vol_annual: float
        disaster_n_sigma: float
        ref_hold_bars: int
        cone_lookback: int
        yz_window: int
        max_hold_hours: float
        symbol: str

    combined_configs = [
        VolExpansionTrial(
            n_entry=cfg.n_entry,
            n_exit=cfg.n_exit,
            k_filter=cfg.k_filter,
            target_vol_annual=cfg.target_vol_annual,
            disaster_n_sigma=cfg.disaster_n_sigma,
            ref_hold_bars=cfg.ref_hold_bars,
            cone_lookback=cfg.cone_lookback,
            yz_window=cfg.yz_window,
            max_hold_hours=cfg.max_hold_hours,
            symbol=sym,
        )
        for cfg, sym in trial_specs
    ]

    def trial_fn(trial: VolExpansionTrial):
        """Build the single-symbol strategy for one trial and run it."""
        sym = trial.symbol
        sym_data_full = {sym: data_full[sym]}
        sym_data_bounded = {sym: data_bounded[sym]}

        strategy = VolExpansionBreakoutStrategy(
            data=sym_data_full,
            symbol_specs={sym: {"bars_per_year": symbol_specs[sym]["bars_per_year"]}},
            n_entry=trial.n_entry,
            n_exit=trial.n_exit,
            k_filter=trial.k_filter,
            target_vol_annual=trial.target_vol_annual,
            disaster_n_sigma=trial.disaster_n_sigma,
            ref_hold_bars=trial.ref_hold_bars,
            cone_lookback=trial.cone_lookback,
            yz_window=trial.yz_window,
            max_hold_hours=trial.max_hold_hours,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        return runner.run(
            strategy=strategy, data=sym_data_bounded, initial_cash=args.cash,
        )

    pbar = tqdm(total=len(combined_configs), desc=f"grid {run_id}", unit="trial")

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
        config_cls=VolExpansionTrial,
    ).run(
        configs=combined_configs, trial_fn=trial_fn, run_id=run_id,
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
