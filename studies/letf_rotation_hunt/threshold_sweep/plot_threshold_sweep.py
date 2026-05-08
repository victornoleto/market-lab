"""Plots for the threshold_sweep sub-study (spec §7).

Three plot functions:
  - plot_sharpe_bar: 12-bar Sharpe per variant + reference line.
  - plot_trade_count_bar: 12-bar trade count per variant.
  - plot_equity_overlay_top4: gross/M1/M2/SPY for top-4 by M1 Sharpe.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

LINEWIDTH = 1.4
COLOR_BAR_PASS = "#2ca02c"  # green
COLOR_BAR_FAIL = "#7f7f7f"  # grey
COLOR_BASELINE = "#1f77b4"  # blue
COLOR_REF = "#d62728"       # red dashed


def plot_sharpe_bar(
    df: pd.DataFrame,
    metric: str,
    reference: float,
    title: str,
    out_path: Path,
) -> None:
    """Bar chart of `metric` (Sharpe) per variant; bars above `reference` green, below grey.
    Baseline gets distinct blue color."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    names = df["name"].tolist()
    values = df[metric].values
    colors = []
    for name, v in zip(names, values):
        if name == "t3d_k2_baseline":
            colors.append(COLOR_BASELINE)
        elif v >= reference:
            colors.append(COLOR_BAR_PASS)
        else:
            colors.append(COLOR_BAR_FAIL)
    bars = ax.bar(range(len(names)), values, color=colors, edgecolor="black", linewidth=0.5)

    ax.axhline(reference, color=COLOR_REF, linestyle="--", linewidth=1.0,
               label=f"Threshold {reference:.3f}")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(title)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    # Value labels on top of bars
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{v:.3f}", ha="center", va="bottom", fontsize=7)

    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_trade_count_bar(df: pd.DataFrame, out_path: Path) -> None:
    """Bar chart of trade_count_m1 per variant. Lower is better (less whipsaw)."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    names = df["name"].tolist()
    values = df["trade_count_m1"].values
    baseline_row = df[df["name"] == "t3d_k2_baseline"]
    if len(baseline_row) > 0:
        baseline_count = float(baseline_row["trade_count_m1"].iloc[0])
        baseline_label = f"Baseline {int(baseline_count)} trades"
    else:
        baseline_count = float(pd.Series(values).median())
        baseline_label = f"Median {int(baseline_count)} trades"

    colors = []
    for name, v in zip(names, values):
        if name == "t3d_k2_baseline":
            colors.append(COLOR_BASELINE)
        elif v < baseline_count:
            colors.append(COLOR_BAR_PASS)  # fewer trades = better
        else:
            colors.append(COLOR_BAR_FAIL)

    bars = ax.bar(range(len(names)), values, color=colors, edgecolor="black", linewidth=0.5)
    ax.axhline(baseline_count, color=COLOR_REF, linestyle="--", linewidth=1.0,
               label=baseline_label)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Trade count (40-year backtest)")
    ax.set_title("Trade count per variant — lower = less whipsaw")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                f"{int(v)}", ha="center", va="bottom", fontsize=7)

    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_equity_overlay_top4(
    equity_curves: dict[str, dict[str, pd.Series]],
    spy_full: pd.Series,
    out_path: Path,
) -> None:
    """Overlay top-4 variants × {gross, M1, M2} + SPY buy-hold.

    `equity_curves[variant_name]` is a dict with keys 'gross', 'm1', 'm2'.
    """
    fig, ax = plt.subplots(figsize=(13, 6))
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for i, (name, curves) in enumerate(equity_curves.items()):
        color = palette[i % len(palette)]
        eq_gross = curves["gross"]
        eq_m1 = curves["m1"]
        ax.plot(eq_gross.index, eq_gross.values, color=color, linewidth=LINEWIDTH,
                label=f"{name} gross", alpha=0.95)
        ax.plot(eq_m1.index, eq_m1.values, color=color, linewidth=0.9,
                linestyle="--", label=f"{name} M1", alpha=0.7)

    # SPY buy-hold normalised to start at first variant equity
    if equity_curves:
        first_curve = next(iter(equity_curves.values()))["gross"]
        spy_aligned = spy_full.reindex(first_curve.index).ffill().dropna()
        if len(spy_aligned) > 0:
            spy_eq = 10_000.0 * (spy_aligned / spy_aligned.iloc[0])
            ax.plot(spy_eq.index, spy_eq.values, color="#7f7f7f",
                    linestyle=":", linewidth=1.2, label="SPY buy-hold")

    ax.set_yscale("log")
    ax.set_title("Top-4 variants by M1 Sharpe — gross (solid) vs M1 (dashed)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($, log scale, $10k seed)")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
