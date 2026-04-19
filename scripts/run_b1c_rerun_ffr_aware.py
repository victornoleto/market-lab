#!/usr/bin/env python3
"""Phase 3.5b Task 7a part 2 — re-run B1c gates with FFR-aware LETF cost.

Injects the Ken French RF series (annualized = RF_daily × 252) into the
B1c grid via :func:`simulate_letf_rotation(..., ffr_annualized=...)` so
every ON-regime return uses the time-varying swap-cost model

    annual_cost[t] = SW·(L-1)·(FFR[t] + SP) + expense_ratio
    r_synth[t]     = L·r_SPX_TR[t] - annual_cost[t] / 252

instead of Gayed's flat 1%/yr drag. The grid topology, splits,
bootstrap settings, and gate thresholds mirror the Phase 3 B1c run
exactly so verdicts are apples-to-apples.

Output
------

* ``reports/phase3_5b/robustness/b1c_rerun_ffr_aware_verdict.json`` — full
  grid verdict (same schema as ``reports/letf_rotation_b1c_verdict.json``).
* ``reports/phase3_5b/robustness/b1c_rerun_ffr_aware.md`` — human-readable
  delta report comparing FFR-aware vs flat-fee for the Phase 3 winner
  (cid=37: EMA100 / 2x / band 0%) and the whole grid.

Phase 3.5b constraint #4 — winner is IMMUTABLE even if gates fail under
FFR-aware. Critical findings flagged with ⚠️ in the report; the winner
record in ``docs/self_improvement/memory.md`` is not reverted.

Citations
---------

* Cost formula ``cost = SW·(L-1)·(FFR + SP) + ER``:
  ``data/external/README.md`` Task 7a section (testfolio model).
* Flat-fee reference: ``[leverage_for_the_long_run, p.16]``.
* Gate thresholds: ``[advances_fin_ml, p.208-211]`` (PBO<0.5),
  ``[advances_fin_ml, p.196-202]`` (DSR, bootstrap), Pardo (2008) ch.10
  (WF ≥ 6/8).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.spx_tr_loader import (
    fetch_ken_french_daily,
    load_spx_tr_daily,
)
from ai_trade.backtest.helpers.synthetic_letf import TRADING_DAYS_PER_YEAR
from ai_trade.backtest.grid.letf_rotation_b1c import (
    B1cGateVerdict,
    evaluate_b1c_gates,
)
from ai_trade.backtest.grid.letf_rotation_grid import GridAxes, build_grid
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    RotationResult,
    simulate_letf_rotation,
)

log = logging.getLogger("ai_trade.grid.letf_rotation.b1c_ffr_aware")


CANONICAL_IS = ("1970-01-02", "2000-12-31")
CANONICAL_OOS = ("2001-01-01", "2015-12-31")
CANONICAL_STRESS = ("2016-01-01", "2026-04-14")

PHASE3_AXES = GridAxes(
    filters=("SMA", "EMA"),
    lookbacks=(100, 125, 150, 200),
    bands=(0.0, 0.03, 0.05),
    leverages=(1.0, 2.0, 3.0),
    gold_weights=(0.0,),
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--start", default="1970-01-02")
    ap.add_argument("--end", default="2026-04-14")
    ap.add_argument(
        "--output-json",
        type=Path,
        default=Path(
            "reports/phase3_5b/robustness/b1c_rerun_ffr_aware_verdict.json"
        ),
    )
    ap.add_argument(
        "--output-md",
        type=Path,
        default=Path(
            "reports/phase3_5b/robustness/b1c_rerun_ffr_aware.md"
        ),
    )
    ap.add_argument("--annual-fee", type=float, default=0.01)
    ap.add_argument("--commission-bps", type=float, default=10.0)
    ap.add_argument("--spread-bps", type=float, default=5.0)
    ap.add_argument("--tax-rate", type=float, default=0.15)
    ap.add_argument("--cash-rate-annual", type=float, default=0.0)
    ap.add_argument("--swap-exposure", type=float, default=1.1)
    ap.add_argument("--ffr-spread", type=float, default=0.004)
    ap.add_argument("--expense-ratio", type=float, default=0.0095)
    ap.add_argument("--bootstrap-n-resamples", type=int, default=2000)
    ap.add_argument("--bootstrap-alpha", type=float, default=0.001)
    ap.add_argument("--bootstrap-block-mean", type=int, default=5)
    ap.add_argument("--cutoff", default="2001-05-14")
    ap.add_argument("--log-level", default="INFO")
    ap.add_argument(
        "--baseline-verdict",
        type=Path,
        default=Path("reports/letf_rotation_b1c_verdict.json"),
    )
    return ap.parse_args(argv)


def _build_tr_price_series(returns: pd.Series) -> pd.Series:
    price = (1.0 + returns).cumprod() * 100.0
    price.name = "spx_tr_price"
    return price


def _load_ffr_annualized(index: pd.DatetimeIndex) -> pd.Series:
    """Annualized FFR proxy (Ken French daily RF × 252) reindexed to ``index``.

    The daily RF is the simple return implied by the 1-month T-bill
    (Ibbotson up to 2024-05, ICE BofA 1m Treasury after) — a standard
    public proxy for the intended daily borrowing cost of leverage (cf.
    Gayed fn.23 re: 1% expense is "FFR + spread" historically). Missing
    days at the edges are ffill / bfill to match the cost-model
    convention in ``synthesize_letf_returns_ffr_aware``.
    """
    kf_df = fetch_ken_french_daily()
    rf_daily = kf_df["rf"].astype(float)
    rf_annual = rf_daily * TRADING_DAYS_PER_YEAR
    return rf_annual.reindex(index).ffill().bfill()


def _run_grid(
    spx_returns: pd.Series,
    spx_prices: pd.Series,
    configs: list[LETFRotationConfig],
    ffr_annualized: pd.Series,
    *,
    swap_exposure: float,
    ffr_spread: float,
    expense_ratio: float,
) -> list[RotationResult]:
    results: list[RotationResult] = []
    for i, cfg in enumerate(configs, 1):
        if i == 1 or i % 12 == 0 or i == len(configs):
            log.info(
                "[%d/%d] %s lb=%d band=%.2f lev=%.1f",
                i, len(configs), cfg.filter, cfg.lookback,
                cfg.band_pct, cfg.leverage,
            )
        results.append(
            simulate_letf_rotation(
                spx_returns,
                spx_prices,
                cfg,
                ffr_annualized=ffr_annualized,
                ffr_swap_exposure=swap_exposure,
                ffr_spread=ffr_spread,
                ffr_expense_ratio=expense_ratio,
            )
        )
    return results


def _build_delta_table(
    new_verdict: B1cGateVerdict,
    baseline_path: Path | None,
) -> pd.DataFrame:
    rows = []
    baseline_by_id: dict[int, dict] = {}
    if baseline_path is not None and baseline_path.exists():
        try:
            base = json.loads(baseline_path.read_text())
            baseline_by_id = {
                e["config_id"]: e for e in base["verdict"]["evaluations"]
            }
        except (KeyError, json.JSONDecodeError) as exc:
            log.warning("baseline verdict unreadable: %s", exc)

    for e in new_verdict.evaluations:
        c = e.config
        bl = baseline_by_id.get(e.config_id)
        row = {
            "cid": e.config_id,
            "filter": c.filter,
            "lb": c.lookback,
            "band": c.band_pct,
            "lev": c.leverage,
            "IS_sh_new": e.is_metrics.sharpe,
            "OOS_sh_new": e.oos_metrics.sharpe,
            "Str_sh_new": e.stress_metrics.sharpe,
            "DSR_p_new": e.dsr_p_value,
            "WF%_new": e.wf_profitable_ratio,
            "verdict_new": e.verdict,
        }
        if bl is not None:
            row["OOS_sh_base"] = bl["oos"]["sharpe"]
            row["OOS_dSh"] = e.oos_metrics.sharpe - bl["oos"]["sharpe"]
            row["verdict_base"] = bl["verdict"]
        rows.append(row)
    return pd.DataFrame(rows)


def _render_markdown(
    new_verdict: B1cGateVerdict,
    delta: pd.DataFrame,
    args: argparse.Namespace,
) -> str:
    lines: list[str] = []
    lines.append("# Phase 3.5b Task 7a — B1c re-run with FFR-aware LETF cost")
    lines.append("")
    lines.append(
        f"**Grid:** {new_verdict.n_configs} configs "
        f"(Phase 3 canonical axes, gold_weight=0.0)."
    )
    lines.append(
        f"**Window:** {args.start} → {args.end} "
        f"(seam {args.cutoff}, KF Mkt+RF pre, Tiingo SPY post)."
    )
    lines.append(
        f"**Cost model:** SW={args.swap_exposure}, "
        f"SP={args.ffr_spread:.3f}/yr, ER={args.expense_ratio:.4f}/yr, "
        f"FFR daily = Ken French RF × 252."
    )
    lines.append(
        f"**Splits:** IS {CANONICAL_IS[0]}→{CANONICAL_IS[1]} · "
        f"OOS {CANONICAL_OOS[0]}→{CANONICAL_OOS[1]} · "
        f"Stress {CANONICAL_STRESS[0]}→{CANONICAL_STRESS[1]}."
    )
    lines.append("")
    lines.append("## Grid-level verdict")
    lines.append("")
    lines.append(
        f"- PBO (FFR-aware) = **{new_verdict.pbo_value:.3f}** "
        f"(pass={'YES' if new_verdict.pbo_pass else 'NO'}, threshold <0.5)."
    )
    lines.append(
        f"- Passing configs: **{new_verdict.n_passing_configs} / "
        f"{new_verdict.n_configs}**."
    )
    wcid = new_verdict.winner_config_id
    if wcid is None:
        lines.append(
            "- **NO winner** — all configs failed at least one gate "
            "under FFR-aware cost."
        )
    else:
        w = new_verdict.evaluations[wcid]
        lines.append(
            f"- New top-passing config (by OOS Sharpe): cid={wcid} "
            f"{w.config.filter}{w.config.lookback} "
            f"band={w.config.band_pct:.2%} lev={w.config.leverage}x · "
            f"OOS Sharpe {w.oos_metrics.sharpe:.3f}, "
            f"bootstrap 99.9% CI [{w.bootstrap_sharpe_lo:.3f}, "
            f"{w.bootstrap_sharpe_hi:.3f}]."
        )
    lines.append("")

    lines.append("## Phase 3 winner (cid=37: EMA100/2x/band 0%) — FFR-aware")
    lines.append("")
    if 37 < len(new_verdict.evaluations):
        e = new_verdict.evaluations[37]
        lines.append(f"- Verdict: **{e.verdict}**")
        if e.failed_gates:
            lines.append(f"- Failed gates: {', '.join(e.failed_gates)}")
        lines.append(
            f"- IS Sharpe: {e.is_metrics.sharpe:.3f} "
            f"(CAGR {e.is_metrics.cagr:.2%}, MDD {e.is_metrics.max_drawdown:.2%})"
        )
        lines.append(
            f"- OOS Sharpe: {e.oos_metrics.sharpe:.3f} "
            f"(CAGR {e.oos_metrics.cagr:.2%}, MDD {e.oos_metrics.max_drawdown:.2%})"
        )
        lines.append(
            f"- Stress Sharpe: {e.stress_metrics.sharpe:.3f} "
            f"(CAGR {e.stress_metrics.cagr:.2%}, MDD {e.stress_metrics.max_drawdown:.2%})"
        )
        lines.append(
            f"- WF profitable ratio: {e.wf_profitable_ratio:.3f} "
            f"(max window MDD {e.wf_max_window_drawdown:.2%})"
        )
        lines.append(f"- DSR p-value (OOS, n_trials=72): {e.dsr_p_value:.4g}")
        if e.bootstrap_sharpe_lo is not None:
            lines.append(
                f"- Bootstrap OOS 99.9% CI: "
                f"[{e.bootstrap_sharpe_lo:.3f}, "
                f"{e.bootstrap_sharpe_hi:.3f}]"
            )
    lines.append("")

    lines.append("## Per-config Sharpe delta (top 15 by OOS_sh_new)")
    lines.append("")
    if not delta.empty:
        top = delta.sort_values("OOS_sh_new", ascending=False).head(15)
        cols = [
            "cid", "filter", "lb", "band", "lev",
            "OOS_sh_base", "OOS_sh_new", "OOS_dSh",
            "verdict_base", "verdict_new",
        ]
        present = [c for c in cols if c in top.columns]
        lines.append("```")
        lines.append(
            top[present].to_string(
                index=False,
                float_format=lambda x: f"{x:.3f}" if isinstance(x, float) else str(x),
            )
        )
        lines.append("```")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    winner_still_passes = (
        37 < len(new_verdict.evaluations)
        and new_verdict.evaluations[37].verdict == "PASS"
    )
    if winner_still_passes:
        lines.append(
            "✅ Phase 3 winner **survives** FFR-aware cost model on all "
            "gates. Flat-fee edge was not an artefact of cost under-modelling; "
            "allocation doc (Task 8) may cite a ~X%/yr CAGR haircut but no "
            "verdict change."
        )
    else:
        lines.append(
            "⚠️ FLAG — Phase 3 winner **does not survive** the FFR-aware "
            "re-run. Per constraint #4 the winner record in "
            "`docs/self_improvement/memory.md` is **immutable** for Phase "
            "3.5b; the allocation doc (Task 8) must cite this as a "
            "critical robustness caveat. Flat-fee materially overstates "
            "the IS edge in the high-FFR regime (1970s-1990s)."
        )
    lines.append("")

    lines.append("## Citations")
    lines.append("")
    lines.append(
        "- FFR-aware cost formula: `data/external/README.md` Task 7a section."
    )
    lines.append(
        "- Gayed flat-fee original (intact): `[leverage_for_the_long_run, p.16]`."
    )
    lines.append(
        "- Gate thresholds: `[advances_fin_ml, p.208-211]` (PBO<0.5), "
        "`[advances_fin_ml, p.196-202]` (DSR, bootstrap CI)."
    )
    lines.append(
        "- Winner-immutability rule Phase 3.5b: constraint #4 of "
        "`docs/self_improvement/memory.md`."
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    cutoff = pd.Timestamp(args.cutoff)
    spx_returns = load_spx_tr_daily(
        start=args.start, end=args.end, cutoff_date=cutoff,
    )
    spx_prices = _build_tr_price_series(spx_returns)
    ffr_annual = _load_ffr_annualized(spx_returns.index)
    log.info(
        "SPX TR loaded: %d bars %s → %s (mean FFR %.3f%%)",
        len(spx_returns),
        spx_returns.index[0].date(), spx_returns.index[-1].date(),
        float(ffr_annual.mean()) * 100,
    )

    configs = build_grid(
        PHASE3_AXES,
        annual_fee=args.annual_fee,
        commission_bps=args.commission_bps,
        spread_bps=args.spread_bps,
        tax_rate=args.tax_rate,
        cash_rate_annual=args.cash_rate_annual,
    )
    log.info("grid: %d configs (canonical Phase 3 axes)", len(configs))

    results = _run_grid(
        spx_returns, spx_prices, configs, ffr_annual,
        swap_exposure=args.swap_exposure,
        ffr_spread=args.ffr_spread,
        expense_ratio=args.expense_ratio,
    )

    verdict = evaluate_b1c_gates(
        configs,
        results,
        is_range=CANONICAL_IS,
        oos_range=CANONICAL_OOS,
        stress_range=CANONICAL_STRESS,
        bootstrap_n_resamples=args.bootstrap_n_resamples,
        bootstrap_alpha=args.bootstrap_alpha,
        bootstrap_block_mean=args.bootstrap_block_mean,
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "run": {
            "mode": "ffr_aware",
            "start": args.start,
            "end": args.end,
            "cutoff_date": args.cutoff,
            "n_configs": len(configs),
            "n_bars": int(len(spx_returns)),
            "splits": {
                "IS": {"start": CANONICAL_IS[0], "end": CANONICAL_IS[1]},
                "OOS": {"start": CANONICAL_OOS[0], "end": CANONICAL_OOS[1]},
                "Stress": {"start": CANONICAL_STRESS[0], "end": CANONICAL_STRESS[1]},
            },
            "costs": {
                "swap_exposure": args.swap_exposure,
                "ffr_spread": args.ffr_spread,
                "expense_ratio": args.expense_ratio,
                "commission_bps": args.commission_bps,
                "spread_bps": args.spread_bps,
                "tax_rate": args.tax_rate,
                "cash_rate_annual": args.cash_rate_annual,
                "mean_ffr_annual": float(ffr_annual.mean()),
            },
            "bootstrap": {
                "n_resamples": args.bootstrap_n_resamples,
                "alpha": args.bootstrap_alpha,
                "block_mean": args.bootstrap_block_mean,
            },
        },
        "verdict": verdict.to_dict(),
    }
    args.output_json.write_text(json.dumps(report, indent=2, default=str))
    log.info("wrote %s", args.output_json)

    delta = _build_delta_table(verdict, args.baseline_verdict)
    args.output_md.write_text(_render_markdown(verdict, delta, args))
    log.info("wrote %s", args.output_md)

    # Terse console summary.
    print(
        f"\n=== FFR-aware re-run — PBO {verdict.pbo_value:.3f} "
        f"(pass={verdict.pbo_pass}); passing "
        f"{verdict.n_passing_configs}/{verdict.n_configs} ==="
    )
    if 37 < len(verdict.evaluations):
        w = verdict.evaluations[37]
        print(
            f"cid=37 (EMA100/2x) verdict: {w.verdict}\n"
            f"  IS Sharpe {w.is_metrics.sharpe:.3f} · "
            f"OOS Sharpe {w.oos_metrics.sharpe:.3f} · "
            f"Stress Sharpe {w.stress_metrics.sharpe:.3f} · "
            f"DSR p {w.dsr_p_value:.4g} · "
            f"WF {w.wf_profitable_ratio:.3f}"
        )
        if w.failed_gates:
            print("  failed: " + ", ".join(w.failed_gates))
    return 0


if __name__ == "__main__":
    sys.exit(main())
