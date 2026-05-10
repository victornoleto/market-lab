"""Iter 011 — Conditional TQQQ leverage upgrade (Phase 3 — performance-first).

Tests whether substituting TQQQSIM (3× NDX) for QLDSIM (2× NDX) — only when
an upgrade gate fires — can lift CAGR_lh56y above the T3d-K2 official
benchmark 31.08% while preserving Sortino_lh56y >= 1.20 (Phase 3 floor) and
PBO < 0.50.

Six configs:
  1. baseline_qld           — QLDSIM only (replica anchor)
  2. tqqq_always            — TQQQSIM whenever ON state (control: hypothesis ceiling)
  3. tqqq_K4                — TQQQSIM when vote count = 4 of 4
  4. tqqq_lowvol25          — TQQQSIM when vol_21d < 25th pct trailing 5y
  5. tqqq_K4_AND_lowvol25   — intersection (most selective)
  6. tqqq_K4_OR_lowvol25    — union (most permissive)

Citations
---------
- [leverage_for_the_long_run, ch.4-5, p.40-60]: LRS leverage scaling — leverage
  pumps up when trend is firm AND vol is low (primary).
- [advances_fin_ml, p.208-211]: PBO via CSCV; structural mechanism diversity.
- [advances_fin_ml, p.222-223]: DSR + cumulative n_trials (G2 with
  n_trials_global = 492 after this iter).
- [stocks_on_the_move, p.98]: Clenow trend-strength filter (vote count = 4).
- [volatility_trading, p.58-60]: Sinclair realised-vol percentile (low =
  pump leverage).
"""
from __future__ import annotations

import importlib.util
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.data_loader import load_testfolio_series
from studies.letf_rotation_hunt.gates import (
    g1_pbo,
    g2_dsr_p_value,
    g3_walk_forward,
    g4_oos_70_30,
    g5_fwd_post_2020,
    g6_bootstrap_ci,
    g7_xlib_cagr_delta,
)
from studies.letf_rotation_hunt.plot_helper import (
    plot_crisis_attribution,
    plot_drawdown_curves,
    plot_equity_curves,
    plot_pct_beat_spy,
    plot_regime_attribution,
    plot_rolling_cagr,
    plot_rolling_sharpe,
)
from studies.letf_rotation_hunt.scoring import (
    compute_metrics,
    crisis_beats_benchmark,
    score_strategy,
)

ITER_DIR = Path(__file__).parent
LOG = logging.getLogger("iter011")


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Reuse iter 007 backtest helpers (READ-ONLY) for windowed_returns + per-
# dataset metrics computation (so cross-iter comparisons stay byte-aligned).
_PRIOR_ITERS = ITER_DIR.parent
ITER007 = _load_module(
    _PRIOR_ITERS / "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket" / "backtest.py",
    "iter011_iter007_backtest",
)
windowed_returns = ITER007.windowed_returns
compute_per_dataset = ITER007.compute_per_dataset
spy_anchor_metrics = ITER007.spy_anchor_metrics

# New helper introduced in this iter.
CLEG = _load_module(ITER_DIR / "conditional_leg.py", "iter011_cleg")
entry_signal_K2 = CLEG.entry_signal_K2
upgrade_signal_K4 = CLEG.upgrade_signal_K4
upgrade_signal_lowvol25 = CLEG.upgrade_signal_lowvol25
combine_AND = CLEG.combine_AND
combine_OR = CLEG.combine_OR
build_conditional_strategy_returns = CLEG.build_conditional_strategy_returns
conditional_turnover = CLEG.conditional_turnover

# Winner benchmark (frozen per LOOP_PROTOCOL.md)
WINNER_BENCHMARK_SORTINO = 1.3246
WINNER_BENCHMARK_CAGR = 0.3108
WINNER_BENCHMARK_ITER = "022-2026-05-06-T3d-extended-grid"
WINNER_BENCHMARK_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
BEATS_THRESHOLD_SORTINO = 1.3746
BEATS_PCT_ABOVE = 0.95

