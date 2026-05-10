#!/usr/bin/env python3
"""CLI runner for the weekly momentum study."""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from studies.weekly_momentum.core import WeeklyMomentumConfig, simulate_weekly_momentum
from studies.weekly_momentum.data import load_variation_prices
from studies.weekly_momentum.reporting import config_slug, write_run_outputs
from market_lab.backtest.metrics.standard_report import load_spy_series


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weekly momentum study")
    parser.add_argument("--variation", choices=["stocks", "etfs"], required=True)
    parser.add_argument("--lookback-days", type=int, default=4)
    parser.add_argument("--signal-weekday", type=int, default=3)
    parser.add_argument("--sell-delay-days", type=int, default=1)
    parser.add_argument("--settlement-delay-days", type=int, default=0)
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--allow-negative-momentum", type=int, choices=[0, 1], default=0)
    parser.add_argument("--no-positive-momentum-filter", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--defensive-asset", default=None, help="Optional defensive asset, e.g. ZROZ. Default is cash.")
    parser.add_argument("--market-filter-type", choices=["none", "sma", "ema"], default="none")
    parser.add_argument("--market-filter-days", type=int, default=None, help="Risk-on only when SPY is above this SMA/EMA window.")
    parser.add_argument("--market-filter-sma-days", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--only-sp500", type=int, choices=[0, 1], default=1)
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--storage-root", default="data/tiingo")
    parser.add_argument("--max-tickers", type=int, default=None)
    parser.add_argument("--output-root", default="studies/weekly_momentum/results")
    parser.add_argument("--spy-path", default="data/tiingo/daily/prices/SPY.parquet")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    prices = load_variation_prices(
        args.variation,
        storage_root=args.storage_root,
        start=start,
        end=end,
        min_bars=args.lookback_days + 2,
        max_tickers=args.max_tickers,
        only_sp500=bool(args.only_sp500),
    )
    if prices.empty:
        raise SystemExit("No prices loaded from Tiingo cache")

    market_filter_type = args.market_filter_type
    market_filter_days = args.market_filter_days
    if args.market_filter_sma_days is not None:
        market_filter_type = "sma"
        market_filter_days = args.market_filter_sma_days
    allow_negative = bool(args.allow_negative_momentum) or args.no_positive_momentum_filter
    config = WeeklyMomentumConfig(
        lookback_days=args.lookback_days,
        signal_weekday=args.signal_weekday,
        sell_delay_days=args.sell_delay_days,
        top_k=args.top_k,
        settlement_delay_days=args.settlement_delay_days,
        allow_negative_momentum=allow_negative,
        defensive_asset=args.defensive_asset.upper() if args.defensive_asset else None,
        market_filter_type=market_filter_type,
        market_filter_days=market_filter_days,
    )
    market_filter_prices = load_spy_series(args.spy_path) if market_filter_type != "none" else None
    result = simulate_weekly_momentum(prices, config, market_filter_prices=market_filter_prices)

    out_dir = Path(args.output_root) / args.variation / config_slug(config)
    payload = write_run_outputs(
        out_dir=out_dir,
        variation=args.variation,
        config=config,
        result=result,
        n_assets=prices.shape[1],
        universe_label=("sp500" if args.only_sp500 else "all_stocks") if args.variation == "stocks" else "all_etfs",
        spy_path=args.spy_path,
    )

    print(f"variation={args.variation}")
    print(f"n_assets={prices.shape[1]}")
    for key, value in payload["metrics"]["strategy"].items():
        if isinstance(value, str):
            print(f"{key}={value}")
            continue
        print(f"{key}={value:.6f}")
    print(f"outputs={out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
