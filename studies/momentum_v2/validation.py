"""Result rows, PBO summary, and the honest validate-phase gates.

Broad/evolution rows carry diagnostics (rolling dominance, crisis MDD, cheap WF,
DSR p-value, turnover, after-tax metrics). The validate phase applies the
project's hard gates `[advances_fin_ml, p.208-211, p.273-275]` to a small
finalist set with an honest trial count, reusing the shared engine
(``pbo``, ``dsr``, ``wf_for_config``). Every row is ``promotion_eligible=false``.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from market_lab.backtest.grid.walk_forward import wf_for_config
from market_lab.backtest.metrics.performance import sharpe
from market_lab.backtest.validation.dsr import dsr, psr
from market_lab.backtest.validation.pbo import pbo
from studies.momentum_v2.core import (
    TRADING_DAYS_PER_YEAR,
    SimulationResult,
    StrategyConfig,
    benchmark_returns_for,
    equity_from_returns,
    metrics_from_returns,
)
from studies.momentum_v2.dominance import (
    crisis_columns,
    relative_equity_metrics,
    rolling_relative_equity_metrics,
    walk_forward_diagnostic,
)


def bootstrap_sharpe_ci_low(returns: pd.Series, resamples: int, block_days: int, pct: float) -> float:
    """Stationary-block bootstrap lower CI on annualized Sharpe."""
    arr = returns.dropna().to_numpy(dtype=float)
    if resamples <= 0 or len(arr) < TRADING_DAYS_PER_YEAR or block_days <= 0:
        return float("nan")
    rng = np.random.default_rng(42)
    n_blocks = max(1, math.ceil(len(arr) / block_days))
    values: list[float] = []
    for _ in range(resamples):
        starts = rng.integers(0, max(len(arr) - block_days + 1, 1), size=n_blocks)
        sample = np.concatenate([arr[start : start + block_days] for start in starts])[: len(arr)]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            values.append(float(sample.mean() / sigma * np.sqrt(TRADING_DAYS_PER_YEAR)))
    return float(np.percentile(values, pct)) if values else float("nan")


def result_row(
    config: StrategyConfig,
    simulation: SimulationResult,
    benchmark_prices: pd.DataFrame,
    *,
    n_trials: int,
    benchmark_symbol: str = "SPY",
    ranked_returns: pd.Series | None = None,
    tax_summary: dict[str, object] | None = None,
    extra: dict[str, object] | None = None,
    bootstrap_resamples: int = 0,
    bootstrap_block_days: int = 21,
    bootstrap_ci_low_pct: float = 0.1,
    xlib_cagr_delta_pp: float = float("nan"),
) -> dict[str, Any]:
    """Build one flat result row (after-tax main metrics, gross alongside)."""
    ranked_returns = ranked_returns if ranked_returns is not None else simulation.returns
    strategy_returns, bench_returns = benchmark_returns_for(ranked_returns, benchmark_prices, benchmark_symbol)
    gross_returns, _ = benchmark_returns_for(simulation.returns, benchmark_prices, benchmark_symbol)
    metrics = metrics_from_returns(strategy_returns)
    gross_metrics = metrics_from_returns(gross_returns)
    bench_metrics = metrics_from_returns(bench_returns)
    rel = relative_equity_metrics(strategy_returns, bench_returns)
    rolling = rolling_relative_equity_metrics(strategy_returns, bench_returns)
    crisis = crisis_columns(strategy_returns, bench_returns)
    wf = walk_forward_diagnostic(strategy_returns)

    p_value = 1.0
    if len(strategy_returns) >= 3:
        arr = strategy_returns.to_numpy(dtype=float)
        p_value = float(dsr(arr, n_trials=n_trials).p_value) if n_trials >= 2 else 1.0 - float(psr(arr, benchmark=0.0))
    oos = strategy_returns.iloc[int(len(strategy_returns) * 0.70) :]
    fwd = strategy_returns[strategy_returns.index >= "2020-01-01"]
    boot_low = bootstrap_sharpe_ci_low(
        strategy_returns, bootstrap_resamples, bootstrap_block_days, bootstrap_ci_low_pct
    )
    tax = tax_summary or {}
    row: dict[str, Any] = {
        "name": config.name,
        "universe": config.universe,
        "mechanism": config.mechanism,
        "score_mode": config.score_mode,
        "lookback_label": config.lookback.label,
        "lookback_months": "/".join(str(m) for m in config.lookback.months),
        "weight_mode": config.weight_mode,
        "absolute_filter": config.absolute_filter,
        "top_n": config.top_n,
        "rebalance_months": config.rebalance_months,
        "rebalance_offset": config.rebalance_offset,
        "n_assets": len(config.assets),
        "promotion_eligible": False,
        "start": metrics["start"],
        "end": metrics["end"],
        "n_obs": metrics["n_obs"],
        "cagr": metrics["cagr"],
        "after_tax_cagr": metrics["cagr"],
        "gross_cagr": gross_metrics["cagr"],
        "tax_drag_cagr": float(gross_metrics["cagr"]) - float(metrics["cagr"]),
        "mdd": metrics["mdd"],
        "after_tax_mdd": metrics["mdd"],
        "gross_mdd": gross_metrics["mdd"],
        "vol": metrics["vol"],
        "after_tax_vol": metrics["vol"],
        "sharpe": metrics["sharpe"],
        "after_tax_sharpe": metrics["sharpe"],
        "gross_sharpe": gross_metrics["sharpe"],
        "sortino": metrics["sortino"],
        "calmar": metrics["calmar"],
        "after_tax_calmar": metrics["calmar"],
        "terminal": metrics["terminal"],
        "spy_cagr": bench_metrics["cagr"],
        "spy_mdd": bench_metrics["mdd"],
        "spy_sharpe": bench_metrics["sharpe"],
        "excess_cagr": float(metrics["cagr"]) - float(bench_metrics["cagr"]),
        "excess_sharpe": float(metrics["sharpe"]) - float(bench_metrics["sharpe"]),
        "pct_time_above_spy": rel["pct_time_above_benchmark"],
        "min_relative_equity": rel["min_relative_equity"],
        "terminal_relative": rel["terminal_relative"],
        **rolling,
        **crisis,
        "dsr_p_value": p_value,
        "oos_sharpe": float(sharpe(oos, TRADING_DAYS_PER_YEAR)) if len(oos) else float("nan"),
        "fwd_sharpe": float(sharpe(fwd, TRADING_DAYS_PER_YEAR)) if len(fwd) else float("nan"),
        "bootstrap_ci_low_sharpe": boot_low,
        "xlib_cagr_delta_pp": xlib_cagr_delta_pp,
        "total_tax_paid": float(tax.get("total_tax_paid", 0.0)),
        "tax_paid_pct_initial": float(tax.get("tax_paid_pct_initial", 0.0)),
        "years_taxed": int(tax.get("years_taxed", 0)),
        **wf,
        **simulation.turnover,
    }
    if extra:
        row.update(extra)
    return row


# --- PBO -------------------------------------------------------------------

def sample_returns_for_pbo(
    returns_by_name: dict[str, pd.Series], max_configs: int | None
) -> tuple[dict[str, pd.Series], bool]:
    """Deterministically downsample a broad screen before CSCV/PBO.

    Full PBO is the honest validation mode `[advances_fin_ml, p.208-211]`; broad
    screens just keep discovery bounded without ranking by performance first.
    """
    if max_configs is None or max_configs <= 0 or len(returns_by_name) <= max_configs:
        return returns_by_name, False
    max_configs = max(2, int(max_configs))
    names = sorted(returns_by_name)
    step = len(names) / float(max_configs)
    selected = list(dict.fromkeys(names[min(int(i * step), len(names) - 1)] for i in range(max_configs)))
    return {name: returns_by_name[name] for name in selected}, True


def pbo_one(
    label: str, returns_by_name: dict[str, pd.Series], n_blocks: int, *, max_configs: int | None = None
) -> dict[str, Any]:
    total = len(returns_by_name)
    returns_by_name, sampled = sample_returns_for_pbo(returns_by_name, max_configs)
    if len(returns_by_name) < 2:
        return {"group": label, "pbo": float("nan"), "n_configs": len(returns_by_name),
                "n_configs_total": total, "sampled": sampled, "pass": True}
    aligned = pd.concat(returns_by_name, axis=1, sort=False).dropna()
    if aligned.shape[1] < 2 or len(aligned) < TRADING_DAYS_PER_YEAR:
        return {"group": label, "pbo": float("nan"), "n_configs": len(returns_by_name),
                "n_configs_total": total, "sampled": sampled, "n_obs": len(aligned),
                "pass": False, "note": "insufficient aligned data"}
    result = pbo(aligned.to_numpy(dtype=float), n_blocks=n_blocks)
    return {"group": label, "pbo": float(result.pbo), "n_configs": len(returns_by_name),
            "n_configs_total": total, "sampled": sampled, "n_obs": len(aligned),
            "n_combinations": int(result.n_combinations), "pass": bool(result.pbo < 0.5)}


def pbo_summary(
    returns_by_name: dict[str, pd.Series], groups: pd.DataFrame, n_blocks: int, max_configs: int | None = None
) -> dict[str, Any]:
    rows = [pbo_one("all", returns_by_name, n_blocks, max_configs=max_configs)]
    if not groups.empty and "mechanism" in groups.columns:
        for mechanism in sorted(groups["mechanism"].unique()):
            names = set(groups.loc[groups["mechanism"] == mechanism, "name"])
            rows.append(pbo_one(f"mechanism:{mechanism}", _filter(returns_by_name, names), n_blocks, max_configs=max_configs))
    return {"rows": rows}


def _filter(returns_by_name: dict[str, pd.Series], names: set[str]) -> dict[str, pd.Series]:
    return {name: value for name, value in returns_by_name.items() if name in names}


# --- validate-phase hard gates ---------------------------------------------

def validate_gates(
    returns_by_name: dict[str, pd.Series],
    *,
    n_trials: int,
    pbo_blocks: int = 10,
    dsr_alpha: float = 0.05,
    wf_min_windows: int = 8,
    wf_max_drawdown: float = 0.25,
    bootstrap_resamples: int = 1000,
    bootstrap_block_days: int = 21,
    xlib_delta_by_name: dict[str, float] | None = None,
    xlib_max_pp: float = 3.0,
) -> dict[str, Any]:
    """Apply the project's hard gates to a finalist set with honest trial count.

    Gates `[advances_fin_ml, p.208-211, p.273-275]`: PBO<0.5 over the set,
    DSR p<0.05, WF>=6/8 (shared engine), bootstrap 99.9%/low CI Sharpe > 0,
    and cross-library CAGR within +/-3pp. ``overall_pass`` is True iff PBO passes
    and at least one config clears every per-config gate.
    """
    xlib_delta_by_name = xlib_delta_by_name or {}
    set_pbo = pbo_one("all", returns_by_name, pbo_blocks)
    pbo_pass = bool(set_pbo.get("pass", False)) and not set_pbo.get("note")

    per_config: list[dict[str, Any]] = []
    for name, returns in returns_by_name.items():
        clean = returns.dropna().astype(float)
        verdict: dict[str, Any] = {"name": name}
        if len(clean) < TRADING_DAYS_PER_YEAR:
            verdict.update(dsr_pass=False, wf_pass=False, bootstrap_pass=False, xlib_pass=False, all_pass=False)
            per_config.append(verdict)
            continue
        arr = clean.to_numpy(dtype=float)
        p_value = float(dsr(arr, n_trials=max(n_trials, 2)).p_value)
        equity = equity_from_returns(clean, start_value=1.0)
        wf = wf_for_config(
            equity_curve=equity, config_id=0, n_windows=wf_min_windows, max_drawdown=wf_max_drawdown
        )
        boot_low = bootstrap_sharpe_ci_low(clean, bootstrap_resamples, bootstrap_block_days, 0.1)
        xlib_delta = abs(float(xlib_delta_by_name.get(name, float("nan"))))
        dsr_pass = p_value < dsr_alpha
        wf_pass = wf.verdict == "pass"
        bootstrap_pass = math.isfinite(boot_low) and boot_low > 0.0
        xlib_pass = math.isfinite(xlib_delta) and xlib_delta <= xlib_max_pp
        verdict.update(
            dsr_p_value=p_value,
            dsr_pass=dsr_pass,
            wf_verdict=wf.verdict,
            wf_profitable=wf.n_profitable,
            wf_windows=wf.n_windows,
            wf_pass=wf_pass,
            bootstrap_ci_low_sharpe=boot_low,
            bootstrap_pass=bootstrap_pass,
            xlib_cagr_delta_pp=xlib_delta,
            xlib_pass=xlib_pass,
            all_pass=bool(dsr_pass and wf_pass and bootstrap_pass and xlib_pass),
        )
        per_config.append(verdict)

    any_config_pass = any(v["all_pass"] for v in per_config)
    return {
        "n_trials": n_trials,
        "pbo": set_pbo,
        "pbo_pass": pbo_pass,
        "per_config": per_config,
        "overall_pass": bool(pbo_pass and any_config_pass),
    }
