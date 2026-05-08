"""Momentum / volatility math helpers (pure functions).

Originally lived in ``strategies/clenow_momentum.py`` from Clenow's
``stocks_on_the_move``. Extracted here in 2026-04-16 cleanup so
``etf_rotation`` can keep using ``adjusted_slope`` after Clenow itself
is retired.

Citations preserved as in the source book — these are NOT optimisation
hooks, the constants are book-prescribed.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

__all__ = ["adjusted_slope", "atr", "max_gap"]


def adjusted_slope(
    prices: pd.Series, lookback: int = 90
) -> tuple[float, float]:
    """Return ``(annualized_slope, r_squared)`` over the last ``lookback`` prices.

    Regresses ``ln(prices)`` on a 0..N-1 time index. The slope is compounded
    over 250 trading days for annualization (Clenow p.72). Raises ``ValueError``
    when ``len(prices) < lookback``.

    Citation: ``[stocks_on_the_move, p.70-72, p.76-77, p.82, p.98]``.
    """
    if len(prices) < lookback:
        raise ValueError(
            f"adjusted_slope needs lookback={lookback} bars, got {len(prices)}"
        )

    tail = prices.iloc[-lookback:]
    log_p = np.log(tail.to_numpy(dtype=float))
    t = np.arange(lookback, dtype=float)

    t_mean = t.mean()
    lp_mean = log_p.mean()
    var_t = ((t - t_mean) ** 2).sum()
    cov = ((t - t_mean) * (log_p - lp_mean)).sum()
    m = cov / var_t
    intercept = lp_mean - m * t_mean

    pred = m * t + intercept
    sse = ((log_p - pred) ** 2).sum()
    sst = ((log_p - lp_mean) ** 2).sum()
    r2 = 1.0 - sse / sst if sst > 0 else 0.0

    ann_slope = math.exp(m) ** 250 - 1.0
    return float(ann_slope), float(r2)


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    lookback: int = 20,
) -> float:
    """Simple-mean ATR over the last ``lookback`` bars.

    TR formula per Clenow p.88: ``max(H-L, |H-C_prev|, |L-C_prev|)``. The first
    bar's TR is just ``H-L`` (no prior close). Uses an arithmetic mean — not
    Wilder's smoothing — to match the book.

    Citation: ``[stocks_on_the_move, p.88]``.
    """
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1, skipna=True)
    tail = tr.iloc[-lookback:]
    if tail.empty:
        return float("nan")
    return float(tail.mean())


def max_gap(close: pd.Series, lookback: int = 90) -> float:
    """Largest absolute close-to-close return in the last ``lookback`` bars.

    Clenow's "single-day move" filter at p.82. Returns 0.0 on a flat series;
    NaN-safe over the tail.

    Citation: ``[stocks_on_the_move, p.82, p.98]``.
    """
    returns = close.pct_change().abs()
    tail = returns.iloc[-lookback:]
    if tail.empty:
        return 0.0
    value = tail.max(skipna=True)
    return 0.0 if pd.isna(value) else float(value)
