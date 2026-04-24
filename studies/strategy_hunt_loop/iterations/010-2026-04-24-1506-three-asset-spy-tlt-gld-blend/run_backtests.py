"""Iter 010 — Three-leg vol-managed SPY+TLT+GLD blend runner.

**Pre-committed cfg** ``vt15_L21_cap20_3leg`` (see hypothesis.md).
NO grid, NO sweep, NO post-hoc selection. Params are IDENTICAL to
iter 008's 2-leg cfg — the only change is adding GLD as a third leg.

Cumulative n_trials advance after iter 010: 4243 → 4246.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity N-asset form.
* `[systematic_trading, p.144, p.170-171, ch.11]` — target_vol / IDM cap.
* Moreira & Muir (2017), *JoF* 72(4) — variance-scaling form.
* Asness-Frazzini-Pedersen (2012) — cross-asset risk-parity argument.
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
from three_leg_blend import apply_blend_variance_target_3leg  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# ---------------------------------------------------------------------------
# Pre-committed single config (identical params to iter 008, new leg added)
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "vt15_L21_cap20_3leg",
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
}
COST_BPS_PER_LEG = 0.0002  # 2 bps per unit of per-leg position change

# ---------------------------------------------------------------------------
# Datasets — iter 008 universes extended with GLD as 3rd leg.
# GLD first cache bar: 2004-11-18 → educational window shrinks vs iter 008.
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "gold_symbol": "GLD",
        "start": "2004-11-18",
        "end": "2026-04-15",
        "role": "SPY+TLT+GLD ~21y (GLD-constrained start)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "gold_symbol": "GLD",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+TLT+GLD 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "TLT",
        "gold_symbol": "GLD",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+TLT+GLD 16y tech-heavy",
    },
}


def load_triple_returns(eq: str, bd: str, gd: str, start: str, end: str) -> pd.DataFrame:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    df_gd = pd.read_parquet(TIINGO_DIR / f"{gd}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_bd = (df_bd.index >= start) & (df_bd.index <= end)
    m_gd = (df_gd.index >= start) & (df_gd.index <= end)
    p = pd.concat({
        "eq": df_eq.loc[m_eq, "adj_close"],
        "bd": df_bd.loc[m_bd, "adj_close"],
        "gd": df_gd.loc[m_gd, "adj_close"],
    }, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd, gd]
    return r


def benchmark_metrics(returns: pd.Series) -> dict:
    eq = (1.0 + returns).cumprod()
    return {
        "sharpe": _sharpe(returns),
        "cagr": _cagr(eq),
        "mdd": _max_drawdown(eq),
        "n_bars": len(returns),
        "first": str(returns.index[0].date()),
        "last": str(returns.index[-1].date()),
    }


def run_single_cfg(returns: pd.DataFrame) -> tuple[dict, pd.Series, pd.DataFrame, pd.Series]:
    eq_col, bd_col, gd_col = returns.columns
    net, positions, scale = apply_blend_variance_target_3leg(
        returns[eq_col], returns[bd_col], returns[gd_col],
        target_vol=CFG["target_vol"],
        lookback=CFG["lookback"],
        max_leverage=CFG["max_leverage"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq = (1.0 + net).cumprod()
    cap_hit = float(
        np.isclose(scale.to_numpy(float), CFG["max_leverage"], rtol=1e-9, atol=1e-12).mean()
    )
    # Median weight per leg.
    w = positions.div(scale.replace(0, np.nan), axis=0)
    w_medians = {c: float(w[c].median()) for c in positions.columns}
    turnover_per_leg = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0])
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = sum(turnover_per_leg.values())

    m = {
        "cfg_id": CFG["cfg_id"],
        "target_vol": CFG["target_vol"],
        "lookback": CFG["lookback"],
        "max_leverage": CFG["max_leverage"],
        "bars": len(net),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "scale_mean": float(scale.mean()),
        "scale_median": float(scale.median()),
        "scale_cap_hit_frac": cap_hit,
        "w_median": w_medians,
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
        "reference_iter": "008-2026-04-24-1411-single-cfg-ex-ante-blend",
    }

    triples: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_triple_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"],
            ds["start"], ds["end"],
        )
        triples[ds_name] = r
        # Equity-leg benchmark for custom scoring on educational.
        bench_series = r.iloc[:, 0]
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        corr_mat = r.corr()
        all_results["leg_correlations"][ds_name] = {
            "eq_bd": float(corr_mat.iloc[0, 1]),
            "eq_gd": float(corr_mat.iloc[0, 2]),
            "bd_gd": float(corr_mat.iloc[1, 2]),
        }
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']}+{ds['gold_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%} "
            f"ρ(eq,bd)={corr_mat.iloc[0, 1]:+.3f} "
            f"ρ(eq,gd)={corr_mat.iloc[0, 2]:+.3f} "
            f"ρ(bd,gd)={corr_mat.iloc[1, 2]:+.3f}"
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
            f"  {m['cfg_id']:24s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale_med={m['scale_median']:.2f} cap_hit={m['scale_cap_hit_frac']:.1%}"
        )
        w_str = " ".join(f"{c}:{m['w_median'][c]:.2f}" for c in positions.columns)
        print(f"    weight_median: {w_str}")
        print(f"    turnover/yr total={m['turnover_annual_total']:.2f}")

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
