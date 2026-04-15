"""Tests for ChanBollingerPairsStrategy [algo_trading_chan, ch.3]."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.chan_bollinger_pairs import (
    ChanBollingerPairsStrategy,
)


def _synth_ohlcv(
    n: int = 2000,
    start: str = "2022-01-03 09:30",
    freq: str = "1h",
    seed: int = 0,
) -> pd.DataFrame:
    """Build a synthetic OHLCV frame with index of length ``n``."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start=start, periods=n, freq=freq)
    close = 100 + np.cumsum(rng.normal(0, 0.1, n))
    return pd.DataFrame(
        {
            "open": close,
            "high": close + 0.05,
            "low": close - 0.05,
            "close": close,
            "volume": 1_000_000,
            "adj_close": close,
        },
        index=idx,
    )


def test_instantiation_with_both_symbols_succeeds():
    # Cointegrated OU synth (same pattern as test_ols_recovers_known_beta):
    # y = 2.5·x + OU noise with half-life ≈ 20 bars → OLS + OU succeed.
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
        long_symbol="GLD",
        short_symbol="SLV",
    )
    assert strat.long_symbol == "GLD"
    assert strat.short_symbol == "SLV"


def test_missing_long_symbol_raises_keyerror():
    df = _synth_ohlcv(seed=1)
    with pytest.raises(KeyError, match="GLD"):
        ChanBollingerPairsStrategy(
            data={"SLV": df},
            long_symbol="GLD",
            short_symbol="SLV",
        )


def test_missing_short_symbol_raises_keyerror():
    df = _synth_ohlcv(seed=1)
    with pytest.raises(KeyError, match="SLV"):
        ChanBollingerPairsStrategy(
            data={"GLD": df},
            long_symbol="GLD",
            short_symbol="SLV",
        )


def test_misaligned_timestamps_raises_valueerror():
    df_long = _synth_ohlcv(n=2000, start="2022-01-03 09:30", seed=1)
    df_short = _synth_ohlcv(n=2000, start="2022-01-04 09:30", seed=2)
    with pytest.raises(ValueError, match="timestamps"):
        ChanBollingerPairsStrategy(
            data={"GLD": df_long, "SLV": df_short},
            long_symbol="GLD",
            short_symbol="SLV",
        )


def test_ols_recovers_known_beta():
    """Synthetic pair with y = 2.5 x + OU noise → β ≈ 2.5."""
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    # OU noise around 2.5·x (mean-reverting spread): half-life ≈ 20 bars
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
    )
    assert abs(strat._beta - 2.5) < 0.1, f"β recovered = {strat._beta}"


def test_ou_recovers_known_half_life():
    """OU synth with λ = -log(2)/20 → half-life bars ≈ 20."""
    rng = np.random.default_rng(7)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    target_hl = 20
    lam = -np.log(2) / target_hl
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
    )
    # Allow a ±50% envelope — OU estimation is noisy on finite samples.
    assert 10 <= strat._half_life_bars <= 40, (
        f"half-life recovered = {strat._half_life_bars}"
    )


def test_ou_rejects_random_walk():
    """Pure random walk spread (no mean reversion) → RuntimeError."""
    rng = np.random.default_rng(99)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.1, n))
    y = 50 + np.cumsum(rng.normal(0, 0.1, n))  # independent RW — no cointegration
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    with pytest.raises(RuntimeError, match=r"(cointegrated|t[-_]stat|half[-_]life)"):
        ChanBollingerPairsStrategy(
            data={"GLD": df_long, "SLV": df_short},
        )


def test_half_life_clamp_rejects_too_slow():
    """OU synth with half-life = 200 bars (> 60 max) → RuntimeError."""
    rng = np.random.default_rng(13)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 200.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    with pytest.raises(RuntimeError, match=r"half[-_]life"):
        ChanBollingerPairsStrategy(
            data={"GLD": df_long, "SLV": df_short},
        )
