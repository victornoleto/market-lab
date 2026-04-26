"""TDD for iter 016 composition primitives (mirror of iter 012 test).

Verifies the Markowitz tangency formula on a closed-form 2-asset case and
the inner-join composition arithmetic. The math is identical to iter 012;
this duplication is intentional — each iter's primitives must pass the
same property tests in isolation, and the iter directory is self-contained.

Run: ``pytest -q studies/gold_swing_loop/iterations/016-*/test_composition.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Make the iter dir importable so ``run_backtest`` is loadable.
ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))

from run_backtest import (  # noqa: E402
    aggregate_intraday_to_daily,
    compose_returns,
    markowitz_tangency_weights,
)


def test_tangency_uncorrelated_proportional_to_sharpe():
    """At ρ=0 with equal sigma, weights ∝ Sharpe (= μ here)."""
    mu = np.array([0.001, 0.0005])  # higher μ stream = stream A
    sigma = np.array([0.01, 0.01])
    w_a, w_b = markowitz_tangency_weights(mu, sigma, rho=0.0)

    # Weights sum to 1.0
    assert w_a + w_b == pytest.approx(1.0, abs=1e-9)
    # Higher-μ stream gets higher weight.
    assert w_a > w_b
    # Closed-form at ρ=0 equal σ: w_a = μ_a / (μ_a + μ_b).
    expected_a = mu[0] / (mu[0] + mu[1])
    assert w_a == pytest.approx(expected_a, abs=1e-9)


def test_tangency_negative_correlation_amplifies_diversification():
    """At ρ<0 with similar Sharpes, both weights stay positive (diversifies)."""
    mu = np.array([0.0008, 0.0006])
    sigma = np.array([0.012, 0.010])
    w_a, w_b = markowitz_tangency_weights(mu, sigma, rho=-0.07)

    # Both positive: a near-zero negative ρ shouldn't induce a short.
    assert w_a > 0
    assert w_b > 0
    assert w_a + w_b == pytest.approx(1.0, abs=1e-9)


def test_tangency_high_correlation_can_produce_negative_weight():
    """At ρ → +1 with disparate Sharpes, lower-Sharpe stream gets shorted."""
    # μ_a >> μ_b but σ_a slightly higher; with ρ near +1, the optimum is to
    # short B and lever A (one weight negative).
    mu = np.array([0.002, 0.0001])
    sigma = np.array([0.012, 0.010])
    w_a, w_b = markowitz_tangency_weights(mu, sigma, rho=0.95)

    # One weight should be negative (caller is responsible for clamping).
    assert (w_a < 0) or (w_b < 0)


def test_compose_returns_inner_joins_and_drops_nan():
    """compose_returns aligns indexes via inner-join and drops NaN rows."""
    dates_a = pd.date_range("2024-01-01", periods=5, freq="D")
    dates_b = pd.date_range("2024-01-03", periods=5, freq="D")  # offset by 2 days
    a = pd.Series([0.001, 0.002, 0.003, 0.004, 0.005], index=dates_a)
    b = pd.Series([0.010, 0.020, 0.030, 0.040, 0.050], index=dates_b)

    composed = compose_returns(a, b, w_a=0.3, w_b=0.7)

    # Inner join: 3 overlap days (2024-01-03..05).
    assert len(composed) == 3
    # Linear combination at first overlap: 0.3*0.003 + 0.7*0.010 = 0.0079.
    assert composed.iloc[0] == pytest.approx(0.3 * 0.003 + 0.7 * 0.010, abs=1e-12)


def test_aggregate_intraday_to_daily_sums_within_day():
    """Sum of 24 hourly returns on one day equals daily aggregate."""
    # Day 1: 3 hourly bars summing to 0.006; Day 2: 2 bars summing to 0.005.
    idx = pd.DatetimeIndex([
        "2024-01-01 09:00", "2024-01-01 10:00", "2024-01-01 11:00",
        "2024-01-02 09:00", "2024-01-02 10:00",
    ])
    rets = pd.Series([0.001, 0.002, 0.003, 0.002, 0.003], index=idx)

    daily = aggregate_intraday_to_daily(rets)

    assert len(daily) == 2
    assert daily.iloc[0] == pytest.approx(0.006, abs=1e-12)
    assert daily.iloc[1] == pytest.approx(0.005, abs=1e-12)


def test_aggregate_intraday_to_daily_drops_empty_days():
    """Empty days (no bars) are dropped, not zero-filled."""
    idx = pd.DatetimeIndex(["2024-01-01 09:00", "2024-01-03 09:00"])
    rets = pd.Series([0.001, 0.002], index=idx)

    daily = aggregate_intraday_to_daily(rets)

    # Only 2 days have data (Jan 1 and Jan 3); Jan 2 dropped.
    assert len(daily) == 2
    assert "2024-01-02" not in [d.strftime("%Y-%m-%d") for d in daily.index]
