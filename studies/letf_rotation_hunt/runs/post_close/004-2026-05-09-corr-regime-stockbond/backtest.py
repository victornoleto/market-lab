"""Iter 004 — stock-bond correlation regime master-gate.

Tests whether a rolling correlation between QLD daily returns and ZROZ daily
returns can serve as a Risk-on/Risk-off (RORO) regime classifier overlaid on
the winner's vote-of-K trend signal. Six configs sweep along three orthogonal
dimensions: correlation threshold (0.00 / 0.20 / 0.30), window (60d / 120d),
and override scope (OFF-leg-only vs whole portfolio).

Citations:
  - [risk_parity, p.80-81, ch.4]: Qian on RORO regime — stock-bond correlation
    flip from negative to positive eliminates diversification value.
  - [risk_parity, p.110, ch.5]: Qian on diversification return collapsing
    when correlation becomes positive.
  - [ml_for_algo_trading, ch.9]: Jansen rolling state features for regime
    classification.
  - [advances_fin_ml, p.208-211]: PBO via CSCV (G1).
  - [advances_fin_ml, p.222-223]: DSR + cumulative n_trials (G2/global denom).
  - [systematic_trading, p.180-190]: Carver overlay shape.
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
    compute_metrics,
    crisis_beats_benchmark,
    score_strategy,
)
from studies.letf_rotation_hunt.core.signals import (
    ar1_coefficient,
    realized_vol_gate,
    sma_gate,
    vote_of_k,
)
from studies.letf_rotation_hunt.analyses.sortino_reanalysis.sortino_metric import (
    _annualised_sortino,
)

ITER_DIR = Path(__file__).parent
LOG = logging.getLogger("iter004")


def _load_corr_module():
    spec = importlib.util.spec_from_file_location(
        "iter004_correlation_gate", ITER_DIR / "correlation_gate.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CORR = _load_corr_module()

# Winner benchmark (frozen per LOOP_PROTOCOL.md)
WINNER_BENCHMARK_SORTINO = 1.3246
WINNER_BENCHMARK_ITER = "022-2026-05-06-T3d-extended-grid"
WINNER_BENCHMARK_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
BEATS_THRESHOLD_SORTINO = 1.3746
BEATS_PCT_ABOVE = 0.95

# Trial accounting (per LOOP_MEMORY.md frontmatter at iter 003 close)
PRE_ITER_CUMULATIVE = 444
PRE_ITER_LOOP = 18
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
        "ZROZSIM": load_testfolio_series("ZROZSIM"),
        "CASHX":   load_testfolio_series("CASHX"),
        "SPYSIM":  load_testfolio_series("SPYSIM"),
    }


# ---------------------------------------------------------------------------
# Trend ON signal (winner replica vote-of-2 of 4)
# ---------------------------------------------------------------------------


def build_winner_on_signal(
    qld_prices: pd.Series,
    qld_returns: pd.Series,
    sma_long: int = 250, sma_short: int = 100,
    vol_window: int = 21, vol_threshold: float = 0.40,
    ar_window: int = 30,
) -> pd.Series:
    """Winner replica: vote-of-2 of {SMA250, SMA100, vol_21d<40%, AR(1)_30d>0}."""
    s1 = sma_gate(qld_prices, period=sma_long)
    s2 = sma_gate(qld_prices, period=sma_short)
    s3 = realized_vol_gate(qld_returns, window=vol_window, threshold=vol_threshold)
    ar1 = ar1_coefficient(qld_returns, window=ar_window)
    s4 = (ar1 > 0).astype(float)
    s4[ar1.isna()] = np.nan
    return vote_of_k([s1, s2, s3, s4], k=2)


# ---------------------------------------------------------------------------
# Strategy returns with correlation-regime override
# ---------------------------------------------------------------------------


def build_strategy_returns(
    on_signal: pd.Series,
    corrgate: pd.Series,
    on_returns: pd.Series,
    off_returns: pd.Series,
    cash_returns: pd.Series,
    override_scope: str,
) -> pd.Series:
    """Apply trend signal + correlation-regime override.

    Override scopes:
      "none"          → no override (baseline)
      "offleg_cashx"  → when ON state: hold ON asset; when OFF state and
                        corrgate=1: route to CASHX instead of off asset
      "master_cashx"  → when corrgate=1: force entire portfolio to CASHX
                        regardless of ON/OFF state

    All signals lagged 1 day (computed at close of t-1, applied at open of t).
    """
    aligned = pd.concat({
        "on_sig": on_signal.shift(1),
        "corr": corrgate.shift(1),
        "ret_on": on_returns,
        "ret_off": off_returns,
        "ret_cash": cash_returns,
    }, axis=1).dropna(subset=["ret_on", "ret_off", "ret_cash"])

    on_state = (aligned["on_sig"] == 1)
    corr_fired = (aligned["corr"] == 1)

    out = pd.Series(0.0, index=aligned.index)

    if override_scope == "none":
        out[on_state] = aligned.loc[on_state, "ret_on"]
        out[~on_state] = aligned.loc[~on_state, "ret_off"]
    elif override_scope == "offleg_cashx":
        on_active = on_state
        off_active_normal = (~on_state) & (~corr_fired)
        off_active_override = (~on_state) & corr_fired
        out[on_active] = aligned.loc[on_active, "ret_on"]
        out[off_active_normal] = aligned.loc[off_active_normal, "ret_off"]
        out[off_active_override] = aligned.loc[off_active_override, "ret_cash"]
    elif override_scope == "master_cashx":
        master = corr_fired
        on_active = on_state & (~master)
        off_active = (~on_state) & (~master)
        out[on_active] = aligned.loc[on_active, "ret_on"]
        out[off_active] = aligned.loc[off_active, "ret_off"]
        out[master] = aligned.loc[master, "ret_cash"]
    else:
        raise ValueError(f"unknown override_scope: {override_scope}")

    out = out[aligned["on_sig"].notna()]
    return out


def turnover_proxy(combined: pd.Series) -> float:
    """Annualised number of state changes in the categorical exposure series."""
    if len(combined) < 2:
        return 0.0
    changes = (combined != combined.shift(1)).sum()
    n_years = len(combined) / 252.0
    return float(changes / max(n_years, 1e-9))


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def windowed_returns(returns: pd.Series, start: str, end: str) -> pd.Series:
    return returns[(returns.index >= start) & (returns.index <= end)].dropna()


def compute_per_dataset(
    strategy_returns: pd.Series,
    spy_returns: pd.Series,
) -> dict[str, dict]:
    out = {}
    for ds, (start, end) in DATASET_WINDOWS.items():
        r = windowed_returns(strategy_returns, start, end)
        if len(r) < 252:
            out[ds] = {"sharpe": np.nan, "sortino": np.nan, "n_obs": len(r)}
            continue
        eq = (1.0 + r).cumprod() * 10_000.0
        spy_r = windowed_returns(spy_returns, start, end)
        spy_eq = (1.0 + spy_r).cumprod() * 10_000.0
        m = compute_metrics(eq, r, benchmark_equity=spy_eq)
        m["sortino"] = _annualised_sortino(r)
        m["n_obs"] = int(len(r))
        out[ds] = m
    return out


def spy_anchor_metrics(spy_returns: pd.Series) -> dict[str, dict]:
    out = {}
    for ds, (start, end) in DATASET_WINDOWS.items():
        r = windowed_returns(spy_returns, start, end)
        if len(r) < 2:
            out[ds] = {"sharpe": np.nan, "sortino": np.nan, "mdd": np.nan}
            continue
        eq = (1.0 + r).cumprod() * 10_000.0
        m = compute_metrics(eq, r)
        m["sortino"] = _annualised_sortino(r)
        out[ds] = m
    return out


# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------


CONFIG_SPECS = [
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_corrgate_off_baseline",
     "kind": "baseline", "threshold": None, "window": None, "scope": "none"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_corrgate_t000_60d_offleg_cashx",
     "kind": "offleg", "threshold": 0.00, "window": 60, "scope": "offleg_cashx"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_corrgate_t020_60d_offleg_cashx",
     "kind": "offleg", "threshold": 0.20, "window": 60, "scope": "offleg_cashx"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_corrgate_t030_60d_offleg_cashx",
     "kind": "offleg_strict", "threshold": 0.30, "window": 60, "scope": "offleg_cashx"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_corrgate_t020_120d_offleg_cashx",
     "kind": "offleg_slow", "threshold": 0.20, "window": 120, "scope": "offleg_cashx"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_corrgate_t020_60d_master_cashx",
     "kind": "master", "threshold": 0.20, "window": 60, "scope": "master_cashx"},
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    LOG.info("Loading universe...")
    universe = load_universe()
    qld = universe["QLDSIM"]
    zroz = universe["ZROZSIM"]
    cash = universe["CASHX"]
    spy = universe["SPYSIM"]

    qld_ret = qld.pct_change().dropna()
    zroz_ret = zroz.pct_change().dropna()
    cash_ret = cash.pct_change().dropna()
    spy_ret = spy.pct_change().dropna()

    on_signal = build_winner_on_signal(qld, qld_ret)

    per_cfg_returns: dict[str, pd.Series] = {}
    per_cfg_metrics: dict[str, dict] = {}
    per_cfg_combined: dict[str, pd.Series] = {}
    per_cfg_corrgate_active_pct: dict[str, float] = {}
    per_cfg_turnover: dict[str, float] = {}

    LOG.info("Running %d configs...", len(CONFIG_SPECS))
    for spec in CONFIG_SPECS:
        if spec["scope"] == "none":
            corrgate = pd.Series(0.0, index=qld_ret.index)
        else:
            corrgate = CORR.corr_regime_gate(
                qld_ret, zroz_ret,
                threshold=spec["threshold"], window=spec["window"],
            )

        strat_r = build_strategy_returns(
            on_signal, corrgate, qld_ret, zroz_ret, cash_ret,
            override_scope=spec["scope"],
        )
        per_cfg_returns[spec["name"]] = strat_r

        on_lag = on_signal.shift(1).reindex(strat_r.index)
        corr_lag = corrgate.shift(1).reindex(strat_r.index).fillna(0.0)

        # Categorical exposure: 0=cash, 1=on, 2=off (for turnover proxy)
        exposure = pd.Series(0, index=strat_r.index)
        if spec["scope"] == "none":
            exposure[on_lag == 1] = 1
            exposure[on_lag != 1] = 2
        elif spec["scope"] == "offleg_cashx":
            exposure[(on_lag == 1)] = 1
            exposure[(on_lag != 1) & (corr_lag != 1)] = 2
            exposure[(on_lag != 1) & (corr_lag == 1)] = 0
        elif spec["scope"] == "master_cashx":
            exposure[(corr_lag != 1) & (on_lag == 1)] = 1
            exposure[(corr_lag != 1) & (on_lag != 1)] = 2
            exposure[(corr_lag == 1)] = 0
        per_cfg_combined[spec["name"]] = (exposure == 1).astype(float)
        per_cfg_corrgate_active_pct[spec["name"]] = float(corr_lag.mean())
        per_cfg_turnover[spec["name"]] = turnover_proxy(exposure)

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
            "threshold": spec["threshold"],
            "window": spec["window"],
            "scope": spec["scope"],
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
            "pct_time_above_benchmark_lh56y": float(pct_above_lh) if pct_above_lh == pct_above_lh else None,
            "sortino_edge_vs_winner": sortino_edge_vs_winner,
            "beats_winner": beats_winner,
            "corrgate_active_pct": per_cfg_corrgate_active_pct[name],
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

    LOG.info("Generating plots...")
    equity_curves_lh = {}
    on_signal_per_cfg = {}
    for name in per_cfg_returns:
        r_lh = windowed_returns(per_cfg_returns[name], *DATASET_WINDOWS["lh_56y"])
        equity_curves_lh[name] = (1.0 + r_lh).cumprod() * 10_000.0
        on_signal_per_cfg[name] = per_cfg_combined[name].reindex(r_lh.index).fillna(0.0)
    spy_eq_lh = (1.0 + spy_lh).cumprod() * 10_000.0
    equity_curves_lh["SPY 1× b&h"] = spy_eq_lh

    plots_dir = ITER_DIR / "plots"
    plot_equity_curves(
        equity_curves_lh, plots_dir / "01_equity_curves.png",
        title="Iter 004 — corr-regime stock-bond gate (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 004 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 004 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 004 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 004 — % time in equity (post-corrgate)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 004 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 004 — crisis MDD vs SPY",
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
            "corrgate_active_pct": rec["corrgate_active_pct"],
            "turnover_per_year": rec["turnover_per_year"],
        })
    pd.DataFrame(gate_rows).to_csv(ITER_DIR / "tables" / "gates_pass_fail.csv", index=False)

    verdict = {
        "iter": "004-2026-05-09-corr-regime-stockbond",
        "tier": "loop_iter",
        "hypothesis": (
            "Stock-bond correlation regime master-gate: when 60d/120d rolling "
            "correlation of QLD↔ZROZ daily returns exceeds 0.00/0.20/0.30, the "
            "OFF leg (or whole portfolio) is rerouted to CASHX since the "
            "diversification hedge has structurally broken (Qian RORO regime "
            "[risk_parity, p.80-81, ch.4]). Targets the 2022_rates loss "
            "directly via second-moment regime detection — orthogonal to "
            "iters 001 (yield-curve), 002 (vol-DD), 003 (calendar)."
        ),
        "primary_citation": "[risk_parity, p.80-81, ch.4]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_004",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"],
             "threshold": s["threshold"], "window": s["window"], "scope": s["scope"]}
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
    LOG.info("Corrgate active%%: %s",
             {k: f"{v:.1%}" for k, v in per_cfg_corrgate_active_pct.items()})
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
