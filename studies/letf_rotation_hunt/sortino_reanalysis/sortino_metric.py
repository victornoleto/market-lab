"""Sortino 1991 helpers for sortino_reanalysis sub-study (spec §3).

Citations:
  - Sortino, F.A. (1991) "Performance Measurement in a Downside Risk Framework",
    Financial Executive, 17(8): 31-34.
  - [advances_fin_ml, p.275] — de Prado, downside-deviation in metric family.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _annualised_sortino(
    returns: pd.Series,
    target: float = 0.0,
    trading_days: int = 252,
) -> float:
    """Annualized Sortino ratio (1991 form) with target-conditional semideviation.

    Formula:
        sortino = (mean(r) - target) / downside_dev * sqrt(trading_days)
        downside_dev = sqrt(mean over ALL N periods of min(r - target, 0)**2)

    NOT the Sortino-Price 1994 form (sample std of negatives subset).

    Edge cases:
        - len(returns) < 2 → NaN (matches scoring.py compute_metrics)
        - downside_dev == 0 (all returns >= target) → +inf
    """
    returns = returns.dropna()
    if len(returns) < 2:
        return float("nan")

    excess = returns - target
    downside = np.minimum(excess, 0.0)
    downside_var = float((downside ** 2).mean())
    downside_dev = np.sqrt(downside_var)

    if downside_dev == 0.0:
        return float("inf")

    return float(excess.mean() / downside_dev * np.sqrt(trading_days))


def _sortino_edge_vs_spy(
    strategy_sortino: float,
    spy_sortino_per_dataset: dict[str, float],
    dataset: str,
) -> float:
    """Subtract strategy Sortino from SPY anchor for the given dataset.

    Mirrors the threshold_sweep convention `gross_edge_vs_canonical = strategy_sharpe
    - canonical_sharpe`, applied to Sortino in the SPY-edge direction. The
    edge-vs-anchor framing is the standard net-of-benchmark evaluation per
    `[advances_fin_ml, p.275]`; SPY is the canonical equity-risk benchmark for
    LETF strategies per parent study `STUDY_FINAL_REPORT.md` §3.4.

    Raises
    ------
    KeyError
        If `dataset` is not a key in `spy_sortino_per_dataset`. Caller is
        responsible for providing complete anchors.
    """
    return float(strategy_sortino - spy_sortino_per_dataset[dataset])
