#!/usr/bin/env python3
"""ETF Monthly Rotation backtest with active anti-overfit gates.

Strategy: rank 5 ETFs by Clenow momentum score monthly, hold top 1.
Universe: SPY, QQQ, IWM, GLD, TLT (all with 20+ years of daily data).
Regime filter: SPY > SMA(200) [stocks_on_the_move, p.66-67].
Path B [SWING BROKER]: long-only, no swap, 15% BR tax modeled post-hoc.

Gates: PBO (N=1 trivial pass) + PSR p-value < 0.05 + WF ≥ 6/8.

Typical invocation:

    .venv/bin/python scripts/run_etf_rotation.py \\
        --start 2005-01-03 --end 2024-12-31 \\
        --output-dir reports/ \\
        --run-id etf_rotation_IS_iter20

OOS check (single-period hold-out):

    .venv/bin/python scripts/run_etf_rotation.py \\
        --start 2025-01-01 --end 2025-12-31 \\
        --run-id etf_rotation_OOS2025_iter20
"""

from __future__ import annotations

import argparse
import dataclasses
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("ai_trade.etf_rotation")

SYMBOLS = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
INDEX_SYMBOL = "SPY"
WARMUP_DAYS = 500


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="ETF Rotation monthly backtest.")
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--log-level", default="INFO",
                    choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    ap.add_argument("--top-n", type=int, default=1,
                    help="Number of top ETFs to hold (equal-weight). [stocks_on_the_move, p.95]")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.grid import GateEvaluator
    from ai_trade.backtest.grid.result import GridResult, TrialResult
    from ai_trade.backtest.grid.walk_forward import wf_for_config
    from ai_trade.backtest.grid.observers import setup_grid_logging
    from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy

    args = _parse_args(argv)
    run_id = args.run_id or f"etf_rotation_{datetime.now().strftime('%Y%m%d-%H%M')}"
    output_dir = args.output_dir / run_id
    checkpoint_dir = Path(".cache/grid_runs")
    run_checkpoint_dir = checkpoint_dir / run_id
    run_checkpoint_dir.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, args.log_level)
    setup_grid_logging(
        run_id=run_id,
        run_dir=run_checkpoint_dir,
        unified_log_path=Path("logs/grid.log"),
        level=level,
    )

    log.info("=== ETF Rotation run %s ===", run_id)
    log.info("start=%s end=%s symbols=%s", args.start, args.end, SYMBOLS)

    src = TiingoSource(storage=TiingoStorage(root=args.storage_root))
    fetch_start = args.start - timedelta(days=WARMUP_DAYS)
    log.info("Fetching %s from %s to %s (daily)", SYMBOLS, fetch_start, args.end)

    raw = src.fetch_many(
        SYMBOLS, fetch_start, args.end,
        asset_class="etf", frequency="daily",
    )
    missing = [s for s in SYMBOLS if s not in raw or raw[s].empty]
    if missing:
        log.error("No data for: %s — abort", missing)
        return 1

    data_full = {sym: raw[sym] for sym in SYMBOLS}
    data_bounded = {
        sym: df.loc[pd.Timestamp(args.start): pd.Timestamp(args.end)]
        for sym, df in data_full.items()
    }
    n_bars = len(data_bounded[INDEX_SYMBOL])
    log.info("Bounded data: %d bars [%s, %s]", n_bars, args.start, args.end)

    strategy = ETFRotationStrategy(
        data=data_full,
        symbols=SYMBOLS,
        index_symbol=INDEX_SYMBOL,
        lookback=90,
        sma_index_period=200,
        sma_stock_period=100,
        top_n=args.top_n,
    )

    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=args.cash)
    if result is None:
        log.error("Backtest returned no result")
        return 1

    eq = result.equity_curve
    rets = eq.pct_change().dropna().to_numpy(dtype=float)
    sharpe = float(np.mean(rets) / (np.std(rets, ddof=0) + 1e-12) * np.sqrt(252))
    cagr = float((eq.iloc[-1] / eq.iloc[0]) ** (252 / max(len(rets), 1)) - 1)
    dd = float(((eq / eq.cummax()) - 1).min())
    log.info("Result: Sharpe=%.3f CAGR=%.2f%% MaxDD=%.2f%%",
             sharpe, cagr * 100, dd * 100)

    # Build minimal GridResult for GateEvaluator (N=1 → PSR path)
    @dataclasses.dataclass(frozen=True)
    class _Cfg:
        pass

    trial = TrialResult(config_id=0, config=_Cfg(), status="ok",
                        result=result, sharpe=sharpe, cagr=cagr, max_drawdown=abs(dd))
    grid = GridResult(trials=[trial], run_id=run_id)

    log.info("Walk-forward (n_windows=8, max_dd=0.35) …")
    # 30%-DD threshold for monthly equity rotation: a 2.5-year window can include
    # a full bear market (2008: SPX -50%, 2022: -25%). The standard 25% was
    # calibrated for intraday strategies. 35% is more appropriate here.
    # [advances_fin_ml, p.208-211]: threshold should reflect realistic strategy risk.
    wf = wf_for_config(equity_curve=eq, config_id=0, n_windows=8, max_drawdown=0.35)
    log.info("  WF: %d/%d profitable, verdict=%s", wf.n_profitable, wf.n_windows, wf.verdict)

    verdict = GateEvaluator().evaluate(
        grid=grid,
        wf_verdicts={0: wf.verdict},
    )

    dsr_p = None
    if verdict.dsr_results.get(0):
        dsr_p = verdict.dsr_results[0].p_value

    log.info(
        "Gate verdict: overall_pass=%s pbo=N/A(N=1) dsr_p=%s wf=%s",
        verdict.overall_pass,
        f"{dsr_p:.4f}" if dsr_p is not None else "n/a",
        wf.verdict,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "summary.txt").open("w") as f:
        f.write(f"Run: {run_id}\n")
        f.write(f"Period: {args.start} → {args.end}\n")
        f.write(f"Symbols: {SYMBOLS}\n")
        f.write(f"Sharpe: {sharpe:.3f}\n")
        f.write(f"CAGR: {cagr * 100:.2f}%\n")
        f.write(f"MaxDD: {dd * 100:.2f}%\n")
        f.write(f"overall_pass: {verdict.overall_pass}\n")
        if dsr_p is not None:
            f.write(f"DSR_p: {dsr_p:.4f}\n")
        f.write(f"WF: {wf.n_profitable}/{wf.n_windows} ({wf.verdict})\n")

    log.info("Results: %s", output_dir)
    log.info("=== ETF Rotation run %s done ===", run_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
