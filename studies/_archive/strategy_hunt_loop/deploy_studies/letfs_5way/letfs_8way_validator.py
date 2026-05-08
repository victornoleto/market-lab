"""8-way LETF portfolio comparison — adds managed-futures + RSSB legs.

Question (2026-04-26): Reddit follow-up to LETFS_5WAY. Two top comments:
  - "Just curious. No managed futures?"
  - "TQQQ is better, so is QLD"
We address (1) here. (TQQQ/QLD are 2x/3x equity-only and would have been
near-wiped through 2000-2002 dot-com — we already explained that in the
post window rationale.)

Portfolios (5 baselines from the previous study + 3 new candidates)
-------------------------------------------------------------------
P1: SPY 100%
P2: NTSX (90/60/-50)
P3: NTSX + GDE blend (the 5-way Sharpe winner)
P4: GDE 100%
P5: SSO/ZROZ/GLD 50/25/25

P6: NTSX + GDE + KMLM 50/35/15  (conservative MF sleeve)
    Tese: 10-20% MF as a *diversifier* sleeve, not core. AQR/Asness style.
    Citation: [asness_devil_finance, ch.6] — managed-futures premia in
    diversified portfolios; literature on trend as ~10-15% sleeve.

P7: NTSX + GDE + KMLM 40/35/25  (aggressive MF / "dragon-lite")
    Tese: closer to Cole/Artemis Dragon weighting (~19% MF). Tests whether
    a chunkier MF sleeve materially shifts Sharpe vs. P6.

P8: RSSB + GDE + KMLM 50/30/20  (full return-stack)
    Tese: swap NTSX (1.5x SPY+IEF) for RSSB (2.0x SPY+US Treasuries).
    More gross exposure, more bond duration. Tests "more stack better".

KMLM is used as the MF leg (full window from 1987-12-31). DBMF (start
2000-01) is run as a separate side-test below to see if the choice of
MF synth matters post-2000.

Window
------
1987-12-31 → 2026-04-17 (~38.3y), bounded by KMLMSIM start.

Side-test
---------
2000-01-03 → 2026-04-17 (~26y), with P6_DBMF and P7_DBMF (replace KMLM
with DBMF). Confirms ordering robustness across MF synth choice.

Methodology notes
-----------------
* Daily-reweighted portfolios. Same convention as letfs_5way_validator.
* Drag only on P5 (already in 5-way). KMLM/DBMF synths in testfol.io
  carry their published expense ratios within the synth construction
  per testfolio docs; no extra drag applied.
* RSSB (2023-launched) synth is testfol.io's `100% S&P TR + 100%
  intermediate Treasuries`. Not modeled: real RSSB futures-roll cost,
  which is small.

Citations
---------
* Asness/Frazzini/Pedersen (2012). "Leverage Aversion and Risk Parity."
  FAJ — academic justification for return-stacking.
* AQR (2017). "A Century of Evidence on Trend-Following Investing."
  — historical robustness of trend / managed futures premia.
* Cole, C. (2020). "The Allegory of the Hawk and Serpent" (Artemis) —
  Dragon Portfolio rationale (~19% MF sleeve; here approximated by P7).
* WisdomTree GDE/NTSX prospectuses — leverage construction.
* Newfound/Resolve (2023). RSSB prospectus — return-stacked S&P + USTs.
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
    """8 portfolios on the 1987-12 → 2026-04 window (KMLM-bounded)."""
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
    print(f"8-way LETF common window: {common.min().date()} → "
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

    portfolios = {
        "P1_SPY_100": r_spy,
        "P2_NTSX": r_ntsx,
        "P3_NTSX_GDE_blend": (
            0.594 * r_spy + 0.396 * r_ief - 0.33 * r_cash + 0.34 * r_gde
        ),
        "P4_GDE_100": r_gde,
        "P5_SSO_ZROZ_GLD": (
            0.50 * r_sso + 0.25 * r_zroz + 0.25 * r_gld - drag_p5
        ),
        # New candidates
        "P6_NTSX_GDE_KMLM_50_35_15": 0.50 * r_ntsx + 0.35 * r_gde + 0.15 * r_kmlm,
        "P7_NTSX_GDE_KMLM_40_35_25": 0.40 * r_ntsx + 0.35 * r_gde + 0.25 * r_kmlm,
        "P8_RSSB_GDE_KMLM_50_30_20": 0.50 * r_rssb + 0.30 * r_gde + 0.20 * r_kmlm,
    }
    return portfolios


def build_portfolios_dbmf_side(df: pd.DataFrame) -> dict:
    """Side-test on 2000-2026 window — KMLM swapped for DBMF in P6/P7.

    P3 incumbent kept as benchmark. P8 dropped (RSSB scope already tested
    against KMLM in main run; DBMF swap doesn't add info for that pair).
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
    blend_p3 = 0.594 * r_spy + 0.396 * r_ief - 0.33 * r_cash + 0.34 * r_gde

    return {
        "P3_NTSX_GDE_blend":          blend_p3,
        "P6_NTSX_GDE_KMLM_50_35_15":  0.50 * r_ntsx + 0.35 * r_gde + 0.15 * r_kmlm,
        "P6_NTSX_GDE_DBMF_50_35_15":  0.50 * r_ntsx + 0.35 * r_gde + 0.15 * r_dbmf,
        "P7_NTSX_GDE_KMLM_40_35_25":  0.40 * r_ntsx + 0.35 * r_gde + 0.25 * r_kmlm,
        "P7_NTSX_GDE_DBMF_40_35_25":  0.40 * r_ntsx + 0.35 * r_gde + 0.25 * r_dbmf,
    }


def report_block(portfolios: dict, label: str) -> dict:
    print(f"\n=== {label} — full-window metrics ===")
    metrics_full = {}
    for name, r in portfolios.items():
        m = metrics(r.dropna(), name)
        metrics_full[name] = m
        print(f"  {name:<32}: Sh {m['sharpe']:.3f} | "
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
            print(f"  {name:<32}: CAGR mean {d['cagr_mean']*100:6.2f}% / "
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
                print(f"     {name:<32}: ret {sr['return_total']*100:+7.2f}% | "
                      f"MDD {sr['mdd']*100:+7.2f}%")
    return stress_results


def main() -> None:
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    print(f"Loaded synth: {df.index.min().date()} → {df.index.max().date()}")

    # === MAIN: 8-way on KMLM-bounded window ===
    portfolios_full = build_portfolios_full(df)
    common = portfolios_full["P1_SPY_100"].index
    block_full = report_block(portfolios_full, "8-WAY (KMLM, 1987-12 → 2026-04)")
    stress_full = stress_block(portfolios_full,
                               "8-WAY (KMLM, 1987-12 → 2026-04)")

    # === SIDE-TEST: DBMF swap on 2000-2026 window ===
    portfolios_side = build_portfolios_dbmf_side(df)
    common_side = portfolios_side["P3_NTSX_GDE_blend"].index
    block_side = report_block(portfolios_side,
                              "DBMF SIDE-TEST (2000-01 → 2026-04)")
    stress_side = stress_block(portfolios_side,
                               "DBMF SIDE-TEST (2000-01 → 2026-04)")

    # === Save ===
    out = {
        "main_run": {
            "window": {"start": str(common.min().date()),
                       "end": str(common.max().date()),
                       "years": len(common) / TRADING_DAYS,
                       "bars": len(common)},
            "portfolios": {
                "P1_SPY_100": "SPY 100%",
                "P2_NTSX": "0.90 SPY + 0.60 IEF - 0.50 CASH (NTSX synth)",
                "P3_NTSX_GDE_blend": ("0.594 SPY + 0.396 IEF - 0.33 CASH + "
                                      "0.34 GDE (~66% NTSX + 34% GDE)"),
                "P4_GDE_100": "GDE 100% (90 SPY + 90 Gold stacked)",
                "P5_SSO_ZROZ_GLD": "50% SSO + 25% ZROZ + 25% GLD; 0.89% drag",
                "P6_NTSX_GDE_KMLM_50_35_15": (
                    "50% NTSX + 35% GDE + 15% KMLM (conservative MF sleeve)"),
                "P7_NTSX_GDE_KMLM_40_35_25": (
                    "40% NTSX + 35% GDE + 25% KMLM (Dragon-lite MF weight)"),
                "P8_RSSB_GDE_KMLM_50_30_20": (
                    "50% RSSB + 30% GDE + 20% KMLM (full return-stack)"),
            },
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
    out_json = OUT_DIR / "LETFS_8WAY_VALIDATION.json"
    out_json.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_json}")

    pd.DataFrame(portfolios_full).to_parquet(
        OUT_DIR / "letfs_8way_returns.parquet"
    )
    pd.DataFrame(portfolios_side).to_parquet(
        OUT_DIR / "letfs_8way_dbmf_side_returns.parquet"
    )
    print(f"Wrote {OUT_DIR / 'letfs_8way_returns.parquet'}")
    print(f"Wrote {OUT_DIR / 'letfs_8way_dbmf_side_returns.parquet'}")


if __name__ == "__main__":
    main()
