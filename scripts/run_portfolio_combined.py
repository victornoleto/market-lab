#!/usr/bin/env python3
"""Run the F3.D combined portfolio grid with active anti-overfit gates.

Orchestrates the end-to-end pipeline for a "two books offline" portfolio
combining Clenow momentum + Ehlers BP Swing:

1. Load OHLCV (Tiingo storage-first): Clenow needs SPX 500 universe,
   Ehlers needs SPY.
2. Build 3 Clenow top-3 configs + 3 Ehlers top-3 configs = 9 pairs.
3. Run each sub-strategy as its own GridRunner pass (3 trials each),
   obtaining 3 Clenow equity curves + 3 Ehlers equity curves.
4. For each (c, e) pair: combine_equity_curves([c, e], [0.5, 0.5]).
5. Wrap 9 combined curves as TrialResult and bundle into a synthetic
   GridResult[PortfolioConfig].
6. Run walk-forward per combined portfolio (8 windows each).
7. Apply GateEvaluator against PBO/DSR/walk-forward rules.
8. Write diagnostic.md + PNGs via GridReportGenerator.

Typical invocation:

    .venv/bin/python scripts/run_portfolio_combined.py \\
        --start 2015-01-01 --end 2023-12-31 \\
        --cash 100000 \\
        --output-dir reports/

Logs: unified append-only log at ``logs/grid.log`` shared with
``run_grid_clenow.py`` / ``run_grid_ehlers.py``. Per-run detail under
``.cache/grid_runs/{run_id}/`` and ``.cache/grid_runs/{run_id}_clenow/``
and ``.cache/grid_runs/{run_id}_ehlers/``. ``logs/f3d.log`` is a
session-level artifact the orchestrator shell appends to — NOT written
by this script.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd


log = logging.getLogger("ai_trade.grid.f3d")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="F3.D combined-portfolio grid with active anti-overfit gates.",
    )
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument(
        "--run-id",
        default=None,
        help="Defaults to grid_portfolio_<YYYYMMDD-HHMM>. Resume a prior run "
        "by reusing its run_id.",
    )
    ap.add_argument(
        "--n-jobs", type=int, default=-1,
        help="-1 = all cores (default); 1 = sequential",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Skip validation/report and just print the 9 portfolio Sharpes.",
    )
    ap.add_argument(
        "--storage-root", type=Path, default=Path("data/tiingo"),
        help="Tiingo parquet+manifest root. Default: data/tiingo.",
    )
    ap.add_argument(
        "--warmup-days", type=int, default=500,
        help="Calendar days of history before --start (default: 500).",
    )
    ap.add_argument(
        "--index-symbol", default="SPY",
        help="Index trend-filter symbol for Clenow (also Ehlers instrument). "
        "Tiingo convention is SPY (not ^GSPC).",
    )
    ap.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


def _build_tiingo_source(storage_root: Path):
    """Construct a TiingoSource with storage-first semantics."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    return TiingoSource(storage=TiingoStorage(root=storage_root))


def _build_subgrid_observer(sub_run_id: str, n_configs: int, checkpoint_dir: Path):
    """Compose the standard observer bundle used by both sub-grids.

    Matches the peer pattern in ``scripts/run_grid_clenow.py`` (§Observers)
    and ``scripts/run_grid_ehlers.py``: JsonlTrialObserver + StatusFileObserver
    (per-sub-run + shared ``logs/grid_latest_status.md``) + tqdm progress bar.
    """
    from tqdm import tqdm

    from ai_trade.backtest.grid import (
        JsonlTrialObserver,
        StatusFileObserver,
        compose_observers,
    )

    sub_dir = checkpoint_dir / sub_run_id
    sub_dir.mkdir(parents=True, exist_ok=True)
    pbar = tqdm(total=n_configs, desc=f"grid {sub_run_id}", unit="cfg")

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
            path=sub_dir / "trials.jsonl", run_id=sub_run_id,
        ),
        StatusFileObserver(
            path=sub_dir / "status.md", run_id=sub_run_id,
        ),
        StatusFileObserver(
            path=Path("logs/grid_latest_status.md"), run_id=sub_run_id,
        ),
        tqdm_observer,
    )
    return observer, pbar


