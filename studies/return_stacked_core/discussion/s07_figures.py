#!/usr/bin/env python3
"""s07 — all discussion figures, generated from saved series/ + tables/ ONLY.

No recomputation here: if a number isn't in an artifact, it can't be in a
figure. Style follows ``regenerate_color_plots.py`` (figsize (11, 6.2),
dpi 180, log equity, SPY black & thicker).
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

FIGSIZE = (11, 6.2)
DPI = 180
C = {
    "benchmark": "#000",
    "primary": "#0d6efd",
    "secondary": "#dc3545",
    "green": "#198754",
    "yellow": "#ffc107",
    "teal": "#20c997",
    "cyan": "#0dcaf0",
    "indigo": "#6610f2",
    "purple": "#6f42c1",
    "pink": "#d63384",
    "orange": "#fd7e14",
}

PRIMARY_EPISODE_ORDER = [
    "Dot-com bust", "2003-07 bull", "GFC", "QE bull", "US downgrade / euro crisis",
    "Taper tantrum", "China/oil correction", "Q4-2018", "Covid crash",
    "Inflation/rates shock", "AI bull",
]
EXTENDED_BANDS = [
    ("Stagflation", "1973-01-11", "1974-10-03"),
    ("Volcker", "1979-10-01", "1982-08-12"),
    ("1987", "1987-08-25", "1987-12-04"),
    ("Dot-com", "2000-03-24", "2002-10-09"),
    ("GFC", "2007-10-09", "2009-03-09"),
    ("2022", "2022-01-03", "2022-10-14"),
]


def _equity(returns: pd.Series) -> pd.Series:
    return (1.0 + returns.dropna()).cumprod()


def _drawdown(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1.0


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


def load_portfolio_curves() -> pd.DataFrame:
    df = pd.read_parquet(dd.SERIES_DIR / "portfolio_equity_primary.parquet")
    df.columns = [c.split("|", 1)[0] for c in df.columns]
    return df


def fig01(primary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    spec = [("SPYSIM", "S&P 500 (SPY)", C["benchmark"], 2.2),
            ("GLDSIM", "Gold (GLD)", C["yellow"], 1.4),
            ("MFBLEND", "Managed futures (70/30 DBMF/KMLM)", C["green"], 1.4),
            ("ZROZSIM", "25y+ STRIPS (ZROZ)", C["primary"], 1.4)]
    for col, label, color, lw in spec:
        eq = _equity(primary[col])
        ax.plot(eq.index, eq / eq.iloc[0], label=label, color=color, lw=lw)
    _log_axis(ax)
    ax.set_title("The four building blocks, 2000-2026 (simulated, growth of $1, log scale)")
    ax.legend(loc="upper left")
    _save(fig, "01_components_equity_log.png")


def fig02(primary: pd.DataFrame, curves: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for col, label, color, lw in [
        ("SPYSIM", "SPY buy & hold", C["benchmark"], 2.2),
        ("GDESIM", "GDE (90% SPY + 90% gold)", C["yellow"], 1.4),
        ("RSSTSIM", "RSST (100% SPY + 100% MF)", C["green"], 1.4),
        ("NTSXSIM", "NTSX (90% SPY + 60% 7-10y)", C["teal"], 1.4),
    ]:
        eq = _equity(primary[col])
        ax.plot(eq.index, eq / eq.iloc[0], label=label, color=color, lw=lw)
    core = curves["A0"].dropna()
    ax.plot(core.index, core / core.iloc[0], label="CORE 35/40/25 (GDE/RSST/ZROZ)",
            color=C["secondary"], lw=2.0)
    _log_axis(ax)
    ax.set_title("Stacked products vs SPY, 2000-2026 (simulated, log scale)")
    ax.legend(loc="upper left")
    _save(fig, "02_products_equity_log.png")


def fig03(primary: pd.DataFrame, curves: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    spy_dd = _drawdown(_equity(primary["SPYSIM"]))
    ax.plot(spy_dd.index, spy_dd, color=C["benchmark"], lw=2.0, label="SPY")
    for cfg, label, color in [("A0", "CORE 35/40/25", C["secondary"]),
                              ("A9", "HFEA 55/45 UPRO/TMF", C["purple"])]:
        ddw = _drawdown(curves[cfg].dropna())
        ax.plot(ddw.index, ddw, color=color, lw=1.6, label=label)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.grid(alpha=0.25)
    ax.set_title("Underwater chart, 2000-2026: drawdown from running peak (simulated)")
    ax.legend(loc="lower right")
    _save(fig, "03_underwater_core_spy_hfea.png")


def _episode_bars(table: pd.DataFrame, assets: list[str], colors: list[str],
                  title: str, fname: str) -> None:
    sub = table[(table["window"] == "primary") & table["asset"].isin(assets)]
    episodes = [e for e in PRIMARY_EPISODE_ORDER if e in set(sub["episode"])]
    ncols, nrows = 4, 3
    fig, axes = plt.subplots(nrows, ncols, figsize=(13, 8), sharey=False)
    for k, episode in enumerate(episodes):
        ax = axes[k // ncols][k % ncols]
        ep = sub[sub["episode"] == episode].set_index("asset").reindex(assets)
        vals = ep["total_return"].to_numpy(dtype=float)
        ax.bar(range(len(assets)), vals, color=colors)
        ax.axhline(0, color="#444", lw=0.8)
        ax.set_xticks(range(len(assets)))
        ax.set_xticklabels(assets, rotation=60, fontsize=7, ha="right")
        start = ep["start"].dropna().iloc[0][:7] if not ep["start"].dropna().empty else ""
        ax.set_title(f"{episode}\n({start})", fontsize=8.5)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
        ax.tick_params(axis="y", labelsize=7)
        ax.grid(alpha=0.2, axis="y")
    for k in range(len(episodes), nrows * ncols):
        axes[k // ncols][k % ncols].axis("off")
    fig.suptitle(title, fontsize=12)
    _save(fig, fname)


def fig06() -> None:
    roll = pd.read_csv(dd.TABLES_DIR / "corr_rolling_252d.csv",
                       parse_dates=["date"]).set_index("date")
    fig, ax = plt.subplots(figsize=FIGSIZE)
    palette = [C["primary"], C["green"], C["secondary"], C["orange"],
               C["purple"], C["teal"]]
    for color, col in zip(palette, roll.columns):
        label = col.replace("SIM", "").replace("~", " ~ ").replace("MFBLEND", "MF")
        ax.plot(roll.index, roll[col], lw=1.1, color=color, label=label)
    ax.axhline(0, color="#000", lw=1.6)
    ax.set_ylim(-1, 1)
    ax.grid(alpha=0.25)
    ax.set_title("Rolling 252-day correlations between sleeves (simulated daily returns)")
    ax.legend(loc="lower left", ncols=3, fontsize=8.5)
    _save(fig, "06_rolling_corr_252d.png")


def fig07() -> None:
    cap = pd.read_csv(dd.TABLES_DIR / "crisis_capture.csv")
    assets = ["SPYSIM", "GLDSIM", "MFBLEND", "ZROZSIM", "BTCSIM", "CARRY_SCALED"]
    labels = ["SPY", "Gold", "Managed futures", "ZROZ", "BTC", "Carry (RSSY sleeve)"]
    conditions = [("spy_down_months", "SPY-down months", C["orange"]),
                  ("spy_worst_decile", "SPY worst-decile months", C["secondary"])]
    width = 0.38
    fig, ax = plt.subplots(figsize=FIGSIZE)
    x = np.arange(len(assets))
    for i, (cond, label, color) in enumerate(conditions):
        sub = cap[cap["condition"] == cond].set_index("asset").reindex(assets)
        n = int(sub["n_months"].max())
        ax.bar(x + (i - 0.5) * width, sub["mean_monthly_return"], width,
               color=color, label=f"{label} (n={n})")
    ax.axhline(0, color="#444", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1%}"))
    ax.grid(alpha=0.25, axis="y")
    ax.set_title("Mean monthly return when stocks fall, 2000-2026 (simulated)")
    ax.legend()
    _save(fig, "07_spy_down_months.png")


def _ternary_xy(gde: np.ndarray, rsst: np.ndarray, zroz: np.ndarray):
    total = gde + rsst + zroz
    b, c = rsst / total, zroz / total
    return b + 0.5 * c, (np.sqrt(3) / 2) * c


def fig08() -> None:
    grid = pd.read_csv(dd.TABLES_DIR / "simplex_grid.csv")
    x, y = _ternary_xy(grid["gde_pct"].to_numpy(float),
                       grid["rsst_pct"].to_numpy(float),
                       grid["zroz_pct"].to_numpy(float))
    fig, ax = plt.subplots(figsize=(11, 8.2))
    sc = ax.tripcolor(x, y, grid["sharpe"], cmap="viridis", shading="gouraud")
    plateau = grid[grid["in_plateau"]]
    px, py = _ternary_xy(plateau["gde_pct"].to_numpy(float),
                         plateau["rsst_pct"].to_numpy(float),
                         plateau["zroz_pct"].to_numpy(float))
    ax.scatter(px, py, s=26, facecolors="none", edgecolors="#fff", lw=1.0,
               label=f"plateau (Sharpe >= 95% of max, n={len(plateau)})")
    core = grid[grid["node"] == "35/40/25"].iloc[0]
    cx, cy = _ternary_xy(np.array([core["gde_pct"]], float),
                         np.array([core["rsst_pct"]], float),
                         np.array([core["zroz_pct"]], float))
    ax.scatter(cx, cy, marker="*", s=420, color=C["secondary"], edgecolor="#000",
               zorder=5, label=f"CORE 35/40/25 (Sharpe {core['sharpe']:.3f})")
    amax = grid.loc[grid["sharpe"].idxmax()]
    axx, axy = _ternary_xy(np.array([amax["gde_pct"]], float),
                           np.array([amax["rsst_pct"]], float),
                           np.array([amax["zroz_pct"]], float))
    ax.scatter(axx, axy, marker="D", s=90, color=C["orange"], edgecolor="#000",
               zorder=5, label=f"argmax {amax['node']} (Sharpe {amax['sharpe']:.3f})")
    for label, xx, yy, ha in [("100% GDE", 0, 0, "right"), ("100% RSST", 1, 0, "left"),
                              ("100% ZROZ", 0.5, np.sqrt(3) / 2 + 0.02, "center")]:
        ax.text(xx, yy - (0.035 if yy == 0 else 0), label, ha=ha, fontsize=10)
    fig.colorbar(sc, ax=ax, label="Sharpe (2000-2026, monthly rebalance)")
    ax.set_axis_off()
    ax.legend(loc="upper left")
    ax.set_title("Sharpe across every 5% GDE/RSST/ZROZ mix - a plateau, not a peak")
    _save(fig, "08_simplex_sharpe_heatmap.png")


def fig09() -> None:
    grid = pd.read_csv(dd.TABLES_DIR / "simplex_grid.csv")
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sc = ax.scatter(grid["mdd"].abs(), grid["cagr"], c=grid["zroz_pct"],
                    cmap="plasma", s=34, alpha=0.9)
    pts = grid[["mdd", "cagr", "node"]].copy()
    pts["mdd_abs"] = pts["mdd"].abs()
    pareto = []
    for _, row in pts.sort_values("mdd_abs").iterrows():
        if not pareto or row["cagr"] > pareto[-1]["cagr"]:
            pareto.append(row)
    pf = pd.DataFrame(pareto)
    ax.plot(pf["mdd_abs"], pf["cagr"], color="#333", lw=1.2, ls="--",
            label="Pareto front (min MDD for given CAGR)")
    for node, label in [("35/40/25", "CORE"), ("100/0/0", "100% GDE"),
                        ("0/100/0", "100% RSST"), ("0/0/100", "100% ZROZ")]:
        row = grid[grid["node"] == node].iloc[0]
        ax.annotate(label, (abs(row["mdd"]), row["cagr"]),
                    textcoords="offset points", xytext=(8, 4), fontsize=9)
        ax.scatter([abs(row["mdd"])], [row["cagr"]], s=110,
                   facecolors="none", edgecolors=C["secondary"], lw=1.8)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("max drawdown (absolute)")
    ax.set_ylabel("CAGR")
    ax.grid(alpha=0.25)
    fig.colorbar(sc, ax=ax, label="ZROZ weight (%)")
    ax.legend(loc="lower right")
    ax.set_title("All 231 GDE/RSST/ZROZ mixes, 2000-2026: CAGR vs max drawdown")
    _save(fig, "09_frontier_cagr_mdd.png")


def fig10(primary: pd.DataFrame, curves: pd.DataFrame) -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), sharex=True,
                                   gridspec_kw={"height_ratios": [2, 1]})
    spy = _equity(primary["SPYSIM"])
    series = [("SPY", spy / spy.iloc[0], C["benchmark"], 2.2),
              ("CORE 35/40/25", curves["A0"].dropna(), C["secondary"], 1.8),
              ("HFEA 55/45 (monthly)", curves["A9"].dropna(), C["purple"], 1.8)]
    for label, eq, color, lw in series:
        ax1.plot(eq.index, eq / eq.iloc[0], label=label, color=color, lw=lw)
        ddw = _drawdown(eq)
        ax2.plot(ddw.index, ddw, color=color, lw=lw * 0.8)
    _log_axis(ax1)
    ax1.legend(loc="upper left")
    ax1.set_title("Same leverage idea, different diversifiers: HFEA vs return stacking (simulated)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax2.grid(alpha=0.25)
    ax2.set_ylabel("drawdown")
    _save(fig, "10_hfea_vs_rsc.png")


def fig11() -> None:
    path = dd.SERIES_DIR / "portfolio_equity_extended.parquet"
    if not path.exists():
        print("fig11 skipped — extended curves missing", file=sys.stderr)
        return
    ext = pd.read_parquet(path)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for col, label, color, lw in [
        ("100% SPY", "SPY", C["benchmark"], 2.2),
        ("CORE-EXT-HAIRCUT 35/40/25", "CORE-EXT (haircut MF proxy)", C["secondary"], 1.8),
        ("HFEA 55/45", "HFEA 55/45", C["purple"], 1.4),
        ("60/40 SPY/IEF", "60/40", C["teal"], 1.4),
    ]:
        eq = ext[col].dropna()
        ax.plot(eq.index, eq / eq.iloc[0], label=label, color=color, lw=lw)
    for name, start, end in EXTENDED_BANDS:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color="#999", alpha=0.18)
        ax.text(pd.Timestamp(start), ax.get_ylim()[0] * 1.5 if ax.get_ylim()[0] > 0 else 0.7,
                name, fontsize=7, rotation=90, va="bottom", color="#555")
    _log_axis(ax)
    ax.set_title("1970-2026 extension - LOW-FIDELITY academic proxies pre-1988 "
                 "(haircut applied), log scale")
    ax.legend(loc="upper left")
    _save(fig, "11_extended_1970.png")


def fig12() -> None:
    abl = pd.read_csv(dd.TABLES_DIR / "ablations_primary.csv")
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.scatter(abl["mdd"].abs(), abl["cagr"], s=60, color=C["primary"])
    core = abl[abl["id"] == "A0"].iloc[0]
    ax.scatter([abs(core["mdd"])], [core["cagr"]], marker="*", s=420,
               color=C["secondary"], edgecolor="#000", zorder=5)
    for _, row in abl.iterrows():
        ax.annotate(row["config"], (abs(row["mdd"]), row["cagr"]),
                    textcoords="offset points", xytext=(7, 4), fontsize=8)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("max drawdown (absolute)")
    ax.set_ylabel("CAGR")
    ax.grid(alpha=0.25)
    ax.set_title("Ablations, 2000-2026: every variant vs the core (star)")
    _save(fig, "12_ablation_summary.png")


def main() -> int:
    primary = pd.read_parquet(dd.SERIES_DIR / "primary_returns.parquet")
    curves = load_portfolio_curves()
    comp = pd.read_csv(dd.TABLES_DIR / "episodes_components.csv")
    prod = pd.read_csv(dd.TABLES_DIR / "episodes_products.csv")

    fig01(primary)
    fig02(primary, curves)
    fig03(primary, curves)
    _episode_bars(
        comp, ["SPY", "GLD", "MFBLEND", "ZROZ", "BTC"],
        [C["benchmark"], C["yellow"], C["green"], C["primary"], C["orange"]],
        "Component returns by episode, 2000-2026 (simulated; BTC n/a before 2010-07)",
        "04_episode_bars_components.png",
    )
    _episode_bars(
        prod, ["SPY", "GDE", "RSST", "NTSX", "CORE 35/40/25", "HFEA 55/45"],
        [C["benchmark"], C["yellow"], C["green"], C["teal"], C["secondary"], C["purple"]],
        "Product & portfolio returns by episode, 2000-2026 (simulated)",
        "05_episode_bars_products.png",
    )
    fig06()
    fig07()
    fig08()
    fig09()
    fig10(primary, curves)
    fig11()
    fig12()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
