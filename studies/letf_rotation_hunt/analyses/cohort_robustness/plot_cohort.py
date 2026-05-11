"""Per-cohort 4-line equity plot for the cohort_robustness sub-study (spec §3.2)."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# Colour scheme
COLOR_CANONICAL = "#1f77b4"   # blue — qld_vote_k2_off_zroz
COLOR_SMA250    = "#ff7f0e"   # orange — qld_voteK2_sma250_100
COLOR_TQQQ      = "#2ca02c"   # green — tqqq_voteK2_off_zroz
COLOR_SPY       = "#7f7f7f"   # grey — SPY
LINEWIDTH = 1.4

CONFIG_COLORS: dict[str, str] = {
    "qld_vote_k2_off_zroz":                          COLOR_CANONICAL,
    "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz":  COLOR_SMA250,
    "tqqq_voteK2_off_zroz":                          COLOR_TQQQ,
}


def plot_cohort(
    cohort: dict,
    eq_per_config: dict[str, pd.Series],
    eq_spy: pd.Series,
    out_path: Path,
) -> None:
    """Plot 4 equity lines (3 configs + SPY) starting from cohort entry date.

    All series must already be normalised to start at $10 000 on the
    cohort's entry date and are passed forward (e.g. 10y of post-entry data).
    """
    fig, ax = plt.subplots(figsize=(11, 5.5))

    for cfg_name, eq in eq_per_config.items():
        color = CONFIG_COLORS.get(cfg_name, "#000000")
        ax.plot(eq.index, eq.values, label=cfg_name, color=color,
                linewidth=LINEWIDTH)

    ax.plot(eq_spy.index, eq_spy.values, label="SPY 1× buy-and-hold",
            color=COLOR_SPY, linestyle="--", linewidth=LINEWIDTH)

    ax.set_yscale("log")
    ax.set_title(f"Cohort {cohort['cohort_id']} — {cohort['event']}\n"
                 f"Entry {cohort['date']} ({cohort['tier']})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($, log scale, $10k seed)")
    ax.axhline(10_000.0, color="black", linestyle=":", linewidth=0.8, alpha=0.4,
               label="Recovery line ($10k)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
