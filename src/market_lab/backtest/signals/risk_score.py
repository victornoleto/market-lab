"""Rolling z-score + sigmoid → composite crash-risk score.

Used by the Phase 2 risk-signal de-leveraging overlay (see
``studies/SPEC_crash_protection_evolution.md §3.1-B``).

Design
------

For each indicator we compute a rolling z-score over a literature-grounded
window, then pass it through a shifted sigmoid so the output is in
``[0, 1]`` and only meaningfully departs from 0 once the z-score exceeds
a threshold (typically 1 σ above the mean in the "risky" direction).

This reflects spec §8.3's concern: a linear signal that de-leverages
across the entire 2010s because CAPE > 30 for a decade would destroy
CAGR. The shifted sigmoid only kicks in during genuine stress spikes.

The final **composite** is the mean of whichever indicators are active
(non-NaN) at each bar. Bars with no active indicator return ``0`` — we
never de-leverage on pure ignorance.

Sign convention
---------------

``RISKY_SIGN[name] ∈ {+1, -1}`` encodes which direction of the indicator
means stress:

* ``ebp``, ``cape``, ``vix`` — **higher = riskier** (sign +1).
* ``term_spread`` — **lower / inverted = riskier** (sign −1).

Literature-grounded window defaults (monthly data expanded to daily at
21 TD/month):

* EBP — 60 months (1 260 TD) rolling. Gilchrist-Zakrajšek 2012 convention.
* term_spread — 60 months (1 260 TD).
* CAPE — 10 years (2 520 TD). Shiller convention.
* VIX — 60 months (1 260 TD).

Citations
---------
* Shifted sigmoid instead of linear de-levering: spec §8.3 ("só de-levera
  acima de threshold alto").
* Small-sample caution (few genuine crashes): spec §6.3 /
  ``crashes_sp500_e_indicadores_preditivos.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

__all__ = [
    "IndicatorSpec",
    "INDICATOR_SPECS",
    "RISKY_SIGN",
    "sigmoid",
    "rolling_zscore",
    "compute_risk_score",
    "compute_composite_risk",
]


@dataclass(frozen=True)
class IndicatorSpec:
    """Configuration for one risk indicator."""

    name: str
    window: int  # rolling window in (daily-aligned) trading days
    sign: Literal[-1, 1]  # +1 if higher = more risk, −1 if lower = more risk
    z_threshold: float = 1.0  # sigmoid midpoint shift in σ-units
    sigmoid_k: float = 2.0  # slope (higher = sharper transition)


RISKY_SIGN: dict[str, int] = {
    "ebp": +1,
    "cape": +1,
    "vix": +1,
    "term_spread": -1,
}


# Literature-grounded rolling windows expressed in trading-day bars.
INDICATOR_SPECS: dict[str, IndicatorSpec] = {
    "ebp": IndicatorSpec(
        name="ebp", window=60 * 21, sign=+1, z_threshold=1.0, sigmoid_k=2.0,
    ),
    "term_spread": IndicatorSpec(
        name="term_spread", window=60 * 21, sign=-1, z_threshold=1.0, sigmoid_k=2.0,
    ),
    "cape": IndicatorSpec(
        name="cape", window=10 * 252, sign=+1, z_threshold=1.0, sigmoid_k=2.0,
    ),
    "vix": IndicatorSpec(
        name="vix", window=60 * 21, sign=+1, z_threshold=1.0, sigmoid_k=2.0,
    ),
}


def sigmoid(x: np.ndarray | float, *, k: float = 1.0, threshold: float = 0.0):
    """Shifted logistic ``1 / (1 + exp(-k·(x − threshold)))``.

    Clipped input to avoid ``exp`` overflow for very extreme z-scores.
    """
    arr = np.asarray(x, dtype=float)
    x_shifted = np.clip(k * (arr - threshold), -20.0, 20.0)
    return 1.0 / (1.0 + np.exp(-x_shifted))


def rolling_zscore(series: pd.Series, window: int) -> pd.Series:
    """Rolling z-score over ``window`` bars with ``min_periods = window``.

    Returns NaN for the first ``window − 1`` bars (warmup) and for bars
    where the rolling std collapses to 0 (constant-value window).
    """
    if window <= 1:
        raise ValueError(f"window must be > 1, got {window}")
    mean = series.rolling(window=window, min_periods=window).mean()
    std = series.rolling(window=window, min_periods=window).std()
    # Wherever std == 0, return 0 (no deviation).
    z = (series - mean) / std
    z = z.where(std > 0, 0.0)
    # Re-NaN the warmup rows (where mean itself is NaN).
    z = z.where(~mean.isna(), np.nan)
    return z


def compute_risk_score(series: pd.Series, spec: IndicatorSpec) -> pd.Series:
    """Map an indicator series to a [0, 1] risk score.

    Formula:

    * ``z_t = rolling_zscore(series, spec.window)``
    * ``risk_t = sigmoid(spec.sign · z_t, k=spec.sigmoid_k, threshold=spec.z_threshold)``

    Bars during warmup remain NaN so the composite aggregator can
    exclude them. The caller decides how to treat NaN (default: 0 = no
    de-lever — ``compute_composite_risk`` applies this).
    """
    z = rolling_zscore(series, spec.window)
    risk_raw = sigmoid(spec.sign * z, k=spec.sigmoid_k, threshold=spec.z_threshold)
    # Preserve NaN from z warmup.
    risk = pd.Series(np.where(z.isna(), np.nan, risk_raw), index=series.index)
    risk.name = f"risk_{spec.name}"
    return risk


def compute_composite_risk(
    risks: dict[str, pd.Series],
    *,
    default_when_all_nan: float = 0.0,
) -> pd.Series:
    """Mean of whichever indicator risks are active (non-NaN) at each bar.

    Parameters
    ----------
    risks : dict[str, pd.Series]
        Per-indicator risk series on a shared index.
    default_when_all_nan : float
        Value used when no indicator is active. Default 0 (no de-lever
        when all indicators are in warmup — conservative: we never de-lever
        on pure ignorance).
    """
    if not risks:
        raise ValueError("at least one indicator series required")
    frame = pd.DataFrame(risks)
    n_active = frame.notna().sum(axis=1)
    total = frame.fillna(0.0).sum(axis=1)
    out = total / n_active.where(n_active > 0, np.nan)
    out = out.fillna(default_when_all_nan)
    out.name = "risk_composite"
    return out
