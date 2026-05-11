"""Iter 022 — rearm-only INDEPENDENT impl + PFV20 vol-confirm gate.

Phase 4 — iter 017 focused validation/refinement.

PRIMARY hypothesis: Independent reimplementation of iter 021's slot 5
rearm-only T40D60 (`rearm_independent.build_postcrash_rearm_gate_independent`)
must produce bit-exact identical strategy returns to iter 017's
`reentry_overlay.build_postcrash_rearm_gate`. Validates that the loop's
highest single-leg Sortino finding (1.4176) is implementation-independent.

SECONDARY hypothesis: A post-flip realised-vol confirmation gate (PFV20) —
fire rearm only if first 5d post-flip QLD realised vol < trailing 5y 20th
percentile of 5d-realised-vol — provides a quality-confirmation filter
topologically distinct from iter 020's pre-flip MDD-rejection gate.

Six configs (mechanism-mix-diverse — 6 distinct upgrade-axis topologies):

  1. baseline_qld_zroz                                                — calibration anchor (13th-gen)
  2. single_K4lv25_g25_rvp70_cashx                                    — iter 014 strict_superset replica (10th-gen)
  3. basket3invvol_K4lv25_g25_rvp70_cashx                             — iter 014 triple-stack replica (8th-gen)
  4. single_K4lv25_g25_rvp70_cashx_T40D60                             — iter 017 NEW strict_superset replica (5th-gen)
  5. single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl  (PRIMARY)     — NEW: independent impl of iter 021 slot 5
  6. single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl_pfv20 (NEW)    — NEW: rearm AND PFV20 vol-confirm

Citations
---------
- [advances_fin_ml, p.222-223] PRIMARY: DSR cumulative n_trials
  (n_global=558); independent reimplementation reduces single-impl risk.
- [advances_fin_ml, p.208-211]: PBO via CSCV (mechanism-mix-diversity).
- [leverage_for_the_long_run, p.6-7, ch.3]: Husson-Trifoni MA flip-on
  streak-window onset.
- [leverage_for_the_long_run, p.4, ch.2]: streaks-vs-seesawing.
- [volatility_trading, p.58-60]: Sinclair vol cone (PFV).
- [stocks_on_the_move, p.98]: Clenow trend (K4 base intuition).
- [risk_parity, p.80-81, ch.4]: Qian RORO.
- [risk_parity, ch.5, p.10]: Carlson stacking.
- [systematic_trading, p.212, ch.13]: Carver re-arm.
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
LOG = logging.getLogger("iter022")


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_PRIOR_ITERS = ITER_DIR.parent
ITER007 = _load_module(
    _PRIOR_ITERS / "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket" / "backtest.py",
    "iter022_iter007_backtest",
)
windowed_returns = ITER007.windowed_returns
compute_per_dataset = ITER007.compute_per_dataset
spy_anchor_metrics = ITER007.spy_anchor_metrics

ITER011 = _load_module(
    _PRIOR_ITERS / "011-2026-05-10-conditional-tqqq-leverage" / "conditional_leg.py",
    "iter022_iter011_cleg",
)
entry_signal_K2 = ITER011.entry_signal_K2
upgrade_signal_K4 = ITER011.upgrade_signal_K4
upgrade_signal_lowvol25 = ITER011.upgrade_signal_lowvol25
combine_AND = ITER011.combine_AND
combine_OR = ITER011.combine_OR

ITER006 = _load_module(
    _PRIOR_ITERS / "006-2026-05-09-bond-ratevol-regime" / "rate_vol_gate.py",
    "iter022_iter006_ratevol",
)
ratevol_regime_gate = ITER006.ratevol_regime_gate

ITER014 = _load_module(
    _PRIOR_ITERS / "014-2026-05-10-mechanism-mix-diverse-graded-blend" / "mechanism_mix_leg.py",
    "iter022_iter014_mechmix",
)
build_single_asset_on_leg = ITER014.build_single_asset_on_leg
build_basket3_on_leg = ITER014.build_basket3_on_leg
build_mechanism_mix_strategy_returns = ITER014.build_mechanism_mix_strategy_returns
mechanism_mix_turnover = ITER014.mechanism_mix_turnover

# Iter 017's reentry_overlay (used by slot 4 calibration anchor only).
ITER017 = _load_module(
    _PRIOR_ITERS / "017-2026-05-10-postcrash-rearm-tqqq-streak" / "reentry_overlay.py",
    "iter022_iter017_rearm",
)
build_postcrash_rearm_gate_iter017 = ITER017.build_postcrash_rearm_gate
diagnose_rearm_events_iter017 = ITER017.diagnose_rearm_events

# Iter 022's INDEPENDENT impl (slots 5, 6).
RI = _load_module(ITER_DIR / "rearm_independent.py", "iter022_rearm_independent")
build_postcrash_rearm_gate_independent = RI.build_postcrash_rearm_gate_independent
diagnose_rearm_events_independent = RI.diagnose_rearm_events_independent
post_flip_vol_confirmation_gate = RI.post_flip_vol_confirmation_gate
diagnose_pfv_events = RI.diagnose_pfv_events


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

# Phase 4 anchor (iter 017 NEW strict_superset).
PHASE4_ANCHOR_ITER = "017-2026-05-10-postcrash-rearm-tqqq-streak"
PHASE4_ANCHOR_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_rearm_single_K4lv25_g25_rvp70_cashx_T40D60"
PHASE4_ANCHOR_SORTINO = 1.4030
PHASE4_ANCHOR_CAGR = 0.3266
PHASE4_ANCHOR_END_EQ_RATIO_VS_BASELINE = 1.620

# Trial accounting (per LOOP_MEMORY frontmatter post-iter-021).
PRE_ITER_CUMULATIVE = 552
PRE_ITER_LOOP = 126
LOCAL_N_CONFIGS = 6

# Calibration anchors (KILL_LOOP replica sanity).
ITER011_BASELINE_SORTINO = 1.3240            # KILL_LOOP #3 (13th-gen target)
ITER014_SINGLE_K4LV25_G25_SORTINO = 1.3951    # KILL_LOOP #4
ITER014_BASKET3_K4LV25_G25_SORTINO = 1.4689   # KILL_LOOP #5
ITER017_T40D60_SORTINO = 1.4030               # KILL_LOOP #6 (5th-gen target)
ITER021_REARMONLY_T40D60_SORTINO = 1.4176     # KILL_LOOP #7 (NEW calibration anchor — 2nd-gen)

# T40D60 anchor parameters (iter 017's recipe, frozen here).
T_CRASH_FROZEN = 40
D_ARM_FROZEN = 60

# PFV20 gate parameters.
PFV_CONFIRM_WINDOW = 5
PFV_PCT_WINDOW = 1260
PFV_PCT_THRESHOLD = 0.20

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


# rearm_mode values:
#   "none"                     → no rearm; upg = base_upg
#   "iter017_unconditional"    → rearm OR-combined with base_upg using ITER017 module (slot 4)
#   "indep_replace"            → rearm REPLACES base_upg using INDEPENDENT module (slot 5)
#   "indep_replace_pfv20"      → PFV-AND-rearm REPLACES base_upg using INDEPENDENT module (slot 6)
CONFIG_SPECS = [
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_indep_baseline_qld_zroz",
        "kind": "baseline_qld_zroz",
        "topology": "single/none/none",
        "use_basket": False,
        "upgrade_kind": "none",
        "gamma": 0.0,
        "ratevol": None,
        "alt_off": None,
        "rearm_mode": "none",
        "t_crash": 0,
        "d_arm": 0,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_indep_single_K4lv25_g25_rvp70_cashx",
        "kind": "single_K4lv25_g25_rvp70_cashx",
        "topology": "single/K4_AND_QLDlv25/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_kind": "K4_AND_lv25",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_mode": "none",
        "t_crash": 0,
        "d_arm": 0,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_indep_basket3invvol_K4lv25_g25_rvp70_cashx",
        "kind": "basket3invvol_K4lv25_g25_rvp70_cashx",
        "topology": "basket3/K4_AND_QLDlv25/g=0.25/p70-cashx",
        "use_basket": True,
        "upgrade_kind": "K4_AND_lv25",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_mode": "none",
        "t_crash": 0,
        "d_arm": 0,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_indep_single_K4lv25_g25_rvp70_cashx_T40D60",
        "kind": "single_K4lv25_g25_rvp70_cashx_T40D60",
        "topology": "single/K4_AND_QLDlv25_OR_rearm_iter017impl/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_kind": "K4_AND_lv25",
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_mode": "iter017_unconditional",
        "t_crash": T_CRASH_FROZEN,
        "d_arm": D_ARM_FROZEN,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_indep_single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl",
        "kind": "single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl",
        "topology": "single/rearm_only_indepimpl/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_kind": "K4_AND_lv25",  # base set but REPLACED by independent rearm
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_mode": "indep_replace",
        "t_crash": T_CRASH_FROZEN,
        "d_arm": D_ARM_FROZEN,
    },
    {
        "name": "qld_voteK2_sma250_100_vol21_40_ar30_indep_single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl_pfv20",
        "kind": "single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl_pfv20",
        "topology": "single/rearm_only_indepimpl_AND_pfv20/g=0.25/p70-cashx",
        "use_basket": False,
        "upgrade_kind": "K4_AND_lv25",  # base set but REPLACED by PFV-AND-rearm
        "gamma": 0.25,
        "ratevol": {"vol_window": 60, "pct_window": 1260, "threshold": 0.70},
        "alt_off": "CASHX",
        "rearm_mode": "indep_replace_pfv20",
        "t_crash": T_CRASH_FROZEN,
        "d_arm": D_ARM_FROZEN,
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


def _subperiod_metrics(strat_returns_lh: pd.Series, spy_returns_lh: pd.Series) -> dict:
    """Compute Sortino/CAGR/MDD per subperiod for slot 5 reporting."""
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
    qld_lv25_gate = upgrade_signal_lowvol25(
        qld_ret, vol_window=21, pct_window=1260, pct_threshold=0.25,
    )
    k4_and_qldlv25_gate = combine_AND(k4_gate, qld_lv25_gate)

    base_upgrade_map = {
        "none":         pd.Series(0.0, index=qld_ret.index),
        "K4_AND_lv25":  k4_and_qldlv25_gate,
    }
    alt_off_returns_map = {"CASHX": cash_ret, "IEFSIM": ief_ret}

    # ----- Parity diagnostic (KILL_LOOP #8) -----
    rearm_iter017 = build_postcrash_rearm_gate_iter017(
        on_signal=on_signal, t_crash=T_CRASH_FROZEN, d_arm=D_ARM_FROZEN,
    )
    rearm_indep = build_postcrash_rearm_gate_independent(
        on_signal=on_signal, t_crash=T_CRASH_FROZEN, d_arm=D_ARM_FROZEN,
    )
    parity_diff = (rearm_iter017.fillna(0.0) - rearm_indep.fillna(0.0)).abs()
    parity_max_abs_diff = float(parity_diff.max())
    parity_n_diff_days = int((parity_diff > 0).sum())
    LOG.info("PARITY CHECK: max abs diff = %.3e | n diff days = %d",
             parity_max_abs_diff, parity_n_diff_days)

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
        base_upg = base_upgrade_map[spec["upgrade_kind"]]
        upg = base_upg

        rearm_mode = spec["rearm_mode"]
        if rearm_mode == "iter017_unconditional":
            rearm_gate = build_postcrash_rearm_gate_iter017(
                on_signal=on_signal, t_crash=spec["t_crash"], d_arm=spec["d_arm"],
            )
            upg = combine_OR(base_upg, rearm_gate)
            per_cfg_rearm_diag[spec["name"]] = diagnose_rearm_events_iter017(
                on_signal=on_signal, t_crash=spec["t_crash"], d_arm=spec["d_arm"],
            )
            per_cfg_rearm_diag[spec["name"]]["impl"] = "iter017"
        elif rearm_mode == "indep_replace":
            rearm_gate = build_postcrash_rearm_gate_independent(
                on_signal=on_signal, t_crash=spec["t_crash"], d_arm=spec["d_arm"],
            )
            upg = rearm_gate
            per_cfg_rearm_diag[spec["name"]] = diagnose_rearm_events_independent(
                on_signal=on_signal, t_crash=spec["t_crash"], d_arm=spec["d_arm"],
            )
        elif rearm_mode == "indep_replace_pfv20":
            pfv_gate = post_flip_vol_confirmation_gate(
                on_signal=on_signal, asset_returns=qld_ret,
                t_crash=spec["t_crash"], d_arm=spec["d_arm"],
                confirm_window=PFV_CONFIRM_WINDOW,
                pct_window=PFV_PCT_WINDOW,
                pct_threshold=PFV_PCT_THRESHOLD,
            )
            upg = pfv_gate
            per_cfg_rearm_diag[spec["name"]] = diagnose_pfv_events(
                on_signal=on_signal, asset_returns=qld_ret,
                t_crash=spec["t_crash"], d_arm=spec["d_arm"],
                confirm_window=PFV_CONFIRM_WINDOW,
                pct_window=PFV_PCT_WINDOW,
                pct_threshold=PFV_PCT_THRESHOLD,
            )
            per_cfg_rearm_diag[spec["name"]]["impl"] = "indep_pfv20"
        else:
            per_cfg_rearm_diag[spec["name"]] = {
                "n_qualified_flips": 0,
                "n_active_rearm_days": 0,
                "rearm_active_pct": 0.0,
                "t_crash": int(spec["t_crash"]),
                "d_arm": int(spec["d_arm"]),
                "impl": "none",
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

    baseline_name = "qld_voteK2_sma250_100_vol21_40_ar30_indep_baseline_qld_zroz"
    baseline_lh_eq = (1.0 + windowed_returns(per_cfg_returns[baseline_name],
                                             *DATASET_WINDOWS["lh_56y"])
                      ).cumprod() * 10_000.0
    baseline_lh_cagr = per_cfg_metrics[baseline_name]["lh_56y"]["cagr"]
    baseline_lh_sortino = per_cfg_metrics[baseline_name]["lh_56y"]["sortino"]

    t40d60_anchor_name = "qld_voteK2_sma250_100_vol21_40_ar30_indep_single_K4lv25_g25_rvp70_cashx_T40D60"
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
            and sortino_lh >= 1.35
            and gate_dict["g1_pbo"] < PHASE3_PBO_CEIL
            and gate_dict["g2_dsr_p_cumulative"] < PHASE3_DSR_CEIL
        )

        results.append({
            "config_name": name,
            "kind": spec["kind"],
            "topology": spec["topology"],
            "use_basket": spec["use_basket"],
            "upgrade_kind": spec["upgrade_kind"],
            "rearm_mode": spec["rearm_mode"],
            "gamma": spec["gamma"],
            "ratevol": spec["ratevol"],
            "alt_off": spec["alt_off"],
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
    any_phase4_improved = any(rec["phase4_anchor_improved"] for rec in results)
    best_sortino_lh = best["sortino_lh56y"] if best["sortino_lh56y"] is not None else 0.0

    baseline_rec = next(r for r in results if r["kind"] == "baseline_qld_zroz")
    single_anchor_rec = next(r for r in results if r["kind"] == "single_K4lv25_g25_rvp70_cashx")
    basket3_anchor_rec = next(r for r in results if r["kind"] == "basket3invvol_K4lv25_g25_rvp70_cashx")
    t40d60_anchor_rec = next(r for r in results if r["kind"] == "single_K4lv25_g25_rvp70_cashx_T40D60")
    rearmonly_indep_rec = next(r for r in results if r["kind"] == "single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl")
    rearmonly_pfv_rec = next(r for r in results if r["kind"] == "single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl_pfv20")

    baseline_sortino = baseline_rec["sortino_lh56y"] or 0.0
    baseline_cagr = baseline_rec["cagr_lh56y"] or 0.0
    single_anchor_sortino = single_anchor_rec["sortino_lh56y"] or 0.0
    basket3_anchor_sortino = basket3_anchor_rec["sortino_lh56y"] or 0.0
    t40d60_anchor_sortino = t40d60_anchor_rec["sortino_lh56y"] or 0.0
    rearmonly_indep_sortino = rearmonly_indep_rec["sortino_lh56y"] or 0.0
    rearmonly_indep_cagr = rearmonly_indep_rec["cagr_lh56y"] or 0.0
    pfv_sortino = rearmonly_pfv_rec["sortino_lh56y"] or 0.0
    pfv_cagr = rearmonly_pfv_rec["cagr_lh56y"] or 0.0
    g1_pbo_value = float(g1_result["pbo"])

    # Subperiod robustness for slot 5 (PRIMARY validation focus).
    rearmonly_indep_returns_lh = windowed_returns(
        per_cfg_returns[rearmonly_indep_rec["config_name"]], *DATASET_WINDOWS["lh_56y"]
    )
    subperiod_table = _subperiod_metrics(rearmonly_indep_returns_lh, spy_lh)

    # Phase 4 anchor validated: rearm-only INDEPENDENT IMPL produces bit-exact
    # parity AND its Sortino lift over baseline is statistically meaningful.
    phase4_anchor_validated = bool(
        parity_max_abs_diff <= 1e-12
        and abs(rearmonly_indep_sortino - ITER021_REARMONLY_T40D60_SORTINO) <= 0.005
        and rearmonly_indep_sortino > baseline_sortino + 0.04
        and rearmonly_indep_cagr > baseline_cagr + 0.005
        and rearmonly_indep_rec["gates"]["g2_dsr_p_cumulative"] < PHASE3_DSR_CEIL
    )

    cmp_detail = [
        {"name": r["config_name"], "kind": r["kind"],
         "rearm_mode": r["rearm_mode"], "use_basket": r["use_basket"],
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
            "rule": "Baseline Sortino_lh56y deviates from iter 011-021 baseline 1.3240 by > 0.005.",
            "baseline_sortino_lh56y": baseline_sortino,
            "expected": ITER011_BASELINE_SORTINO,
        },
        "kill_loop_4_replica_single_K4lv25_g25": {
            "fired": bool(abs(single_anchor_sortino - ITER014_SINGLE_K4LV25_G25_SORTINO) > 0.005),
            "rule": "single_K4lv25_g25_rvp70_cashx Sortino_lh56y deviates from iter 014-021 strict_superset 1.3951 by > 0.005.",
            "single_anchor_sortino_lh56y": single_anchor_sortino,
            "expected": ITER014_SINGLE_K4LV25_G25_SORTINO,
        },
        "kill_loop_5_replica_basket3invvol_K4lv25_g25": {
            "fired": bool(abs(basket3_anchor_sortino - ITER014_BASKET3_K4LV25_G25_SORTINO) > 0.005),
            "rule": "basket3invvol_K4lv25_g25_rvp70_cashx Sortino_lh56y deviates from iter 014-021 triple-stack 1.4689 by > 0.005.",
            "basket3_anchor_sortino_lh56y": basket3_anchor_sortino,
            "expected": ITER014_BASKET3_K4LV25_G25_SORTINO,
        },
        "kill_loop_6_replica_T40D60": {
            "fired": bool(abs(t40d60_anchor_sortino - ITER017_T40D60_SORTINO) > 0.005),
            "rule": "single_K4lv25_g25_rvp70_cashx_T40D60 (iter 017 module) Sortino_lh56y deviates from 1.4030 by > 0.005.",
            "t40d60_anchor_sortino_lh56y": t40d60_anchor_sortino,
            "expected": ITER017_T40D60_SORTINO,
        },
        "kill_loop_7_replica_rearmonly_T40D60": {
            "fired": bool(abs(rearmonly_indep_sortino - ITER021_REARMONLY_T40D60_SORTINO) > 0.005),
            "rule": "single_rearmonly_g25_rvp70_cashx_T40D60 (INDEP IMPL) Sortino_lh56y deviates from iter 021 slot 5 1.4176 by > 0.005.",
            "rearmonly_indep_sortino_lh56y": rearmonly_indep_sortino,
            "expected": ITER021_REARMONLY_T40D60_SORTINO,
        },
        "kill_loop_8_parity_check_indep_impl": {
            "fired": bool(parity_max_abs_diff > 1e-12),
            "rule": "max abs daily-gate diff between INDEPENDENT impl and iter 017 impl > 1e-12. HARD MECHANISM FAIL — algorithms diverge.",
            "parity_max_abs_diff": parity_max_abs_diff,
            "parity_n_diff_days": parity_n_diff_days,
        },
        "kill_loop_9_pbo_blowup": {
            "fired": bool(g1_pbo_value >= 0.55),
            "rule": "G1 PBO >= 0.55 (hard regression threshold).",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_10_pbo_held": {
            "fired": bool(g1_pbo_value < PHASE3_PBO_CEIL),
            "rule": "G1 PBO < 0.50 (Phase 3 hard gate). POSITIVE TAG.",
            "g1_pbo": g1_pbo_value,
        },
        "kill_loop_11_pfv_phase3_perf_candidate": {
            "fired": bool(rearmonly_pfv_rec["phase3_performance_candidate"]),
            "rule": "Slot 6 (PFV20) achieves phase3_performance_candidate=True. CORE WEAK HYPOTHESIS.",
            "pfv_phase3_perf_candidate": bool(rearmonly_pfv_rec["phase3_performance_candidate"]),
        },
        "kill_loop_12_pfv_dominates_rearmonly": {
            "fired": bool(pfv_sortino > ITER021_REARMONLY_T40D60_SORTINO),
            "rule": "Slot 6 (PFV20) Sortino_lh56y > 1.4176 (iter 021 slot 5 rearm-only). STRONG HYPOTHESIS — PFV improves rearm-only.",
            "pfv_sortino_lh56y": pfv_sortino,
            "rearmonly_target": ITER021_REARMONLY_T40D60_SORTINO,
        },
        "compound_detail": cmp_detail,
        "subperiod_table_slot5": subperiod_table,
        "phase4_anchor_validated_components": {
            "parity_pass": bool(parity_max_abs_diff <= 1e-12),
            "rearmonly_drift_pass": bool(
                abs(rearmonly_indep_sortino - ITER021_REARMONLY_T40D60_SORTINO) <= 0.005
            ),
            "sortino_lift_pass": bool(rearmonly_indep_sortino > baseline_sortino + 0.04),
            "cagr_lift_pass": bool(rearmonly_indep_cagr > baseline_cagr + 0.005),
            "dsr_global_pass": bool(
                rearmonly_indep_rec["gates"]["g2_dsr_p_cumulative"] < PHASE3_DSR_CEIL
            ),
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
        title="Iter 022 — rearm-only INDEP IMPL + PFV20 (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 022 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 022 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 022 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 022 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 022 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 022 — crisis MDD vs SPY",
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
            "rearm_mode": rec["rearm_mode"],
            "gamma": rec["gamma"],
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
        "iter": "022-2026-05-10-rearm-only-indep-pfv-confirm",
        "tier": "loop_iter",
        "phase": 4,
        "phase_name": "iter 017 focused validation/refinement",
        "hypothesis": (
            "Rearm-only INDEPENDENT impl + PFV20 vol-confirm gate. "
            "PRIMARY: bit-exact parity validation of iter 021's slot 5 "
            "rearm-only T40D60 finding (Sortino 1.4176, +0.0930 vs winner) "
            "via from-scratch reimplementation in iter 022's "
            "`rearm_independent.py` (no import of iter 017's module). "
            "SECONDARY: post-flip realised-vol confirmation gate (PFV20) — "
            "fire rearm only if first 5d post-flip QLD realised vol < "
            "trailing 5y 20th percentile. Six configs (mechanism-mix-diverse "
            "with 6 distinct upgrade-axis topologies). Primary citation: "
            "[advances_fin_ml, p.222-223] DSR cumulative (n_global=558); "
            "[advances_fin_ml, p.208-211] CSCV PBO."
        ),
        "primary_citation": "[advances_fin_ml, p.222-223]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_022",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"], "topology": s["topology"],
             "use_basket": s["use_basket"], "upgrade_kind": s["upgrade_kind"],
             "rearm_mode": s["rearm_mode"], "gamma": s["gamma"],
             "ratevol": s["ratevol"], "alt_off": s["alt_off"],
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
        "any_phase4_anchor_improved": bool(any_phase4_improved),
        "phase4_anchor_validated": bool(phase4_anchor_validated),
        "parity_max_abs_diff": parity_max_abs_diff,
        "parity_n_diff_days": parity_n_diff_days,
        "rearmonly_indep_sortino_lh56y": rearmonly_indep_sortino,
        "rearmonly_indep_cagr_lh56y": rearmonly_indep_cagr,
        "rearmonly_indep_drift_vs_iter021": float(
            abs(rearmonly_indep_sortino - ITER021_REARMONLY_T40D60_SORTINO)
        ),
        "pfv20_sortino_lh56y": pfv_sortino,
        "pfv20_cagr_lh56y": pfv_cagr,
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
        },
        "winner_benchmark_iter": WINNER_BENCHMARK_ITER,
        "winner_benchmark_config": WINNER_BENCHMARK_CONFIG,
    }

    with open(ITER_DIR / "verdict.json", "w") as f:
        json.dump(verdict, f, indent=2, default=_json_default)

    LOG.info("Best: %s | Sortino_lh56y=%.4f | CAGR_lh56y=%.4f | edge=%+.4f | beats=%s | phase3=%s | strict=%s | p4_imp=%s | p4_val=%s",
             best["config_name"], best["sortino_lh56y"] or 0.0,
             best["cagr_lh56y"] or 0.0, best["sortino_edge_vs_winner"],
             best["beats_winner"], best["phase3_performance_candidate"],
             best["strict_superset"], best["phase4_anchor_improved"],
             phase4_anchor_validated)
    LOG.info("PARITY: max abs diff=%.3e n_diff_days=%d | rearmonly_indep Sortino=%.4f drift=%.4f vs iter 021 1.4176",
             parity_max_abs_diff, parity_n_diff_days,
             rearmonly_indep_sortino,
             abs(rearmonly_indep_sortino - ITER021_REARMONLY_T40D60_SORTINO))
    LOG.info("PFV20: Sortino=%.4f CAGR=%.4f | rearm activation=%s",
             pfv_sortino, pfv_cagr,
             per_cfg_rearm_diag[rearmonly_pfv_rec["config_name"]])
    LOG.info("G1 PBO=%.4f | KILL_LOOP fired summary: %s",
             g1_pbo_value,
             {k: (v["fired"] if isinstance(v, dict) and "fired" in v else "N/A")
              for k, v in kill_loop_results.items() if k not in ("compound_detail", "subperiod_table_slot5", "phase4_anchor_validated_components")})
    LOG.info("Subperiod table (slot 5 rearm-only INDEP IMPL): %s", subperiod_table)
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
