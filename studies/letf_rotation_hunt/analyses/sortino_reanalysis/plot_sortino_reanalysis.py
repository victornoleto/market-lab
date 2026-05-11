"""Plot module for sortino_reanalysis sub-study (spec §6).

Two plots:
  1. sortino_vs_sharpe_scatter — H0 visual + rank-change diagnostic.
  2. track_pass_comparison — 3-panel twin-bar (gross/M1/M2) edge comparison.

Downside-deviation rationale: Sortino (1991) penalises only negative deviations
below the target return, giving a more faithful picture of tail risk than symmetric
standard deviation [advances_fin_ml, p.275].
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


_GROUP_MARKER = {
    "A_spy_anchor": "^",
    "B_canonical": "o",
    "C_top10": "o",
    "D_regime_median": "D",
    "E_threshold_sweep": "s",
}
_TRACK_COLOR = {"gross": "#888888", "m1": "#1f77b4", "m2": "#2ca02c"}


def plot_sortino_vs_sharpe_scatter(df: pd.DataFrame, out_path: Path) -> Path:
    """Scatter Sharpe vs Sortino with reference y=x diagonal + Track A threshold lines.

    Points: lh_56y rows for groups A/B/C/E (D excluded — its metrics are 5y windows,
    not full-period). Color by track (gray/blue/green); shape by group.
    Annotations: canonical, smabuf_5pct, top-1 by sortino_edge_vs_canonical, SPY.

    Citation: downside-deviation Sortino ratio [advances_fin_ml, p.275].
    """
    plot_df = df[
        (df["dataset"] == "lh_56y")
        & (df["group"].isin(["A_spy_anchor", "B_canonical", "C_top10", "E_threshold_sweep"]))
    ].copy()

    fig, ax = plt.subplots(figsize=(12, 8))

    for (group, track), grp in plot_df.groupby(["group", "track"]):
        ax.scatter(
            grp["sharpe"], grp["sortino"],
            marker=_GROUP_MARKER.get(group, "x"),
            color=_TRACK_COLOR.get(track, "k"),
            s=80, alpha=0.7,
            label=f"{group} / {track}",
            edgecolors="black", linewidths=0.5,
        )

    # y = x diagonal
    lo = min(plot_df["sharpe"].min(), plot_df["sortino"].min()) * 0.9
    hi = max(plot_df["sharpe"].max(), plot_df["sortino"].max()) * 1.1
    ax.plot([lo, hi], [lo, hi], "k--", alpha=0.4, label="y = x")

    # Canonical & threshold reference lines
    canonical_lh = plot_df[
        (plot_df["group"] == "B_canonical") & (plot_df["track"] == "gross")
    ]
    if not canonical_lh.empty:
        c_sharpe = float(canonical_lh["sharpe"].iloc[0])
        c_sortino = float(canonical_lh["sortino"].iloc[0])
        ax.axvline(c_sharpe, color="red", linestyle=":", alpha=0.5, linewidth=1,
                   label=f"canonical Sharpe ({c_sharpe:.3f})")
        ax.axhline(c_sortino + 0.05, color="red", linestyle="--", alpha=0.5, linewidth=1,
                   label=f"Track A Sortino threshold ({c_sortino + 0.05:.3f})")

    # Annotations
    annotate_targets = ["qld_vote_k2_off_zroz", "t3d_k2_smabuf_5pct", "SPY"]
    for name in annotate_targets:
        sub = plot_df[(plot_df["strategy"] == name) & (plot_df["track"] == "gross")]
        if not sub.empty:
            row = sub.iloc[0]
            ax.annotate(
                name, xy=(row["sharpe"], row["sortino"]),
                xytext=(5, 5), textcoords="offset points", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7),
            )

    ax.set_xlabel("Sharpe ratio (annualised)")
    ax.set_ylabel("Sortino ratio (annualised, Sortino 1991, target=0)")
    ax.set_title("Sharpe vs Sortino — lh_56y, all groups")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


def plot_track_pass_comparison(df: pd.DataFrame, out_path: Path) -> Path:
    """3-panel horizontal bar chart: one panel per track (gross/M1/M2).

    Twin bars per strategy: Sharpe edge_vs_spy (left, blue) + Sortino edge_vs_spy
    (right, orange). Reference line at +0.05 (anti-curve-fit margin).

    Citation: downside-deviation Sortino ratio [advances_fin_ml, p.275].
    """
    target_strategies = (
        df[(df["group"].isin(["B_canonical", "C_top10", "E_threshold_sweep"]))]
        ["strategy"].drop_duplicates().tolist()
    )

    fig, axes = plt.subplots(1, 3, figsize=(18, max(8, 0.35 * len(target_strategies))), sharey=True)
    track_titles = {"gross": "Gross", "m1": "Net M1 (per-swing 15%)", "m2": "Net M2 (annual 15%)"}

    for ax, track in zip(axes, ["gross", "m1", "m2"]):
        sub = df[
            (df["dataset"] == "lh_56y")
            & (df["track"] == track)
            & (df["strategy"].isin(target_strategies))
        ].copy()
        sub = sub.sort_values("sortino_edge_vs_spy", ascending=True)
        if sub.empty:
            ax.set_title(f"{track_titles[track]} — no data")
            continue
        y = np.arange(len(sub))
        height = 0.4
        ax.barh(y - height / 2, sub["sharpe_edge_vs_spy"], height,
                color="#1f77b4", label="Sharpe edge")
        ax.barh(y + height / 2, sub["sortino_edge_vs_spy"], height,
                color="#ff7f0e", label="Sortino edge")
        ax.axvline(0.0, color="k", linewidth=0.5)
        ax.axvline(0.05, color="red", linestyle="--", linewidth=1, alpha=0.6,
                   label="+0.05 anti-curve-fit")
        ax.set_yticks(y)
        ax.set_yticklabels(sub["strategy"].tolist(), fontsize=8)
        ax.set_title(f"{track_titles[track]} — edge vs SPY")
        ax.set_xlabel("Edge (delta vs SPY)")
        ax.grid(axis="x", alpha=0.3)
        ax.legend(loc="lower right", fontsize=8)

    fig.suptitle("Track pass comparison — Sharpe edge vs Sortino edge by strategy", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path
