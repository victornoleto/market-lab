#!/usr/bin/env python3
"""Phase 3.5b Task 7e — rolling correlation for the 3-leg portfolio.

Computes rolling Pearson ρ for all three cross-pairs of winner-leg
daily returns (LETF rotation EMA100/2x × QQQ Donchian 20/10 × GLD
Donchian 40/20) on 63-day and 252-day windows, summarises per-pair
stats, and flags high-ρ regimes (all three pairs simultaneously ≥
0.7). Also exports the full rolling-ρ time-series to CSV for plotting
downstream.

Output
------
* ``reports/phase3_5b/robustness/rolling_correlation.md`` — Markdown
  summary (stats table + high-ρ regime table).
* ``reports/phase3_5b/robustness/rolling_correlation.json`` — machine
  payload with windows, threshold, per-pair stats, and regime list.
* ``reports/phase3_5b/robustness/rolling_correlation_63d.csv`` —
  per-bar time-series for the 63-day window.
* ``reports/phase3_5b/robustness/rolling_correlation_252d.csv`` —
  per-bar time-series for the 252-day window.

Citations
---------
* Spec: ``specs/phase_3_5b_winners_validation.md`` §Task 7e.
* Rolling correlation risk monitoring:
  ``[advances_fin_ml, p.289-293]``.
* Winner configs frozen (Phase 3 iter 32/36/37/40 jornadas).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.metrics.rolling_correlation import (
    CANONICAL_HIGH_RHO_THRESHOLD,
    CANONICAL_WINDOWS,
    compute_rolling_correlation_report,
    render_rolling_correlation_markdown,
)
from ai_trade.backtest.strategies.letf_rotation import simulate_letf_rotation
from ai_trade.backtest.strategies.tsmom import simulate_tsmom
from validate_phase3_winners import (  # type: ignore[import-not-found]
    GLD_WINNER_CFG,
    LETF_WINNER_CFG,
    QQQ_WINNER_CFG,
    _build_tr_price,
    _load_tiingo_hlc,
)

log = logging.getLogger("phase3_5b.rolling_correlation")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/phase3_5b/robustness"),
    )
    ap.add_argument(
        "--storage-root",
        type=Path,
        default=Path("data/tiingo"),
    )
    ap.add_argument("--spx-start", default="1970-01-02")
    ap.add_argument("--spx-end", default="2026-04-14")
    ap.add_argument("--spx-cutoff", default="2001-05-14")
    ap.add_argument(
        "--threshold",
        type=float,
        default=CANONICAL_HIGH_RHO_THRESHOLD,
        help="high-ρ threshold (default 0.7)",
    )
    ap.add_argument(
        "--windows",
        type=int,
        nargs="+",
        default=list(CANONICAL_WINDOWS),
        help="rolling windows in trading days",
    )
    ap.add_argument(
        "--min-regime-bars",
        type=int,
        default=10,
        help="minimum streak length to count as a high-ρ regime",
    )
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


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
        len(spx_returns), spx_returns.index[0].date(), spx_returns.index[-1].date(),
    )

    log.info("running LETF rotation winner …")
    letf_daily = simulate_letf_rotation(spx_returns, spx_prices, LETF_WINNER_CFG).daily_returns.dropna()

    log.info("loading Tiingo HLC for QQQ + GLD …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")
    g_close, g_high, g_low = _load_tiingo_hlc(args.storage_root, "GLD")

    log.info("running QQQ Donchian winner …")
    qqq_daily = simulate_tsmom(q_high, q_low, q_close, QQQ_WINNER_CFG).daily_returns.dropna()
    log.info("running GLD Donchian winner …")
    gld_daily = simulate_tsmom(g_high, g_low, g_close, GLD_WINNER_CFG).daily_returns.dropna()

    log.info(
        "computing rolling correlations (windows=%s, threshold=%.2f, min_regime_bars=%d) …",
        args.windows, args.threshold, args.min_regime_bars,
    )
    report = compute_rolling_correlation_report(
        letf_daily,
        qqq_daily,
        gld_daily,
        windows=tuple(args.windows),
        threshold=args.threshold,
        min_regime_bars=args.min_regime_bars,
    )

    log.info(
        "common window %s → %s (%d bars)",
        report.common_start.date(), report.common_end.date(), report.bars,
    )
    for stats in report.pair_stats:
        log.info(
            "  %-16s w=%3d  mean=%.3f  median=%.3f  min=%.3f  max=%.3f  frac≥%.2f=%.1f%%  streak=%d",
            stats.pair, stats.window, stats.mean, stats.median,
            stats.min, stats.max, stats.threshold,
            stats.frac_above_threshold * 100, stats.longest_streak_above,
        )

    if report.regimes:
        log.info("high-ρ regimes (all 3 pairs ≥ %.2f, ≥ %d bars):",
                 args.threshold, args.min_regime_bars)
        for r in report.regimes:
            log.info(
                "  w=%3d  %s → %s  (%d bars)  ρLQ=%.3f ρLG=%.3f ρQG=%.3f",
                r.window, r.start.date(), r.end.date(), r.bars,
                r.mean_rho_letf_qqq, r.mean_rho_letf_gld, r.mean_rho_qqq_gld,
            )
    else:
        log.info("no high-ρ regimes detected at threshold %.2f", args.threshold)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    md = render_rolling_correlation_markdown(report)
    header = (
        "<!--\n"
        "Generated by scripts/run_rolling_correlation.py.\n"
        "Windows (bars): "
        + ", ".join(str(w) for w in report.windows)
        + f". Threshold: {report.threshold:.2f}.\n"
        "Winner-leg configs frozen (Phase 3 iter 32/36/37/40 jornadas).\n"
        "-->\n\n"
    )
    md_path = args.output_dir / "rolling_correlation.md"
    md_path.write_text(header + md, encoding="utf-8")

    payload = {
        "common_window": {
            "start": str(report.common_start.date()),
            "end": str(report.common_end.date()),
            "bars": int(report.bars),
        },
        "threshold": float(report.threshold),
        "windows": list(report.windows),
        "min_regime_bars": int(args.min_regime_bars),
        "pair_stats": [s.to_dict() for s in report.pair_stats],
        "regimes": [r.to_dict() for r in report.regimes],
    }
    json_path = args.output_dir / "rolling_correlation.json"
    json_path.write_text(json.dumps(payload, indent=2, default=float), encoding="utf-8")

    # Per-window CSV exports
    for w, frame in report.series.items():
        csv_path = args.output_dir / f"rolling_correlation_{int(w)}d.csv"
        frame.to_csv(csv_path)
        log.info("wrote %s (%d rows × %d cols)", csv_path, frame.shape[0], frame.shape[1])

    log.info("wrote %s", md_path)
    log.info("wrote %s", json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
