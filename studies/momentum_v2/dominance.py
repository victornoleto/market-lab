"""Rolling relative-equity dominance and crisis-window diagnostics.

Ported from ``studies/momentum_13612_universes`` (``extensive.py`` rolling
relative-equity metrics and ``run_stocks_heatmap.py`` crisis windows). These
are the *primary finalist-selection lens* for momentum_v2: they measure how
consistently ``equity / equity_benchmark`` stays above 1.0 across rolling
start dates rather than rewarding a single lucky end-point `[testing_tuning,
p.327-335]`. Stress windows are diagnostics, not fitted parameters.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from market_lab.backtest.validation.walk_forward import walk_forward_splits
from studies.momentum_v2.core import (
    TRADING_DAYS_PER_YEAR,
    equity_from_returns,
    metrics_from_returns,
)

RELATIVE_EQUITY_HORIZONS = (3, 5, 10, 15, 20)
RELATIVE_EQUITY_WEIGHTS = {3: 0.10, 5: 0.15, 10: 0.25, 15: 0.25, 20: 0.25}

# Stress windows are diagnostics, not fitted parameters `[testing_tuning, p.327-335]`.
CRISIS_WINDOWS = {
    "dotcom": ("2000-03-01", "2002-10-31"),
    "gfc": ("2007-10-01", "2009-03-31"),
    "covid": ("2020-02-01", "2020-04-30"),
    "rates2022": ("2022-01-01", "2022-10-31"),
}


def relative_equity_metrics(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> dict[str, float]:
    """Strategy-vs-benchmark equity diagnostics over the full period."""
    if strategy_returns.empty or benchmark_returns.empty:
        return {
            "pct_time_above_benchmark": float("nan"),
            "min_relative_equity": float("nan"),
            "terminal_relative": float("nan"),
        }
    strategy_eq = equity_from_returns(strategy_returns, start_value=1.0)
    benchmark_eq = equity_from_returns(benchmark_returns, start_value=1.0)
    aligned = pd.concat({"strategy": strategy_eq, "benchmark": benchmark_eq}, axis=1).dropna()
    ratio = aligned["strategy"] / aligned["benchmark"]
    post = ratio.iloc[min(252, max(len(ratio) - 1, 0)) :]
    if post.empty:
        post = ratio
    return {
        "pct_time_above_benchmark": float((post > 1.0).mean()),
        "min_relative_equity": float(post.min()),
        "terminal_relative": float(ratio.iloc[-1]),
    }


def rolling_relative_equity_windows(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    horizon_years: int,
) -> pd.DataFrame:
    """Monthly rolling relative-equity windows reset at each start date.

    Each window compares growth of ``$1`` in the strategy vs ``$1`` in the
    benchmark from the same start date, so prior outperformance cannot mask a
    weak later start `[testing_tuning, p.327-335]`.
    """
    if horizon_years <= 0:
        raise ValueError("horizon_years must be positive")
    aligned = pd.concat(
        {
            "strategy": strategy_returns.dropna().astype(float),
            "benchmark": benchmark_returns.dropna().astype(float),
        },
        axis=1,
    ).dropna()
    columns = [
        "start", "end", "n_obs", "pct_time_above_benchmark",
        "terminal_relative", "min_relative_equity", "relative_mdd",
    ]
    if aligned.empty:
        return pd.DataFrame(columns=columns)

    first_month_end = aligned.index[0].to_period("M").to_timestamp("M")
    last_date = pd.Timestamp(aligned.index[-1])
    starts = pd.date_range(first_month_end, last_date, freq="ME")
    rows: list[dict[str, object]] = []
    min_obs = int(horizon_years * TRADING_DAYS_PER_YEAR * 0.75)
    for start in starts:
        end = pd.Timestamp(start) + pd.DateOffset(years=horizon_years)
        if end > last_date:
            continue
        window = aligned.loc[(aligned.index > start) & (aligned.index <= end)]
        if len(window) < min_obs:
            continue
        strategy_eq = (1.0 + window["strategy"]).cumprod()
        benchmark_eq = (1.0 + window["benchmark"]).cumprod()
        ratio_body = strategy_eq / benchmark_eq
        ratio = pd.concat([pd.Series([1.0], index=[pd.Timestamp(start)]), ratio_body])
        relative_drawdown = ratio / ratio.cummax() - 1.0
        rows.append(
            {
                "start": pd.Timestamp(start),
                "end": pd.Timestamp(end),
                "n_obs": int(len(window)),
                "pct_time_above_benchmark": float((ratio >= 1.0).mean()),
                "terminal_relative": float(ratio.iloc[-1]),
                "min_relative_equity": float(ratio.min()),
                "relative_mdd": float(relative_drawdown.min()),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def empty_rolling_relative_equity_metrics(
    horizons: tuple[int, ...] = RELATIVE_EQUITY_HORIZONS,
) -> dict[str, float]:
    out = {
        "rolling_rel_score": float("nan"),
        "rolling_rel_p25_score": float("nan"),
        "rolling_rel_min_score": float("nan"),
    }
    for horizon in horizons:
        prefix = f"rel_{horizon}y"
        out.update(
            {
                f"{prefix}_windows": 0.0,
                f"{prefix}_above_mean": float("nan"),
                f"{prefix}_above_p25": float("nan"),
                f"{prefix}_above_min": float("nan"),
                f"{prefix}_terminal_median": float("nan"),
                f"{prefix}_min_relative_p25": float("nan"),
                f"{prefix}_relative_mdd_median": float("nan"),
            }
        )
    return out


def rolling_relative_equity_metrics(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    horizons: tuple[int, ...] = RELATIVE_EQUITY_HORIZONS,
    weights: dict[int, float] | None = None,
) -> dict[str, float]:
    """Aggregate monthly rolling strategy/benchmark dominance diagnostics.

    The horizon score is the mean percentage of days where the reset relative
    equity curve is at or above ``1.0``. Longer horizons get larger default
    weights to emphasize durable dominance over short noisy windows
    `[testing_tuning, p.327-335]`.
    """
    weights = weights or RELATIVE_EQUITY_WEIGHTS
    out = empty_rolling_relative_equity_metrics(horizons)
    weighted_means: list[tuple[float, float]] = []
    weighted_p25: list[tuple[float, float]] = []
    horizon_mins: list[float] = []

    for horizon in horizons:
        windows = rolling_relative_equity_windows(strategy_returns, benchmark_returns, horizon)
        prefix = f"rel_{horizon}y"
        out[f"{prefix}_windows"] = float(len(windows))
        if windows.empty:
            continue
        above = windows["pct_time_above_benchmark"].to_numpy(dtype=float)
        terminals = windows["terminal_relative"].to_numpy(dtype=float)
        mins = windows["min_relative_equity"].to_numpy(dtype=float)
        relative_mdds = windows["relative_mdd"].to_numpy(dtype=float)
        above_mean = float(np.nanmean(above))
        above_p25 = float(np.nanpercentile(above, 25))
        above_min = float(np.nanmin(above))
        out.update(
            {
                f"{prefix}_above_mean": above_mean,
                f"{prefix}_above_p25": above_p25,
                f"{prefix}_above_min": above_min,
                f"{prefix}_terminal_median": float(np.nanmedian(terminals)),
                f"{prefix}_min_relative_p25": float(np.nanpercentile(mins, 25)),
                f"{prefix}_relative_mdd_median": float(np.nanmedian(relative_mdds)),
            }
        )
        weight = float(weights.get(horizon, 0.0))
        if weight > 0.0:
            weighted_means.append((above_mean, weight))
            weighted_p25.append((above_p25, weight))
        horizon_mins.append(above_min)

    if weighted_means:
        total = sum(weight for _value, weight in weighted_means)
        out["rolling_rel_score"] = sum(value * weight for value, weight in weighted_means) / total
    if weighted_p25:
        total = sum(weight for _value, weight in weighted_p25)
        out["rolling_rel_p25_score"] = sum(value * weight for value, weight in weighted_p25) / total
    if horizon_mins:
        out["rolling_rel_min_score"] = float(np.nanmin(horizon_mins))
    return out


def window_metrics(returns: pd.Series, start: str, end: str, prefix: str) -> dict[str, float]:
    """CAGR/MDD/Sharpe inside one crisis window."""
    window = returns.loc[pd.Timestamp(start): pd.Timestamp(end)].dropna().astype(float)
    if window.empty:
        return {f"{prefix}_cagr": float("nan"), f"{prefix}_mdd": float("nan"), f"{prefix}_sharpe": float("nan")}
    metrics = metrics_from_returns(window)
    return {
        f"{prefix}_cagr": float(metrics["cagr"]),
        f"{prefix}_mdd": float(metrics["mdd"]),
        f"{prefix}_sharpe": float(metrics["sharpe"]),
    }


def crisis_columns(strategy_returns: pd.Series, bench_returns: pd.Series) -> dict[str, float]:
    """Per-crisis CAGR/MDD/Sharpe for strategy and benchmark, plus MDD delta."""
    out: dict[str, float] = {}
    for label, (start, end) in CRISIS_WINDOWS.items():
        out.update(window_metrics(strategy_returns, start, end, label))
        out.update(window_metrics(bench_returns, start, end, f"{label}_spy"))
        if math.isfinite(out[f"{label}_mdd"]) and math.isfinite(out[f"{label}_spy_mdd"]):
            out[f"{label}_mdd_delta"] = out[f"{label}_mdd"] - out[f"{label}_spy_mdd"]
        else:
            out[f"{label}_mdd_delta"] = float("nan")
    return out


def walk_forward_diagnostic(returns: pd.Series) -> dict[str, float]:
    """Compact 8-window positive-OOS diagnostic (cheap broad-phase screen)."""
    n = len(returns)
    window = n // 9
    if window < 63:
        return {"wf_windows": 0.0, "wf_positive": 0.0, "wf_pass": 0.0}
    oos_returns: list[float] = []
    for _, test_range in walk_forward_splits(n, window, window, window):
        r = returns.iloc[list(test_range)]
        oos_returns.append(float((1.0 + r).prod() - 1.0))
        if len(oos_returns) >= 8:
            break
    positive = sum(value > 0.0 for value in oos_returns)
    return {
        "wf_windows": float(len(oos_returns)),
        "wf_positive": float(positive),
        "wf_pass": float(len(oos_returns) >= 8 and positive >= 6),
    }
