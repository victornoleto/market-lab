"""TDD tests for iter 012 composition primitives.

Run from worktree root:
    python -m pytest studies/gold_swing_loop/iterations/012-*/test_composition.py -v
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
    aggregate_intraday_to_daily,
    compose_returns,
    load_component_returns,
    markowitz_tangency_weights,
)


# ---------------------------------------------------------------------------
# markowitz_tangency_weights
# ---------------------------------------------------------------------------


def test_markowitz_zero_correlation_equal_vol():
    """Equal vol, ρ=0: w ∝ μ. S_A=1, S_B=0.5 → w_A=2/3, w_B=1/3."""
    mu = np.array([1.0, 0.5])
    sigma = np.array([1.0, 1.0])
    rho = 0.0
    w_a, w_b = markowitz_tangency_weights(mu, sigma, rho)
    assert w_a == pytest.approx(2.0 / 3.0, abs=1e-9)
    assert w_b == pytest.approx(1.0 / 3.0, abs=1e-9)
    assert w_a + w_b == pytest.approx(1.0, abs=1e-12)


def test_markowitz_symmetric_returns():
    """μ_A=μ_B, σ_A=σ_B → w_A=w_B=0.5 regardless of ρ."""
    for rho in (-0.3, 0.0, 0.3, 0.7):
        mu = np.array([0.001, 0.001])
        sigma = np.array([0.01, 0.01])
        w_a, w_b = markowitz_tangency_weights(mu, sigma, rho)
        assert w_a == pytest.approx(0.5, abs=1e-9), f"rho={rho}"
        assert w_b == pytest.approx(0.5, abs=1e-9), f"rho={rho}"


def test_markowitz_positive_correlation_concentrates_on_higher_sharpe():
    """ρ>0 with S_A>S_B should pull more weight toward A vs the ρ=0 baseline."""
    mu = np.array([1.0, 0.5])
    sigma = np.array([1.0, 1.0])
    w_a_zero, _ = markowitz_tangency_weights(mu, sigma, 0.0)
    w_a_pos, _ = markowitz_tangency_weights(mu, sigma, 0.4)
    assert w_a_pos > w_a_zero
    assert w_a_pos < 1.0


def test_markowitz_negative_weight_signaled():
    """If ρ > S_min/S_max the formula gives negative w_min — caller must handle.

    e.g. S_A=1, S_B=0.1, ρ=0.5 → S_B/S_A = 0.1 < ρ=0.5 → w_B negative.
    """
    mu = np.array([1.0, 0.1])
    sigma = np.array([1.0, 1.0])
    w_a, w_b = markowitz_tangency_weights(mu, sigma, 0.5)
    assert w_b < 0
    assert w_a > 1.0
    assert w_a + w_b == pytest.approx(1.0, abs=1e-9)


def test_markowitz_unequal_volatility():
    """Verify against numpy linear-algebra solve directly.

    Σ⁻¹μ then normalize.
    """
    mu_arr = np.array([0.0008, 0.0003])
    sigma_arr = np.array([0.012, 0.005])
    rho = 0.15
    cov = np.array([
        [sigma_arr[0] ** 2,                       rho * sigma_arr[0] * sigma_arr[1]],
        [rho * sigma_arr[0] * sigma_arr[1],       sigma_arr[1] ** 2],
    ])
    raw = np.linalg.solve(cov, mu_arr)
    expected = raw / raw.sum()
    w_a, w_b = markowitz_tangency_weights(mu_arr, sigma_arr, rho)
    assert w_a == pytest.approx(expected[0], rel=1e-9)
    assert w_b == pytest.approx(expected[1], rel=1e-9)


# ---------------------------------------------------------------------------
# compose_returns
# ---------------------------------------------------------------------------


def test_compose_returns_linearity():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    a = pd.Series([0.01, -0.02, 0.005, 0.0, 0.015], index=idx)
    b = pd.Series([0.005, 0.01, -0.003, 0.002, 0.001], index=idx)
    combined = compose_returns(a, b, 0.6, 0.4)
    expected = 0.6 * a + 0.4 * b
    pd.testing.assert_series_equal(combined, expected, check_names=False)


def test_compose_returns_inner_join_only_overlap():
    idx_a = pd.date_range("2020-01-01", periods=5, freq="D")
    idx_b = pd.date_range("2020-01-03", periods=5, freq="D")
    a = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], index=idx_a)
    b = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0], index=idx_b)
    combined = compose_returns(a, b, 0.5, 0.5)
    assert len(combined) == 3
    assert combined.iloc[0] == pytest.approx(0.5 * 3.0 + 0.5 * 10.0)
    assert combined.iloc[1] == pytest.approx(0.5 * 4.0 + 0.5 * 20.0)
    assert combined.iloc[2] == pytest.approx(0.5 * 5.0 + 0.5 * 30.0)


def test_compose_returns_zero_weight_one_stream():
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    a = pd.Series([0.01, 0.02, 0.03, 0.04], index=idx)
    b = pd.Series([0.1, 0.2, 0.3, 0.4], index=idx)
    pd.testing.assert_series_equal(compose_returns(a, b, 1.0, 0.0), a, check_names=False)
    pd.testing.assert_series_equal(compose_returns(a, b, 0.0, 1.0), b, check_names=False)


# ---------------------------------------------------------------------------
# aggregate_intraday_to_daily
# ---------------------------------------------------------------------------


def test_aggregate_intraday_to_daily_sums_simple_returns():
    """Daily aggregate of simple-arithmetic returns is the sum (small-return approx).

    For small returns r_h ~ O(1e-4), (1+r_1)*(1+r_2)*...*(1+r_24) - 1 ≈ Σ r_h.
    For PnL-as-fraction-of-capital semantics (each r_h ≪ 1), simple sum is
    the cleanest aggregate and matches the run_backtest's bar-PnL convention.
    """
    idx = pd.date_range("2024-01-01 00:00:00", periods=48, freq="h")
    rng = np.random.default_rng(42)
    rets = pd.Series(rng.normal(0, 1e-4, 48), index=idx)
    daily = aggregate_intraday_to_daily(rets)
    assert len(daily) == 2
    assert daily.iloc[0] == pytest.approx(rets.iloc[:24].sum(), abs=1e-12)
    assert daily.iloc[1] == pytest.approx(rets.iloc[24:].sum(), abs=1e-12)


def test_aggregate_intraday_to_daily_handles_zero_bars():
    idx = pd.date_range("2024-01-01 00:00:00", periods=24, freq="h")
    rets = pd.Series(np.zeros(24), index=idx)
    daily = aggregate_intraday_to_daily(rets)
    assert len(daily) == 1
    assert daily.iloc[0] == 0.0


def test_aggregate_intraday_passthrough_for_daily_index():
    """If input is already daily, aggregate is identity (each day has one bar)."""
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    rets = pd.Series([0.01, 0.02, -0.005, 0.0, 0.015], index=idx)
    daily = aggregate_intraday_to_daily(rets)
    assert len(daily) == 5
    pd.testing.assert_series_equal(
        daily.sort_index(), rets.sort_index(), check_names=False
    )


# ---------------------------------------------------------------------------
# load_component_returns (smoke against real iter 003 + 011 outputs)
# ---------------------------------------------------------------------------


REPO_ROOT = ITER_DIR.parents[3]
ITER_003 = REPO_ROOT / "studies" / "gold_swing_loop" / "iterations" / "003-2026-04-26-0228-rsi2-sma200-filter"
ITER_011 = REPO_ROOT / "studies" / "gold_swing_loop" / "iterations" / "011-2026-04-26-1334-vol-regime-gate-inverse"


def test_load_component_returns_iter003_gld_long():
    series = load_component_returns(
        ITER_003, "gld_long", "connors_rsi2_sma200_filter"
    )
    assert isinstance(series, pd.Series)
    assert len(series) == 5384
    assert isinstance(series.index, pd.DatetimeIndex)
    assert pd.Timestamp("2004-11-18") == series.index[0]


def test_load_component_returns_iter011_xauusd_intraday_is_1h():
    series = load_component_returns(
        ITER_011, "xauusd_intraday", "vol_regime_inverse_60_252_long_only"
    )
    assert len(series) == 32195
    diff = series.index[1] - series.index[0]
    assert diff == pd.Timedelta("1h")


def test_load_component_returns_missing_cfg_raises():
    with pytest.raises(KeyError):
        load_component_returns(ITER_003, "gld_long", "no_such_cfg")
