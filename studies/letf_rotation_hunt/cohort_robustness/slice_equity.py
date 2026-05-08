"""Forward-window slicing and recovery-time helpers for cohort analysis.

Per spec §3.2-§3.3.
"""
from __future__ import annotations

import pandas as pd


def slice_forward_window(
    equity: pd.Series, entry_date: str | pd.Timestamp, years: float,
) -> pd.Series:
    """Slice `years` years of equity starting at `entry_date`.

    If `entry_date + years` exceeds the equity index, returns whatever is
    available (truncated). If `entry_date` is before the equity index, the
    returned slice starts at the first available date.
    """
    entry = pd.Timestamp(entry_date)
    end = entry + pd.DateOffset(years=int(years))
    return equity[(equity.index >= entry) & (equity.index <= end)]


def time_to_recovery(equity: pd.Series) -> float:
    """Days from the first bar until equity returns to >= equity.iloc[0].

    Looks for the first index `i > 0` where `equity.iloc[i] >= equity.iloc[0]`
    AFTER the equity has dropped below `equity.iloc[0]` at any point.

    Returns NaN if the equity never recovers (or never dipped to begin with).
    Returns the number of calendar days from `equity.index[0]` to the
    recovery date.
    """
    if len(equity) < 2:
        return float("nan")

    start_value = float(equity.iloc[0])
    start_date = equity.index[0]

    # Find first dip below start_value
    below = equity.iloc[1:] < start_value
    if not below.any():
        return float("nan")  # never dipped, no "recovery" notion

    first_below_idx = below.idxmax()  # first True
    after_dip = equity[equity.index > first_below_idx]

    recovered = after_dip >= start_value
    if not recovered.any():
        return float("nan")

    recovery_date = recovered.idxmax()
    return float((recovery_date - start_date).days)


def time_to_beat_spy(strategy_eq: pd.Series, spy_eq: pd.Series) -> float:
    """Days from start until strategy decisively beats SPY.

    Semantics:
      - If strategy never falls below SPY from the start (i.e., remains
        at or above SPY at every bar), return 0 — the strategy is
        winning "from day 1".
      - Otherwise, find the first bar where strategy dips strictly below
        SPY, then find the first subsequent bar where strategy is strictly
        above SPY again. Return the number of calendar days from the
        start to that crossover.
      - Returns NaN if the strategy never crosses back above SPY after
        falling behind.

    Both series are aligned on a common index; missing values are dropped.
    The caller is responsible for renormalising the two series to share
    the same start point if a fair comparison is desired.
    """
    aligned = pd.concat({"s": strategy_eq, "b": spy_eq}, axis=1, join="inner").dropna()
    if len(aligned) == 0:
        return float("nan")

    start_date = aligned.index[0]

    # Find first bar where strategy is strictly below SPY
    below = aligned["s"] < aligned["b"]
    if not below.any():
        # Strategy never fell behind → winning from day 1
        return 0.0

    first_below_idx = below.idxmax()
    after_below = aligned[aligned.index >= first_below_idx]

    above = after_below["s"] > after_below["b"]
    if not above.any():
        return float("nan")

    first_above = above.idxmax()
    return float((first_above - start_date).days)
