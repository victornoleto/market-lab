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

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"

# Display order (top->bottom in legend) + style. Matches REDDIT_POST.md table:
#   benchmarks first, popular reference, then named profiles in risk order.
SERIES_STYLE = {
    "spy_1x":            {"color": "#000000", "lw": 2.5, "ls": "-",  "label": "SPY 1x buy-hold"},
    "popular_50_25_25":  {"color": "#8c564b", "lw": 1.6, "ls": "-",  "label": "Popular 50/25/25 SSO/GLD/ZROZ"},
    "l1_sleeping_pills": {"color": "#1f77b4", "lw": 1.6, "ls": "-",  "label": "Sleeping pills (L1 CEGB)"},
    "l2_bogleheads":     {"color": "#aec7e8", "lw": 1.4, "ls": "-",  "label": "Bogleheads 67% NTSX (L2)"},
    "b4_conservative":   {"color": "#2ca02c", "lw": 2.0, "ls": "-",  "label": "Conservative (B4 ZROZ)"},
    "b2_balanced":       {"color": "#ff7f0e", "lw": 2.0, "ls": "-",  "label": "Balanced (B2)"},
    "t1_aggressive":     {"color": "#d62728", "lw": 2.5, "ls": "-",  "label": "Aggressive (T1 gold-heavy)"},
    "lrs_sso_200sma":    {"color": "#9467bd", "lw": 1.5, "ls": "--", "label": "Gayed LRS 2x (SSO 200d)"},
    "lrs_upro_200sma":   {"color": "#bcbd22", "lw": 2.0, "ls": "--", "label": "Gayed LRS 3x (UPRO 200d)"},
}


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


def _setup_axes(ax, title: str, ylabel: str):
    ax.set_title(title, fontsize=13, weight="bold", loc="left", pad=12)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, which="both", color="#e8e8e8", linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=10)


def _style(slug: str) -> dict:
    return SERIES_STYLE[slug]


def plot_equity_log(series: list[Series], out_path: Path):
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("white")

    sorted_s = sorted(series, key=lambda s: -s.end_val)
    for s in sorted_s:
        st = _style(s.slug)
        ax.plot(s.dates, s.equity, color=st["color"], lw=st["lw"], ls=st["ls"],
                label=f'{st["label"]}  ${s.end_val/1000:,.0f}k')

    ax.set_yscale("log")
    _setup_axes(ax, "$10k -> ?  |  Equity curves (log scale)  |  testfol.io 1986-2026 annual rebal",
                "Portfolio value ($, log)")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", fontsize=9, frameon=False, labelspacing=0.4)
    ax.set_xlim(min(s.dates[0] for s in series), max(s.dates[-1] for s in series))

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path}", file=sys.stderr)


def plot_drawdown(series: list[Series], out_path: Path):
    fig, ax = plt.subplots(figsize=(14, 4.8))
    fig.patch.set_facecolor("white")

    sorted_s = sorted(series, key=lambda s: s.mdd)  # most negative first
    for s in sorted_s:
        st = _style(s.slug)
        ax.plot(s.dates, s.drawdown, color=st["color"], lw=st["lw"], ls=st["ls"],
                label=f'{st["label"]}  MDD {s.mdd:.1f}%')

    spy = next(s for s in series if s.slug == "spy_1x")
    ax.axhspan(spy.mdd, 0, color="#f5f5f5", alpha=0.5, zorder=0)
    ax.axhline(spy.mdd, color="#000000", linestyle=":", linewidth=1.0, alpha=0.6)
    ax.text(spy.dates[0], spy.mdd + 1.5, f" SPY MDD {spy.mdd:.1f}%", fontsize=8, color="#555")

    _setup_axes(ax, "Underwater chart (peak-to-trough drawdown)", "Drawdown (%)")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="lower right", fontsize=8, frameon=False, ncol=2, labelspacing=0.3)
    ax.set_xlim(min(s.dates[0] for s in series), max(s.dates[-1] for s in series))

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path}", file=sys.stderr)


