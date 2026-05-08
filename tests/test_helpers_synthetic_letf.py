"""Tests for synthetic LETF return helper (Gayed p.16 formula)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.helpers.synthetic_letf import (
    DEFAULT_ANNUAL_FEE,
    DEFAULT_EXPENSE_RATIO,
    DEFAULT_FFR_SPREAD,
    DEFAULT_SWAP_EXPOSURE,
    TRADING_DAYS_PER_YEAR,
    synthesize_letf_prices,
    synthesize_letf_returns,
    synthesize_letf_returns_ffr_aware,
)


@pytest.fixture
def simple_returns() -> pd.Series:
    idx = pd.date_range("2020-01-01", periods=5, freq="B")
    return pd.Series([0.01, -0.02, 0.005, 0.0, 0.015], index=idx)


class TestSynthesizeLetfReturns:
    def test_formula_matches_gayed_p16(self, simple_returns):
        # r_synth = L * r - fee/252
        out = synthesize_letf_returns(simple_returns, leverage=3.0, annual_fee=0.01)
        expected = 3.0 * simple_returns - 0.01 / TRADING_DAYS_PER_YEAR
        pd.testing.assert_series_equal(out, expected)

    def test_leverage_1_no_drag_when_fee_zero(self, simple_returns):
        out = synthesize_letf_returns(simple_returns, leverage=1.0, annual_fee=0.0)
        pd.testing.assert_series_equal(out, simple_returns)

    def test_default_fee_is_one_percent(self):
        assert DEFAULT_ANNUAL_FEE == 0.01

    def test_zero_leverage_raises(self, simple_returns):
        with pytest.raises(ValueError, match="leverage must be > 0"):
            synthesize_letf_returns(simple_returns, leverage=0.0)

    def test_negative_leverage_raises(self, simple_returns):
        with pytest.raises(ValueError, match="leverage must be > 0"):
            synthesize_letf_returns(simple_returns, leverage=-1.0)

    def test_preserves_index(self, simple_returns):
        out = synthesize_letf_returns(simple_returns, leverage=2.0)
        assert out.index.equals(simple_returns.index)

    def test_empty_series(self):
        idx = pd.DatetimeIndex([])
        empty = pd.Series([], index=idx, dtype=float)
        out = synthesize_letf_returns(empty, leverage=3.0)
        assert out.empty

    def test_3x_spx_big_gain_matches_paper_mechanism(self):
        # Single +5% SPX day at 3x leverage and 1% annual fee:
        # r_synth = 3 * 0.05 - 0.01/252 ≈ 0.15 - 0.0000397 ≈ 0.149960
        rets = pd.Series([0.05], index=pd.DatetimeIndex(["2020-01-01"]))
        out = synthesize_letf_returns(rets, leverage=3.0, annual_fee=0.01)
        assert out.iloc[0] == pytest.approx(0.15 - 0.01 / 252)


class TestSynthesizeLetfPrices:
    def test_cumprod_matches_manual(self, simple_returns):
        prices = synthesize_letf_prices(
            simple_returns, leverage=2.0, annual_fee=0.0, start_value=100.0
        )
        manual = (1 + 2.0 * simple_returns).cumprod() * 100.0
        pd.testing.assert_series_equal(prices, manual.astype(float))

    def test_start_value_respected(self, simple_returns):
        prices_100 = synthesize_letf_prices(simple_returns, leverage=1.0, start_value=100.0)
        prices_50 = synthesize_letf_prices(simple_returns, leverage=1.0, start_value=50.0)
        assert prices_100.iloc[0] / prices_50.iloc[0] == pytest.approx(2.0)

    def test_nan_treated_as_zero_return(self):
        idx = pd.date_range("2020-01-01", periods=3, freq="B")
        rets = pd.Series([0.01, np.nan, 0.02], index=idx)
        prices = synthesize_letf_prices(
            rets, leverage=1.0, annual_fee=0.0, start_value=100.0
        )
        # Day 1: 100*1.01=101. Day 2: NaN → 0 → 101. Day 3: 101*1.02=103.02.
        # Note annual_fee=0 so no drag.
        assert prices.iloc[0] == pytest.approx(101.0)
        assert prices.iloc[1] == pytest.approx(101.0)
        assert prices.iloc[2] == pytest.approx(103.02)


class TestSynthesizeLetfReturnsFfrAware:
    """Phase 3.5b Task 7a — testfolio FFR-aware cost model."""

    def test_defaults_match_testfolio(self):
        assert DEFAULT_SWAP_EXPOSURE == 1.1
        assert DEFAULT_FFR_SPREAD == 0.004
        assert DEFAULT_EXPENSE_RATIO == 0.0095

    def test_formula_matches_testfolio_model(self, simple_returns):
        ffr = pd.Series(0.05, index=simple_returns.index)
        out = synthesize_letf_returns_ffr_aware(
            simple_returns,
            leverage=2.0,
            ffr_annualized=ffr,
            swap_exposure=1.1,
            ffr_spread=0.004,
            expense_ratio=0.0095,
        )
        annual_cost = 1.1 * (2.0 - 1.0) * (0.05 + 0.004) + 0.0095
        expected = 2.0 * simple_returns - annual_cost / TRADING_DAYS_PER_YEAR
        pd.testing.assert_series_equal(out, expected)

    def test_leverage_1_only_expense_ratio_applies(self, simple_returns):
        ffr = pd.Series(0.10, index=simple_returns.index)
        out = synthesize_letf_returns_ffr_aware(
            simple_returns,
            leverage=1.0,
            ffr_annualized=ffr,
            expense_ratio=0.0095,
        )
        expected = simple_returns - 0.0095 / TRADING_DAYS_PER_YEAR
        pd.testing.assert_series_equal(out, expected)

    def test_ffr_zero_reduces_to_spread_only_on_swap(self, simple_returns):
        ffr = pd.Series(0.0, index=simple_returns.index)
        out = synthesize_letf_returns_ffr_aware(
            simple_returns,
            leverage=3.0,
            ffr_annualized=ffr,
            swap_exposure=1.1,
            ffr_spread=0.004,
            expense_ratio=0.0,
        )
        # cost = 1.1 * 2 * 0.004 = 0.0088
        expected = 3.0 * simple_returns - 0.0088 / TRADING_DAYS_PER_YEAR
        pd.testing.assert_series_equal(out, expected)

    def test_time_varying_ffr(self, simple_returns):
        ffr = pd.Series(
            [0.02, 0.04, 0.06, 0.08, 0.10], index=simple_returns.index
        )
        out = synthesize_letf_returns_ffr_aware(
            simple_returns,
            leverage=2.0,
            ffr_annualized=ffr,
            swap_exposure=1.1,
            ffr_spread=0.004,
            expense_ratio=0.0095,
        )
        annual_costs = 1.1 * 1.0 * (ffr + 0.004) + 0.0095
        expected = 2.0 * simple_returns - annual_costs / TRADING_DAYS_PER_YEAR
        pd.testing.assert_series_equal(out, expected)

    def test_ffr_reindex_ffill(self, simple_returns):
        # FFR with only the first 2 dates; rest ffilled
        idx = simple_returns.index
        partial_ffr = pd.Series([0.03, 0.05], index=idx[:2])
        out = synthesize_letf_returns_ffr_aware(
            simple_returns,
            leverage=2.0,
            ffr_annualized=partial_ffr,
            expense_ratio=0.0,
            ffr_spread=0.0,
            swap_exposure=1.0,
        )
        # cost = (L-1) * ffr_effective = 1 * ffr
        # Day 0: ffr=0.03 ; Day 1: ffr=0.05 ; Days 2-4 ffilled=0.05
        expected_costs = pd.Series([0.03, 0.05, 0.05, 0.05, 0.05], index=idx)
        expected = 2.0 * simple_returns - expected_costs / TRADING_DAYS_PER_YEAR
        pd.testing.assert_series_equal(out, expected)

    def test_ffr_outside_range_backfills(self, simple_returns):
        # FFR only at last index → backfill to earlier dates
        idx = simple_returns.index
        late_ffr = pd.Series([0.07], index=[idx[-1]])
        out = synthesize_letf_returns_ffr_aware(
            simple_returns,
            leverage=2.0,
            ffr_annualized=late_ffr,
            expense_ratio=0.0,
            ffr_spread=0.0,
            swap_exposure=1.0,
        )
        expected = 2.0 * simple_returns - 0.07 / TRADING_DAYS_PER_YEAR
        pd.testing.assert_series_equal(out, expected)

    def test_ffr_no_overlap_raises(self, simple_returns):
        disjoint_idx = pd.date_range("2030-01-01", periods=3, freq="B")
        far_ffr = pd.Series([np.nan, np.nan, np.nan], index=disjoint_idx)
        with pytest.raises(ValueError, match="no overlap"):
            synthesize_letf_returns_ffr_aware(
                simple_returns, leverage=2.0, ffr_annualized=far_ffr
            )

    def test_zero_leverage_raises(self, simple_returns):
        ffr = pd.Series(0.05, index=simple_returns.index)
        with pytest.raises(ValueError, match="leverage must be > 0"):
            synthesize_letf_returns_ffr_aware(
                simple_returns, leverage=0.0, ffr_annualized=ffr
            )

    def test_high_ffr_gap_vs_flat_model(self):
        # Sanity: in a 5%/yr FFR regime, FFR-aware 2x costs more than
        # flat 1% Gayed model — matches Phase 3.5b Task 7a empirical
        # finding (~+6%/yr gap, concentrated in FFR≥5% bucket).
        idx = pd.date_range("2020-01-01", periods=TRADING_DAYS_PER_YEAR, freq="B")
        rets = pd.Series(0.0004, index=idx)  # ~10%/yr flat
        ffr = pd.Series(0.05, index=idx)
        flat = synthesize_letf_returns(rets, leverage=2.0, annual_fee=0.01)
        aware = synthesize_letf_returns_ffr_aware(
            rets, leverage=2.0, ffr_annualized=ffr
        )
        # aware - flat < 0 (aware costs more → lower return each day)
        assert (aware - flat).mean() < 0
        # Annualized gap > 0.5% (well short of noise)
        annualized_gap = (flat - aware).mean() * TRADING_DAYS_PER_YEAR
        assert annualized_gap > 0.005
