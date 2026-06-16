#!/usr/bin/env python3
"""Focused diagnostics for one US-stocks 13612 heatmap finalist.

The report is research-only. It reconstructs the selected current-S&P-500
yfinance path, compares it to adjacent mechanisms, and audits whether the
absolute-momentum cash filter actually changed holdings. Momentum ranking and
monthly review follow `[stocks_on_the_move, p.60]` and
`[stocks_on_the_move, p.98-99]`; inverse-volatility sizing follows
`[systematic_trading, p.137-148]`; yfinance/current-universe caveats follow
`[advances_fin_ml, p.208-211]`; rolling relative windows follow
`[testing_tuning, p.327-335]`.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from studies.momentum_13612_universes.core import metrics_from_returns  # noqa: E402
from studies.momentum_13612_universes.extensive import (  # noqa: E402
    ExtensiveConfig,
    SimulationResult,
    apply_br_foreign_annual_tax,
    benchmark_returns_for,
    precompute_scores,
    result_row,
    rolling_relative_equity_windows,
    simulate_extensive_config,
)
from studies.momentum_13612_universes.run import (  # noqa: E402
    fmt_num,
    fmt_pct,
    json_safe,
    md_table,
    safe_filename,
)
from studies.momentum_13612_universes.universes import (  # noqa: E402
    drop_extreme_return_tickers,
    load_tiingo_price_frame,
    load_yfinance_price_frame,
    us_stock_tickers_with_membership,
)


STUDY_DIR = Path(__file__).resolve().parent
STOCKS_DIR = STUDY_DIR / "us" / "stocks"
RESULTS_DIR = STOCKS_DIR / "results"
PLOTS_DIR = STOCKS_DIR / "plots" / "analysis"
TIINGO_ROOT = REPO_ROOT / "data" / "tiingo"

TARGET_NAME = "mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0"
REPORT = STOCKS_DIR / "ANALYSIS_raw_abs_cash_lb6_top5_reb3_off0.md"
RESULT_STEM = "analysis_raw_abs_cash_lb6_top5_reb3_off0"
HEATMAP_TRIALS = 4092

CRISIS_WINDOWS = {
    # Stress windows are diagnostics, not tuned gates `[testing_tuning, p.327-335]`.
    "dotcom": ("2000-03-01", "2002-10-31"),
    "gfc": ("2007-10-01", "2009-03-31"),
    "covid": ("2020-02-01", "2020-04-30"),
    "inflation_2022": ("2022-01-01", "2022-12-31"),
}


@dataclass(frozen=True)
class AnalyzedConfig:
    config: ExtensiveConfig
    simulation: SimulationResult
    gross_returns: pd.Series
    after_tax_returns: pd.Series
    tax_summary: dict[str, object]
    row: dict[str, object]
    strategy_returns: pd.Series
    benchmark_returns: pd.Series


@dataclass(frozen=True)
class ConfigSpec:
    config: ExtensiveConfig
    lookback_label: str
    lookback_months: tuple[int, ...]


def load_price_inputs(
    args: argparse.Namespace,
) -> tuple[tuple[str, ...], pd.DataFrame, pd.DataFrame, object | None, list[str]]:
    tickers_list, eligible_by_date = us_stock_tickers_with_membership(
        TIINGO_ROOT,
        limit=args.max_us_stocks,
        universe=args.us_stock_universe,
        start=args.start,
        end=args.end,
    )
    tickers = tuple(tickers_list)
    if args.us_source == "tiingo":
        prices = load_tiingo_price_frame(tickers, TIINGO_ROOT, args.start, args.end)
    else:
        if not args.allow_biased_yfinance:
            raise ValueError("yfinance source requires --allow-biased-yfinance")
        prices = load_yfinance_price_frame(tickers, args.start, args.end)
    prices, dropped_extreme = drop_extreme_return_tickers(prices, args.max_abs_daily_return)
    tickers = tuple(ticker for ticker in tickers if ticker in prices.columns)
    benchmark_prices = load_yfinance_price_frame(("SPY",), args.start, args.end, allow_missing=False)
    return tickers, prices, benchmark_prices, eligible_by_date, dropped_extreme


def comparison_specs(tickers: tuple[str, ...], args: argparse.Namespace) -> list[ConfigSpec]:
    common = {
        "universe": "us_stocks",
        "assets": tickers,
        "top_n": 5,
        "rebalance_months": 3,
        "rebalance_offset": 0,
        "score_mode": "raw_13612",
        "vol_window_days": args.vol_window_days,
        "trend_window_days": args.trend_window_days,
    }
    configs = [
        (
            "mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0",
            "equal",
            False,
        ),
        (
            TARGET_NAME,
            "equal",
            True,
        ),
        (
            "mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb3_off0",
            "inverse_vol",
            False,
        ),
    ]
    return [
        ConfigSpec(
            config=ExtensiveConfig(
                name=name,
                weight_mode=weight_mode,  # type: ignore[arg-type]
                absolute_filter=absolute_filter,
                **common,
            ),
            lookback_label="lb6",
            lookback_months=(6,),
        )
        for name, weight_mode, absolute_filter in configs
    ]


def lookback_months_from_label(label: str) -> tuple[int, ...]:
    if label.startswith("lb"):
        return tuple(int(part) for part in label[2:].split("_") if part)
    return (1, 3, 6, 12)


def bool_from_value(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def heatmap_top20_specs(
    tickers: tuple[str, ...], args: argparse.Namespace
) -> tuple[list[ConfigSpec], dict[str, list[str]], pd.DataFrame]:
    path = RESULTS_DIR / "heatmap_results.csv"
    if not path.exists():
        return [], {}, pd.DataFrame()
    results = pd.read_csv(path)
    if results.empty:
        return [], {}, pd.DataFrame()

    top_count = int(args.top20_count)
    top_sharpe = results.nlargest(top_count, "after_tax_sharpe").copy()
    top_relative = results.nlargest(top_count, "rolling_rel_score").copy()
    groups = {
        "Top 20 After-Tax Sharpe": [str(name) for name in top_sharpe["name"]],
        "Top 20 Rolling Relative": [str(name) for name in top_relative["name"]],
    }
    selected = pd.concat([top_sharpe, top_relative], ignore_index=True).drop_duplicates("name")

    specs: list[ConfigSpec] = []
    for _, row in selected.iterrows():
        lookback_label = str(row["lookback_label"])
        months = lookback_months_from_label(lookback_label)
        specs.append(
            ConfigSpec(
                config=ExtensiveConfig(
                    name=str(row["name"]),
                    universe="us_stocks",
                    assets=tickers,
                    top_n=int(row["top_n"]),
                    rebalance_months=int(row["rebalance_months"]),
                    rebalance_offset=int(row["rebalance_offset"]),
                    score_mode=str(row["score_mode"]),  # type: ignore[arg-type]
                    weight_mode=str(row["weight_mode"]),  # type: ignore[arg-type]
                    absolute_filter=bool_from_value(row["absolute_filter"]),
                    vol_window_days=args.vol_window_days,
                    trend_window_days=args.trend_window_days,
                ),
                lookback_label=lookback_label,
                lookback_months=months,
            )
        )
    return specs, groups, selected


def merge_specs(*spec_groups: list[ConfigSpec]) -> list[ConfigSpec]:
    merged: dict[str, ConfigSpec] = {}
    for specs in spec_groups:
        for spec in specs:
            merged.setdefault(spec.config.name, spec)
    return list(merged.values())


def analyze_configs(
    tickers: tuple[str, ...],
    prices: pd.DataFrame,
    benchmark_prices: pd.DataFrame,
    eligible_by_date: object | None,
    args: argparse.Namespace,
    specs: list[ConfigSpec],
) -> dict[str, AnalyzedConfig]:
    unique_lookbacks = {
        spec.lookback_label: spec.lookback_months
        for spec in specs
    }
    bundles = {
        label: precompute_scores(
            prices,
            tickers,
            vol_window_days=args.vol_window_days,
            trend_window_days=args.trend_window_days,
            lookback_months=months,
        )
        for label, months in unique_lookbacks.items()
    }
    out: dict[str, AnalyzedConfig] = {}
    for spec in specs:
        config = spec.config
        simulation = simulate_extensive_config(
            prices,
            bundles[spec.lookback_label],
            config,
            eligible_by_date=eligible_by_date,  # type: ignore[arg-type]
        )
        tax = apply_br_foreign_annual_tax(simulation.returns, simulation.daily_weights)
        row = result_row(
            config,
            simulation,
            benchmark_prices,
            n_trials=args.n_trials,
            ranked_returns=tax.returns,
            tax_summary=tax.summary,
        )
        strategy_returns, benchmark_returns = benchmark_returns_for(tax.returns, benchmark_prices)
        out[config.name] = AnalyzedConfig(
            config=config,
            simulation=simulation,
            gross_returns=simulation.returns,
            after_tax_returns=tax.returns,
            tax_summary=tax.summary,
            row=row,
            strategy_returns=strategy_returns,
            benchmark_returns=benchmark_returns,
        )
    return out


def aligned_weight_frames(left: pd.DataFrame, right: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    index = left.index.union(right.index).sort_values()
    columns = sorted(set(left.columns) | set(right.columns))
    return (
        left.reindex(index=index, columns=columns, fill_value=0.0).fillna(0.0),
        right.reindex(index=index, columns=columns, fill_value=0.0).fillna(0.0),
    )


def weight_diff_summary(target: AnalyzedConfig, baseline: AnalyzedConfig) -> dict[str, object]:
    target_daily, base_daily = aligned_weight_frames(
        target.simulation.daily_weights,
        baseline.simulation.daily_weights,
    )
    daily_diff = (target_daily - base_daily).abs().sum(axis=1)
    target_reb, base_reb = aligned_weight_frames(
        target.simulation.rebalance_weights,
        baseline.simulation.rebalance_weights,
    )
    rebalance_diff = (target_reb - base_reb).abs().sum(axis=1)
    return {
        "max_daily_weight_l1_diff": float(daily_diff.max()) if len(daily_diff) else 0.0,
        "differing_days": int((daily_diff > 1e-12).sum()),
        "pct_differing_days": float((daily_diff > 1e-12).mean()) if len(daily_diff) else 0.0,
        "max_rebalance_weight_l1_diff": (
            float(rebalance_diff.max()) if len(rebalance_diff) else 0.0
        ),
        "differing_rebalances": int((rebalance_diff > 1e-12).sum()),
    }


def exposure_summary(analysis: AnalyzedConfig) -> dict[str, object]:
    weights = analysis.simulation.daily_weights.reindex(analysis.after_tax_returns.index).fillna(0.0)
    exposure = weights.sum(axis=1)
    rebalance_exposure = analysis.simulation.rebalance_weights.sum(axis=1)
    holdings_count = (analysis.simulation.rebalance_weights > 1e-12).sum(axis=1)
    return {
        "avg_daily_gross_exposure": float(exposure.mean()) if len(exposure) else float("nan"),
        "min_daily_gross_exposure": float(exposure.min()) if len(exposure) else float("nan"),
        "pct_days_below_full_exposure": float((exposure < 1.0 - 1e-12).mean())
        if len(exposure)
        else float("nan"),
        "pct_days_all_cash": float((exposure <= 1e-12).mean()) if len(exposure) else float("nan"),
        "rebalance_events_below_full_exposure": int((rebalance_exposure < 1.0 - 1e-12).sum()),
        "min_rebalance_gross_exposure": float(rebalance_exposure.min())
        if len(rebalance_exposure)
        else float("nan"),
        "avg_names_at_rebalance": float(holdings_count.mean())
        if len(holdings_count)
        else float("nan"),
        "min_names_at_rebalance": int(holdings_count.min()) if len(holdings_count) else 0,
    }


def calendar_year_returns(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> pd.DataFrame:
    aligned = pd.concat(
        {"strategy": strategy_returns.astype(float), "spy": benchmark_returns.astype(float)},
        axis=1,
    ).dropna()
    rows: list[dict[str, object]] = []
    for year, group in aligned.groupby(aligned.index.year):
        strategy_return = float((1.0 + group["strategy"]).prod() - 1.0)
        spy_return = float((1.0 + group["spy"]).prod() - 1.0)
        rows.append(
            {
                "year": int(year),
                "strategy_return": strategy_return,
                "spy_return": spy_return,
                "excess_return": strategy_return - spy_return,
                "strategy_won": strategy_return > spy_return,
            }
        )
    return pd.DataFrame(rows)


def period_metric_rows(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for label, (start, end) in CRISIS_WINDOWS.items():
        strat = strategy_returns.loc[pd.Timestamp(start) : pd.Timestamp(end)].dropna()
        spy = benchmark_returns.loc[pd.Timestamp(start) : pd.Timestamp(end)].dropna()
        if strat.empty or spy.empty:
            continue
        strat_metrics = metrics_from_returns(strat)
        spy_metrics = metrics_from_returns(spy)
        rows.append(
            {
                "period": label,
                "start": start,
                "end": end,
                "strategy_cagr": float(strat_metrics["cagr"]),
                "strategy_mdd": float(strat_metrics["mdd"]),
                "strategy_sharpe": float(strat_metrics["sharpe"]),
                "spy_cagr": float(spy_metrics["cagr"]),
                "spy_mdd": float(spy_metrics["mdd"]),
                "spy_sharpe": float(spy_metrics["sharpe"]),
                "mdd_delta": float(strat_metrics["mdd"]) - float(spy_metrics["mdd"]),
            }
        )
    return pd.DataFrame(rows)


def drawdown_periods(returns: pd.Series, top_n: int = 10) -> pd.DataFrame:
    clean = returns.dropna().astype(float)
    if clean.empty:
        return pd.DataFrame()
    equity = (1.0 + clean).cumprod()
    running_peak = equity.cummax()
    drawdown = equity / running_peak - 1.0

    rows: list[dict[str, object]] = []
    in_drawdown = False
    peak_date = drawdown.index[0]
    start_date = drawdown.index[0]
    valley_date = drawdown.index[0]
    valley = 0.0

    for date, value in drawdown.items():
        dd_value = float(value)
        if dd_value < -1e-12 and not in_drawdown:
            in_drawdown = True
            peak_level = float(running_peak.loc[date])
            peak_candidates = equity.loc[:date][equity.loc[:date] >= peak_level * (1.0 - 1e-12)]
            peak_date = pd.Timestamp(peak_candidates.index[-1]) if len(peak_candidates) else pd.Timestamp(date)
            start_date = pd.Timestamp(date)
            valley_date = pd.Timestamp(date)
            valley = dd_value
        elif in_drawdown:
            if dd_value < valley:
                valley = dd_value
                valley_date = pd.Timestamp(date)
            if dd_value >= -1e-12:
                rows.append(
                    drawdown_row(peak_date, start_date, valley_date, pd.Timestamp(date), valley)
                )
                in_drawdown = False

    if in_drawdown:
        rows.append(drawdown_row(peak_date, start_date, valley_date, None, valley, clean.index[-1]))

    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows).sort_values("depth").head(top_n).reset_index(drop=True)
    return out


def drawdown_row(
    peak_date: pd.Timestamp,
    start_date: pd.Timestamp,
    valley_date: pd.Timestamp,
    recovery_date: pd.Timestamp | None,
    depth: float,
    last_date: pd.Timestamp | None = None,
) -> dict[str, object]:
    end_date = recovery_date if recovery_date is not None else pd.Timestamp(last_date or valley_date)
    return {
        "peak": str(pd.Timestamp(peak_date).date()),
        "start": str(pd.Timestamp(start_date).date()),
        "valley": str(pd.Timestamp(valley_date).date()),
        "recovery": str(pd.Timestamp(recovery_date).date()) if recovery_date is not None else "open",
        "depth": float(depth),
        "underwater_days": int((pd.Timestamp(end_date) - pd.Timestamp(peak_date)).days),
    }


def rolling_window_rows(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for horizon in (3, 5, 10, 15, 20):
        windows = rolling_relative_equity_windows(strategy_returns, benchmark_returns, horizon)
        if windows.empty:
            continue
        windows = windows.copy()
        windows.insert(0, "horizon_years", horizon)
        frames.append(windows)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["start"] = pd.to_datetime(out["start"]).dt.date.astype(str)
    out["end"] = pd.to_datetime(out["end"]).dt.date.astype(str)
    return out


def rolling_summary_rows(windows: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if windows.empty:
        return pd.DataFrame()
    for horizon, group in windows.groupby("horizon_years"):
        rows.append(
            {
                "horizon_years": int(horizon),
                "windows": int(len(group)),
                "above_mean": float(group["pct_time_above_benchmark"].mean()),
                "above_p25": float(group["pct_time_above_benchmark"].quantile(0.25)),
                "above_min": float(group["pct_time_above_benchmark"].min()),
                "terminal_median": float(group["terminal_relative"].median()),
                "terminal_p25": float(group["terminal_relative"].quantile(0.25)),
                "terminal_min": float(group["terminal_relative"].min()),
                "relative_mdd_median": float(group["relative_mdd"].median()),
            }
        )
    return pd.DataFrame(rows)


def parse_float_tuple(raw: str) -> tuple[float, ...]:
    values = tuple(float(part.strip()) for part in raw.split(",") if part.strip())
    if not values or any(value < 0.0 or value > 1.0 for value in values):
        raise ValueError("weights must be comma-separated decimals in [0, 1]")
    return values


def sleeve_blend_rows(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    weights: tuple[float, ...],
) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    aligned = pd.concat(
        {
            "strategy": strategy_returns.dropna().astype(float),
            "spy": benchmark_returns.dropna().astype(float),
        },
        axis=1,
    ).dropna()
    rows: list[dict[str, object]] = []
    returns_by_label: dict[str, pd.Series] = {}
    if aligned.empty:
        return pd.DataFrame(), returns_by_label
    spy_equity = (1.0 + aligned["spy"]).cumprod()
    for weight in weights:
        label = f"{int(round(weight * 100.0))}% strategy / {int(round((1.0 - weight) * 100.0))}% SPY"
        blended = (weight * aligned["strategy"] + (1.0 - weight) * aligned["spy"]).rename(label)
        metrics = metrics_from_returns(blended)
        blend_equity = (1.0 + blended).cumprod()
        rows.append(
            {
                "sleeve": label,
                "strategy_weight": weight,
                "cagr": float(metrics["cagr"]),
                "mdd": float(metrics["mdd"]),
                "vol": float(metrics["vol"]),
                "sharpe": float(metrics["sharpe"]),
                "terminal_vs_spy": float(blend_equity.iloc[-1] / spy_equity.iloc[-1]),
            }
        )
        returns_by_label[label] = blended
    return pd.DataFrame(rows), returns_by_label


def rebalance_rows(analysis: AnalyzedConfig) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for date, weights in analysis.simulation.rebalance_weights.iterrows():
        active = weights[weights > 1e-12].sort_values(ascending=False)
        rows.append(
            {
                "date": str(pd.Timestamp(date).date()),
                "gross_exposure": float(active.sum()),
                "cash_weight": float(1.0 - active.sum()),
                "n_holdings": int(len(active)),
                "holdings": ", ".join(
                    f"{ticker}:{100.0 * float(weight):.1f}%" for ticker, weight in active.items()
                ),
            }
        )
    return pd.DataFrame(rows)


def top_holdings_rows(analysis: AnalyzedConfig) -> pd.DataFrame:
    rows: dict[str, dict[str, float]] = {}
    weights = analysis.simulation.rebalance_weights
    for _date, row in weights.iterrows():
        for ticker, weight in row[row > 1e-12].items():
            item = rows.setdefault(str(ticker), {"rebalance_count": 0.0, "weight_sum": 0.0})
            item["rebalance_count"] += 1.0
            item["weight_sum"] += float(weight)
    total_rebalances = max(len(weights), 1)
    out = [
        {
            "ticker": ticker,
            "rebalance_count": int(values["rebalance_count"]),
            "pct_rebalances": values["rebalance_count"] / total_rebalances,
            "avg_weight_when_held": values["weight_sum"] / values["rebalance_count"],
        }
        for ticker, values in rows.items()
    ]
    return pd.DataFrame(out).sort_values(
        ["rebalance_count", "ticker"],
        ascending=[False, True],
    )


def write_plots(
    analyses: dict[str, AnalyzedConfig],
    target: AnalyzedConfig,
    top20_groups: dict[str, list[str]],
    sleeve_returns: dict[str, pd.Series],
) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []

    def short_label(name: str) -> str:
        return name.replace("mom13612_us_stocks_", "")

    def save_group_plot(title: str, names: list[str], filename: str) -> None:
        fig, ax = plt.subplots(figsize=(13, 7))
        spy = (1.0 + target.benchmark_returns).cumprod()
        spy.plot(ax=ax, color="black", linewidth=1.8, label="SPY")
        target_plotted = False
        for name in names:
            analysis = analyses.get(name)
            if analysis is None:
                continue
            if name == TARGET_NAME:
                target_plotted = True
                continue
            equity = (1.0 + analysis.strategy_returns).cumprod()
            equity.plot(ax=ax, linewidth=0.9, alpha=0.62, label=short_label(name))
        if target_plotted or TARGET_NAME in analyses:
            target_equity = (1.0 + target.strategy_returns).cumprod()
            target_equity.plot(ax=ax, color="tab:red", linewidth=2.4, label="TARGET raw_abs_cash lb6 top5")
        ax.set_title(title)
        ax.set_ylabel("Growth of $1, log scale")
        ax.set_yscale("log")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=6, ncol=2)
        fig.tight_layout()
        path = PLOTS_DIR / filename
        fig.savefig(path, dpi=140)
        plt.close(fig)
        paths.append(str(path.relative_to(STOCKS_DIR)))

    aligned = pd.concat(
        {
            "Strategy": (1.0 + target.strategy_returns).cumprod(),
            "SPY": (1.0 + target.benchmark_returns).cumprod(),
        },
        axis=1,
    ).dropna()
    relative = aligned["Strategy"] / aligned["SPY"]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    aligned.plot(ax=axes[0], linewidth=1.1)
    axes[0].set_title(f"{TARGET_NAME}: after-tax equity vs SPY")
    axes[0].set_ylabel("Growth of $1, log scale")
    axes[0].set_yscale("log")
    axes[0].grid(True, which="both", alpha=0.3)
    relative.plot(ax=axes[1], color="black", linewidth=1.1)
    axes[1].axhline(1.0, color="gray", linestyle="--", linewidth=1.0)
    axes[1].set_title("Strategy / SPY relative equity")
    axes[1].set_ylabel("Ratio, log scale")
    axes[1].set_yscale("log")
    axes[1].grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    path = PLOTS_DIR / f"{safe_filename(TARGET_NAME)}_vs_SPY.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    paths.append(str(path.relative_to(STOCKS_DIR)))

    save_group_plot(
        "Adjacent mechanism comparison: after-tax growth of $1",
        [
            "mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0",
            TARGET_NAME,
            "mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb3_off0",
        ],
        f"{RESULT_STEM}_adjacent_mechanisms_log_equity.png",
    )
    for group_name, names in top20_groups.items():
        filename = f"{RESULT_STEM}_{safe_filename(group_name.lower())}_log_equity.png"
        save_group_plot(f"{group_name}: after-tax growth of $1", names, filename)

    if sleeve_returns:
        fig, ax = plt.subplots(figsize=(13, 7))
        spy = (1.0 + target.benchmark_returns).cumprod()
        spy.plot(ax=ax, color="black", linewidth=1.8, label="SPY")
        for label, returns in sleeve_returns.items():
            equity = (1.0 + returns).cumprod()
            equity.plot(ax=ax, linewidth=1.2, label=label)
        target_equity = (1.0 + target.strategy_returns).cumprod()
        target_equity.plot(ax=ax, color="tab:red", linewidth=2.2, label="100% TARGET")
        ax.set_title("Portfolio-sleeve blends vs SPY")
        ax.set_ylabel("Growth of $1, log scale")
        ax.set_yscale("log")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        path = PLOTS_DIR / f"{RESULT_STEM}_sleeve_blends_log_equity.png"
        fig.savefig(path, dpi=140)
        plt.close(fig)
        paths.append(str(path.relative_to(STOCKS_DIR)))

    return paths


def metric_table_rows(
    analyses: dict[str, AnalyzedConfig],
    names: list[str] | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    selected_names = names or list(analyses)
    for name in selected_names:
        analysis = analyses[name]
        row = analysis.row
        rows.append(
            {
                "Name": name.replace("mom13612_us_stocks_", ""),
                "CAGR": fmt_pct(float(row["after_tax_cagr"])),
                "MDD": fmt_pct(float(row["after_tax_mdd"])),
                "Sharpe": fmt_num(float(row["after_tax_sharpe"])),
                "Vol": fmt_pct(float(row["after_tax_vol"])),
                "Calmar": fmt_num(float(row["after_tax_calmar"])),
                "Terminal/SPY": fmt_num(float(row["terminal_relative"])),
                "RollRel": fmt_pct(float(row["rolling_rel_score"])),
                "RollP25": fmt_pct(float(row["rolling_rel_p25_score"])),
                "Turnover/Yr": fmt_num(float(row["annual_turnover"])),
            }
        )
    target = analyses[TARGET_NAME]
    rows.append(
        {
            "Name": "SPY benchmark",
            "CAGR": fmt_pct(float(target.row["spy_cagr"])),
            "MDD": fmt_pct(float(target.row["spy_mdd"])),
            "Sharpe": fmt_num(float(target.row["spy_sharpe"])),
            "Vol": fmt_pct(float(target.row["spy_vol"])),
            "Calmar": "n/a",
            "Terminal/SPY": "1.000",
            "RollRel": "n/a",
            "RollP25": "n/a",
            "Turnover/Yr": "0.000",
        }
    )
    return rows


def pct_row_table(frame: pd.DataFrame, limit: int | None = None) -> list[dict[str, object]]:
    data = frame.head(limit) if limit else frame
    rows: list[dict[str, object]] = []
    for _, row in data.iterrows():
        out: dict[str, object] = {}
        for column, value in row.items():
            if column in {
                "horizon_years",
                "windows",
                "year",
                "underwater_days",
                "rebalance_count",
            }:
                out[column] = int(value)
            elif isinstance(value, float) and any(
                token in column
                for token in ("cagr", "return", "mdd", "above", "depth", "pct", "weight", "vol")
            ):
                out[column] = fmt_pct(float(value))
            elif isinstance(value, float):
                out[column] = fmt_num(float(value))
            else:
                out[column] = value
        rows.append(out)
    return rows


def write_report(
    args: argparse.Namespace,
    analyses: dict[str, AnalyzedConfig],
    dropped_extreme: list[str],
    diff_summary: dict[str, object],
    exposure: dict[str, object],
    sleeve_frame: pd.DataFrame,
    annual: pd.DataFrame,
    periods: pd.DataFrame,
    strategy_drawdowns: pd.DataFrame,
    spy_drawdowns: pd.DataFrame,
    rolling_summary: pd.DataFrame,
    worst_windows: pd.DataFrame,
    top_holdings: pd.DataFrame,
    rebalance_frame: pd.DataFrame,
    plot_paths: list[str],
) -> None:
    target = analyses[TARGET_NAME]
    row = target.row
    display_end = args.end or row["end"]
    cash_changed = int(diff_summary["differing_days"]) > 0
    best_year = annual.sort_values("excess_return", ascending=False).head(1).iloc[0]
    worst_year = annual.sort_values("excess_return", ascending=True).head(1).iloc[0]
    win_rate = float(annual["strategy_won"].mean()) if len(annual) else float("nan")

    outputs = [
        f"[summary JSON](results/{RESULT_STEM}_summary.json)",
        f"[annual returns CSV](results/{RESULT_STEM}_annual_returns.csv)",
        f"[rolling windows CSV](results/{RESULT_STEM}_rolling_windows.csv)",
        f"[rebalances CSV](results/{RESULT_STEM}_rebalances.csv)",
        f"[top holdings CSV](results/{RESULT_STEM}_top_holdings.csv)",
        f"[sleeve blends CSV](results/{RESULT_STEM}_sleeve_blends.csv)",
        f"[top-20 selected CSV](results/{RESULT_STEM}_top20_selected.csv)",
    ]
    plots = [f"[{Path(path).name}]({path})" for path in plot_paths]
    core_names = [
        "mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0",
        TARGET_NAME,
        "mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb3_off0",
    ]

    report = (
        f"# Focused Analysis - `{TARGET_NAME}`\n\n"
        "Status: research-only. No deployment, paper-trade label or mandate change.\n\n"
        "## Verdict\n\n"
        f"- Full-period after-tax metrics: CAGR `{fmt_pct(float(row['after_tax_cagr']))}`, "
        f"MDD `{fmt_pct(float(row['after_tax_mdd']))}`, Sharpe "
        f"`{fmt_num(float(row['after_tax_sharpe']))}` versus SPY CAGR "
        f"`{fmt_pct(float(row['spy_cagr']))}` and SPY MDD "
        f"`{fmt_pct(float(row['spy_mdd']))}`.\n"
        f"- Rolling relative dominance is high: score "
        f"`{fmt_pct(float(row['rolling_rel_score']))}`, p25 "
        f"`{fmt_pct(float(row['rolling_rel_p25_score']))}`, min "
        f"`{fmt_pct(float(row['rolling_rel_min_score']))}`, terminal/SPY "
        f"`{fmt_num(float(row['terminal_relative']))}`.\n"
        f"- Cash-filter audit: `{'changed holdings' if cash_changed else 'no holding change'}` "
        "versus the raw equal-weight variant. The target is therefore not a "
        "distinct cash-filter improvement on this path.\n"
        "- Portfolio-sleeve conclusion: not efficient enough for real allocation "
        "today. In the biased backtest a small sleeve improves SPY blends, but the "
        "evidence is not investable because the signal is current-universe yfinance, "
        "the cash filter is inactive, and drawdown remains equity-crisis sized. "
        "Operational weight under the mandate remains `0%`.\n"
        f"- Risk remains severe: worst strategy drawdown "
        f"`{fmt_pct(float(strategy_drawdowns.iloc[0]['depth']))}` and GFC MDD "
        f"`{fmt_pct(float(periods.loc[periods['period'] == 'gfc'].iloc[0]['strategy_mdd']))}`.\n"
        "- This remains non-promotable because the run uses yfinance/current S&P "
        "500 constituents without true PIT/delisted returns `[advances_fin_ml, "
        "p.208-211]`.\n\n"
        "## Setup\n\n"
        f"- Start: `{args.start}`\n"
        f"- End: `{display_end}`\n"
        f"- US source: `{args.us_source}`\n"
        f"- US stock universe: `{args.us_stock_universe}`\n"
        f"- Max US stocks: `{args.max_us_stocks}`\n"
        f"- Max abs daily return filter: `{args.max_abs_daily_return}`\n"
        f"- Dropped extreme-return tickers: `{len(dropped_extreme)}`\n"
        "- Target parameters: raw 6-month cross-sectional momentum, top 5, "
        "quarterly rebalance, offset 0, equal weight, absolute filter enabled "
        "`[stocks_on_the_move, p.60]`, `[stocks_on_the_move, p.98-99]`.\n"
        f"- Heatmap trial count used for DSR context: `{args.n_trials}` "
        "`[advances_fin_ml, p.273-275]`.\n\n"
        "This is a focused rerun from the current local yfinance cache, not a "
        "static read of `heatmap_results.csv`; small metric drift can occur when "
        "the cache is refreshed.\n\n"
        "## Algoritmo E Implementacao\n\n"
        "A estrategia e uma rotacao cross-sectional de momentum de 6 meses em acoes "
        "do S&P 500 atual. Ela nao usa previsao macro, stop, leverage ou overlay de "
        "regime. A decisao e puramente relativa: a cada rebalance, compra as 5 acoes "
        "com maior retorno ajustado de 6 meses, desde que o score absoluto seja "
        "positivo `[stocks_on_the_move, p.60]`. O rebalance e trimestral no offset 0, "
        "isto e, nos fechamentos mensais de janeiro, abril, julho e outubro "
        "`[stocks_on_the_move, p.98-99]`.\n\n"
        "Passos operacionais:\n\n"
        "1. Definir o universo negociavel. Nesta analise: S&P 500 atual via yfinance. "
        "Em implementacao real, isso precisa ser substituido por universo point-in-time "
        "com delisted returns; caso contrario o resultado segue enviesado e nao "
        "promovivel `[advances_fin_ml, p.208-211]`.\n"
        "2. Carregar precos diarios ajustados por dividendos/splits para todos os ativos "
        "e para o benchmark SPY. Usar adjusted close, nao close bruto.\n"
        "3. Converter os precos diarios em precos de fechamento mensal (`resample('ME').last()`).\n"
        "4. Em cada mes de rebalance, calcular `score = price_t / price_{t-6m} - 1`. "
        "O lookback `6m`, `top_n=5` e `rebalance=3m` sao parametros escolhidos apos "
        "o heatmap, logo carregam risco de data mining `[advances_fin_ml, p.273-275]`.\n"
        "5. Ordenar os ativos por score decrescente, com desempate alfabetico estavel.\n"
        "6. Selecionar os 5 primeiros e aplicar o filtro absoluto: manter apenas nomes "
        "com `score > 0`. Se menos de 5 nomes passarem, o peso nao usado fica em cash. "
        "Nesta estrategia especifica, o filtro nunca reduziu exposicao: sempre houve "
        "5 nomes positivos.\n"
        "7. Pesar igualmente os nomes selecionados. Com 5 nomes, cada ativo recebe `20%`; "
        "se somente 3 nomes passassem no filtro, a exposicao seria `60%` e cash `40%`.\n"
        "8. Aplicar os pesos somente aos retornos futuros. Na implementacao do estudo, "
        "isso e feito com `daily_weights.shift(1)`, evitando usar o fechamento do "
        "proprio dia como se fosse executavel antes de conhecido `[advances_fin_ml, p.31-34]`.\n"
        "9. Rebalancear apenas nas datas trimestrais elegiveis; entre rebalances, "
        "manter os pesos-alvo forward-filled.\n"
        "10. Para metricas after-tax, aplicar o modelo anual aproximado de 15% sobre "
        "ganho realizado positivo, com compensacao/carrego de perdas. O modelo nao e "
        "lot-level e nao forca liquidacao final.\n\n"
        "Pseudocodigo:\n\n"
        "```text\n"
        "for each month_end in calendar:\n"
        "    if month_end is not Jan/Apr/Jul/Oct:\n"
        "        continue\n"
        "    scores = adjusted_monthly_price[month_end] / adjusted_monthly_price[month_end - 6 months] - 1\n"
        "    ranked = sort_desc(scores)\n"
        "    chosen = first 5 tickers from ranked where score > 0\n"
        "    target_weight = 1 / 5 for each chosen ticker\n"
        "    cash_weight = 1 - sum(target_weight)\n"
        "    hold target weights until next eligible rebalance\n"
        "daily_return[t] = weights[t-1] * asset_returns[t]\n"
        "```\n\n"
        "Regras de implementacao pratica:\n\n"
        "- Executar no primeiro pregao depois do fechamento mensal usado no sinal, ou "
        "usar explicitamente o close seguinte como preco de execucao. Nao executar no "
        "mesmo close usado para calcular o ranking.\n"
        "- Usar lotes inteiros e caixa residual; o backtest assume pesos fracionarios "
        "continuos, entao uma implementacao real deve registrar tracking error por "
        "arredondamento.\n"
        "- Registrar ordens de venda antes das compras para medir realizacao fiscal e "
        "turnover.\n"
        "- Nao tratar o filtro cash como defesa comprovada: neste path ele ficou inativo.\n"
        "- Antes de qualquer paper/live, reimplementar em dataset PIT/delisted, custos "
        "reais, imposto lot-level, e validar em OOS/WF/PBO/DSR. Sem isso, a alocacao "
        "operacional permanece `0%` `[advances_fin_ml, p.208-211]`, "
        "`[advances_fin_ml, p.273-275]`.\n\n"
        "## Full-Period Metrics\n\n"
        + md_table(
            metric_table_rows(analyses, core_names),
            [
                "Name",
                "CAGR",
                "MDD",
                "Sharpe",
                "Vol",
                "Calmar",
                "Terminal/SPY",
                "RollRel",
                "RollP25",
                "Turnover/Yr",
            ],
        )
        + "\nSPY metrics are the adjusted-close buy-hold benchmark without applying "
        "the annual DARF approximation. Strategy metrics are after the study's "
        "annual 15% realized-gain tax approximation.\n\n"
        "## Portfolio-Sleeve Conclusion\n\n"
        "Direct answer: **no, not for real capital in the current evidence state**. "
        "As a research signal, the backtest is strong enough to keep as an aggressive "
        "diagnostic. As an implementable sleeve, it fails the practical bar: the data "
        "are current-universe yfinance, the absolute/cash filter never reduced risk on "
        "this path, GFC drawdown was worse than SPY, turnover is high, and the result "
        "was selected after a large heatmap `[advances_fin_ml, p.208-211]`, "
        "`[advances_fin_ml, p.273-275]`.\n\n"
        "The table below shows why the temptation exists: in this biased sample, small "
        "SPY blends improve CAGR and terminal wealth. That is useful for sizing "
        "intuition, but it is not allocation evidence. A real sleeve would require a "
        "PIT/delisted dataset, independent validation, real taxes/costs and a "
        "portfolio-level test against the actual core portfolio, not just SPY. Until "
        "then, recommended portfolio weight is `0%`.\n\n"
        + md_table(
            pct_row_table(sleeve_frame),
            ["sleeve", "strategy_weight", "cagr", "mdd", "vol", "sharpe", "terminal_vs_spy"],
        )
        + "\n"
        "## Cash-Filter Audit\n\n"
        + md_table(
            [
                {
                    "Metric": "Max daily L1 weight diff vs raw_equal",
                    "Value": fmt_num(float(diff_summary["max_daily_weight_l1_diff"]), 6),
                },
                {"Metric": "Differing daily weight rows", "Value": diff_summary["differing_days"]},
                {
                    "Metric": "Differing rebalance rows",
                    "Value": diff_summary["differing_rebalances"],
                },
                {
                    "Metric": "Avg daily gross exposure",
                    "Value": fmt_pct(float(exposure["avg_daily_gross_exposure"])),
                },
                {
                    "Metric": "Min daily gross exposure",
                    "Value": fmt_pct(float(exposure["min_daily_gross_exposure"])),
                },
                {
                    "Metric": "Rebalances below full exposure",
                    "Value": exposure["rebalance_events_below_full_exposure"],
                },
                {
                    "Metric": "Avg names at rebalance",
                    "Value": fmt_num(float(exposure["avg_names_at_rebalance"])),
                },
            ],
            ["Metric", "Value"],
        )
        + "\nInterpretation: for this exact `lb6/top5/reb3/off0` path, every selected "
        "top-5 stock had positive 6-month momentum at each active rebalance, so "
        "the absolute filter did not create cash exposure.\n\n"
        "## Rolling Relative Dominance\n\n"
        + md_table(
            pct_row_table(rolling_summary),
            [
                "horizon_years",
                "windows",
                "above_mean",
                "above_p25",
                "above_min",
                "terminal_median",
                "terminal_p25",
                "terminal_min",
                "relative_mdd_median",
            ],
        )
        + "\nWorst reset-window starts by time spent above SPY:\n\n"
        + md_table(
            pct_row_table(worst_windows, limit=10),
            [
                "horizon_years",
                "start",
                "end",
                "pct_time_above_benchmark",
                "terminal_relative",
                "min_relative_equity",
                "relative_mdd",
            ],
        )
        + "\n## Stress Windows\n\n"
        + md_table(
            pct_row_table(periods),
            [
                "period",
                "start",
                "end",
                "strategy_cagr",
                "strategy_mdd",
                "strategy_sharpe",
                "spy_cagr",
                "spy_mdd",
                "spy_sharpe",
                "mdd_delta",
            ],
        )
        + "\n## Calendar Years\n\n"
        f"- Strategy beat SPY in `{fmt_pct(win_rate)}` of calendar years.\n"
        f"- Best excess year: `{int(best_year['year'])}` with excess "
        f"`{fmt_pct(float(best_year['excess_return']))}`.\n"
        f"- Worst excess year: `{int(worst_year['year'])}` with excess "
        f"`{fmt_pct(float(worst_year['excess_return']))}`.\n\n"
        + md_table(
            pct_row_table(annual.sort_values("year", ascending=False), limit=12),
            ["year", "strategy_return", "spy_return", "excess_return", "strategy_won"],
        )
        + "\nFull calendar-year table is in the annual returns CSV.\n\n"
        "## Drawdowns\n\n"
        "Strategy top drawdowns:\n\n"
        + md_table(
            pct_row_table(strategy_drawdowns, limit=10),
            ["peak", "start", "valley", "recovery", "depth", "underwater_days"],
        )
        + "\nSPY top drawdowns over the aligned window:\n\n"
        + md_table(
            pct_row_table(spy_drawdowns, limit=5),
            ["peak", "start", "valley", "recovery", "depth", "underwater_days"],
        )
        + "\n## Holdings And Turnover\n\n"
        f"- Rebalance rows: `{len(rebalance_frame)}`\n"
        f"- Annual turnover: `{fmt_num(float(row['annual_turnover']))}`\n"
        f"- Avg turnover per rebalance: `{fmt_num(float(row['avg_turnover_per_rebalance']))}`\n"
        f"- Avg names changed: `{fmt_num(float(row['avg_names_changed']))}`\n"
        f"- Avg holding months: `{fmt_num(float(row['avg_holding_months']))}`\n\n"
        "Top holdings by rebalance count:\n\n"
        + md_table(
            pct_row_table(top_holdings, limit=20),
            ["ticker", "rebalance_count", "pct_rebalances", "avg_weight_when_held"],
        )
        + "\n## Plots\n\n"
        "All equity and relative-equity plots in this report use log scale.\n\n"
        + "\n".join(f"- {path}" for path in plots)
        + "\n\n## Output Files\n\n"
        + "\n".join(f"- {path}" for path in outputs)
        + "\n\n## Notes\n\n"
        "- Offsets and lookbacks are heatmap dimensions, so this analysis is a "
        "post-selection diagnostic, not a validation pass `[advances_fin_ml, "
        "p.273-275]`.\n"
        "- Current-universe yfinance omits delisted losers and can inflate old "
        "US-stock momentum results `[advances_fin_ml, p.208-211]`.\n"
        "- Rolling relative windows reset both strategy and SPY to 1.0 at each "
        "start date; this is a robustness diagnostic, not a promotion gate "
        "`[testing_tuning, p.327-335]`.\n"
    )
    REPORT.write_text(report, encoding="utf-8")


def write_outputs(
    args: argparse.Namespace,
    analyses: dict[str, AnalyzedConfig],
    dropped_extreme: list[str],
    top20_groups: dict[str, list[str]],
    top20_selected: pd.DataFrame,
) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    target = analyses[TARGET_NAME]
    baseline = analyses["mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0"]
    diff_summary = weight_diff_summary(target, baseline)
    exposure = exposure_summary(target)
    annual = calendar_year_returns(target.strategy_returns, target.benchmark_returns)
    periods = period_metric_rows(target.strategy_returns, target.benchmark_returns)
    strategy_drawdowns = drawdown_periods(target.strategy_returns)
    spy_drawdowns = drawdown_periods(target.benchmark_returns)
    rolling_windows = rolling_window_rows(target.strategy_returns, target.benchmark_returns)
    rolling_summary = rolling_summary_rows(rolling_windows)
    sleeve_frame, sleeve_returns = sleeve_blend_rows(
        target.strategy_returns,
        target.benchmark_returns,
        parse_float_tuple(args.sleeve_weights),
    )
    worst_windows = rolling_windows.sort_values(
        ["pct_time_above_benchmark", "terminal_relative"],
        ascending=[True, True],
    ).head(20)
    rebalances = rebalance_rows(target)
    top_holdings = top_holdings_rows(target)
    plot_paths = write_plots(analyses, target, top20_groups, sleeve_returns)

    annual.to_csv(RESULTS_DIR / f"{RESULT_STEM}_annual_returns.csv", index=False)
    rolling_windows.to_csv(RESULTS_DIR / f"{RESULT_STEM}_rolling_windows.csv", index=False)
    rebalances.to_csv(RESULTS_DIR / f"{RESULT_STEM}_rebalances.csv", index=False)
    top_holdings.to_csv(RESULTS_DIR / f"{RESULT_STEM}_top_holdings.csv", index=False)
    sleeve_frame.to_csv(RESULTS_DIR / f"{RESULT_STEM}_sleeve_blends.csv", index=False)
    top20_selected.to_csv(RESULTS_DIR / f"{RESULT_STEM}_top20_selected.csv", index=False)

    summary = {
        "target": TARGET_NAME,
        "args": vars(args),
        "dropped_extreme_tickers": dropped_extreme,
        "rows": {name: analysis.row for name, analysis in analyses.items()},
        "tax_summary": target.tax_summary,
        "cash_filter_diff_vs_raw_equal": diff_summary,
        "exposure": exposure,
        "sleeve_blends": sleeve_frame.to_dict(orient="records"),
        "top20_groups": top20_groups,
        "top20_selected": top20_selected.to_dict(orient="records"),
        "rolling_summary": rolling_summary.to_dict(orient="records"),
        "worst_rolling_windows": worst_windows.to_dict(orient="records"),
        "strategy_drawdowns": strategy_drawdowns.to_dict(orient="records"),
        "spy_drawdowns": spy_drawdowns.to_dict(orient="records"),
        "top_holdings": top_holdings.head(50).to_dict(orient="records"),
        "plots": plot_paths,
    }
    (RESULTS_DIR / f"{RESULT_STEM}_summary.json").write_text(
        json.dumps(json_safe(summary), indent=2, allow_nan=False),
        encoding="utf-8",
    )

    write_report(
        args,
        analyses,
        dropped_extreme,
        diff_summary,
        exposure,
        sleeve_frame,
        annual,
        periods,
        strategy_drawdowns,
        spy_drawdowns,
        rolling_summary,
        worst_windows,
        top_holdings,
        rebalances,
        plot_paths,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze the raw_abs_cash lb6 top5 stock finalist")
    parser.add_argument("--us-source", choices=["yfinance", "tiingo"], default="yfinance")
    parser.add_argument("--allow-biased-yfinance", action="store_true")
    parser.add_argument(
        "--us-stock-universe",
        choices=["sp500", "tiingo_manifest", "sp500_wikipedia_pit"],
        default="sp500",
    )
    parser.add_argument("--max-us-stocks", type=int, default=9999)
    parser.add_argument("--start", default="1990-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--vol-window-days", type=int, default=126)
    parser.add_argument("--trend-window-days", type=int, default=126)
    parser.add_argument("--n-trials", type=int, default=HEATMAP_TRIALS)
    parser.add_argument("--top20-count", type=int, default=20)
    parser.add_argument("--sleeve-weights", default="0.05,0.10,0.20,0.30")
    parser.add_argument(
        "--max-abs-daily-return",
        type=float,
        default=None,
        help="drop tickers whose adjusted-close daily return exceeds this absolute value",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    tickers, prices, benchmark_prices, eligible_by_date, dropped_extreme = load_price_inputs(args)
    core_specs = comparison_specs(tickers, args)
    top20_specs, top20_groups, top20_selected = heatmap_top20_specs(tickers, args)
    specs = merge_specs(core_specs, top20_specs)
    analyses = analyze_configs(tickers, prices, benchmark_prices, eligible_by_date, args, specs)
    write_outputs(args, analyses, dropped_extreme, top20_groups, top20_selected)
    print(f"wrote {REPORT.relative_to(REPO_ROOT)}")
    print(f"wrote {(RESULTS_DIR / f'{RESULT_STEM}_summary.json').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
