"""Iter 078 — TDD spec for Antonacci Dual Momentum (GEM) base strategy.

Tests the rotation logic, T-1 lag (no look-ahead), abs+rel momentum
truth table, transaction cost on rebalance, and pandas/numpy parity.

Citations:
* `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* `[stocks_on_the_move, p.21-30]` — momentum framework.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ITER_DIR))

from antonacci_dual_momentum import (  # noqa: E402
    compute_gem_returns,
    compute_lookback_return,
    compute_monthly_rebalance_dates,
    gem_signal,
)
from numpy_reference_iter078 import compute_gem_returns_np  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def deterministic_prices() -> dict[str, pd.Series]:
    """Build 3-asset deterministic monthly-end price series.

    13 monthly observations covering Jan-2020 through Jan-2021.
    SPY ramps up steadily, EFA crashes mid-period then recovers,
    AGG drifts slowly. Designed so the GEM signal cycles through
    SPY-leads, AGG (defensive), EFA-leads.
    """
    dates = pd.date_range("2020-01-31", periods=13, freq="ME")
    spy = pd.Series(
        [100.0, 102, 105, 108, 110, 112, 115, 118, 120, 122, 124, 126, 128],
        index=dates, name="SPY",
    )
    efa = pd.Series(
        [100.0, 95, 88, 80, 70, 65, 60, 65, 75, 85, 95, 105, 115],
        index=dates, name="EFA",
    )
    agg = pd.Series(
        [100.0, 100.5, 101, 101.5, 102, 102.5, 103, 103.5, 104, 104.5, 105, 105.5, 106],
        index=dates, name="AGG",
    )
    return {"SPY": spy, "EFA": efa, "AGG": agg}


# ---------------------------------------------------------------------------
# 1. Lookback return computation
# ---------------------------------------------------------------------------


def test_lookback_return_3m_basic(deterministic_prices):
    """3-month lookback: P(t)/P(t-3) - 1 at each month-end."""
    spy = deterministic_prices["SPY"]
    lb = compute_lookback_return(spy, lookback_months=3)
    # First 3 entries (idx 0..2) should be NaN (insufficient history).
    assert lb.iloc[0:3].isna().all()
    # At idx=3 (Apr-2020), 3m ret = 108/100 - 1 = 0.08
    assert pytest.approx(lb.iloc[3], abs=1e-9) == 0.08
    # At idx=12 (Jan-2021), 3m ret = 128/122 - 1 ≈ 0.04918
    assert pytest.approx(lb.iloc[12], abs=1e-6) == (128 / 122 - 1)


def test_lookback_return_12m(deterministic_prices):
    """12-month lookback: 1y trailing return."""
    spy = deterministic_prices["SPY"]
    lb = compute_lookback_return(spy, lookback_months=12)
    # First 12 entries should be NaN.
    assert lb.iloc[0:12].isna().all()
    # At idx=12 (Jan-2021), 12m ret = 128/100 - 1 = 0.28
    assert pytest.approx(lb.iloc[12], abs=1e-9) == 0.28


# ---------------------------------------------------------------------------
# 2. GEM signal — relative + absolute momentum truth table
# ---------------------------------------------------------------------------


def test_gem_signal_spy_leads_with_positive_momentum():
    """SPY > EFA AND SPY > 0 → allocate SPY."""
    idx = pd.date_range("2020-01-31", periods=3, freq="ME")
    spy_lb = pd.Series([0.10, 0.05, 0.20], index=idx)
    efa_lb = pd.Series([0.05, -0.02, 0.15], index=idx)
    threshold = pd.Series([0.0, 0.0, 0.0], index=idx)
    sig = gem_signal(spy_lb, efa_lb, threshold)
    assert (sig == "SPY").all()


def test_gem_signal_efa_leads_with_positive_momentum():
    """EFA > SPY AND EFA > 0 → allocate EFA."""
    idx = pd.date_range("2020-01-31", periods=3, freq="ME")
    spy_lb = pd.Series([0.05, 0.10, 0.15], index=idx)
    efa_lb = pd.Series([0.10, 0.20, 0.20], index=idx)
    threshold = pd.Series([0.0, 0.0, 0.0], index=idx)
    sig = gem_signal(spy_lb, efa_lb, threshold)
    assert (sig == "EFA").all()


def test_gem_signal_winner_below_threshold_goes_to_agg():
    """Winner's lookback < threshold → allocate AGG (defensive)."""
    idx = pd.date_range("2020-01-31", periods=3, freq="ME")
    spy_lb = pd.Series([-0.05, -0.10, -0.02], index=idx)
    efa_lb = pd.Series([-0.10, -0.20, -0.05], index=idx)
    threshold = pd.Series([0.0, 0.0, 0.0], index=idx)
    sig = gem_signal(spy_lb, efa_lb, threshold)
    assert (sig == "AGG").all()


