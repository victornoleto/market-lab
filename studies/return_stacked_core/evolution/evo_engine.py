"""Engine extensions for the evolution sub-study.

Reuses ``discussion/engine.py`` verbatim for the canonical monthly
convention (rebalance to target weights at the first trading day of the
period BEFORE that day's return — the convention that reproduces the RSC
anchor). Adds: chunked matrix simulation (5-asset grids would not fit in
memory unchunked) and offset-aware periodic rebalancing for the M4
frequency study `[testing_tuning, p.327-335]`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.return_stacked_core.discussion.engine import (  # noqa: F401
    compute_metrics,
    equity_from_returns,
    generate_weight_vectors,
    metrics_from_matrix,
    rebalanced_equity,
    simulate_matrix,
)


def simulate_matrix_chunked(
    asset_returns: pd.DataFrame,
    weights: np.ndarray,
    chunk: int = 2000,
) -> pd.DataFrame:
    """metrics_from_matrix over many portfolios without holding all equity."""
    rets = asset_returns.dropna(how="any")
    frames = []
    for lo in range(0, weights.shape[0], chunk):
        w = weights[lo : lo + chunk]
        eq = simulate_matrix(rets, w)
        frames.append(metrics_from_matrix(eq, rets.index))
    return pd.concat(frames, ignore_index=True)


def rebalanced_equity_offset(
    asset_returns: pd.DataFrame,
    weights: dict[str, float],
    months_per_period: int,
    offset: int = 0,
) -> pd.Series:
    """Periodic rebalance every ``months_per_period`` months with an offset.

    offset shifts which calendar months start a period (offset=0, quarterly
    → Jan/Apr/Jul/Oct; offset=1 → Feb/May/Aug/Nov). Same first-day-of-period
    convention as the discussion engine.
    """
    cols = list(weights.keys())
    rets = asset_returns[cols].dropna(how="any")
    w = np.array([weights[c] for c in cols], dtype=float)
    if not np.isclose(w.sum(), 1.0, atol=1e-9):
        raise ValueError(f"weights must sum to 1.0, got {w.sum():.6f}")
    r = rets.to_numpy(dtype=float)
    codes = np.array(
        [(d.year * 12 + (d.month - 1) - offset) // months_per_period for d in rets.index],
        dtype=int,
    )
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


def rolling_cagr(equity: pd.Series, years: int = 5, step_months: int = 12) -> pd.Series:
    """CAGR of rolling ``years`` windows stepped yearly, from one equity curve."""
    eq = equity.dropna()
    starts = pd.date_range(eq.index[0], eq.index[-1], freq=f"{step_months}MS")
    out = {}
    for s in starts:
        e = s + pd.DateOffset(years=years)
        if e > eq.index[-1]:
            break
        window = eq.loc[s:e]
        if len(window) < 200:
            continue
        yrs = (window.index[-1] - window.index[0]).days / 365.25
        out[window.index[0]] = (window.iloc[-1] / window.iloc[0]) ** (1.0 / yrs) - 1.0
    return pd.Series(out, name="rolling_cagr")
