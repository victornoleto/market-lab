"""Iter 066 — Feature engineering for tree-based meta-label.

Produces a deterministic 5-feature matrix `X[t]` aligned to bar `t`, using
ONLY data available at end-of-bar `t-1`. All features are shifted +1 day
explicitly to enforce the no-peek invariant per
`[advances_fin_ml, p.162-164]`.

Features
--------
1. ``roll21_sharpe``  — rolling 21-day Sharpe of `r_064` (lagged 1 bar)
2. ``roll63_mdd``     — rolling 63-day max drawdown of `r_064` cumprod (lagged)
3. ``vix``            — VIX close (forward-filled to trading days, lagged 1)
4. ``t10y3m``         — Treasury 10y-3m spread (forward-filled, lagged 1)
5. ``sma200_dist``    — (price[t-1] − SMA200(price)[t-1]) / SMA200

The ``sma200_dist`` feature uses the dataset's benchmark price (SPY for
educational + spy_real, QQQ for ndx_real) — same primitive as Faber 2007
SSRN 962461.

Citations
---------
* `[advances_fin_ml, ch.3]` — meta-label feature design.
* `[advances_fin_ml, p.162-164]` — strict 1-day shift no-peek.
* Faber (2007), SSRN 962461 — 200d SMA primitive (one feature only).
* Whaley (2009), JPM 35(3) 98-105, DOI 10.3905/JPM.2009.35.3.098 — VIX.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


FEATURE_COLS: tuple[str, ...] = (
    "roll21_sharpe",
    "roll63_mdd",
    "vix",
    "t10y3m",
    "sma200_dist",
)


def rolling_sharpe(returns: pd.Series, window: int = 21) -> pd.Series:
    """Annualised rolling Sharpe; NaN during warmup (first ``window-1`` bars)."""
    mu = returns.rolling(window).mean()
    sigma = returns.rolling(window).std(ddof=0)
    daily = mu / sigma.replace(0.0, np.nan)
    return daily * np.sqrt(252.0)


def rolling_mdd(returns: pd.Series, window: int = 63) -> pd.Series:
    """Rolling max drawdown on a window of compounded returns.

    Returns the positive magnitude of the worst peak-to-trough drop.
    NaN during warmup (first ``window-1`` bars).
    """

    def _mdd(arr: np.ndarray) -> float:
        eq = np.cumprod(1.0 + arr)
        peak = np.maximum.accumulate(eq)
        dd = (eq - peak) / peak
        return float(-dd.min())

    return returns.rolling(window).apply(_mdd, raw=True)


def sma_distance(prices: pd.Series, window: int = 200) -> pd.Series:
    """(price - SMA) / SMA; NaN during warmup."""
    sma = prices.rolling(window).mean()
    return (prices - sma) / sma.replace(0.0, np.nan)


def build_feature_matrix(
    r_064: pd.Series,
    bench_prices: pd.Series,
    vix: pd.Series,
    t10y3m: pd.Series,
    *,
    sharpe_window: int = 21,
    mdd_window: int = 63,
    sma_window: int = 200,
) -> pd.DataFrame:
    """Assemble the 5-feature matrix aligned to ``r_064.index``.

    All inputs are aligned by union of indices, then re-indexed to
    ``r_064.index``. Forward-fill applies to VIX/T10Y3M for non-trading
    bar coverage. The final shift(1) call enforces the no-peek invariant
    on ALL features simultaneously.

    Returns
    -------
    pd.DataFrame
        Columns = ``FEATURE_COLS``, index aligned to r_064 with NaN rows
        for warmup bars dropped by the caller.
    """
    if not isinstance(r_064.index, pd.DatetimeIndex):
        r_064 = r_064.copy()
        r_064.index = pd.to_datetime(r_064.index)
    idx = r_064.index

    f1 = rolling_sharpe(r_064, window=sharpe_window)
    f2 = rolling_mdd(r_064, window=mdd_window)

    if not isinstance(bench_prices.index, pd.DatetimeIndex):
        bench_prices = bench_prices.copy()
        bench_prices.index = pd.to_datetime(bench_prices.index)
    f5 = sma_distance(bench_prices, window=sma_window)
    f5_aligned = f5.reindex(idx).ffill()

    if not isinstance(vix.index, pd.DatetimeIndex):
        vix = vix.copy()
        vix.index = pd.to_datetime(vix.index)
    f3 = vix.reindex(idx).ffill()

    if not isinstance(t10y3m.index, pd.DatetimeIndex):
        t10y3m = t10y3m.copy()
        t10y3m.index = pd.to_datetime(t10y3m.index)
    f4 = t10y3m.reindex(idx).ffill()

    df = pd.DataFrame({
        "roll21_sharpe": f1.values,
        "roll63_mdd": f2.values,
        "vix": f3.values,
        "t10y3m": f4.values,
        "sma200_dist": f5_aligned.values,
    }, index=idx)

    # Strict no-peek: all features are state at end-of-(t-1).
    df_lag = df.shift(1)
    return df_lag


def label_positive_return(r_064: pd.Series) -> pd.Series:
    """Binary forward label: 1 if r_064[t] > 0, else 0.

    The label is the variable being predicted from features[t-1]. NOT
    shifted — feature/label alignment per AFML Ch.3 is exactly
    `(X[t-1], y[t])`.
    """
    return (r_064 > 0.0).astype(int)


def warmup_drop(
    X: pd.DataFrame, y: pd.Series, drop_cols: Iterable[str] = FEATURE_COLS,
) -> tuple[pd.DataFrame, pd.Series]:
    """Drop rows where ANY feature is NaN (initial warmup window)."""
    valid = X[list(drop_cols)].notna().all(axis=1)
    return X.loc[valid].copy(), y.loc[valid].copy()
