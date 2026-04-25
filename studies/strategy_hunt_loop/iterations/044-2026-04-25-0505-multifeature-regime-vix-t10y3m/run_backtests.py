"""Iter 044 — Multi-feature composite regime gate (VIX + T10Y3M)
on iter 037's 3-leg static stack.

**Pre-committed cfg** ``multifeature_vix_t10y3m_z252_eq_w_tau0_70_40_40_30_55_55``
— see `hypothesis.md`. NO grid, NO sweep, NO post-hoc selection.

Cumulative n_trials advance after iter 044: 4308 → 4309 (+1).

Citations
---------
* `[advances_fin_ml, ch.17-18]` — multi-feature regime detection.
* `[risk_parity, ch.5]` — preserved 3-leg risk-parity stack.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day lag.
* Estrella-Hardouvelis (1991), JF 46(2), DOI 10.1111/j.1540-6261.1991.tb04617.x.
* Bauer-Mertens (2018), FRBSF Economic Letter 2018-07.
* Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098.
* Bekaert-Hoerova (2014), J Econometrics 183(2), SSRN 2294327.
* Hamilton (1989), Econometrica 57(2), DOI 10.2307/1912559.
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
from multifeature_regime_gate import apply_multifeature_regime_3leg  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"
TS_PATH = ROOT / "data" / "external" / "macro" / "t10y3m_daily.parquet"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "multifeature_vix_t10y3m_z252_eq_w_tau0_70_40_40_30_55_55",
    "z_window": 252,
    "feature_weights": {"vix": 0.5, "neg_t10y3m": 0.5},
    "stress_threshold": 0.0,
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},   # total 1.50×
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},   # total 1.40×
    "feature_lag_days": 1,
    "rebalance": "daily",
    "regime_signal": "VIX z + (-T10Y3M) z, equal-weighted, threshold 0",
    "funding_cost_modeled": False,
}
COST_BPS_PER_LEG = 0.0002

# ---------------------------------------------------------------------------
# Datasets — iter 037-041 windows verbatim
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "start": "2004-11-19",
        "end": "2026-04-15",
        "role": "SPY+IEF+GLD 21y (GLD-aligned, matches iter 035-041)",
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


def load_vix(start: str, end: str) -> pd.Series:
    df = pd.read_parquet(VIX_PATH)
    pad_start = (pd.Timestamp(start) - pd.Timedelta(days=400)).strftime("%Y-%m-%d")
    m = (df.index >= pad_start) & (df.index <= end)
    return df.loc[m, "VIX"]


def load_term_spread(start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TS_PATH)
    pad_start = (pd.Timestamp(start) - pd.Timedelta(days=400)).strftime("%Y-%m-%d")
    m = (df.index >= pad_start) & (df.index <= end)
    return df.loc[m, "term_spread"]


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


def conditional_metrics(returns: pd.Series, regime: pd.Series) -> dict:
    cond: dict = {}
    for label, code in [("calm", 1), ("stress", 0)]:
        mask = regime == code
        sub = returns[mask]
        if len(sub) < 5:
            cond[label] = {"sharpe": float("nan"), "n_bars": int(mask.sum())}
            continue
        eq = (1.0 + sub).cumprod()
        cond[label] = {
            "sharpe": float(_sharpe(sub)),
            "mdd": float(_max_drawdown(eq)),
            "n_bars": int(mask.sum()),
            "frac_positive": float((sub > 0).mean()),
        }
    return cond


def run_single_cfg(
    returns: pd.DataFrame,
    vix: pd.Series,
    term_spread: pd.Series,
) -> tuple[dict, pd.Series, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    eq_col, bd_col, gld_col = returns.columns
    net, positions, scale, regime, composite = apply_multifeature_regime_3leg(
        returns[eq_col], returns[bd_col], returns[gld_col],
        vix, term_spread,
        calm_weights=CFG["calm_weights"],
        stress_weights=CFG["stress_weights"],
        z_window=CFG["z_window"],
        feature_weights=CFG["feature_weights"],
        stress_threshold=CFG["stress_threshold"],
        lag_days=CFG["feature_lag_days"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq_curve = (1.0 + net).cumprod()
    avg_lev = float(scale.mean())
    calm_frac = float((regime == 1).mean())
    stress_frac = float((regime == 0).mean())
    flip_mask = regime.diff().abs() > 0.5
    n_flips = int(flip_mask.fillna(0).sum())

    turnover_per_leg: dict[str, float] = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0])
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    m = {
        "cfg_id": CFG["cfg_id"],
        "z_window": CFG["z_window"],
        "feature_weights": dict(CFG["feature_weights"]),
        "stress_threshold": CFG["stress_threshold"],
        "calm_weights": dict(CFG["calm_weights"]),
        "stress_weights": dict(CFG["stress_weights"]),
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "scale_mean": avg_lev,
        "scale_median": float(scale.median()),
        "calm_frac": calm_frac,
        "stress_frac": stress_frac,
        "n_regime_flips": n_flips,
        "regime_round_trips_per_year": float(n_flips * 252.0 / (2 * max(len(regime), 1))),
        "composite_mean": float(composite.mean()),
        "composite_std": float(composite.std()),
        "composite_p10": float(composite.quantile(0.1)),
        "composite_p90": float(composite.quantile(0.9)),
        "turnover_annual_per_leg": turnover_per_leg,
        "turnover_annual_total": turnover_total,
        "conditional_metrics": conditional_metrics(net, regime),
    }
    return m, net, positions, scale, regime, composite


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [{
            **CFG,
            "calm_weights": dict(CFG["calm_weights"]),
            "stress_weights": dict(CFG["stress_weights"]),
            "feature_weights": dict(CFG["feature_weights"]),
        }],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations": {},
        "regime_summary": {},
        "feature_correlations": {},
        "pre_committed": True,
        "iter_label": "044-2026-04-25-0505-multifeature-regime-vix-t10y3m",
    }

    triples: dict[str, pd.DataFrame] = {}
    vixes: dict[str, pd.Series] = {}
    spreads: dict[str, pd.Series] = {}
    for ds_name, ds in DATASETS.items():
        r = load_triple_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"],
            ds["start"], ds["end"],
        )
        triples[ds_name] = r
        v = load_vix(ds["start"], ds["end"])
        vixes[ds_name] = v
        ts = load_term_spread(ds["start"], ds["end"])
        spreads[ds_name] = ts

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
        v_aligned = v.reindex(r.index, method="ffill").bfill().fillna(20.0)
        ts_aligned = ts.reindex(r.index, method="ffill").bfill().fillna(0.0)
        feat_corr = float(np.corrcoef(v_aligned.diff().dropna(),
                                       ts_aligned.diff().dropna())[0, 1])
        all_results["feature_correlations"][ds_name] = {
            "vix_change_vs_t10y3m_change": feat_corr,
            "vix_mean": float(v_aligned.mean()),
            "vix_median": float(v_aligned.median()),
            "t10y3m_mean": float(ts_aligned.mean()),
            "t10y3m_median": float(ts_aligned.median()),
        }
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']}+{ds['gold_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )
        fc = all_results["feature_correlations"][ds_name]
        print(
            f"  features: VIX μ={fc['vix_mean']:.2f}, T10Y3M μ={fc['t10y3m_mean']:.2f}, "
            f"corr(ΔVIX,ΔT)={fc['vix_change_vs_t10y3m_change']:+.3f}"
        )

    for ds_name, r in triples.items():
        print(f"\n=== {ds_name} ({len(r)} bars) — single cfg {CFG['cfg_id']} ===")
        m, net, positions, scale, regime, composite = run_single_cfg(
            r, vixes[ds_name], spreads[ds_name],
        )
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": [round(float(x), 10) for x in net.tolist()],
            }
        }
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]
        edge = m["sharpe"] - bench_sharpe
        print(
            f"  {m['cfg_id']:60s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"avg_lev={m['scale_mean']:.3f} flips={m['n_regime_flips']}"
        )
        cm = m["conditional_metrics"]
        print(
            f"    calm: Sharpe={cm['calm']['sharpe']:+.3f} bars={cm['calm']['n_bars']} "
            f"| stress: Sharpe={cm['stress']['sharpe']:+.3f} bars={cm['stress']['n_bars']} "
            f"| RT/yr={m['regime_round_trips_per_year']:.2f} "
            f"composite μ={m['composite_mean']:+.3f} σ={m['composite_std']:.3f}"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
