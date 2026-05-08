"""Cohort entry dates for path-dependence analysis (spec §3.1).

Eight specific historical entry dates: 5 "worst-case" peaks immediately
before major drawdowns + 3 "control" troughs marking recovery starts.

All dates fall within the lh_56y data range (1986-2026).
"""
from __future__ import annotations

# Each cohort is a dict with: cohort_id (str), date (str ISO), event (str), tier (str)
COHORT_DATES: list[dict] = [
    {"cohort_id": "01", "date": "1987-08-25", "event": "S&P 500 ATH before Black Monday", "tier": "worst"},
    {"cohort_id": "02", "date": "2000-03-24", "event": "NDX dotcom peak",                  "tier": "worst"},
    {"cohort_id": "03", "date": "2007-10-09", "event": "S&P 500 GFC peak",                  "tier": "worst"},
    {"cohort_id": "04", "date": "2020-02-19", "event": "S&P 500 COVID peak",                "tier": "worst"},
    {"cohort_id": "05", "date": "2021-12-27", "event": "S&P 500 ATH before 2022 rate cycle", "tier": "worst"},
    {"cohort_id": "06", "date": "2003-03-11", "event": "S&P 500 dotcom trough (recovery)",  "tier": "control"},
    {"cohort_id": "07", "date": "2009-03-09", "event": "S&P 500 GFC trough (recovery)",     "tier": "control"},
    {"cohort_id": "08", "date": "2022-10-12", "event": "S&P 500 2022 rates trough (recovery)", "tier": "control"},
]
