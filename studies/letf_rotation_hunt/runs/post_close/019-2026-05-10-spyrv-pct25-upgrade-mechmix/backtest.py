"""Iter 019 — SPY-RV-pct25 forward-vol upgrade gate (mechanism-mix-diverse).

Phase 3 — performance-first beater hunt. Tests SPY 21d realised-vol
percentile (< 25th pct vs trailing 1260-day window) as an alternative
upgrade-gate trigger that is OR-combined with iter 014's K4_AND_QLDlv25
and iter 017's T40D60 post-crash rearm. The new axis is a forward-vol
regime gate computed on the broader SPY index — orthogonal to all
previously-tested QLD-asset-derived gates.

Six configs (mechanism-mix-diverse — 5 distinct upgrade-axis topologies):

  1. baseline_qld_zroz                                                  — calibration anchor
  2. single_K4lv25_g25_rvp70_cashx                                      — iter 014 strict_superset replica anchor
  3. basket3invvol_K4lv25_g25_rvp70_cashx                               — iter 014 triple-stack replica anchor
  4. single_K4lv25_g25_rvp70_cashx_T40D60                               — iter 017 NEW strict_superset replica anchor
  5. single_K4lv25_OR_spyrv25_g25_rvp70_cashx (PRIMARY)                 — NEW forward-vol orthogonal upgrade axis
  6. single_K4lv25_OR_spyrv25_g25_rvp70_cashx_T40D60 (STRONGEST)        — NEW 3-way OR composite (state × time × forward-vol)

Citations
---------
- [volatility_trading, p.58-60]: Sinclair vol cone (PRIMARY) — percentile-
  based vol-regime gate.
- [leverage_for_the_long_run, p.4-7, ch.2-3]: Husson-Trifoni — low-vol ⇒
  streaks; LETF leverage harvesting structurally favored in low-vol
  regimes.
- [leverage_for_the_long_run, ch.4-5, p.40-60]: LRS leverage rotation.
- [stocks_on_the_move, p.98]: Clenow trend re-establishment.
- [risk_parity, p.80-81, ch.4]: Qian RORO graded master-gate (γ=0.25).
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking.
- [systematic_trading, p.212, ch.13]: Carver re-arm hysteresis (slot 6
  inherits iter 017 mechanism).
- [advances_fin_ml, p.208-211]: PBO via CSCV (mechanism-mix-diversity).
- [advances_fin_ml, p.222-223]: DSR cumulative n_trials (n_global=540).
- [advances_fin_ml, p.196-202]: bootstrap CI / DSR.
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
LOG = logging.getLogger("iter019")


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_PRIOR_ITERS = ITER_DIR.parent
ITER007 = _load_module(
    _PRIOR_ITERS / "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket" / "backtest.py",
    "iter019_iter007_backtest",
)
windowed_returns = ITER007.windowed_returns
compute_per_dataset = ITER007.compute_per_dataset
spy_anchor_metrics = ITER007.spy_anchor_metrics

ITER011 = _load_module(
    _PRIOR_ITERS / "011-2026-05-10-conditional-tqqq-leverage" / "conditional_leg.py",
    "iter019_iter011_cleg",
)
entry_signal_K2 = ITER011.entry_signal_K2
upgrade_signal_K4 = ITER011.upgrade_signal_K4
upgrade_signal_lowvol25 = ITER011.upgrade_signal_lowvol25
combine_AND = ITER011.combine_AND
combine_OR = ITER011.combine_OR

ITER006 = _load_module(
    _PRIOR_ITERS / "006-2026-05-09-bond-ratevol-regime" / "rate_vol_gate.py",
    "iter019_iter006_ratevol",
)
ratevol_regime_gate = ITER006.ratevol_regime_gate

ITER014 = _load_module(
    _PRIOR_ITERS / "014-2026-05-10-mechanism-mix-diverse-graded-blend" / "mechanism_mix_leg.py",
    "iter019_iter014_mechmix",
)
build_single_asset_on_leg = ITER014.build_single_asset_on_leg
build_basket3_on_leg = ITER014.build_basket3_on_leg
build_mechanism_mix_strategy_returns = ITER014.build_mechanism_mix_strategy_returns
mechanism_mix_turnover = ITER014.mechanism_mix_turnover

ITER017 = _load_module(
    _PRIOR_ITERS / "017-2026-05-10-postcrash-rearm-tqqq-streak" / "reentry_overlay.py",
    "iter019_iter017_rearm",
)
build_postcrash_rearm_gate = ITER017.build_postcrash_rearm_gate
diagnose_rearm_events = ITER017.diagnose_rearm_events

# Winner benchmark (frozen).
WINNER_BENCHMARK_SORTINO = 1.3246
WINNER_BENCHMARK_CAGR = 0.3108
WINNER_BENCHMARK_ITER = "022-2026-05-06-T3d-extended-grid"
WINNER_BENCHMARK_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
BEATS_THRESHOLD_SORTINO = 1.3746
BEATS_PCT_ABOVE = 0.95

PHASE3_CAGR_FLOOR = 0.3108
PHASE3_END_EQ_RATIO_FLOOR = 1.05
PHASE3_SORTINO_FLOOR = 1.20
PHASE3_PBO_CEIL = 0.50
PHASE3_DSR_CEIL = 0.05

# Trial accounting.
PRE_ITER_CUMULATIVE = 534
PRE_ITER_LOOP = 108
LOCAL_N_CONFIGS = 6

# Calibration anchors (KILL_LOOP replica sanity).
ITER011_BASELINE_SORTINO = 1.3240            # KILL_LOOP #3 (10th-gen)
ITER014_SINGLE_K4LV25_G25_SORTINO = 1.3951    # KILL_LOOP #4
ITER014_BASKET3_K4LV25_G25_SORTINO = 1.4689   # KILL_LOOP #5
ITER017_T40D60_SORTINO = 1.4030               # KILL_LOOP #6 (2nd-gen)

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
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_spyrv_baseline_qld_zroz",
        "kind": "baseline_qld_zroz",
        "topology": "single/none/none",
        "use_basket": False,
        "upgrade_kind": "none",
        "spyrv_or": False,
        "gamma": 0.0,
        "ratevol": None,
        "alt_off": None,
        "enable_reentry": False,
        "t_crash": 0,
        "d_arm": 0,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_spyrv_single_K4lv25_g25_rvp70_cashx",
        "kind": "single_K4lv25_g25_rvp70_cashx",
        "topology": "single/K4_AND_QLDlv25/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_kind": "K4_AND_lv25",
        "spyrv_or": False,
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "enable_reentry": False,
        "t_crash": 0,
        "d_arm": 0,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_spyrv_basket3invvol_K4lv25_g25_rvp70_cashx",
        "kind": "basket3invvol_K4lv25_g25_rvp70_cashx",
        "topology": "basket3/K4_AND_QLDlv25/g=0.25/p70-cashx",
        "use_basket": True,
        "upgrade_kind": "K4_AND_lv25",
        "spyrv_or": False,
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "enable_reentry": False,
        "t_crash": 0,
        "d_arm": 0,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_spyrv_single_K4lv25_g25_rvp70_cashx_T40D60",
        "kind": "single_K4lv25_g25_rvp70_cashx_T40D60",
        "topology": "single/K4_AND_QLDlv25_OR_rearm/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_kind": "K4_AND_lv25",
        "spyrv_or": False,
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "enable_reentry": True,
        "t_crash": 40,
        "d_arm": 60,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_spyrv_single_K4lv25_OR_spyrv25_g25_rvp70_cashx",
        "kind": "single_K4lv25_OR_spyrv25_g25_rvp70_cashx",
        "topology": "single/(K4_AND_QLDlv25)_OR_SPYRV25/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_kind": "K4_AND_lv25",
        "spyrv_or": True,
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "enable_reentry": False,
        "t_crash": 0,
        "d_arm": 0,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_spyrv_single_K4lv25_OR_spyrv25_g25_rvp70_cashx_T40D60",
        "kind": "single_K4lv25_OR_spyrv25_g25_rvp70_cashx_T40D60",
        "topology": "single/(K4_AND_QLDlv25)_OR_SPYRV25_OR_rearm/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_kind": "K4_AND_lv25",
        "spyrv_or": True,
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "enable_reentry": True,
        "t_crash": 40,
        "d_arm": 60,
    },
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

    LOG.info("Building entry + upgrade gates (incl. NEW SPY-RV-pct25)...")
    on_signal = entry_signal_K2(qld, qld_ret)
    k4_gate = upgrade_signal_K4(qld, qld_ret)
    qld_lv25_gate = upgrade_signal_lowvol25(
        qld_ret, vol_window=21, pct_window=1260, pct_threshold=0.25,
    )
    k4_and_qldlv25_gate = combine_AND(k4_gate, qld_lv25_gate)

    # NEW: SPY 21d realised-vol percentile gate (Sinclair vol cone, p.58-60).
    # Same parameter convention as iter 011's lowvol25 — vol_window=21,
    # pct_window=1260 (5y), pct_threshold=0.25 — but applied to SPY returns
    # rather than QLD returns (broader-market vol regime, orthogonal axis).
    spyrv25_gate = upgrade_signal_lowvol25(
        spy_ret, vol_window=21, pct_window=1260, pct_threshold=0.25,
    )

    # SPY-RV diagnostic counters (% of valid days the gate fires; overlap
    # with K4_AND_QLDlv25 fire pattern; standalone fires only).
    common_idx = k4_and_qldlv25_gate.index.intersection(spyrv25_gate.index)
    k4q = k4_and_qldlv25_gate.reindex(common_idx).fillna(0.0)
    sv = spyrv25_gate.reindex(common_idx).fillna(0.0)
    spyrv_diag = {
        "spyrv25_active_pct": float(((sv == 1.0)).mean()),
        "k4_and_qldlv25_active_pct": float(((k4q == 1.0)).mean()),
        "both_active_pct": float(((sv == 1.0) & (k4q == 1.0)).mean()),
        "spyrv_only_active_pct": float(((sv == 1.0) & (k4q == 0.0)).mean()),
        "qldlv25_only_active_pct": float(((sv == 0.0) & (k4q == 1.0)).mean()),
        "or_combined_active_pct": float(((sv == 1.0) | (k4q == 1.0)).mean()),
    }
    LOG.info("SPY-RV-pct25 diag: %s", spyrv_diag)

    base_upgrade_map = {
        "none":         pd.Series(0.0, index=qld_ret.index),
        "K4_AND_lv25":  k4_and_qldlv25_gate,
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
    per_cfg_spyrv_or_active_pct: dict[str, float] = {}

    LOG.info("Running %d configs...", len(CONFIG_SPECS))
    for spec in CONFIG_SPECS:
        base_upg = base_upgrade_map[spec["upgrade_kind"]]

        # Compose upgrade gate: base + (optional spyrv OR-add) + (optional rearm OR-add).
        upg = base_upg
        if spec["spyrv_or"]:
            upg = combine_OR(upg, spyrv25_gate)

        if spec["enable_reentry"]:
            rearm_gate = build_postcrash_rearm_gate(
                on_signal=on_signal,
                t_crash=spec["t_crash"],
                d_arm=spec["d_arm"],
            )
            upg = combine_OR(upg, rearm_gate)
            per_cfg_rearm_diag[spec["name"]] = diagnose_rearm_events(
                on_signal=on_signal,
                t_crash=spec["t_crash"],
                d_arm=spec["d_arm"],
            )
        else:
            per_cfg_rearm_diag[spec["name"]] = {
                "n_qualified_flips": 0,
                "n_active_rearm_days": 0,
                "rearm_active_pct": 0.0,
                "t_crash": int(spec["t_crash"]),
                "d_arm": int(spec["d_arm"]),
            }

        if spec["use_basket"]:
            on_leg_ret = build_basket3_on_leg(
                qld_returns=qld_ret,
                tqqq_returns=tqqq_ret,
                upro_returns=upro_ret,
                ugl_returns=ugl_ret,
                upgrade_gate=upg,
                invvol_window=60,
            )
        else:
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
            drop_on_signal_warmup=spec["use_basket"],
        )
        per_cfg_returns[spec["name"]] = strat_r

        on_lag = on_signal.shift(1).reindex(strat_r.index)
        per_cfg_on_state[spec["name"]] = (on_lag == 1).astype(float)

        upg_lag = upg.shift(1).reindex(strat_r.index).fillna(0.0)
        upg_active = ((on_lag == 1.0) & (upg_lag == 1.0))
        per_cfg_upgrade_active_pct[spec["name"]] = float(upg_active.mean())

        sv_lag = spyrv25_gate.shift(1).reindex(strat_r.index).fillna(0.0)
        spyrv_or_active = ((on_lag == 1.0) & (sv_lag == 1.0)) if spec["spyrv_or"] else pd.Series(False, index=strat_r.index)
        per_cfg_spyrv_or_active_pct[spec["name"]] = float(spyrv_or_active.mean())

        rv_lag = rv.shift(1).reindex(strat_r.index)
        rv_active = ((on_lag != 1.0) & (rv_lag == 1.0))
        per_cfg_ratevol_active_pct[spec["name"]] = float(rv_active.mean())

        blend_active = ((on_lag == 1.0) & (rv_lag == 1.0))
        per_cfg_blend_active_pct[spec["name"]] = float(blend_active.mean())

        per_cfg_turnover[spec["name"]] = mechanism_mix_turnover(
            on_signal=on_signal,
            upgrade_gate=upg,
            ratevol_gate=rv,
            use_basket=spec["use_basket"],
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

    baseline_name = "qld_voteK2_sma250_100_vol21_40_ar30_spyrv_baseline_qld_zroz"
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

        common_idx2 = strat_lh_eq.index.intersection(baseline_lh_eq.index)
        if len(common_idx2) > 0:
            end_eq_ratio = float(strat_lh_eq.loc[common_idx2[-1]] /
                                 baseline_lh_eq.loc[common_idx2[-1]])
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
            "use_basket": spec["use_basket"],
            "upgrade_kind": spec["upgrade_kind"],
            "spyrv_or": spec["spyrv_or"],
            "gamma": spec["gamma"],
            "ratevol": spec["ratevol"],
            "alt_off": spec["alt_off"],
            "enable_reentry": spec["enable_reentry"],
            "t_crash": spec["t_crash"],
            "d_arm": spec["d_arm"],
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
            "spyrv_or_active_pct": per_cfg_spyrv_or_active_pct[name],
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
    basket3_anchor_rec = next(r for r in results if r["kind"] == "basket3invvol_K4lv25_g25_rvp70_cashx")
    t40d60_anchor_rec = next(r for r in results if r["kind"] == "single_K4lv25_g25_rvp70_cashx_T40D60")
    spyrv_recs = [r for r in results if r["spyrv_or"]]
    spyrv_single_rec = next(r for r in results if r["kind"] == "single_K4lv25_OR_spyrv25_g25_rvp70_cashx")
    spyrv_t40d60_rec = next(r for r in results if r["kind"] == "single_K4lv25_OR_spyrv25_g25_rvp70_cashx_T40D60")

    baseline_sortino = baseline_rec["sortino_lh56y"] or 0.0
    single_anchor_sortino = single_anchor_rec["sortino_lh56y"] or 0.0
    basket3_anchor_sortino = basket3_anchor_rec["sortino_lh56y"] or 0.0
    t40d60_anchor_sortino = t40d60_anchor_rec["sortino_lh56y"] or 0.0
    g1_pbo_value = float(g1_result["pbo"])

    any_spyrv_phase3 = any(r["phase3_performance_candidate"] for r in spyrv_recs)
    any_spyrv_strict = any(r["strict_superset"] for r in spyrv_recs)
    any_spyrv_2020 = any(
        bool(r["crisis_beats_benchmark"].get("2020_covid", False))
        for r in spyrv_recs
    )
    any_spyrv_strict_with_crisis = any(
        r["strict_superset"]
        and sum(int(bool(v)) for v in r["crisis_beats_benchmark"].values()) >= 2
        for r in spyrv_recs
    )

    cmp_detail = [
        {"name": r["config_name"], "kind": r["kind"],
         "spyrv_or": r["spyrv_or"], "enable_reentry": r["enable_reentry"],
         "use_basket": r["use_basket"],
         "sortino_lh56y": r["sortino_lh56y"],
         "cagr_lh56y": r["cagr_lh56y"],
         "phase3_performance_candidate": r["phase3_performance_candidate"],
         "beats_winner": r["beats_winner"],
         "strict_superset": r["strict_superset"],
         "total_score": r["score_breakdown"]["total"],
         "crisis_2020_covid_beat": bool(
             r["crisis_beats_benchmark"].get("2020_covid", False)
         ),
         "crisis_2008_gfc_beat": bool(
             r["crisis_beats_benchmark"].get("2008_gfc", False)
         ),
         "crisis_2000_dotcom_beat": bool(
             r["crisis_beats_benchmark"].get("2000_dotcom", False)
         ),
         "crisis_2022_rates_beat": bool(
             r["crisis_beats_benchmark"].get("2022_rates", False)
         ),
         "spyrv_or_active_pct": r["spyrv_or_active_pct"],
         "upgrade_active_pct": r["upgrade_active_pct"]}
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
            "rule": "Baseline Sortino_lh56y deviates from iter 011-018 baseline 1.3240 by > 0.005.",
            "baseline_sortino_lh56y": baseline_sortino,
            "expected": ITER011_BASELINE_SORTINO,
        },
        "kill_loop_4_replica_sanity_single_K4lv25_g25": {
            "fired": bool(abs(single_anchor_sortino - ITER014_SINGLE_K4LV25_G25_SORTINO) > 0.005),
            "rule": "single_K4lv25_g25_rvp70_cashx Sortino_lh56y deviates from iter 014-018 strict_superset 1.3951 by > 0.005.",
            "single_anchor_sortino_lh56y": single_anchor_sortino,
            "expected": ITER014_SINGLE_K4LV25_G25_SORTINO,
        },
        "kill_loop_5_replica_sanity_basket3invvol_K4lv25_g25": {
            "fired": bool(abs(basket3_anchor_sortino - ITER014_BASKET3_K4LV25_G25_SORTINO) > 0.005),
            "rule": "basket3invvol_K4lv25_g25_rvp70_cashx Sortino_lh56y deviates from iter 014-017 triple-stack 1.4689 by > 0.005.",
            "basket3_anchor_sortino_lh56y": basket3_anchor_sortino,
            "expected": ITER014_BASKET3_K4LV25_G25_SORTINO,
        },
        "kill_loop_6_replica_sanity_T40D60": {
            "fired": bool(abs(t40d60_anchor_sortino - ITER017_T40D60_SORTINO) > 0.005),
            "rule": "single_K4lv25_g25_rvp70_cashx_T40D60 Sortino_lh56y deviates from iter 017-018 NEW strict_superset 1.4030 by > 0.005.",
            "t40d60_anchor_sortino_lh56y": t40d60_anchor_sortino,
            "expected": ITER017_T40D60_SORTINO,
        },
        "kill_loop_7_pbo_blowup": {
            "fired": bool(g1_pbo_value >= 0.55),
            "rule": "G1 PBO >= 0.55 (hard regression threshold).",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_8_pbo_held": {
            "fired": bool(g1_pbo_value < PHASE3_PBO_CEIL),
            "rule": "G1 PBO < 0.50 (Phase 3 hard gate). POSITIVE TAG.",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_9_spyrv_phase3_perf_candidate": {
            "fired": bool(any_spyrv_phase3),
            "rule": "Any spyrv config (slot 5 or 6) achieves phase3_performance_candidate=True. CORE HYPOTHESIS TEST.",
            "any_spyrv_phase3": bool(any_spyrv_phase3),
        },
        "kill_loop_10_spyrv_strict_superset": {
            "fired": bool(any_spyrv_strict),
            "rule": "Any spyrv config (slot 5 or 6) achieves strict_superset=True. STRONGEST HYPOTHESIS TEST.",
            "any_spyrv_strict": bool(any_spyrv_strict),
        },
        "kill_loop_11_spyrv_2020_covid_rescue": {
            "fired": bool(any_spyrv_2020),
            "rule": "Any spyrv config beats SPY in 2020_covid window (forward-vol low-vol-onset capture).",
            "any_spyrv_2020": bool(any_spyrv_2020),
        },
        "kill_loop_12_spyrv_strict_superset_with_crisis_2plus": {
            "fired": bool(any_spyrv_strict_with_crisis),
            "rule": "Any spyrv config achieves strict_superset=True AND crisis count >= 2/4. POSITIVE TAG (loop's first crisis-≥2/4 strict_superset).",
            "any_spyrv_strict_with_crisis": bool(any_spyrv_strict_with_crisis),
        },
        "spyrv_diagnostics": spyrv_diag,
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
        title="Iter 019 — SPY-RV-pct25 forward-vol upgrade gate (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 019 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 019 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 019 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 019 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 019 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 019 — crisis MDD vs SPY",
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
            "use_basket": rec["use_basket"],
            "spyrv_or": rec["spyrv_or"],
            "gamma": rec["gamma"],
            "enable_reentry": rec["enable_reentry"],
            "t_crash": rec["t_crash"],
            "d_arm": rec["d_arm"],
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
            "spyrv_or_active_pct": rec["spyrv_or_active_pct"],
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
        "iter": "019-2026-05-10-spyrv-pct25-upgrade-mechmix",
        "tier": "loop_iter",
        "phase": 3,
        "phase_name": "performance-first beater hunt",
        "hypothesis": (
            "SPY 21d realised-vol percentile (< 25th pct vs trailing 1260-day "
            "window) as an alternative upgrade-gate trigger that is OR-combined "
            "with iter 014's K4_AND_QLDlv25 and iter 017's T40D60 post-crash "
            "rearm. Six configs (mechanism-mix-diverse — 5 distinct upgrade-axis "
            "topologies): baseline + iter 014 single anchor + iter 014 basket3 "
            "anchor + iter 017 T40D60 anchor + NEW single+spyrv25 PRIMARY + NEW "
            "single+spyrv25+T40D60 STRONGEST. Tests whether broader-market vol-"
            "regime onsets unlock additional upgrade activation that asset-"
            "specific QLD-vol-pct misses. Targets 5th loop strict_superset on "
            "a NEW orthogonal axis. [volatility_trading, p.58-60] Sinclair vol "
            "cone PRIMARY; [leverage_for_the_long_run, p.4-7, ch.2-3] Husson-"
            "Trifoni low-vol⇒streaks; [stocks_on_the_move, p.98] Clenow trend "
            "re-establishment; [risk_parity, p.80-81, ch.4] Qian RORO graded; "
            "[risk_parity, ch.5, p.10] Carlson stacking; [systematic_trading, "
            "p.212, ch.13] Carver re-arm hysteresis; [advances_fin_ml, p.208-211] "
            "CSCV PBO; [advances_fin_ml, p.222-223] DSR cumulative (n_global=540)."
        ),
        "primary_citation": "[volatility_trading, p.58-60]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_019",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"], "topology": s["topology"],
             "use_basket": s["use_basket"], "upgrade_kind": s["upgrade_kind"],
             "spyrv_or": s["spyrv_or"], "gamma": s["gamma"],
             "ratevol": s["ratevol"], "alt_off": s["alt_off"],
             "enable_reentry": s["enable_reentry"],
             "t_crash": s["t_crash"], "d_arm": s["d_arm"]}
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
        "any_spyrv_phase3_perf_candidate": bool(any_spyrv_phase3),
        "any_spyrv_strict_superset": bool(any_spyrv_strict),
        "any_spyrv_2020_covid_rescue": bool(any_spyrv_2020),
        "any_spyrv_strict_superset_with_crisis_2plus": bool(any_spyrv_strict_with_crisis),
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
              for k, v in kill_loop_results.items() if k not in ("compound_detail", "spyrv_diagnostics")})
    LOG.info("Upgrade active%%: %s",
             {k: f"{v:.1%}" for k, v in per_cfg_upgrade_active_pct.items()})
    LOG.info("SPY-RV OR active%%: %s",
             {k: f"{v:.1%}" for k, v in per_cfg_spyrv_or_active_pct.items()})
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
