#!/usr/bin/env python3
"""Phase 3.5a — Lead T1 screening.

Run canonical Bollinger MR (window=20, std=2.0) on all 12 FX/metal tickers
at 1h, longest available window (2020-01-01 → 2026-04-17), with Pepperstone-
calibrated costs. Output screening table + per-ticker metrics for IS / OOS /
forward-quarter splits and median hold ≤ 5 days check.

This is the SCREENING step for Lead T1. Assets showing PASS-looking metrics
(Sharpe_OOS ≥ 0.5, median_hold ≤ 5 days, forward_Sharpe > 0) advance to the
full 5-gate framework in a follow-up iteration.

Citations
---------
- Bollinger MR canonical (20, 2σ): [bollinger_on_bollinger_bands, p.51-58].
- Short-hold swap-kill threshold (≤5d hold): [systematic_trading, p.185-188].
- EWMA-GARCH vol sizing optional: [machine_trading, p.126-127, ch.4].
- 5-gate framework (pre-screen → gates): [advances_fin_ml, ch.7].
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("ai_trade.phase3_5a.t1")

# Pepperstone cost calibration per asset class (bps per side, conservative):
#   - FX majors: spread Razor ~0.4 bp + commission $3.5/side on $100k ~= 3.5 bp
#     -> half_spread ~ 2 bps; we bake commission inside half_spread as proxy.
#   - Metals (XAUUSD/XAGUSD): spread ~ 2-3 bps per side + commission ~ 3 bps
#     -> half_spread ~ 5 bps.
# Swap daily rate is symmetric-conservative at 5 bps/day (~1.8%/yr); real
# Pepperstone rates asymmetric, refined later if a candidate passes screen.
_HALF_SPREAD_BPS = {
    "forex": 2.0,
    "metal": 5.0,
}
_SWAP_RATE_PER_DAY = 0.00005  # 0.5 bp/day symmetric — conservative upper bound


TICKERS_FX = [
    "eurusd", "gbpusd", "usdjpy", "usdchf",
    "audusd", "usdcad", "nzdusd",
    "eurjpy", "eurgbp", "gbpjpy",
]
TICKERS_METAL = ["xauusd", "xagusd"]

PERIODS_PER_YEAR_1H = 252 * 7


@dataclass
class WindowMetrics:
    label: str
    start: str
    end: str
    n_bars: int
    sharpe: float
    cagr_pct: float
    max_dd_pct: float
    final_equity: float
    n_trades: int
    median_hold_days: float
    median_hold_bars: int


@dataclass
class TickerResult:
    ticker: str
    asset_class: str
    direction: str
    n_bars_full: int
    window_metrics: list[WindowMetrics]
    candidate: bool  # passes screen: OOS Sharpe >= 0.5, median_hold_days <= 5, fwd Sharpe > 0


def _annualized_sharpe(equity: pd.Series, periods_per_year: int) -> float:
    if len(equity) < 2:
        return 0.0
    r = equity.pct_change().dropna()
    if r.std(ddof=0) == 0 or len(r) < 2:
        return 0.0
    return float(np.sqrt(periods_per_year) * r.mean() / r.std(ddof=0))


def _max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min())


def _cagr(final: float, initial: float, years: float) -> float:
    if initial <= 0 or years <= 0 or final <= 0:
        return 0.0
    return (final / initial) ** (1.0 / years) - 1.0


def _median_hold(trades, data_index: pd.DatetimeIndex) -> tuple[float, int]:
    if not trades:
        return 0.0, 0
    holds_days = []
    holds_bars = []
    for t in trades:
        delta = (pd.Timestamp(t.exit_time) - pd.Timestamp(t.entry_time))
        holds_days.append(delta.total_seconds() / 86400.0)
        # Count bars between entry and exit.
        try:
            entry_idx = data_index.get_loc(pd.Timestamp(t.entry_time))
            exit_idx = data_index.get_loc(pd.Timestamp(t.exit_time))
            holds_bars.append(int(exit_idx - entry_idx))
        except KeyError:
            continue
    if not holds_days:
        return 0.0, 0
    return float(np.median(holds_days)), int(np.median(holds_bars) if holds_bars else 0)


def _run_backtest(
    ticker: str, data_full: dict, data_bounded: dict,
    exec_cfg, swap_model, direction: str, cash: float,
):
    from ai_trade.backtest.engine import (
        ExecutionSimulator, Runner,
    )
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    strategy = BollingerMRStrategy(
        data=data_full,
        symbol=ticker,
        window=20,
        std_mult=2.0,
        stop_pct=0.02,
        max_hold=24,
        risk_pct_of_equity=0.95,
        direction=direction,
        garch_lambda=0.0,
    )
    runner = Runner(
        executor=ExecutionSimulator(exec_cfg),
        swap_model=swap_model,
    )
    return runner.run(
        strategy=strategy, data=data_bounded, initial_cash=cash,
    )


def _metrics_for_window(
    label: str, start: pd.Timestamp, end: pd.Timestamp,
    data_full: dict, data_bounded_full: dict, ticker: str,
    exec_cfg, swap_model, direction: str, cash: float,
) -> WindowMetrics:
    df_full = data_bounded_full[ticker]
    mask = (df_full.index >= start) & (df_full.index <= end)
    df_win = df_full[mask]
    if df_win.empty:
        return WindowMetrics(label, str(start.date()), str(end.date()),
                             0, 0.0, 0.0, 0.0, cash, 0, 0.0, 0)

    # Use the full series for indicator warmup, bound the execution window.
    data_for_run = {ticker: data_full[ticker]}
    data_win = {ticker: df_win}
    bt = _run_backtest(ticker, data_for_run, data_win, exec_cfg, swap_model,
                        direction, cash)

    eq = bt.equity_curve
    sharpe = _annualized_sharpe(eq, PERIODS_PER_YEAR_1H)
    mdd = _max_drawdown(eq) if len(eq) > 1 else 0.0
    years = len(df_win) / PERIODS_PER_YEAR_1H
    cagr = _cagr(bt.final_equity, cash, years)

    med_days, med_bars = _median_hold(bt.trades, df_win.index)

    return WindowMetrics(
        label=label,
        start=str(start.date()),
        end=str(end.date()),
        n_bars=len(df_win),
        sharpe=round(sharpe, 3),
        cagr_pct=round(cagr * 100, 2),
        max_dd_pct=round(mdd * 100, 2),
        final_equity=round(bt.final_equity, 2),
        n_trades=len(bt.trades),
        median_hold_days=round(med_days, 2),
        median_hold_bars=med_bars,
    )


def _parse_args(argv=None):
    ap = argparse.ArgumentParser(description="T1 BollingerMR multi-asset screen.")
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--direction", default="both",
                    choices=["long", "short", "both"])
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--output-dir", type=Path,
                    default=Path("reports/phase3_5a/t1_bollinger_mr_fx_metals"))
    ap.add_argument("--warmup-days", type=int, default=0,
                    help="Pre-fetch buffer; Tiingo FX API rejects startDate "
                         "< 2020-01-01 so default=0. BollingerMR only needs "
                         "20 bars (~3 days on 1h) for warmup — the strategy "
                         "skips bars until the MA is valid.")
    ap.add_argument("--tickers", nargs="*", default=None,
                    help="Override default ticker list for smoke tests.")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine.execution import ExecutionConfig, SwapModel

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/grid.log", mode="a"),
        ],
    )

    args = _parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    tickers = args.tickers if args.tickers else TICKERS_FX + TICKERS_METAL
    asset_class_of = {t: ("metal" if t in TICKERS_METAL else "forex")
                      for t in tickers}

    # Use the LONGEST available window per manifest — hard rule.
    start_full = date(2020, 1, 1)
    end_full = date(2026, 4, 17)
    fetch_start = start_full - timedelta(days=args.warmup_days)

    # Splits (mutually exclusive):
    # IS:   2020-01-01 → 2023-12-31
    # OOS:  2024-01-01 → 2025-12-31
    # Fwd:  2026-01-01 → 2026-04-17 (forward-window stress)
    is_window = (pd.Timestamp("2020-01-01"), pd.Timestamp("2023-12-31"))
    oos_window = (pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-31"))
    fwd_window = (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-04-17"))
    full_window = (pd.Timestamp(start_full), pd.Timestamp(end_full))

    log.info("=== T1 BollingerMR multi-asset screen ===")
    log.info("Tickers: %d (%s)", len(tickers), tickers)
    log.info("Window full: %s → %s (IS, OOS, Fwd splits)",
             start_full, end_full)
    log.info("Pepperstone costs: FX half_spread=2bps, metal=5bps, "
             "swap=%.4f%%/day symmetric", _SWAP_RATE_PER_DAY * 100)

    src = TiingoSource(storage=TiingoStorage(root=args.storage_root))

    results: list[TickerResult] = []
    for ticker in tickers:
        ac_tiingo = "forex"  # metals under Tiingo FX umbrella
        log.info("\n--- %s (%s) ---", ticker, asset_class_of[ticker])
        raw = src.fetch_many(
            [ticker], fetch_start, end_full,
            asset_class=ac_tiingo, frequency="1hour",
        )
        if ticker not in raw or raw[ticker].empty:
            log.warning("No data for %s — skipping", ticker)
            continue

        data_full = {ticker: raw[ticker]}
        mask = (raw[ticker].index >= full_window[0]) & (
            raw[ticker].index <= full_window[1] + pd.Timedelta(days=1)
        )
        data_bounded = {ticker: raw[ticker][mask]}
        n_bars_full = len(data_bounded[ticker])
        log.info("Loaded %s: %d bars (%s → %s)",
                 ticker, n_bars_full, data_bounded[ticker].index[0],
                 data_bounded[ticker].index[-1])

        # Per-asset exec config (baked: spread + commission proxy).
        typical_price = float(raw[ticker]["close"].median())
        bps = _HALF_SPREAD_BPS[asset_class_of[ticker]]
        half_spread_price = typical_price * (bps / 10_000.0)
        exec_cfg = ExecutionConfig(
            half_spread=half_spread_price,
            slippage=0.0,
            commission_per_unit=0.0,
        )
        swap_model = SwapModel(
            long_rate_per_day=_SWAP_RATE_PER_DAY,
            short_rate_per_day=_SWAP_RATE_PER_DAY,
        )
        log.info("Exec: half_spread=%.6f (typical_price=%.4f, %.1f bps)",
                 half_spread_price, typical_price, bps)

        windows = []
        for lbl, (s, e) in [
            ("FULL", full_window),
            ("IS", is_window),
            ("OOS", oos_window),
            ("FWD", fwd_window),
        ]:
            try:
                wm = _metrics_for_window(
                    lbl, s, e, data_full, data_bounded, ticker,
                    exec_cfg, swap_model, args.direction, args.cash,
                )
            except Exception as exc:
                log.exception("Window %s %s failed: %s", ticker, lbl, exc)
                wm = WindowMetrics(lbl, str(s.date()), str(e.date()),
                                   0, 0.0, 0.0, 0.0, args.cash, 0, 0.0, 0)
            windows.append(wm)
            log.info("  [%s] sharpe=%.2f cagr=%.2f%% mdd=%.2f%% trades=%d "
                     "med_hold_d=%.2f",
                     wm.label, wm.sharpe, wm.cagr_pct, wm.max_dd_pct,
                     wm.n_trades, wm.median_hold_days)

        oos_m = next(w for w in windows if w.label == "OOS")
        fwd_m = next(w for w in windows if w.label == "FWD")
        candidate = (
            oos_m.sharpe >= 0.5
            and oos_m.median_hold_days <= 5.0
            and oos_m.median_hold_days > 0.0
            and fwd_m.sharpe > 0.0
        )
        results.append(TickerResult(
            ticker=ticker, asset_class=asset_class_of[ticker],
            direction=args.direction, n_bars_full=n_bars_full,
            window_metrics=windows, candidate=candidate,
        ))

    # Output: JSON + summary markdown table.
    summary_json = {
        "spec": "phase_3_5a/T1",
        "strategy": "BollingerMR canonical (window=20, std=2.0)",
        "direction": args.direction,
        "frequency": "1hour",
        "cost_model": {
            "half_spread_bps": _HALF_SPREAD_BPS,
            "swap_rate_per_day": _SWAP_RATE_PER_DAY,
        },
        "results": [
            {
                **{k: v for k, v in asdict(r).items() if k != "window_metrics"},
                "windows": [asdict(w) for w in r.window_metrics],
            }
            for r in results
        ],
    }
    json_path = args.output_dir / "summary.json"
    json_path.write_text(json.dumps(summary_json, indent=2))
    log.info("\nJSON summary: %s", json_path)

    # Markdown report.
    md = [
        "# Phase 3.5a — Lead T1: BollingerMR multi-asset screen",
        "",
        f"- Strategy: **BollingerMR canonical** window=20, std=2.0, max_hold=24, stop=2%",
        f"- Direction: **{args.direction}**",
        f"- Frequency: **1hour**",
        f"- Window full: **2020-01-01 → 2026-04-17**",
        f"- IS: 2020-01-01→2023-12-31 | OOS: 2024-01-01→2025-12-31 | Fwd: 2026-01-01→2026-04-17",
        f"- Costs: FX half_spread=2bps/side, metal=5bps/side, swap={_SWAP_RATE_PER_DAY*100:.4f}%/day sym.",
        "",
        "## Screening table (OOS window → candidate if Sharpe≥0.5 AND median_hold_days ≤ 5)",
        "",
        "| ticker | OOS Sharpe | OOS CAGR% | OOS MDD% | OOS trades | OOS med_hold_d | FWD Sharpe | candidate |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for r in results:
        oos = next(w for w in r.window_metrics if w.label == "OOS")
        fwd = next(w for w in r.window_metrics if w.label == "FWD")
        md.append(
            f"| {r.ticker} | {oos.sharpe:.2f} | {oos.cagr_pct:.2f} | "
            f"{oos.max_dd_pct:.2f} | {oos.n_trades} | {oos.median_hold_days:.2f} | "
            f"{fwd.sharpe:.2f} | {'YES' if r.candidate else 'no'} |"
        )
    md.append("")
    md.append("## Full IS/OOS/FWD breakdown")
    md.append("")
    for r in results:
        md.append(f"### {r.ticker} ({r.asset_class})")
        md.append("")
        md.append("| window | start | end | bars | Sharpe | CAGR% | MDD% | trades | med_hold_d | med_hold_bars |")
        md.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|")
        for w in r.window_metrics:
            md.append(
                f"| {w.label} | {w.start} | {w.end} | {w.n_bars} | "
                f"{w.sharpe:.2f} | {w.cagr_pct:.2f} | {w.max_dd_pct:.2f} | "
                f"{w.n_trades} | {w.median_hold_days:.2f} | {w.median_hold_bars} |"
            )
        md.append("")

    candidates = [r for r in results if r.candidate]
    md.append(f"**Candidates advancing to full 5-gate framework: {len(candidates)}**")
    if candidates:
        md.append("")
        for r in candidates:
            oos = next(w for w in r.window_metrics if w.label == "OOS")
            md.append(
                f"- `{r.ticker}` ({r.asset_class}) — OOS Sharpe {oos.sharpe:.2f}, "
                f"CAGR {oos.cagr_pct:.2f}%, median hold {oos.median_hold_days:.2f}d"
            )

    md_path = args.output_dir / "summary.md"
    md_path.write_text("\n".join(md) + "\n")
    log.info("Markdown summary: %s", md_path)
    log.info("Candidates: %d / %d", len(candidates), len(results))
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