def test_gem_signal_threshold_via_t_bill_proxy():
    """If threshold is positive (T-bill yield > 0), winner must beat it."""
    idx = pd.date_range("2020-01-31", periods=3, freq="ME")
    spy_lb = pd.Series([0.03, 0.01, 0.10], index=idx)
    efa_lb = pd.Series([0.02, 0.005, 0.05], index=idx)
    threshold = pd.Series([0.05, 0.02, 0.05], index=idx)
    sig = gem_signal(spy_lb, efa_lb, threshold)
    # M0: SPY=0.03 < 0.05 threshold → AGG
    # M1: SPY=0.01 < 0.02 → AGG
    # M2: SPY=0.10 > 0.05 → SPY
    assert sig.iloc[0] == "AGG"
    assert sig.iloc[1] == "AGG"
    assert sig.iloc[2] == "SPY"


# ---------------------------------------------------------------------------
# 3. T-1 lag — signal at end-of-month-M applies to month-M+1 returns
# ---------------------------------------------------------------------------


def test_t_minus_1_lag_signal_to_returns():
    """Signal computed on month-M close drives day-1-of-M+1 returns."""
    daily_idx = pd.date_range("2020-01-01", "2020-04-30", freq="B")
    rets = {
        "SPY": pd.Series(0.001, index=daily_idx),
        "EFA": pd.Series(-0.001, index=daily_idx),
        "AGG": pd.Series(0.0001, index=daily_idx),
    }
    monthly_idx = pd.date_range("2020-01-31", periods=4, freq="ME")
    signal = pd.Series(["SPY", "EFA", "AGG", "SPY"], index=monthly_idx)
    out = compute_gem_returns(rets, signal, trans_cost_bps=0.0)
    # Pre-Feb (Jan): no signal applied yet (first month is warmup) → 0
    jan = out.loc[out.index < "2020-02-01"]
    assert np.allclose(jan.values, 0.0, atol=1e-12)
    # Feb returns should follow the Jan-31 signal = "SPY" → +0.001/day
    feb = out.loc[(out.index >= "2020-02-01") & (out.index < "2020-03-01")]
    assert np.allclose(feb.values, 0.001, atol=1e-12)
    # Mar follows Feb-29 signal = "EFA" → -0.001/day
    mar = out.loc[(out.index >= "2020-03-01") & (out.index < "2020-04-01")]
    assert np.allclose(mar.values, -0.001, atol=1e-12)


# ---------------------------------------------------------------------------
# 4. Transaction cost
# ---------------------------------------------------------------------------


