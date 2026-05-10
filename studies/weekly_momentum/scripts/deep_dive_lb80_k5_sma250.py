#!/usr/bin/env python3
"""Deep dive for weekly momentum ``lb80/k5/SMA250`` under PIT SPX membership.

This report answers two deploy-validation questions:

1. Why does the candidate fail DSR? DSR compares the observed Sharpe against the
   expected best Sharpe after multiple trials `[advances_fin_ml, p.273-275]`.
2. Is the strategy robust to entry timing? We evaluate every possible rolling
   1/3/5/10/15/20y entry window against SPY `[trading_systems_methods, ch.21]`.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from market_lab.backtest.metrics.standard_report import load_spy_series
from market_lab.backtest.validation.dsr import dsr, expected_max_sharpe, psr, sharpe_periodic
from studies.weekly_momentum.core import WeeklyMomentumConfig, simulate_weekly_momentum
from studies.weekly_momentum.data import load_variation_prices, sp500_pit_universe_provider
from studies.weekly_momentum.reporting import compute_report_metrics


CONFIG = WeeklyMomentumConfig(
    lookback_days=80,
    top_k=5,
    allow_negative_momentum=False,
    market_filter_type="sma",
    market_filter_days=250,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deep dive lb80/k5/SMA250 weekly momentum")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--storage-root", default="data/tiingo")
    parser.add_argument("--spy-path", default="data/tiingo/daily/prices/SPY.parquet")
    parser.add_argument("--n-trials", type=int, default=200)
    parser.add_argument("--output-dir", default="studies/weekly_momentum/phase3/lb80_k5_sma250_deep_dive")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    out_dir = Path(args.output_dir)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    prices = load_variation_prices(
        "stocks",
        storage_root=args.storage_root,
        start=start,
        end=end,
        min_bars=CONFIG.lookback_days + 2,
        only_sp500=True,
    )
    spy = load_spy_series(args.spy_path).reindex(prices.index).ffill()
    result = simulate_weekly_momentum(
        prices,
        CONFIG,
        market_filter_prices=spy,
        universe_by_date=sp500_pit_universe_provider(),
    )
    spy_returns = spy.pct_change(fill_method=None).fillna(0.0).reindex(result.returns.index).fillna(0.0)
    spy_equity = (1.0 + spy_returns).cumprod() * CONFIG.initial_cash
    aligned = pd.concat(
        {
            "strategy_return": result.returns,
            "strategy_equity": result.equity,
            "spy_return": spy_returns,
            "spy_equity": spy_equity,
        },
        axis=1,
        sort=True,
    ).dropna()

    dsr_rows = _dsr_decomposition(aligned["strategy_return"], args.n_trials)
    window_rows = _all_entry_windows(aligned)
    window_summary = _window_summary(window_rows)
    full_metrics = _full_metrics(aligned)

    aligned.to_csv(out_dir / "aligned_strategy_spy.csv")
    pd.DataFrame(dsr_rows).to_csv(out_dir / "dsr_decomposition.csv", index=False)
    window_rows.to_csv(out_dir / "all_entry_windows.csv", index=False)
    window_summary.to_csv(out_dir / "entry_window_summary.csv", index=False)
    full_metrics.to_csv(out_dir / "full_metrics.csv", index=False)

    _plot_equity(aligned, plots_dir / "equity_vs_spy.png")
    _plot_relative(aligned, plots_dir / "equity_over_spy.png")
    _plot_rolling_cagr(aligned, plots_dir / "rolling_cagr_1_3_5_10_15_20y.png")
    _plot_window_edge_distributions(window_rows, plots_dir / "entry_window_edge_distributions.png")
    _plot_window_win_rates(window_summary, plots_dir / "entry_window_win_rates.png")
    _write_report(out_dir / "DEEP_DIVE_REPORT.md", full_metrics, pd.DataFrame(dsr_rows), window_summary, args)

    print(f"outputs={out_dir}")
    print(full_metrics.to_string(index=False))
    print(window_summary[["years", "n_windows", "pct_beat_spy", "worst_strategy_cagr", "worst_edge"]].to_string(index=False))
    return 0


def _full_metrics(aligned: pd.DataFrame) -> pd.DataFrame:
    strategy = compute_report_metrics(aligned["strategy_equity"], aligned["strategy_return"])
    spy = compute_report_metrics(aligned["spy_equity"], aligned["spy_return"])
    return pd.DataFrame([
        {"series": "strategy", **strategy},
        {"series": "spy", **spy},
    ])


def _dsr_decomposition(returns: pd.Series, n_trials: int) -> list[dict[str, float | int | str]]:
    arr = returns.dropna().to_numpy(dtype=float)
    periodic_sr = sharpe_periodic(arr)
    annual_sr = periodic_sr * np.sqrt(252.0)
    sigma = float(arr.std(ddof=0))
    centered = arr - float(arr.mean())
    skew = float(np.mean(centered**3) / sigma**3) if sigma > 0 else 0.0
    kurt = float(np.mean(centered**4) / sigma**4) if sigma > 0 else 0.0
    rows: list[dict[str, float | int | str]] = []
    for trials in [1, 2, 10, 25, 50, 100, n_trials]:
        if trials == 1:
            benchmark = 0.0
            probability = psr(arr, benchmark=benchmark)
            p_value = 1.0 - probability
            label = "PSR no trial penalty"
        else:
            benchmark = expected_max_sharpe(trials, var_sharpe=1.0 / (len(arr) - 1))
            result = dsr(arr, n_trials=trials)
            probability = result.dsr
            p_value = result.p_value
            label = "DSR"
        denom_sq = 1.0 - skew * periodic_sr + (kurt - 1.0) / 4.0 * periodic_sr**2
        z_score = (periodic_sr - benchmark) * np.sqrt(len(arr) - 1) / np.sqrt(max(denom_sq, 1e-12))
        rows.append({
            "test": label,
            "n_trials": trials,
            "observed_periodic_sharpe": periodic_sr,
            "observed_annual_sharpe": annual_sr,
            "benchmark_periodic_sharpe": benchmark,
            "benchmark_annualized_equivalent": benchmark * np.sqrt(252.0),
            "skew": skew,
            "raw_kurtosis": kurt,
            "z_score": float(z_score),
            "probability_true_sharpe_above_benchmark": float(probability),
            "p_value": float(p_value),
            "pass_p_lt_0p05": bool(p_value < 0.05),
        })
    return rows


def _all_entry_windows(aligned: pd.DataFrame, years_set: tuple[int, ...] = (1, 3, 5, 10, 15, 20)) -> pd.DataFrame:
    rows = []
    for years in years_set:
        bars = years * 252
        if len(aligned) <= bars:
            rows.append({
                "years": years,
                "start": None,
                "end": None,
                "n_bars": 0,
                "strategy_cagr": np.nan,
                "spy_cagr": np.nan,
                "edge": np.nan,
                "strategy_mdd": np.nan,
                "spy_mdd": np.nan,
                "strategy_sharpe": np.nan,
                "spy_sharpe": np.nan,
                "beat_spy": False,
                "insufficient_history": True,
            })
            continue
        for start_idx in range(0, len(aligned) - bars + 1):
            window = aligned.iloc[start_idx:start_idx + bars]
            sm = compute_report_metrics(window["strategy_equity"] / window["strategy_equity"].iloc[0] * 10_000.0, window["strategy_return"])
            bm = compute_report_metrics(window["spy_equity"] / window["spy_equity"].iloc[0] * 10_000.0, window["spy_return"])
            rows.append({
                "years": years,
                "start": str(window.index.min().date()),
                "end": str(window.index.max().date()),
                "n_bars": len(window),
                "strategy_cagr": sm["cagr"],
                "spy_cagr": bm["cagr"],
                "edge": sm["cagr"] - bm["cagr"],
                "strategy_mdd": sm["mdd"],
                "spy_mdd": bm["mdd"],
                "strategy_sharpe": sm["sharpe"],
                "spy_sharpe": bm["sharpe"],
                "beat_spy": bool(sm["cagr"] > bm["cagr"]),
                "insufficient_history": False,
            })
    return pd.DataFrame(rows)


def _window_summary(windows: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for years, group in windows.groupby("years", sort=True):
        valid = group[~group["insufficient_history"]].copy()
        if valid.empty:
            rows.append({
                "years": years,
                "n_windows": 0,
                "pct_beat_spy": np.nan,
                "median_edge": np.nan,
                "worst_edge": np.nan,
                "best_edge": np.nan,
                "worst_strategy_cagr": np.nan,
                "median_strategy_cagr": np.nan,
                "worst_strategy_mdd": np.nan,
                "worst_window_start": None,
                "worst_window_end": None,
            })
            continue
        worst = valid.sort_values("edge").iloc[0]
        rows.append({
            "years": years,
            "n_windows": int(len(valid)),
            "pct_beat_spy": float(valid["beat_spy"].mean()),
            "median_edge": float(valid["edge"].median()),
            "worst_edge": float(valid["edge"].min()),
            "best_edge": float(valid["edge"].max()),
            "worst_strategy_cagr": float(valid["strategy_cagr"].min()),
            "median_strategy_cagr": float(valid["strategy_cagr"].median()),
            "worst_strategy_mdd": float(valid["strategy_mdd"].min()),
            "worst_window_start": worst["start"],
            "worst_window_end": worst["end"],
        })
    return pd.DataFrame(rows)


def _plot_equity(aligned: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(aligned.index, aligned["strategy_equity"], label="lb80/k5/SMA250 PIT", linewidth=1.5)
    ax.plot(aligned.index, aligned["spy_equity"], label="SPY", color="black", linestyle="--", linewidth=1.4)
    ax.set_yscale("log")
    ax.set_title("lb80/k5/SMA250 PIT vs SPY")
    ax.set_ylabel("Equity ($, log scale)")
    ax.grid(True, which="both", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_relative(aligned: pd.DataFrame, out_path: Path) -> None:
    ratio = (aligned["strategy_equity"] / aligned["strategy_equity"].iloc[0]) / (aligned["spy_equity"] / aligned["spy_equity"].iloc[0])
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(ratio.index, ratio, label="Strategy / SPY", linewidth=1.5)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_yscale("log")
    ax.set_title("Relative equity: lb80/k5/SMA250 PIT / SPY")
    ax.set_ylabel("Relative equity")
    ax.grid(True, which="both", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_rolling_cagr(aligned: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(15, 13), sharex=False)
    for ax, years in zip(axes.ravel(), (1, 3, 5, 10, 15, 20), strict=True):
        bars = years * 252
        if len(aligned) <= bars:
            ax.text(0.5, 0.5, f"Insufficient history for {years}y", ha="center", va="center")
            ax.set_title(f"{years}y rolling CAGR")
            ax.grid(True, alpha=0.25)
            continue
        strat = (aligned["strategy_equity"] / aligned["strategy_equity"].shift(bars)) ** (1.0 / years) - 1.0
        spy = (aligned["spy_equity"] / aligned["spy_equity"].shift(bars)) ** (1.0 / years) - 1.0
        ax.plot(strat.index, strat * 100.0, label="Strategy", linewidth=1.2)
        ax.plot(spy.index, spy * 100.0, label="SPY", color="black", linestyle="--", linewidth=1.2)
        ax.axhline(0.0, color="black", linewidth=0.7, alpha=0.5)
        ax.set_title(f"{years}y rolling CAGR")
        ax.set_ylabel("CAGR (%)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Rolling CAGR by entry window vs SPY", y=0.995)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_window_edge_distributions(windows: pd.DataFrame, out_path: Path) -> None:
    valid = windows[~windows["insufficient_history"]].copy()
    fig, ax = plt.subplots(figsize=(12, 7))
    data = [valid.loc[valid["years"] == y, "edge"].dropna() * 100.0 for y in (1, 3, 5, 10, 15, 20)]
    labels = ["1y", "3y", "5y", "10y", "15y", "20y"]
    ax.boxplot(data, tick_labels=labels, showfliers=False)
    ax.axhline(0.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_title("Strategy CAGR edge vs SPY across all entry windows")
    ax.set_ylabel("CAGR edge (pp)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_window_win_rates(summary: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = [f"{int(y)}y" for y in summary["years"]]
    values = summary["pct_beat_spy"] * 100.0
    ax.bar(labels, values)
    ax.axhline(50.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_ylim(0, 100)
    ax.set_title("Percent of all entry windows beating SPY")
    ax.set_ylabel("Win rate (%)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _write_report(
    out_path: Path,
    full_metrics: pd.DataFrame,
    dsr_rows: pd.DataFrame,
    window_summary: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    lines = [
        "# lb80/k5/SMA250 Deep Dive",
        "",
        "## Setup",
        "",
        "- Strategy: `lookback=80`, `top_k=5`, `SPY>SMA250`, cash when all momentum is non-positive.",
        "- Universe: approximate S&P 500 PIT membership via Wikipedia selected changes.",
        f"- DSR primary trial count: `{args.n_trials}` `[advances_fin_ml, p.273-275]`.",
        "- Entry-window robustness: every possible 1/3/5/10/15/20y window `[trading_systems_methods, ch.21]`.",
        "",
        "## Full Period Metrics",
        "",
        full_metrics.to_markdown(index=False),
        "",
        "## Why DSR Fails",
        "",
        dsr_rows.to_markdown(index=False),
        "",
        "Interpretation: DSR fails at the 200-trial penalty because the annual Sharpe around 1.05 is not high enough once the expected best Sharpe from a broad search is used as the benchmark. The no-trial PSR is much more favorable, so the issue is not that the return stream is weak in isolation; it is that the study has already spent many trials.",
        "",
        "## All Entry Windows",
        "",
        window_summary.to_markdown(index=False),
        "",
        "## Plots",
        "",
        "![Equity vs SPY](plots/equity_vs_spy.png)",
        "",
        "![Equity over SPY](plots/equity_over_spy.png)",
        "",
        "![Rolling CAGR](plots/rolling_cagr_1_3_5_10_15_20y.png)",
        "",
        "![Entry window edge distributions](plots/entry_window_edge_distributions.png)",
        "",
        "![Entry window win rates](plots/entry_window_win_rates.png)",
        "",
        "## Caveats",
        "",
        "- 15y/20y windows are unavailable if the PIT candidate history is shorter than those horizons.",
        "- PIT membership is approximate and still lacks a survivorship-free/delisted price feed.",
        "- The DSR trial count is intentionally conservative because the candidate emerged after broad sweeps.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
