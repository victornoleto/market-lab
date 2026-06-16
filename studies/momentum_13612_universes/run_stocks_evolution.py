#!/usr/bin/env python3
"""Evolve selected US-stocks 13612 heatmap finalists.

This follow-up is intentionally narrow: start from the strongest heatmap regions
and test timing-luck reduction plus simple trend/regime filters. The additions
are not free parameters for winner-picking; they are stress diagnostics for the
finalists `[advances_fin_ml, p.273-275]`. Stock ranking remains cross-sectional
momentum `[stocks_on_the_move, p.60]`; the market and stock trend filters follow
Clenow's S&P 500 200-day regime gate and stock 100-day trend filter
`[stocks_on_the_move, p.66-67, p.81-82, p.98-99]`; daily market cash rotation is
also a Gayed-style volatility-regime test `[leverage_for_the_long_run, p.9,
p.13, p.16]`.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from studies.momentum_13612_universes.core import (  # noqa: E402
    canonicalize_columns,
    daily_weights_from_monthly,
    rank_scores,
)
from studies.momentum_13612_universes.extensive import (  # noqa: E402
    EligibleByDate,
    ExtensiveConfig,
    ScoreBundle,
    SimulationResult,
    apply_br_foreign_annual_tax,
    benchmark_returns_for,
    eligible_assets_for_date,
    precompute_scores,
    result_row,
    turnover_diagnostics,
)
from studies.momentum_13612_universes.run import (  # noqa: E402
    fmt_num,
    fmt_pct,
    json_safe,
    md_table,
)
from studies.momentum_13612_universes.run_extensive import (  # noqa: E402
    pbo_summary,
    plot_strategy_vs_spy,
)
from studies.momentum_13612_universes.run_stocks_heatmap import (  # noqa: E402
    LookbackProfile,
    regime_columns,
)
from studies.momentum_13612_universes.universes import (  # noqa: E402
    drop_extreme_return_tickers,
    load_yfinance_price_frame,
    us_stock_tickers_with_membership,
)


OverlayMode = Literal[
    "none",
    "market_sma200_monthly",
    "market_sma200_daily",
    "stock_sma100",
    "market_sma200_monthly_stock_sma100",
    "market_sma200_daily_stock_sma100",
]
OffsetMode = Literal["fixed", "staggered"]


STUDY_DIR = Path(__file__).resolve().parent
STOCKS_DIR = STUDY_DIR / "us" / "stocks"
RESULTS_DIR = STOCKS_DIR / "results"
PLOTS_DIR = STOCKS_DIR / "plots" / "evolution"
FINALIST_PLOTS_DIR = PLOTS_DIR / "finalists"
REPORT = STOCKS_DIR / "EVOLUTION_REPORT.md"
TIINGO_ROOT = REPO_ROOT / "data" / "tiingo"

OVERLAYS: tuple[OverlayMode, ...] = (
    "none",
    "market_sma200_monthly",
    "market_sma200_daily",
    "stock_sma100",
    "market_sma200_monthly_stock_sma100",
    "market_sma200_daily_stock_sma100",
)
OFFSET_MODES: tuple[OffsetMode, ...] = ("fixed", "staggered")


@dataclass(frozen=True)
class FinalistSpec:
    label: str
    mechanism: str
    score_mode: str
    weight_mode: str
    absolute_filter: bool
    lookback: LookbackProfile
    top_n: int
    rebalance_months: int
    rebalance_offset: int
    rationale: str


FINALISTS: tuple[FinalistSpec, ...] = (
    FinalistSpec(
        label="aggressive_raw_lb6_top5_q",
        mechanism="raw_equal",
        score_mode="raw_13612",
        weight_mode="equal",
        absolute_filter=False,
        lookback=LookbackProfile("lb6", (6,)),
        top_n=5,
        rebalance_months=3,
        rebalance_offset=0,
        rationale="Best after-tax Sharpe in heatmap.",
    ),
    FinalistSpec(
        label="aggressive_ivol_lb6_top5_q",
        mechanism="raw_inverse_vol",
        score_mode="raw_13612",
        weight_mode="inverse_vol",
        absolute_filter=False,
        lookback=LookbackProfile("lb6", (6,)),
        top_n=5,
        rebalance_months=3,
        rebalance_offset=0,
        rationale="Best raw inverse-vol high-return row.",
    ),
    FinalistSpec(
        label="balanced_voladj_lb6_top5_q",
        mechanism="voladj_equal",
        score_mode="vol_adjusted_13612",
        weight_mode="equal",
        absolute_filter=False,
        lookback=LookbackProfile("lb6", (6,)),
        top_n=5,
        rebalance_months=3,
        rebalance_offset=0,
        rationale="Best high-CAGR row with MDD above -50%.",
    ),
    FinalistSpec(
        label="balanced_voladj_lb6_top10_m",
        mechanism="voladj_equal",
        score_mode="vol_adjusted_13612",
        weight_mode="equal",
        absolute_filter=False,
        lookback=LookbackProfile("lb6", (6,)),
        top_n=10,
        rebalance_months=1,
        rebalance_offset=0,
        rationale="More diversified vol-adjusted monthly row.",
    ),
    FinalistSpec(
        label="defensive_composite_lb12_top15_y",
        mechanism="composite_equal",
        score_mode="composite_mom_lowvol",
        weight_mode="equal",
        absolute_filter=False,
        lookback=LookbackProfile("lb12", (12,)),
        top_n=15,
        rebalance_months=12,
        rebalance_offset=6,
        rationale="Defensive row with MDD near -34%.",
    ),
    FinalistSpec(
        label="defensive_composite_lb6_12_top20_y",
        mechanism="composite_equal",
        score_mode="composite_mom_lowvol",
        weight_mode="equal",
        absolute_filter=False,
        lookback=LookbackProfile("lb6_12", (6, 12)),
        top_n=20,
        rebalance_months=12,
        rebalance_offset=6,
        rationale="Diversified composite row with MDD below -40%.",
    ),
)


def evolved_name(spec: FinalistSpec, overlay: OverlayMode, offset_mode: OffsetMode, offset: int) -> str:
    return f"evo_{spec.label}_{offset_mode}_off{offset}_{overlay}"


def overlay_uses_stock_filter(overlay: OverlayMode) -> bool:
    return "stock_sma100" in overlay


def overlay_uses_monthly_market(overlay: OverlayMode) -> bool:
    return "market_sma200_monthly" in overlay


def overlay_uses_daily_market(overlay: OverlayMode) -> bool:
    return "market_sma200_daily" in overlay


def market_regime(benchmark_prices: pd.DataFrame, daily_index: pd.DatetimeIndex) -> tuple[pd.Series, pd.Series]:
    """SPY > SMA200 regime flags for daily and month-end overlays."""
    spy_col = "SPY" if "SPY" in benchmark_prices.columns else benchmark_prices.columns[0]
    spy = benchmark_prices[spy_col].astype(float).sort_index()
    sma = spy.rolling(200, min_periods=200).mean()
    daily = (spy > sma).reindex(daily_index, method="ffill").fillna(False).astype(bool)
    monthly = daily.resample("ME").last().astype(bool)
    return daily, monthly


def stock_trend_ok(prices: pd.DataFrame, window_days: int = 100) -> pd.DataFrame:
    """Per-stock price > SMA100 filter used as a buy eligibility screen."""
    daily = canonicalize_columns(prices).sort_index().astype(float)
    sma = daily.rolling(window_days, min_periods=window_days).mean()
    return (daily > sma).resample("ME").last().fillna(False).astype(bool)


def monthly_weights_with_overlay(
    bundle: ScoreBundle,
    config: ExtensiveConfig,
    overlay: OverlayMode,
    monthly_market_ok: pd.Series,
    monthly_stock_ok: pd.DataFrame,
    eligible_by_date: EligibleByDate | None = None,
) -> pd.DataFrame:
    """Build monthly weights with optional SPY/stock trend filters."""
    assets = [asset.upper() for asset in config.assets if asset.upper() in bundle.monthly_prices.columns]
    scores = bundle.scores[config.score_mode].reindex(columns=assets)
    monthly_vol = bundle.monthly_vol.reindex(columns=assets)
    weights = pd.DataFrame(0.0, index=scores.index, columns=assets)
    rebalance_dates: list[pd.Timestamp] = []

    for rebalance_date in scores.index:
        if (pd.Timestamp(rebalance_date).month - 1 - config.rebalance_offset) % config.rebalance_months != 0:
            continue
        rebalance_dates.append(pd.Timestamp(rebalance_date))
        if overlay_uses_monthly_market(overlay) and not bool(monthly_market_ok.reindex([rebalance_date]).fillna(False).iloc[0]):
            continue
        row = scores.loc[rebalance_date].copy()
        eligible = eligible_assets_for_date(eligible_by_date, pd.Timestamp(rebalance_date))
        if eligible is not None:
            if not eligible:
                continue
            row = row.where(row.index.to_series().astype(str).str.upper().isin(eligible), np.nan)
        if overlay_uses_stock_filter(overlay):
            ok = monthly_stock_ok.reindex(index=[rebalance_date], columns=assets).fillna(False).iloc[0]
            row = row.where(ok.astype(bool), np.nan)
        ranked = rank_scores(row)
        if config.absolute_filter:
            ranked = [asset for asset in ranked if float(row[asset]) > 0.0]
        chosen = ranked[: config.top_n]
        if not chosen:
            continue
        if config.weight_mode == "inverse_vol":
            vol = monthly_vol.loc[rebalance_date, chosen].astype(float).replace(0.0, np.nan)
            inv = (1.0 / vol).replace([np.inf, -np.inf], np.nan).dropna()
            if len(inv) == len(chosen) and float(inv.sum()) > 0.0:
                for asset, value in (inv / inv.sum()).items():
                    weights.loc[rebalance_date, str(asset)] = float(value)
                continue
        slot_weight = 1.0 / config.top_n
        for asset in chosen:
            weights.loc[rebalance_date, asset] = slot_weight
    if not rebalance_dates:
        return weights.iloc[0:0]
    return weights.loc[pd.DatetimeIndex(rebalance_dates)]


def simulate_evolved(
    prices: pd.DataFrame,
    bundle: ScoreBundle,
    config: ExtensiveConfig,
    overlay: OverlayMode,
    offset_mode: OffsetMode,
    daily_market_ok: pd.Series,
    monthly_market_ok: pd.Series,
    monthly_stock_ok: pd.DataFrame,
    eligible_by_date: EligibleByDate | None = None,
) -> SimulationResult:
    """Simulate one evolved finalist with fixed or staggered offsets."""
    daily = canonicalize_columns(prices).sort_index()
    offsets = range(config.rebalance_months) if offset_mode == "staggered" else (config.rebalance_offset,)
    sleeve_frames: list[pd.DataFrame] = []
    for offset in offsets:
        cfg = replace(config, rebalance_offset=offset)
        monthly_weights = monthly_weights_with_overlay(
            bundle,
            cfg,
            overlay,
            monthly_market_ok=monthly_market_ok,
            monthly_stock_ok=monthly_stock_ok,
            eligible_by_date=eligible_by_date,
        )
        sleeve = daily_weights_from_monthly(daily, monthly_weights)
        if overlay_uses_daily_market(overlay):
            sleeve = sleeve.where(daily_market_ok.reindex(sleeve.index).fillna(False), 0.0)
        sleeve_frames.append(sleeve)

    columns = sorted({column for frame in sleeve_frames for column in frame.columns})
    daily_weights = pd.DataFrame(0.0, index=daily.index, columns=columns)
    for frame in sleeve_frames:
        daily_weights = daily_weights.add(
            frame.reindex(index=daily.index, columns=columns, fill_value=0.0).fillna(0.0),
            fill_value=0.0,
        )
    daily_weights /= float(len(sleeve_frames))
    asset_returns = daily[daily_weights.columns].pct_change(fill_method=None).fillna(0.0)
    gross = (daily_weights.shift(1).fillna(0.0) * asset_returns).sum(axis=1)
    active = daily_weights.sum(axis=1) > 0.0
    if not active.any():
        empty = pd.Series(dtype=float, name=config.name)
        return SimulationResult(empty, pd.DataFrame(), pd.DataFrame(), turnover_diagnostics(pd.DataFrame(), pd.DatetimeIndex([])))
    first_signal = active[active].index[0]
    returns = gross[gross.index >= first_signal].rename(config.name)
    daily_weights = daily_weights.loc[returns.index]
    changed = daily_weights.diff().abs().sum(axis=1) > 1e-12
    if len(changed):
        changed.iloc[0] = daily_weights.iloc[0].sum() > 1e-12
    rebalance_weights = daily_weights.loc[changed]
    return SimulationResult(
        returns=returns,
        daily_weights=daily_weights,
        rebalance_weights=rebalance_weights,
        turnover=turnover_diagnostics(rebalance_weights, returns.index),
    )


def load_prices(args: argparse.Namespace) -> tuple[tuple[str, ...], pd.DataFrame, pd.DataFrame, EligibleByDate | None, list[str]]:
    if not args.allow_biased_yfinance:
        raise ValueError("stocks evolution requires --allow-biased-yfinance")
    tickers_list, eligible_by_date = us_stock_tickers_with_membership(
        TIINGO_ROOT,
        limit=args.max_us_stocks,
        universe=args.us_stock_universe,
        start=args.start,
        end=args.end,
    )
    tickers = tuple(tickers_list)
    prices = load_yfinance_price_frame(tickers, args.start, args.end)
    prices, dropped_extreme = drop_extreme_return_tickers(prices, args.max_abs_daily_return)
    tickers = tuple(ticker for ticker in tickers if ticker in prices.columns)
    if dropped_extreme:
        suffix = "..." if len(dropped_extreme) > 25 else ""
        print(
            f"dropped {len(dropped_extreme)} tickers with abs daily return > "
            f"{args.max_abs_daily_return}: {', '.join(dropped_extreme[:25])}{suffix}",
            flush=True,
        )
    benchmark = load_yfinance_price_frame(("SPY",), args.start, args.end, allow_missing=False)
    return tickers, prices, benchmark, eligible_by_date, dropped_extreme


def run_evolution(args: argparse.Namespace) -> tuple[pd.DataFrame, dict[str, pd.Series], pd.DataFrame]:
    tickers, prices, benchmark_prices, eligible_by_date, dropped_extreme = load_prices(args)
    daily = canonicalize_columns(prices).sort_index()
    daily_market_ok, monthly_market_ok = market_regime(benchmark_prices, pd.DatetimeIndex(daily.index))
    monthly_stock_ok = stock_trend_ok(daily)
    bundles = {
        spec.lookback.label: precompute_scores(
            prices,
            tickers,
            vol_window_days=args.vol_window_days,
            trend_window_days=args.trend_window_days,
            lookback_months=spec.lookback.months,
        )
        for spec in FINALISTS
    }

    planned = [(spec, overlay, offset_mode) for spec in FINALISTS for overlay in OVERLAYS for offset_mode in OFFSET_MODES]
    rows: list[dict[str, object]] = []
    returns_by_name: dict[str, pd.Series] = {}
    for i, (spec, overlay, offset_mode) in enumerate(planned, start=1):
        config = ExtensiveConfig(
            name=evolved_name(spec, overlay, offset_mode, spec.rebalance_offset),
            universe="us_stocks",
            assets=tickers,
            top_n=spec.top_n,
            rebalance_months=spec.rebalance_months,
            rebalance_offset=spec.rebalance_offset,
            score_mode=spec.score_mode,  # type: ignore[arg-type]
            weight_mode=spec.weight_mode,  # type: ignore[arg-type]
            absolute_filter=spec.absolute_filter,
            vol_window_days=args.vol_window_days,
            trend_window_days=args.trend_window_days,
        )
        simulation = simulate_evolved(
            prices,
            bundles[spec.lookback.label],
            config,
            overlay=overlay,
            offset_mode=offset_mode,
            daily_market_ok=daily_market_ok,
            monthly_market_ok=monthly_market_ok,
            monthly_stock_ok=monthly_stock_ok,
            eligible_by_date=eligible_by_date,
        )
        if simulation.returns.empty:
            continue
        tax = apply_br_foreign_annual_tax(simulation.returns, simulation.daily_weights)
        row = result_row(
            config,
            simulation,
            benchmark_prices,
            n_trials=len(planned),
            ranked_returns=tax.returns,
            tax_summary=tax.summary,
        )
        strategy_returns, bench_returns = benchmark_returns_for(tax.returns, benchmark_prices)
        row.update(regime_columns(strategy_returns, bench_returns))
        row.update(
            {
                "base_label": spec.label,
                "base_mechanism": spec.mechanism,
                "lookback_label": spec.lookback.label,
                "lookback_months": "/".join(str(month) for month in spec.lookback.months),
                "overlay": overlay,
                "offset_mode": offset_mode,
                "us_stock_universe": args.us_stock_universe,
                "dynamic_universe": eligible_by_date is not None,
                "max_abs_daily_return_filter": args.max_abs_daily_return,
                "dropped_extreme_tickers": len(dropped_extreme),
                "rationale": spec.rationale,
            }
        )
        rows.append(row)
        returns_by_name[config.name] = tax.returns
        print(f"simulated {i}/{len(planned)}: {config.name}", flush=True)
    return pd.DataFrame(rows), returns_by_name, benchmark_prices


def write_plots(results: pd.DataFrame, returns_by_name: dict[str, pd.Series], benchmark_prices: pd.DataFrame) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    FINALIST_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []

    fig, ax = plt.subplots(figsize=(10, 6))
    for overlay, sub in results.groupby("overlay"):
        ax.scatter(sub["after_tax_mdd"] * 100.0, sub["after_tax_cagr"] * 100.0, s=50, alpha=0.75, label=overlay)
    ax.set_title("Evolved finalists: after-tax CAGR vs MDD")
    ax.set_xlabel("MDD (%)")
    ax.set_ylabel("CAGR (%)")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7)
    fig.tight_layout()
    scatter = PLOTS_DIR / "evolution_cagr_vs_mdd.png"
    fig.savefig(scatter, dpi=140)
    plt.close(fig)
    paths.append(str(scatter.relative_to(STOCKS_DIR)))

    fig, ax = plt.subplots(figsize=(12, 5))
    top = results.nlargest(20, "after_tax_sharpe")
    labels = [f"{row.base_label}\n{row.overlay}\n{row.offset_mode}" for row in top.itertuples()]
    ax.bar(range(len(top)), top["after_tax_sharpe"], color="steelblue")
    ax.set_xticks(range(len(top)), labels, rotation=75, ha="right", fontsize=6)
    ax.set_title("Top evolved finalists by after-tax Sharpe")
    ax.set_ylabel("Sharpe")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    bars = PLOTS_DIR / "evolution_top_sharpe.png"
    fig.savefig(bars, dpi=140)
    plt.close(fig)
    paths.append(str(bars.relative_to(STOCKS_DIR)))

    plot_names = set(results.nlargest(6, "after_tax_sharpe")["name"]) | set(results.nlargest(6, "after_tax_mdd")["name"])
    for name in plot_names:
        path = plot_strategy_vs_spy(name, returns_by_name[name], benchmark_prices, FINALIST_PLOTS_DIR)
        if path:
            paths.append(str((STUDY_DIR / path).relative_to(STOCKS_DIR)))
    return paths


def format_row(row: pd.Series) -> dict[str, object]:
    return {
        "Name": row["name"],
        "Base": row["base_label"],
        "Overlay": row["overlay"],
        "Offsets": row["offset_mode"],
        "CAGR": fmt_pct(float(row["after_tax_cagr"])),
        "MDD": fmt_pct(float(row["after_tax_mdd"])),
        "Sharpe": fmt_num(float(row["after_tax_sharpe"])),
        "Calmar": fmt_num(float(row["after_tax_calmar"])),
        "RollRel": fmt_pct(float(row["rolling_rel_score"])),
        "RollP25": fmt_pct(float(row["rolling_rel_p25_score"])),
        "GFC MDD": fmt_pct(float(row["gfc_mdd"])),
        "Dotcom MDD": fmt_pct(float(row["dotcom_mdd"])),
        "Turnover": fmt_num(float(row["annual_turnover"])),
    }


def table(frame: pd.DataFrame) -> str:
    return md_table(
        [format_row(row) for _, row in frame.iterrows()],
        [
            "Name",
            "Base",
            "Overlay",
            "Offsets",
            "CAGR",
            "MDD",
            "Sharpe",
            "Calmar",
            "RollRel",
            "RollP25",
            "GFC MDD",
            "Dotcom MDD",
            "Turnover",
        ],
    )


def write_report(results: pd.DataFrame, pbo_rows: list[dict[str, object]], plot_paths: list[str], args: argparse.Namespace) -> None:
    best_sharpe = results.nlargest(1, "after_tax_sharpe").iloc[0]
    best_mdd = results.nlargest(1, "after_tax_mdd").iloc[0]
    best_gfc = results.nlargest(1, "gfc_mdd").iloc[0]
    best_relative = results.nlargest(1, "rolling_rel_score").iloc[0]
    pbo_all = next((row for row in pbo_rows if row["group"] == "all"), {})
    REPORT.write_text(
        "# US Stocks 13612 Finalist Evolution\n\n"
        "Status: research-only. No deployment, paper-trade label or mandate change.\n\n"
        "## Scope\n\n"
        f"- Start: `{args.start}`\n"
        f"- Base finalists: `{len(FINALISTS)}`\n"
        f"- Rows: `{len(results)}`\n"
        f"- Max abs daily return filter: `{args.max_abs_daily_return}`\n"
        "- Evolutions: fixed/staggered offsets, SPY SMA200 monthly/daily filters, stock SMA100 filter, and combinations.\n"
        + (
            "- Source: yfinance + Wikipedia selected-changes PIT-ish S&P 500; "
            "`promotion_eligible=false` until true PIT/delisted prices validate the result "
            "`[advances_fin_ml, p.208-211]`.\n"
            if args.us_stock_universe == "sp500_wikipedia_pit"
            else "- Source: yfinance/current S&P 500 universe; `promotion_eligible=false` "
            "until PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.\n"
        )
        + f"- PBO all: `{float(pbo_all.get('pbo', float('nan'))):.3f}`.\n\n"
        "## Key Readings\n\n"
        f"- Best Sharpe: `{best_sharpe['name']}` with CAGR `{fmt_pct(float(best_sharpe['after_tax_cagr']))}`, "
        f"MDD `{fmt_pct(float(best_sharpe['after_tax_mdd']))}`, Sharpe `{fmt_num(float(best_sharpe['after_tax_sharpe']))}`.\n"
        f"- Best full-period MDD: `{best_mdd['name']}` with CAGR `{fmt_pct(float(best_mdd['after_tax_cagr']))}`, "
        f"MDD `{fmt_pct(float(best_mdd['after_tax_mdd']))}`, Sharpe `{fmt_num(float(best_mdd['after_tax_sharpe']))}`.\n"
        f"- Best GFC MDD: `{best_gfc['name']}` with CAGR `{fmt_pct(float(best_gfc['after_tax_cagr']))}`, "
        f"GFC MDD `{fmt_pct(float(best_gfc['gfc_mdd']))}`, full MDD `{fmt_pct(float(best_gfc['after_tax_mdd']))}`.\n\n"
        f"- Best rolling relative score: `{best_relative['name']}` with score "
        f"`{fmt_pct(float(best_relative['rolling_rel_score']))}`, p25 "
        f"`{fmt_pct(float(best_relative['rolling_rel_p25_score']))}`.\n\n"
        "## Plots\n\n"
        + "\n".join(f"- [{Path(path).name}]({path})" for path in plot_paths)
        + "\n\n## Top 20 By After-Tax Sharpe\n\n"
        + table(results.nlargest(20, "after_tax_sharpe"))
        + "\n## Top 20 By Full-Period MDD\n\n"
        + table(results.nlargest(20, "after_tax_mdd"))
        + "\n## Top 20 By GFC MDD\n\n"
        + table(results.nlargest(20, "gfc_mdd"))
        + "\n## Top 20 By Rolling Relative Score\n\n"
        + table(results.nlargest(20, "rolling_rel_score"))
        + "\n## PBO Summary\n\n"
        + md_table(pbo_rows, ["group", "pbo", "n_configs", "n_obs", "n_combinations", "pass"])
        + "\n## Caveats\n\n"
        "- These are post-heatmap evolutions of selected finalists; the effective trial count is larger than this file alone.\n"
        "- The SPY SMA200 and stock SMA100 filters are literature-grounded diagnostics, but still tested here after seeing the heatmap.\n"
        + (
            "- `sp500_wikipedia_pit` reduces current-constituent leakage, but Wikipedia "
            "changes are incomplete and yfinance still does not provide delisting returns "
            "`[advances_fin_ml, p.208-211]`.\n"
            if args.us_stock_universe == "sp500_wikipedia_pit"
            else "- yfinance/current constituents inflate historical stock screens via survivorship bias `[advances_fin_ml, p.208-211]`.\n"
        ),
        encoding="utf-8",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evolve US-stocks 13612 finalists")
    parser.add_argument("--allow-biased-yfinance", action="store_true")
    parser.add_argument("--max-us-stocks", type=int, default=9999)
    parser.add_argument(
        "--us-stock-universe",
        choices=["sp500", "tiingo_manifest", "sp500_wikipedia_pit"],
        default="sp500",
    )
    parser.add_argument("--start", default="1990-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--vol-window-days", type=int, default=126)
    parser.add_argument("--trend-window-days", type=int, default=126)
    parser.add_argument(
        "--max-abs-daily-return",
        type=float,
        default=None,
        help="drop tickers whose adjusted-close daily return exceeds this absolute value; data-quality diagnostic only",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    results, returns_by_name, benchmark_prices = run_evolution(args)
    results_path = RESULTS_DIR / "evolution_results.csv"
    results.to_csv(results_path, index=False)
    (RESULTS_DIR / "evolution_results.json").write_text(
        json.dumps(json_safe(results.to_dict(orient="records")), indent=2, allow_nan=False),
        encoding="utf-8",
    )
    pbo_data = pbo_summary(returns_by_name, results)
    (RESULTS_DIR / "evolution_pbo.json").write_text(
        json.dumps(json_safe(pbo_data), indent=2, allow_nan=False), encoding="utf-8"
    )
    plot_paths = write_plots(results, returns_by_name, benchmark_prices)
    write_report(results, pbo_data["rows"], plot_paths, args)
    print(f"wrote {REPORT.relative_to(REPO_ROOT)}")
    print(f"wrote {results_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
