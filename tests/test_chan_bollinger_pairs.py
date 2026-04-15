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
    df_long = _synth_ohlcv(seed=1)
    # SLV synth is a noisy linear function of GLD synth: enough signal
    # for OLS + OU to succeed on the training slice.
    df_short = df_long.copy()
    df_short[["open", "high", "low", "close", "adj_close"]] = (
        df_long[["open", "high", "low", "close", "adj_close"]] / 2.5
        + np.random.default_rng(2).normal(0, 0.05, (len(df_long), 5))
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
