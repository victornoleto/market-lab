"""Monthly regime classifier via canonical T3d K=2 Vote-of-K signals.

Per spec §4.1: classifies each calendar month-end by the K-count of the
4 canonical signals on the QQQ underlying:
  s1 = price > SMA200
  s2 = price > SMA50
  s3 = realized_vol_21d < 40%
  s4 = AR(1)_30d > 0

K = sum(s1..s4) ∈ {0,1,2,3,4}.

Regime taxonomy:
  K=4   → All-on    (bull confidence, strategy ON)
  K=3   → Mostly-on (one weak signal, strategy ON)
  K=2   → Borderline (Vote-K=2 threshold barely met, strategy ON)
  K∈{0,1} → Risk-off  (strategy OFF in ZROZ)

Citations:
  - Vote-of-K signals: parent study spec §2.4 + signals.py
  - Regime taxonomy: this spec §4.1
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.signals import (
    ar1_coefficient, realized_vol_gate, sma_gate,
)


def classify_regimes(
    prices: pd.Series,
    sma_long: int = 200,
    sma_short: int = 50,
    vol_window: int = 21,
    vol_threshold: float = 0.40,
    ar1_window: int = 30,
) -> pd.DataFrame:
    """Classify each month-end of `prices` into one of 4 regimes.

    Parameters
    ----------
    prices : pd.Series
        Daily close prices of the underlying (e.g. QQQ).
    sma_long : int
        Long SMA period (default 200, canonical).
    sma_short : int
        Short SMA period (default 50).
    vol_window : int
        Realized vol lookback (default 21).
    vol_threshold : float
        Vol threshold (default 0.40 = 40% annualized).
    ar1_window : int
        AR(1) coefficient window (default 30).

    Returns
    -------
    pd.DataFrame
        Indexed by month-end date, columns: s1, s2, s3, s4, k_count, regime.
        Warmup rows (any signal NaN) are dropped — the first returned row is
        at the first month-end where all 4 signals are valid (driven by
        `sma_long`, the longest warmup).
    """
    returns = prices.pct_change().dropna()

    s1 = sma_gate(prices, period=sma_long)
    s2 = sma_gate(prices, period=sma_short)
    s3 = realized_vol_gate(returns, window=vol_window, threshold=vol_threshold)
    ar1 = ar1_coefficient(returns, window=ar1_window)
    # Degenerate-vol guard: when rolling return std is near-zero, AR(1) is
    # numerically meaningless (floating-point noise on a flat series). In that
    # regime treat s4 as ON: a perfectly trending series has no mean-reversion
    # to dampen LETF compounding [paper.hsieh_2025_letf_compounding].
    rolling_std = returns.rolling(window=ar1_window, min_periods=ar1_window).std()
    degenerate = rolling_std < 1e-10
    s4 = (ar1 > 0).astype(float)
    s4[ar1.isna()] = np.nan
    s4[degenerate.fillna(False)] = 1.0

    daily = pd.DataFrame({"s1": s1, "s2": s2, "s3": s3, "s4": s4})
    daily["k_count"] = daily[["s1", "s2", "s3", "s4"]].sum(axis=1, skipna=False)

    # Resample to month-end (BME = business month end)
    monthly = daily.resample("BME").last()

    # Drop warmup months (NaN k_count) so callers get only valid regimes.
    monthly = monthly.dropna(subset=["k_count"])

    monthly["regime"] = monthly["k_count"].map(_k_to_regime)
    return monthly


def _k_to_regime(k: float) -> str:
    """Map K-count (0..4 or NaN) to regime label."""
    if pd.isna(k):
        return "NaN"
    k_int = int(k)
    if k_int == 4:
        return "All-on"
    if k_int == 3:
        return "Mostly-on"
    if k_int == 2:
        return "Borderline"
    return "Risk-off"  # 0 or 1
