"""Unit tests for Wikipedia SPX reconstruction — pure logic, no network."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from ai_trade.backtest.data.wikipedia_spx import (
    _flatten_changes_table,
    constituents_on,
)


def _make_changes(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["date", "added", "removed"])
    return pd.DataFrame(
        [
            {
                "date": pd.Timestamp(r["date"]),
                "added": r.get("added"),
                "removed": r.get("removed"),
            }
            for r in rows
        ]
    )


def test_constituents_on_same_date_as_current_returns_current():
    current = {"AAPL", "MSFT", "NVDA"}
    changes = _make_changes([])
    assert constituents_on(date(2026, 1, 1), current, changes) == current


def test_constituents_on_undoes_an_addition():
    """If TSLA was added on 2020-12-21, on 2020-01-01 it was NOT in the set."""
    current = {"AAPL", "MSFT", "TSLA"}
    changes = _make_changes([{"date": "2020-12-21", "added": "TSLA", "removed": "AIV"}])
    result = constituents_on(date(2020, 1, 1), current, changes)
    # TSLA removed (was not yet in), AIV restored (was still in).
    assert result == {"AAPL", "MSFT", "AIV"}


def test_constituents_on_walks_back_through_multiple_changes():
    """Rollback order is independent of iteration direction for this logic."""
    current = {"AAPL", "MSFT", "NVDA"}
    changes = _make_changes([
        {"date": "2020-12-21", "added": "TSLA", "removed": "AIV"},
        {"date": "2025-01-15", "added": "NVDA", "removed": "OLD1"},
    ])
    result = constituents_on(date(2020, 1, 1), current, changes)
    # Both additions undone (TSLA, NVDA removed); both removals restored (AIV, OLD1).
    assert result == {"AAPL", "MSFT", "AIV", "OLD1"}


def test_constituents_on_ignores_changes_before_target_date():
    current = {"AAPL", "MSFT", "NVDA"}
    changes = _make_changes([
        {"date": "2019-01-01", "added": "NVDA", "removed": "OLD1"},
    ])
    # Target is after the change, so the change should not be undone.
    result = constituents_on(date(2020, 1, 1), current, changes)
    assert result == current


def test_constituents_on_handles_partial_rows():
    """Changes may have only added OR only removed (spin-off, acquisition)."""
    current = {"AAPL", "MSFT"}
    changes = _make_changes([
        {"date": "2025-06-01", "added": "MSFT", "removed": None},  # add-only
        {"date": "2025-06-15", "added": None, "removed": "OLD"},   # remove-only
    ])
    result = constituents_on(date(2025, 1, 1), current, changes)
    # MSFT added → undo adds means discard MSFT; OLD removed → add OLD back.
    assert result == {"AAPL", "OLD"}


def test_constituents_on_rejects_malformed_changes():
    bad = pd.DataFrame({"date": [pd.Timestamp("2024-01-01")]})  # missing added, removed
    with pytest.raises(ValueError, match="missing columns"):
        constituents_on(date(2020, 1, 1), {"AAPL"}, bad)


def test_flatten_changes_handles_standard_wikipedia_shape():
    """Smoke test for the two-row-header shape we expect from Wikipedia."""
    cols = pd.MultiIndex.from_tuples([
        ("Date", "Date"),
        ("Added", "Ticker"),
        ("Added", "Security"),
        ("Removed", "Ticker"),
        ("Removed", "Security"),
        ("Reason", "Reason"),
    ])
    raw = pd.DataFrame(
        [
            ["December 21, 2020", "TSLA", "Tesla, Inc.", "AIV", "Apartment Invest.", "Market cap"],
            ["June 20, 2023", "FICO", "Fair Isaac Corp.", "LB", "L Brands", "Market cap"],
        ],
        columns=cols,
    )
    flat = _flatten_changes_table(raw)
    assert list(flat.columns) == ["date", "added", "removed"]
    assert len(flat) == 2
    assert pd.Timestamp("2020-12-21") in flat["date"].values
    assert "TSLA" in flat["added"].values
    assert "AIV" in flat["removed"].values


def test_flatten_changes_rejects_flat_columns():
    raw = pd.DataFrame({"Date": ["2020-12-21"], "Added": ["TSLA"], "Removed": ["AIV"]})
    with pytest.raises(ValueError, match="MultiIndex"):
        _flatten_changes_table(raw)
