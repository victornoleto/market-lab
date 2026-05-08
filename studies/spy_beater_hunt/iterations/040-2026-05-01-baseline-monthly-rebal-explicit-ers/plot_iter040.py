#!/usr/bin/env python3
"""Generate iter 040 plots: equity curves, drawdowns, Pareto scatter.

Same visual style as iter 039 reddit_plot_*.png but using iter 040 data
(monthly rebal + explicit ERs).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"

NAME_MAP = {
    "spy_1x": "SPY 1x",
    "popular_50_25_25": "Popular 50/25/25 SSO/GLD/ZROZ",
    "l1_sleeping_pills": "Sleeping Pills (L1 CEGB)",
    "l2_bogleheads": "Bogleheads 67 NTSX (L2)",
    "b4_conservative": "Conservative (B4 ZROZ)",
    "b2_balanced": "Balanced (B2)",
    "t1_aggressive": "Aggressive (T1)",
}

ORDER = [
    "SPY 1x",
    "Popular 50/25/25 SSO/GLD/ZROZ",
    "Sleeping Pills (L1 CEGB)",
    "Bogleheads 67 NTSX (L2)",
    "Conservative (B4 ZROZ)",
    "Balanced (B2)",
    "Aggressive (T1)",
]

COLORS = {
    "SPY 1x": "#666666",
    "Popular 50/25/25 SSO/GLD/ZROZ": "#9b59b6",
    "Sleeping Pills (L1 CEGB)": "#3498db",
    "Bogleheads 67 NTSX (L2)": "#1abc9c",
    "Conservative (B4 ZROZ)": "#27ae60",
    "Balanced (B2)": "#e67e22",
    "Aggressive (T1)": "#e74c3c",
}

with open(SCRIPT_DIR / "metrics.json") as f:
    metrics = json.load(f)

# Build equity curves dict from iter 040 batch JSONs
equity_curves: dict[str, pd.Series] = {}
for letter in ("a", "b"):
    path = DATA_DIR / f"backtest_buyhold_{letter}.json"
    with open(path) as f:
        d = json.load(f)
    timestamps = d["response"]["charts"]["history"][0]
    dates = pd.to_datetime(timestamps, unit="s")
    for i, p in enumerate(d["portfolios"]):
        name = NAME_MAP[p["slug"]]
        vals = np.array(d["response"]["charts"]["history"][i + 1], dtype=float)
        equity_curves[name] = pd.Series(vals, index=dates)

# ==============================
# PLOT 1 — Equity curves (log)
# ==============================
fig, ax = plt.subplots(figsize=(13, 7))
for name in ORDER:
    if name not in equity_curves:
        continue
    s = equity_curves[name]
    m = metrics[name]
    label = (f"{name}: {m['cagr']:.1f}% CAGR / {m['mdd']:.0f}% MDD / "
             f"Sh {m['sharpe']:.2f}")
    ax.plot(s.index, s.values, label=label, color=COLORS[name],
            linewidth=2.0 if name in ("SPY 1x",) else 1.5,
            linestyle="--" if name == "SPY 1x" else "-",
            alpha=0.95)
ax.set_yscale("log")
ax.set_xlabel("Date")
ax.set_ylabel("Portfolio value ($, log scale, $10k start at 1987-12-31)")
ax.set_title("Iter 040 — Equity curves (Monthly rebal + explicit ERs)\n"
             "1987-12-31 → 2026-04-30, dividends reinvested")
ax.grid(True, alpha=0.3, which="both")
ax.legend(loc="upper left", fontsize=9)
ax.xaxis.set_major_locator(mdates.YearLocator(5))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.tight_layout()
out = SCRIPT_DIR / "plot_1_equity.png"
plt.savefig(out, dpi=110, bbox_inches="tight")
plt.close()
print(f"saved {out}")

# ==============================
# PLOT 2 — Drawdowns
# ==============================
fig, ax = plt.subplots(figsize=(13, 7))
for name in ORDER:
    if name not in equity_curves:
        continue
    s = equity_curves[name]
    peak = s.cummax()
    dd = (s / peak - 1) * 100
    label = f"{name}: max DD {metrics[name]['mdd']:.1f}%"
    ax.plot(dd.index, dd.values, label=label, color=COLORS[name],
            linewidth=1.8 if name == "SPY 1x" else 1.4,
            linestyle="--" if name == "SPY 1x" else "-", alpha=0.9)
ax.set_xlabel("Date")
ax.set_ylabel("Drawdown (%)")
ax.set_title("Iter 040 — Drawdowns (Monthly rebal + ERs)\n"
             "1987-12-31 → 2026-04-30")
ax.grid(True, alpha=0.3)
ax.axhline(y=-25, color="gray", linestyle=":", alpha=0.5)
ax.axhline(y=-50, color="gray", linestyle=":", alpha=0.5)
ax.legend(loc="lower left", fontsize=9)
ax.set_ylim(-65, 5)
ax.xaxis.set_major_locator(mdates.YearLocator(5))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.tight_layout()
out = SCRIPT_DIR / "plot_2_drawdown.png"
plt.savefig(out, dpi=110, bbox_inches="tight")
plt.close()
print(f"saved {out}")

# ==============================
# PLOT 3 — CAGR vs MDD scatter (iter 039 vs 040)
# ==============================
with open("/tmp/testfolio_metrics_common_start.json") as f:
    iter039_metrics = json.load(f)

# Use raw testfolio sharpes from iter 039 (re-extracted)
ITER039_DATA = Path("/var/www/pessoal/ai-trade/studies/spy_beater_hunt/iterations/"
                    "039-2026-04-30-reddit-comparison-spy-lrs-vs-static-stack/testfolio_data")
iter039_corrected: dict[str, dict] = {}
for letter in ("a", "b"):
    with open(ITER039_DATA / f"backtest_buyhold_{letter}.json") as f:
        d = json.load(f)
    for p, s in zip(d["portfolios"], d["response"]["stats"]):
        iter039_corrected[NAME_MAP[p["slug"]]] = {
            "cagr": s["cagr"], "mdd": s["max_drawdown"],
            "sharpe": s["sharpe"]}

fig, ax = plt.subplots(figsize=(11, 7))
for name in ORDER:
    if name not in metrics or name not in iter039_corrected:
        continue
    a = iter039_corrected[name]
    b = metrics[name]
    # iter 039 = circle (yearly), iter 040 = square (monthly)
    ax.scatter(-a["mdd"], a["cagr"], s=120, color=COLORS[name],
               edgecolor="gray", linewidth=1.0, marker="o", alpha=0.55)
    ax.scatter(-b["mdd"], b["cagr"], s=180, color=COLORS[name],
               edgecolor="black", linewidth=1.5, marker="s",
               label=f"{name}: Δ {b['cagr']-a['cagr']:+.2f}pp / Δ MDD {b['mdd']-a['mdd']:+.2f}pp",
               zorder=5, alpha=0.92)
    # arrow from iter 039 to iter 040
    ax.annotate("", xy=(-b["mdd"], b["cagr"]), xytext=(-a["mdd"], a["cagr"]),
                arrowprops={"arrowstyle": "->", "color": COLORS[name],
                            "alpha": 0.6, "lw": 1.5})

ax.axhline(y=metrics["SPY 1x"]["cagr"], color="#666666", linestyle=":", alpha=0.5)
ax.set_xlabel("|Max Drawdown| (%, smaller = better)")
ax.set_ylabel("CAGR (%, larger = better)")
ax.set_title("Iter 040 vs 039 — Pareto shift (Yearly+no-ER → Monthly+ERs)\n"
             "circle=iter 039, square=iter 040, arrow shows shift")
ax.grid(True, alpha=0.3)
ax.invert_xaxis()
ax.legend(loc="lower left", fontsize=9)
plt.tight_layout()
out = SCRIPT_DIR / "plot_3_pareto_shift.png"
plt.savefig(out, dpi=110, bbox_inches="tight")
plt.close()
print(f"saved {out}")
