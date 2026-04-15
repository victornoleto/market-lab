"""Tests for ai_trade.backtest.portfolio.combined."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.portfolio.combined import (
    combine_equity_curves,
    compute_portfolio_metrics,
)


def _curve(returns: list[float], start: str = "2020-01-01") -> pd.Series:
    """Build an equity curve from a list of daily returns, starting at 100."""
    idx = pd.date_range(start, periods=len(returns) + 1, freq="B")
    equity = [100.0]
    for r in returns:
        equity.append(equity[-1] * (1.0 + r))
    return pd.Series(equity, index=idx, name="equity")


def test_combine_two_curves_equal_weight_same_index():
    # Curve A: +10% then -5%. Curve B: flat.
    a = _curve([0.10, -0.05])
    b = _curve([0.0, 0.0])
    combined = combine_equity_curves([a, b], [0.5, 0.5], initial_capital=100.0)

    # Day 0: capital = 100.
    # Day 1: return = 0.5*0.10 + 0.5*0.0 = 0.05 → equity = 105.
    # Day 2: return = 0.5*(-0.05) + 0.5*0.0 = -0.025 → equity = 105 * 0.975 = 102.375.
    assert combined.iloc[0] == pytest.approx(100.0)
    assert combined.iloc[1] == pytest.approx(105.0)
    assert combined.iloc[2] == pytest.approx(102.375)
    assert list(combined.index) == list(a.index)


def test_combine_curves_with_different_start_dates_uses_intersection():
    # Curve A: 5 bars from 2020-01-01.
    a = pd.Series(
        [100.0, 101.0, 102.0, 103.0, 104.0],
        index=pd.date_range("2020-01-01", periods=5, freq="B"),
        name="equity",
    )
    # Curve B: 5 bars from 2020-01-03 (overlaps with A on last 3).
    b = pd.Series(
        [100.0, 110.0, 121.0, 133.1, 146.41],
        index=pd.date_range("2020-01-03", periods=5, freq="B"),
        name="equity",
    )
    combined = combine_equity_curves([a, b], [0.5, 0.5], initial_capital=1000.0)

    # Intersection: 2020-01-03 (Fri), 2020-01-06 (Mon), 2020-01-07 (Tue).
    # 3 bars → 2 returns computed.
    assert len(combined) == 3
    assert combined.index[0] == pd.Timestamp("2020-01-03")
    assert combined.index[-1] == pd.Timestamp("2020-01-07")
    assert combined.iloc[0] == pytest.approx(1000.0)


def test_combine_empty_curves_raises():
    with pytest.raises(ValueError, match="non-empty"):
        combine_equity_curves([], [], initial_capital=100.0)


def test_combine_mismatched_weights_raises():
    a = _curve([0.0])
    with pytest.raises(ValueError, match="len"):
        combine_equity_curves([a], [0.5, 0.5], initial_capital=100.0)


def test_combine_weights_must_sum_to_one():
    a = _curve([0.1])
    b = _curve([0.2])
    # Weights [0.5, 0.6] sum to 1.1 — invalid.
    with pytest.raises(ValueError, match="sum"):
        combine_equity_curves([a, b], [0.5, 0.6], initial_capital=100.0)


def test_combine_insufficient_overlap_raises():
    a = pd.Series(
        [100.0, 101.0],
        index=pd.date_range("2020-01-01", periods=2, freq="B"),
        name="equity",
    )
    b = pd.Series(
        [100.0, 101.0],
        index=pd.date_range("2020-01-15", periods=2, freq="B"),
        name="equity",
    )
    with pytest.raises(ValueError, match="overlap"):
        combine_equity_curves([a, b], [0.5, 0.5], initial_capital=100.0)


def test_compute_portfolio_metrics_basic():
    # 252 trading days of 0.1% daily return = ~28% annual.
    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    curve = pd.Series(100.0 * (1.001 ** np.arange(len(dates))), index=dates, name="equity")

    metrics = compute_portfolio_metrics(curve, periods_per_year=252)

    assert "sharpe" in metrics
    assert "cagr" in metrics
    assert "max_drawdown" in metrics
    assert metrics["cagr"] > 0.25  # near 28%
    assert metrics["cagr"] < 0.35
    # Sharpe for a monotonic curve with constant return is +inf (std=0).
    # Our `_safe_sharpe` helper returns 0.0 in that case — accept either.
    assert metrics["sharpe"] == 0.0 or np.isinf(metrics["sharpe"])
    assert metrics["max_drawdown"] == pytest.approx(0.0, abs=1e-9)


def test_make_portfolio_trial_wraps_curve_into_trial_result():
    from ai_trade.backtest.grid.result import TrialResult
    from ai_trade.backtest.portfolio.combined import make_portfolio_trial
    from ai_trade.backtest.portfolio.configs import PortfolioConfig

    curve = _curve([0.01, -0.005, 0.02])
    cfg = PortfolioConfig(
        clenow_config_id=8,
        ehlers_config_id=6,
        clenow_lookback=75,
        clenow_top_pct=0.20,
        clenow_risk_factor=0.001,
        ehlers_hp=48,
        ehlers_lp=20,
        ehlers_pct_of_dcp=0.80,
        ehlers_stop_pct=0.02,
    )

    trial = make_portfolio_trial(
        config_id=0,
        config=cfg,
        equity_curve=curve,
        initial_cash=100.0,
    )

    assert isinstance(trial, TrialResult)
    assert trial.config_id == 0
    assert trial.config is cfg
    assert trial.status == "ok"
    assert trial.result is not None
    assert list(trial.result.equity_curve.values) == list(curve.values)
    assert trial.result.initial_cash == 100.0
    assert trial.result.final_equity == pytest.approx(curve.iloc[-1])
