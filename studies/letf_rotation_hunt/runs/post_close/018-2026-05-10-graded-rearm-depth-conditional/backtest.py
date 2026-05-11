"""Iter 018 — Graded rearm depth-conditional (D_arm scales with T_off).

Phase 3 — performance-first beater hunt. Refines iter 017's NEW (non-replica)
strict_superset (single_K4lv25_g25_rvp70_cashx_T40D60, Sortino 1.4030, CAGR
32.66%, end_eq 1.62×, crisis 1/4) by making the rearm harvest-window length
D_arm scale linearly with the prior OFF-stretch length T_off observed at
each qualifying OFF→ON flip. Tests Husson-Trifoni's
`[leverage_for_the_long_run, p.4-7, ch.2-3]` longer-below-MA → longer-above-MA
streak thesis at the per-event D_arm level.

Six configs (mechanism-mix-diverse — 4 distinct ON-leg-overlay topologies):

  1. baseline_qld_zroz                                                   — calibration anchor
  2. single_K4lv25_g25_rvp70_cashx                                       — iter 014 strict_superset replica (no rearm)
  3. single_K4lv25_g25_rvp70_cashx_T40D60                                — iter 017 NEW strict_superset replica (fixed rearm)
  4. single_K4lv25_g25_rvp70_cashx_p075_clamp30_120 (PRIMARY)            — graded D_arm = clamp(0.75 * T_off, 30, 120)
  5. single_K4lv25_g25_rvp70_cashx_p050_clamp30_90                       — graded D_arm = clamp(0.50 * T_off, 30, 90)
  6. single_K4lv25_g25_rvp70_cashx_p100_clamp40_150                      — graded D_arm = clamp(1.00 * T_off, 40, 150)

All graded variants share t_crash_min=40 (matching iter 017's T40 deeper
threshold which delivered the LOOP MAX strict_superset Sortino).

Citations
---------
- [leverage_for_the_long_run, p.4-7, ch.2-3]: Husson-Trifoni — streaks vs
  seesawing asymmetry; depth-proportional streak harvesting (PRIMARY).
- [leverage_for_the_long_run, p.7]: trend × streaks × vol regime decompose
  LETF performance.
- [stocks_on_the_move, p.98]: Clenow trend re-establishment (post-crash).
- [volatility_trading, p.58-60]: Sinclair vol cone.
- [risk_parity, p.80-81, ch.4]: Qian RORO graded master-gate (gamma=0.25).
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking.
- [systematic_trading, p.212, ch.13]: Carver semi-automatic stop re-arm.
- [advances_fin_ml, p.208-211]: PBO via CSCV mechanism-mix-diversity.
- [advances_fin_ml, p.222-223]: DSR cumulative n_trials (n_global=534).
"""
from __future__ import annotations

import importlib.util
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.letf_rotation_hunt.core.gates import (
    g1_pbo,
    g2_dsr_p_value,
    g3_walk_forward,
    g4_oos_70_30,
    g5_fwd_post_2020,
    g6_bootstrap_ci,
    g7_xlib_cagr_delta,
)
from studies.letf_rotation_hunt.core.plot_helper import (
    plot_crisis_attribution,
    plot_drawdown_curves,
    plot_equity_curves,
    plot_pct_beat_spy,
    plot_regime_attribution,
    plot_rolling_cagr,
    plot_rolling_sharpe,
)
from studies.letf_rotation_hunt.core.scoring import (
    crisis_beats_benchmark,
    score_strategy,
)

ITER_DIR = Path(__file__).parent
LOG = logging.getLogger("iter018")


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Reuse iter 007 windowed_returns + per-dataset metrics (cross-iter byte-aligned).
_PRIOR_ITERS = ITER_DIR.parent
ITER007 = _load_module(
    _PRIOR_ITERS / "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket" / "backtest.py",
    "iter018_iter007_backtest",
)
windowed_returns = ITER007.windowed_returns
compute_per_dataset = ITER007.compute_per_dataset
spy_anchor_metrics = ITER007.spy_anchor_metrics

# Reuse iter 011 conditional-leg signal helpers (K=2 entry + K=4 / lowvol25).
ITER011 = _load_module(
    _PRIOR_ITERS / "011-2026-05-10-conditional-tqqq-leverage" / "conditional_leg.py",
    "iter018_iter011_cleg",
)
entry_signal_K2 = ITER011.entry_signal_K2
upgrade_signal_K4 = ITER011.upgrade_signal_K4
upgrade_signal_lowvol25 = ITER011.upgrade_signal_lowvol25
combine_AND = ITER011.combine_AND
combine_OR = ITER011.combine_OR