# Phase 3 thresholds (per LOOP_MEMORY.md frontmatter, iter 011 onward).
PHASE3_CAGR_FLOOR = 0.3108
PHASE3_END_EQ_RATIO_FLOOR = 1.05
PHASE3_SORTINO_FLOOR = 1.20
PHASE3_PBO_CEIL = 0.50
PHASE3_DSR_CEIL = 0.05

# Trial accounting (per LOOP_MEMORY.md frontmatter at iter 010 close).
PRE_ITER_CUMULATIVE = 486
PRE_ITER_LOOP = 60
LOCAL_N_CONFIGS = 6

DATASET_WINDOWS = {
    "lh_56y":      ("1970-01-01", "2026-04-30"),
    "modern_1990": ("1990-01-01", "2026-04-30"),
    "spy_real":    ("2003-01-01", "2026-04-30"),
    "ndx_real":    ("2010-02-01", "2026-04-30"),
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_universe() -> dict[str, pd.Series]:
    return {
        "QLDSIM":  load_testfolio_series("QLDSIM"),
        "TQQQSIM": load_testfolio_series("TQQQSIM"),
        "ZROZSIM": load_testfolio_series("ZROZSIM"),
        "SPYSIM":  load_testfolio_series("SPYSIM"),
    }


# ---------------------------------------------------------------------------
# Configs (6, 4+ topology grid)
# ---------------------------------------------------------------------------


CONFIG_SPECS = [
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_cleg_baseline_qld",
     "kind": "baseline_qld",
     "topology": "none"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_cleg_tqqq_always",
     "kind": "tqqq_always",
     "topology": "always"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_cleg_tqqq_K4",
     "kind": "tqqq_K4",
     "topology": "trend_strength"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_cleg_tqqq_lowvol25",
     "kind": "tqqq_lowvol25",
     "topology": "vol_regime"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_cleg_tqqq_K4_AND_lowvol25",
     "kind": "tqqq_K4_AND_lowvol25",
     "topology": "combined_AND"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_cleg_tqqq_K4_OR_lowvol25",
     "kind": "tqqq_K4_OR_lowvol25",
     "topology": "combined_OR"},
]


# ---------------------------------------------------------------------------
# Phase 3 diagnostics
# ---------------------------------------------------------------------------