def test_transaction_cost_charged_on_first_day_of_new_allocation():
    """Allocation switch from SPY to EFA: cost charged on first day of new month."""
    daily_idx = pd.date_range("2020-01-01", "2020-03-31", freq="B")
    rets = {
        "SPY": pd.Series(0.001, index=daily_idx),
        "EFA": pd.Series(0.0, index=daily_idx),
        "AGG": pd.Series(0.0, index=daily_idx),
    }
    monthly_idx = pd.date_range("2020-01-31", periods=3, freq="ME")
    signal = pd.Series(["SPY", "EFA", "EFA"], index=monthly_idx)
    out_no_cost = compute_gem_returns(rets, signal, trans_cost_bps=0.0)
    out_with_cost = compute_gem_returns(rets, signal, trans_cost_bps=10.0)
    # Switch days where cost should hit:
    #   Feb-3 (first business day of Feb) — initial SPY allocation = no prior, switch from cash
    #   Mar-2 (first business day of Mar) — switch SPY → EFA
    feb_first = out_with_cost.loc["2020-02-03"]
    mar_first = out_with_cost.loc["2020-03-02"]
    # Cost = 10 bps × 1.0 (full switch) = 0.001
    # Feb-3 has SPY return +0.001 minus cost 0.001 → net 0.0
    assert pytest.approx(feb_first, abs=1e-9) == 0.001 - 0.001
    # Mar-2 has EFA return 0.0 minus cost 0.002 (|w_efa - w_spy| = 2.0)
    # since switching from full SPY (long 1.0) to full EFA (long 1.0) means
    # |Δ_SPY| + |Δ_EFA| = 1.0 + 1.0 = 2.0 turnover units
    assert pytest.approx(mar_first, abs=1e-9) == 0.0 - 0.002
    # No cost on intra-month days
    feb_mid = out_with_cost.loc["2020-02-14"]
    assert pytest.approx(feb_mid, abs=1e-12) == out_no_cost.loc["2020-02-14"]


# ---------------------------------------------------------------------------
# 5. Numpy reference parity (G7)
# ---------------------------------------------------------------------------


def test_numpy_reference_matches_pandas_to_1e9():
    """Numpy-pure GEM returns match pandas implementation element-wise."""
    rng = np.random.default_rng(20260426)
    daily_idx = pd.date_range("2010-01-04", "2024-12-31", freq="B")
    n = len(daily_idx)
    rets = {
        "SPY": pd.Series(rng.normal(5e-4, 0.012, n), index=daily_idx),
        "EFA": pd.Series(rng.normal(3e-4, 0.013, n), index=daily_idx),
        "AGG": pd.Series(rng.normal(1e-4, 0.004, n), index=daily_idx),
    }
    monthly_idx = compute_monthly_rebalance_dates(daily_idx)
    sig_choices = ["SPY", "EFA", "AGG"]
    signal = pd.Series(
        rng.choice(sig_choices, size=len(monthly_idx)),
        index=monthly_idx,
    )

    pd_out = compute_gem_returns(rets, signal, trans_cost_bps=5.0)
    np_out = compute_gem_returns_np(
        spy_returns=rets["SPY"].values,
        efa_returns=rets["EFA"].values,
        agg_returns=rets["AGG"].values,
        daily_dates=daily_idx.values,
        signal_dates=signal.index.values,
        signal_choices=signal.values,
        trans_cost_bps=5.0,
    )
    assert pd_out.shape[0] == np_out.shape[0]
    max_abs = float(np.max(np.abs(pd_out.values - np_out)))
    assert max_abs < 1e-9, f"max_abs_diff={max_abs:.3e}"


# ---------------------------------------------------------------------------
# 6. Monthly rebalance dates from daily index
# ---------------------------------------------------------------------------


def test_monthly_rebalance_dates_pick_last_business_day_of_each_month():
    """compute_monthly_rebalance_dates returns last business day per month."""
    daily_idx = pd.date_range("2020-01-01", "2020-04-30", freq="B")
    out = compute_monthly_rebalance_dates(daily_idx)
    assert len(out) == 4
    # Last bday of Jan-2020 = 2020-01-31 (Friday)
    assert out[0] == pd.Timestamp("2020-01-31")
    # Last bday of Feb-2020 = 2020-02-28 (Friday)
    assert out[1] == pd.Timestamp("2020-02-28")
    # Last bday of Mar-2020 = 2020-03-31 (Tuesday)
    assert out[2] == pd.Timestamp("2020-03-31")
    # Last bday of Apr-2020 = 2020-04-30 (Thursday)
    assert out[3] == pd.Timestamp("2020-04-30")
