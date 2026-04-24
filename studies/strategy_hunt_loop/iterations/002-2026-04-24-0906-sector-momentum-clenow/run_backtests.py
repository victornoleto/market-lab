"""Iteration 002 — run Clenow sector momentum on 3 datasets × 4 configs.

Writes `results.json` with per-(dataset, config) metrics.

Datasets:
  * sectors_long    — 9 original SPDR sectors 2006-01-03 → 2026-04-20 (~20y)
  * sectors_spy     — 11 SPDR sectors 2009-06-25 → 2026-04-20 (17y)
  * sectors_ndx     — 11 SPDR sectors 2010-02-12 → 2026-04-20 (16y)

Configs (minimal sanity grid, respecting `[stocks_on_the_move, p.219-220]`
anti-optimization):
  * top_k ∈ {3, 5}
  * buy_leverage ∈ {1.0, 2.0}
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.engine.execution import (
    ExecutionConfig,
    ExecutionSimulator,
)
from ai_trade.backtest.engine.runner import BacktestResult, Runner
from ai_trade.backtest.metrics.performance import (
    cagr,
    max_drawdown,
    returns_from_equity,
    sharpe,
)
from ai_trade.backtest.strategies.sector_momentum_clenow import (
    SectorMomentumClenow,
)

ROOT = Path(__file__).resolve().parents[4]  # → /var/www/pessoal/ai-trade
DATA_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
OUT_DIR = Path(__file__).parent

SECTORS_ORIGINAL = ["XLK", "XLF", "XLV", "XLY", "XLP", "XLE", "XLI", "XLU", "XLB"]
SECTORS_EXTENDED = SECTORS_ORIGINAL + ["XLRE", "XLC"]

DATASETS = {
    "sectors_long": {
        "universe": SECTORS_ORIGINAL,
        "regime": "SPY",
        "benchmark": "SPY",
        "start": "2006-01-03",
        "end":   "2026-04-20",
        "role":  "educational-analog — longer window with 2008 GFC in-sample",
    },
    "sectors_spy": {
        "universe": SECTORS_EXTENDED,
        "regime": "SPY",
        "benchmark": "SPY",
        "start": "2009-06-25",
        "end":   "2026-04-20",
        "role":  "spy_real — primary beat-SPY test",
    },
    "sectors_ndx": {
        "universe": SECTORS_EXTENDED,
        "regime": "SPY",         # regime still via SPY; benchmark vs QQQ
        "benchmark": "QQQ",
        "start": "2010-02-12",
        "end":   "2026-04-20",
        "role":  "ndx_real — cross-benchmark robustness",
    },
}

CONFIGS = [
    {"cfg_id": "k3_L1", "top_k": 3, "buy_leverage": 1.0},
    {"cfg_id": "k5_L1", "top_k": 5, "buy_leverage": 1.0},
    {"cfg_id": "k3_L2", "top_k": 3, "buy_leverage": 2.0},
    {"cfg_id": "k5_L2", "top_k": 5, "buy_leverage": 2.0},
]

EXEC_CFG = ExecutionConfig(
    half_spread=0.005,   # ~½¢ per share on liquid SPDR sectors
    slippage=0.005,
    commission_per_unit=0.0,  # Inter Internacional = zero brokerage
)


@dataclass
class RunMetrics:
    dataset: str
    cfg_id: str
    sharpe_annualized: float
    cagr: float
    mdd: float
    final_equity: float
    n_bars: int
    n_trades: int


def load_ohlc(symbol: str, start: str, end: str) -> pd.DataFrame:
    df = pd.read_parquet(DATA_DIR / f"{symbol}.parquet")
    df = df.loc[(df.index >= start) & (df.index <= end)]
    keep = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
    return df[keep].copy()


def buy_hold_equity(bench_df: pd.DataFrame, initial_cash: float = 100_000.0) -> pd.Series:
    close = bench_df["close"]
    shares = initial_cash / float(close.iloc[0])
    return close * shares


def run_config(dataset_name: str, cfg: dict) -> tuple[RunMetrics, BacktestResult]:
    ds = DATASETS[dataset_name]
    data: dict[str, pd.DataFrame] = {}
    for sym in ds["universe"] + [ds["regime"], ds["benchmark"]]:
        data.setdefault(sym, load_ohlc(sym, ds["start"], ds["end"]))

    strat = SectorMomentumClenow(
        universe=ds["universe"],
        regime_symbol=ds["regime"],
        top_k=cfg["top_k"],
        buy_leverage=cfg["buy_leverage"],
    )
    runner = Runner(executor=ExecutionSimulator(config=EXEC_CFG))
    initial_cash = 100_000.0
    result = runner.run(strat, data, initial_cash=initial_cash)
    equity = result.equity_curve
    rets = returns_from_equity(equity)
    return (
        RunMetrics(
            dataset=dataset_name,
            cfg_id=cfg["cfg_id"],
            sharpe_annualized=sharpe(rets),
            cagr=cagr(equity),
            mdd=max_drawdown(equity),
            final_equity=float(equity.iloc[-1]),
            n_bars=len(equity),
            n_trades=len(result.trades),
        ),
        result,
    )


def benchmark_metrics(dataset_name: str) -> dict:
    ds = DATASETS[dataset_name]
    bench_df = load_ohlc(ds["benchmark"], ds["start"], ds["end"])
    equity = buy_hold_equity(bench_df)
    rets = returns_from_equity(equity)
    return {
        "symbol": ds["benchmark"],
        "sharpe": sharpe(rets),
        "cagr": cagr(equity),
        "mdd": max_drawdown(equity),
        "n_bars": len(equity),
    }


def main() -> None:
    all_results = {
        "datasets": {name: {**ds, "universe": ds["universe"]} for name, ds in DATASETS.items()},
        "configs": CONFIGS,
        "benchmarks": {},
        "runs": {},
        "equity_curves": {},
    }

    for dataset_name in DATASETS:
        print(f"\n=== {dataset_name} ===")
        bench = benchmark_metrics(dataset_name)
        all_results["benchmarks"][dataset_name] = bench
        print(f"  benchmark {bench['symbol']:4s} Sharpe={bench['sharpe']:.3f} "
              f"CAGR={bench['cagr']:.3%} MDD={bench['mdd']:.2%} "
              f"(n_bars={bench['n_bars']})")
        all_results["runs"][dataset_name] = {}
        all_results["equity_curves"][dataset_name] = {}

        for cfg in CONFIGS:
            m, result = run_config(dataset_name, cfg)
            all_results["runs"][dataset_name][cfg["cfg_id"]] = {
                "sharpe": m.sharpe_annualized,
                "cagr":   m.cagr,
                "mdd":    m.mdd,
                "final_equity": m.final_equity,
                "n_bars": m.n_bars,
                "n_trades": m.n_trades,
            }
            # Save raw equity curve (for later gate computation) — subsample to
            # weekly to keep the JSON readable.
            eq = result.equity_curve
            subsample = eq.iloc[::5]
            rets_full = returns_from_equity(eq)
            all_results["equity_curves"][dataset_name][cfg["cfg_id"]] = {
                "index": [str(t.date()) for t in subsample.index],
                "equity": subsample.round(2).tolist(),
                "returns_full_index": [str(t.date()) for t in rets_full.index],
                "returns_full": rets_full.round(8).tolist(),
            }
            edge = m.sharpe_annualized - bench["sharpe"]
            print(
                f"  cfg={cfg['cfg_id']:6s} Sharpe={m.sharpe_annualized:+.3f} "
                f"(Δ={edge:+.3f}) CAGR={m.cagr:+.3%} MDD={m.mdd:.2%} "
                f"n_trades={m.n_trades}"
            )

    out_path = OUT_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
