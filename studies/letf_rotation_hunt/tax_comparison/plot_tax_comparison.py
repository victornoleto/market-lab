"""Per-strategy and master-summary plots for tax_comparison sub-study.

Each top-N strategy gets two PNG charts:
  A: log-equity curve, 4 lines (gross / model 1 / model 2 / SPY b&h)
  B: equity / SPY ratio, 3 strategy lines + y=1 reference

Plus a master overlay showing edge-vs-SPY decay across all top-N under each tax model.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Colour scheme matches plot_helper.py conventions.
COLOR_GROSS = "#1f77b4"        # blue
COLOR_PER_SWING = "#ff7f0e"    # orange
COLOR_ANNUAL_NET = "#2ca02c"   # green
COLOR_SPY = "#7f7f7f"          # grey
LINEWIDTH = 1.4

TRADING_DAYS_PER_YEAR = 252


def _annualised_sharpe(equity: pd.Series) -> float:
    rets = equity.pct_change().dropna()
    if rets.std() == 0 or len(rets) < 2:
        return float("nan")
    return float(rets.mean() / rets.std() * np.sqrt(TRADING_DAYS_PER_YEAR))


def _cagr(equity: pd.Series) -> float:
    if len(equity) < 2:
        return float("nan")
    n_years = (equity.index[-1] - equity.index[0]).days / 365.25
    if n_years <= 0:
        return float("nan")
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / n_years) - 1.0)


def plot_per_strategy_equity(
    config_name: str,
    eq_gross: pd.Series,
    eq_per_swing: pd.Series,
    eq_annual_net: pd.Series,
    eq_spy: pd.Series,
    out_path: Path,
) -> None:
    """Plot A — log equity curves: gross / Model 1 / Model 2 / SPY."""
    fig, ax = plt.subplots(figsize=(10, 5.5))

    series = [
        ("Gross (no tax)",         eq_gross,       COLOR_GROSS,       "-"),
        ("Model 1 (per-swing 15%)", eq_per_swing,  COLOR_PER_SWING,   "-"),
        ("Model 2 (annual 15%)",   eq_annual_net,  COLOR_ANNUAL_NET,  "-"),
        ("SPY buy-and-hold",       eq_spy,         COLOR_SPY,         "--"),
    ]
    sub_lines = []
    for label, eq, color, ls in series:
        ax.plot(eq.index, eq.values, label=label, color=color,
                linestyle=ls, linewidth=LINEWIDTH)
        sharpe = _annualised_sharpe(eq)
        cagr = _cagr(eq)
        sub_lines.append(f"{label}: CAGR {cagr:.1%}, Sharpe {sharpe:.2f}")

    ax.set_yscale("log")
    ax.set_title(f"{config_name} — Equity ($10k seed, lh_56y)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($, log scale)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.text(0.5, -0.02, "  |  ".join(sub_lines), ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_per_strategy_ratio(
    config_name: str,
    eq_gross: pd.Series,
    eq_per_swing: pd.Series,
    eq_annual_net: pd.Series,
    eq_spy: pd.Series,
    out_path: Path,
) -> None:
    """Plot B — equity / SPY ratio for the 3 strategy variants + y=1 ref."""
    fig, ax = plt.subplots(figsize=(10, 5.5))

    spy_aligned = eq_spy.reindex(eq_gross.index).ffill()

    series = [
        ("Gross / SPY",               eq_gross / spy_aligned,       COLOR_GROSS),
        ("Model 1 (per-swing) / SPY", eq_per_swing / spy_aligned,  COLOR_PER_SWING),
        ("Model 2 (annual) / SPY",    eq_annual_net / spy_aligned,  COLOR_ANNUAL_NET),
    ]
    sub_lines = []
    for label, ratio, color in series:
        ax.plot(ratio.index, ratio.values, label=label, color=color, linewidth=LINEWIDTH)
        sub_lines.append(
            f"{label}: min {ratio.min():.2f}×, final {ratio.iloc[-1]:.1f}×"
        )

    ax.axhline(1.0, color=COLOR_SPY, linestyle="--", linewidth=1.0, label="SPY = 1×")
    ax.set_yscale("log")
    ax.set_title(f"{config_name} — Relative-to-SPY (lh_56y)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Strategy / SPY (log)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.text(0.5, -0.02, "  |  ".join(sub_lines), ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_master_summary(
    rows: list[dict], out_path: Path,
) -> None:
    """Master overlay: 3 panels (gross / per-swing / annual) × N config lines.

    `rows` is a list of dicts with keys:
        config_name, eq_gross, eq_per_swing, eq_annual_net, eq_spy
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), sharey=True)
    panels = [
        ("Gross",           "eq_gross",      COLOR_GROSS),
        ("Model 1 / SPY",   "eq_per_swing",  COLOR_PER_SWING),
        ("Model 2 / SPY",   "eq_annual_net", COLOR_ANNUAL_NET),
    ]
    for ax, (title, key, base_color) in zip(axes, panels):
        for r in rows:
            spy_aligned = r["eq_spy"].reindex(r[key].index).ffill()
            ratio = r[key] / spy_aligned
            ax.plot(ratio.index, ratio.values, label=r["config_name"], linewidth=0.9, alpha=0.85)
        ax.axhline(1.0, color=COLOR_SPY, linestyle="--", linewidth=1.0)
        ax.set_yscale("log")
        ax.set_title(title)
        ax.set_xlabel("Date")
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("Strategy / SPY (log)")
    axes[-1].legend(loc="lower right", fontsize=7, ncol=2)
    fig.suptitle("Top-10 swing strategies — equity / SPY across 3 tax regimes")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
