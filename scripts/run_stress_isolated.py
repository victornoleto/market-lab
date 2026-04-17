#!/usr/bin/env python3
"""Phase 3.5b Task 7b — stress-period isolation for Phase 3 winners.

Re-runs the Phase 3 winner backtests on the longest-available windows
(manifest rule — CLAUDE.md) and slices each equity curve by the four
canonical stress windows defined in ``backtest.metrics.stress_periods``:

* 2008-09-01 → 2009-03-31 (Lehman → March 2009 bottom)
* 2020-02-19 → 2020-04-30 (COVID crash + rebound)
* 2022-01-03 → 2022-12-30 (full-year bear + Fed hikes)
* 2025-01-01 → 2025-03-31 (2025 Q1 tariff/rate stress)

Per strategy + portfolio, we report Sharpe / Sortino / max-DD / total
return / Δ-to-SPY inside each window, and write the consolidated
Markdown to ``reports/phase3_5b/robustness/stress_isolated.md`` with the
machine-readable equivalent in ``stress_isolated.json``.

The winner configs themselves come from
``scripts/validate_phase3_winners`` so we stay bit-identical to the
standard reports emitted for Tasks 3-6. No strategy logic is re-coded
here — we only add the windowed slice.

Citations
---------
* Window definitions: ``specs/phase_3_5b_winners_validation.md`` §Task 7b.
* Winner configs: Phase 3 iter 32/36/37 jornadas
  (``2026-04-17-0055-b1c-letf-rotation-gates-PASS.md``,
  ``2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md``,
  ``2026-04-17-0040-a3d-3leg-letf-qqq-gld-PASS.md``).
* SPY benchmark mandatory: Phase 3.5b spec §4.5.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

# ``scripts/`` isn't a package — make sibling scripts importable by path.
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.grid.portfolio_3leg import blend_equal_weight_3
from ai_trade.backtest.metrics.standard_report import Trade, load_spy_series
from ai_trade.backtest.metrics.stress_periods import (
    STANDARD_STRESS_WINDOWS,
    StressReport,
    compute_all_stress_reports,
    render_multi_strategy_stress_markdown,
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
from validate_phase3_winners import (  # type: ignore[import-not-found]
    GLD_WINNER_CFG,
    LETF_WINNER_CFG,
    QQQ_WINNER_CFG,
    _build_tr_price,
    _filter_trades_to_window,
    _load_tiingo_hlc,
    _scale_equity,
    _scale_trades,
)

log = logging.getLogger("phase3_5b.stress")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/phase3_5b/robustness"),
        help="Directory to place stress_isolated.{md,json}.",
    )
    ap.add_argument(
        "--initial-capital",
        type=float,
        default=100_000.0,
        help="Starting capital (BRL). Must match validate_phase3_winners default.",
    )
    ap.add_argument(
        "--storage-root",
        type=Path,
        default=Path("data/tiingo"),
    )
    ap.add_argument("--spx-start", default="1970-01-02")
    ap.add_argument("--spx-end", default="2026-04-14")
    ap.add_argument("--spx-cutoff", default="2001-05-14")
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _report_to_dict(r: StressReport) -> dict:
    d = asdict(r)
    # Drop the equity curves from the JSON — noisy and already inside the md tables.
    d.pop("equity_curve", None)
    d.pop("spy_equity_curve", None)
    d["window_start"] = pd.Timestamp(r.window_start).strftime("%Y-%m-%d")
    d["window_end"] = pd.Timestamp(r.window_end).strftime("%Y-%m-%d")
    for k, v in list(d.items()):
        if isinstance(v, (np.floating, np.integer)):
            d[k] = float(v)
    return d


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
    log.info(
        "SPX TR: %d bars %s → %s",
        len(spx_returns),
        spx_returns.index[0].date(),
        spx_returns.index[-1].date(),
    )

    log.info("loading Tiingo HLC for QQQ, GLD …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")
    g_close, g_high, g_low = _load_tiingo_hlc(args.storage_root, "GLD")

    log.info("loading SPY benchmark …")
    spy_series = load_spy_series()
    # SPY equity curve: starts at initial_capital, scales with adjusted close.
    spy_equity = (
        args.initial_capital * spy_series / float(spy_series.iloc[0])
    )

    # --- Strategy simulations (match validate_phase3_winners byte-for-byte) ---
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
        qqq_result, q_close, asset_label="QQQ", notional=args.initial_capital
    )
    qqq_equity = _scale_equity(qqq_result.equity, args.initial_capital)

    log.info("simulating GLD Donchian 40/20 …")
    gld_result = simulate_tsmom(g_high, g_low, g_close, GLD_WINNER_CFG)
    gld_trades = tsmom_get_trades(
        gld_result, g_close, asset_label="GLD", notional=args.initial_capital
    )
    gld_equity = _scale_equity(gld_result.equity, args.initial_capital)

    # Portfolio 3-leg EW blend
    letf_daily = letf_result.daily_returns.dropna()
    qqq_daily = qqq_result.daily_returns.dropna()
    gld_daily = gld_result.daily_returns.dropna()
    blend = blend_equal_weight_3(letf_daily, qqq_daily, gld_daily)
    port_equity_unit = (1.0 + blend).cumprod()
    port_equity = _scale_equity(port_equity_unit, args.initial_capital)

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
    leg_notional = args.initial_capital / 3.0
    port_trades: list[Trade] = (
        _scale_trades(letf_trades_pw, leg_notional)
        + _scale_trades(qqq_trades_pw, leg_notional)
        + _scale_trades(gld_trades_pw, leg_notional)
    )

    # --- Stress reports -------------------------------------------------------
    log.info("computing stress-window reports for the 4 strategies …")
    sections: list[tuple[str, list[StressReport]]] = [
        (
            "LETF Rotation EMA100/0%/2x",
            compute_all_stress_reports(letf_equity, letf_trades, spy_equity),
        ),
        (
            "QQQ Donchian 20/10",
            compute_all_stress_reports(qqq_equity, qqq_trades, spy_equity),
        ),
        (
            "GLD Donchian 40/20",
            compute_all_stress_reports(gld_equity, gld_trades, spy_equity),
        ),
        (
            "Portfolio 3-leg EW (LETF+QQQ+GLD)",
            compute_all_stress_reports(port_equity, port_trades, spy_equity),
        ),
    ]

    # --- Emit artefacts --------------------------------------------------------
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    md = render_multi_strategy_stress_markdown(
        sections,
        title="Phase 3.5b Task 7b — Stress-period isolation",
    )
    # Prepend a context header that documents the window set and SPY provenance.
    header = (
        "<!--\n"
        "Generated by scripts/run_stress_isolated.py.\n"
        "Windows: see ai_trade.backtest.metrics.stress_periods.STANDARD_STRESS_WINDOWS.\n"
        "SPY source: data/tiingo/daily/prices/SPY.parquet (adj_close).\n"
        "Strategies re-simulate with Phase 3 winner configs (frozen). Tax model off "
        "in this view — stress windows show gross risk, the tax drag is already "
        "captured by the full-window standard reports in Tasks 3-6.\n"
        "-->\n\n"
    )
    (out_dir / "stress_isolated.md").write_text(header + md, encoding="utf-8")

    json_payload = {
        "windows": [
            {
                "name": w.name,
                "start": w.start.strftime("%Y-%m-%d"),
                "end": w.end.strftime("%Y-%m-%d"),
                "description": w.description,
            }
            for w in STANDARD_STRESS_WINDOWS
        ],
        "strategies": {
            name: [_report_to_dict(r) for r in reports]
            for name, reports in sections
        },
    }
    (out_dir / "stress_isolated.json").write_text(
        json.dumps(json_payload, indent=2, default=float), encoding="utf-8"
    )

    log.info("wrote %s", out_dir / "stress_isolated.md")
    log.info("wrote %s", out_dir / "stress_isolated.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
