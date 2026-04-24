"""Iter 017 — 12-1 top-1 regional rotation backtests on 3 datasets.

**Pre-committed cfg** ``nts_regional_top1_vm_vt15_L21_cap20`` — see
hypothesis.md. NO grid, NO sweep. Single pre-committed cfg inheriting
iter 016's fixed-ratio × vol-target primitive and adding 12-1 top-1
cross-sectional rotation over 3 regional stacked products.

Cumulative n_trials advance after iter 017: 4261 → 4264.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — fixed-weight stack.
* `[stocks_on_the_move, p.76-77]` — cross-sectional ranking framework.
* `[ml_for_algo_trading, ch.4, p.86]` — 12-1 skip-a-month canonical.
* Asness-Moskowitz-Pedersen (2013) — value/momentum across asset classes.
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
from regional_rotation_stack import apply_regional_rotation_vm  # noqa: E402

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
    "cfg_id": "nts_regional_top1_vm_vt15_L21_cap20",
    "eq_weight": 0.6,
    "bd_weight": 0.4,
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
    "long_window": 252,      # 12 months
    "skip": 21,              # 1 month skip (12-1 canonical)
    "rebalance_every": 21,   # monthly
    "rebalance": "daily vol-target + monthly region re-rank",
    "funding_cost_modeled": False,  # same caveat as iter 015/016
}
COST_BPS_PER_LEG = 0.0002
SWITCH_COST_BPS = 0.0002  # one-off per equity switch

# ---------------------------------------------------------------------------
# Datasets — IEF-inception aligned (identical to iter 016)
# ---------------------------------------------------------------------------

# Each dataset defines the US region's equity symbol and the common EFA/EEM/IEF.
DATASETS: dict[str, dict] = {
    "educational": {
        "us_equity": "SPY",
        "intl_equity": "EFA",
        "em_equity":   "EEM",
        "bond":        "IEF",
        "start":       "2006-01-03",
        "end":         "2026-04-15",
        "role":        "SPY/EFA/EEM + IEF ~20y IEF-aligned",
    },
    "spy_real": {
        "us_equity": "SPY",
        "intl_equity": "EFA",
        "em_equity":   "EEM",
        "bond":        "IEF",
        "start":       "2009-06-25",
        "end":         "2026-04-15",
        "role":        "SPY/EFA/EEM + IEF 17y post-GFC",
    },
    "ndx_real": {
        "us_equity": "QQQ",
        "intl_equity": "EFA",
        "em_equity":   "EEM",
        "bond":        "IEF",
        "start":       "2010-02-12",
        "end":         "2026-04-15",
        "role":        "QQQ/EFA/EEM + IEF 16y tech-heavy US region",
    },
}


def load_returns(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    mask = (df.index >= start) & (df.index <= end)
    price = df.loc[mask, "adj_close"]
    r = price.pct_change()
    r.name = symbol
    return r


def load_regions(ds_name: str) -> tuple[dict[str, pd.DataFrame], pd.Series]:
    ds = DATASETS[ds_name]
    r_us = load_returns(ds["us_equity"], ds["start"], ds["end"])
    r_intl = load_returns(ds["intl_equity"], ds["start"], ds["end"])
    r_em = load_returns(ds["em_equity"], ds["start"], ds["end"])
    r_bd = load_returns(ds["bond"], ds["start"], ds["end"])
    # Inner-join on index so all 4 align (IEF inception is binding ~2006).
    df = pd.concat(
        {"US_eq": r_us, "INTL_eq": r_intl, "EM_eq": r_em, "BD": r_bd},
        axis=1, join="inner",
    ).dropna()
    regions = {
        "US":   pd.DataFrame({"equity": df["US_eq"],   "bond": df["BD"]}, index=df.index),
        "INTL": pd.DataFrame({"equity": df["INTL_eq"], "bond": df["BD"]}, index=df.index),
        "EM":   pd.DataFrame({"equity": df["EM_eq"],   "bond": df["BD"]}, index=df.index),
    }
    us_bench = df["US_eq"]
    us_bench.name = ds["us_equity"]
    return regions, us_bench


def benchmark_metrics(returns: pd.Series) -> dict:
    eq = (1.0 + returns).cumprod()
    return {
        "sharpe": float(_sharpe(returns)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "n_bars": int(len(returns)),
        "first": str(returns.index[0].date()),
        "last": str(returns.index[-1].date()),
    }


def run_single_cfg(
    regions: dict[str, pd.DataFrame],
) -> tuple[dict, pd.Series, pd.Series]:
    result = apply_regional_rotation_vm(
        regions,
        eq_weight=CFG["eq_weight"], bd_weight=CFG["bd_weight"],
        target_vol=CFG["target_vol"], lookback=CFG["lookback"],
        max_leverage=CFG["max_leverage"],
        long_window=CFG["long_window"], skip=CFG["skip"],
        rebalance_every=CFG["rebalance_every"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
        switch_cost_bps=SWITCH_COST_BPS,
    )
    net = result["net"]
    eq = (1.0 + net).cumprod()
    selection = result["selection_log"]
    region_counts = selection.value_counts().to_dict()
    region_fractions = {
        k: float(v / len(selection)) for k, v in region_counts.items()
    }

    m = {
        "cfg_id": CFG["cfg_id"],
        **{k: v for k, v in CFG.items() if k != "cfg_id"},
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "turnover_annual_per_leg": result["turnover_annual_per_leg"],
        "turnover_annual_total": result["turnover_annual_total"],
        "switch_count": int(result["switch_count"]),
        "rebalance_count": int(len(selection)),
        "region_selection_counts": {k: int(v) for k, v in region_counts.items()},
        "region_selection_fractions": region_fractions,
        "first_bar": str(net.index[0].date()),
        "last_bar": str(net.index[-1].date()),
    }
    return m, net, selection


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "switch_cost_bps": SWITCH_COST_BPS,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "selection_logs": {},
        "region_correlations": {},
        "pre_committed": True,
        "iter_label": "017-2026-04-24-1750-regional-rotation-stack-vm",
    }

    for ds_name, ds in DATASETS.items():
        regions, us_bench = load_regions(ds_name)
        bench = benchmark_metrics(us_bench)
        all_results["benchmarks"][ds_name] = bench
        # Region correlations for context
        corr = pd.DataFrame({
            "US":   regions["US"]["equity"],
            "INTL": regions["INTL"]["equity"],
            "EM":   regions["EM"]["equity"],
        }).corr().round(4)
        all_results["region_correlations"][ds_name] = corr.to_dict()
        print(
            f"[{ds_name}] {ds['us_equity']}+EFA+EEM+IEF "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars)"
        )
        print(
            f"  bench US({ds['us_equity']}): Sharpe={bench['sharpe']:.3f} "
            f"CAGR={bench['cagr']:.2%} MDD={bench['mdd']:.2%}"
        )
        print(f"  region correlations:\n    {corr.to_string().replace(chr(10), chr(10) + '    ')}")

    for ds_name, ds in DATASETS.items():
        print(f"\n=== {ds_name} — single cfg {CFG['cfg_id']} ===")
        regions, _ = load_regions(ds_name)
        m, net, selection = run_single_cfg(regions)
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
        }
        all_results["selection_logs"][ds_name] = {
            str(date.date()): region for date, region in selection.items()
        }
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]
        edge = m["sharpe"] - bench_sharpe
        print(
            f"  Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"bars={m['bars']} rebalances={m['rebalance_count']}"
        )
        print(
            f"  region fractions: "
            + ", ".join(f"{k}={v:.1%}" for k, v in m["region_selection_fractions"].items())
            + f" | switches={m['switch_count']}"
        )
        print(
            f"  turnover/yr total={m['turnover_annual_total']:.2f}"
            f" (eq={m['turnover_annual_per_leg']['EQ']:.2f}, "
            f"bd={m['turnover_annual_per_leg']['BD']:.2f})"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
