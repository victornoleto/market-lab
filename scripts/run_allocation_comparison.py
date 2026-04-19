#!/usr/bin/env python3
"""Phase 3.5b Task 7d — allocation comparison for the 3-leg portfolio.

Re-blends the LETF + QQQ + GLD daily-return streams under five static
weighting schemes (EW, IVP, HRP, RP, MV) on the longest-available
common window, then writes a Markdown + JSON comparison and decides
whether EW remains the production default.

Decision rule (mandated by spec §Task 7d):
  EW is kept unless a challenger improves BOTH OOS Sharpe (≥ +0.05)
  and Diversification Ratio (≥ +0.05). Margins guard against
  estimation-noise gains [advances_fin_ml, p.298-299].

Output
------
* ``reports/phase3_5b/robustness/allocation_comparison.md``
* ``reports/phase3_5b/robustness/allocation_comparison.json``

Citations
---------
* Spec: ``specs/phase_3_5b_winners_validation.md`` §Task 7d.
* Maillard-Roncalli 2010 (ERC); López de Prado
  ``[advances_fin_ml, p.297-313]``.
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
from ai_trade.backtest.grid.portfolio_3leg import align_returns_3
from ai_trade.backtest.metrics.allocation_comparison import (
    compare_allocations_3,
    render_allocation_comparison_markdown,
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

log = logging.getLogger("phase3_5b.allocation")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--output-dir", type=Path, default=Path("reports/phase3_5b/robustness")
    )
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--spx-start", default="1970-01-02")
    ap.add_argument("--spx-end", default="2026-04-14")
    ap.add_argument("--spx-cutoff", default="2001-05-14")
    # Use the same 60/25/15 split convention as Phase 3 A3d
    # (`scripts/run_a3d_3leg_portfolio.py::_splits_for_window`).
    ap.add_argument("--is-fraction", type=float, default=0.60)
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _is_end_for_window(start: pd.Timestamp, end: pd.Timestamp, fraction: float) -> pd.Timestamp:
    """Mirror the IS-end formula from ``run_a3d_3leg_portfolio._splits_for_window``."""
    total = (end - start).days
    return start + pd.Timedelta(days=int(total * fraction))


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
    letf_r = simulate_letf_rotation(spx_returns, spx_prices, LETF_WINNER_CFG)
    letf_daily = letf_r.daily_returns.dropna()

    log.info("loading Tiingo HLC for QQQ + GLD …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")
    g_close, g_high, g_low = _load_tiingo_hlc(args.storage_root, "GLD")

    log.info("running QQQ Donchian winner …")
    qqq_daily = simulate_tsmom(q_high, q_low, q_close, QQQ_WINNER_CFG).daily_returns.dropna()
    log.info("running GLD Donchian winner …")
    gld_daily = simulate_tsmom(g_high, g_low, g_close, GLD_WINNER_CFG).daily_returns.dropna()

    a, b, c = align_returns_3(letf_daily, qqq_daily, gld_daily)
    common_start = a.index.min()
    common_end = a.index.max()
    is_end = _is_end_for_window(common_start, common_end, args.is_fraction)
    log.info(
        "common window %s → %s (%d bars), IS-end=%s (fraction=%.2f)",
        common_start.date(), common_end.date(), len(a),
        is_end.date(), args.is_fraction,
    )

    leg_names = ("LETF_EMA100_2x", "QQQ_Donchian_20_10", "GLD_Donchian_40_20")
    verdict = compare_allocations_3(a, b, c, is_end=is_end, leg_names=leg_names)

    log.info("default allocation -> %s", verdict.default_method)
    log.info(verdict.rationale)
    for row in verdict.rows:
        log.info(
            "  %-13s w=(%.3f,%.3f,%.3f)  Sharpe(full)=%.3f  Sharpe(IS)=%.3f  "
            "Sharpe(OOS)=%.3f  CAGR=%.2f%%  MaxDD=%.2f%%  DR=%.3f",
            row.method, row.weights[0], row.weights[1], row.weights[2],
            row.full_sharpe, row.is_sharpe, row.oos_sharpe,
            row.full_cagr_pct * 100, row.full_max_drawdown_pct * 100,
            row.diversification_ratio,
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    md = render_allocation_comparison_markdown(verdict)
    header = (
        "<!--\n"
        "Generated by scripts/run_allocation_comparison.py.\n"
        "IS/OOS split: 60/40 of common window (matches Phase 3 A3d convention).\n"
        "Weights for non-EW methods are fitted on the IS slice only.\n"
        "Winner-leg configs frozen (Phase 3 iter 32/36/37/40 jornadas).\n"
        "-->\n\n"
    )
    md_path = args.output_dir / "allocation_comparison.md"
    md_path.write_text(header + md, encoding="utf-8")

    payload = {
        "common_window": {
            "start": str(common_start.date()),
            "end": str(common_end.date()),
            "bars": int(len(a)),
        },
        "is_end": str(is_end.date()),
        "is_fraction": float(args.is_fraction),
        "comparison": verdict.to_dict(),
    }
    json_path = args.output_dir / "allocation_comparison.json"
    json_path.write_text(json.dumps(payload, indent=2, default=float), encoding="utf-8")

    log.info("wrote %s", md_path)
    log.info("wrote %s", json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
