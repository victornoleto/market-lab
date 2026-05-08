"""T3 (Composite signal) tier dispatcher per spec §2.4.

Inheritance: T1c canonical (`qld_sma200_off_zroz`) per spec §3.4 fallback
(KILL T1→T2 fired in iter 010). All T3 configs use QLD as on-asset and
ZROZ as off-asset; only the SIGNAL composition varies.

Sub-phases (one config per signal_type unless noted):
  - T3a: SMA200 AND realized-vol < 40%             [leverage_for_the_long_run, p.5-6]
  - T3b: VIX-managed continuous weight (via VXX)   [paper.bozovic_2024_vix_managed]
  - T3c: SMA200 AND AR(1)_30d > 0                  [paper.hsieh_2025_letf_compounding]
  - T3d: Vote-of-K (K=2,3,4) over {SMA200, vol, AR(1), SMA50}   composite
  - T3e (optional): HMM 2-state regime classifier  [knowledge/indicators/regime_hmm]

Anti-curve-fit threshold T2→T3 per spec §3.4 + §3.4 inheritance fallback:
T3-best Sharpe must exceed T1c-best (0.752) + 0.05 = 0.802 to claim T3 winner
(since KILL T1→T2 fired, T1c is the active reference).

Reuses run_iter_t1's gates / scoring / artifact-writing pipeline.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.data_loader import (
    load_ffr_daily, load_testfolio_series, load_tiingo_real_etf,
)
from studies.letf_rotation_hunt.gates import (
    g1_pbo, g2_dsr_p_value, g3_walk_forward, g4_oos_70_30,
    g5_fwd_post_2020, g6_bootstrap_ci, g7_xlib_cagr_delta,
)
from studies.letf_rotation_hunt.run_iter_t1 import (
    DATASET_WINDOWS, LETF_TESTFOLIO, SPY_ANCHOR_SHARPE, SPY_MDD,
    _NAN_METRICS, _write_iter_artifacts,
)
from studies.letf_rotation_hunt.scoring import (
    compute_metrics, crisis_beats_benchmark, score_strategy,
)
from studies.letf_rotation_hunt.signals import (
    ar1_coefficient, ema_gate, hmm_regime_gate, realized_vol_gate,
    sma_gate, vix_scaling, vote_of_k,
)
from studies.letf_rotation_hunt.strategies.composite_signal import build_positions
from studies.letf_rotation_hunt.synths import letf_synth_by_ticker

# T1c-best Sharpe (lh_56y) for KILL T2→T3 threshold per spec §3.4 + fallback
_T1_BEST_SHARPE_LH56Y = 0.752
_KILL_T2_T3_THRESHOLD = _T1_BEST_SHARPE_LH56Y + 0.05  # = 0.802


def run(config: dict, verdict: dict, out_dir: Path) -> dict:
    """Run T3 sub-fase iteration."""
    tier = config["tier"]
    if not tier.startswith("T3"):
        raise ValueError(f"run_iter_t3 expects T3*, got {tier!r}")

    ffr_daily = load_ffr_daily()
    results: list[dict] = []
    n_trials_local = len(config["configs_tested"])
    n_trials_cumulative = max(
        1,
        int(config.get("cumulative_n_trials_at_iter", 0)) + n_trials_local,
    )

    for cfg in config["configs_tested"]:
        try:
            result = _run_single_composite_config(
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

    kill_status = _evaluate_kill_t2_t3(valid_results)
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


def _evaluate_kill_t2_t3(valid_results: list[dict]) -> str:
    """KILL T2→T3 (with T2 fallback): T3-best Sharpe vs T1c+0.05 = 0.802."""
    if not valid_results:
        return "N/A"
    best_sharpe = max(
        r["metrics_gross"].get("lh_56y", {}).get("sharpe", float("-inf"))
        for r in valid_results
    )
    return "PASS" if best_sharpe >= _KILL_T2_T3_THRESHOLD else "FIRES"


def _resolve_asset_returns(asset: str, ffr_daily: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Load (returns, prices) for one asset (mirrors run_iter_t2)."""
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


