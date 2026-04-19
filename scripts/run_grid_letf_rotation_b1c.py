#!/usr/bin/env python3
"""LETF rotation Phase 3 Lead B1c — canonical grid + gates + verdict.

Runs the full no-gold Phase 3 grid (2×4×3×3×1 = 72 configs) on the
stitched SPX TR series 1970-01-02 → 2026-04-14 and evaluates the
investment-mandate gates:

* PBO (CSCV) < 0.5
* DSR p-value < 0.05 (per config, n_trials = 72)
* Walk-forward ≥ 6/8 profitable windows, MaxDD ≤ 25% in every window
* OOS Sharpe > 0 on 2001-01-01 → 2015-12-31
* Stress Sharpe > 0 on 2016-01-01 → 2026-04-14
* Stationary-bootstrap 99.9% CI lower bound > 0 on OOS Sharpe
  (``alpha=0.001`` per mandate §4)

Citations
---------

* Split discipline and PBO < 0.5:
  ``[advances_fin_ml, p.208-211]``.
* Canonical Gayed splits and LRS parameters:
  ``[leverage_for_the_long_run, p.13, p.14, p.17, Table 5-6]``.
* Stationary block bootstrap (Politis-Romano 1994):
  ``[advances_fin_ml, p.196-202]``.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.grid.letf_rotation_b1c import (
    B1cGateVerdict,
    evaluate_b1c_gates,
)
from ai_trade.backtest.grid.letf_rotation_grid import GridAxes, build_grid
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    RotationResult,
    simulate_letf_rotation,
)

log = logging.getLogger("ai_trade.grid.letf_rotation.b1c")


CANONICAL_IS = ("1970-01-02", "2000-12-31")
CANONICAL_OOS = ("2001-01-01", "2015-12-31")
CANONICAL_STRESS = ("2016-01-01", "2026-04-14")


# Full 72-config grid (no gold — pre-2004 gold series not yet plugged in).
# Gold axis collapses to {0.0}, collapsing 360 → 72 configs.
PHASE3_AXES = GridAxes(
    filters=("SMA", "EMA"),
    lookbacks=(100, 125, 150, 200),
    bands=(0.0, 0.03, 0.05),
    leverages=(1.0, 2.0, 3.0),
    gold_weights=(0.0,),
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--start", default="1970-01-02",
        help="Start date of the backtest window (default: canonical IS start).",
    )
    ap.add_argument(
        "--end", default="2026-04-14",
        help="End date of the backtest window (default: current stress end).",
    )
    ap.add_argument(
        "--output", type=Path,
        default=Path("reports/letf_rotation_b1c_verdict.json"),
    )
    ap.add_argument("--annual-fee", type=float, default=0.01)
    ap.add_argument("--commission-bps", type=float, default=10.0)
    ap.add_argument("--spread-bps", type=float, default=5.0)
    ap.add_argument("--tax-rate", type=float, default=0.15)
    ap.add_argument("--cash-rate-annual", type=float, default=0.0)
    ap.add_argument("--bootstrap-n-resamples", type=int, default=2000)
    ap.add_argument("--bootstrap-alpha", type=float, default=0.001)
    ap.add_argument("--bootstrap-block-mean", type=int, default=5)
    ap.add_argument(
        "--smoke", action="store_true",
        help="Run with the smoke 16-config grid instead of the full 72.",
    )
    ap.add_argument(
        "--cutoff", default="2001-05-14",
        help="KF→Tiingo seam cutoff (default: manifest first SPY bar).",
    )
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _build_tr_price_series(returns: pd.Series) -> pd.Series:
    """TR-aware price index from daily returns (Gayed p.8 convention)."""
    price = (1.0 + returns).cumprod() * 100.0
    price.name = "spx_tr_price"
    return price


def _run_full_period_grid(
    spx_returns: pd.Series,
    spx_prices: pd.Series,
    configs: list[LETFRotationConfig],
) -> list[RotationResult]:
    results: list[RotationResult] = []
    for i, cfg in enumerate(configs, 1):
        log.info(
            "[%d/%d] simulating %s lb=%d band=%.2f lev=%.1f gw=%.2f",
            i, len(configs), cfg.filter, cfg.lookback, cfg.band_pct,
            cfg.leverage, cfg.gold_weight,
        )
        result = simulate_letf_rotation(spx_returns, spx_prices, cfg)
        results.append(result)
    return results


def _print_summary(verdict: B1cGateVerdict, top_n: int = 10) -> None:
    rows = []
    for e in verdict.evaluations:
        c = e.config
        rows.append({
            "cid": e.config_id,
            "filter": c.filter,
            "lb": c.lookback,
            "band": c.band_pct,
            "lev": c.leverage,
            "IS_sh": e.is_metrics.sharpe,
            "OOS_sh": e.oos_metrics.sharpe,
            "Str_sh": e.stress_metrics.sharpe,
            "OOS_cagr": e.oos_metrics.cagr,
            "OOS_mdd": e.oos_metrics.max_drawdown,
            "WF%": e.wf_profitable_ratio,
            "WF_mxdd": e.wf_max_window_drawdown,
            "DSR_p": e.dsr_p_value,
            "bs_lo": e.bootstrap_sharpe_lo,
            "verdict": e.verdict,
        })
    df = pd.DataFrame(rows)
    df_sorted = df.sort_values("OOS_sh", ascending=False).head(top_n)
    print(f"\n=== B1c verdict — PBO = {verdict.pbo_value:.3f} "
          f"(pass={verdict.pbo_pass}); passing configs: "
          f"{verdict.n_passing_configs} / {verdict.n_configs} ===")
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(df_sorted.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    if verdict.winner_config_id is not None:
        w = verdict.evaluations[verdict.winner_config_id]
        wc = w.config
        print(f"\nWINNER: cid={w.config_id} {wc.filter}{wc.lookback} "
              f"band={wc.band_pct:.2%} lev={wc.leverage}x "
              f"| IS={w.is_metrics.sharpe:.3f} OOS={w.oos_metrics.sharpe:.3f} "
              f"Stress={w.stress_metrics.sharpe:.3f} "
              f"| bootstrap 99.9% CI OOS Sharpe "
              f"[{w.bootstrap_sharpe_lo:.3f}, {w.bootstrap_sharpe_hi:.3f}]")
    else:
        print("\nNO WINNER — all configs failed one or more gates.")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    cutoff = pd.Timestamp(args.cutoff)
    spx_returns = load_spx_tr_daily(
        start=args.start,
        end=args.end,
        cutoff_date=cutoff,
    )
    spx_prices = _build_tr_price_series(spx_returns)
    log.info(
        "SPX TR loaded: %d bars %s → %s",
        len(spx_returns),
        spx_returns.index[0].date(), spx_returns.index[-1].date(),
    )

    axes = GridAxes() if args.smoke else PHASE3_AXES
    log.info(
        "grid axes: filters=%s lookbacks=%s bands=%s levs=%s gw=%s "
        "(%d configs)",
        axes.filters, axes.lookbacks, axes.bands, axes.leverages,
        axes.gold_weights, axes.n_configs,
    )
    configs = build_grid(
        axes,
        annual_fee=args.annual_fee,
        commission_bps=args.commission_bps,
        spread_bps=args.spread_bps,
        tax_rate=args.tax_rate,
        cash_rate_annual=args.cash_rate_annual,
    )

    results = _run_full_period_grid(spx_returns, spx_prices, configs)

    verdict = evaluate_b1c_gates(
        configs,
        results,
        is_range=CANONICAL_IS,
        oos_range=CANONICAL_OOS,
        stress_range=CANONICAL_STRESS,
        bootstrap_n_resamples=args.bootstrap_n_resamples,
        bootstrap_alpha=args.bootstrap_alpha,
        bootstrap_block_mean=args.bootstrap_block_mean,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "run": {
            "start": args.start,
            "end": args.end,
            "cutoff_date": args.cutoff,
            "n_configs": len(configs),
            "n_bars": int(len(spx_returns)),
            "splits": {
                "IS": {"start": CANONICAL_IS[0], "end": CANONICAL_IS[1]},
                "OOS": {"start": CANONICAL_OOS[0], "end": CANONICAL_OOS[1]},
                "Stress": {"start": CANONICAL_STRESS[0], "end": CANONICAL_STRESS[1]},
            },
            "costs": {
                "annual_fee": args.annual_fee,
                "commission_bps": args.commission_bps,
                "spread_bps": args.spread_bps,
                "tax_rate": args.tax_rate,
                "cash_rate_annual": args.cash_rate_annual,
            },
            "bootstrap": {
                "n_resamples": args.bootstrap_n_resamples,
                "alpha": args.bootstrap_alpha,
                "block_mean": args.bootstrap_block_mean,
            },
        },
        "verdict": verdict.to_dict(),
    }
    args.output.write_text(json.dumps(report, indent=2, default=str))
    log.info("wrote %s", args.output)

    _print_summary(verdict, top_n=10)
    return 0


if __name__ == "__main__":
    sys.exit(main())
