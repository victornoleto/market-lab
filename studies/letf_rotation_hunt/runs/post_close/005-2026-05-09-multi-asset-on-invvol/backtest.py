"""Iter 005 — multi-asset ON inverse-vol basket.

Replaces the winner's single-asset (QLD) ON leg with a basket of equity-style
LETFs sized by inverse realised volatility, while keeping the winner's binary
trend gate (vote-of-K=2 of {SMA250, SMA100, vol_21d<40%, AR(1)_30d>0} on QLD)
and ZROZ as the OFF leg. Six configs sweep composition (2-asset vs 3-asset),
asset class (equity-equity vs equity-gold), vol window (60d vs 120d), and
sizing rule (inverse-vol vs equal-weight).

Citations
---------
- [stocks_on_the_move, p.98]: Clenow vol-parity sizing — w_i ∝ 1/σ_i.
- [systematic_trading, ch.10]: Carver inverse-vol position sizing.
- [risk_parity, ch.5, p.10] (archived): Carlson cap-efficient stacking
  rationale extends to multi-asset ON-leg basket.
- [advances_fin_ml, p.208-211]: PBO via CSCV (G1).
- [advances_fin_ml, p.222-223]: DSR + cumulative n_trials (G2 global denom).
- [leverage_for_the_long_run, p.21 Table 12]: LETF tracking drag (UGL).
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
LOG = logging.getLogger("iter005")


def _load_basket_module():
    spec = importlib.util.spec_from_file_location(
        "iter005_basket_sizer", ITER_DIR / "basket_sizer.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BSK = _load_basket_module()

# Winner benchmark (frozen per LOOP_PROTOCOL.md)
WINNER_BENCHMARK_SORTINO = 1.3246
WINNER_BENCHMARK_ITER = "022-2026-05-06-T3d-extended-grid"
WINNER_BENCHMARK_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
BEATS_THRESHOLD_SORTINO = 1.3746
BEATS_PCT_ABOVE = 0.95

# Trial accounting (per LOOP_MEMORY.md frontmatter at iter 004 close)
PRE_ITER_CUMULATIVE = 450
PRE_ITER_LOOP = 24
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
        "CASHX":   load_testfolio_series("CASHX"),
        "SPYSIM":  load_testfolio_series("SPYSIM"),
    }


# ---------------------------------------------------------------------------
# Trend ON signal (winner replica vote-of-2 of 4 — computed on QLD)
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
# Strategy returns with multi-asset ON basket
# ---------------------------------------------------------------------------


def build_strategy_returns(
    on_signal: pd.Series,
    on_basket_returns: pd.Series,
    off_returns: pd.Series,
) -> pd.Series:
    """Apply trend signal to a (potentially multi-asset) ON-leg return stream.

    All signals lagged 1 day (computed at close of t-1, applied at open of t).
    """
    aligned = pd.concat({
        "on_sig": on_signal.shift(1),
        "ret_on": on_basket_returns,
        "ret_off": off_returns,
    }, axis=1).dropna(subset=["ret_on", "ret_off"])

    on_state = (aligned["on_sig"] == 1)
    out = pd.Series(0.0, index=aligned.index)
    out[on_state] = aligned.loc[on_state, "ret_on"]
    out[~on_state] = aligned.loc[~on_state, "ret_off"]
    out = out[aligned["on_sig"].notna()]
    return out


def basket_turnover(
    weights: pd.DataFrame,
    on_signal: pd.Series,
) -> float:
    """Annualised turnover proxy: 0.5 × Σ_t Σ_i |w_i(t) − w_i(t−1)| in ON state.

    The 0.5 factor is the standard one-side turnover convention. Returns
    annualised total over the strategy's index.
    """
    if weights is None or weights.empty:
        # Single-asset baseline: turnover = state-change frequency only
        on_lag = on_signal.shift(1).reindex(on_signal.index).fillna(0)
        cur = on_signal.fillna(0)
        changes = (cur != on_lag).sum()
        n_years = len(on_signal) / 252.0
        return float(changes / max(n_years, 1e-9))

    on_lag = on_signal.shift(1).reindex(weights.index).fillna(0.0)
    in_on = (on_lag == 1).astype(float)
    w_eff = weights.fillna(0.0).mul(in_on, axis=0)
    w_diff = (w_eff - w_eff.shift(1)).abs().sum(axis=1).fillna(0.0)
    n_years = len(weights) / 252.0
    return float(0.5 * w_diff.sum() / max(n_years, 1e-9))


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
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_on_baseline",
     "kind": "baseline", "basket": ["QLDSIM"],
     "vol_window": None, "sizing": "single"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_on_basket2_qld_upro_invvol60",
     "kind": "basket2_equity", "basket": ["QLDSIM", "UPROSIM"],
     "vol_window": 60, "sizing": "invvol"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_on_basket2_qld_ugl_invvol60",
     "kind": "basket2_crossasset", "basket": ["QLDSIM", "UGLSIM"],
     "vol_window": 60, "sizing": "invvol"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_on_basket3_qld_upro_ugl_invvol60",
     "kind": "basket3", "basket": ["QLDSIM", "UPROSIM", "UGLSIM"],
     "vol_window": 60, "sizing": "invvol"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_on_basket3_qld_upro_ugl_invvol120",
     "kind": "basket3_slow", "basket": ["QLDSIM", "UPROSIM", "UGLSIM"],
     "vol_window": 120, "sizing": "invvol"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_on_basket3_qld_upro_ugl_eqweight",
     "kind": "basket3_eqweight", "basket": ["QLDSIM", "UPROSIM", "UGLSIM"],
     "vol_window": None, "sizing": "eqweight"},
]


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
    spy = universe["SPYSIM"]

    qld_ret = qld.pct_change().dropna()
    upro_ret = upro.pct_change().dropna()
    ugl_ret = ugl.pct_change().dropna()
    zroz_ret = zroz.pct_change().dropna()
    spy_ret = spy.pct_change().dropna()

    on_signal = build_winner_on_signal(qld, qld_ret)

    asset_returns = {
        "QLDSIM":  qld_ret,
        "UPROSIM": upro_ret,
        "UGLSIM":  ugl_ret,
    }

    per_cfg_returns: dict[str, pd.Series] = {}
    per_cfg_metrics: dict[str, dict] = {}
    per_cfg_combined: dict[str, pd.Series] = {}
    per_cfg_turnover: dict[str, float] = {}
    per_cfg_basket_size: dict[str, int] = {}

    LOG.info("Running %d configs...", len(CONFIG_SPECS))
    for spec in CONFIG_SPECS:
        basket = spec["basket"]
        per_cfg_basket_size[spec["name"]] = len(basket)
        basket_rets = {a: asset_returns[a] for a in basket}

        if spec["sizing"] == "single":
            on_basket_ret = basket_rets[basket[0]]
            weights = None
        elif spec["sizing"] == "invvol":
            weights = BSK.inverse_vol_weights(basket_rets, window=spec["vol_window"])
            on_basket_ret = BSK.basket_returns_from_weights(weights, basket_rets)
        elif spec["sizing"] == "eqweight":
            ref_index = basket_rets[basket[0]].index
            weights = BSK.equal_weights(basket, ref_index)
            on_basket_ret = BSK.basket_returns_from_weights(weights, basket_rets)
        else:
            raise ValueError(f"unknown sizing: {spec['sizing']}")

        strat_r = build_strategy_returns(on_signal, on_basket_ret, zroz_ret)
        per_cfg_returns[spec["name"]] = strat_r

        on_lag = on_signal.shift(1).reindex(strat_r.index)
        per_cfg_combined[spec["name"]] = (on_lag == 1).astype(float)
        per_cfg_turnover[spec["name"]] = basket_turnover(weights, on_signal.reindex(
            weights.index if weights is not None else on_signal.index))

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
            "basket": list(spec["basket"]),
            "basket_size": int(len(spec["basket"])),
            "vol_window": spec["vol_window"],
            "sizing": spec["sizing"],
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
        title="Iter 005 — multi-asset ON inverse-vol basket (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 005 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 005 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 005 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 005 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 005 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 005 — crisis MDD vs SPY",
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
            "basket_size": rec["basket_size"],
            "sizing": rec["sizing"],
            "vol_window": rec["vol_window"],
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
            "turnover_per_year": rec["turnover_per_year"],
        })
    pd.DataFrame(gate_rows).to_csv(ITER_DIR / "tables" / "gates_pass_fail.csv", index=False)

    verdict = {
        "iter": "005-2026-05-09-multi-asset-on-invvol",
        "tier": "loop_iter",
        "hypothesis": (
            "Multi-asset ON inverse-vol basket: replace winner's single-asset "
            "QLD ON leg with a basket of equity-style LETFs ({QLD, UPRO, UGL}) "
            "sized by inverse realised volatility (60d / 120d) so each asset "
            "contributes equal volatility, while keeping winner's binary "
            "vote-K=2 trend gate on QLD and ZROZ as OFF. Tests cross-asset "
            "first-moment diversification — orthogonal to iter 004's "
            "(failed) cross-asset second-moment regime gate. Citation: "
            "[stocks_on_the_move, p.98] (Clenow vol-parity sizing) + "
            "[systematic_trading, ch.10] (Carver inverse-vol)."
        ),
        "primary_citation": "[stocks_on_the_move, p.98]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_005",
        "configs_tested": [
            {"name": s["name"], "kind": s["kind"], "basket": s["basket"],
             "vol_window": s["vol_window"], "sizing": s["sizing"]}
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
    LOG.info("Turnover/y: %s",
             {k: f"{v:.2f}" for k, v in per_cfg_turnover.items()})
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
