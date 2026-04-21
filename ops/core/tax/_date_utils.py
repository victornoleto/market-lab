"""Shared date utilities for tax regime modules (private package API)."""
from __future__ import annotations

import calendar
from datetime import date, timedelta

import holidays

_BR = holidays.country_holidays("BR")


def last_business_day_of_month(year: int, month: int) -> date:
    """Last business day of (year, month), skipping weekends and BR holidays."""
    _, last = calendar.monthrange(year, month)
    d = date(year, month, last)
    while d.weekday() >= 5 or d in _BR:
        d -= timedelta(days=1)
    return d


def next_month(d: date) -> tuple[int, int]:
    """Year+month of the month after d."""
    if d.month == 12:
        return (d.year + 1, 1)
    return (d.year, d.month + 1)
