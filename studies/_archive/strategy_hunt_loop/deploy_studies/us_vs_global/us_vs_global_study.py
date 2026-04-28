"""US vs Global — long-horizon study for 20-30y portfolio decision.

Question from user (2026-04-26): "Will the US be the dominant economic
power in the next 20-30 years? I want to maximize my retirement wealth
based on academic evidence, not opinion."

This study uses the testfolio synth cache (~56 years 1969-2026) to test:

1. Replicate user's testfolio 5-way comparison
   (NTSX vs NTSX+GDE vs SPY vs VT vs GDE)
2. Head-to-head US-only vs Global-cap-weighted over multiple windows
3. Rolling 20y CAGR distributions (where does each win?)
4. "Lost decade" scenarios (2000-2013 specifically)
5. Crash-time correlations (does global hurt or help in stress?)
6. Country dispersion analysis (VEA / VWO / SPY relative)

The empirical answer informs the academic framework, not the other way.

Citations
---------
* Dimson, Marsh, Staunton (2002, ongoing). "Triumph of the Optimists" + UBS
  Global Investment Returns Yearbook. — long-run real returns by country
  1900-2024; dispersion ranges 2-7% real CAGR; survivorship bias warnings.
* Asness, Israelov, Liew (2011). "International Diversification Works
  (Eventually)." Financial Analysts Journal 67(3). — diversification helps
  long-run terminal wealth even when correlations rise in crashes.
* Vanguard Capital Markets Model (2024). — 10y forecasts US 4-6% nominal
  vs intl 7-9% nominal based on valuation mean reversion.
* Shiller, R. (2000, 2015). "Irrational Exuberance." — CAPE methodology.
  Current US CAPE ~38 (2025) vs long-term avg ~17.
* Buffett, W. (Berkshire 2013 letter, recurring). — "90% S&P, 10% bonds"
  for personal estate; tied to "bet on America" thesis but explicit caveat
  that this could end.
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


# --- Data + synth ------------------------------------------------------------


def returns_from_prices(p: pd.Series) -> pd.Series:
    return p.pct_change().dropna()


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


# --- Section 1: Replicate user's testfolio comparison -----------------------


def replicate_testfolio_5way(df: pd.DataFrame) -> dict:
    """5-way comparison from user's testfolio query (annual rebalance).

    Strategies (weights as percentage of capital, can be negative):
      A: NTSX_synth (90 SPY + 60 IEF - 50 CASH)
      B: NTSX+GDE blend (59.4 SPY + 39.6 IEF - 33 CASH + 34 GDE)
      C: SPY 100%
      D: VT 100% (cap-weighted global)
      E: GDE 100%
    """
    r_spy = returns_from_prices(df["SPYSIM"])
    r_ief = returns_from_prices(df["IEFSIM"])
    r_cash = returns_from_prices(df["CASHX"])
    r_vt = returns_from_prices(df["VTSIM"])
    r_gde = returns_from_prices(df["GDESIM"])

    # Common index across all
    idx = (r_spy.index.intersection(r_ief.index)
                  .intersection(r_cash.index)
                  .intersection(r_vt.index)
                  .intersection(r_gde.index))
    print(f"5-way common window: {idx.min().date()} → {idx.max().date()} ({len(idx)} bars)")

    r_spy = r_spy.reindex(idx)
    r_ief = r_ief.reindex(idx)
    r_cash = r_cash.reindex(idx)
    r_vt = r_vt.reindex(idx)
    r_gde = r_gde.reindex(idx)

    strategies = {
        "A_NTSX_synth": 0.90 * r_spy + 0.60 * r_ief - 0.50 * r_cash,
        "B_NTSX_GDE_blend": (0.594 * r_spy + 0.396 * r_ief - 0.33 * r_cash + 0.34 * r_gde),
        "C_SPY_100pct": r_spy,
        "D_VT_100pct_global_cap": r_vt,
        "E_GDE_100pct": r_gde,
    }
    out = {}
    for k, v in strategies.items():
        out[k] = metrics(v.dropna(), k)
    return {"window": {"start": str(idx.min().date()), "end": str(idx.max().date()),
                       "bars": len(idx), "years": len(idx) / TRADING_DAYS},
            "strategies": out, "returns": strategies}


# --- Section 2: Rolling N-year CAGR + Sharpe distributions ------------------


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


def rolling_distributions(returns_dict: dict, window_years: int) -> dict:
    """For each strategy, compute rolling N-y metrics distribution."""
    out = {}
    for name, r in returns_dict.items():
        rw = rolling_window_metrics(r.dropna(), window_years)
        if rw.empty:
            continue
        out[name] = {
            "n_windows": len(rw),
            "cagr_mean": float(rw["cagr"].mean()),
            "cagr_median": float(rw["cagr"].median()),
            "cagr_5pct": float(rw["cagr"].quantile(0.05)),
            "cagr_95pct": float(rw["cagr"].quantile(0.95)),
            "cagr_min": float(rw["cagr"].min()),
            "cagr_max": float(rw["cagr"].max()),
            "sharpe_mean": float(rw["sharpe"].mean()),
            "sharpe_5pct": float(rw["sharpe"].quantile(0.05)),
            "mdd_mean": float(rw["mdd"].mean()),
            "mdd_95pct": float(rw["mdd"].quantile(0.95)),
            "p_cagr_below_5pct": float((rw["cagr"] < 0.05).mean()),
            "p_cagr_below_3pct": float((rw["cagr"] < 0.03).mean()),
        }
    return out


# --- Section 3: Lost decade scenarios ---------------------------------------


def stress_window(r: pd.Series, start: str, end: str) -> dict:
    seg = r.loc[start:end]
    if len(seg) == 0:
        return {"return": np.nan, "cagr": np.nan, "mdd": np.nan, "n_bars": 0}
    ret = (1 + seg).prod() - 1
    eq = (1 + seg).cumprod()
    mdd = (eq / eq.cummax() - 1).min()
    years = len(seg) / TRADING_DAYS
    cagr = (1 + ret) ** (1 / years) - 1 if years > 0 else 0
    return {"return_total": float(ret), "cagr": float(cagr),
            "mdd": float(mdd), "n_bars": len(seg), "years": years}


# --- Section 4: Crash-time correlation analysis -----------------------------


def crash_correlation(r1: pd.Series, r2: pd.Series, label1: str, label2: str) -> dict:
    """Compute correlation in crash regimes vs normal."""
    common = r1.index.intersection(r2.index)
    r1, r2 = r1.loc[common], r2.loc[common]
    # 60d rolling MDD for each, then identify "crash" regime
    eq1 = (1 + r1).cumprod()
    dd1 = (eq1 / eq1.cummax() - 1)
    crash_mask = dd1 < -0.15  # in drawdown > 15% from peak
    if crash_mask.sum() < 50:
        return {"crash_corr": np.nan, "normal_corr": np.nan, "n_crash_days": int(crash_mask.sum())}
    crash_corr = r1[crash_mask].corr(r2[crash_mask])
    normal_corr = r1[~crash_mask].corr(r2[~crash_mask])
    return {"crash_corr": float(crash_corr), "normal_corr": float(normal_corr),
            "n_crash_days": int(crash_mask.sum()), "n_normal_days": int((~crash_mask).sum()),
            "label_pair": f"{label1} vs {label2}"}


# --- Main --------------------------------------------------------------------


def main() -> None:
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    print(f"Loaded synth: {df.index.min().date()} → {df.index.max().date()}")

    # === SECTION 1: Replicate user's 5-way ===
    print("\n" + "=" * 70)
    print("SECTION 1: 5-way comparison (replicate user's testfolio query)")
    print("=" * 70)
    res5 = replicate_testfolio_5way(df)
    print(f"\nWindow: {res5['window']['start']} → {res5['window']['end']} "
          f"({res5['window']['years']:.1f}y)")
    for k, m in res5["strategies"].items():
        print(f"  {k}:")
        print(f"     Sharpe {m['sharpe']:.3f} | CAGR {m['cagr']*100:.2f}% | MDD {m['mdd']*100:.2f}%")

    # === SECTION 2: Rolling 20y CAGR distributions (US vs Global) ===
    print("\n" + "=" * 70)
    print("SECTION 2: Rolling 20y and 30y distributions — US vs Global")
    print("=" * 70)

    # Pure components
    r_spy = returns_from_prices(df["SPYSIM"])
    r_vt = returns_from_prices(df["VTSIM"])
    r_vea = returns_from_prices(df["VEASIM"])
    r_vxus = returns_from_prices(df["VXUSSIM"])
    r_vwo = returns_from_prices(df["VWOSIM"])
    r_vbr = returns_from_prices(df["VBRSIM"])

    # Synthetic "US 60/40" and "Global 60/40" for context
    idx_max = r_spy.index.intersection(r_vt.index).intersection(r_vea.index)
    pure = {
        "SPY_US": r_spy.reindex(idx_max),
        "VT_global_cap": r_vt.reindex(idx_max),
        "VEA_DM": r_vea.reindex(idx_max),
        "VXUS_intl": r_vxus.reindex(idx_max),
        "VBR_US_SCV": r_vbr.reindex(idx_max),
    }
    pure = {k: v.dropna() for k, v in pure.items()}

    for window in [20, 30]:
        dist = rolling_distributions(pure, window)
        print(f"\nRolling {window}y CAGR distributions:")
        print(f"  {'strategy':<25} {'mean':>7} {'median':>7} {'5%':>7} {'95%':>7} "
              f"{'min':>7} {'max':>7} {'P(<5%)':>7} {'P(<3%)':>7}")
        for name, d in dist.items():
            print(f"  {name:<25} "
                  f"{d['cagr_mean']*100:>6.2f}% "
                  f"{d['cagr_median']*100:>6.2f}% "
                  f"{d['cagr_5pct']*100:>6.2f}% "
                  f"{d['cagr_95pct']*100:>6.2f}% "
                  f"{d['cagr_min']*100:>6.2f}% "
                  f"{d['cagr_max']*100:>6.2f}% "
                  f"{d['p_cagr_below_5pct']*100:>5.1f}% "
                  f"{d['p_cagr_below_3pct']*100:>5.1f}%")

    # === SECTION 3: Lost decades ===
    print("\n" + "=" * 70)
    print("SECTION 3: Lost decade scenarios")
    print("=" * 70)

    lost_decades = {
        "1969_1979_stagflation": ("1969-12-31", "1979-12-31"),
        "1973_1974_oil": ("1972-12-31", "1974-12-31"),
        "2000_2013_dotcom_to_recovery": ("2000-01-01", "2012-12-31"),
        "2000_2002_dotcom": ("2000-01-01", "2002-12-31"),
        "2007_2009_GFC": ("2007-10-01", "2009-03-31"),
        "post_2009_QE_era": ("2009-04-01", "2021-12-31"),
        "2022_rate_cycle": ("2022-01-01", "2022-12-31"),
    }

    print(f"\n{'period':<35} {'SPY_US':>20} {'VT_global':>20} {'VEA_DM':>20} {'winner':>10}")
    lost_results = {}
    for period_name, (start, end) in lost_decades.items():
        s_spy = stress_window(r_spy.dropna(), start, end)
        s_vt = stress_window(r_vt.dropna(), start, end)
        s_vea = stress_window(r_vea.dropna(), start, end)
        if all(s["n_bars"] > 0 for s in [s_spy, s_vt, s_vea]):
            winner = max([("SPY", s_spy["return_total"]),
                           ("VT", s_vt["return_total"]),
                           ("VEA", s_vea["return_total"])], key=lambda x: x[1])[0]
        else:
            winner = "n/a"
        lost_results[period_name] = {"SPY": s_spy, "VT": s_vt, "VEA": s_vea, "winner": winner}
        spy_str = f"{s_spy['return_total']*100:+.1f}% / CAGR {s_spy['cagr']*100:+.1f}%" if s_spy['n_bars'] > 0 else "N/A"
        vt_str = f"{s_vt['return_total']*100:+.1f}% / CAGR {s_vt['cagr']*100:+.1f}%" if s_vt['n_bars'] > 0 else "N/A"
        vea_str = f"{s_vea['return_total']*100:+.1f}% / CAGR {s_vea['cagr']*100:+.1f}%" if s_vea['n_bars'] > 0 else "N/A"
        print(f"  {period_name:<35} {spy_str:>20} {vt_str:>20} {vea_str:>20} {winner:>10}")

    # === SECTION 4: Crash correlations ===
    print("\n" + "=" * 70)
    print("SECTION 4: Crash-time correlations (does global help when needed?)")
    print("=" * 70)

    cc_spy_vt = crash_correlation(r_spy, r_vt, "SPY", "VT")
    cc_spy_vea = crash_correlation(r_spy, r_vea, "SPY", "VEA")
    cc_spy_vwo = crash_correlation(r_spy, r_vwo, "SPY", "VWO")
    print(f"\n  {'pair':<20} {'normal_corr':>12} {'crash_corr':>12} {'Δ':>10} {'n_crash_days':>15}")
    for cc in [cc_spy_vt, cc_spy_vea, cc_spy_vwo]:
        delta = cc["crash_corr"] - cc["normal_corr"] if not np.isnan(cc["crash_corr"]) else np.nan
        print(f"  {cc['label_pair']:<20} "
              f"{cc['normal_corr']:>11.3f} {cc['crash_corr']:>11.3f} "
              f"{delta:>9.3f} {cc['n_crash_days']:>15}")

    # === SECTION 5: Country dispersion (VEA vs VWO vs SPY rolling) ===
    print("\n" + "=" * 70)
    print("SECTION 5: Regional dispersion 1994-2026 (since VWOSIM)")
    print("=" * 70)

    r_em = r_vwo.dropna()
    r_dm = r_vea.reindex(r_em.index).dropna()
    r_us = r_spy.reindex(r_em.index).dropna()
    common94 = r_em.index.intersection(r_dm.index).intersection(r_us.index)
    regional = {"US_SPY": r_us.loc[common94],
                "DM_VEA": r_dm.loc[common94],
                "EM_VWO": r_em.loc[common94]}
    for window in [10, 20]:
        dist = rolling_distributions(regional, window)
        print(f"\nRolling {window}y CAGR (1994+, n_windows={list(dist.values())[0]['n_windows'] if dist else 0}):")
        for name, d in dist.items():
            print(f"  {name:<10} mean {d['cagr_mean']*100:>6.2f}% / "
                  f"5pct {d['cagr_5pct']*100:>6.2f}% / "
                  f"95pct {d['cagr_95pct']*100:>6.2f}% / "
                  f"min {d['cagr_min']*100:>6.2f}% / max {d['cagr_max']*100:>6.2f}%")

    # === Save all data ===
    out = {
        "section_1_5way": {"window": res5["window"], "strategies": res5["strategies"]},
        "section_2_rolling_distributions": {
            "rolling_20y": rolling_distributions(pure, 20),
            "rolling_30y": rolling_distributions(pure, 30),
        },
        "section_3_lost_decades": lost_results,
        "section_4_crash_correlations": {
            "SPY_vs_VT": cc_spy_vt,
            "SPY_vs_VEA": cc_spy_vea,
            "SPY_vs_VWO": cc_spy_vwo,
        },
        "section_5_regional_94plus": {
            "rolling_10y": rolling_distributions(regional, 10),
            "rolling_20y": rolling_distributions(regional, 20),
        },
    }
    out_json = OUT_DIR / "US_VS_GLOBAL_STUDY.json"
    out_json.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_json}")

    # Save returns for plotting
    series = pd.DataFrame({
        "SPY": r_spy, "VT": r_vt, "VEA": r_vea, "VXUS": r_vxus, "VBR": r_vbr,
        "GDE": returns_from_prices(df["GDESIM"]),
        "NTSX_synth": (0.90 * r_spy + 0.60 * returns_from_prices(df["IEFSIM"])
                       - 0.50 * returns_from_prices(df["CASHX"])),
    })
    series.to_parquet(OUT_DIR / "us_vs_global_returns.parquet")


if __name__ == "__main__":
    main()
