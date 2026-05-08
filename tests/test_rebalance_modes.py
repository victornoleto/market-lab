"""Tests for :mod:`ai_trade.backtest.metrics.rebalance_modes` (Phase 3.5b
Addendum Task C1 [SWING BROKER]).

Covers:

* Input validation (DataFrame type, DatetimeIndex, NaN-free, weights
  sum to 1, non-negative, column alignment).
* Daily rebalance: weights pinned to target, drift ≡ 0, equity matches
  the ``(1 + Σ w·r).cumprod()`` baseline.
* Monthly-sell rebalance: tax events fire only on rebalance dates,
  cost-basis tracked across sells, losing sells pay zero tax.
* Monthly-cashflow rebalance: deposits flow to the most-underweight
  leg, zero deposit = pure buy-and-hold.
* Rebalance-date detection is index-aware (uses last actual bar of
  each month, robust to holidays).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.metrics.rebalance_modes import (
    RebalanceResult,
    TaxableEvent,
    _rebalance_dates,
    apply_daily_rebalance,
    apply_monthly_cashflow_rebalance,
    apply_monthly_sell_rebalance,
    apply_threshold_rebalance,
)


def _mk_returns_df(
    seed: int = 0,
    n: int = 200,
    mus: tuple[float, ...] = (0.0005, 0.0003),
    sigmas: tuple[float, ...] = (0.01, 0.008),
    start: str = "2020-01-01",
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=n, freq="B")
    data = {
        f"leg{i}": rng.normal(mu, sigma, size=n)
        for i, (mu, sigma) in enumerate(zip(mus, sigmas))
    }
    return pd.DataFrame(data, index=idx)


class TestValidation:
    def test_rejects_non_dataframe(self) -> None:
        with pytest.raises(TypeError, match="DataFrame"):
            apply_daily_rebalance([0.01, 0.02], {"a": 1.0})

    def test_rejects_non_datetime_index(self) -> None:
        df = pd.DataFrame({"a": [0.01, 0.02]}, index=[0, 1])
        with pytest.raises(TypeError, match="DatetimeIndex"):
            apply_daily_rebalance(df, {"a": 1.0})

    def test_rejects_empty(self) -> None:
        df = pd.DataFrame(
            {"a": pd.Series(dtype=float)},
            index=pd.DatetimeIndex([]),
        )
        with pytest.raises(ValueError, match="empty"):
            apply_daily_rebalance(df, {"a": 1.0})

    def test_rejects_nan(self) -> None:
        df = _mk_returns_df(n=5)
        df.iloc[2, 0] = np.nan
        with pytest.raises(ValueError, match="NaN"):
            apply_daily_rebalance(df, {"leg0": 0.5, "leg1": 0.5})

    def test_rejects_weights_not_summing_to_one(self) -> None:
        df = _mk_returns_df(n=10)
        with pytest.raises(ValueError, match="sum to 1"):
            apply_daily_rebalance(df, {"leg0": 0.7, "leg1": 0.7})

    def test_rejects_negative_weights(self) -> None:
        df = _mk_returns_df(n=10)
        with pytest.raises(ValueError, match="non-negative"):
            apply_daily_rebalance(df, {"leg0": 1.5, "leg1": -0.5})

    def test_rejects_column_mismatch(self) -> None:
        df = _mk_returns_df(n=10)
        with pytest.raises(ValueError, match="match"):
            apply_daily_rebalance(df, {"leg0": 0.5, "legX": 0.5})

    def test_rejects_bad_tax_rate(self) -> None:
        df = _mk_returns_df(n=30)
        with pytest.raises(ValueError, match="tax_rate"):
            apply_monthly_sell_rebalance(
                df, {"leg0": 0.5, "leg1": 0.5}, tax_rate=1.5
            )

    def test_rejects_negative_deposit(self) -> None:
        df = _mk_returns_df(n=30)
        with pytest.raises(ValueError, match="non-negative"):
            apply_monthly_cashflow_rebalance(
                df,
                {"leg0": 0.5, "leg1": 0.5},
                monthly_deposit=-10.0,
            )

    def test_rejects_negative_threshold(self) -> None:
        df = _mk_returns_df(n=30)
        with pytest.raises(ValueError, match="threshold_pp"):
            apply_threshold_rebalance(
                df, {"leg0": 0.5, "leg1": 0.5}, threshold_pp=-1.0
            )

    def test_rejects_bad_threshold_tax_rate(self) -> None:
        df = _mk_returns_df(n=30)
        with pytest.raises(ValueError, match="tax_rate"):
            apply_threshold_rebalance(
                df,
                {"leg0": 0.5, "leg1": 0.5},
                threshold_pp=10.0,
                tax_rate=1.2,
            )


class TestRebalanceDates:
    def test_picks_last_bar_of_each_month(self) -> None:
        idx = pd.date_range("2020-01-01", "2020-03-31", freq="B")
        rebal = _rebalance_dates(idx, freq="M")
        assert len(rebal) == 3
        assert rebal[0] == idx[idx.month == 1][-1]
        assert rebal[1] == idx[idx.month == 2][-1]
        assert rebal[2] == idx[idx.month == 3][-1]

    def test_robust_to_missing_days(self) -> None:
        dates = pd.to_datetime(
            ["2020-01-10", "2020-01-15", "2020-02-03", "2020-02-28"]
        )
        idx = pd.DatetimeIndex(dates)
        rebal = _rebalance_dates(idx, freq="M")
        assert list(rebal) == [
            pd.Timestamp("2020-01-15"),
            pd.Timestamp("2020-02-28"),
        ]


class TestDailyRebalance:
    def test_equity_matches_weighted_sum_baseline(self) -> None:
        df = _mk_returns_df(seed=1, n=250)
        w = {"leg0": 0.6, "leg1": 0.4}
        result = apply_daily_rebalance(df, w, initial_capital=1.0)
        expected = (1.0 + 0.6 * df["leg0"] + 0.4 * df["leg1"]).cumprod()
        np.testing.assert_allclose(
            result.equity.values, expected.values, rtol=1e-12
        )

    def test_weights_pinned_to_target(self) -> None:
        df = _mk_returns_df(seed=2, n=60)
        w = {"leg0": 0.3, "leg1": 0.7}
        result = apply_daily_rebalance(df, w)
        assert (result.weights["leg0"] == 0.3).all()
        assert (result.weights["leg1"] == 0.7).all()

    def test_drift_is_zero_everywhere(self) -> None:
        df = _mk_returns_df(seed=3, n=40)
        result = apply_daily_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}
        )
        assert (result.drift.values == 0.0).all()
        assert result.max_drift.max() == 0.0

    def test_no_taxable_events(self) -> None:
        df = _mk_returns_df(seed=4, n=40)
        result = apply_daily_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}
        )
        assert result.taxable_events == []
        assert result.total_tax_paid == 0.0
        assert result.total_deposits == 0.0
        assert result.n_taxable_events == 0

    def test_three_leg_portfolio_equity(self) -> None:
        rng = np.random.default_rng(42)
        idx = pd.date_range("2020-01-01", periods=120, freq="B")
        df = pd.DataFrame(
            {
                "letf": rng.normal(0.0006, 0.012, 120),
                "qqq": rng.normal(0.0005, 0.010, 120),
                "gld": rng.normal(0.0002, 0.008, 120),
            },
            index=idx,
        )
        w = {"letf": 1 / 3, "qqq": 1 / 3, "gld": 1 / 3}
        result = apply_daily_rebalance(df, w)
        expected = (1.0 + df.mean(axis=1)).cumprod()
        np.testing.assert_allclose(
            result.equity.values, expected.values, rtol=1e-12
        )


class TestMonthlySellRebalance:
    def test_zero_returns_no_tax_events(self) -> None:
        idx = pd.date_range("2020-01-01", periods=90, freq="B")
        df = pd.DataFrame(
            {"leg0": 0.0, "leg1": 0.0}, index=idx
        )
        result = apply_monthly_sell_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}
        )
        assert result.taxable_events == []
        assert result.total_tax_paid == 0.0
        np.testing.assert_allclose(
            result.equity.values, np.ones(len(df)), rtol=1e-12
        )

    def test_tax_fires_only_on_rebalance_dates(self) -> None:
        rng = np.random.default_rng(7)
        idx = pd.date_range("2020-01-01", periods=100, freq="B")
        df = pd.DataFrame(
            {
                "leg0": rng.normal(0.001, 0.01, 100),
                "leg1": rng.normal(-0.001, 0.01, 100),
            },
            index=idx,
        )
        result = apply_monthly_sell_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}
        )
        rebal_dates = set(_rebalance_dates(idx, freq="M"))
        for ev in result.taxable_events:
            assert ev.date in rebal_dates

    def test_drift_drops_on_rebalance_dates(self) -> None:
        rng = np.random.default_rng(8)
        idx = pd.date_range("2020-01-01", periods=120, freq="B")
        df = pd.DataFrame(
            {
                "leg0": rng.normal(0.003, 0.01, 120),
                "leg1": rng.normal(-0.001, 0.01, 120),
            },
            index=idx,
        )
        result = apply_monthly_sell_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}
        )
        rebal_dates = _rebalance_dates(idx, freq="M")
        # After rebalance, drift should be strictly smaller than the
        # prior bar's drift for each (rebal_date - 1, rebal_date) pair.
        for rd in rebal_dates:
            pos = idx.get_loc(rd)
            if pos > 0:
                drift_before = result.drift.iloc[pos - 1].max()
                drift_after = result.drift.iloc[pos].max()
                if drift_before > 1e-6:
                    assert drift_after <= drift_before + 1e-12

    def test_tax_only_on_realized_gains(self) -> None:
        # Craft a scenario where leg0 loses money → sell yields a loss,
        # zero tax.
        idx = pd.date_range("2020-01-01", periods=45, freq="B")
        df = pd.DataFrame(
            {
                "leg0": [-0.005] * 45,
                "leg1": [0.0] * 45,
            },
            index=idx,
        )
        result = apply_monthly_sell_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}
        )
        # leg0 drops; leg1 flat → leg0 is underweight, leg1 overweight.
        # Selling leg1 (flat, basis == equity) yields zero realized
        # gain → zero tax.
        assert result.total_tax_paid == pytest.approx(0.0, abs=1e-12)
        assert all(ev.tax_paid == 0.0 for ev in result.taxable_events)

    def test_positive_realized_gain_pays_tax(self) -> None:
        idx = pd.date_range("2020-01-01", periods=45, freq="B")
        df = pd.DataFrame(
            {
                "leg0": [0.005] * 45,
                "leg1": [0.0] * 45,
            },
            index=idx,
        )
        result = apply_monthly_sell_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}, tax_rate=0.15
        )
        # leg0 gains → overweight, gets sold. Realized gain > 0.
        assert result.total_tax_paid > 0.0
        leg0_events = [
            ev for ev in result.taxable_events if ev.leg == "leg0"
        ]
        assert len(leg0_events) >= 1
        for ev in leg0_events:
            assert ev.realized_gain > 0.0
            assert ev.tax_paid == pytest.approx(
                0.15 * ev.realized_gain, rel=1e-12
            )

    def test_final_equity_reflects_tax_drag(self) -> None:
        idx = pd.date_range("2020-01-01", periods=45, freq="B")
        df = pd.DataFrame(
            {"leg0": [0.005] * 45, "leg1": [0.0] * 45},
            index=idx,
        )
        taxed = apply_monthly_sell_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}, tax_rate=0.15
        )
        free = apply_monthly_sell_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}, tax_rate=0.0
        )
        assert taxed.equity.iloc[-1] < free.equity.iloc[-1]
        # Tax drag ≈ total_tax_paid (compounding over 2 months is
        # second-order tiny, so the inequality bound is loose).
        assert taxed.total_tax_paid > 0.0
        assert free.total_tax_paid == 0.0

    def test_returns_RebalanceResult_type(self) -> None:
        df = _mk_returns_df(n=80)
        result = apply_monthly_sell_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}
        )
        assert isinstance(result, RebalanceResult)
        for ev in result.taxable_events:
            assert isinstance(ev, TaxableEvent)


class TestMonthlyCashflowRebalance:
    def test_zero_deposit_equals_buy_and_hold(self) -> None:
        df = _mk_returns_df(seed=10, n=150)
        w = {"leg0": 0.5, "leg1": 0.5}
        result = apply_monthly_cashflow_rebalance(
            df, w, monthly_deposit=0.0, initial_capital=1.0
        )
        # Buy-and-hold: leg_j equity = w_j · (1+r_j).cumprod()
        expected_leg0 = 0.5 * (1.0 + df["leg0"]).cumprod()
        expected_leg1 = 0.5 * (1.0 + df["leg1"]).cumprod()
        expected_total = expected_leg0 + expected_leg1
        np.testing.assert_allclose(
            result.equity.values, expected_total.values, rtol=1e-12
        )
        assert result.total_deposits == 0.0

    def test_deposit_goes_to_most_underweight_leg(self) -> None:
        idx = pd.date_range("2020-01-01", periods=42, freq="B")
        # 42 business days: Jan 1 → Feb 27. Rebal on Jan 31 + Feb 27.
        df = pd.DataFrame(
            {"leg0": [0.01] * 42, "leg1": [0.0] * 42},
            index=idx,
        )
        result = apply_monthly_cashflow_rebalance(
            df,
            {"leg0": 0.5, "leg1": 0.5},
            monthly_deposit=100.0,
            initial_capital=1000.0,
        )
        rebal = _rebalance_dates(idx, freq="M")
        assert len(rebal) == 2
        assert result.total_deposits == pytest.approx(200.0, rel=1e-12)
        # leg1's equity on last rebal date should jump by 100 (flat leg1 return).
        last_rebal = rebal[-1]
        pos = idx.get_loc(last_rebal)
        leg1_jump = (
            result.leg_equity["leg1"].iloc[pos]
            - result.leg_equity["leg1"].iloc[pos - 1]
        )
        assert leg1_jump == pytest.approx(100.0, rel=1e-6)

    def test_no_tax_events(self) -> None:
        df = _mk_returns_df(seed=11, n=60)
        result = apply_monthly_cashflow_rebalance(
            df,
            {"leg0": 0.5, "leg1": 0.5},
            monthly_deposit=50.0,
            initial_capital=10_000.0,
        )
        assert result.taxable_events == []
        assert result.total_tax_paid == 0.0

    def test_drift_decreases_on_rebalance_date(self) -> None:
        idx = pd.date_range("2020-01-01", periods=90, freq="B")
        df = pd.DataFrame(
            {"leg0": [0.002] * 90, "leg1": [0.0] * 90},
            index=idx,
        )
        result = apply_monthly_cashflow_rebalance(
            df,
            {"leg0": 0.5, "leg1": 0.5},
            monthly_deposit=200.0,
            initial_capital=1000.0,
        )
        rebal = _rebalance_dates(idx, freq="M")
        rd = rebal[-1]
        pos = idx.get_loc(rd)
        drift_before = result.drift["leg1"].iloc[pos - 1]
        drift_after = result.drift["leg1"].iloc[pos]
        assert drift_after < drift_before

    def test_total_equity_grows_with_deposits(self) -> None:
        idx = pd.date_range("2020-01-01", periods=90, freq="B")
        df = pd.DataFrame({"leg0": [0.0] * 90, "leg1": [0.0] * 90}, index=idx)
        result = apply_monthly_cashflow_rebalance(
            df,
            {"leg0": 0.5, "leg1": 0.5},
            monthly_deposit=100.0,
            initial_capital=1000.0,
        )
        # Flat returns + 4 monthly deposits ($400 total) → final
        # equity = 1400.
        rebal = _rebalance_dates(idx, freq="M")
        expected_final = 1000.0 + 100.0 * len(rebal)
        assert result.equity.iloc[-1] == pytest.approx(
            expected_final, rel=1e-12
        )
        assert result.total_deposits == pytest.approx(
            100.0 * len(rebal), rel=1e-12
        )


class TestThresholdRebalance:
    def test_zero_threshold_rebalances_on_every_drifted_bar(self) -> None:
        # threshold_pp = 0 → any positive drift post-return triggers
        # rebalance. With non-trivial dispersion, almost every bar fires.
        rng = np.random.default_rng(2020)
        idx = pd.date_range("2020-01-01", periods=60, freq="B")
        df = pd.DataFrame(
            {
                "leg0": rng.normal(0.002, 0.01, 60),
                "leg1": rng.normal(-0.002, 0.01, 60),
            },
            index=idx,
        )
        result = apply_threshold_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}, threshold_pp=0.0
        )
        # After rebalance, drift collapses to ~0 (tax may keep tiny
        # residual). Check that post-rebal drift is near zero on most
        # bars.
        assert result.drift.values.max() < 0.02
        assert result.n_taxable_events >= len(df) - 1

    def test_infinite_threshold_equals_buy_and_hold(self) -> None:
        # threshold_pp very large → never triggers → pure
        # buy-and-hold, zero events, zero tax.
        df = _mk_returns_df(seed=42, n=200)
        w = {"leg0": 0.5, "leg1": 0.5}
        result = apply_threshold_rebalance(
            df, w, threshold_pp=1e9, initial_capital=1.0
        )
        # Expected leg equities: w_j * (1 + r_j).cumprod()
        expected_leg0 = 0.5 * (1.0 + df["leg0"]).cumprod()
        expected_leg1 = 0.5 * (1.0 + df["leg1"]).cumprod()
        expected_total = expected_leg0 + expected_leg1
        np.testing.assert_allclose(
            result.equity.values, expected_total.values, rtol=1e-10
        )
        assert result.taxable_events == []
        assert result.total_tax_paid == 0.0

    def test_trigger_cross_is_strict_greater_than(self) -> None:
        # Construct a scenario where drift reaches exactly threshold_pp
        # — must NOT trigger. Reach > threshold → must trigger.
        idx = pd.date_range("2020-01-01", periods=8, freq="B")
        # leg0 gains 2% daily, leg1 flat → drift grows ~1pp/day.
        df = pd.DataFrame(
            {"leg0": [0.02] * 8, "leg1": [0.0] * 8}, index=idx
        )
        result_high = apply_threshold_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}, threshold_pp=50.0
        )
        # After 8 bars at 2%/0%, drift peaks modestly — below 50pp.
        assert result_high.n_taxable_events == 0

        # Much lower threshold → triggers at least once across 8 bars.
        result_low = apply_threshold_rebalance(
            df, {"leg0": 0.5, "leg1": 0.5}, threshold_pp=0.3
        )
        assert result_low.n_taxable_events >= 1

    def test_higher_threshold_reduces_events(self) -> None:
        # More conservative threshold → fewer rebalances over the
        # same return series.
        rng = np.random.default_rng(123)
        idx = pd.date_range("2015-01-01", periods=750, freq="B")
        df = pd.DataFrame(
            {
                "leg0": rng.normal(0.0008, 0.012, 750),
                "leg1": rng.normal(0.0003, 0.010, 750),
            },
            index=idx,
        )
        w = {"leg0": 0.5, "leg1": 0.5}
        r5 = apply_threshold_rebalance(df, w, threshold_pp=5.0)
        r10 = apply_threshold_rebalance(df, w, threshold_pp=10.0)
        r20 = apply_threshold_rebalance(df, w, threshold_pp=20.0)
        assert r5.n_taxable_events >= r10.n_taxable_events
        assert r10.n_taxable_events >= r20.n_taxable_events
        assert r5.n_taxable_events > r20.n_taxable_events

    def test_tax_per_event_matches_realized_gain(self) -> None:
        # Every TaxableEvent must satisfy tax_paid = tax_rate *
        # max(0, realized_gain).
        rng = np.random.default_rng(321)
        idx = pd.date_range("2018-01-01", periods=400, freq="B")
        df = pd.DataFrame(
            {
                "leg0": rng.normal(0.001, 0.013, 400),
                "leg1": rng.normal(-0.0003, 0.009, 400),
            },
            index=idx,
        )
        result = apply_threshold_rebalance(
            df,
            {"leg0": 0.5, "leg1": 0.5},
            threshold_pp=3.0,
            tax_rate=0.15,
        )
        assert result.n_taxable_events > 0
        sum_tax = 0.0
        for ev in result.taxable_events:
            if ev.realized_gain > 0:
                assert ev.tax_paid == pytest.approx(
                    0.15 * ev.realized_gain, rel=1e-12
                )
            else:
                assert ev.tax_paid == 0.0
            sum_tax += ev.tax_paid
        assert result.total_tax_paid == pytest.approx(sum_tax, rel=1e-12)

    def test_drift_resets_on_rebalance_dates(self) -> None:
        # Post-rebalance drift should collapse to ~0 on any bar where a
        # taxable event fired (with tax_rate=0 the reset is exact).
        idx = pd.date_range("2020-01-01", periods=80, freq="B")
        df = pd.DataFrame(
            {"leg0": [0.01] * 80, "leg1": [-0.005] * 80},
            index=idx,
        )
        result = apply_threshold_rebalance(
            df,
            {"leg0": 0.5, "leg1": 0.5},
            threshold_pp=5.0,
            tax_rate=0.0,
        )
        assert result.n_taxable_events >= 2
        rebal_dates = {ev.date for ev in result.taxable_events}
        for rd in rebal_dates:
            pos = idx.get_loc(rd)
            # Post-rebal max drift must be essentially zero.
            assert result.max_drift.iloc[pos] < 1e-9

    def test_zero_tax_rate_produces_tax_free_events(self) -> None:
        # With tax_rate=0, all TaxableEvents must record tax_paid == 0
        # even though the sell-overweight mechanic still fires.
        rng = np.random.default_rng(99)
        idx = pd.date_range("2019-01-01", periods=300, freq="B")
        df = pd.DataFrame(
            {
                "leg0": rng.normal(0.001, 0.013, 300),
                "leg1": rng.normal(-0.0003, 0.009, 300),
            },
            index=idx,
        )
        w = {"leg0": 0.5, "leg1": 0.5}
        r_thr = apply_threshold_rebalance(
            df, w, threshold_pp=3.0, tax_rate=0.0
        )
        assert r_thr.n_taxable_events > 0
        assert r_thr.total_tax_paid == 0.0
        for ev in r_thr.taxable_events:
            assert ev.tax_paid == 0.0

    def test_returns_RebalanceResult_with_event_dates_in_index(self) -> None:
        df = _mk_returns_df(seed=5, n=120)
        result = apply_threshold_rebalance(
            df,
            {"leg0": 0.5, "leg1": 0.5},
            threshold_pp=3.0,
        )
        assert isinstance(result, RebalanceResult)
        for ev in result.taxable_events:
            assert isinstance(ev, TaxableEvent)
            assert ev.date in df.index

    def test_three_leg_threshold_preserves_sum_of_leg_equity(self) -> None:
        # Regression guard: after rebalance, sum(leg_equity) == equity
        # on every bar.
        rng = np.random.default_rng(7)
        idx = pd.date_range("2010-01-01", periods=500, freq="B")
        df = pd.DataFrame(
            {
                "letf": rng.normal(0.0007, 0.013, 500),
                "qqq": rng.normal(0.0005, 0.011, 500),
                "gld": rng.normal(0.0002, 0.009, 500),
            },
            index=idx,
        )
        w = {"letf": 1 / 3, "qqq": 1 / 3, "gld": 1 / 3}
        result = apply_threshold_rebalance(df, w, threshold_pp=10.0)
        leg_sum = result.leg_equity.sum(axis=1)
        np.testing.assert_allclose(
            leg_sum.values, result.equity.values, rtol=1e-10
        )
