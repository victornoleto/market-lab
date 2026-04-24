"""Phase 3 — gate cross-dataset common candidates.

The main Phase 3 sweep gates only the top-5 per-dataset by effectiveness.
That may miss cross-dataset winners — a (base, combo) pair that is
mediocre in one dataset but solid in the other two may still be the
honest candidate under spec §0 validation
("top configs precisam passar ≥ 5/7 gates no synth E ≥ 4/7 no real").

This script:

1. Intersects the 3 per-dataset Phase-3 csvs to find bases present in
   all 3 top-20 lists.
2. For each (common_base, combo) × dataset tuple, re-runs the sim and
   evaluates the 7-gate battery.
3. Emits ``studies/.../phase3/cross_dataset_gates.md`` with the verdict
   per (base, combo).

Gates reuse the same n_trials as Phase 3 (4 020).
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from run_phase3_sweep import (  # type: ignore  # same directory import
    DatasetContext,
    N_TRIALS_CUMULATIVE,
    PHASE3_COMBOS,
    Phase3Gates,
    Phase3Metrics,
    _build_educational,
    _build_real,
    _build_risks,
    _evaluate_gates,
    _fill_deltas,
    _metrics_from_result,
    CombinationSpec,
)
from ai_trade.backtest.grid.real_etf_regime_runner import NDX_MARKET, SPY_MARKET
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    max_drawdown as _max_drawdown,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    TRADING_DAYS_PER_YEAR,
)
from ai_trade.backtest.strategies.stop_loss_and_risk_signals import (
    RiskSignalConfig,
    StopLossConfig,
)

STUDY_DIR = Path(__file__).parent


def _fmt_pct(x, digits=2):
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x * 100:+.{digits}f}%"


def _fmt_num(x, digits=2):
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{digits}f}"


def _setup_logging() -> logging.Logger:
    logger = logging.getLogger("phase3_cross")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


def main() -> int:
    log = _setup_logging()
    t0 = time.time()

    # 1. Find common bases.
    csv_paths = {
        "educational": STUDY_DIR / "phase3" / "educational" / "configs_combined.csv",
        "spy_real": STUDY_DIR / "phase3" / "spy_real" / "configs_combined.csv",
        "ndx_real": STUDY_DIR / "phase3" / "ndx_real" / "configs_combined.csv",
    }
    dfs = {k: pd.read_csv(v) for k, v in csv_paths.items()}
    bases_by_ds = {k: set(df.base_cfg_id.unique()) for k, df in dfs.items()}
    common_bases = (
        bases_by_ds["educational"] & bases_by_ds["spy_real"] & bases_by_ds["ndx_real"]
    )
    log.info("common bases across all 3 datasets: %d (%s)",
             len(common_bases), sorted(common_bases))

    if not common_bases:
        log.warning("no common bases — nothing to cross-gate.")
        return 0

    # 2. Build contexts for each dataset.
    contexts: dict[str, tuple[DatasetContext, list]] = {}
    for label, builder in [
        ("educational", lambda: _build_educational(20)),
        ("spy_real", lambda: _build_real(SPY_MARKET, 20, "ema_sma_threshold_spy_real")),
        ("ndx_real", lambda: _build_real(NDX_MARKET, 20, "ema_sma_threshold_nasdaq_real")),
    ]:
        ctx, top = builder()
        contexts[label] = (ctx, top)

    # 3. For each dataset, evaluate gates for every (common_base × combo).
    all_results: dict[str, dict[tuple[str, str], tuple[Phase3Metrics, Phase3Gates]]] = {}
    for ds_label, (ctx, top_configs) in contexts.items():
        log.info("=== %s ===", ds_label)
        risks = _build_risks(ctx.daily_index, log)

        # Baselines for deltas.
        baseline_by_base: dict[str, tuple[float, float]] = {}
        for base in top_configs:
            res = ctx.simulate_fn(
                base, StopLossConfig(stop_loss_pct=None),
                risks["composite"],
                RiskSignalConfig(indicator_type="composite", lambda_de_lever=0.0),
            )
            bcagr = float(_cagr(res.equity, TRADING_DAYS_PER_YEAR))
            bmdd = float(_max_drawdown(res.equity))
            baseline_by_base[base.cfg_id] = (bcagr, bmdd)

        # Only simulate common bases × all 4 combos.
        common_configs = [c for c in top_configs if c.cfg_id in common_bases]
        rank_map = {c.cfg_id: i + 1 for i, c in enumerate(top_configs)}

        metrics: list[Phase3Metrics] = []
        for base in common_configs:
            for combo in PHASE3_COMBOS:
                risk_cfg = RiskSignalConfig(
                    indicator_type=combo.risk_indicator,
                    lambda_de_lever=combo.risk_lambda,
                )
                risk_series = risks[combo.risk_indicator]
                res = ctx.simulate_fn(base, combo.stop_cfg, risk_series, risk_cfg)
                m = _metrics_from_result(rank_map[base.cfg_id], base, combo, res)
                metrics.append(m)

        _fill_deltas(metrics, baseline_by_base)

        # Gate all common pairs — but PBO uses the FULL 80-variant grid
        # from the dataset's configs_combined.csv (already computed).
        # For accuracy we re-run the 80-variant sims here too so we have
        # the returns matrix in memory — cheap (~80 sims).
        log.info("  gating %d common pairs", len(metrics))
        all_metrics_for_pbo: list[Phase3Metrics] = []
        for base in top_configs:
            for combo in PHASE3_COMBOS:
                risk_cfg = RiskSignalConfig(
                    indicator_type=combo.risk_indicator,
                    lambda_de_lever=combo.risk_lambda,
                )
                risk_series = risks[combo.risk_indicator]
                res = ctx.simulate_fn(base, combo.stop_cfg, risk_series, risk_cfg)
                all_metrics_for_pbo.append(
                    _metrics_from_result(rank_map[base.cfg_id], base, combo, res)
                )
        _fill_deltas(all_metrics_for_pbo, baseline_by_base)

        gates = _evaluate_gates(
            metrics, all_metrics_for_pbo, ctx, risks, N_TRIALS_CUMULATIVE, log,
        )
        all_results[ds_label] = {
            (m.base_cfg_id, m.combo_label): (m, g) for m, g in zip(metrics, gates)
        }

    # 4. Write cross-dataset report.
    out_path = STUDY_DIR / "phase3" / "cross_dataset_gates.md"
    md = ["# Phase 3 — Cross-dataset gate verdict\n"]
    md.append(
        "> Gates on every (common_base × combo) pair across all 3 datasets.\n"
        f"> Common bases: {sorted(common_bases)}\n"
        f"> n_trials (DSR, cumulative): {N_TRIALS_CUMULATIVE}\n"
    )

    md.append("\n## Results by (base, combo)\n")
    md.append(
        "Spec §0 criterion: **≥ 5/7 gates in educational AND ≥ 4/7 in each real dataset**.\n"
    )
    md.append(
        "| base | combo | edu CAGR / ΔCAGR | edu MDD / ΔMDD | edu gates | "
        "spy gates | ndx gates | spec §0 met? |\n"
        "|---|---|---|---|---|---|---|---|"
    )
    any_winner = False
    winner_lines: list[str] = []
    for base in sorted(common_bases):
        for combo in PHASE3_COMBOS:
            key = (base, combo.label)
            if any(key not in all_results[d] for d in all_results):
                continue
            edu_m, edu_g = all_results["educational"][key]
            spy_m, spy_g = all_results["spy_real"][key]
            ndx_m, ndx_g = all_results["ndx_real"][key]
            spec_met = (
                edu_g.n_passed >= 5
                and spy_g.n_passed >= 4
                and ndx_g.n_passed >= 4
            )
            if spec_met:
                any_winner = True
                winner_lines.append(f"{base} × {combo.label}")
            md.append(
                f"| `{base}` | {combo.label} | "
                f"{_fmt_pct(edu_m.cagr)} / {_fmt_pct(edu_m.delta_cagr)} | "
                f"{_fmt_pct(edu_m.max_drawdown)} / {_fmt_pct(edu_m.delta_mdd)} | "
                f"**{edu_g.n_passed}/7** | "
                f"{spy_g.n_passed}/7 | "
                f"{ndx_g.n_passed}/7 | "
                f"{'✅' if spec_met else '❌'} |"
            )

    md.append("\n## Gate-by-gate breakdown (pass/fail matrix)\n")
    md.append(
        "For each (base, combo) × dataset, which specific gates fail? "
        "This matters because G1 PBO is grid-level (same verdict for all configs in "
        "a dataset) but G2-G7 are per-config.\n"
    )
    md.append(
        "| base | combo | dataset | G1 PBO | G2 DSR | G3 WF | G4 OOS | G5 FWD | G6 BS | G7 XLib |\n"
        "|---|---|---|---|---|---|---|---|---|---|"
    )
    for base in sorted(common_bases):
        for combo in PHASE3_COMBOS:
            key = (base, combo.label)
            for ds_label in ("educational", "spy_real", "ndx_real"):
                if key not in all_results[ds_label]:
                    continue
                _m, g = all_results[ds_label][key]
                icons = (
                    "✅" if g.g1_pbo else "❌",
                    "✅" if g.g2_dsr else "❌",
                    "✅" if g.g3_walk_forward else "❌",
                    "✅" if g.g4_oos_sharpe else "❌",
                    "✅" if g.g5_fwd_stress else "❌",
                    "✅" if g.g6_bootstrap else "❌",
                    "✅" if g.g7_cross_lib else "❌",
                )
                md.append(
                    f"| `{base}` | {combo.label} | {ds_label} | " +
                    " | ".join(icons) + " |"
                )

    md.append("\n## Verdict\n")
    if any_winner:
        md.append(
            f"✅ **{len(winner_lines)} (base, combo) pair(s) meet spec §0 across "
            "all 3 datasets.** List:\n"
        )
        for w in winner_lines:
            md.append(f"* `{w}`")
    else:
        md.append(
            "❌ **No (base, combo) pair meets spec §0 across all 3 datasets** "
            "(≥5/7 edu AND ≥4/7 spy AND ≥4/7 ndx simultaneously).\n"
            "Per-dataset winners exist (see per-dataset reports) but the "
            "cross-dataset honesty bar is not met — any candidate that passes "
            "in one dataset fails in another.\n"
        )

    md.append("\n---\n*Citations: spec §0, §6.1, §6.2. PBO grid-level per "
              "dataset. DSR uses cumulative `n_trials = %d`.*\n" % N_TRIALS_CUMULATIVE)
    out_path.write_text("\n".join(md), encoding="utf-8")
    log.info("wrote %s", out_path)
    log.info("TOTAL %.1fs", time.time() - t0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
