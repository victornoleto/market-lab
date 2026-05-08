#!/usr/bin/env python3
"""Generate plots for iter 056 (Part A) + iter 057 (Part B) and the narrative doc.

Outputs PNGs into:
    studies/long_term_portfolio/iterations/056-*/plots/
    studies/long_term_portfolio/iterations/057-*/plots/
    studies/long_term_portfolio/B4_DEEP_DIVE_plots/  (consolidated copies)

Plot list:
    A. iter 056 equity curves (10.56y window, log scale)
    B. iter 056 Pareto Sharpe × CAGR (colored by BTC vehicle)
    C. iter 056 beats-SPY % by window (3y/5y/10y bars)
    D. iter 057 equity curves vs SPY + VT (~31y window)
    E. iter 057 Pareto Sharpe × CAGR (colored by US/non-US split)
    F. iter 057 beats-SPY % by window (3y/5y/10y/15y bars)
    G. iter 057 beats-VT % by window (3y/5y/10y/15y bars)
    H. Combined Pareto (Part A + Part B together)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from ai_trade.backtest.data.testfolio_loader import load_testfolio_series
from studies.long_term_portfolio.run_iter import portfolio_returns_from_config


ITER_056_DIR = REPO / "studies/long_term_portfolio/iterations/056-2026-05-05-b4-reallocation"
ITER_057_DIR = REPO / "studies/long_term_portfolio/iterations/057-2026-05-05-global-fork-hybrid"
COMBINED_DIR = REPO / "studies/long_term_portfolio/B4_DEEP_DIVE_plots"

# Color palette for BTC vehicles (iter 056)
VEHICLE_COLORS = {
    "spy": "#888888",  # gray for SPY benchmark
    "base": "#1f77b4",  # blue for B4 base
    "spot": "#2ca02c",  # green for BTC spot
    "btgd": "#d62728",  # red for BTGD
    "rssx": "#ff7f0e",  # orange for RSSX
    "no_btc": "#9467bd",  # purple for combo no BTC
}

# Splits for iter 057
SPLIT_COLORS = {
    "100_00": "#1f77b4",  # blue (US-only)
    "70_30": "#2ca02c",   # green (light global)
    "60_40": "#ff7f0e",   # orange (user's primary)
    "55_45": "#d62728",   # red (heavy global)
}


def _classify_iter056(slug: str) -> str:
    if slug == "SPY_1x":
        return "spy"
    if slug == "P1_B4_base":
        return "base"
    if "rssx" in slug.lower():
        return "rssx"
    if "btgd" in slug.lower():
        return "btgd"
    if "no_btc" in slug.lower():
        return "no_btc"
    return "spot"


def _classify_iter057(name: str) -> str:
    if name == "B4_us_only":
        return "100_00"
    return name.split("__")[0]


# ---------------------------------------------------------------------------
# iter 056 — equity curves from cached testfolio responses
# ---------------------------------------------------------------------------


def load_iter056_curves() -> dict[str, dict]:
    """Returns {slug: {label, equity (pd.Series), stats, vehicle_class}}."""
    out: dict[str, dict] = {}
    for letter in ("a", "b"):
        path = ITER_056_DIR / "testfolio_data" / f"backtest_{letter}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        portfolios = data["portfolios"]
        response = data["response"]
        history = response["charts"]["history"]
        ts = history[0]
        dates = pd.DatetimeIndex(pd.to_datetime(ts, unit="s", utc=True).tz_convert(None))
        for j, p in enumerate(portfolios):
            curve = pd.Series(history[j + 1], index=dates, dtype=float).sort_index()
            curve = curve[~curve.index.duplicated(keep="last")]
            out[p["slug"]] = {
                "label": p["label"],
                "equity": curve,
                "stats": response["stats"][j],
                "vehicle": _classify_iter056(p["slug"]),
                "drag_pct": p["drag_pct"],
            }
    return out


# ---------------------------------------------------------------------------
# iter 057 — recompute returns via internal engine
# ---------------------------------------------------------------------------


def load_iter057_curves() -> dict[str, dict]:
    """Returns {name: {equity, metrics, split_class}}."""
    verdict = json.loads((ITER_057_DIR / "verdict.json").read_text())
    out: dict[str, dict] = {}
    for r in verdict["ranking"]:
        name = r["name"]
        cfg = r["config"]
        returns = portfolio_returns_from_config(cfg, dataset="lh_56y")
        equity = (1.0 + returns).cumprod() * 10_000.0
        out[name] = {
            "label": name,
            "equity": equity,
            "metrics": r["metrics"],
            "windows_beat_spy": r["windows_beat_spy"],
            "windows_beat_vt": r["windows_beat_vt"],
            "split": _classify_iter057(name),
        }
    return out


# ---------------------------------------------------------------------------
# Plot helpers
# ---------------------------------------------------------------------------


def _save(fig: plt.Figure, *paths: Path) -> None:
    for p in paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] wrote {paths[0].name}")


# Plot A — iter 056 equity curves
def plot_iter056_equity(curves: dict[str, dict], out_paths: list[Path]) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    # Plot SPY first (gray, thin), then base, then variants
    order = ["SPY_1x", "P1_B4_base", "P2_B4_btc5_spot",
             "P3a_combo_spmo_btc", "P3b_combo_mtum_btc", "P3c_combo_no_btc",
             "P4a_btgd_5pct", "P4b_btgd_10pct_reduce_gde",
             "P5a_rssx_5pct", "P5b_rssx_10pct_reduce_ntsx"]
    for slug in order:
        if slug not in curves:
            continue
        c = curves[slug]
        eq = c["equity"]
        color = VEHICLE_COLORS[c["vehicle"]]
        is_winner = (slug == "P5b_rssx_10pct_reduce_ntsx")
        is_spy = (slug == "SPY_1x")
        is_base = (slug == "P1_B4_base")
        lw = 3.0 if is_winner else (2.0 if is_base else (1.2 if is_spy else 1.5))
        alpha = 1.0 if (is_winner or is_spy or is_base) else 0.7
        ls = "--" if is_spy else "-"
        s = c["stats"]
        label = (f"{slug}  [Sharpe {s['sharpe']:.3f} / "
                 f"CAGR {s['cagr']:.1f}%]")
        ax.plot(eq.index, eq.values, label=label, color=color, lw=lw, alpha=alpha, linestyle=ls)
    ax.set_yscale("log")
    ax.set_title("Iter 056 (Part A) — B4 Reallocation Equity Curves "
                 "(2015-10 → 2026-05, log scale)\n"
                 "Winner: P5b RSSX 10% reducing NTSX 25→20",
                 fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($, log scale, $10k start)")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    _save(fig, *out_paths)


# Plot B — iter 056 Pareto Sharpe × CAGR
def plot_iter056_pareto(curves: dict[str, dict], out_paths: list[Path]) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    by_vehicle: dict[str, list[tuple[str, float, float, float]]] = {}
    for slug, c in curves.items():
        s = c["stats"]
        by_vehicle.setdefault(c["vehicle"], []).append(
            (slug, s["cagr"], s["sharpe"], -s["max_drawdown"])
        )
    legend_labels = {
        "spy": "SPY benchmark",
        "base": "B4 base (no BTC)",
        "no_btc": "Combo SCV+MOM (no BTC)",
        "spot": "BTC spot vehicle",
        "btgd": "BTGD vehicle",
        "rssx": "RSSX vehicle",
    }
    for vehicle, points in by_vehicle.items():
        slugs, cagrs, sharpes, mdds = zip(*points)
        ax.scatter(cagrs, sharpes, s=[max(40, m * 10) for m in mdds],
                   color=VEHICLE_COLORS[vehicle], alpha=0.75,
                   edgecolor="black", linewidth=0.6,
                   label=legend_labels.get(vehicle, vehicle))
        for slug, x, y, _ in points:
            ax.annotate(slug.replace("_", " ")
                        .replace("P5b rssx 10pct reduce ntsx", "P5b★")
                        .replace("P4b btgd 10pct reduce gde", "P4b")
                        .replace("P5a rssx 5pct", "P5a")
                        .replace("P4a btgd 5pct", "P4a")
                        .replace("P3a combo spmo btc", "P3a")
                        .replace("P3b combo mtum btc", "P3b")
                        .replace("P3c combo no btc", "P3c")
                        .replace("P2 B4 btc5 spot", "P2")
                        .replace("P1 B4 base", "P1")
                        .replace("SPY 1x", "SPY"),
                        (x, y), xytext=(6, 4), textcoords="offset points",
                        fontsize=8.5)
    ax.axhline(y=curves["SPY_1x"]["stats"]["sharpe"], color="gray", ls=":", alpha=0.5,
               label=f"SPY Sharpe = {curves['SPY_1x']['stats']['sharpe']:.3f}")
    ax.axvline(x=curves["SPY_1x"]["stats"]["cagr"], color="gray", ls=":", alpha=0.5,
               label=f"SPY CAGR = {curves['SPY_1x']['stats']['cagr']:.2f}%")
    ax.set_title("Iter 056 (Part A) — Pareto Sharpe × CAGR by BTC vehicle\n"
                 "Bubble size ∝ max drawdown magnitude",
                 fontsize=13)
    ax.set_xlabel("CAGR (%)")
    ax.set_ylabel("Sharpe ratio (annualized)")
    ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, *out_paths)


# Plot C — iter 056 beats-SPY % bars
def plot_iter056_beats(curves: dict[str, dict], out_paths: list[Path]) -> None:
    verdict = json.loads((ITER_056_DIR / "verdict.json").read_text())
    portfolios = [r for r in verdict["ranking"] if r["slug"] != "SPY_1x"]
    portfolios.sort(key=lambda r: -r["stats"]["sharpe"])

    slugs = [r["slug"].replace("_", " ")[:30] for r in portfolios]
    win3 = [(r["windows_beat"]["SPY_1x"].get("3") or 0) * 100 for r in portfolios]
    win5 = [(r["windows_beat"]["SPY_1x"].get("5") or 0) * 100 for r in portfolios]
    win10 = [(r["windows_beat"]["SPY_1x"].get("10") or 0) * 100 for r in portfolios]

    x = np.arange(len(slugs))
    w = 0.27
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.bar(x - w, win3, w, label="3y rolling", color="#1f77b4")
    ax.bar(x, win5, w, label="5y rolling", color="#2ca02c")
    ax.bar(x + w, win10, w, label="10y rolling", color="#d62728")
    ax.set_xticks(x)
    ax.set_xticklabels(slugs, rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("% of rolling windows where Sharpe(strat) > Sharpe(SPY)")
    ax.set_title("Iter 056 (Part A) — % rolling-windows beating SPY by window size",
                 fontsize=13)
    ax.set_ylim(0, 105)
    ax.axhline(y=50, color="gray", ls=":", alpha=0.5)
    ax.legend(loc="lower right")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save(fig, *out_paths)


# Plot D — iter 057 equity curves
def plot_iter057_equity(curves: dict[str, dict], out_paths: list[Path]) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    spy_eq = (1.0 + load_testfolio_series("SPYSIM").pct_change().dropna()).cumprod() * 10_000
    vt_eq = (1.0 + load_testfolio_series("VTSIM").pct_change().dropna()).cumprod() * 10_000
    # Truncate benchmarks to 1988+ for cleaner visual
    cutoff = pd.Timestamp("1988-01-04")
    spy_eq = spy_eq.loc[cutoff:]
    spy_eq = spy_eq / spy_eq.iloc[0] * 10_000
    vt_eq = vt_eq.loc[cutoff:]
    vt_eq = vt_eq / vt_eq.iloc[0] * 10_000

    ax.plot(spy_eq.index, spy_eq.values, label="SPY 1x [bench]", color="#888888",
            lw=1.4, ls="--", alpha=0.9)
    ax.plot(vt_eq.index, vt_eq.values, label="VT 1x [bench]", color="#bbbbbb",
            lw=1.4, ls=":", alpha=0.9)

    # Sort: B4_us_only first, then by Sharpe desc
    ordered_keys = sorted(
        curves.keys(),
        key=lambda k: (0 if k == "B4_us_only" else 1, -curves[k]["metrics"]["sharpe"]),
    )
    for name in ordered_keys:
        c = curves[name]
        eq = c["equity"]
        eq_n = eq / eq.iloc[0] * 10_000
        color = SPLIT_COLORS[c["split"]]
        is_winner = (name == "B4_us_only")
        lw = 3.0 if is_winner else 1.4
        alpha = 1.0 if is_winner else 0.7
        m = c["metrics"]
        label = f"{name}  [Sharpe {m['sharpe']:.3f} / CAGR {m['cagr']*100:.2f}%]"
        ax.plot(eq_n.index, eq_n.values, label=label, color=color, lw=lw, alpha=alpha)
    ax.set_yscale("log")
    ax.set_title("Iter 057 (Part B) — Global Hybrid Fork Equity Curves vs SPY/VT\n"
                 "Winner on Sharpe: B4 US-only (38y window); global hybrid Sharpe peaks at 70/30",
                 fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($, log scale, $10k start at 1988-01)")
    ax.legend(loc="upper left", fontsize=7.5, framealpha=0.9, ncol=2)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    _save(fig, *out_paths)


# Plot E — iter 057 Pareto
def plot_iter057_pareto(curves: dict[str, dict], out_paths: list[Path]) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    by_split: dict[str, list[tuple[str, float, float, float]]] = {}
    for name, c in curves.items():
        m = c["metrics"]
        by_split.setdefault(c["split"], []).append(
            (name, m["cagr"] * 100, m["sharpe"], -m["mdd"] * 100)
        )
    split_labels = {
        "100_00": "100% B4 US-only",
        "70_30": "70/30 hybrid",
        "60_40": "60/40 hybrid (user's primary)",
        "55_45": "55/45 hybrid",
    }
    for split, points in by_split.items():
        names, cagrs, sharpes, mdds = zip(*points)
        ax.scatter(cagrs, sharpes, s=[max(50, m * 7) for m in mdds],
                   color=SPLIT_COLORS[split], alpha=0.75,
                   edgecolor="black", linewidth=0.6,
                   label=split_labels.get(split, split))
        for name, x, y, _ in points:
            short = (name.replace("70_30__NB", "70/30 NB")
                         .replace("60_40__NB", "60/40 NB")
                         .replace("55_45__NB", "55/45 NB")
                         .replace("_factor40", " 40%fct")
                         .replace("_factor30", " 30%fct")
                         .replace("_avnm_only", " avnm"))
            ax.annotate(short, (x, y), xytext=(6, 4),
                        textcoords="offset points", fontsize=8)
    # SPY / VT reference lines (full lh_56y for those benches)
    spy_returns = load_testfolio_series("SPYSIM").pct_change().dropna()
    vt_returns = load_testfolio_series("VTSIM").pct_change().dropna()
    spy_sharpe = float(spy_returns.mean() / spy_returns.std() * np.sqrt(252))
    vt_sharpe = float(vt_returns.mean() / vt_returns.std() * np.sqrt(252))
    ax.axhline(y=spy_sharpe, color="#888888", ls="--", alpha=0.6,
               label=f"SPY Sharpe = {spy_sharpe:.3f}")
    ax.axhline(y=vt_sharpe, color="#bbbbbb", ls=":", alpha=0.6,
               label=f"VT Sharpe = {vt_sharpe:.3f}")
    ax.set_title("Iter 057 (Part B) — Pareto Sharpe × CAGR by US/non-US split\n"
                 "Bubble size ∝ max drawdown magnitude",
                 fontsize=13)
    ax.set_xlabel("CAGR (%)")
    ax.set_ylabel("Sharpe ratio (annualized)")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, *out_paths)


# Plots F, G — iter 057 beats-SPY and beats-VT
def plot_iter057_beats(curves: dict[str, dict], bench: str, out_paths: list[Path]) -> None:
    key = f"windows_beat_{bench.lower()}"
    bench_label = bench.upper()
    ordered = sorted(curves.items(), key=lambda kv: -kv[1]["metrics"]["sharpe"])

    short_names = []
    rows: dict[str, list[float]] = {"3": [], "5": [], "10": [], "15": []}
    for name, c in ordered:
        short_names.append(
            name.replace("70_30__NB", "70/30 NB")
                .replace("60_40__NB", "60/40 NB")
                .replace("55_45__NB", "55/45 NB")
                .replace("_factor40", " 40%fct")
                .replace("_factor30", " 30%fct")
                .replace("_avnm_only", " avnm")
        )
        for w in ("3", "5", "10", "15"):
            d = c[key].get(w, {})
            pct = d.get("pct_strat_wins")
            rows[w].append(0 if pct is None else pct * 100)

    x = np.arange(len(short_names))
    width = 0.20
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.bar(x - 1.5 * width, rows["3"], width, label="3y", color="#1f77b4")
    ax.bar(x - 0.5 * width, rows["5"], width, label="5y", color="#2ca02c")
    ax.bar(x + 0.5 * width, rows["10"], width, label="10y", color="#ff7f0e")
    ax.bar(x + 1.5 * width, rows["15"], width, label="15y", color="#d62728")
    ax.set_xticks(x)
    ax.set_xticklabels(short_names, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel(f"% of rolling windows where Sharpe(strat) > Sharpe({bench_label})")
    ax.set_title(f"Iter 057 (Part B) — % rolling-windows beating {bench_label} by window size",
                 fontsize=13)
    ax.set_ylim(0, 105)
    ax.axhline(y=50, color="gray", ls=":", alpha=0.5)
    ax.legend(loc="lower right")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save(fig, *out_paths)


# Plot H — combined Pareto (Part A + Part B)
def plot_combined_pareto(
    curves_a: dict[str, dict], curves_b: dict[str, dict], out_paths: list[Path]
) -> None:
    fig, ax = plt.subplots(figsize=(12, 7.5))
    # Part A
    for slug, c in curves_a.items():
        s = c["stats"]
        ax.scatter(s["cagr"], s["sharpe"], s=80,
                   color=VEHICLE_COLORS[c["vehicle"]], alpha=0.7,
                   marker="o", edgecolor="black", linewidth=0.5)
        # Annotate winner only to keep clean
        if slug == "P5b_rssx_10pct_reduce_ntsx":
            ax.annotate("P5b★ (RSSX 10%)", (s["cagr"], s["sharpe"]),
                        xytext=(8, 6), textcoords="offset points",
                        fontsize=10, fontweight="bold")
    # Part B (use diamond marker to distinguish)
    for name, c in curves_b.items():
        m = c["metrics"]
        ax.scatter(m["cagr"] * 100, m["sharpe"], s=80,
                   color=SPLIT_COLORS[c["split"]], alpha=0.7,
                   marker="D", edgecolor="black", linewidth=0.5)
        if name == "B4_us_only":
            ax.annotate("B4_us_only★ (38y)", (m["cagr"] * 100, m["sharpe"]),
                        xytext=(8, -10), textcoords="offset points",
                        fontsize=10, fontweight="bold")

    # Custom legend
    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", color="#888888",
                   label="Part A (iter 056) — 10.56y"),
        plt.Line2D([0], [0], marker="D", linestyle="", color="#888888",
                   label="Part B (iter 057) — 31-38y"),
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=10)
    ax.set_title("Combined Pareto — Part A (10.56y) vs Part B (31-38y)\n"
                 "Different windows: not directly comparable Sharpe-for-Sharpe",
                 fontsize=13)
    ax.set_xlabel("CAGR (%)")
    ax.set_ylabel("Sharpe ratio (annualized)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, *out_paths)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("[plot] loading iter 056 curves from cached testfolio responses...")
    curves_a = load_iter056_curves()
    print(f"[plot] iter 056: loaded {len(curves_a)} portfolios")

    print("[plot] loading iter 057 curves (re-running portfolio_returns_from_config)...")
    curves_b = load_iter057_curves()
    print(f"[plot] iter 057: loaded {len(curves_b)} configs")

    iter_a_plots = ITER_056_DIR / "plots"
    iter_b_plots = ITER_057_DIR / "plots"
    iter_a_plots.mkdir(parents=True, exist_ok=True)
    iter_b_plots.mkdir(parents=True, exist_ok=True)
    COMBINED_DIR.mkdir(parents=True, exist_ok=True)

    plot_iter056_equity(curves_a,
                        [iter_a_plots / "A_equity_curves.png",
                         COMBINED_DIR / "A_iter056_equity_curves.png"])
    plot_iter056_pareto(curves_a,
                        [iter_a_plots / "B_pareto_sharpe_cagr.png",
                         COMBINED_DIR / "B_iter056_pareto.png"])
    plot_iter056_beats(curves_a,
                       [iter_a_plots / "C_beats_spy_by_window.png",
                        COMBINED_DIR / "C_iter056_beats_spy.png"])
    plot_iter057_equity(curves_b,
                        [iter_b_plots / "D_equity_curves.png",
                         COMBINED_DIR / "D_iter057_equity_curves.png"])
    plot_iter057_pareto(curves_b,
                        [iter_b_plots / "E_pareto_sharpe_cagr.png",
                         COMBINED_DIR / "E_iter057_pareto.png"])
    plot_iter057_beats(curves_b, "spy",
                       [iter_b_plots / "F_beats_spy_by_window.png",
                        COMBINED_DIR / "F_iter057_beats_spy.png"])
    plot_iter057_beats(curves_b, "vt",
                       [iter_b_plots / "G_beats_vt_by_window.png",
                        COMBINED_DIR / "G_iter057_beats_vt.png"])
    plot_combined_pareto(curves_a, curves_b,
                         [COMBINED_DIR / "H_combined_pareto.png"])

    print(f"\n[plot] all plots written to:")
    print(f"  {iter_a_plots}/")
    print(f"  {iter_b_plots}/")
    print(f"  {COMBINED_DIR}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
