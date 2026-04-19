#!/usr/bin/env python3
"""Phase 3.5b Task 7c — slippage sensitivity for Phase 3 winners.

Sweeps total round-trip transaction cost per switch at the canonical
levels ``{0, 1, 5, 10}`` bps across the three winner strategies plus
the 3-leg EW portfolio. Each run re-simulates on the longest-available
historical window (manifest rule — CLAUDE.md) with only the
``commission_bps`` / ``spread_bps`` fields perturbed — lookbacks,
leverage, gold weight, tax rate, annual fee, and any FFR-aware drag
stay at Phase 3 winner defaults.

Output
------

* ``reports/phase3_5b/robustness/slippage_sensitivity.md`` — human
  Markdown table (4 strategies × 4 slippage levels).
* ``reports/phase3_5b/robustness/slippage_sensitivity.json`` — machine
  payload with the same data plus level/window metadata.

Citations
---------
* Spec: ``specs/phase_3_5b_winners_validation.md`` §Task 7c.
* Cost ablation methodology: ``[advances_fin_ml, p.261-266]``.
* Winner configs frozen (Phase 3 iter 32/36/37/40 jornadas).
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

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.grid.portfolio_3leg import blend_equal_weight_3
from ai_trade.backtest.metrics.slippage_sensitivity import (
    CANONICAL_SLIPPAGE_LEVELS_BPS,
    SlippageRow,
    make_cost_varied_config,
    render_multi_strategy_slippage_markdown,
    summarize_equity,
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

log = logging.getLogger("phase3_5b.slippage")


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
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _row_to_json(row: SlippageRow) -> dict:
    d = asdict(row)
    for k, v in list(d.items()):
        if isinstance(v, (np.floating, np.integer)):
            d[k] = float(v)
    return d


def _run_letf(spx_returns, spx_prices, level_bps: float):
    cfg = make_cost_varied_config(LETF_WINNER_CFG, level_bps)
    return simulate_letf_rotation(spx_returns, spx_prices, cfg)


def _run_tsmom(high, low, close, base_cfg, level_bps: float):
    cfg = make_cost_varied_config(base_cfg, level_bps)
    return simulate_tsmom(high, low, close, cfg)


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

    # --- Sweep ---------------------------------------------------------------
    letf_rows: list[SlippageRow] = []
    qqq_rows: list[SlippageRow] = []
    gld_rows: list[SlippageRow] = []
    port_rows: list[SlippageRow] = []

    for level in CANONICAL_SLIPPAGE_LEVELS_BPS:
        log.info("=== slippage level: %s bps ===", level)

        letf_r = _run_letf(spx_returns, spx_prices, level)
        letf_switches = int(letf_r.switches.sum())
        letf_cum = float(letf_r.cum_cost_pct)
        letf_rows.append(
            summarize_equity(letf_r.equity, level, letf_switches, letf_cum)
        )

        qqq_r = _run_tsmom(q_high, q_low, q_close, QQQ_WINNER_CFG, level)
        qqq_switches = int(qqq_r.switches.sum())
        qqq_cum = float(qqq_r.cum_cost_pct)
        qqq_rows.append(summarize_equity(qqq_r.equity, level, qqq_switches, qqq_cum))

        gld_r = _run_tsmom(g_high, g_low, g_close, GLD_WINNER_CFG, level)
        gld_switches = int(gld_r.switches.sum())
        gld_cum = float(gld_r.cum_cost_pct)
        gld_rows.append(summarize_equity(gld_r.equity, level, gld_switches, gld_cum))

        # Portfolio 3-leg EW — align and blend daily returns.
        blend = blend_equal_weight_3(
            letf_r.daily_returns.dropna(),
            qqq_r.daily_returns.dropna(),
            gld_r.daily_returns.dropna(),
        )
        port_equity = (1.0 + blend).cumprod()
        port_switches = letf_switches + qqq_switches + gld_switches
        # EW blend of the per-leg cost drag — each leg holds 1/3 of capital
        # so its per-unit-equity cost drag scales by 1/3 at the portfolio level.
        port_cum_cost = (letf_cum + qqq_cum + gld_cum) / 3.0
        port_rows.append(
            summarize_equity(port_equity, level, port_switches, port_cum_cost)
        )

        log.info(
            "  LETF Sharpe=%.3f CAGR=%.2f%% | QQQ Sharpe=%.3f CAGR=%.2f%% | "
            "GLD Sharpe=%.3f CAGR=%.2f%% | 3-leg Sharpe=%.3f CAGR=%.2f%%",
            letf_rows[-1].sharpe, letf_rows[-1].cagr_pct * 100,
            qqq_rows[-1].sharpe, qqq_rows[-1].cagr_pct * 100,
            gld_rows[-1].sharpe, gld_rows[-1].cagr_pct * 100,
            port_rows[-1].sharpe, port_rows[-1].cagr_pct * 100,
        )

    sections = [
        ("LETF Rotation EMA100/0%/2x", letf_rows),
        ("QQQ Donchian 20/10", qqq_rows),
        ("GLD Donchian 40/20", gld_rows),
        ("Portfolio 3-leg EW (LETF+QQQ+GLD)", port_rows),
    ]

    # --- Emit artefacts ------------------------------------------------------
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    md = render_multi_strategy_slippage_markdown(
        sections,
        title="Phase 3.5b Task 7c — Slippage sensitivity",
        levels_bps=CANONICAL_SLIPPAGE_LEVELS_BPS,
    )
    header = (
        "<!--\n"
        "Generated by scripts/run_slippage_sensitivity.py.\n"
        "Levels: backtest.metrics.slippage_sensitivity.CANONICAL_SLIPPAGE_LEVELS_BPS.\n"
        "Windows: longest-available per manifest rule (CLAUDE.md).\n"
        "Per run: cfg = replace(winner_cfg, commission_bps=0, spread_bps=level).\n"
        "Tax, annual fee, FFR drag held at Phase 3 defaults.\n"
        "-->\n\n"
    )
    (out_dir / "slippage_sensitivity.md").write_text(header + md, encoding="utf-8")

    payload = {
        "levels_bps": list(CANONICAL_SLIPPAGE_LEVELS_BPS),
        "windows": {
            "letf": {
                "start": str(spx_returns.index[0].date()),
                "end": str(spx_returns.index[-1].date()),
                "bars": int(len(spx_returns)),
            },
            "qqq": {
                "start": str(q_close.index[0].date()),
                "end": str(q_close.index[-1].date()),
                "bars": int(len(q_close)),
            },
            "gld": {
                "start": str(g_close.index[0].date()),
                "end": str(g_close.index[-1].date()),
                "bars": int(len(g_close)),
            },
        },
        "strategies": {
            name: [_row_to_json(r) for r in rows] for name, rows in sections
        },
    }
    (out_dir / "slippage_sensitivity.json").write_text(
        json.dumps(payload, indent=2, default=float), encoding="utf-8"
    )

    log.info("wrote %s", out_dir / "slippage_sensitivity.md")
    log.info("wrote %s", out_dir / "slippage_sensitivity.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
