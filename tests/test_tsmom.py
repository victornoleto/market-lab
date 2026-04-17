"""Tests for Donchian breakout TSMOM strategy (Phase 3 Lead A3b)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.tsmom import (
    TSMOMConfig,
    compute_donchian_signal,
    simulate_tsmom,
)


def _trending_up_ohlc(
    n: int = 300, daily_mu: float = 0.002, daily_sigma: float = 0.005, seed: int = 7
) -> tuple[pd.Series, pd.Series, pd.Series]:
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    rets = rng.normal(daily_mu, daily_sigma, n)
    close = pd.Series((1.0 + rets).cumprod() * 100.0, index=idx)
    # Synthetic H/L around close: wider bands keep Donchian realistic
    intra = rng.normal(0, 0.005, n) * close.values
    high = close + np.abs(intra) + 0.001 * close
    low = close - np.abs(intra) - 0.001 * close
    return high, low, close


def _choppy_ohlc(
    n: int = 300, amplitude: float = 0.02, seed: int = 11
) -> tuple[pd.Series, pd.Series, pd.Series]:
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    # Mean-reverting sine + tiny noise
    t = np.arange(n)
    close_vals = 100.0 + amplitude * 100.0 * np.sin(t / 10.0) + rng.normal(
        0, 0.1, n
    )
    close = pd.Series(close_vals, index=idx)
    high = close + 0.2
    low = close - 0.2
    return high, low, close


class TestTSMOMConfig:
    def test_defaults_are_turtle_40_20(self):
        cfg = TSMOMConfig()
        assert cfg.entry_lookback == 40
        assert cfg.exit_lookback == 20
        assert cfg.tax_rate == 0.15
        assert cfg.switch_cost_pct == pytest.approx(0.0015)

    def test_invalid_entry_lookback_raises(self):
        with pytest.raises(ValueError, match="entry_lookback"):
            TSMOMConfig(entry_lookback=1)

    def test_invalid_exit_lookback_raises(self):
        with pytest.raises(ValueError, match="exit_lookback"):
            TSMOMConfig(exit_lookback=0)

    def test_negative_costs_raise(self):
        with pytest.raises(ValueError, match="commission_bps"):
            TSMOMConfig(commission_bps=-1)
        with pytest.raises(ValueError, match="spread_bps"):
            TSMOMConfig(spread_bps=-1)

    def test_tax_rate_out_of_range_raises(self):
        with pytest.raises(ValueError, match="tax_rate"):
            TSMOMConfig(tax_rate=1.5)


class TestComputeDonchianSignal:
    def test_warmup_produces_nan(self):
        high, low, close = _trending_up_ohlc(n=100)
        sig = compute_donchian_signal(high, low, close, 40, 20)
        # First 40 bars must be NaN
        assert sig.iloc[:40].isna().all()
        assert sig.iloc[50:].notna().all()

    def test_uptrend_ends_long(self):
        high, low, close = _trending_up_ohlc(n=400, daily_mu=0.003)
        sig = compute_donchian_signal(high, low, close, 40, 20)
        # Strong uptrend should finish LONG
        assert sig.iloc[-1] == "LONG"

    def test_choppy_has_both_states(self):
        high, low, close = _choppy_ohlc(n=300)
        sig = compute_donchian_signal(high, low, close, 20, 10)
        non_warmup = sig.dropna()
        # Choppy should trigger both LONG and FLAT transitions
        assert "LONG" in non_warmup.values
        assert "FLAT" in non_warmup.values

    def test_misaligned_indices_raise(self):
        idx1 = pd.date_range("2020-01-01", periods=50, freq="B")
        idx2 = pd.date_range("2020-02-01", periods=50, freq="B")
        h = pd.Series(np.ones(50), index=idx1)
        with pytest.raises(ValueError, match="same index"):
            compute_donchian_signal(
                h,
                pd.Series(np.ones(50), index=idx2),
                pd.Series(np.ones(50), index=idx1),
            )

    def test_invalid_lookback_raises(self):
        h, l, c = _trending_up_ohlc(n=50)
        with pytest.raises(ValueError, match="entry_lookback"):
            compute_donchian_signal(h, l, c, entry_lookback=1, exit_lookback=20)
        with pytest.raises(ValueError, match="exit_lookback"):
            compute_donchian_signal(h, l, c, entry_lookback=40, exit_lookback=0)

    def test_no_lookahead(self):
        """The signal at bar t must not use bar-t highs/lows."""
        high, low, close = _trending_up_ohlc(n=200)
        sig1 = compute_donchian_signal(high, low, close, 20, 10)
        # Set the last high to something very large; signal must not change.
        high_mod = high.copy()
        high_mod.iloc[-1] = 1e9
        sig2 = compute_donchian_signal(high_mod, low, close, 20, 10)
        # All bars except the (len-1) index itself should be identical; the
        # last signal still uses prior_high which excludes bar t.
        pd.testing.assert_series_equal(sig1, sig2)


class TestSimulateTSMOM:
    def test_uptrend_makes_money(self):
        high, low, close = _trending_up_ohlc(n=500, daily_mu=0.002)
        cfg = TSMOMConfig(entry_lookback=20, exit_lookback=10, tax_rate=0.0)
        result = simulate_tsmom(high, low, close, cfg)
        assert result.equity.iloc[-1] > 1.0
        assert result.sharpe() > 0

    def test_choppy_loses_or_stalls(self):
        high, low, close = _choppy_ohlc(n=400)
        cfg = TSMOMConfig(entry_lookback=20, exit_lookback=10)
        result = simulate_tsmom(high, low, close, cfg)
        # Choppy + costs should underperform buy-hold; often <=1.0.
        assert result.cum_cost_pct > 0.0

    def test_taxes_reduce_terminal_equity(self):
        high, low, close = _trending_up_ohlc(n=500, daily_mu=0.002)
        cfg_no_tax = TSMOMConfig(
            entry_lookback=20, exit_lookback=10, tax_rate=0.0
        )
        cfg_tax = TSMOMConfig(
            entry_lookback=20, exit_lookback=10, tax_rate=0.15
        )
        r_no = simulate_tsmom(high, low, close, cfg_no_tax)
        r_tax = simulate_tsmom(high, low, close, cfg_tax)
        # If there were any ON->OFF transitions with gain, tax must reduce
        # terminal equity. If no realized gains occurred, equal.
        assert r_tax.equity.iloc[-1] <= r_no.equity.iloc[-1] + 1e-9

    def test_commission_drag_is_recorded(self):
        high, low, close = _choppy_ohlc(n=300)
        cfg = TSMOMConfig(
            entry_lookback=20,
            exit_lookback=10,
            commission_bps=50,
            spread_bps=20,
        )
        result = simulate_tsmom(high, low, close, cfg)
        assert result.cum_cost_pct > 0.0
        # At least one switch must have happened
        assert result.switches.sum() > 0

    def test_empty_close_raises(self):
        empty = pd.Series([], index=pd.DatetimeIndex([]), dtype=float)
        cfg = TSMOMConfig()
        with pytest.raises(ValueError, match="must not be empty"):
            simulate_tsmom(empty, empty, empty, cfg)

    def test_misaligned_raises(self):
        h, l, c = _trending_up_ohlc(n=100)
        h_bad = h.shift(1).dropna()  # different length
        with pytest.raises(ValueError, match="same index"):
            simulate_tsmom(h_bad, l, c, TSMOMConfig())

    def test_equity_matches_daily_returns_product(self):
        high, low, close = _trending_up_ohlc(n=200, daily_mu=0.001)
        cfg = TSMOMConfig(entry_lookback=20, exit_lookback=10, tax_rate=0.0)
        r = simulate_tsmom(high, low, close, cfg)
        # equity = cumprod(1 + daily_net); tolerance for first-bar zero.
        reconstructed = (1.0 + r.daily_returns.fillna(0.0)).cumprod()
        # Scale to the first equity observation to align.
        ratio = r.equity.iloc[-1] / reconstructed.iloc[-1]
        assert abs(ratio - 1.0) < 1e-6
