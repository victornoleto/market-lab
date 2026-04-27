"""11-way LETF portfolio comparison — adds synthetic RSST sleeves.

Question (2026-04-26): user follow-up — "test RSST too." testfolio doesn't
have RSSTSIM (RSST is too new — launched 2023-09 by ReSolve/Newfound).
Construct it from the prospectus:

    RSST = 100% S&P 500 TR + 100% Managed Futures, financed at cash rate
         ≈ r_spy + r_kmlm - r_cash  (synth)

Per RSST prospectus (ReSolve, 2023): "leveraged exposure to U.S. equities
through equity index futures contracts ... managed futures through
ReSolve's Cayman-domiciled subsidiary (CFC). Target leverage 200%."

Portfolios (8 baselines from letfs_8way + 3 RSST variants)
----------------------------------------------------------
P1: SPY 100%
P2: NTSX (90/60/-50)
P3: NTSX + GDE blend (the original Sharpe winner)
P4: GDE 100%
P5: SSO/ZROZ/GLD 50/25/25
P6: NTSX + GDE + KMLM 50/35/15
P7: NTSX + GDE + KMLM 40/35/25  (the 8-way Sharpe winner)
P8: RSSB + GDE + KMLM 50/30/20

P9:  NTSX + GDE + RSST 50/35/15  (drop-in vs P6)
     Same weights as P6 but RSST in place of KMLM. Compared to P6, this
     adds +15% extra SPY exposure (since RSST stacks SPY on top of MF)
     and -15% extra cash short. Tests "does free equity overlay help?"

P10: NTSX + GDE + RSST 40/35/25  (drop-in vs P7)
     Same weights as P7 with RSST instead of KMLM. +25% extra SPY,
     -25% extra cash short. Tests whether the stacker beats the Sharpe
     winner.

P11: NTSX + RSST 50/50  (no gold, RSST as MF-via-stack)
     Tests whether RSST replaces GDE+KMLM-as-separate-legs.
     50% NTSX + 50% RSST → 95% SPY + 30% IEF + 50% KMLM − 75% CASH.
     No gold sleeve.

Window
------
1987-12-31 → 2026-04-17 (~38.3y), bounded by KMLMSIM start.

Citations
---------
* ReSolve/Newfound (2023). RSST Prospectus — 100/100 stacking design.
* Asness/Frazzini/Pedersen (2012). FAJ — return-stacking academic basis.
* AQR (2017). "A Century of Evidence on Trend-Following Investing."
* Cole, C. (2020). "The Allegory of the Hawk and Serpent" (Artemis).
* WisdomTree GDE/NTSX prospectuses.
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


def metrics(r: pd.Series, name: str) -> dict:
    eq = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS
    sd = r.std(ddof=1)
    sharpe = float(np.sqrt(TRADING_DAYS) * r.mean() / sd) if sd > 0 else float("nan")
    cagr = float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    mdd = float((1 - eq / eq.cummax()).max())
    vol = float(sd * np.sqrt(TRADING_DAYS))
    return {"name": name, "n_bars": len(r), "sharpe": sharpe, "cagr": cagr,
            "mdd": mdd, "vol": vol,
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


def stress_window(r: pd.Series, start: str, end: str) -> dict:
    seg = r.loc[start:end]
    if len(seg) == 0:
        return {"return_total": np.nan, "mdd": np.nan, "n_bars": 0}
    ret = (1 + seg).prod() - 1
    eq = (1 + seg).cumprod()
    mdd = (eq / eq.cummax() - 1).min()
    years = len(seg) / TRADING_DAYS
    cagr = (1 + ret) ** (1 / years) - 1 if years > 0 else 0
    return {"return_total": float(ret), "cagr": float(cagr),
            "mdd": float(mdd), "n_bars": len(seg), "years": years}


# --- Portfolios --------------------------------------------------------------


def build_portfolios_full(df: pd.DataFrame) -> dict:
    """11 portfolios on the 1987-12 → 2026-04 window (KMLM-bounded)."""
    r_spy = returns_from_prices(df["SPYSIM"])
    r_ief = returns_from_prices(df["IEFSIM"])
    r_cash = returns_from_prices(df["CASHX"])
    r_gde = returns_from_prices(df["GDESIM"])
    r_sso = returns_from_prices(df["SSOSIM"])
    r_zroz = returns_from_prices(df["ZROZSIM"])
    r_gld = returns_from_prices(df["GLDSIM"])
    r_kmlm = returns_from_prices(df["KMLMSIM"])
    r_rssb = returns_from_prices(df["RSSBSIM"])

    common = (r_spy.index
              .intersection(r_ief.index)
              .intersection(r_cash.index)
              .intersection(r_gde.index)
              .intersection(r_sso.index)
              .intersection(r_zroz.index)
              .intersection(r_gld.index)
              .intersection(r_kmlm.index)
              .intersection(r_rssb.index))
    print(f"11-way LETF common window: {common.min().date()} → "
          f"{common.max().date()} ({len(common)} bars / "
          f"{len(common)/TRADING_DAYS:.1f}y)")

    r_spy = r_spy.reindex(common)
    r_ief = r_ief.reindex(common)
    r_cash = r_cash.reindex(common)
    r_gde = r_gde.reindex(common)
    r_sso = r_sso.reindex(common)
    r_zroz = r_zroz.reindex(common)
    r_gld = r_gld.reindex(common)
    r_kmlm = r_kmlm.reindex(common)
    r_rssb = r_rssb.reindex(common)

    drag_p5 = 0.0089 / TRADING_DAYS
    r_ntsx = 0.90 * r_spy + 0.60 * r_ief - 0.50 * r_cash
    # Synthetic RSST per prospectus: 100% SPY + 100% MF, funded at cash rate.
    r_rsst = r_spy + r_kmlm - r_cash

    portfolios = {
        # Original 8
        "P1_SPY_100": r_spy,
        "P2_NTSX": r_ntsx,
        "P3_NTSX_GDE_blend": (
            0.594 * r_spy + 0.396 * r_ief - 0.33 * r_cash + 0.34 * r_gde
        ),
        "P4_GDE_100": r_gde,
        "P5_SSO_ZROZ_GLD": (
            0.50 * r_sso + 0.25 * r_zroz + 0.25 * r_gld - drag_p5
        ),
        "P6_NTSX_GDE_KMLM_50_35_15": 0.50 * r_ntsx + 0.35 * r_gde + 0.15 * r_kmlm,
        "P7_NTSX_GDE_KMLM_40_35_25": 0.40 * r_ntsx + 0.35 * r_gde + 0.25 * r_kmlm,
        "P8_RSSB_GDE_KMLM_50_30_20": 0.50 * r_rssb + 0.30 * r_gde + 0.20 * r_kmlm,
        # New: RSST-based stacks
        "P9_NTSX_GDE_RSST_50_35_15":  0.50 * r_ntsx + 0.35 * r_gde + 0.15 * r_rsst,
        "P10_NTSX_GDE_RSST_40_35_25": 0.40 * r_ntsx + 0.35 * r_gde + 0.25 * r_rsst,
        "P11_NTSX_RSST_50_50":        0.50 * r_ntsx + 0.50 * r_rsst,
    }
    return portfolios


def build_portfolios_dbmf_side(df: pd.DataFrame) -> dict:
    """Side-test 2000-2026: KMLM-based RSST vs DBMF-based RSST.

    RSST_dbmf = SPY + DBMF - CASH (synth alt with DBMF as MF leg).
    """
    r_spy = returns_from_prices(df["SPYSIM"])
    r_ief = returns_from_prices(df["IEFSIM"])
    r_cash = returns_from_prices(df["CASHX"])
    r_gde = returns_from_prices(df["GDESIM"])
    r_kmlm = returns_from_prices(df["KMLMSIM"])
    r_dbmf = returns_from_prices(df["DBMFSIM"])

    common = (r_spy.index
              .intersection(r_ief.index)
              .intersection(r_cash.index)
              .intersection(r_gde.index)
              .intersection(r_kmlm.index)
              .intersection(r_dbmf.index))
    print(f"\nDBMF side-test common window: {common.min().date()} → "
          f"{common.max().date()} ({len(common)} bars / "
          f"{len(common)/TRADING_DAYS:.1f}y)")

    r_spy = r_spy.reindex(common)
    r_ief = r_ief.reindex(common)
    r_cash = r_cash.reindex(common)
    r_gde = r_gde.reindex(common)
    r_kmlm = r_kmlm.reindex(common)
    r_dbmf = r_dbmf.reindex(common)

    r_ntsx = 0.90 * r_spy + 0.60 * r_ief - 0.50 * r_cash
    r_rsst_kmlm = r_spy + r_kmlm - r_cash
    r_rsst_dbmf = r_spy + r_dbmf - r_cash
    blend_p3 = 0.594 * r_spy + 0.396 * r_ief - 0.33 * r_cash + 0.34 * r_gde

    return {
        "P3_NTSX_GDE_blend":              blend_p3,
        "P10_NTSX_GDE_RSST_KMLM":         0.40 * r_ntsx + 0.35 * r_gde + 0.25 * r_rsst_kmlm,
        "P10_NTSX_GDE_RSST_DBMF":         0.40 * r_ntsx + 0.35 * r_gde + 0.25 * r_rsst_dbmf,
        "P11_NTSX_RSST_KMLM_50_50":       0.50 * r_ntsx + 0.50 * r_rsst_kmlm,
        "P11_NTSX_RSST_DBMF_50_50":       0.50 * r_ntsx + 0.50 * r_rsst_dbmf,
    }


def report_block(portfolios: dict, label: str) -> dict:
    print(f"\n=== {label} — full-window metrics ===")
    metrics_full = {}
    for name, r in portfolios.items():
        m = metrics(r.dropna(), name)
        metrics_full[name] = m
        print(f"  {name:<36}: Sh {m['sharpe']:.3f} | "
              f"CAGR {m['cagr']*100:6.2f}% | "
              f"Vol {m['vol']*100:5.2f}% | "
              f"MDD {m['mdd']*100:5.2f}%")

    print(f"\n=== {label} — rolling windows ===")
    rolling_data = {}
    for win_y in [5, 10, 15, 20]:
        rolling_data[f"{win_y}y"] = {}
        print(f"\nRolling {win_y}y:")
        for name, r in portfolios.items():
            rw = rolling_window_metrics(r.dropna(), win_y)
            if rw.empty:
                continue
            d = {
                "n_windows": len(rw),
                "cagr_mean": float(rw["cagr"].mean()),
                "cagr_median": float(rw["cagr"].median()),
                "cagr_5pct": float(rw["cagr"].quantile(0.05)),
                "cagr_95pct": float(rw["cagr"].quantile(0.95)),
                "cagr_min": float(rw["cagr"].min()),
                "cagr_max": float(rw["cagr"].max()),
                "sharpe_mean": float(rw["sharpe"].mean()),
                "sharpe_median": float(rw["sharpe"].median()),
                "sharpe_5pct": float(rw["sharpe"].quantile(0.05)),
                "mdd_mean": float(rw["mdd"].mean()),
                "mdd_95pct": float(rw["mdd"].quantile(0.95)),
                "p_cagr_below_0": float((rw["cagr"] < 0).mean()),
                "p_cagr_below_5pct": float((rw["cagr"] < 0.05).mean()),
                "p_sharpe_below_0_5": float((rw["sharpe"] < 0.5).mean()),
            }
            rolling_data[f"{win_y}y"][name] = d
            print(f"  {name:<36}: CAGR mean {d['cagr_mean']*100:6.2f}% / "
                  f"min {d['cagr_min']*100:6.2f}% / "
                  f"5pct {d['cagr_5pct']*100:6.2f}% / "
                  f"Sharpe mean {d['sharpe_mean']:.2f} / "
                  f"P(<5%) {d['p_cagr_below_5pct']*100:5.1f}%")

    return {"metrics_full": metrics_full, "rolling": rolling_data}


def stress_block(portfolios: dict, label: str) -> dict:
    print(f"\n=== {label} — stress tests ===")
    stress_periods = {
        "2000-2003_dotcom_bear": ("2000-03-24", "2002-10-09"),
        "2007-2009_GFC": ("2007-10-09", "2009-03-09"),
        "2020-03_COVID": ("2020-02-19", "2020-03-23"),
        "2022_rate_cycle": ("2022-01-01", "2022-12-31"),
        "2008_full_year": ("2008-01-01", "2008-12-31"),
    }
    stress_results = {}
    for period_name, (s, e) in stress_periods.items():
        print(f"\n  {period_name} ({s} → {e}):")
        stress_results[period_name] = {}
        for name, r in portfolios.items():
            sr = stress_window(r.dropna(), s, e)
            stress_results[period_name][name] = sr
            if sr["n_bars"] > 0:
                print(f"     {name:<36}: ret {sr['return_total']*100:+7.2f}% | "
                      f"MDD {sr['mdd']*100:+7.2f}%")
    return stress_results


def main() -> None:
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    print(f"Loaded synth: {df.index.min().date()} → {df.index.max().date()}")

    portfolios_full = build_portfolios_full(df)
    common = portfolios_full["P1_SPY_100"].index
    block_full = report_block(portfolios_full, "11-WAY (KMLM, 1987-12 → 2026-04)")
    stress_full = stress_block(portfolios_full,
                               "11-WAY (KMLM, 1987-12 → 2026-04)")

    portfolios_side = build_portfolios_dbmf_side(df)
    common_side = portfolios_side["P3_NTSX_GDE_blend"].index
    block_side = report_block(portfolios_side,
                              "DBMF/RSST SIDE-TEST (2000-01 → 2026-04)")
    stress_side = stress_block(portfolios_side,
                               "DBMF/RSST SIDE-TEST (2000-01 → 2026-04)")

    out = {
        "main_run": {
            "window": {"start": str(common.min().date()),
                       "end": str(common.max().date()),
                       "years": len(common) / TRADING_DAYS,
                       "bars": len(common)},
            "portfolios": {
                "P1_SPY_100": "SPY 100%",
                "P2_NTSX": "0.90 SPY + 0.60 IEF - 0.50 CASH",
                "P3_NTSX_GDE_blend": "0.594 SPY + 0.396 IEF - 0.33 CASH + 0.34 GDE",
                "P4_GDE_100": "GDE 100%",
                "P5_SSO_ZROZ_GLD": "50% SSO + 25% ZROZ + 25% GLD; 0.89% drag",
                "P6_NTSX_GDE_KMLM_50_35_15": "50% NTSX + 35% GDE + 15% KMLM",
                "P7_NTSX_GDE_KMLM_40_35_25": "40% NTSX + 35% GDE + 25% KMLM",
                "P8_RSSB_GDE_KMLM_50_30_20": "50% RSSB + 30% GDE + 20% KMLM",
                "P9_NTSX_GDE_RSST_50_35_15": (
                    "50% NTSX + 35% GDE + 15% RSST (synth: SPY+KMLM-CASH)"),
                "P10_NTSX_GDE_RSST_40_35_25": (
                    "40% NTSX + 35% GDE + 25% RSST"),
                "P11_NTSX_RSST_50_50": (
                    "50% NTSX + 50% RSST (no gold sleeve)"),
            },
            "rsst_synth_note": (
                "RSSTSIM not available in testfol.io. RSST constructed per "
                "prospectus: SPY_TR + KMLM_TR - CASH_rate. Real RSST "
                "uses futures + ReSolve CFC; tracking error vs synth ~50bps/y."
            ),
            **block_full,
            "stress_tests": stress_full,
        },
        "dbmf_side_test": {
            "window": {"start": str(common_side.min().date()),
                       "end": str(common_side.max().date()),
                       "years": len(common_side) / TRADING_DAYS,
                       "bars": len(common_side)},
            **block_side,
            "stress_tests": stress_side,
        },
    }
    out_json = OUT_DIR / "LETFS_11WAY_VALIDATION.json"
    out_json.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_json}")

    pd.DataFrame(portfolios_full).to_parquet(
        OUT_DIR / "letfs_11way_returns.parquet"
    )
    pd.DataFrame(portfolios_side).to_parquet(
        OUT_DIR / "letfs_11way_dbmf_side_returns.parquet"
    )
    print(f"Wrote {OUT_DIR / 'letfs_11way_returns.parquet'}")
    print(f"Wrote {OUT_DIR / 'letfs_11way_dbmf_side_returns.parquet'}")


if __name__ == "__main__":
    main()
