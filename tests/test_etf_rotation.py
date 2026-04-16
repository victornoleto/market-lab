"""Tests for ETFRotationStrategy."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy
from ai_trade.backtest.engine.execution import Bar, ExecutionConfig, ExecutionSimulator
from ai_trade.backtest.engine.runner import Runner


def _make_ohlcv(close_series: pd.Series) -> pd.DataFrame:
    c = close_series.astype(float)
    return pd.DataFrame({
        "open": c.shift(1).fillna(c.iloc[0]),
        "high": c * 1.001,
        "low": c * 0.999,
        "close": c,
        "volume": 1_000_000.0,
    }, index=c.index)


def _make_universe(n: int = 600, freq: str = "B") -> dict[str, pd.DataFrame]:
    """5-ETF universe: SPY trending up, others flat-ish."""
    idx = pd.date_range("2020-01-01", periods=n, freq=freq)
    rng = np.random.default_rng(42)

    data = {}
    # SPY trends up — should always be #1 in regime
    spy = pd.Series(100 * np.cumprod(1 + rng.normal(0.0006, 0.01, n)), index=idx)
    data["SPY"] = _make_ohlcv(spy)

    for sym, drift in [("QQQ", 0.0003), ("IWM", 0.0001), ("GLD", -0.0001), ("TLT", -0.0002)]:
        prices = pd.Series(100 * np.cumprod(1 + rng.normal(drift, 0.012, n)), index=idx)
        data[sym] = _make_ohlcv(prices)

    return data


class TestETFRotationBasic:
    def test_init(self):
        data = _make_universe()
        strat = ETFRotationStrategy(
            data=data,
            symbols=["SPY", "QQQ", "IWM", "GLD", "TLT"],
        )
        assert strat.lookback == 90
        assert strat.sma_index_period == 200

    def test_missing_symbol_raises(self):
        data = _make_universe()
        with pytest.raises(KeyError):
            ETFRotationStrategy(data=data, symbols=["NONEXISTENT"])

    def test_monthly_rebalance_trigger(self):
        data = _make_universe()
        strat = ETFRotationStrategy(
            data=data,
            symbols=["SPY", "QQQ", "IWM", "GLD", "TLT"],
        )
        # First call always rebalances (prev_month=-1)
        ts1 = pd.Timestamp("2021-01-04")
        assert strat.should_rebalance(ts1, {}) is True
        # Same month: no rebalance
        ts2 = pd.Timestamp("2021-01-15")
        assert strat.should_rebalance(ts2, {}) is False
        # Next month: rebalance again
        ts3 = pd.Timestamp("2021-02-01")
        assert strat.should_rebalance(ts3, {}) is True

    def test_runner_completes(self):
        data = _make_universe(n=600)
        strat = ETFRotationStrategy(
            data=data,
            symbols=["SPY", "QQQ", "IWM", "GLD", "TLT"],
            lookback=90,
            sma_index_period=200,
            sma_stock_period=100,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        # Slice to last 300 bars for the bounded run
        idx = data["SPY"].index
        bounded = {sym: df.loc[idx[300]:] for sym, df in data.items()}
        result = runner.run(strategy=strat, data=bounded, initial_cash=100_000.0)
        assert result is not None
        assert result.equity_curve is not None
        assert len(result.equity_curve) > 0
        # Should end with some equity (not zero)
        assert float(result.equity_curve.iloc[-1]) > 0

    def test_flat_in_bear_regime(self):
        """When index is below SMA200 throughout, should hold no positions."""
        idx = pd.date_range("2020-01-01", periods=500, freq="B")
        # Strongly downtrending SPY
        spy_close = pd.Series(100 * np.cumprod(1 + np.full(500, -0.003)), index=idx)
        spy_df = _make_ohlcv(spy_close)
        qqq_close = pd.Series(100 * np.ones(500), index=idx)
        qqq_df = _make_ohlcv(qqq_close)
        data = {"SPY": spy_df, "QQQ": qqq_df}

        strat = ETFRotationStrategy(
            data=data,
            symbols=["SPY", "QQQ"],
            index_symbol="SPY",
            sma_index_period=200,
        )
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        bounded = {sym: df.iloc[300:] for sym, df in data.items()}
        result = runner.run(strategy=strat, data=bounded, initial_cash=100_000.0)
        # Should end near initial cash (flat in bear regime)
        assert float(result.equity_curve.iloc[-1]) == pytest.approx(100_000.0, rel=0.01)