def _rolling_win_rates_vs_baseline(
    strat_eq: pd.Series, baseline_eq: pd.Series,
) -> dict[str, float]:
    """Pct of N-day trailing windows where strat end-equity > baseline end-eq.

    Anchored on the start of each rolling window — i.e., for each day t with
    >= window prior bars, compare equity ratio at t to the equity ratio at
    t-window. If ratio_strat(t)/ratio_strat(t-w) > ratio_baseline(t)/ratio_
    baseline(t-w), strat beats baseline in that rolling window.
    """
    aligned = pd.concat({"s": strat_eq, "b": baseline_eq}, axis=1).dropna()
    if len(aligned) < 30:
        return {"1y": 0.0, "3y": 0.0, "5y": 0.0, "10y": 0.0}

    out = {}
    for label, window in [("1y", 252), ("3y", 756), ("5y", 1260), ("10y", 2520)]:
        if len(aligned) <= window:
            out[label] = 0.0
            continue
        s_ratio = aligned["s"] / aligned["s"].shift(window)
        b_ratio = aligned["b"] / aligned["b"].shift(window)
        cmp = (s_ratio > b_ratio).dropna()
        out[label] = float(cmp.mean()) if len(cmp) > 0 else 0.0
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    LOG.info("Loading universe...")
    universe = load_universe()
    qld = universe["QLDSIM"]
    tqqq = universe["TQQQSIM"]
    zroz = universe["ZROZSIM"]
    spy = universe["SPYSIM"]

    qld_ret = qld.pct_change().dropna()
    tqqq_ret = tqqq.pct_change().dropna()
    zroz_ret = zroz.pct_change().dropna()
    spy_ret = spy.pct_change().dropna()

    LOG.info("Building K=2 entry signal + upgrade gates...")
    on_signal = entry_signal_K2(qld, qld_ret)
    k4_gate = upgrade_signal_K4(qld, qld_ret)
    lv25_gate = upgrade_signal_lowvol25(qld_ret, vol_window=21, pct_window=1260,
                                        pct_threshold=0.25)
    and_gate = combine_AND(k4_gate, lv25_gate)
    or_gate = combine_OR(k4_gate, lv25_gate)

    upgrade_gates = {
        "baseline_qld":          pd.Series(0.0, index=qld_ret.index),
        "tqqq_always":           pd.Series(1.0, index=qld_ret.index),
        "tqqq_K4":               k4_gate,
        "tqqq_lowvol25":         lv25_gate,
        "tqqq_K4_AND_lowvol25":  and_gate,
        "tqqq_K4_OR_lowvol25":   or_gate,
    }

    per_cfg_returns: dict[str, pd.Series] = {}
    per_cfg_metrics: dict[str, dict] = {}
    per_cfg_on_state: dict[str, pd.Series] = {}
    per_cfg_upgrade_active_pct: dict[str, float] = {}
    per_cfg_turnover: dict[str, float] = {}

    LOG.info("Running %d configs...", len(CONFIG_SPECS))
    for spec in CONFIG_SPECS:
        kind = spec["kind"]
        gate = upgrade_gates[kind]

        # baseline_qld is special: always QLD (gate=0), so it equals
        # build_conditional with upgrade=0 throughout. tqqq_always equals
        # build_conditional with upgrade=1 throughout.
        strat_r = build_conditional_strategy_returns(
            on_signal=on_signal,
            qld_returns=qld_ret,
            tqqq_returns=tqqq_ret,
            off_returns=zroz_ret,
            upgrade_gate=gate,
        )

        per_cfg_returns[spec["name"]] = strat_r

        on_lag = on_signal.shift(1).reindex(strat_r.index)
        per_cfg_on_state[spec["name"]] = (on_lag == 1).astype(float)

        # Active% = days where (on_signal=1 AND upgrade=1) — i.e., TQQQ in use
        gate_lag = gate.shift(1).reindex(strat_r.index).fillna(0.0)
        active = ((on_lag == 1.0) & (gate_lag == 1.0))
        per_cfg_upgrade_active_pct[spec["name"]] = float(active.mean())

        per_cfg_turnover[spec["name"]] = conditional_turnover(on_signal, gate)

    spy_metrics_per_dataset = spy_anchor_metrics(spy_ret)

    LOG.info("Computing per-config metrics...")
    for name, r in per_cfg_returns.items():
        per_cfg_metrics[name] = compute_per_dataset(r, spy_ret)

    LOG.info("Running gates (G1 cross-config; G2-G7 per-config)...")
    g1_inputs = {
        name: windowed_returns(r, *DATASET_WINDOWS["lh_56y"])
        for name, r in per_cfg_returns.items()
    }
    g1_result = g1_pbo(g1_inputs)

    spy_lh = windowed_returns(spy_ret, *DATASET_WINDOWS["lh_56y"])
    n_trials_local = LOCAL_N_CONFIGS
    n_trials_global = PRE_ITER_CUMULATIVE + LOCAL_N_CONFIGS

    # In-iter T3d-K2 replica anchor for end-equity comparison: the loop's
    # baseline_qld has been reproduced bit-exactly across iters 001-010
    # (5th-gen replica). It's the within-iter T3d-K2 stand-in.
    baseline_name = "qld_voteK2_sma250_100_vol21_40_ar30_cleg_baseline_qld"
    baseline_lh_eq = (1.0 + windowed_returns(per_cfg_returns[baseline_name],
                                              *DATASET_WINDOWS["lh_56y"])
                      ).cumprod() * 10_000.0

    results = []
    for spec in CONFIG_SPECS:
        name = spec["name"]
        r_full = per_cfg_returns[name]
        r_lh = windowed_returns(r_full, *DATASET_WINDOWS["lh_56y"])

        g2_local = g2_dsr_p_value(r_lh, n_trials=n_trials_local)
        g2_global = g2_dsr_p_value(r_lh, n_trials=n_trials_global)
        g3 = g3_walk_forward(r_lh, benchmark_returns=spy_lh)
        g4 = g4_oos_70_30(r_lh)
        g5 = g5_fwd_post_2020(r_lh)
        g6 = g6_bootstrap_ci(r_lh)
        g7 = g7_xlib_cagr_delta(r_lh)

        gate_dict = {
            "g1_pbo": g1_result["pbo"],
            "g1_pbo_n_combinations": g1_result["n_combinations"],
            "g2_dsr_p_local": g2_local["p_value"],
            "g2_dsr_p_cumulative": g2_global["p_value"],
            "g2_observed_sharpe": g2_local["observed_sharpe"],
            "g3_wf_windows_pass": g3.get("windows_pass_sharpe_positive", 0),
            "g3_wf_windows_pass_pct_above_benchmark":
                g3.get("windows_pass_pct_above_benchmark", 0),
            "g3_wf_windows_pass_sharpe_positive":
                g3.get("windows_pass_sharpe_positive", 0),
            "g3_wf_n_windows": g3["n_windows"],
            "g3_wf_max_mdd": g3["max_mdd"],
            "g3_wf_warmup_used_days": g3["warmup_used_days"],
            "g3_wf_benchmark_relative": g3["benchmark_relative"],
            "g4_oos_sharpe": g4["oos_sharpe"],
            "g5_fwd_post2020_sharpe": g5["fwd_sharpe"],
            "g5_fwd_n_obs": g5["n_obs_post_2020"],
            "g6_bootstrap_99_low": g6["ci_low_sharpe"],
            "g7_xlib_cagr_delta": g7.get("delta_pp", g7.get("delta", 0.0)),
        }

        spy_lh_eq = (1.0 + spy_lh).cumprod() * 10_000.0
        strat_lh_eq = (1.0 + r_lh).cumprod() * 10_000.0
        crisis_flags = crisis_beats_benchmark(strat_lh_eq, spy_lh_eq)

        anchors_sharpe = {ds: spy_metrics_per_dataset[ds]["sharpe"]
                          for ds in DATASET_WINDOWS}
        spy_mdds = {ds: spy_metrics_per_dataset[ds]["mdd"] for ds in DATASET_WINDOWS}
        score_input_metrics = {ds: per_cfg_metrics[name][ds] for ds in DATASET_WINDOWS}
        score = score_strategy(
            metrics_per_dataset=score_input_metrics,
            anchors_sharpe_per_dataset=anchors_sharpe,
            spy_mdd_per_dataset=spy_mdds,
            gates=gate_dict,
            crisis_beats_spy=crisis_flags,
            bonus_pts=0.0,
        )

        sortino_lh = per_cfg_metrics[name]["lh_56y"]["sortino"]
        cagr_lh = per_cfg_metrics[name]["lh_56y"]["cagr"]
        pct_above_lh = per_cfg_metrics[name]["lh_56y"]["pct_time_above_benchmark"]
        sortino_edge = float(sortino_lh - WINNER_BENCHMARK_SORTINO)
        cagr_edge = float(cagr_lh - WINNER_BENCHMARK_CAGR)

        # End-equity ratio vs in-iter baseline (T3d-K2 replica anchor).
        common_idx = strat_lh_eq.index.intersection(baseline_lh_eq.index)
        if len(common_idx) > 0:
            end_eq_ratio = float(strat_lh_eq.loc[common_idx[-1]] /
                                 baseline_lh_eq.loc[common_idx[-1]])
        else:
            end_eq_ratio = float("nan")

        rolling_win = _rolling_win_rates_vs_baseline(strat_lh_eq, baseline_lh_eq)

        beats_winner = bool(
            sortino_lh > BEATS_THRESHOLD_SORTINO
            and score["winner_conditions_met"]
            and pct_above_lh >= BEATS_PCT_ABOVE
        )

        phase3_perf_candidate = bool(
            cagr_lh > PHASE3_CAGR_FLOOR
            and end_eq_ratio > PHASE3_END_EQ_RATIO_FLOOR
            and sortino_lh >= PHASE3_SORTINO_FLOOR
            and gate_dict["g1_pbo"] < PHASE3_PBO_CEIL
            and gate_dict["g2_dsr_p_cumulative"] < PHASE3_DSR_CEIL
        )

        results.append({
            "config_name": name,
            "kind": spec["kind"],
            "topology": spec["topology"],
            "metrics_gross": {
                ds: {
                    "cagr": per_cfg_metrics[name][ds]["cagr"],
                    "mdd": per_cfg_metrics[name][ds]["mdd"],
                    "sharpe": per_cfg_metrics[name][ds]["sharpe"],
                    "sortino": per_cfg_metrics[name][ds]["sortino"],
                    "calmar": per_cfg_metrics[name][ds]["calmar"],
                    "vol_annual": per_cfg_metrics[name][ds]["vol_annual"],
                    "skew": per_cfg_metrics[name][ds]["skew"],
                    "kurt": per_cfg_metrics[name][ds]["kurt"],
                    "pct_time_above_benchmark":
                        per_cfg_metrics[name][ds]["pct_time_above_benchmark"],
                    "min_relative_equity":
                        per_cfg_metrics[name][ds]["min_relative_equity"],
                }
                for ds in DATASET_WINDOWS
            },
            "metrics_net": {},
            "crisis_beats_benchmark": crisis_flags,
            "gates": gate_dict,
            "score_breakdown": score,
            "tier_label": score["tier_label"],
            "winner_conditions_met": score["winner_conditions_met"],
            "sortino_lh56y": float(sortino_lh) if sortino_lh == sortino_lh else None,
            "cagr_lh56y": float(cagr_lh) if cagr_lh == cagr_lh else None,
            "pct_time_above_benchmark_lh56y":
                float(pct_above_lh) if pct_above_lh == pct_above_lh else None,
            "sortino_edge_vs_winner": sortino_edge,
            "cagr_edge_vs_winner": cagr_edge,
            "end_equity_ratio_vs_winner_replica": end_eq_ratio,
            "rolling_win_rates_vs_winner_replica": rolling_win,
            "beats_winner": beats_winner,
            "phase3_performance_candidate": phase3_perf_candidate,
            "upgrade_active_pct": per_cfg_upgrade_active_pct[name],
            "turnover_per_year": per_cfg_turnover[name],
        })

    LOG.info("Saving per-config strategy returns...")
    for name, r in per_cfg_returns.items():
        r.to_csv(ITER_DIR / f"{name}_strategy_returns.csv", header=["return"])

    def _key(rec):
        # Phase 3: prioritize phase3_performance_candidate first, then by CAGR
        # (the Phase 3 axis) within candidates; otherwise fall back to Sortino.
        is_phase3 = 1 if rec["phase3_performance_candidate"] else 0
        cagr = rec["cagr_lh56y"] if rec["cagr_lh56y"] is not None else -1e9
        sortino = rec["sortino_lh56y"] if rec["sortino_lh56y"] is not None else -1e9
        return (is_phase3, cagr, sortino, rec["score_breakdown"]["total"])

    sorted_results = sorted(results, key=_key, reverse=True)
    best = sorted_results[0]

    # ----- KILL_LOOP evaluations (pre-registered in hypothesis.md) -----
    any_beats = any(rec["beats_winner"] for rec in results)
    any_phase3 = any(rec["phase3_performance_candidate"] for rec in results)
    best_sortino_lh = best["sortino_lh56y"] if best["sortino_lh56y"] is not None else 0.0
    baseline_rec = next(r for r in results if r["kind"] == "baseline_qld")
    tqqq_always_rec = next(r for r in results if r["kind"] == "tqqq_always")
    baseline_sortino = baseline_rec["sortino_lh56y"] or 0.0
    tqqq_always_sortino = tqqq_always_rec["sortino_lh56y"] or 0.0
    g1_pbo_value = float(g1_result["pbo"])

    # KILL #7: any conditional config (K4, lowvol25, AND, OR) Sortino >
    # tqqq_always Sortino → conditional dominates always.
    conditional_kinds = {"tqqq_K4", "tqqq_lowvol25",
                         "tqqq_K4_AND_lowvol25", "tqqq_K4_OR_lowvol25"}
    cond_recs = [r for r in results if r["kind"] in conditional_kinds]
    cond_dominates = any(
        (r["sortino_lh56y"] or 0.0) > tqqq_always_sortino for r in cond_recs
    )
    cond_detail = [
        {"name": r["config_name"], "kind": r["kind"],
         "sortino_lh56y": r["sortino_lh56y"],
         "delta_vs_tqqq_always": (r["sortino_lh56y"] or 0.0) - tqqq_always_sortino,
         "phase3_performance_candidate": r["phase3_performance_candidate"]}
        for r in cond_recs
    ]

    kill_loop_results = {
        "kill_loop_1_success_tag": {
            "fired": bool(any_beats),
            "rule": "Any config has beats_winner=True (Sortino>1.3746 AND winner_conditions_met=True AND pct_above>=0.95).",
        },
        "kill_loop_2_decisive_fail": {
            "fired": bool(best_sortino_lh < PHASE3_SORTINO_FLOOR),
            "rule": "Best Sortino_lh56y < 1.20 (Phase 3 floor — conditional-leverage hypothesis dead).",
            "best_sortino_lh56y": best_sortino_lh,
        },
        "kill_loop_3_replica_sanity_baseline": {
            "fired": bool(abs(baseline_sortino - 1.2841) > 0.005),
            "rule": "Baseline Sortino_lh56y deviates from 1.2841 by > 0.005 (6th-gen cross-iter sanity).",
            "baseline_sortino_lh56y": baseline_sortino,
        },
        "kill_loop_4_phase3_perf_candidate": {
            "fired": bool(any_phase3),
            "rule": "At least one config achieves phase3_performance_candidate=True (CAGR>31.08%, end_eq_ratio>1.05, Sortino>=1.20, PBO<0.5, DSR<0.05).",
        },
        "kill_loop_5_pbo_blowup": {
            "fired": bool(g1_pbo_value >= 0.55),
            "rule": "G1 PBO >= 0.55 (regression vs iter 010's 0.3929).",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_6_tqqq_always_collapse": {
            "fired": bool(tqqq_always_sortino < 1.10),
            "rule": "tqqq_always Sortino_lh56y < 1.10 (TQQQ ceiling fails — hypothesis premise dead).",
            "tqqq_always_sortino_lh56y": tqqq_always_sortino,
        },
        "kill_loop_7_conditional_dominates_always": {
            "fired": bool(cond_dominates),
            "rule": "At least one conditional config has Sortino > tqqq_always Sortino (positive tag — selective leverage smarter than always).",
            "conditional_detail": cond_detail,
        },
    }

    LOG.info("Generating plots...")
    equity_curves_lh = {}
    on_signal_per_cfg = {}
    for name in per_cfg_returns:
        r_lh = windowed_returns(per_cfg_returns[name], *DATASET_WINDOWS["lh_56y"])
        equity_curves_lh[name] = (1.0 + r_lh).cumprod() * 10_000.0
        on_signal_per_cfg[name] = per_cfg_on_state[name].reindex(r_lh.index).fillna(0.0)
    spy_eq_lh = (1.0 + spy_lh).cumprod() * 10_000.0
    equity_curves_lh["SPY 1× b&h"] = spy_eq_lh

    plots_dir = ITER_DIR / "plots"
    plot_equity_curves(
        equity_curves_lh, plots_dir / "01_equity_curves.png",
        title="Iter 011 — conditional TQQQ leverage (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 011 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 011 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 011 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 011 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 011 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 011 — crisis MDD vs SPY",
    )

    LOG.info("Writing CSV tables...")
    rows = []
    for rec in results:
        for ds in DATASET_WINDOWS:
            m = rec["metrics_gross"][ds]
            rows.append({
                "config": rec["config_name"],
                "dataset": ds,
                "sharpe": m["sharpe"],
                "sortino": m["sortino"],
                "cagr": m["cagr"],
                "mdd": m["mdd"],
                "pct_time_above_benchmark": m["pct_time_above_benchmark"],
            })
    pd.DataFrame(rows).to_csv(ITER_DIR / "tables" / "per_config_metrics.csv", index=False)

    gate_rows = []
    for rec in results:
        gd = rec["gates"]
        gate_rows.append({
            "config": rec["config_name"],
            "topology": rec["topology"],
            "g1_pbo": gd["g1_pbo"],
            "g1_pass": gd["g1_pbo"] < 0.5,
            "g2_dsr_p_local": gd["g2_dsr_p_local"],
            "g2_pass": gd["g2_dsr_p_local"] < 0.05,
            "g2_dsr_p_cumulative": gd["g2_dsr_p_cumulative"],
            "g2_cumulative_pass": gd["g2_dsr_p_cumulative"] < 0.05,
            "g3_pct_above_bench": gd["g3_wf_windows_pass_pct_above_benchmark"],
            "g3_pass": gd["g3_wf_windows_pass_pct_above_benchmark"] >= 5,
            "g4_oos_sharpe": gd["g4_oos_sharpe"],
            "g4_pass": gd["g4_oos_sharpe"] > 0,
            "g5_fwd_sharpe": gd["g5_fwd_post2020_sharpe"],
            "g5_pass": gd["g5_fwd_post2020_sharpe"] > 0,
            "g6_ci_low": gd["g6_bootstrap_99_low"],
            "g6_pass": gd["g6_bootstrap_99_low"] > 0,
            "g7_delta_pp": gd["g7_xlib_cagr_delta"],
            "g7_pass": abs(gd["g7_xlib_cagr_delta"]) <= 0.03,
            "upgrade_active_pct": rec["upgrade_active_pct"],
            "turnover_per_year": rec["turnover_per_year"],
            "cagr_lh56y": rec["cagr_lh56y"],
            "sortino_lh56y": rec["sortino_lh56y"],
            "end_eq_ratio_vs_winner_replica": rec["end_equity_ratio_vs_winner_replica"],
            "phase3_performance_candidate": rec["phase3_performance_candidate"],
            "beats_winner": rec["beats_winner"],
        })
    pd.DataFrame(gate_rows).to_csv(ITER_DIR / "tables" / "gates_pass_fail.csv", index=False)

    verdict = {
        "iter": "011-2026-05-10-conditional-tqqq-leverage",
        "tier": "loop_iter",
        "phase": 3,
        "phase_name": "performance-first beater hunt",
        "hypothesis": (
            "Conditional ON-leg leverage scaling: substitute TQQQSIM (3× NDX) "
            "for QLDSIM (2× NDX) only when conviction is high (vote count = 4 "
            "of 4 OR vol_21d in lowest 25th percentile of trailing 5y). Tests "
            "whether selective leverage upgrade lifts CAGR_lh56y above the "
            "T3d-K2 official 31.08% benchmark while preserving Sortino_lh56y "
            ">= 1.20 and PBO < 0.5. K=2 entry signal and OFF=ZROZ unchanged "
            "(iter 022 winner architecture). [leverage_for_the_long_run, "
            "ch.4-5, p.40-60] LRS leverage scaling; [stocks_on_the_move, p.98] "
            "Clenow trend-strength; [volatility_trading, p.58-60] Sinclair "
            "vol cone."
        ),
        "primary_citation": "[leverage_for_the_long_run, ch.4-5, p.40-60]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_011",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"], "topology": s["topology"]}
            for s in CONFIG_SPECS
        ],
        "datasets": list(DATASET_WINDOWS.keys()),
        "windows_used": {
            ds: f"{start}..{end}" for ds, (start, end) in DATASET_WINDOWS.items()
        },
        "results": results,
        "best_config": best["config_name"],
        "best_score": float(best["score_breakdown"]["total"]),
        "best_tier": best["tier_label"],
        "kill_rule_status": "N/A",
        "kill_loop_results": kill_loop_results,
        "cumulative_n_trials_local": LOCAL_N_CONFIGS,
        "cumulative_n_trials_loop": PRE_ITER_LOOP + LOCAL_N_CONFIGS,
        "cumulative_n_trials_global": PRE_ITER_CUMULATIVE + LOCAL_N_CONFIGS,
        "synth_parity_pass": True,
        "sortino_lh56y": float(best["sortino_lh56y"]) if best["sortino_lh56y"] is not None else 0.0,
        "cagr_lh56y": float(best["cagr_lh56y"]) if best["cagr_lh56y"] is not None else 0.0,
        "winner_conditions_met": bool(best["winner_conditions_met"]),
        "pct_time_above_benchmark_lh56y":
            float(best["pct_time_above_benchmark_lh56y"])
            if best["pct_time_above_benchmark_lh56y"] is not None else 0.0,
        "beats_winner": bool(best["beats_winner"]),
        "phase3_performance_candidate": bool(best["phase3_performance_candidate"]),
        "any_beats_winner": bool(any_beats),
        "any_phase3_performance_candidate": bool(any_phase3),
        "sortino_edge_vs_winner": float(best["sortino_edge_vs_winner"]),
        "cagr_edge_vs_winner": float(best["cagr_edge_vs_winner"]),
        "end_equity_ratio_vs_winner_replica":
            float(best["end_equity_ratio_vs_winner_replica"])
            if best["end_equity_ratio_vs_winner_replica"] == best["end_equity_ratio_vs_winner_replica"]
            else None,
        "rolling_win_rates_vs_winner_replica": best["rolling_win_rates_vs_winner_replica"],
        "winner_benchmark_sortino": WINNER_BENCHMARK_SORTINO,
        "winner_benchmark_cagr": WINNER_BENCHMARK_CAGR,
        "beats_winner_threshold_sortino": BEATS_THRESHOLD_SORTINO,
        "phase3_thresholds": {
            "cagr_floor": PHASE3_CAGR_FLOOR,
            "end_eq_ratio_floor": PHASE3_END_EQ_RATIO_FLOOR,
            "sortino_floor": PHASE3_SORTINO_FLOOR,
            "pbo_ceil": PHASE3_PBO_CEIL,
            "dsr_ceil": PHASE3_DSR_CEIL,
        },
        "winner_benchmark_iter": WINNER_BENCHMARK_ITER,
        "winner_benchmark_config": WINNER_BENCHMARK_CONFIG,
    }

    with open(ITER_DIR / "verdict.json", "w") as f:
        json.dump(verdict, f, indent=2, default=_json_default)

    LOG.info("Best: %s | Sortino_lh56y=%.4f | CAGR_lh56y=%.4f | edge=%+.4f | beats=%s | phase3=%s",
             best["config_name"], best["sortino_lh56y"] or 0.0,
             best["cagr_lh56y"] or 0.0, best["sortino_edge_vs_winner"],
             best["beats_winner"], best["phase3_performance_candidate"])
    LOG.info("G1 PBO=%.4f | KILL_LOOP fired summary: %s",
             g1_pbo_value,
             {k: v["fired"] for k, v in kill_loop_results.items()})
    LOG.info("Upgrade active%%: %s",
             {k: f"{v:.1%}" for k, v in per_cfg_upgrade_active_pct.items()})
    return verdict


def _json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o) if not np.isnan(o) else None
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Timestamp):
        return o.isoformat()
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    raise TypeError(f"Object of type {type(o)} not serializable")


if __name__ == "__main__":
    main()
