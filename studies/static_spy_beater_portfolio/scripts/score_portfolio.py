"""Portfolio scoring for the static SPY-beater study.

Rolling-window scoring uses all possible start/end windows by default. The optional
`rolling_step` parameter exists for smoke runs only; production discovery should use
`1` to match the pre-registered design `[testing_tuning, p.327-335]`.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.static_spy_beater_portfolio.scripts.universe import (  # noqa: E402
    B4_WEIGHTS,
    CORE_35_40_25_WEIGHTS,
    equal_weight_for_universe,
    has_b4,
    load_universe_returns,
    portfolio_effective_exposure,
)

TRADING_DAYS_PER_YEAR = 252
HORIZON_DAYS = {"1y": 252, "3y": 756, "5y": 1260, "10y": 2520, "15y": 3780, "20y": 5040}
HORIZON_WEIGHTS = {"1y": 0.025, "3y": 0.075, "5y": 0.15, "10y": 0.25, "15y": 0.25, "20y": 0.25}


@dataclass(frozen=True)
class PortfolioScore:
    weights: dict[str, float]
    full_metrics: dict[str, float | str]
    benchmark_metrics: dict[str, dict[str, float | str]]
    rolling: dict[str, dict[str, float]]
    fitness: dict[str, float]
    exposure: dict[str, float]


BenchmarkCache = dict[str, dict[str, dict[str, np.ndarray]]]


@dataclass(frozen=True)
class GrowthCache:
    """Precomputed within-month growth factors shared across portfolio candidates.

    For monthly-rebalanced portfolios, intra-month asset cumprod is independent of
    weights. Caching this tensor turns per-candidate scoring into a matrix-vector
    multiply instead of a Python groupby loop.
    """

    growth: np.ndarray  # shape (n_days, n_assets); cumprod resets at each month start
    month_starts: np.ndarray  # int64 indices of first day in each month
    month_ends: np.ndarray  # int64 indices of last day in each month
    columns: tuple[str, ...]
    index: pd.DatetimeIndex
    column_index: dict[str, int]


def precompute_growth_matrix(asset_returns: pd.DataFrame) -> GrowthCache:
    """Compute within-month cumprod for every asset once, reusable across candidates.

    The caller is responsible for passing a DataFrame already aligned to the common
    universe window (no NaN). Candidates that select a subset of columns combine
    asset growth linearly via the static weight vector.
    """
    if asset_returns.isna().any().any():
        raise ValueError("precompute_growth_matrix requires NaN-free asset returns")
    arr = np.asarray(asset_returns.to_numpy(dtype=float))
    n_days = arr.shape[0]
    if n_days == 0:
        raise ValueError("asset_returns is empty")
    periods = asset_returns.index.to_period("M")
    codes, _ = pd.factorize(periods, sort=False)
    boundaries = np.where(np.diff(codes, prepend=codes[0] - 1) != 0)[0]
    month_starts = boundaries.astype(np.int64)
    month_ends = np.concatenate([month_starts[1:] - 1, [n_days - 1]]).astype(np.int64)
    growth = np.empty_like(arr)
    one_plus = 1.0 + arr
    for s, e in zip(month_starts.tolist(), month_ends.tolist(), strict=True):
        np.cumprod(one_plus[s : e + 1], axis=0, out=growth[s : e + 1])
    columns = tuple(asset_returns.columns)
    return GrowthCache(
        growth=growth,
        month_starts=month_starts,
        month_ends=month_ends,
        columns=columns,
        index=asset_returns.index,
        column_index={c: i for i, c in enumerate(columns)},
    )


def monthly_rebalanced_returns(
    asset_returns: pd.DataFrame,
    weights: dict[str, float],
    *,
    growth_cache: GrowthCache | None = None,
) -> pd.Series:
    """Return monthly rebalanced daily returns for static weights.

    If `growth_cache` is provided (and covers all selected assets), the precomputed
    within-month tensor is used; otherwise the function falls back to the legacy
    per-call groupby path for one-off scoring.
    """
    if growth_cache is not None and all(asset in growth_cache.column_index for asset in weights):
        return _monthly_rebalanced_returns_cached(weights, growth_cache)
    return _monthly_rebalanced_returns_legacy(asset_returns, weights)


def _monthly_rebalanced_returns_legacy(asset_returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    aligned = asset_returns[list(weights)].dropna()
    if aligned.empty:
        raise ValueError("portfolio has no aligned returns")
    target = np.array([weights[col] for col in aligned.columns], dtype=float)
    values: list[np.ndarray] = []
    dates: list[pd.DatetimeIndex] = []
    portfolio_value = 1.0
    for _month, month_returns in aligned.groupby(aligned.index.to_period("M"), sort=True):
        growth = np.cumprod(1.0 + month_returns.to_numpy(dtype=float), axis=0)
        month_values = portfolio_value * (growth @ target)
        values.append(month_values)
        dates.append(month_returns.index)
        portfolio_value = float(month_values[-1])
    equity = pd.Series(np.concatenate(values), index=dates[0].append(dates[1:]), name="portfolio_equity")
    returns = equity.pct_change()
    returns.iloc[0] = equity.iloc[0] - 1.0
    returns.name = "portfolio"
    return returns


def _monthly_rebalanced_returns_cached(weights: dict[str, float], cache: GrowthCache) -> pd.Series:
    weight_vec = np.zeros(len(cache.columns), dtype=float)
    for asset, value in weights.items():
        weight_vec[cache.column_index[asset]] = float(value)
    daily_combined = cache.growth @ weight_vec  # within-month weighted growth factor at every day
    month_end_factors = daily_combined[cache.month_ends]
    cum_prev = np.concatenate([[1.0], np.cumprod(month_end_factors)[:-1]])
    lengths = (cache.month_ends - cache.month_starts + 1).astype(np.int64)
    scale = np.repeat(cum_prev, lengths)
    equity_arr = scale * daily_combined
    returns_arr = np.empty(equity_arr.shape[0], dtype=float)
    returns_arr[0] = equity_arr[0] - 1.0
    returns_arr[1:] = equity_arr[1:] / equity_arr[:-1] - 1.0
    return pd.Series(returns_arr, index=cache.index, name="portfolio")


def metrics_from_returns(returns: pd.Series) -> dict[str, float | str]:
    r = returns.dropna().astype(float)
    if len(r) < 2:
        return _empty_metrics(r)
    equity = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS_PER_YEAR
    drawdown = equity / equity.cummax() - 1.0
    vol = float(r.std(ddof=0))
    downside = float(r[r < 0.0].std(ddof=0))
    cagr = float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else math.nan
    mdd = float(drawdown.min())
    return {
        "start": str(r.index[0].date()),
        "end": str(r.index[-1].date()),
        "days": float(len(r)),
        "years": float(years),
        "cagr": cagr,
        "mdd": mdd,
        "sharpe": float(r.mean() / vol * math.sqrt(TRADING_DAYS_PER_YEAR)) if vol > 0 else math.nan,
        "sortino": float(r.mean() / downside * math.sqrt(TRADING_DAYS_PER_YEAR)) if downside > 0 else math.nan,
        "calmar": float(cagr / abs(mdd)) if mdd < 0 else math.nan,
        "terminal_wealth": float(equity.iloc[-1]),
    }


def _empty_metrics(returns: pd.Series) -> dict[str, float | str]:
    return {
        "start": str(returns.index[0].date()) if len(returns) else "",
        "end": str(returns.index[-1].date()) if len(returns) else "",
        "days": float(len(returns)),
        "years": float(len(returns) / TRADING_DAYS_PER_YEAR),
        "cagr": math.nan,
        "mdd": math.nan,
        "sharpe": math.nan,
        "sortino": math.nan,
        "calmar": math.nan,
        "terminal_wealth": math.nan,
    }


def score_portfolio(
    returns_frame: pd.DataFrame,
    weights: dict[str, float],
    *,
    rolling_step: int = 1,
    include_benchmarks: bool = True,
    benchmark_cache: BenchmarkCache | None = None,
    compute_drawdown: bool = True,
    growth_cache: GrowthCache | None = None,
) -> PortfolioScore:
    """Score a portfolio against SPY and QQQ rolling benchmarks."""
    strategy = monthly_rebalanced_returns(returns_frame, weights, growth_cache=growth_cache)
    core = None
    if set(CORE_35_40_25_WEIGHTS).issubset(set(returns_frame.columns)):
        core = monthly_rebalanced_returns(returns_frame, CORE_35_40_25_WEIGHTS, growth_cache=growth_cache)
    aligned = pd.concat(
        {
            "portfolio": strategy,
            "SPYSIM": returns_frame["SPYSIM"],
            "QQQSIM": returns_frame["QQQSIM"],
            **({"core_35_40_25": core} if core is not None else {}),
        },
        axis=1,
        sort=True,
    ).dropna()
    strategy = aligned["portfolio"]
    spy = aligned["SPYSIM"]
    qqq = aligned["QQQSIM"]
    core_aligned = aligned["core_35_40_25"] if "core_35_40_25" in aligned.columns else None

    rolling = rolling_summary(
        strategy,
        spy,
        qqq,
        core_aligned,
        rolling_step=rolling_step,
        benchmark_cache=benchmark_cache,
        compute_drawdown=compute_drawdown,
    )
    fitness = fitness_from_rolling(rolling)
    full_metrics = metrics_from_returns(strategy)
    benchmark_metrics = {}
    if include_benchmarks:
        benchmark_metrics = {
            "SPYSIM": metrics_from_returns(spy),
            "QQQSIM": metrics_from_returns(qqq),
        }
        if core_aligned is not None:
            benchmark_metrics["core_35_40_25"] = metrics_from_returns(core_aligned)
    spy_metrics = benchmark_metrics.get("SPYSIM") or metrics_from_returns(spy)
    fitness["spy_beater_mdd_guard"] = _apply_full_spy_mdd_guard(
        fitness.get("spy_beater_mdd_guard", math.nan),
        full_metrics.get("mdd", math.nan),
        spy_metrics.get("mdd", math.nan),
    )
    fitness["spy_beater_calmar_guard"] = _apply_full_spy_calmar_guard(
        fitness.get("spy_beater_calmar_guard", math.nan),
        full_metrics.get("cagr", math.nan),
        full_metrics.get("mdd", math.nan),
        spy_metrics.get("cagr", math.nan),
        spy_metrics.get("mdd", math.nan),
    )
    fitness["spy_beater_consistency_guard"] = _apply_full_spy_calmar_guard(
        fitness.get("spy_beater_consistency_guard", math.nan),
        full_metrics.get("cagr", math.nan),
        full_metrics.get("mdd", math.nan),
        spy_metrics.get("cagr", math.nan),
        spy_metrics.get("mdd", math.nan),
    )
    fitness["spy_beater_p10_mdd_guard"] = _apply_full_spy_calmar_guard(
        fitness.get("spy_beater_p10_mdd_guard", math.nan),
        full_metrics.get("cagr", math.nan),
        full_metrics.get("mdd", math.nan),
        spy_metrics.get("cagr", math.nan),
        spy_metrics.get("mdd", math.nan),
    )
    return PortfolioScore(
        weights=weights,
        full_metrics=full_metrics,
        benchmark_metrics=benchmark_metrics,
        rolling=rolling,
        fitness=fitness,
        exposure=portfolio_effective_exposure(weights),
    )


def rolling_summary(
    portfolio: pd.Series,
    spy: pd.Series,
    qqq: pd.Series,
    core: pd.Series | None = None,
    *,
    rolling_step: int = 1,
    benchmark_cache: BenchmarkCache | None = None,
    compute_drawdown: bool = True,
) -> dict[str, dict[str, float]]:
    aligned = pd.concat(
        {"p": portfolio, "spy": spy, "qqq": qqq, **({"core": core} if core is not None else {})},
        axis=1,
    ).dropna()
    out: dict[str, dict[str, float]] = {}
    cumulatives = {
        "p": _series_cumulatives(aligned["p"].to_numpy(dtype=float)),
        "spy": _series_cumulatives(aligned["spy"].to_numpy(dtype=float)),
        "qqq": _series_cumulatives(aligned["qqq"].to_numpy(dtype=float)),
    }
    if "core" in aligned.columns:
        cumulatives["core"] = _series_cumulatives(aligned["core"].to_numpy(dtype=float))
    for horizon, days in HORIZON_DAYS.items():
        if len(aligned) < days:
            continue
        starts = _rolling_starts(len(aligned), days, rolling_step)
        pm = _rolling_metrics_from_cumulatives(cumulatives["p"], days, starts, compute_drawdown=compute_drawdown)
        if benchmark_cache is not None and horizon in benchmark_cache:
            sm = benchmark_cache[horizon]["spy"]
            qm = benchmark_cache[horizon]["qqq"]
            cm = benchmark_cache[horizon].get("core")
        else:
            sm = _rolling_metrics_from_cumulatives(
                cumulatives["spy"], days, starts, compute_drawdown=compute_drawdown
            )
            qm = _rolling_metrics_from_cumulatives(
                cumulatives["qqq"], days, starts, compute_drawdown=compute_drawdown
            )
            cm = (
                _rolling_metrics_from_cumulatives(cumulatives["core"], days, starts, compute_drawdown=compute_drawdown)
                if "core" in cumulatives
                else None
            )
        data = {
            "cagr_spy_spread": pm["cagr"] - sm["cagr"],
            "cagr_qqq_spread": pm["cagr"] - qm["cagr"],
            "sharpe_spy_spread": pm["sharpe"] - sm["sharpe"],
            "sharpe_qqq_spread": pm["sharpe"] - qm["sharpe"],
            "sortino_spy_spread": pm["sortino"] - sm["sortino"],
            "sortino_qqq_spread": pm["sortino"] - qm["sortino"],
            "calmar_spy_spread": pm["calmar"] - sm["calmar"],
            "calmar_qqq_spread": pm["calmar"] - qm["calmar"],
            "wealth_spy_ratio_minus1": pm["terminal_wealth"] / sm["terminal_wealth"] - 1.0,
            "wealth_qqq_ratio_minus1": pm["terminal_wealth"] / qm["terminal_wealth"] - 1.0,
            "mdd_minus_spy_mdd": pm["mdd"] - sm["mdd"],
            "mdd_minus_qqq_mdd": pm["mdd"] - qm["mdd"],
        }
        if cm is not None:
            core_relative_wealth = pm["terminal_wealth"] / cm["terminal_wealth"] - 1.0
            data.update(
                {
                    "cagr_core_spread": pm["cagr"] - cm["cagr"],
                    "calmar_core_spread": pm["calmar"] - cm["calmar"],
                    "wealth_core_ratio_minus1": core_relative_wealth,
                    "mdd_minus_core_mdd": pm["mdd"] - cm["mdd"],
                    "wealth_core_win": (core_relative_wealth >= 0.0).astype(float),
                }
            )
        df = pd.DataFrame(data)
        out[horizon] = {"n_windows": float(len(df))}
        for col in df.columns:
            values = df[col].replace([np.inf, -np.inf], np.nan).dropna()
            if values.empty:
                out[horizon][col] = math.nan
                out[horizon][f"{col}_mean"] = math.nan
                out[horizon][f"{col}_median"] = math.nan
                out[horizon][f"{col}_p10"] = math.nan
                continue
            mean = float(values.mean())
            median = float(values.median())
            p10 = float(values.quantile(0.10))
            out[horizon][f"{col}_mean"] = mean
            out[horizon][f"{col}_median"] = median
            out[horizon][f"{col}_p10"] = p10
            out[horizon][f"{col}_latest"] = _last_finite(df[col])
            out[horizon][col] = 0.50 * mean + 0.25 * median + 0.25 * p10
    return out


def build_benchmark_cache(
    spy: pd.Series,
    qqq: pd.Series,
    core: pd.Series | None = None,
    *,
    rolling_step: int,
    compute_drawdown: bool = True,
) -> BenchmarkCache:
    """Precompute rolling benchmark metrics reused by every GA candidate."""
    aligned = pd.concat({"spy": spy, "qqq": qqq, **({"core": core} if core is not None else {})}, axis=1).dropna()
    cumulatives = {
        "spy": _series_cumulatives(aligned["spy"].to_numpy(dtype=float)),
        "qqq": _series_cumulatives(aligned["qqq"].to_numpy(dtype=float)),
    }
    if "core" in aligned.columns:
        cumulatives["core"] = _series_cumulatives(aligned["core"].to_numpy(dtype=float))
    cache: BenchmarkCache = {}
    for horizon, days in HORIZON_DAYS.items():
        if len(aligned) < days:
            continue
        starts = _rolling_starts(len(aligned), days, rolling_step)
        cache[horizon] = {
            "spy": _rolling_metrics_from_cumulatives(
                cumulatives["spy"], days, starts, compute_drawdown=compute_drawdown
            ),
            "qqq": _rolling_metrics_from_cumulatives(
                cumulatives["qqq"], days, starts, compute_drawdown=compute_drawdown
            ),
        }
        if "core" in cumulatives:
            cache[horizon]["core"] = _rolling_metrics_from_cumulatives(
                cumulatives["core"], days, starts, compute_drawdown=compute_drawdown
            )
    return cache


def _rolling_starts(n_rows: int, days: int, rolling_step: int) -> np.ndarray:
    """Sample rolling starts while always including the latest available window."""
    last_start = n_rows - days
    starts = np.arange(0, last_start + 1, rolling_step, dtype=int)
    if starts.size == 0 or starts[-1] != last_start:
        starts = np.append(starts, np.array([last_start], dtype=int))
    return starts


def _last_finite(values: pd.Series) -> float:
    clean = values.replace([np.inf, -np.inf], np.nan).dropna()
    return float(clean.iloc[-1]) if not clean.empty else math.nan


def _series_cumulatives(returns: np.ndarray) -> dict[str, np.ndarray]:
    """Pre-cumulate per-series arrays once so per-horizon scoring is O(n_starts)."""
    logs = np.log1p(returns)
    neg = np.where(returns < 0.0, returns, 0.0)
    return {
        "log_cum": np.concatenate([[0.0], np.cumsum(logs)]),
        "sum_cum": np.concatenate([[0.0], np.cumsum(returns)]),
        "sumsq_cum": np.concatenate([[0.0], np.cumsum(returns * returns)]),
        "neg_cum": np.concatenate([[0.0], np.cumsum(neg)]),
        "negsq_cum": np.concatenate([[0.0], np.cumsum(np.where(returns < 0.0, returns * returns, 0.0))]),
        "negcount_cum": np.concatenate([[0.0], np.cumsum((returns < 0.0).astype(float))]),
    }


# Target ~128KB working set per chunk so the temp 2D arrays stay close to L2-resident.
# For very long horizons (20y ≈ 5040 days) this falls back to single-window-per-chunk, which
# is dominated by NumPy intrinsics rather than Python overhead.
_MDD_CHUNK_BYTES_TARGET = 128 * 1024


def _mdd_chunk_size(days: int) -> int:
    estimate = _MDD_CHUNK_BYTES_TARGET // max(1, 8 * (days + 1))
    return max(8, min(4096, estimate))


def _vectorized_mdd(log_cum: np.ndarray, days: int, starts: np.ndarray) -> np.ndarray:
    """Per-window max drawdown computed in log-space with cache-aware chunking."""
    n_starts = starts.shape[0]
    if n_starts == 0:
        return np.empty(0, dtype=float)
    chunk = _mdd_chunk_size(days)
    mdd = np.empty(n_starts, dtype=float)
    offsets = np.arange(days + 1, dtype=np.int64)
    for chunk_start in range(0, n_starts, chunk):
        sub = starts[chunk_start : chunk_start + chunk]
        window_log = log_cum[sub[:, None] + offsets[None, :]]
        window_log -= window_log[:, :1]
        body = window_log[:, 1:]
        running_log_max = np.maximum.accumulate(body, axis=1)
        body -= running_log_max
        log_dd_min = body.min(axis=1)
        mdd[chunk_start : chunk_start + sub.shape[0]] = np.expm1(log_dd_min)
    return mdd


def _rolling_metrics_from_cumulatives(
    cumulatives: dict[str, np.ndarray],
    days: int,
    starts: np.ndarray,
    *,
    compute_drawdown: bool = True,
) -> dict[str, np.ndarray]:
    """Compute rolling metrics using cumulative arrays computed once per series."""
    ends = starts + days
    log_cum = cumulatives["log_cum"]
    sum_cum = cumulatives["sum_cum"]
    sumsq_cum = cumulatives["sumsq_cum"]
    neg_cum = cumulatives["neg_cum"]
    negsq_cum = cumulatives["negsq_cum"]
    negcount_cum = cumulatives["negcount_cum"]

    log_total = log_cum[ends] - log_cum[starts]
    terminal = np.exp(log_total)
    years = days / TRADING_DAYS_PER_YEAR
    cagr = np.power(terminal, 1.0 / years) - 1.0

    sums = sum_cum[ends] - sum_cum[starts]
    sumsqs = sumsq_cum[ends] - sumsq_cum[starts]
    mean = sums / days
    var = np.maximum(sumsqs / days - mean * mean, 0.0)
    std = np.sqrt(var)
    sharpe = np.divide(
        mean * math.sqrt(TRADING_DAYS_PER_YEAR),
        std,
        out=np.full_like(mean, np.nan),
        where=std > 0,
    )

    neg_counts = negcount_cum[ends] - negcount_cum[starts]
    neg_sums = neg_cum[ends] - neg_cum[starts]
    neg_sumsqs = negsq_cum[ends] - negsq_cum[starts]
    neg_mean = np.divide(neg_sums, neg_counts, out=np.zeros_like(neg_sums), where=neg_counts > 0)
    downside_var = np.maximum(
        np.divide(neg_sumsqs, neg_counts, out=np.zeros_like(neg_sumsqs), where=neg_counts > 0)
        - neg_mean * neg_mean,
        0.0,
    )
    downside = np.sqrt(downside_var)
    sortino = np.divide(
        mean * math.sqrt(TRADING_DAYS_PER_YEAR),
        downside,
        out=np.full_like(mean, np.nan),
        where=downside > 0,
    )

    if compute_drawdown:
        mdd = _vectorized_mdd(log_cum, days, starts)
        calmar = np.divide(cagr, np.abs(mdd), out=np.full_like(cagr, np.nan), where=mdd < 0)
    else:
        # Honest semantics: fast-discovery skips drawdown entirely. Downstream weighting
        # and `_balanced` both treat NaN as "not contributing" instead of biasing toward
        # zero spreads `[testing_tuning, p.327-335]`.
        mdd = np.full(len(starts), np.nan, dtype=float)
        calmar = np.full(len(starts), np.nan, dtype=float)
    return {
        "cagr": cagr,
        "mdd": mdd,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "terminal_wealth": terminal,
    }


def _rolling_metrics_array(
    returns: np.ndarray,
    days: int,
    starts: np.ndarray,
    *,
    compute_drawdown: bool = True,
) -> dict[str, np.ndarray]:
    """Legacy entry point retained for external callers; delegates to the cumulative path."""
    return _rolling_metrics_from_cumulatives(
        _series_cumulatives(returns),
        days,
        starts,
        compute_drawdown=compute_drawdown,
    )


def fitness_from_rolling(rolling: dict[str, dict[str, float]]) -> dict[str, float]:
    def weighted(metric: str) -> float:
        total = 0.0
        weight_sum = 0.0
        for horizon, weight in HORIZON_WEIGHTS.items():
            value = rolling.get(horizon, {}).get(metric, math.nan)
            if pd.notna(value):
                total += weight * float(value)
                weight_sum += weight
        return total / weight_sum if weight_sum else math.nan

    cagr_spy = _clip(weighted("cagr_spy_spread"), -1.0, 1.0)
    cagr_qqq = _clip(weighted("cagr_qqq_spread"), -1.0, 1.0)
    sharpe_spy = _clip(weighted("sharpe_spy_spread"), -5.0, 5.0)
    sortino_spy = _clip(weighted("sortino_spy_spread"), -5.0, 5.0)
    sortino_qqq = _clip(weighted("sortino_qqq_spread"), -5.0, 5.0)
    calmar_spy = _clip(weighted("calmar_spy_spread"), -5.0, 5.0)
    calmar_qqq = _clip(weighted("calmar_qqq_spread"), -5.0, 5.0)
    wealth_spy = _clip(weighted("wealth_spy_ratio_minus1"), -1.0, 10.0)
    wealth_qqq = _clip(weighted("wealth_qqq_ratio_minus1"), -1.0, 10.0)
    wealth_core = _clip(weighted("wealth_core_ratio_minus1"), -1.0, 10.0)
    cagr_core = _clip(weighted("cagr_core_spread"), -1.0, 1.0)
    calmar_core = _clip(weighted("calmar_core_spread"), -5.0, 5.0)
    mdd_core = _clip(weighted("mdd_minus_core_mdd"), -1.0, 1.0)
    win_core = _clip(weighted("wealth_core_win"), 0.0, 1.0)
    mdd_spy = _clip(weighted("mdd_minus_spy_mdd"), -1.0, 1.0)
    mdd_qqq = _clip(weighted("mdd_minus_qqq_mdd"), -1.0, 1.0)
    worst_cagr_p10 = _worst_horizon_metric(rolling, "cagr_spy_spread_p10", min_horizon="3y")
    worst_wealth_p10 = _worst_horizon_metric(rolling, "wealth_spy_ratio_minus1_p10", min_horizon="3y")
    worst_mdd_p10 = _worst_horizon_metric(rolling, "mdd_minus_spy_mdd_p10", min_horizon="3y")
    worst_mdd_p10_5y = _worst_horizon_metric(rolling, "mdd_minus_spy_mdd_p10", min_horizon="5y")
    worst_core_wealth_p10_5y = _worst_horizon_metric(rolling, "wealth_core_ratio_minus1_p10", min_horizon="5y")
    worst_core_cagr_p10_5y = _worst_horizon_metric(rolling, "cagr_core_spread_p10", min_horizon="5y")
    latest_3y_cagr = _clip(rolling.get("3y", {}).get("cagr_spy_spread_latest", math.nan), -1.0, 1.0)
    latest_3y_wealth = _clip(rolling.get("3y", {}).get("wealth_spy_ratio_minus1_latest", math.nan), -1.0, 10.0)
    latest_3y_mdd = _clip(rolling.get("3y", {}).get("mdd_minus_spy_mdd_latest", math.nan), -1.0, 1.0)
    min_regret = min(
        [
            _clip(rolling[h].get("wealth_spy_ratio_minus1_p10", math.nan), -1.0, 10.0)
            for h in rolling
            if pd.notna(rolling[h].get("wealth_spy_ratio_minus1_p10", math.nan))
        ]
        or [math.nan]
    )
    return {
        "cagr_robust": cagr_spy,
        "sharpe_robust": sharpe_spy,
        "sortino_robust": sortino_spy,
        "calmar_robust": calmar_spy,
        "relative_wealth_spy": wealth_spy,
        "relative_wealth_qqq": wealth_qqq,
        "core_relative_wealth_dominance": _core_relative_wealth_dominance(
            cagr_core,
            wealth_core,
            calmar_core,
            mdd_core,
            win_core,
            worst_core_wealth_p10_5y,
            worst_core_cagr_p10_5y,
        ),
        "balanced_spy_beater": _balanced(cagr_spy, calmar_spy, sortino_spy, wealth_spy, mdd_spy),
        "spy_beater_mdd_guard": _spy_beater_mdd_guard(cagr_spy, wealth_spy, sharpe_spy, mdd_spy),
        "spy_beater_calmar_guard": _spy_beater_calmar_guard(cagr_spy, wealth_spy, calmar_spy, mdd_spy),
        "spy_beater_consistency_guard": _spy_beater_consistency_guard(
            cagr_spy,
            wealth_spy,
            calmar_spy,
            mdd_spy,
            worst_cagr_p10,
            worst_wealth_p10,
            worst_mdd_p10,
            latest_3y_cagr,
            latest_3y_wealth,
            latest_3y_mdd,
        ),
        "spy_beater_p10_mdd_guard": _spy_beater_p10_mdd_guard(
            cagr_spy,
            wealth_spy,
            calmar_spy,
            mdd_spy,
            worst_cagr_p10,
            worst_wealth_p10,
            worst_mdd_p10_5y,
            latest_3y_cagr,
            latest_3y_wealth,
            latest_3y_mdd,
        ),
        "balanced_dual_beater": _balanced(
            min(cagr_spy, cagr_qqq),
            min(calmar_spy, calmar_qqq),
            min(sortino_spy, sortino_qqq),
            min(wealth_spy, wealth_qqq),
            min(mdd_spy, mdd_qqq),
        ),
        "min_regret": float(min_regret),
    }


def _worst_horizon_metric(
    rolling: dict[str, dict[str, float]],
    metric: str,
    *,
    min_horizon: str,
) -> float:
    min_days = HORIZON_DAYS[min_horizon]
    values = [
        _clip(data.get(metric, math.nan), -1.0, 10.0)
        for horizon, data in rolling.items()
        if HORIZON_DAYS.get(horizon, 0) >= min_days and pd.notna(data.get(metric, math.nan))
    ]
    return float(min(values)) if values else math.nan


def _balanced(cagr: float, calmar: float, sortino: float, wealth: float, mdd_delta: float) -> float:
    """Balanced beater score that cannot be won by defensive underperformance.

    Calmar/Sortino can explode for cash-like portfolios. They are useful only after
    the portfolio is at least competitive on return/wealth, so positive risk-adjusted
    terms are muted when relative CAGR or relative wealth is negative
    `[testing_tuning, p.327-335]`.
    """
    if pd.isna(cagr) or pd.isna(wealth):
        return math.nan
    downside_penalty = min(0.0, cagr) * 2.0 + min(0.0, wealth) * 1.0
    risk_credit_scale = 1.0 if cagr > 0.0 and wealth > 0.0 else 0.0
    safe_calmar = 0.0 if pd.isna(calmar) else calmar
    safe_sortino = 0.0 if pd.isna(sortino) else sortino
    risk_credit = risk_credit_scale * (0.12 * safe_calmar + 0.08 * safe_sortino)
    mdd_credit = 0.10 * mdd_delta if pd.notna(mdd_delta) else 0.0
    return 0.40 * wealth + 0.30 * cagr + risk_credit + mdd_credit + downside_penalty


def _core_relative_wealth_dominance(
    cagr: float,
    wealth: float,
    calmar: float,
    mdd_delta: float,
    win_rate: float,
    worst_wealth_p10_5y: float,
    worst_cagr_p10_5y: float,
) -> float:
    """Score dominance versus the no-margin core benchmark.

    The core question is whether candidate equity beats benchmark equity across most
    rolling windows. MDD is a penalty/guardrail rather than the primary objective so
    high-return portfolios are not discarded solely for tolerable drawdown expansion
    `[testing_tuning, p.327-335]`, `[leverage_for_the_long_run, p.13]`.
    """
    values = [cagr, wealth, calmar, mdd_delta, win_rate, worst_wealth_p10_5y, worst_cagr_p10_5y]
    if any(pd.isna(value) for value in values):
        return math.nan
    p10_penalty = 1.50 * min(0.0, worst_wealth_p10_5y) + 1.00 * min(0.0, worst_cagr_p10_5y)
    mdd_penalty = 0.75 * min(0.0, mdd_delta)
    win_penalty = 1.50 * min(0.0, win_rate - 0.70)
    return (
        0.35 * win_rate
        + 0.25 * wealth
        + 0.20 * worst_wealth_p10_5y
        + 0.10 * cagr
        + 0.05 * calmar
        + 0.05 * max(0.0, mdd_delta)
        + p10_penalty
        + mdd_penalty
        + win_penalty
    )


def _spy_beater_mdd_guard(cagr: float, wealth: float, sharpe: float, mdd_delta: float) -> float:
    """SPY-beater score with hard preference for no worse drawdown than SPY.

    `mdd_delta` is portfolio MDD minus SPY MDD, so positive is better/shallower.
    The score prioritizes relative wealth and CAGR, but strongly penalizes MDD worse
    than SPY to search for long-term efficient beaters rather than pure leverage
    `[testing_tuning, p.327-335]`.
    """
    if pd.isna(cagr) or pd.isna(wealth) or pd.isna(mdd_delta):
        return math.nan
    return_gate_penalty = 2.0 * min(0.0, cagr) + 1.5 * min(0.0, wealth)
    mdd_penalty = 4.0 * min(0.0, mdd_delta)
    mdd_credit = 0.25 * max(0.0, mdd_delta)
    sharpe_credit = 0.05 * (0.0 if pd.isna(sharpe) else sharpe)
    return 0.45 * wealth + 0.35 * cagr + mdd_credit + sharpe_credit + return_gate_penalty + mdd_penalty


def _spy_beater_calmar_guard(cagr: float, wealth: float, calmar: float, mdd_delta: float) -> float:
    """Calmar-led SPY beater score gated by SPY drawdown feasibility.

    Calmar is useful only after requiring SPY-competitive return and drawdown. The
    full-period feasibility guard is applied after full metrics are available; this
    rolling score ranks viable candidates by Calmar spread, then relative CAGR and
    wealth `[testing_tuning, p.327-335]`.
    """
    if pd.isna(cagr) or pd.isna(wealth) or pd.isna(calmar) or pd.isna(mdd_delta):
        return math.nan
    return_gate_penalty = 2.0 * min(0.0, cagr) + 1.5 * min(0.0, wealth)
    mdd_penalty = 3.0 * min(0.0, mdd_delta)
    mdd_credit = 0.10 * max(0.0, mdd_delta)
    return 0.60 * calmar + 0.25 * cagr + 0.15 * wealth + mdd_credit + return_gate_penalty + mdd_penalty


def _spy_beater_consistency_guard(
    cagr: float,
    wealth: float,
    calmar: float,
    mdd_delta: float,
    worst_cagr_p10: float,
    worst_wealth_p10: float,
    worst_mdd_p10: float,
    latest_3y_cagr: float,
    latest_3y_wealth: float,
    latest_3y_mdd: float,
) -> float:
    """Window-consistency score for portfolios that should survive regime changes.

    This is stricter than full-period Calmar: it requires the latest 3y window to beat
    SPY and penalizes poor 10th-percentile rolling outcomes across 3y+ horizons, so a
    HFEA-like death window cannot be hidden by strong early history
    `[testing_tuning, p.327-335]`, `[risk_parity, p.80-81]`.
    """
    values = [
        cagr,
        wealth,
        calmar,
        mdd_delta,
        worst_cagr_p10,
        worst_wealth_p10,
        worst_mdd_p10,
        latest_3y_cagr,
        latest_3y_wealth,
        latest_3y_mdd,
    ]
    if any(pd.isna(value) for value in values):
        return math.nan
    if latest_3y_cagr <= 0.0 or latest_3y_wealth <= 0.0:
        return -0.75 + 3.0 * min(latest_3y_cagr, latest_3y_wealth)
    p10_penalty = 2.0 * min(0.0, worst_cagr_p10) + 0.75 * min(0.0, worst_wealth_p10)
    mdd_penalty = 1.5 * min(0.0, worst_mdd_p10) + 2.0 * min(0.0, latest_3y_mdd)
    consistency_credit = 0.15 * max(0.0, worst_cagr_p10) + 0.10 * max(0.0, latest_3y_mdd)
    return (
        0.35 * calmar
        + 0.20 * cagr
        + 0.15 * wealth
        + 0.20 * latest_3y_cagr
        + 0.10 * latest_3y_wealth
        + consistency_credit
        + p10_penalty
        + mdd_penalty
    )


def _spy_beater_p10_mdd_guard(
    cagr: float,
    wealth: float,
    calmar: float,
    mdd_delta: float,
    worst_cagr_p10: float,
    worst_wealth_p10: float,
    worst_mdd_p10_5y: float,
    latest_3y_cagr: float,
    latest_3y_wealth: float,
    latest_3y_mdd: float,
) -> float:
    """Strict consistency score requiring 5y+ p10 drawdown no worse than SPY.

    The full-period guard is applied later. Here, any negative 5y+ p10 MDD spread is
    rejected so the GA must search for candidates whose bad rolling drawdown windows
    are SPY-compatible, not merely acceptable on average `[testing_tuning, p.327-335]`.
    """
    values = [
        cagr,
        wealth,
        calmar,
        mdd_delta,
        worst_cagr_p10,
        worst_wealth_p10,
        worst_mdd_p10_5y,
        latest_3y_cagr,
        latest_3y_wealth,
        latest_3y_mdd,
    ]
    if any(pd.isna(value) for value in values):
        return math.nan
    if latest_3y_cagr <= 0.0 or latest_3y_wealth <= 0.0:
        return -0.75 + 3.0 * min(latest_3y_cagr, latest_3y_wealth)
    if worst_mdd_p10_5y < 0.0:
        return -0.25 + 5.0 * worst_mdd_p10_5y
    p10_penalty = 2.0 * min(0.0, worst_cagr_p10) + 0.75 * min(0.0, worst_wealth_p10)
    return (
        0.30 * calmar
        + 0.20 * cagr
        + 0.15 * wealth
        + 0.15 * latest_3y_cagr
        + 0.10 * latest_3y_wealth
        + 0.10 * worst_mdd_p10_5y
        + 0.10 * max(0.0, latest_3y_mdd)
        + p10_penalty
    )


def _apply_full_spy_mdd_guard(score: float, portfolio_mdd: float | str, spy_mdd: float | str) -> float:
    """Reject portfolios whose full-period MDD is worse than SPY.

    MDD values are negative, so `portfolio_mdd >= spy_mdd` means the portfolio's
    worst drawdown is no worse than SPY. This turns the MDD requirement into a hard
    feasibility guard instead of a soft preference, reducing leverage-driven false
    positives `[testing_tuning, p.327-335]`.
    """
    if pd.isna(score) or pd.isna(portfolio_mdd) or pd.isna(spy_mdd):
        return math.nan
    full_mdd_delta = float(portfolio_mdd) - float(spy_mdd)
    if full_mdd_delta < 0.0:
        return -1.0 + 4.0 * full_mdd_delta
    return float(score) + 0.25 * full_mdd_delta


def _apply_full_spy_calmar_guard(
    score: float,
    portfolio_cagr: float | str,
    portfolio_mdd: float | str,
    spy_cagr: float | str,
    spy_mdd: float | str,
) -> float:
    """Reject portfolios that fail full-period SPY CAGR or MDD guards.

    The objective can then safely maximize Calmar-like efficiency without selecting
    low-return defensive portfolios or high-return portfolios with deeper full-period
    drawdowns than SPY `[testing_tuning, p.327-335]`.
    """
    if (
        pd.isna(score)
        or pd.isna(portfolio_cagr)
        or pd.isna(portfolio_mdd)
        or pd.isna(spy_cagr)
        or pd.isna(spy_mdd)
    ):
        return math.nan
    full_mdd_delta = float(portfolio_mdd) - float(spy_mdd)
    full_cagr_delta = float(portfolio_cagr) - float(spy_cagr)
    if full_mdd_delta < 0.0:
        return -1.0 + 4.0 * full_mdd_delta
    if full_cagr_delta <= 0.0:
        return -0.5 + 4.0 * full_cagr_delta
    return float(score) + 0.20 * full_mdd_delta + 0.20 * full_cagr_delta


def _clip(value: float, low: float, high: float) -> float:
    if pd.isna(value):
        return math.nan
    return float(np.clip(float(value), low, high))


def _diff(a: float | str, b: float | str) -> float:
    return float(a) - float(b) if pd.notna(a) and pd.notna(b) else math.nan


def _ratio_minus1(a: float | str, b: float | str) -> float:
    if pd.isna(a) or pd.isna(b) or float(b) == 0.0:
        return math.nan
    return float(a) / float(b) - 1.0


def score_named_benchmarks(
    universe: str,
    returns_frame: pd.DataFrame,
    rolling_step: int,
    benchmark_cache: BenchmarkCache | None = None,
    compute_drawdown: bool = True,
    growth_cache: GrowthCache | None = None,
) -> dict[str, PortfolioScore]:
    benchmarks: dict[str, dict[str, float]] = {}
    if "SPYSIM" in returns_frame.columns:
        benchmarks["spy_buy_hold"] = {"SPYSIM": 1.0}
    if "QQQSIM" in returns_frame.columns:
        benchmarks["qqq_buy_hold"] = {"QQQSIM": 1.0}
    benchmarks["equal_weight"] = equal_weight_for_universe(universe)
    if has_b4(universe):
        benchmarks["b4"] = B4_WEIGHTS
    if set(CORE_35_40_25_WEIGHTS).issubset(set(returns_frame.columns)):
        benchmarks["core_35_40_25"] = CORE_35_40_25_WEIGHTS
    return {
        name: score_portfolio(
            returns_frame,
            weights,
            rolling_step=rolling_step,
            include_benchmarks=False,
            benchmark_cache=benchmark_cache,
            compute_drawdown=compute_drawdown,
            growth_cache=growth_cache,
        )
        for name, weights in benchmarks.items()
    }


def score_to_dict(score: PortfolioScore) -> dict:
    return {
        "weights": score.weights,
        "full_metrics": score.full_metrics,
        "benchmark_metrics": score.benchmark_metrics,
        "rolling": score.rolling,
        "fitness": score.fitness,
        "exposure": score.exposure,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", required=True)
    parser.add_argument("--weights", required=True, help='JSON object, e.g. {"SPYSIM":0.5,"ZROZSIM":0.5}')
    parser.add_argument("--rolling-step", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    frame = load_universe_returns(args.universe)
    weights = json.loads(args.weights)
    score = score_portfolio(frame, weights, rolling_step=args.rolling_step)
    payload = score_to_dict(score)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
