#!/usr/bin/env python3
"""Deep dive diagnostics for Phase 5 ADV5M dynamic all-stocks momentum.

This script does not search new parameters. It decomposes the already-frozen
ADV5M walk-forward output into symbol contribution, annual dependence,
concentration, stress-removal diagnostics and extreme days. The goal is to audit
whether the attractive headline CAGR is broad or driven by fragile tails
`[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from studies.weekly_momentum.data import load_variation_prices
from studies.weekly_momentum.reporting import compute_report_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ADV5M dynamic all-stocks deep dive")
    parser.add_argument(
        "--input-dir",
        default="studies/weekly_momentum/phase5_all_stocks_dynamic_adv5m/dynamic_wf_all_stocks",
    )
    parser.add_argument("--output-dir", default="studies/weekly_momentum/phase5_adv5m_deep_dive")
    parser.add_argument("--storage-root", default="data/tiingo")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    aligned = _read_indexed_csv(input_dir / "aligned_strategy_spy.csv")
    weights = _read_indexed_csv(input_dir / "weights.csv")
    selections = pd.read_csv(input_dir / "selections.csv")
    prices = load_variation_prices("stocks", storage_root=args.storage_root, only_sp500=False, min_bars=102)
    prices = prices.reindex(weights.index).reindex(columns=weights.columns)
    asset_returns = prices.pct_change(fill_method=None).fillna(0.0)
    contributions = weights * asset_returns

    symbol_summary = _symbol_summary(weights, contributions, prices)
    annual = _annual_summary(aligned, contributions)
    top_days = _extreme_days(aligned, weights, contributions)
    removal = _removal_stress(aligned["strategy_return"], contributions)
    concentration = _concentration(symbol_summary)

    symbol_summary.to_csv(out_dir / "symbol_contribution.csv", index=False)
    annual.to_csv(out_dir / "annual_summary.csv", index=False)
    top_days.to_csv(out_dir / "extreme_days.csv", index=False)
    removal.to_csv(out_dir / "top_contributor_removal_stress.csv", index=False)
    concentration.to_csv(out_dir / "concentration_summary.csv", index=False)
    selections.to_csv(out_dir / "wf_selections.csv", index=False)

    _plot_top_contributors(symbol_summary, plots_dir / "top_contributors.png")
    _plot_annual(annual, plots_dir / "annual_returns_vs_spy.png")
    _plot_removal(removal, plots_dir / "top_contributor_removal_stress.png")
    _write_report(out_dir / "ADV5M_DEEP_DIVE_REPORT.md", symbol_summary, annual, top_days, removal, concentration, selections)

    print(f"outputs={out_dir}")
    print(symbol_summary.head(10)[["symbol", "total_contribution", "held_days", "avg_weight_when_held"]].to_string(index=False))
    print(removal[["scenario", "cagr", "mdd", "sharpe"]].to_string(index=False))
    return 0


def _read_indexed_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=[0])
    df = df.rename(columns={df.columns[0]: "date"}).set_index("date")
    return df.sort_index()


def _symbol_summary(weights: pd.DataFrame, contributions: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    held = weights > 0.0
    stale = held & prices.isna()
    total = contributions.sum(axis=0)
    positive = contributions.clip(lower=0.0).sum(axis=0)
    negative = contributions.clip(upper=0.0).sum(axis=0)
    held_days = held.sum(axis=0)
    stale_held_days = stale.sum(axis=0)
    avg_weight = weights.where(held).mean(axis=0).fillna(0.0)
    best_day = contributions.max(axis=0)
    worst_day = contributions.min(axis=0)
    first_held = held.apply(lambda col: col.index[col].min().date().isoformat() if bool(col.any()) else "")
    last_held = held.apply(lambda col: col.index[col].max().date().isoformat() if bool(col.any()) else "")
    last_valid_price = prices.notna().apply(lambda col: col.index[col].max().date().isoformat() if bool(col.any()) else "")
    rows = pd.DataFrame({
        "symbol": total.index.astype(str),
        "total_contribution": total.to_numpy(dtype=float),
        "positive_contribution": positive.to_numpy(dtype=float),
        "negative_contribution": negative.to_numpy(dtype=float),
        "held_days": held_days.to_numpy(dtype=int),
        "stale_held_days": stale_held_days.to_numpy(dtype=int),
        "avg_weight_when_held": avg_weight.to_numpy(dtype=float),
        "best_day_contribution": best_day.to_numpy(dtype=float),
        "worst_day_contribution": worst_day.to_numpy(dtype=float),
        "first_held": first_held.to_numpy(),
        "last_held": last_held.to_numpy(),
        "last_valid_price": last_valid_price.to_numpy(),
    })
    rows = rows[rows["held_days"] > 0].sort_values("total_contribution", ascending=False)
    rows["rank_total_contribution"] = range(1, len(rows) + 1)
    return rows


def _annual_summary(aligned: pd.DataFrame, contributions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, strategy in aligned["strategy_return"].groupby(aligned.index.year):
        spy = aligned.loc[strategy.index, "spy_return"]
        year_contrib = contributions.loc[strategy.index]
        active_days = int((year_contrib.abs().sum(axis=1) > 0.0).sum())
        rows.append({
            "year": int(year),
            "strategy_return": float((1.0 + strategy).prod() - 1.0),
            "spy_return": float((1.0 + spy).prod() - 1.0),
            "excess_return": float((1.0 + strategy).prod() / (1.0 + spy).prod() - 1.0),
            "active_days": active_days,
            "top_symbol": str(year_contrib.sum(axis=0).idxmax()),
            "top_symbol_contribution": float(year_contrib.sum(axis=0).max()),
            "worst_symbol": str(year_contrib.sum(axis=0).idxmin()),
            "worst_symbol_contribution": float(year_contrib.sum(axis=0).min()),
        })
    return pd.DataFrame(rows)


def _extreme_days(aligned: pd.DataFrame, weights: pd.DataFrame, contributions: pd.DataFrame) -> pd.DataFrame:
    selected_dates = list(aligned["strategy_return"].nlargest(10).index)
    selected_dates.extend(aligned["strategy_return"].nsmallest(10).index)
    rows = []
    for date in selected_dates:
        day_weights = weights.loc[date]
        day_contrib = contributions.loc[date]
        held = day_weights[day_weights > 0.0].sort_values(ascending=False)
        lead = day_contrib.reindex(held.index).sort_values(ascending=False)
        rows.append({
            "date": date.date().isoformat(),
            "strategy_return": float(aligned.loc[date, "strategy_return"]),
            "spy_return": float(aligned.loc[date, "spy_return"]),
            "n_held": int(len(held)),
            "held_symbols": ",".join(held.index.astype(str).tolist()),
            "best_symbol": str(lead.index[0]) if len(lead) else "",
            "best_contribution": float(lead.iloc[0]) if len(lead) else 0.0,
            "worst_symbol": str(lead.index[-1]) if len(lead) else "",
            "worst_contribution": float(lead.iloc[-1]) if len(lead) else 0.0,
        })
    return pd.DataFrame(rows).drop_duplicates("date")


def _removal_stress(strategy_returns: pd.Series, contributions: pd.DataFrame) -> pd.DataFrame:
    total_by_symbol = contributions.sum(axis=0).sort_values(ascending=False)
    scenarios: list[tuple[str, list[str]]] = [("base", [])]
    for n in [1, 3, 5, 10, 20]:
        scenarios.append((f"remove_top_{n}_contributors", total_by_symbol.head(n).index.astype(str).tolist()))
    rows = []
    for name, symbols in scenarios:
        adjusted = strategy_returns.copy()
        if symbols:
            adjusted = adjusted - contributions[symbols].sum(axis=1)
        equity = (1.0 + adjusted).cumprod() * 10_000.0
        rows.append({"scenario": name, "removed_symbols": ",".join(symbols), **compute_report_metrics(equity, adjusted)})
    return pd.DataFrame(rows)


def _concentration(symbol_summary: pd.DataFrame) -> pd.DataFrame:
    positive_total = float(symbol_summary["positive_contribution"].sum())
    net_total = float(symbol_summary["total_contribution"].sum())
    rows = []
    for n in [1, 3, 5, 10, 20, 50]:
        head = symbol_summary.head(n)
        rows.append({
            "top_n": n,
            "net_contribution": float(head["total_contribution"].sum()),
            "share_of_net_arithmetic_contribution": float(head["total_contribution"].sum() / net_total) if net_total else 0.0,
            "positive_contribution": float(head["positive_contribution"].sum()),
            "share_of_positive_contribution": float(head["positive_contribution"].sum() / positive_total) if positive_total else 0.0,
        })
    return pd.DataFrame(rows)


def _plot_top_contributors(symbol_summary: pd.DataFrame, out_path: Path) -> None:
    top = symbol_summary.head(20).sort_values("total_contribution")
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(top["symbol"], top["total_contribution"])
    ax.set_title("ADV5M top arithmetic symbol contributions")
    ax.set_xlabel("Daily contribution sum")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_annual(annual: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(annual["year"] - 0.2, annual["strategy_return"], width=0.4, label="ADV5M")
    ax.bar(annual["year"] + 0.2, annual["spy_return"], width=0.4, label="SPY")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_title("ADV5M annual returns vs SPY")
    ax.set_ylabel("Return")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_removal(removal: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(removal["scenario"], removal["cagr"], marker="o", label="CAGR")
    ax.plot(removal["scenario"], removal["sharpe"], marker="o", label="Sharpe")
    ax.set_title("ADV5M stress after removing top contributors")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _write_report(
    out_path: Path,
    symbol_summary: pd.DataFrame,
    annual: pd.DataFrame,
    top_days: pd.DataFrame,
    removal: pd.DataFrame,
    concentration: pd.DataFrame,
    selections: pd.DataFrame,
) -> None:
    lines = [
        "# ADV5M Deep Dive",
        "",
        "## TL;DR",
        "",
        "This is a decomposition of the frozen Phase 5 ADV5M dynamic all-stocks output. It does not add parameters or search a better variant.",
        "",
        "Main finding: ADV5M is economically interesting, but the decomposition increases concern rather than reducing it. The result is heavily helped by 2020-2021 meme/high-beta winners, and the output contains held positions after the last valid cached price for some symbols. That stale/delisting behavior must be fixed before treating the backtest as deploy evidence `[advances_fin_ml, p.208-211]`.",
        "",
        "## Walk-Forward Selection Path",
        "",
        selections.to_markdown(index=False),
        "",
        "## Annual Dependence",
        "",
        annual.to_markdown(index=False),
        "",
        "## Concentration",
        "",
        concentration.to_markdown(index=False),
        "",
        "## Top Symbol Contributions",
        "",
        symbol_summary.head(25).to_markdown(index=False),
        "",
        "## Stale Held Symbols",
        "",
        symbol_summary[symbol_summary["stale_held_days"] > 0]
        .sort_values(["stale_held_days", "total_contribution"], ascending=[False, False])
        .head(25)
        .to_markdown(index=False),
        "",
        "## Removal Stress",
        "",
        removal[["scenario", "removed_symbols", "cagr", "mdd", "sharpe", "sortino", "calmar"]].to_markdown(index=False),
        "",
        "## Extreme Days",
        "",
        top_days.to_markdown(index=False),
        "",
        "## Plots",
        "",
        "![Top contributors](plots/top_contributors.png)",
        "",
        "![Annual returns vs SPY](plots/annual_returns_vs_spy.png)",
        "",
        "![Top contributor removal stress](plots/top_contributor_removal_stress.png)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
