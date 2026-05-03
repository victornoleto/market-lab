#!/usr/bin/env python3
"""Build live-strategy plots for B4 + 5% BTC vs SPY.

Uses the saved testfol.io curves from iter 047 instead of re-querying the API.
Rolling windows are descriptive diagnostics, not a new parameter search; this
keeps the live document focused on the selected static allocation and avoids
post-hoc optimization `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).parent
PLOT_DIR = SCRIPT_DIR / "live_strategy_plots"
TARGET = "B4_btc5_from_zroz"
BENCHMARK = "SPY_1x"


def load_curve(backtest_file: Path, slug: str) -> pd.Series:
    payload = json.loads(backtest_file.read_text())
    slugs = [p["slug"] for p in payload["portfolios"]]
    idx = slugs.index(slug)
    history = payload["response"]["charts"]["history"]
    dates = [dt.datetime.fromtimestamp(ts, tz=dt.UTC).date() for ts in history[0]]
    values = pd.Series(history[idx + 1], index=pd.to_datetime(dates), name=slug, dtype="float64")
    return values


def cagr(values: pd.Series) -> float:
    years = (values.index[-1] - values.index[0]).days / 365.25
    return (values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1


def max_drawdown(values: pd.Series) -> float:
    return (values / values.cummax() - 1).min()


def sharpe(values: pd.Series) -> float:
    returns = values.pct_change().dropna()
    return np.sqrt(252) * returns.mean() / returns.std(ddof=0)


def rolling_cagr(values: pd.Series, years: int) -> pd.Series:
    window = 252 * years
    return values.pct_change(window).add(1).pow(1 / years).sub(1)


def rolling_sharpe(values: pd.Series, years: int) -> pd.Series:
    returns = values.pct_change()
    window = 252 * years
    return np.sqrt(252) * returns.rolling(window).mean() / returns.rolling(window).std(ddof=0)


def plot_equity(frame: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    normalized = frame / frame.iloc[0] * 10_000
    normalized[TARGET].plot(ax=ax, label="B4 + 5% BTC", color="#2563eb", linewidth=2)
    normalized[BENCHMARK].plot(ax=ax, label="SPY", color="#6b7280", linewidth=1.8)
    ax.set_yscale("log")
    ax.set_title("Growth of $10,000: B4 + 5% BTC vs SPY")
    ax.set_ylabel("Portfolio value, log scale")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "b4_btc5_vs_spy_equity.png", dpi=160)
    plt.close(fig)


def plot_drawdown(frame: pd.DataFrame) -> None:
    dd = frame / frame.cummax() - 1
    fig, ax = plt.subplots(figsize=(11, 5))
    (dd[TARGET] * 100).plot(ax=ax, label="B4 + 5% BTC", color="#2563eb", linewidth=2)
    (dd[BENCHMARK] * 100).plot(ax=ax, label="SPY", color="#6b7280", linewidth=1.8)
    ax.set_title("Drawdown: B4 + 5% BTC vs SPY")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "b4_btc5_vs_spy_drawdown.png", dpi=160)
    plt.close(fig)


def plot_rolling_cagr(frame: pd.DataFrame, years: int) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    (rolling_cagr(frame[TARGET], years) * 100).plot(ax=ax, label="B4 + 5% BTC", color="#2563eb", linewidth=2)
    (rolling_cagr(frame[BENCHMARK], years) * 100).plot(ax=ax, label="SPY", color="#6b7280", linewidth=1.8)
    ax.axhline(0, color="#111827", linewidth=0.8, alpha=0.5)
    ax.set_title(f"Rolling {years}-Year CAGR")
    ax.set_ylabel("Annualized return (%)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOT_DIR / f"b4_btc5_vs_spy_rolling_{years}y_cagr.png", dpi=160)
    plt.close(fig)


def plot_rolling_sharpe(frame: pd.DataFrame, years: int) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    rolling_sharpe(frame[TARGET], years).plot(ax=ax, label="B4 + 5% BTC", color="#2563eb", linewidth=2)
    rolling_sharpe(frame[BENCHMARK], years).plot(ax=ax, label="SPY", color="#6b7280", linewidth=1.8)
    ax.axhline(0, color="#111827", linewidth=0.8, alpha=0.5)
    ax.set_title(f"Rolling {years}-Year Sharpe")
    ax.set_ylabel("Sharpe")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOT_DIR / f"b4_btc5_vs_spy_rolling_{years}y_sharpe.png", dpi=160)
    plt.close(fig)


def write_metrics(frame: pd.DataFrame) -> None:
    rows = []
    for slug in [TARGET, BENCHMARK]:
        rows.append(
            {
                "slug": slug,
                "start": str(frame.index[0].date()),
                "end": str(frame.index[-1].date()),
                "cagr_pct": cagr(frame[slug]) * 100,
                "mdd_pct": max_drawdown(frame[slug]) * 100,
                "sharpe_daily_rf0": sharpe(frame[slug]),
                "end_value_start_10000": frame[slug].iloc[-1] / frame[slug].iloc[0] * 10_000,
            }
        )
    (PLOT_DIR / "b4_btc5_vs_spy_metrics.json").write_text(json.dumps(rows, indent=2))


def main() -> int:
    PLOT_DIR.mkdir(exist_ok=True)
    target = load_curve(SCRIPT_DIR / "testfolio_data" / "backtest_a.json", TARGET)
    spy = load_curve(SCRIPT_DIR / "testfolio_data" / "backtest_b.json", BENCHMARK)
    frame = pd.concat([target, spy], axis=1).dropna()
    plot_equity(frame)
    plot_drawdown(frame)
    plot_rolling_cagr(frame, 3)
    plot_rolling_cagr(frame, 5)
    plot_rolling_sharpe(frame, 3)
    write_metrics(frame)
    print(f"wrote plots to {PLOT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