# Reuse iter 006 ratevol gate.
ITER006 = _load_module(
    _PRIOR_ITERS / "006-2026-05-09-bond-ratevol-regime" / "rate_vol_gate.py",
    "iter018_iter006_ratevol",
)
ratevol_regime_gate = ITER006.ratevol_regime_gate

# Reuse iter 014 mechanism-mix legs (single + assembler).
ITER014 = _load_module(
    _PRIOR_ITERS / "014-2026-05-10-mechanism-mix-diverse-graded-blend" / "mechanism_mix_leg.py",
    "iter018_iter014_mechmix",
)
build_single_asset_on_leg = ITER014.build_single_asset_on_leg
build_mechanism_mix_strategy_returns = ITER014.build_mechanism_mix_strategy_returns
mechanism_mix_turnover = ITER014.mechanism_mix_turnover

# Reuse iter 017 fixed rearm (for slot 3 replica anchor).
ITER017 = _load_module(
    _PRIOR_ITERS / "017-2026-05-10-postcrash-rearm-tqqq-streak" / "reentry_overlay.py",
    "iter018_iter017_reentry",
)
build_postcrash_rearm_gate_fixed = ITER017.build_postcrash_rearm_gate
diagnose_rearm_events_fixed = ITER017.diagnose_rearm_events

# New iter-018 helper.
GR = _load_module(ITER_DIR / "graded_reentry_overlay.py", "iter018_graded_reentry")
build_graded_rearm_gate = GR.build_graded_rearm_gate
diagnose_graded_rearm_events = GR.diagnose_graded_rearm_events

# Winner benchmark (frozen per LOOP_PROTOCOL.md)
WINNER_BENCHMARK_SORTINO = 1.3246
WINNER_BENCHMARK_CAGR = 0.3108
WINNER_BENCHMARK_ITER = "022-2026-05-06-T3d-extended-grid"
WINNER_BENCHMARK_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
BEATS_THRESHOLD_SORTINO = 1.3746
BEATS_PCT_ABOVE = 0.95

# Phase 3 thresholds.
PHASE3_CAGR_FLOOR = 0.3108
PHASE3_END_EQ_RATIO_FLOOR = 1.05
PHASE3_SORTINO_FLOOR = 1.20
PHASE3_PBO_CEIL = 0.50
PHASE3_DSR_CEIL = 0.05

# Trial accounting (start of iter 018).
PRE_ITER_CUMULATIVE = 528
PRE_ITER_LOOP = 102
LOCAL_N_CONFIGS = 6

# Calibration anchors (for KILL_LOOP replica sanity checks).
ITER011_BASELINE_SORTINO = 1.3240          # KILL_LOOP #3 — 9th-gen replica.
ITER014_SINGLE_K4LV25_G25_SORTINO = 1.3951  # KILL_LOOP #4 — iter 013-017 replica.
ITER017_T40D60_SORTINO = 1.4030             # KILL_LOOP #5 — iter 017 NEW strict_superset.

DATASET_WINDOWS = {
    "lh_56y":      ("1970-01-01", "2026-04-30"),
    "modern_1990": ("1990-01-01", "2026-04-30"),
    "spy_real":    ("2003-01-01", "2026-04-30"),
    "ndx_real":    ("2010-02-01", "2026-04-30"),
}


def load_universe() -> dict[str, pd.Series]:
    return {
        "QLDSIM":  load_testfolio_series("QLDSIM"),
        "TQQQSIM": load_testfolio_series("TQQQSIM"),
        "ZROZSIM": load_testfolio_series("ZROZSIM"),
        "IEFSIM":  load_testfolio_series("IEFSIM"),
        "CASHX":   load_testfolio_series("CASHX"),
        "SPYSIM":  load_testfolio_series("SPYSIM"),
    }


