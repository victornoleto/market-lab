"""Monthly-rebalanced portfolio engine + metrics for the discussion sub-study.

Adapted from ``us_core/four_asset_grid/run.py`` (generate_weight_vectors,
monthly_rebalanced loop, vectorized matrix simulation) but generalized to an
arbitrary asset list. Rebalance convention: holdings reset to target weights
at the FIRST trading day of each period BEFORE applying that day's return —
this is the convention that reproduces the canonical RSC anchor
(12.40%/−30.76%/0.838 within tolerance; daily rebalancing does NOT).

Metric conventions match ``generate_robustness_report.metrics``: calendar-year
CAGR, population-std Sharpe/Sortino annualized by sqrt(periods), ulcer index
`[systematic_trading, p.185-188]`. Long-only fund-level weights; leverage is
embedded inside the capital-efficient ETFs, never external margin
`[leverage_for_the_long_run, p.13]`.
"""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def equity_from_returns(returns: pd.Series) -> pd.Series:
    r = returns.dropna().astype(float)
    return (1.0 + r).cumprod()


def rebalanced_equity(
    asset_returns: pd.DataFrame,
    weights: dict[str, float],
    frequency: str = "M",
) -> pd.Series:
    """Equity curve (start=1.0) of a periodically rebalanced long-only portfolio.

    frequency: "M" monthly (default, canonical) or "Q" quarterly (HFEA
    sensitivity convention).
    """
    cols = list(weights.keys())
    rets = asset_returns[cols].dropna(how="any")
    if rets.empty:
        raise ValueError(f"no aligned dates for assets {cols}")
    w = np.array([weights[c] for c in cols], dtype=float)
    if not math.isclose(w.sum(), 1.0, abs_tol=1e-9):
        raise ValueError(f"weights must sum to 1.0, got {w.sum():.6f}")

    r = rets.to_numpy(dtype=float)
    if frequency == "M":
        codes = np.array([d.year * 12 + d.month for d in rets.index], dtype=int)
    elif frequency == "Q":
        codes = np.array(
            [d.year * 4 + (d.month - 1) // 3 for d in rets.index], dtype=int
        )
    else:
        raise ValueError(f"unknown frequency {frequency!r}")

    n = r.shape[0]
    equity = np.empty(n, dtype=float)
    value = 1.0
    holdings = w * value
    current = None
    for i in range(n):
        if int(codes[i]) != current:
            holdings = w * value
            current = int(codes[i])
        holdings = holdings * (1.0 + r[i])
        value = float(holdings.sum())
        equity[i] = value
    return pd.Series(equity, index=rets.index, name="equity")


def simulate_matrix(asset_returns: pd.DataFrame, weights: np.ndarray) -> np.ndarray:
    """Vectorized monthly-rebalanced equity for many portfolios at once.

    weights: (n_portfolios, n_assets) aligned to asset_returns.columns.
    Returns (n_days, n_portfolios) equity matrix (start value applied
    after the first day, consistent with rebalanced_equity).
    """
    rets = asset_returns.dropna(how="any")
    returns = rets.to_numpy(dtype=float)
    codes = np.array([d.year * 12 + d.month for d in rets.index], dtype=int)
    n_days = returns.shape[0]
    n_pf = weights.shape[0]
    equity = np.empty((n_days, n_pf), dtype=float)
    values = np.ones(n_pf, dtype=float)
    holdings = values[:, None] * weights
    current = None
    for i in range(n_days):
        if int(codes[i]) != current:
            holdings = values[:, None] * weights
            current = int(codes[i])
        holdings = holdings * (1.0 + returns[i])
        values = holdings.sum(axis=1)
        equity[i] = values
    return equity


def generate_weight_vectors(
    n_assets: int, step_pct: int = 5
) -> list[tuple[int, ...]]:
    """All integer weight vectors on the simplex with the given step (sums to 100)."""
    units = 100 // step_pct

    def rec(remaining: int, slots: int) -> Iterable[tuple[int, ...]]:
        if slots == 1:
            yield (remaining * step_pct,)
            return
        for k in range(remaining + 1):
            for tail in rec(remaining - k, slots - 1):
                yield (k * step_pct, *tail)

    return list(rec(units, n_assets))


def compute_metrics(
    equity: pd.Series, periods_per_year: int = TRADING_DAYS
) -> dict[str, float | str]:
    """Calendar-year CAGR, MDD, vol, Sharpe, Sortino, Calmar, Ulcer, terminal."""
    clean = equity.dropna().astype(float)
    clean = clean / clean.iloc[0]
    returns = clean.pct_change().dropna()
    start, end = clean.index[0], clean.index[-1]
    years = (end - start).days / 365.25
    dd = clean / clean.cummax() - 1.0
    vol = returns.std(ddof=0)
    downside = returns[returns < 0.0].std(ddof=0)
    cagr = clean.iloc[-1] ** (1.0 / years) - 1.0 if years > 0 else math.nan
    mdd = float(dd.min())
    sharpe = (
        float(returns.mean() / vol * math.sqrt(periods_per_year))
        if vol and vol > 0
        else math.nan
    )
    sortino = (
        float(returns.mean() / downside * math.sqrt(periods_per_year))
        if downside and downside > 0
        else math.nan
    )
    return {
        "start": str(start.date()),
        "end": str(end.date()),
        "years": float(years),
        "cagr": float(cagr),
        "mdd": mdd,
        "vol": float(vol * math.sqrt(periods_per_year)),
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": float(cagr / abs(mdd)) if mdd < 0 else math.nan,
        "ulcer": float(((dd * dd).mean()) ** 0.5),
        "terminal": float(clean.iloc[-1]),
    }


def metrics_from_matrix(
    equity: np.ndarray, index: pd.DatetimeIndex
) -> pd.DataFrame:
    """Vectorized metrics for a (n_days, n_portfolios) equity matrix."""
    years = (index[-1] - index[0]).days / 365.25
    terminal = equity[-1]
    first = equity[0]
    norm = equity / first
    cagr = (terminal / first) ** (1.0 / years) - 1.0
    peak = np.maximum.accumulate(norm, axis=0)
    dd = norm / peak - 1.0
    mdd = dd.min(axis=0)
    rets = equity[1:] / equity[:-1] - 1.0
    mean = rets.mean(axis=0)
    std = rets.std(axis=0, ddof=0)
    sharpe = np.divide(mean, std, out=np.zeros_like(mean), where=std > 1e-12)
    sharpe = sharpe * np.sqrt(TRADING_DAYS)
    downside = np.where(rets < 0.0, rets, np.nan)
    with np.errstate(invalid="ignore"):
        dstd = np.nanstd(downside, axis=0, ddof=0)
    sortino = np.divide(mean, dstd, out=np.zeros_like(mean), where=dstd > 1e-12)
    sortino = sortino * np.sqrt(TRADING_DAYS)
    vol = std * np.sqrt(TRADING_DAYS)
    ulcer = np.sqrt((dd * dd).mean(axis=0))
    return pd.DataFrame(
        {
            "cagr": cagr,
            "mdd": mdd,
            "vol": vol,
            "sharpe": sharpe,
            "sortino": sortino,
            "calmar": np.where(mdd < 0, cagr / np.abs(mdd), np.nan),
            "ulcer": ulcer,
            "terminal": terminal / first,
        }
    )
