"""4-way portfolio comparison: V1 vs V3_1 v3.5 vs V_HYBRID vs V_HYBRID_SIMPLE.

User's question (2026-04-26): "Combine V3_1 + NTSX+GDE optimally. Also
evaluate using AVNM (or AVNM+AVNV) as simplifier of multiple Avantis ETFs."

Designs
-------

V1 NTSX+GDE 67/33 (2 ETFs):
    67% NTSX_synth (90% SPY + 60% IEF - 50% CASH)
    33% GDE
    → US-only, capital efficiency, no factor tilts, no global

V3_1 v3.5 (11 ETFs):
    25% GDE | 12% AVUS | 20% AVDE | 13% AVEM | 10% AVUV | 5% AVDV
    7% SPMO | 3% IDMO | 5% BTGD
    → Plano C accumulation 30-45, factor + global + 1.25× via stacking

V_HYBRID (11 ETFs, minimal change from V3_1):
    Same as V3_1 except 12% AVUS → 12% NTSX_synth
    → Adds USD bond exposure (7.2%) + capital efficiency on US sleeve
    → Keeps DM/EM/SCV/Mom/GDE/BTGD intact
    → Trade-off: violates "bonds em BRL only" partially

V_HYBRID_SIMPLE (9 ETFs, consolidation of intl via AVNM proxy):
    25% GDE | 12% NTSX | 33% AVNM (proxy=VXUS, replaces AVDE+AVEM)
    10% AVUV | 5% AVDV | 7% SPMO | 3% IDMO | 5% BTGD
    → 9 holdings vs 11; one less ETF
    → CAVEAT: AVNM cap-weighted ≈ 85% DM + 15% EM
    → V3_1 was 60/40 DM/EM (heavy EM tilt) — AVNM loses this

Window
------
1994-05-04 → 2026-04-17 (~32y, bounded by VWOSIM EM proxy)
Same window as v1_vs_planoc_validator.

Citations
---------
* Same as v1_vs_planoc_validator.py.
* AVNM (Avantis All International Equity Markets ETF) — inception 2022-07,
  AUM ~$200M (Apr 2025); not in testfolio synth, proxied via VXUSSIM.
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


def synth_ntsx(r_spy, r_ief, r_cash):
    """NTSX = 0.90 SPY + 0.60 IEF - 0.50 CASH (testfolio-validated)."""
    common = r_spy.index.intersection(r_ief.index).intersection(r_cash.index)
    return 0.90 * r_spy.loc[common] + 0.60 * r_ief.loc[common] - 0.50 * r_cash.loc[common]


def metrics(r: pd.Series, name: str = "") -> dict:
    eq = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS
    sd = r.std(ddof=1)
    sharpe = float(np.sqrt(TRADING_DAYS) * r.mean() / sd) if sd > 0 else float("nan")
    cagr = float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    mdd = float((1 - eq / eq.cummax()).max())
    return {"name": name, "n_bars": len(r), "sharpe": sharpe, "cagr": cagr, "mdd": mdd,
            "start": str(r.index[0].date()), "end": str(r.index[-1].date()),
            "years": years}


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


def strat_v1(df):
    """V1: 67% NTSX_synth + 33% GDE."""
    r_spy = returns_from_prices(df["SPYSIM"])
    r_ief = returns_from_prices(df["IEFSIM"])
    r_cash = returns_from_prices(df["CASHX"])
    r_gde = returns_from_prices(df["GDESIM"])
    r_ntsx = synth_ntsx(r_spy, r_ief, r_cash)
    common = r_ntsx.index.intersection(r_gde.index)
    return (0.67 * r_ntsx.loc[common] + 0.33 * r_gde.loc[common]).rename("V1_NTSX_GDE")


def strat_v3_1(df):
    """V3_1 v3.5 with proxies (matches v1_vs_planoc_validator)."""
    r_gde = returns_from_prices(df["GDESIM"])
    r_spy = returns_from_prices(df["SPYSIM"])      # AVUS proxy
    r_vea = returns_from_prices(df["VEASIM"])      # AVDE proxy
    r_vwo = returns_from_prices(df["VWOSIM"])      # AVEM proxy
    r_vbr = returns_from_prices(df["VBRSIM"])      # AVUV proxy
    r_avdv = 0.5 * r_vea + 0.5 * r_vbr              # AVDV proxy
    r_btgd = returns_from_prices(df["GLDSIM"])     # BTGD proxy

    weights = {"GDE": 0.25, "AVUS": 0.12, "AVDE": 0.20, "AVEM": 0.13,
               "AVUV": 0.10, "AVDV": 0.05, "SPMO": 0.07, "IDMO": 0.03, "BTGD": 0.05}
    rmap = {"GDE": r_gde, "AVUS": r_spy, "AVDE": r_vea, "AVEM": r_vwo,
            "AVUV": r_vbr, "AVDV": r_avdv, "SPMO": r_spy, "IDMO": r_vea, "BTGD": r_btgd}
    common = None
    for r in rmap.values():
        common = r.index if common is None else common.intersection(r.index)
    aligned = {k: r.reindex(common).fillna(0.0) for k, r in rmap.items()}
    return sum(weights[k] * aligned[k] for k in weights).dropna().rename("V3_1_PlanoC")


def strat_v_hybrid(df):
    """V_HYBRID: V3_1 with 12% AVUS replaced by 12% NTSX_synth."""
    r_gde = returns_from_prices(df["GDESIM"])
    r_spy = returns_from_prices(df["SPYSIM"])
    r_ief = returns_from_prices(df["IEFSIM"])
    r_cash = returns_from_prices(df["CASHX"])
    r_vea = returns_from_prices(df["VEASIM"])
    r_vwo = returns_from_prices(df["VWOSIM"])
    r_vbr = returns_from_prices(df["VBRSIM"])
    r_avdv = 0.5 * r_vea + 0.5 * r_vbr
    r_btgd = returns_from_prices(df["GLDSIM"])
    r_ntsx = synth_ntsx(r_spy, r_ief, r_cash)

    weights = {"GDE": 0.25, "NTSX": 0.12, "AVDE": 0.20, "AVEM": 0.13,
               "AVUV": 0.10, "AVDV": 0.05, "SPMO": 0.07, "IDMO": 0.03, "BTGD": 0.05}
    rmap = {"GDE": r_gde, "NTSX": r_ntsx, "AVDE": r_vea, "AVEM": r_vwo,
            "AVUV": r_vbr, "AVDV": r_avdv, "SPMO": r_spy, "IDMO": r_vea, "BTGD": r_btgd}
    common = None
    for r in rmap.values():
        common = r.index if common is None else common.intersection(r.index)
    aligned = {k: r.reindex(common).fillna(0.0) for k, r in rmap.items()}
    return sum(weights[k] * aligned[k] for k in weights).dropna().rename("V_HYBRID")


def strat_v_hybrid_simple(df):
    """V_HYBRID_SIMPLE: V_HYBRID with AVDE+AVEM consolidated as 33% AVNM (=VXUS proxy)."""
    r_gde = returns_from_prices(df["GDESIM"])
    r_spy = returns_from_prices(df["SPYSIM"])
    r_ief = returns_from_prices(df["IEFSIM"])
    r_cash = returns_from_prices(df["CASHX"])
    r_vxus = returns_from_prices(df["VXUSSIM"])  # AVNM proxy: total intl ex-US
    r_vea = returns_from_prices(df["VEASIM"])    # for IDMO proxy
    r_vbr = returns_from_prices(df["VBRSIM"])
    r_avdv = 0.5 * r_vea + 0.5 * r_vbr
    r_btgd = returns_from_prices(df["GLDSIM"])
    r_ntsx = synth_ntsx(r_spy, r_ief, r_cash)

    weights = {"GDE": 0.25, "NTSX": 0.12, "AVNM": 0.33,
               "AVUV": 0.10, "AVDV": 0.05, "SPMO": 0.07, "IDMO": 0.03, "BTGD": 0.05}
    rmap = {"GDE": r_gde, "NTSX": r_ntsx, "AVNM": r_vxus,
            "AVUV": r_vbr, "AVDV": r_avdv, "SPMO": r_spy, "IDMO": r_vea, "BTGD": r_btgd}
    common = None
    for r in rmap.values():
        common = r.index if common is None else common.intersection(r.index)
    aligned = {k: r.reindex(common).fillna(0.0) for k, r in rmap.items()}
    return sum(weights[k] * aligned[k] for k in weights).dropna().rename("V_HYBRID_SIMPLE")


STRATEGIES = {
    "V1_NTSX_GDE_67_33": strat_v1,
    "V3_1_PlanoC_v3.5": strat_v3_1,
    "V_HYBRID_NTSX_replaces_AVUS": strat_v_hybrid,
    "V_HYBRID_SIMPLE_AVNM_proxy": strat_v_hybrid_simple,
}


def main() -> None:
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)

    required = ["SPYSIM", "IEFSIM", "GDESIM", "VEASIM", "VWOSIM",
                "VBRSIM", "GLDSIM", "CASHX", "VXUSSIM"]
    df_aligned = df[required].dropna()
    print(f"Aligned window: {df_aligned.index.min().date()} → "
          f"{df_aligned.index.max().date()} ({len(df_aligned)} bars)")

    # Compute strategies
    series = {}
    for name, fn in STRATEGIES.items():
        series[name] = fn(df_aligned).dropna()

    # Common index
    common = None
    for r in series.values():
        common = r.index if common is None else common.intersection(r.index)
    series = {k: v.loc[common] for k, v in series.items()}
    print(f"Common 4-way window: {common.min().date()} → {common.max().date()} "
          f"({len(common)/TRADING_DAYS:.1f}y)")

    # Benchmark
    r_spy = returns_from_prices(df_aligned["SPYSIM"]).reindex(common).dropna()
    bench = metrics(r_spy, "SPYSIM b&h")

    # Full window metrics
    print(f"\n=== Full window {len(common)/TRADING_DAYS:.1f}y ===")
    print(f"  bench {bench['name']}: Sharpe {bench['sharpe']:.3f} | "
          f"CAGR {bench['cagr']*100:.2f}% | MDD {bench['mdd']*100:.2f}%")
    metrics_full = {bench['name']: bench}
    for name, r in series.items():
        m = metrics(r, name)
        metrics_full[name] = m
        print(f"  {name}: Sharpe {m['sharpe']:.3f} | CAGR {m['cagr']*100:.2f}% | "
              f"MDD {m['mdd']*100:.2f}%")

    # Rolling 10y/20y
    print(f"\n=== Rolling windows ===")
    rolling_data = {}
    for win_years in [10, 20]:
        rolling_data[f"{win_years}y"] = {}
        print(f"\nRolling {win_years}y:")
        ref_n = None
        for name, r in series.items():
            rw = rolling_window_metrics(r, win_years)
            rolling_data[f"{win_years}y"][name] = {
                "n_windows": len(rw),
                "cagr_mean": float(rw["cagr"].mean()),
                "cagr_5pct": float(rw["cagr"].quantile(0.05)),
                "cagr_95pct": float(rw["cagr"].quantile(0.95)),
                "cagr_min": float(rw["cagr"].min()),
                "cagr_max": float(rw["cagr"].max()),
                "sharpe_mean": float(rw["sharpe"].mean()),
                "mdd_mean": float(rw["mdd"].mean()),
                "p_below_5pct": float((rw["cagr"] < 0.05).mean()),
            }
            if ref_n is None:
                ref_n = len(rw)
            d = rolling_data[f"{win_years}y"][name]
            print(f"  {name}: mean CAGR {d['cagr_mean']*100:>6.2f}% / "
                  f"min {d['cagr_min']*100:>6.2f}% / "
                  f"5pct {d['cagr_5pct']*100:>6.2f}% / "
                  f"P(<5%) {d['p_below_5pct']*100:>5.1f}% / "
                  f"mean Sharpe {d['sharpe_mean']:.2f} / "
                  f"mean MDD {d['mdd_mean']*100:.1f}%")

    # Stress tests
    stress_periods = {
        "2000-2013_lost_decade": ("2000-01-01", "2012-12-31"),
        "2008_GFC": ("2007-10-01", "2009-03-31"),
        "2008_full_year": ("2008-01-01", "2008-12-31"),
        "2020_COVID": ("2020-02-15", "2020-04-30"),
        "2022_rate_cycle": ("2022-01-01", "2022-12-31"),
    }
    stress_results = {}
    print(f"\n=== Stress tests ===")
    for period_name, (s, e) in stress_periods.items():
        print(f"\n  {period_name} ({s} → {e}):")
        stress_results[period_name] = {}
        for name, r in series.items():
            sr = stress_window(r, s, e)
            stress_results[period_name][name] = sr
            if sr["n_bars"] > 0:
                print(f"     {name}: ret {sr['return']*100:+7.2f}% | MDD {sr['mdd']*100:+7.2f}%")

    # Save
    out = {
        "window": {"start": str(common.min().date()), "end": str(common.max().date()),
                   "years": len(common) / TRADING_DAYS, "bars": len(common)},
        "designs": {
            "V1_NTSX_GDE_67_33": "67% NTSX_synth + 33% GDE; 2 ETFs; US-only",
            "V3_1_PlanoC_v3.5": "11 ETFs; factor + global + 1.25× via stacking",
            "V_HYBRID_NTSX_replaces_AVUS": "V3_1 with 12% AVUS → 12% NTSX_synth; 11 ETFs",
            "V_HYBRID_SIMPLE_AVNM_proxy": "V_HYBRID with AVDE+AVEM → 33% AVNM (VXUS proxy); 9 ETFs",
        },
        "metrics_full": metrics_full,
        "rolling": rolling_data,
        "stress_tests": stress_results,
    }
    out_json = OUT_DIR / "PORTFOLIO_4WAY_VALIDATION.json"
    out_json.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_json}")

    # Save returns
    pd.DataFrame(series).to_parquet(OUT_DIR / "portfolio_4way_returns.parquet")


if __name__ == "__main__":
    main()
