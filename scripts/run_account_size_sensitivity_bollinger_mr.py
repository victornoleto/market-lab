#!/usr/bin/env python3
"""Phase B Lead #8 — Account size sensitivity for BollingerMR GARCH SPY 1h.

Tests whether the canonical BollingerMR GARCH config produces consistent
percentage metrics (Sharpe, MaxDD%) across account sizes, and reports
minimum viable account given Pepperstone SPX500 lot constraints.

Pepperstone SPX500 CFD min lot: 0.01 contracts = ~$50 notional at SPX=5000.
risk_pct_of_equity=0.95 (canonical).

Account sizes tested: $1k, $5k, $10k, $50k, $100k.
Window: 2019-11-25 → 2024-12-31 (IS full manifest window).
"""

from __future__ import annotations

import logging
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("ai_trade.account_sensitivity_bollinger")

IS_START = date(2019, 11, 25)
IS_END = date(2024, 12, 31)
ACCOUNT_SIZES = [1_000, 5_000, 10_000, 50_000, 100_000]
# Canonical GARCH config from winner #1 [machine_trading, p.126-127]
CANONICAL = dict(
    window=20,
    std_mult=2.0,
    stop_pct=0.02,
    max_hold=24,
    risk_pct_of_equity=0.95,
    garch_lambda=0.94,
    direction="long",
)
PEPPERSTONE_MIN_NOTIONAL = 50.0  # 0.01 SPX500 lot at ~$5000 index


def _run(data: dict, cash: float) -> dict:
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    spy = data["SPY"]
    data_full = {"SPY": spy}
    exec_cfg = ExecutionConfig(half_spread=0.01, commission_per_unit=0.0186)
    strategy = BollingerMRStrategy(data=data_full, symbol="SPY", **CANONICAL)
    runner = Runner(executor=ExecutionSimulator(exec_cfg))

    data_bounded = {"SPY": spy.loc[pd.Timestamp(IS_START): pd.Timestamp(IS_END)]}
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=cash)
    if result is None:
        return {}

    eq = result.equity_curve
    rets = eq.pct_change().dropna().to_numpy(dtype=float)
    sharpe = float(np.mean(rets) / (np.std(rets, ddof=0) + 1e-12) * np.sqrt(252 * 6.5))
    cagr = float((eq.iloc[-1] / eq.iloc[0]) ** (252 / max(len(rets), 1)) - 1)
    dd = float(((eq / eq.cummax()) - 1).min())
    final_equity = float(eq.iloc[-1])
    net_profit = final_equity - cash

    n_trades = len(result.trades) if hasattr(result, "trades") and result.trades else 0

    return {
        "cash": cash,
        "sharpe": sharpe,
        "cagr_pct": cagr * 100,
        "max_dd_pct": dd * 100,
        "net_profit_usd": net_profit,
        "n_trades": n_trades,
        "min_notional_ok": (cash * 0.95 * CANONICAL["risk_pct_of_equity"]) >= PEPPERSTONE_MIN_NOTIONAL,
    }


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
    fetch_start = IS_START - timedelta(days=60)
    log.info("Fetching SPY daily+1h from %s to %s", fetch_start, IS_END)

    raw = src.fetch_many(
        ["SPY"], fetch_start, IS_END, asset_class="etf", frequency="1hour",
    )
    if "SPY" not in raw or raw["SPY"].empty:
        log.error("No SPY data — abort")
        return 1

    data = {"SPY": raw["SPY"]}
    n_bars = len(data["SPY"].loc[pd.Timestamp(IS_START): pd.Timestamp(IS_END)])
    log.info("SPY 1h bars in IS window: %d", n_bars)

    results = []
    for cash in ACCOUNT_SIZES:
        log.info("Running at $%.0f ...", cash)
        r = _run(data, cash)
        if r:
            log.info(
                "  $%6.0f → Sharpe=%.3f CAGR=%.2f%% MaxDD=%.2f%% NetProfit=$%.0f",
                cash, r["sharpe"], r["cagr_pct"], r["max_dd_pct"], r["net_profit_usd"],
            )
            results.append(r)

    print("\n=== Account Size Sensitivity — BollingerMR GARCH SPY 1h (IS) ===")
    print(f"{'Account':>10}  {'Sharpe':>7}  {'CAGR%':>6}  {'MaxDD%':>7}  {'NetProfit$':>11}  {'MinLotOK':>8}")
    for r in results:
        print(
            f"${r['cash']:>9,.0f}  {r['sharpe']:>7.3f}  {r['cagr_pct']:>6.2f}  "
            f"{r['max_dd_pct']:>7.2f}  ${r['net_profit_usd']:>10,.0f}  "
            f"{'YES' if r['min_notional_ok'] else 'NO':>8}"
        )

    print(f"\nPepperstone SPX500 min notional: ${PEPPERSTONE_MIN_NOTIONAL:.0f}")
    min_viable = next((r["cash"] for r in results if r["min_notional_ok"]), None)
    print(f"Minimum viable account: ${min_viable:,.0f}" if min_viable else "No viable size found")
    print("\nNote: Sharpe/CAGR%/MaxDD% should be ~constant (scale-invariant).")
    print("Net profit scales linearly with account size — that is the key result.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