def _load_data(
    start: date,
    end: date,
    index_symbol: str,
    storage_root: Path,
    warmup_days: int,
):
    """Load Clenow SPX point-in-time universe + index proxy + Ehlers SPY.

    Mirrors ``scripts/run_grid_clenow.py`` lines 116-195: uses
    :class:`WikipediaSPX` for point-in-time constituents, Tiingo storage
    for OHLCV, and returns the ``constituents_provider`` closure that
    intersects Wikipedia membership with actually-loaded tickers (so
    Clenow doesn't attempt to trade a ticker with no data).

    Returns
    -------
    clenow_data : dict[ticker, OHLCV DataFrame]
        Point-in-time universe + index proxy (SPY). Input to
        ``_run_clenow_top3``.
    spy_data : pd.DataFrame
        SPY OHLCV slice — passed to Ehlers as its sole instrument.
    constituents_provider : Callable[[date], set[str]]
        Closure: given a date, returns the subset of the SPX
        point-in-time constituents that we actually have data for on
        that date. Required by ``ClenowMomentumStrategy``.
    """
    from ai_trade.backtest.data.wikipedia_spx import WikipediaSPX

    src = _build_tiingo_source(storage_root)
    fetch_start = start - timedelta(days=warmup_days)

    log.info("Loading Wikipedia SPX point-in-time membership")
    wiki = WikipediaSPX()
    universe_at_start = wiki.constituents_on(start)
    log.info(
        "Point-in-time universe on %s: %d tickers",
        start, len(universe_at_start),
    )

    spx_tickers = sorted(t for t in universe_at_start if t != index_symbol)

    # Fetch SPX constituents as equity (taxonomy correct for the ~500 stocks).
    log.info(
        "Fetching %d SPX tickers %s → %s via Tiingo (asset_class=equity)",
        len(spx_tickers), fetch_start, end,
    )
    raw_spx = src.fetch_many(
        spx_tickers, fetch_start, end, asset_class="equity",
    )
    clenow_data = {t: df for t, df in raw_spx.items() if not df.empty}
    dropped = len(raw_spx) - len(clenow_data)
    if dropped:
        log.warning(
            "Tiingo returned no data for %d SPX tickers (survivorship-"
            "honest: these are absent from the manifest on purpose)",
            dropped,
        )

    # Fetch index proxy (SPY) as ETF. Passing asset_class="equity" here
    # would silently overwrite SPY's manifest entry from "etf" to "equity"
    # on cold rebuild (TiingoStorage.write mutates the taxonomy). See
    # code review of commit 36c0f57 issue I2.
    log.info(
        "Fetching index proxy %s %s → %s via Tiingo (asset_class=etf)",
        index_symbol, fetch_start, end,
    )
    raw_index = src.fetch_many(
        [index_symbol], fetch_start, end, asset_class="etf",
    )
    if index_symbol not in raw_index or raw_index[index_symbol].empty:
        raise RuntimeError(
            f"No Tiingo data for index proxy {index_symbol} — abort"
        )
    spy_df = raw_index[index_symbol]
    clenow_data[index_symbol] = spy_df

    available = set(clenow_data.keys())

    def constituents_provider(d: date) -> set[str]:
        return wiki.constituents_on(d) & available

    log.info(
        "Data ready: %d Clenow tickers (post-drop), SPY bars=%d",
        len(clenow_data), len(spy_df),
    )
    return clenow_data, spy_df, constituents_provider


def _run_clenow_top3(
    data: dict[str, pd.DataFrame],
    constituents_provider: "Callable[[date], set[str]]",
    index_symbol: str,
    start: date,
    end: date,
    cash: float,
    n_jobs: int,
    checkpoint_dir: Path,
    run_id: str,
):
    """Run the 3 top-3 Clenow configs; return a list of 3 equity curves.

    The strategy needs a point-in-time ``constituents_provider`` and the
    ``index_symbol`` that drives Clenow's regime filter — both mirror how
    ``scripts/run_grid_clenow.py`` wires its trial_fn.
    """
    from ai_trade.backtest.engine import (
        ExecutionConfig, ExecutionSimulator, Runner,
    )
    from ai_trade.backtest.grid import ClenowGridConfig, GridRunner
    from ai_trade.backtest.portfolio.configs import clenow_top3_grid_configs
    from ai_trade.backtest.strategies.clenow_momentum import (
        ClenowMomentumStrategy,
    )

    clenow_configs = clenow_top3_grid_configs()

    data_bounded = {
        sym: df.loc[pd.Timestamp(start) : pd.Timestamp(end)]
        for sym, df in data.items()
    }

    def trial_fn(cfg: ClenowGridConfig):
        strategy = ClenowMomentumStrategy(
            data=data,
            constituents_provider=constituents_provider,
            index_symbol=index_symbol,
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
            strategy=strategy, data=data_bounded, initial_cash=cash,
        )

    log.info("Running Clenow top-3 grid (3 configs)")
    sub_run_id = f"{run_id}_clenow"
    observer, pbar = _build_subgrid_observer(
        sub_run_id, len(clenow_configs), checkpoint_dir,
    )
    try:
        grid = GridRunner(
            checkpoint_dir=checkpoint_dir,
            n_jobs=n_jobs,
            config_cls=ClenowGridConfig,
        ).run(
            configs=clenow_configs, trial_fn=trial_fn,
            run_id=sub_run_id, progress_cb=observer,
        )
    finally:
        pbar.close()
    ok = grid.ok_trials
    if len(ok) != 3:
        raise RuntimeError(
            f"Expected 3 OK Clenow trials; got {len(ok)}. Error msgs: "
            f"{[t.error_msg for t in grid.trials if t.status == 'error']}"
        )
    return [t.result.equity_curve for t in ok]


