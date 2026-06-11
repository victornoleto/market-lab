#!/usr/bin/env python3
"""s04 — allocation simplex scan + plateau analysis for {GDE, RSST, ZROZ}.

231 nodes (5% grid), monthly rebalance, primary window. The output is a
DESCRIPTIVE MAP, not a selection: picking the argmax of 231 backtests would
be textbook selection bias `[advances_fin_ml, p.208-211, p.222-223]`. The
question answered is whether 35/40/25 sits on a robust plateau — parameter
plateaus beat peaks for live robustness `[testing_tuning, p.327-335]`.

Plateau methodology:
- neighbors(w) = nodes reachable by one 5pp transfer between two sleeves (≤6);
- robustness_gap = sharpe − min(neighbor sharpes) (small = flat neighborhood);
- plateau set = nodes with sharpe ≥ 0.95 × max(sharpe); contiguity checked by
  BFS over the neighbor graph from the argmax.

Start-date sensitivity: the grid re-run from 8 inception dates (2000..2014,
fixed end). Reported: argmax trajectory, plateau Jaccard overlap between
consecutive starts, CORE membership per start.

Outputs: ``tables/simplex_grid.csv``, ``tables/simplex_plateau.csv``,
``tables/simplex_start_sensitivity.csv``.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402
from studies.return_stacked_core.discussion import engine  # noqa: E402

ASSETS = ["GDESIM", "RSSTSIM", "ZROZSIM"]
CORE_NODE = (35, 40, 25)
PLATEAU_FRAC = 0.95
START_DATES = ["2000-01-04", "2002-01-02", "2004-01-02", "2006-01-03",
               "2008-01-02", "2010-01-04", "2012-01-03", "2014-01-02"]


def neighbors(node: tuple[int, int, int]) -> list[tuple[int, int, int]]:
    out = []
    n = len(node)
    for i in range(n):
        for j in range(n):
            if i == j or node[i] < 5:
                continue
            cand = list(node)
            cand[i] -= 5
            cand[j] += 5
            out.append(tuple(cand))
    return out


def grid_metrics(returns: pd.DataFrame, vectors: list[tuple[int, ...]]) -> pd.DataFrame:
    weights = np.array(vectors, dtype=float) / 100.0
    rets = returns[ASSETS].dropna(how="any")
    equity = engine.simulate_matrix(rets, weights)
    frame = engine.metrics_from_matrix(equity, rets.index)
    for k, asset in enumerate(ASSETS):
        frame.insert(k, asset.replace("SIM", "").lower() + "_pct",
                     [v[k] for v in vectors])
    frame.insert(0, "node", [f"{v[0]}/{v[1]}/{v[2]}" for v in vectors])
    return frame


def plateau_stats(frame: pd.DataFrame, vectors: list[tuple[int, ...]]) -> tuple[pd.DataFrame, dict]:
    by_node = {v: i for i, v in enumerate(vectors)}
    sharpe = frame["sharpe"].to_numpy()
    max_sharpe = float(sharpe.max())
    threshold = PLATEAU_FRAC * max_sharpe

    nbhd_min, nbhd_mean = [], []
    for v in vectors:
        ns = [sharpe[by_node[n]] for n in neighbors(v) if n in by_node]
        nbhd_min.append(min(ns) if ns else np.nan)
        nbhd_mean.append(float(np.mean(ns)) if ns else np.nan)
    out = frame.copy()
    out["nbhd_min_sharpe"] = nbhd_min
    out["nbhd_mean_sharpe"] = nbhd_mean
    out["robustness_gap"] = out["sharpe"] - out["nbhd_min_sharpe"]
    out["in_plateau"] = out["sharpe"] >= threshold

    plateau_nodes = {v for v, keep in zip(vectors, out["in_plateau"]) if keep}
    argmax_node = vectors[int(np.argmax(sharpe))]

    # Contiguity: BFS from argmax across plateau members.
    seen = {argmax_node}
    queue = [argmax_node]
    while queue:
        cur = queue.pop()
        for n in neighbors(cur):
            if n in plateau_nodes and n not in seen:
                seen.add(n)
                queue.append(n)
    contiguous = len(seen) == len(plateau_nodes)

    summary = {
        "max_sharpe": max_sharpe,
        "argmax_node": "/".join(map(str, argmax_node)),
        "plateau_threshold": threshold,
        "plateau_size": len(plateau_nodes),
        "plateau_contiguous": contiguous,
        "core_in_plateau": CORE_NODE in plateau_nodes,
        "core_sharpe": float(sharpe[by_node[CORE_NODE]]),
        "core_sharpe_pctile": float((sharpe <= sharpe[by_node[CORE_NODE]]).mean()),
    }
    return out, summary


def main() -> int:
    primary = pd.read_parquet(dd.SERIES_DIR / "primary_returns.parquet")
    vectors = [tuple(v) for v in engine.generate_weight_vectors(3, 5)]
    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    frame = grid_metrics(primary, vectors)
    detailed, summary = plateau_stats(frame, vectors)
    detailed.to_csv(dd.TABLES_DIR / "simplex_grid.csv", index=False)

    top_maximin = (
        detailed.sort_values("nbhd_min_sharpe", ascending=False)
        .head(10)[["node", "sharpe", "nbhd_min_sharpe", "robustness_gap", "in_plateau"]]
    )
    top_maximin.to_csv(dd.TABLES_DIR / "simplex_plateau.csv", index=False)

    print("full-window:", {k: (round(v, 4) if isinstance(v, float) else v)
                           for k, v in summary.items()})

    # Start-date sensitivity.
    rows = []
    prev_plateau: set | None = None
    for start in START_DATES:
        sub = primary.loc[start:]
        f = grid_metrics(sub, vectors)
        det, summ = plateau_stats(f, vectors)
        plateau = set(det.loc[det["in_plateau"], "node"])
        jaccard = (
            len(plateau & prev_plateau) / len(plateau | prev_plateau)
            if prev_plateau is not None
            else np.nan
        )
        rows.append(
            {
                "start": start,
                "argmax_node": summ["argmax_node"],
                "max_sharpe": summ["max_sharpe"],
                "plateau_size": summ["plateau_size"],
                "plateau_contiguous": summ["plateau_contiguous"],
                "core_in_plateau": summ["core_in_plateau"],
                "core_sharpe": summ["core_sharpe"],
                "core_sharpe_pctile": summ["core_sharpe_pctile"],
                "jaccard_vs_prev_start": jaccard,
            }
        )
        prev_plateau = plateau
    sens = pd.DataFrame(rows)
    sens.to_csv(dd.TABLES_DIR / "simplex_start_sensitivity.csv", index=False)
    print(sens[["start", "argmax_node", "plateau_size", "core_in_plateau",
                "jaccard_vs_prev_start"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
