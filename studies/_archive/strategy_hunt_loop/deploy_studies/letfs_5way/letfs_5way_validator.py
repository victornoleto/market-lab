"""5-way LETF portfolio comparison for r/LETFs post.

Question (2026-04-26): "Is there anything materially better than NTSX+GDE
blend? Compare against SPY baseline, vanilla NTSX, GDE alone, and the
classic 50/25/25 SSO/ZROZ/GLD trio."

Portfolios
----------
P1: SPY 100%
    Baseline. Plain S&P 500.

P2: NTSX (synth: 0.90 SPYSIM + 0.60 IEFSIM - 0.50 CASHX)
    1.5x return-stacked S&P 500 + IEF (7-10y treasuries).
    Yearly rebal, no drag.

P3: NTSX + GDE blend (0.594 SPYSIM + 0.396 IEFSIM - 0.33 CASHX + 0.34 GDESIM)
    Equivalent of 66% NTSX + 34% GDE.
    Adds gold leg via WisdomTree GDE (90% S&P + 90% gold futures).
    Yearly rebal, no drag.

P4: GDE 100%
    1.8x stacked S&P + gold. Pure return-stacking with gold overlay.

P5: SSO/ZROZ/GLD 50/25/25
    Classic Hedgefundie-style trio: 2x S&P (SSO) + 25y zero coupon
    treasuries (ZROZ) + gold (GLD).
    Monthly rebal, 0.89% expense drag (mix of SSO 0.91 + ZROZ 0.15 + GLD 0.40).

Window
------
Bounded by SSOSIM/ZROZSIM/GLDSIM start: 1986-01-02 → 2026-04-17 (~40y).

Methodology notes
-----------------
* Daily-reweighted portfolios (continuous rebalance approximation). This
  diverges slightly from yearly/monthly rebalance but ranking is preserved.
  Confirmed against testfolio by the prior us_vs_global_study report.
* Drag only applied to P5 (the only portfolio with non-trivial expense
  ratio differential vs the SPY baseline).
* All metrics use daily returns annualized to 252 trading days.

Citations
---------
* WisdomTree (2024). "GDE Fund Page" + prospectus — 90/90 stacking design.
* Wisdom Tree (2018). "NTSX Fund Page" — 90/60 stacking design.
* Hedgefundie (Bogleheads, 2019). "The Excellent Adventure" thread —
  origin of UPRO/TMF, then SSO/ZROZ/GLD as the more conservative cousin.
* Asness, Frazzini, Pedersen (2012). "Leverage Aversion and Risk Parity."
  FAJ — academic justification for return-stacked portfolios.
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


def build_portfolios(df: pd.DataFrame) -> dict:
    r_spy = returns_from_prices(df["SPYSIM"])
    r_ief = returns_from_prices(df["IEFSIM"])
    r_cash = returns_from_prices(df["CASHX"])
    r_gde = returns_from_prices(df["GDESIM"])
    r_sso = returns_from_prices(df["SSOSIM"])
    r_zroz = returns_from_prices(df["ZROZSIM"])
    r_gld = returns_from_prices(df["GLDSIM"])

    common = (r_spy.index
              .intersection(r_ief.index)
              .intersection(r_cash.index)
              .intersection(r_gde.index)
              .intersection(r_sso.index)
              .intersection(r_zroz.index)
              .intersection(r_gld.index))
    print(f"5-way LETF common window: {common.min().date()} → "
          f"{common.max().date()} ({len(common)} bars / "
          f"{len(common)/TRADING_DAYS:.1f}y)")

    r_spy = r_spy.reindex(common)
    r_ief = r_ief.reindex(common)
    r_cash = r_cash.reindex(common)
    r_gde = r_gde.reindex(common)
    r_sso = r_sso.reindex(common)
    r_zroz = r_zroz.reindex(common)
    r_gld = r_gld.reindex(common)

    drag_p5 = 0.0089 / TRADING_DAYS  # 0.89% annual expense drag, daily

    portfolios = {
        "P1_SPY_100": r_spy,
        "P2_NTSX": 0.90 * r_spy + 0.60 * r_ief - 0.50 * r_cash,
        "P3_NTSX_GDE_blend": (
            0.594 * r_spy + 0.396 * r_ief - 0.33 * r_cash + 0.34 * r_gde
        ),
        "P4_GDE_100": r_gde,
        "P5_SSO_ZROZ_GLD": (
            0.50 * r_sso + 0.25 * r_zroz + 0.25 * r_gld - drag_p5
        ),
    }
    return portfolios


# --- Main --------------------------------------------------------------------


def main() -> None:
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    print(f"Loaded synth: {df.index.min().date()} → {df.index.max().date()}")

    portfolios = build_portfolios(df)
    common = portfolios["P1_SPY_100"].index

    # === Full-window metrics ===
    print("\n=== Full window metrics ===")
    metrics_full = {}
    for name, r in portfolios.items():
        m = metrics(r.dropna(), name)
        metrics_full[name] = m
        print(f"  {name:<22}: Sh {m['sharpe']:.3f} | CAGR {m['cagr']*100:6.2f}% | "
              f"Vol {m['vol']*100:5.2f}% | MDD {m['mdd']*100:5.2f}%")

    # === Rolling 5y / 10y / 15y / 20y ===
    print("\n=== Rolling windows ===")
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
            print(f"  {name:<22}: CAGR mean {d['cagr_mean']*100:6.2f}% / "
                  f"min {d['cagr_min']*100:6.2f}% / "
                  f"5pct {d['cagr_5pct']*100:6.2f}% / "
                  f"Sharpe mean {d['sharpe_mean']:.2f} / "
                  f"P(<5%) {d['p_cagr_below_5pct']*100:5.1f}%")

    # === Stress periods ===
    print("\n=== Stress tests ===")
    stress_periods = {
        "2000-2003_dotcom_bear": ("2000-03-24", "2002-10-09"),
        "2007-2009_GFC": ("2007-10-09", "2009-03-09"),
        "2020-03_COVID": ("2020-02-19", "2020-03-23"),
        "2022_rate_cycle": ("2022-01-01", "2022-12-31"),
        "2008_full_year": ("2008-01-01", "2008-12-31"),
        "1987_crash": ("1987-08-25", "1987-12-04"),
    }
    stress_results = {}
    for period_name, (s, e) in stress_periods.items():
        print(f"\n  {period_name} ({s} → {e}):")
        stress_results[period_name] = {}
        for name, r in portfolios.items():
            sr = stress_window(r.dropna(), s, e)
            stress_results[period_name][name] = sr
            if sr["n_bars"] > 0:
                print(f"     {name:<22}: ret {sr['return_total']*100:+7.2f}% | "
                      f"MDD {sr['mdd']*100:+7.2f}%")

    # === Save ===
    out = {
        "window": {"start": str(common.min().date()),
                   "end": str(common.max().date()),
                   "years": len(common) / TRADING_DAYS,
                   "bars": len(common)},
        "portfolios": {
            "P1_SPY_100": "SPY 100% (SPYSIM)",
            "P2_NTSX": "0.90 SPY + 0.60 IEF - 0.50 CASH (NTSX synth, 1.5x stacked)",
            "P3_NTSX_GDE_blend": ("0.594 SPY + 0.396 IEF - 0.33 CASH + 0.34 GDE "
                                   "(equiv 66% NTSX + 34% GDE)"),
            "P4_GDE_100": "GDE 100% (90 SPY + 90 Gold stacked)",
            "P5_SSO_ZROZ_GLD": ("50% SSO (2x SPY) + 25% ZROZ (25y zero) + 25% GLD; "
                                  "monthly rebal; 0.89% drag"),
        },
        "metrics_full": metrics_full,
        "rolling": rolling_data,
        "stress_tests": stress_results,
    }
    out_json = OUT_DIR / "LETFS_5WAY_VALIDATION.json"
    out_json.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_json}")

    pd.DataFrame(portfolios).to_parquet(OUT_DIR / "letfs_5way_returns.parquet")
    print(f"Wrote {OUT_DIR / 'letfs_5way_returns.parquet'}")


if __name__ == "__main__":
    main()
