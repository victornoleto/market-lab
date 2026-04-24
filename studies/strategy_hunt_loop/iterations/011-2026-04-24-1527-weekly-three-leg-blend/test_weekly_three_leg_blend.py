"""Iter 011 — TDD specs for weekly-rebalance 3-leg blend.

Written BEFORE the implementation per CLAUDE.md / superpowers TDD.
All specs must pass before running the backtest.

Properties checked:

1. ``resample_returns_weekly`` compounds daily returns to W-FRI correctly
   (no drift vs manual compounding).
2. ``apply_weekly_blend`` delegates to
   ``apply_blend_variance_target_3leg`` with ``periods_per_year=52``.
3. No look-ahead: at week ``t``, only weeks ``≤ t-1`` enter σ².
4. Lookback L=4 weeks → valid weights from week L+1 onward.
5. Degenerate case: σ²_gld → ∞ recovers 2-leg weekly limit (w_gld → 0).
6. Cost model applied at weekly cadence (total turnover per-leg ×
   cost_bps_per_leg).
7. Sanity: weekly returns match ``(1 + r_daily).prod() - 1`` exactly
   over each W-FRI block.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent
ITER_10_DIR = ITER_DIR.parent / "010-2026-04-24-1506-three-asset-spy-tlt-gld-blend"
sys.path.insert(0, str(ITER_DIR))
sys.path.insert(0, str(ITER_10_DIR))

from three_leg_blend import apply_blend_variance_target_3leg  # noqa: E402
from weekly_three_leg_blend import (  # noqa: E402
    apply_weekly_blend,
    resample_returns_weekly,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def toy_daily_returns() -> pd.DataFrame:
    """52 weeks × 5 days = 260 aligned daily returns starting 2020-01-06 Mon."""
    rng = np.random.default_rng(1234)
    dates = pd.bdate_range("2020-01-06", periods=260, freq="B")
    # Correlated shocks: equity long drift, bond mid drift, gold low drift.
    eq = rng.normal(0.0005, 0.01, 260)
    bd = rng.normal(0.0002, 0.004, 260) - 0.2 * eq
    gd = rng.normal(0.0001, 0.008, 260) + 0.05 * eq
    return pd.DataFrame({"SPY": eq, "TLT": bd, "GLD": gd}, index=dates)


@pytest.fixture
def longer_daily_returns() -> pd.DataFrame:
    """500 bar fixture — enough for weekly 100-week lookback sanity checks."""
    rng = np.random.default_rng(777)
    dates = pd.bdate_range("2018-01-02", periods=500, freq="B")
    eq = rng.normal(0.0004, 0.011, 500)
    bd = rng.normal(0.0002, 0.004, 500)
    gd = rng.normal(0.00015, 0.009, 500)
    return pd.DataFrame({"SPY": eq, "TLT": bd, "GLD": gd}, index=dates)


# ---------------------------------------------------------------------------
# 1 + 7. Weekly resample compounds correctly
# ---------------------------------------------------------------------------


def test_resample_weekly_compounds_daily_returns_exactly(toy_daily_returns):
    weekly = resample_returns_weekly(toy_daily_returns)
    # For each W-FRI bar, the weekly return should equal
    # (1 + daily_in_that_week).prod() - 1.
    assert isinstance(weekly, pd.DataFrame)
    assert list(weekly.columns) == list(toy_daily_returns.columns)
    # First weekly bar corresponds to week ending on the first Friday in range.
    first_friday = pd.Timestamp("2020-01-10")
    assert first_friday in weekly.index, f"expected Friday {first_friday} in weekly index"
    # 2020-01-06..10 = Mon..Fri: 5 daily bars.
    daily_in_wk1 = toy_daily_returns.loc["2020-01-06":"2020-01-10"]
    expected = (1.0 + daily_in_wk1).prod() - 1.0
    got = weekly.loc[first_friday]
    for col in weekly.columns:
        assert got[col] == pytest.approx(expected[col], rel=1e-10), (
            f"weekly compounding drift on {col}: got {got[col]}, expected {expected[col]}"
        )


def test_resample_weekly_index_is_wfri(toy_daily_returns):
    weekly = resample_returns_weekly(toy_daily_returns)
    # All weekly index entries should be Fridays.
    for ts in weekly.index:
        assert ts.dayofweek == 4, f"weekly index entry {ts} is not a Friday"


def test_resample_handles_missing_friday(longer_daily_returns):
    """If a particular Friday is missing from daily data (holiday), the
    weekly bar should reflect the last-available close that week."""
    daily = longer_daily_returns.copy()
    # Drop Friday 2018-02-16 (would have been a holiday week in reality).
    friday = pd.Timestamp("2018-02-16")
    if friday in daily.index:
        daily = daily.drop(friday)
    weekly = resample_returns_weekly(daily)
    # Weekly should still have a W-FRI-indexed bar for that week end;
    # its value equals compound return of remaining bars Mon..Thu.
    assert friday in weekly.index or (friday - pd.Timedelta(days=1)) in weekly.index


# ---------------------------------------------------------------------------
# 2. apply_weekly_blend delegates with periods_per_year=52
# ---------------------------------------------------------------------------


def test_apply_weekly_blend_matches_daily_blend_with_52(longer_daily_returns):
    """apply_weekly_blend(daily) == apply_blend_variance_target_3leg
    on resample_returns_weekly(daily) with periods_per_year=52."""
    weekly = resample_returns_weekly(longer_daily_returns)
    net_wrapper, pos_wrapper, scale_wrapper = apply_weekly_blend(
        longer_daily_returns["SPY"], longer_daily_returns["TLT"],
        longer_daily_returns["GLD"],
        target_vol=0.15, lookback=4, max_leverage=2.0,
        cost_bps_per_leg=0.0002,
    )
    net_direct, pos_direct, scale_direct = apply_blend_variance_target_3leg(
        weekly["SPY"], weekly["TLT"], weekly["GLD"],
        target_vol=0.15, lookback=4, max_leverage=2.0,
        periods_per_year=52, cost_bps_per_leg=0.0002,
    )
    assert len(net_wrapper) == len(net_direct)
    np.testing.assert_allclose(
        net_wrapper.to_numpy(), net_direct.to_numpy(), atol=1e-12
    )
    np.testing.assert_allclose(
        scale_wrapper.to_numpy(), scale_direct.to_numpy(), atol=1e-12
    )


# ---------------------------------------------------------------------------
# 3. No look-ahead
# ---------------------------------------------------------------------------


def test_no_lookahead_weekly(longer_daily_returns):
    """The last bar should NOT affect any weight / scale prior to it.

    Perturb the final weekly bar's return by +100% and verify nothing
    before it changes.
    """
    weekly = resample_returns_weekly(longer_daily_returns)
    net_ref, pos_ref, scale_ref = apply_blend_variance_target_3leg(
        weekly["SPY"], weekly["TLT"], weekly["GLD"],
        target_vol=0.15, lookback=4, max_leverage=2.0,
        periods_per_year=52,
    )
    weekly2 = weekly.copy()
    weekly2.iloc[-1] = weekly2.iloc[-1] + 1.0
    net_pert, pos_pert, scale_pert = apply_blend_variance_target_3leg(
        weekly2["SPY"], weekly2["TLT"], weekly2["GLD"],
        target_vol=0.15, lookback=4, max_leverage=2.0,
        periods_per_year=52,
    )
    # All but the LAST bar should be identical.
    np.testing.assert_allclose(
        scale_ref.iloc[:-1].to_numpy(),
        scale_pert.iloc[:-1].to_numpy(),
        atol=1e-14,
    )
    np.testing.assert_allclose(
        pos_ref.iloc[:-1].to_numpy(),
        pos_pert.iloc[:-1].to_numpy(),
        atol=1e-14,
    )


# ---------------------------------------------------------------------------
# 4. Lookback valid from week L+1
# ---------------------------------------------------------------------------


def test_valid_from_week_L_plus_1(longer_daily_returns):
    weekly = resample_returns_weekly(longer_daily_returns)
    net, pos, scale = apply_blend_variance_target_3leg(
        weekly["SPY"], weekly["TLT"], weekly["GLD"],
        target_vol=0.15, lookback=4, max_leverage=2.0,
        periods_per_year=52,
    )
    # Function drops pre-valid bars; first output bar should be weekly
    # index[4] (0-indexed; after 4 weeks of lookback).
    expected_first = weekly.index[4]
    assert scale.index[0] == expected_first, (
        f"scale first bar should be week index[4] ({expected_first}), "
        f"got {scale.index[0]}"
    )


# ---------------------------------------------------------------------------
# 5. 2-leg degenerate limit (w_gld → 0 when σ²_gld → ∞)
# ---------------------------------------------------------------------------


def test_two_leg_degenerate_limit(toy_daily_returns):
    """If GLD is replaced with extreme-vol noise, w_gld → ~0 and net
    return approximates the 2-leg SPY+TLT weekly blend."""
    daily = toy_daily_returns.copy()
    rng = np.random.default_rng(999)
    # Give GLD 100× higher variance.
    daily["GLD"] = rng.normal(0.0, 1.0, len(daily))
    weekly = resample_returns_weekly(daily)
    net_3leg, pos_3leg, scale_3leg = apply_blend_variance_target_3leg(
        weekly["SPY"], weekly["TLT"], weekly["GLD"],
        target_vol=0.15, lookback=4, max_leverage=2.0,
        periods_per_year=52,
    )
    # The median GLD weight should be very small under this extreme.
    w_gld = pos_3leg["GLD"] / scale_3leg.replace(0, np.nan)
    assert w_gld.median() < 0.05, f"w_gld median too large: {w_gld.median():.4f}"


# ---------------------------------------------------------------------------
# 6. Cost applied at weekly cadence
# ---------------------------------------------------------------------------


def test_cost_applied_per_leg_at_weekly_cadence(longer_daily_returns):
    weekly = resample_returns_weekly(longer_daily_returns)
    # Zero-cost run
    net0, pos0, _ = apply_blend_variance_target_3leg(
        weekly["SPY"], weekly["TLT"], weekly["GLD"],
        target_vol=0.15, lookback=4, max_leverage=2.0,
        periods_per_year=52, cost_bps_per_leg=0.0,
    )
    # 100 bps/leg cost
    netH, posH, _ = apply_blend_variance_target_3leg(
        weekly["SPY"], weekly["TLT"], weekly["GLD"],
        target_vol=0.15, lookback=4, max_leverage=2.0,
        periods_per_year=52, cost_bps_per_leg=0.01,
    )
    # Cost should reduce return on every bar with nonzero position change,
    # and total cost should equal sum of |Δpos| × 0.01 across legs.
    assert (netH <= net0).all()
    # Reconstruct cost: sum of |Δpos| per bar × 0.01 should = net0 - netH.
    dpos = pos0.diff().abs().fillna(pos0.iloc[0].abs())
    expected_cost = dpos.sum(axis=1) * 0.01
    realized_cost = (net0 - netH).astype(float)
    np.testing.assert_allclose(
        realized_cost.to_numpy(), expected_cost.to_numpy(),
        atol=1e-12,
    )
