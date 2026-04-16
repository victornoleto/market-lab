"""Tests for YangZhangCone + RegimeReading [volatility_trading, p.22-23, p.58-60]."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.vol_expansion_breakout import (
    RegimeReading,
    YangZhangCone,
)


def test_regime_reading_dataclass_fields() -> None:
    r = RegimeReading(
        is_quiet=True,
        sigma_yz_annual=0.20,
        sigma_yz_percentile=12.0,
        bars_in_history=1700,
    )
    assert r.is_quiet is True
    assert r.sigma_yz_annual == pytest.approx(0.20)
    assert r.sigma_yz_percentile == pytest.approx(12.0)
    assert r.bars_in_history == 1700


# ---------------------------------------------------------------------------
# Task 3: Yang-Zhang estimator helpers
# ---------------------------------------------------------------------------

def _ohlc_df(opens, highs, lows, closes) -> pd.DataFrame:
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes})


def test_yz_k_weighting_factor_n20() -> None:
    """k = 0.34 / (1.34 + (N+1)/(N-1)) for N=20."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=1638)
    expected_k = 0.34 / (1.34 + (20 + 1) / (20 - 1))
    assert cone._k() == pytest.approx(expected_k)


def test_yz_constant_prices_returns_zero() -> None:
    """Constant OHLC -> all variance components 0 -> sigma_yz=0."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=1638)
    df = _ohlc_df([100.0]*30, [100.0]*30, [100.0]*30, [100.0]*30)
    sigma_per_bar = cone._yz_per_bar(df)
    assert sigma_per_bar == pytest.approx(0.0, abs=1e-12)


def test_yz_opening_jump_dominates_close_to_close() -> None:
    """Overnight gaps push YZ above close-to-close (Sinclair p.22 claim)."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=1638)
    rng = np.random.default_rng(42)
    n = 30
    closes = 100.0 + np.cumsum(rng.normal(0, 0.5, n))
    opens = closes + rng.normal(0, 1.5, n)  # large overnight jumps
    highs = np.maximum(opens, closes) + 0.1
    lows = np.minimum(opens, closes) - 0.1
    df = _ohlc_df(opens, highs, lows, closes)
    yz = cone._yz_per_bar(df)
    log_returns = np.log(closes[1:] / closes[:-1])
    cc_per_bar = float(log_returns.std(ddof=0))
    assert yz > cc_per_bar


def test_yz_annualization_spy_bars_per_year() -> None:
    """sigma_yz_annual = sigma_per_bar × sqrt(bars_per_year). SPY=1638."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=1638)
    annual = cone._annualize(0.01)
    assert annual == pytest.approx(0.01 * math.sqrt(1638))


def test_yz_annualization_fx_bars_per_year() -> None:
    """FX uses 6240 bars/year."""
    cone = YangZhangCone(yz_window=20, cone_lookback=1700, k_filter=33.0, bars_per_year=6240)
    annual = cone._annualize(0.01)
    assert annual == pytest.approx(0.01 * math.sqrt(6240))


# ---------------------------------------------------------------------------
# Task 4: cone percentile read() + k_filter gate
# ---------------------------------------------------------------------------

def _synth_ohlc(n: int, seed: int = 0, scale: float = 1.0) -> pd.DataFrame:
    """Synthetic OHLC with controllable noise scale."""
    rng = np.random.default_rng(seed)
    closes = 100.0 + np.cumsum(rng.normal(0, 0.5 * scale, n))
    opens = closes + rng.normal(0, 0.2 * scale, n)
    highs = np.maximum(opens, closes) + np.abs(rng.normal(0, 0.3 * scale, n))
    lows = np.minimum(opens, closes) - np.abs(rng.normal(0, 0.3 * scale, n))
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes})


def test_cone_warmup_returns_not_quiet() -> None:
    """Until cone_lookback bars accumulate, is_quiet=False, percentile=NaN."""
    cone = YangZhangCone(yz_window=20, cone_lookback=100, k_filter=33.0, bars_per_year=1638)
    df = _synth_ohlc(50)
    reading = cone.read(df)
    assert reading.is_quiet is False
    assert reading.bars_in_history < 100
    assert math.isnan(reading.sigma_yz_percentile)


def test_cone_post_warmup_emits_percentile() -> None:
    """Past warmup, percentile is in [0, 100]."""
    cone = YangZhangCone(yz_window=20, cone_lookback=100, k_filter=33.0, bars_per_year=1638)
    df = _synth_ohlc(200, seed=7)
    reading = cone.read(df)
    assert reading.bars_in_history >= 100
    assert 0.0 <= reading.sigma_yz_percentile <= 100.0
    assert reading.sigma_yz_annual >= 0.0


def test_cone_quiet_when_current_yz_below_k_percentile() -> None:
    """If current YZ is in the bottom k_filter pct of history, is_quiet=True."""
    cone = YangZhangCone(yz_window=20, cone_lookback=100, k_filter=33.0, bars_per_year=1638)
    high_vol = _synth_ohlc(150, seed=1, scale=3.0)
    low_vol = _synth_ohlc(30, seed=2, scale=0.3)
    low_vol = low_vol + (high_vol["close"].iloc[-1] - low_vol["close"].iloc[0])
    df = pd.concat([high_vol, low_vol], ignore_index=True)
    reading = cone.read(df)
    assert reading.is_quiet is True
    assert reading.sigma_yz_percentile <= 33.0
