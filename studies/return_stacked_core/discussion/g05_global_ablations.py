#!/usr/bin/env python3
"""g05 — global ablation battery, benchmark VT, monthly rebalance.

Two tables: ``tables/global_ablations_primary.csv`` (2000+, MFBLEND sleeves)
and ``tables/global_ablations_1988.csv`` (canonical window, KMLM-only).
Also exports ``series/global_portfolio_equity.parquet`` for g07 figures.

The battery answers the global composition questions directly: what NTSD/RSIT
actually buy vs their Sharpe cost, NTSI vs NTSD, the one-fund NTSG/RSSB
routes, EM-beta add-on, and the US core as the always-available alternative
`[risk_parity, ch.5]`, `[testing_tuning, p.327-335]`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402
from studies.return_stacked_core.discussion import engine  # noqa: E402

THIRD = 4.0 / 15.0  # 20/15-renormalized share

CONFIGS_PRIMARY: list[tuple[str, str, dict[str, float]]] = [
    ("G0", "CORE-GLOBAL 20/15/20/20/25",
     {"GDESIM": .20, "NTSDSIM": .15, "RSSTSIM": .20, "RSITSIM": .20, "ZROZSIM": .25}),
    ("G1", "US CORE 35/40/25", {"GDESIM": .35, "RSSTSIM": .40, "ZROZSIM": .25}),
    ("G2", "Benchmark-purist 25/10NTSI/25/15/25",
     {"GDESIM": .25, "NTSISIM": .10, "RSSTSIM": .25, "RSITSIM": .15, "ZROZSIM": .25}),
    ("G3", "NTSI swap 20/15NTSI/20/20/25",
     {"GDESIM": .20, "NTSISIM": .15, "RSSTSIM": .20, "RSITSIM": .20, "ZROZSIM": .25}),
    ("G4", "No-RSIT (MF all-US) 20/15/40/25",
     {"GDESIM": .20, "NTSDSIM": .15, "RSSTSIM": .40, "ZROZSIM": .25}),
    ("G5", "No-NTSD 25/25/25/25",
     {"GDESIM": .25, "RSSTSIM": .25, "RSITSIM": .25, "ZROZSIM": .25}),
    ("G6", "No-ZROZ renorm",
     {"GDESIM": THIRD, "NTSDSIM": .20, "RSSTSIM": THIRD, "RSITSIM": THIRD}),
    ("G7", "RSSB for ZROZ 20/15/20/20/25",
     {"GDESIM": .20, "NTSDSIM": .15, "RSSTSIM": .20, "RSITSIM": .20, "RSSBSIM": .25}),
    ("G8", "NTSG core 35/40/25",
     {"NTSGSIM": .35, "RSSTSIM": .40, "ZROZSIM": .25}),
    ("G9", "CORE-GLOBAL + 10% VWO (pro-rata)",
     {"GDESIM": .18, "NTSDSIM": .135, "RSSTSIM": .18, "RSITSIM": .18,
      "ZROZSIM": .225, "VWOSIM": .10}),
    ("G10", "Half-intl 27.5/7.5/30/10/25",
     {"GDESIM": .275, "NTSDSIM": .075, "RSSTSIM": .30, "RSITSIM": .10, "ZROZSIM": .25}),
    ("G11", "100% VT", {"VTSIM": 1.0}),
    ("G12", "66/34 VTI/VEA", {"VTISIM": .66, "VEASIM": .34}),
    ("G13", "100% NTSD", {"NTSDSIM": 1.0}),
    ("G14", "100% NTSI", {"NTSISIM": 1.0}),
    ("G15", "100% RSIT", {"RSITSIM": 1.0}),
    ("G16", "100% NTSG", {"NTSGSIM": 1.0}),
    ("G17", "100% RSSB", {"RSSBSIM": 1.0}),
]

CONFIGS_1988: list[tuple[str, str, dict[str, float]]] = [
    ("G0", "CORE-GLOBAL 20/15/20/20/25",
     {"GDESIM": .20, "NTSDSIM": .15, "RSST_KM": .20, "RSIT_KM": .20, "ZROZSIM": .25}),
    ("G1", "US CORE 35/40/25", {"GDESIM": .35, "RSST_KM": .40, "ZROZSIM": .25}),
    ("G4", "No-RSIT (MF all-US) 20/15/40/25",
     {"GDESIM": .20, "NTSDSIM": .15, "RSST_KM": .40, "ZROZSIM": .25}),
    ("G10", "Half-intl 27.5/7.5/30/10/25",
     {"GDESIM": .275, "NTSDSIM": .075, "RSST_KM": .30, "RSIT_KM": .10, "ZROZSIM": .25}),
    ("G11", "100% VT", {"VTSIM": 1.0}),
    ("G12", "66/34 VTI/VEA", {"VTISIM": .66, "VEASIM": .34}),
]

EQUITY_EXPORT = ["G0", "G1", "G10", "G11", "G12", "G7", "G8"]


def run_battery(daily: pd.DataFrame, configs, window_label: str):
    rows, curves = [], {}
    base = None
    for cfg_id, label, weights in configs:
        equity = engine.rebalanced_equity(daily, weights)
        m = engine.compute_metrics(equity)
        if cfg_id == "G0":
            base = m
        rows.append({"id": cfg_id, "config": label, "window": window_label, **m})
        curves[cfg_id] = equity
    frame = pd.DataFrame(rows)
    for key in ("cagr", "mdd", "sharpe"):
        frame[f"d_{key}_vs_core_global"] = frame[key] - base[key]
    return frame, curves


def main() -> int:
    primary = pd.read_parquet(dd.SERIES_DIR / "global_primary_returns.parquet")
    g88 = pd.read_parquet(dd.SERIES_DIR / "global_1988_returns.parquet")
    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    prim, curves = run_battery(primary, CONFIGS_PRIMARY, "primary 2000+")
    prim.to_csv(dd.TABLES_DIR / "global_ablations_primary.csv", index=False)

    g88_frame, _ = run_battery(g88, CONFIGS_1988, "canonical 1988+")
    g88_frame.to_csv(dd.TABLES_DIR / "global_ablations_1988.csv", index=False)

    labels = {cfg_id: label for cfg_id, label, _ in CONFIGS_PRIMARY}
    export = pd.DataFrame({c: curves[c] for c in EQUITY_EXPORT})
    export.columns = [f"{c}|{labels[c]}" for c in export.columns]
    export.to_parquet(dd.SERIES_DIR / "global_portfolio_equity.parquet")

    cols = ["id", "config", "cagr", "mdd", "sharpe", "d_sharpe_vs_core_global"]
    print(prim[cols].round(4).to_string(index=False))
    print()
    print(g88_frame[cols].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
