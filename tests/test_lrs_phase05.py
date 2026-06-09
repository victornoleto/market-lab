from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lrs.phases.phase05_rsc_overlay_proxy.run import (
    monthly_rebalanced_returns,
    relative_to_core_stats,
    returns_from_equity,
    underwater_stats,
)


def test_underwater_stats_counts_recovery_streaks() -> None:
    idx = pd.bdate_range("2020-01-01", periods=6)
    equity = pd.Series([1.0, 0.9, 0.95, 1.01, 0.99, 1.02], index=idx)
    returns = returns_from_equity(equity, "x")

    stats = underwater_stats(returns)

    assert stats["max_recovery_days"] == 2
    assert stats["current_underwater_days"] == 0
    assert stats["time_underwater_pct"] > 0


def test_monthly_rebalanced_returns_rebalances_at_month_boundaries() -> None:
    idx = pd.bdate_range("2020-01-30", periods=5)
    returns = pd.DataFrame(
        {
            "a": [0.10, 0.00, 0.00, 0.00, 0.00],
            "b": [0.00, 0.00, 0.00, 0.00, 0.00],
        },
        index=idx,
    )

    portfolio, summary = monthly_rebalanced_returns(returns, {"a": 0.5, "b": 0.5})

    assert len(portfolio) == len(returns)
    assert portfolio.iloc[0] == pytest.approx(0.05)
    assert summary["rebalance_trade_count"] >= 1
    assert summary["rebalance_turnover_per_year"] > 0


def test_monthly_rebalanced_returns_rejects_bad_weights() -> None:
    idx = pd.bdate_range("2020-01-01", periods=3)
    returns = pd.DataFrame({"a": np.zeros(3)}, index=idx)

    with pytest.raises(ValueError, match="non-negative"):
        monthly_rebalanced_returns(returns, {"a": -1.0})

    with pytest.raises(KeyError, match="missing"):
        monthly_rebalanced_returns(returns, {"b": 1.0})


def test_relative_to_core_stats_detects_relative_drawdown() -> None:
    idx = pd.bdate_range("2020-01-01", periods=5)
    candidate = pd.Series([0.10, -0.20, 0.00, 0.00, 0.00], index=idx)
    core = pd.Series([0.00, 0.00, 0.00, 0.00, 0.00], index=idx)

    stats = relative_to_core_stats(candidate, core)

    assert stats["terminal_vs_rsc"] < 1.0
    assert stats["pct_days_below_rsc"] > 0
    assert stats["max_relative_drawdown_vs_rsc"] < 0