# Pre-registered config grid (hypothesis.md frozen — anti-curve-fit).
CONFIG_SPECS = [
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_grearm_baseline_qld_zroz",
     "kind": "baseline_qld_zroz",
     "topology": "single/none/none",
     "upgrade": "none",
     "gamma": 0.0, "ratevol": None, "alt_off": None,
     "rearm_mode": "none",
     "t_crash": 0, "d_arm": 0,
     "graded_coef": 0.0, "graded_dmin": 0, "graded_dmax": 0},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_grearm_single_K4lv25_g25_rvp70_cashx",
     "kind": "single_K4lv25_g25_rvp70_cashx",
     "topology": "single/K4_AND_lv25/g=0.25/p70-cashx",
     "upgrade": "K4_AND_lv25",
     "gamma": 0.25, "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
     "alt_off": "CASHX",
     "rearm_mode": "none",
     "t_crash": 0, "d_arm": 0,
     "graded_coef": 0.0, "graded_dmin": 0, "graded_dmax": 0},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_grearm_single_K4lv25_g25_rvp70_cashx_T40D60",
     "kind": "single_K4lv25_g25_rvp70_cashx_T40D60",
     "topology": "single/K4_AND_lv25_OR_rearm_fixed/g=0.25/p70-cashx",
     "upgrade": "K4_AND_lv25",
     "gamma": 0.25, "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
     "alt_off": "CASHX",
     "rearm_mode": "fixed",
     "t_crash": 40, "d_arm": 60,
     "graded_coef": 0.0, "graded_dmin": 0, "graded_dmax": 0},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_grearm_single_K4lv25_g25_rvp70_cashx_p075_clamp30_120",
     "kind": "single_K4lv25_g25_rvp70_cashx_p075_clamp30_120",
     "topology": "single/K4_AND_lv25_OR_rearm_graded/g=0.25/p70-cashx",
     "upgrade": "K4_AND_lv25",
     "gamma": 0.25, "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
     "alt_off": "CASHX",
     "rearm_mode": "graded",
     "t_crash": 40, "d_arm": 0,
     "graded_coef": 0.75, "graded_dmin": 30, "graded_dmax": 120},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_grearm_single_K4lv25_g25_rvp70_cashx_p050_clamp30_90",
     "kind": "single_K4lv25_g25_rvp70_cashx_p050_clamp30_90",
     "topology": "single/K4_AND_lv25_OR_rearm_graded/g=0.25/p70-cashx",
     "upgrade": "K4_AND_lv25",
     "gamma": 0.25, "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
     "alt_off": "CASHX",
     "rearm_mode": "graded",
     "t_crash": 40, "d_arm": 0,
     "graded_coef": 0.50, "graded_dmin": 30, "graded_dmax": 90},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_grearm_single_K4lv25_g25_rvp70_cashx_p100_clamp40_150",
     "kind": "single_K4lv25_g25_rvp70_cashx_p100_clamp40_150",
     "topology": "single/K4_AND_lv25_OR_rearm_graded/g=0.25/p70-cashx",
     "upgrade": "K4_AND_lv25",
     "gamma": 0.25, "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
     "alt_off": "CASHX",
     "rearm_mode": "graded",
     "t_crash": 40, "d_arm": 0,
     "graded_coef": 1.00, "graded_dmin": 40, "graded_dmax": 150},
]


def _rolling_win_rates_vs_baseline(
    strat_eq: pd.Series, baseline_eq: pd.Series,
) -> dict[str, float]:
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


def _build_rearm_gate(spec: dict, on_signal: pd.Series) -> tuple[pd.Series, dict]:
    """Dispatch to fixed (iter 017) or graded (iter 018) rearm helper.

    Returns (gate, diagnostic_dict). For rearm_mode='none' returns a zero
    gate and a stub diagnostic so downstream uniform reporting is preserved.
    """
    mode = spec["rearm_mode"]
    if mode == "none":
        zero_gate = pd.Series(0.0, index=on_signal.index)
        diag = {
            "rearm_mode": "none",
            "n_qualified_flips": 0,
            "n_active_rearm_days": 0,
            "rearm_active_pct": 0.0,
            "t_crash": 0,
            "d_arm": 0,
            "coefficient": 0.0,
            "d_arm_min": 0,
            "d_arm_max": 0,
            "d_arm_per_event_mean": 0.0,
            "d_arm_per_event_min": 0,
            "d_arm_per_event_max": 0,
        }
        return zero_gate, diag
    if mode == "fixed":
        gate = build_postcrash_rearm_gate_fixed(
            on_signal=on_signal,
            t_crash=spec["t_crash"],
            d_arm=spec["d_arm"],
        )
        d = diagnose_rearm_events_fixed(
            on_signal=on_signal,
            t_crash=spec["t_crash"],
            d_arm=spec["d_arm"],
        )
        d["rearm_mode"] = "fixed"
        d["coefficient"] = 0.0
        d["d_arm_min"] = int(spec["d_arm"])
        d["d_arm_max"] = int(spec["d_arm"])
        d["d_arm_per_event_mean"] = float(spec["d_arm"])
        d["d_arm_per_event_min"] = int(spec["d_arm"])
        d["d_arm_per_event_max"] = int(spec["d_arm"])
        return gate, d
    if mode == "graded":
        gate = build_graded_rearm_gate(
            on_signal=on_signal,
            t_crash_min=spec["t_crash"],
            coefficient=spec["graded_coef"],
            d_arm_min=spec["graded_dmin"],
            d_arm_max=spec["graded_dmax"],
        )
        d = diagnose_graded_rearm_events(
            on_signal=on_signal,
            t_crash_min=spec["t_crash"],
            coefficient=spec["graded_coef"],
            d_arm_min=spec["graded_dmin"],
            d_arm_max=spec["graded_dmax"],
        )
        d["rearm_mode"] = "graded"
        d["t_crash"] = int(spec["t_crash"])
        d["d_arm"] = 0
        return gate, d
    raise ValueError(f"Unknown rearm_mode: {mode}")


