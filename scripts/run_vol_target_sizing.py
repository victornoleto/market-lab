#!/usr/bin/env python3
"""Phase 3.5b Task 7f — vol-target 10% sizing on 3-leg portfolio.

Takes the three Phase 3 winner-leg daily return streams (LETF rotation
EMA100/2x, QQQ Donchian 20/10, GLD Donchian 40/20), builds the EW
blend, and sweeps an ex-ante vol-target sizing layer over the
cartesian product ``{63, 126, 252} × {1.5, 2.0, 3.0}`` caps with a
fixed 10% annualised target. Emits per-config metrics + a production
default verdict via the dual-margin rule (ΔOOS Sharpe ≥ +0.05 AND
ΔOOS CAGR ≥ +1.0 pp).

Output
------
* ``reports/phase3_5b/robustness/vol_target_sizing.md`` — Markdown
  summary (sweep table + default-sizing block).
* ``reports/phase3_5b/robustness/vol_target_sizing.json`` — machine
  payload (rows + default + rationale).

Citations
---------
* Spec: ``specs/phase_3_5b_winners_validation.md`` §Task 7f.
* Volatility standardisation: ``[systematic_trading_carver, p.107-111]``.
* Double-margin promotion rule: ``[advances_fin_ml, p.298-299]``.
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
from ai_trade.backtest.grid.portfolio_3leg import align_returns_3, blend_equal_weight_3
from ai_trade.backtest.metrics.vol_target import (
    CANONICAL_LOOKBACKS,
    CANONICAL_MAX_LEVERAGES,
    CANONICAL_TARGET_VOL,
    VolTargetConfig,
    compare_vol_target_configs,
    render_vol_target_markdown,
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

log = logging.getLogger("phase3_5b.vol_target")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/phase3_5b/robustness"),
    )
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--spx-start", default="1970-01-02")
    ap.add_argument("--spx-end", default="2026-04-14")
    ap.add_argument("--spx-cutoff", default="2001-05-14")
    ap.add_argument(
        "--is-end",
        default="2017-09-21",
        help="IS cut-off timestamp (same 60/40 split used in Task 7d).",
    )
    ap.add_argument(
        "--target-vol",
        type=float,
        default=CANONICAL_TARGET_VOL,
        help="Annualised vol target as a fraction (default 0.10).",
    )
    ap.add_argument(
        "--lookbacks",
        type=int,
        nargs="+",
        default=list(CANONICAL_LOOKBACKS),
    )
    ap.add_argument(
        "--max-leverages",
        type=float,
        nargs="+",
        default=list(CANONICAL_MAX_LEVERAGES),
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
    letf_daily = simulate_letf_rotation(
        spx_returns, spx_prices, LETF_WINNER_CFG
    ).daily_returns.dropna()

    log.info("loading Tiingo HLC for QQQ + GLD …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")
    g_close, g_high, g_low = _load_tiingo_hlc(args.storage_root, "GLD")

    log.info("running QQQ Donchian winner …")
    qqq_daily = simulate_tsmom(
        q_high, q_low, q_close, QQQ_WINNER_CFG
    ).daily_returns.dropna()
    log.info("running GLD Donchian winner …")
    gld_daily = simulate_tsmom(
        g_high, g_low, g_close, GLD_WINNER_CFG
    ).daily_returns.dropna()

    # Align + EW blend — Task 7e's common window pattern.
    a, b, c = align_returns_3(letf_daily, qqq_daily, gld_daily)
    blended = blend_equal_weight_3(a, b, c)
    log.info(
        "EW 3-leg blend: %d bars %s → %s",
        len(blended), blended.index[0].date(), blended.index[-1].date(),
    )

    configs = tuple(
        VolTargetConfig(args.target_vol, int(L), float(cap))
        for L in args.lookbacks
        for cap in args.max_leverages
    )
    log.info(
        "running vol-target sweep: target=%.2f, lookbacks=%s, caps=%s (%d configs)",
        args.target_vol, args.lookbacks, args.max_leverages, len(configs),
    )
    is_end = pd.Timestamp(args.is_end)

    cmp = compare_vol_target_configs(blended, is_end=is_end, configs=configs)

    log.info(
        "baseline_ew: OOS Sharpe=%.3f, OOS CAGR=%.2f%%, MaxDD(full)=%.2f%%",
        cmp.rows[0].oos_sharpe,
        cmp.rows[0].oos_cagr_pct * 100,
        cmp.rows[0].full_max_drawdown_pct * 100,
    )
    for row in cmp.rows[1:]:
        log.info(
            "  %-32s OOS Sh=%.3f  OOS CAGR=%.2f%%  MaxDD=%.2f%%  s̄=%.2f  cap%%=%.1f",
            row.label,
            row.oos_sharpe,
            row.oos_cagr_pct * 100,
            row.full_max_drawdown_pct * 100,
            row.scale_mean,
            row.scale_cap_hit_frac * 100,
        )

    log.info("DEFAULT SIZING: %s — %s", cmp.default_label, cmp.rationale)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    md = render_vol_target_markdown(cmp)
    header = (
        "<!--\n"
        "Generated by scripts/run_vol_target_sizing.py.\n"
        f"Target vol: {args.target_vol:.2%}. "
        f"Lookbacks: {args.lookbacks}. Caps: {args.max_leverages}. "
        f"IS-end: {args.is_end}.\n"
        "Winner-leg configs frozen (Phase 3 iter 32/36/37/40 jornadas).\n"
        "-->\n\n"
    )
    md_path = args.output_dir / "vol_target_sizing.md"
    md_path.write_text(header + md, encoding="utf-8")

    payload = {
        "target_vol": float(args.target_vol),
        "lookbacks": [int(x) for x in args.lookbacks],
        "max_leverages": [float(x) for x in args.max_leverages],
        "is_end": str(is_end.date()),
        "common_window": {
            "start": str(blended.index[0].date()),
            "end": str(blended.index[-1].date()),
            "bars": int(len(blended)),
        },
        **cmp.to_dict(),
    }
    json_path = args.output_dir / "vol_target_sizing.json"
    json_path.write_text(json.dumps(payload, indent=2, default=float), encoding="utf-8")

    log.info("wrote %s", md_path)
    log.info("wrote %s", json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