def _run_ehlers_top3(
    spy_data: pd.DataFrame,
    start: date,
    end: date,
    cash: float,
    n_jobs: int,
    checkpoint_dir: Path,
    run_id: str,
):
    """Run the 3 top-3 Ehlers configs on SPY; return a list of 3 equity curves."""
    from ai_trade.backtest.engine import (
        ExecutionConfig, ExecutionSimulator, Runner,
    )
    from ai_trade.backtest.grid import EhlersGridConfig, GridRunner
    from ai_trade.backtest.portfolio.configs import ehlers_top3_grid_configs
    from ai_trade.backtest.strategies.ehlers_bp_swing import (
        EhlersBPSwingStrategy,
    )

    ehlers_configs = ehlers_top3_grid_configs()

    data = {"SPY": spy_data}
    data_bounded = {
        "SPY": spy_data.loc[pd.Timestamp(start) : pd.Timestamp(end)]
    }

    def trial_fn(cfg: EhlersGridConfig):
        strategy = EhlersBPSwingStrategy(
            data=data,
            symbol="SPY",
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
            strategy=strategy, data=data_bounded, initial_cash=cash,
        )

    log.info("Running Ehlers top-3 grid (3 configs)")
    sub_run_id = f"{run_id}_ehlers"
    observer, pbar = _build_subgrid_observer(
        sub_run_id, len(ehlers_configs), checkpoint_dir,
    )
    try:
        grid = GridRunner(
            checkpoint_dir=checkpoint_dir,
            n_jobs=n_jobs,
            config_cls=EhlersGridConfig,
        ).run(
            configs=ehlers_configs, trial_fn=trial_fn,
            run_id=sub_run_id, progress_cb=observer,
        )
    finally:
        pbar.close()
    ok = grid.ok_trials
    if len(ok) != 3:
        raise RuntimeError(
            f"Expected 3 OK Ehlers trials; got {len(ok)}. Error msgs: "
            f"{[t.error_msg for t in grid.trials if t.status == 'error']}"
        )
    return [t.result.equity_curve for t in ok]