def plot_rolling_cagr(series: list[Series], out_path: Path):
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("white")

    for s in series:
        if s.roll_cagr.size == 0:
            continue
        st = _style(s.slug)
        ax.plot(s.roll_dates, s.roll_cagr, color=st["color"], lw=st["lw"], ls=st["ls"],
                label=st["label"])

    ax.axhline(0, color="#999999", linewidth=0.6)
    _setup_axes(ax, "Rolling 5-year CAGR  |  testfol.io",
                "Annualized return over 5y window (%)")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper right", fontsize=8, frameon=False, ncol=2, labelspacing=0.3)

    for year, label in [(2000, "Dotcom"), (2008, "GFC"), (2022, "Inflation")]:
        ax.axvline(datetime(year, 1, 1, tzinfo=timezone.utc),
                   color="#cccccc", linewidth=0.5, linestyle=":")
        ax.text(datetime(year, 6, 1, tzinfo=timezone.utc),
                ax.get_ylim()[1] * 0.97, label, fontsize=7, color="#888")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path}", file=sys.stderr)


def plot_cagr_mdd_scatter(series: list[Series], out_path: Path):
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor("white")

    spy = next(s for s in series if s.slug == "spy_1x")
    xlim = (min(s.mdd for s in series) - 5, 0)
    ylim = (min(0, min(s.cagr for s in series) - 1), max(s.cagr for s in series) + 2)
    ax.axvspan(spy.mdd, 0,
               ymin=(spy.cagr - ylim[0]) / (ylim[1] - ylim[0]), ymax=1.0,
               color="#a8d99a", alpha=0.2, zorder=0)
    ax.axvspan(xlim[0], spy.mdd,
               ymin=0, ymax=(spy.cagr - ylim[0]) / (ylim[1] - ylim[0]),
               color="#f0a8a8", alpha=0.2, zorder=0)
    ax.axvline(spy.mdd, color="#000000", linewidth=0.8, linestyle="--", alpha=0.6)
    ax.axhline(spy.cagr, color="#000000", linewidth=0.8, linestyle="--", alpha=0.6)

    for s in series:
        st = _style(s.slug)
        marker = "X" if s.slug == "spy_1x" else ("D" if s.slug.startswith("lrs_") else "o")
        size = 220 if s.slug == "spy_1x" else 140
        ax.scatter(s.mdd, s.cagr, s=size, c=st["color"], marker=marker,
                   edgecolors="white", linewidths=1.5, zorder=3)
        short = st["label"].split("(")[-1].split(")")[0] if "(" in st["label"] else st["label"].split()[0]
        ax.annotate(short, (s.mdd, s.cagr), xytext=(8, 4),
                    textcoords="offset points", fontsize=8, color=st["color"])

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    _setup_axes(ax, "Pareto: CAGR vs MaxDD  |  beats SPY = upper-right quadrant", "CAGR (%)")
    ax.set_xlabel("MaxDD (%)", fontsize=11)
    ax.text(spy.mdd - 1, ylim[1] - 1, "Beats SPY on both",
            fontsize=9, color="#2a7a2a", weight="bold", ha="right", va="top")
    ax.text(xlim[0] + 1, ylim[0] + 1, "Worse on both",
            fontsize=9, color="#993333", weight="bold", ha="left", va="bottom")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
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
        "b2_balanced": "**Balanced (B2)**",
        "t1_aggressive": "**Aggressive (T1)**",
        "lrs_sso_200sma": "Gayed LRS 2x (SSO 200d)",
        "lrs_upro_200sma": "Gayed LRS 3x (UPRO 200d)",
    }
    order = ["spy_1x", "popular_50_25_25", "l1_sleeping_pills", "l2_bogleheads",
             "b4_conservative", "b2_balanced", "t1_aggressive",
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
    print("Loading series from testfolio_data/...", file=sys.stderr)
    series = load_all()
    print(f"  loaded {len(series)} series", file=sys.stderr)

    print("\nGenerating plots...", file=sys.stderr)
    plot_equity_log(series,        SCRIPT_DIR / "testfolio_01_equity.png")
    plot_drawdown(series,          SCRIPT_DIR / "testfolio_02_drawdown.png")
    plot_rolling_cagr(series,      SCRIPT_DIR / "testfolio_03_rolling5y.png")
    plot_cagr_mdd_scatter(series,  SCRIPT_DIR / "testfolio_04_scatter.png")

    print_summary(series)
    print(f"\nDone. PNGs in {SCRIPT_DIR}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
