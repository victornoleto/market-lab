"""Regression tests for studies/gold_swing_loop/cost_models.py.

These guard the dual-broker cost helpers used by every gold-swing-loop
iteration. Iter 001 introduced them; iter 002+ should not silently
break the published rate cards or the DARF month allocation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studies" / "gold_swing_loop"))

from cost_models import (  # noqa: E402
    INTER_DARF_RATE,
    INTER_FX_RT_BPS,
    PEPPERSTONE_SPREAD_RT_BPS,
    PEPPERSTONE_SWAP_LONG_BPS,
    PEPPERSTONE_WEEKEND_MULT,
    apply_inter_costs_with_darf,
    apply_pepperstone_costs,
)


@pytest.fixture
def daily_index_31bd():
    return pd.date_range("2024-01-01", periods=31, freq="B")


@pytest.fixture
def long_step_30bp_daily(daily_index_31bd):
    """Open at bar 1, hold +1 long for 30 business days, +5% total return."""
    ret = pd.Series([0.0] + [0.05 / 30] * 30, index=daily_index_31bd)
    pos = pd.Series([1.0] * 31, index=daily_index_31bd)
    pos.iloc[0] = 0.0  # opens at bar 1
    return ret, pos


def test_pep_intraday_close_zeroes_swap(long_step_30bp_daily):
    ret, pos = long_step_30bp_daily
    br = apply_pepperstone_costs(ret, pos, intraday_close=True)
    s = br.summary()
    assert s["swap_total_pnl"] == 0.0
    assert s["n_swap_nights"] == 0
    assert s["n_weekend_holds"] == 0
    # Spread = 4 bps per side × turnover 1.0 = 4 bps
    assert abs(s["spread_total_pnl"] + PEPPERSTONE_SPREAD_RT_BPS / 2 / 1e4) < 1e-9


def test_pep_swing_charges_swap_per_night_with_weekend_mult(long_step_30bp_daily):
    ret, pos = long_step_30bp_daily
    br = apply_pepperstone_costs(ret, pos, intraday_close=False)
    s = br.summary()
    # 30 nights overnight (the open-bar position is 0 then carries over the
    # remaining 30 bars; pos.shift(1) turns into 1 from bar 2 onward → 29
    # nights with overnight). Weekend Mondays during the 30-bd window get the
    # 3x multiplier.
    assert s["n_swap_nights"] > 25
    # Weekend hold count is positive (within 30 business days there are weeks).
    assert s["n_weekend_holds"] >= 4
    # Net is gross minus spread minus swap.
    assert s["swap_total_pnl"] < 0  # swap is a drag for longs
    assert s["spread_total_pnl"] < 0
    assert s["fx_total_pnl"] == 0
    assert s["darf_total_pnl"] == 0


def test_pep_weekend_mult_strict():
    """Hold +1 long over a Fri→Mon weekend; the Monday bar must apply the
    3× weekend multiplier on swap.

    Convention: pos[t] = decision at end of bar t, applied to ret[t+1]
    via shift(1). pos[Fri]=1 means the long is carried over the weekend
    into Monday's bar — Monday's swap = 1 night × 3× weekend mult.
    """
    idx = pd.date_range("2024-01-05", periods=4, freq="B")  # Fri Mon Tue Wed
    ret = pd.Series([0.0] * 4, index=idx)
    pos = pd.Series([1.0] * 4, index=idx)  # already long at start (held from prior bar)
    br = apply_pepperstone_costs(ret, pos, intraday_close=False)

    # Overnight position at each bar: pos.shift(1) = [NaN→0, 1, 1, 1].
    # So 3 nights with swap accrual: Mon, Tue, Wed. Mon is the weekend bar.
    swap_per_night = abs(PEPPERSTONE_SWAP_LONG_BPS) / 1e4
    expected_swap = swap_per_night * (PEPPERSTONE_WEEKEND_MULT + 1 + 1)  # Mon×3 + Tue + Wed
    actual_swap = -br.summary()["swap_total_pnl"]
    assert abs(actual_swap - expected_swap) < 1e-9


def test_pep_index_mismatch_raises():
    a = pd.Series([0.0] * 5, index=pd.date_range("2024-01-01", periods=5, freq="B"))
    b = pd.Series([1.0] * 5, index=pd.date_range("2024-02-01", periods=5, freq="B"))
    with pytest.raises(ValueError):
        apply_pepperstone_costs(a, b)


def test_inter_long_only_enforced(long_step_30bp_daily):
    ret, pos = long_step_30bp_daily
    with pytest.raises(ValueError, match="LONG-ONLY"):
        apply_inter_costs_with_darf(ret, -pos)


def test_inter_fx_charged_per_turn_no_swap(long_step_30bp_daily):
    ret, pos = long_step_30bp_daily
    br = apply_inter_costs_with_darf(ret, pos)
    s = br.summary()
    assert s["swap_total_pnl"] == 0.0
    assert s["n_swap_nights"] == 0
    # FX = 50 bps per side × turnover 1.0 = 50 bps.
    expected_fx = -INTER_FX_RT_BPS / 2 / 1e4
    assert abs(s["fx_total_pnl"] - expected_fx) < 1e-9


def test_inter_darf_only_on_positive_months(long_step_30bp_daily):
    """+5% over Jan should produce positive DARF; -5% should produce zero."""
    ret_pos, pos = long_step_30bp_daily
    br_pos = apply_inter_costs_with_darf(ret_pos, pos)
    assert -br_pos.summary()["darf_total_pnl"] > 0  # cost is positive

    ret_neg = ret_pos * -1.0
    br_neg = apply_inter_costs_with_darf(ret_neg, pos)
    assert br_neg.summary()["darf_total_pnl"] == 0.0


def test_inter_darf_rate_matches_constant():
    """The aggregate DARF on a single positive month equals 15% of monthly
    pre-tax PnL."""
    idx = pd.date_range("2024-02-01", periods=20, freq="B")
    ret = pd.Series([0.0] + [0.04 / 19] * 19, index=idx)
    pos = pd.Series([1.0] * 20, index=idx)
    pos.iloc[0] = 0.0
    br = apply_inter_costs_with_darf(ret, pos)
    pre_tax = br.summary()["gross_total_pnl"] + br.summary()["fx_total_pnl"]
    expected_darf = INTER_DARF_RATE * pre_tax
    actual_darf = -br.summary()["darf_total_pnl"]
    assert abs(actual_darf - expected_darf) < 1e-9


def test_pep_zero_position_zero_costs(daily_index_31bd):
    ret = pd.Series(np.linspace(-0.001, 0.001, 31), index=daily_index_31bd)
    pos = pd.Series([0.0] * 31, index=daily_index_31bd)
    br = apply_pepperstone_costs(ret, pos)
    s = br.summary()
    assert s["spread_total_pnl"] == 0.0
    assert s["swap_total_pnl"] == 0.0
    assert s["net_total_pnl"] == 0.0
