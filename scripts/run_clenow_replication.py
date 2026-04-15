#!/usr/bin/env python3
"""Run the Clenow ``stocks_on_the_move`` replication backtest.

Fetches S&P 500 daily OHLCV from Yahoo Finance, reconstructs point-in-time
membership from Wikipedia, runs the Clenow momentum strategy through the
ai-trade backtest engine, and generates a Markdown + PNG report in
``--output-dir``.

Usage
-----
    .venv/bin/python scripts/run_clenow_replication.py \\
        --start 2022-01-01 --end 2023-12-31 \\
        --cash 100000 --output-dir reports/

Notes
-----
* **Cold-cache first run takes 20-40 minutes.** ~500 Yahoo fetches (one per
  ticker) at the unofficial rate limit. Subsequent runs use the parquet
  cache in ``.cache/yfinance/``.
* **Warmup.** The strategy needs ~200 days before ``--start`` so the SPX
  200-day MA and the per-stock 90-day regression have enough history. The
  script fetches ``--warmup-days`` extra trading days before ``--start``;
  the Runner iterates only over ``[start, end]`` so the equity curve starts
  at ``--start``.
* **Survivorship bias.** The yfinance+Wikipedia pipeline is severely
  survivorship-biased (current-ticker-only fetch, missing delistings). The
  generated report carries a mandatory disclaimer; migrate to a paid
  survivorship-free feed before trusting any gate decision (ROADMAP
  §"Deferred decisions").
* **Validation coverage.** A single-trial replication (fixed Clenow
  parameters) produces one equity curve. Walk-forward stats on that curve
  are reported as a sanity check. CPCV/PBO/DSR require a grid of strategy
  variants (multiple parameter sets tested under common splits); they are
  out of scope for a basic replication and will be wired in Phase 3 once
  we evaluate the Clenow vs. alternatives grid.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd


log = logging.getLogger("ai_trade.scripts.clenow")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Run Clenow momentum replication on yfinance+Wikipedia data."
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
        "--index-symbol",
        default="^GSPC",
        help="Yahoo ticker for the regime-filter index (default: ^GSPC).",
    )
    ap.add_argument(
        "--warmup-days",
        type=int,
        default=500,
        help="Calendar days of history to fetch before --start (default: 500).",
    )
    ap.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


def _walk_forward_on_equity(
    equity: pd.Series, n_windows: int = 8
) -> dict[str, Any] | None:
    """Compute walk-forward stats on a single realized equity curve.

    Splits the curve into ``n_windows`` contiguous chunks, computes per-window
    return and max drawdown, then runs the ai-trade walk-forward gate
    (rule #5: ≥ 8 windows, ≥ 6/8 profitable, max DD ≤ 25%).
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
    from ai_trade.backtest.data.wikipedia_spx import WikipediaSPX
    from ai_trade.backtest.data.yfinance_source import YFinanceSource
    from ai_trade.backtest.engine import (
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.metrics.report import generate_report
    from ai_trade.backtest.strategies.clenow_momentum import (
        ClenowMomentumStrategy,
    )

    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    fetch_start = args.start - timedelta(days=args.warmup_days)

    log.info("Loading Wikipedia SPX tables")
    wiki = WikipediaSPX()
    universe_at_start = wiki.constituents_on(args.start)
    log.info(
        "Point-in-time universe on %s: %d tickers",
        args.start,
        len(universe_at_start),
    )

    tickers = sorted(universe_at_start)
    if args.index_symbol not in tickers:
        tickers.append(args.index_symbol)

    log.info(
        "Fetching %d tickers from %s to %s (first run may take 30 min)",
        len(tickers),
        fetch_start,
        args.end,
    )
    src = YFinanceSource()
    raw = src.fetch_many(tickers, fetch_start, args.end)
    data = {t: df for t, df in raw.items() if not df.empty}
    dropped = len(raw) - len(data)
    if dropped:
        log.warning(
            "yfinance returned no data for %d tickers — survivorship bias "
            "materialized (delisted/renamed/unknown tickers)",
            dropped,
        )

    if args.index_symbol not in data:
        log.error("No data for index %s — cannot run regime filter", args.index_symbol)
        return 1

    available = set(data.keys())

    def constituents_on(d: date) -> set[str]:
        return wiki.constituents_on(d) & available

    log.info("Building Clenow strategy")
    strategy = ClenowMomentumStrategy(
        data=data,
        constituents_provider=constituents_on,
        index_symbol=args.index_symbol,
    )

    # Bound the Runner to [start, end]; strategy still reads the full
    # ``data`` dict for lookbacks, so the 200d MA / 90d regression have
    # warmup.
    data_bounded = {
        t: df.loc[pd.Timestamp(args.start):pd.Timestamp(args.end)]
        for t, df in data.items()
    }
    data_bounded = {t: df for t, df in data_bounded.items() if not df.empty}

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
        strategy_name="clenow_momentum",
        output_dir=args.output_dir,
        data_source="yfinance",
    )
    log.info("Report written: %s", report_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
