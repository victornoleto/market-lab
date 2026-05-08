"""Unit tests for Clenow cross-sectional momentum primitives.

Book canonical spec: `[stocks_on_the_move, p.70-77, 81-82, 88-89, 98-99]`.

These tests pin the mathematical building blocks — annualized exponential
regression slope, adjusted slope (slope × R²), ATR, risk-parity sizing,
gap filter, regime filter, top-K ranking — so the strategy's edge (or
lack thereof) is not obscured by silent arithmetic bugs.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.strategies.sector_momentum_clenow import (
    SectorMomentumClenow,
    adjusted_slope,
    atr,
    disqualify_gap,
    disqualify_trend,
    position_size_shares,
    regime_allows_new_buys,
    top_k_ranks,
)


# ---------------------------------------------------------------------------
# Adjusted slope
# ---------------------------------------------------------------------------


class TestAdjustedSlope:
    def test_pure_exponential_produces_exact_annualized_slope(self):
        """A series P_t = P_0 * exp(m * t) must recover slope m exactly.

        Annualized slope formula: (e^m)^250 - 1  [p.77]. With m=0.001
        (daily log-return), annualized ≈ (e^0.001)^250 - 1 = 28.40%.
        """
        m = 0.001
        prices = pd.Series(np.exp(m * np.arange(90)) * 100.0)
        slope, r2 = adjusted_slope(prices, lookback=90)
        expected_annualized = math.exp(m) ** 250 - 1
        assert slope == pytest.approx(expected_annualized, abs=1e-6)
        assert r2 == pytest.approx(1.0, abs=1e-9)

    def test_r_squared_penalizes_noisy_same_mean_slope(self):
        """Two series with same mean daily log-slope but different R² →
        adjusted slope (= annualized × R²) ranks the smooth one higher."""
        rng = np.random.default_rng(42)
        t = np.arange(90)
        m = 0.0005
        smooth = np.exp(m * t)
        noisy = smooth * np.exp(rng.normal(0, 0.02, size=90))
        slope_smooth, r2_smooth = adjusted_slope(pd.Series(smooth), lookback=90)
        slope_noisy, r2_noisy = adjusted_slope(pd.Series(noisy), lookback=90)
        adj_smooth = slope_smooth * r2_smooth
        adj_noisy = slope_noisy * r2_noisy
        assert r2_smooth > r2_noisy
        assert adj_smooth > adj_noisy

    def test_flat_series_yields_slope_zero_and_low_r_squared(self):
        """A constant-price series has slope = 0 and undefined (clamped) R².
        Either way, the adjusted rank should be 0 or slightly negative."""
        prices = pd.Series(np.full(90, 100.0))
        slope, r2 = adjusted_slope(prices, lookback=90)
        assert slope == pytest.approx(0.0, abs=1e-9)
        # R² undefined when variance = 0; implementation should return 0.0.
        assert r2 == pytest.approx(0.0, abs=1e-9)

    def test_rejects_series_shorter_than_lookback(self):
        """Clenow requires a full 90d window. Shorter = NaN."""
        prices = pd.Series([100.0] * 50)
        with pytest.raises(ValueError):
            adjusted_slope(prices, lookback=90)


# ---------------------------------------------------------------------------
# ATR
# ---------------------------------------------------------------------------


class TestAtr:
    def test_atr_on_known_ohlc_example(self):
        """Synthetic OHLC: H=102, L=98, close_prev=100 → TR=4 (H-L).

        Over 20 bars with identical TR, ATR20 = 4.0 exactly.
        """
        n = 25
        df = pd.DataFrame({
            "open": np.full(n, 100.0),
            "high": np.full(n, 102.0),
            "low": np.full(n, 98.0),
            "close": np.full(n, 100.0),
        })
        # Shift close_prev manually for consistency.
        val = atr(df, lookback=20)
        # Last ATR value should be 4.0 — every bar's TR = max(102-98, ...) = 4.
        assert val == pytest.approx(4.0, abs=1e-9)

    def test_atr_respects_gap_up_via_close_prev(self):
        """Gap up: today H=105, L=104, close_prev=100 → TR=5 (|H - close_prev|)."""
        df = pd.DataFrame({
            "open": [100, 100, 100, 105],
            "high": [101, 101, 101, 105.5],
            "low":  [ 99,  99,  99, 104.0],
            "close":[100, 100, 100, 105.0],
        })
        # lookback=3: ATR = mean of TR for last 3 bars.
        # TR_0 = NaN (no prev), TR_1 = max(2, 1, 1) = 2, TR_2 = 2,
        # TR_3 = max(1.5, |105.5-100|, |104-100|) = 5.5.
        val = atr(df, lookback=3)
        assert val == pytest.approx((2 + 2 + 5.5) / 3, abs=1e-9)


# ---------------------------------------------------------------------------
# Position sizing
# ---------------------------------------------------------------------------


class TestPositionSize:
    def test_clenow_monster_beverage_example(self):
        """`[p.89]`: Account $100k, Monster Beverage ATR=3.26, 10bps risk
        → 100_000 * 0.001 / 3.26 = 30.67 → floor to 30 shares."""
        shares = position_size_shares(equity=100_000.0, atr20=3.26, risk_factor=0.001)
        assert shares == 30

    def test_zero_atr_returns_zero_shares(self):
        """Degenerate ATR (no movement) → no position."""
        assert position_size_shares(equity=100_000.0, atr20=0.0, risk_factor=0.001) == 0

    def test_scales_with_equity(self):
        small = position_size_shares(equity=50_000.0, atr20=2.0, risk_factor=0.001)
        big = position_size_shares(equity=200_000.0, atr20=2.0, risk_factor=0.001)
        assert big == 4 * small


# ---------------------------------------------------------------------------
# Gap filter
# ---------------------------------------------------------------------------


class TestGapFilter:
    def test_disqualifies_20pct_single_day(self):
        """20% single-day move > 15% threshold → disqualified `[p.82]`."""
        prices = pd.Series([100] * 50 + [120] + [120] * 39)
        assert disqualify_gap(prices, lookback=90, threshold=0.15) is True

    def test_allows_gradual_30pct_rise(self):
        """Gradual rise with no single-day >15% move → allowed."""
        prices = pd.Series(np.linspace(100, 130, 90))
        assert disqualify_gap(prices, lookback=90, threshold=0.15) is False

    def test_disqualifies_on_big_down_day(self):
        """Big negative gap also counts (abs value)."""
        prices = pd.Series([100] * 50 + [80] + [80] * 39)
        assert disqualify_gap(prices, lookback=90, threshold=0.15) is True


# ---------------------------------------------------------------------------
# Trend / regime filters
# ---------------------------------------------------------------------------


class TestTrendAndRegimeFilter:
    def test_stock_below_100d_sma_is_disqualified(self):
        """Per-stock trend filter `[p.81-82]`: close < SMA(100) → reject."""
        # Uptrend for 100 days then drops
        prices = pd.Series(list(np.linspace(100, 150, 100)) + [100.0])
        # Last close = 100; SMA over last 100d ≈ mean(100..150) = 125.
        assert disqualify_trend(prices, lookback=100) is True

    def test_stock_above_100d_sma_passes(self):
        prices = pd.Series(list(np.linspace(100, 200, 101)))
        assert disqualify_trend(prices, lookback=100) is False

    def test_regime_off_blocks_new_buys(self):
        """SPY < 200d SMA → no new positions `[p.98-99]`."""
        # Downtrend: prices below SMA.
        prices = pd.Series(list(np.linspace(200, 100, 201)))
        assert regime_allows_new_buys(prices, lookback=200) is False

    def test_regime_on_allows_new_buys(self):
        prices = pd.Series(list(np.linspace(100, 300, 201)))
        assert regime_allows_new_buys(prices, lookback=200) is True


# ---------------------------------------------------------------------------
# Top-K ranking
# ---------------------------------------------------------------------------


class TestTopKRanks:
    def test_picks_highest_scoring_k(self):
        scores = {"A": 0.10, "B": 0.30, "C": 0.05, "D": 0.25, "E": 0.20}
        top3 = top_k_ranks(scores, k=3)
        assert top3 == ["B", "D", "E"]

    def test_excludes_disqualified(self):
        scores = {"A": 0.30, "B": 0.20, "C": 0.10}
        disq = {"A"}
        top2 = top_k_ranks(scores, k=2, disqualified=disq)
        assert top2 == ["B", "C"]

    def test_nan_scores_excluded(self):
        scores = {"A": float("nan"), "B": 0.10, "C": 0.20}
        top1 = top_k_ranks(scores, k=1)
        assert top1 == ["C"]


# ---------------------------------------------------------------------------
# Strategy integration (smoke — uses full Runner)
# ---------------------------------------------------------------------------


class TestStrategyIntegration:
    """End-to-end smoke test: synthetic 3-sector universe + SPY regime."""

    @pytest.fixture
    def synthetic_data(self):
        """Three sectors with distinct trends + SPY always up (regime ON)."""
        rng = np.random.default_rng(0)
        n = 400
        idx = pd.bdate_range("2020-01-01", periods=n)

        def make_series(start: float, drift: float, noise: float = 0.005) -> pd.DataFrame:
            rets = rng.normal(drift, noise, size=n)
            close = start * np.exp(np.cumsum(rets))
            df = pd.DataFrame({
                "open": close * (1 - 0.001),
                "high": close * 1.005,
                "low":  close * 0.995,
                "close": close,
                "volume": 1e6,
            }, index=idx)
            return df

        return {
            "XLK": make_series(100, 0.0008),   # strongest uptrend
            "XLF": make_series(100, 0.0004),   # moderate
            "XLP": make_series(100, 0.0001),   # weakest
            "SPY": make_series(300, 0.0005),   # always up → regime ON
        }

    def test_strategy_runs_without_errors(self, synthetic_data):
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
        )
        from market_lab.backtest.engine.runner import Runner

        strategy = SectorMomentumClenow(
            universe=["XLK", "XLF", "XLP"],
            regime_symbol="SPY",
            top_k=2,
            buy_leverage=1.0,
        )
        runner = Runner(executor=ExecutionSimulator(config=ExecutionConfig()))
        result = runner.run(strategy, synthetic_data, initial_cash=100_000.0)
        assert len(result.equity_curve) > 0
        assert result.final_equity > 0

    def test_strategy_favors_strongest_trend(self, synthetic_data):
        """At end of run, the strategy should have concentrated exposure in
        the strongest-trend sector (XLK) more than in the weakest (XLP)."""
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
        )
        from market_lab.backtest.engine.runner import Runner

        strategy = SectorMomentumClenow(
            universe=["XLK", "XLF", "XLP"],
            regime_symbol="SPY",
            top_k=1,  # force concentration into top-1
            buy_leverage=1.0,
        )
        runner = Runner(executor=ExecutionSimulator(config=ExecutionConfig()))
        result = runner.run(strategy, synthetic_data, initial_cash=100_000.0)
        # Count trades per symbol — XLK should dominate.
        xlk_trades = sum(1 for t in result.trades if t.symbol == "XLK")
        xlp_trades = sum(1 for t in result.trades if t.symbol == "XLP")
        # Strategy should have entered XLK multiple times (it's top-1 for most
        # of the window). XLP should rarely or never be entered.
        assert xlk_trades >= xlp_trades


# ---------------------------------------------------------------------------
# Cross-lib numpy reference parity (G7 gate primitive)
# ---------------------------------------------------------------------------


class TestNumpyReferenceParity:
    """Independent numpy-only reimplementation of adjusted_slope — ±1e-10."""

    def _numpy_ref_adjusted_slope(self, prices: np.ndarray, lookback: int = 90):
        y = np.log(prices[-lookback:])
        x = np.arange(lookback, dtype=float)
        x_mean = x.mean()
        y_mean = y.mean()
        cov = ((x - x_mean) * (y - y_mean)).sum()
        var_x = ((x - x_mean) ** 2).sum()
        var_y = ((y - y_mean) ** 2).sum()
        slope_m = cov / var_x
        annualized = math.exp(slope_m) ** 250 - 1
        if var_y == 0.0:
            r2 = 0.0
        else:
            r2 = (cov ** 2) / (var_x * var_y)
        return annualized, r2

    def test_adjusted_slope_matches_numpy_reference(self):
        rng = np.random.default_rng(7)
        prices = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, 90))))
        impl_slope, impl_r2 = adjusted_slope(prices, lookback=90)
        ref_slope, ref_r2 = self._numpy_ref_adjusted_slope(prices.values, lookback=90)
        assert impl_slope == pytest.approx(ref_slope, abs=1e-10)
        assert impl_r2 == pytest.approx(ref_r2, abs=1e-10)
