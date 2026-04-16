#!/usr/bin/env python3
"""Out-of-sample hold-out test for Kalman pairs best config on SPY-IWM 1h.

Runs the fixed best config (delta=1e-5, entry_z=1.5) from the iter 12 grid
on a pure OOS period (2025-01-01 to 2025-12-31), compared with training
period (2021-2024) under the same config.

The grid was run on 2021-2025 (iter 12) so 2025 was not strictly held out.
This script re-seeds the Kalman filter from the training slice, then runs
it on each period separately, giving a clean view of temporal robustness.

Citations:
- Kalman state [α_t, β_t] evolves each bar via Q=δ·I
  `[algo_trading_chan, p.76-80, ch.3]`.
- OOS validation protocol: `[advances_fin_ml, p.208-211, ch.12]`.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def _run_period(
    src, long_sym: str, short_sym: str,
    period_start: date, period_end: date,
    warmup_days: int, cash: float,
    delta: float, entry_z: float,
    asset_class: str, storage_root: Path,
):
    from ai_trade.backtest.engine import (
        ExecutionConfig, ExecutionSimulator, Runner,
    )
    from ai_trade.backtest.strategies.kalman_pairs import KalmanPairsStrategy

    fetch_start = period_start - timedelta(days=warmup_days)
    raw = src.fetch_many(
        [long_sym, short_sym], fetch_start, period_end,
        asset_class=asset_class, frequency="1hour",
    )
    # Align to common index.
    df_l = raw[long_sym]
    df_s = raw[short_sym]
    common = df_l.index.intersection(df_s.index)
    df_l = df_l.loc[common]
    df_s = df_s.loc[common]
    data_full = {long_sym: df_l, short_sym: df_s}

    data_bounded = {
        long_sym: df_l.loc[pd.Timestamp(period_start):pd.Timestamp(period_end)],
        short_sym: df_s.loc[pd.Timestamp(period_start):pd.Timestamp(period_end)],
    }

    n_bars = len(data_bounded[long_sym])
    if n_bars == 0:
        return None, 0

    strategy = KalmanPairsStrategy(
        data=data_full,
        long_symbol=long_sym, short_symbol=short_sym,
        delta=delta, entry_z=entry_z,
    )
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(
        strategy=strategy, data=data_bounded, initial_cash=cash,
    )
    return result, n_bars


def _metrics(result, n_bars: int, cash: float) -> dict:
    eq = result.equity_curve
    periods_per_year = 252 * 7
    returns = eq.pct_change().dropna()
    if len(returns) < 2:
        return {}
    mean_ret = float(returns.mean())
    std_ret = float(returns.std())
    sharpe = (
        (mean_ret / std_ret) * np.sqrt(periods_per_year)
        if std_ret > 0 else 0.0
    )
    n_years = n_bars / periods_per_year
    total_ret = result.final_equity / cash
    cagr = total_ret ** (1 / n_years) - 1 if n_years > 0 else 0.0
    peak = eq.cummax()
    dd = (eq - peak) / peak
    max_dd = float(dd.min())
    n_trades = len(result.trades)
    wins = sum(1 for t in result.trades if t.pnl > 0)
    wr = wins / n_trades if n_trades else 0.0
    pf = 0.0
    if n_trades:
        gains = sum(t.pnl for t in result.trades if t.pnl > 0)
        losses = -sum(t.pnl for t in result.trades if t.pnl < 0)
        pf = gains / losses if losses > 0 else float("inf")
    return {
        "bars": n_bars, "sharpe": sharpe, "cagr": cagr,
        "max_dd": max_dd, "final": result.final_equity,
        "trades": n_trades, "wr": wr, "pf": pf,
    }


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    ap = argparse.ArgumentParser(
        description="OOS hold-out test for Kalman pairs (SPY-IWM 1h)",
    )
    ap.add_argument("--long-symbol", default="SPY")
    ap.add_argument("--short-symbol", default="IWM")
    ap.add_argument("--train-start", type=date.fromisoformat, default=date(2021, 1, 1))
    ap.add_argument("--train-end", type=date.fromisoformat, default=date(2024, 12, 31))
    ap.add_argument("--oos-start", type=date.fromisoformat, default=date(2025, 1, 1))
    ap.add_argument("--oos-end", type=date.fromisoformat, default=date(2025, 12, 31))
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--asset-class", default="etf")
    # Fixed best config from iter 12 grid:
    ap.add_argument("--delta", type=float, default=1e-5)
    ap.add_argument("--entry-z", type=float, default=1.5)
    # Kalman init_train_bars default 500 → warmup_days ~90 gives ~630 bars at 7h/day
    ap.add_argument("--warmup-days", type=int, default=180)
    args = ap.parse_args(argv)

    src = TiingoSource(storage=TiingoStorage(root=args.storage_root))

    print(f"Kalman pairs OOS: {args.long_symbol}-{args.short_symbol}")
    print(f"Config: delta={args.delta}, entry_z={args.entry_z}")
    print(
        f"Train: {args.train_start} → {args.train_end} | "
        f"OOS: {args.oos_start} → {args.oos_end}",
    )

    print("\n--- Running training period ---")
    train_res, train_bars = _run_period(
        src, args.long_symbol, args.short_symbol,
        args.train_start, args.train_end,
        args.warmup_days, args.cash,
        args.delta, args.entry_z,
        args.asset_class, args.storage_root,
    )
    if train_res is None:
        print("ERROR: no training data")
        return 1
    train = _metrics(train_res, train_bars, args.cash)
    print(
        f"Train bars={train['bars']}  Sharpe={train['sharpe']:.3f}  "
        f"CAGR={train['cagr']*100:.2f}%  DD={train['max_dd']*100:.2f}%  "
        f"Trades={train['trades']}  WR={train['wr']*100:.1f}%",
    )

    print("\n--- Running OOS period ---")
    oos_res, oos_bars = _run_period(
        src, args.long_symbol, args.short_symbol,
        args.oos_start, args.oos_end,
        args.warmup_days, args.cash,
        args.delta, args.entry_z,
        args.asset_class, args.storage_root,
    )
    if oos_res is None:
        print("ERROR: no OOS data")
        return 1
    oos = _metrics(oos_res, oos_bars, args.cash)
    print(
        f"OOS bars={oos['bars']}  Sharpe={oos['sharpe']:.3f}  "
        f"CAGR={oos['cagr']*100:.2f}%  DD={oos['max_dd']*100:.2f}%  "
        f"Trades={oos['trades']}  WR={oos['wr']*100:.1f}%",
    )

    print("\n" + "=" * 60)
    print(f"KALMAN PAIRS OOS HOLD-OUT — {args.long_symbol}-{args.short_symbol} 1h")
    print(f"Config: delta={args.delta}, entry_z={args.entry_z}")
    print("=" * 60)
    print(f"\n{'Metric':<22} {'Training (21-24)':<20} {'OOS (2025)':<20}")
    print("-" * 62)
    print(f"{'Bars':<22} {train['bars']:<20} {oos['bars']:<20}")
    print(f"{'Sharpe':<22} {train['sharpe']:<20.3f} {oos['sharpe']:<20.3f}")
    print(f"{'CAGR':<22} {train['cagr']*100:<19.2f}% {oos['cagr']*100:<19.2f}%")
    print(f"{'Max DD':<22} {train['max_dd']*100:<19.2f}% {oos['max_dd']*100:<19.2f}%")
    print(f"{'Final equity':<22} ${train['final']:<19,.0f} ${oos['final']:<19,.0f}")
    print(f"{'# Trades':<22} {train['trades']:<20} {oos['trades']:<20}")
    print(f"{'Win rate':<22} {train['wr']*100:<19.1f}% {oos['wr']*100:<19.1f}%")
    print(
        f"{'Profit factor':<22} {train['pf']:<20.2f} "
        f"{oos['pf']:<20.2f}",
    )

    print("\n--- OOS Verdict ---")
    oos_profitable = oos["final"] > args.cash
    sharpe_holds = oos["sharpe"] > 0.3  # lower bar than Bollinger: Kalman baseline is 0.55
    dd_ok = oos["max_dd"] > -0.25
    print(
        f"OOS Profitable: {'YES' if oos_profitable else 'NO'} "
        f"(final=${oos['final']:,.0f})",
    )
    print(
        f"OOS Sharpe > 0.3: {'YES' if sharpe_holds else 'NO'} "
        f"(Sharpe={oos['sharpe']:.3f})",
    )
    print(
        f"OOS Max DD > -25%: {'YES' if dd_ok else 'NO'} "
        f"(DD={oos['max_dd']*100:.2f}%)",
    )
    if train["sharpe"] != 0:
        decay = (oos["sharpe"] - train["sharpe"]) / abs(train["sharpe"]) * 100
        print(f"Sharpe decay vs training: {decay:+.1f}%")
    if oos_profitable and sharpe_holds and dd_ok:
        print("\n★ OOS PASS — Edge persists in 2025. Kalman pairs is temporally robust.")
    elif oos_profitable:
        print("\n◐ OOS MARGINAL — Profitable but Sharpe/DD degraded. Use with caution.")
    else:
        print("\n✗ OOS FAIL — Edge did not persist in 2025.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
