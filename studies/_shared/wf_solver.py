"""Walk-forward portfolio solver.

Adapted from bestfolio.app/blog/walk-forward-portfolios methodology with
embargoed CV defense against serial correlation per
``[advances_fin_ml, p.105-108]``. Reused by
``studies/bestfolio_meta_wf_hunt/`` to allocate monthly weights across a
fixed universe of pre-validated sleeves.

Constraints (bestfolio defaults, kept identical for reproducibility):
- Lookback: 36 months of daily returns
- Rebalance: monthly (last trading day per month present in the index)
- Bounds: 0 <= w_i <= 0.40 (no shorts, max 40% per sleeve)
- Equality: sum(w) = 1
- Objectives: max-Sharpe (Conservative variant) or max-CAGR via max geometric
  mean of log-returns (Aggressive variant)
- Embargo: 21 calendar days between train end and rebal date — addition over
  bestfolio for serial-correlation defense.

Citations
---------
- bestfolio.app/blog/walk-forward-portfolios (consulted 2026-04-29)
- ``[advances_fin_ml, p.105-108]`` — embargoed CV
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass
class WFResult:
    weights: pd.DataFrame  # index = rebal_date, columns = sleeve
    portfolio_returns: pd.Series  # daily portfolio returns
    rebal_dates: pd.DatetimeIndex


def _solve_weights(
    returns_window: np.ndarray,
    max_weight: float,
    objective: Literal["sharpe", "cagr"],
) -> np.ndarray:
    T, N = returns_window.shape
    if T < 2:
        return np.full(N, 1.0 / N)

    if objective == "sharpe":
        mu = returns_window.mean(axis=0)
        cov = np.cov(returns_window, rowvar=False) + np.eye(N) * 1e-10

        def neg_obj(w: np.ndarray) -> float:
            var = float(w @ cov @ w)
            if var <= 1e-15:
                return 0.0
            return -float(w @ mu) / np.sqrt(var)

    elif objective == "cagr":

        def neg_obj(w: np.ndarray) -> float:
            port = returns_window @ w
            gross = np.where(1.0 + port <= 1e-10, 1e-10, 1.0 + port)
            return -float(np.mean(np.log(gross)))

    else:
        raise ValueError(f"unknown objective: {objective!r}")

    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1.0}]
    bounds = [(0.0, max_weight)] * N
    w0 = np.full(N, 1.0 / N)

    result = minimize(
        neg_obj,
        w0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 200, "ftol": 1e-9},
    )

    if not result.success or np.any(np.isnan(result.x)):
        return np.full(N, 1.0 / N)

    w = np.clip(result.x, 0.0, max_weight)
    total = w.sum()
    if total <= 0:
        return np.full(N, 1.0 / N)
    return w / total


def walk_forward_solve(
    returns: pd.DataFrame,
    lookback_months: int = 36,
    max_weight: float = 0.40,
    embargo_days: int = 21,
    objective: Literal["sharpe", "cagr"] = "sharpe",
    min_train_obs: int = 60,
    strict_lookback: bool = True,
) -> WFResult:
    """Run walk-forward solver over a sleeve return matrix.

    Parameters
    ----------
    returns
        DataFrame with a DatetimeIndex (daily) and one column per sleeve.
        Values are simple daily returns (e.g. ``0.001`` for +0.10%).
    lookback_months
        Trailing window length used to fit weights. Default 36 months
        (bestfolio's choice; kept for reproducibility).
    max_weight
        Upper bound per sleeve. Default 0.40 (bestfolio's choice).
    embargo_days
        Calendar days excluded between train-window end and rebal date.
        Default 21. Set 0 to disable (bestfolio default behavior).
    objective
        ``'sharpe'`` for max-Sharpe (Conservative) or ``'cagr'`` for max
        log-return mean (Aggressive).
    min_train_obs
        Minimum observations required in the train window. Rebalances with
        fewer are skipped (warm-up period).
    strict_lookback
        If True (default, matches bestfolio.app), skip rebalances where the
        full ``lookback_months`` window is not available in the data. Set
        False to allow partial-history rebalances down to ``min_train_obs``.

    Returns
    -------
    WFResult
        ``weights`` indexed by rebal date with sleeve weights,
        ``portfolio_returns`` daily series spanning all post-warmup dates,
        ``rebal_dates`` the actual rebalance dates used.
    """
    if not isinstance(returns.index, pd.DatetimeIndex):
        returns.index = pd.to_datetime(returns.index)
    returns = returns.dropna().sort_index()

    monthly = returns.groupby([returns.index.year, returns.index.month])
    rebal_dates = pd.DatetimeIndex([g.index[-1] for _, g in monthly])

    weights_records: list[pd.Series] = []
    forward_parts: list[pd.Series] = []

    data_start = returns.index[0]
    for i, t in enumerate(rebal_dates):
        train_end = t - pd.Timedelta(days=embargo_days)
        train_start = t - pd.DateOffset(months=lookback_months)
        if strict_lookback and train_start < data_start - pd.Timedelta(days=10):
            continue
        train = returns.loc[train_start:train_end]
        if len(train) < min_train_obs:
            continue

        w = _solve_weights(train.values, max_weight, objective)
        weights_records.append(pd.Series(w, index=returns.columns, name=t))

        if i + 1 < len(rebal_dates):
            t_next = rebal_dates[i + 1]
            forward = returns.loc[(returns.index > t) & (returns.index <= t_next)]
        else:
            forward = returns.loc[returns.index > t]

        if len(forward) > 0:
            port_ret = forward.values @ w
            forward_parts.append(pd.Series(port_ret, index=forward.index))

    if not weights_records:
        return WFResult(
            weights=pd.DataFrame(columns=returns.columns),
            portfolio_returns=pd.Series(dtype=float),
            rebal_dates=pd.DatetimeIndex([]),
        )

    weights_df = pd.DataFrame(weights_records)
    portfolio_returns = (
        pd.concat(forward_parts) if forward_parts else pd.Series(dtype=float)
    )

    return WFResult(
        weights=weights_df,
        portfolio_returns=portfolio_returns,
        rebal_dates=pd.DatetimeIndex(weights_df.index),
    )
