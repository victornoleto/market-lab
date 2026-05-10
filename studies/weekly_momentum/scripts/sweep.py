#!/usr/bin/env python3
"""Structured parameter sweep for weekly_momentum.

This is the broad-search layer before walk-forward/PBO/DSR. It reports full
period, subperiod and rolling-window edge metrics so candidates are ranked by
stability instead of one full-period CAGR. Parameter searches must later pay the
overfit-control cost `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import numpy as np
import pandas as pd

from market_lab.backtest.metrics.standard_report import load_spy_series
from studies.weekly_momentum.core import WeeklyMomentumConfig, simulate_weekly_momentum
from studies.weekly_momentum.data import load_variation_prices, sp500_pit_universe_provider
from studies.weekly_momentum.reporting import config_slug, compute_report_metrics
from studies.weekly_momentum.scripts.walk_forward import _parse_ints, _parse_market_filters


SUBPERIODS = {
    "2014_2019": ("2014-01-01", "2019-12-31"),
    "2014_2020": ("2014-01-01", "2020-12-31"),
    "2021_2026": ("2021-01-01", "2026-04-14"),
    "2022_2026": ("2022-01-01", "2026-04-14"),
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Weekly momentum structured sweep")
    parser.add_argument("--variation", choices=["stocks", "etfs"], default="stocks")
    parser.add_argument("--only-sp500", type=int, choices=[0, 1], default=1)
    parser.add_argument("--sp500-pit", action="store_true")
    parser.add_argument("--lookbacks", default="4,20,60,90,126")
    parser.add_argument("--top-ks", default="3,5,10,20")
    parser.add_argument("--market-filters", default="none,sma100,sma200,ema100,ema200")
    parser.add_argument("--allow-negative-momentum", default="0,1")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--storage-root", default="data/tiingo")
    parser.add_argument("--spy-path", default="data/tiingo/daily/prices/SPY.parquet")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-root", default="studies/weekly_momentum/sweeps")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    lookbacks = _parse_ints(args.lookbacks)
    top_ks = _parse_ints(args.top_ks)
    market_filters = _parse_market_filters(None, args.market_filters)
    allow_negative_values = [bool(v) for v in _parse_ints(args.allow_negative_momentum)]
    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.output_root) / args.variation / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

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
    spy_returns = spy.pct_change(fill_method=None).fillna(0.0)
    spy_equity = (1.0 + spy_returns).cumprod() * 10_000.0
    universe_provider = sp500_pit_universe_provider() if args.sp500_pit and args.variation == "stocks" and bool(args.only_sp500) else None

    configs = _build_configs(lookbacks, top_ks, market_filters, allow_negative_values)
    rows = []
    subperiod_rows = []
    rolling_rows = []
    for cfg in configs:
        slug = config_slug(cfg)
        result = simulate_weekly_momentum(
            prices,
            cfg,
            market_filter_prices=spy if cfg.market_filter_type != "none" else None,
            universe_by_date=universe_provider,
        )
        equity = result.equity.reindex(spy.index).dropna()
        returns = result.returns.reindex(equity.index).fillna(0.0)
        metrics = compute_report_metrics(equity, returns)
        roll = rolling_edge_metrics(equity, spy_equity.reindex(equity.index).dropna())
        row = {"config": slug, **asdict(cfg), **metrics, **roll}
        row["score"] = _score(row)
        rows.append(row)
        for name, (lo, hi) in SUBPERIODS.items():
            sub = returns.loc[lo:hi]
            sub_eq = (1.0 + sub).cumprod() * 10_000.0
            sm = compute_report_metrics(sub_eq, sub) if len(sub) > 20 else {}
            subperiod_rows.append({"config": slug, "subperiod": name, **sm})
        for years in (1, 3, 5, 10):
            rolling_rows.append({"config": slug, "window_years": years, **rolling_edge_metrics(equity, spy_equity.reindex(equity.index).dropna(), (years,))})

    metrics_df = pd.DataFrame(rows).sort_values("score", ascending=False)
    subperiod_df = pd.DataFrame(subperiod_rows)
    rolling_df = pd.DataFrame(rolling_rows)
    configs_payload = {config_slug(cfg): asdict(cfg) for cfg in configs}
    metrics_df.to_csv(out_dir / "metrics.csv", index=False)
    subperiod_df.to_csv(out_dir / "subperiod_metrics.csv", index=False)
    rolling_df.to_csv(out_dir / "rolling_window_metrics.csv", index=False)
    (out_dir / "configs.json").write_text(json.dumps(configs_payload, indent=2) + "\n", encoding="utf-8")
    write_report(out_dir / "sweep_report.md", args, metrics_df, subperiod_df)
    print(f"configs={len(configs)}")
    print(f"outputs={out_dir}")
    print(metrics_df.head(10)[["config", "score", "cagr", "mdd", "sharpe", "roll_1y_pct_beat_spy", "roll_3y_pct_beat_spy"]].to_string(index=False))
    return 0


def rolling_edge_metrics(
    strategy_equity: pd.Series,
    spy_equity: pd.Series,
    windows_years: tuple[int, ...] = (1, 3, 5, 10),
) -> dict[str, float]:
    aligned = pd.concat({"s": strategy_equity, "b": spy_equity}, axis=1).dropna()
    out: dict[str, float] = {}
    for years in windows_years:
        window = years * 252
        if len(aligned) <= window:
            out[f"roll_{years}y_pct_beat_spy"] = float("nan")
            out[f"roll_{years}y_median_edge"] = float("nan")
            out[f"roll_{years}y_worst_edge"] = float("nan")
            out[f"roll_{years}y_worst_cagr"] = float("nan")
            continue
        strat = (aligned["s"] / aligned["s"].shift(window)) ** (1.0 / years) - 1.0
        bench = (aligned["b"] / aligned["b"].shift(window)) ** (1.0 / years) - 1.0
        edge = (strat - bench).dropna()
        strat = strat.dropna()
        out[f"roll_{years}y_pct_beat_spy"] = float((edge > 0).mean())
        out[f"roll_{years}y_median_edge"] = float(edge.median())
        out[f"roll_{years}y_worst_edge"] = float(edge.min())
        out[f"roll_{years}y_worst_cagr"] = float(strat.min())
    return out


def write_report(
    out_path: Path,
    args: argparse.Namespace,
    metrics_df: pd.DataFrame,
    subperiod_df: pd.DataFrame,
) -> None:
    top = metrics_df.head(25).copy()
    show_cols = [
        "config", "score", "cagr", "mdd", "sharpe", "sortino", "calmar",
        "roll_1y_pct_beat_spy", "roll_3y_pct_beat_spy", "roll_5y_pct_beat_spy",
        "roll_1y_worst_edge", "roll_3y_worst_edge",
    ]
    lines = [
        f"# Weekly Momentum Sweep - {args.variation}",
        "",
        "## Setup",
        "",
        f"- Variation: `{args.variation}`.",
        f"- only_sp500: `{args.only_sp500}`.",
        f"- sp500_pit: `{args.sp500_pit}`.",
        f"- lookbacks: `{args.lookbacks}`.",
        f"- top_k: `{args.top_ks}`.",
        f"- market filters: `{args.market_filters}`.",
        f"- allow_negative_momentum: `{args.allow_negative_momentum}`.",
        "- Score: Sharpe + CAGR - |MDD| + rolling 1y/3y beat-rate and edge terms.",
        "",
        "## Top Configs",
        "",
        top[show_cols].to_markdown(index=False),
        "",
        "## Subperiod Metrics For Top 10",
        "",
        subperiod_df[subperiod_df["config"].isin(top["config"].head(10))].to_markdown(index=False),
        "",
        "## Caveats",
        "",
        "- Sweep is exploratory and must be followed by walk-forward/PBO/DSR/bootstrap.",
        "- Current S&P 500 universe remains survivorship-biased when `only_sp500=1`.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _score(row: dict) -> float:
    return float(
        row.get("sharpe", 0.0)
        + row.get("cagr", 0.0)
        - abs(row.get("mdd", 0.0))
        + 0.50 * _safe(row.get("roll_1y_pct_beat_spy"))
        + 0.75 * _safe(row.get("roll_3y_pct_beat_spy"))
        + 0.50 * _safe(row.get("roll_1y_median_edge"))
        + 0.75 * _safe(row.get("roll_3y_median_edge"))
        + 0.25 * _safe(row.get("roll_1y_worst_edge"))
    )


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


def _safe(value: object) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return 0.0
    return f if np.isfinite(f) else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
