"""Iter 003 — equal-notional sector momentum: 24 configs × 3 datasets.

Grid:
  * top_k ∈ {3, 5, 7, 9}
  * lookback_slope ∈ {60, 90, 120}
  * buy_leverage ∈ {1.0, 2.0}
= 24 configs

Datasets (identical windows to iter 002 for apples-to-apples comparison):
  * sectors_long  — 9 SPDR sectors 2006-2026 vs SPY
  * sectors_spy   — 11 SPDR sectors 2009-2026 vs SPY
  * sectors_ndx   — 11 SPDR sectors 2010-2026 vs QQQ

Writes ``results.json`` with per-(dataset, config) metrics + equity curves
(for later gate computation + deployment / exposure fractions).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path

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
from ai_trade.backtest.strategies.sector_momentum_equal_notional import (
    SectorMomentumEqualNotional,
)

ROOT = Path(__file__).resolve().parents[4]  # → /var/www/pessoal/ai-trade
DATA_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
OUT_DIR = Path(__file__).parent

SECTORS_ORIGINAL = ["XLK", "XLF", "XLV", "XLY", "XLP", "XLE", "XLI", "XLU", "XLB"]
SECTORS_EXTENDED = SECTORS_ORIGINAL + ["XLRE", "XLC"]

DATASETS: dict[str, dict] = {
    "sectors_long": {
        "universe": SECTORS_ORIGINAL,
        "regime": "SPY",
        "benchmark": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-20",
        "role": "educational-analog — longer window with 2008 GFC in-sample",
    },
    "sectors_spy": {
        "universe": SECTORS_EXTENDED,
        "regime": "SPY",
        "benchmark": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-20",
        "role": "spy_real — primary beat-SPY test",
    },
    "sectors_ndx": {
        "universe": SECTORS_EXTENDED,
        "regime": "SPY",
        "benchmark": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-20",
        "role": "ndx_real — cross-benchmark robustness",
    },
}

# Note: top_k=9 on the 9-sector universe equals "all sectors held" → equal
# weight; on 11-sector universes it's 9 of 11. This stress-tests the signal
# at both concentration extremes.
TOP_K_GRID = (3, 5, 7, 9)
LOOKBACK_GRID = (60, 90, 120)
LEVERAGE_GRID = (1.0, 2.0)

CONFIGS: list[dict] = [
    {
        "cfg_id": f"k{k}_L{int(round(10*lev)):02d}_lb{lb}",
        "top_k": k,
        "buy_leverage": lev,
        "lookback_slope": lb,
    }
    for k, lb, lev in product(TOP_K_GRID, LOOKBACK_GRID, LEVERAGE_GRID)
]

EXEC_CFG = ExecutionConfig(
    half_spread=0.005,
    slippage=0.005,
    commission_per_unit=0.0,  # Inter-style zero-brokerage
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
    deployment_median: float  # median of (gross_exposure / equity) over time


def load_ohlc(symbol: str, start: str, end: str) -> pd.DataFrame:
    df = pd.read_parquet(DATA_DIR / f"{symbol}.parquet")
    df = df.loc[(df.index >= start) & (df.index <= end)]
    keep = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
    return df[keep].copy()


def buy_hold_equity(bench_df: pd.DataFrame, initial_cash: float = 100_000.0) -> pd.Series:
    close = bench_df["close"]
    shares = initial_cash / float(close.iloc[0])
    return close * shares


def compute_deployment(result: BacktestResult, data: dict[str, pd.DataFrame]) -> float:
    """Median of gross-exposure / equity over time (post-lookback bars).

    Reconstructs positions from ``fills`` (per-order execution records).
    """
    fills = sorted(result.fills, key=lambda f: f.fill_time)
    timestamps = list(result.equity_curve.index)
    close_series = {s: data[s]["close"] for s in data.keys()}

    positions: dict[str, float] = {}
    f_idx = 0
    n = len(fills)
    ratios: list[float] = []
    for ts in timestamps:
        while f_idx < n and fills[f_idx].fill_time <= ts:
            fl = fills[f_idx]
            sign = 1.0 if fl.order.side == "buy" else -1.0
            positions[fl.order.symbol] = positions.get(fl.order.symbol, 0.0) + sign * fl.order.volume
            f_idx += 1
        gross = 0.0
        for s, v in positions.items():
            if abs(v) < 1e-12:
                continue
            cs = close_series.get(s)
            if cs is not None and ts in cs.index:
                gross += abs(v) * float(cs.loc[ts])
        equity = float(result.equity_curve.loc[ts])
        if equity > 0:
            ratios.append(gross / equity)
    if not ratios:
        return 0.0
    ratios.sort()
    return ratios[len(ratios) // 2]


def run_config(
    dataset_name: str, cfg: dict
) -> tuple[RunMetrics, BacktestResult, dict[str, pd.DataFrame]]:
    ds = DATASETS[dataset_name]
    data: dict[str, pd.DataFrame] = {}
    for sym in ds["universe"] + [ds["regime"], ds["benchmark"]]:
        data.setdefault(sym, load_ohlc(sym, ds["start"], ds["end"]))

    strat = SectorMomentumEqualNotional(
        universe=ds["universe"],
        regime_symbol=ds["regime"],
        top_k=cfg["top_k"],
        buy_leverage=cfg["buy_leverage"],
        lookback_slope=cfg["lookback_slope"],
    )
    runner = Runner(executor=ExecutionSimulator(config=EXEC_CFG))
    result = runner.run(strat, data, initial_cash=100_000.0)
    equity = result.equity_curve
    rets = returns_from_equity(equity)
    deployment = compute_deployment(result, data)
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
            deployment_median=deployment,
        ),
        result,
        data,
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
    all_results: dict = {
        "datasets": {
            name: {
                "universe": ds["universe"],
                "regime": ds["regime"],
                "benchmark": ds["benchmark"],
                "start": ds["start"],
                "end": ds["end"],
                "role": ds["role"],
            }
            for name, ds in DATASETS.items()
        },
        "configs": CONFIGS,
        "benchmarks": {},
        "runs": {},
        "equity_curves": {},
    }

    for dataset_name in DATASETS:
        print(f"\n=== {dataset_name} ===")
        bench = benchmark_metrics(dataset_name)
        all_results["benchmarks"][dataset_name] = bench
        print(
            f"  benchmark {bench['symbol']:4s} Sharpe={bench['sharpe']:.3f} "
            f"CAGR={bench['cagr']:.3%} MDD={bench['mdd']:.2%} "
            f"(n_bars={bench['n_bars']})"
        )
        all_results["runs"][dataset_name] = {}
        all_results["equity_curves"][dataset_name] = {}

        for cfg in CONFIGS:
            m, result, _ = run_config(dataset_name, cfg)
            all_results["runs"][dataset_name][cfg["cfg_id"]] = {
                "sharpe": m.sharpe_annualized,
                "cagr": m.cagr,
                "mdd": m.mdd,
                "final_equity": m.final_equity,
                "n_bars": m.n_bars,
                "n_trades": m.n_trades,
                "deployment_median": m.deployment_median,
            }
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
                f"  cfg={cfg['cfg_id']:18s} Sharpe={m.sharpe_annualized:+.3f} "
                f"(Δ={edge:+.3f}) CAGR={m.cagr:+.3%} MDD={m.mdd:.2%} "
                f"dep={m.deployment_median:.2f} n_tr={m.n_trades}"
            )

    out_path = OUT_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
