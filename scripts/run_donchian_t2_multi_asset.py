#!/usr/bin/env python3
"""Phase 3.5a — Lead T2 screening (Donchian breakout, intraday).

Run two canonical Donchian configs (entry/exit = 20/10 and 10/5) on the
12 FX/metal tickers + SPY/QQQ at 1h, longest available window per
manifest, with Pepperstone-calibrated costs. Outputs per-ticker IS/OOS/
forward-quarter metrics and median-hold check (≤5 days, swap-kill
threshold).

Configs are 2 lookback combos × 3 directions × 14 tickers = 84 runs.
Candidates passing screen (OOS Sharpe ≥ 0.5 AND median_hold ≤ 5d AND
fwd Sharpe > 0) advance to the full 5-gate framework.

Citations
---------
- Donchian 20/10 entry/exit (Turtles canonical): [trading_systems_methods,
  p.353].
- Time-series momentum family: [algo_trading_chan, p.133, ch.6].
- ATR stop & time-stop: [machine_trading, p.126, ch.4].
- 5-gate framework: [advances_fin_ml, ch.7].
- Swap-kill ≤5d: [systematic_trading, p.185-188].
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict, field
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("ai_trade.phase3_5a.t2")

# Pepperstone cost calibration (same as T1 — comparable across screens).
_HALF_SPREAD_BPS = {
    "forex": 2.0,
    "metal": 5.0,
    "etf": 1.0,  # SPY/QQQ via Pepperstone CFD: ~0.5 bp spread + tiny commission
}
_SWAP_RATE_PER_DAY = 0.00005

TICKERS_FX = [
    "eurusd", "gbpusd", "usdjpy", "usdchf",
    "audusd", "usdcad", "nzdusd",
    "eurjpy", "eurgbp", "gbpjpy",
]
TICKERS_METAL = ["xauusd", "xagusd"]
TICKERS_ETF = ["SPY", "QQQ"]

# Bars/year baseline for Sharpe annualization.
PERIODS_PER_YEAR_1H_FX = 252 * 24  # FX trades 24/5 ~ 6048 bars/yr (approx)
PERIODS_PER_YEAR_1H_ETF = 252 * 7  # ETF 1h ~ 6.5h/day

# Donchian configs to test.
DONCHIAN_CONFIGS = [
    ("D10_5", 10, 5),
    ("D20_10", 20, 10),
]


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
    config_name: str
    entry_lookback: int
    exit_lookback: int
    direction: str
    n_bars_full: int
    window_metrics: list[WindowMetrics]
    candidate: bool


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
        delta = pd.Timestamp(t.exit_time) - pd.Timestamp(t.entry_time)
        holds_days.append(delta.total_seconds() / 86400.0)
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
    ticker, data_full, data_bounded, exec_cfg, swap_model,
    direction, entry_lb, exit_lb, cash,
):
    from ai_trade.backtest.engine import ExecutionSimulator, Runner
    from ai_trade.backtest.strategies.donchian_breakout import (
        DonchianBreakoutStrategy,
    )

    strategy = DonchianBreakoutStrategy(
        data=data_full, symbol=ticker,
        entry_lookback=entry_lb, exit_lookback=exit_lb,
        atr_lookback=14, atr_stop_mult=2.0,
        max_hold=120, risk_pct_of_equity=0.95,
        direction=direction,
    )
    runner = Runner(
        executor=ExecutionSimulator(exec_cfg),
        swap_model=swap_model,
    )
    return runner.run(strategy=strategy, data=data_bounded, initial_cash=cash)


def _metrics_for_window(
    label, start, end, data_full, data_bounded, ticker, asset_class,
    exec_cfg, swap_model, direction, entry_lb, exit_lb, cash,
) -> WindowMetrics:
    df_full = data_bounded[ticker]
    mask = (df_full.index >= start) & (df_full.index <= end)
    df_win = df_full[mask]
    if df_win.empty:
        return WindowMetrics(label, str(start.date()), str(end.date()),
                             0, 0.0, 0.0, 0.0, cash, 0, 0.0, 0)

    data_for_run = {ticker: data_full[ticker]}
    data_win = {ticker: df_win}
    bt = _run_backtest(
        ticker, data_for_run, data_win, exec_cfg, swap_model,
        direction, entry_lb, exit_lb, cash,
    )

    eq = bt.equity_curve
    ppy = (
        PERIODS_PER_YEAR_1H_ETF if asset_class == "etf"
        else PERIODS_PER_YEAR_1H_FX
    )
    sharpe = _annualized_sharpe(eq, ppy)
    mdd = _max_drawdown(eq) if len(eq) > 1 else 0.0
    years = len(df_win) / ppy
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
    ap = argparse.ArgumentParser(description="T2 Donchian breakout multi-asset screen.")
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--directions", nargs="*",
                    default=["long", "short", "both"])
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--output-dir", type=Path,
                    default=Path("reports/phase3_5a/t2_donchian_breakout"))
    ap.add_argument("--tickers", nargs="*", default=None,
                    help="Override default ticker list for smoke tests.")
    ap.add_argument("--configs", nargs="*", default=None,
                    help="Override config names (D10_5, D20_10).")
    return ap.parse_args(argv)


def _load_data(src, ticker, ac_tiingo, fetch_start, end_full, full_window):
    raw = src.fetch_many(
        [ticker], fetch_start, end_full,
        asset_class=ac_tiingo, frequency="1hour",
    )
    if ticker not in raw or raw[ticker].empty:
        return None, None, 0
    df = raw[ticker]
    mask = (df.index >= full_window[0]) & (
        df.index <= full_window[1] + pd.Timedelta(days=1)
    )
    bounded = {ticker: df[mask]}
    return {ticker: df}, bounded, len(bounded[ticker])


def _typical_half_spread(asset_class: str, df: pd.DataFrame) -> float:
    typical_price = float(df["close"].median())
    bps = _HALF_SPREAD_BPS[asset_class]
    return typical_price * (bps / 10_000.0)


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

    fx_metal_tickers = TICKERS_FX + TICKERS_METAL
    etf_tickers = TICKERS_ETF
    all_tickers = fx_metal_tickers + etf_tickers
    if args.tickers:
        all_tickers = args.tickers
        fx_metal_tickers = [t for t in all_tickers if t.lower() in fx_metal_tickers]
        etf_tickers = [t for t in all_tickers if t in TICKERS_ETF]

    asset_class_of = {}
    for t in all_tickers:
        if t in TICKERS_ETF:
            asset_class_of[t] = "etf"
        elif t in TICKERS_METAL:
            asset_class_of[t] = "metal"
        else:
            asset_class_of[t] = "forex"

    configs = DONCHIAN_CONFIGS
    if args.configs:
        configs = [c for c in DONCHIAN_CONFIGS if c[0] in args.configs]

    # Hard rule: longest available window per manifest. FX manifest 2020-01-01
    # → 2026-04-17. SPY/QQQ 1h overlapping window starts ~2019-08/2020-01.
    start_full = date(2020, 1, 6)  # latest of all 1h start dates
    end_full = date(2026, 4, 14)
    fetch_start = start_full

    is_window = (pd.Timestamp("2020-01-06"), pd.Timestamp("2023-12-31"))
    oos_window = (pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-31"))
    fwd_window = (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-04-14"))
    full_window = (pd.Timestamp(start_full), pd.Timestamp(end_full))

    log.info("=== T2 Donchian breakout multi-asset screen ===")
    log.info("Tickers: %d (%s)", len(all_tickers), all_tickers)
    log.info("Configs: %s", [c[0] for c in configs])
    log.info("Directions: %s", args.directions)
    log.info("Window: %s → %s | IS %s | OOS %s | Fwd %s",
             start_full, end_full, is_window, oos_window, fwd_window)

    src = TiingoSource(storage=TiingoStorage(root=args.storage_root))

    # Cache loaded data (avoid re-fetch per config × direction).
    loaded: dict[str, tuple] = {}
    for ticker in all_tickers:
        ac = asset_class_of[ticker]
        ac_tiingo = "etf" if ac == "etf" else "forex"
        log.info("--- loading %s (%s) ---", ticker, ac)
        full, bounded, n = _load_data(src, ticker, ac_tiingo, fetch_start,
                                       end_full, full_window)
        if full is None:
            log.warning("No data for %s — skipping", ticker)
            continue
        log.info("Loaded %s: %d bars (%s → %s)",
                 ticker, n, bounded[ticker].index[0], bounded[ticker].index[-1])
        half_spread = _typical_half_spread(ac, bounded[ticker])
        exec_cfg = ExecutionConfig(half_spread=half_spread, slippage=0.0,
                                   commission_per_unit=0.0)
        swap_model = SwapModel(long_rate_per_day=_SWAP_RATE_PER_DAY,
                               short_rate_per_day=_SWAP_RATE_PER_DAY)
        loaded[ticker] = (full, bounded, n, exec_cfg, swap_model, ac)

    results: list[TickerResult] = []
    for cfg_name, entry_lb, exit_lb in configs:
        for direction in args.directions:
            for ticker, (full, bounded, n, exec_cfg, swap_model, ac) in loaded.items():
                log.info("\n--- %s | %s | %s ---", ticker, cfg_name, direction)
                windows = []
                for lbl, (s, e) in [
                    ("FULL", full_window),
                    ("IS", is_window),
                    ("OOS", oos_window),
                    ("FWD", fwd_window),
                ]:
                    try:
                        wm = _metrics_for_window(
                            lbl, s, e, full, bounded, ticker, ac,
                            exec_cfg, swap_model, direction,
                            entry_lb, exit_lb, args.cash,
                        )
                    except Exception as exc:
                        log.exception("Window %s %s/%s failed: %s",
                                      ticker, cfg_name, lbl, exc)
                        wm = WindowMetrics(lbl, str(s.date()), str(e.date()),
                                           0, 0.0, 0.0, 0.0, args.cash,
                                           0, 0.0, 0)
                    windows.append(wm)
                    log.info("  [%s] sharpe=%.2f cagr=%.2f%% mdd=%.2f%% "
                             "trades=%d med_hold_d=%.2f",
                             wm.label, wm.sharpe, wm.cagr_pct, wm.max_dd_pct,
                             wm.n_trades, wm.median_hold_days)

                oos_m = next(w for w in windows if w.label == "OOS")
                fwd_m = next(w for w in windows if w.label == "FWD")
                candidate = (
                    oos_m.sharpe >= 0.5
                    and 0.0 < oos_m.median_hold_days <= 5.0
                    and fwd_m.sharpe > 0.0
                )
                results.append(TickerResult(
                    ticker=ticker, asset_class=ac,
                    config_name=cfg_name, entry_lookback=entry_lb,
                    exit_lookback=exit_lb, direction=direction,
                    n_bars_full=n, window_metrics=windows,
                    candidate=candidate,
                ))

    summary_json = {
        "spec": "phase_3_5a/T2",
        "strategy": "Donchian breakout (entry/exit channels) + ATR stop + time-stop",
        "configs": [{"name": c[0], "entry_lb": c[1], "exit_lb": c[2]}
                    for c in configs],
        "directions": args.directions,
        "frequency": "1hour",
        "cost_model": {
            "half_spread_bps": _HALF_SPREAD_BPS,
            "swap_rate_per_day": _SWAP_RATE_PER_DAY,
        },
        "n_runs": len(results),
        "results": [
            {**{k: v for k, v in asdict(r).items() if k != "window_metrics"},
             "windows": [asdict(w) for w in r.window_metrics]}
            for r in results
        ],
    }
    json_path = args.output_dir / "summary.json"
    json_path.write_text(json.dumps(summary_json, indent=2))
    log.info("\nJSON summary: %s", json_path)

    md = [
        "# Phase 3.5a — Lead T2: Donchian breakout multi-asset screen",
        "",
        f"- Configs: **D10/5** (entry=10, exit=5), **D20/10** (entry=20, exit=10)",
        f"- ATR stop: 2.0×ATR(14), time-stop: 120 bars (~5d FX 1h, ~17d ETF 1h)",
        f"- Directions: **{', '.join(args.directions)}**",
        f"- Frequency: **1hour**, Window: **{start_full} → {end_full}**",
        f"- IS: {is_window[0].date()}→{is_window[1].date()} | "
        f"OOS: {oos_window[0].date()}→{oos_window[1].date()} | "
        f"Fwd: {fwd_window[0].date()}→{fwd_window[1].date()}",
        f"- Costs: FX half_spread=2bps/side, metal=5bps/side, etf=1bps/side, "
        f"swap={_SWAP_RATE_PER_DAY*100:.4f}%/day sym.",
        f"- Total runs: **{len(results)}**",
        "",
        "## Screening table — OOS gate (Sharpe≥0.5 AND 0<med_hold_d≤5 AND Fwd Sharpe>0)",
        "",
        "| ticker | config | dir | OOS Sharpe | OOS CAGR% | OOS MDD% | OOS trades | OOS med_hold_d | FWD Sharpe | candidate |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for r in sorted(results, key=lambda r: -next(
            w for w in r.window_metrics if w.label == "OOS").sharpe):
        oos = next(w for w in r.window_metrics if w.label == "OOS")
        fwd = next(w for w in r.window_metrics if w.label == "FWD")
        md.append(
            f"| {r.ticker} | {r.config_name} | {r.direction} | "
            f"{oos.sharpe:.2f} | {oos.cagr_pct:.2f} | {oos.max_dd_pct:.2f} | "
            f"{oos.n_trades} | {oos.median_hold_days:.2f} | "
            f"{fwd.sharpe:.2f} | {'YES' if r.candidate else 'no'} |"
        )

    candidates = [r for r in results if r.candidate]
    md.append("")
    md.append(f"**Candidates advancing to full 5-gate: {len(candidates)} / {len(results)}**")
    if candidates:
        md.append("")
        for r in candidates:
            oos = next(w for w in r.window_metrics if w.label == "OOS")
            md.append(
                f"- `{r.ticker}` ({r.asset_class}) {r.config_name} "
                f"{r.direction} — OOS Sharpe {oos.sharpe:.2f}, "
                f"CAGR {oos.cagr_pct:.2f}%, MDD {oos.max_dd_pct:.2f}%, "
                f"med_hold {oos.median_hold_days:.2f}d"
            )

    md_path = args.output_dir / "summary.md"
    md_path.write_text("\n".join(md) + "\n")
    log.info("Markdown summary: %s", md_path)
    log.info("Candidates: %d / %d", len(candidates), len(results))
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
