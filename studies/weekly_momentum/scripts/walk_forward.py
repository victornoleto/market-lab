#!/usr/bin/env python3
"""Walk-forward parameter search for weekly_momentum.

The goal is to reduce overfit risk by selecting parameters only on a trailing
training window, then evaluating the selected config on the next unseen window.
Walk-forward validation is a required robustness gate in the project mandate and
is used here as a first diagnostic before deeper PBO/DSR/bootstrap work
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.196-202]`.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
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
from studies.weekly_momentum.core import WeeklyMomentumConfig, simulate_weekly_momentum
from studies.weekly_momentum.data import load_variation_prices
from studies.weekly_momentum.reporting import config_slug, compute_report_metrics


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Weekly momentum walk-forward search")
    parser.add_argument("--variation", choices=["stocks", "etfs"], default="stocks")
    parser.add_argument("--stock-universe", choices=["sp500", "all"], default="sp500")
    parser.add_argument("--only-sp500", type=int, choices=[0, 1], default=1)
    parser.add_argument("--lookbacks", default="4,20,60")
    parser.add_argument("--top-ks", default="3,5,10,20")
    parser.add_argument("--market-filters", default="none,sma100,sma200,ema100,ema200")
    parser.add_argument("--market-smas", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--allow-negative-momentum", default="0,1")
    parser.add_argument("--train-years", type=int, default=3)
    parser.add_argument("--test-years", type=int, default=1)
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--storage-root", default="data/tiingo")
    parser.add_argument("--spy-path", default="data/tiingo/daily/prices/SPY.parquet")
    parser.add_argument("--output-dir", default="studies/weekly_momentum/walk_forward/stocks")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    lookbacks = _parse_ints(args.lookbacks)
    top_ks = _parse_ints(args.top_ks)
    market_filters = _parse_market_filters(args.market_smas, args.market_filters)
    allow_negative_values = [bool(v) for v in _parse_ints(args.allow_negative_momentum)]

    prices = load_variation_prices(
        args.variation,
        storage_root=args.storage_root,
        start=start,
        end=end,
        min_bars=max(lookbacks) + 2,
        only_sp500=bool(args.only_sp500),
    )
    if prices.empty:
        raise SystemExit("No prices loaded")
    spy = load_spy_series(args.spy_path).reindex(prices.index).ffill()

    configs = _build_configs(lookbacks, top_ks, market_filters, allow_negative_values)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    returns_by_config: dict[str, pd.Series] = {}
    configs_by_slug: dict[str, WeeklyMomentumConfig] = {}
    for cfg in configs:
        slug = config_slug(cfg)
        result = simulate_weekly_momentum(
            prices,
            cfg,
            market_filter_prices=spy if cfg.market_filter_type != "none" else None,
        )
        returns_by_config[slug] = result.returns
        configs_by_slug[slug] = cfg

    windows = _walk_forward_windows(prices.index, args.train_years, args.test_years)
    selections, wf_returns = _run_walk_forward(returns_by_config, windows)
    wf_equity = (1.0 + wf_returns).cumprod() * 10_000.0
    spy_returns = spy.pct_change(fill_method=None).fillna(0.0).reindex(wf_returns.index).fillna(0.0)
    spy_equity = (1.0 + spy_returns).cumprod() * 10_000.0

    metrics = {
        "walk_forward": compute_report_metrics(wf_equity, wf_returns),
        "spy": compute_report_metrics(spy_equity, spy_returns),
    }
    per_config = _per_config_metrics(returns_by_config)

    pd.DataFrame(selections).to_csv(out_dir / "selections.csv", index=False)
    pd.DataFrame({"wf_return": wf_returns, "wf_equity": wf_equity}).to_csv(out_dir / "walk_forward_equity.csv")
    pd.DataFrame(metrics).to_csv(out_dir / "metrics.csv")
    per_config.to_csv(out_dir / "per_config_metrics.csv", index=False)
    (out_dir / "config_grid.json").write_text(
        json.dumps({slug: asdict(cfg) for slug, cfg in configs_by_slug.items()}, indent=2) + "\n",
        encoding="utf-8",
    )
    _plot_wf_equity(wf_equity, spy_equity, out_dir / "walk_forward_vs_spy.png")
    _write_report(out_dir / "WALK_FORWARD_REPORT.md", args, metrics, selections, per_config)

    print(f"configs={len(configs)}")
    print(f"windows={len(selections)}")
    print(f"wf_cagr={metrics['walk_forward']['cagr']:.6f}")
    print(f"wf_mdd={metrics['walk_forward']['mdd']:.6f}")
    print(f"wf_sharpe={metrics['walk_forward']['sharpe']:.6f}")
    print(f"outputs={out_dir}")
    return 0


def _build_configs(
    lookbacks: list[int],
    top_ks: list[int],
    market_filters: list[tuple[str, int | None]],
    allow_negative_values: list[bool],
) -> list[WeeklyMomentumConfig]:
    configs = []
    for lookback in lookbacks:
        for top_k in top_ks:
            for filter_type, filter_days in market_filters:
                for allow_negative in allow_negative_values:
                    configs.append(
                        WeeklyMomentumConfig(
                            lookback_days=lookback,
                            top_k=top_k,
                            allow_negative_momentum=allow_negative,
                            market_filter_type=filter_type,
                            market_filter_days=filter_days,
                        )
                    )
    return configs


def _walk_forward_windows(
    index: pd.DatetimeIndex,
    train_years: int,
    test_years: int,
) -> list[dict[str, pd.Timestamp]]:
    first = pd.Timestamp(index.min()).normalize()
    last = pd.Timestamp(index.max()).normalize()
    train_start = first
    windows = []
    while True:
        train_end = train_start + pd.DateOffset(years=train_years) - pd.Timedelta(days=1)
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + pd.DateOffset(years=test_years) - pd.Timedelta(days=1)
        if test_end > last:
            break
        windows.append({
            "train_start": train_start,
            "train_end": train_end,
            "test_start": test_start,
            "test_end": test_end,
        })
        train_start = train_start + pd.DateOffset(years=test_years)
    return windows


def _run_walk_forward(
    returns_by_config: dict[str, pd.Series],
    windows: list[dict[str, pd.Timestamp]],
) -> tuple[list[dict], pd.Series]:
    selections = []
    wf_parts = []
    for window in windows:
        train_scores = []
        for slug, returns in returns_by_config.items():
            train = returns.loc[window["train_start"]:window["train_end"]]
            train_scores.append((slug, _selection_score(train), _period_stats(train)))
        train_scores.sort(key=lambda row: (-row[1], row[0]))
        selected, score, train_stats = train_scores[0]
        test = returns_by_config[selected].loc[window["test_start"]:window["test_end"]]
        test_stats = _period_stats(test)
        wf_parts.append(test)
        selections.append({
            **{k: str(v.date()) for k, v in window.items()},
            "selected_config": selected,
            "selection_score": score,
            "train_cagr": train_stats["cagr"],
            "train_mdd": train_stats["mdd"],
            "train_sharpe": train_stats["sharpe"],
            "test_cagr": test_stats["cagr"],
            "test_mdd": test_stats["mdd"],
            "test_sharpe": test_stats["sharpe"],
        })
    wf_returns = pd.concat(wf_parts).sort_index() if wf_parts else pd.Series(dtype=float)
    wf_returns = wf_returns[~wf_returns.index.duplicated(keep="first")]
    return selections, wf_returns.rename("wf_return")


def _selection_score(returns: pd.Series) -> float:
    stats = _period_stats(returns)
    if not np.isfinite(stats["sharpe"]):
        return float("-inf")
    # Train-only score: prefer high Sharpe/CAGR while penalising drawdown.
    return float(stats["sharpe"] + stats["cagr"] - abs(stats["mdd"]))


def _period_stats(returns: pd.Series) -> dict[str, float]:
    returns = returns.dropna()
    if len(returns) < 20:
        return {"cagr": float("nan"), "mdd": float("nan"), "sharpe": float("-inf")}
    equity = (1.0 + returns).cumprod()
    years = len(returns) / 252.0
    cagr = float(equity.iloc[-1] ** (1.0 / years) - 1.0)
    mdd = float((equity / equity.cummax() - 1.0).min())
    std = float(returns.std(ddof=1))
    sharpe = float(returns.mean() / std * np.sqrt(252.0)) if std > 0 else 0.0
    return {"cagr": cagr, "mdd": mdd, "sharpe": sharpe}


def _per_config_metrics(returns_by_config: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for slug, returns in returns_by_config.items():
        stats = _period_stats(returns)
        rows.append({"config": slug, **stats})
    return pd.DataFrame(rows).sort_values(["sharpe", "cagr"], ascending=False)


def _plot_wf_equity(wf_equity: pd.Series, spy_equity: pd.Series, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.plot(wf_equity.index, wf_equity.values, label="Walk-forward selected", linewidth=1.6)
    ax.plot(spy_equity.index, spy_equity.values, label="SPY buy & hold", color="black", linestyle="--", linewidth=1.4)
    ax.set_yscale("log")
    ax.set_title("Weekly momentum walk-forward vs SPY")
    ax.set_ylabel("Equity ($, log scale)")
    ax.grid(True, which="both", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def _write_report(
    out_path: Path,
    args: argparse.Namespace,
    metrics: dict[str, dict[str, float]],
    selections: list[dict],
    per_config: pd.DataFrame,
) -> None:
    wf = metrics["walk_forward"]
    spy = metrics["spy"]
    sel = pd.DataFrame(selections)
    lines = [
        "# Weekly Momentum Walk-Forward Report",
        "",
        "## Setup",
        "",
        f"- Variation: `{args.variation}` / universe `{_universe_label(args)}`.",
        f"- Grid: lookbacks `{args.lookbacks}`, top_k `{args.top_ks}`, market filters `{args.market_filters}`, allow_negative `{args.allow_negative_momentum}`.",
        f"- Windows: `{args.train_years}`y train -> `{args.test_years}`y test, rolled by test window.",
        "- Selection score: train Sharpe + train CAGR - abs(train MDD).",
        "- Purpose: reduce parameter overfit by evaluating each selected config only in subsequent unseen windows `[advances_fin_ml, p.208-211]`.",
        "",
        "## Walk-Forward Result",
        "",
        "| metric | walk-forward | SPY |",
        "|---|---:|---:|",
        f"| CAGR | {_pct(wf['cagr'])} | {_pct(spy['cagr'])} |",
        f"| MDD | {_pct(wf['mdd'])} | {_pct(spy['mdd'])} |",
        f"| Sharpe | {wf['sharpe']:.3f} | {spy['sharpe']:.3f} |",
        f"| Sortino | {wf['sortino']:.3f} | {spy['sortino']:.3f} |",
        "",
        "![Walk-forward vs SPY](walk_forward_vs_spy.png)",
        "",
        "## Window Selections",
        "",
        sel.to_markdown(index=False) if not sel.empty else "No windows generated.",
        "",
        "## Top Full-Period Configs In Grid",
        "",
        per_config.head(15).to_markdown(index=False),
        "",
        "## Caveats",
        "",
        "- This is walk-forward, not yet full CPCV/PBO/DSR/bootstrap validation.",
        f"- {_universe_caveat(args)}",
        "- Costs, slippage and taxes are still absent.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _parse_ints(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def _parse_market_filters(
    legacy_smas: str | None,
    raw: str,
) -> list[tuple[str, int | None]]:
    if legacy_smas is not None:
        return [("none", None) if v == 0 else ("sma", v) for v in _parse_ints(legacy_smas)]
    out: list[tuple[str, int | None]] = []
    for item in raw.split(","):
        token = item.strip().lower()
        if not token:
            continue
        if token == "none" or token == "0":
            out.append(("none", None))
        elif token.startswith("sma"):
            out.append(("sma", int(token[3:])))
        elif token.startswith("ema"):
            out.append(("ema", int(token[3:])))
        else:
            raise ValueError(f"unknown market filter token: {item!r}")
    return out


def _universe_label(args: argparse.Namespace) -> str:
    if args.variation != "stocks":
        return "all_etfs"
    return "sp500" if bool(args.only_sp500) else "all_stocks"


def _universe_caveat(args: argparse.Namespace) -> str:
    if args.variation != "stocks":
        return "ETF cache coverage is not a point-in-time investable universe."
    if bool(args.only_sp500):
        return "Current S&P 500 membership remains survivorship-biased."
    return "Full stock cache coverage is not a point-in-time investable universe."


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%" if np.isfinite(value) else "nan"


if __name__ == "__main__":
    raise SystemExit(main())
