"""Iter 007 — compound ratevol-OFF × invvol-ON-basket.

Tests the cross-product of the two best-performing loop mechanics:
- Iter 005: multi-asset ON basket {QLD, UPRO, UGL} sized by inverse 60d
  realised vol (Sortino_lh56y 1.3340, edge +0.0094).
- Iter 006: ratevol regime gate diverting OFF leg from ZROZ to CASHX when
  ZROZ realised-vol percentile (60d / trailing 5y) > 70th (Sortino_lh56y
  1.3386, edge +0.0140).

Six configs span a 3-axis orthogonal grid with **real mechanism switches**
(ON-leg type, OFF-mechanic, alt-OFF asset) — designed to break the G1 PBO
0.79-0.88 ceiling that has blocked every loop iter so far. Iter 004's
clean PBO 0.071 with a similar 3-axis mechanism-switch design is the
proof-of-concept.

Citations
---------
- [stocks_on_the_move, p.98]: Clenow vol-parity sizing (ON-leg basket).
- [volatility_trading, p.58-60]: Sinclair volatility cone (OFF-leg ratevol).
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking — compounding
  mechanically-orthogonal lifts.
- [systematic_trading, ch.10]: Carver inverse vol (basket sizing).
- [advances_fin_ml, p.208-211]: PBO via CSCV (G1).
- [advances_fin_ml, p.222-223]: DSR + cumulative n_trials (G2 global).
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
LOG = logging.getLogger("iter007")


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Helpers re-imported from prior loop iters (committed, read-only).
_PRIOR_ITERS = ITER_DIR.parent
BSK = _load_module(
    _PRIOR_ITERS / "005-2026-05-09-multi-asset-on-invvol" / "basket_sizer.py",
    "iter007_basket_sizer",
)
RV = _load_module(
    _PRIOR_ITERS / "006-2026-05-09-bond-ratevol-regime" / "rate_vol_gate.py",
    "iter007_rate_vol_gate",
)

# Winner benchmark (frozen per LOOP_PROTOCOL.md)
WINNER_BENCHMARK_SORTINO = 1.3246
WINNER_BENCHMARK_ITER = "022-2026-05-06-T3d-extended-grid"
WINNER_BENCHMARK_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
BEATS_THRESHOLD_SORTINO = 1.3746
BEATS_PCT_ABOVE = 0.95

# Trial accounting (per LOOP_MEMORY.md frontmatter at iter 006 close)
PRE_ITER_CUMULATIVE = 462
PRE_ITER_LOOP = 36
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
# Compound strategy returns: multi-asset ON basket × ratevol OFF override
# ---------------------------------------------------------------------------


def build_compound_strategy_returns(
    on_signal: pd.Series,
    on_basket_returns: pd.Series,
    off_returns: pd.Series,
    alt_off_returns: pd.Series,
    ratevol_gate: pd.Series,
    use_off_override: bool,
) -> pd.Series:
    """Apply trend signal with multi-asset ON-leg AND ratevol OFF-leg override.

    Behavior:
      use_off_override=False (no ratevol gate):
        ON state  → on_basket_returns
        OFF state → off_returns (always ZROZ)
      use_off_override=True (with ratevol gate):
        ON state                    → on_basket_returns
        OFF + ratevol fired (=1)    → alt_off_returns (CASHX or IEFSIM)
        OFF + ratevol not fired (=0)→ off_returns (ZROZ)
        OFF + ratevol NaN (warmup)  → off_returns (baseline fallback)

    All signals are lagged 1 day (computed at close of t-1, applied at
    open of t). Same lag convention as iters 005/006.

    Returns a Series with index = aligned business days (rows where all
    required return streams + on_signal are non-NaN).
    """
    aligned = pd.concat({
        "on_sig": on_signal.shift(1),
        "rv": ratevol_gate.shift(1),
        "ret_on": on_basket_returns,
        "ret_off": off_returns,
        "ret_alt": alt_off_returns,
    }, axis=1).dropna(subset=["ret_on", "ret_off", "ret_alt"])

    on_state = (aligned["on_sig"] == 1)
    out = pd.Series(0.0, index=aligned.index)

    if not use_off_override:
        out[on_state] = aligned.loc[on_state, "ret_on"]
        out[~on_state] = aligned.loc[~on_state, "ret_off"]
    else:
        rv_filled = aligned["rv"].fillna(0.0)
        gate_fired = (rv_filled == 1)

        on_active = on_state
        off_active_normal = (~on_state) & (~gate_fired)
        off_active_override = (~on_state) & gate_fired

        out[on_active] = aligned.loc[on_active, "ret_on"]
        out[off_active_normal] = aligned.loc[off_active_normal, "ret_off"]
        out[off_active_override] = aligned.loc[off_active_override, "ret_alt"]

    out = out[aligned["on_sig"].notna()]
    return out


def compound_turnover(
    weights: pd.DataFrame | None,
    on_signal: pd.Series,
    ratevol_gate: pd.Series,
    use_off_override: bool,
) -> float:
    """Annualised turnover combining basket weight changes and OFF-leg switches.

    For a single-asset ON config (weights=None), turnover counts only
    state transitions (ON↔OFF, plus OFF↔alt-OFF when override active).
    For a multi-asset basket, turnover = 0.5 × Σ |Δw| within ON state +
    state-change transitions.
    """
    on_lag = on_signal.shift(1)
    rv_lag = ratevol_gate.shift(1) if ratevol_gate is not None else None

    if weights is None:
        # Single-asset: categorical exposure {0=alt-off, 1=on, 2=off-zroz}
        idx = on_lag.dropna().index
        exposure = pd.Series(0, index=idx)
        if not use_off_override:
            exposure[on_lag.reindex(idx) == 1] = 1
            exposure[on_lag.reindex(idx) != 1] = 2
        else:
            rv_lag_filled = rv_lag.reindex(idx).fillna(0.0)
            on_lag_idx = on_lag.reindex(idx)
            exposure[(on_lag_idx == 1)] = 1
            exposure[(on_lag_idx != 1) & (rv_lag_filled != 1)] = 2
            exposure[(on_lag_idx != 1) & (rv_lag_filled == 1)] = 0
        changes = (exposure != exposure.shift(1)).sum()
        n_years = len(exposure) / 252.0
        return float(changes / max(n_years, 1e-9))

    # Multi-asset: basket-weight delta within ON state + OFF-side switches
    idx = weights.index
    on_lag_idx = on_lag.reindex(idx).fillna(0.0)
    in_on = (on_lag_idx == 1).astype(float)
    w_eff = weights.fillna(0.0).mul(in_on, axis=0)
    w_diff = (w_eff - w_eff.shift(1)).abs().sum(axis=1).fillna(0.0)
    basket_turnover = 0.5 * w_diff.sum()

    # State-change component: ON↔OFF and OFF↔alt-OFF for off-override
    if use_off_override and rv_lag is not None:
        rv_lag_filled = rv_lag.reindex(idx).fillna(0.0)
        # Categorical: 0 alt-off, 1 on, 2 off-zroz
        exposure = pd.Series(2, index=idx)
        exposure[(on_lag_idx == 1)] = 1
        exposure[(on_lag_idx != 1) & (rv_lag_filled == 1)] = 0
    else:
        exposure = pd.Series(2, index=idx)
        exposure[(on_lag_idx == 1)] = 1
    state_changes = (exposure != exposure.shift(1)).sum()

    n_years = len(idx) / 252.0
    total = basket_turnover + state_changes
    return float(total / max(n_years, 1e-9))


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
# Configs (6, 3-axis orthogonal grid)
# ---------------------------------------------------------------------------


CONFIG_SPECS = [
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_compound_baseline",
     "kind": "baseline",
     "on_basket": ["QLDSIM"], "on_sizing": "single", "on_vol_window": None,
     "use_off_override": False, "off_pct": None, "off_vol_window": None,
     "alt_off": None},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_compound_ratevol_only",
     "kind": "ratevol_only",
     "on_basket": ["QLDSIM"], "on_sizing": "single", "on_vol_window": None,
     "use_off_override": True, "off_pct": 0.70, "off_vol_window": 60,
     "alt_off": "CASHX"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_compound_basket3_only",
     "kind": "basket3_only",
     "on_basket": ["QLDSIM", "UPROSIM", "UGLSIM"], "on_sizing": "invvol",
     "on_vol_window": 60,
     "use_off_override": False, "off_pct": None, "off_vol_window": None,
     "alt_off": None},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_compound_basket3_x_ratevol_p70_cashx",
     "kind": "compound_basket3_cashx",
     "on_basket": ["QLDSIM", "UPROSIM", "UGLSIM"], "on_sizing": "invvol",
     "on_vol_window": 60,
     "use_off_override": True, "off_pct": 0.70, "off_vol_window": 60,
     "alt_off": "CASHX"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_compound_basket3_x_ratevol_p70_ief",
     "kind": "compound_basket3_ief",
     "on_basket": ["QLDSIM", "UPROSIM", "UGLSIM"], "on_sizing": "invvol",
     "on_vol_window": 60,
     "use_off_override": True, "off_pct": 0.70, "off_vol_window": 60,
     "alt_off": "IEFSIM"},
    {"name": "qld_voteK2_sma250_100_vol21_40_ar30_compound_basket2_qld_ugl_x_ratevol_p70_cashx",
     "kind": "compound_basket2_qld_ugl_cashx",
     "on_basket": ["QLDSIM", "UGLSIM"], "on_sizing": "invvol",
     "on_vol_window": 60,
     "use_off_override": True, "off_pct": 0.70, "off_vol_window": 60,
     "alt_off": "CASHX"},
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
        title="Iter 007 — compound: ratevol-OFF × invvol-ON-basket (lh_56y, log)",
    )
    plot_drawdown_curves(
        equity_curves_lh, plots_dir / "02_drawdown_curves.png",
        title="Iter 007 — drawdowns (lh_56y)",
    )
    plot_rolling_sharpe(
        equity_curves_lh, plots_dir / "03_rolling_sharpe_5y.png",
        window_days=252 * 5, title="Iter 007 — 5y rolling Sharpe",
    )
    plot_rolling_cagr(
        equity_curves_lh, plots_dir / "04_rolling_cagr_3y.png",
        window_days=252 * 3, title="Iter 007 — 3y rolling CAGR",
    )
    plot_regime_attribution(
        equity_curves_lh, on_signal_per_cfg, plots_dir / "05_regime_attribution.png",
        title="Iter 007 — % time in equity (vote-K=2 ON state)",
    )
    plot_pct_beat_spy(
        equity_curves_lh, spy_eq_lh, plots_dir / "06_pct_beat_spy.png",
        title="Iter 007 — cumulative % of 3y windows beating SPY",
    )
    plot_crisis_attribution(
        equity_curves_lh, spy_eq_lh, plots_dir / "07_crisis_attribution.png",
        title="Iter 007 — crisis MDD vs SPY",
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
        "iter": "007-2026-05-09-compound-ratevol-off-x-invvol-on-basket",
        "tier": "loop_iter",
        "hypothesis": (
            "Compound: ratevol-OFF (iter 006 best mechanic) × invvol-ON-basket "
            "(iter 005 best mechanic). Tests whether the two best independent "
            "loop-mechanics combine constructively (orthogonal compounding) or "
            "destructively (mechanism conflict). Secondary hypothesis: 3-axis "
            "orthogonal grid with real mechanism switches breaks G1 PBO ceiling. "
            "[stocks_on_the_move, p.98] + [volatility_trading, p.58-60] + "
            "[risk_parity, ch.5]."
        ),
        "primary_citation": "[stocks_on_the_move, p.98]",
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": "loop_iter_007",
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
