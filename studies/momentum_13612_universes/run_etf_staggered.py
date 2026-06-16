#!/usr/bin/env python3
"""Run the ETF-only staggered-offset 13612 hypothesis.

This is a narrower follow-up to the broad US grid: ETF universe only, raw 13612
ranking, optional inverse-volatility sizing, and rebalance frequencies whose
offsets are combined as equal-capital sleeves instead of selected ex-post. The
choices keep the cross-sectional momentum source `[stocks_on_the_move, p.60]`,
monthly rebalance convention `[stocks_on_the_move, p.98-99]`, and inverse-vol
sizing diagnostic `[systematic_trading, p.137-148]`, while reducing timing-luck
selection in a parameter grid `[advances_fin_ml, p.273-275]`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from studies.momentum_13612_universes.extensive import (  # noqa: E402
    ExtensiveConfig,
    apply_br_foreign_annual_tax,
    precompute_scores,
    result_row,
    simulate_staggered_offsets,
)
from studies.momentum_13612_universes.run import (  # noqa: E402
    fmt_num,
    fmt_pct,
    json_safe,
    md_table,
)
from studies.momentum_13612_universes.run_extensive import (  # noqa: E402
    load_us_price_frame,
    parse_int_tuple,
    pbo_summary,
    plot_strategy_vs_spy,
)
from studies.momentum_13612_universes.universes import (  # noqa: E402
    load_yfinance_price_frame,
    us_etf_tickers,
)


STUDY_DIR = Path(__file__).resolve().parent
RESULTS_DIR = STUDY_DIR / "results"
PLOTS_DIR = STUDY_DIR / "plots" / "etf_staggered"
FINALIST_PLOTS_DIR = PLOTS_DIR / "finalists"
REPORT = STUDY_DIR / "REPORT_ETF_STAGGERED.md"
TIINGO_ROOT = REPO_ROOT / "data" / "tiingo"

DEFAULT_TOP_N = (3, 5, 10)
DEFAULT_REBALANCE_MONTHS = (3, 6, 12)
MECHANISMS: tuple[tuple[str, str, str], ...] = (
    ("raw_equal", "raw_13612", "equal"),
    ("raw_inverse_vol", "raw_13612", "inverse_vol"),
)


def make_staggered_name(mechanism: str, top_n: int, rebalance_months: int) -> str:
    return f"mom13612_us_etfs_{mechanism}_top{top_n}_reb{rebalance_months}_staggered"


def build_configs(args: argparse.Namespace, tickers: tuple[str, ...]) -> list[ExtensiveConfig]:
    configs: list[ExtensiveConfig] = []
    for mechanism, score_mode, weight_mode in MECHANISMS:
        for top_n in parse_int_tuple(args.top_n):
            for freq in parse_int_tuple(args.rebalance_months):
                configs.append(
                    ExtensiveConfig(
                        name=make_staggered_name(mechanism, top_n, freq),
                        universe="us_etfs",
                        assets=tickers,
                        top_n=top_n,
                        rebalance_months=freq,
                        rebalance_offset=0,
                        score_mode=score_mode,  # type: ignore[arg-type]
                        weight_mode=weight_mode,  # type: ignore[arg-type]
                        absolute_filter=False,
                        vol_window_days=args.vol_window_days,
                        trend_window_days=args.trend_window_days,
                    )
                )
    return configs


def select_finalists(results: pd.DataFrame, max_finalists: int) -> pd.DataFrame:
    selected = [
        results.nlargest(6, "after_tax_sharpe"),
        results.nlargest(6, "after_tax_calmar"),
        results.nlargest(6, "excess_cagr"),
        results.nlargest(4, "min_relative_equity"),
        results.nlargest(4, "rolling_rel_score"),
    ]
    out = pd.concat(selected).drop_duplicates("name")
    out = out.sort_values(["after_tax_sharpe", "after_tax_calmar"], ascending=False)
    return out.head(max_finalists).copy()


def write_aggregate_plots(results: pd.DataFrame) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []

    fig, ax = plt.subplots(figsize=(9, 6))
    for mechanism, sub in results.groupby("mechanism"):
        ax.scatter(
            sub["after_tax_mdd"] * 100.0,
            sub["after_tax_cagr"] * 100.0,
            s=35 + sub["top_n"].astype(float) * 2.0,
            alpha=0.75,
            label=mechanism,
        )
        for _, row in sub.iterrows():
            ax.annotate(
                f"T{int(row['top_n'])}/R{int(row['rebalance_months'])}",
                (row["after_tax_mdd"] * 100.0, row["after_tax_cagr"] * 100.0),
                fontsize=7,
                alpha=0.75,
            )
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=1.0)
    ax.set_title("ETF staggered configs: after-tax CAGR vs MDD")
    ax.set_xlabel("MDD (%)")
    ax.set_ylabel("CAGR (%)")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    paths.append(save_fig(fig, "staggered_cagr_vs_mdd.png"))

    fig, ax = plt.subplots(figsize=(11, 5))
    labels = [f"{row.mechanism}\nT{int(row.top_n)} R{int(row.rebalance_months)}" for row in results.itertuples()]
    ordered = results.sort_values("after_tax_sharpe", ascending=False)
    labels = [f"{row.mechanism}\nT{int(row.top_n)} R{int(row.rebalance_months)}" for row in ordered.itertuples()]
    ax.bar(range(len(ordered)), ordered["after_tax_sharpe"], color="steelblue")
    ax.set_xticks(range(len(ordered)), labels, rotation=75, ha="right", fontsize=7)
    ax.set_title("ETF staggered configs by after-tax Sharpe")
    ax.set_ylabel("Sharpe")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    paths.append(save_fig(fig, "staggered_sharpe_rank.png"))

    fig, ax = plt.subplots(figsize=(8, 5))
    for freq, sub in results.groupby("rebalance_months"):
        ax.scatter(
            sub["annual_turnover"],
            sub["tax_drag_cagr"] * 100.0,
            s=45,
            alpha=0.75,
            label=f"reb{int(freq)}",
        )
    ax.set_title("Turnover vs annual tax drag")
    ax.set_xlabel("Turnover/year")
    ax.set_ylabel("Tax drag CAGR (pp)")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    paths.append(save_fig(fig, "staggered_turnover_tax_drag.png"))
    return paths


def save_fig(fig, filename: str) -> str:
    path = PLOTS_DIR / filename
    fig.savefig(path, dpi=140)
    import matplotlib.pyplot as plt

    plt.close(fig)
    return str(path.relative_to(STUDY_DIR))


def format_result_row(row: pd.Series) -> dict[str, object]:
    return {
        "Name": row["name"],
        "Mechanism": row["mechanism"],
        "Top-N": int(row["top_n"]),
        "Reb": int(row["rebalance_months"]),
        "Sleeves": int(row["n_sleeves"]),
        "CAGR": fmt_pct(float(row["after_tax_cagr"])),
        "Gross CAGR": fmt_pct(float(row["gross_cagr"])),
        "Tax Drag": fmt_pct(float(row["tax_drag_cagr"])),
        "SPY CAGR": fmt_pct(float(row["spy_cagr"])),
        "Excess": fmt_pct(float(row["excess_cagr"])),
        "MDD": fmt_pct(float(row["after_tax_mdd"])),
        "Vol": fmt_pct(float(row["after_tax_vol"])),
        "Sharpe": fmt_num(float(row["after_tax_sharpe"])),
        "Calmar": fmt_num(float(row["after_tax_calmar"])),
        "Turnover/yr": fmt_num(float(row["annual_turnover"])),
        "Above SPY": fmt_pct(float(row["pct_time_above_spy"])),
        "Rolling Rel": fmt_pct(float(row["rolling_rel_score"])),
    }


def result_table(frame: pd.DataFrame) -> str:
    rows = [format_result_row(row) for _, row in frame.iterrows()]
    return md_table(
        rows,
        [
            "Name",
            "Mechanism",
            "Top-N",
            "Reb",
            "Sleeves",
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
            "Mechanism",
            "Top-N",
            "Reb",
            "Sleeves",
            "CAGR",
            "Excess",
            "MDD",
            "Sharpe",
            "Calmar",
            "Turnover/yr",
            "Above SPY",
            "Rolling Rel",
            "Plot",
        ],
    )


def key_findings(results: pd.DataFrame, pbo_rows: list[dict[str, object]]) -> str:
    best = results.nlargest(1, "after_tax_sharpe").iloc[0]
    best_relative = results.nlargest(1, "rolling_rel_score").iloc[0]
    best_balanced = results[results["after_tax_mdd"] >= -0.30]
    balance_line = "- Nenhuma configuração manteve MDD acima de `-30%`.\n"
    if not best_balanced.empty:
        row = best_balanced.nlargest(1, "after_tax_sharpe").iloc[0]
        balance_line = (
            f"- Melhor linha com MDD >= `-30%`: `{row['name']}`, CAGR "
            f"`{fmt_pct(float(row['after_tax_cagr']))}`, MDD "
            f"`{fmt_pct(float(row['after_tax_mdd']))}`, Sharpe "
            f"`{fmt_num(float(row['after_tax_sharpe']))}`.\n"
        )
    turnover = results.groupby("rebalance_months").agg(
        median_sharpe=("after_tax_sharpe", "median"),
        median_turnover=("annual_turnover", "median"),
        median_tax_drag=("tax_drag_cagr", "median"),
    )
    best_freq = int(turnover["median_sharpe"].idxmax())
    low_turnover_freq = int(turnover["median_turnover"].idxmin())
    all_pbo = float(next((row.get("pbo") for row in pbo_rows if row["group"] == "all"), float("nan")))
    return (
        f"- Melhor Sharpe after-tax: `{best['name']}`, CAGR "
        f"`{fmt_pct(float(best['after_tax_cagr']))}`, MDD "
        f"`{fmt_pct(float(best['after_tax_mdd']))}`, Sharpe "
        f"`{fmt_num(float(best['after_tax_sharpe']))}`, turnover "
        f"`{fmt_num(float(best['annual_turnover']))}x/ano`.\n"
        f"- Melhor rolling relative score vs SPY: `{best_relative['name']}`, score "
        f"`{fmt_pct(float(best_relative['rolling_rel_score']))}`, p25 "
        f"`{fmt_pct(float(best_relative['rolling_rel_p25_score']))}`.\n"
        f"{balance_line}"
        f"- Frequência com maior Sharpe mediano: `{best_freq}m`; menor turnover mediano: "
        f"`{low_turnover_freq}m`.\n"
        f"- PBO do painel staggered ETF: `{all_pbo:.3f}` sobre retornos after-tax. "
        "Ainda é yfinance/current-universe screen-only `[advances_fin_ml, p.208-211]`.\n"
    )


def write_report(
    results: pd.DataFrame,
    finalists: pd.DataFrame,
    pbo_rows: list[dict[str, object]],
    aggregate_plots: list[str],
    args: argparse.Namespace,
) -> None:
    top_sharpe = results.nlargest(20, "after_tax_sharpe")
    top_excess = results.nlargest(20, "excess_cagr")
    pbo_table = [row for row in pbo_rows if row["group"] == "all" or str(row["group"]).startswith("mechanism:")]
    overall = next((row for row in pbo_rows if row["group"] == "all"), {})
    verdict = (
        "Screen-only FAIL: yfinance/current ETF universe is non-promotable, and "
        f"overall PBO is {float(overall.get('pbo', float('nan'))):.3f}."
    )

    REPORT.write_text(
        "# ETF Staggered Momentum 13612 Report\n\n"
        "Status: research-only. No deployment, paper-trade label or mandate change.\n\n"
        "## Verdict\n\n"
        f"{verdict}\n\n"
        "## Grid\n\n"
        "- Universe: `us_etfs` current curated ETF list\n"
        f"- Top-N: `{args.top_n}`\n"
        f"- Rebalance frequencies: `{args.rebalance_months}` months\n"
        "- Offset policy: all offsets are equal-capital sleeves; no best-offset selection\n"
        f"- Mechanisms: `{', '.join(name for name, *_ in MECHANISMS)}`\n"
        f"- Rows: `{len(results)}`\n"
        "- Ranking metric: after-tax strategy returns under Brazil's annual 15% realized-gain rule\n"
        "- Benchmark: SPY adjusted close as S&P 500 proxy\n\n"
        "## Key Findings\n\n"
        + key_findings(results, pbo_rows)
        + "\n## Aggregate Plots\n\n"
        + "\n".join(f"- [{Path(path).name}]({path})" for path in aggregate_plots)
        + "\n\n## Top By After-Tax Sharpe\n\n"
        + result_table(top_sharpe)
        + "\n## Top By After-Tax Excess CAGR\n\n"
        + result_table(top_excess)
        + "\n## Finalists With Individual Plots\n\n"
        + finalist_table(finalists)
        + "\n## PBO Summary\n\n"
        + md_table(pbo_table, ["group", "pbo", "n_configs", "n_obs", "n_combinations", "pass"])
        + "\n## Caveats\n\n"
        "- All rows are yfinance/current-universe screens and `promotion_eligible=false` "
        "until PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.\n"
        "- The staggered construction reduces timing-luck selection but does not remove "
        "data-mining risk or survivorship bias `[advances_fin_ml, p.273-275]`.\n"
        "- Main rankings are after-tax for realized capital gains, but still gross of "
        "transaction costs/slippage.\n"
        "- Tax model nets realized gains/losses annually at 15% and does not force a "
        "final liquidation of unrealized positions.\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ETF-only staggered 13612 grid")
    parser.add_argument("--us-source", choices=["yfinance", "tiingo"], default="yfinance")
    parser.add_argument("--allow-biased-yfinance", action="store_true")
    parser.add_argument("--us-etf-universe", choices=["curated", "tiingo_manifest"], default="curated")
    parser.add_argument("--max-us-etfs", type=int, default=9999)
    parser.add_argument("--top-n", default=",".join(str(value) for value in DEFAULT_TOP_N))
    parser.add_argument(
        "--rebalance-months",
        default=",".join(str(value) for value in DEFAULT_REBALANCE_MONTHS),
    )
    parser.add_argument("--start", default="2000-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--vol-window-days", type=int, default=126)
    parser.add_argument("--trend-window-days", type=int, default=126)
    parser.add_argument("--max-finalists", type=int, default=12)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    FINALIST_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    tickers = tuple(us_etf_tickers(TIINGO_ROOT, limit=args.max_us_etfs, universe=args.us_etf_universe))
    configs = build_configs(args, tickers)
    benchmark_prices = load_yfinance_price_frame(("SPY",), args.start, args.end, allow_missing=False)
    prices, _source = load_us_price_frame(tickers, args)
    bundle = precompute_scores(
        prices,
        tickers,
        vol_window_days=args.vol_window_days,
        trend_window_days=args.trend_window_days,
    )

    rows: list[dict[str, object]] = []
    returns_by_name: dict[str, pd.Series] = {}
    n_trials = len(configs)
    for i, config in enumerate(configs, start=1):
        simulation = simulate_staggered_offsets(prices, bundle, config)
        if simulation.returns.empty:
            continue
        tax = apply_br_foreign_annual_tax(simulation.returns, simulation.daily_weights)
        row = result_row(
            config,
            simulation,
            benchmark_prices,
            n_trials=n_trials,
            ranked_returns=tax.returns,
            tax_summary=tax.summary,
        )
        row["staggered_offsets"] = "all"
        row["n_sleeves"] = config.rebalance_months
        rows.append(row)
        returns_by_name[config.name] = tax.returns
        print(f"simulated {i}/{n_trials}: {config.name}", flush=True)

    results = pd.DataFrame(rows)
    results_path = RESULTS_DIR / "staggered_etf_results.csv"
    results.to_csv(results_path, index=False)
    (RESULTS_DIR / "staggered_etf_results.json").write_text(
        json.dumps(json_safe(results.to_dict(orient="records")), indent=2, allow_nan=False),
        encoding="utf-8",
    )
    pbo_data = pbo_summary(returns_by_name, results)
    (RESULTS_DIR / "staggered_etf_pbo.json").write_text(
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
    finalists.to_csv(RESULTS_DIR / "staggered_etf_finalists.csv", index=False)
    write_report(results, finalists, pbo_data["rows"], aggregate_plots, args)

    print(f"wrote {REPORT.relative_to(REPO_ROOT)}")
    print(f"wrote {results_path.relative_to(REPO_ROOT)}")
    print(f"wrote {(RESULTS_DIR / 'staggered_etf_finalists.csv').relative_to(REPO_ROOT)}")
    print(f"wrote {len(aggregate_plots)} aggregate plots and {len(plot_paths)} finalist plots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
