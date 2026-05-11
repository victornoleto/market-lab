"""Forward Sharpe heatmap (entry month × horizon) per spec §5.

Reuses `data/robustness/all_windows.parquet` rather than re-running backtests.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_forward_heatmap(
    df: pd.DataFrame,
    config_name: str,
    out_path: Path,
    spy_anchor: float = 0.682,
    annotate_cohort_dates: list[str] | None = None,
) -> None:
    """Plot heatmap: X = entry month, Y = horizon (window_size_y), color = Sharpe.

    `df` must have columns: config, window_size_y, start_date, sharpe.
    Filters to `df['config'] == config_name` internally.
    """
    sub = df[df["config"] == config_name].copy()
    if sub.empty:
        raise ValueError(f"No rows for config {config_name!r}")

    # Pivot: rows = window_size_y, cols = start_date
    pivot = sub.pivot_table(
        index="window_size_y", columns="start_date", values="sharpe", aggfunc="first",
    )
    pivot = pivot.sort_index(ascending=True)  # 3 → 20

    fig, ax = plt.subplots(figsize=(14, 4))

    # Center colormap at SPY anchor: subtract anchor for diverging
    centered = pivot.values - spy_anchor
    vmax = np.nanmax(np.abs(centered)) if not np.all(np.isnan(centered)) else 1.0
    im = ax.imshow(
        centered, aspect="auto", cmap="RdYlGn",
        vmin=-vmax, vmax=vmax, interpolation="nearest",
    )

    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f"{w}y" for w in pivot.index])
    ax.set_ylabel("Forward horizon")

    # X-axis: pick ~12 evenly-spaced ticks
    n_cols = len(pivot.columns)
    if n_cols > 0:
        n_ticks = min(12, n_cols)
        idxs = np.linspace(0, n_cols - 1, n_ticks).astype(int)
        ax.set_xticks(idxs)
        ax.set_xticklabels([pivot.columns[i].strftime("%Y-%m") for i in idxs],
                           rotation=45, ha="right")
    ax.set_xlabel("Entry month-end")

    if annotate_cohort_dates:
        for d_str in annotate_cohort_dates:
            d = pd.Timestamp(d_str)
            # Find nearest column index
            if n_cols > 0:
                diffs = (pivot.columns - d).map(abs)
                nearest = int(np.argmin(diffs))
                ax.axvline(nearest, color="black", linestyle=":",
                           linewidth=0.8, alpha=0.7)

    fig.colorbar(im, ax=ax, label=f"Forward Sharpe − SPY ({spy_anchor:.3f})")
    ax.set_title(f"{config_name} — Forward Sharpe by entry date and horizon")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
