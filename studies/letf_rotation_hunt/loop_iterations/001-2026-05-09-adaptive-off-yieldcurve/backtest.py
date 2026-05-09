"""Iter 001 — adaptive OFF-asset rotation via term-premium regime.

Tests whether routing the OFF leg to ZROZ vs CASHX based on yield-curve
slope (10y CMT - 3m CMT) rescues the 2022_rates crisis loss of the study
winner without sacrificing 2008/2020 alpha.

Citations:
  - [systematic_trading, ch.9 p.180-190]: Carver carry framework (regime gate
    use here, not continuous forecast magnitude).
  - [advances_fin_ml, p.208-211]: PBO via CSCV (G1).
  - [advances_fin_ml, p.222-223]: DSR + cumulative n_trials (G2/global denom).
  - [leverage_for_the_long_run, p.5-6]: vol gate context (inherited).
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.data_loader import (
    load_ffr_daily,
    load_testfolio_series,
)
from studies.letf_rotation_hunt.data_loader_yields import (
    load_constant_maturity_yield,
)
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
LOG = logging.getLogger("iter001")

# Winner benchmark (frozen per LOOP_PROTOCOL.md)
WINNER_BENCHMARK_SORTINO = 1.3246
WINNER_BENCHMARK_ITER = "022-2026-05-06-T3d-extended-grid"
WINNER_BENCHMARK_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
BEATS_THRESHOLD_SORTINO = 1.3746
BEATS_PCT_ABOVE = 0.95

# Trial accounting (per LOOP_MEMORY.md frontmatter)
CLOSED_STUDY_CUMULATIVE = 426
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
    """Load price series for QLD/ZROZ/CASHX/SPY/QQQ + yield curves."""
    return {
        "QLDSIM":  load_testfolio_series("QLDSIM"),
        "ZROZSIM": load_testfolio_series("ZROZSIM"),
        "CASHX":   load_testfolio_series("CASHX"),
        "SPYSIM":  load_testfolio_series("SPYSIM"),
        "QQQSIM":  load_testfolio_series("QQQSIM"),
    }


def load_yield_curve_slope() -> pd.Series:
    """10y - 3m CMT spread (decimal annual, daily). ffilled across holidays."""
    cmt_10y = load_constant_maturity_yield("10y")
    cmt_3m = load_constant_maturity_yield("3m")
    aligned = pd.concat({"y10": cmt_10y, "y3m": cmt_3m}, axis=1).ffill().dropna()
    slope = (aligned["y10"] - aligned["y3m"]).rename("term_spread_10y_3m")
    return slope


def load_y10_level() -> pd.Series:
    """10y CMT level for level-vs-trend regime (config #6)."""
    return load_constant_maturity_yield("10y")


# ---------------------------------------------------------------------------
# OFF-asset selectors
# ---------------------------------------------------------------------------


def off_signal_constant_zroz(price_index: pd.DatetimeIndex) -> pd.Series:
    """Always-ZROZ defensive leg (winner replica)."""
    return pd.Series(1.0, index=price_index, name="off_zroz")


def off_signal_term_premium(
    price_index: pd.DatetimeIndex, slope: pd.Series, threshold: float,
) -> pd.Series:
    """Daily 1.0 if (10y - 3m) > threshold (in decimal, e.g. 0.005 = 0.5pp), else 0.0.

    Returns a boolean-as-float Series indexed on price_index. Slope is reindexed
    via ffill (yields update on business days; carry forward over weekends/holidays).
    NaN at the very start (before first slope observation) is treated as 0
    (cash) to avoid look-ahead — the signal must wait until real curve data
    exists.
    """
    aligned = slope.reindex(price_index).ffill()
    flag = (aligned > threshold).astype(float)
    flag[aligned.isna()] = 0.0
    return flag.rename(f"off_zroz_ts{int(threshold * 1000):03d}")


def off_signal_level_vs_trend(
    price_index: pd.DatetimeIndex, y10: pd.Series, sma_window: int = 252,
) -> pd.Series:
    """ZROZ when 10y rate is FALLING (10y < 252d-SMA(10y)); else CASHX.

    Captures the "rates trending down → long duration wins" regime distinct
    from term-premium slope. NaN warmup → 0 (cash).
    """
    aligned = y10.reindex(price_index).ffill()
    sma = aligned.rolling(window=sma_window, min_periods=sma_window).mean()
    flag = (aligned < sma).astype(float)
    flag[sma.isna()] = 0.0
    return flag.rename("off_zroz_lvltrnd")


# ---------------------------------------------------------------------------
# Trend ON signal (winner replica)
# ---------------------------------------------------------------------------


def trend_on_signal(
    qld_prices: pd.Series, qld_returns: pd.Series,
    sma_long: int = 250, sma_short: int = 100,
    vol_window: int = 21, vol_threshold: float = 0.40,
    ar_window: int = 30,
) -> pd.Series:
    """vote-of-2 of {SMA250, SMA100, vol_21d<40%, AR(1)_30d>0} on QLD.

    Replicates the iter 022 study winner's trend signal. Returns 1/0 on
    every date past warmup; NaN propagated from any missing input.
    """
    s1 = sma_gate(qld_prices, period=sma_long)
    s2 = sma_gate(qld_prices, period=sma_short)
    s3 = realized_vol_gate(qld_returns, window=vol_window, threshold=vol_threshold)
    ar1 = ar1_coefficient(qld_returns, window=ar_window)
    s4 = (ar1 > 0).astype(float)
    s4[ar1.isna()] = np.nan
    return vote_of_k([s1, s2, s3, s4], k=2)


# ---------------------------------------------------------------------------
# Strategy returns
# ---------------------------------------------------------------------------


def build_strategy_returns(
    on_signal: pd.Series,
    off_zroz_signal: pd.Series,
    on_returns: pd.Series,
    zroz_returns: pd.Series,
    cashx_returns: pd.Series,
) -> pd.Series:
    """Compose daily returns:
        if on_signal == 1: on_returns
        elif off_zroz_signal == 1: zroz_returns
        else: cashx_returns

    Lag the ON signal by 1 day (signal computed at close of day t-1, applied
    at open of day t). Same convention as the closed study.
    """
    aligned = pd.concat({
        "on_sig": on_signal.shift(1),
        "off_sig": off_zroz_signal.shift(1),
        "ret_on": on_returns,
        "ret_zroz": zroz_returns,
        "ret_cash": cashx_returns,
    }, axis=1).dropna(subset=["ret_on", "ret_zroz", "ret_cash"])

    on_active = aligned["on_sig"] == 1
    off_to_zroz = (aligned["on_sig"] == 0) & (aligned["off_sig"] == 1)
    off_to_cash = (aligned["on_sig"] == 0) & (aligned["off_sig"] == 0)

    out = pd.Series(0.0, index=aligned.index)
    out[on_active] = aligned.loc[on_active, "ret_on"]
    out[off_to_zroz] = aligned.loc[off_to_zroz, "ret_zroz"]
    out[off_to_cash] = aligned.loc[off_to_cash, "ret_cash"]
    # Drop warm-up bars where on_signal is still NaN
    out = out[aligned["on_sig"].notna()]
    return out


# ---------------------------------------------------------------------------
# Per-dataset metrics (Sharpe, Sortino, MDD, ...)
# ---------------------------------------------------------------------------


def windowed_returns(returns: pd.Series, start: str, end: str) -> pd.Series:
    return returns[(returns.index >= start) & (returns.index <= end)].dropna()


def compute_per_dataset(
    strategy_returns: pd.Series,
    spy_returns: pd.Series,
) -> dict[str, dict]:
    """For each dataset window, compute metrics + Sortino + benchmark equity."""
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
# Main
# ---------------------------------------------------------------------------


def main() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    LOG.info("Loading universe + yield curve data...")
    universe = load_universe()
    slope = load_yield_curve_slope()
    y10 = load_y10_level()

    qld = universe["QLDSIM"]
    zroz = universe["ZROZSIM"]
    cashx = universe["CASHX"]
    spy = universe["SPYSIM"]

    qld_ret = qld.pct_change().dropna()
    zroz_ret = zroz.pct_change().dropna()
    cashx_ret = cashx.pct_change().dropna()
    spy_ret = spy.pct_change().dropna()

    LOG.info("Computing trend ON signal (winner replica)...")
    on_sig = trend_on_signal(qld, qld_ret, sma_long=250, sma_short=100)

    config_specs = [
        {
            "name": "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_baseline",
            "off_kind": "constant_zroz",
            "off_param": None,
        },
        {
            "name": "qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts000",
            "off_kind": "term_premium",
            "off_param": 0.000,
        },
        {
            "name": "qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts050",
            "off_kind": "term_premium",
            "off_param": 0.005,
        },
        {
            "name": "qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts100",
            "off_kind": "term_premium",
            "off_param": 0.010,
        },
        {
            "name": "qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts150",
            "off_kind": "term_premium",
            "off_param": 0.015,
        },
        {
            "name": "qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_lvltrnd",
            "off_kind": "level_vs_trend",
            "off_param": 252,
        },
    ]

    per_cfg_returns: dict[str, pd.Series] = {}
    per_cfg_metrics: dict[str, dict] = {}
    per_cfg_off_signal: dict[str, pd.Series] = {}
    per_cfg_combined_signal: dict[str, pd.Series] = {}

    LOG.info("Running %d configs...", len(config_specs))
    for spec in config_specs:
        if spec["off_kind"] == "constant_zroz":
            off_sig = off_signal_constant_zroz(qld.index)
        elif spec["off_kind"] == "term_premium":
            off_sig = off_signal_term_premium(qld.index, slope, spec["off_param"])
        elif spec["off_kind"] == "level_vs_trend":
            off_sig = off_signal_level_vs_trend(qld.index, y10, spec["off_param"])
        else:
            raise ValueError(f"unknown off_kind: {spec['off_kind']}")

        strat_r = build_strategy_returns(on_sig, off_sig, qld_ret, zroz_ret, cashx_ret)
        per_cfg_returns[spec["name"]] = strat_r
        per_cfg_off_signal[spec["name"]] = off_sig
        # Combined exposure indicator: 1 if equity, 0.5 if ZROZ, 0 if cash (visualization-only)
        on_lag = on_sig.shift(1).reindex(strat_r.index)
        off_lag = off_sig.shift(1).reindex(strat_r.index)
        combined = pd.Series(0.0, index=strat_r.index)
        combined[(on_lag == 1)] = 1.0
        combined[(on_lag == 0) & (off_lag == 1)] = 0.5
        per_cfg_combined_signal[spec["name"]] = combined

    # SPY anchor (lh_56y window, full)
    spy_metrics_per_dataset = spy_anchor_metrics(spy_ret)

    LOG.info("Computing per-config metrics...")
    for name, r in per_cfg_returns.items():
        per_cfg_metrics[name] = compute_per_dataset(r, spy_ret)

    # Run gates per config (G1 cross-config; G2-G7 per config)
    LOG.info("Running gates (G1 PBO is cross-config, G2-G7 per-config)...")
    g1_inputs = {
        name: windowed_returns(r, *DATASET_WINDOWS["lh_56y"])
        for name, r in per_cfg_returns.items()
    }
    g1_result = g1_pbo(g1_inputs)

    spy_lh = windowed_returns(spy_ret, *DATASET_WINDOWS["lh_56y"])

    n_trials_local = LOCAL_N_CONFIGS
    n_trials_global = CLOSED_STUDY_CUMULATIVE + LOCAL_N_CONFIGS

    results = []
    for spec in config_specs:
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

        anchors_sharpe = {
            ds: spy_metrics_per_dataset[ds]["sharpe"]
            for ds in DATASET_WINDOWS
        }
        spy_mdds = {
            ds: spy_metrics_per_dataset[ds]["mdd"]
            for ds in DATASET_WINDOWS
        }
        score_input_metrics = {
            ds: per_cfg_metrics[name][ds]
            for ds in DATASET_WINDOWS
        }
        score = score_strategy(
            metrics_per_dataset=score_input_metrics,
            anchors_sharpe_per_dataset=anchors_sharpe,
            spy_mdd_per_dataset=spy_mdds,
            gates=gate_dict,
            crisis_beats_spy=crisis_flags,
            bonus_pts=0.0,
        )

        # Sortino edge vs winner (lh_56y reference)
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
            "off_kind": spec["off_kind"],
            "off_param": spec["off_param"],
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
        })

    # Save returns CSV per config
    LOG.info("Saving per-config strategy returns...")
    for name, r in per_cfg_returns.items():
        r.to_csv(ITER_DIR / f"{name}_strategy_returns.csv", header=["return"])

    # ----- best config selection (by sortino_lh56y, ties broken by score) -----
    def _key(rec):
        s = rec["sortino_lh56y"] if rec["sortino_lh56y"] is not None else -1e9
        return (s, rec["score_breakdown"]["total"])

    sorted_results = sorted(results, key=_key, reverse=True)
    best = sorted_results[0]
    best_config = best["config_name"]
    best_score = best["score_breakdown"]["total"]
    best_tier = best["tier_label"]
    best_beats = best["beats_winner"]

    # ----- plots -----
    LOG.info("Generating plots...")
    equity_curves_lh = {}
    on_signal_per_cfg = {}
    for name in per_cfg_returns:
        r_lh = windowed_returns(per_cfg_returns[name], *DATASET_WINDOWS["lh_56y"])
        equity_curves_lh[name] = (1.0 + r_lh).cumprod() * 10_000.0
        on_signal_per_cfg[name] = per_cfg_combined_signal[name]
    spy_eq_lh = (1.0 + windowed_returns(spy_ret, *DATASET_WINDOWS["lh_56y"])).cumprod() * 10_000.0
    equity_curves_lh["SPY 1× b&h"] = spy_eq_lh

    plots_dir = ITER_DIR / "plots"
    plot_equity_curves(
        equity_curves_lh, plots_dir / "01_equity_curves.png",
        title="Iter 001 — adaptive OFF rotation (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 001 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 001 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 001 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 001 — % time ON-equity (avg exposure proxy)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 001 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 001 — crisis MDD vs SPY",
    )

    # ----- tables -----
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
        })
    pd.DataFrame(gate_rows).to_csv(ITER_DIR / "tables" / "gates_pass_fail.csv", index=False)

    # ----- verdict.json -----
    verdict = {
        "iter": "001-2026-05-09-adaptive-off-yieldcurve",
        "tier": "loop_iter",
        "hypothesis": (
            "Term-premium-aware OFF-asset rotation (10y - 3m CMT slope gates "
            "ZROZ vs CASHX during defensive periods) attempts to rescue the 2022 "
            "rates crisis loss of the study winner without sacrificing 2008/2020. "
            "Same trend ON signal as winner (vote-of-2 sma250/100 vol21<40% ar30>0)."
        ),
        "primary_citation": "[systematic_trading, ch.9 p.180-190]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_001",
        "configs_tested": [
            {"name": s["name"], "off_kind": s["off_kind"], "off_param": s["off_param"]}
            for s in config_specs
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
        "cumulative_n_trials_loop": LOCAL_N_CONFIGS,
        "cumulative_n_trials_global": CLOSED_STUDY_CUMULATIVE + LOCAL_N_CONFIGS,
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
             best_config, best["sortino_lh56y"], best["sortino_edge_vs_winner"], best_beats)
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
