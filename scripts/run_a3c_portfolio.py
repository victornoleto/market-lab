#!/usr/bin/env python3
"""Phase 3 Lead A3c — 2-strategy Path B portfolio evaluation.

Combines the two Phase 3 PASS winners of Path B into a blended daily
return stream and tests whether the portfolio beats the best single
leg on the COMMON window:

* **Leg 1 — LETF rotation EMA100 band=0% lev=2x** (Lead B1c winner, iter
  32). Simulated on stitched SPX TR 1970-2026, then sliced to the
  common window.
* **Leg 2 — QQQ Donchian 20/10** (Lead A3b winner, iter 36). Simulated
  on Tiingo QQQ daily 2001-05-14 → 2026-04-14.

Common window: ``2001-05-14 → 2026-04-14`` (limited by QQQ Tiingo start).

Splits (IS 60% / OOS 25% / Stress 15%, mutually exclusive):
same convention as Lead A3b.

Gates per mandate:

* Portfolio OOS Sharpe **>** max(leg OOS Sharpe) on the common-window
  OOS split — primary gate.
* Diversification Ratio **>** 1.2 per HRP/IVP framework
  ``[advances_fin_ml, p.302-313, ch.16]``.
* Supporting: DSR p<0.05, WF ≥6/8, OOS>0, Stress>0, bootstrap 99.9%
  CI lower bound >0.

Writes ``reports/a3c_portfolio_verdict.json`` and prints a summary.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.grid.portfolio_combiner import evaluate_a3c_gates
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    simulate_letf_rotation,
)
from ai_trade.backtest.strategies.tsmom import TSMOMConfig, simulate_tsmom

log = logging.getLogger("a3c")


# Phase 3 Lead B1c winner (iter 32).
LETF_WINNER_CONFIG = LETFRotationConfig(
    filter="EMA",
    lookback=100,
    band_pct=0.0,
    leverage=2.0,
    gold_weight=0.0,
)

# Phase 3 Lead A3b winner (iter 36).
QQQ_TSMOM_WINNER_CONFIG = TSMOMConfig(entry_lookback=20, exit_lookback=10)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--qqq-ticker", default="QQQ")
    ap.add_argument("--storage-root", default="data/tiingo")
    ap.add_argument(
        "--spx-start", default="1970-01-02",
        help="Start of SPX TR simulation (for MA warmup).",
    )
    ap.add_argument("--spx-end", default="2026-04-14")
    ap.add_argument(
        "--cutoff", default="2001-05-14",
        help="KF→Tiingo seam for SPX TR stitching.",
    )
    ap.add_argument(
        "--output", type=Path,
        default=Path("reports/a3c_portfolio_verdict.json"),
    )
    ap.add_argument("--bootstrap-n-resamples", type=int, default=2000)
    ap.add_argument("--rolling-lookback", type=int, default=63)
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _build_tr_price(returns: pd.Series) -> pd.Series:
    price = (1.0 + returns).cumprod() * 100.0
    price.name = "spx_tr_price"
    return price


def _load_qqq_ohlc(storage_root: str, ticker: str) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return adjusted (close, high, low) for the Tiingo daily QQQ series."""
    storage = TiingoStorage(root=Path(storage_root))
    df = storage.read(ticker, frequency="daily")
    if df.empty:
        raise ValueError(f"{ticker}: empty daily frame")

    raw_close = df["close"].astype(float)
    adj_close = (
        df["adj_close"].astype(float)
        if "adj_close" in df.columns
        else raw_close
    )
    scale = (adj_close / raw_close).replace([pd.NA, pd.NaT], 1.0).fillna(1.0)
    close = adj_close.dropna()
    high = (df["high"].astype(float) * scale).loc[close.index].dropna()
    low = (df["low"].astype(float) * scale).loc[close.index].dropna()
    common = close.index.intersection(high.index).intersection(low.index)
    return close.loc[common], high.loc[common], low.loc[common]


def _splits_for_window(
    start: pd.Timestamp, end: pd.Timestamp
) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
    """IS 60% / OOS 25% / Stress 15% — matches A3b convention."""
    total = (end - start).days
    is_end = start + pd.Timedelta(days=int(total * 0.60))
    oos_end = start + pd.Timedelta(days=int(total * 0.85))
    fmt = "%Y-%m-%d"
    return (
        (start.strftime(fmt), is_end.strftime(fmt)),
        (
            (is_end + pd.Timedelta(days=1)).strftime(fmt),
            oos_end.strftime(fmt),
        ),
        (
            (oos_end + pd.Timedelta(days=1)).strftime(fmt),
            end.strftime(fmt),
        ),
    )


