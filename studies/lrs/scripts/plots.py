"""Plot helpers specific to the lrs scoring framework.

Three plots that visualise the output of :mod:`studies.lrs.scripts.scoring`
and sweep runs:

* :func:`plot_score_timeline` — for each window length, a panel showing
  the per-window score across the dataset, both tax scenarios overlaid,
  with a zero reference line. Lets you see *when* a strategy is winning
  or losing vs the benchmark.

* :func:`plot_score_by_length` — box / strip plot of all window scores by
  window length and tax scenario. Shows distribution shape, outliers and
  whether tax materially shifts the score.

* :func:`plot_sweep_heatmap` — for a (on_leg × tax_scenario) panel, a grid
  of heatmaps (one per risk-off asset) showing ``final_score`` as a
  function of ``(filter, lookback)``. Used by phase-1 sweep runs.

All plots follow the lrs PNG conventions: headless backend, clear external
legend, ≤300KB typical output.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")  # headless

import matplotlib.pyplot as plt
import numpy as np

from studies.lrs.scripts.scoring import ScoreReport, WindowScore

# Stable colour map per strategy (kept consistent across both plots).
STRATEGY_COLORS: dict[str, str] = {
    "B&H SPY":  "#7f7f7f",
    "B&H SSO":  "#16a34a",
    "B&H UPRO": "#d62728",
    "LRS-SSO":  "#0066ff",
    "LRS-UPRO": "#ff8c00",
}

SCENARIO_STYLES: dict[str, dict[str, object]] = {
    "tax_free":      {"linestyle": "-",  "alpha": 0.85, "linewidth": 1.4},
    "br_lei_14754":  {"linestyle": "--", "alpha": 0.85, "linewidth": 1.4},
}


def _group_by_strategy(reports: Iterable[ScoreReport]) -> dict[str, dict[str, ScoreReport]]:
    grouped: dict[str, dict[str, ScoreReport]] = defaultdict(dict)
    for r in reports:
        grouped[r.strategy_name][r.tax_scenario] = r
    return dict(grouped)


def plot_score_timeline(
    reports: Iterable[ScoreReport],
    out_path: Path,
    *,
    window_years: tuple[int, ...] = (1, 3, 5, 10, 15, 20),
    title: str = "studies/lrs — score per rolling window over time",
) -> None:
    """Grid of panels, one per window length, score-over-time per strategy.

    Tax-free and BR-Lei-14754 scenarios are overlaid (solid vs dashed) so
    you can see when the tax bites. A zero reference line marks the
    benchmark.
    """
    grouped = _group_by_strategy(reports)

    n_panels = len(window_years)
    n_cols = 2
    n_rows = (n_panels + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(13, 2.4 * n_rows), sharex=False, sharey=True)
    axes = np.atleast_2d(axes).flatten()

    for ax, years in zip(axes, window_years):
        ax.axhline(0.0, color="black", linewidth=0.8, alpha=0.6, zorder=1)
        for strat_name, scenarios in grouped.items():
            colour = STRATEGY_COLORS.get(strat_name, "#444444")
            for scenario, rep in scenarios.items():
                style = SCENARIO_STYLES.get(scenario, {})
                # Pull this length's windows out of the report.
                pts = [w for w in rep.windows if w.length_years == years]
                if not pts:
                    continue
                pts.sort(key=lambda w: w.start_date)
                xs = [w.start_date for w in pts]
                ys = [w.score for w in pts]
                ax.plot(xs, ys, color=colour, label=f"{strat_name} · {scenario}", **style)
        ax.set_title(f"{years}y window")
        ax.set_ylabel("score")
        ax.grid(True, which="major", linestyle="-", linewidth=0.3, alpha=0.4)

    # Hide unused subplots if any.
    for ax in axes[n_panels:]:
        ax.set_visible(False)

    # One shared legend below the grid (avoid duplicates).
    handles, labels = axes[0].get_legend_handles_labels()
    seen: set[str] = set()
    unique = [(h, l) for h, l in zip(handles, labels) if not (l in seen or seen.add(l))]
    if unique:
        fig.legend(
            [h for h, _ in unique],
            [l for _, l in unique],
            loc="lower center",
            ncol=min(5, len(unique)),
            fontsize=8,
            framealpha=0.85,
            bbox_to_anchor=(0.5, -0.02),
        )

    fig.suptitle(title, fontsize=11)
    fig.tight_layout(rect=(0.0, 0.04, 1.0, 0.97))
    fig.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def plot_score_by_length(
    reports: Iterable[ScoreReport],
    out_path: Path,
    *,
    window_years: tuple[int, ...] = (1, 3, 5, 10, 15, 20),
    title: str = "studies/lrs — window-score distribution by length and tax scenario",
) -> None:
    """Box plot of window scores grouped by (window length, tax scenario).

    Each strategy gets one row in the legend. Two boxes per window length
    (tax-free, taxed) per strategy. Useful for spotting which tax scenario
    each strategy is sensitive to.
    """
    grouped = _group_by_strategy(reports)
    strategies = list(grouped.keys())

    fig, axes = plt.subplots(1, len(window_years), figsize=(2.4 * len(window_years), 5.0),
                             sharey=True)
    axes = np.atleast_1d(axes)

    box_width = 0.7 / max(1, len(strategies) * 2)
    for ax, years in zip(axes, window_years):
        ax.axhline(0.0, color="black", linewidth=0.8, alpha=0.6, zorder=1)
        positions: list[float] = []
        data: list[list[float]] = []
        colours: list[str] = []
        labels: list[str] = []
        for i, strat_name in enumerate(strategies):
            for j, scenario in enumerate(("tax_free", "br_lei_14754")):
                rep = grouped.get(strat_name, {}).get(scenario)
                if rep is None:
                    continue
                ws: list[WindowScore] = [w for w in rep.windows if w.length_years == years]
                if not ws:
                    continue
                positions.append(i + (j - 0.5) * box_width * 2)
                data.append([w.score for w in ws])
                colours.append(STRATEGY_COLORS.get(strat_name, "#444444"))
                labels.append(f"{strat_name} · {scenario}")
        if data:
            bp = ax.boxplot(
                data,
                positions=positions,
                widths=box_width * 1.6,
                patch_artist=True,
                showfliers=False,
            )
            for patch, c, scen_label in zip(bp["boxes"], colours, labels):
                patch.set_facecolor(c)
                patch.set_alpha(0.45 if scen_label.endswith("br_lei_14754") else 0.85)
                patch.set_edgecolor(c)
            for med in bp["medians"]:
                med.set_color("black")
                med.set_linewidth(1.0)
        ax.set_title(f"{years}y")
        ax.set_xticks(range(len(strategies)))
        ax.set_xticklabels(strategies, rotation=30, ha="right", fontsize=8)
        ax.grid(True, axis="y", linewidth=0.3, alpha=0.4)

    axes[0].set_ylabel("window score")
    fig.suptitle(title, fontsize=11)

    # Legend: one entry per (strategy, scenario) pair, deduped.
    legend_handles = []
    seen: set[str] = set()
    for strat_name in strategies:
        colour = STRATEGY_COLORS.get(strat_name, "#444444")
        for scenario, alpha in (("tax_free", 0.85), ("br_lei_14754", 0.45)):
            label = f"{strat_name} · {scenario}"
            if label in seen:
                continue
            seen.add(label)
            legend_handles.append(
                plt.Rectangle((0, 0), 1, 1, facecolor=colour, alpha=alpha, edgecolor=colour, label=label)
            )
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=min(5, len(legend_handles)),
        fontsize=7,
        framealpha=0.85,
        bbox_to_anchor=(0.5, -0.08),
    )

    fig.tight_layout(rect=(0.0, 0.08, 1.0, 0.95))
    fig.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def plot_sweep_heatmap(
    sweep_df: "pd.DataFrame",
    out_path: Path,
    *,
    on_leg: str,
    tax_scenario: str,
    risk_offs: tuple[str, ...] = ("CASH", "GLD", "IEF", "ZROZ"),
    filters: tuple[str, ...] = ("SMA", "EMA"),
    title: str | None = None,
    vmin: float = -0.35,
    vmax: float = +0.35,
) -> None:
    """Render the 4-risk-off heatmap panel for one (on_leg, tax_scenario) cell.

    Layout: 4 horizontal subplots, one per risk-off asset. Each subplot is a
    ``filter (2 rows) × lookback (cols)`` heatmap coloured by ``final_score``.

    Parameters
    ----------
    sweep_df : pd.DataFrame
        Must have columns ``filter``, ``lookback``, ``on_leg``, ``risk_off``,
        ``tax_scenario``, ``final_score``.
    out_path : Path
        Output PNG.
    on_leg, tax_scenario : str
        The cell of the sweep to plot (filters ``sweep_df``).
    risk_offs : tuple[str, ...]
        Column order (left-to-right subplots).
    filters : tuple[str, ...]
        Row order (top-to-bottom in each subplot).
    title : str, optional
        Overall figure title. Defaults to a descriptive one.
    vmin, vmax : float
        Colour scale. Symmetric around zero by default so blue/red split
        on benchmark-tie.
    """
    import pandas as pd

    sub = sweep_df[
        (sweep_df["on_leg"] == on_leg) & (sweep_df["tax_scenario"] == tax_scenario)
    ]
    if sub.empty:
        return

    fig, axes = plt.subplots(1, len(risk_offs), figsize=(3.4 * len(risk_offs), 2.6), sharey=True)
    axes = np.atleast_1d(axes)

    # Determine common lookback axis.
    lookbacks = sorted(sub["lookback"].unique())

    cmap = plt.get_cmap("RdBu")  # red=negative, white=zero, blue=positive
    for ax, risk_off in zip(axes, risk_offs):
        cell = sub[sub["risk_off"] == risk_off]
        if cell.empty:
            ax.set_title(f"{risk_off}\n(no data)")
            ax.axis("off")
            continue
        grid = (
            cell.pivot(index="filter", columns="lookback", values="final_score")
                .reindex(filters)
                .reindex(columns=lookbacks)
        )
        im = ax.imshow(
            grid.values,
            aspect="auto",
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            interpolation="nearest",
        )
        ax.set_title(f"off-leg: {risk_off}")
        ax.set_yticks(range(len(filters)))
        ax.set_yticklabels(filters)
        # Lookback x-ticks: show every 10th value to avoid clutter.
        n_lb = len(lookbacks)
        tick_idx = list(range(0, n_lb, max(1, n_lb // 8)))
        ax.set_xticks(tick_idx)
        ax.set_xticklabels([str(lookbacks[i]) for i in tick_idx], fontsize=8, rotation=0)
        ax.set_xlabel("lookback (days)")

        # Mark the cell of the single best config in this risk-off panel.
        best_idx = cell["final_score"].idxmax()
        best = cell.loc[best_idx]
        try:
            row = filters.index(best["filter"])
            col = lookbacks.index(best["lookback"])
            ax.plot(col, row, marker="*", color="black", markersize=10,
                    markeredgecolor="white", markeredgewidth=0.6)
            ax.text(col, row + 0.32,
                    f"{best['final_score']:+.3f}",
                    color="black", fontsize=7, ha="center", va="top",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7))
        except (ValueError, KeyError):
            pass

    # Colorbar on the right side of the figure.
    cbar = fig.colorbar(im, ax=axes, orientation="vertical", fraction=0.02, pad=0.02)
    cbar.set_label("final_score", fontsize=9)

    if title is None:
        title = f"studies/lrs phase-1 — {on_leg} on-leg, {tax_scenario} scenario"
    fig.suptitle(title, fontsize=11)

    fig.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)
