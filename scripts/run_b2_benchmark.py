#!/usr/bin/env python3
"""Phase 3 Lead B2 — LETF rotation vs ETFRotation top-1 benchmark [SWING BROKER].

Regenerates the daily net-of-cost return series for the two Phase 3 /
Phase B winners and runs them through
:mod:`ai_trade.backtest.grid.strategy_benchmark`:

* **Strategy A (LETF rotation):** Lead B1c winner = ``EMA100 band=0
  lev=2x`` on the stitched SPX TR 1970-2026. Costs: Gayed 1% annual
  drag, 10 bps commission + 5 bps spread per switch, **15% BR tax**
  on RISK_ON exits with realized gain (mandate §4).
* **Strategy B (ETFRotation top-1):** Phase A winner = Clenow monthly
  rotation SPY/QQQ/IWM/GLD/TLT, 90-day regression slope × R², SPY
  SMA200 regime, per-ETF SMA100 trend filter.

Overlapping window is GLD-bounded: SPY/QQQ/IWM start 2001-05, GLD
2004-11, TLT 2002-07. With the 500-day warmup the ETFRotation
equity curve starts at its requested ``--start``; we default to
**2007-01-03** (≈500 trading days after GLD's first bar) to give the
rotation a valid full-universe warmup. The LETF winner's returns are
sliced to the same window so both series cover ~19 years of daily
data (longest available for the five-ETF universe).

Output: ``reports/b2_benchmark/<run-id>/verdict.json`` with
correlations, individual and blended metrics, and the decision. A
terse summary is also printed to stdout.

Citations
---------

* LETF rotation parameters: ``[leverage_for_the_long_run, p.13-17]``.
* ETFRotation parameters: ``[stocks_on_the_move, p.66, p.81, p.95]``.
* Sharpe / DSR framework: ``[advances_fin_ml, p.196-202]``.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


log = logging.getLogger("ai_trade.b2")


WINNER_LETF = dict(
    filter="EMA",
    lookback=100,
    band_pct=0.0,
    leverage=2.0,
    gold_weight=0.0,
)
"""Lead B1c winner — see docs/self_improvement/memory.md frontmatter."""

WINNER_ETF_ROTATION = dict(
    symbols=("SPY", "QQQ", "IWM", "GLD", "TLT"),
    index_symbol="SPY",
    lookback=90,
    sma_index_period=200,
    sma_stock_period=100,
    top_n=1,
)
"""Phase A winner — see docs/self_improvement/memory.md frontmatter."""


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--start", type=date.fromisoformat, default=date(2007, 1, 3),
        help="Start of overlap window (default 2007-01-03).",
    )
    ap.add_argument(
        "--end", type=date.fromisoformat, default=date(2026, 4, 14),
        help="End of overlap window (default 2026-04-14).",
    )
    ap.add_argument(
        "--output-dir", type=Path, default=Path("reports/b2_benchmark"),
    )
    ap.add_argument(
        "--run-id", default=None,
        help="Defaults to b2_letf_vs_etfrot_<stamp>.",
    )
    ap.add_argument(
        "--storage-root", type=Path, default=Path("data/tiingo"),
    )
    ap.add_argument(
        "--initial-cash", type=float, default=100_000.0,
        help="ETFRotation starting equity (has no effect on the Sharpe).",
    )
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _letf_returns(start: date, end: date) -> pd.Series:
    """Rebuild the Lead B1c winner net daily returns on [start, end]."""
    from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
    from ai_trade.backtest.strategies.letf_rotation import (
        LETFRotationConfig,
        simulate_letf_rotation,
    )

    # Load the full stitched TR series so the EMA100 warmup happens well
    # before the overlap window (>500 trading days of pre-history).
    warmup_start = "2004-01-02"  # plenty for lookback=100 with safety margin
    spx_returns = load_spx_tr_daily(
        start=warmup_start,
        end=str(end),
    )
    log.info(
        "SPX TR loaded: %d bars %s → %s",
        len(spx_returns),
        spx_returns.index[0].date(), spx_returns.index[-1].date(),
    )
    spx_price = (1.0 + spx_returns).cumprod() * 100.0
    cfg = LETFRotationConfig(**WINNER_LETF)
    result = simulate_letf_rotation(spx_returns, spx_price, cfg)

    sliced = result.daily_returns.loc[
        (result.daily_returns.index >= pd.Timestamp(start))
        & (result.daily_returns.index <= pd.Timestamp(end))
    ].rename("letf_rotation")
    log.info(
        "LETF winner net returns: %d bars on [%s, %s]",
        len(sliced), sliced.index[0].date(), sliced.index[-1].date(),
    )
    return sliced


def _etf_rotation_returns(
    start: date, end: date, storage_root: Path, initial_cash: float
) -> pd.Series:
    """Rebuild ETFRotation top-1 net daily returns on [start, end]."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy

    src = TiingoSource(storage=TiingoStorage(root=storage_root))
    symbols = list(WINNER_ETF_ROTATION["symbols"])
    fetch_start = start - timedelta(days=500)  # standard warmup
    raw = src.fetch_many(
        symbols, fetch_start, end, asset_class="etf", frequency="daily",
    )
    missing = [s for s in symbols if s not in raw or raw[s].empty]
    if missing:
        raise RuntimeError(f"missing Tiingo daily data for {missing}")

    data_full = {sym: raw[sym] for sym in symbols}
    data_bounded = {
        sym: df.loc[pd.Timestamp(start): pd.Timestamp(end)]
        for sym, df in data_full.items()
    }

    strategy = ETFRotationStrategy(
        data=data_full,
        symbols=symbols,
        index_symbol=WINNER_ETF_ROTATION["index_symbol"],
        lookback=WINNER_ETF_ROTATION["lookback"],
        sma_index_period=WINNER_ETF_ROTATION["sma_index_period"],
        sma_stock_period=WINNER_ETF_ROTATION["sma_stock_period"],
        top_n=WINNER_ETF_ROTATION["top_n"],
    )

    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(
        strategy=strategy, data=data_bounded, initial_cash=initial_cash,
    )
    if result is None:
        raise RuntimeError("ETFRotation backtest returned no result")

    equity = result.equity_curve.dropna()
    rets = equity.pct_change().dropna()
    rets.name = "etf_rotation_top1"
    log.info(
        "ETFRotation top-1 net returns: %d bars on [%s, %s]",
        len(rets), rets.index[0].date(), rets.index[-1].date(),
    )
    return rets


