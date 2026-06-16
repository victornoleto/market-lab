"""Validation diagnostics for momentum grid outputs."""

from __future__ import annotations

import math
from dataclasses import asdict
from typing import Any

import numpy as np
import pandas as pd

from market_lab.backtest.metrics.performance import (
    cagr,
    calmar,
    max_drawdown,
    sharpe,
    sortino,
    volatility,
)
from market_lab.backtest.validation.dsr import dsr, psr
from market_lab.backtest.validation.pbo import pbo
from market_lab.backtest.validation.walk_forward import walk_forward_splits
from studies.momentum.features import TRADING_DAYS_PER_YEAR
from studies.momentum.strategies import SimulationResult, StrategyConfig


def equity_from_returns(returns: pd.Series, start_value: float = 1.0) -> pd.Series:
    clean = returns.dropna().astype(float)
    if clean.empty:
        return pd.Series(dtype=float, name="equity")
    start = pd.Series([start_value], index=[clean.index[0] - pd.Timedelta(days=1)])
    compounded = (1.0 + clean).cumprod() * start_value
    out = pd.concat([start, compounded])
    out.name = "equity"
    return out


def metrics_from_returns(returns: pd.Series) -> dict[str, float | str | int]:
    clean = returns.dropna().astype(float)
    if clean.empty:
        return {
            "start": "n/a",
            "end": "n/a",
            "n_obs": 0,
            "years": 0.0,
            "cagr": 0.0,
            "mdd": 0.0,
            "vol": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "calmar": 0.0,
            "terminal": 1.0,
        }
    equity = equity_from_returns(clean)
    return {
        "start": str(clean.index[0].date()),
        "end": str(clean.index[-1].date()),
        "n_obs": int(len(clean)),
        "years": float(len(clean) / TRADING_DAYS_PER_YEAR),
        "cagr": float(cagr(equity, TRADING_DAYS_PER_YEAR)),
        "mdd": -float(max_drawdown(equity)),
        "vol": float(volatility(clean, TRADING_DAYS_PER_YEAR)),
        "sharpe": float(sharpe(clean, TRADING_DAYS_PER_YEAR)),
        "sortino": float(sortino(clean, TRADING_DAYS_PER_YEAR)),
        "calmar": float(calmar(equity, TRADING_DAYS_PER_YEAR)),
        "terminal": float(equity.iloc[-1]),
    }


def benchmark_returns(strategy_returns: pd.Series, benchmark_prices: pd.DataFrame) -> pd.Series:
    if strategy_returns.empty or benchmark_prices.empty:
        return pd.Series(dtype=float, name="benchmark")
    prices = benchmark_prices.iloc[:, 0].astype(float).sort_index()
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None)
    prices = prices.reindex(strategy_returns.index, method="ffill").dropna()
    if prices.empty:
        return pd.Series(dtype=float, name="benchmark")
    return prices.pct_change(fill_method=None).fillna(0.0).rename(str(benchmark_prices.columns[0]))


def relative_metrics(strategy_returns: pd.Series, bench_returns: pd.Series) -> dict[str, float]:
    aligned = pd.concat({"strategy": strategy_returns, "benchmark": bench_returns}, axis=1).dropna()
    if aligned.empty:
        return {
            "pct_time_above_benchmark": float("nan"),
            "min_relative_equity": float("nan"),
            "terminal_relative": float("nan"),
        }
    strategy_eq = equity_from_returns(aligned["strategy"])
    bench_eq = equity_from_returns(aligned["benchmark"])
    ratio = pd.concat({"s": strategy_eq, "b": bench_eq}, axis=1).dropna()
    rel = ratio["s"] / ratio["b"]
    post = rel.iloc[min(252, max(len(rel) - 1, 0)) :]
    if post.empty:
        post = rel
    return {
        "pct_time_above_benchmark": float((post > 1.0).mean()),
        "min_relative_equity": float(post.min()),
        "terminal_relative": float(rel.iloc[-1]),
    }


