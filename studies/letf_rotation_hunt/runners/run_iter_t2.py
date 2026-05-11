"""T2 (HFEA-binary basket) tier dispatcher per spec §2.3.

Dispatches T2a (HFEA classic), T2b (weight sweep), T2c (HFEA-NDX), T2d
(no-decay-bond), T2e (HFEA-trinity), T2f (half-off explicit). Each config
specifies an on_basket dict (asset → weight) plus off_asset/off_mode +
signal driver.

Reuses run_iter_t1's gates / scoring / artifact-writing pipeline; only the
strategy is different (basket via hfea_binary.build_positions instead of
single_letf_gayed.build_positions).

Citations
---------
* Carlson HFEA capital-efficient stacking: [risk_parity, ch.5, p.10]
* LETF daily-return formula (FFR-aware): [leverage_for_the_long_run, p.16, footnote 22-23]
* Anti-curve-fit T1→T2 threshold: spec §3.4 (T2-best Sharpe > T1-best + 0.05)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_ffr_daily, load_testfolio_series
from studies.letf_rotation_hunt.core.gates import (
    g1_pbo,
    g2_dsr_p_value,
    g3_walk_forward,
    g4_oos_70_30,
    g5_fwd_post_2020,
    g6_bootstrap_ci,
    g7_xlib_cagr_delta,
)
from studies.letf_rotation_hunt.runners.run_iter_t1 import (
    DATASET_WINDOWS,
    LETF_TESTFOLIO,
    SPY_ANCHOR_SHARPE,
    SPY_MDD,
    _NAN_METRICS,
    _write_iter_artifacts,
)
from studies.letf_rotation_hunt.core.scoring import (
    compute_metrics, crisis_beats_benchmark, score_strategy,
)
from studies.letf_rotation_hunt.core.signals import ema_gate, sma_gate
from studies.letf_rotation_hunt.core.strategies.hfea_binary import build_positions
from studies.letf_rotation_hunt.core.synths import letf_synth_by_ticker

# T1-best Sharpe (lh_56y) for KILL T1→T2 threshold per spec §3.4.
# Source: iter 003 T1c qld_sma200_off_zroz Sharpe 0.752.
_T1_BEST_SHARPE_LH56Y = 0.752
_KILL_T1_T2_THRESHOLD = _T1_BEST_SHARPE_LH56Y + 0.05  # = 0.802


def run(config: dict, verdict: dict, out_dir: Path) -> dict:
    """Run T2 sub-fase iteration (a/b/c/d/e/f).

    Parameters
    ----------
    config:
        Loaded iter config YAML. Tier must be T2a-T2f.
    verdict:
        Scaffold verdict to fill.
    out_dir:
        Output directory.

    Returns
    -------
    dict
        Updated verdict (schema-compliant).
    """
    tier = config["tier"]
    if not tier.startswith("T2"):
        raise ValueError(f"run_iter_t2 expects T2*, got {tier!r}")

    ffr_daily = load_ffr_daily()
    results: list[dict] = []
    n_trials_local = len(config["configs_tested"])
    n_trials_cumulative = max(
        1,
        int(config.get("cumulative_n_trials_at_iter", 0)) + n_trials_local,
    )

    for cfg in config["configs_tested"]:
        try:
            result = _run_single_basket_config(
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

    # Cross-config G1 PBO + G2 cumulative + re-score
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

    # Best config by Sharpe on lh_56y
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

    # KILL T1→T2 evaluation per spec §3.4.
    kill_status = _evaluate_kill_t1_t2(valid_results)
    verdict["kill_rule_status"] = kill_status
    verdict["advance_to_next_tier"] = True  # informational; loop continues

    # Write artifacts BEFORE stripping internal keys
    if valid_results:
        _write_iter_artifacts(config, verdict, valid_results, out_dir, kill_status)

    # Strip internal-only fields
    for r in valid_results:
        r.pop("_strategy_returns", None)
        r.pop("_equity", None)
        r.pop("_signal", None)

    verdict["results"] = results
    return verdict


def _evaluate_kill_t1_t2(valid_results: list[dict]) -> str:
    """KILL T1→T2: T2-best Sharpe (lh_56y) vs T1-best + 0.05 threshold.

    Returns "PASS" / "FIRES" / "N/A". Informational only — loop always
    continues per spec §3.4. PASS means basket adds value over single-LETF
    rotation; FIRES means basket is at-or-below noise band of T1.
    """
    if not valid_results:
        return "N/A"
    best_sharpe = max(
        r["metrics_gross"].get("lh_56y", {}).get("sharpe", float("-inf"))
        for r in valid_results
    )
    return "PASS" if best_sharpe >= _KILL_T1_T2_THRESHOLD else "FIRES"


def _resolve_asset_returns(
    asset: str, ffr_daily: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    """Load (returns, prices) for one asset using LETF_TESTFOLIO mapping.

    Returns the daily returns Series + the underlying price Series. Prices
    are the testfolio cache equity-curve (so they can drive the SMA/EMA
    signal when this asset is the equity component).
    """
    if asset not in LETF_TESTFOLIO:
        raise ValueError(
            f"No testfolio mapping for asset={asset!r}. "
            f"Known: {sorted(LETF_TESTFOLIO)}"
        )
    tf_ticker, is_direct = LETF_TESTFOLIO[asset]
    series = load_testfolio_series(tf_ticker)
    if is_direct:
        returns = series.pct_change().dropna()
    else:
        underlying_returns = series.pct_change().dropna()
        returns = letf_synth_by_ticker(asset, underlying_returns, ffr_daily)
    return returns, series


def _run_single_basket_config(
    cfg: dict, datasets: list[str], ffr_daily: pd.Series, n_trials_local: int = 1,
) -> dict:
    """Run a single HFEA-binary basket config.

    Config dict keys:
      - name (str)
      - on_basket (dict[str, float]): asset → weight, sums to 1.0
      - off_asset (str): cash-equivalent or alternative
      - off_mode (str, optional): "full_off" (default) | "half_off"
      - bond_sleeve_assets (list[str], optional): required if off_mode="half_off"
      - signal_asset (str): which on_basket asset drives the signal
        (typically the equity LETF; signal computed on its underlying)
      - signal (str): "sma" | "ema"
      - period (int): lookback in trading days
    """
    name = cfg["name"]
    on_basket = cfg["on_basket"]
    off_asset = cfg["off_asset"]
    off_mode = cfg.get("off_mode", "full_off")
    bond_sleeve = cfg.get("bond_sleeve_assets")
    signal_asset = cfg["signal_asset"]
    signal_name = cfg["signal"]
    period = int(cfg.get("period", 200))

    if abs(sum(on_basket.values()) - 1.0) > 1e-6:
        raise ValueError(
            f"on_basket weights must sum to 1.0 in {name!r}, got "
            f"{sum(on_basket.values()):.6f}"
        )

    # --- resolve returns for every asset (basket + off) ---
    asset_returns_dict: dict[str, pd.Series] = {}
    for asset in list(on_basket.keys()):
        rets, _prices = _resolve_asset_returns(asset, ffr_daily)
        asset_returns_dict[asset] = rets
    if off_asset not in asset_returns_dict:
        rets, _prices = _resolve_asset_returns(off_asset, ffr_daily)
        asset_returns_dict[off_asset] = rets

    # --- signal: SMA/EMA on the underlying of signal_asset ---
    # Per [leverage_for_the_long_run, p.13]: signal computed on underlying
    # (e.g. SPY for UPRO) not on the LETF itself.
    if signal_asset not in LETF_TESTFOLIO:
        raise ValueError(f"signal_asset {signal_asset!r} not in LETF_TESTFOLIO")
    sa_tf_ticker, _ = LETF_TESTFOLIO[signal_asset]
    underlying_prices = load_testfolio_series(sa_tf_ticker)
    if signal_name == "sma":
        signal = sma_gate(underlying_prices, period=period)
    elif signal_name == "ema":
        signal = ema_gate(underlying_prices, period=period)
    else:
        raise ValueError(f"Unknown signal: {signal_name!r}")

    # --- positions (HFEA binary) ---
    positions = build_positions(
        signal=signal,
        on_basket=on_basket,
        off_asset=off_asset,
        off_mode=off_mode,
        bond_sleeve_assets=bond_sleeve,
    )

    # --- align positions with asset returns ---
    asset_returns_df = pd.DataFrame(asset_returns_dict)
    aligned = positions.join(
        asset_returns_df, lsuffix="_w", rsuffix="_r", how="inner",
    ).dropna()
    if len(aligned) < 252:
        raise ValueError(
            f"Insufficient aligned data after join: {len(aligned)} rows "
            f"(need >= 252) for {name!r}"
        )

    # Strategy returns: sum over assets of weight[t-1] * return[t]
    cols = positions.columns.tolist()
    strategy_returns = sum(
        aligned[f"{c}_w"].shift(1) * aligned[f"{c}_r"] for c in cols
    ).dropna()
    equity = (1.0 + strategy_returns).cumprod() * 10_000.0

    # --- metrics per dataset (windowed) ---
    # SPY benchmark for underwater-vs-bench scoring (v2 §3.2)
    spy_full = load_testfolio_series("SPYSIM").dropna()
    metrics_per_dataset: dict[str, dict] = {}
    for ds in datasets:
        win = DATASET_WINDOWS.get(ds)
        if win is None:
            ds_eq, ds_ret = equity, strategy_returns
            ds_bench = spy_full
        else:
            start, end = win
            ds_eq = equity[(equity.index >= start) & (equity.index <= end)]
            ds_ret = strategy_returns[(strategy_returns.index >= start) & (strategy_returns.index <= end)]
            ds_bench = spy_full[(spy_full.index >= start) & (spy_full.index <= end)]
        if len(ds_ret) < 252 or len(ds_eq) < 2:
            metrics_per_dataset[ds] = dict(_NAN_METRICS)
        else:
            metrics_per_dataset[ds] = compute_metrics(ds_eq, ds_ret, benchmark_equity=ds_bench)

    # --- gates G2-G7 (G1 + G2-cumulative populated cross-config in run()) ---
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
        "_strategy_returns": strategy_returns,
        "_equity": equity,
        "_signal": signal.reindex(strategy_returns.index).fillna(0).astype(float),
        "_score_inputs": {
            "metrics": metrics_per_dataset,
            "anchors": anchors,
            "spy_mdds": spy_mdds,
            "crisis": crisis,
        },
    }
