#!/usr/bin/env python3
"""Phase 3.5b — produce standard reports for the 3 Phase 3 winners + portfolio.

Runs the canonical winner configs end-to-end on the LONGEST available
windows (per CLAUDE.md hard rule: always use manifest ``first_dt`` →
``last_dt``). For each of {LETF rotation EMA100/2x, QQQ Donchian 20/10,
GLD Donchian 40/20} and for the equal-weight 3-leg portfolio blend,
emit four artefacts:

* ``trade_log.csv`` — per-trade round-trips with 15% BR tax on winners.
* ``trade_log.md`` — same data as a Markdown table.
* ``standard_report.md`` — ``backtesting.py``-style metrics block + SPY
  benchmark + Strategy-vs-SPY comparison.
* ``summary.json`` — machine-readable snapshot of the metrics.

Output root: ``reports/phase3_5b/<strategy>/``.

Usage
-----
::

    .venv/bin/python scripts/validate_phase3_winners.py \
        --output-dir reports/phase3_5b --initial-capital 100000

Phase 3.5b Task 2 — scaffold + wiring. Tasks 3-6 consume these artefacts
for the per-strategy/portfolio jornada writeups.

Citations
---------
* LETF winner (EMA100/band 0/leverage 2x): Phase 3 iter 32 jornada
  ``2026-04-17-0055-b1c-letf-rotation-gates-PASS.md``.
* QQQ winner (Donchian 20/10): Phase 3 iter 36 jornada
  ``2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md``.
* 3-leg portfolio winner: Phase 3 iter 37 jornada
  ``2026-04-17-0040-a3d-3leg-letf-qqq-gld-PASS.md``.
* SPY benchmark mandatory: ``specs/phase_3_5b_winners_validation.md`` §4.5.
* Path B 15% tax per profitable trade: Investment Mandate §4.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.grid.portfolio_3leg import (
    aggregate_leg_trades,
    blend_equal_weight_3,
)
from ai_trade.backtest.metrics.standard_report import (
    StandardReport,
    Trade,
    build_spy_benchmark,
    build_standard_report,
    compare_vs_spy,
    load_spy_series,
    render_markdown,
    render_trade_log,
)
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    get_trades as letf_get_trades,
    simulate_letf_rotation,
)
from ai_trade.backtest.strategies.tsmom import (
    TSMOMConfig,
    get_trades as tsmom_get_trades,
    simulate_tsmom,
)

log = logging.getLogger("phase3_5b.validate")

# --- Winner configs (Phase 3 frozen) ---------------------------------------

LETF_WINNER_CFG = LETFRotationConfig(
    filter="EMA",
    lookback=100,
    band_pct=0.0,
    leverage=2.0,
    gold_weight=0.0,
)
QQQ_WINNER_CFG = TSMOMConfig(entry_lookback=20, exit_lookback=10)
GLD_WINNER_CFG = TSMOMConfig(entry_lookback=40, exit_lookback=20)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/phase3_5b"),
        help="Root directory for per-strategy report folders.",
    )
    ap.add_argument(
        "--initial-capital",
        type=float,
        default=100_000.0,
        help="Starting capital (BRL). Scales equity curves and trade notional.",
    )
    ap.add_argument(
        "--storage-root",
        type=Path,
        default=Path("data/tiingo"),
        help="Root of the Tiingo parquet cache.",
    )
    ap.add_argument(
        "--spx-start",
        default="1970-01-02",
        help="Longest-available SPX TR start (Ken French era).",
    )
    ap.add_argument(
        "--spx-end",
        default="2026-04-14",
        help="SPX TR end (matches manifest latest bar).",
    )
    ap.add_argument(
        "--spx-cutoff",
        default="2001-05-14",
        help="Stitch cutoff for KF→TR in spx_tr_loader.",
    )
    ap.add_argument("--tax-rate", type=float, default=0.15)
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


# --- Data loading helpers ---------------------------------------------------


def _load_tiingo_hlc(
    storage_root: Path, ticker: str
) -> tuple[pd.Series, pd.Series, pd.Series]:
    storage = TiingoStorage(root=storage_root)
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


def _build_tr_price(returns: pd.Series) -> pd.Series:
    price = (1.0 + returns).cumprod() * 100.0
    price.name = "spx_tr_price"
    return price


# --- Report emission --------------------------------------------------------


def _scale_equity(equity_unit: pd.Series, initial_capital: float) -> pd.Series:
    """Rebase a unit-equity (starting at 1.0) series to ``initial_capital``."""
    if len(equity_unit) == 0:
        raise ValueError("empty equity series — cannot scale")
    e0 = float(equity_unit.iloc[0])
    if e0 <= 0:
        raise ValueError(f"equity[0]={e0} non-positive")
    return initial_capital * equity_unit / e0


def _scale_trades(trades: list[Trade], notional: float) -> list[Trade]:
    """Return copies with notional replaced (Trade is frozen)."""
    return [
        Trade(
            asset=t.asset,
            entry_date=t.entry_date,
            exit_date=t.exit_date,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            notional=notional,
            direction=t.direction,
        )
        for t in trades
    ]


def _filter_trades_to_window(
    trades: list[Trade],
    window_start: pd.Timestamp,
    window_end: pd.Timestamp,
) -> list[Trade]:
    """Keep trades fully contained in [window_start, window_end].

    Portfolio 3-leg equity curve starts on the intersection of the 3 legs'
    common-window (daily returns ∩ non-NaN), so a leg trade whose entry
    pre-dates the portfolio's first tradeable bar was NOT actually taken
    by the portfolio. Excluding those trades keeps the trade log
    consistent with the equity curve and the tax aggregates.
    """
    return [
        t
        for t in trades
        if pd.Timestamp(t.entry_date) >= window_start
        and pd.Timestamp(t.exit_date) <= window_end
    ]


def _plot_equity_curve(
    path: Path,
    title: str,
    strategy_equity: pd.Series,
    spy_equity: pd.Series,
) -> None:
    """Emit a two-line log-scale equity curve (strategy + SPY benchmark)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(strategy_equity.index, strategy_equity.values, label="Strategy",
            color="#1f6feb", linewidth=1.2)
    ax.plot(spy_equity.index, spy_equity.values, label="SPY buy&hold",
            color="#8b949e", linewidth=1.0, linestyle="--")
    ax.set_yscale("log")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (BRL, log scale)")
    ax.legend(loc="upper left")
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _emit_reports(
    out_dir: Path,
    strategy_name: str,
    params: str,
    equity: pd.Series,
    trades: list[Trade],
    spy_series: pd.Series,
    initial_capital: float,
    tax_rate: float,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_standard_report(
        equity=equity,
        trades=trades,
        strategy_name=strategy_name,
        params=params,
    )
    window_start = pd.Timestamp(equity.index[0])
    window_end = pd.Timestamp(equity.index[-1])
    spy_bench = build_spy_benchmark(
        spy_series,
        initial_capital=initial_capital,
        window_start=window_start,
        window_end=window_end,
    )
    comparison = compare_vs_spy(equity, spy_bench.equity_curve)
    md = render_markdown(report, spy_benchmark=spy_bench, spy_comparison=comparison)
    (out_dir / "standard_report.md").write_text(md, encoding="utf-8")

    csv_text, md_text = render_trade_log(
        trades, initial_capital=initial_capital, tax_rate=tax_rate
    )
    (out_dir / "trade_log.csv").write_text(csv_text, encoding="utf-8")
    (out_dir / "trade_log.md").write_text(md_text, encoding="utf-8")

    metrics_serialisable: dict = {}
    for k, v in asdict(report).items():
        if k == "equity_curve":
            continue
        if isinstance(v, pd.Timestamp):
            metrics_serialisable[k] = v.isoformat()
        elif isinstance(v, (int, float, np.floating, np.integer)):
            metrics_serialisable[k] = float(v)
        else:
            metrics_serialisable[k] = v

    summary = {
        "strategy": strategy_name,
        "params": params,
        "window_start": window_start.strftime("%Y-%m-%d"),
        "window_end": window_end.strftime("%Y-%m-%d"),
        "initial_capital": initial_capital,
        "tax_rate": tax_rate,
        "metrics": metrics_serialisable,
        "spy_benchmark": {
            "return_pct": spy_bench.return_pct,
            "cagr_pct": spy_bench.cagr_pct,
            "max_drawdown_pct": spy_bench.max_drawdown_pct,
            "sharpe": spy_bench.sharpe,
        },
        "vs_spy": {
            "excess_return_pct": comparison.excess_return_pct,
            "excess_cagr_pct": comparison.excess_cagr_pct,
            "delta_max_dd_pct": comparison.delta_max_dd_pct,
            "information_ratio": comparison.information_ratio,
            "correlation": comparison.correlation,
            "beta": comparison.beta,
        },
        "n_trades": report.n_trades,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=float), encoding="utf-8"
    )
    _plot_equity_curve(
        out_dir / "equity_curve.png",
        title=strategy_name,
        strategy_equity=equity,
        spy_equity=spy_bench.equity_curve,
    )
    log.info(
        "  %s → %s (%d trades, Sharpe=%.3f, CAGR=%.2f%%)",
        strategy_name,
        out_dir,
        report.n_trades,
        report.sharpe,
        report.cagr_pct * 100.0,
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    log.info("loading SPX TR stitched series …")
    spx_returns = load_spx_tr_daily(
        start=args.spx_start,
        end=args.spx_end,
        cutoff_date=pd.Timestamp(args.spx_cutoff),
    )
    spx_prices = _build_tr_price(spx_returns)
    log.info("SPX TR: %d bars %s → %s",
             len(spx_returns),
             spx_returns.index[0].date(),
             spx_returns.index[-1].date())

    log.info("loading Tiingo HLC for QQQ, GLD …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")
    g_close, g_high, g_low = _load_tiingo_hlc(args.storage_root, "GLD")
    log.info("QQQ: %d bars  GLD: %d bars", len(q_close), len(g_close))

    log.info("loading SPY benchmark …")
    spy_series = load_spy_series()
    log.info("SPY: %d bars %s → %s",
             len(spy_series),
             spy_series.index[0].date(),
             spy_series.index[-1].date())

    # --- Run each winner -----------------------------------------------
    log.info("simulating LETF rotation EMA100/2x …")
    letf_result = simulate_letf_rotation(spx_returns, spx_prices, LETF_WINNER_CFG)
    letf_trades = letf_get_trades(
        letf_result,
        spx_returns,
        LETF_WINNER_CFG,
        asset_label="LETF_2x",
        notional=args.initial_capital,
    )
    letf_equity = _scale_equity(letf_result.equity, args.initial_capital)

    log.info("simulating QQQ Donchian 20/10 …")
    qqq_result = simulate_tsmom(q_high, q_low, q_close, QQQ_WINNER_CFG)
    qqq_trades = tsmom_get_trades(
        qqq_result,
        q_close,
        asset_label="QQQ",
        notional=args.initial_capital,
    )
    qqq_equity = _scale_equity(qqq_result.equity, args.initial_capital)

    log.info("simulating GLD Donchian 40/20 …")
    gld_result = simulate_tsmom(g_high, g_low, g_close, GLD_WINNER_CFG)
    gld_trades = tsmom_get_trades(
        gld_result,
        g_close,
        asset_label="GLD",
        notional=args.initial_capital,
    )
    gld_equity = _scale_equity(gld_result.equity, args.initial_capital)

    out_root = args.output_dir
    summaries: dict[str, dict] = {}

    summaries["letf_rotation_ema100_2x"] = _emit_reports(
        out_dir=out_root / "letf_rotation_ema100_2x",
        strategy_name="LETF Rotation EMA100/0%/2x",
        params="filter=EMA lookback=100 band=0.00 leverage=2.0 off=CASH",
        equity=letf_equity,
        trades=letf_trades,
        spy_series=spy_series,
        initial_capital=args.initial_capital,
        tax_rate=args.tax_rate,
    )
    summaries["qqq_donchian_20_10"] = _emit_reports(
        out_dir=out_root / "qqq_donchian_20_10",
        strategy_name="QQQ Donchian 20/10",
        params="entry=20 exit=10 commission_bps=10 spread_bps=5",
        equity=qqq_equity,
        trades=qqq_trades,
        spy_series=spy_series,
        initial_capital=args.initial_capital,
        tax_rate=args.tax_rate,
    )
    summaries["gld_donchian_40_20"] = _emit_reports(
        out_dir=out_root / "gld_donchian_40_20",
        strategy_name="GLD Donchian 40/20",
        params="entry=40 exit=20 commission_bps=10 spread_bps=5",
        equity=gld_equity,
        trades=gld_trades,
        spy_series=spy_series,
        initial_capital=args.initial_capital,
        tax_rate=args.tax_rate,
    )

    # --- Portfolio 3-leg EW ---------------------------------------------
    log.info("building 3-leg EW blend …")
    letf_daily = letf_result.daily_returns.dropna()
    qqq_daily = qqq_result.daily_returns.dropna()
    gld_daily = gld_result.daily_returns.dropna()
    blend = blend_equal_weight_3(letf_daily, qqq_daily, gld_daily)
    port_equity_unit = (1.0 + blend).cumprod()
    port_equity = _scale_equity(port_equity_unit, args.initial_capital)

    # Portfolio was only tradeable once all 3 legs are aligned. Filter
    # each leg's trades to the blend window so the consolidated trade
    # log matches the equity curve (Phase 3.5b Task 6 correctness fix).
    port_window_start = pd.Timestamp(blend.index[0])
    port_window_end = pd.Timestamp(blend.index[-1])
    letf_trades_pw = _filter_trades_to_window(
        letf_trades, port_window_start, port_window_end
    )
    qqq_trades_pw = _filter_trades_to_window(
        qqq_trades, port_window_start, port_window_end
    )
    gld_trades_pw = _filter_trades_to_window(
        gld_trades, port_window_start, port_window_end
    )
    log.info(
        "  portfolio window %s → %s — kept %d/%d LETF, %d/%d QQQ, %d/%d GLD trades",
        port_window_start.date(),
        port_window_end.date(),
        len(letf_trades_pw), len(letf_trades),
        len(qqq_trades_pw), len(qqq_trades),
        len(gld_trades_pw), len(gld_trades),
    )

    # Per-leg trade notional = initial_capital / 3 (EW), so each trade's
    # gross PnL reflects the leg's slice. This is the Phase 3.5b §3 rule:
    # 15% tax applied to each leg's profitable trades individually.
    leg_notional = args.initial_capital / 3.0
    port_trades = aggregate_leg_trades(
        [
            ("LETF_2x", _scale_trades(letf_trades_pw, leg_notional)),
            ("QQQ", _scale_trades(qqq_trades_pw, leg_notional)),
            ("GLD", _scale_trades(gld_trades_pw, leg_notional)),
        ]
    )
    summaries["portfolio_3leg_ew"] = _emit_reports(
        out_dir=out_root / "portfolio_3leg_ew",
        strategy_name="Portfolio 3-leg EW (LETF+QQQ+GLD)",
        params="weights=(1/3,1/3,1/3) rebalance=daily tax_per_leg=15%",
        equity=port_equity,
        trades=port_trades,
        spy_series=spy_series,
        initial_capital=args.initial_capital,
        tax_rate=args.tax_rate,
    )

    (out_root / "summary.json").write_text(
        json.dumps(summaries, indent=2, default=float), encoding="utf-8"
    )
    log.info("done — wrote 4 report folders under %s", out_root)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
