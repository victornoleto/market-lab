from __future__ import annotations

import numpy as np
import pandas as pd

from lrs.lib.backtest import constant_weight_frame, simulate_weight_frame
from lrs.phases.phase06a_aftertax_frontier.run import (
    DARF_RATE,
    contribution_simulation,
    final_liquidation_tax,
    pick_most_underweight,
)


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2010-01-01", periods=n)


def _drifting_returns(n: int) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "A": 0.0008 + 0.012 * rng.standard_normal(n),
            "B": 0.0002 + 0.004 * rng.standard_normal(n),
        },
        index=_days(n),
    )


def test_force_rebalance_mask_none_is_regression_safe() -> None:
    returns = _drifting_returns(600)
    targets = constant_weight_frame(returns.index, {"A": 0.6, "B": 0.4})

    old_path, old_summary = simulate_weight_frame(returns, targets, taxable=True)
    new_path, new_summary = simulate_weight_frame(
        returns, targets, taxable=True, force_rebalance_mask=None
    )

    pd.testing.assert_series_equal(old_path, new_path)
    assert old_summary == new_summary
    # Constant targets with no mask never trade after the initial allocation.
    assert old_summary["trade_count"] == 0.0


def test_force_rebalance_mask_taxes_static_rebalance_turnover() -> None:
    returns = _drifting_returns(600)
    targets = constant_weight_frame(returns.index, {"A": 0.6, "B": 0.4})
    periods = returns.index.to_period("M")
    monthly = pd.Series(
        np.r_[True, periods[1:].to_numpy() != periods[:-1].to_numpy()], index=returns.index
    )

    taxed, summary = simulate_weight_frame(
        returns, targets, taxable=True, force_rebalance_mask=monthly
    )

    # Drift between months makes the forced rebalances real trades.
    assert summary["trade_count"] > 0.0
    assert summary["turnover_per_year"] > 0.0
    baseline, _ = simulate_weight_frame(returns, targets, taxable=True)
    assert not np.allclose(taxed.to_numpy(), baseline.to_numpy())


def test_final_liquidation_tax_on_gain() -> None:
    rets = pd.Series([0.10, 0.10], index=_days(2))

    taxed = final_liquidation_tax(rets)

    gross_terminal = 1.10 * 1.10
    expected_net = gross_terminal - DARF_RATE * (gross_terminal - 1.0)
    net_terminal = float((1.0 + taxed).prod())
    assert abs(net_terminal - expected_net) < 1e-12
    # Path before the final day is untouched (taxes only at liquidation).
    assert taxed.iloc[0] == rets.iloc[0]


def test_final_liquidation_tax_no_tax_on_loss() -> None:
    rets = pd.Series([-0.10, -0.05], index=_days(2))

    taxed = final_liquidation_tax(rets)

    pd.testing.assert_series_equal(taxed, rets)


def test_pick_most_underweight() -> None:
    targets = {"A": 0.5, "B": 0.3, "C": 0.2}
    values = {"A": 60.0, "B": 25.0, "C": 15.0}  # weights 0.60 / 0.25 / 0.15

    # Underweights vs target: A -0.10, B +0.05, C +0.05 -> B and C tie; max()
    # picks deterministically the first max, so just assert it is not A.
    assert pick_most_underweight(targets, values) != "A"

    values = {"A": 40.0, "B": 40.0, "C": 20.0}  # A is 0.40 vs target 0.50
    assert pick_most_underweight(targets, values) == "A"


def test_contribution_simulation_zero_returns_accounting() -> None:
    idx = pd.bdate_range("2010-01-01", periods=300)
    frame = pd.DataFrame({"A": 0.0, "B": 0.0}, index=idx)
    targets = {"A": 0.6, "B": 0.4}

    stats = contribution_simulation(
        frame, targets, {"A", "B"}, start_equity=10_000.0, contribution=1_000.0
    )

    # Zero returns: terminal equals contributions, no gains -> no final tax,
    # and the money-weighted return is ~0.
    assert stats["terminal_gross"] == stats["contributed"]
    assert stats["final_tax"] == 0.0
    assert abs(stats["irr_annual"]) < 1e-6
    assert stats["n_contributions"] == float(
        int(pd.Series(idx).dt.to_period("M").nunique()) - 1
    )


def test_contribution_simulation_buys_lagging_component() -> None:
    idx = pd.bdate_range("2010-01-01", periods=130)
    # A rallies, B is flat -> every monthly contribution should go to B,
    # keeping weights closer to target than buying A would.
    frame = pd.DataFrame({"A": 0.002, "B": 0.0}, index=idx)
    targets = {"A": 0.5, "B": 0.5}

    stats = contribution_simulation(
        frame, targets, {"A", "B"}, start_equity=10_000.0, contribution=1_000.0
    )

    # Gains exist (A compounds) -> positive final tax on the gross components.
    assert stats["final_tax"] > 0.0
    # Buy-only rebalancing keeps the mean deviation modest in this toy setup.
    assert stats["mean_abs_weight_dev"] < 0.10
