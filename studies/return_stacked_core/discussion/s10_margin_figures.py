#!/usr/bin/env python3
"""s10 — figures for POST_MARGIN.md (trend<->gold dial + IBKR margin).

Offline, deterministic: curves are rebuilt from the canonical sleeve-return
matrix via ``engine`` (same source that reproduces the published anchor) and
the metric points are read from ``tables/margin_sweep_matched.csv`` written by
s09. Style matches s07_figures.py (figsize, dpi 180, log equity, SPY black).

Four figures:
  20 — equity curves: the dial (gold/balanced/MF) + NTSX vs SPY (log).
  21 — underwater: same set, drawdown from running peak (crisis valleys).
  22 — the dial as CAGR vs MDD (unlevered): the smooth trade + NTSX dominated.
  23 — margin-call danger: account leverage vs drawdown magnitude — the book's
       historical MDD rising while the maintenance call-thresholds fall, and
       where they cross `[leverage_for_the_long_run, p.13]`,
       `[systematic_trading, p.185-188]`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402
from studies.return_stacked_core.discussion import engine  # noqa: E402
from studies.return_stacked_core.discussion.s09_margin_sweep import (  # noqa: E402
    FINANCING_LEG, MAINTENANCE, PORTFOLIOS, apply_cost_drags, margin_call_drop,
)

FIGSIZE = (11, 6.2)
DPI = 180
C = {"benchmark": "#000", "primary": "#0d6efd", "secondary": "#dc3545",
     "green": "#198754", "yellow": "#ffc107", "teal": "#20c997",
     "orange": "#fd7e14", "purple": "#6f42c1"}

# Dial display order (gold -> MF) + colours.
DIAL = [
    ("RSST25/GDE50/ZROZ25 (gold-heavy)", "Gold-heavy (RSST25/GDE50)", C["yellow"]),
    ("RSST37.5/GDE37.5/ZROZ25 (balanced)", "Balanced (RSST37.5/GDE37.5)", C["primary"]),
    ("RSST50/GDE25/ZROZ25 (MF-heavy)", "MF-heavy (RSST50/GDE25)", C["green"]),
    ("RSST25/NTSX25/GDE25/ZROZ25 (+NTSX)", "+NTSX (25/25/25/25)", C["teal"]),
]
BALANCED = "RSST37.5/GDE37.5/ZROZ25 (balanced)"
LEVERED_SHOW = [(1.00, C["primary"]), (1.25, C["teal"]),
                (1.50, C["orange"]), (2.00, C["secondary"])]


def _base() -> pd.DataFrame:
    base = apply_cost_drags(dd.load_primary_returns().copy())
    cashx = dd.load_cache_returns(["CASHX"])["CASHX"].reindex(base.index)
    base[FINANCING_LEG] = cashx + dd.FINANCING_SPREAD_ANNUAL / dd.TRADING_DAYS
    return base


def _curve(base: pd.DataFrame, weights: dict, lev: float = 1.0) -> pd.Series:
    w = {k: v * lev for k, v in weights.items()}
    if lev != 1.0:
        w[FINANCING_LEG] = 1.0 - lev
    eq = engine.rebalanced_equity(base, w, "M")
    return eq / eq.iloc[0]


def _spy(base: pd.DataFrame) -> pd.Series:
    eq = engine.rebalanced_equity(base, {"SPYSIM": 1.0}, "M")
    return eq / eq.iloc[0]


def _save(fig, name: str) -> None:
    dd.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(dd.FIGURES_DIR / name, dpi=DPI)
    plt.close(fig)
    print("wrote", name)


def _log_axis(ax) -> None:
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}x"))
    ax.grid(alpha=0.25)


def _pct_axis(ax) -> None:
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.grid(alpha=0.25)


def fig20(base: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    spy = _spy(base)
    ax.plot(spy.index, spy, label="100% SPY", color=C["benchmark"], lw=2.2)
    for key, label, color in DIAL:
        eq = _curve(base, PORTFOLIOS[key])
        ax.plot(eq.index, eq, label=f"{label}  ->  {eq.iloc[-1]:.0f}x", color=color, lw=1.6)
    _log_axis(ax)
    ax.set_title("The trend<->gold dial vs SPY, 2000-2026 (simulated, growth of $1, log)")
    ax.legend(loc="upper left", fontsize=9)
    _save(fig, "20_dial_equity_log.png")


def fig21(base: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True, sharey=True)
    spy = _spy(base)
    spy_dd = spy / spy.cummax() - 1.0
    for ax, (key, label, color) in zip(axes.flat, DIAL):
        eq = _curve(base, PORTFOLIOS[key])
        ddw = eq / eq.cummax() - 1.0
        ax.fill_between(spy_dd.index, spy_dd.values, 0, color=C["benchmark"], alpha=0.12)
        ax.plot(spy_dd.index, spy_dd.values, color=C["benchmark"], lw=1.3, label="100% SPY")
        ax.fill_between(ddw.index, ddw.values, 0, color=color, alpha=0.35)
        ax.plot(ddw.index, ddw.values, color=color, lw=1.4, label=label)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
        ax.grid(alpha=0.25)
        ax.set_title(f"{label}  —  worst {ddw.min():.0%}  (SPY worst {spy_dd.min():.0%})", fontsize=10)
        ax.legend(loc="lower left", fontsize=8.5)
    fig.suptitle("Underwater chart, 2000-2026: each mix vs SPY, drawdown from running peak (simulated)",
                 fontsize=12)
    _save(fig, "21_dial_underwater.png")


def fig22() -> None:
    df = pd.read_csv(dd.TABLES_DIR / "margin_sweep_matched.csv")
    u = df[df["leverage"] == 1.0]
    fig, ax = plt.subplots(figsize=FIGSIZE)
    dial_pts = u[~u["portfolio"].str.startswith("100%")].set_index("portfolio")
    # faint line through the 3-fund dial in gold->MF order shows the trade-off
    line = dial_pts.loc[[k for k, _, _ in DIAL[:3]]]
    ax.plot(line["mdd"].abs(), line["cagr"], color="#888", lw=1.2, ls="--", zorder=1)
    for key, label, color in DIAL:
        row = dial_pts.loc[key]
        ax.scatter([abs(row["mdd"])], [row["cagr"]], s=150, color=color,
                   edgecolor="#000", zorder=5)
        ax.annotate(f"{label}\nSharpe {row['sharpe']:.2f}", (abs(row["mdd"]), row["cagr"]),
                    textcoords="offset points", xytext=(10, -4), fontsize=8.5)
    spy = u[u["portfolio"].str.startswith("100%")].iloc[0]
    ax.scatter([abs(spy["mdd"])], [spy["cagr"]], marker="X", s=140,
               color=C["benchmark"], zorder=5)
    ax.annotate("100% SPY", (abs(spy["mdd"]), spy["cagr"]),
                textcoords="offset points", xytext=(10, -4), fontsize=8.5)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("max drawdown (absolute)")
    ax.set_ylabel("CAGR")
    ax.grid(alpha=0.25)
    ax.set_title("The dial, unlevered: more gold = more CAGR + deeper DD; more trend = the reverse")
    _save(fig, "22_dial_cagr_vs_mdd.png")


def fig23() -> None:
    df = pd.read_csv(dd.TABLES_DIR / "margin_sweep_matched.csv")
    fig, ax = plt.subplots(figsize=FIGSIZE)
    # Portfolio historical drawdown magnitude rises with leverage (3-fund dial band).
    dial_keys = [k for k, _, _ in DIAL[:3]]
    dial = df[df["portfolio"].isin(dial_keys)]
    levs = sorted(dial["leverage"].unique())
    by_lev = dial.groupby("leverage")["mdd"]
    lo, hi = (-by_lev.max()), (-by_lev.min())  # shallowest..deepest |MDD|
    ax.fill_between(levs, lo.loc[levs].values, hi.loc[levs].values, color=C["secondary"],
                    alpha=0.18, label="dial historical |MDD| (gold-heavy = deep edge)")
    bal = df[df["portfolio"] == BALANCED].set_index("leverage")["mdd"].abs()
    ax.plot(bal.index, bal.values, color=C["secondary"], lw=2.2, marker="o",
            label="balanced |MDD|")
    # Maintenance call-threshold drop magnitude falls with leverage.
    gate_colors = {0.25: C["green"], 0.30: C["orange"], 0.50: C["purple"]}
    xs = [L for L in levs if L > 1.0]
    for m in MAINTENANCE:
        ys = [-margin_call_drop(L, m) for L in xs]
        ax.plot(xs, ys, color=gate_colors[m], lw=1.6, ls="--",
                label=f"margin call @ {int(m*100)}% maintenance")
    ax.set_ylim(0, 0.9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}x"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("account margin (external leverage)")
    ax.set_ylabel("drawdown magnitude")
    ax.grid(alpha=0.25)
    ax.set_title("When does margin call you? Book drawdown (solid/shaded) vs call gates (dashed)")
    ax.legend(loc="upper right", fontsize=8.5)
    _save(fig, "23_margin_call_danger.png")


def main() -> int:
    base = _base()
    fig20(base)
    fig21(base)
    fig22()
    fig23()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
