"""Tests for synthetic LETF return helper (Gayed p.16 formula)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.helpers.synthetic_letf import (
    DEFAULT_ANNUAL_FEE,
    TRADING_DAYS_PER_YEAR,
    synthesize_letf_prices,
    synthesize_letf_returns,
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
