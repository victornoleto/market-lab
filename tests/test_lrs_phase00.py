from __future__ import annotations

import pandas as pd

from lrs.lib.backtest import (
    build_sma_signal,
    build_weekly_lagged_weights,
    build_weekly_lrs_weights,
    simulate_weight_frame,
)


def test_build_sma_signal_is_lagged() -> None:
    prices = pd.Series([1.0, 2.0, 3.0, 4.0], index=pd.date_range("2020-01-01", periods=4))

    signal = build_sma_signal(prices, lookback=2)

    assert signal.tolist() == [False, False, True, True]


def test_weekly_lrs_lag_delays_new_sleeve() -> None:
    index = pd.date_range("2020-01-06", periods=8, freq="B")
    signal = pd.Series([False, False, False, False, False, True, True, True], index=index)

    weights, summary = build_weekly_lrs_weights(
        index,
        signal,
        risk_on_weights={"SSOSIM": 1.0},
        risk_off_weights={"CASHX": 1.0},
        lag_days=2,
    )

    assert weights.loc[index[5], "CASHX"] == 1.0
    assert weights.loc[index[6], "CASHX"] == 1.0
    assert weights.loc[index[7], "SSOSIM"] == 1.0
    assert summary["state_changes"] == 1.0


def test_simulation_does_not_rebalance_unchanged_target_daily() -> None:
    index = pd.date_range("2020-01-01", periods=2, freq="B")
    returns = pd.DataFrame({"A": [0.10, 0.10], "B": [0.0, 0.0]}, index=index)
    weights = pd.DataFrame({"A": [0.50, 0.50], "B": [0.50, 0.50]}, index=index)

    portfolio_returns, summary = simulate_weight_frame(returns, weights, taxable=False)

    assert round(portfolio_returns.iloc[0], 12) == round(0.05, 12)
    assert round(portfolio_returns.iloc[1], 6) == round(1.105 / 1.05 - 1.0, 6)
    assert summary["trade_count"] == 0.0


def test_weekly_lagged_weights_support_dynamic_targets() -> None:
    index = pd.date_range("2020-01-06", periods=8, freq="B")
    desired = pd.DataFrame(
        {
            "A": [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            "B": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        },
        index=index,
    )

    weights, summary = build_weekly_lagged_weights(desired, lag_days=1)

    assert weights.loc[index[5], "CASHX"] == 1.0
    assert weights.loc[index[6], "B"] == 1.0
    assert summary["state_changes"] == 1.0
