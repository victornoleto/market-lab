"""e02 — robustness gauntlet on every C1∧C2' candidate (PLAN.md G1-G4).

G1 start-date sensitivity (8 starts, beat CORE CAGR in >=7/8)
G2 neighborhood plateau (all +-5pp one-step neighbors: MDD >= -32%,
   mean neighbor CAGR > CORE) `[testing_tuning, p.327-335]`
G3 drag stress (+50bps/yr on every sleeve not in the current core)
G4 rolling 5y dominance (beat CORE rolling CAGR in >= 60% of windows)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine
from studies.return_stacked_core.evolution.e01_grids import ALL_ASSETS, MENUS

DRAG_DAILY = 0.0050 / 252
NBHD_MDD_FLOOR = -0.32
CORE_SLEEVES = {"GDESIM", "RSSTSIM", "ZROZSIM"}


def parse_sig(sig: str) -> dict[str, int]:
    return {p.split(":")[0]: int(p.split(":")[1]) for p in sig.split("|")}


def weight_row(sig: str) -> np.ndarray:
    w = parse_sig(sig)
    return np.array([w.get(a, 0) / 100.0 for a in ALL_ASSETS], dtype=float)


def main() -> None:
    matrix = evo_data.load_primary_matrix()
    rets = matrix[ALL_ASSETS].dropna(how="any")
    cands = pd.read_csv(evo_data.TABLES_DIR / "candidates.csv")
    sigs = cands["sig"].tolist()
    W = np.vstack([weight_row(s) for s in sigs])
    core_sig = "GDESIM:35|RSSTSIM:40|ZROZSIM:25"
    Wall = np.vstack([W, weight_row(core_sig)])  # last row = CORE

    # ---- G1: start-date sensitivity -------------------------------------
    g1_beats = np.zeros(len(sigs), dtype=int)
    g1_detail = {}
    for start in evo_data.START_DATES:
        sub = rets.loc[start:]
        met = evo_engine.simulate_matrix_chunked(sub, Wall)
        core_cagr = met["cagr"].iloc[-1]
        beats = (met["cagr"].iloc[:-1].to_numpy() > core_cagr).astype(int)
        g1_beats += beats
        g1_detail[start] = core_cagr
    print("G1 core cagr per start:", {k: round(v, 4) for k, v in g1_detail.items()})

    # ---- G2: neighborhood plateau ---------------------------------------
    grid_lookup = {}
    for menu, (assets, _step) in MENUS.items():
        g = pd.read_csv(evo_data.TABLES_DIR / f"grid_{menu}.csv")
        key = g[[f"w_{a}" for a in assets]].astype(int).apply(tuple, axis=1)
        grid_lookup[menu] = dict(zip(key, zip(g["cagr"], g["mdd"])))

    g2_pass = []
    g2_nbhd_min_cagr = []
    for _, row in cands.iterrows():
        menu = row["menu"]
        assets, step = MENUS[menu]
        w = parse_sig(row["sig"])
        vec = tuple(int(w.get(a, 0)) for a in assets)
        nb_cagr, nb_mdd = [], []
        for i in range(len(assets)):
            if vec[i] < step:
                continue
            for j in range(len(assets)):
                if i == j:
                    continue
                nb = list(vec)
                nb[i] -= step
                nb[j] += step
                c, m = grid_lookup[menu][tuple(nb)]
                nb_cagr.append(c)
                nb_mdd.append(m)
        ok = (
            len(nb_cagr) > 0
            and min(nb_mdd) >= NBHD_MDD_FLOOR
            and float(np.mean(nb_cagr)) > evo_data.CORE_CAGR
        )
        g2_pass.append(ok)
        g2_nbhd_min_cagr.append(min(nb_cagr) if nb_cagr else np.nan)

    # ---- G3: drag stress -------------------------------------------------
    stressed = rets.copy()
    for a in ALL_ASSETS:
        if a not in CORE_SLEEVES:
            stressed[a] = stressed[a] - DRAG_DAILY
    met_stress = evo_engine.simulate_matrix_chunked(stressed, W)
    g3_pass = met_stress["cagr"].to_numpy() > evo_data.CORE_CAGR

    # ---- G4: rolling 5y dominance ----------------------------------------
    eq_all = evo_engine.simulate_matrix(rets, Wall)
    eq_index = rets.index
    core_eq = pd.Series(eq_all[:, -1], index=eq_index)
    core_roll = evo_engine.rolling_cagr(core_eq)
    g4_share = []
    for k in range(len(sigs)):
        cand_roll = evo_engine.rolling_cagr(pd.Series(eq_all[:, k], index=eq_index))
        joined = pd.concat([cand_roll, core_roll], axis=1, keys=["c", "core"]).dropna()
        g4_share.append(float((joined["c"] > joined["core"]).mean()))
    g4_share = np.array(g4_share)

    out = cands.copy()
    out["g1_beats"] = g1_beats
    out["g1_pass"] = g1_beats >= 7
    out["g2_pass"] = g2_pass
    out["g2_nbhd_min_cagr"] = g2_nbhd_min_cagr
    out["g3_cagr_stressed"] = met_stress["cagr"].to_numpy()
    out["g3_pass"] = g3_pass
    out["g4_share"] = g4_share
    out["g4_pass"] = g4_share >= 0.60
    out["gauntlet_pass"] = out[["g1_pass", "g2_pass", "g3_pass", "g4_pass"]].all(axis=1)
    out.to_csv(evo_data.TABLES_DIR / "gauntlet.csv", index=False)

    finalists = out[out["gauntlet_pass"]].sort_values("cagr", ascending=False)
    finalists.to_csv(evo_data.TABLES_DIR / "finalists.csv", index=False)
    print(f"\ncandidates: {len(out)} | pass G1: {out['g1_pass'].sum()} | "
          f"G2: {out['g2_pass'].sum()} | G3: {out['g3_pass'].sum()} | "
          f"G4: {out['g4_pass'].sum()} | ALL: {len(finalists)}")
    if len(finalists):
        cols = ["menu", "sig", "cagr", "mdd", "sharpe", "g1_beats", "g3_cagr_stressed", "g4_share"]
        print(finalists.head(25)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
