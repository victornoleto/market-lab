"""Bond rate-vol regime indicator (iter 006 helper).

Computes rolling realised volatility of a return series, then a binary regime
indicator that fires when the current vol exceeds a percentile threshold of a
trailing-window vol distribution. Modeled on the Sinclair volatility-cone
primitive `[volatility_trading, p.58-60]`.

Citations:
  - [volatility_trading, p.58-60]: Sinclair on volatility cones — current
    realised vol placed against historical percentile distribution as
    regime-detection primitive.
  - [systematic_trading, p.212, ch.13]: Carver on vol-scaled regime thresholds.
  - [ml_for_algo_trading, ch.9]: Jansen on rolling state features.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def rolling_realised_vol(
    returns: pd.Series,
    window: int = 60,
    annualise: bool = True,
) -> pd.Series:
    """Rolling realised volatility (annualised by default, sqrt(252)).

    Parameters
    ----------
    returns : pd.Series
        Daily returns.
    window : int
        Rolling window in trading days (default 60).
    annualise : bool
        If True (default), multiply rolling std by sqrt(252).

    Returns
    -------
    pd.Series
        Realised vol; NaN during warmup.
    """
    if window < 2:
        raise ValueError(f"window must be >= 2, got {window}")
    sigma = returns.rolling(window=window, min_periods=window).std(ddof=1)
    if annualise:
        sigma = sigma * np.sqrt(252.0)
    return sigma


def rolling_percentile_rank(
    series: pd.Series,
    window: int = 1260,
    min_periods: int | None = None,
) -> pd.Series:
    """Rolling percentile rank in [0, 1] of the latest value within window.

    Implementation: at each t, rank latest value among the trailing
    `window` observations and return rank/(N-1). NaN during warmup.

    Parameters
    ----------
    series : pd.Series
        Numeric series (e.g. realised vol).
    window : int
        Rolling window length (default 1260 ≈ 5 years of trading days).
    min_periods : int | None
        Minimum non-NaN observations to emit a rank. Defaults to `window`
        (no warmup-shortcut to avoid look-ahead-style early activation).
    """
    if min_periods is None:
        min_periods = window

    def _rank_last(arr: np.ndarray) -> float:
        # arr: rolling slice of latest `window` observations (numpy view).
        # Last element's percentile rank in [0,1] (linear, ignoring ties).
        if np.isnan(arr).any():
            return np.nan
        latest = arr[-1]
        # Strict-less count gives left-tail rank in [0, n-1]; divide by n-1.
        n = len(arr)
        if n < 2:
            return np.nan
        less_count = float((arr < latest).sum())
        return less_count / float(n - 1)

    return series.rolling(window=window, min_periods=min_periods).apply(
        _rank_last, raw=True,
    )


def ratevol_regime_gate(
    bond_returns: pd.Series,
    vol_window: int = 60,
    pct_window: int = 1260,
    threshold: float = 0.80,
) -> pd.Series:
    """Binary gate: 1 when bond realised-vol percentile > threshold.

    Parameters
    ----------
    bond_returns : pd.Series
        Daily returns of the bond series whose vol regime is gated
        (e.g. ZROZSIM pct_change).
    vol_window : int
        Rolling realised-vol window (default 60d).
    pct_window : int
        Trailing-window length for percentile rank (default 1260d ≈ 5y).
    threshold : float
        Percentile threshold in [0, 1] above which gate fires
        (e.g. 0.70 = 70th percentile, 0.80 = 80th percentile).

    Returns
    -------
    pd.Series
        {0, 1, NaN}. NaN during warmup (≈ vol_window + pct_window days).
        1 means "high-vol regime" — divert OFF leg to alt asset.
    """
    if not (0.0 < threshold < 1.0):
        raise ValueError(f"threshold must be in (0,1), got {threshold}")
    sigma = rolling_realised_vol(bond_returns, window=vol_window, annualise=True)
    pct_rank = rolling_percentile_rank(sigma, window=pct_window)
    gate = (pct_rank > threshold).astype(float)
    gate[pct_rank.isna()] = np.nan
    return gate
