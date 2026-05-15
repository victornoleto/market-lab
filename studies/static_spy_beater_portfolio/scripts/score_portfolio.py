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

from studies.static_spy_beater_portfolio.scripts.universe import (
    B4_WEIGHTS,
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


def monthly_rebalanced_returns(asset_returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Return monthly rebalanced daily returns for static weights."""
    aligned = asset_returns[list(weights)].dropna()
    if aligned.empty:
        raise ValueError("portfolio has no aligned returns")
    target = pd.Series(weights, dtype=float)
    holdings = target.copy()
    value = 1.0
    current_month: tuple[int, int] | None = None
    out: list[float] = []
    dates: list[pd.Timestamp] = []
    for date, row in aligned.iterrows():
        month = (date.year, date.month)
        if month != current_month:
            holdings = target * value
            current_month = month
        previous = value
        holdings = holdings * (1.0 + row[holdings.index])
        value = float(holdings.sum())
        out.append(value / previous - 1.0)
        dates.append(date)
    return pd.Series(out, index=pd.DatetimeIndex(dates), name="portfolio")


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
) -> PortfolioScore:
    """Score a portfolio against SPY and QQQ rolling benchmarks."""
    strategy = monthly_rebalanced_returns(returns_frame, weights)
    aligned = pd.concat(
        {
            "portfolio": strategy,
            "SPYSIM": returns_frame["SPYSIM"],
            "QQQSIM": returns_frame["QQQSIM"],
        },
        axis=1,
        sort=True,
    ).dropna()
    strategy = aligned["portfolio"]
    spy = aligned["SPYSIM"]
    qqq = aligned["QQQSIM"]

    rolling = rolling_summary(strategy, spy, qqq, rolling_step=rolling_step)
    fitness = fitness_from_rolling(rolling)
    benchmark_metrics = {}
    if include_benchmarks:
        benchmark_metrics = {
            "SPYSIM": metrics_from_returns(spy),
            "QQQSIM": metrics_from_returns(qqq),
        }
    return PortfolioScore(
        weights=weights,
        full_metrics=metrics_from_returns(strategy),
        benchmark_metrics=benchmark_metrics,
        rolling=rolling,
        fitness=fitness,
        exposure=portfolio_effective_exposure(weights),
    )


def rolling_summary(
    portfolio: pd.Series,
    spy: pd.Series,
    qqq: pd.Series,
    *,
    rolling_step: int = 1,
) -> dict[str, dict[str, float]]:
    aligned = pd.concat({"p": portfolio, "spy": spy, "qqq": qqq}, axis=1).dropna()
    out: dict[str, dict[str, float]] = {}
    arrays = {
        "p": aligned["p"].to_numpy(dtype=float),
        "spy": aligned["spy"].to_numpy(dtype=float),
        "qqq": aligned["qqq"].to_numpy(dtype=float),
    }
    for horizon, days in HORIZON_DAYS.items():
        if len(aligned) < days:
            continue
        starts = np.arange(0, len(aligned) - days + 1, rolling_step, dtype=int)
        pm = _rolling_metrics_array(arrays["p"], days, starts)
        sm = _rolling_metrics_array(arrays["spy"], days, starts)
        qm = _rolling_metrics_array(arrays["qqq"], days, starts)
        df = pd.DataFrame(
            {
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
        )
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
            out[horizon][col] = 0.50 * mean + 0.25 * median + 0.25 * p10
    return out


def _rolling_metrics_array(returns: np.ndarray, days: int, starts: np.ndarray) -> dict[str, np.ndarray]:
    """Compute rolling metrics from NumPy arrays without per-window pandas objects."""
    ends = starts + days
    logs = np.log1p(returns)
    log_cum = np.concatenate([[0.0], np.cumsum(logs)])
    sum_cum = np.concatenate([[0.0], np.cumsum(returns)])
    sumsq_cum = np.concatenate([[0.0], np.cumsum(returns * returns)])
    neg = np.where(returns < 0.0, returns, 0.0)
    negsq = np.where(returns < 0.0, returns * returns, 0.0)
    negcount = (returns < 0.0).astype(float)
    neg_cum = np.concatenate([[0.0], np.cumsum(neg)])
    negsq_cum = np.concatenate([[0.0], np.cumsum(negsq)])
    negcount_cum = np.concatenate([[0.0], np.cumsum(negcount)])

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

    mdd = np.empty(len(starts), dtype=float)
    for i, start in enumerate(starts):
        end = start + days
        window_log_equity = log_cum[start + 1 : end + 1] - log_cum[start]
        equity = np.exp(window_log_equity)
        drawdown = equity / np.maximum.accumulate(equity) - 1.0
        mdd[i] = float(np.min(drawdown))
    calmar = np.divide(cagr, np.abs(mdd), out=np.full_like(cagr, np.nan), where=mdd < 0)
    return {
        "cagr": cagr,
        "mdd": mdd,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "terminal_wealth": terminal,
    }


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

    cagr_spy = weighted("cagr_spy_spread")
    cagr_qqq = weighted("cagr_qqq_spread")
    sharpe_spy = weighted("sharpe_spy_spread")
    sharpe_qqq = weighted("sharpe_qqq_spread")
    sortino_spy = weighted("sortino_spy_spread")
    sortino_qqq = weighted("sortino_qqq_spread")
    calmar_spy = weighted("calmar_spy_spread")
    calmar_qqq = weighted("calmar_qqq_spread")
    wealth_spy = weighted("wealth_spy_ratio_minus1")
    wealth_qqq = weighted("wealth_qqq_ratio_minus1")
    mdd_spy = weighted("mdd_minus_spy_mdd")
    mdd_qqq = weighted("mdd_minus_qqq_mdd")
    min_regret = min(
        [
            rolling[h].get("wealth_spy_ratio_minus1_p10", math.nan)
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
        "balanced_spy_beater": _balanced(cagr_spy, calmar_spy, sortino_spy, wealth_spy, mdd_spy),
        "balanced_dual_beater": _balanced(
            min(cagr_spy, cagr_qqq),
            min(calmar_spy, calmar_qqq),
            min(sortino_spy, sortino_qqq),
            min(wealth_spy, wealth_qqq),
            min(mdd_spy, mdd_qqq),
        ),
        "min_regret": float(min_regret),
    }


def _balanced(cagr: float, calmar: float, sortino: float, wealth: float, mdd_delta: float) -> float:
    penalty = min(0.0, mdd_delta) * 0.50 if pd.notna(mdd_delta) else 0.0
    return 0.30 * cagr + 0.25 * calmar + 0.20 * sortino + 0.25 * wealth + penalty


def _diff(a: float | str, b: float | str) -> float:
    return float(a) - float(b) if pd.notna(a) and pd.notna(b) else math.nan


def _ratio_minus1(a: float | str, b: float | str) -> float:
    if pd.isna(a) or pd.isna(b) or float(b) == 0.0:
        return math.nan
    return float(a) / float(b) - 1.0


def score_named_benchmarks(universe: str, returns_frame: pd.DataFrame, rolling_step: int) -> dict[str, PortfolioScore]:
    benchmarks = {"equal_weight": equal_weight_for_universe(universe)}
    if has_b4(universe):
        benchmarks["b4"] = B4_WEIGHTS
    return {
        name: score_portfolio(returns_frame, weights, rolling_step=rolling_step, include_benchmarks=False)
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
