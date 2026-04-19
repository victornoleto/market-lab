#!/usr/bin/env python3
"""Leverage sweep for BollingerMR canonical on SPY 1h (Phase 3 Lead A1).

Runs BollingerMRStrategy (window=20, std_mult=2.0, canonical) on the
longest available SPY 1h window from the Tiingo cache, at
``risk_pct_of_equity`` ∈ {0.95, 2.0, 5.0, 10.0, 20.0}. Reports, per
leverage level:

* Net Sharpe (annualised, ``periods_per_year = 252 × 7`` for 1h bars).
* CAGR (net of modelled half-spread 0.02).
* Close-to-close max drawdown.
* **Intra-bar ruin flag** — bar.low/high reachability of ``equity ≤ 0``.
* **Bootstrap prob-of-ruin** — stationary block bootstrap of trade
  returns × leverage (10 000 paths, block=5, horizon = n_trades).
* Kelly f* vs leverage (half-Kelly comparison).

Gate (Phase 3 A1)
-----------------
A leverage L passes if:
  - Final equity > cash-only (1x) baseline final equity, AND
  - Max close-to-close DD ≤ 50 %, AND
  - Bootstrap prob-of-ruin < 5 %, AND
  - No intra-bar ruin over the backtest window.

Emit a GO / NO-GO verdict per leverage and a global
"best-growth-optimal L" cross-checked with Kelly f/2.

Citations
---------
- Bollinger MR: ``[algo_trading_chan, p.28-30, ch.2]``,
  ``[machine_trading, p.204-205, ch.7]``.
- Kelly / leverage space: ``[math_money_mgmt, Vince]``,
  ``[leverage_space, Vince]``.
- Margin/ruin floor: ``[leverage_for_the_long_run, p.7]``.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


LEVERAGE_LEVELS = [0.95, 2.0, 5.0, 10.0, 20.0]
HALF_SPREAD_DEFAULT = 0.02  # Pepperstone SPX500 US hours, ~$0.02/share SPY-equivalent.
PERIODS_PER_YEAR_1H = 252 * 7


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Leverage sweep: BollingerMR canonical SPY 1h.")
    p.add_argument("--symbol", default="SPY")
    p.add_argument("--asset-class", default="etf")
    p.add_argument("--frequency", default="1hour")
    p.add_argument("--storage-root", default="data/tiingo")
    p.add_argument("--start", default=None, help="ISO date (default: manifest first_dt)")
    p.add_argument("--end", default=None, help="ISO date (default: manifest last_dt)")
    p.add_argument("--cash", type=float, default=1_000.0, help="$1k per mandate target")
    p.add_argument("--warmup-days", type=int, default=60)
    p.add_argument("--half-spread", type=float, default=HALF_SPREAD_DEFAULT)
    p.add_argument("--output-dir", default="reports")
    p.add_argument("--run-id", default=None)
    p.add_argument("--n-bootstrap", type=int, default=10_000)
    p.add_argument("--block-size", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def _manifest_window(storage_root: Path, symbol: str, freq: str) -> tuple[date, date]:
    manifest_path = storage_root / "manifest.json"
    m = json.loads(manifest_path.read_text())
    entry = m[symbol][freq]
    first = datetime.fromisoformat(entry["first_dt"]).date()
    last = datetime.fromisoformat(entry["last_dt"]).date()
    return first, last


def _annualized_sharpe(equity: pd.Series, periods_per_year: int) -> float:
    rets = equity.pct_change().dropna()
    std = float(rets.std())
    if std <= 0:
        return 0.0
    return float(rets.mean() / std) * float(np.sqrt(periods_per_year))


def _max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min()) if len(dd) else 0.0


def _cagr(final_equity: float, initial_cash: float, years: float) -> float:
    if years <= 0 or final_equity <= 0:
        return 0.0
    return float((final_equity / initial_cash) ** (1.0 / years) - 1.0)


def _trade_returns(trades, cash_at_start: float) -> np.ndarray:
    """Per-trade net return ≈ pnl / cash_at_start (constant account proxy).

    The engine actually compounds; this approximation is fine for a
    bootstrap of the trade-return *distribution*.
    """
    if not trades:
        return np.array([], dtype=float)
    return np.asarray([t.pnl / cash_at_start for t in trades], dtype=float)


def main() -> int:
    args = _parse_args()

    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
    from ai_trade.backtest.engine.runner import Runner
    from ai_trade.backtest.helpers.leverage import (
        bootstrap_prob_of_ruin,
        intra_bar_ruin_scan,
        kelly_fraction_from_trades,
    )
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    storage_root = Path(args.storage_root)
    first, last = _manifest_window(storage_root, args.symbol, args.frequency)

    start = date.fromisoformat(args.start) if args.start else first
    end = date.fromisoformat(args.end) if args.end else last
    fetch_start = start - timedelta(days=args.warmup_days)

    print(f"[leverage-sweep] {args.symbol} {args.frequency}  window {start} → {end}")
    print(f"[leverage-sweep] manifest reports {first} → {last} (using longest available).")

    src = TiingoSource(storage=TiingoStorage(root=storage_root))
    raw = src.fetch_many(
        [args.symbol], fetch_start, end, asset_class=args.asset_class, frequency=args.frequency,
    )
    if args.symbol not in raw or raw[args.symbol].empty:
        print(f"ERROR: no data for {args.symbol}", file=sys.stderr)
        return 1

    data_full = {args.symbol: raw[args.symbol]}
    mask = (
        (raw[args.symbol].index >= pd.Timestamp(start))
        & (raw[args.symbol].index <= pd.Timestamp(end) + pd.Timedelta(days=1))
    )
    data_bounded = {args.symbol: raw[args.symbol][mask]}
    n_bars = len(data_bounded[args.symbol])
    years = n_bars / PERIODS_PER_YEAR_1H
    print(f"[leverage-sweep] {n_bars} bars over ~{years:.2f}y.")

    exec_cfg = ExecutionConfig(
        half_spread=args.half_spread, slippage=0.0, commission_per_unit=0.0,
    )

    rows: list[dict] = []
    per_leverage_trade_returns: dict[float, np.ndarray] = {}

    for lev in LEVERAGE_LEVELS:
        strategy = BollingerMRStrategy(
            data=data_full,
            symbol=args.symbol,
            window=20,
            std_mult=2.0,
            stop_pct=0.02,
            max_hold=24,
            risk_pct_of_equity=lev,
        )
        runner = Runner(executor=ExecutionSimulator(exec_cfg))
        bt = runner.run(strategy=strategy, data=data_bounded, initial_cash=args.cash)

        eq = bt.equity_curve
        sharpe = _annualized_sharpe(eq, PERIODS_PER_YEAR_1H)
        mdd = _max_drawdown(eq)
        cagr = _cagr(bt.final_equity, args.cash, years)

        ruin = intra_bar_ruin_scan(
            bt.trades, data_bounded[args.symbol], args.cash, ruin_threshold=0.0,
        )

        trade_rets_raw = _trade_returns(bt.trades, args.cash)
        # At leverage L, trade_returns already embed L (position size ∝ L),
        # so the bootstrap should use the *unlevered* return distribution
        # (trade_return_raw / L) and re-apply L in the simulator.
        if trade_rets_raw.size > 0 and lev > 0:
            unlevered_rets = trade_rets_raw / lev
        else:
            unlevered_rets = trade_rets_raw
        per_leverage_trade_returns[lev] = unlevered_rets

        p_ruin = bootstrap_prob_of_ruin(
            unlevered_rets,
            leverage=lev,
            n_paths=args.n_bootstrap,
            block_size=args.block_size,
            horizon=unlevered_rets.size or 1,
            ruin_floor=0.0,
            seed=args.seed,
        )

        kelly_f = kelly_fraction_from_trades(
            [t.pnl for t in bt.trades],
            capital_at_entry=[args.cash] * len(bt.trades),  # constant-cash proxy
        )

        rows.append(
            {
                "leverage": lev,
                "sharpe": sharpe,
                "cagr": cagr,
                "max_dd": mdd,
                "final_equity": bt.final_equity,
                "n_trades": len(bt.trades),
                "worst_intrabar_equity": ruin.worst_equity,
                "intrabar_ruin": ruin.ruined,
                "intrabar_ruin_time": ruin.ruin_time,
                "p_ruin_bootstrap": p_ruin,
                "kelly_f_star": kelly_f,
            }
        )

    # Baseline is the first leverage (0.95, effectively 1x cash).
    baseline_final = rows[0]["final_equity"]

    print()
    print("=" * 110)
    print(
        f"LEVERAGE SWEEP — BollingerMR canonical (w=20, σ=2.0) "
        f"on {args.symbol} {args.frequency} {start} → {end}  cash=${args.cash:.0f}"
    )
    print("=" * 110)
    header = (
        f"{'L':>5} {'Sharpe':>7} {'CAGR':>8} {'MaxDD':>8} "
        f"{'FinEq':>10} {'NTrd':>5} {'WorstIB':>10} {'IBruin':>7} "
        f"{'PoR':>6} {'Kelly f*':>9} {'Verdict':>10}"
    )
    print(header)
    print("-" * 110)
    for r in rows:
        intrabar_symbol = "YES" if r["intrabar_ruin"] else "no"
        gate_growth = r["final_equity"] > baseline_final
        gate_dd = r["max_dd"] >= -0.50
        gate_por = r["p_ruin_bootstrap"] < 0.05
        gate_ib = not r["intrabar_ruin"]
        passed = gate_growth and gate_dd and gate_por and gate_ib
        verdict = "GO" if passed else "NO-GO"
        print(
            f"{r['leverage']:>5.2f} {r['sharpe']:>7.3f} {r['cagr']*100:>7.2f}% "
            f"{r['max_dd']*100:>7.2f}% ${r['final_equity']:>9,.0f} "
            f"{r['n_trades']:>5} ${r['worst_intrabar_equity']:>9,.0f} "
            f"{intrabar_symbol:>7} {r['p_ruin_bootstrap']*100:>5.2f}% "
            f"{r['kelly_f_star']:>9.3f} {verdict:>10}"
        )

    print()
    # Best Sharpe-scaled L and Kelly-f/2 comparison.
    best = max(rows, key=lambda r: r["sharpe"] if r["final_equity"] > 0 else -1e9)
    print(f"Best (Sharpe):     L={best['leverage']:.2f}  Sharpe={best['sharpe']:.3f}  CAGR={best['cagr']*100:.2f}%")

    kelly_any_row = next((r for r in rows if r["kelly_f_star"] > 0), None)
    if kelly_any_row:
        f_star = kelly_any_row["kelly_f_star"]
        print(f"Kelly f* (trades): {f_star:.3f}  →  half-Kelly L = {f_star/2 * 10:.2f} (* 10x proxy)")
        print(
            "Note: Kelly f* here is a 'fraction of equity risked per trade' — "
            "to map to leverage, divide by stop_pct (0.02): "
            f"L_kelly_half ≈ f/2 / stop_pct = {f_star / 2 / 0.02:.2f}"
        )

    # Persist results as JSON + markdown if output-dir specified.
    if args.output_dir:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        rid = args.run_id or f"leverage_sweep_{args.symbol}_{args.frequency}_{datetime.now():%Y%m%d_%H%M}"
        json_path = out / f"{rid}.json"
        payload = {
            "symbol": args.symbol,
            "frequency": args.frequency,
            "start": str(start),
            "end": str(end),
            "initial_cash": args.cash,
            "half_spread": args.half_spread,
            "n_bars": n_bars,
            "years": years,
            "rows": [
                {
                    **{k: (v.isoformat() if isinstance(v, pd.Timestamp) else v) for k, v in r.items()},
                }
                for r in rows
            ],
        }
        json_path.write_text(json.dumps(payload, indent=2, default=str))
        print(f"\n[leverage-sweep] wrote {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
