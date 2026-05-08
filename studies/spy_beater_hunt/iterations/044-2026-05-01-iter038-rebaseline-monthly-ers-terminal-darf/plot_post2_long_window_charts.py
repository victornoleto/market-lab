#!/usr/bin/env python3
"""Generate Post 2 long-window charts from iter 044 data.

This is the Post 2 publication choice: use `RSST = SPY + KMLM - cash` as a
longer-window managed-futures proxy so the main static-stack study can run from
1987 instead of being clipped by DBMFSIM's 2000 start. This is a deliberate
historical-sensitivity trade-off, not a claim that KMLM-only tracks live RSST as
closely as the later 70/30 DBMF/KMLM check. Return stacking rationale follows
Carlson `[risk_parity, ch.5, p.10]`; managed-futures diversification rationale
follows Ilmanen `[ilmanen_expected_returns, ch.19]`.
"""
from __future__ import annotations

import json
import sys
import urllib.request
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
POST_DIR = SCRIPT_DIR.parent / "039-2026-04-30-reddit-comparison-spy-lrs-vs-static-stack"
API_BACKTEST = "https://testfol.io/api/backtest"
WINDOW_LABEL = "1987-12-30 to 2026-04-29 · monthly rebal · ERs explicit · RSST proxy = SPY + KMLM - cash"

STYLE = {
    "spy_1x": {"color": "#1a1a1a", "lw": 2.5, "label": "SPY 1x"},
    "L1_cegb_proxy": {"color": "#2a5c8c", "lw": 2.2, "label": "L1 CEGB"},
    "L2_bogleheads_67ntsx": {"color": "#8fa8c2", "lw": 1.6, "label": "L2 Bogleheads 67% NTSX"},
    "B4_zroz_instead_of_tmf": {"color": "#1e7b33", "lw": 2.6, "label": "B4 ZROZ"},
    "T1_gold_heavy": {"color": "#e89b2a", "lw": 2.1, "label": "T1 gold-heavy"},
    "B2_tmf10_balanced": {"color": "#c1272d", "lw": 2.1, "label": "B2 TMF10"},
    "B5_no_duration": {"color": "#7f3c8d", "lw": 1.9, "label": "B5 no duration"},
}

SCATTER_COLORS = {
    "B": "#1e7b33",
    "T": "#e89b2a",
    "L": "#2a5c8c",
    "M": "#666666",
    "S": "#1a1a1a",
}

EXCLUDE_SCATTER = {"M2_dbmf_no_rsst", "M3_kmlm_dbmf_blend"}


@dataclass
class Series:
    slug: str
    label: str
    dates: np.ndarray
    equity: np.ndarray
    drawdown: np.ndarray
    cagr: float
    mdd: float
    sharpe: float
    calmar: float
    end_val: float


def apply_style() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "IBM Plex Sans", "Arial", "DejaVu Sans"],
        "font.size": 10.5,
        "axes.titlesize": 14,
        "axes.titleweight": "semibold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#cccccc",
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": "#eeeeee",
        "grid.linewidth": 0.7,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.frameon": False,
        "savefig.dpi": 150,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })


def ts_to_dt(timestamps: list[float]) -> np.ndarray:
    arr = np.asarray(timestamps, dtype=np.float64)
    if arr.size and arr.max() > 1e11:
        arr = arr / 1000.0
    return np.array([datetime.fromtimestamp(float(t), tz=timezone.utc) for t in arr])


def load_series() -> list[Series]:
    series: list[Series] = []
    for path in sorted(DATA_DIR.glob("backtest_*.json")):
        blob = json.loads(path.read_text())
        response = blob["response"]
        hist = response["charts"]["history"]
        dd = response["charts"]["drawdown"]
        dates = ts_to_dt(hist[0])
        for idx, portfolio in enumerate(blob["portfolios"]):
            stats = response["stats"][idx]
            series.append(Series(
                slug=portfolio["slug"],
                label=portfolio["label"],
                dates=dates,
                equity=np.asarray(hist[idx + 1], dtype=np.float64),
                drawdown=np.asarray(dd[idx + 1], dtype=np.float64),
                cagr=float(stats["cagr"]),
                mdd=float(stats["max_drawdown"]),
                sharpe=float(stats["sharpe"]),
                calmar=float(stats.get("calmar", 0.0)),
                end_val=float(stats["end_val"]),
            ))
    if not any(s.slug == "spy_1x" for s in series):
        series.append(fetch_spy_series())
    return series


