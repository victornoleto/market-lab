"""T4 (Cross-sectional rotation) tier dispatcher per spec §2.5.

Pool of LETFs ranked daily by Clenow slope×R² or EWMAC composite; hold
top-K equally-weighted; master gate (SPY > SMA200) determines ON/OFF.

Sub-phases (per spec §2.5):
  - T4a: Clenow slope × R² 90d, top-2, pool {UPRO, QLD, UGL, TMF}
  - T4b: Clenow same, top-3
  - T4c: EWMAC(16,64) + EWMAC(64,256) composite, top-2
  - T4d: Clenow + per-asset vol_21d<40%, top-2, pool +SOXL (window 2010+)

Inheritance: T3-best `qld_vote_k2_off_zroz` (Sharpe 0.853) per spec §3.4.
Anti-curve-fit threshold T3→T4: T4-best Sharpe ≥ 0.903 to claim T4 winner.

OFF asset = ZROZ (default) per T1c/T1d findings (ZROZ universal preference).
Spec §2.5 didn't specify; using empirical-backed ZROZ instead of cash.

Reuses run_iter_t1's gates / scoring / artifact-writing pipeline.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_ffr_daily, load_testfolio_series
from studies.letf_rotation_hunt.core.gates import (
    g1_pbo, g2_dsr_p_value, g3_walk_forward, g4_oos_70_30,
    g5_fwd_post_2020, g6_bootstrap_ci, g7_xlib_cagr_delta,
)
from studies.letf_rotation_hunt.runners.run_iter_t1 import (
    DATASET_WINDOWS, LETF_TESTFOLIO, SPY_ANCHOR_SHARPE, SPY_MDD,
    _NAN_METRICS, _write_iter_artifacts,
)
from studies.letf_rotation_hunt.core.scoring import (
    compute_metrics, crisis_beats_benchmark, score_strategy,
)
from studies.letf_rotation_hunt.core.signals import (
    clenow_score, ewmac_forecast, realized_vol_gate, sma_gate,
)
from studies.letf_rotation_hunt.core.strategies.cross_sectional import build_positions
from studies.letf_rotation_hunt.core.synths import letf_synth_by_ticker

# T3-best Sharpe (lh_56y) — qld_vote_k2_off_zroz
_T3_BEST_SHARPE_LH56Y = 0.853
_KILL_T3_T4_THRESHOLD = _T3_BEST_SHARPE_LH56Y + 0.05  # = 0.903


def run(config: dict, verdict: dict, out_dir: Path) -> dict:
    """Run T4 sub-fase iteration."""
    tier = config["tier"]
    if not tier.startswith("T4"):
        raise ValueError(f"run_iter_t4 expects T4*, got {tier!r}")

    ffr_daily = load_ffr_daily()
    results: list[dict] = []
    n_trials_local = len(config["configs_tested"])
    n_trials_cumulative = max(
        1,
        int(config.get("cumulative_n_trials_at_iter", 0)) + n_trials_local,
    )

    for cfg in config["configs_tested"]:
        try:
            result = _run_single_xs_config(
                cfg, config["datasets"], ffr_daily,
                n_trials_local=n_trials_local,
            )
            results.append(result)
        except Exception as exc:
            results.append({
                "config_name": cfg.get("name", "unknown"),
                "error": str(exc),
                "metrics_gross": {},
                "metrics_net": {},
                "score_breakdown": {},
                "tier_label": "ERROR",
            })

    valid_results = [r for r in results if "error" not in r]
    per_cfg_returns = {
        r["config_name"]: r["_strategy_returns"]
        for r in valid_results if "_strategy_returns" in r
    }
    g1_result = g1_pbo(per_cfg_returns) if per_cfg_returns else {
        "pbo": float("nan"), "n_combinations": 0, "pass_gate": True,
    }
    for r in valid_results:
        r["gates"]["g1_pbo"] = float(g1_result["pbo"])
        r["gates"]["g1_pbo_n_combinations"] = int(g1_result["n_combinations"])
        if "_strategy_returns" in r:
            g2_cum = g2_dsr_p_value(
                r["_strategy_returns"], n_trials=max(2, n_trials_cumulative),
            )
            r["gates"]["g2_dsr_p_cumulative"] = float(g2_cum["p_value"])
        cached = r.pop("_score_inputs")
        score = score_strategy(
            cached["metrics"], cached["anchors"], cached["spy_mdds"],
            r["gates"], cached["crisis"],
        )
        r["score_breakdown"] = score
        r["tier_label"] = score["tier_label"]
        r["winner_conditions_met"] = bool(score.get("winner_conditions_met", False))

    if not valid_results:
        verdict["best_config"] = ""
        verdict["best_score"] = 0.0
        verdict["best_tier"] = "FAIL"
    else:
        best = max(
            valid_results,
            key=lambda r: r["metrics_gross"].get("lh_56y", {}).get("sharpe", -999),
        )
        verdict["best_config"] = best["config_name"]
        verdict["best_score"] = best.get("score_breakdown", {}).get("total", 0.0)
        verdict["best_tier"] = best.get("tier_label", "FAIL")

    kill_status = _evaluate_kill_t3_t4(valid_results)
    verdict["kill_rule_status"] = kill_status
    verdict["advance_to_next_tier"] = True

    if valid_results:
        _write_iter_artifacts(config, verdict, valid_results, out_dir, kill_status)

    for r in valid_results:
        r.pop("_strategy_returns", None)
        r.pop("_equity", None)
        r.pop("_signal", None)
        r.pop("_positions", None)
        r.pop("_asset_returns_aligned", None)

    verdict["results"] = results
    return verdict


def _evaluate_kill_t3_t4(valid_results: list[dict]) -> str:
    """KILL T3→T4: T4-best Sharpe vs T3-best+0.05 = 0.903."""
    if not valid_results:
        return "N/A"
    best_sharpe = max(
        r["metrics_gross"].get("lh_56y", {}).get("sharpe", float("-inf"))
        for r in valid_results
    )
    return "PASS" if best_sharpe >= _KILL_T3_T4_THRESHOLD else "FIRES"


def _resolve_asset_returns(asset: str, ffr_daily: pd.Series) -> tuple[pd.Series, pd.Series]:
    if asset not in LETF_TESTFOLIO:
        raise ValueError(f"No testfolio mapping for asset={asset!r}")
    tf_ticker, is_direct = LETF_TESTFOLIO[asset]
    series = load_testfolio_series(tf_ticker)
    if is_direct:
        returns = series.pct_change().dropna()
    else:
        underlying_returns = series.pct_change().dropna()
        returns = letf_synth_by_ticker(asset, underlying_returns, ffr_daily)
    return returns, series


def _compute_pool_scores(
    pool: list[str], score_method: str, asset_prices: dict[str, pd.Series],
    asset_returns: dict[str, pd.Series], per_asset_vol_gate: bool,
    clenow_window: int = 90,
) -> pd.DataFrame:
    """Compute daily ranking score per asset in pool. Optionally vol-gated."""
    scores_dict: dict[str, pd.Series] = {}
    for a in pool:
        prices = asset_prices[a]
        if score_method == "clenow_90":
            s = clenow_score(prices, window=clenow_window)
        elif score_method == "ewmac_composite":
            f1 = ewmac_forecast(prices, lfast=16, lslow=64)
            f2 = ewmac_forecast(prices, lfast=64, lslow=256)
            s = (f1 + f2) / 2.0
        else:
            raise ValueError(f"Unknown score_method: {score_method!r}")

        if per_asset_vol_gate:
            vol_ok = realized_vol_gate(asset_returns[a], window=21, threshold=0.40)
            # Align vol_ok index to s index, mask out where vol_ok != 1
            vol_ok = vol_ok.reindex(s.index).fillna(0).astype(float)
            s = s.where(vol_ok == 1.0)
        scores_dict[a] = s
    return pd.DataFrame(scores_dict)


def _run_single_xs_config(
    cfg: dict, datasets: list[str], ffr_daily: pd.Series, n_trials_local: int = 1,
) -> dict:
    """Run one T4 cross-sectional config.

    Config dict keys:
      - name (str)
      - pool (list[str]) — risk-on LETF universe to rank
      - top_k (int) — number of top-ranked to hold equally-weighted
      - off_asset (str) — held when master_gate=0 or pool insufficient
      - score_method (str) — "clenow_90" or "ewmac_composite"
      - per_asset_vol_gate (bool, optional, default False) — T4d
      - master_signal_asset (str, default "SPY") — testfolio ticker for master gate
      - master_signal_period (int, default 200)
    """
    name = cfg["name"]
    pool = cfg["pool"]
    top_k = int(cfg["top_k"])
    off_asset = cfg["off_asset"]
    score_method = cfg["score_method"]
    per_asset_vol_gate = bool(cfg.get("per_asset_vol_gate", False))
    master_signal_asset = cfg.get("master_signal_asset", "SPYSIM")
    master_signal_period = int(cfg.get("master_signal_period", 200))

    # --- resolve returns + prices for all assets (pool + off) ---
    asset_returns: dict[str, pd.Series] = {}
    asset_prices: dict[str, pd.Series] = {}
    for a in list(pool) + [off_asset]:
        rets, pr = _resolve_asset_returns(a, ffr_daily)
        asset_returns[a] = rets
        asset_prices[a] = pr

    # --- scores per asset in pool ---
    scores_df = _compute_pool_scores(
        pool, score_method, asset_prices, asset_returns, per_asset_vol_gate,
    )

    # --- master gate: SPY > SMA200 (or analogous) ---
    master_prices = load_testfolio_series(master_signal_asset)
    master_gate = sma_gate(master_prices, period=master_signal_period)
    # Reindex to scores_df index (so positions builder has values per row)
    master_gate = master_gate.reindex(scores_df.index).ffill()

    # --- positions ---
    positions = build_positions(scores_df, master_gate, top_k=top_k, off_asset=off_asset)

    # --- align positions × asset returns ---
    asset_returns_df = pd.DataFrame(
        {c: asset_returns[c] for c in positions.columns}
    )
    aligned = positions.join(
        asset_returns_df, lsuffix="_w", rsuffix="_r", how="inner",
    ).dropna()
    if len(aligned) < 252:
        raise ValueError(
            f"Insufficient aligned data after join: {len(aligned)} rows for {name!r}"
        )

    cols = positions.columns.tolist()
    strategy_returns = sum(
        aligned[f"{c}_w"].shift(1) * aligned[f"{c}_r"] for c in cols
    ).dropna()
    equity = (1.0 + strategy_returns).cumprod() * 10_000.0

    # --- metrics per dataset (windowed) with SPY benchmark ---
    spy_full = load_testfolio_series("SPYSIM").dropna()
    metrics_per_dataset: dict[str, dict] = {}
    for ds in datasets:
        win = DATASET_WINDOWS.get(ds)
        if win is None:
            ds_eq, ds_ret, ds_bench = equity, strategy_returns, spy_full
        else:
            start, end = win
            ds_eq = equity[(equity.index >= start) & (equity.index <= end)]
            ds_ret = strategy_returns[(strategy_returns.index >= start) & (strategy_returns.index <= end)]
            ds_bench = spy_full[(spy_full.index >= start) & (spy_full.index <= end)]
        if len(ds_ret) < 252 or len(ds_eq) < 2:
            metrics_per_dataset[ds] = dict(_NAN_METRICS)
        else:
            metrics_per_dataset[ds] = compute_metrics(ds_eq, ds_ret, benchmark_equity=ds_bench)

    # --- gates G2-G7 ---
    g2 = g2_dsr_p_value(strategy_returns, n_trials=max(2, n_trials_local))
    spy_returns_full = spy_full.pct_change().dropna()
    g3 = g3_walk_forward(strategy_returns, benchmark_returns=spy_returns_full)
    g4 = g4_oos_70_30(strategy_returns)
    g5 = g5_fwd_post_2020(strategy_returns)
    g6 = g6_bootstrap_ci(strategy_returns)
    g7 = g7_xlib_cagr_delta(strategy_returns)
    gates = {
        "g1_pbo": float("nan"),
        "g1_pbo_n_combinations": 0,
        "g2_dsr_p_local": float(g2["p_value"]),
        "g2_dsr_p_cumulative": float("nan"),
        "g2_observed_sharpe": float(g2["observed_sharpe"]),
        "g3_wf_windows_pass": int(g3["windows_pass"]),
        "g3_wf_windows_pass_pct_above_benchmark": int(g3["windows_pass_pct_above_benchmark"]),
        "g3_wf_windows_pass_sharpe_positive": int(g3["windows_pass_sharpe_positive"]),
        "g3_wf_n_windows": int(g3["n_windows"]),
        "g3_wf_max_mdd": float(g3["max_mdd"]) if not pd.isna(g3["max_mdd"]) else float("nan"),
        "g3_wf_warmup_used_days": int(g3.get("warmup_used_days", 0)),
        "g3_wf_benchmark_relative": bool(g3.get("benchmark_relative", False)),
        "g4_oos_sharpe": float(g4["oos_sharpe"]),
        "g5_fwd_post2020_sharpe": float(g5["fwd_sharpe"]),
        "g5_fwd_n_obs": int(g5["n_obs_post_2020"]),
        "g6_bootstrap_99_low": float(g6["ci_low_sharpe"]),
        "g7_xlib_cagr_delta": float(g7["delta_pp"] / 100.0),
    }

    crisis = crisis_beats_benchmark(equity, spy_full)
    anchors = {ds: SPY_ANCHOR_SHARPE.get(ds, 0.7) for ds in datasets}
    spy_mdds = {ds: SPY_MDD.get(ds, -0.50) for ds in datasets}
    score_result = score_strategy(metrics_per_dataset, anchors, spy_mdds, gates, crisis)

    # Master gate summary as the "_signal" for plot purposes
    signal_idx = master_gate.reindex(strategy_returns.index).fillna(0).astype(float)

    # Aligned positions + per-asset returns for tax_comparison sub-study reuse.
    asset_returns_aligned = pd.DataFrame(
        {c: aligned[f"{c}_r"] for c in positions.columns}
    ).reindex(strategy_returns.index).dropna()
    positions_aligned = positions.reindex(strategy_returns.index).dropna()

    return {
        "config_name": name,
        "metrics_gross": metrics_per_dataset,
        "metrics_net": {},
        "rolling_pct_beat_spy": {"3y": None, "5y": None, "10y": None},
        "crisis_mdd": {}, "crisis_beats_benchmark": dict(crisis),
        "gates": gates,
        "score_breakdown": score_result,
        "tier_label": score_result["tier_label"],
        "winner_conditions_met": score_result.get("winner_conditions_met", False),
        "pool": list(pool),
        "top_k": top_k,
        "score_method": score_method,
        "_positions": positions_aligned,
        "_asset_returns_aligned": asset_returns_aligned,
        "_strategy_returns": strategy_returns,
        "_equity": equity,
        "_signal": signal_idx,
        "_score_inputs": {
            "metrics": metrics_per_dataset,
            "anchors": anchors,
            "spy_mdds": spy_mdds,
            "crisis": crisis,
        },
    }
