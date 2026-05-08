"""Tests for ``market_lab.backtest.helpers.momentum`` pure helpers.

Migrated from the deleted ``test_clenow_strategy.py`` (math helpers
section only) during the 2026-04-16 post-winners cleanup. Strategy-level
Clenow tests were removed with the strategy itself.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.helpers.momentum import adjusted_slope, atr, max_gap


class TestAdjustedSlope:
    def test_pure_exponential_is_perfect_fit(self):
        """log(P) linear in t → R² = 1; annualized slope = exp(m)^250 - 1."""
        m = 0.001
        prices = pd.Series(np.exp(m * np.arange(90)))

        ann_slope, r2 = adjusted_slope(prices, lookback=90)

        expected_ann = math.exp(m) ** 250 - 1
        assert ann_slope == pytest.approx(expected_ann, rel=1e-9)
        assert r2 == pytest.approx(1.0, rel=1e-9)

    def test_negative_slope_returns_negative_annualized(self):
        m = -0.002
        prices = pd.Series(np.exp(m * np.arange(90)))
        ann_slope, r2 = adjusted_slope(prices, lookback=90)

        assert ann_slope < 0
        assert ann_slope == pytest.approx(math.exp(m) ** 250 - 1, rel=1e-9)
        assert r2 == pytest.approx(1.0, rel=1e-9)

    def test_noisy_series_has_lower_r2(self):
        """Noise around a trend reduces R² below 1."""
        rng = np.random.default_rng(42)
        m = 0.001
        noise = rng.normal(0, 0.02, 90)
        prices = pd.Series(np.exp(m * np.arange(90) + noise))

        _, r2 = adjusted_slope(prices, lookback=90)
        assert 0.0 <= r2 < 0.95

    def test_uses_last_lookback_bars_only(self):
        """Function must slice the tail; earlier data doesn't affect result."""
        m = 0.001
        head = np.ones(30) * 100.0
        tail = np.exp(m * np.arange(90))
        prices = pd.Series(np.concatenate([head, tail]))

        ann_slope, r2 = adjusted_slope(prices, lookback=90)
        assert r2 == pytest.approx(1.0, rel=1e-9)
        assert ann_slope == pytest.approx(math.exp(m) ** 250 - 1, rel=1e-9)

    def test_raises_on_insufficient_history(self):
        prices = pd.Series(np.exp(0.001 * np.arange(50)))  # only 50 bars
        with pytest.raises(ValueError, match="lookback"):
            adjusted_slope(prices, lookback=90)


class TestATR:
    def test_constant_range_returns_that_range(self):
        """If every bar has TR=R, ATR over N bars = R."""
        n = 30
        close = pd.Series(np.full(n, 100.0))
        high = pd.Series(np.full(n, 101.0))
        low = pd.Series(np.full(n, 99.0))
        value = atr(high, low, close, lookback=20)
        assert value == pytest.approx(2.0)

    def test_uses_prev_close_in_tr_when_there_is_a_gap(self):
        """TR[t] = max(H-L, |H-C_prev|, |L-C_prev|); gap expands TR."""
        # 21 bars. Bar 0 close=100. Bars 1..19 close=100 flat. Bar 20 gaps up:
        # prev close 100, today open/low=108, high=110, close=109.
        # TR[20] = max(110-108=2, |110-100|=10, |108-100|=8) = 10.
        highs = [100.0] + [101.0] * 19 + [110.0]
        lows = [100.0] + [99.0] * 19 + [108.0]
        closes = [100.0] * 20 + [109.0]
        value = atr(
            pd.Series(highs),
            pd.Series(lows),
            pd.Series(closes),
            lookback=20,
        )
        # Last 20 TRs: 19 bars of TR=2, plus the gap bar TR=10.
        # mean = (19*2 + 10) / 20 = 48 / 20 = 2.4
        assert value == pytest.approx(2.4)


class TestMaxGap:
    def test_flat_series_has_zero_max_gap(self):
        close = pd.Series(np.full(100, 100.0))
        assert max_gap(close, lookback=90) == pytest.approx(0.0)

    def test_detects_large_single_day_jump(self):
        """A +20% one-day return shows up as max_gap = 0.20."""
        close = [100.0] * 50 + [120.0] + [120.0] * 49  # 100 bars
        value = max_gap(pd.Series(close), lookback=90)
        assert value == pytest.approx(0.20, rel=1e-9)

    def test_detects_large_negative_move(self):
        close = [100.0] * 50 + [75.0] + [75.0] * 49  # −25% jump
        value = max_gap(pd.Series(close), lookback=90)
        assert value == pytest.approx(0.25, rel=1e-9)

    def test_only_considers_last_lookback_returns(self):
        """Gap older than ``lookback`` must be ignored."""
        close = [100.0] * 10 + [200.0] + [200.0] * 189
        value = max_gap(pd.Series(close), lookback=90)
        assert value == pytest.approx(0.0)
