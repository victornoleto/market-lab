"""Plot helpers specific to the lrs scoring framework.

Two plots that visualise the output of :mod:`studies.lrs.scripts.scoring`:

* :func:`plot_score_timeline` — for each window length, a panel showing
  the per-window score across the dataset, both tax scenarios overlaid,
  with a zero reference line. Lets you see *when* a strategy is winning
  or losing vs the benchmark.

* :func:`plot_score_by_length` — box / strip plot of all window scores by
  window length and tax scenario. Shows distribution shape, outliers and
  whether tax materially shifts the score.

Both plots follow the lrs PNG conventions: headless backend, ≤200KB output,
clear external legend.
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
