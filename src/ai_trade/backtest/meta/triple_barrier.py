"""Triple-barrier labeling [advances_fin_ml, p.45-49, §3.4].

For each trigger event, place three barriers:

* **Upper (profit-take)** — ``entry · (1 + pt · trgt · side)``.
* **Lower (stop-loss)**  — ``entry · (1 − sl · trgt · side)``.
* **Vertical (time-out)** — ``events.t1``.

Label is:
  * ``+1 · side``  if the profit barrier is touched first
  * ``−1 · side``  if the stop barrier is touched first
  * ``0``           if neither is touched inside ``[t0, t1]``

``pt_sl = (pt, sl)`` are multipliers on the per-event volatility target
``events.trgt`` (typically ATR/close or daily-return stdev). ``side`` ∈
``{+1, −1}`` maps long/short and swaps the barriers accordingly.

The returned frame carries ``bin``, ``t1_actual`` (timestamp of first
touch, or ``events.t1`` for a vertical hit) and ``ret`` (realized return
from entry to ``t1_actual``).
"""

from __future__ import annotations

from typing import Tuple

import pandas as pd


def apply_triple_barrier(
    close: pd.Series,
    events: pd.DataFrame,
    pt_sl: Tuple[float, float],
) -> pd.DataFrame:
    """Label each event by which barrier is touched first.

    Parameters
    ----------
    close : pd.Series
        Monotone-indexed price series; must cover the union of event
        windows. Ticker is irrelevant — this function labels a single
        instrument at a time.
    events : pd.DataFrame
        Indexed by event-trigger timestamp ``t0``. Required columns:

        * ``t1``    — vertical barrier timestamp (inclusive upper).
        * ``trgt``  — per-event volatility target (e.g. ATR/close).
        * ``side``  — ``+1`` long, ``−1`` short.
    pt_sl : (pt, sl)
        Profit-taking and stop-loss multipliers applied to ``trgt``.

    Returns
    -------
    pd.DataFrame
        Same index as ``events``, columns ``[bin, t1_actual, ret]``.
    """
    pt, sl = pt_sl
    out = pd.DataFrame(
        index=events.index.copy(),
        columns=["bin", "t1_actual", "ret"],
    )
    for t0, ev in events.iterrows():
        path = close.loc[t0 : ev["t1"]]
        if path.empty:
            out.loc[t0] = [0, ev["t1"], 0.0]
            continue

        entry = float(path.iloc[0])
        if entry <= 0:
            out.loc[t0] = [0, ev["t1"], 0.0]
            continue

        side = int(ev["side"])
        trgt = float(ev["trgt"])
        upper = entry * (1 + pt * trgt * side)
        lower = entry * (1 - sl * trgt * side)

        if side >= 0:
            hit_up = path[path >= upper].index
            hit_dn = path[path <= lower].index
        else:
            hit_up = path[path <= upper].index  # "up" in trade-PnL sense
            hit_dn = path[path >= lower].index

        touch_up = hit_up.min() if len(hit_up) else None
        touch_dn = hit_dn.min() if len(hit_dn) else None

        # ``upper`` is the profit-taking barrier (by construction), ``lower``
        # is the stop-loss barrier — for both long and short sides, since
        # ``side`` already flipped the arithmetic above. So bin is simply
        # +1 on upper-hit, -1 on lower-hit, 0 on vertical-hit.
        candidates: list[tuple[pd.Timestamp, int]] = []
        if touch_up is not None:
            candidates.append((touch_up, +1))
        if touch_dn is not None:
            candidates.append((touch_dn, -1))
        candidates.append((ev["t1"], 0))
        candidates.sort(key=lambda x: x[0])

        t_actual, bin_val = candidates[0]
        ret = float(close.loc[t_actual] / entry - 1.0) * side
        out.loc[t0] = [bin_val, t_actual, ret]

    out["bin"] = out["bin"].astype(int)
    out["ret"] = out["ret"].astype(float)
    return out