def _build_portfolio_grid(
    clenow_curves: list[pd.Series],
    ehlers_curves: list[pd.Series],
    initial_cash: float,
    run_id: str,
):
    """Combine 3 Clenow × 3 Ehlers equity curves into 9 portfolios.

    Returns a synthetic GridResult[PortfolioConfig] with 9 TrialResults,
    ready for the existing gate pipeline.
    """
    from ai_trade.backtest.grid.result import GridResult
    from ai_trade.backtest.portfolio.combined import (
        combine_equity_curves,
        make_portfolio_trial,
    )
    from ai_trade.backtest.portfolio.configs import portfolio_configs

    configs = portfolio_configs()
    assert len(configs) == 9

    trials = []
    for i, cfg in enumerate(configs):
        # Map config IDs back to the index in the top-3 tuples.
        # portfolio_configs() order: outer=Clenow ranks, inner=Ehlers ranks.
        clenow_rank = i // 3
        ehlers_rank = i % 3
        c_curve = clenow_curves[clenow_rank]
        e_curve = ehlers_curves[ehlers_rank]
        combined = combine_equity_curves(
            [c_curve, e_curve],
            [0.5, 0.5],
            initial_capital=initial_cash,
        )
        trials.append(
            make_portfolio_trial(
                config_id=i,
                config=cfg,
                equity_curve=combined,
                initial_cash=initial_cash,
            )
        )

    return GridResult(trials=trials, run_id=run_id)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    run_id = args.run_id or f"grid_portfolio_{datetime.now().strftime('%Y%m%d-%H%M')}"
    output_dir = args.output_dir / run_id
    checkpoint_dir = Path(".cache/grid_runs")
    run_checkpoint_dir = checkpoint_dir / run_id
    run_checkpoint_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    from ai_trade.backtest.grid import (
        DiagnosticAnalyzer, GateEvaluator, GridReportGenerator,
        setup_grid_logging, wf_for_grid,
    )

    setup_grid_logging(
        run_id=run_id,
        run_dir=run_checkpoint_dir,
        unified_log_path=Path("logs/grid.log"),
        level=getattr(logging, args.log_level),
    )
    log.info("=== F3.D portfolio run %s ===", run_id)
    log.info(
        "start=%s end=%s cash=$%.0f n_jobs=%d dry_run=%s",
        args.start, args.end, args.cash, args.n_jobs, args.dry_run,
    )

    # 1. Load data.
    clenow_data, spy_data, constituents_provider = _load_data(
        start=args.start, end=args.end,
        index_symbol=args.index_symbol,
        storage_root=args.storage_root,
        warmup_days=args.warmup_days,
    )

    # 2. Run sub-grids (3 Clenow + 3 Ehlers).
    clenow_curves = _run_clenow_top3(
        data=clenow_data,
        constituents_provider=constituents_provider,
        index_symbol=args.index_symbol,
        start=args.start, end=args.end, cash=args.cash,
        n_jobs=args.n_jobs,
        checkpoint_dir=checkpoint_dir, run_id=run_id,
    )
    ehlers_curves = _run_ehlers_top3(
        spy_data=spy_data,
        start=args.start, end=args.end, cash=args.cash,
        n_jobs=args.n_jobs,
        checkpoint_dir=checkpoint_dir, run_id=run_id,
    )

    # 3. Combine 9 portfolios.
    portfolio_grid = _build_portfolio_grid(
        clenow_curves=clenow_curves,
        ehlers_curves=ehlers_curves,
        initial_cash=args.cash,
        run_id=run_id,
    )
    log.info(
        "9 portfolios built: Sharpes=%s",
        [f"{t.sharpe:.3f}" for t in portfolio_grid.ok_trials],
    )

    if args.dry_run:
        log.info("--dry-run: skipping validation/report")
        for t in portfolio_grid.ok_trials:
            log.info(
                "cfg %d (clenow=%d, ehlers=%d): Sharpe %.3f CAGR %.2f%% DD %.2f%%",
                t.config_id,
                t.config.clenow_config_id,
                t.config.ehlers_config_id,
                t.sharpe, t.cagr * 100, t.max_drawdown * 100,
            )
        return 0

    # 4. Walk-forward per combined portfolio.
    log.info("Running walk-forward per portfolio (n_windows=8)")
    wf_results = wf_for_grid(portfolio_grid, n_windows=8, n_jobs=args.n_jobs)

    # 5. Gate evaluation.
    log.info("Evaluating gates (PBO, DSR, walk-forward)")
    verdict = GateEvaluator().evaluate(
        grid=portfolio_grid,
        wf_verdicts={cid: wf.verdict for cid, wf in wf_results.items()},
    )
    pbo_val = (
        float(verdict.pbo_result.pbo)
        if verdict.pbo_result else float("nan")
    )
    log.info(
        "Gate verdict: overall_pass=%s best_config_id=%s "
        "pbo=%.3f dsr_pass=%d/%d wf_pass=%d/%d",
        verdict.overall_pass, verdict.best_config_id, pbo_val,
        len(verdict.dsr_pass_ids), len(verdict.dsr_results),
        len(verdict.wf_pass_ids), len(verdict.wf_verdicts),
    )

    # 6. Report.
    report_gen = GridReportGenerator()
    if verdict.overall_pass:
        path = report_gen.write_pass_report(
            grid=portfolio_grid, verdict=verdict, wf_results=wf_results,
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("PASS report: %s", path)
    else:
        diagnostic = DiagnosticAnalyzer().analyze(
            grid=portfolio_grid, verdict=verdict, wf_results=wf_results,
        )
        path = report_gen.write_fail_report(
            grid=portfolio_grid, verdict=verdict, wf_results=wf_results,
            diagnostic=diagnostic,
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("FAIL diagnostic report: %s", path)
        log.info(
            "Failure modes: %s",
            [m.label for m in diagnostic.failure_modes],
        )

    log.info("=== F3.D portfolio run %s done ===", run_id)
    return 0 if verdict.overall_pass else 2


if __name__ == "__main__":
    sys.exit(main())
