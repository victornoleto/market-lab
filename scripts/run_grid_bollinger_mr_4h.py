#!/usr/bin/env python3
"""Bollinger MR grid on 4h resampled SPY data.

Fetches SPY 1h from Tiingo (cached), resamples to 4h by grouping every
4 consecutive bars, then runs the same 2×2 grid (N=4) with adjusted
max_hold and periods_per_year.

Lead #10: longer timeframe variant — same logic, fewer bars, less noise.
[algo_trading_chan, p.28-30, ch.2]

Resampling: bar-based (every 4 consecutive 1h bars → 1 OHLCV bar).
US equity has ~6 bars/day at 1h → ~1.5 bars/day at 4h → ~391 bars/year.
max_hold adjusted from 24 (1h) to 6 (4h) ≈ same calendar duration.
"""

from __future__ import annotations

import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

log = logging.getLogger("ai_trade.grid.bollinger_mr_4h")


def resample_bars(df: pd.DataFrame, n: int = 4) -> pd.DataFrame:
    """Group every *n* consecutive 1h bars into one OHLCV bar.

    Standard aggregation: O=first, H=max, L=min, C=last, V=sum.
    The timestamp of each output bar is the timestamp of its LAST input bar.
    """
    n_full = (len(df) // n) * n
    df_trim = df.iloc[:n_full]
    groups = np.arange(n_full) // n
    agg = df_trim.groupby(groups).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    })
    # Use the last timestamp in each group as the index
    agg.index = df_trim.index[n - 1::n][:len(agg)]
    return agg


