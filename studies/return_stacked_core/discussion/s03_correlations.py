#!/usr/bin/env python3
"""s03 — decorrelation evidence: full-period, rolling and conditional correlations.

Outputs:
- ``tables/corr_full_daily.csv`` — pairwise Pearson on daily returns
  (pairwise max window, min_periods=252).
- ``tables/corr_full_monthly.csv`` — monthly compounding, incl. the AQR carry
  sleeve (monthly-native, so it only ever appears here and in s05's monthly
  table).
- ``tables/corr_rolling_252d.csv`` — 252-day rolling correlation, 6 sleeve pairs.
- ``tables/corr_conditional.csv`` — sleeve correlation matrices conditioned on
  SPY-down months and SPY worst-decile months.
- ``tables/crisis_capture.csv`` — mean monthly sleeve return + positive-month
  hit rate per condition ("who shows up in equity drawdowns").

Conditional correlation is where diversification claims live or die — average
correlation is dominated by calm regimes `[risk_parity, ch.5]`. Estimation
noise on decile-conditioned samples is material (n≈31 months); treat point
estimates as descriptive `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402

DAILY_COLS = [
    "SPYSIM", "GLDSIM", "MFBLEND", "DBMFSIM", "KMLMSIM", "ZROZSIM", "TLTPROXY",
    "BTCSIM", "GDESIM", "RSSTSIM", "NTSXSIM", "RSSXSIM",
]
ROLLING_PAIRS = [
    ("SPYSIM", "GLDSIM"),
    ("SPYSIM", "MFBLEND"),
    ("SPYSIM", "ZROZSIM"),
    ("GLDSIM", "ZROZSIM"),
    ("MFBLEND", "ZROZSIM"),
    ("GLDSIM", "MFBLEND"),
]
SLEEVES_MONTHLY = ["SPYSIM", "GLDSIM", "MFBLEND", "ZROZSIM", "BTCSIM", "CARRY_SCALED"]


def main() -> int:
    primary = pd.read_parquet(dd.SERIES_DIR / "primary_returns.parquet")
    proxies = pd.read_parquet(dd.SERIES_DIR / "proxy_returns.parquet")
    daily = primary.join(proxies)[DAILY_COLS]

    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    corr_daily = daily.corr(method="pearson", min_periods=252)
    corr_daily.to_csv(dd.TABLES_DIR / "corr_full_daily.csv")

    monthly = dd.monthly_returns(daily)
    rssy_path = dd.SERIES_DIR / "rssy_monthly.parquet"
    if rssy_path.exists():
        carry = pd.read_parquet(rssy_path)["CARRY_SCALED"]
        carry.index = carry.index.to_period("M").to_timestamp("M")
        monthly = monthly.join(carry, how="left")
    else:
        print("WARNING: rssy_monthly missing — carry column absent from monthly corr.",
              file=sys.stderr)
    corr_monthly = monthly.corr(method="pearson", min_periods=24)
    corr_monthly.to_csv(dd.TABLES_DIR / "corr_full_monthly.csv")

    rolling = pd.DataFrame(index=daily.index)
    for a, b in ROLLING_PAIRS:
        rolling[f"{a}~{b}"] = daily[a].rolling(252, min_periods=252).corr(daily[b])
    rolling.dropna(how="all").to_csv(
        dd.TABLES_DIR / "corr_rolling_252d.csv", index_label="date"
    )

    # Conditional analysis on monthly sleeve returns.
    sleeves = [c for c in SLEEVES_MONTHLY if c in monthly.columns]
    m = monthly[sleeves]
    spy = m["SPYSIM"].dropna()
    down_months = spy[spy < 0].index
    decile_cut = spy.quantile(0.10)
    worst_decile = spy[spy <= decile_cut].index

    cond_frames = []
    capture_rows = []
    for label, idx in (
        ("all_months", spy.index),
        ("spy_down_months", down_months),
        ("spy_worst_decile", worst_decile),
    ):
        sub = m.loc[m.index.intersection(idx)]
        c = sub.corr(method="pearson", min_periods=12)
        c.insert(0, "condition", label)
        c.insert(1, "n_months", len(sub))
        cond_frames.append(c)
        for col in sleeves:
            vals = sub[col].dropna()
            capture_rows.append(
                {
                    "condition": label,
                    "asset": col,
                    "n_months": len(vals),
                    "mean_monthly_return": float(vals.mean()),
                    "hit_rate_positive": float((vals > 0).mean()),
                }
            )

    pd.concat(cond_frames).to_csv(
        dd.TABLES_DIR / "corr_conditional.csv", index_label="asset"
    )
    pd.DataFrame(capture_rows).to_csv(
        dd.TABLES_DIR / "crisis_capture.csv", index=False
    )

    pairs = corr_monthly.loc["SPYSIM", ["GLDSIM", "MFBLEND", "ZROZSIM"]]
    print("monthly corr vs SPY:", {k: round(v, 3) for k, v in pairs.items()})
    print(f"SPY-down months: {len(down_months)}; worst decile: {len(worst_decile)} "
          f"(cut {decile_cut:.2%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
