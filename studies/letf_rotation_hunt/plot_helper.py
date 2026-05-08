"""Standardized matplotlib helpers per spec §5.6.

Conventions:
  - Log scale Y for equity, linear for drawdown
  - $10k starting capital
  - SPY = gray dashed, Gayed canon = black dashed, configs categorical palette
  - External legend, titled, ≤ 200KB output
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SPY_STYLE = {"color": "gray", "linestyle": "--", "linewidth": 1.5, "label": "SPY 1× b&h"}
GAYED_STYLE = {"color": "black", "linestyle": "--", "linewidth": 1.5, "label": "Gayed canon"}
CONFIG_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]


def plot_tier_relative_to_spy(
    equity_curves: dict[str, pd.Series],
    spy_equity: pd.Series,
    out_path: Path,
    title: str = "",
    top_n_bold: int = 5,
    rank_by: dict[str, float] | None = None,
) -> None:
    """All-configs-in-tier overlay: each config as ratio to SPY (renormalised).

    Top ``top_n_bold`` configs (by ``rank_by`` if provided, else by terminal
    ratio) are colored bold; remaining configs faded (alpha=0.25). SPY=1.0
    drawn in black dashed. Log-scale Y per the user convention 2026-05-06
    (mirrors ``STUDY_top20_relative_to_spy.png``).

    Parameters
    ----------
    equity_curves : dict[str, pd.Series]
        Strategy equity curves keyed by config name.
    spy_equity : pd.Series
        SPY benchmark equity.
    out_path : Path
        PNG path.
    title : str
        Plot title.
    top_n_bold : int
        How many top configs to color bold (default 5).
    rank_by : dict[str, float] | None
        Optional mapping config_name → score for ranking; if None, ranks by
        terminal ratio (config_eq[-1]/spy_eq[-1]).
    """
    if not equity_curves:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No configs to plot", ha="center", va="center")
        plt.savefig(out_path, dpi=80, bbox_inches="tight")
        plt.close(fig)
        return

    spy = spy_equity.dropna()
    if len(spy) < 2:
        return

    # Build per-config ratio series (renormalized to 1.0 on first common date)
    ratios: dict[str, pd.Series] = {}
    for label, eq in equity_curves.items():
        eq_clean = eq.dropna()
        common = eq_clean.index.intersection(spy.index)
        if len(common) < 2:
            continue
        eq_aligned = eq_clean.loc[common]
        spy_aligned = spy.loc[common]
        ratio = (eq_aligned / float(eq_aligned.iloc[0])) / (
            spy_aligned / float(spy_aligned.iloc[0])
        )
        ratios[label] = ratio

    if not ratios:
        return

    # Rank: by user-provided score, else by terminal ratio
    if rank_by is not None:
        ranked = sorted(ratios.keys(), key=lambda n: -rank_by.get(n, float("-inf")))
    else:
        ranked = sorted(ratios.keys(), key=lambda n: -float(ratios[n].iloc[-1]))
    top_set = set(ranked[:top_n_bold])

    fig, ax = plt.subplots(figsize=(11, 7))

    # SPY = 1.0 reference (black dashed)
    if ratios:
        any_ratio = next(iter(ratios.values()))
        ax.axhline(1.0, color="black", linestyle="--", linewidth=1.5,
                   label="SPY 1× b&h (=1.0)", zorder=3)

    # Plot non-top first (faded background)
    palette_top = CONFIG_PALETTE
    palette_idx = 0
    for label in ranked:
        ratio = ratios[label]
        if label in top_set:
            continue
        ax.plot(ratio.index, ratio.values, color="#888888",
                linewidth=0.8, alpha=0.25, zorder=1)

    # Plot top configs bold + colored on top
    for label in ranked:
        if label not in top_set:
            continue
        ratio = ratios[label]
        color = palette_top[palette_idx % len(palette_top)]
        palette_idx += 1
        terminal = float(ratio.iloc[-1])
        ax.plot(
            ratio.index, ratio.values,
            color=color, linewidth=2.0, alpha=0.95, zorder=2,
            label=f"{label} ({terminal:.1f}×)",
        )

    ax.set_yscale("log")
    ax.set_ylabel("Ratio strategy_eq / SPY_eq (renormalised)")
    ax.set_xlabel("Date")
    ax.set_title(title or "All configs ratio to SPY (top-N bold; rest faded)")
    ax.grid(True, which="both", linestyle="-", linewidth=0.3, alpha=0.4)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.85)
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def plot_equity_curves(equity_curves: dict[str, pd.Series], out_path: Path, title: str = "") -> None:
    """Plot equity curves (log scale, $10k base).

    Parameters
    ----------
    equity_curves : dict[str, pd.Series]
        {label: equity_series}. Special labels "SPY 1× b&h" and "Gayed canon"
        get reserved styling.
    out_path : Path
        PNG output path.
    title : str
        Plot title.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    palette_idx = 0
    for label, equity in equity_curves.items():
        if label == "SPY 1× b&h":
            ax.plot(equity.index, equity.values, **SPY_STYLE)
        elif label == "Gayed canon":
            ax.plot(equity.index, equity.values, **GAYED_STYLE)
        else:
            color = CONFIG_PALETTE[palette_idx % len(CONFIG_PALETTE)]
            ax.plot(equity.index, equity.values, color=color, label=label, linewidth=1.2)
            palette_idx += 1

    ax.set_yscale("log")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($, log scale)")
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def plot_drawdown_curves(equity_curves: dict[str, pd.Series], out_path: Path, title: str = "") -> None:
    """Plot drawdown (peak-to-trough) per config."""
    fig, ax = plt.subplots(figsize=(10, 6))
    palette_idx = 0
    for label, equity in equity_curves.items():
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        if label == "SPY 1× b&h":
            ax.plot(drawdown.index, drawdown.values * 100, **SPY_STYLE)
        elif label == "Gayed canon":
            ax.plot(drawdown.index, drawdown.values * 100, **GAYED_STYLE)
        else:
            color = CONFIG_PALETTE[palette_idx % len(CONFIG_PALETTE)]
            ax.plot(drawdown.index, drawdown.values * 100, color=color, label=label, linewidth=1.2)
            palette_idx += 1

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    ax.legend(loc="lower left", bbox_to_anchor=(1.02, 0), fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def plot_rolling_sharpe(equity_curves: dict[str, pd.Series], out_path: Path, window_days: int = 252 * 5, title: str = "") -> None:
    """Plot rolling Sharpe (5y default) per config."""
    fig, ax = plt.subplots(figsize=(10, 6))
    palette_idx = 0
    for label, equity in equity_curves.items():
        returns = equity.pct_change().dropna()
        rolling_mean = returns.rolling(window=window_days).mean()
        rolling_std = returns.rolling(window=window_days).std()
        sharpe = (rolling_mean / rolling_std.replace(0, np.nan)) * np.sqrt(252)
        if label == "SPY 1× b&h":
            ax.plot(sharpe.index, sharpe.values, **SPY_STYLE)
        elif label == "Gayed canon":
            ax.plot(sharpe.index, sharpe.values, **GAYED_STYLE)
        else:
            color = CONFIG_PALETTE[palette_idx % len(CONFIG_PALETTE)]
            ax.plot(sharpe.index, sharpe.values, color=color, label=label, linewidth=1.2)
            palette_idx += 1

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Rolling Sharpe ({window_days // 252}y)")
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def plot_rolling_cagr(
    equity_curves: dict[str, pd.Series], out_path: Path,
    window_days: int = 252 * 3, title: str = "",
) -> None:
    """Rolling CAGR (3y default). Useful for spotting regime shifts.

    Citation: standard rolling-return decomposition; see
    `[trading_systems_methods, ch.21]` (Kaufman) on regime sensitivity testing.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    palette_idx = 0
    for label, equity in equity_curves.items():
        equity_ratio = equity / equity.shift(window_days)
        years = window_days / 252
        cagr = equity_ratio ** (1.0 / years) - 1.0
        if label == "SPY 1× b&h":
            ax.plot(cagr.index, cagr.values * 100, **SPY_STYLE)
        elif label == "Gayed canon":
            ax.plot(cagr.index, cagr.values * 100, **GAYED_STYLE)
        else:
            color = CONFIG_PALETTE[palette_idx % len(CONFIG_PALETTE)]
            ax.plot(cagr.index, cagr.values * 100, color=color, label=label, linewidth=1.2)
            palette_idx += 1
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Rolling {window_days // 252}y CAGR (%)")
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def plot_pct_beat_spy(
    equity_curves: dict[str, pd.Series], spy_equity: pd.Series, out_path: Path,
    window_days: int = 252 * 3, title: str = "",
) -> None:
    """Rolling % of N-day windows where strategy CAGR > SPY CAGR.

    For each rolling N-day window ending at date t, compute strategy CAGR vs
    SPY CAGR over the same window. Plot the rolling fraction of windows
    (cumulative-to-date) where strategy beat SPY.

    Threshold reference for KILL T0 evaluation: rotation that fails to beat
    SPY in ≥50% of rolling 3y windows is structural underperformance.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    palette_idx = 0
    for label, equity in equity_curves.items():
        if label in {"SPY 1× b&h", "Gayed canon"}:
            continue
        aligned = pd.concat({"strat": equity, "spy": spy_equity}, axis=1, sort=True).dropna()
        if len(aligned) < window_days + 1:
            continue
        strat_ratio = aligned["strat"] / aligned["strat"].shift(window_days)
        spy_ratio = aligned["spy"] / aligned["spy"].shift(window_days)
        beats = (strat_ratio > spy_ratio).astype(float)
        # Cumulative fraction of windows beaten (running mean from first valid point)
        valid = beats.dropna()
        cumfrac = valid.expanding().mean() * 100
        color = CONFIG_PALETTE[palette_idx % len(CONFIG_PALETTE)]
        ax.plot(cumfrac.index, cumfrac.values, color=color, label=label, linewidth=1.2)
        palette_idx += 1
    ax.axhline(y=50, color="black", linestyle=":", linewidth=0.8, label="50% threshold")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Cumulative % of {window_days // 252}y windows beating SPY")
    ax.set_ylim(0, 100)
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


# Crisis windows per spec §3.2 — peak-to-trough range for SPY in each event
CRISIS_WINDOWS: dict[str, tuple[str, str]] = {
    "2000-02 dotcom":  ("2000-09-01", "2002-10-31"),
    "2008 GFC":        ("2007-10-01", "2009-03-31"),
    "2020 COVID":      ("2020-02-19", "2020-04-30"),
    "2022 rates":      ("2022-01-03", "2022-12-31"),
}


def plot_crisis_attribution(
    equity_curves: dict[str, pd.Series], spy_equity: pd.Series, out_path: Path,
    title: str = "",
) -> None:
    """Bar chart: max drawdown per crisis window per config vs SPY.

    Lower (less negative) bar is better. SPY drawn as gray hatched bars for
    reference. Crisis windows pre-registered per spec §3.2 to avoid p-hacking
    the periods.
    """
    crises = list(CRISIS_WINDOWS.keys())
    cfg_labels = [k for k in equity_curves if k not in {"SPY 1× b&h", "Gayed canon"}]
    n_crises = len(crises)
    n_cfgs = len(cfg_labels)
    if n_cfgs == 0:
        return

    width = 0.8 / (n_cfgs + 1)
    x = np.arange(n_crises)

    def _mdd(eq: pd.Series, win: tuple[str, str]) -> float:
        sub = eq[(eq.index >= win[0]) & (eq.index <= win[1])]
        if len(sub) < 2:
            return float("nan")
        peak = sub.cummax()
        dd = (sub - peak) / peak
        return float(dd.min())

    fig, ax = plt.subplots(figsize=(10, 6))
    spy_mdds = [_mdd(spy_equity, CRISIS_WINDOWS[c]) * 100 for c in crises]
    ax.bar(x - 0.4, spy_mdds, width, color="gray", alpha=0.5, hatch="//", label="SPY 1× b&h")
    for i, cfg in enumerate(cfg_labels):
        mdds = [_mdd(equity_curves[cfg], CRISIS_WINDOWS[c]) * 100 for c in crises]
        color = CONFIG_PALETTE[i % len(CONFIG_PALETTE)]
        ax.bar(x - 0.4 + (i + 1) * width, mdds, width, color=color, label=cfg)

    ax.set_xticks(x)
    ax.set_xticklabels(crises, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Max drawdown in window (%)")
    ax.set_title(title)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.grid(True, axis="y", linewidth=0.3, alpha=0.5)
    ax.legend(loc="lower left", bbox_to_anchor=(1.02, 0), fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def plot_underwater_vs_benchmark(
    winner_equity: pd.Series, benchmark_equity: pd.Series, out_path: Path,
    winner_label: str = "winner", benchmark_label: str = "SPY",
    sharpe: float | None = None, title_suffix: str = "",
    warmup_days: int = 252,
) -> dict:
    """Standardized "winner equity / benchmark equity" plot.

    Per user convention 2026-05-06: every TIER_X_REPORT.md must include an
    underwater-vs-benchmark plot of the tier winner so readers see immediately
    whether the strategy stays above the buy-hold alternative throughout
    history (the v2 scoring criterion).

    Renormalises both series to start at the same value on the first common
    date and plots the ratio with green-fill above parity / red-fill below.
    Annotates the worst absolute MDD point with the underwater context.

    Returns
    -------
    dict
        Stats: ``pct_above`` (0-1), ``min_ratio_post_warmup``, ``end_ratio``.
    """
    aligned = pd.concat({"win": winner_equity, "bench": benchmark_equity},
                        axis=1, sort=True).dropna()
    ratio = (aligned["win"] / aligned["win"].iloc[0]) / (
        aligned["bench"] / aligned["bench"].iloc[0]
    )
    pct_above = float((ratio > 1.0).mean())
    min_ratio = float(ratio.iloc[warmup_days:].min()) if len(ratio) > warmup_days else float(ratio.min())
    end_ratio = float(ratio.iloc[-1])

    peak = aligned["win"].cummax()
    dd = (aligned["win"] - peak) / peak
    worst_dd_date = dd.idxmin()
    dd_at_worst = float(dd.min())
    ratio_at_worst = float(ratio.loc[worst_dd_date])

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.fill_between(ratio.index, 1, ratio.values, where=ratio.values >= 1,
                    color="#2ca02c", alpha=0.4, label=f"{winner_label} above {benchmark_label}")
    ax.fill_between(ratio.index, 1, ratio.values, where=ratio.values < 1,
                    color="#d62728", alpha=0.6, label=f"{winner_label} below {benchmark_label}")
    ax.plot(ratio.index, ratio.values, color="black", linewidth=1.0)
    ax.axhline(y=1.0, color="black", linestyle="--", linewidth=1, alpha=0.7,
               label=f"parity ({winner_label} = {benchmark_label})")
    ax.axhline(y=0.95, color="darkred", linestyle=":", linewidth=1, alpha=0.7,
               label="WINNER strict bar (0.95)")
    ax.annotate(
        f"{worst_dd_date.date()}\nMDD {dd_at_worst*100:.1f}%\n{winner_label} {ratio_at_worst:.1f}× {benchmark_label}",
        xy=(worst_dd_date, ratio_at_worst),
        xytext=(worst_dd_date, ratio_at_worst * 6),
        fontsize=9, ha="center",
        arrowprops=dict(arrowstyle="->", color="black"),
    )

    ax.set_yscale("log")
    ax.set_ylabel(f"{winner_label} / {benchmark_label} ratio (log scale)")
    ax.set_xlabel("Date")
    sharpe_str = f" (Sh {sharpe:.3f})" if sharpe is not None else ""
    ax.set_title(
        f"Underwater-vs-Benchmark: {winner_label}{sharpe_str} relative to "
        f"{benchmark_label} buy-hold{title_suffix}\n"
        f"{pct_above*100:.2f}% of days above {benchmark_label}; "
        f"min ratio post-warmup {min_ratio:.2f}×; end ratio {end_ratio:.1f}×"
    )
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)

    return {
        "pct_above": pct_above,
        "min_ratio_post_warmup": min_ratio,
        "end_ratio": end_ratio,
    }


def plot_sharpe_heatmap(
    df: pd.DataFrame, out_path: Path, title: str = "", cmap: str = "RdYlGn",
    vmin: float | None = None, vmax: float | None = None,
) -> None:
    """Heatmap of a 2D metric grid (rows × cols of cells like Sharpe per
    (on×period, off) combo).

    Used for large parameter sweeps (T1d 360 configs) where line plots become
    illegible. Caller pre-shapes the DataFrame (rows = one axis, cols = other).
    """
    import matplotlib.colors as mcolors
    fig, ax = plt.subplots(figsize=(max(8, df.shape[1] * 0.9), max(6, df.shape[0] * 0.25)))
    arr = df.to_numpy(dtype=float)
    if vmin is None:
        vmin = float(np.nanmin(arr))
    if vmax is None:
        vmax = float(np.nanmax(arr))
    im = ax.imshow(arr, aspect="auto", cmap=cmap,
                   norm=mcolors.Normalize(vmin=vmin, vmax=vmax))
    ax.set_xticks(range(df.shape[1]))
    ax.set_xticklabels(df.columns, rotation=20, ha="right", fontsize=9)
    ax.set_yticks(range(df.shape[0]))
    ax.set_yticklabels(df.index, fontsize=8)
    # Annotate cells with values
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            v = arr[i, j]
            if v == v:  # not NaN
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=7, color="black")
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Sharpe (annualised)", fontsize=9)
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


def plot_regime_attribution(
    equity_curves: dict[str, pd.Series], signal_per_config: dict[str, pd.Series],
    out_path: Path, title: str = "",
) -> None:
    """Per-config % of time ON (signal=ON) — regime exposure summary.

    For each config, show the fraction of trading days where the signal was
    ON (allocated to risk asset). Complements equity curves by exposing how
    aggressive each config is in regime selection.
    """
    cfg_labels = [k for k in equity_curves if k in signal_per_config]
    if not cfg_labels:
        return
    pct_on = [float(signal_per_config[c].mean() * 100) for c in cfg_labels]
    colors = [CONFIG_PALETTE[i % len(CONFIG_PALETTE)] for i in range(len(cfg_labels))]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(cfg_labels, pct_on, color=colors)
    for bar, v in zip(bars, pct_on):
        ax.text(
            bar.get_x() + bar.get_width() / 2, v + 1, f"{v:.1f}%",
            ha="center", va="bottom", fontsize=9,
        )
    ax.set_ylabel("% of days ON (signal=1)")
    ax.set_ylim(0, 100)
    ax.set_title(title)
    ax.grid(True, axis="y", linewidth=0.3, alpha=0.5)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)
