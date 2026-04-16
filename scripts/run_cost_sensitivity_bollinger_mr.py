#!/usr/bin/env python3
"""Transaction cost sensitivity analysis for Bollinger MR best config.

Runs the fixed best config (window=20, std_mult=1.5, stop_pct=0.02,
max_hold=24) on SPY 1h 2021-2025 at varying spread levels to determine
whether the edge survives Pepperstone SPX500 CFD friction.

Pepperstone SPX500 CFD cost model:
- Commission: $0 (CFD indices are spread-only).
- Spread during US hours: ~0.4 points on SPX500 (~5000).
  Half-spread = 0.2 pts / 5000 = 0.004% = 0.4 bps.
  In SPY terms (~$500): half_spread ≈ $0.02/share.
- Slippage: 0.1-0.3 bps additional on liquid US indices.

Citations:
- Cost-aware backtesting: [machine_trading, p.126-127, ch.4].
- Config from: [algo_trading_chan, p.28-30, ch.2].
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np


# Half-spread levels in SPY $ terms, with annotations.
COST_SCENARIOS: list[tuple[float, str]] = [
    (0.00, "zero (baseline)"),
    (0.01, "~0.2 bps (tight)"),
    (0.02, "~0.4 bps (Pepperstone US hours)"),
    (0.05, "~1.0 bps (moderate + slippage)"),
    (0.10, "~2.0 bps (conservative)"),
    (0.20, "~4.0 bps (stress test)"),
    (0.50, "~10 bps (extreme stress)"),
]


def main() -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import (
        BacktestResult,
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    symbol = "SPY"
    start = date(2021, 1, 1)
    end = date(2025, 12, 31)
    cash = 100_000.0
    warmup_days = 100
    periods_per_year = 252 * 7  # 1h bars

    # Fixed best config from Iteration 2 (gate-passing).
    window, std_mult, stop_pct, max_hold = 20, 1.5, 0.02, 24

    # Fetch data once.
    fetch_start = start - timedelta(days=warmup_days)
    print(f"Fetching {symbol} 1h: {fetch_start} → {end}")
    src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
    raw = src.fetch_many(
        [symbol], fetch_start, end, asset_class="etf", frequency="1hour",
    )
    if symbol not in raw or raw[symbol].empty:
        print(f"ERROR: No data for {symbol}")
        return 1

    import pandas as pd

    data_full = {symbol: raw[symbol]}
    data_bounded = {
        symbol: raw[symbol].loc[pd.Timestamp(start):pd.Timestamp(end)]
    }
    n_bars = len(data_bounded[symbol])
    print(f"Data: {n_bars} bars in [{start}, {end}]")
    print(f"Config: w={window}, std={std_mult}, stop={stop_pct}, max_hold={max_hold}")
    print()

    results: list[dict] = []

    for half_spread, label in COST_SCENARIOS:
        exec_cfg = ExecutionConfig(
            half_spread=half_spread,
            slippage=0.0,
            commission_per_unit=0.0,
        )
        strategy = BollingerMRStrategy(
            data=data_full,
            symbol=symbol,
            window=window,
            std_mult=std_mult,
            stop_pct=stop_pct,
            max_hold=max_hold,
            risk_pct_of_equity=0.95,
        )
        runner = Runner(executor=ExecutionSimulator(exec_cfg))
        bt: BacktestResult = runner.run(
            strategy=strategy, data=data_bounded, initial_cash=cash,
        )

        eq = bt.equity_curve
        returns = eq.pct_change().dropna()
        mean_ret = float(returns.mean())
        std_ret = float(returns.std())
        sharpe = (mean_ret / std_ret) * np.sqrt(periods_per_year) if std_ret > 0 else 0.0

        n_years = n_bars / periods_per_year
        total_return = bt.final_equity / cash
        cagr = total_return ** (1 / n_years) - 1 if n_years > 0 else 0.0

        peak = eq.cummax()
        dd = (eq - peak) / peak
        max_dd = float(dd.min())

        n_trades = len(bt.trades)
        wins = sum(1 for t in bt.trades if t.pnl > 0) if n_trades else 0
        win_rate = wins / n_trades if n_trades else 0.0

        # Total cost paid.
        total_commission = sum(f.commission for f in bt.fills)
        total_slippage = sum(f.slippage_cost for f in bt.fills)
        total_cost = total_commission + total_slippage

        # Cost as % of final equity.
        cost_pct = total_cost / cash * 100

        row = {
            "half_spread": half_spread,
            "label": label,
            "sharpe": sharpe,
            "cagr": cagr,
            "max_dd": max_dd,
            "final_equity": bt.final_equity,
            "n_trades": n_trades,
            "win_rate": win_rate,
            "total_cost": total_cost,
            "cost_pct": cost_pct,
        }
        results.append(row)

    # Print results table.
    print("=" * 100)
    print("TRANSACTION COST SENSITIVITY — Bollinger MR SPY 1h (2021-2025)")
    print(f"Config: w={window}, std={std_mult}, stop={stop_pct}, max_hold={max_hold}")
    print("=" * 100)

    header = (
        f"{'Half-spread':<12} {'Label':<30} {'Sharpe':>8} {'CAGR':>8} "
        f"{'MaxDD':>8} {'Final $':>12} {'Trades':>7} {'WinRate':>8} "
        f"{'TotalCost':>10} {'Cost%':>7}"
    )
    print(header)
    print("-" * 100)

    baseline_sharpe = results[0]["sharpe"]
    baseline_cagr = results[0]["cagr"]

    for r in results:
        sharpe_decay = (
            (r["sharpe"] - baseline_sharpe) / baseline_sharpe * 100
            if baseline_sharpe != 0 else 0.0
        )
        line = (
            f"${r['half_spread']:<11.3f} {r['label']:<30} "
            f"{r['sharpe']:>8.3f} {r['cagr']*100:>7.2f}% "
            f"{r['max_dd']*100:>7.2f}% ${r['final_equity']:>11,.0f} "
            f"{r['n_trades']:>7} {r['win_rate']*100:>7.1f}% "
            f"${r['total_cost']:>9,.0f} {r['cost_pct']:>6.2f}%"
        )
        print(line)

    # Summary.
    print()
    print("--- Impact Summary ---")
    pepperstone_row = results[2]  # $0.02 half-spread
    conservative_row = results[4]  # $0.10 half-spread

    print(f"Baseline (zero cost):      Sharpe={results[0]['sharpe']:.3f}, CAGR={results[0]['cagr']*100:.2f}%")
    print(f"Pepperstone estimate:      Sharpe={pepperstone_row['sharpe']:.3f} ({(pepperstone_row['sharpe']-baseline_sharpe)/baseline_sharpe*100:+.1f}%), CAGR={pepperstone_row['cagr']*100:.2f}%")
    print(f"Conservative estimate:     Sharpe={conservative_row['sharpe']:.3f} ({(conservative_row['sharpe']-baseline_sharpe)/baseline_sharpe*100:+.1f}%), CAGR={conservative_row['cagr']*100:.2f}%")

    # Break-even: find where CAGR goes negative.
    breakeven = None
    for r in results:
        if r["cagr"] <= 0:
            breakeven = r["half_spread"]
            break

    if breakeven is not None:
        print(f"Break-even half-spread:    ~${breakeven:.3f} (CAGR turns negative)")
    else:
        print(f"Break-even half-spread:    > ${results[-1]['half_spread']:.3f} (strategy profitable at all tested levels)")

    # Verdict.
    print()
    pep_sharpe = pepperstone_row["sharpe"]
    if pep_sharpe >= 1.0:
        print("★ COST VERDICT: STRONG — Edge survives Pepperstone costs with Sharpe ≥ 1.0")
    elif pep_sharpe >= 0.5:
        print("◐ COST VERDICT: VIABLE — Edge degraded but still tradeable (Sharpe ≥ 0.5)")
    elif pep_sharpe > 0:
        print("△ COST VERDICT: MARGINAL — Edge barely survives costs (Sharpe < 0.5)")
    else:
        print("✗ COST VERDICT: FAIL — Edge destroyed by transaction costs")

    return 0


if __name__ == "__main__":
    sys.exit(main())
