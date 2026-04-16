#!/usr/bin/env python3
"""Ablation study: Bollinger MR best config WITH vs WITHOUT SMA200 regime filter.

Tests whether adding SMA(200) regime filter improves the already-passing
Bollinger MR strategy on SPY 1h.

Regime filter citation: [stocks_on_the_move, p.110] — "go flat when
the index is below its 200-day moving average" to avoid bear market
drawdowns.

Runs the fixed best config (w=20, std=1.5, stop=0.02, max_hold=24)
on SPY 1h 2021-2025 twice:
  A) regime_sma=0   (no filter — baseline)
  B) regime_sma=200 (SMA200 regime filter)

Also tests regime_sma=100 for shorter-term regime filtering.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def _run_single(
    *,
    symbol: str,
    start: date,
    end: date,
    storage_root: Path,
    cash: float,
    window: int,
    std_mult: float,
    stop_pct: float,
    max_hold: int,
    regime_sma: int,
) -> dict:
    """Run one backtest config and return metrics dict."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import (
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    warmup_days = max(300, regime_sma + 50) if regime_sma > 0 else 100
    fetch_start = start - timedelta(days=warmup_days)

    src = TiingoSource(storage=TiingoStorage(root=storage_root))
    raw = src.fetch_many(
        [symbol], fetch_start, end,
        asset_class="etf", frequency="1hour",
    )
    if symbol not in raw or raw[symbol].empty:
        raise RuntimeError(f"No data for {symbol}")

    data_full = {symbol: raw[symbol]}
    data_bounded = {
        symbol: raw[symbol].loc[pd.Timestamp(start):pd.Timestamp(end)]
    }
    n_bars = len(data_bounded[symbol])

    strategy = BollingerMRStrategy(
        data=data_full,
        symbol=symbol,
        window=window,
        std_mult=std_mult,
        stop_pct=stop_pct,
        max_hold=max_hold,
        risk_pct_of_equity=0.95,
        regime_sma=regime_sma,
    )
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=cash)

    # Metrics.
    eq = result.equity_curve
    periods_per_year = 252 * 7
    returns = eq.pct_change().dropna()
    mean_ret = float(returns.mean())
    std_ret = float(returns.std())
    sharpe = (mean_ret / std_ret) * np.sqrt(periods_per_year) if std_ret > 0 else 0.0

    n_years = n_bars / periods_per_year
    total_return = result.final_equity / cash
    cagr = total_return ** (1 / n_years) - 1 if n_years > 0 else 0.0

    peak = eq.cummax()
    dd = (eq - peak) / peak
    max_dd = float(dd.min())

    n_trades = len(result.trades)
    wins = sum(1 for t in result.trades if t.pnl > 0) if n_trades else 0
    win_rate = wins / n_trades if n_trades else 0.0

    return {
        "regime_sma": regime_sma,
        "label": f"SMA{regime_sma}" if regime_sma > 0 else "no filter",
        "n_bars": n_bars,
        "sharpe": sharpe,
        "cagr": cagr,
        "max_dd": max_dd,
        "final_equity": result.final_equity,
        "n_trades": n_trades,
        "win_rate": win_rate,
    }


def main() -> int:
    symbol = "SPY"
    start = date(2021, 1, 1)
    end = date(2025, 12, 31)
    storage_root = Path("data/tiingo")
    cash = 100_000.0

    # Best config from gate-pass.
    window = 20
    std_mult = 1.5
    stop_pct = 0.02
    max_hold = 24

    regime_values = [0, 100, 200]
    results = []

    for regime in regime_values:
        label = f"SMA{regime}" if regime > 0 else "baseline"
        print(f"\nRunning: regime_sma={regime} ({label})...")
        m = _run_single(
            symbol=symbol,
            start=start,
            end=end,
            storage_root=storage_root,
            cash=cash,
            window=window,
            std_mult=std_mult,
            stop_pct=stop_pct,
            max_hold=max_hold,
            regime_sma=regime,
        )
        results.append(m)
        print(f"  Sharpe={m['sharpe']:.3f}, CAGR={m['cagr']*100:.2f}%, "
              f"MaxDD={m['max_dd']*100:.2f}%, Trades={m['n_trades']}, "
              f"WinRate={m['win_rate']*100:.1f}%")

    # Print comparison table.
    baseline = results[0]
    print("\n" + "=" * 75)
    print("REGIME FILTER ABLATION — Bollinger MR SPY 1h (w=20, std=1.5)")
    print(f"Period: {start} → {end}")
    print("Citation: [stocks_on_the_move, p.110]")
    print("=" * 75)

    print(f"\n{'Filter':<15} {'Sharpe':>8} {'CAGR':>8} {'MaxDD':>8} "
          f"{'Trades':>7} {'WinRate':>8} {'Sharpe Δ':>10}")
    print("-" * 75)
    for m in results:
        delta = ((m["sharpe"] - baseline["sharpe"]) / baseline["sharpe"] * 100
                 if baseline["sharpe"] != 0 else 0)
        print(f"{m['label']:<15} {m['sharpe']:>8.3f} {m['cagr']*100:>7.2f}% "
              f"{m['max_dd']*100:>7.2f}% {m['n_trades']:>7} "
              f"{m['win_rate']*100:>7.1f}% {delta:>+9.1f}%")

    # Analysis.
    print("\n--- Analysis ---")
    best = max(results, key=lambda x: x["sharpe"])
    print(f"Best Sharpe: {best['label']} ({best['sharpe']:.3f})")

    # Check if any filtered version beats baseline.
    for m in results[1:]:
        if m["sharpe"] > baseline["sharpe"]:
            print(f"  {m['label']} IMPROVES Sharpe by "
                  f"{(m['sharpe']-baseline['sharpe'])/baseline['sharpe']*100:+.1f}%")
        else:
            print(f"  {m['label']} HURTS Sharpe by "
                  f"{(m['sharpe']-baseline['sharpe'])/baseline['sharpe']*100:+.1f}%")

    # Check max drawdown improvement.
    for m in results[1:]:
        if m["max_dd"] > baseline["max_dd"]:  # less negative = better
            print(f"  {m['label']} IMPROVES MaxDD: {m['max_dd']*100:.2f}% vs "
                  f"{baseline['max_dd']*100:.2f}%")
        else:
            print(f"  {m['label']} WORSENS MaxDD: {m['max_dd']*100:.2f}% vs "
                  f"{baseline['max_dd']*100:.2f}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
