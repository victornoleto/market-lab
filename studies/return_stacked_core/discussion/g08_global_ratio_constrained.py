#!/usr/bin/env python3
"""g08 — best global mix under a fixed US/intl equity ratio (60/40 and 66/34).

User-chartered constraint: hold the look-through equity geography at 60/40 or
66/34 US/international (the sleeves are developed-ex-US only, so 66/34 mirrors
the world ex-EM ratio). This is a CONSTRAINED descriptive map over the saved
10,626-node grids — the ratio band is a policy choice, the scan only shows the
best shapes inside it `[advances_fin_ml, p.208-211]`, `[testing_tuning,
p.327-335]`.

Look-through equity per $1 of sleeve (repo proxy formulas):

    GDE  0.90 US            NTSD 0.90 US + 0.60 intl
    RSST 1.00 US            RSIT 1.00 intl          ZROZ none

us_share = US / (US + intl); band = target ± 2.5pp. Nodes with zero equity are
excluded.

Outputs:
- ``tables/global_ratio_constrained.csv`` — top-10 by Sharpe per
  (window × target) with exposures + in_plateau flag, plus extended-window
  (1970+) metrics for the primary-window top-3 of each target.
- ``tables/global_ratio_constrained_starts.csv`` — per-start best in-band node
  (primary window, 8 starts) — argmax stability under the constraint.
- ``figures/g10_ratio_constrained_frontier.png`` — the 66/34 band slice.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import pandas as pd  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402
from studies.return_stacked_core.discussion import engine  # noqa: E402
from studies.return_stacked_core.discussion.g04_global_simplex import (  # noqa: E402
    ASSETS_PRIMARY, START_DATES, grid_metrics,
)
from studies.return_stacked_core.discussion.s07_figures import C, FIGSIZE, _save  # noqa: E402

TARGETS = {"60/40": 0.60, "66/34": 0.66}
BAND_PP = 0.025
KMLM_INCEPTION = pd.Timestamp("1987-12-31")


def add_exposures(grid: pd.DataFrame) -> pd.DataFrame:
    g = grid.copy()
    w = {c: g[f"{c}_pct"] / 100.0 for c in ("gde", "ntsd", "rsst", "rsit", "zroz")}
    g["us_eq"] = 0.90 * w["gde"] + 0.90 * w["ntsd"] + 1.00 * w["rsst"]
    g["intl_eq"] = 0.60 * w["ntsd"] + 1.00 * w["rsit"]
    total = g["us_eq"] + g["intl_eq"]
    g = g[total > 0].copy()
    g["us_share"] = g["us_eq"] / total
    g["total_eq"] = total
    return g


def in_band(g: pd.DataFrame, target: float) -> pd.DataFrame:
    return g[(g["us_share"] - target).abs() <= BAND_PP]


def extended_metrics_for(node: str) -> dict | None:
    """1970+ LOW-fidelity metrics for a grid node (haircut MF sleeves)."""
    path = dd.SERIES_DIR / "global_extended_returns.parquet"
    if not path.exists():
        return None
    ext = pd.read_parquet(path)
    cash = ext["CASHX"]
    drag = dd.FINANCING_SPREAD_ANNUAL / dd.TRADING_DAYS
    kmlm = ext["KMLM_SPLICED"]
    pre = ext.index < KMLM_INCEPTION
    kmlm_hc = kmlm.copy()
    kmlm_hc[pre] = cash[pre] + 0.5 * (kmlm[pre] - cash[pre])
    ext = ext.copy()
    ext["RSST_HC"] = ext["SPYSIM"] + kmlm_hc - (cash + drag)
    ext["RSIT_HC"] = ext["VXUSSIM"] + kmlm_hc - (cash + drag)
    pct = [float(x) for x in node.split("/")]
    weights = dict(zip(
        ["GDESIM", "NTSDSIM", "RSST_HC", "RSIT_HC", "ZROZSIM"],
        [x / 100.0 for x in pct],
    ))
    weights = {k: v for k, v in weights.items() if v > 0}
    m = engine.compute_metrics(engine.rebalanced_equity(ext, weights))
    return {"ext_cagr": m["cagr"], "ext_mdd": m["mdd"], "ext_sharpe": m["sharpe"]}


def main() -> int:
    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    grids = {
        "primary": add_exposures(pd.read_csv(dd.TABLES_DIR / "global_simplex_grid.csv")),
        "1988": add_exposures(pd.read_csv(dd.TABLES_DIR / "global_simplex_grid_1988.csv")),
    }

    rows = []
    for window, g in grids.items():
        for label, target in TARGETS.items():
            band = in_band(g, target).sort_values("sharpe", ascending=False)
            top = band.head(10)
            for rank, (_, r) in enumerate(top.iterrows(), 1):
                row = {
                    "window": window, "target": label, "rank": rank,
                    "node": r["node"], "us_share": r["us_share"],
                    "total_equity": r["total_eq"],
                    "cagr": r["cagr"], "mdd": r["mdd"], "sharpe": r["sharpe"],
                    "in_unconstrained_plateau": bool(r["in_plateau"]),
                    "n_in_band": len(band),
                }
                if window == "primary" and rank <= 3:
                    ext = extended_metrics_for(r["node"])
                    if ext:
                        row.update(ext)
                rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(dd.TABLES_DIR / "global_ratio_constrained.csv", index=False)

    # CORE-GLOBAL reference inside the 66/34 band.
    core = grids["primary"][grids["primary"]["node"] == "20/15/20/20/25"].iloc[0]
    print(f"CORE-GLOBAL us_share={core['us_share']:.1%} "
          f"(in 66/34 band: {abs(core['us_share'] - 0.66) <= BAND_PP})")
    for (window, target), sub in out.groupby(["window", "target"]):
        b = sub.iloc[0]
        print(f"{window} {target}: n_in_band={b['n_in_band']:.0f} best {b['node']} "
              f"Sharpe {b['sharpe']:.3f} CAGR {b['cagr']:.2%} MDD {b['mdd']:.2%}")

    # Start-date stability of the constrained best (primary window).
    primary_returns = pd.read_parquet(dd.SERIES_DIR / "global_primary_returns.parquet")
    vectors = [tuple(v) for v in engine.generate_weight_vectors(5, 5)]
    start_rows = []
    for start in START_DATES:
        f = add_exposures(grid_metrics(primary_returns.loc[start:], ASSETS_PRIMARY, vectors))
        for label, target in TARGETS.items():
            band = in_band(f, target)
            best = band.loc[band["sharpe"].idxmax()]
            core_row = f[f["node"] == "20/15/20/20/25"]
            core_sharpe = float(core_row["sharpe"].iloc[0]) if not core_row.empty else float("nan")
            band_sorted = band.sort_values("sharpe", ascending=False)
            core_rank = (
                int((band_sorted["node"] == "20/15/20/20/25").to_numpy().argmax()) + 1
                if "20/15/20/20/25" in set(band["node"]) else -1
            )
            start_rows.append({
                "start": start, "target": label, "best_node": best["node"],
                "best_sharpe": best["sharpe"], "core_global_sharpe": core_sharpe,
                "core_global_rank_in_band": core_rank, "n_in_band": len(band),
            })
    starts = pd.DataFrame(start_rows)
    starts.to_csv(dd.TABLES_DIR / "global_ratio_constrained_starts.csv", index=False)
    print(starts[starts["target"] == "66/34"][
        ["start", "best_node", "best_sharpe", "core_global_rank_in_band"]
    ].to_string(index=False))

    # Figure: the 66/34 band slice (primary window).
    band = in_band(grids["primary"], 0.66)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sc = ax.scatter(band["mdd"].abs(), band["cagr"], c=band["zroz_pct"],
                    cmap="plasma", s=30, alpha=0.9)
    best = band.loc[band["sharpe"].idxmax()]
    ax.scatter([abs(best["mdd"])], [best["cagr"]], marker="D", s=130,
               color=C["orange"], edgecolor="#000", zorder=5,
               label=f"best in band: {best['node']} (Sharpe {best['sharpe']:.3f})")
    ax.scatter([abs(core["mdd"])], [core["cagr"]], marker="*", s=420,
               color=C["secondary"], edgecolor="#000", zorder=5,
               label=f"CORE-GLOBAL 20/15/20/20/25 (Sharpe {core['sharpe']:.3f})")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("max drawdown (absolute)")
    ax.set_ylabel("CAGR")
    ax.grid(alpha=0.25)
    fig.colorbar(sc, ax=ax, label="ZROZ weight (%)")
    ax.legend(loc="lower right")
    ax.set_title(f"All {len(band)} mixes with 66/34 (+-2.5pp) US/intl equity, "
                 "2000-2026 (simulated)")
    _save(fig, "g10_ratio_constrained_frontier.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
