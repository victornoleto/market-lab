"""Iter 022 — TOM-seasonality overlay on iter 016 base, 3 datasets.

Single pre-committed cfg ``ntsx_vm_vt15_L21_cap20_tom_b90_m50``.
Modulates eq_weight between 0.9 (TOM window: last 3 + first 3 business
days of each month) and 0.5 (mid-month). Otherwise identical to iter
016 (target_vol=0.15, lookback=21, max_leverage=2.0, cost=2 bps/leg).

Pre-run gate: **Kill #1 mechanism sanity**. Before the main backtest,
we measure standalone TOM-day vs non-TOM-day mean equity return per
dataset and abort with a Kill #1 verdict if the TOM premium is absent.

Cumulative n_trials advance: 4270 → 4271.

Citations
---------
* `[trading_systems_methods, p.479-481]` — turn-of-month seasonality.
* `[risk_parity, p.10-11, ch.1]` — iter 016 base stack.
* `[systematic_trading, p.40, ch.2]` — vol standardisation primitive.
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

from tom_seasonality_overlay import (  # noqa: E402
    apply_tom_static_stack_vm,
    compute_tom_flag,
)

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
    "cfg_id": "ntsx_vm_vt15_L21_cap20_tom_b90_m50",
    # iter 016 inheritance (unchanged)
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
    "rebalance": "daily",
    "funding_cost_modeled": False,  # OPTIMISTIC (same caveat as iter 016)
    # TOM modulator (NEW)
    "tom_last_n": 3,
    "tom_first_n": 3,
    "eq_weight_tom": 0.9,
    "bd_weight_tom": 0.1,
    "eq_weight_mid": 0.5,
    "bd_weight_mid": 0.5,
}
COST_BPS_PER_LEG = 0.0002  # matches iter 016


# ---------------------------------------------------------------------------
# Datasets (IEF-inception aligned, matches iter 016/018/020/021)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "SPY+IEF ~20y (IEF-inception-aligned, synth proxy)",
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


def measure_tom_premium(returns: pd.DataFrame) -> dict:
    """Measure raw TOM-day vs non-TOM-day mean equity returns + Sharpe.

    This is the Kill #1 sanity check. If TOM-day mean equity return
    ≤ non-TOM-day mean, the mechanism is not present in the data.
    """
    eq_col = returns.columns[0]
    eq_r = returns[eq_col]
    tom = compute_tom_flag(eq_r.index, last_n=3, first_n=3)
    tom_r = eq_r[tom]
    mid_r = eq_r[~tom]
    # Annualised Sharpe for daily mean/std (population std for stability).
    def _daily_sharpe(x: pd.Series) -> float:
        if len(x) < 2 or x.std(ddof=0) == 0:
            return float("nan")
        return float(x.mean() / x.std(ddof=0) * np.sqrt(252))
    return {
        "n_tom_bars": int(tom.sum()),
        "n_mid_bars": int((~tom).sum()),
        "tom_mean_daily": float(tom_r.mean()),
        "mid_mean_daily": float(mid_r.mean()),
        "tom_minus_mid_bps": float((tom_r.mean() - mid_r.mean()) * 1e4),
        "tom_std_daily": float(tom_r.std(ddof=0)),
        "mid_std_daily": float(mid_r.std(ddof=0)),
        "tom_ann_sharpe": _daily_sharpe(tom_r),
        "mid_ann_sharpe": _daily_sharpe(mid_r),
        "tom_frac": float(tom.mean()),
    }


def run_single_cfg(returns: pd.DataFrame) -> tuple[dict, pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    eq_col, bd_col = returns.columns
    net, pos_eq, pos_bd, scale, tom_flag = apply_tom_static_stack_vm(
        returns[eq_col],
        returns[bd_col],
        eq_weight_tom=CFG["eq_weight_tom"],
        eq_weight_mid=CFG["eq_weight_mid"],
        bd_weight_tom=CFG["bd_weight_tom"],
        bd_weight_mid=CFG["bd_weight_mid"],
        tom_last_n=CFG["tom_last_n"],
        tom_first_n=CFG["tom_first_n"],
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

    # Additional diagnostic: split net returns by TOM state.
    tom_net = net[tom_flag]
    mid_net = net[~tom_flag]
    def _daily_sharpe(x: pd.Series) -> float:
        if len(x) < 2 or x.std(ddof=0) == 0:
            return float("nan")
        return float(x.mean() / x.std(ddof=0) * np.sqrt(252))

    m = {
        "cfg_id": CFG["cfg_id"],
        "eq_weight_tom": CFG["eq_weight_tom"],
        "eq_weight_mid": CFG["eq_weight_mid"],
        "bd_weight_tom": CFG["bd_weight_tom"],
        "bd_weight_mid": CFG["bd_weight_mid"],
        "tom_last_n": CFG["tom_last_n"],
        "tom_first_n": CFG["tom_first_n"],
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
        "tom_bars_frac": float(tom_flag.mean()),
        "tom_net_mean_daily": float(tom_net.mean()),
        "mid_net_mean_daily": float(mid_net.mean()),
        "tom_net_ann_sharpe": _daily_sharpe(tom_net),
        "mid_net_ann_sharpe": _daily_sharpe(mid_net),
    }
    return m, net, positions, scale, tom_flag


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations": {},
        "tom_premium_raw": {},
        "pre_committed": True,
        "iter_label": "022-2026-04-24-1942-tom-seasonality-overlay",
    }

    # Pre-run Kill #1 sanity check: raw TOM premium in equity data.
    print("\n=== Kill #1 sanity check: raw TOM-day vs mid-month equity returns ===")
    kill1_flags = {}
    pairs: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_pair_returns(ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"])
        pairs[ds_name] = r
        tom_diag = measure_tom_premium(r)
        all_results["tom_premium_raw"][ds_name] = tom_diag
        premium_ok = tom_diag["tom_minus_mid_bps"] > 0
        kill1_flags[ds_name] = not premium_ok
        print(
            f"  [{ds_name}] TOM ({tom_diag['n_tom_bars']} bars) mean={tom_diag['tom_mean_daily']*1e4:+.2f}bps/d "
            f"| mid ({tom_diag['n_mid_bars']}) mean={tom_diag['mid_mean_daily']*1e4:+.2f}bps/d "
            f"| Δ={tom_diag['tom_minus_mid_bps']:+.2f}bps/d "
            f"(tom-ann-Sharpe={tom_diag['tom_ann_sharpe']:+.2f} | mid-ann-Sharpe={tom_diag['mid_ann_sharpe']:+.2f}) "
            f"{'✅ premium present' if premium_ok else '❌ premium ABSENT'}"
        )
    n_fails = sum(kill1_flags.values())
    kill1_triggered = n_fails >= 2
    all_results["kill_1_mechanism_absence"] = {
        "criterion": "TOM-day mean equity return ≤ non-TOM-day mean on ≥ 2/3 datasets",
        "failures_per_dataset": kill1_flags,
        "triggered": kill1_triggered,
    }
    if kill1_triggered:
        print(f"\n⚠️  Kill #1 TRIGGERED ({n_fails}/3 datasets). Mechanism falsified.")
        print("    Continuing to full backtest to generate full metrics for the record,")
        print("    but final verdict will incorporate this falsification.")

    # Benchmarks.
    for ds_name, ds in DATASETS.items():
        r = pairs[ds_name]
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
        m, net, positions, scale, tom_flag = run_single_cfg(r)
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
            f"  {m['cfg_id']:40s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale[mean/med/min/max]={m['scale_mean']:.2f}/{m['scale_median']:.2f}/"
            f"{m['scale_min']:.2f}/{m['scale_max']:.2f} "
            f"cap_hit={m['scale_cap_hit_frac']:.2%}"
        )
        print(
            f"    TOM net mean={m['tom_net_mean_daily']*1e4:+.2f}bps/d "
            f"(ann-Sharpe {m['tom_net_ann_sharpe']:+.2f}) | "
            f"mid net mean={m['mid_net_mean_daily']*1e4:+.2f}bps/d "
            f"(ann-Sharpe {m['mid_net_ann_sharpe']:+.2f})"
        )
        print(
            f"    turnover/yr total={m['turnover_annual_total']:.4f}"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
