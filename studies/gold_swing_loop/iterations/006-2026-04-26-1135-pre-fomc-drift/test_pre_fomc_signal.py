"""TDD tests for iter 006 — Pre-FOMC drift T-2 to T+1.

Verifies (before running full backtest):

1. FOMC date list integrity (~170 events 2004-2026, no duplicates,
   monotonically increasing, all weekdays).
2. Trading-day arithmetic helper returns correct T-2 and T+1 indices.
3. Position state machine: a single FOMC event produces position == 1.0
   on exactly 4 consecutive bars and 0.0 elsewhere.
4. Mean hold = 4.0 with non-overlapping FOMC windows.
5. Edge cases: FOMC date out of dataset window → no contribution.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))

from run_backtest import (  # noqa: E402
    FOMC_DATES,
    pre_fomc_position,
    compute_mean_hold_days,
    pre_validation_screen,
)


# ---------------------------------------------------------------------------
# 1. FOMC date list integrity
# ---------------------------------------------------------------------------


def test_fomc_dates_count_in_range():
    """22 yr × 8 events/yr = 176, plus partial 2026 → expect 170-180."""
    assert 170 <= len(FOMC_DATES) <= 180


def test_fomc_dates_monotonically_increasing():
    sorted_dates = sorted(FOMC_DATES)
    assert FOMC_DATES == sorted_dates, "FOMC_DATES must be in chronological order"


def test_fomc_dates_no_duplicates():
    assert len(set(FOMC_DATES)) == len(FOMC_DATES)


def test_fomc_dates_all_weekdays():
    """Scheduled FOMC announcements never fall on Sat/Sun."""
    for d in FOMC_DATES:
        ts = pd.Timestamp(d)
        assert ts.dayofweek < 5, f"{d} is a weekend (dayofweek={ts.dayofweek})"


def test_fomc_dates_span_full_window():
    """First FOMC ≤ 2004-12-31, last FOMC ≥ 2026-01-01."""
    assert FOMC_DATES[0] <= "2005-01-01"
    assert FOMC_DATES[-1] >= "2026-01-01"


# ---------------------------------------------------------------------------
# 2/3. Position state machine on a synthetic calendar
# ---------------------------------------------------------------------------


def test_pre_fomc_position_single_event_4_bars_held():
    """One FOMC date in the middle of a 21-bar synthetic calendar →
    exactly 4 bars held [T-2, T-1, T, T+1], rest 0."""
    calendar = pd.bdate_range("2024-01-01", "2024-01-29")  # 21 business days
    fomc = ["2024-01-17"]  # mid-window
    pos = pre_fomc_position(calendar, fomc)

    fomc_idx = list(calendar).index(pd.Timestamp("2024-01-17"))
    expected = np.zeros(len(calendar))
    expected[fomc_idx - 2:fomc_idx + 2] = 1.0  # [T-2, T-1, T, T+1]
    np.testing.assert_array_equal(pos.values, expected)


def test_pre_fomc_position_two_events_each_4_bars():
    """Two non-overlapping FOMC events → 8 total bars held."""
    calendar = pd.bdate_range("2024-01-01", "2024-03-31")
    fomc = ["2024-01-31", "2024-03-20"]  # spaced > 4 bars apart
    pos = pre_fomc_position(calendar, fomc)
    assert pos.sum() == 8.0
    assert (pos > 0).sum() == 8


def test_pre_fomc_position_event_outside_window_ignored():
    """FOMC date outside calendar → contributes nothing."""
    calendar = pd.bdate_range("2024-01-01", "2024-01-31")
    fomc = ["2025-06-01"]  # far future
    pos = pre_fomc_position(calendar, fomc)
    assert pos.sum() == 0.0


def test_pre_fomc_position_event_too_close_to_start_truncated():
    """FOMC at index 1 → T-2 would be index -1 (out of range), so the
    event is dropped (no partial position). Strict full-4-bar coverage."""
    calendar = pd.bdate_range("2024-01-01", "2024-01-31")
    # Pick the FOMC = calendar[1] so T-2 = calendar[-1] is invalid
    too_early = calendar[1].strftime("%Y-%m-%d")
    pos = pre_fomc_position(calendar, [too_early])
    assert pos.sum() == 0.0, "event with no T-2 should be dropped"


def test_pre_fomc_position_event_too_close_to_end_truncated():
    """FOMC at index N-1 → T+1 would be N (out of range), so the event
    is dropped."""
    calendar = pd.bdate_range("2024-01-01", "2024-01-31")
    too_late = calendar[-1].strftime("%Y-%m-%d")
    pos = pre_fomc_position(calendar, [too_late])
    assert pos.sum() == 0.0


def test_pre_fomc_position_non_calendar_date_skipped():
    """FOMC date not present in trading calendar (e.g. holiday) is
    aligned to nearest backward business day for T0; the strategy
    still produces 4-bar window, BUT we treat the FOMC as belonging
    to the actual session at its date — if no exact match, drop."""
    # Use a Saturday → not in bdate_range
    calendar = pd.bdate_range("2024-01-01", "2024-01-31")
    weekend = "2024-01-13"  # Saturday
    pos = pre_fomc_position(calendar, [weekend])
    assert pos.sum() == 0.0, "weekend FOMC date should be dropped"


# ---------------------------------------------------------------------------
# 4. Mean hold computation
# ---------------------------------------------------------------------------


def test_mean_hold_with_two_events_equals_4():
    calendar = pd.bdate_range("2024-01-01", "2024-03-31")
    fomc = ["2024-01-31", "2024-03-20"]
    pos = pre_fomc_position(calendar, fomc)
    mean_hold, n_trades = compute_mean_hold_days(pos)
    assert n_trades == 2
    assert mean_hold == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# 5. Pre-validation screen smoke test on a synthetic positive-drift fixture
# ---------------------------------------------------------------------------


def test_pre_validation_screen_passes_on_synthetic_positive_drift():
    """Build a fixture where the 4-bar pre-FOMC window is engineered
    to be reliably positive (large effect size). Verify that
    pre_validation_screen returns passed=True. The synthetic lift is
    deliberately large (+5%) to ensure t-stat clears 0.5 against the
    underlying random-walk noise."""
    n = 800
    rng = np.random.default_rng(42)
    base_price = 100.0
    rets = rng.normal(0.0, 0.005, size=n)
    closes = base_price * np.cumprod(1.0 + rets)
    idx = pd.bdate_range("2010-01-01", periods=n)
    close = pd.Series(closes, index=idx, name="close")

    # Inject 60 FOMC events at known positions with +5% lift on T+1.
    # Need ≥ 50 events to pass min_events.
    fomc_positions = list(range(50, n - 5, 12))[:60]
    fomc_dates = [idx[i].strftime("%Y-%m-%d") for i in fomc_positions]
    for i in fomc_positions:
        close.iloc[i + 1] *= 1.05  # +5% lift per event (large effect)

    pre_val = pre_validation_screen(close, fomc_dates)
    assert pre_val["n_events"] >= 50
    assert pre_val["mean_4d_log_return"] > 0
    assert pre_val["passed"]


def test_pre_validation_screen_fails_on_negative_drift_fixture():
    """Build a fixture with negative drift → pre_validation_screen
    returns passed=False (kill-criterion fires)."""
    n = 500
    rng = np.random.default_rng(7)
    rets = rng.normal(0.0, 0.005, size=n)
    closes = 100.0 * np.cumprod(1.0 + rets)
    idx = pd.bdate_range("2010-01-01", periods=n)
    close = pd.Series(closes, index=idx, name="close")

    fomc_positions = list(range(50, n - 5, 15))[:30]
    fomc_dates = [idx[i].strftime("%Y-%m-%d") for i in fomc_positions]
    for i in fomc_positions:
        close.iloc[i + 1] *= 0.99  # negative 1% drift per event

    pre_val = pre_validation_screen(close, fomc_dates)
    assert pre_val["n_events"] >= 25
    assert pre_val["mean_4d_log_return"] < 0
    assert not pre_val["passed"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
