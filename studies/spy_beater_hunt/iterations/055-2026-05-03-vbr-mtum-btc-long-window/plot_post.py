#!/usr/bin/env python3
"""Generate r/ETF post plots for iter 055.

Plots compare B4, B4+BTC5, the proposed B4+BTC+SCV+Momentum proxy portfolio,
and SPY. The proposed proxy uses VBR/MTUM/BTCSIM to avoid the very short live
history of AVUV/SPMO/FMTM. This is presentation material, not a new validation
gate `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).parent
PLOT_DIR = SCRIPT_DIR / "post_plots"
TARGET = "proxy_sat_from_zroz_ntsx"
COLORS = {
    "SPY": "#000000",
    "B4 base": "#009E73",
    "B4 + 5% BTC": "#0072B2",
    "B4 + BTC + SCV + Momentum": "#D55E00",
    "ZROZ-only funding variant": "#CC79A7",
}


def load_iter_module():
    spec = importlib.util.spec_from_file_location("iter055", SCRIPT_DIR / "run_iter055.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load run_iter055.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize(series: pd.Series) -> pd.Series:
    return 10_000 * series / series.iloc[0]


def drawdown(series: pd.Series) -> pd.Series:
    return series / series.cummax() - 1


def rolling_cagr(series: pd.Series, years: int) -> pd.Series:
    window = 252 * years
    return (series / series.shift(window)) ** (252 / window) - 1


def metrics(series: pd.Series) -> dict[str, float]:
    rets = series.pct_change().dropna()
    years = (series.index[-1] - series.index[0]).days / 365.25
    cagr = (series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1
    mdd = drawdown(series).min()
    sharpe = np.sqrt(252) * rets.mean() / rets.std(ddof=0)
    return {"cagr": cagr * 100, "mdd": mdd * 100, "sharpe": sharpe}


def build_curves() -> dict[str, pd.Series]:
    mod = load_iter_module()
    rets = mod.sleeve_returns(include_btc=True).loc["2010-01-01":]
    specs = {p["slug"]: p["allocation_real"] for p in mod.WITH_BTC}
    wanted = {
        "SPY": "SPY",
        "B4 base": "B4_base",
        "B4 + 5% BTC": "B4_btc5",
        "B4 + BTC + SCV + Momentum": TARGET,
        "ZROZ-only funding variant": "proxy_sat_from_zroz_only",
    }
    curves = {}
    for label, slug in wanted.items():
        curves[label] = normalize(mod.monthly_curve(rets, specs[slug]))
    return curves


def plot_equity(curves: dict[str, pd.Series]) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    for label, series in curves.items():
        ax.plot(series.index, series, label=label, linewidth=2.2 if label == "B4 + BTC + SCV + Momentum" else 1.8, color=COLORS[label])
    ax.set_yscale("log")
    ax.set_title("Growth of $10,000, 2010-2026")
    ax.set_ylabel("Portfolio value, log scale")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "01_equity_log.png", dpi=180)
    plt.close(fig)


def plot_drawdown(curves: dict[str, pd.Series]) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for label, series in curves.items():
        if label == "ZROZ-only funding variant":
            continue
        ax.plot(series.index, drawdown(series) * 100, label=label, linewidth=2.2 if label == "B4 + BTC + SCV + Momentum" else 1.8, color=COLORS[label])
    ax.set_title("Drawdowns, 2010-2026")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "02_drawdown.png", dpi=180)
    plt.close(fig)


def plot_rolling(curves: dict[str, pd.Series]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True)
    for years, ax in zip([1, 2, 3, 5], axes.ravel(), strict=True):
        for label in ["SPY", "B4 base", "B4 + 5% BTC", "B4 + BTC + SCV + Momentum"]:
            ax.plot(curves[label].index, rolling_cagr(curves[label], years) * 100, label=label, linewidth=1.9 if label == "B4 + BTC + SCV + Momentum" else 1.5, color=COLORS[label])
        ax.axhline(0, color="black", linewidth=0.8, alpha=0.4)
        ax.set_title(f"Rolling {years}-year CAGR")
        ax.set_ylabel("CAGR (%)")
        ax.grid(True, alpha=0.25)
    axes[0, 0].legend(frameon=False, ncols=2, fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "03_rolling_cagr.png", dpi=180)
    plt.close(fig)


def plot_scatter(curves: dict[str, pd.Series]) -> None:
    rows = []
    for label, series in curves.items():
        m = metrics(series)
        rows.append({"label": label, **m})
    fig, ax = plt.subplots(figsize=(8, 6))
    for row in rows:
        ax.scatter(abs(row["mdd"]), row["cagr"], s=95)
        ax.annotate(row["label"], (abs(row["mdd"]), row["cagr"]), xytext=(6, 5), textcoords="offset points", fontsize=9)
    ax.set_title("CAGR vs Max Drawdown, 2010-2026")
    ax.set_xlabel("Max drawdown magnitude (%)")
    ax.set_ylabel("CAGR (%)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "04_cagr_mdd_scatter.png", dpi=180)
    plt.close(fig)
    (PLOT_DIR / "metrics_for_post.json").write_text(json.dumps(rows, indent=2))


def main() -> int:
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    curves = build_curves()
    plot_equity(curves)
    plot_drawdown(curves)
    plot_rolling(curves)
    plot_scatter(curves)
    print(f"wrote plots to {PLOT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