def main() -> int:
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
        compose_observers,
        setup_grid_logging,
        wf_for_grid,
    )
    from ai_trade.backtest.grid.bollinger_mr_config import (
        BollingerMRGridConfig,
        bollinger_mr_grid_configs,
    )
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    run_id = f"grid_bollinger_mr_spy_4h_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    output_dir = Path("reports") / run_id
    checkpoint_dir = Path(".cache/grid_runs")
    run_checkpoint_dir = checkpoint_dir / run_id
    run_checkpoint_dir.mkdir(parents=True, exist_ok=True)
    unified_log_path = Path("logs/grid.log")

    setup_grid_logging(
        run_id=run_id,
        run_dir=run_checkpoint_dir,
        unified_log_path=unified_log_path,
        level=logging.INFO,
    )

    log.info("=== 4h resampled Bollinger MR grid: %s ===", run_id)

    # --- Fetch 1h data ---
    start = date(2021, 1, 1)
    end = date(2025, 12, 31)
    warmup_days = 100
    symbol = "SPY"
    cash = 100_000.0

    src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
    fetch_start = start - timedelta(days=warmup_days)
    raw = src.fetch_many([symbol], fetch_start, end, asset_class="etf", frequency="1hour")
    if symbol not in raw or raw[symbol].empty:
        log.error("No 1h data for %s", symbol)
        return 1

    df_1h = raw[symbol]
    log.info("1h data: %d bars [%s, %s]", len(df_1h), df_1h.index[0], df_1h.index[-1])

    # --- Resample to 4h ---
    df_4h = resample_bars(df_1h, n=4)
    log.info("4h data: %d bars [%s, %s]", len(df_4h), df_4h.index[0], df_4h.index[-1])

    # Bound to requested range
    data_full = {symbol: df_4h}
    data_bounded = {
        symbol: df_4h.loc[pd.Timestamp(start):pd.Timestamp(end)]
    }
    if data_bounded[symbol].empty:
        log.error("Bounded range empty after resample")
        return 1
    log.info("Bounded 4h: %d bars", len(data_bounded[symbol]))

    # --- Grid configs with adjusted max_hold ---
    # max_hold=6 on 4h ≈ max_hold=24 on 1h (same calendar duration: ~4 trading days)
    configs_4h = [
        BollingerMRGridConfig(window=cfg.window, std_mult=cfg.std_mult,
                              stop_pct=cfg.stop_pct, max_hold=6,
                              risk_pct_of_equity=cfg.risk_pct_of_equity)
        for cfg in bollinger_mr_grid_configs()
    ]
    log.info("Grid: %d configs (N=%d for DSR), max_hold=6", len(configs_4h), len(configs_4h))
    for i, c in enumerate(configs_4h):
        log.info("  config %d: window=%d, std_mult=%.1f, stop=%.2f, max_hold=%d",
                 i, c.window, c.std_mult, c.stop_pct, c.max_hold)

    # periods_per_year: ~391 4h bars/year for SPY
    # (7818 1h bars / 5 years / 4 = ~391)
    bars_in_range = len(data_bounded[symbol])
    years = (pd.Timestamp(end) - pd.Timestamp(start)).days / 365.25
    periods_per_year = int(round(bars_in_range / years))
    log.info("periods_per_year=%d (bars=%d, years=%.1f)", periods_per_year, bars_in_range, years)

    def trial_fn(cfg: BollingerMRGridConfig):
        strategy = BollingerMRStrategy(
            data=data_full,
            symbol=symbol,
            window=cfg.window,
            std_mult=cfg.std_mult,
            stop_pct=cfg.stop_pct,
            max_hold=cfg.max_hold,
            risk_pct_of_equity=cfg.risk_pct_of_equity,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        return runner.run(
            strategy=strategy, data=data_bounded, initial_cash=cash,
        )

    pbar = tqdm(total=len(configs_4h), desc=f"grid {run_id}", unit="cfg")

    def tqdm_observer(completed: int, total: int, trial) -> None:
        pbar.update(1)
        pbar.set_postfix({
            "cfg_id": trial.config_id,
            "status": trial.status,
            "sharpe": f"{trial.sharpe:.2f}" if trial.status == "ok" else "—",
        })

    observer = compose_observers(
        JsonlTrialObserver(path=run_checkpoint_dir / "trials.jsonl", run_id=run_id),
        StatusFileObserver(path=run_checkpoint_dir / "status.md", run_id=run_id),
        tqdm_observer,
    )

    grid = GridRunner(
        checkpoint_dir=checkpoint_dir,
        n_jobs=4,
        config_cls=BollingerMRGridConfig,
        periods_per_year=periods_per_year,
    ).run(
        configs=configs_4h, trial_fn=trial_fn, run_id=run_id,
        progress_cb=observer,
    )
    pbar.close()

    log.info("Grid complete: %d/%d OK", len(grid.ok_trials), len(grid.trials))
    for t in grid.ok_trials:
        n_trades = len(t.result.trades) if t.result else 0
        log.info("  config %d: Sharpe=%.3f, CAGR=%.2f%%, MaxDD=%.2f%%, #trades=%d",
                 t.config_id, t.sharpe, t.cagr * 100, t.max_drawdown * 100, n_trades)

    log.info("Running walk-forward (n_windows=8)")
    wf_results = wf_for_grid(grid, n_windows=8, n_jobs=4)

    log.info("Evaluating gates")
    verdict = GateEvaluator().evaluate(
        grid=grid,
        wf_verdicts={cid: wf.verdict for cid, wf in wf_results.items()},
    )
    pbo_val = float(verdict.pbo_result.pbo) if verdict.pbo_result else float("nan")
    log.info(
        "VERDICT: overall_pass=%s PBO=%.3f DSR_pass=%d/%d WF_pass=%d/%d best_config=%s",
        verdict.overall_pass, pbo_val,
        len(verdict.dsr_pass_ids), len(verdict.dsr_results),
        len(verdict.wf_pass_ids), len(verdict.wf_verdicts),
        verdict.best_config_id,
    )

    # Print per-config DSR details
    for cid, dsr_r in sorted(verdict.dsr_results.items()):
        log.info("  DSR config %d: p=%.4f, observed_sharpe=%.4f, pass=%s",
                 cid, dsr_r.p_value, dsr_r.observed_sharpe, cid in verdict.dsr_pass_ids)

    # Print per-config WF details
    for cid, wfv in sorted(verdict.wf_verdicts.items()):
        log.info("  WF config %d: verdict=%s, pass=%s",
                 cid, wfv, cid in verdict.wf_pass_ids)

    # Write report
    output_dir.mkdir(parents=True, exist_ok=True)
    report_gen = GridReportGenerator()
    if verdict.overall_pass:
        path = report_gen.write_pass_report(
            grid=grid, verdict=verdict, wf_results=wf_results,
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("★ PASS report: %s", path)
    else:
        diagnostic = DiagnosticAnalyzer().analyze(
            grid=grid, verdict=verdict, wf_results=wf_results,
        )
        path = report_gen.write_fail_report(
            grid=grid, verdict=verdict, wf_results=wf_results,
            diagnostic=diagnostic,
            output_dir=output_dir, data_source="tiingo",
        )
        log.info("FAIL report: %s", path)
        log.info("Failure modes: %s", [m.label for m in diagnostic.failure_modes])

    log.info("=== done ===")
    return 0 if verdict.overall_pass else 2


if __name__ == "__main__":
    sys.exit(main())