def walk_forward_diagnostic(returns: pd.Series, min_windows: int, min_positive: int) -> dict[str, Any]:
    n = len(returns)
    window = n // (min_windows + 1)
    if window < 63:
        return {"wf_windows": 0, "wf_positive": 0, "wf_pass": False, "wf_oos_returns": []}
    oos_returns: list[float] = []
    for _, test_range in walk_forward_splits(n, window, window, window):
        r = returns.iloc[list(test_range)]
        oos_returns.append(float((1.0 + r).prod() - 1.0))
        if len(oos_returns) >= min_windows:
            break
    positive = sum(value > 0.0 for value in oos_returns)
    return {
        "wf_windows": len(oos_returns),
        "wf_positive": positive,
        "wf_pass": bool(len(oos_returns) >= min_windows and positive >= min_positive),
        "wf_oos_returns": oos_returns,
    }


def bootstrap_sharpe_ci_low(returns: pd.Series, resamples: int, block_days: int, pct: float) -> float:
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


def rolling_window_metrics(returns: pd.Series, years: list[int]) -> dict[str, float]:
    out: dict[str, float] = {}
    clean = returns.dropna().astype(float)
    for year in years:
        window = int(year * TRADING_DAYS_PER_YEAR)
        if len(clean) < window:
            out[f"rolling_{year}y_min_return"] = float("nan")
            continue
        compounded = (1.0 + clean).rolling(window).apply(np.prod, raw=True) - 1.0
        out[f"rolling_{year}y_min_return"] = float(compounded.min())
    return out


def result_row(
    config: StrategyConfig,
    simulation: SimulationResult,
    benchmark_prices: pd.DataFrame,
    *,
    n_trials: int,
    validation_config: dict[str, Any],
    xlib_cagr_delta_pp: float,
) -> dict[str, Any]:
    returns = simulation.returns.dropna().astype(float)
    metrics = metrics_from_returns(returns)
    bench = benchmark_returns(returns, benchmark_prices)
    bench_metrics = metrics_from_returns(bench)
    rel = relative_metrics(returns, bench)
    p_value = 1.0
    if len(returns) >= 3:
        arr = returns.to_numpy(dtype=float)
        p_value = float(dsr(arr, n_trials=n_trials).p_value) if n_trials >= 2 else 1.0 - float(psr(arr))
    wf = walk_forward_diagnostic(
        returns,
        int(validation_config.get("wf_min_windows", 8)),
        int(validation_config.get("wf_min_positive", 6)),
    )
    oos = returns.iloc[int(len(returns) * 0.70) :]
    fwd = returns[returns.index >= "2020-01-01"]
    boot_low = bootstrap_sharpe_ci_low(
        returns,
        int(validation_config.get("bootstrap_resamples", 1000)),
        int(validation_config.get("bootstrap_block_days", 21)),
        float(validation_config.get("bootstrap_ci_low_pct", 0.1)),
    )
    rolling = rolling_window_metrics(returns, [int(x) for x in validation_config.get("rolling_years", [])])
    return {
        "name": config.name,
        "universe": config.universe,
        "mechanism": config.mechanism,
        "score_mode": config.score_mode,
        "weight_mode": config.weight_mode,
        "top_n": config.top_n,
        "rebalance_months": config.rebalance_months,
        "rebalance_offset": config.rebalance_offset,
        "absolute_filter": config.absolute_filter,
        "staggered_offsets": config.staggered_offsets,
        "n_assets": len(config.assets),
        "promotion_eligible": False,
        "strategy_config": asdict(config),
        **metrics,
        "benchmark_cagr": bench_metrics["cagr"],
        "benchmark_mdd": bench_metrics["mdd"],
        "benchmark_sharpe": bench_metrics["sharpe"],
        "excess_cagr": float(metrics["cagr"]) - float(bench_metrics["cagr"]),
        "excess_sharpe": float(metrics["sharpe"]) - float(bench_metrics["sharpe"]),
        **rel,
        "dsr_p_value": p_value,
        "oos_sharpe": float(sharpe(oos, TRADING_DAYS_PER_YEAR)) if len(oos) else float("nan"),
        "fwd_sharpe": float(sharpe(fwd, TRADING_DAYS_PER_YEAR)) if len(fwd) else float("nan"),
        "bootstrap_ci_low_sharpe": boot_low,
        "xlib_cagr_delta_pp": xlib_cagr_delta_pp,
        **wf,
        **rolling,
        **simulation.turnover,
    }


