"""e09 — Round 6 final extension: 5-asset simplices under bands (menus F, H).

GDE/RSST/ZROZ/RSBT/GLD and GDE/RSST/ZROZ/GLD/KMLM, 10,626 nodes each,
gauntlet at band 20% with plateau screens at 15/25 (PLAN.md Round 6 final
extension; gates unchanged). These simplices contain the untested
{GDE,RSST,ZROZ,GLD} face — GLD is the only sleeve that is both a late-start
CAGR driver and a crisis asset, the combination the G1×G2 squeeze demands.
After this, the band route is closed for good.
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
    "F": ["GDESIM", "RSSTSIM", "ZROZSIM", "RSBTSIM", "GLDSIM"],
    "H": ["GDESIM", "RSSTSIM", "ZROZSIM", "GLDSIM", "KMLMSIM"],
}
BANDS = [0.15, 0.20, 0.25]
MAIN_BAND = 0.20
DRAG_DAILY = 0.0050 / 252
CORE_SLEEVES = {"GDESIM", "RSSTSIM", "ZROZSIM"}
CORE_W = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}
CHUNK = 3000


def band_metrics_chunked(
    rets: pd.DataFrame, W: np.ndarray, band: float
) -> pd.DataFrame:
    frames = []
    sub = rets.dropna(how="any")
    for lo in range(0, W.shape[0], CHUNK):
        eq = band_simulate_matrix(sub, W[lo : lo + CHUNK], band)
        frames.append(evo_engine.metrics_from_matrix(eq, sub.index))
    return pd.concat(frames, ignore_index=True)


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
        vecs = evo_engine.generate_weight_vectors(5, step_pct=5)
        W = np.array(vecs, dtype=float) / 100.0
        idx_of = {v: i for i, v in enumerate(vecs)}
        rets = matrix[assets].dropna(how="any")

        met_band = {b: band_metrics_chunked(rets, W, b) for b in BANDS}
        main_met = met_band[MAIN_BAND]
        cagr20 = main_met["cagr"].to_numpy()
        mdd20 = main_met["mdd"].to_numpy()

        beats = np.zeros(len(vecs), dtype=int)
        for s, core_c in core_by_start.items():
            ssub = rets.loc[s:]
            ms = band_metrics_chunked(ssub, W, MAIN_BAND)
            beats += (ms["cagr"].to_numpy() > core_c).astype(int)

        stressed = rets.copy()
        for a in assets:
            if a not in CORE_SLEEVES:
                stressed[a] = stressed[a] - DRAG_DAILY
        met_stress = band_metrics_chunked(stressed, W, MAIN_BAND)

        screen = (mdd20 >= evo_data.MDD_CAP) & (cagr20 > evo_data.CORE_CAGR)
        idx_screen = np.where(screen)[0]
        print(f"menu {menu}: screen {len(idx_screen)}/{len(vecs)}, "
              f"G1>=7: {int(((beats >= 7) & screen).sum())}")

        lw_assets = [MAP88.get(a, a) for a in assets]
        lsub = lw[lw_assets].dropna(how="any")
        if len(idx_screen):
            ml = evo_engine.metrics_from_matrix(
                band_simulate_matrix(lsub, W[idx_screen], MAIN_BAND), lsub.index
            )
            cagr88 = dict(zip(idx_screen, ml["cagr"]))
            mdd88 = dict(zip(idx_screen, ml["mdd"]))
        else:
            cagr88, mdd88 = {}, {}

        sub = rets.dropna(how="any")
        for k in idx_screen:
            v = vecs[k]
            nb_cagr, nb_mdd = [], []
            for i in range(5):
                if v[i] < 5:
                    continue
                for j in range(5):
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
            g1 = int(beats[k]) >= 7
            g3 = met_stress["cagr"].iloc[k] > evo_data.CORE_CAGR
            plateau = all(
                met_band[b]["mdd"].iloc[k] >= evo_data.MDD_CAP
                and met_band[b]["cagr"].iloc[k] > evo_data.CORE_CAGR
                for b in (0.15, 0.25)
            )
            # G4 only where the cheap gates allow a finalist.
            if g1 and g2 and g3 and plateau:
                eqk = band_simulate_matrix(sub, W[k : k + 1], MAIN_BAND)[:, 0]
                roll = evo_engine.rolling_cagr(pd.Series(eqk, index=sub.index))
                j = pd.concat([roll, core_roll], axis=1, keys=["c", "core"]).dropna()
                g4 = float((j["c"] > j["core"]).mean())
            else:
                g4 = np.nan
            finalist = bool(g1 and g2 and g3 and plateau and g4 >= 0.60)
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

    df = pd.DataFrame(all_rows)
    df.to_csv(evo_data.TABLES_DIR / "band_menus_5asset.csv", index=False)
    fin = df[df["finalist"]].sort_values("cagr", ascending=False)
    print(
        f"\nscreen total: {len(df)} | G1: {(df['g1_beats']>=7).sum()} | "
        f"G2: {int(df['g2_pass'].sum())} | G1&G2: "
        f"{int(((df['g1_beats']>=7) & df['g2_pass']).sum())} | "
        f"FINALISTS: {len(fin)} | tier-1: {int(df['tier1_definitive'].sum())}"
    )
    cols = ["menu", "node", "cagr", "mdd", "sharpe", "g1_beats", "g2_pass",
            "g2_worst_nb_mdd", "g3_cagr_stressed", "g4_share", "band_plateau",
            "cagr_1988", "mdd_1988", "g5_flag", "tier1_definitive"]
    if len(fin):
        print(fin[cols].to_string(index=False))
    else:
        near = df[(df["g1_beats"] >= 7) & df["band_plateau"]]
        print("\nnear (G1+plateau, any G2):")
        print(near.sort_values("cagr", ascending=False).head(15)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
