#!/usr/bin/env python3
"""Generate final ADV5M comparison plots for weekly momentum.

The plots compare the three frozen Phase 5c variants: baseline, focused
optimization, and aggressive neighborhood. This is reporting only, not another
parameter search `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


RUNS = {
    "ADV5M baseline": Path("studies/weekly_momentum/evidence/phase5c_adv5m_variants/adv5m_baseline_aligned_strategy_spy.csv"),
    "Focused optimization": Path("studies/weekly_momentum/evidence/phase5c_adv5m_variants/focused_optimization_aligned_strategy_spy.csv"),
    "Aggressive neighborhood": Path("studies/weekly_momentum/evidence/phase5c_adv5m_variants/aggressive_neighborhood_aligned_strategy_spy.csv"),
}


def main() -> int:
    out_dir = Path("studies/weekly_momentum/plots/phase5")
    out_dir.mkdir(parents=True, exist_ok=True)
    aligned = {name: _load_aligned(path) for name, path in RUNS.items()}
    spy = next(iter(aligned.values()))["spy_equity"].rename("SPY")

    equity = pd.concat({name: df["strategy_equity"] for name, df in aligned.items()} | {"SPY": spy}, axis=1).dropna()
    equity = equity / equity.iloc[0]
    ratio = equity.drop(columns=["SPY"]).div(equity["SPY"], axis=0)
    rolling = _rolling_window_table(equity)
    drawdown = equity / equity.cummax() - 1.0

    _plot_performance(equity, drawdown, out_dir / "phase5_adv5m_performance_vs_spy.png")
    _plot_ratio(ratio, out_dir / "phase5_adv5m_equity_over_spy.png")
    _plot_rolling_summary(rolling, out_dir / "phase5_adv5m_rolling_summary_vs_spy.png")
    _plot_rolling_cagr_series(equity, out_dir / "phase5_adv5m_rolling_cagr_1_3_5y.png")
    rolling.to_csv(out_dir / "phase5_adv5m_rolling_windows.csv", index=False)
    print(f"outputs={out_dir}")
    return 0


def _load_aligned(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.set_index("date").sort_index()


def _rolling_window_table(equity: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for years in [1, 3, 5]:
        window = years * 252
        if len(equity) <= window:
            continue
        spy_cagr = (equity["SPY"] / equity["SPY"].shift(window)) ** (1.0 / years) - 1.0
        for name in equity.columns:
            if name == "SPY":
                continue
            strat_cagr = (equity[name] / equity[name].shift(window)) ** (1.0 / years) - 1.0
            edge = (strat_cagr - spy_cagr).dropna()
            rows.append({
                "run": name,
                "window_years": years,
                "pct_beat_spy": float((edge > 0.0).mean()),
                "median_edge": float(edge.median()),
                "worst_edge": float(edge.min()),
                "worst_strategy_cagr": float(strat_cagr.dropna().min()),
            })
    return pd.DataFrame(rows)


def _plot_performance(equity: pd.DataFrame, drawdown: pd.DataFrame, out_path: Path) -> None:
    fig, (ax_eq, ax_dd) = plt.subplots(2, 1, figsize=(12, 9), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    for col in equity.columns:
        kwargs = {"color": "black", "linestyle": "--"} if col == "SPY" else {}
        ax_eq.plot(equity.index, equity[col], label=col, linewidth=1.5, **kwargs)
        ax_dd.plot(drawdown.index, drawdown[col], label=col, linewidth=1.1, **kwargs)
    ax_eq.set_yscale("log")
    ax_eq.set_title("Weekly momentum Phase 5c variants vs SPY")
    ax_eq.set_ylabel("Growth of $1")
    ax_eq.grid(True, which="both", alpha=0.3)
    ax_eq.legend(ncol=2)
    ax_dd.set_ylabel("Drawdown")
    ax_dd.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def _plot_ratio(ratio: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in ratio.columns:
        ax.plot(ratio.index, ratio[col], label=col, linewidth=1.5)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_yscale("log")
    ax.set_title("Equity / SPY equity")
    ax.set_ylabel("Relative wealth vs SPY")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def _plot_rolling_summary(rolling: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    metrics = [
        ("pct_beat_spy", "Pct Windows Beat SPY"),
        ("median_edge", "Median CAGR Edge"),
        ("worst_edge", "Worst CAGR Edge"),
    ]
    for ax, (metric, title) in zip(axes, metrics, strict=True):
        pivot = rolling.pivot(index="window_years", columns="run", values=metric)
        pivot.plot(kind="bar", ax=ax)
        ax.set_title(title)
        ax.set_xlabel("Rolling window years")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend().remove()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3)
    fig.suptitle("Rolling window robustness vs SPY")
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def _plot_rolling_cagr_series(equity: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(12, 11), sharex=True)
    for ax, years in zip(axes, [1, 3, 5], strict=True):
        window = years * 252
        rolling_cagr = (equity / equity.shift(window)) ** (1.0 / years) - 1.0
        for col in rolling_cagr.columns:
            kwargs = {"color": "black", "linestyle": "--", "linewidth": 1.3} if col == "SPY" else {"linewidth": 1.2}
            ax.plot(rolling_cagr.index, rolling_cagr[col], label=col, **kwargs)
        ax.axhline(0.0, color="black", linewidth=0.8, alpha=0.5)
        ax.set_title(f"Rolling {years}y CAGR")
        ax.set_ylabel("CAGR")
        ax.grid(True, alpha=0.3)
    axes[0].legend(ncol=2)
    fig.suptitle("Phase 5/5b/5c ADV5M variants vs SPY rolling CAGR")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
