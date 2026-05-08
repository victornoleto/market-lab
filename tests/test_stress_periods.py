"""Unit tests for ``backtest.metrics.stress_periods`` — Phase 3.5b Task 7b.

Covers window slicing, metric computation, SPY alignment, and Markdown
rendering. Spec reference: ``specs/phase_3_5b_winners_validation.md``
§Task 7b.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.metrics.standard_report import Trade
from market_lab.backtest.metrics.stress_periods import (
    STANDARD_STRESS_WINDOWS,
    StressWindow,
    compute_all_stress_reports,
    compute_stress_report,
    render_multi_strategy_stress_markdown,
    render_stress_markdown,
)


def _make_equity(dates: pd.DatetimeIndex, start: float, pct_per_bar: float) -> pd.Series:
    """Synthetic geometric equity curve ``start * (1 + r) ** n``."""
    steps = np.arange(len(dates), dtype=float)
    values = start * (1.0 + pct_per_bar) ** steps
    return pd.Series(values, index=dates, name="equity")


# ---------------------------------------------------------------------------
# Canonical windows
# ---------------------------------------------------------------------------


def test_standard_windows_canonical_set():
    names = {w.name for w in STANDARD_STRESS_WINDOWS}
    assert names == {"2008_crisis", "2020_covid", "2022_bear", "2025_q1"}
    for w in STANDARD_STRESS_WINDOWS:
        assert w.start < w.end
        assert w.description  # non-empty


# ---------------------------------------------------------------------------
# compute_stress_report
# ---------------------------------------------------------------------------


def test_stress_report_positive_window():
    """Strategy +0.5%/day beats SPY −0.3%/day over a 50-bar window."""
    idx = pd.bdate_range("2020-02-19", periods=50)
    strat = _make_equity(idx, 100_000.0, 0.005)
    spy = _make_equity(idx, 100_000.0, -0.003)
    window = StressWindow(
        name="covid_synth",
        start=idx[0],
        end=idx[-1],
        description="synthetic",
    )
    report = compute_stress_report(strat, [], spy, window)
    assert report.bars == 50
    assert report.spy_bars == 50
    # Strategy compounds upwards, so total_return > 0 and max_dd ≈ 0.
    assert report.total_return_pct > 0.20
    assert report.max_drawdown_pct == pytest.approx(0.0, abs=1e-9)
    # SPY drifts down every bar → total_return < 0 and max_dd == 1 − (1-0.003)^49
    assert report.spy_total_return_pct < 0
    assert report.spy_max_drawdown_pct > 0.10
    # Excess return is strictly positive.
    assert report.excess_return_pct > 0
    # ΔDD is negative (strategy safer).
    assert report.delta_max_dd_pct < 0


def test_stress_report_window_outside_data_returns_empty():
    idx = pd.bdate_range("2010-01-04", periods=30)
    strat = _make_equity(idx, 100_000.0, 0.001)
    spy = _make_equity(idx, 100_000.0, 0.001)
    window = StressWindow(
        name="future",
        start=pd.Timestamp("2099-01-01"),
        end=pd.Timestamp("2099-12-31"),
        description="no data",
    )
    report = compute_stress_report(strat, [], spy, window)
    assert report.bars == 0
    assert report.spy_bars == 0
    assert report.total_return_pct == 0.0
    assert report.sharpe == 0.0


def test_stress_report_counts_only_fully_contained_trades():
    idx = pd.bdate_range("2008-09-01", periods=150)
    strat = _make_equity(idx, 100_000.0, 0.0)  # flat
    spy = _make_equity(idx, 100_000.0, 0.0)
    window = StressWindow(
        name="crisis",
        start=pd.Timestamp("2008-09-15"),
        end=pd.Timestamp("2009-01-15"),
        description="",
    )
    trades = [
        # fully inside — should count
        Trade(
            asset="X",
            entry_date=pd.Timestamp("2008-09-20"),
            exit_date=pd.Timestamp("2008-10-20"),
            entry_price=100.0,
            exit_price=110.0,
        ),
        # entry before window — excluded
        Trade(
            asset="X",
            entry_date=pd.Timestamp("2008-09-01"),
            exit_date=pd.Timestamp("2008-10-10"),
            entry_price=100.0,
            exit_price=95.0,
        ),
        # exit after window — excluded
        Trade(
            asset="X",
            entry_date=pd.Timestamp("2009-01-01"),
            exit_date=pd.Timestamp("2009-02-15"),
            entry_price=100.0,
            exit_price=105.0,
        ),
    ]
    report = compute_stress_report(strat, trades, spy, window)
    assert report.n_trades == 1


def test_stress_report_slice_rebases_to_window_start():
    """Metrics should be self-contained to the window, not carry the full-curve scale."""
    idx = pd.bdate_range("2000-01-03", periods=5000)
    # Full curve: long-run compounding
    full = _make_equity(idx, 1.0, 0.001)
    spy = _make_equity(idx, 1.0, 0.0005)
    window = StressWindow(
        name="mid_slice",
        start=pd.Timestamp("2015-01-02"),
        end=pd.Timestamp("2016-01-04"),
        description="",
    )
    report = compute_stress_report(full, [], spy, window)
    # First slice bar is the window's rebased start (equity=1.0).
    assert report.equity_curve.iloc[0] == pytest.approx(1.0)
    # Return over a year at 0.1%/bar ≈ 29% (1.001^252 - 1). No dependence on
    # the 15y of history before the window.
    assert 0.20 < report.total_return_pct < 0.40


# ---------------------------------------------------------------------------
# compute_all_stress_reports — runs the canonical 4 windows in one call
# ---------------------------------------------------------------------------


def test_compute_all_stress_reports_fires_each_window():
    idx = pd.bdate_range("2007-01-01", "2026-01-01")
    strat = _make_equity(idx, 100_000.0, 0.0003)
    spy = _make_equity(idx, 100_000.0, 0.0002)
    reports = compute_all_stress_reports(strat, [], spy)
    assert len(reports) == 4
    names = [r.window_name for r in reports]
    assert names == ["2008_crisis", "2020_covid", "2022_bear", "2025_q1"]
    for r in reports:
        assert r.bars > 0, f"{r.window_name}: empty slice"
        assert r.spy_bars > 0


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_render_stress_markdown_produces_table_and_window_legend():
    idx = pd.bdate_range("2008-01-01", "2023-12-31")
    strat = _make_equity(idx, 100_000.0, 0.0003)
    spy = _make_equity(idx, 100_000.0, 0.0002)
    reports = compute_all_stress_reports(strat, [], spy)
    md = render_stress_markdown("LETF Rotation EMA100/2x", reports)
    assert "## LETF Rotation EMA100/2x" in md
    assert "| window |" in md
    # Separator row for a 13-column table.
    assert "| --- " in md
    # Every window name appears in the row + legend.
    for w in STANDARD_STRESS_WINDOWS:
        assert w.name in md


def test_render_multi_strategy_stress_markdown_header():
    idx = pd.bdate_range("2008-01-01", "2023-12-31")
    strat = _make_equity(idx, 100_000.0, 0.0003)
    spy = _make_equity(idx, 100_000.0, 0.0002)
    reports = compute_all_stress_reports(strat, [], spy)
    md = render_multi_strategy_stress_markdown(
        [("LETF", reports), ("QQQ", reports)],
        title="Phase 3.5b stress",
    )
    assert md.startswith("# Phase 3.5b stress")
    assert "## LETF" in md
    assert "## QQQ" in md
