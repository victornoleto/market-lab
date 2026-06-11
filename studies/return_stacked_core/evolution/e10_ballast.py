"""e10 — Round 7: plain-ballast sleeves (IEF, CASHX) — monthly AND band-20.

Coverage gap closure (PLAN.md Round 7): IEFSIM/CASHX were never menu
assets in Rounds 1-6. Both rebalance modes go through the full gauntlet vs
CORE-monthly. Ballast-form diversification rationale: the G2 breaches all
trace to the 2022-form regime (GDE and ZROZ falling together); IEF/cash are
the rate-shock-proof ballast forms `[risk_parity, ch.5]`.
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
    "P": ["GDESIM", "RSSTSIM", "ZROZSIM", "IEFSIM"],
    "Q": ["GDESIM", "RSSTSIM", "ZROZSIM", "CASHX"],
    "R": ["GDESIM", "RSSTSIM", "ZROZSIM", "IEFSIM", "GLDSIM"],
}
BANDS = [0.15, 0.20, 0.25]
MAIN_BAND = 0.20
DRAG_DAILY = 0.0050 / 252
NO_DRAG = {"GDESIM", "RSSTSIM", "ZROZSIM", "CASHX"}
CORE_W = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}
CHUNK = 3000


def metrics_for(rets: pd.DataFrame, W: np.ndarray, mode: str, band: float) -> pd.DataFrame:
    sub = rets.dropna(how="any")
    frames = []
    for lo in range(0, W.shape[0], CHUNK):
        w = W[lo : lo + CHUNK]
        if mode == "monthly":
            eq = evo_engine.simulate_matrix(sub, w)
        else:
            eq = band_simulate_matrix(sub, w, band)
        frames.append(evo_engine.metrics_from_matrix(eq, sub.index))
    return pd.concat(frames, ignore_index=True)


def node_equity(rets: pd.DataFrame, w: np.ndarray, mode: str, band: float) -> pd.Series:
    sub = rets.dropna(how="any")
    if mode == "monthly":
        eq = evo_engine.simulate_matrix(sub, w[None, :])
    else:
        eq = band_simulate_matrix(sub, w[None, :], band)
    return pd.Series(eq[:, 0], index=sub.index)


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
        n = len(assets)
        vecs = evo_engine.generate_weight_vectors(n, step_pct=5)
        W = np.array(vecs, dtype=float) / 100.0
        idx_of = {v: i for i, v in enumerate(vecs)}
        rets = matrix[assets].dropna(how="any")
        lw_assets = [MAP88.get(a, a) for a in assets]
        lsub = lw[lw_assets].dropna(how="any")

        for mode in ("monthly", "band"):
            met = metrics_for(rets, W, mode, MAIN_BAND)
            cagr_m = met["cagr"].to_numpy()
            mdd_m = met["mdd"].to_numpy()
            screen = (mdd_m >= evo_data.MDD_CAP) & (cagr_m > evo_data.CORE_CAGR)
            idx_screen = np.where(screen)[0]

            beats = np.zeros(len(vecs), dtype=int)
            for s, core_c in core_by_start.items():
                ms = metrics_for(rets.loc[s:], W, mode, MAIN_BAND)
                beats += (ms["cagr"].to_numpy() > core_c).astype(int)

            stressed = rets.copy()
            for a in assets:
                if a not in NO_DRAG:
                    stressed[a] = stressed[a] - DRAG_DAILY
            met_stress = metrics_for(stressed, W, mode, MAIN_BAND)

            if mode == "band":
                met15 = metrics_for(rets, W, mode, 0.15)
                met25 = metrics_for(rets, W, mode, 0.25)

            if len(idx_screen):
                if mode == "monthly":
                    eql = evo_engine.simulate_matrix(lsub, W[idx_screen])
                else:
                    eql = band_simulate_matrix(lsub, W[idx_screen], MAIN_BAND)
                ml = evo_engine.metrics_from_matrix(eql, lsub.index)
                cagr88 = dict(zip(idx_screen, ml["cagr"]))
                mdd88 = dict(zip(idx_screen, ml["mdd"]))
            else:
                cagr88, mdd88 = {}, {}

            n_fin = 0
            for k in idx_screen:
                v = vecs[k]
                nb_cagr, nb_mdd = [], []
                for i in range(n):
                    if v[i] < 5:
                        continue
                    for j in range(n):
                        if i == j:
                            continue
                        nb = list(v)
                        nb[i] -= 5
                        nb[j] += 5
                        kk = idx_of[tuple(nb)]
                        nb_cagr.append(cagr_m[kk])
                        nb_mdd.append(mdd_m[kk])
                g2 = (
                    min(nb_mdd) >= -0.32
                    and float(np.mean(nb_cagr)) > evo_data.CORE_CAGR
                )
                g1 = int(beats[k]) >= 7
                g3 = met_stress["cagr"].iloc[k] > evo_data.CORE_CAGR
                if mode == "band":
                    plateau = all(
                        m["mdd"].iloc[k] >= evo_data.MDD_CAP
                        and m["cagr"].iloc[k] > evo_data.CORE_CAGR
                        for m in (met15, met25)
                    )
                else:
                    plateau = True  # n/a for monthly
                if g1 and g2 and g3 and plateau:
                    eqk = node_equity(rets, W[k], mode, MAIN_BAND)
                    roll = evo_engine.rolling_cagr(eqk)
                    j = pd.concat(
                        [roll, core_roll], axis=1, keys=["c", "core"]
                    ).dropna()
                    g4 = float((j["c"] > j["core"]).mean())
                else:
                    g4 = np.nan
                finalist = bool(g1 and g2 and g3 and plateau and g4 >= 0.60)
                n_fin += int(finalist)
                all_rows.append(
                    {
                        "menu": menu, "mode": mode,
                        "node": "/".join(str(x) for x in v),
                        "cagr": cagr_m[k], "mdd": mdd_m[k],
                        "sharpe": met["sharpe"].iloc[k],
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
                        "tier1_definitive": bool(
                            finalist and cagr_m[k] >= evo_data.C2_PRIMARY
                        ),
                    }
                )
            print(f"menu {menu} {mode}: screen {len(idx_screen)}/{len(vecs)}, "
                  f"G1>=7 in screen: {int(((beats >= 7) & screen).sum())}, "
                  f"finalists: {n_fin}")

    df = pd.DataFrame(all_rows)
    df.to_csv(evo_data.TABLES_DIR / "ballast_menus.csv", index=False)
    fin = df[df["finalist"]].sort_values("cagr", ascending=False)
    print(
        f"\nscreen total: {len(df)} | G1&G2: "
        f"{int(((df['g1_beats']>=7) & df['g2_pass']).sum())} | "
        f"FINALISTS: {len(fin)} | tier-1: {int(df['tier1_definitive'].sum())}"
    )
    cols = ["menu", "mode", "node", "cagr", "mdd", "sharpe", "g1_beats",
            "g2_pass", "g2_worst_nb_mdd", "g3_cagr_stressed", "g4_share",
            "cagr_1988", "mdd_1988", "g5_flag", "tier1_definitive"]
    if len(fin):
        print(fin[cols].head(30).to_string(index=False))
    else:
        near = df[(df["g1_beats"] >= 7)]
        print("\nnear (G1>=7, any G2):")
        print(near.sort_values("cagr", ascending=False).head(15)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
