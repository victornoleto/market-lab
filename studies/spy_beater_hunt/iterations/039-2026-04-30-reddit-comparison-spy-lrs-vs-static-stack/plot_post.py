#!/usr/bin/env python3
"""Generate 4 testfolio-derived PNGs + metrics summary table.

Reads testfolio_data/{backtest_buyhold,tactical_lrs_sso,tactical_lrs_upro}.json.

Writes (alongside the existing internal-lib reddit_plot_*.png):
  testfolio_01_equity.png       — log-scale equity curves
  testfolio_02_drawdown.png     — underwater chart
  testfolio_03_rolling5y.png    — rolling 5y CAGR
  testfolio_04_scatter.png      — Pareto CAGR vs MaxDD

Stdout: markdown table with CAGR/MDD/Sharpe/Sortino/$10k->end_val.
Use this to update the Results table in REDDIT_POST.md if numbers drift.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"

# === Modern style preset =====================================================
# Visual hierarchy:
#   tier 1 — named CE-stack profiles (B2/T1/B4/L1): saturated, line weight 2.0-2.4
#   tier 2 — references (SPY/popular/L2/Gayed): muted, line weight 1.4-2.0
# Palette inspired by Datawrapper / FT — better contrast on white than Tableau-10,
# less "candy" saturation. SPY stays charcoal (anchor benchmark).
SERIES_STYLE = {
    "spy_1x":            {"color": "#1a1a1a", "lw": 2.4, "ls": "-",  "label": "SPY 1x buy-hold"},
    "popular_50_25_25":  {"color": "#a87b50", "lw": 1.4, "ls": "-",  "label": "Popular 50/25/25 SSO/GLD/ZROZ"},
    "l1_sleeping_pills": {"color": "#2a5c8c", "lw": 2.0, "ls": "-",  "label": "Sleeping pills (L1 CEGB)"},
    "l2_bogleheads":     {"color": "#8fa8c2", "lw": 1.4, "ls": "-",  "label": "Bogleheads 67% NTSX (L2)"},
    "b4_conservative":   {"color": "#1e7b33", "lw": 2.4, "ls": "-",  "label": "Conservative (B4 ZROZ)"},
    # Note: T1 and B2 labels swapped 2026-04-30 — testfol.io shows B2 has
    # higher CAGR AND worse MDD than T1, so B2 is genuinely the aggressive
    # one (more equity exposure: 84% vs 74.5%). T1's extra gold/duration
    # makes it actually more balanced. See REDDIT_POST.md "What the data tells us".
    "t1_aggressive":     {"color": "#e89b2a", "lw": 2.0, "ls": "-",  "label": "Balanced (T1 gold-heavy)"},
    "b2_balanced":       {"color": "#c1272d", "lw": 2.4, "ls": "-",  "label": "Aggressive (B2 high-equity)"},
    "lrs_sso_200sma":    {"color": "#8e74aa", "lw": 1.5, "ls": "--", "label": "Gayed LRS 2x (SSO 200d)"},
    "lrs_upro_200sma":   {"color": "#b7a040", "lw": 1.8, "ls": "--", "label": "Gayed LRS 3x (UPRO 200d)"},
}


def apply_modern_style() -> None:
    """Set rcParams for clean/minimal dashboard look. Call once before plotting."""
    mpl.rcParams.update({
        # Typography — fallback chain, DejaVu Sans is always present on Linux
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "IBM Plex Sans", "Source Sans 3",
                            "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 10.5,
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "axes.titlecolor": "#1a1a1a",
        "axes.labelsize": 10.5,
        "axes.labelcolor": "#555555",
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "xtick.color": "#777777",
        "ytick.color": "#777777",
        "legend.fontsize": 9,
        "legend.frameon": False,

        # Spines — keep only left/bottom, very light
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#cccccc",
        "axes.linewidth": 0.7,

        # Grid — horizontal only, faint
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": "#eeeeee",
        "grid.linewidth": 0.6,
        "grid.linestyle": "-",

        # Tick marks — labels only, no stick marks
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "xtick.minor.size": 0,
        "ytick.minor.size": 0,
        "xtick.major.pad": 6,
        "ytick.major.pad": 6,

        # Figure
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": 150,
    })


def _dollar_fmt(value: float, _pos=None) -> str:
    """Format y-axis as $1k/$10k/$100k/$1M (cleaner than 10^x on log scale)."""
    if value >= 1e6:
        return f"${value/1e6:.0f}M"
    if value >= 1e3:
        return f"${value/1e3:.0f}k"
    return f"${value:.0f}"


def _add_titles(ax, title: str, subtitle: str) -> None:
    """Bold title + muted subtitle pattern — modern dashboard convention."""
    ax.text(0.0, 1.08, title, transform=ax.transAxes, fontsize=14,
            weight="semibold", color="#1a1a1a", va="bottom", ha="left")
    ax.text(0.0, 1.02, subtitle, transform=ax.transAxes, fontsize=10,
            color="#888888", va="bottom", ha="left")


@dataclass
class Series:
    slug: str
    dates: np.ndarray
    equity: np.ndarray
    drawdown: np.ndarray
    roll_dates: np.ndarray
    roll_cagr: np.ndarray
    cagr: float
    mdd: float
    sharpe: float
    sortino: float
    calmar: float
    end_val: float
    std: float


def _ts_to_dt(timestamps: list) -> np.ndarray:
    arr = np.asarray(timestamps, dtype=np.float64)
    if arr.size and arr.max() > 1e11:
        arr = arr / 1000.0  # ms -> s
    return np.array([datetime.fromtimestamp(t, tz=timezone.utc) for t in arr])


def parse_response_series(response: dict, idx: int, slug: str) -> Series:
    """Pull one portfolio (by index) out of a testfolio API response.

    Schema (verified against data/testfolio/*.json):
      response.charts.history    = [timestamps, eq_0, eq_1, ...]
      response.charts.drawdown   = [timestamps, dd_0, dd_1, ...]
      response.charts.rolling.cagr = [timestamps, cagr_0, cagr_1, ...]
      response.stats             = [stat_0, stat_1, ...]
    """
    charts = response["charts"]
    hist = charts["history"]
    dd = charts["drawdown"]
    rc = charts["rolling"]["cagr"]
    s = response["stats"][idx]
    return Series(
        slug=slug,
        dates=_ts_to_dt(hist[0]),
        equity=np.asarray(hist[1 + idx], dtype=np.float64),
        drawdown=np.asarray(dd[1 + idx], dtype=np.float64),
        roll_dates=_ts_to_dt(rc[0]),
        roll_cagr=np.asarray(rc[1 + idx], dtype=np.float64),
        cagr=float(s["cagr"]),
        mdd=float(s["max_drawdown"]),
        sharpe=float(s["sharpe"]),
        sortino=float(s["sortino"]),
        calmar=float(s["calmar"]),
        end_val=float(s["end_val"]),
        std=float(s.get("std", float("nan"))),
    )


def find_strategy_index(response: dict, substr: str) -> int:
    """Find the rotation-strategy index in a /api/tactical response.

    Tactical responses have N+1 entries in stats: N individual allocation legs
    (each held constant) plus the *combined* tactical strategy that switches
    between them per signals. The combined strategy's stats name matches the
    payload's top-level 'name' field — match that, not the per-leg labels.
    """
    sl = substr.lower()
    for i, s in enumerate(response.get("stats", [])):
        if sl in str(s.get("name", "")).lower():
            return i
    raise SystemExit(f"error: no stats entry name contains {substr!r}; "
                     f"got {[s.get('name') for s in response.get('stats', [])]}")


def load_all() -> list[Series]:
    bh_paths = sorted(DATA_DIR.glob("backtest_buyhold_*.json"))
    sso_path = DATA_DIR / "tactical_lrs_sso.json"
    upro_path = DATA_DIR / "tactical_lrs_upro.json"
    if not bh_paths:
        sys.exit("fatal: no backtest_buyhold_*.json — run fetch_testfolio.py first")
    for p in (sso_path, upro_path):
        if not p.exists():
            sys.exit(f"fatal: {p} missing — run fetch_testfolio.py first")

    series: list[Series] = []
    for bh_path in bh_paths:
        bh_blob = json.loads(bh_path.read_text())
        bh_response = bh_blob["response"]
        for i, p in enumerate(bh_blob["portfolios"]):
            series.append(parse_response_series(bh_response, i, p["slug"]))

    sso_response = json.loads(sso_path.read_text())
    series.append(parse_response_series(
        sso_response, find_strategy_index(sso_response, "lev 2x"), "lrs_sso_200sma"))

    upro_response = json.loads(upro_path.read_text())
    series.append(parse_response_series(
        upro_response, find_strategy_index(upro_response, "lev 3x"), "lrs_upro_200sma"))

    return series


def _style(slug: str) -> dict:
    return SERIES_STYLE[slug]


def plot_equity_log(series: list[Series], out_path: Path):
    fig, ax = plt.subplots(figsize=(13, 7.5))

    sorted_s = sorted(series, key=lambda s: -s.end_val)
    for s in sorted_s:
        st = _style(s.slug)
        end_label = (f"${s.end_val/1e6:.1f}M" if s.end_val >= 1e6
                     else f"${s.end_val/1e3:.0f}k")
        ax.plot(s.dates, s.equity, color=st["color"], lw=st["lw"], ls=st["ls"],
                label=f'{st["label"]}   {end_label}', alpha=0.95)

    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(_dollar_fmt))

    _add_titles(ax, "Equity growth — $10k initial",
                "Log scale · 1987-2026 (~38y) · annual rebalance · testfol.io")
    ax.set_ylabel("")  # subtitle covers context; axis self-evident from $ format
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", labelspacing=0.6, borderpad=0.4,
              handlelength=2.0, handletextpad=0.8)
    ax.set_xlim(min(s.dates[0] for s in series), max(s.dates[-1] for s in series))

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path}", file=sys.stderr)


def plot_drawdown(series: list[Series], out_path: Path):
    fig, ax = plt.subplots(figsize=(13, 5.5))

    sorted_s = sorted(series, key=lambda s: s.mdd)  # most negative first
    for s in sorted_s:
        st = _style(s.slug)
        ax.plot(s.dates, s.drawdown, color=st["color"], lw=st["lw"], ls=st["ls"],
                label=f'{st["label"]}   {s.mdd:.1f}%', alpha=0.95)

    spy = next(s for s in series if s.slug == "spy_1x")
    ax.axhline(spy.mdd, color="#bbbbbb", linestyle="--", linewidth=0.7, zorder=0)
    ax.text(spy.dates[-1], spy.mdd, f"  SPY {spy.mdd:.1f}%",
            fontsize=8.5, color="#999999", va="center", ha="left")
    ax.axhline(0, color="#cccccc", linewidth=0.7, zorder=0)

    _add_titles(ax, "Drawdown — peak to trough",
                "Underwater chart · 1987-2026 · all portfolios")
    ax.set_ylabel("")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="lower right", ncol=2, labelspacing=0.5, columnspacing=1.4,
              handlelength=2.0, handletextpad=0.8)
    ax.set_xlim(min(s.dates[0] for s in series), max(s.dates[-1] for s in series))

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path}", file=sys.stderr)


def _rolling_annualized(equity: np.ndarray, years: int) -> np.ndarray:
    """Rolling annualized return over `years` years, assuming ~252 bus days/yr.

    Output array length = len(equity) - n_days. Aligns with dates[n_days:].
    """
    n = years * 252
    if equity.size <= n:
        return np.array([])
    rolled = equity[n:] / equity[:-n]
    return (rolled ** (1.0 / years) - 1.0) * 100.0


def plot_rolling_grid(series: list[Series], out_path: Path):
    """2x2 grid: rolling 5y / 10y / 15y / 20y CAGR."""
    fig, axs = plt.subplots(2, 2, figsize=(15, 9.5), sharex=True)

    windows = [(5, axs[0, 0]), (10, axs[0, 1]), (15, axs[1, 0]), (20, axs[1, 1])]
    for years, ax in windows:
        for s in series:
            roll = _rolling_annualized(s.equity, years)
            if roll.size == 0:
                continue
            n = years * 252
            roll_dates = s.dates[n:]
            st = _style(s.slug)
            ax.plot(roll_dates, roll, color=st["color"], lw=st["lw"], ls=st["ls"],
                    label=st["label"], alpha=0.92)
        ax.axhline(0, color="#cccccc", linewidth=0.7, zorder=0)
        ax.set_title(f"Rolling {years}-year CAGR", fontsize=11.5,
                     weight="semibold", color="#1a1a1a", loc="left", pad=8)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
        ax.xaxis.set_major_locator(mdates.YearLocator(5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.04),
               ncol=3, frameon=False, handlelength=2.2, handletextpad=0.8,
               columnspacing=2.0)

    fig.text(0.005, 0.985, "Rolling CAGR consistency",
             fontsize=15, weight="semibold", color="#1a1a1a", ha="left", va="top")
    fig.text(0.005, 0.955, "Annualized return over overlapping windows · 1987-2026 · testfol.io",
             fontsize=10, color="#888888", ha="left", va="top")

    fig.tight_layout(rect=[0, 0.03, 1, 0.93])
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path}", file=sys.stderr)


def plot_cagr_mdd_scatter(series: list[Series], out_path: Path):
    fig, ax = plt.subplots(figsize=(11, 7.5))

    spy = next(s for s in series if s.slug == "spy_1x")
    xlim = (min(s.mdd for s in series) - 6, -2)
    ylim = (min(0, min(s.cagr for s in series) - 1.5), max(s.cagr for s in series) + 2.5)

    # Quadrant shading — green NE = beats SPY both axes; red SW = worse on both
    spy_x_norm = (spy.cagr - ylim[0]) / (ylim[1] - ylim[0])
    ax.axvspan(spy.mdd, xlim[1], ymin=spy_x_norm, ymax=1.0,
               color="#2e8b57", alpha=0.07, zorder=0)
    ax.axvspan(xlim[0], spy.mdd, ymin=0, ymax=spy_x_norm,
               color="#c1272d", alpha=0.07, zorder=0)
    ax.axvline(spy.mdd, color="#bbbbbb", linewidth=0.7, linestyle="--", zorder=1)
    ax.axhline(spy.cagr, color="#bbbbbb", linewidth=0.7, linestyle="--", zorder=1)

    for s in series:
        st = _style(s.slug)
        marker = "X" if s.slug == "spy_1x" else ("D" if s.slug.startswith("lrs_") else "o")
        size = 240 if s.slug == "spy_1x" else 160
        ax.scatter(s.mdd, s.cagr, s=size, c=st["color"], marker=marker,
                   edgecolors="white", linewidths=1.8, zorder=3, alpha=0.95)
        short = (st["label"].split("(")[-1].split(")")[0]
                 if "(" in st["label"] else st["label"].split()[0])
        ax.annotate(short, (s.mdd, s.cagr), xytext=(10, 5),
                    textcoords="offset points", fontsize=9, color=st["color"],
                    weight="medium")

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))

    _add_titles(ax, "CAGR vs Max drawdown — Pareto frontier",
                "Upper-right quadrant beats SPY on both axes · 1987-2026 · testfol.io")
    ax.set_xlabel("Max drawdown")
    ax.set_ylabel("CAGR")

    ax.text(spy.mdd - 0.6, ylim[1] - 0.4, "Beats SPY on both",
            fontsize=10, color="#1e7b33", weight="semibold", ha="right", va="top")
    ax.text(xlim[0] + 0.6, ylim[0] + 0.4, "Worse on both",
            fontsize=10, color="#993333", weight="semibold", ha="left", va="bottom")

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path}", file=sys.stderr)


def print_summary(series: list[Series]):
    print()
    print("Markdown table for REDDIT_POST.md (replace lines ~31-39):")
    print()
    print("| portfolio | CAGR | Max DD | Sharpe | Sortino | StdDev | $10k -> end |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    label_for_post = {
        "spy_1x": "SPY 1x buy-hold",
        "popular_50_25_25": "**Popular 50/25/25 SSO/GLD/ZROZ**",
        "l1_sleeping_pills": "**Sleeping pills (L1 CEGB)**",
        "l2_bogleheads": "Bogleheads 67% NTSX (L2)",
        "b4_conservative": "**Conservative (B4 ZROZ)**",
        "t1_aggressive": "**Balanced (T1 gold-heavy)**",
        "b2_balanced": "**Aggressive (B2 high-equity)**",
        "lrs_sso_200sma": "Gayed LRS 2x (SSO 200d)",
        "lrs_upro_200sma": "Gayed LRS 3x (UPRO 200d)",
    }
    # Order: benchmarks → popular → low-risk → high-risk → LRS reference.
    # Swapped t1↔b2 2026-04-30: B2 is more aggressive than T1 by MDD.
    order = ["spy_1x", "popular_50_25_25", "l1_sleeping_pills", "l2_bogleheads",
             "b4_conservative", "t1_aggressive", "b2_balanced",
             "lrs_sso_200sma", "lrs_upro_200sma"]
    by_slug = {s.slug: s for s in series}
    for slug in order:
        s = by_slug.get(slug)
        if not s:
            continue
        print(f"| {label_for_post[slug]} | {s.cagr:.2f}% | {s.mdd:.2f}% | "
              f"{s.sharpe:.3f} | {s.sortino:.3f} | {s.std:.2f}% | "
              f"${s.end_val:,.0f} |")


def main() -> int:
    apply_modern_style()
    print("Loading series from testfolio_data/...", file=sys.stderr)
    series = load_all()
    print(f"  loaded {len(series)} series", file=sys.stderr)

    print("\nGenerating plots...", file=sys.stderr)
    plot_equity_log(series,       SCRIPT_DIR / "testfolio_01_equity.png")
    plot_drawdown(series,         SCRIPT_DIR / "testfolio_02_drawdown.png")
    plot_cagr_mdd_scatter(series, SCRIPT_DIR / "testfolio_03_scatter.png")
    plot_rolling_grid(series,     SCRIPT_DIR / "testfolio_04_rolling_grid.png")

    print_summary(series)
    print(f"\nDone. PNGs in {SCRIPT_DIR}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
