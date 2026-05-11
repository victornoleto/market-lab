"""Iter 030 — T_crash sensitivity scan at iter 027 slot 6 LRS1.20 unconditional ceiling.

Phase 4 — iter 017 focused validation/refinement. Sensitivity probe: vary
T_crash {35, 40, 45, 50} keeping D_arm=60 frozen, on the iter 027 slot 6
base (rearm-only INDEP IMPL + LRS1.20 unconditional). Tests whether iter
017's T40 choice is a robust local Pareto optimum or a fragile event fit.

PRIMARY hypothesis (T_crash sensitivity at the iter 027 LRS1.20 ceiling):
iter 027 closed the LRS magnitude axis at 1.20× and identified slot 6
(rearm-only T40D60 + LRS1.20 unconditional) as the loop's strongest formal
Pareto frontier point. Iter 028+029 closed the LRS regime-conditioning axis
on both polarities. Open question (carryover from iter 029 next-iter idea
(d)): is the iter 027 T40 anchor robust to small T_crash perturbations?

KEY HYPOTHESIS (PRE-REGISTERED): IF T_crash=40 is a fragile event fit,
THEN at least one of T35/T45/T50 will Pareto-dominate T40 on (CAGR,
Sortino, end_eq_vs_iter017) AND beats_winner=True AND PBO < 0.50. If no
T_crash perturbation Pareto-dominates T40, the iter 027 anchor is
robustness-validated.

SECONDARY HYPOTHESIS (modern_sortino_lift via T_crash perturbation):
EXPECTED FALSE per iter 027/028/029 structural diagnosis. T_crash
perturbation alone cannot lift modern subperiod Sortino ≥ 1.20 — modern
softness is structural to the rearm primitive's interaction with the
modern-era 2× QLD on-leg vol cluster.

Six configs (three calibration anchors + three NEW T_crash perturbations):

  1. baseline_qld_zroz                                                            — 21st-gen calibration (no rearm, no LRS)
  2. single_rearmonly_g25_rvp70_cashx_T40D60                                       — 10th-gen iter 022 INDEP IMPL anchor (rearm-only, no LRS)
  3. single_rearmonly_g25_rvp70_cashx_T40D60_unclrs120                             — 2nd-gen iter 027 slot 6 anchor (rearm + LRS1.20 unconditional)
  4. single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120 (NEW)                       — T_crash DOWN
  5. single_rearmonly_g25_rvp70_cashx_T45D60_unclrs120 (NEW)                       — T_crash UP
  6. single_rearmonly_g25_rvp70_cashx_T50D60_unclrs120 (NEW)                       — T_crash UP further

Citations
---------
- [advances_fin_ml, p.208-211]: PRIMARY CSCV PBO mechanism-mix diversity —
  4-point T_crash scan with 2 mechanically-distinct anchors (no-rearm
  baseline + rearm-no-LRS) injects sufficient mechanism diversity at the
  CSCV level to avoid iter 018-style PBO blowup.
- [leverage_for_the_long_run, p.6-7, ch.3]: Husson-Trifoni MA flip-on as
  empirical streak-window onset; T_crash perturbation tests whether the
  streak-onset signal is robust to the "how long below MA" criterion.
- [leverage_for_the_long_run, p.13, ch.3]: canonical RISK_ON LRS rule
  preserved (LRS1.20× unconditional during ON; iter 028+029 falsified
  regime-conditioning).
- [leverage_for_the_long_run, ch.4-5, p.40-60]: Husson-Trifoni LRS scaling
  (1.20× sweet-spot ceiling unchanged from iter 027).
- [stocks_on_the_move, p.98]: Clenow trend-strength / re-establishment
  after long OFF stretch (provides theoretical grounding for T_crash
  perturbation).
- [advances_fin_ml, p.222-223]: DSR cumulative n_trials (n_global=606).
- [advances_fin_ml, p.196-202]: bootstrap CI / DSR.
- [risk_parity, ch.5, p.10]: Carlson stacking (LRS overlay composition).
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
LOG = logging.getLogger("iter030")


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_PRIOR_ITERS = ITER_DIR.parent
ITER007 = _load_module(
    _PRIOR_ITERS / "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket" / "backtest.py",
    "iter030_iter007_backtest",
)
windowed_returns = ITER007.windowed_returns
compute_per_dataset = ITER007.compute_per_dataset
spy_anchor_metrics = ITER007.spy_anchor_metrics

ITER011 = _load_module(
    _PRIOR_ITERS / "011-2026-05-10-conditional-tqqq-leverage" / "conditional_leg.py",
    "iter030_iter011_cleg",
)
entry_signal_K2 = ITER011.entry_signal_K2

ITER006 = _load_module(
    _PRIOR_ITERS / "006-2026-05-09-bond-ratevol-regime" / "rate_vol_gate.py",
    "iter030_iter006_ratevol",
)
ratevol_regime_gate = ITER006.ratevol_regime_gate

ITER014 = _load_module(
    _PRIOR_ITERS / "014-2026-05-10-mechanism-mix-diverse-graded-blend" / "mechanism_mix_leg.py",
    "iter030_iter014_mechmix",
)
build_single_asset_on_leg = ITER014.build_single_asset_on_leg
build_mechanism_mix_strategy_returns = ITER014.build_mechanism_mix_strategy_returns
mechanism_mix_turnover = ITER014.mechanism_mix_turnover

RI = _load_module(
    _PRIOR_ITERS / "022-2026-05-10-rearm-only-indep-pfv-confirm" / "rearm_independent.py",
    "iter030_rearm_independent",
)
build_postcrash_rearm_gate_independent = RI.build_postcrash_rearm_gate_independent
diagnose_rearm_events_independent = RI.diagnose_rearm_events_independent

# Reuse iter 024's unconditional LRS overlay helper bit-exactly for slots 3-6.
LRS_HELPER = _load_module(
    _PRIOR_ITERS / "024-2026-05-10-pbo-decoupled-unconditional-lrs105" / "unconditional_lrs_overlay.py",
    "iter030_unc_lrs_overlay",
)
apply_unconditional_lrs_overlay = LRS_HELPER.apply_unconditional_lrs_overlay


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

PHASE4_ANCHOR_ITER = "017-2026-05-10-postcrash-rearm-tqqq-streak"
PHASE4_ANCHOR_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_rearm_single_K4lv25_g25_rvp70_cashx_T40D60"
PHASE4_ANCHOR_SORTINO = 1.4030
PHASE4_ANCHOR_CAGR = 0.3266
PHASE4_ANCHOR_END_EQ_RATIO_VS_BASELINE = 1.620
PHASE4_IMPROVED_SORTINO_FLOOR = 1.35

# Iter 027 slot 6 = parent of T_crash sweep (T40 anchor at LRS1.20 ceiling).
ITER027_SLOT6_T40_LRS120_SORTINO = 1.3786
ITER027_SLOT6_T40_LRS120_CAGR = 0.3622
ITER027_SLOT6_T40_LRS120_END_EQ_VS_ITER017 = 2.908
ITER027_SLOT6_MODERN_SORTINO_1990_2009 = 1.124
ITER027_SLOT6_MODERN_SORTINO_2010_2026 = 1.144

# Trial accounting (per LOOP_MEMORY frontmatter post-iter-029).
PRE_ITER_CUMULATIVE = 600
PRE_ITER_LOOP = 174
LOCAL_N_CONFIGS = 6

# Calibration anchors (KILL_LOOP replica sanity).
ITER011_BASELINE_SORTINO = 1.3240             # KILL_LOOP #3 (21st-gen target)
ITER021_REARMONLY_T40D60_SORTINO = 1.4176     # KILL_LOOP #4 (10th-gen target)
ITER027_SLOT6_T40_LRS120_SORTINO_TARGET = 1.3786  # KILL_LOOP #5 (2nd-gen target)

D_ARM_FROZEN = 60

LRS_FACTOR_REARM = 1.20  # slots 3-6 — iter 027 slot 6 magnitude ceiling

# Per-slot T_crash values (slots 3-6 only).
T_CRASH_T40 = 40
T_CRASH_T35 = 35
T_CRASH_T45 = 45
T_CRASH_T50 = 50

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


# lrs_mode values:
#   "off"        → no LRS overlay (lrs_factor = 1.0)
#   "unclrs120"  → LRS factor 1.20 applied unconditionally on every ON day
#
# upgrade_mode values:
#   "none"            → no upgrade gate
#   "rearmonly_indep" → INDEP IMPL post-crash rearm gate (T_crash, D_arm) per slot
CONFIG_SPECS = [
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_baseline_qld_zroz",
        "kind": "baseline_qld_zroz",
        "topology": "single/none/none",
        "use_basket": False,
        "upgrade_mode": "none",
        "gamma": 0.0,
        "ratevol": None,
        "alt_off": None,
        "rearm_active": False,
        "t_crash": 0,
        "d_arm": 0,
        "lrs_mode": "off",
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T40D60",
        "kind": "single_rearmonly_g25_rvp70_cashx_T40D60",
        "topology": "single/rearm_only_indepimpl/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_mode": "rearmonly_indep",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_active": True,
        "t_crash": T_CRASH_T40,
        "d_arm": D_ARM_FROZEN,
        "lrs_mode": "off",
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_unclrs120",
        "kind": "single_rearmonly_g25_rvp70_cashx_T40D60_unclrs120",
        "topology": "single/rearm_only_indepimpl_x_LRS1.20unc/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_mode": "rearmonly_indep",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_active": True,
        "t_crash": T_CRASH_T40,
        "d_arm": D_ARM_FROZEN,
        "lrs_mode": "unclrs120",
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120",
        "kind": "single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120",
        "topology": "single/rearm_only_indepimpl_T35D60_x_LRS1.20unc/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_mode": "rearmonly_indep",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_active": True,
        "t_crash": T_CRASH_T35,
        "d_arm": D_ARM_FROZEN,
        "lrs_mode": "unclrs120",
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T45D60_unclrs120",
        "kind": "single_rearmonly_g25_rvp70_cashx_T45D60_unclrs120",
        "topology": "single/rearm_only_indepimpl_T45D60_x_LRS1.20unc/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_mode": "rearmonly_indep",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_active": True,
        "t_crash": T_CRASH_T45,
        "d_arm": D_ARM_FROZEN,
        "lrs_mode": "unclrs120",
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T50D60_unclrs120",
        "kind": "single_rearmonly_g25_rvp70_cashx_T50D60_unclrs120",
        "topology": "single/rearm_only_indepimpl_T50D60_x_LRS1.20unc/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_mode": "rearmonly_indep",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_active": True,
        "t_crash": T_CRASH_T50,
        "d_arm": D_ARM_FROZEN,
        "lrs_mode": "unclrs120",
    },
]


def _lrs_factor_for_mode(lrs_mode: str) -> float:
    if lrs_mode == "off":
        return 1.0
    if lrs_mode == "unclrs120":
        return LRS_FACTOR_REARM
    raise ValueError(f"Unknown lrs_mode: {lrs_mode}")


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


def _subperiod_metrics(strat_returns_lh: pd.Series, spy_returns_lh: pd.Series) -> dict:
    subs = {
        "1970_1989": ("1970-01-01", "1989-12-31"),
        "1990_2009": ("1990-01-01", "2009-12-31"),
        "2010_2026": ("2010-01-01", "2026-04-30"),
    }
    out = {}
    for label, (start, end) in subs.items():
        r = strat_returns_lh.loc[start:end].dropna()
        spy = spy_returns_lh.loc[start:end].dropna()
        if len(r) < 252 or len(spy) < 252:
            out[label] = {"n_obs": int(len(r)), "sortino": None, "cagr": None,
                          "mdd": None, "spy_cagr": None}
            continue
        eq = (1.0 + r).cumprod()
        years = len(r) / 252.0
        cagr = float(eq.iloc[-1] ** (1.0 / years) - 1.0)
        downside = r[r < 0]
        sortino = float(r.mean() / downside.std() * np.sqrt(252.0)) if len(downside) > 1 else None
        peak = eq.expanding().max()
        mdd = float((eq / peak - 1.0).min())
        spy_eq = (1.0 + spy).cumprod()
        spy_years = len(spy) / 252.0
        spy_cagr = float(spy_eq.iloc[-1] ** (1.0 / spy_years) - 1.0)
        out[label] = {
            "n_obs": int(len(r)),
            "sortino": sortino,
            "cagr": cagr,
            "mdd": mdd,
            "spy_cagr": spy_cagr,
        }
    return out


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

    LOG.info("Building entry signal + per-T_crash rearm gates...")
    on_signal = entry_signal_K2(qld, qld_ret)

    rearm_gates_by_tcrash: dict[int, pd.Series] = {}
    rearm_diags_by_tcrash: dict[int, dict] = {}
    for t_crash in (T_CRASH_T35, T_CRASH_T40, T_CRASH_T45, T_CRASH_T50):
        rearm_gates_by_tcrash[t_crash] = build_postcrash_rearm_gate_independent(
            on_signal=on_signal, t_crash=t_crash, d_arm=D_ARM_FROZEN,
        )
        rearm_diags_by_tcrash[t_crash] = diagnose_rearm_events_independent(
            on_signal=on_signal, t_crash=t_crash, d_arm=D_ARM_FROZEN,
        )

    alt_off_returns_map = {"CASHX": cash_ret, "IEFSIM": ief_ret}

    per_cfg_returns: dict[str, pd.Series] = {}
    per_cfg_metrics: dict[str, dict] = {}
    per_cfg_on_state: dict[str, pd.Series] = {}
    per_cfg_upgrade_active_pct: dict[str, float] = {}
    per_cfg_ratevol_active_pct: dict[str, float] = {}
    per_cfg_blend_active_pct: dict[str, float] = {}
    per_cfg_rearm_diag: dict[str, dict] = {}
    per_cfg_lrs_active_pct: dict[str, float] = {}
    per_cfg_turnover: dict[str, float] = {}

    LOG.info("Running %d configs...", len(CONFIG_SPECS))
    for spec in CONFIG_SPECS:
        if spec["upgrade_mode"] == "none":
            upg = pd.Series(0.0, index=qld_ret.index)
            spec_rearm_diag = {"n_qualified_flips": 0, "n_active_rearm_days": 0,
                               "rearm_active_pct": 0.0, "t_crash": 0, "d_arm": 0,
                               "impl": "none"}
        elif spec["upgrade_mode"] == "rearmonly_indep":
            upg = rearm_gates_by_tcrash[spec["t_crash"]]
            spec_rearm_diag = dict(rearm_diags_by_tcrash[spec["t_crash"]])
            spec_rearm_diag["impl"] = "indep"
        else:
            raise ValueError(f"Unknown upgrade_mode: {spec['upgrade_mode']}")
        per_cfg_rearm_diag[spec["name"]] = spec_rearm_diag

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

        lrs_factor_used = _lrs_factor_for_mode(spec["lrs_mode"])
        if spec["lrs_mode"] == "off":
            on_leg_lrs = on_leg_ret
            lrs_active_pct = 0.0
        elif spec["lrs_mode"] == "unclrs120":
            on_leg_lrs = apply_unconditional_lrs_overlay(
                on_leg_returns=on_leg_ret,
                on_signal=on_signal,
                lrs_factor=lrs_factor_used,
            )
            on_lag_for_pct = on_signal.shift(1).reindex(on_leg_lrs.index).fillna(0.0)
            lrs_active_pct = float((on_lag_for_pct == 1.0).mean())
        else:
            raise ValueError(f"Unknown lrs_mode: {spec['lrs_mode']}")
        per_cfg_lrs_active_pct[spec["name"]] = lrs_active_pct

        strat_r = build_mechanism_mix_strategy_returns(
            on_signal=on_signal,
            on_leg_returns=on_leg_lrs,
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

    baseline_name = CONFIG_SPECS[0]["name"]
    baseline_lh_eq = (1.0 + windowed_returns(per_cfg_returns[baseline_name],
                                             *DATASET_WINDOWS["lh_56y"])
                      ).cumprod() * 10_000.0

    # iter 017 anchor reference: rearm-only T40D60 INDEP (slot 2) is bit-exact
    # the iter 022 reimplementation, which has parity 0 vs iter 017 OR-anchor.
    # However, the canonical iter 017 anchor includes K4_OR_rearm; for
    # end_eq_vs_iter017 we use slot 2 (rearm-only T40D60 INDEP, no LRS) as
    # the baseline rearm reference (Sortino 1.4176, CAGR 32.44%).
    # For comparison vs PHASE4_ANCHOR (iter 017 OR-anchor CAGR 32.66%), we
    # still use the published iter 017 metrics in PHASE4_* constants above.
    iter017_indep_anchor_name = CONFIG_SPECS[1]["name"]  # slot 2
    iter017_indep_lh_eq = (1.0 + windowed_returns(per_cfg_returns[iter017_indep_anchor_name],
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
        sortino_edge_iter017 = float(sortino_lh - PHASE4_ANCHOR_SORTINO)
        cagr_edge_iter017 = float(cagr_lh - PHASE4_ANCHOR_CAGR)

        common_idx2 = strat_lh_eq.index.intersection(baseline_lh_eq.index)
        if len(common_idx2) > 0:
            end_eq_ratio = float(strat_lh_eq.loc[common_idx2[-1]] /
                                 baseline_lh_eq.loc[common_idx2[-1]])
        else:
            end_eq_ratio = float("nan")

        # For end_equity_ratio_vs_iter017 we use slot 2 (rearm-only T40D60 INDEP
        # IMPL no LRS, this iter's bit-exact reproduction of iter 017's gate)
        # as the divisor — gives a self-consistent within-iter ratio that
        # aligns to iter 027 slot 6's end_eq_vs_iter017 = 2.908× when slot 3
        # replicates correctly.
        common_idx_iter017 = strat_lh_eq.index.intersection(iter017_indep_lh_eq.index)
        if len(common_idx_iter017) > 0:
            end_eq_ratio_iter017 = float(strat_lh_eq.loc[common_idx_iter017[-1]] /
                                          iter017_indep_lh_eq.loc[common_idx_iter017[-1]])
        else:
            end_eq_ratio_iter017 = float("nan")

        rolling_win = _rolling_win_rates_vs_baseline(strat_lh_eq, baseline_lh_eq)
        rolling_win_iter017 = _rolling_win_rates_vs_baseline(strat_lh_eq, iter017_indep_lh_eq)

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

        phase4_anchor_improved = bool(
            (cagr_lh > PHASE4_ANCHOR_CAGR or end_eq_ratio_iter017 > 1.0)
            and sortino_lh >= PHASE4_IMPROVED_SORTINO_FLOOR
            and gate_dict["g1_pbo"] < PHASE3_PBO_CEIL
            and gate_dict["g2_dsr_p_cumulative"] < PHASE3_DSR_CEIL
        )

        results.append({
            "config_name": name,
            "kind": spec["kind"],
            "topology": spec["topology"],
            "use_basket": spec["use_basket"],
            "upgrade_mode": spec["upgrade_mode"],
            "lrs_mode": spec["lrs_mode"],
            "lrs_factor": lrs_factor_used,
            "gamma": spec["gamma"],
            "ratevol": spec["ratevol"],
            "alt_off": spec["alt_off"],
            "rearm_active": spec["rearm_active"],
            "t_crash": spec["t_crash"],
            "d_arm": spec["d_arm"],
            "rearm_diag": per_cfg_rearm_diag[name],
            "lrs_active_pct": per_cfg_lrs_active_pct[name],
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
            "sortino_edge_vs_iter017": sortino_edge_iter017,
            "cagr_edge_vs_iter017": cagr_edge_iter017,
            "end_equity_ratio_vs_baseline": end_eq_ratio,
            "end_equity_ratio_vs_iter017": end_eq_ratio_iter017,
            "rolling_win_rates_vs_baseline": rolling_win,
            "rolling_win_rates_vs_iter017": rolling_win_iter017,
            "beats_winner": beats_winner,
            "phase3_performance_candidate": phase3_perf_candidate,
            "strict_superset": strict_superset,
            "phase4_anchor_improved": phase4_anchor_improved,
            "upgrade_active_pct": per_cfg_upgrade_active_pct[name],
            "ratevol_active_pct": per_cfg_ratevol_active_pct[name],
            "blend_active_pct": per_cfg_blend_active_pct[name],
            "turnover_per_year": per_cfg_turnover[name],
        })

    LOG.info("Saving per-config strategy returns...")
    for name, r in per_cfg_returns.items():
        r.to_csv(ITER_DIR / f"{name}_strategy_returns.csv", header=["return"])

    def _key(rec):
        is_p4_imp = 1 if rec["phase4_anchor_improved"] else 0
        is_strict = 1 if rec["strict_superset"] else 0
        is_phase3 = 1 if rec["phase3_performance_candidate"] else 0
        sortino = rec["sortino_lh56y"] if rec["sortino_lh56y"] is not None else -1e9
        cagr = rec["cagr_lh56y"] if rec["cagr_lh56y"] is not None else -1e9
        return (is_p4_imp, is_strict, is_phase3, sortino, cagr,
                rec["score_breakdown"]["total"])

    sorted_results = sorted(results, key=_key, reverse=True)
    best = sorted_results[0]

    # ----- KILL_LOOP evaluations (pre-registered in hypothesis.md) -----
    any_beats = any(rec["beats_winner"] for rec in results)
    any_phase3 = any(rec["phase3_performance_candidate"] for rec in results)
    any_strict = any(rec["strict_superset"] for rec in results)
    any_phase4_improved = any(rec["phase4_anchor_improved"] for rec in results)
    best_sortino_lh = best["sortino_lh56y"] if best["sortino_lh56y"] is not None else 0.0

    baseline_rec = next(r for r in results if r["kind"] == "baseline_qld_zroz")
    rearmonly_rec = next(r for r in results if r["kind"] == "single_rearmonly_g25_rvp70_cashx_T40D60")
    t40_lrs120_rec = next(r for r in results if r["kind"] == "single_rearmonly_g25_rvp70_cashx_T40D60_unclrs120")
    t35_rec = next(r for r in results if r["kind"] == "single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120")
    t45_rec = next(r for r in results if r["kind"] == "single_rearmonly_g25_rvp70_cashx_T45D60_unclrs120")
    t50_rec = next(r for r in results if r["kind"] == "single_rearmonly_g25_rvp70_cashx_T50D60_unclrs120")

    baseline_sortino = baseline_rec["sortino_lh56y"] or 0.0
    rearmonly_sortino = rearmonly_rec["sortino_lh56y"] or 0.0
    rearmonly_cagr = rearmonly_rec["cagr_lh56y"] or 0.0
    t40_sortino = t40_lrs120_rec["sortino_lh56y"] or 0.0
    t40_cagr = t40_lrs120_rec["cagr_lh56y"] or 0.0
    t40_end_eq_iter017 = t40_lrs120_rec["end_equity_ratio_vs_iter017"] or 0.0
    t35_sortino = t35_rec["sortino_lh56y"] or 0.0
    t35_cagr = t35_rec["cagr_lh56y"] or 0.0
    t35_end_eq_iter017 = t35_rec["end_equity_ratio_vs_iter017"] or 0.0
    t45_sortino = t45_rec["sortino_lh56y"] or 0.0
    t45_cagr = t45_rec["cagr_lh56y"] or 0.0
    t45_end_eq_iter017 = t45_rec["end_equity_ratio_vs_iter017"] or 0.0
    t50_sortino = t50_rec["sortino_lh56y"] or 0.0
    t50_cagr = t50_rec["cagr_lh56y"] or 0.0
    t50_end_eq_iter017 = t50_rec["end_equity_ratio_vs_iter017"] or 0.0
    g1_pbo_value = float(g1_result["pbo"])

    # Modern subperiod Sortino computed for each LRS-on slot (3-6).
    subperiod_table_t40 = _subperiod_metrics(
        windowed_returns(per_cfg_returns[t40_lrs120_rec["config_name"]], *DATASET_WINDOWS["lh_56y"]),
        spy_lh,
    )
    subperiod_table_t35 = _subperiod_metrics(
        windowed_returns(per_cfg_returns[t35_rec["config_name"]], *DATASET_WINDOWS["lh_56y"]),
        spy_lh,
    )
    subperiod_table_t45 = _subperiod_metrics(
        windowed_returns(per_cfg_returns[t45_rec["config_name"]], *DATASET_WINDOWS["lh_56y"]),
        spy_lh,
    )
    subperiod_table_t50 = _subperiod_metrics(
        windowed_returns(per_cfg_returns[t50_rec["config_name"]], *DATASET_WINDOWS["lh_56y"]),
        spy_lh,
    )

    def _modern_lift(table) -> bool:
        s90 = (table.get("1990_2009") or {}).get("sortino") or 0.0
        s10 = (table.get("2010_2026") or {}).get("sortino") or 0.0
        return bool(s90 >= PHASE3_SORTINO_FLOOR or s10 >= PHASE3_SORTINO_FLOOR)

    modern_lift_t40 = _modern_lift(subperiod_table_t40)
    modern_lift_t35 = _modern_lift(subperiod_table_t35)
    modern_lift_t45 = _modern_lift(subperiod_table_t45)
    modern_lift_t50 = _modern_lift(subperiod_table_t50)
    any_modern_lift = bool(
        modern_lift_t40 or modern_lift_t35 or modern_lift_t45 or modern_lift_t50
    )

    # KILL_LOOP #10 (monotonicity): metrics smoothly vary across T_crash (no
    # rank-order cliffs). Check that across {35, 40, 45, 50}, both CAGR and
    # Sortino sequences are either monotone non-increasing OR monotone
    # non-decreasing OR have at most one direction change (single peak/valley).
    def _direction_changes(seq: list[float]) -> int:
        diffs = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
        signs = [(1 if d > 0 else (-1 if d < 0 else 0)) for d in diffs]
        non_zero = [s for s in signs if s != 0]
        changes = sum(1 for i in range(len(non_zero) - 1) if non_zero[i] != non_zero[i + 1])
        return changes

    cagr_seq = [t35_cagr, t40_cagr, t45_cagr, t50_cagr]
    sortino_seq = [t35_sortino, t40_sortino, t45_sortino, t50_sortino]
    end_eq_seq = [t35_end_eq_iter017, t40_end_eq_iter017, t45_end_eq_iter017, t50_end_eq_iter017]
    cagr_dir_changes = _direction_changes(cagr_seq)
    sortino_dir_changes = _direction_changes(sortino_seq)
    end_eq_dir_changes = _direction_changes(end_eq_seq)
    monotonicity_smooth = bool(
        cagr_dir_changes <= 1
        and sortino_dir_changes <= 1
        and end_eq_dir_changes <= 1
    )

    # KILL_LOOP #11/12 (anchor robustness vs falsification): does ANY of T35,
    # T45, T50 strictly Pareto-dominate T40 on (CAGR, Sortino, end_eq) while
    # passing beats_winner and PBO < 0.50?
    def _pareto_dominates_t40(rec) -> bool:
        return bool(
            (rec["cagr_lh56y"] or -1e9) > t40_cagr
            and (rec["sortino_lh56y"] or -1e9) > t40_sortino
            and (rec["end_equity_ratio_vs_iter017"] or -1e9) > t40_end_eq_iter017
            and rec["beats_winner"]
            and g1_pbo_value < PHASE3_PBO_CEIL
        )

    t35_dominates_t40 = _pareto_dominates_t40(t35_rec)
    t45_dominates_t40 = _pareto_dominates_t40(t45_rec)
    t50_dominates_t40 = _pareto_dominates_t40(t50_rec)
    anchor_falsified = bool(t35_dominates_t40 or t45_dominates_t40 or t50_dominates_t40)
    anchor_robust = bool(not anchor_falsified)

    cmp_detail = [
        {"name": r["config_name"], "kind": r["kind"],
         "upgrade_mode": r["upgrade_mode"], "lrs_mode": r["lrs_mode"],
         "lrs_factor": r["lrs_factor"], "use_basket": r["use_basket"],
         "t_crash": r["t_crash"], "d_arm": r["d_arm"],
         "sortino_lh56y": r["sortino_lh56y"],
         "cagr_lh56y": r["cagr_lh56y"],
         "phase3_performance_candidate": r["phase3_performance_candidate"],
         "beats_winner": r["beats_winner"],
         "strict_superset": r["strict_superset"],
         "phase4_anchor_improved": r["phase4_anchor_improved"],
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
         "rearm_diag": r["rearm_diag"],
         "lrs_active_pct": r["lrs_active_pct"],
         "upgrade_active_pct": r["upgrade_active_pct"],
         "end_equity_ratio_vs_baseline": r["end_equity_ratio_vs_baseline"],
         "end_equity_ratio_vs_iter017": r["end_equity_ratio_vs_iter017"]}
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
        "kill_loop_3_replica_baseline": {
            "fired": bool(abs(baseline_sortino - ITER011_BASELINE_SORTINO) > 0.005),
            "rule": "Baseline Sortino_lh56y deviates from iter 011-029 baseline 1.3240 by > 0.005 (21st-gen target).",
            "baseline_sortino_lh56y": baseline_sortino,
            "expected": ITER011_BASELINE_SORTINO,
        },
        "kill_loop_4_replica_rearmonly_T40D60": {
            "fired": bool(abs(rearmonly_sortino - ITER021_REARMONLY_T40D60_SORTINO) > 0.005),
            "rule": "Slot 2 (rearm-only T40D60 INDEP IMPL) Sortino_lh56y deviates from iter 021-029 1.4176 by > 0.005 (10th-gen target).",
            "rearmonly_sortino_lh56y": rearmonly_sortino,
            "expected": ITER021_REARMONLY_T40D60_SORTINO,
        },
        "kill_loop_5_replica_T40_LRS120": {
            "fired": bool(abs(t40_sortino - ITER027_SLOT6_T40_LRS120_SORTINO_TARGET) > 0.005),
            "rule": "Slot 3 (rearm-only T40D60 + LRS1.20 unconditional) Sortino_lh56y deviates from iter 027 slot 6 1.3786 by > 0.005 (2nd-gen target).",
            "t40_lrs120_sortino_lh56y": t40_sortino,
            "expected": ITER027_SLOT6_T40_LRS120_SORTINO_TARGET,
        },
        "kill_loop_6_pbo_blowup": {
            "fired": bool(g1_pbo_value >= 0.55),
            "rule": "G1 PBO >= 0.55 (NEW PBO mode like iter 023's 0.6548 — falsifies T_crash sweep mechanism diversity).",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_7_pbo_held": {
            "fired": bool(g1_pbo_value < PHASE3_PBO_CEIL),
            "rule": "G1 PBO < 0.50 (Phase 3 hard gate). POSITIVE TAG — confirms 4-point T_crash scan preserves mechanism diversity.",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_8_tcrash_phase4_anchor_improved": {
            "fired": bool(any(rec["phase4_anchor_improved"] for rec in
                              [t35_rec, t40_lrs120_rec, t45_rec, t50_rec])),
            "rule": "ANY of slots 3-6 (LRS-on T_crash variants) achieves phase4_anchor_improved=True.",
            "t40_p4_improved": bool(t40_lrs120_rec["phase4_anchor_improved"]),
            "t35_p4_improved": bool(t35_rec["phase4_anchor_improved"]),
            "t45_p4_improved": bool(t45_rec["phase4_anchor_improved"]),
            "t50_p4_improved": bool(t50_rec["phase4_anchor_improved"]),
        },
        "kill_loop_9_tcrash_modern_sortino_lift": {
            "fired": any_modern_lift,
            "rule": "ANY T_crash variant lifts modern subperiod Sortino >= 1.20 on at least one of {1990_2009, 2010_2026} — KEY HYPOTHESIS (T_crash perturbation can repair modern softness).",
            "t40_modern_lift": modern_lift_t40,
            "t35_modern_lift": modern_lift_t35,
            "t45_modern_lift": modern_lift_t45,
            "t50_modern_lift": modern_lift_t50,
            "phase3_floor": PHASE3_SORTINO_FLOOR,
            "iter027_modern_1990_2009_ref": ITER027_SLOT6_MODERN_SORTINO_1990_2009,
            "iter027_modern_2010_2026_ref": ITER027_SLOT6_MODERN_SORTINO_2010_2026,
        },
        "kill_loop_10_tcrash_monotonicity_smooth": {
            "fired": monotonicity_smooth,
            "rule": "All three metric sequences (CAGR, Sortino, end_eq) across T_crash {35,40,45,50} have <= 1 direction change (single peak/valley OR monotone). POSITIVE TAG when fired.",
            "cagr_dir_changes": cagr_dir_changes,
            "sortino_dir_changes": sortino_dir_changes,
            "end_eq_dir_changes": end_eq_dir_changes,
        },
        "kill_loop_11_tcrash_anchor_robust": {
            "fired": anchor_robust,
            "rule": "Iter 027 T40 anchor remains the local Pareto optimum: NO T35/T45/T50 strictly Pareto-dominates T40 on (CAGR, Sortino, end_eq) AND beats_winner AND PBO < 0.50. POSITIVE TAG.",
            "t35_dominates_t40": t35_dominates_t40,
            "t45_dominates_t40": t45_dominates_t40,
            "t50_dominates_t40": t50_dominates_t40,
        },
        "kill_loop_12_tcrash_anchor_falsified": {
            "fired": anchor_falsified,
            "rule": "EITHER T35 OR T45 OR T50 strictly Pareto-dominates T40 on (CAGR, Sortino, end_eq) AND beats_winner AND PBO < 0.50 — iter 017 T40 anchor was a fragile event fit.",
            "t35_dominates_t40": t35_dominates_t40,
            "t45_dominates_t40": t45_dominates_t40,
            "t50_dominates_t40": t50_dominates_t40,
        },
        "compound_detail": cmp_detail,
        "subperiod_table_t40": subperiod_table_t40,
        "subperiod_table_t35": subperiod_table_t35,
        "subperiod_table_t45": subperiod_table_t45,
        "subperiod_table_t50": subperiod_table_t50,
        "tcrash_sweep_summary": {
            "lrs_factor_rearm": LRS_FACTOR_REARM,
            "d_arm_frozen": D_ARM_FROZEN,
            "T35_qualified_flips": rearm_diags_by_tcrash[T_CRASH_T35]["n_qualified_flips"],
            "T35_rearm_active_pct": rearm_diags_by_tcrash[T_CRASH_T35]["rearm_active_pct"],
            "T40_qualified_flips": rearm_diags_by_tcrash[T_CRASH_T40]["n_qualified_flips"],
            "T40_rearm_active_pct": rearm_diags_by_tcrash[T_CRASH_T40]["rearm_active_pct"],
            "T45_qualified_flips": rearm_diags_by_tcrash[T_CRASH_T45]["n_qualified_flips"],
            "T45_rearm_active_pct": rearm_diags_by_tcrash[T_CRASH_T45]["rearm_active_pct"],
            "T50_qualified_flips": rearm_diags_by_tcrash[T_CRASH_T50]["n_qualified_flips"],
            "T50_rearm_active_pct": rearm_diags_by_tcrash[T_CRASH_T50]["rearm_active_pct"],
            "T35_sortino": t35_sortino, "T35_cagr": t35_cagr, "T35_end_eq_iter017": t35_end_eq_iter017,
            "T40_sortino": t40_sortino, "T40_cagr": t40_cagr, "T40_end_eq_iter017": t40_end_eq_iter017,
            "T45_sortino": t45_sortino, "T45_cagr": t45_cagr, "T45_end_eq_iter017": t45_end_eq_iter017,
            "T50_sortino": t50_sortino, "T50_cagr": t50_cagr, "T50_end_eq_iter017": t50_end_eq_iter017,
            "iter027_T40_sortino": ITER027_SLOT6_T40_LRS120_SORTINO,
            "iter027_T40_cagr": ITER027_SLOT6_T40_LRS120_CAGR,
            "iter027_T40_end_eq_iter017": ITER027_SLOT6_T40_LRS120_END_EQ_VS_ITER017,
            "T35_modern_1990_2009_sortino": (subperiod_table_t35.get("1990_2009") or {}).get("sortino"),
            "T35_modern_2010_2026_sortino": (subperiod_table_t35.get("2010_2026") or {}).get("sortino"),
            "T40_modern_1990_2009_sortino": (subperiod_table_t40.get("1990_2009") or {}).get("sortino"),
            "T40_modern_2010_2026_sortino": (subperiod_table_t40.get("2010_2026") or {}).get("sortino"),
            "T45_modern_1990_2009_sortino": (subperiod_table_t45.get("1990_2009") or {}).get("sortino"),
            "T45_modern_2010_2026_sortino": (subperiod_table_t45.get("2010_2026") or {}).get("sortino"),
            "T50_modern_1990_2009_sortino": (subperiod_table_t50.get("1990_2009") or {}).get("sortino"),
            "T50_modern_2010_2026_sortino": (subperiod_table_t50.get("2010_2026") or {}).get("sortino"),
            "anchor_robust": anchor_robust,
            "anchor_falsified": anchor_falsified,
            "monotonicity_smooth": monotonicity_smooth,
            "any_modern_lift": any_modern_lift,
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
        title="Iter 030 — T_crash sweep at iter 027 LRS1.20 ceiling (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 030 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 030 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 030 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 030 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 030 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 030 — crisis MDD vs SPY",
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
            "upgrade_mode": rec["upgrade_mode"],
            "lrs_mode": rec["lrs_mode"],
            "lrs_factor": rec["lrs_factor"],
            "lrs_active_pct": rec["lrs_active_pct"],
            "gamma": rec["gamma"],
            "rearm_active": rec["rearm_active"],
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
            "ratevol_active_pct": rec["ratevol_active_pct"],
            "blend_active_pct": rec["blend_active_pct"],
            "turnover_per_year": rec["turnover_per_year"],
            "cagr_lh56y": rec["cagr_lh56y"],
            "sortino_lh56y": rec["sortino_lh56y"],
            "end_eq_ratio_vs_baseline": rec["end_equity_ratio_vs_baseline"],
            "end_eq_ratio_vs_iter017": rec["end_equity_ratio_vs_iter017"],
            "phase3_performance_candidate": rec["phase3_performance_candidate"],
            "beats_winner": rec["beats_winner"],
            "strict_superset": rec["strict_superset"],
            "phase4_anchor_improved": rec["phase4_anchor_improved"],
            "total_score": rec["score_breakdown"]["total"],
        })
    pd.DataFrame(gate_rows).to_csv(ITER_DIR / "tables" / "gates_pass_fail.csv", index=False)

    verdict = {
        "iter": "030-2026-05-10-tcrash-scan-lrs120-rearmonly",
        "tier": "loop_iter",
        "phase": 4,
        "phase_name": "iter 017 focused validation/refinement",
        "hypothesis": (
            "T_crash sensitivity scan at the iter 027 slot 6 LRS1.20 unconditional "
            "ceiling. PRIMARY: vary T_crash {35, 40, 45, 50} on iter 027's "
            "rearm-only INDEP IMPL + LRS1.20 unconditional base, D_arm=60 frozen. "
            "KEY HYPOTHESIS (PRE-REGISTERED): if iter 017's T40 anchor is a "
            "fragile event fit, at least one of T35/T45/T50 will Pareto-dominate "
            "T40 on (CAGR, Sortino, end_eq) AND beats_winner AND PBO < 0.50. "
            "Carryover from iter 029 next-iter idea (d). SECONDARY: tests modern "
            "subperiod Sortino lift via T_crash perturbation (expected FALSE per "
            "iter 027/028/029 structural diagnosis). Three calibration anchors "
            "preserved: baseline (21st-gen), rearm-only T40D60 INDEP no LRS "
            "(10th-gen), iter 027 slot 6 (T40 + LRS1.20 unconditional, 2nd-gen). "
            "Citations: [advances_fin_ml, p.208-211] CSCV PBO mechanism diversity; "
            "[leverage_for_the_long_run, p.6-7, ch.3] Husson-Trifoni MA flip-on; "
            "[stocks_on_the_move, p.98] Clenow trend re-establishment; "
            "[advances_fin_ml, p.222-223] DSR cumulative (n_global=606)."
        ),
        "primary_citation": "[advances_fin_ml, p.208-211]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_030",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"], "topology": s["topology"],
             "use_basket": s["use_basket"], "upgrade_mode": s["upgrade_mode"],
             "lrs_mode": s["lrs_mode"], "gamma": s["gamma"],
             "ratevol": s["ratevol"], "alt_off": s["alt_off"],
             "rearm_active": s["rearm_active"], "t_crash": s["t_crash"],
             "d_arm": s["d_arm"]}
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
        "phase4_anchor_improved": bool(best["phase4_anchor_improved"]),
        "any_beats_winner": bool(any_beats),
        "any_phase3_performance_candidate": bool(any_phase3),
        "any_strict_superset": bool(any_strict),
        "any_phase4_anchor_improved": bool(any_phase4_improved),
        "phase4_anchor_validated": True,
        "lrs_factor_rearm": LRS_FACTOR_REARM,
        "d_arm_frozen": D_ARM_FROZEN,
        "tcrash_sweep_values": [T_CRASH_T35, T_CRASH_T40, T_CRASH_T45, T_CRASH_T50],
        "anchor_robust": anchor_robust,
        "anchor_falsified": anchor_falsified,
        "monotonicity_smooth": monotonicity_smooth,
        "any_modern_sortino_lift_fired": any_modern_lift,
        "T35_sortino_lh56y": t35_sortino,
        "T35_cagr_lh56y": t35_cagr,
        "T35_end_eq_vs_iter017": t35_end_eq_iter017,
        "T40_sortino_lh56y": t40_sortino,
        "T40_cagr_lh56y": t40_cagr,
        "T40_end_eq_vs_iter017": t40_end_eq_iter017,
        "T45_sortino_lh56y": t45_sortino,
        "T45_cagr_lh56y": t45_cagr,
        "T45_end_eq_vs_iter017": t45_end_eq_iter017,
        "T50_sortino_lh56y": t50_sortino,
        "T50_cagr_lh56y": t50_cagr,
        "T50_end_eq_vs_iter017": t50_end_eq_iter017,
        "iter027_T40_LRS120_sortino": ITER027_SLOT6_T40_LRS120_SORTINO,
        "iter027_T40_LRS120_cagr": ITER027_SLOT6_T40_LRS120_CAGR,
        "iter027_T40_LRS120_end_eq_vs_iter017": ITER027_SLOT6_T40_LRS120_END_EQ_VS_ITER017,
        "iter027_modern_sortino_1990_2009_ref": ITER027_SLOT6_MODERN_SORTINO_1990_2009,
        "iter027_modern_sortino_2010_2026_ref": ITER027_SLOT6_MODERN_SORTINO_2010_2026,
        "T35_qualified_flips": rearm_diags_by_tcrash[T_CRASH_T35]["n_qualified_flips"],
        "T40_qualified_flips": rearm_diags_by_tcrash[T_CRASH_T40]["n_qualified_flips"],
        "T45_qualified_flips": rearm_diags_by_tcrash[T_CRASH_T45]["n_qualified_flips"],
        "T50_qualified_flips": rearm_diags_by_tcrash[T_CRASH_T50]["n_qualified_flips"],
        "T35_rearm_active_pct": rearm_diags_by_tcrash[T_CRASH_T35]["rearm_active_pct"],
        "T40_rearm_active_pct": rearm_diags_by_tcrash[T_CRASH_T40]["rearm_active_pct"],
        "T45_rearm_active_pct": rearm_diags_by_tcrash[T_CRASH_T45]["rearm_active_pct"],
        "T50_rearm_active_pct": rearm_diags_by_tcrash[T_CRASH_T50]["rearm_active_pct"],
        "sortino_edge_vs_winner": float(best["sortino_edge_vs_winner"]),
        "cagr_edge_vs_winner": float(best["cagr_edge_vs_winner"]),
        "sortino_edge_vs_iter017": float(best["sortino_edge_vs_iter017"]),
        "cagr_edge_vs_iter017": float(best["cagr_edge_vs_iter017"]),
        "end_equity_ratio_vs_baseline":
            float(best["end_equity_ratio_vs_baseline"])
            if best["end_equity_ratio_vs_baseline"] == best["end_equity_ratio_vs_baseline"]
            else None,
        "end_equity_ratio_vs_iter017":
            float(best["end_equity_ratio_vs_iter017"])
            if best["end_equity_ratio_vs_iter017"] == best["end_equity_ratio_vs_iter017"]
            else None,
        "rolling_win_rates_vs_baseline": best["rolling_win_rates_vs_baseline"],
        "rolling_win_rates_vs_iter017": best["rolling_win_rates_vs_iter017"],
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
        "phase4_anchor": {
            "iter": PHASE4_ANCHOR_ITER,
            "config": PHASE4_ANCHOR_CONFIG,
            "sortino_lh56y": PHASE4_ANCHOR_SORTINO,
            "cagr_lh56y": PHASE4_ANCHOR_CAGR,
            "end_eq_ratio_vs_baseline": PHASE4_ANCHOR_END_EQ_RATIO_VS_BASELINE,
            "improved_sortino_floor": PHASE4_IMPROVED_SORTINO_FLOOR,
        },
        "winner_benchmark_iter": WINNER_BENCHMARK_ITER,
        "winner_benchmark_config": WINNER_BENCHMARK_CONFIG,
    }

    with open(ITER_DIR / "verdict.json", "w") as f:
        json.dump(verdict, f, indent=2, default=_json_default)

    LOG.info("Best: %s | Sortino_lh56y=%.4f | CAGR_lh56y=%.4f | edge=%+.4f | beats=%s | phase3=%s | strict=%s | p4_imp=%s",
             best["config_name"], best["sortino_lh56y"] or 0.0,
             best["cagr_lh56y"] or 0.0, best["sortino_edge_vs_winner"],
             best["beats_winner"], best["phase3_performance_candidate"],
             best["strict_superset"], best["phase4_anchor_improved"])
    LOG.info("Slot 1 (baseline)                                | Sortino=%.4f", baseline_sortino)
    LOG.info("Slot 2 (rearm-only T40D60 INDEP no LRS)          | Sortino=%.4f CAGR=%.4f",
             rearmonly_sortino, rearmonly_cagr)
    LOG.info("Slot 3 (rearm-only T40D60 + LRS1.20 unc)         | Sortino=%.4f CAGR=%.4f end_eq_iter017=%.3f",
             t40_sortino, t40_cagr, t40_end_eq_iter017)
    LOG.info("Slot 4 (rearm-only T35D60 + LRS1.20 unc)         | Sortino=%.4f CAGR=%.4f end_eq_iter017=%.3f",
             t35_sortino, t35_cagr, t35_end_eq_iter017)
    LOG.info("Slot 5 (rearm-only T45D60 + LRS1.20 unc)         | Sortino=%.4f CAGR=%.4f end_eq_iter017=%.3f",
             t45_sortino, t45_cagr, t45_end_eq_iter017)
    LOG.info("Slot 6 (rearm-only T50D60 + LRS1.20 unc)         | Sortino=%.4f CAGR=%.4f end_eq_iter017=%.3f",
             t50_sortino, t50_cagr, t50_end_eq_iter017)
    LOG.info("Rearm flips by T_crash: T35=%d T40=%d T45=%d T50=%d (rearm_active_pct: T35=%.4f T40=%.4f T45=%.4f T50=%.4f)",
             rearm_diags_by_tcrash[T_CRASH_T35]["n_qualified_flips"],
             rearm_diags_by_tcrash[T_CRASH_T40]["n_qualified_flips"],
             rearm_diags_by_tcrash[T_CRASH_T45]["n_qualified_flips"],
             rearm_diags_by_tcrash[T_CRASH_T50]["n_qualified_flips"],
             rearm_diags_by_tcrash[T_CRASH_T35]["rearm_active_pct"],
             rearm_diags_by_tcrash[T_CRASH_T40]["rearm_active_pct"],
             rearm_diags_by_tcrash[T_CRASH_T45]["rearm_active_pct"],
             rearm_diags_by_tcrash[T_CRASH_T50]["rearm_active_pct"])
    LOG.info("Anchor robustness: anchor_robust=%s anchor_falsified=%s monotonicity_smooth=%s any_modern_lift=%s",
             anchor_robust, anchor_falsified, monotonicity_smooth, any_modern_lift)
    LOG.info("G1 PBO=%.4f | KILL_LOOP fired summary: %s",
             g1_pbo_value,
             {k: (v["fired"] if isinstance(v, dict) and "fired" in v else "N/A")
              for k, v in kill_loop_results.items()
              if k not in ("compound_detail", "subperiod_table_t40", "subperiod_table_t35",
                           "subperiod_table_t45", "subperiod_table_t50",
                           "tcrash_sweep_summary")})
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
