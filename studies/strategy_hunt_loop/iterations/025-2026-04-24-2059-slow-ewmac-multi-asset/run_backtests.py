"""Iter 025 — Slow-EWMAC multi-asset backtests on 3 datasets.

**Pre-committed cfg** ``sema_slow_64_256_32_128_6asset_vt15_v1`` —
see hypothesis.md. NO grid, NO sweep, NO post-hoc selection. Single
config across 3 datasets.

Cumulative n_trials advance: 4277 → 4278 (+1).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]

sys.path.insert(0, str(ITER_DIR))
from slow_ewmac_multi_asset import apply_slow_ewmac_strategy  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "sema_slow_64_256_32_128_6asset_vt15_v1",
    "speeds": [(32, 128), (64, 256)],
    "speed_scalars": [2.65, 1.87],     # Carver Table 49
    "speed_weights": [0.5, 0.5],
    "fdm": 1.10,                       # 2 forecasts at ρ ≈ 0.85
    "target_vol_per_asset": 0.04,      # ~15%/yr at √(N · (1+(N-1)·0.3))
    "asset_vol_span": 36,
    "lag_bars": 1,
    "no_trade_buffer_pct": 0.10,
    "max_per_asset_leverage": 0.6,
    "long_only": True,
    "cost_bps_per_leg": 0.0002,         # 2 bps / |Δposition|
    "sigma_span": 36,
}

# ---------------------------------------------------------------------------
# Datasets — 6-asset broad-asset-class basket
# ---------------------------------------------------------------------------

ASSETS_BASE = ["TLT", "IEF", "GLD", "EFA", "EEM"]  # 5 non-equity diversifiers

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "diversifiers": ASSETS_BASE,
        "start": "2007-01-11",
        "end": "2026-04-15",
        "role": "SPY+TLT+IEF+GLD+EFA+EEM ~19y (matches iter 024 alignment)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "diversifiers": ASSETS_BASE,
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+TLT+IEF+GLD+EFA+EEM 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "diversifiers": ASSETS_BASE,
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+TLT+IEF+GLD+EFA+EEM 16y tech-heavy",
    },
}


def load_prices(ds: dict) -> pd.DataFrame:
    """Load adj_close for the equity + 5 diversifiers, inner-join on dates."""
    symbols = [ds["equity_symbol"]] + ds["diversifiers"]
    series_list = {}
    start = pd.Timestamp(ds["start"])
    end = pd.Timestamp(ds["end"])
    for sym in symbols:
        df = pd.read_parquet(TIINGO_DIR / f"{sym}.parquet")
        m = (df.index >= start) & (df.index <= end)
        series_list[sym] = df.loc[m, "adj_close"]
    prices = pd.concat(series_list, axis=1, join="inner").dropna()
    return prices


def benchmark_metrics(equity_prices: pd.Series, valid_index: pd.Index) -> dict:
    """Buy-hold benchmark: equity_only on the valid_index window."""
    eq_aligned = equity_prices.loc[valid_index]
    rets = eq_aligned.pct_change().dropna()
    eq_curve = (1.0 + rets).cumprod()
    return {
        "sharpe": float(_sharpe(rets)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "n_bars": int(len(rets)),
        "first": str(rets.index[0].date()),
        "last": str(rets.index[-1].date()),
    }


def run_single_cfg(prices_df: pd.DataFrame) -> tuple[
    dict, pd.Series, pd.DataFrame, pd.DataFrame, pd.DataFrame,
]:
    net, held, target, fcast = apply_slow_ewmac_strategy(
        prices_df,
        speeds=CFG["speeds"],
        speed_scalars=CFG["speed_scalars"],
        speed_weights=CFG["speed_weights"],
        fdm=CFG["fdm"],
        target_vol_per_asset=CFG["target_vol_per_asset"],
        asset_vol_span=CFG["asset_vol_span"],
        lag_bars=CFG["lag_bars"],
        no_trade_buffer_pct=CFG["no_trade_buffer_pct"],
        max_per_asset_leverage=CFG["max_per_asset_leverage"],
        long_only=CFG["long_only"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
        sigma_span=CFG["sigma_span"],
    )
    eq = (1.0 + net).cumprod()

    # Diagnostics — turnover, mean leverage, signal usage.
    turnover_per_year_per_leg = {}
    mean_leverage_per_asset = {}
    for col in held.columns:
        d = held[col].diff().abs().fillna(held[col].iloc[0])
        years = len(held) / 252.0
        turnover_per_year_per_leg[col] = float(d.sum() / years) if years > 0 else 0.0
        mean_leverage_per_asset[col] = float(held[col].mean())
    gross_leverage = held.abs().sum(axis=1)
    target_gross = target.abs().sum(axis=1)

    # Buffer effectiveness: pre vs post turnover ratio.
    target_dpos = {col: target[col].diff().abs().fillna(target[col].abs().iloc[0])
                   for col in target.columns}
    held_dpos = {col: held[col].diff().abs().fillna(held[col].abs().iloc[0])
                 for col in held.columns}
    pre_buffer_turnover = float(sum(s.sum() for s in target_dpos.values()))
    post_buffer_turnover = float(sum(s.sum() for s in held_dpos.values()))
    buffer_ratio = (post_buffer_turnover / pre_buffer_turnover
                    if pre_buffer_turnover > 0 else 0.0)

    summary = {
        "cfg_id": CFG["cfg_id"],
        **{k: v for k, v in CFG.items() if k != "cfg_id"},
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "n_bars": int(len(net)),
        "first_date": str(net.index[0].date()),
        "last_date": str(net.index[-1].date()),
        "turnover_per_year_per_leg": turnover_per_year_per_leg,
        "mean_turnover_per_year": float(np.mean(list(turnover_per_year_per_leg.values()))),
        "mean_leverage_per_asset": mean_leverage_per_asset,
        "gross_leverage_mean": float(gross_leverage.mean()),
        "gross_leverage_std": float(gross_leverage.std(ddof=0)),
        "target_gross_mean": float(target_gross.mean()),
        "buffer_turnover_ratio": float(buffer_ratio),
    }
    return summary, net, held, target, fcast


def main() -> None:
    print("Iter 025 — Slow-EWMAC multi-asset single-cfg run")
    print(f"cfg = {CFG['cfg_id']}")
    print(f"speeds = {CFG['speeds']}, target_vol_per_asset = {CFG['target_vol_per_asset']}")
    print(f"cost = {CFG['cost_bps_per_leg'] * 1e4:.0f} bps/leg/Δpos")
    print()

    runs: dict[str, dict[str, dict]] = {}
    benchmarks: dict[str, dict] = {}
    returns_series: dict[str, dict[str, dict]] = {}

    for ds_name, ds in DATASETS.items():
        print(f"=== {ds_name} ({ds['role']}) ===")
        prices = load_prices(ds)
        print(f"  loaded {prices.shape[0]} bars, {prices.shape[1]} assets:"
              f" {prices.index[0].date()} → {prices.index[-1].date()}")

        summary, net, held, target, fcast = run_single_cfg(prices)
        bench = benchmark_metrics(prices[ds["equity_symbol"]], net.index)

        runs[ds_name] = {summary["cfg_id"]: summary}
        benchmarks[ds_name] = bench
        returns_series[ds_name] = {
            summary["cfg_id"]: {
                "index": [d.isoformat() for d in net.index],
                "net_returns": net.tolist(),
                "gross_leverage": held.abs().sum(axis=1).tolist(),
            }
        }

        print(f"  Sharpe={summary['sharpe']:.4f}  "
              f"CAGR={summary['cagr']*100:.2f}%  "
              f"MDD={summary['mdd']*100:.2f}%")
        print(f"  vs bench: Sharpe={bench['sharpe']:.4f}  "
              f"CAGR={bench['cagr']*100:.2f}%  "
              f"MDD={bench['mdd']*100:.2f}%")
        print(f"  mean turnover / leg / yr = {summary['mean_turnover_per_year']:.2f} (Kill #B check)")
        print(f"  mean gross leverage = {summary['gross_leverage_mean']:.3f}")
        print(f"  buffer turnover ratio = {summary['buffer_turnover_ratio']:.3f} (Kill #D check)")
        print()

    out = {
        "iteration": "025-2026-04-24-2059-slow-ewmac-multi-asset",
        "cumulative_n_trials_post": 4277 + 1,
        "cost_bps_per_leg": CFG["cost_bps_per_leg"],
        "configs": [CFG],
        "datasets": DATASETS,
        "runs": runs,
        "benchmarks": benchmarks,
        "returns_series": returns_series,
    }
    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"results.json written ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
