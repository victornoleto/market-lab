#!/usr/bin/env python3
"""Out-of-sample hold-out test for Bollinger MR best config on SPY 1h.

Runs the fixed best config (window=20, std_mult=1.5, stop_pct=0.02,
max_hold=24) on a pure OOS period (2025-01-01 to 2025-12-31).

The config was selected on 2021-2024 data. This test verifies
temporal robustness — the edge didn't decay in 2025.

Citations:
- Config selected from [algo_trading_chan, p.28-30, ch.2].
- OOS validation protocol: [advances_fin_ml, p.208-211, ch.12].
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import (
        BacktestResult,
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    ap = argparse.ArgumentParser(description="OOS hold-out test for Bollinger MR")
    ap.add_argument("--symbol", default="SPY")
    ap.add_argument("--oos-start", type=date.fromisoformat, default=date(2025, 1, 1))
    ap.add_argument("--oos-end", type=date.fromisoformat, default=date(2025, 12, 31))
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    # Fixed best config from training (2021-2024):
    ap.add_argument("--window", type=int, default=20)
    ap.add_argument("--std-mult", type=float, default=1.5)
    ap.add_argument("--stop-pct", type=float, default=0.02)
    ap.add_argument("--max-hold", type=int, default=24)
    args = ap.parse_args(argv)

    # Fetch data with warmup for MA calculation.
    warmup_days = 100
    fetch_start = args.oos_start - timedelta(days=warmup_days)
    print(f"Fetching {args.symbol} 1h: {fetch_start} → {args.oos_end}")

    src = TiingoSource(storage=TiingoStorage(root=args.storage_root))
    raw = src.fetch_many(
        [args.symbol], fetch_start, args.oos_end,
        asset_class="etf", frequency="1hour",
    )
    if args.symbol not in raw or raw[args.symbol].empty:
        print(f"ERROR: No data for {args.symbol}")
        return 1

    data_full = {args.symbol: raw[args.symbol]}
    data_oos = {
        args.symbol: raw[args.symbol].loc[
            pd.Timestamp(args.oos_start):pd.Timestamp(args.oos_end)
        ]
    }

    n_bars_oos = len(data_oos[args.symbol])
    print(f"OOS period: {args.oos_start} → {args.oos_end}, {n_bars_oos} bars")

    if n_bars_oos == 0:
        print("ERROR: No OOS data")
        return 1

    # Run the strategy with fixed config.
    strategy = BollingerMRStrategy(
        data=data_full,
        symbol=args.symbol,
        window=args.window,
        std_mult=args.std_mult,
        stop_pct=args.stop_pct,
        max_hold=args.max_hold,
        risk_pct_of_equity=0.95,
    )
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result: BacktestResult = runner.run(
        strategy=strategy, data=data_oos, initial_cash=args.cash,
    )

    # Compute metrics.
    eq = result.equity_curve
    periods_per_year = 252 * 7  # 1h bars

    # Returns and Sharpe.
    returns = eq.pct_change().dropna()
    if len(returns) < 2:
        print("ERROR: Too few bars for metric computation")
        return 1

    mean_ret = float(returns.mean())
    std_ret = float(returns.std())
    sharpe = (mean_ret / std_ret) * np.sqrt(periods_per_year) if std_ret > 0 else 0.0

    # CAGR.
    n_years = n_bars_oos / periods_per_year
    total_return = result.final_equity / args.cash
    cagr = total_return ** (1 / n_years) - 1 if n_years > 0 else 0.0

    # Max drawdown.
    peak = eq.cummax()
    dd = (eq - peak) / peak
    max_dd = float(dd.min())

    # Trade stats.
    n_trades = len(result.trades)
    if n_trades > 0:
        wins = sum(1 for t in result.trades if t.pnl > 0)
        win_rate = wins / n_trades
        avg_pnl = sum(t.pnl for t in result.trades) / n_trades
        total_pnl = sum(t.pnl for t in result.trades)
    else:
        win_rate = avg_pnl = total_pnl = 0.0

    # Also compute metrics for the training period (2021-2024) using same config.
    print("\n--- Training period comparison (2021-2024) ---")
    train_start = date(2021, 1, 1)
    train_end = date(2024, 12, 31)
    train_fetch_start = train_start - timedelta(days=warmup_days)
    raw_train = src.fetch_many(
        [args.symbol], train_fetch_start, train_end,
        asset_class="etf", frequency="1hour",
    )
    data_train_full = {args.symbol: raw_train[args.symbol]}
    data_train_bounded = {
        args.symbol: raw_train[args.symbol].loc[
            pd.Timestamp(train_start):pd.Timestamp(train_end)
        ]
    }
    n_bars_train = len(data_train_bounded[args.symbol])
    print(f"Training period: {train_start} → {train_end}, {n_bars_train} bars")

    strategy_train = BollingerMRStrategy(
        data=data_train_full,
        symbol=args.symbol,
        window=args.window,
        std_mult=args.std_mult,
        stop_pct=args.stop_pct,
        max_hold=args.max_hold,
        risk_pct_of_equity=0.95,
    )
    result_train = runner.run(
        strategy=strategy_train, data=data_train_bounded, initial_cash=args.cash,
    )

    eq_train = result_train.equity_curve
    ret_train = eq_train.pct_change().dropna()
    mean_t = float(ret_train.mean())
    std_t = float(ret_train.std())
    sharpe_train = (mean_t / std_t) * np.sqrt(periods_per_year) if std_t > 0 else 0.0
    n_years_train = n_bars_train / periods_per_year
    total_ret_train = result_train.final_equity / args.cash
    cagr_train = total_ret_train ** (1 / n_years_train) - 1 if n_years_train > 0 else 0.0
    peak_t = eq_train.cummax()
    dd_t = (eq_train - peak_t) / peak_t
    max_dd_train = float(dd_t.min())
    n_trades_train = len(result_train.trades)
    wins_train = sum(1 for t in result_train.trades if t.pnl > 0) if n_trades_train else 0
    wr_train = wins_train / n_trades_train if n_trades_train else 0.0

    # Print results.
    print("\n" + "=" * 60)
    print("BOLLINGER MR OOS HOLD-OUT TEST — SPY 1h")
    print(f"Config: w={args.window}, std={args.std_mult}, stop={args.stop_pct}, max_hold={args.max_hold}")
    print("=" * 60)

    print(f"\n{'Metric':<25} {'Training (2021-24)':<20} {'OOS (2025)':<20}")
    print("-" * 65)
    print(f"{'Bars':<25} {n_bars_train:<20} {n_bars_oos:<20}")
    print(f"{'Sharpe (ann.)':<25} {sharpe_train:<20.3f} {sharpe:<20.3f}")
    print(f"{'CAGR':<25} {cagr_train*100:<19.2f}% {cagr*100:<19.2f}%")
    print(f"{'Max DD':<25} {max_dd_train*100:<19.2f}% {max_dd*100:<19.2f}%")
    print(f"{'Final equity':<25} ${result_train.final_equity:<19,.0f} ${result.final_equity:<19,.0f}")
    print(f"{'# Trades':<25} {n_trades_train:<20} {n_trades:<20}")
    print(f"{'Win rate':<25} {wr_train*100:<19.1f}% {win_rate*100:<19.1f}%")

    # Verdict.
    print("\n--- OOS Verdict ---")
    oos_profitable = result.final_equity > args.cash
    sharpe_holds = sharpe > 0.5  # reasonable OOS threshold
    dd_ok = max_dd > -0.25
    print(f"OOS Profitable: {'YES' if oos_profitable else 'NO'} (final=${result.final_equity:,.0f})")
    print(f"OOS Sharpe > 0.5: {'YES' if sharpe_holds else 'NO'} (Sharpe={sharpe:.3f})")
    print(f"OOS Max DD > -25%: {'YES' if dd_ok else 'NO'} (DD={max_dd*100:.2f}%)")

    sharpe_decay = (sharpe - sharpe_train) / sharpe_train * 100 if sharpe_train != 0 else 0
    print(f"Sharpe decay vs training: {sharpe_decay:+.1f}%")

    if oos_profitable and sharpe_holds and dd_ok:
        print("\n★ OOS PASS — Edge persists in 2025. Strategy is temporally robust.")
    elif oos_profitable:
        print("\n◐ OOS MARGINAL — Profitable but Sharpe/DD degraded. Use with caution.")
    else:
        print("\n✗ OOS FAIL — Edge did not persist in 2025.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
