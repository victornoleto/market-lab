"""LRS Phase 4 mandate validation gates (thin wrappers over the canonical core).

Research-only / diagnostic. Each gate wraps the canonical
``market_lab.backtest.validation`` implementations and applies the mandate §5
hard-block thresholds (PBO < 0.5, DSR p < 0.05, walk-forward >= 6/8, single-block
OOS, FWD stress, bootstrap 99.9% CI low > 0, cross-lib +/-3pp CAGR). The trend
strategy is the LRS leveraged-rotation after-tax daily returns series; CAGR/MDD
stay warning-only tiers and are NOT gates `[advances_fin_ml, p.208-211]`.

This module imports ONLY the canonical core package (no ``studies/`` import), so
``lrs/`` stays self-contained from ``studies/`` while reusing the blessed
statistics `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from market_lab.backtest.validation import (
    dsr,
    pbo,
    sharpe_annualized,
    walk_forward_gate,
    walk_forward_splits,
)
from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades

TRADING_DAYS = 252


def _ann_sharpe(returns: np.ndarray) -> float:
    arr = np.asarray(returns, dtype=float)
    sd = arr.std(ddof=0)
    if sd <= 1e-12:
        return 0.0
    return float(arr.mean() / sd * np.sqrt(TRADING_DAYS))


def _cagr_pandas(returns: pd.Series) -> float:
    equity = (1.0 + returns.astype(float)).cumprod()
    years = len(returns) / TRADING_DAYS
    if years <= 0:
        return float("nan")
    return float(equity.iloc[-1] ** (1.0 / years) - 1.0)


def _cagr_numpy(returns: pd.Series) -> float:
    arr = returns.to_numpy(dtype=float)
    n = len(arr)
    if n == 0:
        return float("nan")
    growth = float(np.prod(1.0 + arr))
    return float(growth ** (TRADING_DAYS / n) - 1.0)


def gate_pbo(returns_matrix: np.ndarray, *, n_blocks: int = 10, threshold: float = 0.5) -> dict:
    """G1 - Probability of Backtest Overfitting via CSCV `[advances_fin_ml, p.208-211]`.

    ``returns_matrix`` is ``(T, N)``: T periods x N trial configs. Pass iff
    ``pbo < threshold``.
    """
    result = pbo(np.asarray(returns_matrix, dtype=float), n_blocks=n_blocks)
    return {
        "pbo": float(result.pbo),
        "n_combinations": int(result.n_combinations),
        "n_configs": int(np.asarray(returns_matrix).shape[1]),
        "pass_gate": bool(result.pbo < threshold),
    }


def gate_dsr(returns: pd.Series, n_trials: int, *, alpha: float = 0.05) -> dict:
    """G2 - Deflated Sharpe Ratio `[advances_fin_ml, p.273-275]`.

    Corrects the observed Sharpe for selection bias across ``n_trials`` tried
    configurations. Pass iff ``p_value = 1 - DSR < alpha``.
    """
    result = dsr(returns.to_numpy(dtype=float), n_trials=int(n_trials))
    return {
        "p_value": float(result.p_value),
        "dsr": float(result.dsr),
        "observed_sharpe": float(result.observed_sharpe),
        "benchmark_sharpe": float(result.benchmark_sharpe),
        "n_trials": int(n_trials),
        "pass_gate": bool(result.p_value < alpha),
    }


def _oos_total_return(returns: pd.Series, sl: range) -> float:
    seg = returns.iloc[sl.start : sl.stop].to_numpy(dtype=float)
    if len(seg) == 0:
        return 0.0
    return float(np.prod(1.0 + seg) - 1.0)


def _segment_mdd(returns: pd.Series, sl: range) -> float:
    seg = returns.iloc[sl.start : sl.stop].to_numpy(dtype=float)
    if len(seg) == 0:
        return 0.0
    equity = np.cumprod(1.0 + seg)
    peak = np.maximum.accumulate(equity)
    return float((1.0 - equity / peak).max())  # positive magnitude


def gate_walk_forward(
    strategy: pd.Series,
    benchmark: pd.Series,
    *,
    is_size: int,
    oos_size: int,
    step: int,
    min_windows: int = 8,
    min_profitable_ratio: float = 6.0 / 8.0,
) -> dict:
    """G3 - rolling walk-forward; >= 6/8 OOS windows must beat the benchmark.

    Per-window OOS metric = strategy total return minus benchmark total return.
    The per-window MDD is reported as a DIAGNOSTIC only (no cap), because this is
    a leveraged sleeve whose drawdown is governed by the restart's tiers, not the
    core 25%/50% gate `[testing_tuning, p.318-320]`, `[advances_fin_ml,
    p.211-216]`. Reuses the canonical ``walk_forward_gate`` by passing the
    relative (strategy - benchmark) per-window returns with the MDD cap disabled.
    """
    aligned = pd.concat({"s": strategy, "b": benchmark}, axis=1).dropna()
    s = aligned["s"]
    b = aligned["b"]
    n_obs = len(s)
    rel_returns: list[float] = []
    oos_mdds: list[float] = []
    for _train, test in walk_forward_splits(n_obs, is_size=is_size, oos_size=oos_size, step=step):
        rel_returns.append(_oos_total_return(s, test) - _oos_total_return(b, test))
        oos_mdds.append(_segment_mdd(s, test))
    n = len(rel_returns)
    verdict = (
        walk_forward_gate(
            rel_returns,
            [0.0] * n,  # MDD cap disabled below
            min_windows=min_windows,
            min_profitable_ratio=min_profitable_ratio,
            max_drawdown=1.0,
        )
        if n
        else "reject"
    )
    return {
        "n_windows": int(n),
        "windows_beat_benchmark": int(sum(1 for r in rel_returns if r > 0)),
        "oos_rel_returns": [float(r) for r in rel_returns],
        "oos_mdds_diagnostic": [float(d) for d in oos_mdds],
        "pass_gate": bool(verdict == "pass"),
    }


def gate_oos(strategy: pd.Series, benchmark: pd.Series, *, oos_frac: float = 0.30) -> dict:
    """G4 - single-block OOS (last ``oos_frac`` of dates).

    Pass iff OOS Sharpe > 0 AND OOS strategy compound return beats the benchmark
    `[testing_tuning, p.327-335]`.
    """
    aligned = pd.concat({"s": strategy, "b": benchmark}, axis=1).dropna()
    cutoff = int(len(aligned) * (1.0 - oos_frac))
    oos_s = aligned["s"].iloc[cutoff:]
    oos_b = aligned["b"].iloc[cutoff:]
    oos_sharpe = _ann_sharpe(oos_s.to_numpy(dtype=float))
    strat_growth = float(np.prod(1.0 + oos_s.to_numpy(dtype=float)))
    bench_growth = float(np.prod(1.0 + oos_b.to_numpy(dtype=float)))
    beats = bool(strat_growth > bench_growth)
    return {
        "oos_sharpe": oos_sharpe,
        "n_oos_obs": int(len(oos_s)),
        "beats_benchmark": beats,
        "pass_gate": bool(oos_sharpe > 0.0 and beats),
    }


def gate_fwd_stress(strategy: pd.Series, *, cutoff: str = "2020-01-01") -> dict:
    """G5 - forward stress on the post-``cutoff`` block; Sharpe > 0 `[testing_tuning, p.318-320]`."""
    fwd = strategy[strategy.index >= pd.Timestamp(cutoff)]
    sharpe = _ann_sharpe(fwd.to_numpy(dtype=float)) if len(fwd) else float("nan")
    return {
        "fwd_sharpe": float(sharpe),
        "n_obs": int(len(fwd)),
        "cutoff": cutoff,
        "pass_gate": bool(len(fwd) > 0 and sharpe > 0.0),
    }


def gate_bootstrap(
    returns: pd.Series,
    *,
    ci_pct: float = 99.9,
    block: int = 21,
    n_resamples: int = 5000,
    seed: int = 42,
) -> dict:
    """G6 - stationary block bootstrap; lower bound of the ``ci_pct`` CI of the
    annualized Sharpe must exceed 0 `[advances_fin_ml, p.211-216]`."""
    arr = returns.to_numpy(dtype=float)
    resamples = stationary_bootstrap_trades(arr, block_mean=block, n_resamples=n_resamples, seed=seed)
    means = resamples.mean(axis=1)
    sds = resamples.std(axis=1, ddof=0)
    sds = np.where(sds <= 1e-12, np.nan, sds)
    sharpes = means / sds * np.sqrt(TRADING_DAYS)
    sharpes = sharpes[np.isfinite(sharpes)]
    lower_pct = (100.0 - ci_pct) / 2.0
    ci_low = float(np.percentile(sharpes, lower_pct))
    return {
        "ci_low_sharpe": ci_low,
        "ci_pct": ci_pct,
        "n_resamples": int(len(sharpes)),
        "pass_gate": bool(ci_low > 0.0),
    }


def gate_cross_lib(returns: pd.Series, *, threshold_pp: float = 3.0) -> dict:
    """G7 - cross-library agreement: after-tax CAGR computed via a pandas path
    and an independent numpy path must agree within ``threshold_pp`` pp
    `[advances_fin_ml, p.208-211]`."""
    cagr_pd = _cagr_pandas(returns)
    cagr_np = _cagr_numpy(returns)
    delta_pp = abs(cagr_np - cagr_pd) * 100.0
    return {
        "cagr_pandas": float(cagr_pd),
        "cagr_numpy": float(cagr_np),
        "delta_pp": float(delta_pp),
        "pass_gate": bool(delta_pp <= threshold_pp),
    }


def run_gate_suite(
    base_returns: pd.Series,
    returns_matrix: np.ndarray,
    benchmark: pd.Series,
    *,
    n_trials: int,
    wf_is_size: int,
    wf_oos_size: int,
    wf_step: int,
    fwd_cutoff: str = "2020-01-01",
) -> dict:
    """Run all seven mandate gates and aggregate the hard-block verdict.

    ``overall_pass`` is the conjunction of every gate (zero bypass, mandate §5).
    """
    gates = {
        "g1_pbo": gate_pbo(returns_matrix),
        "g2_dsr": gate_dsr(base_returns, n_trials=n_trials),
        "g3_walk_forward": gate_walk_forward(
            base_returns, benchmark, is_size=wf_is_size, oos_size=wf_oos_size, step=wf_step
        ),
        "g4_oos": gate_oos(base_returns, benchmark),
        "g5_fwd_stress": gate_fwd_stress(base_returns, cutoff=fwd_cutoff),
        "g6_bootstrap": gate_bootstrap(base_returns),
        "g7_cross_lib": gate_cross_lib(base_returns),
    }
    overall = all(g["pass_gate"] for g in gates.values())
    return {"gates": gates, "overall_pass": bool(overall)}
