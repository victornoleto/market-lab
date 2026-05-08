"""Two-pole high-pass filter with ``K = 0.707`` Butterworth factor.

Formula (Code Listing 7-3, [cycle_analytics, p.81-82, ch.7])::

    α = (cos(√2·π/period) + sin(√2·π/period) - 1) / cos(√2·π/period)
    HP[t] = (1 - α/2)² · (P[t] - 2·P[t-1] + P[t-2])
          + 2·(1 - α)·HP[t-1]
          - (1 - α)²·HP[t-2]

Notes
-----
* The EasyLanguage original uses ``.707·360°/HPPeriod`` in degrees; in radians
  that is ``√2·π/period`` (since ``.707 ≈ √2/2`` and ``360° = 2π``).
* This is the **two-pole** variant used by Code Listing 7-3 (the generalized
  roofing-filter indicator). Code Listing 7-1 is a single-pole variant
  hardcoded to period 48; we use the two-pole form per the note at
  [cycle_analytics, p.82, ch.7] recommending it as the preferred version.
* DC rejection is exact: the `(P[t] - 2·P[t-1] + P[t-2])` second-difference
  numerator has a double zero at DC.
* Warm-up: HP[0] = HP[1] = 0 (standard EasyLanguage semantics for negative
  indices). Transient dies within ~2·period bars.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def high_pass(series: pd.Series, period: int) -> pd.Series:
    """Apply Ehlers's two-pole high-pass filter.

    Parameters
    ----------
    series : pd.Series
        Input signal.
    period : int
        Cutoff period in bars. Must be ≥ 2.

    Returns
    -------
    pd.Series
        High-pass-filtered output, same length and index as ``series``.
    """
    if period < 2:
        raise ValueError(f"HighPass period must be ≥ 2, got {period}")

    angle = math.sqrt(2) * math.pi / period
    alpha = (math.cos(angle) + math.sin(angle) - 1) / math.cos(angle)

    values = series.to_numpy(dtype=float, copy=True)
    n = len(values)
    hp = np.zeros(n)

    k = (1 - alpha / 2) ** 2
    one_minus_alpha = 1 - alpha
    sq_one_minus_alpha = one_minus_alpha * one_minus_alpha

    for t in range(2, n):
        hp[t] = (
            k * (values[t] - 2 * values[t - 1] + values[t - 2])
            + 2 * one_minus_alpha * hp[t - 1]
            - sq_one_minus_alpha * hp[t - 2]
        )

    return pd.Series(hp, index=series.index, name=series.name)
