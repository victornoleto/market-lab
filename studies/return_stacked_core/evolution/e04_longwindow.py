"""e04 — G5 long-window diagnostic (1988+, KMLM-only MF sleeve).

LOW-fidelity lens: RSST88/RSBT88 replace the 70/30 DBMF/KMLM blend with
100% KMLM (DBMFSIM starts in 2000). Adds the 1988-2000 regime (1990
recession, 1994 bond massacre, 1998 LTCM) as a sanity check on the Round 1/2
near-misses. Diagnostic only — never a pass/fail gate on its own (PLAN.md).
"""
from __future__ import annotations

import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine

# Primary-window sleeve -> long-window equivalent.
MAP88 = {"RSSTSIM": "RSST88", "RSBTSIM": "RSBT88"}

PORTFOLIOS = {
    "CORE 35/40/25": {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25},
    "EW 33/33/33": {"GDESIM": 1 / 3, "RSSTSIM": 1 / 3, "ZROZSIM": 1 / 3},
    "3A in-cap argmax 45/25/30": {"GDESIM": 0.45, "RSSTSIM": 0.25, "ZROZSIM": 0.30},
    "RSBT structure 60/20/20": {"GDESIM": 0.60, "ZROZSIM": 0.20, "RSBTSIM": 0.20},
    "KMLM structure 55/10/15/20": {
        "GDESIM": 0.55, "RSSTSIM": 0.10, "ZROZSIM": 0.15, "KMLMSIM": 0.20,
    },
    "KMLM structure 60/5/20/15": {
        "GDESIM": 0.60, "RSSTSIM": 0.05, "ZROZSIM": 0.20, "KMLMSIM": 0.15,
    },
    "G1-passer 60/5/35 (no ZROZ)": {
        "GDESIM": 0.60, "RSSTSIM": 0.05, "KMLMSIM": 0.35,
    },
    "G4-passer 50/20/15/15 QQQ": {
        "GDESIM": 0.50, "ZROZSIM": 0.20, "RSBTSIM": 0.15, "QQQSIM": 0.15,
    },
    "100% SPY": {"SPYSIM": 1.0},
}


def main() -> None:
    matrix = evo_data.load_longwindow_matrix()
    rows = []
    for name, weights in PORTFOLIOS.items():
        w88 = {MAP88.get(k, k): v for k, v in weights.items()}
        eq = evo_engine.rebalanced_equity(matrix, w88)
        m = evo_engine.compute_metrics(eq)
        rows.append({"portfolio": name, **m})
        print(
            f"{name}: cagr={m['cagr']:.4f} mdd={m['mdd']:.4f} "
            f"sharpe={m['sharpe']:.4f} ({m['start']}..{m['end']})"
        )
    df = pd.DataFrame(rows)
    core = df[df["portfolio"] == "CORE 35/40/25"].iloc[0]
    df["d_cagr_vs_core"] = df["cagr"] - core["cagr"]
    df["d_mdd_vs_core"] = df["mdd"] - core["mdd"]
    df["g5_flag"] = (df["cagr"] < core["cagr"]) | (df["mdd"] < core["mdd"] - 0.02)
    df.to_csv(evo_data.TABLES_DIR / "longwindow_1988.csv", index=False)
    print("\nG5 flags (underperforms CORE-1988 CAGR or deepens MDD >2pp):")
    print(df[["portfolio", "cagr", "mdd", "g5_flag"]].to_string(index=False))


if __name__ == "__main__":
    main()
