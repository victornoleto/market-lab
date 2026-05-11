"""T5 (Carver vol-target) tier dispatcher per spec §2.6.

Continuous position sizing per Carver `[systematic_trading, ch.7-12]`:
EWMAC forecast → forecast / 10 × σ_target / σ_realized × IDM.
Position inertia 10%; long-only (negative forecasts → 0); cash residual.

Sub-phases:
  - T5a: single-asset QLD, EWMAC(16,64)+(64,256) composite, σ_target=0.25,
    IDM=1.0 (single-asset → no diversification multiplier)
  - T5c: multi-asset {UPRO, QLD, UGL, TMF}, same EWMAC, IDM=2.5 (max per
    Carver [p.170-171])

Skipped:
  - T5b carry forecast (requires yield-curve data — out of scope for now)
  - T5d HRP weighting (optional per spec §2.6)

Inheritance: T3d K=2 canonical (Sharpe 0.853) per spec §3.4 fallback.
Threshold T4→T5 unchanged at 0.903 (T4 fired KILL T3→T4).

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
from studies.letf_rotation_hunt.core.signals import ewmac_forecast
from studies.letf_rotation_hunt.core.strategies.vol_targeted import build_positions
from studies.letf_rotation_hunt.core.synths import letf_synth_by_ticker

_T3_BEST_SHARPE_LH56Y = 0.853
_KILL_T4_T5_THRESHOLD = _T3_BEST_SHARPE_LH56Y + 0.05  # = 0.903


def run(config: dict, verdict: dict, out_dir: Path) -> dict:
    tier = config["tier"]
    if not tier.startswith("T5"):
        raise ValueError(f"run_iter_t5 expects T5*, got {tier!r}")

    ffr_daily = load_ffr_daily()
    results: list[dict] = []
    n_trials_local = len(config["configs_tested"])
    n_trials_cumulative = max(
        1,
        int(config.get("cumulative_n_trials_at_iter", 0)) + n_trials_local,
    )

    for cfg in config["configs_tested"]:
        try:
            result = _run_single_voltarget_config(
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

    kill_status = _evaluate_kill_t4_t5(valid_results)
    verdict["kill_rule_status"] = kill_status
    verdict["advance_to_next_tier"] = False  # T5 is final tier; no advance

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


def _evaluate_kill_t4_t5(valid_results: list[dict]) -> str:
    """KILL T4→T5: T5-best Sharpe vs T3-best+0.05 = 0.903 (per §3.4 §2.6 +0.10
    threshold, but using +0.05 since T4 fired KILL — fallback)."""
    if not valid_results:
        return "N/A"
    best_sharpe = max(
        r["metrics_gross"].get("lh_56y", {}).get("sharpe", float("-inf"))
        for r in valid_results
    )
    return "PASS" if best_sharpe >= _KILL_T4_T5_THRESHOLD else "FIRES"


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


def _compute_ewmac_composite_forecast(
    prices: pd.Series, fdm: float = 1.41,
) -> pd.Series:
    """Composite EWMAC forecast averaged across (16,64) and (64,256) windows.

    Per Carver `[systematic_trading, ch.8 p.156]`: FDM (forecast diversification
    multiplier) for 2-window EWMAC composite is ~1.41 (Table 49 [p.285]).
    Composite cap retained at ±20.
    """
    f1 = ewmac_forecast(prices, lfast=16, lslow=64, scalar=3.75, cap=20.0)
    f2 = ewmac_forecast(prices, lfast=64, lslow=256, scalar=1.91, cap=20.0)
    composite = (f1 + f2) / 2.0 * fdm
    return composite.clip(-20.0, 20.0)


def _run_single_voltarget_config(
    cfg: dict, datasets: list[str], ffr_daily: pd.Series, n_trials_local: int = 1,
) -> dict:
    """Run one T5 Carver vol-target config.

    Config dict keys:
      - name (str)
      - pool (list[str]) — single or multi-asset universe
      - off_asset (str) — cash residual ticker
      - sigma_target (float) — annual portfolio vol target
      - idm (float) — instrument diversification multiplier (≤2.5)
      - position_inertia (float) — rebalance threshold
      - vol_window (int, default 21) — rolling daily-vol window for sizing
      - fdm (float, default 1.41) — forecast diversification multiplier
    """
    name = cfg["name"]
    pool = cfg["pool"]
    off_asset = cfg["off_asset"]
    sigma_target = float(cfg.get("sigma_target", 0.25))
    idm = float(cfg.get("idm", 1.0))
    position_inertia = float(cfg.get("position_inertia", 0.10))
    vol_window = int(cfg.get("vol_window", 21))
    fdm = float(cfg.get("fdm", 1.41))

    # --- resolve returns + prices for all assets (pool + off) ---
    asset_returns: dict[str, pd.Series] = {}
    asset_prices: dict[str, pd.Series] = {}
    for a in list(pool) + [off_asset]:
        rets, pr = _resolve_asset_returns(a, ffr_daily)
        asset_returns[a] = rets
        asset_prices[a] = pr

    # --- forecasts per asset ---
    forecasts_dict: dict[str, pd.Series] = {}
    vols_dict: dict[str, pd.Series] = {}
    for a in pool:
        f = _compute_ewmac_composite_forecast(asset_prices[a], fdm=fdm)
        forecasts_dict[a] = f
        # Daily realized vol on returns (decimal)
        vols_dict[a] = asset_returns[a].rolling(window=vol_window, min_periods=vol_window).std()

    forecasts_df = pd.DataFrame(forecasts_dict)
    vols_df = pd.DataFrame(vols_dict)

    # Align on common dates
    common_idx = forecasts_df.dropna(how="all").index.intersection(
        vols_df.dropna(how="all").index
    )
    forecasts_df = forecasts_df.loc[common_idx]
    vols_df = vols_df.loc[common_idx]

    # --- positions via Carver vol-target ---
    positions = build_positions(
        forecasts=forecasts_df, vol_per_asset=vols_df,
        sigma_target=sigma_target, idm=idm,
        position_inertia=position_inertia, off_asset=off_asset,
    )

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

    # Total exposure = sum of pool weights (excluding off) — proxy for "% time risk-on"
    pool_weights = positions[pool].sum(axis=1)
    signal_idx = pool_weights.reindex(strategy_returns.index).fillna(0).astype(float)

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
        "sigma_target": sigma_target,
        "idm": idm,
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
