"""Iter 043 — Hysteretic VIX-regime weights on iter 037's 3-leg static stack.

**Pre-committed cfg** ``hysteretic_vix_low18_high22_w70_40_40_30_55_55``
— see `hypothesis.md`. NO grid, NO sweep, NO post-hoc selection.

Same iter 041 weights (calm 0.70/0.40/0.40, stress 0.30/0.55/0.55) and
identical datasets / cost model. Only the regime gate is changed: a
Schmitt trigger with low=18, high=22 around iter 041's binary 20.

Cumulative n_trials advance after iter 043: 4307 → 4308 (+1).

Citations
---------
* `[advances_fin_ml, ch.17-18]` — regime detection with whipsaw cost.
* `[advances_fin_ml, p.162-164]` — no-lookahead lag.
* `[advances_fin_ml, p.222-223]` — DSR + cumulative n_trials.
* `[risk_parity, ch.5]` — risk-parity stack with regime weight tilts.
* Hamilton (1989), Econometrica 57(2), DOI 10.2307/1912559.
* Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098.
* Bekaert-Hoerova (2014), J Econometrics 183(2), SSRN 2294327.
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
from regime_weights_hysteretic import apply_regime_weights_hysteretic_3leg  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "hysteretic_vix_low18_high22_w70_40_40_30_55_55",
    "low_threshold": 18.0,
    "high_threshold": 22.0,
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},   # total 1.50×
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},   # total 1.40×
    "vix_lag_days": 1,
    "rebalance": "daily",
    "regime_signal": "VIX level (1-day lag) with Schmitt trigger [18, 22]",
    "funding_cost_modeled": False,
}
COST_BPS_PER_LEG = 0.0002

# ---------------------------------------------------------------------------
# Datasets — iter 041 windows verbatim (apples-to-apples comparison)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "start": "2004-11-19",
        "end": "2026-04-15",
        "role": "SPY+IEF+GLD 21y (GLD-aligned, matches iter 035-042)",
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
    pad_start = (pd.Timestamp(start) - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    m = (df.index >= pad_start) & (df.index <= end)
    return df.loc[m, "VIX"]


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
    returns: pd.DataFrame, vix: pd.Series,
) -> tuple[dict, pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    eq_col, bd_col, gld_col = returns.columns
    net, positions, scale, regime = apply_regime_weights_hysteretic_3leg(
        returns[eq_col], returns[bd_col], returns[gld_col], vix,
        calm_weights=CFG["calm_weights"],
        stress_weights=CFG["stress_weights"],
        low_threshold=CFG["low_threshold"],
        high_threshold=CFG["high_threshold"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq_curve = (1.0 + net).cumprod()
    avg_lev = float(scale.mean())
    calm_frac = float((regime == 1).mean())
    stress_frac = float((regime == 0).mean())
    flip_mask = regime.diff().abs() > 0.5
    n_flips = int(flip_mask.fillna(0).sum())

    # Band-occupancy fraction: fraction of bars where VIX is in [low, high)
    vix_aligned = vix.reindex(returns.index, method="ffill").fillna(CFG["high_threshold"])
    vix_lag = vix_aligned.shift(1)
    vix_lag.iloc[0] = vix_aligned.iloc[0]
    in_band = (vix_lag >= CFG["low_threshold"]) & (vix_lag < CFG["high_threshold"])
    band_frac = float(in_band.mean())

    turnover_per_leg: dict[str, float] = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0])
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    m = {
        "cfg_id": CFG["cfg_id"],
        "low_threshold": CFG["low_threshold"],
        "high_threshold": CFG["high_threshold"],
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
        "band_frac": band_frac,  # bars where VIX is in [low, high)
        "n_regime_flips": n_flips,
        "regime_round_trips_per_year": float(n_flips * 252.0 / (2 * max(len(regime), 1))),
        "turnover_annual_per_leg": turnover_per_leg,
        "turnover_annual_total": turnover_total,
        "conditional_metrics": conditional_metrics(net, regime),
    }
    return m, net, positions, scale, regime


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [{
            **CFG,
            "calm_weights": dict(CFG["calm_weights"]),
            "stress_weights": dict(CFG["stress_weights"]),
        }],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations": {},
        "regime_summary": {},
        "pre_committed": True,
        "iter_label": "043-2026-04-25-0441-hysteretic-vix-regime-weights",
    }

    triples: dict[str, pd.DataFrame] = {}
    vixes: dict[str, pd.Series] = {}
    for ds_name, ds in DATASETS.items():
        r = load_triple_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"],
            ds["start"], ds["end"],
        )
        triples[ds_name] = r
        v = load_vix(ds["start"], ds["end"])
        vixes[ds_name] = v
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
        v_aligned = v.reindex(r.index, method="ffill").fillna(CFG["high_threshold"])
        v_lag = v_aligned.shift(1).fillna(v_aligned.iloc[0])
        in_band = (v_lag >= CFG["low_threshold"]) & (v_lag < CFG["high_threshold"])
        all_results["regime_summary"][ds_name] = {
            "vix_first": str(v_aligned.index[0].date()),
            "vix_last": str(v_aligned.index[-1].date()),
            "vix_mean": float(v_aligned.mean()),
            "vix_median": float(v_aligned.median()),
            "below_low_frac_lagged": float((v_lag < CFG["low_threshold"]).mean()),
            "in_band_frac_lagged": float(in_band.mean()),
            "above_high_frac_lagged": float((v_lag >= CFG["high_threshold"]).mean()),
        }
        rs = all_results["regime_summary"][ds_name]
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']}+{ds['gold_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )
        print(
            f"  VIX mean={rs['vix_mean']:.2f}, median={rs['vix_median']:.2f}, "
            f"below_18={rs['below_low_frac_lagged']:.3f}, "
            f"in_band={rs['in_band_frac_lagged']:.3f}, "
            f"above_22={rs['above_high_frac_lagged']:.3f}"
        )

    for ds_name, r in triples.items():
        print(f"\n=== {ds_name} ({len(r)} bars) — single cfg {CFG['cfg_id']} ===")
        m, net, positions, scale, regime = run_single_cfg(r, vixes[ds_name])
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
            f"  {m['cfg_id']:55s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"avg_lev={m['scale_mean']:.3f} flips={m['n_regime_flips']} "
            f"RT/yr={m['regime_round_trips_per_year']:.2f}"
        )
        cm = m["conditional_metrics"]
        print(
            f"    calm: Sharpe={cm['calm']['sharpe']:+.3f} bars={cm['calm']['n_bars']} "
            f"({m['calm_frac']:.1%}) | stress: Sharpe={cm['stress']['sharpe']:+.3f} "
            f"bars={cm['stress']['n_bars']} ({m['stress_frac']:.1%})"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
