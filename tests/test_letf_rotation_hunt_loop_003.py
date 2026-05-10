"""Tests for iter 003 calendar_gate helpers."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ITER_DIR = (
    Path(__file__).parent.parent
    / "studies"
    / "letf_rotation_hunt"
    / "loop_iterations"
    / "003-2026-05-09-calendar-halloween-gate"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("calendar_gate", ITER_DIR / "calendar_gate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load_module()


def test_halloween_indicator_default_hirsch(mod):
    """Default mode: 1 in Nov-Apr, 0 in May-Oct."""
    idx = pd.date_range("2024-01-01", "2024-12-31", freq="MS")  # one date per month
    series = mod.halloween_indicator(idx)
    expected = {1: 1, 2: 1, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 1, 12: 1}
    for date, want in zip(idx, expected.values()):
        assert series.loc[date] == float(want), f"{date.month_name()} expected {want}"


def test_halloween_indicator_index_preserved(mod):
    idx = pd.bdate_range("2020-01-01", "2020-12-31")
    series = mod.halloween_indicator(idx)
    assert (series.index == idx).all()
    assert series.dtype == float


def test_summer_stall_indicator_jun_sep(mod):
    """Summer-stall variant: 0 only Jun-Sep, 1 elsewhere (incl. May & Oct)."""
    idx = pd.date_range("2024-01-15", "2024-12-15", freq="MS")
    series = mod.summer_stall_indicator(idx)
    for date in idx:
        m = date.month
        want = 0.0 if m in {6, 7, 8, 9} else 1.0
        assert series.loc[date] == want, f"month {m} expected {want}"


def test_halloween_no_lookahead(mod):
    """Indicator at date t depends only on month(t) — no future leakage by construction."""
    idx = pd.bdate_range("2022-04-25", "2022-05-05")
    series = mod.halloween_indicator(idx)
    apr = series[series.index.month == 4]
    may = series[series.index.month == 5]
    assert (apr == 1.0).all()
    assert (may == 0.0).all()


def test_halloween_indicator_long_window_balances(mod):
    """Across full years, ~half the days are good (Nov-Apr); within rounding."""
    idx = pd.bdate_range("2000-01-01", "2024-12-31")
    series = mod.halloween_indicator(idx)
    frac_on = float(series.mean())
    assert 0.45 <= frac_on <= 0.55, f"frac_on={frac_on:.3f} outside expected band"


def test_summer_stall_fraction_on(mod):
    """Summer stall: ~8 of 12 months ON (Jan-May, Oct-Dec) → ~67% of days."""
    idx = pd.bdate_range("2000-01-01", "2024-12-31")
    series = mod.summer_stall_indicator(idx)
    frac_on = float(series.mean())
    assert 0.62 <= frac_on <= 0.72, f"frac_on={frac_on:.3f} outside expected band"
