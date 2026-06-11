"""e01 — simplex grids over the pre-registered menus (PLAN.md).

5%-step long-only weight vectors, monthly rebalance, primary window.
Writes per-menu tables + a deduped candidate list (C1: MDD >= -30%,
C2': CAGR > CORE). Selection discipline: candidates only enter the verdict
via the e02 gauntlet, never as raw argmax `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine

ALL_ASSETS = ["GDESIM", "RSSTSIM", "ZROZSIM", "RSBTSIM", "RSSBSIM", "GLDSIM", "KMLMSIM", "QQQSIM"]

# menu -> (assets, step_pct). H/I are the pre-registered Round 2 amendment.
MENUS = {
    "A": (["GDESIM", "RSSTSIM", "ZROZSIM", "RSBTSIM"], 5),
    "B": (["GDESIM", "RSSTSIM", "ZROZSIM", "GLDSIM"], 5),
    "C": (["GDESIM", "RSSTSIM", "ZROZSIM", "QQQSIM"], 5),
    "D": (["GDESIM", "RSSTSIM", "ZROZSIM", "KMLMSIM"], 5),
    "E": (["GDESIM", "RSSTSIM", "ZROZSIM", "RSSBSIM"], 5),
    "F": (["GDESIM", "RSSTSIM", "ZROZSIM", "RSBTSIM", "GLDSIM"], 5),
    "G": (["GDESIM", "RSSTSIM", "ZROZSIM", "RSBTSIM", "QQQSIM"], 5),
    "H": (["GDESIM", "RSSTSIM", "ZROZSIM", "GLDSIM", "KMLMSIM"], 5),
    "I": (ALL_ASSETS, 10),
}


def signature(assets: list[str], vec: tuple[int, ...]) -> str:
    """Menu-independent weight signature over the full asset universe."""
    w = dict(zip(assets, vec))
    return "|".join(f"{a}:{w.get(a, 0)}" for a in ALL_ASSETS if w.get(a, 0) > 0)


def main() -> None:
    matrix = evo_data.load_primary_matrix()
    evo_data.TABLES_DIR.mkdir(exist_ok=True)
    n_trials = 0
    all_rows = []
    for menu, (assets, step) in MENUS.items():
        vecs = evo_engine.generate_weight_vectors(len(assets), step_pct=step)
        weights = np.array(vecs, dtype=float) / 100.0
        rets = matrix[assets]
        met = evo_engine.simulate_matrix_chunked(rets, weights)
        for i, a in enumerate(assets):
            met[f"w_{a}"] = [v[i] for v in vecs]
        met["menu"] = menu
        met["sig"] = [signature(assets, v) for v in vecs]
        met.to_csv(evo_data.TABLES_DIR / f"grid_{menu}.csv", index=False)
        n_trials += len(met)
        all_rows.append(met)
        top_cap = met[met["mdd"] >= evo_data.MDD_CAP].sort_values("cagr", ascending=False)
        best = top_cap.iloc[0] if len(top_cap) else None
        print(
            f"menu {menu} ({'/'.join(a.replace('SIM','') for a in assets)}): "
            f"{len(met)} nodes, {len(top_cap)} in cap, "
            + (
                f"best in-cap cagr={best['cagr']:.4f} mdd={best['mdd']:.4f} sig={best['sig']}"
                if best is not None
                else "none in cap"
            )
        )

    full = pd.concat(all_rows, ignore_index=True)
    dedup = full.sort_values("menu").drop_duplicates(subset="sig", keep="first")
    cands = dedup[
        (dedup["mdd"] >= evo_data.MDD_CAP) & (dedup["cagr"] > evo_data.CORE_CAGR)
    ].sort_values("cagr", ascending=False)
    cands.to_csv(evo_data.TABLES_DIR / "candidates.csv", index=False)
    with open(evo_data.TABLES_DIR / "n_trials.txt", "w") as fh:
        fh.write(f"raw={n_trials}\ndeduped={len(dedup)}\ncandidates={len(cands)}\n")
    print(f"\nn_trials raw={n_trials} deduped={len(dedup)}")
    print(f"candidates (C1 & C2'): {len(cands)}, of which C2 primary (cagr>={evo_data.C2_PRIMARY:.4f}): "
          f"{(cands['cagr'] >= evo_data.C2_PRIMARY).sum()}")
    print(cands.head(20)[["menu", "sig", "cagr", "mdd", "sharpe", "calmar"]].to_string(index=False))


if __name__ == "__main__":
    main()
