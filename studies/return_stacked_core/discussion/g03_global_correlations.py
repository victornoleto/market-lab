#!/usr/bin/env python3
"""g03 — global decorrelation evidence, conditioned on VT (not SPY).

Outputs:
- ``tables/global_corr_full_daily.csv`` / ``global_corr_full_monthly.csv``
- ``tables/global_corr_rolling_252d.csv`` — 6 pairs incl. the US~intl equity
  pair (the key question for going global: how much diversification does
  international equity actually add vs the alternative sleeves?)
- ``tables/global_corr_conditional.csv`` / ``global_crisis_capture.csv`` —
  VT-down months and VT worst-decile months `[risk_parity, ch.5]`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402

COLS = ["VTSIM", "SPYSIM", "VEASIM", "VXUSSIM", "VWOSIM", "GLDSIM", "MFBLEND",
        "ZROZSIM", "NTSDSIM", "NTSISIM", "RSITSIM", "RSSBSIM", "GDESIM", "RSSTSIM"]
ROLLING_PAIRS = [
    ("SPYSIM", "VEASIM"),
    ("SPYSIM", "VXUSSIM"),
    ("VTSIM", "GLDSIM"),
    ("VTSIM", "MFBLEND"),
    ("VTSIM", "ZROZSIM"),
    ("VEASIM", "MFBLEND"),
]
SLEEVES_MONTHLY = ["VTSIM", "SPYSIM", "VEASIM", "VXUSSIM", "VWOSIM", "GLDSIM",
                   "MFBLEND", "ZROZSIM"]


def main() -> int:
    daily = pd.read_parquet(dd.SERIES_DIR / "global_primary_returns.parquet")[COLS]
    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    daily.corr(method="pearson", min_periods=252).to_csv(
        dd.TABLES_DIR / "global_corr_full_daily.csv"
    )
    monthly = dd.monthly_returns(daily)
    monthly.corr(method="pearson", min_periods=24).to_csv(
        dd.TABLES_DIR / "global_corr_full_monthly.csv"
    )

    rolling = pd.DataFrame(index=daily.index)
    for a, b in ROLLING_PAIRS:
        rolling[f"{a}~{b}"] = daily[a].rolling(252, min_periods=252).corr(daily[b])
    rolling.dropna(how="all").to_csv(
        dd.TABLES_DIR / "global_corr_rolling_252d.csv", index_label="date"
    )

    m = monthly[SLEEVES_MONTHLY]
    vt = m["VTSIM"].dropna()
    down = vt[vt < 0].index
    cut = vt.quantile(0.10)
    worst = vt[vt <= cut].index

    cond_frames, capture_rows = [], []
    for label, idx in (("all_months", vt.index), ("vt_down_months", down),
                       ("vt_worst_decile", worst)):
        sub = m.loc[m.index.intersection(idx)]
        c = sub.corr(method="pearson", min_periods=12)
        c.insert(0, "condition", label)
        c.insert(1, "n_months", len(sub))
        cond_frames.append(c)
        for col in SLEEVES_MONTHLY:
            vals = sub[col].dropna()
            capture_rows.append({
                "condition": label, "asset": col, "n_months": len(vals),
                "mean_monthly_return": float(vals.mean()),
                "hit_rate_positive": float((vals > 0).mean()),
            })

    pd.concat(cond_frames).to_csv(
        dd.TABLES_DIR / "global_corr_conditional.csv", index_label="asset"
    )
    pd.DataFrame(capture_rows).to_csv(
        dd.TABLES_DIR / "global_crisis_capture.csv", index=False
    )

    corr_m = monthly.corr(min_periods=24)
    print("monthly corr vs VT:",
          {k: round(v, 3) for k, v in
           corr_m.loc["VTSIM", ["SPYSIM", "VEASIM", "GLDSIM", "MFBLEND", "ZROZSIM"]].items()})
    print("US~intl equity monthly corr:",
          round(float(corr_m.loc["SPYSIM", "VXUSSIM"]), 3))
    print(f"VT-down months: {len(down)}; worst decile: {len(worst)} (cut {cut:.2%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