def _compute_composite_signal(
    cfg: dict, on_asset: str, ffr_daily: pd.Series,
) -> tuple[pd.Series, str]:
    """Compute the composite signal/weight per config.

    Returns (signal_or_weight_series, signal_description). The series is in
    [0, 1]: binary {0, 1} for gate-style signals; continuous for vix_managed.
    NaN propagated during warmup.
    """
    signal_type = cfg["signal_type"]

    # Underlying prices for the on-asset (drives SMA/EMA/AR1)
    on_tf_ticker, _ = LETF_TESTFOLIO[on_asset]
    underlying_prices = load_testfolio_series(on_tf_ticker)
    underlying_returns = underlying_prices.pct_change().dropna()

    if signal_type == "sma_vol_gate":
        period = int(cfg.get("period", 200))
        vol_window = int(cfg.get("vol_window", 21))
        vol_threshold = float(cfg.get("vol_threshold", 0.40))
        sma = sma_gate(underlying_prices, period=period)
        vol = realized_vol_gate(underlying_returns, window=vol_window, threshold=vol_threshold)
        signal = ((sma == 1.0) & (vol == 1.0)).astype(float)
        signal[sma.isna() | vol.isna()] = np.nan
        return signal, f"SMA{period} AND vol_{vol_window}d < {vol_threshold:.0%}"

    if signal_type == "sma_ar1_gate":
        period = int(cfg.get("period", 200))
        ar1_window = int(cfg.get("ar1_window", 30))
        sma = sma_gate(underlying_prices, period=period)
        ar1 = ar1_coefficient(underlying_returns, window=ar1_window)
        ar1_gate = (ar1 > 0).astype(float)
        ar1_gate[ar1.isna()] = np.nan
        signal = ((sma == 1.0) & (ar1_gate == 1.0)).astype(float)
        signal[sma.isna() | ar1_gate.isna()] = np.nan
        return signal, f"SMA{period} AND AR(1)_{ar1_window}d > 0"

    if signal_type == "vote_of_k":
        # T3d-extended (iter 022): config-driven signal-subset params for
        # statistical-power grid sweep over Vote-of-K. Defaults preserve
        # the original T3d K∈{2,3,4} behavior (4 signals: SMA200, SMA50,
        # vol_21d<40%, AR(1)_30d>0).
        k = int(cfg["k"])
        sma_long = int(cfg.get("sma_long_period", 200))
        sma_short = int(cfg.get("sma_short_period", 50))
        vol_window = int(cfg.get("vol_window", 21))
        vol_threshold = float(cfg.get("vol_threshold", 0.40))
        ar1_window = int(cfg.get("ar1_window", 30))
        use_ema = bool(cfg.get("use_ema", False))
        # Threshold buffer params (default 0 → canonical strict-crossover behavior)
        sma_long_buf_on  = float(cfg.get("sma_long_buffer_on",  0.0))
        sma_long_buf_off = float(cfg.get("sma_long_buffer_off", 0.0))
        sma_short_buf_on  = float(cfg.get("sma_short_buffer_on",  0.0))
        sma_short_buf_off = float(cfg.get("sma_short_buffer_off", 0.0))
        ar1_buf = float(cfg.get("ar1_buffer", 0.0))

        any_sma_buffer = (
            sma_long_buf_on > 0 or sma_long_buf_off > 0
            or sma_short_buf_on > 0 or sma_short_buf_off > 0
        )
        if any_sma_buffer and use_ema:
            raise ValueError(
                "EMA + SMA buffer not supported (use_ema=True with non-zero buffer)"
            )
        if any_sma_buffer:
            from studies.letf_rotation_hunt.threshold_sweep.threshold_signals import (
                sma_gate_with_buffer,
            )
            long_g = sma_gate_with_buffer(
                underlying_prices, period=sma_long,
                on_threshold=sma_long_buf_on, off_threshold=sma_long_buf_off,
            )
            short_g = sma_gate_with_buffer(
                underlying_prices, period=sma_short,
                on_threshold=sma_short_buf_on, off_threshold=sma_short_buf_off,
            )
        else:
            gate_fn = ema_gate if use_ema else sma_gate
            long_g = gate_fn(underlying_prices, period=sma_long)
            short_g = gate_fn(underlying_prices, period=sma_short)

        vol = realized_vol_gate(
            underlying_returns, window=vol_window, threshold=vol_threshold,
        )

        if ar1_buf > 0:
            from studies.letf_rotation_hunt.threshold_sweep.threshold_signals import (
                ar1_gate_with_buffer,
            )
            ar1_gate = ar1_gate_with_buffer(
                underlying_returns, window=ar1_window, threshold=ar1_buf,
            )
        else:
            ar1 = ar1_coefficient(underlying_returns, window=ar1_window)
            ar1_gate = (ar1 > 0).astype(float)
            ar1_gate[ar1.isna()] = np.nan

        signal = vote_of_k([long_g, short_g, vol, ar1_gate], k=k)
        prefix = "EMA" if use_ema else "SMA"
        buf_suffix = ""
        if any_sma_buffer:
            buf_suffix = f" [smabuf_on={sma_long_buf_on}/off={sma_long_buf_off}]"
        if ar1_buf > 0:
            buf_suffix += f" [ar1>{ar1_buf}]"
        desc = (
            f"Vote-of-{k} of {{{prefix}{sma_long}, {prefix}{sma_short}, "
            f"vol_{vol_window}d<{vol_threshold:.0%}, AR(1)_{ar1_window}d>0}}"
            f"{buf_suffix}"
        )
        return signal, desc

    if signal_type == "vix_managed":
        # VIX proxy via VXX (Tiingo). VXX inception 2009-01-30 — pre-2009 NaN.
        vxx_path_exists = True
        try:
            vxx = load_tiingo_real_etf("VXX")
        except FileNotFoundError:
            vxx_path_exists = False
        if not vxx_path_exists:
            raise RuntimeError("VXX.parquet not in Tiingo cache for VIX-managed config")
        baseline = int(cfg.get("vix_baseline_days", 252))
        prev = int(cfg.get("vix_prev_days", 21))
        weight = vix_scaling(vxx, lookback_baseline=baseline, lookback_prev_month=prev)
        # Reindex to underlying_prices index, forward-fill (VXX trading days
        # may differ slightly); pre-VXX-inception → NaN preserved
        weight = weight.reindex(underlying_prices.index).ffill()
        return weight, f"VXX scaling baseline={baseline}d, prev={prev}d"

    if signal_type == "hmm":
        n_states = int(cfg.get("n_states", 2))
        sticky = int(cfg.get("sticky_days", 3))
        signal = hmm_regime_gate(
            underlying_returns, n_states=n_states, sticky_days=sticky,
        )
        return signal, f"HMM {n_states}-state, sticky={sticky}d"

    raise ValueError(f"Unknown signal_type: {signal_type!r}")