def _format_number(x: float) -> str:
    if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))):
        return f"{x}"
    return f"{x:.4f}"


def _print_summary(verdict_dict: dict) -> None:
    print("\n=== B2 benchmark verdict ===")
    print(
        f"window: {verdict_dict['window_start']} → {verdict_dict['window_end']} "
        f"({verdict_dict['n_bars']} bars)"
    )
    print(
        f"Pearson  = {_format_number(verdict_dict['pearson'])}   "
        f"Spearman = {_format_number(verdict_dict['spearman'])}"
    )
    rc = verdict_dict["rolling_corr"]
    print(
        f"Rolling 252d corr: min={_format_number(rc['min'])} "
        f"median={_format_number(rc['median'])} max={_format_number(rc['max'])}"
    )
    a = verdict_dict["a"]
    b = verdict_dict["b"]
    blend = verdict_dict["blend"]
    print(
        f"{verdict_dict['strat_a']:>24}: Sharpe={_format_number(a['sharpe'])} "
        f"CAGR={_format_number(a['cagr'])} MaxDD={_format_number(a['max_drawdown'])} "
        f"MAR={_format_number(a['mar'])}"
    )
    print(
        f"{verdict_dict['strat_b']:>24}: Sharpe={_format_number(b['sharpe'])} "
        f"CAGR={_format_number(b['cagr'])} MaxDD={_format_number(b['max_drawdown'])} "
        f"MAR={_format_number(b['mar'])}"
    )
    print(
        f"{'risk-parity blend':>24}: Sharpe={_format_number(blend['sharpe'])} "
        f"CAGR={_format_number(blend['cagr'])} MaxDD={_format_number(blend['max_drawdown'])} "
        f"MAR={_format_number(blend['mar'])} "
        f"D={_format_number(blend['diversification_ratio'])}"
    )
    w = blend["weights"]
    pieces = ", ".join(f"{k}={v:.3f}" for k, v in w.items())
    print(f"blend weights (inverse-vol): {pieces}")
    print(f"DECISION: {verdict_dict['decision']}")
    for reason in verdict_dict["decision_reasons"]:
        print(f"  • {reason}")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    run_id = (
        args.run_id
        or f"b2_letf_vs_etfrot_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    output_dir = args.output_dir / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    log.info("=== B2 benchmark run %s ===", run_id)
    log.info("window: %s → %s", args.start, args.end)

    from ai_trade.backtest.grid.strategy_benchmark import run_benchmark

    letf_rets = _letf_returns(args.start, args.end)
    etf_rets = _etf_rotation_returns(
        args.start, args.end, args.storage_root, args.initial_cash,
    )

    verdict = run_benchmark(
        "letf_rotation_EMA100_lev2x",
        letf_rets,
        "etf_rotation_top1",
        etf_rets,
    )
    verdict_dict = verdict.to_dict()

    report = {
        "run_id": run_id,
        "window": {"start": str(args.start), "end": str(args.end)},
        "letf_config": WINNER_LETF,
        "etf_rotation_config": {
            **WINNER_ETF_ROTATION,
            "symbols": list(WINNER_ETF_ROTATION["symbols"]),
        },
        "verdict": verdict_dict,
    }
    out_json = output_dir / "verdict.json"
    out_json.write_text(json.dumps(report, indent=2, default=str))
    log.info("wrote %s", out_json)

    # Also persist the aligned daily returns + blend for audit.
    aligned = pd.DataFrame(
        {
            verdict.strat_a: letf_rets,
            verdict.strat_b: etf_rets,
            "blend_inverse_vol": verdict.blend.daily_returns,
        }
    ).dropna()
    aligned.to_csv(output_dir / "daily_returns.csv")
    log.info("wrote %s", output_dir / "daily_returns.csv")

    _print_summary(verdict_dict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
