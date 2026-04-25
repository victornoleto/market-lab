"""Iter 033 — NTSX long-duration variant (0.9 SPY + 0.6 TLT) backtests.

**Pre-committed cfg** ``ntsx_synth_90_60_spy_tlt`` — see hypothesis.md.
NO grid, NO sweep, NO post-hoc selection. Single fixed-weight stack.

Reuses iter 015's stacking engine verbatim (`apply_static_stack`) —
the only structural change is the bond ticker (TLT vs IEF) and the
educational window (TLT-inception-aligned 2002-07-26 vs IEF's 2006-01-03).

Cumulative n_trials advance after iter 033: 4285 → 4288 (+3).

Citations
---------
* `[risk_parity, p.5, p.10-11, ch.1]` — risk-parity static stack.
* `[risk_parity, ch.5]` — bond term-premium decomposition.
* `[leverage_for_the_long_run, p.19-20]` — leverage on diversified base.
* Koijen-Moskowitz-Pedersen-Vrugt (2018), JFE 127(2) — bond carry premium
  largest at 20-30y duration band.
* WisdomTree NTSX prospectus — 90/60 weights are manufacturer-prescribed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER015_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "015-2026-04-24-1704-return-stacked-static-ntsx"

sys.path.insert(0, str(ITER015_DIR))
from synth_stacked_etf import apply_static_stack  # noqa: E402

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
    "cfg_id": "ntsx_synth_90_60_spy_tlt",
    "eq_w": 0.90,
    "bd_w": 0.60,
    "rebalance": "daily",
    "funding_cost_modeled": False,
}
COST_BPS_PER_LEG = 0.0002  # 2 bps per unit per-leg ∆position (matches iter 015)

# ---------------------------------------------------------------------------
# Datasets — TLT-aligned windows (TLT first cache bar 2002-07-26)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "start": "2002-07-26",
        "end": "2026-04-15",
        "role": "SPY+TLT ~24y (TLT-inception-aligned, 4y longer than iter 015 IEF)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+TLT 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "TLT",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+TLT 16y tech-heavy",
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
    net, positions, scale = apply_static_stack(
        returns[eq_col],
        returns[bd_col],
        eq_w=CFG["eq_w"],
        bd_w=CFG["bd_w"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq = (1.0 + net).cumprod()
    cap_hit = float(np.isclose(scale.to_numpy(float), CFG["eq_w"] + CFG["bd_w"], atol=1e-12).mean())
    turnover_per_leg = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0])
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    m = {
        "cfg_id": CFG["cfg_id"],
        "eq_w": CFG["eq_w"],
        "bd_w": CFG["bd_w"],
        "total_leverage": CFG["eq_w"] + CFG["bd_w"],
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "scale_mean": float(scale.mean()),
        "scale_median": float(scale.median()),
        "scale_cap_hit_frac": cap_hit,
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
        "iter_label": "033-2026-04-25-0056-ntsx-tlt-long-duration",
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
            f"  {m['cfg_id']:32s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale={m['scale_median']:.2f}"
        )
        print(f"    turnover/yr total={m['turnover_annual_total']:.4f} (≈ 0 expected for static)")

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
