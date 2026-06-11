#!/usr/bin/env python3
"""g07 — global discussion figures (g01..g10), from saved artifacts only.

Style mirrors s07 (figsize (11, 6.2), dpi 180, log equity, benchmark black &
thicker — benchmark here is VT).
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
from studies.return_stacked_core.discussion.s07_figures import (  # noqa: E402
    C, FIGSIZE, _drawdown, _equity, _log_axis, _save,
)

PRIMARY_EPISODES = [
    "Dot-com bust", "2003-07 bull", "GFC", "QE bull", "Taper tantrum",
    "China/oil correction", "Q4-2018", "Covid crash", "Inflation/rates shock",
    "AI bull",
]


def load_curves() -> pd.DataFrame:
    df = pd.read_parquet(dd.SERIES_DIR / "global_portfolio_equity.parquet")
    df.columns = [c.split("|", 1)[0] for c in df.columns]
    return df


def g01(primary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for col, label, color, lw in [
        ("VTSIM", "VT (global equity)", C["benchmark"], 2.2),
        ("SPYSIM", "SPY (US)", C["primary"], 1.4),
        ("VXUSSIM", "VXUS (intl ex-US)", C["orange"], 1.4),
        ("GLDSIM", "Gold", C["yellow"], 1.4),
        ("MFBLEND", "Managed futures", C["green"], 1.4),
        ("ZROZSIM", "ZROZ", C["teal"], 1.4),
    ]:
        eq = _equity(primary[col])
        ax.plot(eq.index, eq / eq.iloc[0], label=label, color=color, lw=lw)
    _log_axis(ax)
    ax.set_title("Global building blocks, 2000-2026 (simulated, growth of $1, log)")
    ax.legend(loc="upper left")
    _save(fig, "g01_global_components_equity_log.png")


def g02(primary: pd.DataFrame, curves: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    vt = _equity(primary["VTSIM"])
    ax.plot(vt.index, vt / vt.iloc[0], label="VT buy & hold", color=C["benchmark"], lw=2.2)
    for cfg, label, color in [
        ("G0", "CORE-GLOBAL 20/15/20/20/25", C["primary"]),
        ("G10", "Half-intl 27.5/7.5/30/10/25", C["green"]),
        ("G1", "US CORE 35/40/25", C["secondary"]),
        ("G12", "66/34 VTI/VEA", C["purple"]),
    ]:
        eq = curves[cfg].dropna()
        ax.plot(eq.index, eq / eq.iloc[0], label=label, color=color, lw=1.7)
    _log_axis(ax)
    ax.set_title("Global stacked portfolios vs VT, 2000-2026 (simulated, log)")
    ax.legend(loc="upper left")
    _save(fig, "g02_global_portfolios_vs_vt.png")


def g03(primary: pd.DataFrame, curves: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    vt_dd = _drawdown(_equity(primary["VTSIM"]))
    ax.plot(vt_dd.index, vt_dd, color=C["benchmark"], lw=2.0, label="VT")
    for cfg, label, color in [("G0", "CORE-GLOBAL", C["primary"]),
                              ("G1", "US CORE", C["secondary"])]:
        ddw = _drawdown(curves[cfg].dropna())
        ax.plot(ddw.index, ddw, color=color, lw=1.6, label=label)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.grid(alpha=0.25)
    ax.set_title("Underwater, 2000-2026: VT vs global core vs US core (simulated)")
    ax.legend(loc="lower right")
    _save(fig, "g03_global_underwater.png")


def _episode_bars_global(table: pd.DataFrame, assets: list[str], colors: list[str],
                         title: str, fname: str) -> None:
    sub = table[(table["window"] == "primary") & table["asset"].isin(assets)]
    episodes = [e for e in PRIMARY_EPISODES if e in set(sub["episode"])]
    fig, axes = plt.subplots(3, 4, figsize=(13, 8))
    for k, episode in enumerate(episodes):
        ax = axes[k // 4][k % 4]
        ep = sub[sub["episode"] == episode].set_index("asset").reindex(assets)
        ax.bar(range(len(assets)), ep["total_return"].to_numpy(float), color=colors)
        ax.axhline(0, color="#444", lw=0.8)
        ax.set_xticks(range(len(assets)))
        ax.set_xticklabels(assets, rotation=60, fontsize=6.5, ha="right")
        ax.set_title(episode, fontsize=8.5)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
        ax.tick_params(axis="y", labelsize=7)
        ax.grid(alpha=0.2, axis="y")
    for k in range(len(episodes), 12):
        axes[k // 4][k % 4].axis("off")
    fig.suptitle(title, fontsize=12)
    _save(fig, fname)


def g06_rolling() -> None:
    roll = pd.read_csv(dd.TABLES_DIR / "global_corr_rolling_252d.csv",
                       parse_dates=["date"]).set_index("date")
    fig, ax = plt.subplots(figsize=FIGSIZE)
    palette = [C["primary"], C["indigo"], C["yellow"], C["green"], C["teal"],
               C["orange"]]
    for color, col in zip(palette, roll.columns):
        label = col.replace("SIM", "").replace("~", " ~ ").replace("MFBLEND", "MF")
        ax.plot(roll.index, roll[col], lw=1.1, color=color, label=label)
    ax.axhline(0, color="#000", lw=1.6)
    ax.set_ylim(-1, 1)
    ax.grid(alpha=0.25)
    ax.set_title("Rolling 252-day correlations — note SPY~VEA/VXUS pinned near +0.9")
    ax.legend(loc="lower left", ncols=3, fontsize=8.5)
    _save(fig, "g06_global_rolling_corr.png")


def g07_vt_down() -> None:
    cap = pd.read_csv(dd.TABLES_DIR / "global_crisis_capture.csv")
    assets = ["VTSIM", "SPYSIM", "VEASIM", "VWOSIM", "GLDSIM", "MFBLEND", "ZROZSIM"]
    labels = ["VT", "SPY", "VEA", "VWO (EM)", "Gold", "Mgd futures", "ZROZ"]
    conditions = [("vt_down_months", "VT-down months", C["orange"]),
                  ("vt_worst_decile", "VT worst-decile months", C["secondary"])]
    width = 0.38
    fig, ax = plt.subplots(figsize=FIGSIZE)
    x = np.arange(len(assets))
    for i, (cond, label, color) in enumerate(conditions):
        sub = cap[cap["condition"] == cond].set_index("asset").reindex(assets)
        ax.bar(x + (i - 0.5) * width, sub["mean_monthly_return"], width,
               color=color, label=f"{label} (n={int(sub['n_months'].max())})")
    ax.axhline(0, color="#444", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1%}"))
    ax.grid(alpha=0.25, axis="y")
    ax.set_title("Mean monthly return when global stocks fall, 2000-2026 "
                 "(simulated) — intl equity falls WITH the market")
    ax.legend()
    _save(fig, "g07_vt_down_months.png")


def g08_price_curve() -> None:
    pc = pd.read_csv(dd.TABLES_DIR / "global_intl_price_curve.csv")
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for window, color in [("primary", C["primary"]), ("1988", C["secondary"])]:
        sub = pc[pc["window"] == window]
        ax.plot(sub["intl_floor_pct"], sub["sharpe"], marker="o", color=color,
                label=f"best Sharpe given intl floor ({window} window)")
    ax.set_xlabel("minimum NTSD+RSIT allocation (%)")
    ax.set_ylabel("best achievable Sharpe")
    ax.grid(alpha=0.25)
    ax.axvline(35, color="#888", ls=":", lw=1.2)
    ax.text(35.5, ax.get_ylim()[0] + 0.005, "CORE-GLOBAL intl total (35%)",
            fontsize=8.5, color="#555")
    ax.set_title("The price of going global: best Sharpe vs required international allocation")
    ax.legend()
    _save(fig, "g08_intl_price_curve.png")


def g09_frontier() -> None:
    grid = pd.read_csv(dd.TABLES_DIR / "global_simplex_grid.csv")
    intl = grid["ntsd_pct"] + grid["rsit_pct"]
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sc = ax.scatter(grid["mdd"].abs(), grid["cagr"], c=intl, cmap="viridis",
                    s=8, alpha=0.7)
    for node, label in [("20/15/20/20/25", "CORE-GLOBAL"),
                        ("27.5/7.5/30/10/25", None),  # not on 5% grid
                        ("35/0/40/0/25", "US CORE shape"),
                        ("0/0/0/0/100", "100% ZROZ")]:
        row = grid[grid["node"] == node]
        if row.empty:
            continue
        row = row.iloc[0]
        ax.scatter([abs(row["mdd"])], [row["cagr"]], s=120, facecolors="none",
                   edgecolors=C["secondary"], lw=1.8)
        if label:
            ax.annotate(label, (abs(row["mdd"]), row["cagr"]),
                        textcoords="offset points", xytext=(8, 4), fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("max drawdown (absolute)")
    ax.set_ylabel("CAGR")
    ax.grid(alpha=0.25)
    fig.colorbar(sc, ax=ax, label="NTSD+RSIT weight (%)")
    ax.set_title("All 10,626 global mixes, 2000-2026: more international (bright) "
                 "= lower CAGR at similar drawdown")
    _save(fig, "g09_global_frontier.png")


def g11_extended() -> None:
    path = dd.SERIES_DIR / "global_portfolio_equity_extended.parquet"
    if not path.exists():
        print("g11 skipped — extended curves missing", file=sys.stderr)
        return
    ext = pd.read_parquet(path)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for col, label, color, lw in [
        ("100% VT", "VT", C["benchmark"], 2.2),
        ("CORE-GLOBAL-EXT-HAIRCUT 20/15/20/20/25", "CORE-GLOBAL (haircut MF)",
         C["primary"], 1.7),
        ("US-CORE-EXT-HAIRCUT 35/40/25", "US CORE (haircut MF)", C["secondary"], 1.7),
        ("60/40 VT/IEF", "60/40 VT/IEF", C["teal"], 1.4),
    ]:
        eq = ext[col].dropna()
        ax.plot(eq.index, eq / eq.iloc[0], label=label, color=color, lw=lw)
    _log_axis(ax)
    ax.set_title("1970-2026 global extension - LOW FIDELITY (academic proxies "
                 "pre-1988, haircut applied), log scale")
    ax.legend(loc="upper left")
    _save(fig, "g11_global_extended_1970.png")


def g12_ablations() -> None:
    abl = pd.read_csv(dd.TABLES_DIR / "global_ablations_primary.csv")
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.scatter(abl["mdd"].abs(), abl["cagr"], s=60, color=C["primary"])
    core = abl[abl["id"] == "G0"].iloc[0]
    ax.scatter([abs(core["mdd"])], [core["cagr"]], marker="*", s=420,
               color=C["secondary"], edgecolor="#000", zorder=5)
    for _, row in abl.iterrows():
        ax.annotate(row["config"], (abs(row["mdd"]), row["cagr"]),
                    textcoords="offset points", xytext=(7, 4), fontsize=7.5)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("max drawdown (absolute)")
    ax.set_ylabel("CAGR")
    ax.grid(alpha=0.25)
    ax.set_title("Global ablations, 2000-2026: every variant vs CORE-GLOBAL (star)")
    _save(fig, "g12_global_ablation_summary.png")


def main() -> int:
    primary = pd.read_parquet(dd.SERIES_DIR / "global_primary_returns.parquet")
    curves = load_curves()
    comp = pd.read_csv(dd.TABLES_DIR / "global_episodes_components.csv")
    prod = pd.read_csv(dd.TABLES_DIR / "global_episodes_products.csv")

    g01(primary)
    g02(primary, curves)
    g03(primary, curves)
    _episode_bars_global(
        comp, ["VT", "SPY", "VEA (dev ex-US)", "VWO (EM)", "GLD", "MFBLEND", "ZROZ"],
        [C["benchmark"], C["primary"], C["indigo"], C["pink"], C["yellow"],
         C["green"], C["teal"]],
        "Global component returns by episode, 2000-2026 (simulated)",
        "g04_global_episode_bars_components.png",
    )
    _episode_bars_global(
        prod, ["VT", "NTSD", "NTSI", "RSIT", "CORE-GLOBAL 20/15/20/20/25",
               "US CORE 35/40/25"],
        [C["benchmark"], C["primary"], C["indigo"], C["orange"], C["green"],
         C["secondary"]],
        "Global products by episode, 2000-2026 (simulated)",
        "g05_global_episode_bars_products.png",
    )
    g06_rolling()
    g07_vt_down()
    g08_price_curve()
    g09_frontier()
    g11_extended()
    g12_ablations()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