def pbo_summary(
    returns_by_name: dict[str, pd.Series],
    groups: pd.DataFrame,
    n_blocks: int,
    max_configs: int | None = None,
) -> dict[str, Any]:
    rows = [pbo_one("all", returns_by_name, n_blocks, max_configs=max_configs)]
    if not groups.empty:
        for universe in sorted(groups["universe"].unique()):
            names = set(groups.loc[groups["universe"] == universe, "name"])
            rows.append(
                pbo_one(
                    f"universe:{universe}",
                    _filter(returns_by_name, names),
                    n_blocks,
                    max_configs=max_configs,
                )
            )
        for mechanism in sorted(groups["mechanism"].unique()):
            names = set(groups.loc[groups["mechanism"] == mechanism, "name"])
            rows.append(
                pbo_one(
                    f"mechanism:{mechanism}",
                    _filter(returns_by_name, names),
                    n_blocks,
                    max_configs=max_configs,
                )
            )
    return {"rows": rows}


def _filter(returns_by_name: dict[str, pd.Series], names: set[str]) -> dict[str, pd.Series]:
    return {name: value for name, value in returns_by_name.items() if name in names}


def pbo_one(
    label: str,
    returns_by_name: dict[str, pd.Series],
    n_blocks: int,
    *,
    max_configs: int | None = None,
) -> dict[str, Any]:
    total_configs = len(returns_by_name)
    returns_by_name, sampled = sample_returns_for_pbo(returns_by_name, max_configs)
    if len(returns_by_name) < 2:
        return {
            "group": label,
            "pbo": float("nan"),
            "n_configs": len(returns_by_name),
            "n_configs_total": total_configs,
            "sampled": sampled,
            "pass": True,
        }
    aligned = pd.concat(returns_by_name, axis=1, sort=False).dropna()
    if aligned.shape[1] < 2 or len(aligned) < TRADING_DAYS_PER_YEAR:
        return {
            "group": label,
            "pbo": float("nan"),
            "n_configs": len(returns_by_name),
            "n_configs_total": total_configs,
            "sampled": sampled,
            "n_obs": len(aligned),
            "pass": False,
            "note": "insufficient aligned data",
        }
    result = pbo(aligned.to_numpy(dtype=float), n_blocks=n_blocks)
    return {
        "group": label,
        "pbo": float(result.pbo),
        "n_configs": len(returns_by_name),
        "n_configs_total": total_configs,
        "sampled": sampled,
        "n_obs": len(aligned),
        "n_combinations": int(result.n_combinations),
        "pass": bool(result.pbo < 0.5),
    }


def sample_returns_for_pbo(
    returns_by_name: dict[str, pd.Series], max_configs: int | None
) -> tuple[dict[str, pd.Series], bool]:
    """Deterministically downsample broad screens before CSCV/PBO.

    Full PBO remains the honest validation mode `[advances_fin_ml, p.208-211]`.
    Broad screens can be much larger, so this keeps the discovery run bounded
    without ranking by performance before sampling.
    """
    if max_configs is None or max_configs <= 0 or len(returns_by_name) <= max_configs:
        return returns_by_name, False
    max_configs = max(2, int(max_configs))
    names = sorted(returns_by_name)
    if len(names) <= max_configs:
        return returns_by_name, False
    step = len(names) / float(max_configs)
    selected = [names[min(int(i * step), len(names) - 1)] for i in range(max_configs)]
    selected = list(dict.fromkeys(selected))
    return {name: returns_by_name[name] for name in selected}, True