def fetch_spy_series() -> Series:
    payload = {
        "start_date": "1987-12-30",
        "end_date": "2100-01-01",
        "start_val": 10000,
        "adj_inflation": False,
        "cashflow": 0,
        "cashflow_freq": "Yearly",
        "cashflow_offset": 0,
        "match_first_portfolio_income_cashflows": False,
        "one_time_cashflows": [],
        "rolling_window": 60,
        "withdrawal_surface_include": False,
        "withdrawal_surface_projection": "NONE",
        "withdrawal_surface_projection_min_years": 10,
        "withdrawal_surface_start_years": 5,
        "withdrawal_surface_end_years": 50,
        "withdrawal_surface_step_years": 1,
        "cashflow_legs": [],
        "backtests": [{
            "invest_dividends": True,
            "rebalance_freq": "Monthly",
            "rebalance_offset": 0,
            "allocation": {"SPYSIM": 100.0},
            "drag": 0.0945,
            "absolute_dev": 0,
            "relative_dev": 0,
        }],
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_BACKTEST, data=body, method="POST", headers={
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
    })
    with urllib.request.urlopen(req, timeout=180) as resp:
        response = json.loads(resp.read())
    hist = response["charts"]["history"]
    dd = response["charts"]["drawdown"]
    stats = response["stats"][0]
    return Series(
        slug="spy_1x",
        label="SPY 1x buy-hold",
        dates=ts_to_dt(hist[0]),
        equity=np.asarray(hist[1], dtype=np.float64),
        drawdown=np.asarray(dd[1], dtype=np.float64),
        cagr=float(stats["cagr"]),
        mdd=float(stats["max_drawdown"]),
        sharpe=float(stats["sharpe"]),
        calmar=float(stats.get("calmar", 0.0)),
        end_val=float(stats["end_val"]),
    )


def title(ax, main: str, subtitle: str = WINDOW_LABEL) -> None:
    ax.text(0.0, 1.08, main, transform=ax.transAxes, fontsize=14,
            weight="semibold", color="#1a1a1a", va="bottom", ha="left")
    ax.text(0.0, 1.02, subtitle, transform=ax.transAxes, fontsize=10,
            color="#888888", va="bottom", ha="left")


def dollar_fmt(value: float, _pos=None) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}k"
    return f"${value:.0f}"


def pct_fmt(value: float, _pos=None) -> str:
    return f"{value:.0f}%"


def selected(series: list[Series]) -> list[Series]:
    by_slug = {s.slug: s for s in series}
    return [by_slug[slug] for slug in STYLE]


def plot_equity(series: list[Series]) -> None:
    fig, ax = plt.subplots(figsize=(13, 7.5))
    for s in sorted(selected(series), key=lambda x: -x.end_val):
        st = STYLE[s.slug]
        end_label = f"${s.end_val / 1_000_000:.2f}M" if s.end_val >= 1_000_000 else f"${s.end_val / 1000:.0f}k"
        ax.plot(s.dates, s.equity, color=st["color"], lw=st["lw"],
                label=f"{st['label']}   CAGR {s.cagr:.2f}%   {end_label}")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_fmt))
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    title(ax, "Equity growth - $10k initial")
    ax.legend(loc="upper left", labelspacing=0.55)
    ax.set_xlim(selected(series)[0].dates[0], selected(series)[0].dates[-1])
    fig.tight_layout()
    fig.savefig(POST_DIR / "testfolio_01_equity.png", bbox_inches="tight")
    plt.close(fig)


def plot_drawdown(series: list[Series]) -> None:
    fig, ax = plt.subplots(figsize=(13, 5.6))
    for s in sorted(selected(series), key=lambda x: x.mdd):
        st = STYLE[s.slug]
        ax.plot(s.dates, s.drawdown, color=st["color"], lw=st["lw"],
                label=f"{st['label']}   MDD {s.mdd:.1f}%")
    spy = next(s for s in series if s.slug == "spy_1x")
    ax.axhline(spy.mdd, color="#bbbbbb", linestyle="--", linewidth=0.8)
    ax.axhline(0, color="#cccccc", linewidth=0.8)
    ax.yaxis.set_major_formatter(FuncFormatter(pct_fmt))
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    title(ax, "Drawdown - peak to trough")
    ax.legend(loc="lower right", ncol=2, labelspacing=0.5, columnspacing=1.2)
    ax.set_xlim(selected(series)[0].dates[0], selected(series)[0].dates[-1])
    fig.tight_layout()
    fig.savefig(POST_DIR / "testfolio_02_drawdown.png", bbox_inches="tight")
    plt.close(fig)


