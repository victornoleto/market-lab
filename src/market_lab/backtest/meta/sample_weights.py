"""Sample weights for overlapping financial events [advances_fin_ml, §4, p.59-69].

Financial labels are rarely IID — two events can share part of their
outcome window, so a naive fit gives overlapping samples the same weight
as non-overlapping ones and over-represents the concurrent region. AFML's
fix is a two-part weight:

* **Uniqueness**  — inverse of the number of events active at each bar
  (``get_concurrent_events`` + ``get_avg_uniqueness``). Weight ``∝ 1/c``
  where ``c`` is the average count of concurrent events during ``[t0, t1]``.

* **Return attribution** — absolute realized log-return over ``[t0, t1]``
  divided by concurrency at each bar, summed over the event's window.
  Events with large PnL get more weight because they carry more signal.

These two are multiplicative in AFML's framework; a combined weight is
returned by ``get_sample_weights_by_return``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def get_concurrent_events(
    close_index: pd.DatetimeIndex, t1: pd.Series
) -> pd.Series:
    """Count of events in flight at each timestamp of ``close_index``.

    Parameters
    ----------
    close_index : pd.DatetimeIndex
        The price bars' timestamps.
    t1 : pd.Series
        Indexed by event ``t0`` (trigger timestamp), values are ``t1``
        (vertical barrier timestamp or first-touch timestamp).

    Returns
    -------
    pd.Series
        Indexed by ``close_index``, integer counts.
    """
    if t1.empty:
        return pd.Series(0, index=close_index, dtype="int64")

    t1 = t1.fillna(close_index.max())
    t1 = t1[t1.index.isin(close_index)]  # safety — drop stale indices

    counts = pd.Series(0, index=close_index, dtype="int64")
    for t0, tend in t1.items():
        window = close_index[(close_index >= t0) & (close_index <= tend)]
        counts.loc[window] += 1
    return counts


def get_avg_uniqueness(
    t1: pd.Series, concurrent: pd.Series
) -> pd.Series:
    """Average per-event uniqueness ``(1/c)`` over the event's window.

    Higher value → event window has fewer concurrent events → more unique.
    Uniqueness is bounded in (0, 1].
    """
    out = pd.Series(index=t1.index, dtype="float64")
    for t0, tend in t1.items():
        window = concurrent.loc[t0:tend]
        window = window[window > 0]
        out.loc[t0] = (1.0 / window).mean() if len(window) else 0.0
    return out


def get_sample_weights_by_return(
    t1: pd.Series,
    close: pd.Series,
    concurrent: pd.Series | None = None,
) -> pd.Series:
    """Combined weight: absolute log-return attribution × uniqueness [p.69].

    Parameters
    ----------
    t1 : pd.Series
        Per-event ``t0 → t1`` mapping.
    close : pd.Series
        Price series for the instrument (used only for log-returns).
    concurrent : pd.Series | None
        Pre-computed concurrency count. Recomputed from ``t1`` if None.

    Returns
    -------
    pd.Series
        Indexed by event ``t0``; non-negative weights normalised to sum
        to ``len(t1)`` (average weight is 1.0), following AFML convention.
    """
    if concurrent is None:
        concurrent = get_concurrent_events(close.index, t1)

    log_ret = np.log(close / close.shift(1))
    log_ret = log_ret.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    out = pd.Series(index=t1.index, dtype="float64")
    for t0, tend in t1.items():
        seg_ret = log_ret.loc[t0:tend]
        seg_conc = concurrent.loc[t0:tend].replace(0, 1)
        attributed = (seg_ret / seg_conc).abs().sum()
        out.loc[t0] = attributed

    total = out.sum()
    if total > 0:
        out = out * (len(out) / total)
    return out
