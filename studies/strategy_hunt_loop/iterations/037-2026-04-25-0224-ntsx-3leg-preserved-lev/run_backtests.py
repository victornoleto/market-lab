"""Iter 037 — leverage-preserved 3-leg static stack: 0.6 SPY + 0.45 IEF + 0.45 GLD.

**Pre-committed cfg** ``ntsx_3leg_preserved_60_45_45_spy_ief_gld`` —
see hypothesis.md. NO grid, NO sweep, NO post-hoc selection. Single
fixed-weight 3-leg stack at iter 015's preserved 1.50× total leverage.

Departure from iter 036: weights redistributed from 0.90/0.60/0.30
(total 1.80×) to **0.60/0.45/0.45 (total 1.50×)**. Equity weight is cut
33% to make budget for an equal-notional GLD leg at preserved
leverage. The 3-leg primitive is vendored verbatim from iter 036
(asset-agnostic; the function does not bake the weights in).

Cumulative n_trials advance after iter 037: 4297 → 4300 (+3).

Citations
---------
* `[risk_parity, ch.5]` — multi-leg risk-parity at preserved total leverage.
* `[risk_parity, p.5, p.10-11, ch.1]` — risk-parity static stack mechanism.
* `[leverage_for_the_long_run, p.19-20]` — leverage on diversified base.
* Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold strategic role.
* Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021 — cross-asset orthogonality.
* Koijen-Moskowitz-Pedersen-Vrugt (2018), JFE 127(2) §3 — gold spot-forward basis ≈ 0.
* Ilmanen (2011), Expected Returns, ch.6 + ch.10 — term + commodity premia.
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
from synth_stacked_etf_3leg import apply_static_stack_3leg  # noqa: E402

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
    "cfg_id": "ntsx_3leg_preserved_60_45_45_spy_ief_gld",
    "eq_w": 0.60,        # equity cut from iter 015/036's 0.90 to make budget
    "bd_short_w": 0.45,  # IEF (re-using iter 036's bd_short_w slot)
    "bd_long_w": 0.45,   # GLD (re-using iter 036's bd_long_w slot)
    "rebalance": "daily",
    "funding_cost_modeled": False,
}
COST_BPS_PER_LEG = 0.0002  # 2 bps per unit per-leg ∆position (matches iter 015/033/034/035/036)

# ---------------------------------------------------------------------------
# Datasets — GLD-aligned windows (preserved verbatim from iter 036)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "start": "2004-11-19",
        "end": "2026-04-15",
        "role": "SPY+IEF+GLD 21y (GLD-inception-aligned, matches iter 035/036 window)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+IEF+GLD 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+IEF+GLD 16y tech-heavy",
    },
}


def load_triple_returns(
    eq: str, bd: str, gld: str, start: str, end: str,
) -> pd.DataFrame:
    """Load and inner-join three return streams (equity, bond, gold)."""
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    df_gld = pd.read_parquet(TIINGO_DIR / f"{gld}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_bd = (df_bd.index >= start) & (df_bd.index <= end)
    m_gld = (df_gld.index >= start) & (df_gld.index <= end)
    p = pd.concat({
        "eq": df_eq.loc[m_eq, "adj_close"],
        "bd": df_bd.loc[m_bd, "adj_close"],
        "gld": df_gld.loc[m_gld, "adj_close"],
    }, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd, gld]
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
    eq_col, bd_col, gld_col = returns.columns
    net, positions, scale = apply_static_stack_3leg(
        returns[eq_col],
        returns[bd_col],
        returns[gld_col],
        eq_w=CFG["eq_w"],
        bd_short_w=CFG["bd_short_w"],
        bd_long_w=CFG["bd_long_w"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq = (1.0 + net).cumprod()
    cap_target = CFG["eq_w"] + CFG["bd_short_w"] + CFG["bd_long_w"]
    cap_hit = float(np.isclose(scale.to_numpy(float), cap_target, atol=1e-12).mean())
    turnover_per_leg: dict[str, float] = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0])
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    m = {
        "cfg_id": CFG["cfg_id"],
        "eq_w": CFG["eq_w"],
        "bd_w": CFG["bd_short_w"],
        "gld_w": CFG["bd_long_w"],
        "diversifier_notional": CFG["bd_short_w"] + CFG["bd_long_w"],
        "total_leverage": cap_target,
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
        "iter_label": "037-2026-04-25-0224-ntsx-3leg-preserved-lev",
    }

    triples: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_triple_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"],
            ds["start"], ds["end"],
        )
        triples[ds_name] = r
        bench_series = r.iloc[:, 0]
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        corr_mat = r.corr()
        eq_col, bd_col, gld_col = r.columns
        all_results["leg_correlations"][ds_name] = {
            "eq_bd": float(corr_mat.loc[eq_col, bd_col]),
            "eq_gld": float(corr_mat.loc[eq_col, gld_col]),
            "bd_gld": float(corr_mat.loc[bd_col, gld_col]),
        }
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']}+{ds['gold_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )
        print(
            f"  ρ(eq,bd)={all_results['leg_correlations'][ds_name]['eq_bd']:+.3f} "
            f"ρ(eq,gld)={all_results['leg_correlations'][ds_name]['eq_gld']:+.3f} "
            f"ρ(bd,gld)={all_results['leg_correlations'][ds_name]['bd_gld']:+.3f}"
        )

    for ds_name, r in triples.items():
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
            f"  {m['cfg_id']:48s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale={m['scale_median']:.2f} total_lev={m['total_leverage']:.2f}"
        )
        print(f"    turnover/yr total={m['turnover_annual_total']:.4f} (≈ 0 expected for static)")

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
