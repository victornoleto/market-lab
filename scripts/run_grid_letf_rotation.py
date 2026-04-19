#!/usr/bin/env python3
"""LETF rotation grid smoke-runner — Lead B1b-i.

Loads Tiingo SPY daily (and optionally GLD daily for gold-blend configs),
expands the smoke grid (16 configs by default), runs each config on the
IS / OOS / Stress splits, and writes a JSON report with per-cell
performance metrics.

Usage (default smoke grid, no gold)::

    .venv/bin/python scripts/run_grid_letf_rotation.py \\
        --storage-root data/tiingo \\
        --output reports/letf_rotation_grid_smoke.json

Full 360-config grid (Lead B1b-ii when SPX TR pre-2001 is plugged in)::

    .venv/bin/python scripts/run_grid_letf_rotation.py \\
        --full-grid --include-gold --storage-root data/tiingo \\
        --output reports/letf_rotation_grid_full_proxy.json

This script uses **SPY daily as an SPX TR proxy** because Tiingo cache
starts 2001-05-14. The canonical Gayed split IS 1970-2000 is therefore
unreachable here; this smoke run uses a **shifted split**:

* IS     = 2005-01-01 → 2013-12-31  (9 y — starts when GLD opens)
* OOS    = 2014-01-01 → 2019-12-31  (6 y)
* Stress = 2020-01-01 → 2026-04-14  (6+ y)

Lead B1b-ii will add a Shiller / Ken-French loader to restore the
1970-2000 IS block; the canonical split is then plugged in via the
same CLI. Citations:

* ``[leverage_for_the_long_run, p.13, Table 5]`` — split discipline.
* ``[advances_fin_ml, p.208-211]`` — split-leakage avoidance.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.grid.letf_rotation_grid import (
    GridAxes,
    SplitDef,
    build_grid,
    run_letf_rotation_grid,
)

log = logging.getLogger("ai_trade.grid.letf_rotation")


DEFAULT_SPLITS = (
    SplitDef("IS", "2005-01-03", "2013-12-31"),
    SplitDef("OOS", "2014-01-01", "2019-12-31"),
    SplitDef("Stress", "2020-01-01", "2026-04-14"),
)

FULL_AXES = GridAxes(
    filters=("SMA", "EMA"),
    lookbacks=(100, 125, 150, 200),
    bands=(0.0, 0.03, 0.05),
    leverages=(1.0, 2.0, 3.0),
    gold_weights=(0.0, 0.25, 0.50, 0.75, 1.0),
)

SMOKE_AXES = GridAxes()  # 16 configs, no gold.


def _load_daily(storage_root: Path, ticker: str) -> pd.DataFrame:
    p = storage_root / "daily" / "prices" / f"{ticker}.parquet"
    if not p.exists():
        raise FileNotFoundError(f"Tiingo daily parquet not found: {p}")
    df = pd.read_parquet(p)
    if "adj_close" not in df.columns:
        raise ValueError(f"{p} missing adj_close")
    return df.sort_index()


def _prices_returns(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    price = df["adj_close"].astype(float)
    ret = price.pct_change().fillna(0.0)
    return price, ret


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--spx-ticker", default="SPY")
    ap.add_argument("--gold-ticker", default="GLD")
    ap.add_argument("--full-grid", action="store_true",
                    help="Use the 360-config mandate grid instead of the "
                         "16-config smoke grid.")
    ap.add_argument("--include-gold", action="store_true",
                    help="Include gold_weight>0 configs. Requires GLD in "
                         "storage-root and the IS split starting after GLD's "
                         "inception (default IS=2005 satisfies this).")
    ap.add_argument("--output", type=Path,
                    default=Path("reports/letf_rotation_grid_smoke.json"))
    ap.add_argument("--progress", action="store_true")
    ap.add_argument("--annual-fee", type=float, default=0.01,
                    help="[leverage_for_the_long_run, p.16]")
    ap.add_argument("--commission-bps", type=float, default=10.0)
    ap.add_argument("--spread-bps", type=float, default=5.0)
    ap.add_argument("--tax-rate", type=float, default=0.15,
                    help="BR swing capital-gains tax. Investment Mandate §4.")
    ap.add_argument("--cash-rate-annual", type=float, default=0.0,
                    help="[leverage_for_the_long_run, p.21] cash, not BIL.")
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    spx_df = _load_daily(args.storage_root, args.spx_ticker)
    spx_price, spx_ret = _prices_returns(spx_df)

    gold_ret: pd.Series | None = None
    if args.include_gold:
        gold_df = _load_daily(args.storage_root, args.gold_ticker)
        _, gold_ret = _prices_returns(gold_df)
        gold_ret = gold_ret.reindex(spx_ret.index).fillna(0.0)
        log.info("loaded gold %s: %d bars", args.gold_ticker, len(gold_ret))

    log.info(
        "loaded %s: %d bars, %s → %s",
        args.spx_ticker, len(spx_ret),
        spx_ret.index[0].date(), spx_ret.index[-1].date(),
    )

    if args.full_grid:
        if args.include_gold:
            axes = FULL_AXES
        else:
            axes = GridAxes(
                filters=FULL_AXES.filters,
                lookbacks=FULL_AXES.lookbacks,
                bands=FULL_AXES.bands,
                leverages=FULL_AXES.leverages,
                gold_weights=(0.0,),
            )
    else:
        axes = SMOKE_AXES
        if args.include_gold:
            axes = GridAxes(
                filters=axes.filters,
                lookbacks=axes.lookbacks,
                bands=axes.bands,
                leverages=axes.leverages,
                gold_weights=(0.0, 0.5, 1.0),
            )

    log.info("grid: %d configs × %d splits = %d cells",
             axes.n_configs, len(DEFAULT_SPLITS),
             axes.n_configs * len(DEFAULT_SPLITS))

    configs = build_grid(
        axes,
        annual_fee=args.annual_fee,
        commission_bps=args.commission_bps,
        spread_bps=args.spread_bps,
        tax_rate=args.tax_rate,
        cash_rate_annual=args.cash_rate_annual,
    )

    trials = run_letf_rotation_grid(
        spx_returns=spx_ret,
        spx_prices=spx_price,
        splits=DEFAULT_SPLITS,
        configs=configs,
        gold_returns=gold_ret,
        progress=args.progress,
    )

    report = {
        "run": {
            "spx_ticker": args.spx_ticker,
            "gold_ticker": args.gold_ticker if args.include_gold else None,
            "n_configs": len(configs),
            "splits": [{"name": s.name, "start": s.start, "end": s.end}
                       for s in DEFAULT_SPLITS],
            "costs": {
                "annual_fee": args.annual_fee,
                "commission_bps": args.commission_bps,
                "spread_bps": args.spread_bps,
                "tax_rate": args.tax_rate,
                "cash_rate_annual": args.cash_rate_annual,
            },
            "spx_first_bar": str(spx_ret.index[0].date()),
            "spx_last_bar": str(spx_ret.index[-1].date()),
        },
        "trials": [t.to_dict() for t in trials],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, default=str))
    log.info("wrote %s (%d trials)", args.output, len(trials))

    _print_top_summary(trials, top_n=5)
    return 0


def _print_top_summary(trials: list, top_n: int = 5) -> None:
    rows = []
    for t in trials:
        oos = t.by_split("OOS")
        stress = t.by_split("Stress")
        is_m = t.by_split("IS")
        rows.append(
            {
                "filter": t.config.filter,
                "lookback": t.config.lookback,
                "band": t.config.band_pct,
                "lev": t.config.leverage,
                "gw": t.config.gold_weight,
                "IS_sharpe": is_m.sharpe if is_m else float("nan"),
                "OOS_sharpe": oos.sharpe if oos else float("nan"),
                "Stress_sharpe": stress.sharpe if stress else float("nan"),
                "OOS_cagr": oos.cagr if oos else float("nan"),
                "OOS_mdd": oos.max_drawdown if oos else float("nan"),
                "n_switch_OOS": oos.n_switches if oos else 0,
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return
    df_sorted = df.sort_values("OOS_sharpe", ascending=False).head(top_n)
    print("\nTop by OOS Sharpe:")
    print(df_sorted.to_string(index=False, float_format=lambda x: f"{x:.3f}"))


if __name__ == "__main__":
    sys.exit(main())
