"""Generate focused plots for the 35/40/25 final core report.

The figures are diagnostic only: they visualize path dependence, drawdown, rolling
relative wealth and challenger trade-offs for the selected static benchmark before
any deployment or validation claim `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.static_spy_beater_portfolio.scripts.score_portfolio import (  # noqa: E402
    metrics_from_returns,
    monthly_rebalanced_returns,
)
from studies.static_spy_beater_portfolio.scripts.universe import load_universe_returns  # noqa: E402

STUDY_DIR = REPO / "studies" / "static_spy_beater_portfolio"
OUT_DIR = STUDY_DIR / "results" / "final_core_report"
PLOT_DIR = OUT_DIR / "plots"

CORE = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}
CANDIDATES: dict[str, dict[str, float]] = {
    "35/40/25 core": CORE,
    "B4 original": {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25},
    "SPY buy-hold": {"SPYSIM": 1.0},
    "GA robust": {"GDESIM": 0.35, "RSSTSIM": 0.50, "SPYSIM": 0.10, "ZROZSIM": 0.05},
    "GA aggressive": {"GDESIM": 0.35, "RSSTSIM": 0.50, "TQQQSIM": 0.05, "ZROZSIM": 0.10},
}
REGIMES = {
    "Dot-com": ("2000-03-24", "2002-10-09"),
    "GFC": ("2007-10-09", "2009-03-09"),
    "QE bull": ("2010-01-04", "2019-12-31"),
    "Covid": ("2020-02-19", "2020-03-23"),
    "Inflation": ("2021-12-27", "2022-10-20"),
    "Recovery": ("2023-01-03", "2026-04-17"),
}


def main() -> None:
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    frame = load_universe_returns("mf_1988")
    required = sorted({ticker for weights in CANDIDATES.values() for ticker in weights})
    aligned = frame[required].dropna()
    returns = pd.DataFrame(
        {
            name: monthly_rebalanced_returns(aligned, weights)
            for name, weights in CANDIDATES.items()
        }
    ).dropna()
    equity = (1.0 + returns).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    metrics = write_metrics(returns)

    plot_equity(equity)
    plot_drawdown(drawdown)
    plot_relative_wealth(equity)
    plot_rolling_relative_wealth(returns)
    plot_risk_return(metrics)
    plot_regime_wealth(returns)


def write_metrics(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name in returns.columns:
        row = {"candidate": name}
        row.update(metrics_from_returns(returns[name]))
        rows.append(row)
    metrics = pd.DataFrame(rows)
    metrics.to_csv(OUT_DIR / "final_core_metrics.csv", index=False)
    return metrics


def plot_equity(equity: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    for name in equity.columns:
        width = 3.0 if name == "35/40/25 core" else 1.6
        alpha = 1.0 if name == "35/40/25 core" else 0.78
        ax.plot(equity.index, equity[name], label=name, linewidth=width, alpha=alpha)
    ax.set_yscale("log")
    ax.set_title("Equity Curves - Monthly Rebalanced Static Portfolios")
    ax.set_ylabel("Growth of $1, log scale")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "equity_curves.png")


def plot_drawdown(drawdown: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.8))
    for name in drawdown.columns:
        width = 3.0 if name == "35/40/25 core" else 1.4
        alpha = 1.0 if name == "35/40/25 core" else 0.70
        ax.plot(drawdown.index, drawdown[name] * 100.0, label=name, linewidth=width, alpha=alpha)
    ax.set_title("Drawdowns")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower left", fontsize=9)
    save(fig, "drawdowns.png")


def plot_relative_wealth(equity: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.8))
    base = equity["SPY buy-hold"]
    for name in ["35/40/25 core", "B4 original", "GA robust", "GA aggressive"]:
        width = 3.0 if name == "35/40/25 core" else 1.5
        ax.plot(equity.index, equity[name] / base, label=name, linewidth=width)
    ax.axhline(1.0, color="black", linewidth=1.0, linestyle="--", alpha=0.65)
    ax.set_yscale("log")
    ax.set_title("Relative Wealth Versus SPY Buy-Hold")
    ax.set_ylabel("Portfolio equity / SPY equity, log scale")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "relative_wealth_vs_spy.png")


def plot_rolling_relative_wealth(returns: pd.DataFrame) -> None:
    horizons = {"3y": 252 * 3, "5y": 252 * 5, "10y": 252 * 10, "15y": 252 * 15}
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=False)
    for ax, (label, days) in zip(axes.ravel(), horizons.items(), strict=True):
        data = rolling_relative_wealth(returns["35/40/25 core"], returns["SPY buy-hold"], days)
        ax.plot(data.index, data * 100.0, linewidth=2.2, color="#1f77b4")
        ax.axhline(0.0, color="black", linewidth=1.0, linestyle="--", alpha=0.65)
        ax.set_title(f"{label} Rolling Relative Wealth vs SPY")
        ax.set_ylabel("Core minus SPY wealth (%)")
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    save(fig, "rolling_relative_wealth_vs_spy.png")


def rolling_relative_wealth(portfolio: pd.Series, benchmark: pd.Series, days: int) -> pd.Series:
    aligned = pd.concat({"p": portfolio, "b": benchmark}, axis=1).dropna()
    p_log = np.log1p(aligned["p"])
    b_log = np.log1p(aligned["b"])
    # Rolling log terminal wealth avoids cumulative floating-point drift over long windows.
    rel = np.exp((p_log.rolling(days).sum() - b_log.rolling(days).sum()).dropna()) - 1.0
    rel.name = f"rolling_{days}d_relative_wealth"
    return rel


def plot_risk_return(metrics: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    for row in metrics.to_dict("records"):
        name = str(row["candidate"])
        size = 130 if name == "35/40/25 core" else 70
        color = "#1f77b4" if name == "35/40/25 core" else "#888888"
        ax.scatter(abs(float(row["mdd"])) * 100.0, float(row["cagr"]) * 100.0, s=size, color=color)
        ax.annotate(name, (abs(float(row["mdd"])) * 100.0, float(row["cagr"]) * 100.0), xytext=(6, 4), textcoords="offset points", fontsize=8)
    ax.set_title("Return Versus Max Drawdown")
    ax.set_xlabel("Absolute max drawdown (%)")
    ax.set_ylabel("CAGR (%)")
    ax.grid(True, alpha=0.25)
    save(fig, "cagr_vs_mdd.png")


def plot_regime_wealth(returns: pd.DataFrame) -> None:
    rows = []
    for regime, (start, end) in REGIMES.items():
        sliced = returns.loc[start:end]
        if sliced.empty:
            continue
        core_wealth = float((1.0 + sliced["35/40/25 core"]).prod())
        spy_wealth = float((1.0 + sliced["SPY buy-hold"]).prod())
        b4_wealth = float((1.0 + sliced["B4 original"]).prod())
        rows.append(
            {
                "regime": regime,
                "core_vs_spy": core_wealth / spy_wealth,
                "core_vs_b4": core_wealth / b4_wealth,
            }
        )
    df = pd.DataFrame(rows).set_index("regime")
    fig, ax = plt.subplots(figsize=(10, 5.6))
    (df - 1.0).mul(100.0).plot(kind="bar", ax=ax, width=0.72)
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_title("Core Relative Wealth By Regime")
    ax.set_ylabel("Relative wealth advantage (%)")
    ax.set_xlabel("")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(["Core vs SPY", "Core vs B4"], fontsize=9)
    fig.tight_layout()
    save(fig, "regime_relative_wealth.png")


def save(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(PLOT_DIR / filename, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