def _run_single_composite_config(
    cfg: dict, datasets: list[str], ffr_daily: pd.Series, n_trials_local: int = 1,
) -> dict:
    """Run one T3 composite-signal config.

    Config dict keys:
      - name (str)
      - on_asset (str) — typically "QLD" inherited from T1c
      - off_asset (str) — typically "ZROZ" inherited from T1c
      - signal_type (str) — one of: sma_vol_gate, sma_ar1_gate, vote_of_k,
        vix_managed, hmm
      - signal-specific params (period, vol_window, k, etc.)
    """
    name = cfg["name"]
    on_asset = cfg["on_asset"]
    off_asset = cfg["off_asset"]

    on_returns, _ = _resolve_asset_returns(on_asset, ffr_daily)
    off_returns, _ = _resolve_asset_returns(off_asset, ffr_daily)

    signal_or_weight, signal_desc = _compute_composite_signal(cfg, on_asset, ffr_daily)

    # composite_signal accepts continuous weight ∈ [0, 1]
    on_basket = {on_asset: 1.0}
    positions = build_positions(
        weight=signal_or_weight, on_basket=on_basket, off_asset=off_asset,
    )

    asset_returns_df = pd.DataFrame({on_asset: on_returns, off_asset: off_returns})
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

    # Per-dataset metrics with SPY benchmark (scoring v2)
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

    # Real gates G2-G7
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

    # Reindex signal_or_weight to strategy_returns index for plot consistency
    signal_idx = signal_or_weight.reindex(strategy_returns.index).fillna(0).astype(float)

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
        "signal_description": signal_desc,
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
