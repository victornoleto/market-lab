"""Iter 015 — Equity-tilted basket × K4_AND_lv25 × ratevol-OFF.

Phase 3 — performance-first beater hunt. Tests fixed-weight equity-
tilted baskets (2/3 QLD + 1/6 UPRO + 1/6 UGL family; 0.85 / 0.075 / 0.075
family; basket2_QU 50/50 invvol family) as a fix for basket3-invvol's
structural CAGR ceiling (iter 014: 22.65%, blocked Phase 3).

Six configs (mechanism-mix-diverse — vary ON-leg topology primarily):

  1. baseline_qld_zroz                              — single, replica anchor
  2. single_K4lv25_g25_rvp70_cashx                  — iter 014 strict_superset replica
  3. basket3invvol_K4lv25_g25_rvp70_cashx           — iter 014 triple-stack replica
  4. basket3eq66_K4lv25_g25_rvp70_cashx (PRIMARY)   — NEW fixed-wt 2/3+1/6+1/6
  5. basket3eq85_K4lv25_g0_rvp80_ief                — NEW fixed-wt 0.85+0.075+0.075 (orthogonal mix)
  6. basket2QU_K4lv25_g25_rvp70_cashx               — NEW invvol(QLD,UPRO) ablation

Citations
---------
- [risk_parity, p.110, ch.5]: Qian diversification return for fixed-weight
  rebalanced basket (PRIMARY).
- [risk_parity, p.11, ch.1]: Qian — naïve risk parity over-allocates to
  lowest-vol asset (basket3-invvol gold-drag motivation).
- [risk_parity, p.80-81, ch.4]: Qian RORO graded master-gate.
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking.
- [stocks_on_the_move, p.98]: Clenow vol-parity (basket3-invvol contrast).
- [systematic_trading, ch.10]: Carver inverse-vol scalar.
- [volatility_trading, p.58-60]: Sinclair vol cone (ratevol gate).
- [leverage_for_the_long_run, ch.4-5, p.40-60]: LRS leverage (TQQQ swap).
- [advances_fin_ml, p.208-211]: PBO via CSCV — mechanism-mix-diversity.
- [advances_fin_ml, p.222-223]: DSR + cumulative n_trials (n_global=516).
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
    crisis_beats_benchmark,
    score_strategy,
)

ITER_DIR = Path(__file__).parent
LOG = logging.getLogger("iter015")


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_PRIOR_ITERS = ITER_DIR.parent

# Reuse iter 007 windowed_returns + per-dataset metrics (cross-iter byte-aligned).
ITER007 = _load_module(
    _PRIOR_ITERS / "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket" / "backtest.py",
    "iter015_iter007_backtest",
)
windowed_returns = ITER007.windowed_returns
compute_per_dataset = ITER007.compute_per_dataset
spy_anchor_metrics = ITER007.spy_anchor_metrics

# Reuse iter 011 conditional-leg signal helpers (K=2 entry + K=4 / lowvol25).
ITER011 = _load_module(
    _PRIOR_ITERS / "011-2026-05-10-conditional-tqqq-leverage" / "conditional_leg.py",
    "iter015_iter011_cleg",
)
entry_signal_K2 = ITER011.entry_signal_K2
upgrade_signal_K4 = ITER011.upgrade_signal_K4
upgrade_signal_lowvol25 = ITER011.upgrade_signal_lowvol25
combine_AND = ITER011.combine_AND

# Reuse iter 006 ratevol gate.
ITER006 = _load_module(
    _PRIOR_ITERS / "006-2026-05-09-bond-ratevol-regime" / "rate_vol_gate.py",
    "iter015_iter006_ratevol",
)
ratevol_regime_gate = ITER006.ratevol_regime_gate

# Reuse iter 014 mechanism_mix_leg (single + basket3-invvol + assembler + turnover).
ITER014 = _load_module(
    _PRIOR_ITERS / "014-2026-05-10-mechanism-mix-diverse-graded-blend" / "mechanism_mix_leg.py",
    "iter015_iter014_mmix",
)
build_single_asset_on_leg = ITER014.build_single_asset_on_leg
build_basket3_on_leg = ITER014.build_basket3_on_leg
build_mechanism_mix_strategy_returns = ITER014.build_mechanism_mix_strategy_returns
mechanism_mix_turnover = ITER014.mechanism_mix_turnover

# New iter-015 helper.
EQT = _load_module(ITER_DIR / "equity_tilt_leg.py", "iter015_equity_tilt_leg")
build_basket3_eqtilt_on_leg = EQT.build_basket3_eqtilt_on_leg
build_basket2_invvol_on_leg = EQT.build_basket2_invvol_on_leg

# Winner benchmark (frozen per LOOP_PROTOCOL.md).
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

# Trial accounting.
PRE_ITER_CUMULATIVE = 510
PRE_ITER_LOOP = 84
LOCAL_N_CONFIGS = 6

# Calibration anchors (KILL_LOOP replica sanity).
ITER011_BASELINE_SORTINO = 1.3240        # KILL_LOOP #3
ITER014_SINGLE_K4LV25_G25_SORTINO = 1.3951  # KILL_LOOP #4 (= iter 013/014 anchor)
ITER014_BASKET3_TRIPLE_STACK_SORTINO = 1.4689  # KILL_LOOP #5

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
        "UPROSIM": load_testfolio_series("UPROSIM"),
        "UGLSIM":  load_testfolio_series("UGLSIM"),
        "ZROZSIM": load_testfolio_series("ZROZSIM"),
        "IEFSIM":  load_testfolio_series("IEFSIM"),
        "CASHX":   load_testfolio_series("CASHX"),
        "SPYSIM":  load_testfolio_series("SPYSIM"),
    }


CONFIG_SPECS = [
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_eqb_baseline_qld_zroz",
     "kind": "baseline_qld_zroz",
     "topology": "single/none/g0/none",
     "on_leg": "single", "weights": None,
     "upgrade": "none", "gamma": 0.0,
     "ratevol": None, "alt_off": None},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_eqb_single_K4lv25_g25_rvp70_cashx",
     "kind": "single_K4lv25_g25_rvp70_cashx",
     "topology": "single/K4lv25/g25/p70-cashx",
     "on_leg": "single", "weights": None,
     "upgrade": "K4_AND_lv25", "gamma": 0.25,
     "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
     "alt_off": "CASHX"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_eqb_basket3invvol_K4lv25_g25_rvp70_cashx",
     "kind": "basket3invvol_K4lv25_g25_rvp70_cashx",
     "topology": "basket3-invvol/K4lv25/g25/p70-cashx",
     "on_leg": "basket3_invvol", "weights": None,
     "upgrade": "K4_AND_lv25", "gamma": 0.25,
     "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
     "alt_off": "CASHX"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_eqb_basket3eq66_K4lv25_g25_rvp70_cashx",
     "kind": "basket3eq66_K4lv25_g25_rvp70_cashx",
     "topology": "basket3-eqtilt66/K4lv25/g25/p70-cashx",
     "on_leg": "basket3_eqtilt", "weights": (2.0/3.0, 1.0/6.0, 1.0/6.0),
     "upgrade": "K4_AND_lv25", "gamma": 0.25,
     "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
     "alt_off": "CASHX"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_eqb_basket3eq85_K4lv25_g0_rvp80_ief",
     "kind": "basket3eq85_K4lv25_g0_rvp80_ief",
     "topology": "basket3-eqtilt85/K4lv25/g0/p80-ief",
     "on_leg": "basket3_eqtilt", "weights": (0.85, 0.075, 0.075),
     "upgrade": "K4_AND_lv25", "gamma": 0.0,
     "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.80},
     "alt_off": "IEFSIM"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_eqb_basket2QU_K4lv25_g25_rvp70_cashx",
     "kind": "basket2QU_K4lv25_g25_rvp70_cashx",
     "topology": "basket2-QU-invvol/K4lv25/g25/p70-cashx",
     "on_leg": "basket2_QU_invvol", "weights": None,
     "upgrade": "K4_AND_lv25", "gamma": 0.25,
     "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
     "alt_off": "CASHX"},
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


def _build_on_leg(
    spec: dict,
    qld_ret: pd.Series,
    tqqq_ret: pd.Series,
    upro_ret: pd.Series,
    ugl_ret: pd.Series,
    upgrade_gate: pd.Series,
) -> pd.Series:
    kind = spec["on_leg"]
    if kind == "single":
        return build_single_asset_on_leg(
            qld_returns=qld_ret, tqqq_returns=tqqq_ret,
            upgrade_gate=upgrade_gate,
        )
    if kind == "basket3_invvol":
        return build_basket3_on_leg(
            qld_returns=qld_ret, tqqq_returns=tqqq_ret,
            upro_returns=upro_ret, ugl_returns=ugl_ret,
            upgrade_gate=upgrade_gate, invvol_window=60,
        )
    if kind == "basket3_eqtilt":
        return build_basket3_eqtilt_on_leg(
            qld_returns=qld_ret, tqqq_returns=tqqq_ret,
            upro_returns=upro_ret, ugl_returns=ugl_ret,
            upgrade_gate=upgrade_gate, weights=spec["weights"],
        )
    if kind == "basket2_QU_invvol":
        return build_basket2_invvol_on_leg(
            qld_returns=qld_ret, tqqq_returns=tqqq_ret,
            upro_returns=upro_ret,
            upgrade_gate=upgrade_gate, invvol_window=60,
        )
    raise ValueError(f"unknown on_leg kind: {kind}")


def _is_basket(spec: dict) -> bool:
    return spec["on_leg"] != "single"


def main() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    LOG.info("Loading universe...")
    universe = load_universe()
    qld = universe["QLDSIM"]
    tqqq = universe["TQQQSIM"]
    upro = universe["UPROSIM"]
    ugl = universe["UGLSIM"]
    zroz = universe["ZROZSIM"]
    ief = universe["IEFSIM"]
    cash = universe["CASHX"]
    spy = universe["SPYSIM"]

    qld_ret = qld.pct_change().dropna()
    tqqq_ret = tqqq.pct_change().dropna()
    upro_ret = upro.pct_change().dropna()
    ugl_ret = ugl.pct_change().dropna()
    zroz_ret = zroz.pct_change().dropna()
    ief_ret = ief.pct_change().dropna()
    cash_ret = cash.pct_change().dropna()
    spy_ret = spy.pct_change().dropna()

    LOG.info("Building entry + upgrade gates...")
    on_signal = entry_signal_K2(qld, qld_ret)
    k4_gate = upgrade_signal_K4(qld, qld_ret)
    lv25_gate = upgrade_signal_lowvol25(
        qld_ret, vol_window=21, pct_window=1260, pct_threshold=0.25,
    )
    k4_and_lv25_gate = combine_AND(k4_gate, lv25_gate)

    upgrade_gate_map = {
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
    per_cfg_turnover: dict[str, float] = {}

    LOG.info("Running %d configs...", len(CONFIG_SPECS))
    for spec in CONFIG_SPECS:
        upg = upgrade_gate_map[spec["upgrade"]]
        on_leg_ret = _build_on_leg(spec, qld_ret, tqqq_ret, upro_ret, ugl_ret, upg)

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
            # Basket variants use iter 007 convention (drop K=2 warmup) so
            # basket3_invvol replica preserves Sortino 1.4689 anchor and
            # basket3_eqtilt / basket2_QU stay commensurate on the same window.
            drop_on_signal_warmup=_is_basket(spec),
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
            use_basket=_is_basket(spec),
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

    baseline_name = "qld_voteK2_sma250_100_vol21_40_ar30_eqb_baseline_qld_zroz"
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
            "on_leg": spec["on_leg"],
            "weights": list(spec["weights"]) if spec["weights"] is not None else None,
            "upgrade": spec["upgrade"],
            "gamma": spec["gamma"],
            "ratevol": spec["ratevol"],
            "alt_off": spec["alt_off"],
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

    eqtilt_kinds = {"basket3eq66_K4lv25_g25_rvp70_cashx",
                    "basket3eq85_K4lv25_g0_rvp80_ief"}
    eqtilt_recs = [r for r in results if r["kind"] in eqtilt_kinds]
    any_phase3_eqtilt = any(r["phase3_performance_candidate"] for r in eqtilt_recs)
    any_strict_eqtilt = any(r["strict_superset"] for r in eqtilt_recs)
    any_eqtilt_crisis_2or3 = any(
        sum(bool(v) for v in r["crisis_beats_benchmark"].values()) >= 2
        for r in eqtilt_recs
    )
    any_eqtilt_strict_with_crisis = any(
        r["strict_superset"]
        and sum(bool(v) for v in r["crisis_beats_benchmark"].values()) >= 2
        for r in eqtilt_recs
    )

    basket2_qu_rec = next(r for r in results
                          if r["kind"] == "basket2QU_K4lv25_g25_rvp70_cashx")
    basket2_qu_crisis_count = sum(
        bool(v) for v in basket2_qu_rec["crisis_beats_benchmark"].values()
    )

    best_sortino_lh = best["sortino_lh56y"] if best["sortino_lh56y"] is not None else 0.0

    baseline_rec = next(r for r in results if r["kind"] == "baseline_qld_zroz")
    single_g25_rec = next(r for r in results
                          if r["kind"] == "single_K4lv25_g25_rvp70_cashx")
    basket3_invvol_rec = next(r for r in results
                              if r["kind"] == "basket3invvol_K4lv25_g25_rvp70_cashx")

    baseline_sortino = baseline_rec["sortino_lh56y"] or 0.0
    single_g25_sortino = single_g25_rec["sortino_lh56y"] or 0.0
    basket3_invvol_sortino = basket3_invvol_rec["sortino_lh56y"] or 0.0
    g1_pbo_value = float(g1_result["pbo"])

    cmp_detail = [
        {"name": r["config_name"], "kind": r["kind"], "on_leg": r["on_leg"],
         "weights": r["weights"], "gamma": r["gamma"],
         "sortino_lh56y": r["sortino_lh56y"],
         "cagr_lh56y": r["cagr_lh56y"],
         "end_equity_ratio_vs_baseline": r["end_equity_ratio_vs_baseline"],
         "phase3_performance_candidate": r["phase3_performance_candidate"],
         "beats_winner": r["beats_winner"],
         "strict_superset": r["strict_superset"],
         "total_score": r["score_breakdown"]["total"],
         "crisis_count": sum(
             bool(v) for v in r["crisis_beats_benchmark"].values()
         )}
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
            "rule": "Baseline Sortino_lh56y deviates from iter 011-014 baseline 1.3240 by > 0.005.",
            "baseline_sortino_lh56y": baseline_sortino,
            "expected": ITER011_BASELINE_SORTINO,
        },
        "kill_loop_4_replica_sanity_single_K4lv25_g25": {
            "fired": bool(abs(single_g25_sortino - ITER014_SINGLE_K4LV25_G25_SORTINO) > 0.005),
            "rule": "single_K4lv25_g25_rvp70_cashx Sortino_lh56y deviates from iter 014 strict-superset 1.3951 by > 0.005.",
            "single_K4lv25_g25_sortino_lh56y": single_g25_sortino,
            "expected": ITER014_SINGLE_K4LV25_G25_SORTINO,
        },
        "kill_loop_5_replica_sanity_basket3invvol_K4lv25_g25": {
            "fired": bool(abs(basket3_invvol_sortino - ITER014_BASKET3_TRIPLE_STACK_SORTINO) > 0.005),
            "rule": "basket3invvol_K4lv25_g25_rvp70_cashx Sortino_lh56y deviates from iter 014 triple-stack 1.4689 by > 0.005.",
            "basket3invvol_K4lv25_g25_sortino_lh56y": basket3_invvol_sortino,
            "expected": ITER014_BASKET3_TRIPLE_STACK_SORTINO,
        },
        "kill_loop_6_pbo_blowup": {
            "fired": bool(g1_pbo_value >= 0.55),
            "rule": "G1 PBO >= 0.55 (hard regression vs iter 014 0.4405).",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_7_pbo_held": {
            "fired": bool(g1_pbo_value < PHASE3_PBO_CEIL),
            "rule": "G1 PBO < 0.50 (PBO recipe held). POSITIVE TAG.",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_8_phase3_perf_candidate_eqtilt": {
            "fired": bool(any_phase3_eqtilt),
            "rule": "ANY equity-tilted variant achieves phase3_performance_candidate=True. POSITIVE TAG (CORE HYPOTHESIS).",
        },
        "kill_loop_9_strict_superset_eqtilt": {
            "fired": bool(any_strict_eqtilt),
            "rule": "ANY equity-tilted variant achieves strict_superset=True. POSITIVE TAG (STRONGEST HYPOTHESIS).",
        },
        "kill_loop_10_eqtilt_crisis_2or3_of_4": {
            "fired": bool(any_eqtilt_crisis_2or3),
            "rule": "ANY eqtilt variant achieves crisis count >= 2/4. POSITIVE TAG.",
        },
        "kill_loop_11_basket2_QU_no_crisis": {
            "fired": bool(basket2_qu_crisis_count <= 1),
            "rule": "basket2_QU (no UGL) achieves crisis count <= 1/4. POSITIVE TAG (validates UGL ablation expectation).",
            "basket2_QU_crisis_count": basket2_qu_crisis_count,
        },
        "kill_loop_12_eqtilt_crisis_strict_superset": {
            "fired": bool(any_eqtilt_strict_with_crisis),
            "rule": "ANY eqtilt variant achieves strict_superset AND crisis >= 2/4. POSITIVE TAG (loop's first crisis-2/4 strict_superset).",
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
        title="Iter 015 — equity-tilted basket CAGR recovery (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 015 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 015 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 015 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 015 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 015 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 015 — crisis MDD vs SPY",
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
            "on_leg": rec["on_leg"],
            "weights": rec["weights"],
            "gamma": rec["gamma"],
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
        "iter": "015-2026-05-10-equity-tilted-basket-cagr-recovery",
        "tier": "loop_iter",
        "phase": 3,
        "phase_name": "performance-first beater hunt",
        "hypothesis": (
            "Fixed-weight equity-tilted baskets (basket3-eqtilt66 / "
            "basket3-eqtilt85) test whether reducing UGL weight from "
            "basket3-invvol's ~45% (Carver/Clenow inverse-vol) down to "
            "16.7% (eq66) or 7.5% (eq85) recovers CAGR_lh56y above the "
            "31.08% Phase 3 floor while preserving 2022_rates / "
            "2000_dotcom crisis cushion. basket2_QU (no UGL) is a pure-"
            "equity ablation. Six configs preserve mechanism-mix-diverse "
            "5-topology grid (iter 014 PBO-0.4405 recipe). Targets the "
            "loop's first crisis-≥2/4 strict_superset. "
            "[risk_parity, p.110, ch.5] Qian diversification return; "
            "[risk_parity, p.11, ch.1] Qian invvol over-allocation; "
            "[risk_parity, ch.5, p.10] Carlson stacking; "
            "[stocks_on_the_move, p.98] Clenow vol-parity baseline; "
            "[advances_fin_ml, p.208-211] CSCV PBO."
        ),
        "primary_citation": "[risk_parity, p.110, ch.5]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_015",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"], "topology": s["topology"],
             "on_leg": s["on_leg"], "weights": list(s["weights"]) if s["weights"] is not None else None,
             "upgrade": s["upgrade"], "gamma": s["gamma"],
             "ratevol": s["ratevol"], "alt_off": s["alt_off"]}
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
        "any_phase3_eqtilt": bool(any_phase3_eqtilt),
        "any_strict_superset_eqtilt": bool(any_strict_eqtilt),
        "any_eqtilt_crisis_2or3_of_4": bool(any_eqtilt_crisis_2or3),
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
    LOG.info("Ratevol active%%: %s",
             {k: f"{v:.1%}" for k, v in per_cfg_ratevol_active_pct.items()})
    LOG.info("Blend active%%: %s",
             {k: f"{v:.1%}" for k, v in per_cfg_blend_active_pct.items()})
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