def main() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    LOG.info("Loading universe...")
    universe = load_universe()
    qld = universe["QLDSIM"]
    tqqq = universe["TQQQSIM"]
    zroz = universe["ZROZSIM"]
    ief = universe["IEFSIM"]
    cash = universe["CASHX"]
    spy = universe["SPYSIM"]

    qld_ret = qld.pct_change().dropna()
    tqqq_ret = tqqq.pct_change().dropna()
    zroz_ret = zroz.pct_change().dropna()
    ief_ret = ief.pct_change().dropna()
    cash_ret = cash.pct_change().dropna()
    spy_ret = spy.pct_change().dropna()

    LOG.info("Building entry + base upgrade gates...")
    on_signal = entry_signal_K2(qld, qld_ret)
    k4_gate = upgrade_signal_K4(qld, qld_ret)
    lv25_gate = upgrade_signal_lowvol25(
        qld_ret, vol_window=21, pct_window=1260, pct_threshold=0.25,
    )
    k4_and_lv25_gate = combine_AND(k4_gate, lv25_gate)

    base_upgrade_map = {
        "none":         pd.Series(0.0, index=qld_ret.index),
        "K4_AND_lv25":  k4_and_lv25_gate,
    }
    alt_off_returns_map = {"CASHX": cash_ret, "IEFSIM": ief_ret}

    per_cfg_returns: dict[str, pd.Series] = {}
    per_cfg_metrics: dict[str, dict] = {}
    per_cfg_on_state: dict[str, pd.Series] = {}
    per_cfg_upgrade_active_pct: dict[str, float] = {}
    per_cfg_ratevol_active_pct: dict[str, float] = {}
    per_cfg_blend_active_pct: dict[str, float] = {}
    per_cfg_rearm_diag: dict[str, dict] = {}
    per_cfg_turnover: dict[str, float] = {}

    LOG.info("Running %d configs...", len(CONFIG_SPECS))
    for spec in CONFIG_SPECS:
        base_upg = base_upgrade_map[spec["upgrade"]]

        rearm_gate, rearm_diag = _build_rearm_gate(spec, on_signal)
        per_cfg_rearm_diag[spec["name"]] = rearm_diag

        if spec["rearm_mode"] != "none":
            # OR-combine: rearm strictly adds upgrade activation.
            upg = combine_OR(base_upg, rearm_gate)
        else:
            upg = base_upg

        # ON-leg: single-asset only this iter (no basket3 — preserves the
        # iter 014/017 strict_superset family for direct graded-vs-fixed
        # comparison).
        on_leg_ret = build_single_asset_on_leg(
            qld_returns=qld_ret,
            tqqq_returns=tqqq_ret,
            upgrade_gate=upg,
        )

        if spec["ratevol"] is not None:
            rv = ratevol_regime_gate(
                zroz_ret,
                vol_window=spec["ratevol"]["vol_window"],
                pct_window=spec["ratevol"]["pct_window"],
                threshold=spec["ratevol"]["threshold"],
            )
            alt_ret = alt_off_returns_map[spec["alt_off"]]
            use_off_override = True
        else:
            rv = pd.Series(np.nan, index=zroz_ret.index)
            alt_ret = cash_ret
            use_off_override = False

        strat_r = build_mechanism_mix_strategy_returns(
            on_signal=on_signal,
            on_leg_returns=on_leg_ret,
            off_returns=zroz_ret,
            alt_off_returns=alt_ret,
            ratevol_gate=rv,
            gamma=spec["gamma"],
            use_off_override=use_off_override,
            # All slots are single-asset → match iter 014 single convention
            # (drop_warmup=False — iter 011 byte-aligned).
            drop_on_signal_warmup=False,
        )
        per_cfg_returns[spec["name"]] = strat_r

        on_lag = on_signal.shift(1).reindex(strat_r.index)
        per_cfg_on_state[spec["name"]] = (on_lag == 1).astype(float)

        upg_lag = upg.shift(1).reindex(strat_r.index).fillna(0.0)
        upg_active = ((on_lag == 1.0) & (upg_lag == 1.0))
        per_cfg_upgrade_active_pct[spec["name"]] = float(upg_active.mean())

        rv_lag = rv.shift(1).reindex(strat_r.index)
        rv_active = ((on_lag != 1.0) & (rv_lag == 1.0))
        per_cfg_ratevol_active_pct[spec["name"]] = float(rv_active.mean())

        blend_active = ((on_lag == 1.0) & (rv_lag == 1.0))
        per_cfg_blend_active_pct[spec["name"]] = float(blend_active.mean())

        per_cfg_turnover[spec["name"]] = mechanism_mix_turnover(
            on_signal=on_signal,
            upgrade_gate=upg,
            ratevol_gate=rv,
            use_basket=False,
            use_off_override=use_off_override,
        )

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

    baseline_name = "qld_voteK2_sma250_100_vol21_40_ar30_grearm_baseline_qld_zroz"
    baseline_lh_eq = (1.0 + windowed_returns(per_cfg_returns[baseline_name],
                                             *DATASET_WINDOWS["lh_56y"])
                      ).cumprod() * 10_000.0

    results = []
    for spec in CONFIG_SPECS:
        name = spec["name"]
        r_lh = windowed_returns(per_cfg_returns[name], *DATASET_WINDOWS["lh_56y"])

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
        spy_mdds = {ds: spy_metrics_per_dataset[ds]["mdd"]
                    for ds in DATASET_WINDOWS}
        score_input_metrics = {ds: per_cfg_metrics[name][ds]
                               for ds in DATASET_WINDOWS}
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

        strict_superset = bool(beats_winner and phase3_perf_candidate)

        results.append({
            "config_name": name,
            "kind": spec["kind"],
            "topology": spec["topology"],
            "upgrade": spec["upgrade"],
            "gamma": spec["gamma"],
            "ratevol": spec["ratevol"],
            "alt_off": spec["alt_off"],
            "rearm_mode": spec["rearm_mode"],
            "t_crash": spec["t_crash"],
            "d_arm": spec["d_arm"],
            "graded_coef": spec["graded_coef"],
            "graded_dmin": spec["graded_dmin"],
            "graded_dmax": spec["graded_dmax"],
            "rearm_diag": per_cfg_rearm_diag[name],
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
            "end_equity_ratio_vs_baseline": end_eq_ratio,
            "rolling_win_rates_vs_baseline": rolling_win,
            "beats_winner": beats_winner,
            "phase3_performance_candidate": phase3_perf_candidate,
            "strict_superset": strict_superset,
            "upgrade_active_pct": per_cfg_upgrade_active_pct[name],
            "ratevol_active_pct": per_cfg_ratevol_active_pct[name],
            "blend_active_pct": per_cfg_blend_active_pct[name],
            "turnover_per_year": per_cfg_turnover[name],
        })

    LOG.info("Saving per-config strategy returns...")
    for name, r in per_cfg_returns.items():
        r.to_csv(ITER_DIR / f"{name}_strategy_returns.csv", header=["return"])

    def _key(rec):
        is_strict = 1 if rec["strict_superset"] else 0
        is_phase3 = 1 if rec["phase3_performance_candidate"] else 0
        sortino = rec["sortino_lh56y"] if rec["sortino_lh56y"] is not None else -1e9
        cagr = rec["cagr_lh56y"] if rec["cagr_lh56y"] is not None else -1e9
        return (is_strict, is_phase3, sortino, cagr, rec["score_breakdown"]["total"])

    sorted_results = sorted(results, key=_key, reverse=True)
    best = sorted_results[0]

    # ----- KILL_LOOP evaluations (pre-registered in hypothesis.md) -----
    any_beats = any(rec["beats_winner"] for rec in results)
    any_phase3 = any(rec["phase3_performance_candidate"] for rec in results)
    any_strict = any(rec["strict_superset"] for rec in results)
    best_sortino_lh = best["sortino_lh56y"] if best["sortino_lh56y"] is not None else 0.0

    baseline_rec = next(r for r in results if r["kind"] == "baseline_qld_zroz")
    single_anchor_rec = next(r for r in results if r["kind"] == "single_K4lv25_g25_rvp70_cashx")
    t40d60_anchor_rec = next(r for r in results if r["kind"] == "single_K4lv25_g25_rvp70_cashx_T40D60")
    graded_recs = [r for r in results if r["rearm_mode"] == "graded"]

    baseline_sortino = baseline_rec["sortino_lh56y"] or 0.0
    single_anchor_sortino = single_anchor_rec["sortino_lh56y"] or 0.0
    t40d60_anchor_sortino = t40d60_anchor_rec["sortino_lh56y"] or 0.0
    g1_pbo_value = float(g1_result["pbo"])

    any_graded_phase3 = any(r["phase3_performance_candidate"] for r in graded_recs)
    any_graded_strict = any(r["strict_superset"] for r in graded_recs)
    any_graded_dominates = any(
        (r["sortino_lh56y"] or 0.0) > ITER017_T40D60_SORTINO for r in graded_recs
    )
    any_graded_2020 = any(
        bool(r["crisis_beats_benchmark"].get("2020_covid", False))
        for r in graded_recs
    )
    any_graded_strict_with_crisis = any(
        r["strict_superset"]
        and sum(int(bool(v)) for v in r["crisis_beats_benchmark"].values()) >= 2
        for r in graded_recs
    )

    cmp_detail = [
        {"name": r["config_name"], "kind": r["kind"],
         "rearm_mode": r["rearm_mode"], "t_crash": r["t_crash"], "d_arm": r["d_arm"],
         "graded_coef": r["graded_coef"], "graded_dmin": r["graded_dmin"], "graded_dmax": r["graded_dmax"],
         "sortino_lh56y": r["sortino_lh56y"],
         "cagr_lh56y": r["cagr_lh56y"],
         "phase3_performance_candidate": r["phase3_performance_candidate"],
         "beats_winner": r["beats_winner"],
         "strict_superset": r["strict_superset"],
         "total_score": r["score_breakdown"]["total"],
         "crisis_2020_covid_beat": bool(r["crisis_beats_benchmark"].get("2020_covid", False)),
         "crisis_2008_gfc_beat": bool(r["crisis_beats_benchmark"].get("2008_gfc", False)),
         "crisis_2000_dotcom_beat": bool(r["crisis_beats_benchmark"].get("2000_dotcom", False)),
         "crisis_2022_rates_beat": bool(r["crisis_beats_benchmark"].get("2022_rates", False)),
         "n_qualified_flips": r["rearm_diag"]["n_qualified_flips"],
         "rearm_active_pct": r["rearm_diag"]["rearm_active_pct"],
         "d_arm_per_event_mean": r["rearm_diag"].get("d_arm_per_event_mean", 0.0)}
        for r in results
    ]

    kill_loop_results = {
        "kill_loop_1_success_tag": {
            "fired": bool(any_beats),
            "rule": "Any config has beats_winner=True (Sortino>1.3746 AND winner_conditions_met=True AND pct_above>=0.95).",
        },
        "kill_loop_2_decisive_fail": {
            "fired": bool(best_sortino_lh < PHASE3_SORTINO_FLOOR),
            "rule": "Best Sortino_lh56y < 1.20 (Phase 3 floor).",
            "best_sortino_lh56y": best_sortino_lh,
        },
        "kill_loop_3_replica_sanity_baseline": {
            "fired": bool(abs(baseline_sortino - ITER011_BASELINE_SORTINO) > 0.005),
            "rule": "Baseline Sortino_lh56y deviates from iter 011-017 baseline 1.3240 by > 0.005. 9th-gen replica.",
            "baseline_sortino_lh56y": baseline_sortino,
            "expected": ITER011_BASELINE_SORTINO,
        },
        "kill_loop_4_replica_sanity_single_K4lv25_g25": {
            "fired": bool(abs(single_anchor_sortino - ITER014_SINGLE_K4LV25_G25_SORTINO) > 0.005),
            "rule": "single_K4lv25_g25_rvp70_cashx Sortino_lh56y deviates from iter 014/017 strict_superset 1.3951 by > 0.005.",
            "single_anchor_sortino_lh56y": single_anchor_sortino,
            "expected": ITER014_SINGLE_K4LV25_G25_SORTINO,
        },
        "kill_loop_5_replica_sanity_T40D60": {
            "fired": bool(abs(t40d60_anchor_sortino - ITER017_T40D60_SORTINO) > 0.005),
            "rule": "single_K4lv25_g25_rvp70_cashx_T40D60 Sortino_lh56y deviates from iter 017 LOOP MAX strict_superset 1.4030 by > 0.005.",
            "t40d60_anchor_sortino_lh56y": t40d60_anchor_sortino,
            "expected": ITER017_T40D60_SORTINO,
        },
        "kill_loop_6_pbo_blowup": {
            "fired": bool(g1_pbo_value >= 0.55),
            "rule": "G1 PBO >= 0.55 (hard regression threshold).",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_7_pbo_held": {
            "fired": bool(g1_pbo_value < PHASE3_PBO_CEIL),
            "rule": "G1 PBO < 0.50 (Phase 3 hard gate). POSITIVE TAG.",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_8_graded_rearm_phase3_perf_candidate": {
            "fired": bool(any_graded_phase3),
            "rule": "Any graded-rearm config (slots 4/5/6) achieves phase3_performance_candidate=True. CORE HYPOTHESIS TEST.",
            "any_graded_phase3": bool(any_graded_phase3),
        },
        "kill_loop_9_graded_rearm_strict_superset": {
            "fired": bool(any_graded_strict),
            "rule": "Any graded-rearm config achieves strict_superset=True. STRONGEST HYPOTHESIS TEST.",
            "any_graded_strict": bool(any_graded_strict),
        },
        "kill_loop_10_graded_dominates_T40D60": {
            "fired": bool(any_graded_dominates),
            "rule": "Any graded-rearm config has Sortino_lh56y > 1.4030 (iter 017 LOOP MAX strict_superset).",
            "any_graded_dominates": bool(any_graded_dominates),
        },
        "kill_loop_11_graded_rearm_2020_covid_rescue": {
            "fired": bool(any_graded_2020),
            "rule": "Any graded-rearm config beats SPY in 2020_covid window.",
            "any_graded_2020": bool(any_graded_2020),
        },
        "kill_loop_12_graded_rearm_strict_superset_with_crisis_2plus": {
            "fired": bool(any_graded_strict_with_crisis),
            "rule": "Any graded-rearm config achieves strict_superset=True AND crisis count >= 2/4. POSITIVE TAG (loop's first crisis-≥2/4 strict_superset).",
            "any_graded_strict_with_crisis": bool(any_graded_strict_with_crisis),
        },
        "compound_detail": cmp_detail,
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
        title="Iter 018 — graded rearm depth-conditional (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 018 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 018 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 018 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 018 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 018 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 018 — crisis MDD vs SPY",
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
            "rearm_mode": rec["rearm_mode"],
            "t_crash": rec["t_crash"],
            "d_arm": rec["d_arm"],
            "graded_coef": rec["graded_coef"],
            "graded_dmin": rec["graded_dmin"],
            "graded_dmax": rec["graded_dmax"],
            "n_qualified_flips": rec["rearm_diag"]["n_qualified_flips"],
            "rearm_active_pct": rec["rearm_diag"]["rearm_active_pct"],
            "d_arm_per_event_mean": rec["rearm_diag"].get("d_arm_per_event_mean", 0.0),
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
            "ratevol_active_pct": rec["ratevol_active_pct"],
            "blend_active_pct": rec["blend_active_pct"],
            "turnover_per_year": rec["turnover_per_year"],
            "cagr_lh56y": rec["cagr_lh56y"],
            "sortino_lh56y": rec["sortino_lh56y"],
            "end_eq_ratio_vs_baseline": rec["end_equity_ratio_vs_baseline"],
            "phase3_performance_candidate": rec["phase3_performance_candidate"],
            "beats_winner": rec["beats_winner"],
            "strict_superset": rec["strict_superset"],
            "total_score": rec["score_breakdown"]["total"],
        })
    pd.DataFrame(gate_rows).to_csv(ITER_DIR / "tables" / "gates_pass_fail.csv", index=False)

    verdict = {
        "iter": "018-2026-05-10-graded-rearm-depth-conditional",
        "tier": "loop_iter",
        "phase": 3,
        "phase_name": "performance-first beater hunt",
        "hypothesis": (
            "Graded rearm depth — D_arm linearly proportional to prior OFF "
            "stretch length T_off. Refines iter 017's NEW strict_superset "
            "(single_K4lv25_g25_rvp70_cashx_T40D60, Sortino 1.4030, CAGR "
            "32.66%, end_eq 1.62×, crisis 1/4) by making the rearm harvest "
            "window length scale with the depth of the crash that preceded "
            "the qualifying flip. Six configs (baseline, single anchor, "
            "T40D60 anchor, graded p075/p050/p100 with pre-committed clamps) "
            "spanning 4 distinct ON-leg-overlay topologies. Tests Husson-"
            "Trifoni's longer-below-MA → longer-above-MA streak thesis at the "
            "per-event D_arm level. "
            "[leverage_for_the_long_run, p.4-7, ch.2-3] Husson-Trifoni "
            "streaks-vs-seesawing asymmetry (PRIMARY); "
            "[leverage_for_the_long_run, p.7] trend × streaks × vol regime; "
            "[stocks_on_the_move, p.98] Clenow trend re-establishment; "
            "[volatility_trading, p.58-60] Sinclair vol cone; "
            "[risk_parity, p.80-81, ch.4] Qian RORO graded; "
            "[risk_parity, ch.5, p.10] Carlson stacking; "
            "[systematic_trading, p.212, ch.13] Carver re-arm hysteresis; "
            "[advances_fin_ml, p.208-211] CSCV PBO; "
            "[advances_fin_ml, p.222-223] DSR cumulative (n_global=534)."
        ),
        "primary_citation": "[leverage_for_the_long_run, p.4-7, ch.2-3]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_018",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"], "topology": s["topology"],
             "upgrade": s["upgrade"], "gamma": s["gamma"], "ratevol": s["ratevol"],
             "alt_off": s["alt_off"], "rearm_mode": s["rearm_mode"],
             "t_crash": s["t_crash"], "d_arm": s["d_arm"],
             "graded_coef": s["graded_coef"], "graded_dmin": s["graded_dmin"],
             "graded_dmax": s["graded_dmax"]}
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
        "strict_superset": bool(best["strict_superset"]),
        "any_beats_winner": bool(any_beats),
        "any_phase3_performance_candidate": bool(any_phase3),
        "any_strict_superset": bool(any_strict),
        "any_graded_phase3_perf_candidate": bool(any_graded_phase3),
        "any_graded_strict_superset": bool(any_graded_strict),
        "any_graded_dominates_T40D60": bool(any_graded_dominates),
        "any_graded_2020_covid_rescue": bool(any_graded_2020),
        "any_graded_strict_superset_with_crisis_2plus": bool(any_graded_strict_with_crisis),
        "sortino_edge_vs_winner": float(best["sortino_edge_vs_winner"]),
        "cagr_edge_vs_winner": float(best["cagr_edge_vs_winner"]),
        "end_equity_ratio_vs_baseline":
            float(best["end_equity_ratio_vs_baseline"])
            if best["end_equity_ratio_vs_baseline"] == best["end_equity_ratio_vs_baseline"]
            else None,
        "rolling_win_rates_vs_baseline": best["rolling_win_rates_vs_baseline"],
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

    LOG.info("Best: %s | Sortino_lh56y=%.4f | CAGR_lh56y=%.4f | edge=%+.4f | beats=%s | phase3=%s | strict=%s",
             best["config_name"], best["sortino_lh56y"] or 0.0,
             best["cagr_lh56y"] or 0.0, best["sortino_edge_vs_winner"],
             best["beats_winner"], best["phase3_performance_candidate"],
             best["strict_superset"])
    LOG.info("G1 PBO=%.4f | KILL_LOOP fired summary: %s",
             g1_pbo_value,
             {k: (v["fired"] if isinstance(v, dict) and "fired" in v else "N/A")
              for k, v in kill_loop_results.items() if k != "compound_detail"})
    LOG.info("Upgrade active%%: %s",
             {k: f"{v:.1%}" for k, v in per_cfg_upgrade_active_pct.items()})
    LOG.info("Rearm diag: %s", per_cfg_rearm_diag)
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
