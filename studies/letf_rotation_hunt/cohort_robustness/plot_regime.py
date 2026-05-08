"""Regime-stratified violin plot for cohort_robustness (spec §4.4)."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

REGIME_ORDER = ["Risk-off", "Borderline", "Mostly-on", "All-on"]


def plot_regime_violin(df: pd.DataFrame, out_path: Path) -> None:
    """One facet per config; violin of forward_5y_sharpe across 4 regimes.

    `df` columns: regime, config_name, forward_5y_sharpe.
    """
    configs = sorted(df["config_name"].unique())
    n = len(configs)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5.5), sharey=True)
    if n == 1:
        axes = [axes]

    for ax, cfg in zip(axes, configs):
        sub = df[df["config_name"] == cfg]
        data = [sub[sub["regime"] == r]["forward_5y_sharpe"].dropna().values
                for r in REGIME_ORDER]
        # Filter out empty entries
        positions = list(range(1, len(REGIME_ORDER) + 1))
        nonempty = [(p, d, r) for p, d, r in zip(positions, data, REGIME_ORDER)
                    if len(d) > 0]
        if not nonempty:
            ax.set_title(f"{cfg}\n(no data)")
            continue
        ps, ds, rs = zip(*nonempty)
        parts = ax.violinplot(ds, positions=list(ps), showmedians=True, widths=0.7)
        for pc in parts["bodies"]:
            pc.set_alpha(0.6)
        ax.set_xticks(list(ps))
        ax.set_xticklabels(rs, rotation=20)
        ax.axhline(0.682, color="grey", linestyle="--", linewidth=0.8,
                   label="SPY anchor 0.682")
        ax.set_title(cfg, fontsize=9)
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend(loc="upper left", fontsize=7)

    axes[0].set_ylabel("Forward 5y Sharpe")
    fig.suptitle("Forward 5y Sharpe by entry regime (top-3 swing strategies)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
