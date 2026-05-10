#!/usr/bin/env python3
"""Build Phase 5 report for dynamic all-stocks weekly momentum.

Phase 5 reopens the broad-stock dynamic hypothesis with point-in-time
tradability filters: observed age, adjusted price, and ADV20. Liquidity filters
use only information available by the signal date `[stocks_on_the_move, p.81]`;
walk-forward selection uses past train windows only `[advances_fin_ml, p.208-211]`.
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

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from studies.weekly_momentum.reporting import compute_report_metrics


ROOT = Path("studies/weekly_momentum")
OUT_DIR = ROOT / "phase5_dynamic_all_stocks"
PLOTS_DIR = OUT_DIR / "plots"
RUNS = {
    "Dynamic ADV5M": ROOT / "phase5_all_stocks_dynamic_adv5m/dynamic_wf_all_stocks/aligned_strategy_spy.csv",
    "Dynamic ADV10M": ROOT / "phase5_all_stocks_dynamic_adv10m/dynamic_wf_all_stocks/aligned_strategy_spy.csv",
}
COMPARISONS = {
    "ADV5M": ROOT / "phase5_all_stocks_dynamic_adv5m/candidate_comparison.csv",
    "ADV10M": ROOT / "phase5_all_stocks_dynamic_adv10m/candidate_comparison.csv",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    series = _load_strategy_series()
    benchmarks = _load_benchmarks(series)
    all_series = {**series, **benchmarks}
    metrics = _metrics_table(all_series)
    comparisons = _comparison_table()

    metrics.to_csv(OUT_DIR / "benchmark_metrics.csv", index=False)
    comparisons.to_csv(OUT_DIR / "dynamic_grid_summary.csv", index=False)
    _plot_equity(all_series, PLOTS_DIR / "phase5_equity_vs_benchmarks.png")
    _plot_relative(series, benchmarks["SPY"], PLOTS_DIR / "phase5_equity_over_spy.png")
    _plot_drawdown(all_series, PLOTS_DIR / "phase5_drawdown_vs_benchmarks.png")
    _plot_rolling_cagr(all_series, PLOTS_DIR / "phase5_rolling_cagr_1_3_5y.png")
    _write_report(OUT_DIR / "PHASE5_DYNAMIC_ALL_STOCKS_REPORT.md", metrics, comparisons)
    print(f"outputs={OUT_DIR}")
    print(comparisons.to_string(index=False))
    return 0


def _load_strategy_series() -> dict[str, pd.Series]:
    out = {}
    for label, path in RUNS.items():
        df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
        out[label] = (df["strategy_equity"] / df["strategy_equity"].iloc[0]).rename(label)
    return out


def _load_benchmarks(series: dict[str, pd.Series]) -> dict[str, pd.Series]:
    start = min(item.index.min() for item in series.values())
    end = max(item.index.max() for item in series.values())
    storage = TiingoStorage(Path("data/tiingo"))
    out: dict[str, pd.Series] = {}
    for ticker in ["SPY", "SPMO", "FMTM"]:
        try:
            df = storage.read(ticker, start=start.date(), end=end.date(), frequency="daily")
        except KeyError:
            continue
        if df.empty:
            continue
        price = df["adj_close"].astype(float).dropna()
        out[ticker] = (price / price.iloc[0]).rename(ticker)
    return out


def _metrics_table(series: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for label, equity in series.items():
        returns = equity.pct_change(fill_method=None).fillna(0.0)
        metrics = compute_report_metrics(equity * 10_000.0, returns)
        rows.append({"series": label, "start": equity.index.min().date(), "end": equity.index.max().date(), "n_bars": len(equity), **metrics})
    return pd.DataFrame(rows)


def _comparison_table() -> pd.DataFrame:
    rows = []
    cols = [
        "cagr", "mdd", "sharpe", "spy_cagr", "spy_mdd", "spy_sharpe",
        "pbo_family", "pbo_family_pass", "dsr_p_value", "dsr_pass",
        "bootstrap_cagr_ci_low_0p1pct", "bootstrap_pass", "cost10bps_tax_cagr",
        "oos_positive_windows", "oos_windows", "oos_beat_spy_windows", "oos_beat_spy_ratio",
        "median_held_adv20", "min_held_adv20", "avg_positions_when_invested",
    ]
    for label, path in COMPARISONS.items():
        row = pd.read_csv(path).iloc[0]
        rows.append({"run": label, **{col: row.get(col) for col in cols}})
    return pd.DataFrame(rows)


def _plot_equity(series: dict[str, pd.Series], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for label, equity in series.items():
        style = "--" if label in {"SPY", "SPMO", "FMTM"} else "-"
        width = 1.8 if label in {"SPY", "SPMO", "FMTM"} else 1.4
        ax.plot(equity.index, equity.values, label=label, linestyle=style, linewidth=width)
    ax.set_yscale("log")
    ax.set_title("Phase 5 Dynamic All-Stocks vs Momentum ETF Benchmarks")
    ax.set_ylabel("Growth of $1, log scale")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_relative(series: dict[str, pd.Series], spy: pd.Series, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for label, equity in series.items():
        aligned = pd.concat({"s": equity, "b": spy}, axis=1).dropna()
        ratio = (aligned["s"] / aligned["s"].iloc[0]) / (aligned["b"] / aligned["b"].iloc[0])
        ax.plot(ratio.index, ratio.values, label=f"{label} / SPY", linewidth=1.4)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_yscale("log")
    ax.set_title("Phase 5 Relative Equity To SPY")
    ax.set_ylabel("Strategy / SPY")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_drawdown(series: dict[str, pd.Series], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for label, equity in series.items():
        dd = equity / equity.cummax() - 1.0
        ax.plot(dd.index, dd.values * 100.0, label=label, linewidth=1.3)
    ax.set_title("Phase 5 Drawdown vs Benchmarks")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_rolling_cagr(series: dict[str, pd.Series], out_path: Path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(12, 11), sharex=True)
    for ax, years in zip(axes, [1, 3, 5], strict=True):
        window = years * 252
        for label, equity in series.items():
            rolling = (equity / equity.shift(window)) ** (1.0 / years) - 1.0
            ax.plot(rolling.index, rolling.values * 100.0, label=label, linewidth=1.1)
        ax.axhline(0.0, color="black", linewidth=0.7, alpha=0.4)
        ax.set_title(f"{years}y rolling CAGR")
        ax.set_ylabel("CAGR (%)")
        ax.grid(True, alpha=0.25)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _write_report(path: Path, metrics: pd.DataFrame, comparisons: pd.DataFrame) -> None:
    show_metrics = metrics.copy()
    for col in ["total_return", "cagr", "mdd", "vol_annual", "var_5", "best_day", "worst_day"]:
        show_metrics[col] = show_metrics[col].map(_fmt_pct)
    for col in ["sharpe", "sortino", "calmar"]:
        show_metrics[col] = show_metrics[col].map(_fmt_float)

    show_comp = comparisons.copy()
    for col in ["cagr", "mdd", "spy_cagr", "spy_mdd", "bootstrap_cagr_ci_low_0p1pct", "cost10bps_tax_cagr"]:
        show_comp[col] = show_comp[col].map(_fmt_pct)
    for col in ["sharpe", "spy_sharpe", "pbo_family", "dsr_p_value", "median_held_adv20", "min_held_adv20", "avg_positions_when_invested"]:
        show_comp[col] = show_comp[col].map(_fmt_float)

    lines = [
        "# Phase 5 Dynamic All-Stocks Report",
        "",
        "## TL;DR",
        "",
        "The dynamic all-stocks hypothesis is worth keeping alive as a separate research branch, but it is not deployable yet. The ADV5M grid is economically strong, while ADV10M is weaker. Both still fail at least one hard robustness gate, especially PBO/bootstrap.",
        "",
        "## Setup",
        "",
        "- Universe: all cached Tiingo equities, not S&P 500 membership.",
        "- Point-in-time tradability filters: observed age >= 252 bars, adjusted price >= $5, ADV20 >= $5M or $10M.",
        "- Dynamic WF grid: lookbacks 60/80/100, top_k 5/10/20, filters SMA200/SMA250, allow_negative=0.",
        "- Walk-forward: 3y train, 1y test, selecting parameters only from prior train windows `[advances_fin_ml, p.208-211]`.",
        "- Benchmarks: SPY, SPMO, FMTM. FMTM has short Tiingo history, so its comparison is limited.",
        "",
        "## Candidate Summary",
        "",
        show_comp.to_markdown(index=False),
        "",
        "## Benchmark Metrics",
        "",
        show_metrics[["series", "start", "end", "n_bars", "cagr", "mdd", "sharpe", "sortino", "vol_annual"]].to_markdown(index=False),
        "",
        "## Plots",
        "",
        "![Equity vs benchmarks](plots/phase5_equity_vs_benchmarks.png)",
        "",
        "![Equity over SPY](plots/phase5_equity_over_spy.png)",
        "",
        "![Drawdown vs benchmarks](plots/phase5_drawdown_vs_benchmarks.png)",
        "",
        "![Rolling CAGR](plots/phase5_rolling_cagr_1_3_5y.png)",
        "",
        "## Interpretation",
        "",
        "- ADV5M is stronger than ADV10M, which implies part of the edge may come from smaller/less liquid names.",
        "- ADV5M passes DSR but fails PBO and bootstrap; this is not deployable.",
        "- ADV10M fails PBO, DSR and bootstrap; stricter liquidity weakens the result.",
        "- This is a different hypothesis from S&P 500 weekly momentum and should be tracked as a new branch, not as a continuation of the rejected S&P 500 family.",
        "",
        "## Next Step",
        "",
        "Do not expand to a broad 200-config sweep. First test robustness with pre-registered variants: ADV20 thresholds, train/test lengths, and a single-block holdout. If bootstrap remains negative, stop this branch too.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _fmt_pct(value: object) -> str:
    try:
        return f"{float(value):.2%}"
    except (TypeError, ValueError):
        return "n/a"


def _fmt_float(value: object) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "n/a"


if __name__ == "__main__":
    raise SystemExit(main())
