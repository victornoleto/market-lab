#!/usr/bin/env python3
"""Run the extensive US-only 13612 mechanism/frequency grid.

This is a deliberately broad research batch, not a selection procedure. It
compares every tested configuration with SPY adjusted close as the S&P 500 proxy
and reports the full surface because wide grids are highly exposed to overfit
and timing luck `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from market_lab.backtest.validation.pbo import pbo  # noqa: E402
from studies.momentum_13612_universes.extensive import (  # noqa: E402
    ExtensiveConfig,
    apply_br_foreign_annual_tax,
    benchmark_returns_for,
    make_config_name,
    precompute_scores,
    result_row,
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
    load_tiingo_price_frame,
    load_yfinance_price_frame,
    us_etf_tickers,
    us_stock_tickers,
)


STUDY_DIR = Path(__file__).resolve().parent
RESULTS_DIR = STUDY_DIR / "results"
PLOTS_DIR = STUDY_DIR / "plots" / "extensive"
FINALIST_PLOTS_DIR = PLOTS_DIR / "finalists"
REPORT = STUDY_DIR / "REPORT_EXTENSIVE.md"
TIINGO_ROOT = REPO_ROOT / "data" / "tiingo"

DEFAULT_TOP_N = (1, 3, 5, 10, 15, 20)
DEFAULT_REBALANCE_MONTHS = (1, 3, 6, 12)
DEFAULT_UNIVERSES = ("us_stocks", "us_etfs", "us_mixed")
MECHANISMS: tuple[tuple[str, str, str, bool], ...] = (
    ("raw_equal", "raw_13612", "equal", False),
    ("voladj_equal", "vol_adjusted_13612", "equal", False),
    ("clenow_equal", "clenow_trend", "equal", False),
    ("composite_equal", "composite_mom_lowvol", "equal", False),
    ("raw_inverse_vol", "raw_13612", "inverse_vol", False),
    ("raw_abs_cash", "raw_13612", "equal", True),
)


def parse_int_tuple(raw: str) -> tuple[int, ...]:
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not values or any(value <= 0 for value in values):
        raise ValueError(f"invalid positive integer list: {raw!r}")
    return values


def parse_universe_tuple(raw: str) -> tuple[str, ...]:
    values = tuple(part.strip() for part in raw.split(",") if part.strip())
    allowed = set(DEFAULT_UNIVERSES)
    if not values or any(value not in allowed for value in values):
        raise ValueError(f"universes must be a comma-separated subset of {sorted(allowed)}")
    return values


def universe_tickers(universe: str, args: argparse.Namespace) -> tuple[str, ...]:
    stocks = us_stock_tickers(TIINGO_ROOT, limit=args.max_us_stocks, universe=args.us_stock_universe)
    etfs = us_etf_tickers(TIINGO_ROOT, limit=args.max_us_etfs, universe=args.us_etf_universe)
    if universe == "us_stocks":
        return tuple(stocks)
    if universe == "us_etfs":
        return tuple(etfs)
    if universe == "us_mixed":
        return tuple(sorted(set(stocks) | set(etfs)))
    raise ValueError(f"unknown universe {universe!r}")


def load_us_price_frame(tickers: tuple[str, ...], args: argparse.Namespace) -> tuple[pd.DataFrame, str]:
    if args.us_source == "tiingo":
        return load_tiingo_price_frame(tickers, TIINGO_ROOT, args.start, args.end), "tiingo"
    if not args.allow_biased_yfinance:
        raise ValueError("yfinance source requires --allow-biased-yfinance")
    return load_yfinance_price_frame(tickers, args.start, args.end), "yfinance"


def build_configs(args: argparse.Namespace, universes: tuple[str, ...]) -> list[ExtensiveConfig]:
    configs: list[ExtensiveConfig] = []
    top_values = parse_int_tuple(args.top_n)
    freq_values = parse_int_tuple(args.rebalance_months)
    for universe in universes:
        tickers = universe_tickers(universe, args)
        for mechanism, score_mode, weight_mode, absolute_filter in MECHANISMS:
            for top_n in top_values:
                for freq in freq_values:
                    for offset in range(freq):
                        configs.append(
                            ExtensiveConfig(
                                name=make_config_name(universe, mechanism, top_n, freq, offset),
                                universe=universe,
                                assets=tickers,
                                top_n=top_n,
                                rebalance_months=freq,
                                rebalance_offset=offset,
                                score_mode=score_mode,  # type: ignore[arg-type]
                                weight_mode=weight_mode,  # type: ignore[arg-type]
                                absolute_filter=absolute_filter,
                                vol_window_days=args.vol_window_days,
                                trend_window_days=args.trend_window_days,
                            )
                        )
    return configs


def pbo_summary(returns_by_name: dict[str, pd.Series], groups: pd.DataFrame) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    rows.append(pbo_one("all", returns_by_name))
    for universe in sorted(groups["universe"].unique()):
        names = set(groups.loc[groups["universe"] == universe, "name"])
        rows.append(pbo_one(f"universe:{universe}", filter_returns(returns_by_name, names)))
    for mechanism in sorted(groups["mechanism"].unique()):
        names = set(groups.loc[groups["mechanism"] == mechanism, "name"])
        rows.append(pbo_one(f"mechanism:{mechanism}", filter_returns(returns_by_name, names)))
    for (universe, mechanism), sub in groups.groupby(["universe", "mechanism"]):
        rows.append(
            pbo_one(
                f"{universe}:{mechanism}",
                filter_returns(returns_by_name, set(sub["name"])),
            )
        )
    return {"rows": rows}


def filter_returns(returns_by_name: dict[str, pd.Series], names: set[str]) -> dict[str, pd.Series]:
    return {name: series for name, series in returns_by_name.items() if name in names}


def pbo_one(label: str, returns_by_name: dict[str, pd.Series]) -> dict[str, object]:
    if len(returns_by_name) < 2:
        return {"group": label, "pbo": float("nan"), "n_configs": len(returns_by_name), "pass": True}
    aligned = pd.concat(returns_by_name, axis=1, sort=False).dropna()
    if aligned.shape[1] < 2 or len(aligned) < 252:
        return {
            "group": label,
            "pbo": float("nan"),
            "n_configs": len(returns_by_name),
            "n_obs": len(aligned),
            "pass": False,
            "note": "insufficient aligned data",
        }
    result = pbo(aligned.to_numpy(dtype=float), n_blocks=10)
    return {
        "group": label,
        "pbo": float(result.pbo),
        "n_configs": len(returns_by_name),
        "n_obs": len(aligned),
        "n_combinations": int(result.n_combinations),
        "pass": bool(result.pbo < 0.5),
    }


def select_finalists(results: pd.DataFrame, max_finalists: int = 30) -> pd.DataFrame:
    """Select diagnostic finalists for individual plots."""
    selected: list[pd.DataFrame] = []
    for _, sub in results.groupby("universe"):
        selected.append(sub.nlargest(4, "after_tax_sharpe"))
        selected.append(sub.nlargest(4, "after_tax_calmar"))
        selected.append(sub.nlargest(4, "excess_cagr"))
        selected.append(sub.nlargest(3, "min_relative_equity"))
        selected.append(sub.nlargest(3, "rolling_rel_score"))
    selected.append(results.nlargest(8, "terminal_relative"))
    out = pd.concat(selected).drop_duplicates("name")
    out = out.sort_values(["after_tax_sharpe", "excess_cagr"], ascending=False)
    return out.head(max_finalists).copy()


def plot_strategy_vs_spy(
    name: str,
    returns: pd.Series,
    benchmark_prices: pd.DataFrame,
    out_dir: Path,
) -> str | None:
    strategy_returns, bench_returns = benchmark_returns_for(returns, benchmark_prices, "SPY")
    if strategy_returns.empty or bench_returns.empty:
        return None
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    strategy_eq = (1.0 + strategy_returns).cumprod()
    spy_eq = (1.0 + bench_returns).cumprod()
    aligned = pd.concat({"Strategy": strategy_eq, "SPY": spy_eq}, axis=1).dropna()
    dd = aligned / aligned.cummax() - 1.0
    ratio = aligned["Strategy"] / aligned["SPY"]

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    aligned.plot(ax=axes[0], linewidth=1.2)
    axes[0].set_title(f"{name}: after-tax equity vs SPY")
    axes[0].set_ylabel("Growth of $1")
    axes[0].grid(True, alpha=0.3)
    dd.plot(ax=axes[1], linewidth=1.1)
    axes[1].set_title("Drawdown")
    axes[1].set_ylabel("Drawdown")
    axes[1].grid(True, alpha=0.3)
    ratio.plot(ax=axes[2], color="black", linewidth=1.1)
    axes[2].axhline(1.0, color="gray", linestyle="--", linewidth=1.0)
    axes[2].set_title("Strategy / SPY relative equity")
    axes[2].set_ylabel("Ratio")
    axes[2].grid(True, alpha=0.3)
    fig.tight_layout()
    path = out_dir / f"{safe_filename(name)}_vs_SPY.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return str(path.relative_to(STUDY_DIR))


def write_aggregate_plots(results: pd.DataFrame) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    colors = dict(zip(sorted(results["mechanism"].unique()), plt.cm.tab10.colors, strict=False))

    universes = sorted(results["universe"].unique())
    fig, axes = plt.subplots(1, len(universes), figsize=(max(7, 5.7 * len(universes)), 5), sharey=True)
    if len(universes) == 1:
        axes = [axes]
    for ax, universe in zip(axes, universes, strict=False):
        sub = results[results["universe"] == universe]
        for mechanism, mech_sub in sub.groupby("mechanism"):
            ax.scatter(
                mech_sub["mdd"] * 100.0,
                mech_sub["cagr"] * 100.0,
                s=16 + mech_sub["top_n"].to_numpy(dtype=float),
                alpha=0.55,
                label=mechanism,
                color=colors.get(mechanism),
            )
        ax.set_title(universe)
        ax.set_xlabel("MDD (%)")
        ax.grid(True, alpha=0.25)
    axes[0].set_ylabel("CAGR (%)")
    axes[-1].legend(fontsize=7, loc="best")
    fig.suptitle("All configs: after-tax CAGR vs MDD (size = top-N)")
    fig.tight_layout()
    paths.append(save_fig(fig, "all_configs_cagr_vs_mdd.png"))

    fig, ax = plt.subplots(figsize=(12, 5))
    labels = [str(value) for value in sorted(results["rebalance_months"].unique())]
    values = [
        results.loc[results["rebalance_months"] == int(label), "excess_cagr"].dropna() * 100.0
        for label in labels
    ]
    ax.boxplot(values, tick_labels=labels, showfliers=False)
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=1.0)
    ax.set_title("Timing/frequency surface: after-tax excess CAGR vs SPY")
    ax.set_xlabel("Rebalance frequency (months)")
    ax.set_ylabel("Excess CAGR (pp)")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    paths.append(save_fig(fig, "boxplot_excess_cagr_by_frequency.png"))

    paths.append(plot_heatmap(results, "sharpe", "max", "best_sharpe_by_mechanism_freq.png"))
    paths.append(plot_heatmap(results, "vol", "median", "median_vol_by_mechanism_freq.png"))
    paths.append(plot_topn_frequency_heatmap(results))
    return paths


def plot_heatmap(results: pd.DataFrame, value: str, agg: str, filename: str) -> str:
    import matplotlib.pyplot as plt

    universes = sorted(results["universe"].unique())
    fig, axes = plt.subplots(1, len(universes), figsize=(17, 5), sharey=True)
    if len(universes) == 1:
        axes = [axes]
    for ax, universe in zip(axes, universes, strict=False):
        sub = results[results["universe"] == universe]
        pivot = sub.pivot_table(
            index="mechanism", columns="rebalance_months", values=value, aggfunc=agg
        ).sort_index()
        data = pivot.to_numpy(dtype=float)
        im = ax.imshow(data, aspect="auto", cmap="viridis")
        ax.set_title(f"{universe}: {agg} {value}")
        ax.set_xticks(range(len(pivot.columns)), [str(col) for col in pivot.columns])
        ax.set_yticks(range(len(pivot.index)), list(pivot.index), fontsize=7)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                if math.isfinite(float(data[i, j])):
                    ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center", fontsize=7)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    return save_fig(fig, filename)


def plot_topn_frequency_heatmap(results: pd.DataFrame) -> str:
    import matplotlib.pyplot as plt

    universes = sorted(results["universe"].unique())
    fig, axes = plt.subplots(1, len(universes), figsize=(17, 5), sharey=True)
    if len(universes) == 1:
        axes = [axes]
    for ax, universe in zip(axes, universes, strict=False):
        sub = results[results["universe"] == universe]
        pivot = sub.pivot_table(
            index="top_n", columns="rebalance_months", values="mdd", aggfunc="median"
        ).sort_index()
        data = pivot.to_numpy(dtype=float) * 100.0
        im = ax.imshow(data, aspect="auto", cmap="magma_r")
        ax.set_title(f"{universe}: median MDD by top-N/frequency")
        ax.set_xticks(range(len(pivot.columns)), [str(col) for col in pivot.columns])
        ax.set_yticks(range(len(pivot.index)), [str(idx) for idx in pivot.index])
        ax.set_xlabel("Rebalance months")
        ax.set_ylabel("Top-N")
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                if math.isfinite(float(data[i, j])):
                    ax.text(j, i, f"{data[i, j]:.0f}%", ha="center", va="center", fontsize=7)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    return save_fig(fig, "median_mdd_by_topn_frequency.png")


def save_fig(fig, filename: str) -> str:
    path = PLOTS_DIR / filename
    fig.savefig(path, dpi=140)
    import matplotlib.pyplot as plt

    plt.close(fig)
    return str(path.relative_to(STUDY_DIR))


def write_report(
    results: pd.DataFrame,
    finalists: pd.DataFrame,
    pbo_rows: list[dict[str, object]],
    aggregate_plots: list[str],
    args: argparse.Namespace,
    universes: tuple[str, ...],
) -> None:
    top_sharpe = results.nlargest(20, "after_tax_sharpe")
    top_excess = results.nlargest(20, "excess_cagr")
    mechanism_summary = summarize_group(results, ["mechanism"])
    freq_summary = summarize_group(results, ["rebalance_months"])
    topn_summary = summarize_group(results, ["top_n"])
    findings = key_findings(results, pbo_rows)
    pbo_table = [
        row for row in pbo_rows if row["group"] == "all" or str(row["group"]).startswith("universe:")
    ]
    overall = next((row for row in pbo_rows if row["group"] == "all"), {})
    verdict = (
        "Screen-only FAIL: yfinance/current-universe data are non-promotable, and "
        f"overall PBO is {float(overall.get('pbo', float('nan'))):.3f}."
    )

    REPORT.write_text(
        "# Extensive Momentum 13612 US Grid Report\n\n"
        "Status: research-only. No deployment, paper-trade label or mandate change.\n\n"
        "## Verdict\n\n"
        f"{verdict}\n\n"
        "## Grid\n\n"
        f"- Universes: `{', '.join(universes)}`\n"
        f"- Top-N: `{args.top_n}`\n"
        f"- Rebalance frequencies: `{args.rebalance_months}` months, all offsets\n"
        f"- Mechanisms: `{', '.join(name for name, *_ in MECHANISMS)}`\n"
        f"- Rows: `{len(results)}`\n"
        "- Ranking metric: after-tax strategy returns under Brazil's annual 15% realized-gain rule\n"
        "- Benchmark: SPY adjusted close as S&P 500 proxy\n\n"
        "## Key Findings\n\n"
        + findings
        + "\n## Aggregate Plots\n\n"
        + "\n".join(f"- [{Path(path).name}]({path})" for path in aggregate_plots)
        + "\n\n## Top 20 By After-Tax Sharpe\n\n"
        + result_table(top_sharpe)
        + "\n## Top 20 By After-Tax Excess CAGR\n\n"
        + result_table(top_excess)
        + "\n## Finalists With Individual Plots\n\n"
        + finalist_table(finalists)
        + "\n## PBO Summary\n\n"
        + md_table(pbo_table, ["group", "pbo", "n_configs", "n_obs", "n_combinations", "pass"])
        + "\n## Mechanism Summary\n\n"
        + summary_table(mechanism_summary)
        + "\n## Rebalance Frequency Summary\n\n"
        + summary_table(freq_summary)
        + "\n## Top-N Summary\n\n"
        + summary_table(topn_summary)
        + "\n## Caveats\n\n"
        "- All rows are yfinance/current-universe screens and `promotion_eligible=false` "
        "until PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.\n"
        "- The grid is intentionally broad; PBO/DSR are diagnostics against data-mining "
        "and not optional `[advances_fin_ml, p.273-275]`.\n"
        "- Main rankings are after-tax for realized capital gains, but still gross of "
        "transaction costs/slippage.\n"
        "- Tax model nets realized gains/losses annually at 15% and does not force a "
        "final liquidation of unrealized positions.\n"
        "- Individual finalist plots are diagnostic picks, not winners.\n",
        encoding="utf-8",
    )


def result_table(frame: pd.DataFrame) -> str:
    rows = []
    for _, row in frame.iterrows():
        rows.append(format_result_row(row))
    return md_table(
        rows,
        [
            "Name",
            "Universe",
            "Mechanism",
            "Top-N",
            "Reb",
            "Off",
            "CAGR",
            "Gross CAGR",
            "Tax Drag",
            "SPY CAGR",
            "Excess",
            "MDD",
            "Vol",
            "Sharpe",
            "Calmar",
            "Turnover/yr",
            "Above SPY",
            "Rolling Rel",
        ],
    )


def key_findings(results: pd.DataFrame, pbo_rows: list[dict[str, object]]) -> str:
    topn = results.groupby("top_n").agg(median_vol=("vol", "median"), median_mdd=("mdd", "median"))
    top1 = topn.loc[topn.index.min()]
    topmax = topn.loc[topn.index.max()]
    freq = results.groupby("rebalance_months").agg(
        median_sharpe=("after_tax_sharpe", "median"),
        median_turnover=("annual_turnover", "median"),
    )
    best_freq = int(freq["median_sharpe"].idxmax())
    low_turnover_freq = int(freq["median_turnover"].idxmin())
    best = results.nlargest(1, "after_tax_sharpe").iloc[0]
    best_relative = results.nlargest(1, "rolling_rel_score").iloc[0]
    best_by_universe = results.loc[results.groupby("universe")["after_tax_sharpe"].idxmax()]
    mechanism = results.groupby("mechanism").agg(
        median_cagr=("after_tax_cagr", "median"),
        median_mdd=("after_tax_mdd", "median"),
        median_vol=("after_tax_vol", "median"),
        median_tax_drag=("tax_drag_cagr", "median"),
    )
    pbo_lookup = {str(row["group"]): row for row in pbo_rows}
    all_pbo = float(pbo_lookup.get("all", {}).get("pbo", float("nan")))
    universe_pbo = ", ".join(
        f"{group.removeprefix('universe:')} `{float(row.get('pbo', float('nan'))):.3f}`"
        for group, row in sorted(pbo_lookup.items())
        if group.startswith("universe:")
    )
    raw = mechanism.loc["raw_13612"]
    voladj = mechanism.loc["vol_adjusted_13612"]
    composite = mechanism.loc["composite_mom_lowvol"]
    universe_lines = "".join(
        f"- Melhor `{row['universe']}` por Sharpe after-tax: `{row['name']}`, CAGR "
        f"`{fmt_pct(float(row['after_tax_cagr']))}`, MDD "
        f"`{fmt_pct(float(row['after_tax_mdd']))}`, Sharpe "
        f"`{fmt_num(float(row['after_tax_sharpe']))}`.\n"
        for _, row in best_by_universe.sort_values("universe").iterrows()
    )
    return (
        f"- Top-N funcionou para risco: mediana de vol caiu de "
        f"`{fmt_pct(float(top1['median_vol']))}` em top{int(topn.index.min())} para "
        f"`{fmt_pct(float(topmax['median_vol']))}` em top{int(topn.index.max())}; "
        f"MDD mediano caiu de `{fmt_pct(float(top1['median_mdd']))}` para "
        f"`{fmt_pct(float(topmax['median_mdd']))}`.\n"
        f"- Melhor Sharpe after-tax: `{best['name']}`, CAGR `{fmt_pct(float(best['after_tax_cagr']))}`, "
        f"MDD `{fmt_pct(float(best['after_tax_mdd']))}`, Sharpe "
        f"`{fmt_num(float(best['after_tax_sharpe']))}`.\n"
        f"- Melhor rolling relative score vs SPY: `{best_relative['name']}`, score "
        f"`{fmt_pct(float(best_relative['rolling_rel_score']))}`, p25 "
        f"`{fmt_pct(float(best_relative['rolling_rel_p25_score']))}`.\n"
        f"{universe_lines}"
        f"- Score shaping reduziu risco: raw mediano MDD `{fmt_pct(float(raw['median_mdd']))}`/vol "
        f"`{fmt_pct(float(raw['median_vol']))}`; vol-adjusted `{fmt_pct(float(voladj['median_mdd']))}`/"
        f"`{fmt_pct(float(voladj['median_vol']))}`; composite `{fmt_pct(float(composite['median_mdd']))}`/"
        f"`{fmt_pct(float(composite['median_vol']))}`.\n"
        f"- Frequência com maior Sharpe mediano: `{best_freq}m`; menor turnover mediano: "
        f"`{low_turnover_freq}m`.\n"
        f"- PBO: all `{all_pbo:.3f}`"
        f"{', ' + universe_pbo if universe_pbo else ''} sobre retornos after-tax. "
        f"Tudo segue screen-only yfinance/current-universe "
        f"`[advances_fin_ml, p.208-211]`.\n"
    )


def finalist_table(frame: pd.DataFrame) -> str:
    rows = []
    for _, row in frame.iterrows():
        item = format_result_row(row)
        item["Plot"] = f"[{Path(str(row.get('plot_path', ''))).name}]({row.get('plot_path', '')})"
        rows.append(item)
    return md_table(
        rows,
        [
            "Name",
            "Universe",
            "Mechanism",
            "Top-N",
            "Reb",
            "Off",
            "CAGR",
            "Excess",
            "MDD",
            "Sharpe",
            "Turnover/yr",
            "Above SPY",
            "Rolling Rel",
            "Plot",
        ],
    )


def format_result_row(row: pd.Series) -> dict[str, object]:
    return {
        "Name": row["name"],
        "Universe": row["universe"],
        "Mechanism": row["mechanism"],
        "Top-N": int(row["top_n"]),
        "Reb": int(row["rebalance_months"]),
        "Off": int(row["rebalance_offset"]),
        "CAGR": fmt_pct(float(row["cagr"])),
        "Gross CAGR": fmt_pct(float(row["gross_cagr"])),
        "Tax Drag": fmt_pct(float(row["tax_drag_cagr"])),
        "SPY CAGR": fmt_pct(float(row["spy_cagr"])),
        "Excess": fmt_pct(float(row["excess_cagr"])),
        "MDD": fmt_pct(float(row["mdd"])),
        "Vol": fmt_pct(float(row["vol"])),
        "Sharpe": fmt_num(float(row["after_tax_sharpe"])),
        "Calmar": fmt_num(float(row["after_tax_calmar"])),
        "Turnover/yr": fmt_num(float(row["annual_turnover"])),
        "Above SPY": fmt_pct(float(row["pct_time_above_spy"])),
        "Rolling Rel": fmt_pct(float(row["rolling_rel_score"])),
    }


def summarize_group(results: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    grouped = results.groupby(by).agg(
        n=("name", "count"),
        max_cagr=("after_tax_cagr", "max"),
        median_cagr=("after_tax_cagr", "median"),
        median_mdd=("after_tax_mdd", "median"),
        median_vol=("after_tax_vol", "median"),
        max_sharpe=("after_tax_sharpe", "max"),
        median_tax_drag=("tax_drag_cagr", "median"),
        median_turnover=("annual_turnover", "median"),
    )
    return grouped.reset_index()


def summary_table(frame: pd.DataFrame) -> str:
    rows = []
    for _, row in frame.iterrows():
        label_cols = [col for col in frame.columns if col not in {
            "n", "max_cagr", "median_cagr", "median_mdd", "median_vol", "max_sharpe",
            "median_tax_drag", "median_turnover",
        }]
        rows.append(
            {
                "Group": "/".join(str(row[col]) for col in label_cols),
                "N": int(row["n"]),
                "Max CAGR": fmt_pct(float(row["max_cagr"])),
                "Median CAGR": fmt_pct(float(row["median_cagr"])),
                "Median MDD": fmt_pct(float(row["median_mdd"])),
                "Median Vol": fmt_pct(float(row["median_vol"])),
                "Max Sharpe": fmt_num(float(row["max_sharpe"])),
                "Median Tax Drag": fmt_pct(float(row["median_tax_drag"])),
                "Median Turnover": fmt_num(float(row["median_turnover"])),
            }
        )
    return md_table(
        rows,
        [
            "Group",
            "N",
            "Max CAGR",
            "Median CAGR",
            "Median MDD",
            "Median Vol",
            "Max Sharpe",
            "Median Tax Drag",
            "Median Turnover",
        ],
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run extensive US-only 13612 grid")
    parser.add_argument("--us-source", choices=["yfinance", "tiingo"], default="yfinance")
    parser.add_argument("--allow-biased-yfinance", action="store_true")
    parser.add_argument(
        "--universes",
        default=",".join(DEFAULT_UNIVERSES),
        help="Comma-separated subset: us_stocks,us_etfs,us_mixed",
    )
    parser.add_argument("--us-stock-universe", choices=["sp500", "tiingo_manifest"], default="sp500")
    parser.add_argument("--us-etf-universe", choices=["curated", "tiingo_manifest"], default="curated")
    parser.add_argument("--max-us-stocks", type=int, default=120)
    parser.add_argument("--max-us-etfs", type=int, default=60)
    parser.add_argument("--top-n", default=",".join(str(value) for value in DEFAULT_TOP_N))
    parser.add_argument(
        "--rebalance-months",
        default=",".join(str(value) for value in DEFAULT_REBALANCE_MONTHS),
    )
    parser.add_argument("--start", default="2010-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--vol-window-days", type=int, default=126)
    parser.add_argument("--trend-window-days", type=int, default=126)
    parser.add_argument("--max-finalists", type=int, default=30)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    universes = parse_universe_tuple(args.universes)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    FINALIST_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    configs = build_configs(args, universes)
    n_trials = len(configs)
    benchmark_prices = load_yfinance_price_frame(("SPY",), args.start, args.end, allow_missing=False)
    rows: list[dict[str, object]] = []
    returns_by_name: dict[str, pd.Series] = {}
    price_cache: dict[str, pd.DataFrame] = {}
    bundle_cache = {}

    for universe in universes:
        tickers = universe_tickers(universe, args)
        prices, _source = load_us_price_frame(tickers, args)
        price_cache[universe] = prices
        bundle_cache[universe] = precompute_scores(
            prices,
            tickers,
            vol_window_days=args.vol_window_days,
            trend_window_days=args.trend_window_days,
        )

    for i, config in enumerate(configs, start=1):
        prices = price_cache[config.universe]
        bundle = bundle_cache[config.universe]
        simulation = simulate_extensive_config(prices, bundle, config)
        if simulation.returns.empty:
            continue
        tax = apply_br_foreign_annual_tax(simulation.returns, simulation.daily_weights)
        rows.append(
            result_row(
                config,
                simulation,
                benchmark_prices,
                n_trials=n_trials,
                ranked_returns=tax.returns,
                tax_summary=tax.summary,
            )
        )
        returns_by_name[config.name] = tax.returns
        if i % 250 == 0:
            print(f"simulated {i}/{n_trials}", flush=True)

    results = pd.DataFrame(rows)
    results_path = RESULTS_DIR / "extensive_results.csv"
    results.to_csv(results_path, index=False)
    (RESULTS_DIR / "extensive_results.json").write_text(
        json.dumps(json_safe(results.to_dict(orient="records")), indent=2, allow_nan=False),
        encoding="utf-8",
    )

    pbo_data = pbo_summary(returns_by_name, results)
    (RESULTS_DIR / "extensive_pbo.json").write_text(
        json.dumps(json_safe(pbo_data), indent=2, allow_nan=False), encoding="utf-8"
    )
    aggregate_plots = write_aggregate_plots(results)
    finalists = select_finalists(results, max_finalists=args.max_finalists)
    plot_paths: dict[str, str] = {}
    for name in finalists["name"]:
        path = plot_strategy_vs_spy(name, returns_by_name[name], benchmark_prices, FINALIST_PLOTS_DIR)
        if path:
            plot_paths[name] = path
    finalists = finalists.copy()
    finalists["plot_path"] = finalists["name"].map(plot_paths)
    finalists.to_csv(RESULTS_DIR / "extensive_finalists.csv", index=False)

    write_report(results, finalists, pbo_data["rows"], aggregate_plots, args, universes)
    print(f"wrote {REPORT.relative_to(REPO_ROOT)}")
    print(f"wrote {results_path.relative_to(REPO_ROOT)}")
    print(f"wrote {(RESULTS_DIR / 'extensive_finalists.csv').relative_to(REPO_ROOT)}")
    print(f"wrote {len(aggregate_plots)} aggregate plots and {len(plot_paths)} finalist plots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
