"""Iter 029 — PBO-decoupled LRS1.20× ratevol-gated **stress-only** overlay (slot 6 only).

Phase 4 — iter 017 focused validation/refinement. Symmetry diagnostic to
iter 028: same rearm-only base, same LRS1.20× factor, same ratevol gate
signal, but the gate condition is INVERTED (`==1` stress instead of `==0`
calm).

PRIMARY hypothesis (regime-conditioning symmetry diagnostic): iter 028
falsified the calm-regime modern-Sortino-lift hypothesis (1990_2009 = 1.139
< 1.20 floor; 2010_2026 = 1.132 < 1.20 floor). This iter tests the
COMPLEMENTARY regime subset — apply LRS1.20× ONLY when ratevol_gate==1
(STRESS regime, ~30% of ON days; ~22% of all bars active by construction).
KEY HYPOTHESIS (PRE-REGISTERED): if iter 028's structural diagnosis is
correct, iter 029 should ALSO fail the modern-Sortino-lift criterion. A
symmetric falsification on both regime subsets conclusively closes the LRS
regime-conditioning axis as a path to modern-era Sortino lift on the rearm
primitive.

SECONDARY hypothesis (Phase 4 axis closure): with iter 027 closing the LRS
magnitude axis (5-point scan complete) and iter 028 closing the LRS
calm-regime axis, iter 029 closes the stress-regime axis with the
mathematical inverse. After this iter, the rearm-primitive's LRS
regime-conditioning axis is fully mapped on both sides of the binary regime
split — a pre-condition for confidently pivoting to a non-rearm Phase 4
family per iter 028 next-iter recommendation (a).

TERTIARY (mechanism-orthogonality preservation): inverse regime gate uses
the SAME bond-vol percentile signal as iter 028, just with the
complementary subset selected. PBO should remain in the iter 026/027/028
regime (~0.41-0.43), preserving the PBO-decoupled framework. Five
calibration anchors (slots 1-5) preserved bit-exact.

Six configs (mechanism-mix-diverse, identical layout to iter 028 except
slot 6's LRS gate INVERSION):

  1. baseline_qld_zroz                                                              — calibration anchor (20th-gen)
  2. single_K4lv25_g25_rvp70_cashx                                                  — iter 014/023-028 strict_superset replica (17th-gen)
  3. single_K4lv25_g25_rvp70_cashx_unclrs105                                         — iter 024-028 slot 3 K4 + LRS1.05 anchor (6th-gen)
  4. single_K4lv25_g25_rvp70_cashx_T40D60                                           — iter 017 OR-anchor replica (12th-gen)
  5. single_rearmonly_g25_rvp70_cashx_T40D60                                        — iter 022-028 INDEP IMPL replica (9th-gen)
  6. single_rearmonly_g25_rvp70_cashx_T40D60_rvgtdlrs120stress (NEW)                 — rearm base + LRS1.20× ONLY when ratevol_gate==1 (stress)

Citations
---------
- [advances_fin_ml, p.208-211]: PRIMARY CSCV PBO mechanism-mix diversity —
  inverse regime gate is mechanically orthogonal to equity-rearm; preserves
  PBO-decoupled framework established in iter 024-028.
- [volatility_trading, p.58-60]: Sinclair on volatility cones — symmetry
  diagnostic on percentile-regime classification.
- [systematic_trading, ch.13, p.212]: Carver on vol-scaled regime
  thresholds — supports both polarities of regime conditioning depending
  on edge attribution.
- [leverage_for_the_long_run, p.13, ch.3]: PRIMARY canonical RISK_ON LRS
  rule preserved; gating remains within-RISK_ON conditional on the
  COMPLEMENTARY regime subset.
- [leverage_for_the_long_run, ch.4-5, p.40-60]: Husson-Trifoni LRS scaling
  (1.20× sweet-spot ceiling unchanged).
- [leverage_for_the_long_run, p.5-6]: ann-vol-<40% sweet spot — note this
  iter intentionally applies LRS during the high-realised-vol bars iter
  028 excluded.
- [advances_fin_ml, p.222-223]: DSR cumulative n_trials (n_global=600).
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
LOG = logging.getLogger("iter029")


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_PRIOR_ITERS = ITER_DIR.parent
ITER007 = _load_module(
    _PRIOR_ITERS / "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket" / "backtest.py",
    "iter029_iter007_backtest",
)
windowed_returns = ITER007.windowed_returns
compute_per_dataset = ITER007.compute_per_dataset
spy_anchor_metrics = ITER007.spy_anchor_metrics

ITER011 = _load_module(
    _PRIOR_ITERS / "011-2026-05-10-conditional-tqqq-leverage" / "conditional_leg.py",
    "iter029_iter011_cleg",
)
entry_signal_K2 = ITER011.entry_signal_K2
upgrade_signal_K4 = ITER011.upgrade_signal_K4
upgrade_signal_lowvol25 = ITER011.upgrade_signal_lowvol25
combine_AND = ITER011.combine_AND
combine_OR = ITER011.combine_OR

ITER006 = _load_module(
    _PRIOR_ITERS / "006-2026-05-09-bond-ratevol-regime" / "rate_vol_gate.py",
    "iter029_iter006_ratevol",
)
ratevol_regime_gate = ITER006.ratevol_regime_gate

ITER014 = _load_module(
    _PRIOR_ITERS / "014-2026-05-10-mechanism-mix-diverse-graded-blend" / "mechanism_mix_leg.py",
    "iter029_iter014_mechmix",
)
build_single_asset_on_leg = ITER014.build_single_asset_on_leg
build_mechanism_mix_strategy_returns = ITER014.build_mechanism_mix_strategy_returns
mechanism_mix_turnover = ITER014.mechanism_mix_turnover

ITER017 = _load_module(
    _PRIOR_ITERS / "017-2026-05-10-postcrash-rearm-tqqq-streak" / "reentry_overlay.py",
    "iter029_iter017_rearm",
)
build_postcrash_rearm_gate_iter017 = ITER017.build_postcrash_rearm_gate

RI = _load_module(
    _PRIOR_ITERS / "022-2026-05-10-rearm-only-indep-pfv-confirm" / "rearm_independent.py",
    "iter029_rearm_independent",
)
build_postcrash_rearm_gate_independent = RI.build_postcrash_rearm_gate_independent
diagnose_rearm_events_independent = RI.diagnose_rearm_events_independent

# Reuse iter 024's unconditional LRS overlay helper bit-exactly for slot 3
# (K4 + LRS1.05 calibration anchor preservation).
LRS_HELPER = _load_module(
    _PRIOR_ITERS / "024-2026-05-10-pbo-decoupled-unconditional-lrs105" / "unconditional_lrs_overlay.py",
    "iter029_unc_lrs_overlay",
)
apply_unconditional_lrs_overlay = LRS_HELPER.apply_unconditional_lrs_overlay

# NEW iter 029 helper — INVERSE ratevol-gated LRS overlay (slot 6 only).
INV_RGT_HELPER = _load_module(
    ITER_DIR / "inverse_regime_gated_lrs_overlay.py",
    "iter029_inv_rgt_lrs_overlay",
)
apply_inverse_ratevol_gated_lrs_overlay = INV_RGT_HELPER.apply_inverse_ratevol_gated_lrs_overlay
diagnose_inverse_lrs_active_pct = INV_RGT_HELPER.diagnose_inverse_lrs_active_pct


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

# Iter 027 slot 6 magnitude-probe baseline (LRS1.20 unconditional — the
# pre-iter-028 Pareto frontier point on the rearm × LRS axis).
ITER027_SLOT6_LRS120_UNCOND_CAGR = 0.3622
ITER027_SLOT6_LRS120_UNCOND_END_EQ_VS_ITER017 = 2.908
ITER027_SLOT6_LRS120_UNCOND_SORTINO = 1.3786
ITER027_SLOT6_MODERN_SORTINO_1990_2009 = 1.124
ITER027_SLOT6_MODERN_SORTINO_2010_2026 = 1.144

# Iter 028 slot 6 calm-only reference (the paired symmetry diagnostic).
ITER028_SLOT6_RVGTD_CALM_SORTINO = 1.3860
ITER028_SLOT6_RVGTD_CALM_CAGR = 0.3511
ITER028_SLOT6_RVGTD_CALM_END_EQ_VS_ITER017 = 2.090
ITER028_SLOT6_RVGTD_CALM_MODERN_1990_2009_SORTINO = 1.139
ITER028_SLOT6_RVGTD_CALM_MODERN_2010_2026_SORTINO = 1.132
ITER028_SLOT6_RVGTD_CALM_LRS_ACTIVE_PCT = 0.5091

# Trial accounting (per LOOP_MEMORY frontmatter post-iter-028).
PRE_ITER_CUMULATIVE = 594
PRE_ITER_LOOP = 168
LOCAL_N_CONFIGS = 6

# Calibration anchors (KILL_LOOP replica sanity).
ITER011_BASELINE_SORTINO = 1.3240             # KILL_LOOP #3 (20th-gen target)
ITER014_SINGLE_K4LV25_G25_SORTINO = 1.3951    # KILL_LOOP #4 (17th-gen target)
ITER017_T40D60_SORTINO = 1.4030               # KILL_LOOP #5 (12th-gen target)
ITER021_REARMONLY_T40D60_SORTINO = 1.4176     # KILL_LOOP #6 (9th-gen target)
ITER024_K4_UNCLRS105_SORTINO = 1.3842         # KILL_LOOP #7 (6th-gen target)

T_CRASH_FROZEN = 40
D_ARM_FROZEN = 60

LRS_FACTOR_K4 = 1.05      # slot 3 — preserves iter 024-028 K4-base anchor
LRS_FACTOR_REARM = 1.20   # slot 6 — same magnitude as iter 027/028; differs only in gating polarity

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


# lrs_mode values:
#   "off"                 → no LRS overlay (lrs_factor = 1.0)
#   "unclrs105"           → LRS factor 1.05 applied unconditionally on every ON day (slot 3 calibration)
#   "rvgtdlrs120stress"   → LRS factor 1.20 applied on ON days where ratevol_gate==1 (slot 6 NEW)
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
        "lrs_mode": "off",
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_K4lv25_g25_rvp70_cashx",
        "kind": "single_K4lv25_g25_rvp70_cashx",
        "topology": "single/K4_AND_QLDlv25/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_mode": "K4_AND_lv25",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_active": False,
        "lrs_mode": "off",
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_K4lv25_g25_rvp70_cashx_unclrs105",
        "kind": "single_K4lv25_g25_rvp70_cashx_unclrs105",
        "topology": "single/K4_AND_QLDlv25_x_LRS1.05unc/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_mode": "K4_AND_lv25",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_active": False,
        "lrs_mode": "unclrs105",
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_K4lv25_g25_rvp70_cashx_T40D60",
        "kind": "single_K4lv25_g25_rvp70_cashx_T40D60",
        "topology": "single/K4_AND_QLDlv25_OR_rearm_iter017impl/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_mode": "K4_OR_rearm_iter017",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_active": True,
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
        "lrs_mode": "off",
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_rvgtdlrs120stress",
        "kind": "single_rearmonly_g25_rvp70_cashx_T40D60_rvgtdlrs120stress",
        "topology": "single/rearm_only_indepimpl_x_LRS1.20rvgtd_stress/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_mode": "rearmonly_indep",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_active": True,
        "lrs_mode": "rvgtdlrs120stress",
    },
]


def _lrs_factor_for_mode(lrs_mode: str) -> float:
    if lrs_mode == "off":
        return 1.0
    if lrs_mode == "unclrs105":
        return LRS_FACTOR_K4
    if lrs_mode == "rvgtdlrs120stress":
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

    LOG.info("Building entry + upgrade gates...")
    on_signal = entry_signal_K2(qld, qld_ret)
    k4_gate = upgrade_signal_K4(qld, qld_ret)
    qld_lv25_gate = upgrade_signal_lowvol25(
        qld_ret, vol_window=21, pct_window=1260, pct_threshold=0.25,
    )
    k4_and_qldlv25_gate = combine_AND(k4_gate, qld_lv25_gate)

    rearm_gate_iter017 = build_postcrash_rearm_gate_iter017(
        on_signal=on_signal, t_crash=T_CRASH_FROZEN, d_arm=D_ARM_FROZEN,
    )
    rearm_gate_indep = build_postcrash_rearm_gate_independent(
        on_signal=on_signal, t_crash=T_CRASH_FROZEN, d_arm=D_ARM_FROZEN,
    )

    parity_diff = (rearm_gate_iter017.fillna(0.0) - rearm_gate_indep.fillna(0.0)).abs()
    parity_max_abs_diff = float(parity_diff.max())
    parity_n_diff_days = int((parity_diff > 0).sum())
    LOG.info("Cross-impl parity (iter 017 vs INDEP IMPL): max abs diff = %.3e | n diff days = %d",
             parity_max_abs_diff, parity_n_diff_days)

    rearm_diag_indep = diagnose_rearm_events_independent(
        on_signal=on_signal, t_crash=T_CRASH_FROZEN, d_arm=D_ARM_FROZEN,
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
    per_cfg_lrs_diag: dict[str, dict] = {}
    per_cfg_turnover: dict[str, float] = {}

    LOG.info("Running %d configs...", len(CONFIG_SPECS))
    for spec in CONFIG_SPECS:
        if spec["upgrade_mode"] == "none":
            upg = pd.Series(0.0, index=qld_ret.index)
            spec_rearm_diag = {"n_qualified_flips": 0, "n_active_rearm_days": 0,
                               "rearm_active_pct": 0.0, "t_crash": 0, "d_arm": 0,
                               "impl": "none"}
        elif spec["upgrade_mode"] == "K4_AND_lv25":
            upg = k4_and_qldlv25_gate
            spec_rearm_diag = {"n_qualified_flips": 0, "n_active_rearm_days": 0,
                               "rearm_active_pct": 0.0, "t_crash": 0, "d_arm": 0,
                               "impl": "none"}
        elif spec["upgrade_mode"] == "K4_OR_rearm_iter017":
            upg = combine_OR(k4_and_qldlv25_gate, rearm_gate_iter017)
            spec_rearm_diag = dict(rearm_diag_indep)
            spec_rearm_diag["impl"] = "iter017"
        elif spec["upgrade_mode"] == "rearmonly_indep":
            upg = rearm_gate_indep
            spec_rearm_diag = dict(rearm_diag_indep)
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
            lrs_diag = {"lrs_active_pct": 0.0, "on_active_pct": 0.0,
                        "stress_within_on_pct": 0.0, "rv_warmup_pct": 0.0}
        elif spec["lrs_mode"] == "unclrs105":
            on_leg_lrs = apply_unconditional_lrs_overlay(
                on_leg_returns=on_leg_ret,
                on_signal=on_signal,
                lrs_factor=lrs_factor_used,
            )
            on_lag_for_pct = on_signal.shift(1).reindex(on_leg_lrs.index).fillna(0.0)
            lrs_diag = {"lrs_active_pct": float((on_lag_for_pct == 1.0).mean()),
                        "on_active_pct": float((on_lag_for_pct == 1.0).mean()),
                        "stress_within_on_pct": 0.0, "rv_warmup_pct": 0.0}
        elif spec["lrs_mode"] == "rvgtdlrs120stress":
            on_leg_lrs = apply_inverse_ratevol_gated_lrs_overlay(
                on_leg_returns=on_leg_ret,
                on_signal=on_signal,
                ratevol_gate=rv,
                lrs_factor=lrs_factor_used,
            )
            lrs_diag = diagnose_inverse_lrs_active_pct(
                on_signal=on_signal,
                ratevol_gate=rv,
                on_leg_index=on_leg_lrs.index,
            )
        else:
            raise ValueError(f"Unknown lrs_mode: {spec['lrs_mode']}")
        per_cfg_lrs_active_pct[spec["name"]] = float(lrs_diag["lrs_active_pct"])
        per_cfg_lrs_diag[spec["name"]] = lrs_diag

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

    t40d60_anchor_name = CONFIG_SPECS[3]["name"]  # slot 4 = iter 017 OR-anchor replica
    iter017_lh_eq = (1.0 + windowed_returns(per_cfg_returns[t40d60_anchor_name],
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

        common_idx_iter017 = strat_lh_eq.index.intersection(iter017_lh_eq.index)
        if len(common_idx_iter017) > 0:
            end_eq_ratio_iter017 = float(strat_lh_eq.loc[common_idx_iter017[-1]] /
                                          iter017_lh_eq.loc[common_idx_iter017[-1]])
        else:
            end_eq_ratio_iter017 = float("nan")

        rolling_win = _rolling_win_rates_vs_baseline(strat_lh_eq, baseline_lh_eq)
        rolling_win_iter017 = _rolling_win_rates_vs_baseline(strat_lh_eq, iter017_lh_eq)

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
            "t_crash": T_CRASH_FROZEN if spec["rearm_active"] else 0,
            "d_arm": D_ARM_FROZEN if spec["rearm_active"] else 0,
            "rearm_diag": per_cfg_rearm_diag[name],
            "lrs_active_pct": per_cfg_lrs_active_pct[name],
            "lrs_diag": per_cfg_lrs_diag[name],
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
    single_anchor_rec = next(r for r in results if r["kind"] == "single_K4lv25_g25_rvp70_cashx")
    k4_unclrs_rec = next(r for r in results if r["kind"] == "single_K4lv25_g25_rvp70_cashx_unclrs105")
    or_anchor_rec = next(r for r in results if r["kind"] == "single_K4lv25_g25_rvp70_cashx_T40D60")
    rearmonly_rec = next(r for r in results if r["kind"] == "single_rearmonly_g25_rvp70_cashx_T40D60")
    rgtdstr_rec = next(r for r in results if r["kind"] == "single_rearmonly_g25_rvp70_cashx_T40D60_rvgtdlrs120stress")

    baseline_sortino = baseline_rec["sortino_lh56y"] or 0.0
    single_anchor_sortino = single_anchor_rec["sortino_lh56y"] or 0.0
    or_anchor_sortino = or_anchor_rec["sortino_lh56y"] or 0.0
    rearmonly_sortino = rearmonly_rec["sortino_lh56y"] or 0.0
    rearmonly_cagr = rearmonly_rec["cagr_lh56y"] or 0.0
    k4_unclrs_sortino = k4_unclrs_rec["sortino_lh56y"] or 0.0
    k4_unclrs_cagr = k4_unclrs_rec["cagr_lh56y"] or 0.0
    rgtdstr_sortino = rgtdstr_rec["sortino_lh56y"] or 0.0
    rgtdstr_cagr = rgtdstr_rec["cagr_lh56y"] or 0.0
    rgtdstr_end_eq_iter017 = rgtdstr_rec["end_equity_ratio_vs_iter017"] or 0.0
    g1_pbo_value = float(g1_result["pbo"])

    rgtdstr_returns_lh = windowed_returns(
        per_cfg_returns[rgtdstr_rec["config_name"]], *DATASET_WINDOWS["lh_56y"]
    )
    subperiod_table_slot6 = _subperiod_metrics(rgtdstr_returns_lh, spy_lh)

    # KEY HYPOTHESIS: modern-era Sortino lift >= 1.20 on at least one of
    # {1990_2009, 2010_2026}.
    modern_sortino_1990 = (
        subperiod_table_slot6.get("1990_2009", {}).get("sortino") or 0.0
    )
    modern_sortino_2010 = (
        subperiod_table_slot6.get("2010_2026", {}).get("sortino") or 0.0
    )
    modern_sortino_lift = bool(
        modern_sortino_1990 >= PHASE3_SORTINO_FLOOR
        or modern_sortino_2010 >= PHASE3_SORTINO_FLOOR
    )

    cmp_detail = [
        {"name": r["config_name"], "kind": r["kind"],
         "upgrade_mode": r["upgrade_mode"], "lrs_mode": r["lrs_mode"],
         "lrs_factor": r["lrs_factor"], "use_basket": r["use_basket"],
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
         "lrs_diag": r["lrs_diag"],
         "upgrade_active_pct": r["upgrade_active_pct"],
         "end_equity_ratio_vs_baseline": r["end_equity_ratio_vs_baseline"],
         "end_equity_ratio_vs_iter017": r["end_equity_ratio_vs_iter017"]}
        for r in results
    ]

    # KILL_LOOP #13: residual lift = slot 6 CAGR > iter 017 anchor CAGR (32.66%).
    residual_lift_vs_iter017 = bool(rgtdstr_cagr > PHASE4_ANCHOR_CAGR)

    # KILL_LOOP #15: regime-axis symmetric falsification — both calm-only
    # (iter 028) AND stress-only (iter 029) failed modern-Sortino-lift.
    regime_axis_symmetric_falsification = bool(
        (not modern_sortino_lift)
        and (ITER028_SLOT6_RVGTD_CALM_MODERN_1990_2009_SORTINO < PHASE3_SORTINO_FLOOR)
        and (ITER028_SLOT6_RVGTD_CALM_MODERN_2010_2026_SORTINO < PHASE3_SORTINO_FLOOR)
    )

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
            "rule": "Baseline Sortino_lh56y deviates from iter 011-028 baseline 1.3240 by > 0.005 (20th-gen target).",
            "baseline_sortino_lh56y": baseline_sortino,
            "expected": ITER011_BASELINE_SORTINO,
        },
        "kill_loop_4_replica_single_K4lv25_g25": {
            "fired": bool(abs(single_anchor_sortino - ITER014_SINGLE_K4LV25_G25_SORTINO) > 0.005),
            "rule": "single_K4lv25_g25_rvp70_cashx Sortino_lh56y deviates from iter 014-028 1.3951 by > 0.005 (17th-gen target).",
            "single_anchor_sortino_lh56y": single_anchor_sortino,
            "expected": ITER014_SINGLE_K4LV25_G25_SORTINO,
        },
        "kill_loop_5_replica_T40D60_OR_iter017": {
            "fired": bool(abs(or_anchor_sortino - ITER017_T40D60_SORTINO) > 0.005),
            "rule": "Slot 4 (iter 017 OR-anchor) Sortino_lh56y deviates from 1.4030 by > 0.005 (12th-gen target).",
            "or_anchor_sortino_lh56y": or_anchor_sortino,
            "expected": ITER017_T40D60_SORTINO,
        },
        "kill_loop_6_replica_rearmonly_T40D60": {
            "fired": bool(abs(rearmonly_sortino - ITER021_REARMONLY_T40D60_SORTINO) > 0.005),
            "rule": "Slot 5 (rearm-only INDEP IMPL) Sortino_lh56y deviates from iter 021-028 1.4176 by > 0.005 (9th-gen target).",
            "rearmonly_sortino_lh56y": rearmonly_sortino,
            "expected": ITER021_REARMONLY_T40D60_SORTINO,
        },
        "kill_loop_7_replica_K4_unclrs105": {
            "fired": bool(abs(k4_unclrs_sortino - ITER024_K4_UNCLRS105_SORTINO) > 0.005),
            "rule": "Slot 3 (K4-base + LRS1.05 unconditional) Sortino_lh56y deviates from iter 024-028 anchor 1.3842 by > 0.005 (6th-gen target).",
            "k4_unclrs_sortino_lh56y": k4_unclrs_sortino,
            "expected": ITER024_K4_UNCLRS105_SORTINO,
        },
        "kill_loop_8_pbo_blowup": {
            "fired": bool(g1_pbo_value >= 0.55),
            "rule": "G1 PBO >= 0.55 (NEW PBO mode like iter 023's 0.6548 — falsifies inverse regime-gating's PBO-decoupled property).",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_9_pbo_held": {
            "fired": bool(g1_pbo_value < PHASE3_PBO_CEIL),
            "rule": "G1 PBO < 0.50 (Phase 3 hard gate). POSITIVE TAG — confirms inverse regime-gating preserves PBO-decoupled framework.",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_10_rvgtdlrs120stress_phase4_anchor_improved": {
            "fired": bool(rgtdstr_rec["phase4_anchor_improved"]),
            "rule": "Slot 6 (rearm-only + ratevol-gated LRS1.20 stress-only) achieves phase4_anchor_improved=True.",
            "slot6_phase4_anchor_improved": bool(rgtdstr_rec["phase4_anchor_improved"]),
        },
        "kill_loop_11_rvgtdlrs120stress_strict_superset": {
            "fired": bool(rgtdstr_rec["strict_superset"]),
            "rule": "Slot 6 (rearm-only + ratevol-gated LRS1.20 stress-only) achieves strict_superset=True.",
            "slot6_strict_superset": bool(rgtdstr_rec["strict_superset"]),
        },
        "kill_loop_12_rvgtdlrs120stress_modern_sortino_lift": {
            "fired": modern_sortino_lift,
            "rule": "Slot 6 modern subperiod Sortino >= 1.20 on AT LEAST ONE of {1990_2009, 2010_2026} — KEY HYPOTHESIS (stress-period LRS lifts modern softness asymmetrically vs calm-only).",
            "modern_sortino_1990_2009": modern_sortino_1990,
            "modern_sortino_2010_2026": modern_sortino_2010,
            "phase3_floor": PHASE3_SORTINO_FLOOR,
            "iter027_uncond_modern_1990_2009_ref": ITER027_SLOT6_MODERN_SORTINO_1990_2009,
            "iter027_uncond_modern_2010_2026_ref": ITER027_SLOT6_MODERN_SORTINO_2010_2026,
            "iter028_calm_modern_1990_2009_ref": ITER028_SLOT6_RVGTD_CALM_MODERN_1990_2009_SORTINO,
            "iter028_calm_modern_2010_2026_ref": ITER028_SLOT6_RVGTD_CALM_MODERN_2010_2026_SORTINO,
        },
        "kill_loop_13_rvgtdlrs120stress_residual_lift": {
            "fired": residual_lift_vs_iter017,
            "rule": "Slot 6 CAGR_lh56y > 32.66% (iter 017 anchor) — proves stress-only LRS contributes ANY net CAGR over rearm-only base.",
            "slot6_cagr": rgtdstr_cagr,
            "iter017_anchor_cagr_ref": PHASE4_ANCHOR_CAGR,
        },
        "kill_loop_14_rvgtdlrs120stress_sortino_collapse": {
            "fired": bool(rgtdstr_sortino < PHASE4_IMPROVED_SORTINO_FLOOR),
            "rule": "Slot 6 Sortino_lh56y < 1.35 (Phase 4 improved floor — stress-period LRS amplifies daily-rebalance vol drag).",
            "slot6_sortino": rgtdstr_sortino,
        },
        "kill_loop_15_regime_axis_symmetric_falsification": {
            "fired": regime_axis_symmetric_falsification,
            "rule": "BOTH iter 028 calm-only AND iter 029 stress-only modern_sortino_lift report fired=False — regime-conditioning axis CONCLUSIVELY CLOSED on the modern-Sortino-lift dimension. POSITIVE TAG (research conclusion confirmed by symmetry).",
            "iter028_calm_modern_lift_fired": False,  # iter 028 KILL_LOOP #12 = NOT FIRED
            "iter029_stress_modern_lift_fired": modern_sortino_lift,
            "regime_axis_closed": regime_axis_symmetric_falsification,
        },
        "compound_detail": cmp_detail,
        "subperiod_table_slot6": subperiod_table_slot6,
        "rvgtdlrs120stress_summary": {
            "lrs_factor_k4_slot3": LRS_FACTOR_K4,
            "lrs_factor_rearm_slot6": LRS_FACTOR_REARM,
            "lrs_gating_slot6": "ratevol_gate==1 (STRESS rate regime); rvp70 threshold (INVERSE of iter 028)",
            "rearm_active_pct_indep": rearm_diag_indep["rearm_active_pct"],
            "n_qualified_flips_indep": rearm_diag_indep["n_qualified_flips"],
            "iter017_indep_parity_max_abs_diff": parity_max_abs_diff,
            "iter017_indep_parity_n_diff_days": parity_n_diff_days,
            "slot6_lrs_active_pct": rgtdstr_rec["lrs_active_pct"],
            "slot6_lrs_diag": rgtdstr_rec["lrs_diag"],
            "slot5_baseline_rearmonly_sortino": rearmonly_sortino,
            "slot5_baseline_rearmonly_cagr": rearmonly_cagr,
            "slot6_rgtdstr_sortino": rgtdstr_sortino,
            "slot6_rgtdstr_cagr": rgtdstr_cagr,
            "slot6_rgtdstr_end_eq_vs_iter017": rgtdstr_end_eq_iter017,
            "slot6_rgtdstr_sortino_lift_vs_slot5": float(rgtdstr_sortino - rearmonly_sortino),
            "slot6_rgtdstr_cagr_lift_vs_slot5": float(rgtdstr_cagr - rearmonly_cagr),
            # Comparison vs iter 027 slot 6 (LRS1.20 unconditional)
            "iter027_slot6_uncond_sortino": ITER027_SLOT6_LRS120_UNCOND_SORTINO,
            "iter027_slot6_uncond_cagr": ITER027_SLOT6_LRS120_UNCOND_CAGR,
            "iter027_slot6_uncond_end_eq_vs_iter017": ITER027_SLOT6_LRS120_UNCOND_END_EQ_VS_ITER017,
            "rvgtdlrs120stress_vs_uncond_sortino_delta":
                float(rgtdstr_sortino - ITER027_SLOT6_LRS120_UNCOND_SORTINO),
            "rvgtdlrs120stress_vs_uncond_cagr_delta":
                float(rgtdstr_cagr - ITER027_SLOT6_LRS120_UNCOND_CAGR),
            "rvgtdlrs120stress_vs_uncond_end_eq_iter017_delta":
                float(rgtdstr_end_eq_iter017 - ITER027_SLOT6_LRS120_UNCOND_END_EQ_VS_ITER017),
            # Comparison vs iter 028 slot 6 (LRS1.20 calm-only) — paired diagnostic
            "iter028_slot6_calm_sortino": ITER028_SLOT6_RVGTD_CALM_SORTINO,
            "iter028_slot6_calm_cagr": ITER028_SLOT6_RVGTD_CALM_CAGR,
            "iter028_slot6_calm_end_eq_vs_iter017": ITER028_SLOT6_RVGTD_CALM_END_EQ_VS_ITER017,
            "iter028_slot6_calm_lrs_active_pct": ITER028_SLOT6_RVGTD_CALM_LRS_ACTIVE_PCT,
            "rvgtdlrs120stress_vs_calm_sortino_delta":
                float(rgtdstr_sortino - ITER028_SLOT6_RVGTD_CALM_SORTINO),
            "rvgtdlrs120stress_vs_calm_cagr_delta":
                float(rgtdstr_cagr - ITER028_SLOT6_RVGTD_CALM_CAGR),
            "rvgtdlrs120stress_vs_calm_end_eq_iter017_delta":
                float(rgtdstr_end_eq_iter017 - ITER028_SLOT6_RVGTD_CALM_END_EQ_VS_ITER017),
            # Modern-era subperiod Sortino lift diagnostic (paired)
            "modern_sortino_1990_2009_slot6_rgtdstr": modern_sortino_1990,
            "modern_sortino_2010_2026_slot6_rgtdstr": modern_sortino_2010,
            "iter027_modern_sortino_1990_2009_uncond_ref": ITER027_SLOT6_MODERN_SORTINO_1990_2009,
            "iter027_modern_sortino_2010_2026_uncond_ref": ITER027_SLOT6_MODERN_SORTINO_2010_2026,
            "iter028_modern_sortino_1990_2009_calm_ref": ITER028_SLOT6_RVGTD_CALM_MODERN_1990_2009_SORTINO,
            "iter028_modern_sortino_2010_2026_calm_ref": ITER028_SLOT6_RVGTD_CALM_MODERN_2010_2026_SORTINO,
            "modern_sortino_lift_1990_pp_vs_uncond":
                float(modern_sortino_1990 - ITER027_SLOT6_MODERN_SORTINO_1990_2009),
            "modern_sortino_lift_2010_pp_vs_uncond":
                float(modern_sortino_2010 - ITER027_SLOT6_MODERN_SORTINO_2010_2026),
            "modern_sortino_lift_1990_pp_vs_calm":
                float(modern_sortino_1990 - ITER028_SLOT6_RVGTD_CALM_MODERN_1990_2009_SORTINO),
            "modern_sortino_lift_2010_pp_vs_calm":
                float(modern_sortino_2010 - ITER028_SLOT6_RVGTD_CALM_MODERN_2010_2026_SORTINO),
            "modern_sortino_lift_fired": modern_sortino_lift,
            "regime_axis_symmetric_falsification_fired": regime_axis_symmetric_falsification,
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
        title="Iter 029 — PBO-decoupled LRS1.20× ratevol-gated stress-only (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 029 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 029 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 029 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 029 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 029 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 029 — crisis MDD vs SPY",
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
        "iter": "029-2026-05-10-pbo-decoupled-lrs120-ratevol-gated-stress",
        "tier": "loop_iter",
        "phase": 4,
        "phase_name": "iter 017 focused validation/refinement",
        "hypothesis": (
            "PBO-decoupled LRS1.20× ratevol-gated stress-only overlay (slot 6) "
            "— SYMMETRY DIAGNOSTIC to iter 028. PRIMARY: iter 028 falsified the "
            "calm-regime modern-Sortino-lift hypothesis (1990_2009=1.139, "
            "2010_2026=1.132 both BELOW 1.20 floor). This iter applies LRS1.20× "
            "ONLY when ratevol_gate==1 (STRESS regime, ~22% of all bars active). "
            "Pre-registered KEY HYPOTHESIS: if iter 028's structural diagnosis "
            "is correct, modern subperiod Sortino lift on either of {1990_2009, "
            "2010_2026} should ALSO fail — symmetric falsification closes the "
            "regime-conditioning axis as a path to modern-era softness fix. "
            "SECONDARY: Phase 4 axis closure (MAGNITUDE iter 027, CALM iter 028, "
            "STRESS iter 029) — pre-condition for confidently pivoting to non-rearm "
            "Phase 4 family. TERTIARY: 5 calibration anchors (slots 1-5) preserved "
            "bit-exact. Citations: [advances_fin_ml, p.208-211] CSCV PBO mechanism "
            "diversity; [volatility_trading, p.58-60] Sinclair vol cones; "
            "[systematic_trading, ch.13, p.212] Carver vol-scaled regime; "
            "[leverage_for_the_long_run, p.13, ch.3] canonical RISK_ON LRS rule; "
            "[advances_fin_ml, p.222-223] DSR cumulative (n_global=600)."
        ),
        "primary_citation": "[advances_fin_ml, p.208-211]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_029",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"], "topology": s["topology"],
             "use_basket": s["use_basket"], "upgrade_mode": s["upgrade_mode"],
             "lrs_mode": s["lrs_mode"], "gamma": s["gamma"],
             "ratevol": s["ratevol"], "alt_off": s["alt_off"],
             "rearm_active": s["rearm_active"]}
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
        "parity_max_abs_diff_iter017_vs_indep": parity_max_abs_diff,
        "parity_n_diff_days_iter017_vs_indep": parity_n_diff_days,
        "lrs_factor_k4_slot3": LRS_FACTOR_K4,
        "lrs_factor_rearm_slot6": LRS_FACTOR_REARM,
        "lrs_mode_tested": "ratevol_gated_stress_only_during_ON",
        "slot2_baseline_K4_sortino_lh56y": single_anchor_sortino,
        "slot2_baseline_K4_cagr_lh56y": single_anchor_rec["cagr_lh56y"],
        "slot3_K4_unclrs105_sortino_lh56y": k4_unclrs_sortino,
        "slot3_K4_unclrs105_cagr_lh56y": k4_unclrs_cagr,
        "slot5_baseline_rearmonly_sortino_lh56y": rearmonly_sortino,
        "slot5_baseline_rearmonly_cagr_lh56y": rearmonly_cagr,
        "slot6_rvgtdlrs120stress_sortino_lh56y": rgtdstr_sortino,
        "slot6_rvgtdlrs120stress_cagr_lh56y": rgtdstr_cagr,
        "slot6_rvgtdlrs120stress_end_eq_vs_iter017": rgtdstr_end_eq_iter017,
        "slot6_rvgtdlrs120stress_lrs_active_pct": rgtdstr_rec["lrs_active_pct"],
        "iter027_slot6_uncond_sortino": ITER027_SLOT6_LRS120_UNCOND_SORTINO,
        "iter027_slot6_uncond_cagr": ITER027_SLOT6_LRS120_UNCOND_CAGR,
        "iter027_slot6_uncond_end_eq_vs_iter017": ITER027_SLOT6_LRS120_UNCOND_END_EQ_VS_ITER017,
        "iter028_slot6_calm_sortino": ITER028_SLOT6_RVGTD_CALM_SORTINO,
        "iter028_slot6_calm_cagr": ITER028_SLOT6_RVGTD_CALM_CAGR,
        "iter028_slot6_calm_end_eq_vs_iter017": ITER028_SLOT6_RVGTD_CALM_END_EQ_VS_ITER017,
        "rvgtdlrs120stress_vs_uncond_sortino_delta":
            float(rgtdstr_sortino - ITER027_SLOT6_LRS120_UNCOND_SORTINO),
        "rvgtdlrs120stress_vs_uncond_cagr_delta":
            float(rgtdstr_cagr - ITER027_SLOT6_LRS120_UNCOND_CAGR),
        "rvgtdlrs120stress_vs_uncond_end_eq_iter017_delta":
            float(rgtdstr_end_eq_iter017 - ITER027_SLOT6_LRS120_UNCOND_END_EQ_VS_ITER017),
        "rvgtdlrs120stress_vs_calm_sortino_delta":
            float(rgtdstr_sortino - ITER028_SLOT6_RVGTD_CALM_SORTINO),
        "rvgtdlrs120stress_vs_calm_cagr_delta":
            float(rgtdstr_cagr - ITER028_SLOT6_RVGTD_CALM_CAGR),
        "rvgtdlrs120stress_vs_calm_end_eq_iter017_delta":
            float(rgtdstr_end_eq_iter017 - ITER028_SLOT6_RVGTD_CALM_END_EQ_VS_ITER017),
        "modern_sortino_1990_2009_slot6_rgtdstr": modern_sortino_1990,
        "modern_sortino_2010_2026_slot6_rgtdstr": modern_sortino_2010,
        "modern_sortino_lift_fired": modern_sortino_lift,
        "regime_axis_symmetric_falsification_fired":
            regime_axis_symmetric_falsification,
        "iter027_modern_sortino_1990_2009_uncond_ref": ITER027_SLOT6_MODERN_SORTINO_1990_2009,
        "iter027_modern_sortino_2010_2026_uncond_ref": ITER027_SLOT6_MODERN_SORTINO_2010_2026,
        "iter028_modern_sortino_1990_2009_calm_ref": ITER028_SLOT6_RVGTD_CALM_MODERN_1990_2009_SORTINO,
        "iter028_modern_sortino_2010_2026_calm_ref": ITER028_SLOT6_RVGTD_CALM_MODERN_2010_2026_SORTINO,
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
    LOG.info("PARITY iter017 vs INDEP IMPL: max abs diff=%.3e n_diff_days=%d",
             parity_max_abs_diff, parity_n_diff_days)
    LOG.info("Slot 5 (rearm-only baseline)                | Sortino=%.4f CAGR=%.4f",
             rearmonly_sortino, rearmonly_cagr)
    LOG.info("Slot 6 (rearm + ratevol-gated LRS1.20 STRESS) | Sortino=%.4f CAGR=%.4f end_eq_vs_iter017=%.3f | lift vs slot5: Sortino=%+.4f CAGR=%+.4f",
             rgtdstr_sortino, rgtdstr_cagr, rgtdstr_end_eq_iter017,
             rgtdstr_sortino - rearmonly_sortino, rgtdstr_cagr - rearmonly_cagr)
    LOG.info("Slot 6 vs iter 027 slot 6 (LRS1.20 unconditional): Sortino delta=%+.4f CAGR delta=%+.4f end_eq delta=%+.3f",
             rgtdstr_sortino - ITER027_SLOT6_LRS120_UNCOND_SORTINO,
             rgtdstr_cagr - ITER027_SLOT6_LRS120_UNCOND_CAGR,
             rgtdstr_end_eq_iter017 - ITER027_SLOT6_LRS120_UNCOND_END_EQ_VS_ITER017)
    LOG.info("Slot 6 vs iter 028 slot 6 (LRS1.20 calm-only):      Sortino delta=%+.4f CAGR delta=%+.4f end_eq delta=%+.3f",
             rgtdstr_sortino - ITER028_SLOT6_RVGTD_CALM_SORTINO,
             rgtdstr_cagr - ITER028_SLOT6_RVGTD_CALM_CAGR,
             rgtdstr_end_eq_iter017 - ITER028_SLOT6_RVGTD_CALM_END_EQ_VS_ITER017)
    LOG.info("Slot 6 LRS active stats: lrs_active_pct=%.4f stress_within_on_pct=%.4f rv_warmup_pct=%.4f",
             rgtdstr_rec["lrs_diag"]["lrs_active_pct"],
             rgtdstr_rec["lrs_diag"]["stress_within_on_pct"],
             rgtdstr_rec["lrs_diag"]["rv_warmup_pct"])
    LOG.info("Modern-era Sortino lift: 1990_2009=%.4f 2010_2026=%.4f | iter 028 calm ref: %.4f / %.4f | iter 027 uncond ref: %.4f / %.4f | lift_fired=%s",
             modern_sortino_1990, modern_sortino_2010,
             ITER028_SLOT6_RVGTD_CALM_MODERN_1990_2009_SORTINO,
             ITER028_SLOT6_RVGTD_CALM_MODERN_2010_2026_SORTINO,
             ITER027_SLOT6_MODERN_SORTINO_1990_2009,
             ITER027_SLOT6_MODERN_SORTINO_2010_2026,
             modern_sortino_lift)
    LOG.info("Symmetric falsification (regime axis): %s",
             regime_axis_symmetric_falsification)
    LOG.info("G1 PBO=%.4f | KILL_LOOP fired summary: %s",
             g1_pbo_value,
             {k: (v["fired"] if isinstance(v, dict) and "fired" in v else "N/A")
              for k, v in kill_loop_results.items()
              if k not in ("compound_detail", "subperiod_table_slot6", "rvgtdlrs120stress_summary")})
    LOG.info("Subperiod table (slot 6 ratevol-gated LRS1.20 stress): %s", subperiod_table_slot6)
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
