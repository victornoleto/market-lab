#!/usr/bin/env python3
"""g04 — 5-asset global allocation simplex {GDE, NTSD, RSST, RSIT, ZROZ}.

10,626 nodes (5% grid, C(24,4)), monthly rebalance. Same descriptive-map
discipline as s04: no argmax selection `[advances_fin_ml, p.208-211,
p.222-223]`; plateau-over-peak `[testing_tuning, p.327-335]`.

Runs on two windows:
- primary 2000+ (MFBLEND sleeves) — full grid + 8 start dates;
- 1988+ canonical (KMLM-only sleeves) — full grid once, regime robustness.

Simulation is chunked (2,048 portfolios per chunk) to keep the
(days × portfolios) equity matrices under ~250 MB.

Outputs: ``tables/global_simplex_grid.csv`` (primary),
``tables/global_simplex_grid_1988.csv``, ``tables/global_simplex_plateau.csv``
(maximin top-10 + plateau weight ranges), ``tables/global_simplex_start_sensitivity.csv``.
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
from studies.return_stacked_core.discussion.s04_simplex import neighbors  # noqa: E402

ASSETS_PRIMARY = ["GDESIM", "NTSDSIM", "RSSTSIM", "RSITSIM", "ZROZSIM"]
ASSETS_1988 = ["GDESIM", "NTSDSIM", "RSST_KM", "RSIT_KM", "ZROZSIM"]
SLEEVE_LABELS = ["gde", "ntsd", "rsst", "rsit", "zroz"]
CORE_NODE = (20, 15, 20, 20, 25)
PLATEAU_FRAC = 0.95
CHUNK = 2048
START_DATES = ["2000-01-04", "2002-01-02", "2004-01-02", "2006-01-03",
               "2008-01-02", "2010-01-04", "2012-01-03", "2014-01-02"]


def grid_metrics(returns: pd.DataFrame, assets: list[str],
                 vectors: list[tuple[int, ...]]) -> pd.DataFrame:
    rets = returns[assets].dropna(how="any")
    weights = np.array(vectors, dtype=float) / 100.0
    frames = []
    for lo in range(0, len(vectors), CHUNK):
        w = weights[lo : lo + CHUNK]
        equity = engine.simulate_matrix(rets, w)
        frames.append(engine.metrics_from_matrix(equity, rets.index))
    frame = pd.concat(frames, ignore_index=True)
    for k, label in enumerate(SLEEVE_LABELS):
        frame.insert(k, f"{label}_pct", [v[k] for v in vectors])
    frame.insert(0, "node", ["/".join(map(str, v)) for v in vectors])
    return frame


def plateau_summary(frame: pd.DataFrame, vectors: list[tuple[int, ...]]) -> tuple[pd.DataFrame, dict]:
    by_node = {v: i for i, v in enumerate(vectors)}
    sharpe = frame["sharpe"].to_numpy()
    max_sharpe = float(sharpe.max())
    threshold = PLATEAU_FRAC * max_sharpe

    nbhd_min = np.full(len(vectors), np.nan)
    for i, v in enumerate(vectors):
        ns = [sharpe[by_node[n]] for n in neighbors(v) if n in by_node]
        if ns:
            nbhd_min[i] = min(ns)
    out = frame.copy()
    out["nbhd_min_sharpe"] = nbhd_min
    out["robustness_gap"] = out["sharpe"] - out["nbhd_min_sharpe"]
    out["in_plateau"] = out["sharpe"] >= threshold

    plateau_nodes = {v for v, keep in zip(vectors, out["in_plateau"]) if keep}
    argmax_node = vectors[int(np.argmax(sharpe))]
    seen, queue = {argmax_node}, [argmax_node]
    while queue:
        cur = queue.pop()
        for n in neighbors(cur):
            if n in plateau_nodes and n not in seen:
                seen.add(n)
                queue.append(n)

    plateau_arr = np.array(sorted(plateau_nodes), dtype=int)
    weight_ranges = {
        label: (int(plateau_arr[:, k].min()), int(plateau_arr[:, k].max()))
        for k, label in enumerate(SLEEVE_LABELS)
    } if len(plateau_arr) else {}

    summary = {
        "max_sharpe": max_sharpe,
        "argmax_node": "/".join(map(str, argmax_node)),
        "plateau_size": len(plateau_nodes),
        "plateau_contiguous": len(seen) == len(plateau_nodes),
        "core_in_plateau": CORE_NODE in plateau_nodes,
        "core_sharpe": float(sharpe[by_node[CORE_NODE]]),
        "core_sharpe_pctile": float((sharpe <= sharpe[by_node[CORE_NODE]]).mean()),
        "plateau_weight_ranges": weight_ranges,
    }
    return out, summary


def main() -> int:
    vectors = [tuple(v) for v in engine.generate_weight_vectors(5, 5)]
    print(f"grid: {len(vectors)} nodes")
    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    primary = pd.read_parquet(dd.SERIES_DIR / "global_primary_returns.parquet")
    frame = grid_metrics(primary, ASSETS_PRIMARY, vectors)
    detailed, summary = plateau_summary(frame, vectors)
    detailed.to_csv(dd.TABLES_DIR / "global_simplex_grid.csv", index=False)
    print("primary 2000+:", {k: v for k, v in summary.items()})

    g88 = pd.read_parquet(dd.SERIES_DIR / "global_1988_returns.parquet")
    frame88 = grid_metrics(g88, ASSETS_1988, vectors)
    detailed88, summary88 = plateau_summary(frame88, vectors)
    detailed88.to_csv(dd.TABLES_DIR / "global_simplex_grid_1988.csv", index=False)
    print("1988+ (KMLM-only):", {k: v for k, v in summary88.items()})

    top = detailed.sort_values("nbhd_min_sharpe", ascending=False).head(10)
    ranges_rows = [
        {"window": w, "sleeve": s, "plateau_min_pct": lo, "plateau_max_pct": hi}
        for w, summ in (("primary", summary), ("1988", summary88))
        for s, (lo, hi) in summ["plateau_weight_ranges"].items()
    ]
    pd.concat(
        [top[["node", "sharpe", "nbhd_min_sharpe", "robustness_gap", "in_plateau"]],
         pd.DataFrame(ranges_rows)],
        axis=0,
    ).to_csv(dd.TABLES_DIR / "global_simplex_plateau.csv", index=False)

    # Globalness price curve: best node subject to a minimum international
    # allocation (NTSD+RSIT). Answers "what does structural intl exposure
    # cost?" without selecting any single node as optimal.
    price_rows = []
    for window, det in (("primary", detailed), ("1988", detailed88)):
        intl = det["ntsd_pct"] + det["rsit_pct"]
        for floor in range(0, 55, 5):
            sub = det[intl >= floor]
            best = sub.loc[sub["sharpe"].idxmax()]
            price_rows.append({
                "window": window, "intl_floor_pct": floor, "best_node": best["node"],
                "sharpe": best["sharpe"], "cagr": best["cagr"], "mdd": best["mdd"],
                "sharpe_cost_vs_unconstrained": best["sharpe"] - det["sharpe"].max(),
            })
    pd.DataFrame(price_rows).to_csv(
        dd.TABLES_DIR / "global_intl_price_curve.csv", index=False
    )

    rows = []
    prev: set | None = None
    for start in START_DATES:
        f = grid_metrics(primary.loc[start:], ASSETS_PRIMARY, vectors)
        det, summ = plateau_summary(f, vectors)
        plateau = set(det.loc[det["in_plateau"], "node"])
        jaccard = len(plateau & prev) / len(plateau | prev) if prev is not None else np.nan
        rows.append({
            "start": start, "argmax_node": summ["argmax_node"],
            "max_sharpe": summ["max_sharpe"], "plateau_size": summ["plateau_size"],
            "plateau_contiguous": summ["plateau_contiguous"],
            "core_in_plateau": summ["core_in_plateau"],
            "core_sharpe": summ["core_sharpe"],
            "core_sharpe_pctile": summ["core_sharpe_pctile"],
            "jaccard_vs_prev_start": jaccard,
        })
        prev = plateau
    sens = pd.DataFrame(rows)
    sens.to_csv(dd.TABLES_DIR / "global_simplex_start_sensitivity.csv", index=False)
    print(sens[["start", "argmax_node", "plateau_size", "core_in_plateau",
                "jaccard_vs_prev_start"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
