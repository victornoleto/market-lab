"""Iter 034 — NTSX bond-carry sleeve (3-leg static stack) backtests.

**Pre-committed cfg** ``ntsx_synth_90_spy_40_ief_20_tlt`` — see hypothesis.md.
NO grid, NO sweep, NO post-hoc selection. Single fixed-weight 3-leg stack.

Reuses iter 034's local 3-leg stacking engine
(`apply_static_stack_3leg`) — generalisation of iter 015's primitive
to support a third leg (long-duration bond) at preserved total bond
notional. Iter 015's 2-leg primitive is recoverable by setting
``bd_long_w == 0`` (verified by `test_3leg_stack_returns_match_2leg_when_alpha_zero`).

Cumulative n_trials advance after iter 034: 4288 → 4291 (+3).

Citations
---------
* `[risk_parity, ch.5]` — bond term-premium decomposition.
* `[risk_parity, p.5, p.10-11, ch.1]` — risk-parity static stack.
* `[leverage_for_the_long_run, p.19-20]` — leverage on diversified base.
* Koijen-Moskowitz-Pedersen-Vrugt (2018), JFE 127(2) — cross-sectional
  bond carry premium.
* WisdomTree NTSX prospectus — 90/60 weights (preserved verbatim).
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
    "cfg_id": "ntsx_synth_90_spy_40_ief_20_tlt",
    "eq_w": 0.90,
    "bd_short_w": 0.40,  # 0.60 × (1 − α=0.2)
    "bd_long_w": 0.20,   # 0.60 × α=0.2
    "rebalance": "daily",
    "funding_cost_modeled": False,
}
COST_BPS_PER_LEG = 0.0002  # 2 bps per unit per-leg ∆position (matches iter 015/033)

# ---------------------------------------------------------------------------
# Datasets — TLT-aligned windows (TLT first cache bar 2002-07-26)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_short_symbol": "IEF",
        "bond_long_symbol": "TLT",
        "start": "2002-07-26",
        "end": "2026-04-15",
        "role": "SPY+IEF+TLT 24y (TLT-inception-aligned, matches iter 033 window)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_short_symbol": "IEF",
        "bond_long_symbol": "TLT",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+IEF+TLT 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_short_symbol": "IEF",
        "bond_long_symbol": "TLT",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+IEF+TLT 16y tech-heavy",
    },
}


def load_triple_returns(
    eq: str, bd_short: str, bd_long: str, start: str, end: str,
) -> pd.DataFrame:
    """Load and inner-join three return streams."""
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd_s = pd.read_parquet(TIINGO_DIR / f"{bd_short}.parquet")
    df_bd_l = pd.read_parquet(TIINGO_DIR / f"{bd_long}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_s = (df_bd_s.index >= start) & (df_bd_s.index <= end)
    m_l = (df_bd_l.index >= start) & (df_bd_l.index <= end)
    p = pd.concat({
        "eq": df_eq.loc[m_eq, "adj_close"],
        "bd_s": df_bd_s.loc[m_s, "adj_close"],
        "bd_l": df_bd_l.loc[m_l, "adj_close"],
    }, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd_short, bd_long]
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
    eq_col, bd_s_col, bd_l_col = returns.columns
    net, positions, scale = apply_static_stack_3leg(
        returns[eq_col],
        returns[bd_s_col],
        returns[bd_l_col],
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
        "bd_short_w": CFG["bd_short_w"],
        "bd_long_w": CFG["bd_long_w"],
        "bond_notional": CFG["bd_short_w"] + CFG["bd_long_w"],
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
        "iter_label": "034-2026-04-25-0120-ntsx-bond-carry-sleeve",
    }

    triples: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_triple_returns(
            ds["equity_symbol"], ds["bond_short_symbol"], ds["bond_long_symbol"],
            ds["start"], ds["end"],
        )
        triples[ds_name] = r
        bench_series = r.iloc[:, 0]
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        # 3 pairwise correlations (eq~bd_s, eq~bd_l, bd_s~bd_l)
        corr_mat = r.corr()
        eq_col, bd_s_col, bd_l_col = r.columns
        all_results["leg_correlations"][ds_name] = {
            "eq_bd_short": float(corr_mat.loc[eq_col, bd_s_col]),
            "eq_bd_long":  float(corr_mat.loc[eq_col, bd_l_col]),
            "bd_short_bd_long": float(corr_mat.loc[bd_s_col, bd_l_col]),
        }
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_short_symbol']}+{ds['bond_long_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )
        print(
            f"  ρ(eq,bd_s)={all_results['leg_correlations'][ds_name]['eq_bd_short']:+.3f} "
            f"ρ(eq,bd_l)={all_results['leg_correlations'][ds_name]['eq_bd_long']:+.3f} "
            f"ρ(bd_s,bd_l)={all_results['leg_correlations'][ds_name]['bd_short_bd_long']:+.3f}"
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
            f"  {m['cfg_id']:36s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale={m['scale_median']:.2f} bond_notional={m['bond_notional']:.2f}"
        )
        print(f"    turnover/yr total={m['turnover_annual_total']:.4f} (≈ 0 expected for static)")

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
