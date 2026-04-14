#!/usr/bin/env python3
"""Run the Ehlers Band-Pass Swing Trader replication backtest.

Single-instrument swing trading on daily OHLCV for ``--symbol`` (default
``^GSPC``). Fetches from Yahoo Finance, runs the Ehlers Band-Pass Swing
strategy with literature defaults, and writes a Markdown + PNG report to
``--output-dir``.

Usage
-----
    .venv/bin/python scripts/run_ehlers_replication.py \\
        --start 2022-01-01 --end 2023-12-31 \\
        --cash 100000 --output-dir reports/

Notes
-----
* **Single-trial.** Runs one fixed config (``hp_period=48, lp_period=10,
  pct_of_dcp=0.90, stop_pct=0.05`` — defaults from [cycle_analytics, ch.7
  p.77 text example; p.152-153 tuning; p.225-226 stop]). To search the
  parameter grid and apply PBO/DSR gates, use ``run_grid_ehlers.py``
  (Commit 9 of this Execução).
* **Warmup.** The roofing filter needs ~2·hp_period bars, the Homodyne
  DCP another ~50 for its EMA cascades to converge. The script fetches
  ``--warmup-days`` extra trading days before ``--start``; the Runner
  iterates only over ``[start, end]`` so the equity curve starts at
  ``--start`` but with indicators already converged.
* **Survivorship bias.** Single-instrument on the SPX index is lightly
  affected (index prices are themselves biased by continuous-constituent
  weighting), but the report still carries the standard disclaimer.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd


log = logging.getLogger("ai_trade.scripts.ehlers")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Run Ehlers Band-Pass Swing Trader replication on yfinance data."
    )
    ap.add_argument(
        "--start",
        type=date.fromisoformat,
        required=True,
        help="First backtest date (YYYY-MM-DD).",
    )
    ap.add_argument(
        "--end",
        type=date.fromisoformat,
        required=True,
        help="Last backtest date (YYYY-MM-DD).",
    )
    ap.add_argument(
        "--symbol",
        default="^GSPC",
        help="Yahoo ticker to trade (default: ^GSPC).",
    )
    ap.add_argument(
        "--cash",
        type=float,
        default=100_000.0,
        help="Initial cash in USD (default: 100000).",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports"),
        help="Directory for the Markdown report + PNG assets.",
    )
    ap.add_argument(
        "--warmup-days",
        type=int,
        default=500,
        help="Calendar days of history to fetch before --start (default: 500).",
    )
    ap.add_argument("--hp-period", type=int, default=48)
    ap.add_argument("--lp-period", type=int, default=10)
    ap.add_argument("--pct-of-dcp", type=float, default=0.90)
    ap.add_argument("--stop-pct", type=float, default=0.05)
    ap.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


def _walk_forward_on_equity(
    equity: pd.Series, n_windows: int = 8
) -> dict[str, Any] | None:
    """Walk-forward stats on a single realised equity curve.

    Mirrors the helper in ``run_clenow_replication.py``: splits into
    ``n_windows`` contiguous chunks, computes per-window return and max
    drawdown, then runs ``walk_forward_gate`` (rule #5).
    """
    from ai_trade.backtest.validation.walk_forward import walk_forward_gate

    n = len(equity)
    if n < n_windows * 10:
        return None

    size = n // n_windows
    returns: list[float] = []
    drawdowns: list[float] = []
    for i in range(n_windows):
        start = i * size
        stop = start + size if i < n_windows - 1 else n
        window = equity.iloc[start:stop]
        if len(window) < 2:
            continue
        returns.append(float(window.iloc[-1] / window.iloc[0] - 1.0))
        peak = window.cummax()
        drawdowns.append(float(((peak - window) / peak).max()))

    return {
        "n_windows": len(returns),
        "n_profitable": sum(1 for r in returns if r > 0),
        "max_drawdown": max(drawdowns) if drawdowns else 0.0,
        "verdict": walk_forward_gate(returns, drawdowns),
    }


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.yfinance_source import YFinanceSource
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.metrics.report import generate_report
    from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    fetch_start = args.start - timedelta(days=args.warmup_days)

    log.info(
        "Fetching %s from %s to %s (warmup %d days)",
        args.symbol,
        fetch_start,
        args.end,
        args.warmup_days,
    )
    src = YFinanceSource()
    raw = src.fetch_many([args.symbol], fetch_start, args.end)
    if args.symbol not in raw or raw[args.symbol].empty:
        log.error("No data for %s — cannot run backtest", args.symbol)
        return 1
    data = {args.symbol: raw[args.symbol]}

    log.info(
        "Building Ehlers BP Swing strategy (hp=%d, lp=%d, pct=%.2f, stop=%.3f)",
        args.hp_period,
        args.lp_period,
        args.pct_of_dcp,
        args.stop_pct,
    )
    strategy = EhlersBPSwingStrategy(
        data=data,
        symbol=args.symbol,
        hp_period=args.hp_period,
        lp_period=args.lp_period,
        pct_of_dcp=args.pct_of_dcp,
        stop_pct=args.stop_pct,
    )

    # Bound the Runner to [start, end] — indicators are pre-computed on
    # the full ``data`` so their IIR warm-up is absorbed by the warmup
    # window before --start.
    df = data[args.symbol]
    data_bounded = {
        args.symbol: df.loc[pd.Timestamp(args.start): pd.Timestamp(args.end)]
    }
    if data_bounded[args.symbol].empty:
        log.error("Bounded range [%s, %s] is empty", args.start, args.end)
        return 1

    log.info("Running engine")
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(
        strategy=strategy, data=data_bounded, initial_cash=args.cash
    )
    log.info(
        "Final equity: $%.2f (from $%.2f) | trades=%d | fills=%d",
        result.final_equity,
        args.cash,
        len(result.trades),
        len(result.fills),
    )

    validation: dict[str, Any] = {}
    wf = _walk_forward_on_equity(result.equity_curve)
    if wf is not None:
        validation["walk_forward"] = wf
        log.info(
            "Walk-forward: %d windows | %d profitable | max DD=%.2f%% | %s",
            wf["n_windows"],
            wf["n_profitable"],
            wf["max_drawdown"] * 100,
            wf["verdict"],
        )

    log.info("Generating report → %s", args.output_dir)
    report_path = generate_report(
        result=result,
        validation=validation,
        strategy_name="ehlers_bp_swing",
        output_dir=args.output_dir,
        data_source="yfinance",
    )
    log.info("Report written: %s", report_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
