"""e07 — Round 5: full {GDE,RSST,ZROZ} simplex under band rebalancing.

231 nodes x bands {15%, 20%, 25%} through the complete gauntlet vs the
CORE-monthly benchmark (PLAN.md Round 5; gates G1-G4 + band plateau, G5
recorded). Band simulation vectorized across nodes: each node rebalances
to target when its OWN effective weights drift beyond the relative band
`[systematic_trading, p.137-148]`, `[testing_tuning, p.327-335]`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine
from studies.return_stacked_core.evolution.e05_bands import MAP88

ASSETS = ["GDESIM", "RSSTSIM", "ZROZSIM"]
BANDS = [0.15, 0.20, 0.25]
MAIN_BAND = 0.20
CORE_W = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}


def band_simulate_matrix(
    asset_returns: pd.DataFrame, weights: np.ndarray, band: float
) -> np.ndarray:
    """Equity (n_days, n_portfolios) under per-node band-triggered resets."""
    rets = asset_returns.dropna(how="any")
    r = rets.to_numpy(dtype=float)
    n_days = r.shape[0]
    n_pf = weights.shape[0]
    lo = weights * (1.0 - band)
    hi = weights * (1.0 + band)
    values = np.ones(n_pf, dtype=float)
    holdings = weights.copy()
    equity = np.empty((n_days, n_pf), dtype=float)
    for i in range(n_days):
        eff = holdings / values[:, None]
        trigger = ((eff < lo) | (eff > hi)).any(axis=1)
        if trigger.any():
            holdings[trigger] = weights[trigger] * values[trigger, None]
        holdings = holdings * (1.0 + r[i])
        values = holdings.sum(axis=1)
        equity[i] = values
    return equity


def main() -> None:
    matrix = evo_data.load_primary_matrix()
    rets = matrix[ASSETS]
    lw = evo_data.load_longwindow_matrix()
    lw_assets = [MAP88.get(a, a) for a in ASSETS]

    vecs = evo_engine.generate_weight_vectors(3, step_pct=5)
    W = np.array(vecs, dtype=float) / 100.0
    labels = [f"{v[0]}/{v[1]}/{v[2]}" for v in vecs]
    idx_of = {v: i for i, v in enumerate(vecs)}

    # CORE-monthly benchmarks.
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

    per_band: dict[float, pd.DataFrame] = {}
    for band in BANDS:
        sub = rets.dropna(how="any")
        eq = band_simulate_matrix(sub, W, band)
        met = evo_engine.metrics_from_matrix(eq, sub.index)
        met["node"] = labels
        met["band"] = band

        if band == MAIN_BAND:
            # G1 per start.
            beats = np.zeros(len(vecs), dtype=int)
            for s, core_c in core_by_start.items():
                ssub = rets.loc[s:].dropna(how="any")
                eqs = band_simulate_matrix(ssub, W, band)
                ms = evo_engine.metrics_from_matrix(eqs, ssub.index)
                beats += (ms["cagr"].to_numpy() > core_c).astype(int)
            met["g1_beats"] = beats
            # G4 rolling share.
            g4 = []
            for k in range(len(vecs)):
                roll = evo_engine.rolling_cagr(pd.Series(eq[:, k], index=sub.index))
                j = pd.concat([roll, core_roll], axis=1, keys=["c", "core"]).dropna()
                g4.append(float((j["c"] > j["core"]).mean()))
            met["g4_share"] = g4
            # G5 long-window.
            lsub = lw[lw_assets].dropna(how="any")
            eql = band_simulate_matrix(lsub, W, band)
            ml = evo_engine.metrics_from_matrix(eql, lsub.index)
            met["cagr_1988"] = ml["cagr"].to_numpy()
            met["mdd_1988"] = ml["mdd"].to_numpy()
        per_band[band] = met

    main_df = per_band[MAIN_BAND].set_index("node")
    aux15 = per_band[0.15].set_index("node")
    aux25 = per_band[0.25].set_index("node")

    rows = []
    for v in vecs:
        node = f"{v[0]}/{v[1]}/{v[2]}"
        m = main_df.loc[node]
        c1c2 = m["mdd"] >= evo_data.MDD_CAP and m["cagr"] > evo_data.CORE_CAGR
        # G2 neighbors at the same band.
        nb_cagr, nb_mdd = [], []
        for i in range(3):
            if v[i] < 5:
                continue
            for j in range(3):
                if i == j:
                    continue
                nb = list(v)
                nb[i] -= 5
                nb[j] += 5
                nrow = main_df.iloc[idx_of[tuple(nb)]]
                nb_cagr.append(nrow["cagr"])
                nb_mdd.append(nrow["mdd"])
        g2 = (
            len(nb_mdd) > 0
            and min(nb_mdd) >= -0.32
            and float(np.mean(nb_cagr)) > evo_data.CORE_CAGR
        )
        a15, a25 = aux15.loc[node], aux25.loc[node]
        band_plateau = (
            a15["mdd"] >= evo_data.MDD_CAP and a15["cagr"] > evo_data.CORE_CAGR
            and a25["mdd"] >= evo_data.MDD_CAP and a25["cagr"] > evo_data.CORE_CAGR
        )
        g1 = int(m["g1_beats"]) >= 7
        g4 = float(m["g4_share"]) >= 0.60
        finalist = bool(c1c2 and g1 and g2 and g4 and band_plateau)
        rows.append(
            {
                "node": node, "cagr": m["cagr"], "mdd": m["mdd"],
                "sharpe": m["sharpe"], "calmar": m["calmar"],
                "g1_beats": int(m["g1_beats"]), "g2_pass": g2,
                "g4_share": float(m["g4_share"]), "band_plateau": band_plateau,
                "cagr_b15": a15["cagr"], "mdd_b15": a15["mdd"],
                "cagr_b25": a25["cagr"], "mdd_b25": a25["mdd"],
                "cagr_1988": m["cagr_1988"], "mdd_1988": m["mdd_1988"],
                "g5_flag": bool(
                    m["cagr_1988"] < core88["cagr"]
                    or m["mdd_1988"] < core88["mdd"] - 0.02
                ),
                "screen_pass": bool(c1c2), "finalist": finalist,
                "tier1_definitive": bool(finalist and m["cagr"] >= evo_data.C2_PRIMARY),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(evo_data.TABLES_DIR / "band_simplex.csv", index=False)
    fin = df[df["finalist"]].sort_values("cagr", ascending=False)
    print(f"nodes: {len(df)} | screen: {int(df['screen_pass'].sum())} | "
          f"G1: {(df['g1_beats']>=7).sum()} | G2: {int(df['g2_pass'].sum())} | "
          f"G4: {(df['g4_share']>=0.6).sum()} | band-plateau: {int(df['band_plateau'].sum())} | "
          f"FINALISTS: {len(fin)} | tier-1: {int(df['tier1_definitive'].sum())}")
    cols = ["node", "cagr", "mdd", "sharpe", "g1_beats", "g4_share",
            "cagr_b15", "cagr_b25", "cagr_1988", "mdd_1988", "g5_flag",
            "tier1_definitive"]
    if len(fin):
        print(fin[cols].to_string(index=False))


if __name__ == "__main__":
    main()