def _print_summary(verdict, args) -> None:
    print("\n=== A3c portfolio verdict ===")
    print(f"baseline OOS Sharpe = {verdict.baseline_sharpe_oos:.3f}"
          f"  (leg: {verdict.baseline_leg_name})")
    for leg, m in verdict.leg_metrics.items():
        print(f"  leg {leg}: IS Sh={m['is']['sharpe']:.3f}  "
              f"OOS Sh={m['oos']['sharpe']:.3f}  "
              f"Str Sh={m['stress']['sharpe']:.3f}  "
              f"CAGR(oos)={m['oos']['cagr']:.3%}")

    print("\n--- blends ---")
    for e in verdict.blends:
        w = e.weights
        w_str = (
            f"({w[0]:.3f},{w[1]:.3f})"
            if isinstance(w, tuple)
            else str(w)
        )
        print(
            f"  {e.name:<14} w={w_str:<20}  "
            f"IS={e.is_metrics.sharpe:.3f}  "
            f"OOS={e.oos_metrics.sharpe:.3f}  "
            f"Str={e.stress_metrics.sharpe:.3f}  "
            f"CAGR(oos)={e.oos_metrics.cagr:.3%}  "
            f"DR={e.diversification_ratio_full:.3f}  "
            f"ρ={e.pearson_full:.3f}  "
            f"DSR_p={e.dsr_p_value:.4f}  "
            f"WF={e.wf_profitable_ratio:.2f}  "
            f"MDD(oos)={e.oos_metrics.max_drawdown:.2%}  "
            f"verdict={e.verdict}"
        )
        if e.failed_gates:
            print(f"      failed: {', '.join(e.failed_gates)}")
        if e.bootstrap_sharpe_lo is not None:
            print(
                f"      boot99.9% CI OOS Sharpe = "
                f"[{e.bootstrap_sharpe_lo:.3f}, {e.bootstrap_sharpe_hi:.3f}]"
            )

    print("\nwinner:", verdict.winner_blend if verdict.winner_blend else "(none)")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # --- Leg 1: LETF rotation EMA100/0%/2x on stitched SPX TR ---
    log.info("loading SPX TR %s → %s (cutoff %s)", args.spx_start, args.spx_end, args.cutoff)
    spx_returns = load_spx_tr_daily(
        start=args.spx_start,
        end=args.spx_end,
        cutoff_date=pd.Timestamp(args.cutoff),
    )
    spx_prices = _build_tr_price(spx_returns)
    log.info("SPX TR %d bars", len(spx_returns))
    log.info("simulating LETF rotation (EMA100 band=0 lev=2x gw=0)")
    letf_result = simulate_letf_rotation(
        spx_returns, spx_prices, LETF_WINNER_CONFIG
    )

    # --- Leg 2: QQQ Donchian 20/10 ---
    log.info("loading Tiingo daily %s", args.qqq_ticker)
    close, high, low = _load_qqq_ohlc(args.storage_root, args.qqq_ticker)
    log.info("QQQ %d bars  %s → %s", len(close), close.index[0].date(), close.index[-1].date())
    qqq_result = simulate_tsmom(high, low, close, QQQ_TSMOM_WINNER_CONFIG)

    # Align common window.
    letf_daily = letf_result.daily_returns.dropna()
    qqq_daily = qqq_result.daily_returns.dropna()
    common = letf_daily.index.intersection(qqq_daily.index)
    if common.empty:
        raise RuntimeError("no overlapping dates between LETF and QQQ series")
    common_start = common.min()
    common_end = common.max()
    log.info(
        "common window: %s → %s  (%d overlapping bars)",
        common_start.date(), common_end.date(), len(common),
    )

    is_range, oos_range, stress_range = _splits_for_window(common_start, common_end)
    log.info("splits  IS=%s  OOS=%s  STRESS=%s", is_range, oos_range, stress_range)

    # --- Gate battery ---
    verdict = evaluate_a3c_gates(
        letf_daily,
        qqq_daily,
        leg_names=("LETF_EMA100_2x", "QQQ_Donchian_20_10"),
        is_range=is_range,
        oos_range=oos_range,
        stress_range=stress_range,
        bootstrap_n_resamples=args.bootstrap_n_resamples,
        rolling_lookback=args.rolling_lookback,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "run": {
            "common_start": common_start.strftime("%Y-%m-%d"),
            "common_end": common_end.strftime("%Y-%m-%d"),
            "common_bars": int(len(common)),
            "splits": {
                "IS": {"start": is_range[0], "end": is_range[1]},
                "OOS": {"start": oos_range[0], "end": oos_range[1]},
                "Stress": {"start": stress_range[0], "end": stress_range[1]},
            },
            "leg_configs": {
                "LETF_EMA100_2x": {
                    "filter": LETF_WINNER_CONFIG.filter,
                    "lookback": LETF_WINNER_CONFIG.lookback,
                    "band_pct": LETF_WINNER_CONFIG.band_pct,
                    "leverage": LETF_WINNER_CONFIG.leverage,
                    "gold_weight": LETF_WINNER_CONFIG.gold_weight,
                    "annual_fee": LETF_WINNER_CONFIG.annual_fee,
                    "commission_bps": LETF_WINNER_CONFIG.commission_bps,
                    "spread_bps": LETF_WINNER_CONFIG.spread_bps,
                    "tax_rate": LETF_WINNER_CONFIG.tax_rate,
                },
                "QQQ_Donchian_20_10": {
                    "entry_lookback": QQQ_TSMOM_WINNER_CONFIG.entry_lookback,
                    "exit_lookback": QQQ_TSMOM_WINNER_CONFIG.exit_lookback,
                    "commission_bps": QQQ_TSMOM_WINNER_CONFIG.commission_bps,
                    "spread_bps": QQQ_TSMOM_WINNER_CONFIG.spread_bps,
                    "tax_rate": QQQ_TSMOM_WINNER_CONFIG.tax_rate,
                },
            },
            "bootstrap_n_resamples": args.bootstrap_n_resamples,
            "rolling_lookback": args.rolling_lookback,
        },
        "verdict": verdict.to_dict(),
    }
    args.output.write_text(json.dumps(report, indent=2, default=str))
    log.info("wrote %s", args.output)

    _print_summary(verdict, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
