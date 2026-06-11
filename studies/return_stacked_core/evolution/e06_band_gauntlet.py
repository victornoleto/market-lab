"""e06 — full gauntlet on the Round-4 band candidates vs CORE-monthly.

Candidates = (structure, band) pairs from e05 with parameter-plateau
improvement, full-window CAGR > CORE-monthly and MDD >= -30%. Gates mirror
PLAN.md G1-G5 with the band mechanism held fixed:

G1 start-date: beats CORE-monthly CAGR (same start) in >= 7/8 starts.
G2 weight-neighborhood: all +-5pp one-step weight neighbors, SAME band,
   have MDD >= -32% and mean neighbor CAGR > CORE-monthly. (Band plateau
   was already established in e05.)
G3 drag stress: +50bps/yr on sleeves not in {GDE,RSST,ZROZ}.
G4 rolling 5y dominance vs CORE-monthly >= 60% of windows.
G5 1988+ diagnostic (KMLM-only proxies): flag if CAGR < CORE-monthly-1988
   or MDD deepened > 2pp vs CORE-monthly-1988.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine
from studies.return_stacked_core.evolution.e05_bands import (
    MAP88,
    band_rebalanced_equity,
)

DRAG_DAILY = 0.0050 / 252
CORE_SLEEVES = {"GDESIM", "RSSTSIM", "ZROZSIM"}

# (label, weights, band) — e05 plateau rows with cagr > CORE and in-cap.
CANDIDATES = [
    ("45/25/30 b15", {"GDESIM": 45, "RSSTSIM": 25, "ZROZSIM": 30}, 0.15),
    ("45/25/30 b20", {"GDESIM": 45, "RSSTSIM": 25, "ZROZSIM": 30}, 0.20),
    ("45/25/30 b25", {"GDESIM": 45, "RSSTSIM": 25, "ZROZSIM": 30}, 0.25),
    ("RSBT 60/20/20 b10", {"GDESIM": 60, "ZROZSIM": 20, "RSBTSIM": 20}, 0.10),
    ("RSBT 60/20/20 b15", {"GDESIM": 60, "ZROZSIM": 20, "RSBTSIM": 20}, 0.15),
    ("RSBT 60/20/20 b20", {"GDESIM": 60, "ZROZSIM": 20, "RSBTSIM": 20}, 0.20),
    ("RSBT 60/20/20 b25", {"GDESIM": 60, "ZROZSIM": 20, "RSBTSIM": 20}, 0.25),
    ("KMLM 55/10/15/20 b10",
     {"GDESIM": 55, "RSSTSIM": 10, "ZROZSIM": 15, "KMLMSIM": 20}, 0.10),
    ("KMLM 55/10/15/20 b15",
     {"GDESIM": 55, "RSSTSIM": 10, "ZROZSIM": 15, "KMLMSIM": 20}, 0.15),
    ("KMLM 55/10/15/20 b20",
     {"GDESIM": 55, "RSSTSIM": 10, "ZROZSIM": 15, "KMLMSIM": 20}, 0.20),
    ("KMLM 55/10/15/20 b25",
     {"GDESIM": 55, "RSSTSIM": 10, "ZROZSIM": 15, "KMLMSIM": 20}, 0.25),
    ("EW b50", {"GDESIM": 33.34, "RSSTSIM": 33.33, "ZROZSIM": 33.33}, 0.50),
]

CORE_W = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}


def frac(w: dict[str, float]) -> dict[str, float]:
    return {k: v / 100.0 for k, v in w.items()}


def neighbors(w: dict[str, float]) -> list[dict[str, float]]:
    keys = list(w)
    out = []
    for i in keys:
        if w[i] < 5:
            continue
        for j in keys:
            if i == j:
                continue
            nb = dict(w)
            nb[i] -= 5
            nb[j] += 5
            out.append(nb)
    return out


def main() -> None:
    matrix = evo_data.load_primary_matrix()
    lw = evo_data.load_longwindow_matrix()

    core_eq = evo_engine.rebalanced_equity(matrix, CORE_W)
    core_roll = evo_engine.rolling_cagr(core_eq)
    core_by_start = {
        s: evo_engine.compute_metrics(
            evo_engine.rebalanced_equity(matrix.loc[s:], CORE_W)
        )["cagr"]
        for s in evo_data.START_DATES
    }
    core88 = evo_engine.compute_metrics(
        evo_engine.rebalanced_equity(lw, {MAP88.get(k, k): v for k, v in CORE_W.items()})
    )
    print(f"CORE-1988 monthly: cagr={core88['cagr']:.4f} mdd={core88['mdd']:.4f}")

    rows = []
    for label, w_pct, band in CANDIDATES:
        w = frac(w_pct)
        eq = band_rebalanced_equity(matrix, w, band)
        m = evo_engine.compute_metrics(eq)

        # G1
        beats = 0
        per_start = {}
        for s, core_c in core_by_start.items():
            mc = evo_engine.compute_metrics(
                band_rebalanced_equity(matrix.loc[s:], w, band)
            )["cagr"]
            per_start[s] = mc - core_c
            beats += int(mc > core_c)

        # G2 (weight neighbors at same band)
        nb_cagr, nb_mdd = [], []
        for nb in neighbors(w_pct):
            nm = evo_engine.compute_metrics(
                band_rebalanced_equity(matrix, frac(nb), band)
            )
            nb_cagr.append(nm["cagr"])
            nb_mdd.append(nm["mdd"])
        g2 = min(nb_mdd) >= -0.32 and float(np.mean(nb_cagr)) > evo_data.CORE_CAGR

        # G3
        stressed = matrix.copy()
        for a in w:
            if a not in CORE_SLEEVES:
                stressed[a] = stressed[a] - DRAG_DAILY
        g3_cagr = evo_engine.compute_metrics(
            band_rebalanced_equity(stressed, w, band)
        )["cagr"]

        # G4
        roll = evo_engine.rolling_cagr(eq)
        joined = pd.concat([roll, core_roll], axis=1, keys=["c", "core"]).dropna()
        g4 = float((joined["c"] > joined["core"]).mean())

        # G5
        w88 = {MAP88.get(k, k): v for k, v in w.items()}
        m88 = evo_engine.compute_metrics(band_rebalanced_equity(lw, w88, band))
        g5_flag = (m88["cagr"] < core88["cagr"]) or (m88["mdd"] < core88["mdd"] - 0.02)

        row = {
            "candidate": label, "band": band, "cagr": m["cagr"], "mdd": m["mdd"],
            "sharpe": m["sharpe"], "g1_beats": beats, "g1_pass": beats >= 7,
            "g2_pass": g2, "g2_nbhd_min_cagr": min(nb_cagr),
            "g2_nbhd_worst_mdd": min(nb_mdd),
            "g3_cagr_stressed": g3_cagr, "g3_pass": g3_cagr > evo_data.CORE_CAGR,
            "g4_share": g4, "g4_pass": g4 >= 0.60,
            "cagr_1988": m88["cagr"], "mdd_1988": m88["mdd"], "g5_flag": g5_flag,
            **{f"d_{s[:4]}": per_start[s] for s in evo_data.START_DATES},
        }
        row["gauntlet_pass"] = bool(
            row["g1_pass"] and row["g2_pass"] and row["g3_pass"] and row["g4_pass"]
        )
        rows.append(row)
        print(
            f"{label}: cagr={m['cagr']:.4f} mdd={m['mdd']:.4f} | G1 {beats}/8 "
            f"G2 {g2} G3 {g3_cagr:.4f} G4 {g4:.2f} | 1988+ {m88['cagr']:.4f}/"
            f"{m88['mdd']:.4f} flag={g5_flag} | PASS={row['gauntlet_pass']}"
        )

    df = pd.DataFrame(rows)
    df.to_csv(evo_data.TABLES_DIR / "band_gauntlet.csv", index=False)
    print(f"\nfinalists: {int(df['gauntlet_pass'].sum())}/{len(df)}")


if __name__ == "__main__":
    main()