def rolling_cagr(equity: np.ndarray, years: int) -> np.ndarray:
    n = years * 252
    if len(equity) <= n:
        return np.array([])
    return ((equity[n:] / equity[:-n]) ** (1.0 / years) - 1.0) * 100.0


def plot_rolling(series: list[Series]) -> None:
    fig, axs = plt.subplots(2, 2, figsize=(15, 9.5), sharex=True)
    for years, ax in [(5, axs[0, 0]), (10, axs[0, 1]), (15, axs[1, 0]), (20, axs[1, 1])]:
        n = years * 252
        for s in selected(series):
            roll = rolling_cagr(s.equity, years)
            if roll.size == 0:
                continue
            st = STYLE[s.slug]
            ax.plot(s.dates[n:], roll, color=st["color"], lw=st["lw"], label=st["label"], alpha=0.93)
        ax.axhline(0, color="#cccccc", linewidth=0.8)
        ax.set_title(f"Rolling {years}-year CAGR", loc="left", fontsize=11.5, weight="semibold")
        ax.yaxis.set_major_formatter(FuncFormatter(pct_fmt))
        ax.xaxis.set_major_locator(mdates.YearLocator(5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.04),
               ncol=4, frameon=False, handlelength=2.2, columnspacing=1.5)
    fig.text(0.005, 0.985, "Rolling CAGR consistency", fontsize=15, weight="semibold", ha="left", va="top")
    fig.text(0.005, 0.955, WINDOW_LABEL, fontsize=10, color="#888888", ha="left", va="top")
    fig.tight_layout(rect=[0, 0.04, 1, 0.93])
    fig.savefig(POST_DIR / "testfolio_04_rolling_grid.png", bbox_inches="tight")
    plt.close(fig)


def plot_scatter(series: list[Series]) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 7.8))
    long_window = [s for s in series if s.slug not in EXCLUDE_SCATTER]
    spy = next(s for s in long_window if s.slug == "spy_1x")
    xlim = (min(s.mdd for s in long_window) - 4, -20)
    ylim = (min(s.cagr for s in long_window) - 0.8, max(s.cagr for s in long_window) + 1.2)
    spy_y_norm = (spy.cagr - ylim[0]) / (ylim[1] - ylim[0])
    ax.axvspan(spy.mdd, xlim[1], ymin=spy_y_norm, ymax=1.0, color="#2e8b57", alpha=0.08)
    ax.axvline(spy.mdd, color="#bbbbbb", linestyle="--", linewidth=0.8)
    ax.axhline(spy.cagr, color="#bbbbbb", linestyle="--", linewidth=0.8)
    for s in long_window:
        family = s.slug[:1].upper()
        color = SCATTER_COLORS.get(family, "#666666")
        if s.slug == "spy_1x":
            color = STYLE["spy_1x"]["color"]
        marker = "X" if s.slug == "spy_1x" else "o"
        size = 210 if s.slug in STYLE else 95
        ax.scatter(s.mdd, s.cagr, s=size, c=color, marker=marker, edgecolors="white", linewidths=1.5, zorder=3)
        short = s.slug.replace("_instead_of_tmf", "").replace("_balanced", "").replace("_proxy", "")
        short = short.split("_")[0] if s.slug != "spy_1x" else "SPY"
        ax.annotate(short, (s.mdd, s.cagr), xytext=(8, 4), textcoords="offset points", fontsize=8.7, color=color)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.xaxis.set_major_formatter(FuncFormatter(pct_fmt))
    ax.yaxis.set_major_formatter(FuncFormatter(pct_fmt))
    ax.set_xlabel("Max drawdown")
    ax.set_ylabel("CAGR")
    title(ax, "CAGR vs Max drawdown - long-window Pareto frontier")
    ax.text(spy.mdd - 0.5, ylim[1] - 0.2, "Beats SPY on both", color="#1e7b33", weight="semibold", ha="right", va="top")
    fig.tight_layout()
    fig.savefig(POST_DIR / "testfolio_03_scatter.png", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    apply_style()
    series = load_series()
    if len(series) != 15:
        raise SystemExit(f"expected 15 series after adding SPY, got {len(series)}")
    plot_equity(series)
    plot_drawdown(series)
    plot_scatter(series)
    plot_rolling(series)
    print(f"wrote Post 2 long-window charts to {POST_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
