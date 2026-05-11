"""Calendar-month seasonal gate (Halloween / Hirsch best-6-months) helper.

Local to iter 003 — not promoted to studies/letf_rotation_hunt/core/signals.py.

Mechanic [trading_systems_methods, p.479-481]:
    halloween_indicator(t) = 1 if month(t) in {Nov,Dec,Jan,Feb,Mar,Apr} else 0
    summer_stall_indicator(t) = 1 if month(t) in {Jan..May,Oct..Dec} else 0
        (i.e. 0 during Jun-Sep — narrower "summer stall" window)

These are pure date functions; no price/vol dependency. They are designed to
be combined with the winner's vote-of-K stack via three aggregation rules:

1. Hard veto: ``force_off = (indicator == 0)`` — overrides vote-of-K to 0.
2. Augment as 5th vote: append indicator to the vote list, raise/keep K.
3. Replacement: substitute one existing vote member with the indicator.

The 1-day signal lag (compute at close of t-1, apply at open of t) is
applied at the strategy-returns level, identical to all other signals in
this study.
"""
from __future__ import annotations

import pandas as pd

# Hirsch best-6-months: Nov, Dec, Jan, Feb, Mar, Apr = 1; May-Oct = 0.
HIRSCH_GOOD_MONTHS: frozenset[int] = frozenset({11, 12, 1, 2, 3, 4})

# "Summer stall" narrower definition: Jun, Jul, Aug, Sep = 0; rest = 1.
SUMMER_STALL_GOOD_MONTHS: frozenset[int] = frozenset({1, 2, 3, 4, 5, 10, 11, 12})


def halloween_indicator(
    index: pd.DatetimeIndex,
    good_months: frozenset[int] = HIRSCH_GOOD_MONTHS,
) -> pd.Series:
    """Return 1.0/0.0 Series indexed by date.

    Defaults to Hirsch May-Oct OFF / Nov-Apr ON. The month is read directly
    from the index (no shift), so callers are responsible for applying the
    1-day lag at strategy assembly time.
    """
    months = pd.Index(index).month
    values = [1.0 if m in good_months else 0.0 for m in months]
    return pd.Series(values, index=index, name="halloween_ind")


def summer_stall_indicator(index: pd.DatetimeIndex) -> pd.Series:
    """Tighter Jun-Sep OFF window (0 = Jun-Sep, 1 elsewhere)."""
    return halloween_indicator(index, good_months=SUMMER_STALL_GOOD_MONTHS).rename(
        "summer_stall_ind",
    )
