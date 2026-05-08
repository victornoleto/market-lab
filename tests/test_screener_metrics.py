"""Tests for screener.metrics — atr_pct, realized_vol, dollar_volume."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.screener.metrics import (
    atr_pct,
    dollar_volume,
    realized_vol_annualized,
)


def _ohlcv(n: int = 300, base: float = 100.0, atr: float = 2.0, vol: float = 1e6):
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(7)
    closes = base + np.cumsum(rng.normal(0.0, 0.5, size=n))
    closes = np.clip(closes, base / 2, None)
    highs = closes + atr / 2
    lows = closes - atr / 2
    volumes = np.full(n, vol)
    return pd.DataFrame(
        {
            "open": closes,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        },
        index=idx,
    )


class TestAtrPct:
    def test_known_atr_value(self):
        df = _ohlcv(n=100, base=100.0, atr=2.0)
        result = atr_pct(df, lookback=20)
        # ATR ~ 2.0; mean close ~ 100 → ratio ~ 0.02
        assert 0.005 < result < 0.05

    def test_short_input_raises(self):
        df = _ohlcv(n=10)
        with pytest.raises(ValueError, match=">="):
            atr_pct(df, lookback=20)


class TestRealizedVolAnnualized:
    def test_zero_returns_yields_zero(self):
        idx = pd.date_range("2020-01-01", periods=300, freq="B")
        df = pd.DataFrame(
            {
                "open": 100.0,
                "high": 100.0,
                "low": 100.0,
                "close": 100.0,
                "volume": 1.0,
            },
            index=idx,
        )
        assert realized_vol_annualized(df, lookback=252) == 0.0

    def test_unit_log_returns_scale_to_sqrt_252(self):
        idx = pd.date_range("2020-01-01", periods=300, freq="B")
        rng = np.random.default_rng(11)
        log_ret = rng.normal(0.0, 1.0, size=299)
        log_p = np.concatenate(([np.log(100.0)], np.log(100.0) + np.cumsum(log_ret)))
        prices = np.exp(log_p)
        df = pd.DataFrame(
            {
                "open": prices,
                "high": prices,
                "low": prices,
                "close": prices,
                "volume": 1.0,
            },
            index=idx,
        )
        rv = realized_vol_annualized(df, lookback=252)
        # daily std ≈ 1.0, annualised ≈ √252 ≈ 15.87
        assert 12.0 < rv < 20.0

    def test_short_input_raises(self):
        df = _ohlcv(n=10)
        with pytest.raises(ValueError, match=">="):
            realized_vol_annualized(df, lookback=252)


class TestDollarVolume:
    def test_constant_volume_constant_close(self):
        df = _ohlcv(n=300, base=100.0, atr=0.0, vol=1_000_000.0)
        dv = dollar_volume(df, lookback=252)
        assert dv > 0
        # close ~100, vol = 1e6 → dv ≈ 1e8
        assert 5e7 < dv < 5e8

    def test_zero_volume_returns_zero(self):
        df = _ohlcv(n=300, vol=0.0)
        assert dollar_volume(df, lookback=252) == 0.0

    def test_nan_volume_treated_as_zero(self):
        df = _ohlcv(n=300, vol=1.0)
        df["volume"] = float("nan")
        assert dollar_volume(df, lookback=252) == 0.0

    def test_short_input_raises(self):
        df = _ohlcv(n=10)
        with pytest.raises(ValueError, match=">="):
            dollar_volume(df, lookback=252)
