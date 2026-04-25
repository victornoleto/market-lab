"""Iter 073 — Run 4 cfgs × 3 datasets for the Gayed-gate × vol-managed stack.

Cfg sweep (theory-driven, NOT data-snooped):
  cfg1 `gayed_g16_vt15_L21_cap20`: target_vol=0.15, max_lev=2.0  (iter 016 baseline + gate)
  cfg2 `gayed_g16_vt15_L21_cap25`: target_vol=0.15, max_lev=2.5  (higher Carver IDM cap)
  cfg3 `gayed_g16_vt18_L21_cap25`: target_vol=0.18, max_lev=2.5  (higher vol target — primary)
  cfg4 `gayed_g16_vt20_L21_cap25`: target_vol=0.20, max_lev=2.5  (aggressive vol target)

Datasets:
  educational : SPY+IEF 2006-01-04 → 2026-04-15 (iter 016 IEF-aligned)
  spy_real    : SPY+IEF 2009-06-25 → 2026-04-15
  ndx_real    : QQQ+IEF 2010-02-12 → 2026-04-15

Cumulative n_trials advance: 4348 (post iter 072) + 4 cfgs × 3 ds = 4360.

Citations
---------
* Gayed (2016) — `[leverage_for_the_long_run, p.13, p.16, p.21]`.
* `[risk_parity, ch.1, ch.4]`, `[systematic_trading, ch.2, ch.11]`.
* Moreira & Muir (2017) — variance-target scaling.
* `[advances_fin_ml, p.31-34, p.162-164]` — parity + no-peek.
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
from gayed_gate_stack import apply_gayed_gate_stack  # noqa: E402
from numpy_reference_gayed import apply_gayed_gate_stack_np  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
COST_BPS_PER_LEG = 0.0002  # 2 bps per unit ∆position (matches iter 016)

CFGS: list[dict] = [
    {
        "cfg_id": "gayed_g16_vt15_L21_cap20",
        "eq_weight": 0.6, "bd_weight": 0.4,
        "target_vol": 0.15, "lookback": 21, "max_leverage": 2.0,
        "ma_period": 200,
        "rationale": "iter 016 baseline + Gayed gate (minimal change)",
    },
    {
        "cfg_id": "gayed_g16_vt15_L21_cap25",
        "eq_weight": 0.6, "bd_weight": 0.4,
        "target_vol": 0.15, "lookback": 21, "max_leverage": 2.5,
        "ma_period": 200,
        "rationale": "higher Carver IDM cap, same vol target",
    },
    {
        "cfg_id": "gayed_g16_vt18_L21_cap25",
        "eq_weight": 0.6, "bd_weight": 0.4,
        "target_vol": 0.18, "lookback": 21, "max_leverage": 2.5,
        "ma_period": 200,
        "rationale": "primary cfg (higher vol target, IDM cap)",
    },
    {
        "cfg_id": "gayed_g16_vt20_L21_cap25",
        "eq_weight": 0.6, "bd_weight": 0.4,
        "target_vol": 0.20, "lookback": 21, "max_leverage": 2.5,
        "ma_period": 200,
        "rationale": "aggressive vol target — sensitivity",
    },
]

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY", "bond_symbol": "IEF",
        "start": "2006-01-03", "end": "2026-04-15",
        "role": "SPY+IEF ~20y (IEF-inception-aligned, matches iter 016)",
    },
    "spy_real": {
        "equity_symbol": "SPY", "bond_symbol": "IEF",
        "start": "2009-06-25", "end": "2026-04-15",
        "role": "SPY+IEF 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ", "bond_symbol": "IEF",
        "start": "2010-02-12", "end": "2026-04-15",
        "role": "QQQ+IEF 16y tech-heavy (gate signal on QQQ)",
    },
}


def load_pair(eq: str, bd: str, start: str, end: str) -> tuple[pd.DataFrame, pd.Series]:
    """Returns (returns_df with [eq,bd] cols, px_eq adj_close series)."""
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
    px_eq = p["eq"].loc[r.index]
    return r, px_eq


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


def run_cfg(cfg: dict, returns: pd.DataFrame, px_eq: pd.Series) -> tuple[dict, pd.Series, pd.Series]:
    eq_col, bd_col = returns.columns
    net, pos_eq, pos_bd, scale, gate_on = apply_gayed_gate_stack(
        returns[eq_col], returns[bd_col], px_eq,
        eq_weight=cfg["eq_weight"], bd_weight=cfg["bd_weight"],
        target_vol=cfg["target_vol"], lookback=cfg["lookback"],
        max_leverage=cfg["max_leverage"], ma_period=cfg["ma_period"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq_curve = (1.0 + net).cumprod()
    cap_hit = float(
        np.isclose(scale.to_numpy(float), cfg["max_leverage"], atol=1e-9).mean()
    )
    on_frac = float(gate_on.mean())
    flips = int(gate_on.astype(int).diff().abs().fillna(0).sum())
    turnover_total = 0.0
    for c, pos in [("EQ", pos_eq), ("BD", pos_bd)]:
        dpos = pos.diff().abs().fillna(pos.iloc[0])
        turnover_total += float(dpos.sum() * 252.0 / len(dpos))

    m = {
        "cfg_id": cfg["cfg_id"],
        **{k: cfg[k] for k in ["eq_weight", "bd_weight", "target_vol",
                                "lookback", "max_leverage", "ma_period"]},
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "scale_mean": float(scale.mean()),
        "scale_median": float(scale.median()),
        "scale_min": float(scale.min()),
        "scale_max": float(scale.max()),
        "scale_cap_hit_frac": cap_hit,
        "scale_zero_frac": float((scale < 1e-6).mean()),
        "gate_on_fraction": on_frac,
        "gate_flips": flips,
        "turnover_annual_total": turnover_total,
    }
    return m, net, gate_on


def run_cfg_numpy(cfg: dict, returns: pd.DataFrame, px_eq: pd.Series) -> dict:
    """G7 cross-lib echo — pure-numpy reference CAGR for parity."""
    eq_col, bd_col = returns.columns
    net_np, _, _, _, _ = apply_gayed_gate_stack_np(
        returns[eq_col].to_numpy(), returns[bd_col].to_numpy(), px_eq.to_numpy(),
        eq_weight=cfg["eq_weight"], bd_weight=cfg["bd_weight"],
        target_vol=cfg["target_vol"], lookback=cfg["lookback"],
        max_leverage=cfg["max_leverage"], ma_period=cfg["ma_period"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq_curve = np.cumprod(1.0 + net_np)
    years = len(net_np) / 252.0
    np_cagr = float(eq_curve[-1] ** (1.0 / years) - 1.0)
    return {"np_cagr": np_cagr, "np_bars": int(len(net_np))}


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": CFGS,
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "crosslib": {},
        "iter_label": "073-2026-04-25-1659-gayed-ma-gate-on-iter016",
    }

    pairs: dict[str, tuple[pd.DataFrame, pd.Series]] = {}
    for ds_name, ds in DATASETS.items():
        r, px = load_pair(ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"])
        pairs[ds_name] = (r, px)
        bench = benchmark_metrics(r.iloc[:, 0])
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

    for ds_name, (r, px) in pairs.items():
        print(f"\n=== {ds_name} ({len(r)} bars, gate signal on {DATASETS[ds_name]['equity_symbol']}) ===")
        all_results["runs"][ds_name] = {}
        all_results["returns_series"][ds_name] = {}
        all_results["crosslib"][ds_name] = {}
        for cfg in CFGS:
            m, net, gate_on = run_cfg(cfg, r, px)
            xl = run_cfg_numpy(cfg, r, px)
            diff_pp = abs(xl["np_cagr"] - m["cagr"]) * 100
            all_results["runs"][ds_name][cfg["cfg_id"]] = m
            all_results["returns_series"][ds_name][cfg["cfg_id"]] = {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
            all_results["crosslib"][ds_name][cfg["cfg_id"]] = {
                "engine_cagr": m["cagr"],
                "np_cagr": xl["np_cagr"],
                "abs_diff_pp": float(diff_pp),
                "n_bars_engine": m["bars"],
                "n_bars_np": xl["np_bars"],
            }
            edge = m["sharpe"] - all_results["benchmarks"][ds_name]["sharpe"]
            print(
                f"  {m['cfg_id']:30s} S={m['sharpe']:+.4f} (Δ{edge:+.4f}) "
                f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
                f"on={m['gate_on_fraction']:.2%} flips={m['gate_flips']:3d} "
                f"scale_avg={m['scale_mean']:.2f} G7={diff_pp:.4f}pp"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
