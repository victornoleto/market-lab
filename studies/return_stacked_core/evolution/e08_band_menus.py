"""e08 — Round 6: 4-asset simplices under tolerance bands, full gauntlet.

Menus A (GDE/RSST/ZROZ/RSBT) and D (GDE/RSST/ZROZ/KMLM), 1,771 nodes each,
bands {15%, 20%, 25%} with the gauntlet at 20% (PLAN.md Round 6; gates
identical to Round 5, +G3 drag on the non-core sleeve). Vectorized band
engine from e07 `[systematic_trading, p.137-148]`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine
from studies.return_stacked_core.evolution.e05_bands import MAP88
from studies.return_stacked_core.evolution.e07_band_simplex import (
    band_simulate_matrix,
)

MENUS = {
    "A": ["GDESIM", "RSSTSIM", "ZROZSIM", "RSBTSIM"],
    "D": ["GDESIM", "RSSTSIM", "ZROZSIM", "KMLMSIM"],
}
BANDS = [0.15, 0.20, 0.25]
MAIN_BAND = 0.20
DRAG_DAILY = 0.0050 / 252
CORE_SLEEVES = {"GDESIM", "RSSTSIM", "ZROZSIM"}
CORE_W = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}


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

    all_rows = []
    for menu, assets in MENUS.items():
        vecs = evo_engine.generate_weight_vectors(4, step_pct=5)
        W = np.array(vecs, dtype=float) / 100.0
        idx_of = {v: i for i, v in enumerate(vecs)}
        rets = matrix[assets].dropna(how="any")

        met_band = {}
        for band in BANDS:
            eq = band_simulate_matrix(rets, W, band)
            met_band[band] = evo_engine.metrics_from_matrix(eq, rets.index)
        main_met = met_band[MAIN_BAND]
        eq_main = band_simulate_matrix(rets, W, MAIN_BAND)

        # G1 per start (vectorized per window).
        beats = np.zeros(len(vecs), dtype=int)
        for s, core_c in core_by_start.items():
            ssub = rets.loc[s:]
            ms = evo_engine.metrics_from_matrix(
                band_simulate_matrix(ssub, W, MAIN_BAND), ssub.index
            )
            beats += (ms["cagr"].to_numpy() > core_c).astype(int)

        # G3 stressed full-window (non-core sleeve −50bps/yr).
        stressed = rets.copy()
        for a in assets:
            if a not in CORE_SLEEVES:
                stressed[a] = stressed[a] - DRAG_DAILY
        met_stress = evo_engine.metrics_from_matrix(
            band_simulate_matrix(stressed, W, MAIN_BAND), rets.index
        )

        screen = (
            (main_met["mdd"].to_numpy() >= evo_data.MDD_CAP)
            & (main_met["cagr"].to_numpy() > evo_data.CORE_CAGR)
        )
        cagr20 = main_met["cagr"].to_numpy()
        mdd20 = main_met["mdd"].to_numpy()

        # G5 long-window (band sim on 1988+ proxies) for screen passers only.
        lw_assets = [MAP88.get(a, a) for a in assets]
        lsub = lw[lw_assets].dropna(how="any")
        idx_screen = np.where(screen)[0]
        if len(idx_screen):
            ml = evo_engine.metrics_from_matrix(
                band_simulate_matrix(lsub, W[idx_screen], MAIN_BAND), lsub.index
            )
            cagr88 = dict(zip(idx_screen, ml["cagr"]))
            mdd88 = dict(zip(idx_screen, ml["mdd"]))
        else:
            cagr88, mdd88 = {}, {}

        for k in idx_screen:
            v = vecs[k]
            # G2 same-band neighbors within the menu.
            nb_cagr, nb_mdd = [], []
            for i in range(4):
                if v[i] < 5:
                    continue
                for j in range(4):
                    if i == j:
                        continue
                    nb = list(v)
                    nb[i] -= 5
                    nb[j] += 5
                    kk = idx_of[tuple(nb)]
                    nb_cagr.append(cagr20[kk])
                    nb_mdd.append(mdd20[kk])
            g2 = (
                min(nb_mdd) >= -0.32
                and float(np.mean(nb_cagr)) > evo_data.CORE_CAGR
            )
            # G4 rolling for this node.
            roll = evo_engine.rolling_cagr(pd.Series(eq_main[:, k], index=rets.index))
            j = pd.concat([roll, core_roll], axis=1, keys=["c", "core"]).dropna()
            g4 = float((j["c"] > j["core"]).mean())
            # Band plateau.
            plateau = all(
                met_band[b]["mdd"].iloc[k] >= evo_data.MDD_CAP
                and met_band[b]["cagr"].iloc[k] > evo_data.CORE_CAGR
                for b in (0.15, 0.25)
            )
            g1 = int(beats[k]) >= 7
            g3 = met_stress["cagr"].iloc[k] > evo_data.CORE_CAGR
            finalist = bool(g1 and g2 and g3 and g4 >= 0.60 and plateau)
            all_rows.append(
                {
                    "menu": menu,
                    "node": "/".join(str(x) for x in v),
                    "cagr": cagr20[k], "mdd": mdd20[k],
                    "sharpe": main_met["sharpe"].iloc[k],
                    "g1_beats": int(beats[k]), "g2_pass": g2,
                    "g2_worst_nb_mdd": min(nb_mdd),
                    "g3_cagr_stressed": met_stress["cagr"].iloc[k],
                    "g4_share": g4, "band_plateau": plateau,
                    "cagr_1988": cagr88.get(k), "mdd_1988": mdd88.get(k),
                    "g5_flag": bool(
                        cagr88.get(k, 1) < core88["cagr"]
                        or mdd88.get(k, 0) < core88["mdd"] - 0.02
                    ),
                    "finalist": finalist,
                    "tier1_definitive": bool(finalist and cagr20[k] >= evo_data.C2_PRIMARY),
                }
            )
        print(f"menu {menu}: screen {len(idx_screen)}/{len(vecs)}")

    df = pd.DataFrame(all_rows)
    df.to_csv(evo_data.TABLES_DIR / "band_menus_4asset.csv", index=False)
    fin = df[df["finalist"]].sort_values("cagr", ascending=False)
    print(
        f"\nscreen total: {len(df)} | G1: {(df['g1_beats']>=7).sum()} | "
        f"G2: {int(df['g2_pass'].sum())} | G4: {(df['g4_share']>=0.6).sum()} | "
        f"plateau: {int(df['band_plateau'].sum())} | FINALISTS: {len(fin)} "
        f"| tier-1: {int(df['tier1_definitive'].sum())}"
    )
    cols = ["menu", "node", "cagr", "mdd", "sharpe", "g1_beats", "g2_pass",
            "g2_worst_nb_mdd", "g3_cagr_stressed", "g4_share", "band_plateau",
            "cagr_1988", "mdd_1988", "g5_flag", "tier1_definitive"]
    if len(fin):
        print(fin[cols].to_string(index=False))
    else:
        near = df[(df["g1_beats"] >= 7) & (df["g4_share"] >= 0.6) & df["band_plateau"]]
        print("\nnear (G1+G4+plateau, any G2):")
        print(near.sort_values("cagr", ascending=False).head(15)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
