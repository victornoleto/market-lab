"""Per-window Sortino over fixed-length lookbacks.

Mirrors :mod:`studies.spy_beater_hunt.rolling_metrics` (which covers CAGR/MDD)
but computes Sortino per window. Used by ``run_lrs_baseline_comparison`` for
the 3y/5y/10y/15y robustness panels.

Sortino is the study's primary metric per the Sortino-first reanalysis
(STUDY_FINAL_REPORT.md), so a per-window view is the natural companion to
the headline figure.

Citations
---------
* Sortino definition (downside-deviation denominator): see
  :func:`market_lab.backtest.metrics.performance.sortino` and references
  therein (Kaufman 2020 ch.21).
"""
from __future__ import annotations

import pandas as pd

from market_lab.backtest.metrics.performance import sortino

TRADING_DAYS_PER_YEAR = 252
DEFAULT_WINDOWS_YEARS: list[int] = [3, 5, 10, 15]


def rolling_sortino_at_windows(
    returns: pd.Series,
    windows_years: list[int] = DEFAULT_WINDOWS_YEARS,
    step_days: int = TRADING_DAYS_PER_YEAR,
) -> dict[int, list[dict]]:
    """Per-window Sortino keyed by window-size in years.

    Returns
    -------
    ``{w_years: [{"start": Timestamp, "end": Timestamp, "sortino": float}, ...]}``
    Empty list for window sizes that exceed the available history.
    """
    rets = returns.dropna()
    out: dict[int, list[dict]] = {}
    n = len(rets)
    for w in windows_years:
        win_days = w * TRADING_DAYS_PER_YEAR
        if n < win_days:
            out[w] = []
            continue
        rows: list[dict] = []
        for start in range(0, n - win_days + 1, step_days):
            sample = rets.iloc[start : start + win_days]
            rows.append({
                "start": sample.index[0],
                "end": sample.index[-1],
                "sortino": float(sortino(sample)),
            })
        out[w] = rows
    return out
