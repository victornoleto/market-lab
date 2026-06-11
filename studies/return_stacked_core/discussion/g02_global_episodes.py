#!/usr/bin/env python3
"""g02 — global per-episode behavior, benchmark VT.

Same slicing methodology as s02 (full-period equity curves, episode windows,
re-anchored episode MDD), now with spread vs VT. Three window tiers:

- primary 2000+ episodes (same dates as s02, cross-comparable with the US
  tables);
- 1988+ extras only reachable on the canonical global window: 1990 recession
  / Gulf War and the 1997-98 Asia/LTCM crisis;
- extended 1970+ episodes (LOW fidelity) if the matrix exists.

Outputs: ``tables/global_episodes_components.csv``,
``tables/global_episodes_products.csv``.
Diversifier-in-equity-drawdown framing: `[risk_parity, ch.5]`.
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
from studies.return_stacked_core.discussion.s02_episodes import (  # noqa: E402
    EPISODES, episode_table,
)

EPISODES_1988 = [
    ("1990 recession / Gulf War", "1990-07-16", "1990-10-11", "g1988"),
    ("Asia crisis + LTCM", "1997-07-01", "1998-10-08", "g1988"),
]

GLOBAL_CORE = {
    "GDESIM": 0.20, "NTSDSIM": 0.15, "RSSTSIM": 0.20, "RSITSIM": 0.20,
    "ZROZSIM": 0.25,
}
GLOBAL_CORE_KM = {
    "GDESIM": 0.20, "NTSDSIM": 0.15, "RSST_KM": 0.20, "RSIT_KM": 0.20,
    "ZROZSIM": 0.25,
}
US_CORE = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}
US_CORE_KM = {"GDESIM": 0.35, "RSST_KM": 0.40, "ZROZSIM": 0.25}
BENCH_6634 = {"VTISIM": 0.66, "VEASIM": 0.34}


def main() -> int:
    primary = pd.read_parquet(dd.SERIES_DIR / "global_primary_returns.parquet")
    g88 = pd.read_parquet(dd.SERIES_DIR / "global_1988_returns.parquet")
    eq = engine.equity_from_returns

    primary_eps = [e for e in EPISODES if e[3] == "primary"]
    vt_eq = eq(primary["VTSIM"])

    components = {
        "VT": vt_eq,
        "SPY": eq(primary["SPYSIM"]),
        "VEA (dev ex-US)": eq(primary["VEASIM"]),
        "VXUS (total intl)": eq(primary["VXUSSIM"]),
        "VWO (EM)": eq(primary["VWOSIM"]),
        "GLD": eq(primary["GLDSIM"]),
        "MFBLEND": eq(primary["MFBLEND"]),
        "ZROZ": eq(primary["ZROZSIM"]),
    }
    comp_df = episode_table(components, primary_eps, vt_eq)

    products = {
        "VT": vt_eq,
        "66/34 VTI/VEA": engine.rebalanced_equity(primary, BENCH_6634),
        "GDE": eq(primary["GDESIM"]),
        "NTSD": eq(primary["NTSDSIM"]),
        "NTSI": eq(primary["NTSISIM"]),
        "RSIT": eq(primary["RSITSIM"]),
        "RSSB": eq(primary["RSSBSIM"]),
        "CORE-GLOBAL 20/15/20/20/25": engine.rebalanced_equity(primary, GLOBAL_CORE),
        "US CORE 35/40/25": engine.rebalanced_equity(primary, US_CORE),
    }
    prod_df = episode_table(products, primary_eps, vt_eq)

    # 1988+ extras (KMLM-only sleeves).
    vt88 = eq(g88["VTSIM"])
    comp88 = {
        "VT": vt88,
        "SPY": eq(g88["SPYSIM"]),
        "VEA (dev ex-US)": eq(g88["VEASIM"]),
        "GLD": eq(g88["GLDSIM"]),
        "KMLM": eq(g88["KMLMSIM"]),
        "ZROZ": eq(g88["ZROZSIM"]),
    }
    prod88 = {
        "VT": vt88,
        "CORE-GLOBAL 20/15/20/20/25": engine.rebalanced_equity(g88, GLOBAL_CORE_KM),
        "US CORE 35/40/25": engine.rebalanced_equity(g88, US_CORE_KM),
    }
    comp_df = pd.concat(
        [comp_df, episode_table(comp88, EPISODES_1988, vt88)], ignore_index=True
    )
    prod_df = pd.concat(
        [prod_df, episode_table(prod88, EPISODES_1988, vt88)], ignore_index=True
    )

    # Extended 1970+ (LOW fidelity).
    ext_path = dd.SERIES_DIR / "global_extended_returns.parquet"
    if ext_path.exists():
        ext = pd.read_parquet(ext_path)
        ext_eps = [e for e in EPISODES if e[3] == "extended"]
        vt_ext = eq(ext["VTSIM"])
        comp_ext = {
            "VT": vt_ext,
            "SPY": eq(ext["SPYSIM"]),
            "VEA (dev ex-US)": eq(ext["VEASIM"]),
            "GLD": eq(ext["GLDSIM"]),
            "KMLM_SPLICED": eq(ext["KMLM_SPLICED"]),
            "ZROZ": eq(ext["ZROZSIM"]),
        }
        comp_df = pd.concat(
            [comp_df, episode_table(comp_ext, ext_eps, vt_ext)], ignore_index=True
        )
    else:
        print("WARNING: global extended matrix missing — extended episodes skipped.",
              file=sys.stderr)

    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    rename = {"spread_vs_spy": "spread_vs_vt"}  # benchmark here is VT
    comp_df.rename(columns=rename).to_csv(
        dd.TABLES_DIR / "global_episodes_components.csv", index=False
    )
    prod_df.rename(columns=rename).to_csv(
        dd.TABLES_DIR / "global_episodes_products.csv", index=False
    )
    print(f"global episodes: {len(comp_df)} component rows, {len(prod_df)} product rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
