"""Iter 016 — Static-ratio × vol-managed hybrid backtests on 3 datasets.

**Pre-committed cfg** ``ntsx_vm_vt15_L21_cap20`` — see hypothesis.md.
NO grid, NO sweep, NO post-hoc selection. Single pre-committed cfg
combining iter 015's fixed 60:40 ratio with iter 008's vol-target.

Cumulative n_trials advance after iter 016: 4258 → 4261.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity with fixed weights.
* `[systematic_trading, p.40, ch.2]` — volatility standardisation primitive.
* Moreira & Muir (2017) — variance-target scaling.
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
from static_stack_vm import apply_static_stack_vol_managed  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------
#
# Parameters chosen to match iter 008 exactly on the three vol-management
# axes (target_vol=0.15, lookback=21, max_leverage=2.0). Only structural
# difference vs iter 008: weights are FIXED (0.6 / 0.4 normalised), not
# inverse-variance dynamic.
#
# Weights 0.6 / 0.4 normalised (= 0.9 / 0.6 un-normalised) reproduce iter 015
# exactly when scale is pinned to cap = 1.5. With max_lev = 2.0 and target_vol
# 0.15, the scale can expand up to 2.0 during low-vol regimes (pos_eq up to
# 1.2, pos_bd up to 0.8 — total 2.0) and contract as low as 0 during crashes.

CFG: dict = {
    "cfg_id": "ntsx_vm_vt15_L21_cap20",
    "eq_weight": 0.6,       # normalised; un-normalised = 0.9 at scale=1.5
    "bd_weight": 0.4,       # normalised; un-normalised = 0.6 at scale=1.5
    "target_vol": 0.15,     # matches iter 008 vt15
    "lookback": 21,         # matches iter 008 L21
    "max_leverage": 2.0,    # matches iter 008 cap20
    "rebalance": "daily",
    "funding_cost_modeled": False,  # OPTIMISTIC (same caveat as iter 015)
}
COST_BPS_PER_LEG = 0.0002  # 2 bps per unit ∆position (matches iter 010, 015)

# ---------------------------------------------------------------------------
# Datasets — IEF-inception aligned (same as iter 015 for direct comparison)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "SPY+IEF ~20y (IEF-inception-aligned)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+IEF 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "IEF",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+IEF 16y tech-heavy",
    },
}


def load_pair_returns(eq: str, bd: str, start: str, end: str) -> pd.DataFrame:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_bd = (df_bd.index >= start) & (df_bd.index <= end)
    p = pd.concat({
        "eq": df_eq.loc[m_eq, "adj_close"],
        "bd": df_bd.loc[m_bd, "adj_close"],
    }, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd]
    return r


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


def run_single_cfg(returns: pd.DataFrame) -> tuple[dict, pd.Series, pd.DataFrame, pd.Series]:
    eq_col, bd_col = returns.columns
    net, pos_eq, pos_bd, scale = apply_static_stack_vol_managed(
        returns[eq_col],
        returns[bd_col],
        eq_weight=CFG["eq_weight"],
        bd_weight=CFG["bd_weight"],
        target_vol=CFG["target_vol"],
        lookback=CFG["lookback"],
        max_leverage=CFG["max_leverage"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    positions = pd.DataFrame({"EQ": pos_eq, "BD": pos_bd})
    eq = (1.0 + net).cumprod()
    cap_hit = float(
        np.isclose(scale.to_numpy(float), CFG["max_leverage"], atol=1e-9).mean()
    )
    turnover_per_leg = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0])
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    m = {
        "cfg_id": CFG["cfg_id"],
        "eq_weight": CFG["eq_weight"],
        "bd_weight": CFG["bd_weight"],
        "target_vol": CFG["target_vol"],
        "lookback": CFG["lookback"],
        "max_leverage": CFG["max_leverage"],
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "scale_mean": float(scale.mean()),
        "scale_median": float(scale.median()),
        "scale_min": float(scale.min()),
        "scale_max": float(scale.max()),
        "scale_cap_hit_frac": cap_hit,
        "scale_zero_frac": float((scale < 1e-6).mean()),
        "turnover_annual_per_leg": turnover_per_leg,
        "turnover_annual_total": turnover_total,
    }
    return m, net, positions, scale


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations": {},
        "pre_committed": True,
        "iter_label": "016-2026-04-24-1729-static-stack-vm-hybrid",
    }

    pairs: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_pair_returns(ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"])
        pairs[ds_name] = r
        bench_series = r.iloc[:, 0]
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        corr = r.corr().iloc[0, 1]
        all_results["leg_correlations"][ds_name] = {"eq_bd": float(corr)}
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%} ρ(eq,bd)={corr:+.3f}"
        )

    for ds_name, r in pairs.items():
        print(f"\n=== {ds_name} ({len(r)} bars) — single cfg {CFG['cfg_id']} ===")
        m, net, positions, scale = run_single_cfg(r)
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
        }
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]
        edge = m["sharpe"] - bench_sharpe
        print(
            f"  {m['cfg_id']:28s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale[mean/med/min/max]={m['scale_mean']:.2f}/{m['scale_median']:.2f}/"
            f"{m['scale_min']:.2f}/{m['scale_max']:.2f} "
            f"cap_hit={m['scale_cap_hit_frac']:.2%}"
        )
        print(
            f"    turnover/yr total={m['turnover_annual_total']:.4f} "
            f"(scale dynamic, nonzero expected)"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
