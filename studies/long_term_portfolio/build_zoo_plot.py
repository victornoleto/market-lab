"""Build comprehensive Pareto comparison plot for STRATEGY_ZOO.md.

Reads all iters/0??-*/verdict.json + scoring.BENCHMARKS, produces a 3-panel
scatter (Sharpe vs CAGR per dataset, marker size = inverse-MDD, colored
by tier) plus a horizontal-bar tier ranking.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from studies.long_term_portfolio.scoring import BENCHMARKS, avg_benchmark


LOOP = REPO_ROOT / "studies" / "long_term_portfolio"
ITERS = sorted((LOOP / "iterations").glob("0??-*"))
PLOTS_DIR = LOOP / "plots_zoo"
PLOTS_DIR.mkdir(exist_ok=True)

DATASETS = ["lh_56y", "vt_real", "ndx_real"]
DATASET_LABELS = {"lh_56y": "lh_56y (1986-2026, 40y eff)", "vt_real": "vt_real (2008-2026, ~17y)", "ndx_real": "ndx_real (2010-2026, ~16y)"}

TIER_COLORS = {
    "WINNER":    "#1f77b4",   # blue
    "STRONG":    "#2ca02c",   # green
    "PROMISING": "#ff7f0e",   # orange
    "MARGINAL":  "#d62728",   # red
    "FAIL":      "#7f7f7f",   # gray
}

# iter 022 is a known model artifact — flag as invalid
INVALID_ITERS = {"022"}


def load_all_iters() -> list[dict]:
    rows = []
    for iter_dir in ITERS:
        verdict_file = iter_dir / "verdict.json"
        if not verdict_file.exists():
            continue
        v = json.loads(verdict_file.read_text())
        iter_num = iter_dir.name.split("-")[0]
        slug = v.get("hypothesis_slug", "?")
        score = v.get("total_score", 0)
        tier = v.get("tier", "?")
        winner_met = v.get("winner_conditions_met", False)
        metrics = v.get("metrics_used", {})
        # iters 001-011 use legacy 'educational' key for lh_56y window (same dataset, renamed)
        def get_ds_metric(ds_key):
            m = metrics.get(ds_key)
            if m is not None:
                return m
            if ds_key == "lh_56y":
                return metrics.get("educational", {})
            return {}

        rows.append({
            "iter":   iter_num,
            "slug":   slug,
            "score":  score,
            "tier":   tier,
            "winner": winner_met,
            "valid":  iter_num not in INVALID_ITERS,
            "metrics": {ds: {"sharpe": get_ds_metric(ds).get("sharpe"), "cagr": get_ds_metric(ds).get("cagr"), "mdd": get_ds_metric(ds).get("mdd")} for ds in DATASETS},
        })
    return rows


def plot_pareto_3panel(rows: list[dict]) -> Path:
    """3-panel scatter: Sharpe (y) vs CAGR (x) per dataset, marker size inv-MDD, color by tier."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Strategy Zoo — Pareto Frontier (Sharpe vs CAGR per dataset)", fontsize=14, fontweight="bold")

    for ax, ds in zip(axes, DATASETS):
        bm = avg_benchmark(BENCHMARKS[ds])
        # Plot benchmark first so it's behind
        ax.scatter([bm.cagr], [bm.sharpe], marker="*", s=400, c="black", edgecolors="white", linewidths=1.5, label=f"avg(SPY,VT) bench", zorder=5)
        ax.annotate(f"avg(SPY,VT)\n{bm.sharpe:.2f} / {bm.cagr:.0%} / {bm.mdd:.0%}", (bm.cagr, bm.sharpe), xytext=(10, 5), textcoords="offset points", fontsize=8, fontweight="bold")

        for r in rows:
            m = r["metrics"][ds]
            if m["sharpe"] is None or m["cagr"] is None:
                continue
            color = TIER_COLORS.get(r["tier"], "#7f7f7f")
            # Invalid iters: red x marker
            if not r["valid"]:
                ax.scatter(m["cagr"], m["sharpe"], marker="x", s=200, c="red", linewidths=2, label=f"iter {r['iter']} (⚠️ artifact)", zorder=4)
                ax.annotate(f"⚠️ {r['iter']}", (m["cagr"], m["sharpe"]), xytext=(8, -3), textcoords="offset points", fontsize=8, color="red", fontweight="bold")
                continue
            # Valid iters: marker size proportional to 1/MDD (smaller MDD = bigger marker)
            # Scale: MDD 10% → 400, MDD 50% → 80
            size = max(50, min(400, 8000 / (max(m["mdd"], 0.01) * 100)))
            edge = "gold" if r["winner"] else "black"
            edge_w = 2 if r["winner"] else 0.5
            ax.scatter(m["cagr"], m["sharpe"], s=size, c=color, alpha=0.7, edgecolors=edge, linewidths=edge_w, zorder=3)
            ax.annotate(r["iter"], (m["cagr"], m["sharpe"]), xytext=(0, 0), textcoords="offset points", fontsize=7, ha="center", va="center", fontweight="bold")

        # Reference lines
        ax.axhline(bm.sharpe, color="gray", linestyle=":", linewidth=0.8, alpha=0.5)
        ax.axhline(bm.sharpe + 0.10, color="green", linestyle="--", linewidth=0.8, alpha=0.5, label="bench + 0.10 (winner gate)")
        ax.set_xlabel("CAGR (gross)")
        ax.set_ylabel("Sharpe (gross)")
        ax.set_title(DATASET_LABELS[ds])
        ax.grid(True, alpha=0.3)
        ax.set_xlim(left=0.05)

    # Build legend (only on first panel for tiers)
    handles = [
        plt.scatter([], [], marker="*", s=200, c="black", label="avg(SPY,VT) benchmark"),
        plt.scatter([], [], s=150, c=TIER_COLORS["WINNER"], edgecolors="gold", linewidths=2, label="WINNER tier (winner_conds met)"),
        plt.scatter([], [], s=150, c=TIER_COLORS["WINNER"], edgecolors="black", linewidths=0.5, label="WINNER tier (no winner conds)"),
        plt.scatter([], [], s=150, c=TIER_COLORS["STRONG"], edgecolors="black", linewidths=0.5, label="STRONG tier"),
        plt.scatter([], [], s=150, c=TIER_COLORS["PROMISING"], edgecolors="black", linewidths=0.5, label="PROMISING tier"),
        plt.scatter([], [], s=150, c=TIER_COLORS["MARGINAL"], edgecolors="black", linewidths=0.5, label="MARGINAL tier"),
        plt.scatter([], [], marker="x", s=150, c="red", linewidths=2, label="⚠️ Invalid (model artifact)"),
        plt.Line2D([], [], linestyle="--", color="green", label="bench + 0.10 (winner Sharpe gate)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.03), fontsize=8, frameon=False)
    fig.text(0.5, 0.91, "Marker size proportional to 1/MDD (bigger = lower MDD). Gold edge = WINNER tier conditions met.", ha="center", fontsize=9, fontstyle="italic", color="#444")

    plt.tight_layout()
    plt.subplots_adjust(top=0.85, bottom=0.12)
    out = PLOTS_DIR / "pareto_3panel.png"
    plt.savefig(out, dpi=130, bbox_inches="tight")
    plt.close()
    return out


def plot_score_ranking(rows: list[dict]) -> Path:
    """Horizontal bar of all iters by score, colored by tier."""
    rows_sorted = sorted(rows, key=lambda r: r["score"])
    iters = [r["iter"] for r in rows_sorted]
    slugs = [r["slug"][:40] for r in rows_sorted]
    scores = [r["score"] for r in rows_sorted]
    colors = [TIER_COLORS.get(r["tier"], "#7f7f7f") if r["valid"] else "#ff0000" for r in rows_sorted]
    edges = ["gold" if r["winner"] and r["valid"] else "black" for r in rows_sorted]

    fig, ax = plt.subplots(figsize=(12, 9))
    y = np.arange(len(iters))
    bars = ax.barh(y, scores, color=colors, edgecolor=edges, linewidth=1.3)

    for i, (it, s) in enumerate(zip(iters, scores)):
        suffix = ""
        if not rows_sorted[i]["valid"]:
            suffix = " ⚠️ ARTIFACT"
        ax.text(s + 1, i, f"{s}{suffix}", va="center", fontsize=8)

    ax.set_yticks(y)
    ax.set_yticklabels([f"{it}: {sl}" for it, sl in zip(iters, slugs)], fontsize=8)
    ax.set_xlabel("Score / 100")
    ax.set_title("Strategy Zoo — All 22 iterations, ranked by score", fontsize=13, fontweight="bold")
    ax.axvline(60, color="orange", linestyle=":", linewidth=0.8, alpha=0.5, label="PROMISING threshold (60)")
    ax.axvline(75, color="green", linestyle=":", linewidth=0.8, alpha=0.5, label="STRONG threshold (75)")
    ax.axvline(90, color="blue", linestyle=":", linewidth=0.8, alpha=0.5, label="WINNER tier threshold (90)")
    ax.set_xlim(0, 110)
    ax.grid(True, axis="x", alpha=0.3)
    ax.legend(loc="lower right", fontsize=9)

    plt.tight_layout()
    out = PLOTS_DIR / "score_ranking.png"
    plt.savefig(out, dpi=130, bbox_inches="tight")
    plt.close()
    return out


def plot_metric_heatmap(rows: list[dict]) -> Path:
    """Heatmap: each iter (row) × dataset (col) showing Sharpe color-coded."""
    rows_sorted = sorted(rows, key=lambda r: -r["score"])
    n = len(rows_sorted)
    sharpe_grid = np.array([[r["metrics"][ds]["sharpe"] or np.nan for ds in DATASETS] for r in rows_sorted])
    cagr_grid = np.array([[r["metrics"][ds]["cagr"] or np.nan for ds in DATASETS] for r in rows_sorted])
    mdd_grid = np.array([[r["metrics"][ds]["mdd"] or np.nan for ds in DATASETS] for r in rows_sorted])

    fig, axes = plt.subplots(1, 3, figsize=(14, max(6, n * 0.35)))

    for ax, grid, title, fmt, vmin, vmax in [
        (axes[0], sharpe_grid, "Sharpe", "{:.2f}", 0.4, 1.6),
        (axes[1], cagr_grid * 100, "CAGR (%)", "{:.1f}", 5, 20),
        (axes[2], mdd_grid * 100, "MaxDD (%)", "{:.1f}", 5, 50),
    ]:
        cmap = "RdYlGn" if title != "MaxDD (%)" else "RdYlGn_r"
        im = ax.imshow(grid, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_xticks(range(len(DATASETS)))
        ax.set_xticklabels(DATASETS, fontsize=9)
        ax.set_yticks(range(n))
        if ax is axes[0]:
            yt = []
            for r in rows_sorted:
                tag = " ⚠️" if not r["valid"] else (" 🏆" if r["winner"] else "")
                yt.append(f"{r['iter']} ({r['score']}){tag}")
            ax.set_yticklabels(yt, fontsize=8)
        else:
            ax.set_yticklabels([])
        ax.set_title(title, fontsize=11)
        for i in range(n):
            for j in range(len(DATASETS)):
                v = grid[i, j]
                if np.isfinite(v):
                    ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=7, color="black")
        plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

    fig.suptitle("Strategy Zoo — gross metrics per iter × dataset (sorted by score desc)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    out = PLOTS_DIR / "metrics_heatmap.png"
    plt.savefig(out, dpi=130, bbox_inches="tight")
    plt.close()
    return out


def main():
    rows = load_all_iters()
    print(f"Loaded {len(rows)} iters")

    p1 = plot_pareto_3panel(rows)
    print(f"Pareto 3-panel: {p1}")

    p2 = plot_score_ranking(rows)
    print(f"Score ranking: {p2}")

    p3 = plot_metric_heatmap(rows)
    print(f"Metrics heatmap: {p3}")

    # Also dump structured JSON for STRATEGY_ZOO.md
    out_json = LOOP / "plots_zoo" / "all_iters_data.json"
    out_json.write_text(json.dumps(rows, indent=2, default=str))
    print(f"Data JSON: {out_json}")


if __name__ == "__main__":
    main()
