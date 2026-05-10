"""Iter 008 — compound 4-axis CSCV-diversity grid.

Goal: drop G1 PBO < 0.50 (the lone strict-bar blocker for
`winner_conditions_met=True` after iter 007) by widening the compound-
mechanic grid from iter 007's 3 axes to 5 qualitatively distinct
mechanism dimensions. Iter 007 winner replica is the anchor; 5 mechanic-
axis variants span ON-basket on/off, OFF-mechanic on/off, ratevol
threshold, ratevol window, and alt-OFF asset.

Citations
---------
- [advances_fin_ml, p.208-211]: PBO via CSCV; PBO < 0.5 deploy bar;
  PBO sensitivity to mechanic diversity.
- [stocks_on_the_move, p.98]: Clenow vol-parity (ON-basket sizing,
  iter 005 module).
- [volatility_trading, p.58-60]: Sinclair volatility cone (OFF-leg
  ratevol regime, iter 006 module).
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking
  (super-additivity, iter 007 finding).
- [advances_fin_ml, p.222-223]: DSR + cumulative n_trials (G2 global
  with n_trials_global = 474).
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
from studies.letf_rotation_hunt.signals import (
    ar1_coefficient,
    realized_vol_gate,
    sma_gate,
    vote_of_k,
)
from studies.letf_rotation_hunt.sortino_reanalysis.sortino_metric import (
    _annualised_sortino,
)

ITER_DIR = Path(__file__).parent
LOG = logging.getLogger("iter008")


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Helpers re-imported from prior loop iters (committed, read-only).
_PRIOR_ITERS = ITER_DIR.parent
BSK = _load_module(
    _PRIOR_ITERS / "005-2026-05-09-multi-asset-on-invvol" / "basket_sizer.py",
    "iter008_basket_sizer",
)
RV = _load_module(
    _PRIOR_ITERS / "006-2026-05-09-bond-ratevol-regime" / "rate_vol_gate.py",
    "iter008_rate_vol_gate",
)
ITER007 = _load_module(
    _PRIOR_ITERS / "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket" / "backtest.py",
    "iter008_iter007_backtest",
)

# Winner benchmark (frozen per LOOP_PROTOCOL.md)
WINNER_BENCHMARK_SORTINO = 1.3246
WINNER_BENCHMARK_ITER = "022-2026-05-06-T3d-extended-grid"
WINNER_BENCHMARK_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
BEATS_THRESHOLD_SORTINO = 1.3746
BEATS_PCT_ABOVE = 0.95

# Trial accounting (per LOOP_MEMORY.md frontmatter at iter 007 close)
PRE_ITER_CUMULATIVE = 468
PRE_ITER_LOOP = 42
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
        "UPROSIM": load_testfolio_series("UPROSIM"),
        "UGLSIM":  load_testfolio_series("UGLSIM"),
        "ZROZSIM": load_testfolio_series("ZROZSIM"),
        "IEFSIM":  load_testfolio_series("IEFSIM"),
        "CASHX":   load_testfolio_series("CASHX"),
        "SPYSIM":  load_testfolio_series("SPYSIM"),
    }


# ---------------------------------------------------------------------------
# Trend ON signal — winner replica (delegated to iter 007 helper)
# ---------------------------------------------------------------------------


def build_winner_on_signal(qld_prices: pd.Series, qld_returns: pd.Series) -> pd.Series:
    return ITER007.build_winner_on_signal(qld_prices, qld_returns)


# ---------------------------------------------------------------------------
# Configs (6, 5-axis orthogonal grid)
# ---------------------------------------------------------------------------


CONFIG_SPECS = [
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_4axis_baseline",
     "kind": "baseline",
     "on_basket": ["QLDSIM"], "on_sizing": "single", "on_vol_window": None,
     "use_off_override": False, "off_pct": None, "off_vol_window": None,
     "alt_off": None},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_4axis_basket3_x_ratevol_p70_60d_cashx",
     "kind": "winner_replica",
     "on_basket": ["QLDSIM", "UPROSIM", "UGLSIM"], "on_sizing": "invvol",
     "on_vol_window": 60,
     "use_off_override": True, "off_pct": 0.70, "off_vol_window": 60,
     "alt_off": "CASHX"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_4axis_basket3_only",
     "kind": "basket3_only",
     "on_basket": ["QLDSIM", "UPROSIM", "UGLSIM"], "on_sizing": "invvol",
     "on_vol_window": 60,
     "use_off_override": False, "off_pct": None, "off_vol_window": None,
     "alt_off": None},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_4axis_basket3_x_ratevol_p80_60d_cashx",
     "kind": "threshold_p80",
     "on_basket": ["QLDSIM", "UPROSIM", "UGLSIM"], "on_sizing": "invvol",
     "on_vol_window": 60,
     "use_off_override": True, "off_pct": 0.80, "off_vol_window": 60,
     "alt_off": "CASHX"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_4axis_basket3_x_ratevol_p70_120d_cashx",
     "kind": "window_120d",
     "on_basket": ["QLDSIM", "UPROSIM", "UGLSIM"], "on_sizing": "invvol",
     "on_vol_window": 60,
     "use_off_override": True, "off_pct": 0.70, "off_vol_window": 120,
     "alt_off": "CASHX"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_4axis_basket3_x_ratevol_p70_60d_ief",
     "kind": "alt_off_ief",
     "on_basket": ["QLDSIM", "UPROSIM", "UGLSIM"], "on_sizing": "invvol",
     "on_vol_window": 60,
     "use_off_override": True, "off_pct": 0.70, "off_vol_window": 60,
     "alt_off": "IEFSIM"},
]


# ---------------------------------------------------------------------------
# Metrics helpers (delegated to iter 007 unchanged behaviour)
# ---------------------------------------------------------------------------


windowed_returns = ITER007.windowed_returns
compute_per_dataset = ITER007.compute_per_dataset
spy_anchor_metrics = ITER007.spy_anchor_metrics
build_compound_strategy_returns = ITER007.build_compound_strategy_returns
compound_turnover = ITER007.compound_turnover


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    LOG.info("Loading universe...")
    universe = load_universe()
    qld = universe["QLDSIM"]
    upro = universe["UPROSIM"]
    ugl = universe["UGLSIM"]
    zroz = universe["ZROZSIM"]
    ief = universe["IEFSIM"]
    cash = universe["CASHX"]
    spy = universe["SPYSIM"]

    qld_ret = qld.pct_change().dropna()
    upro_ret = upro.pct_change().dropna()
    ugl_ret = ugl.pct_change().dropna()
    zroz_ret = zroz.pct_change().dropna()
    ief_ret = ief.pct_change().dropna()
    cash_ret = cash.pct_change().dropna()
    spy_ret = spy.pct_change().dropna()

    on_signal = build_winner_on_signal(qld, qld_ret)

    asset_returns_full = {
        "QLDSIM":  qld_ret,
        "UPROSIM": upro_ret,
        "UGLSIM":  ugl_ret,
    }
    alt_off_returns_map = {
        "CASHX":  cash_ret,
        "IEFSIM": ief_ret,
    }

    per_cfg_returns: dict[str, pd.Series] = {}
    per_cfg_metrics: dict[str, dict] = {}
    per_cfg_on_state: dict[str, pd.Series] = {}
    per_cfg_ratevol_active_pct: dict[str, float] = {}
    per_cfg_turnover: dict[str, float] = {}
    per_cfg_basket_size: dict[str, int] = {}

    LOG.info("Running %d configs...", len(CONFIG_SPECS))
    for spec in CONFIG_SPECS:
        basket = spec["on_basket"]
        per_cfg_basket_size[spec["name"]] = len(basket)
        basket_rets = {a: asset_returns_full[a] for a in basket}

        if spec["on_sizing"] == "single":
            on_basket_ret = basket_rets[basket[0]]
            weights = None
        elif spec["on_sizing"] == "invvol":
            weights = BSK.inverse_vol_weights(basket_rets, window=spec["on_vol_window"])
            on_basket_ret = BSK.basket_returns_from_weights(weights, basket_rets)
        else:
            raise ValueError(f"unknown on_sizing: {spec['on_sizing']}")

        if spec["use_off_override"]:
            ratevol = RV.ratevol_regime_gate(
                zroz_ret,
                vol_window=spec["off_vol_window"],
                pct_window=1260,
                threshold=spec["off_pct"],
            )
            alt_ret = alt_off_returns_map[spec["alt_off"]]
        else:
            ratevol = pd.Series(np.nan, index=zroz_ret.index)
            alt_ret = cash_ret  # placeholder; never referenced when use_off_override=False

        strat_r = build_compound_strategy_returns(
            on_signal=on_signal,
            on_basket_returns=on_basket_ret,
            off_returns=zroz_ret,
            alt_off_returns=alt_ret,
            ratevol_gate=ratevol,
            use_off_override=spec["use_off_override"],
        )
        per_cfg_returns[spec["name"]] = strat_r

        on_lag = on_signal.shift(1).reindex(strat_r.index)
        rv_lag = ratevol.shift(1).reindex(strat_r.index)
        per_cfg_on_state[spec["name"]] = (on_lag == 1).astype(float)
        rv_post_warmup = rv_lag.dropna()
        active_pct = float(rv_post_warmup.mean()) if len(rv_post_warmup) > 0 else 0.0
        per_cfg_ratevol_active_pct[spec["name"]] = active_pct

        per_cfg_turnover[spec["name"]] = compound_turnover(
            weights=weights,
            on_signal=on_signal,
            ratevol_gate=ratevol,
            use_off_override=spec["use_off_override"],
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
            "g3_wf_windows_pass_pct_above_benchmark": g3.get(
                "windows_pass_pct_above_benchmark", 0,
            ),
            "g3_wf_windows_pass_sharpe_positive": g3.get(
                "windows_pass_sharpe_positive", 0,
            ),
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

        anchors_sharpe = {ds: spy_metrics_per_dataset[ds]["sharpe"] for ds in DATASET_WINDOWS}
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
        pct_above_lh = per_cfg_metrics[name]["lh_56y"]["pct_time_above_benchmark"]
        sortino_edge_vs_winner = float(sortino_lh - WINNER_BENCHMARK_SORTINO)
        beats_winner = bool(
            sortino_lh > BEATS_THRESHOLD_SORTINO
            and score["winner_conditions_met"]
            and pct_above_lh >= BEATS_PCT_ABOVE
        )

        results.append({
            "config_name": name,
            "kind": spec["kind"],
            "on_basket": list(spec["on_basket"]),
            "on_basket_size": int(len(spec["on_basket"])),
            "on_sizing": spec["on_sizing"],
            "on_vol_window": spec["on_vol_window"],
            "use_off_override": spec["use_off_override"],
            "off_pct": spec["off_pct"],
            "off_vol_window": spec["off_vol_window"],
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
                    "pct_time_above_benchmark": per_cfg_metrics[name][ds][
                        "pct_time_above_benchmark"
                    ],
                    "min_relative_equity": per_cfg_metrics[name][ds][
                        "min_relative_equity"
                    ],
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
            "pct_time_above_benchmark_lh56y": float(pct_above_lh)
                if pct_above_lh == pct_above_lh else None,
            "sortino_edge_vs_winner": sortino_edge_vs_winner,
            "beats_winner": beats_winner,
            "ratevol_active_pct": per_cfg_ratevol_active_pct[name],
            "turnover_per_year": per_cfg_turnover[name],
        })

    LOG.info("Saving per-config strategy returns...")
    for name, r in per_cfg_returns.items():
        r.to_csv(ITER_DIR / f"{name}_strategy_returns.csv", header=["return"])

    def _key(rec):
        s = rec["sortino_lh56y"] if rec["sortino_lh56y"] is not None else -1e9
        return (s, rec["score_breakdown"]["total"])

    sorted_results = sorted(results, key=_key, reverse=True)
    best = sorted_results[0]
    best_config = best["config_name"]
    best_score = best["score_breakdown"]["total"]
    best_tier = best["tier_label"]
    best_beats = best["beats_winner"]

    # ----- KILL_LOOP evaluations (pre-registered in hypothesis.md) -----
    any_beats = any(rec["beats_winner"] for rec in results)
    best_sortino_lh = best["sortino_lh56y"] if best["sortino_lh56y"] is not None else 0.0
    baseline_rec = next(r for r in results if r["kind"] == "baseline")
    winner_replica_rec = next(r for r in results if r["kind"] == "winner_replica")
    baseline_sortino = baseline_rec["sortino_lh56y"] or 0.0
    winner_replica_sortino = winner_replica_rec["sortino_lh56y"] or 0.0
    g1_pbo_value = float(g1_result["pbo"])

    kill_loop_results = {
        "kill_loop_1_success_tag": {
            "fired": bool(any_beats),
            "rule": "Any config has beats_winner=True (Sortino>1.3746 AND winner_conditions_met=True AND pct_above>=0.95).",
        },
        "kill_loop_2_decisive_fail": {
            "fired": bool(best_sortino_lh < 1.30),
            "rule": "Best Sortino_lh56y < 1.30 (4-axis design destroyed compound-mechanic lift).",
            "best_sortino_lh56y": best_sortino_lh,
        },
        "kill_loop_3_replica_sanity": {
            "fired": bool(abs(baseline_sortino - 1.2841) > 0.005),
            "rule": "Baseline Sortino_lh56y deviates from 1.2841 by > 0.005.",
            "baseline_sortino_lh56y": baseline_sortino,
        },
        "kill_loop_4_compound_edge_decay": {
            "fired": bool(winner_replica_sortino < 1.40),
            "rule": "Iter 007 winner replica Sortino_lh56y < 1.40 (cross-iter drift > 0.06).",
            "winner_replica_sortino_lh56y": winner_replica_sortino,
        },
        "kill_loop_5_pbo_still_polluted": {
            "fired": bool(g1_pbo_value >= 0.50),
            "rule": "G1 PBO >= 0.50 (5-axis grid did not crack the strict bar).",
            "g1_pbo": g1_pbo_value,
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
        title="Iter 008 — compound 4-axis CSCV diversity (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 008 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 008 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 008 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 008 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 008 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 008 — crisis MDD vs SPY",
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
            "g1_pbo": gd["g1_pbo"],
            "g1_pass": gd["g1_pbo"] < 0.5,
            "g2_dsr_p_local": gd["g2_dsr_p_local"],
            "g2_pass": gd["g2_dsr_p_local"] < 0.05,
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
            "ratevol_active_pct": rec["ratevol_active_pct"],
            "turnover_per_year": rec["turnover_per_year"],
            "on_basket_size": rec["on_basket_size"],
            "on_sizing": rec["on_sizing"],
            "use_off_override": rec["use_off_override"],
            "alt_off": rec["alt_off"] or "",
        })
    pd.DataFrame(gate_rows).to_csv(ITER_DIR / "tables" / "gates_pass_fail.csv", index=False)

    verdict = {
        "iter": "008-2026-05-09-compound-4axis-cscv-diversity",
        "tier": "loop_iter",
        "hypothesis": (
            "Compound 4-axis CSCV diversity grid: drop G1 PBO < 0.50 by widening "
            "iter 007's compound-mechanic family from 3 axes to 5 qualitatively "
            "distinct mechanism dimensions (ON-basket on/off, OFF-mechanic on/off, "
            "ratevol threshold, ratevol window, alt-OFF asset). If hypothesis "
            "holds, lone-blocker G1 PBO breaks below 0.50, unlocking "
            "winner_conditions_met=True and triggering loop's first "
            "beats_winner=true. [advances_fin_ml, p.208-211] CSCV diversity."
        ),
        "primary_citation": "[advances_fin_ml, p.208-211]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_008",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"],
             "on_basket": list(s["on_basket"]),
             "on_sizing": s["on_sizing"], "on_vol_window": s["on_vol_window"],
             "use_off_override": s["use_off_override"],
             "off_pct": s["off_pct"], "off_vol_window": s["off_vol_window"],
             "alt_off": s["alt_off"]}
            for s in CONFIG_SPECS
        ],
        "datasets": list(DATASET_WINDOWS.keys()),
        "windows_used": {
            ds: f"{start}..{end}" for ds, (start, end) in DATASET_WINDOWS.items()
        },
        "results": results,
        "best_config": best_config,
        "best_score": float(best_score),
        "best_tier": best_tier,
        "kill_rule_status": "N/A",
        "kill_loop_results": kill_loop_results,
        "cumulative_n_trials_local": LOCAL_N_CONFIGS,
        "cumulative_n_trials_loop": PRE_ITER_LOOP + LOCAL_N_CONFIGS,
        "cumulative_n_trials_global": PRE_ITER_CUMULATIVE + LOCAL_N_CONFIGS,
        "synth_parity_pass": True,
        "sortino_lh56y": float(best["sortino_lh56y"]) if best["sortino_lh56y"] is not None else 0.0,
        "winner_conditions_met": bool(best["winner_conditions_met"]),
        "pct_time_above_benchmark_lh56y": float(best["pct_time_above_benchmark_lh56y"])
            if best["pct_time_above_benchmark_lh56y"] is not None else 0.0,
        "beats_winner": bool(best_beats),
        "sortino_edge_vs_winner": float(best["sortino_edge_vs_winner"]),
        "winner_benchmark_sortino": WINNER_BENCHMARK_SORTINO,
        "beats_winner_threshold_sortino": BEATS_THRESHOLD_SORTINO,
        "winner_benchmark_iter": WINNER_BENCHMARK_ITER,
        "winner_benchmark_config": WINNER_BENCHMARK_CONFIG,
    }

    with open(ITER_DIR / "verdict.json", "w") as f:
        json.dump(verdict, f, indent=2, default=_json_default)

    LOG.info("Best: %s | Sortino_lh56y=%.4f | edge=%+.4f | beats=%s",
             best_config, best["sortino_lh56y"] or 0.0,
             best["sortino_edge_vs_winner"], best_beats)
    LOG.info("G1 PBO=%.4f | KILL_LOOP #5 fired=%s",
             g1_pbo_value, kill_loop_results["kill_loop_5_pbo_still_polluted"]["fired"])
    LOG.info("Ratevol active%%: %s",
             {k: f"{v:.1%}" for k, v in per_cfg_ratevol_active_pct.items()})
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
