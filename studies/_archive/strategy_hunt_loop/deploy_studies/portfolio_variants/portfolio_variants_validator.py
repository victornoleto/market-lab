"""V_HYBRID variants — search for empirically better Sharpe+CAGR+MDD.

User clarified (2026-04-26): "I like investing, like studying. Don't mind a
'not so simple' portfolio if it makes sense and produces better
Sharpe+CAGR+MDD."

Goal: find empirically dominant variant of V_HYBRID by adding orthogonal
sleeves (managed futures) and more capital efficiency (NTSI/NTSE/RSST synth).

Strategies tested (all 1994-2026, 32y synth window):

  V_HYBRID                — baseline (V3_1 with NTSX replacing AVUS)
  V_HYBRID_MF             — adds 10% KMLM (managed futures, orthogonal)
  V_HYBRID_GLOBAL_STACK   — adds NTSI_synth + NTSE_synth (full intl/EM stacking)
  V_HYBRID_RSST           — replaces NTSX with RSST (S&P + MF stacked)
  V_HYBRID_KITCHEN_SINK   — combine MF + global stacking + RSSB

Synth formulas (all use testfolio-validated -0.50×CASH financing model):
  NTSX = 0.90 SPYSIM + 0.60 IEFSIM - 0.50 CASHX
  NTSI = 0.90 VEASIM + 0.60 IEFSIM - 0.50 CASHX
  NTSE = 0.90 VWOSIM + 0.60 IEFSIM - 0.50 CASHX
  RSST = 1.00 SPYSIM + 1.00 KMLMSIM - 1.00 CASHX (S&P + MF + financing)
  AVNM = VXUSSIM (cap-weighted intl proxy)

CAVEAT: NTSI/NTSE were explicitly REJECTED by Plano C V3.5 (2026-04-23)
based on real 2021-2026 data showing AVDE beat NTSI by +4.6pp CAGR. Testing
here on 32y synth to see if longer-window evidence contradicts that decision.

Citations
---------
* Same testfolio-validated formula as v1_vs_planoc_validator.py.
* WisdomTree NTSX/NTSI/NTSE prospectuses — 90% equity + 60% Treasury futures.
* Newfound + ReSolve "Return Stacked" series — RSST/RSSY/RSSB methodology.
* Hurst, Ooi, Pedersen (2017). "A Century of Evidence on Trend-Following."
  J. Portfolio Management 44(1) — managed futures historical performance.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
TF_PATH = ROOT / "data/testfolio/cache/history.parquet"
OUT_DIR = Path(__file__).resolve().parent
TRADING_DAYS = 252


def returns_from_prices(p: pd.Series) -> pd.Series:
    return p.pct_change().dropna()


def synth_stacked(r_eq, r_bond, r_cash, eq_w=0.90, bond_w=0.60, cash_w=-0.50):
    """Generic return-stacked formula: eq + bond + cash_short."""
    common = r_eq.index.intersection(r_bond.index).intersection(r_cash.index)
    return eq_w * r_eq.loc[common] + bond_w * r_bond.loc[common] + cash_w * r_cash.loc[common]


def metrics(r: pd.Series, name: str = "") -> dict:
    eq = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS
    sd = r.std(ddof=1)
    sharpe = float(np.sqrt(TRADING_DAYS) * r.mean() / sd) if sd > 0 else float("nan")
    cagr = float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    mdd = float((1 - eq / eq.cummax()).max())
    return {"name": name, "n_bars": len(r), "sharpe": sharpe, "cagr": cagr, "mdd": mdd}


def rolling_window_metrics(r: pd.Series, window_years: int) -> pd.DataFrame:
    win = window_years * TRADING_DAYS
    if len(r) < win:
        return pd.DataFrame()
    out_idx = r.index[win - 1:]
    rows = []
    arr = r.values
    for i in range(len(out_idx)):
        seg = arr[i:i + win]
        sd = seg.std(ddof=1)
        s = (np.sqrt(TRADING_DAYS) * seg.mean() / sd) if sd > 0 else np.nan
        eq = (1 + seg).cumprod()
        c = eq[-1] ** (1 / window_years) - 1
        m = (1 - eq / np.maximum.accumulate(eq)).max()
        rows.append({"sharpe": s, "cagr": c, "mdd": m})
    return pd.DataFrame(rows, index=out_idx[:len(rows)])


def stress_window(r, start, end):
    seg = r.loc[start:end]
    if len(seg) == 0:
        return {"return": np.nan, "mdd": np.nan, "n_bars": 0}
    ret = (1 + seg).prod() - 1
    eq = (1 + seg).cumprod()
    mdd = (eq / eq.cummax() - 1).min()
    return {"return": float(ret), "mdd": float(mdd), "n_bars": len(seg)}


# --- Strategies --------------------------------------------------------------


def build_returns(df):
    """Build dict of base + synth returns for portfolio assembly."""
    r_spy = returns_from_prices(df["SPYSIM"])
    r_vea = returns_from_prices(df["VEASIM"])
    r_vwo = returns_from_prices(df["VWOSIM"])
    r_vbr = returns_from_prices(df["VBRSIM"])
    r_ief = returns_from_prices(df["IEFSIM"])
    r_cash = returns_from_prices(df["CASHX"])
    r_gld = returns_from_prices(df["GLDSIM"])
    r_gde = returns_from_prices(df["GDESIM"])
    r_kmlm = returns_from_prices(df["KMLMSIM"])
    r_rssb = returns_from_prices(df["RSSBSIM"])

    # Synthesized return-stacked sleeves
    r_ntsx = synth_stacked(r_spy, r_ief, r_cash)
    r_ntsi = synth_stacked(r_vea, r_ief, r_cash)
    r_ntse = synth_stacked(r_vwo, r_ief, r_cash)
    # RSST = 100% SPY + 100% MF - 100% CASH (financing)
    r_rsst = synth_stacked(r_spy, r_kmlm, r_cash, eq_w=1.0, bond_w=1.0, cash_w=-1.0)

    return {
        "SPY": r_spy, "VEA": r_vea, "VWO": r_vwo, "VBR": r_vbr,
        "IEF": r_ief, "CASH": r_cash, "GLD": r_gld,
        "GDE": r_gde, "KMLM": r_kmlm, "RSSB": r_rssb,
        "NTSX": r_ntsx, "NTSI": r_ntsi, "NTSE": r_ntse, "RSST": r_rsst,
        "AVDV_proxy": 0.5 * r_vea + 0.5 * r_vbr,
    }


def assemble(rmap, weights):
    """Assemble portfolio from dict of returns + dict of weights (sums to 1.0)."""
    assert abs(sum(weights.values()) - 1.0) < 1e-6, f"weights sum={sum(weights.values())}"
    common = None
    for k in weights:
        if k not in rmap:
            raise KeyError(f"missing return for {k}")
        common = rmap[k].index if common is None else common.intersection(rmap[k].index)
    aligned = {k: rmap[k].reindex(common).fillna(0.0) for k in weights}
    return sum(weights[k] * aligned[k] for k in weights).dropna()


def main():
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    required = ["SPYSIM", "VEASIM", "VWOSIM", "VBRSIM", "IEFSIM", "CASHX",
                "GLDSIM", "GDESIM", "KMLMSIM", "RSSBSIM"]
    df_aligned = df[required].dropna()
    print(f"Aligned window: {df_aligned.index.min().date()} → "
          f"{df_aligned.index.max().date()} ({len(df_aligned)/TRADING_DAYS:.1f}y, "
          f"bounded by VWOSIM 1994+)")

    rmap = build_returns(df_aligned)

    # Define variants. All must sum to 1.00 in weights (100% capital).
    # Note: GDE is an existing real ETF; NTSX/NTSI/NTSE/RSST/AVDV_proxy synthesized.
    portfolios = {
        # Reference baselines
        "V1_NTSX_GDE_67_33": {"NTSX": 0.67, "GDE": 0.33},
        "V3_1_PlanoC_v3.5": {
            "GDE": 0.25, "SPY": 0.12, "VEA": 0.20, "VWO": 0.13,
            "VBR": 0.10, "AVDV_proxy": 0.05, "SPY": 0.07,  # SPY appears twice for SPMO; will collapse
            "IDMO_via_VEA": 0.03, "GLD": 0.05,
        },
        # The above has duplicate SPY key; need different approach
    }
    # Rebuild V3_1 properly (Avantis Mom proxies with separate keys)
    # Use synthetic trick: assemble component-wise with separate dict
    # Instead let's add explicit aliasing
    rmap["SPMO_proxy"] = rmap["SPY"]
    rmap["IDMO_proxy"] = rmap["VEA"]
    rmap["BTGD_proxy"] = rmap["GLD"]
    rmap["AVUS_proxy"] = rmap["SPY"]
    rmap["AVDE_proxy"] = rmap["VEA"]
    rmap["AVEM_proxy"] = rmap["VWO"]
    rmap["AVUV_proxy"] = rmap["VBR"]

    portfolios = {
        "V1_NTSX_GDE_67_33": {"NTSX": 0.67, "GDE": 0.33},
        "V3_1_PlanoC_v3.5": {
            "GDE": 0.25, "AVUS_proxy": 0.12, "AVDE_proxy": 0.20, "AVEM_proxy": 0.13,
            "AVUV_proxy": 0.10, "AVDV_proxy": 0.05, "SPMO_proxy": 0.07,
            "IDMO_proxy": 0.03, "BTGD_proxy": 0.05,
        },
        "V_HYBRID_baseline": {
            "GDE": 0.25, "NTSX": 0.12, "AVDE_proxy": 0.20, "AVEM_proxy": 0.13,
            "AVUV_proxy": 0.10, "AVDV_proxy": 0.05, "SPMO_proxy": 0.07,
            "IDMO_proxy": 0.03, "BTGD_proxy": 0.05,
        },
        # +10% KMLM, reduce others proportionally by 0.90
        "V_HYBRID_PLUS_MF": {
            "GDE": 0.225, "NTSX": 0.108, "AVDE_proxy": 0.18, "AVEM_proxy": 0.117,
            "AVUV_proxy": 0.09, "AVDV_proxy": 0.045, "SPMO_proxy": 0.063,
            "IDMO_proxy": 0.027, "BTGD_proxy": 0.045, "KMLM": 0.10,
        },
        # Full return-stacking for intl + EM (testing despite Plano C V3.5 rejection)
        "V_HYBRID_GLOBAL_STACK": {
            "GDE": 0.25, "NTSX": 0.12, "NTSI": 0.10, "NTSE": 0.05,
            "AVDE_proxy": 0.10, "AVEM_proxy": 0.08, "AVUV_proxy": 0.10,
            "AVDV_proxy": 0.05, "SPMO_proxy": 0.05, "IDMO_proxy": 0.05,
            "BTGD_proxy": 0.05,
        },
        # NTSX replaced by RSST (S&P + MF stacked)
        "V_HYBRID_RSST_substitute": {
            "GDE": 0.25, "RSST": 0.12, "AVDE_proxy": 0.20, "AVEM_proxy": 0.13,
            "AVUV_proxy": 0.10, "AVDV_proxy": 0.05, "SPMO_proxy": 0.07,
            "IDMO_proxy": 0.03, "BTGD_proxy": 0.05,
        },
        # Combine: MF + Global Stack + RSST (kitchen sink — most aggressive)
        "V_HYBRID_KITCHEN_SINK": {
            "GDE": 0.20, "NTSX": 0.10, "NTSI": 0.08, "NTSE": 0.04,
            "RSST": 0.05,
            "AVDE_proxy": 0.10, "AVEM_proxy": 0.10, "AVUV_proxy": 0.10,
            "AVDV_proxy": 0.05, "SPMO_proxy": 0.05, "IDMO_proxy": 0.03,
            "BTGD_proxy": 0.04, "KMLM": 0.06,
        },
        # 50/50 V1 + V_HYBRID — averaging the two paradigms
        "V_HYBRID_50_50_with_V1": {
            "NTSX": 0.335 + 0.06, "GDE": 0.165 + 0.125, "AVDE_proxy": 0.10,
            "AVEM_proxy": 0.065, "AVUV_proxy": 0.05, "AVDV_proxy": 0.025,
            "SPMO_proxy": 0.035, "IDMO_proxy": 0.015, "BTGD_proxy": 0.025,
        },
    }

    # Verify weights sum
    for name, w in portfolios.items():
        s = sum(w.values())
        if abs(s - 1.0) > 1e-6:
            print(f"WARNING {name} weights sum {s:.6f}, normalizing")
            portfolios[name] = {k: v / s for k, v in w.items()}

    # Compute returns for each
    series = {}
    for name, w in portfolios.items():
        try:
            series[name] = assemble(rmap, w).rename(name)
        except Exception as e:
            print(f"  {name}: FAILED ({e})")

    # Common index
    common = None
    for r in series.values():
        common = r.index if common is None else common.intersection(r.index)
    series = {k: v.loc[common] for k, v in series.items()}
    print(f"\nFinal common window: {common.min().date()} → {common.max().date()} "
          f"({len(common)/TRADING_DAYS:.1f}y)")

    # Benchmark
    r_spy = rmap["SPY"].reindex(common).dropna()
    bench = metrics(r_spy, "SPYSIM b&h")

    # Full window metrics
    print(f"\n=== Full window {len(common)/TRADING_DAYS:.1f}y ===")
    print(f"  bench {bench['name']}: Sharpe {bench['sharpe']:.3f} | "
          f"CAGR {bench['cagr']*100:.2f}% | MDD {bench['mdd']*100:.2f}%")
    metrics_full = {bench['name']: bench}
    rows_sorted = []
    for name, r in series.items():
        m = metrics(r, name)
        metrics_full[name] = m
        rows_sorted.append((name, m))
    rows_sorted.sort(key=lambda x: x[1]['sharpe'], reverse=True)
    for name, m in rows_sorted:
        marker = "🏆" if m == rows_sorted[0][1] else "  "
        print(f"  {marker} {name}: Sharpe {m['sharpe']:.3f} | "
              f"CAGR {m['cagr']*100:.2f}% | MDD {m['mdd']*100:.2f}%")

    # Rolling 10y/20y
    print(f"\n=== Rolling 10y ===")
    print(f"  {'name':<35} {'mean_CAGR':>10} {'min_CAGR':>10} {'5pct':>8} "
          f"{'P(<5%)':>8} {'meanShar':>9} {'meanMDD':>9}")
    rolling_data = {"10y": {}, "20y": {}}
    for win in [10, 20]:
        rolling_data[f"{win}y"] = {}
        for name, r in series.items():
            rw = rolling_window_metrics(r, win)
            d = {
                "n": len(rw),
                "cagr_mean": float(rw["cagr"].mean()),
                "cagr_min": float(rw["cagr"].min()),
                "cagr_5pct": float(rw["cagr"].quantile(0.05)),
                "p_below_5": float((rw["cagr"] < 0.05).mean()),
                "sharpe_mean": float(rw["sharpe"].mean()),
                "mdd_mean": float(rw["mdd"].mean()),
            }
            rolling_data[f"{win}y"][name] = d
            if win == 10:
                print(f"  {name:<35} {d['cagr_mean']*100:>9.2f}% "
                      f"{d['cagr_min']*100:>9.2f}% {d['cagr_5pct']*100:>7.2f}% "
                      f"{d['p_below_5']*100:>7.1f}% {d['sharpe_mean']:>9.2f} "
                      f"{d['mdd_mean']*100:>8.1f}%")

    print(f"\n=== Rolling 20y ===")
    print(f"  {'name':<35} {'mean_CAGR':>10} {'min_CAGR':>10} {'5pct':>8} "
          f"{'meanShar':>9} {'meanMDD':>9}")
    for name, d in rolling_data["20y"].items():
        print(f"  {name:<35} {d['cagr_mean']*100:>9.2f}% "
              f"{d['cagr_min']*100:>9.2f}% {d['cagr_5pct']*100:>7.2f}% "
              f"{d['sharpe_mean']:>9.2f} {d['mdd_mean']*100:>8.1f}%")

    # Stress tests
    stress_periods = {
        "2000-2013_lost_decade": ("2000-01-01", "2012-12-31"),
        "2008_GFC": ("2007-10-01", "2009-03-31"),
        "2020_COVID": ("2020-02-15", "2020-04-30"),
        "2022_rate_cycle": ("2022-01-01", "2022-12-31"),
    }
    stress_results = {}
    print(f"\n=== Stress tests ===")
    for period_name, (s, e) in stress_periods.items():
        print(f"\n  {period_name}:")
        stress_results[period_name] = {}
        rows_stress = []
        for name, r in series.items():
            sr = stress_window(r, s, e)
            stress_results[period_name][name] = sr
            if sr["n_bars"] > 0:
                rows_stress.append((name, sr))
        rows_stress.sort(key=lambda x: x[1]["return"], reverse=True)
        for name, sr in rows_stress:
            print(f"     {name}: ret {sr['return']*100:+7.2f}% | MDD {sr['mdd']*100:+7.2f}%")

    # Save
    out = {
        "window": {"start": str(common.min().date()), "end": str(common.max().date()),
                   "years": len(common) / TRADING_DAYS},
        "designs": {k: dict(v) for k, v in portfolios.items()},
        "metrics_full": metrics_full,
        "rolling": rolling_data,
        "stress_tests": stress_results,
    }
    out_json = OUT_DIR / "PORTFOLIO_VARIANTS_VALIDATION.json"
    out_json.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_json}")
    pd.DataFrame(series).to_parquet(OUT_DIR / "portfolio_variants_returns.parquet")


if __name__ == "__main__":
    main()
