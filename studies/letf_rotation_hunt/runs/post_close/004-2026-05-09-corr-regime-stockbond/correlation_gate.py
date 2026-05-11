"""Stock-bond correlation regime indicator (iter 004 helper).

Computes rolling correlation between two return series and a binary regime
indicator that fires when correlation exceeds a threshold.

Citation:
  - [risk_parity, p.80-81, ch.4]: Qian on Risk-on/Risk-off (RORO) regimes.
    Stock-bond correlation can flip from negative to positive; when this
    happens the bond leg loses its hedging value.
  - [risk_parity, p.110, ch.5]: Qian on diversification return — collapses
    to zero / negative when correlation becomes positive.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def rolling_correlation(
    returns_a: pd.Series,
    returns_b: pd.Series,
    window: int = 60,
) -> pd.Series:
    """Rolling Pearson correlation between two daily return series.

    Parameters
    ----------
    returns_a, returns_b : pd.Series
        Daily returns; indices aligned by intersection.
    window : int
        Rolling window in trading days (default 60).

    Returns
    -------
    pd.Series
        Correlation in [-1, 1]. NaN during warmup. Index = intersection of
        both inputs.
    """
    if window < 2:
        raise ValueError(f"window must be >= 2, got {window}")
    df = pd.concat({"a": returns_a, "b": returns_b}, axis=1).dropna()
    rho = df["a"].rolling(window=window, min_periods=window).corr(df["b"])
    return rho


def corr_regime_gate(
    returns_a: pd.Series,
    returns_b: pd.Series,
    threshold: float,
    window: int = 60,
) -> pd.Series:
    """Binary RORO gate: 1 when rolling corr exceeds threshold, else 0.

    A value of 1 means the diversification hedge has structurally broken
    (per [risk_parity, ch.4]) and the OFF leg should be redirected.

    Parameters
    ----------
    returns_a, returns_b : pd.Series
        Daily returns of the two assets whose correlation regime is gated.
    threshold : float
        Correlation level above which the gate fires (e.g. 0.0, 0.2, 0.3).
    window : int
        Rolling window (default 60d per [ml_for_algo_trading, ch.9]).

    Returns
    -------
    pd.Series
        {0, 1, NaN}. NaN during warmup.
    """
    rho = rolling_correlation(returns_a, returns_b, window=window)
    gate = (rho > threshold).astype(float)
    gate[rho.isna()] = np.nan
    return gate
