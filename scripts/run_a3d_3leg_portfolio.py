#!/usr/bin/env python3
"""Phase 3 Lead A3d — 3-leg portfolio evaluation.

Goal: find a 3rd-leg daily-return stream whose blend with the iter 37
2-leg portfolio {LETF EMA100/2x + QQQ Donchian 20/10} pushes the
Diversification Ratio above **1.3** (A3c failed at DR=1.124 because
both legs were long-equity-US with ρ=0.555).

Candidate 3rd legs evaluated (one at a time):

* **TLT Donchian 55/20** — long-duration Treasury, negative-rho regime
  to equities during risk-off.
* **GLD Donchian 40/20** — gold, classical equity diversifier.

Per-candidate pipeline:

1. Simulate TSMOM Donchian on the full Tiingo daily history.
2. Align returns with leg 1 (LETF EMA100/2x) + leg 2 (QQQ Donchian 20/10).
3. Report Pearson ρ leg3-vs-leg1 and Sharpe(leg3) on common window —
   screening gate per the A3d lead description.
4. Run :func:`evaluate_a3d_gates` — EW / IVP / HRP blends vs baseline
   Sharpe (max of 3 legs on OOS), DR ≥ 1.3, DSR, WF, bootstrap.

Emit:

* ``reports/a3d_3leg_TLT.json``
* ``reports/a3d_3leg_GLD.json``

Path tag: **[SWING BROKER]** — BR 15% capital-gains tax baked into each
leg's simulator; HRP blend-layer adds no extra cost.

Citations
---------

* HRP recursive bisection + IVP cluster var: ``[advances_fin_ml,
  p.302-313, ch.16]``, Listing 16.2.
* Donchian 55/20 (Turtle canonical): ``[trading_systems_methods,
  p.353]``.
* DR Choueifaty-Coignard: ``[advances_fin_ml, p.302-313, ch.16]``.
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
from ai_trade.backtest.grid.portfolio_3leg import (
    A3dGateVerdict,
    evaluate_a3d_gates,
)
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    simulate_letf_rotation,
)
from ai_trade.backtest.strategies.tsmom import TSMOMConfig, simulate_tsmom

log = logging.getLogger("a3d")


LETF_WINNER_CONFIG = LETFRotationConfig(
    filter="EMA",
    lookback=100,
    band_pct=0.0,
    leverage=2.0,
    gold_weight=0.0,
)
QQQ_TSMOM_WINNER_CONFIG = TSMOMConfig(entry_lookback=20, exit_lookback=10)

CANDIDATE_3RD_LEGS: dict[str, tuple[str, TSMOMConfig]] = {
    "TLT_Donchian_55_20": ("TLT", TSMOMConfig(entry_lookback=55, exit_lookback=20)),
    "GLD_Donchian_40_20": ("GLD", TSMOMConfig(entry_lookback=40, exit_lookback=20)),
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--qqq-ticker", default="QQQ")
    ap.add_argument("--storage-root", default="data/tiingo")
    ap.add_argument("--spx-start", default="1970-01-02")
    ap.add_argument("--spx-end", default="2026-04-14")
    ap.add_argument("--cutoff", default="2001-05-14")
    ap.add_argument("--output-dir", type=Path, default=Path("reports"))
    ap.add_argument("--bootstrap-n-resamples", type=int, default=2000)
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _build_tr_price(returns: pd.Series) -> pd.Series:
    price = (1.0 + returns).cumprod() * 100.0
    price.name = "spx_tr_price"
    return price


def _load_tiingo_hlc(
    storage_root: str, ticker: str
) -> tuple[pd.Series, pd.Series, pd.Series]:
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
    """IS 60% / OOS 25% / Stress 15% — matches A3b/A3c convention."""
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


def _print_verdict(candidate_tag: str, v: A3dGateVerdict) -> None:
    print(f"\n=== A3d verdict — 3rd leg = {candidate_tag} ===")
    print(f"baseline OOS Sharpe = {v.baseline_sharpe_oos:.3f}"
          f" (leg: {v.baseline_leg_name})")
    for name, block in v.leg_metrics.items():
        print(f"  leg {name}: IS={block['is']['sharpe']:.3f}  "
              f"OOS={block['oos']['sharpe']:.3f}  "
              f"Str={block['stress']['sharpe']:.3f}  "
              f"CAGR(oos)={block['oos']['cagr']:.3%}")
    print("  pair correlations (full common window):")
    for pair, rho in v.leg_correlations.items():
        print(f"    ρ({pair}) = {rho:+.3f}")
    print("  screening |ρ|<0.2 AND Sharpe>0:")
    for leg, ok in v.screening_pass.items():
        print(f"    {leg}: {'PASS' if ok else 'FAIL'}")

    print("\n  --- blends ---")
    for b in v.blends:
        w = b.weights
        print(
            f"  {b.name:<16} w=({w[0]:.3f},{w[1]:.3f},{w[2]:.3f})  "
            f"IS={b.is_metrics.sharpe:.3f}  "
            f"OOS={b.oos_metrics.sharpe:.3f}  "
            f"Str={b.stress_metrics.sharpe:.3f}  "
            f"CAGR(oos)={b.oos_metrics.cagr:.3%}  "
            f"DR={b.diversification_ratio_full:.3f}  "
            f"DSR_p={b.dsr_p_value:.4f}  "
            f"WF={b.wf_profitable_ratio:.2f}  "
            f"MDD(oos)={b.oos_metrics.max_drawdown:.2%}  "
            f"verdict={b.verdict}"
        )
        if b.failed_gates:
            print(f"      failed: {', '.join(b.failed_gates)}")
        if b.bootstrap_sharpe_lo is not None:
            print(
                f"      boot 99.9% CI OOS Sharpe = "
                f"[{b.bootstrap_sharpe_lo:.3f}, {b.bootstrap_sharpe_hi:.3f}]"
            )
    print(f"\n  winner: {v.winner_blend or '(none)'}")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Leg 1: LETF rotation on stitched SPX TR 1970-2026.
    log.info("loading SPX TR %s → %s (cutoff %s)",
             args.spx_start, args.spx_end, args.cutoff)
    spx_returns = load_spx_tr_daily(
        start=args.spx_start,
        end=args.spx_end,
        cutoff_date=pd.Timestamp(args.cutoff),
    )
    spx_prices = _build_tr_price(spx_returns)
    log.info("SPX TR %d bars", len(spx_returns))
    letf_result = simulate_letf_rotation(
        spx_returns, spx_prices, LETF_WINNER_CONFIG
    )
    letf_daily = letf_result.daily_returns.dropna()

    # Leg 2: QQQ Donchian 20/10.
    log.info("loading Tiingo daily %s", args.qqq_ticker)
    q_close, q_high, q_low = _load_tiingo_hlc(
        args.storage_root, args.qqq_ticker
    )
    log.info(
        "%s %d bars  %s → %s",
        args.qqq_ticker, len(q_close),
        q_close.index[0].date(), q_close.index[-1].date(),
    )
    qqq_result = simulate_tsmom(q_high, q_low, q_close, QQQ_TSMOM_WINNER_CONFIG)
    qqq_daily = qqq_result.daily_returns.dropna()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, dict] = {}

    for tag, (ticker, cfg) in CANDIDATE_3RD_LEGS.items():
        log.info("=== candidate %s (ticker=%s)", tag, ticker)
        c_close, c_high, c_low = _load_tiingo_hlc(
            args.storage_root, ticker
        )
        log.info(
            "%s %d bars  %s → %s",
            ticker, len(c_close),
            c_close.index[0].date(), c_close.index[-1].date(),
        )
        cand_result = simulate_tsmom(c_high, c_low, c_close, cfg)
        cand_daily = cand_result.daily_returns.dropna()

        common = (
            letf_daily.index.intersection(qqq_daily.index)
                           .intersection(cand_daily.index)
        )
        if common.empty:
            log.warning("no overlapping dates with candidate %s — skipping", tag)
            continue
        common_start = common.min()
        common_end = common.max()
        log.info(
            "common window %s → %s  (%d bars)",
            common_start.date(), common_end.date(), len(common),
        )
        is_range, oos_range, stress_range = _splits_for_window(
            common_start, common_end
        )
        log.info("splits IS=%s OOS=%s STRESS=%s",
                 is_range, oos_range, stress_range)

        verdict = evaluate_a3d_gates(
            letf_daily,
            qqq_daily,
            cand_daily,
            leg_names=("LETF_EMA100_2x", "QQQ_Donchian_20_10", tag),
            is_range=is_range,
            oos_range=oos_range,
            stress_range=stress_range,
            bootstrap_n_resamples=args.bootstrap_n_resamples,
        )

        report = {
            "run": {
                "candidate_tag": tag,
                "ticker": ticker,
                "candidate_config": {
                    "entry_lookback": cfg.entry_lookback,
                    "exit_lookback": cfg.exit_lookback,
                    "commission_bps": cfg.commission_bps,
                    "spread_bps": cfg.spread_bps,
                    "tax_rate": cfg.tax_rate,
                },
                "common_start": common_start.strftime("%Y-%m-%d"),
                "common_end": common_end.strftime("%Y-%m-%d"),
                "common_bars": int(len(common)),
                "splits": {
                    "IS": {"start": is_range[0], "end": is_range[1]},
                    "OOS": {"start": oos_range[0], "end": oos_range[1]},
                    "Stress": {
                        "start": stress_range[0], "end": stress_range[1]
                    },
                },
            },
            "verdict": verdict.to_dict(),
        }

        out_path = args.output_dir / f"a3d_3leg_{tag}.json"
        out_path.write_text(json.dumps(report, indent=2, default=str))
        log.info("wrote %s", out_path)

        summary[tag] = {
            "common_bars": int(len(common)),
            "baseline_sharpe": verdict.baseline_sharpe_oos,
            "baseline_leg": verdict.baseline_leg_name,
            "winner_blend": verdict.winner_blend,
            "screening_pass": verdict.screening_pass,
            "blend_verdicts": {
                b.name: {
                    "verdict": b.verdict,
                    "oos_sharpe": b.oos_metrics.sharpe,
                    "dr_full": b.diversification_ratio_full,
                    "dsr_p": b.dsr_p_value,
                    "wf_ratio": b.wf_profitable_ratio,
                    "failed": b.failed_gates,
                }
                for b in verdict.blends
            },
        }

        _print_verdict(tag, verdict)

    summary_path = args.output_dir / "a3d_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    log.info("wrote %s", summary_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
