# studies/letf_rotation_hunt/run_iter_t5_extended.py
"""Extended T5 dispatcher with forecast_type and weighting_scheme.

Routes per-config based on optional keys:
  - forecast_type ∈ {"ewmac", "ewmac_carry", "carry_only"} (default "ewmac")
  - weighting_scheme ∈ {"idm", "hrp", "erc"} (default "idm")

When both default, behavior is identical to run_iter_t5._run_single_voltarget_config.
Citation: spec §3.4 (docs/specs/2026-05-08-t5-expansion-design.md).
[systematic_trading, ch.7-12 p.98-202]
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from studies.letf_rotation_hunt import run_iter_t5, signals_carry
from studies.letf_rotation_hunt.data_loader import load_ffr_daily, load_testfolio_series
from studies.letf_rotation_hunt.gates import g1_pbo, g2_dsr_p_value
from studies.letf_rotation_hunt.run_iter_t1 import (
    DATASET_WINDOWS, LETF_TESTFOLIO, SPY_ANCHOR_SHARPE, SPY_MDD,
    _NAN_METRICS, _write_iter_artifacts,
)
from studies.letf_rotation_hunt.run_iter_t5 import (
    _compute_ewmac_composite_forecast, _resolve_asset_returns,
    _run_single_voltarget_config,
)
from studies.letf_rotation_hunt.scoring import (
    compute_metrics, crisis_beats_benchmark, score_strategy,
)
from studies.letf_rotation_hunt.strategies.hrp_weighter import (
    compute_erc_weights, compute_hrp_weights,
)
from studies.letf_rotation_hunt.strategies.vol_targeted import build_positions


def run(config: dict, verdict: dict, out_dir: Path) -> dict:
    """Mirror of run_iter_t5.run with extended config keys."""
    tier = config["tier"]
    if not tier.startswith("T5"):
        raise ValueError(f"run_iter_t5_extended expects T5*, got {tier!r}")

    ffr_daily = load_ffr_daily()
    results: list[dict] = []
    n_trials_local = len(config["configs_tested"])
    n_trials_cumulative = max(
        1,
        int(config.get("cumulative_n_trials_at_iter", 0)) + n_trials_local,
    )

    for cfg in config["configs_tested"]:
        try:
            if _is_extended_config(cfg):
                result = _run_single_extended(
                    cfg, config["datasets"], ffr_daily,
                    n_trials_local=n_trials_local,
                )
            else:
                result = _run_single_voltarget_config(
                    cfg, config["datasets"], ffr_daily,
                    n_trials_local=n_trials_local,
                )
            results.append(result)
        except Exception as exc:
            results.append({
                "config_name": cfg.get("name", "unknown"),
                "error": str(exc),
                "metrics_gross": {}, "metrics_net": {},
                "score_breakdown": {}, "tier_label": "ERROR",
            })

    valid = [r for r in results if "error" not in r]
    per_cfg_returns = {
        r["config_name"]: r["_strategy_returns"]
        for r in valid if "_strategy_returns" in r
    }
    g1_result = g1_pbo(per_cfg_returns) if per_cfg_returns else {
        "pbo": float("nan"), "n_combinations": 0, "pass_gate": True,
    }
    for r in valid:
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

    if not valid:
        verdict.update({"best_config": "", "best_score": 0.0, "best_tier": "FAIL"})
    else:
        best = max(
            valid,
            key=lambda r: r["metrics_gross"].get("lh_56y", {}).get("sharpe", -999),
        )
        verdict.update({
            "best_config": best["config_name"],
            "best_score": best.get("score_breakdown", {}).get("total", 0.0),
            "best_tier": best.get("tier_label", "FAIL"),
        })

    verdict["kill_rule_status"] = run_iter_t5._evaluate_kill_t4_t5(valid)
    verdict["advance_to_next_tier"] = False

    if valid:
        _write_iter_artifacts(config, verdict, valid, out_dir, verdict["kill_rule_status"])

    for r in valid:
        for k in ("_strategy_returns", "_equity", "_signal", "_positions",
                  "_asset_returns_aligned"):
            r.pop(k, None)

    verdict["results"] = results
    return verdict


def _is_extended_config(cfg: dict) -> bool:
    return ("forecast_type" in cfg) or ("weighting_scheme" in cfg)


def _run_single_extended(
    cfg: dict, datasets: list[str], ffr_daily: pd.Series, n_trials_local: int = 1,
) -> dict:
    forecast_type = cfg.get("forecast_type", "ewmac")
    weighting_scheme = cfg.get("weighting_scheme", "idm")
    name = cfg["name"]
    pool = cfg["pool"]
    off_asset = cfg["off_asset"]
    sigma_target = float(cfg.get("sigma_target", 0.25))
    idm = float(cfg.get("idm", 1.0))
    position_inertia = float(cfg.get("position_inertia", 0.10))
    vol_window = int(cfg.get("vol_window", 21))

    asset_returns: dict[str, pd.Series] = {}
    asset_prices: dict[str, pd.Series] = {}
    for a in list(pool) + [off_asset]:
        rets, pr = _resolve_asset_returns(a, ffr_daily)
        asset_returns[a] = rets
        asset_prices[a] = pr

    forecasts_dict: dict[str, pd.Series] = {}
    vols_dict: dict[str, pd.Series] = {}
    for a in pool:
        forecasts_dict[a] = _compute_forecast(
            forecast_type, a, asset_prices[a], ffr_daily,
        )
        vols_dict[a] = asset_returns[a].rolling(window=vol_window, min_periods=vol_window).std()

    forecasts_df = pd.DataFrame(forecasts_dict)
    vols_df = pd.DataFrame(vols_dict)
    common_idx = forecasts_df.dropna(how="all").index.intersection(
        vols_df.dropna(how="all").index
    )
    forecasts_df = forecasts_df.loc[common_idx]
    vols_df = vols_df.loc[common_idx]

    external_weights = _compute_external_weights(
        weighting_scheme, asset_returns, pool, common_idx,
    )

    positions = build_positions(
        forecasts=forecasts_df, vol_per_asset=vols_df,
        sigma_target=sigma_target, idm=idm,
        position_inertia=position_inertia, off_asset=off_asset,
        external_weights=external_weights,
    )

    # Reuse the rest of run_iter_t5 single-config metrics/gates pipeline
    # by manually replicating the scoring tail (cannot import as it lives
    # inline in _run_single_voltarget_config). The simplest reliable path:
    # delegate to the baseline _run_single_voltarget_config helper for
    # metrics, but pass our pre-built positions via a thin shim.
    return _finalize_extended(
        cfg, positions, asset_returns, datasets, n_trials_local, name, pool,
        sigma_target, idm,
    )


def _compute_forecast(
    forecast_type: str, asset: str, prices: pd.Series, ffr_daily: pd.Series,
) -> pd.Series:
    if forecast_type == "ewmac":
        return _compute_ewmac_composite_forecast(prices, fdm=1.41)
    if forecast_type == "carry_only":
        return signals_carry.compute_carry_forecast(asset, prices, ffr_daily, fdm=1.0)
    if forecast_type == "ewmac_carry":
        ewmac = _compute_ewmac_composite_forecast(prices, fdm=1.0)
        carry = signals_carry.compute_carry_forecast(asset, prices, ffr_daily, fdm=1.0)
        return signals_carry.compose_ewmac_carry(ewmac, carry, fdm=1.41)
    raise ValueError(f"unknown forecast_type {forecast_type!r}")


def _compute_external_weights(
    scheme: str, asset_returns: dict[str, pd.Series], pool: list[str],
    common_idx: pd.Index,
) -> pd.DataFrame | None:
    if scheme == "idm":
        return None
    rets = pd.DataFrame({a: asset_returns[a] for a in pool}).reindex(common_idx).dropna()
    if scheme == "hrp":
        return compute_hrp_weights(rets)
    if scheme == "erc":
        return compute_erc_weights(rets)
    raise ValueError(f"unknown weighting_scheme {scheme!r}")


def _finalize_extended(
    cfg, positions, asset_returns, datasets, n_trials_local, name, pool,
    sigma_target, idm,
):
    """Tail of metrics/gates/scoring; replicates the latter half of
    run_iter_t5._run_single_voltarget_config for our pre-built positions.
    """
    from studies.letf_rotation_hunt.gates import (
        g3_walk_forward, g4_oos_70_30, g5_fwd_post_2020,
        g6_bootstrap_ci, g7_xlib_cagr_delta,
    )

    asset_returns_df = pd.DataFrame(
        {c: asset_returns[c] for c in positions.columns}
    )
    aligned = positions.join(
        asset_returns_df, lsuffix="_w", rsuffix="_r", how="inner",
    ).dropna()
    if len(aligned) < 252:
        raise ValueError(f"Insufficient aligned data: {len(aligned)} for {name!r}")

    cols = positions.columns.tolist()
    strategy_returns = sum(
        aligned[f"{c}_w"].shift(1) * aligned[f"{c}_r"] for c in cols
    ).dropna()
    equity = (1.0 + strategy_returns).cumprod() * 10_000.0

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

    g2 = g2_dsr_p_value(strategy_returns, n_trials=max(2, n_trials_local))
    spy_returns_full = spy_full.pct_change().dropna()
    g3 = g3_walk_forward(strategy_returns, benchmark_returns=spy_returns_full)
    g4 = g4_oos_70_30(strategy_returns)
    g5 = g5_fwd_post_2020(strategy_returns)
    g6 = g6_bootstrap_ci(strategy_returns)
    g7 = g7_xlib_cagr_delta(strategy_returns)
    gates = {
        "g1_pbo": float("nan"), "g1_pbo_n_combinations": 0,
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
    pool_weights = positions[pool].sum(axis=1)
    signal_idx = pool_weights.reindex(strategy_returns.index).fillna(0).astype(float)
    asset_returns_aligned = pd.DataFrame(
        {c: aligned[f"{c}_r"] for c in positions.columns}
    ).reindex(strategy_returns.index).dropna()
    positions_aligned = positions.reindex(strategy_returns.index).dropna()
    return {
        "config_name": name,
        "metrics_gross": metrics_per_dataset, "metrics_net": {},
        "rolling_pct_beat_spy": {"3y": None, "5y": None, "10y": None},
        "crisis_mdd": {}, "crisis_beats_benchmark": dict(crisis),
        "gates": gates,
        "score_breakdown": score_result,
        "tier_label": score_result["tier_label"],
        "winner_conditions_met": score_result.get("winner_conditions_met", False),
        "pool": list(pool), "sigma_target": sigma_target, "idm": idm,
        "_positions": positions_aligned,
        "_asset_returns_aligned": asset_returns_aligned,
        "_strategy_returns": strategy_returns,
        "_equity": equity, "_signal": signal_idx,
        "_score_inputs": {
            "metrics": metrics_per_dataset, "anchors": anchors,
            "spy_mdds": spy_mdds, "crisis": crisis,
        },
    }
