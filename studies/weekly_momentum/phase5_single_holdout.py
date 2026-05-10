#!/usr/bin/env python3
"""Single-block holdout for Phase 5 dynamic all-stocks momentum.

The config is selected once on a training block using the same score as the
walk-forward runner, then evaluated on one final contiguous holdout block. This
is a stricter sanity check than rolling WF because the final block is not used
for repeated reselection `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from market_lab.backtest.metrics.standard_report import load_spy_series
from studies.weekly_momentum.core import simulate_weekly_momentum
from studies.weekly_momentum.data import load_variation_prices
from studies.weekly_momentum.reporting import compute_report_metrics, config_slug
from studies.weekly_momentum.validate_candidates import _tradability_provider
from studies.weekly_momentum.walk_forward import _build_configs, _parse_market_filters, _selection_score


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 5 single holdout")
    parser.add_argument("--adv20", type=float, default=5_000_000.0)
    parser.add_argument("--train-start", default="2013-01-02")
    parser.add_argument("--train-end", default="2022-12-31")
    parser.add_argument("--test-start", default="2023-01-01")
    parser.add_argument("--test-end", default="2025-12-31")
    parser.add_argument("--output-dir", default="studies/weekly_momentum/phase5_single_holdout_adv5m")
    parser.add_argument("--storage-root", default="data/tiingo")
    parser.add_argument("--spy-path", default="data/tiingo/daily/prices/SPY.parquet")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    prices = load_variation_prices("stocks", storage_root=args.storage_root, only_sp500=False, min_bars=102)
    provider_args = SimpleNamespace(
        pit_min_age_bars=252,
        pit_min_adv20=args.adv20,
        pit_min_price=5.0,
        storage_root=args.storage_root,
    )
    universe_provider = _tradability_provider(prices, provider_args)
    spy = load_spy_series(args.spy_path).reindex(prices.index).ffill()
    configs = _build_configs(
        [60, 80, 100],
        [5, 10, 20],
        _parse_market_filters(None, "sma200,sma250"),
        [False],
    )
    returns_by_slug = {}
    train_scores = []
    for cfg in configs:
        slug = config_slug(cfg)
        result = simulate_weekly_momentum(
            prices,
            cfg,
            market_filter_prices=spy,
            universe_by_date=universe_provider,
        )
        returns_by_slug[slug] = result.returns
        train = result.returns.loc[args.train_start:args.train_end]
        train_scores.append({"config": slug, "score": _selection_score(train), **_metrics_from_returns(train)})
        print(f"holdout adv20={args.adv20:g} config={len(train_scores)}/{len(configs)} slug={slug}", flush=True)
    score_df = pd.DataFrame(train_scores).sort_values(["score", "config"], ascending=[False, True])
    selected = str(score_df.iloc[0]["config"])
    test_returns = returns_by_slug[selected].loc[args.test_start:args.test_end]
    spy_returns = spy.pct_change(fill_method=None).fillna(0.0).loc[test_returns.index]
    test_equity = (1.0 + test_returns).cumprod() * 10_000.0
    spy_equity = (1.0 + spy_returns).cumprod() * 10_000.0
    metrics = pd.DataFrame([
        {"series": "strategy", **compute_report_metrics(test_equity, test_returns)},
        {"series": "spy", **compute_report_metrics(spy_equity, spy_returns)},
    ])
    aligned = pd.DataFrame({
        "strategy_return": test_returns,
        "strategy_equity": test_equity,
        "spy_return": spy_returns,
        "spy_equity": spy_equity,
    })
    score_df.to_csv(out_dir / "train_scores.csv", index=False)
    aligned.to_csv(out_dir / "holdout_aligned.csv")
    metrics.to_csv(out_dir / "holdout_metrics.csv", index=False)
    _plot(aligned, plots_dir / "holdout_equity_vs_spy.png")
    _write_report(out_dir / "HOLDOUT_REPORT.md", args, selected, metrics, score_df)
    print(f"selected={selected}")
    print(metrics[["series", "cagr", "mdd", "sharpe"]].to_string(index=False))
    print(f"outputs={out_dir}")
    return 0


def _metrics_from_returns(returns: pd.Series) -> dict[str, float]:
    equity = (1.0 + returns.dropna()).cumprod() * 10_000.0
    return compute_report_metrics(equity, returns.dropna())


def _plot(aligned: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.plot(aligned.index, aligned["strategy_equity"] / aligned["strategy_equity"].iloc[0], label="selected strategy")
    ax.plot(aligned.index, aligned["spy_equity"] / aligned["spy_equity"].iloc[0], label="SPY", linestyle="--", color="black")
    ax.set_yscale("log")
    ax.set_title("Single-block holdout vs SPY")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _write_report(out_path: Path, args: argparse.Namespace, selected: str, metrics: pd.DataFrame, scores: pd.DataFrame) -> None:
    lines = [
        "# Phase 5 Single-Block Holdout",
        "",
        f"- ADV20 threshold: `${args.adv20:,.0f}`.",
        f"- Train: `{args.train_start}`..`{args.train_end}`.",
        f"- Test: `{args.test_start}`..`{args.test_end}`.",
        f"- Selected config: `{selected}`.",
        "",
        "## Holdout Metrics",
        "",
        metrics.to_markdown(index=False),
        "",
        "## Top Train Scores",
        "",
        scores.head(10).to_markdown(index=False),
        "",
        "## Plot",
        "",
        "![Holdout equity vs SPY](plots/holdout_equity_vs_spy.png)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
