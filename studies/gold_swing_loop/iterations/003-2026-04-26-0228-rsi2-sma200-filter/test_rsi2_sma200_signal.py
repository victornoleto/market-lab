"""TDD tests for `connors_rsi2_signal_with_trend_filter` — iter 003.

The signal extends iter 001's RSI(2)<5 + SMA(5) MR strategy with one
additional entry gate: ``close > SMA(N_trend)``. Exit rule is unchanged.

Citations
---------
* `[short_term_trading_strategies, p.105-118]` — Connors trend-filter chapter
* `[advances_fin_ml, p.31-34]` — verifying simulator behavior in tests first
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))

from run_backtest import connors_rsi2_signal_with_trend_filter, wilder_rsi  # noqa: E402


def _synthetic_close(values: list[float], start: str = "2020-01-01") -> pd.DataFrame:
    """Build a daily-OHLC dataframe from a close series."""
    idx = pd.date_range(start=start, periods=len(values), freq="B")
    s = pd.Series(values, index=idx, dtype=float)
    return pd.DataFrame({"open": s, "high": s, "low": s, "close": s,
                         "adj_close": s, "volume": 0.0})


def test_backward_compat_when_trend_period_is_none():
    """sma_trend_period=None must reproduce iter 001's signal exactly."""
    np.random.seed(0)
    rng = np.random.default_rng(0)
    n = 500
    rets = rng.normal(0.0005, 0.012, size=n)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _synthetic_close(list(close))

    pos_filtered = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=None,
    )
    # Reproduce iter-001 logic inline as the reference.
    rsi = wilder_rsi(df["close"], 2)
    sma = df["close"].rolling(5, min_periods=5).mean()
    enter = (rsi < 5.0) & (df["close"] < sma)
    exit_ = df["close"] > sma
    pos_ref = np.zeros(len(df))
    state = 0
    for i in range(len(df)):
        if state == 0 and bool(enter.iloc[i]):
            state = 1
        elif state == 1 and bool(exit_.iloc[i]):
            state = 0
        pos_ref[i] = state
    np.testing.assert_array_equal(pos_filtered.values, pos_ref)


def test_filter_blocks_entry_when_close_below_sma_trend():
    """When close < SMA(200) the entry gate must block, even if RSI(2)<5."""
    # Construct: long downtrend (close < SMA(200) for > 250 bars), then
    # RSI(2) gets <5 deep in the slump → with filter, NO long must be opened.
    n = 320
    # First 60 bars: ramp up from 100 to 130 (so SMA(200) starts well below
    # current close once available); then 260 bars of monotonic decline
    # 130 → 60 with a tiny final RSI dip.
    up = np.linspace(100.0, 130.0, 60)
    down = np.linspace(130.0, 60.0, 260)
    close = np.concatenate([up, down])
    # Inject a 4-bar oversold dip near the end: 60 → 56 → 53 → 50 → 49
    close[-5:] = [56.0, 53.0, 50.0, 49.0, 48.5]
    df = _synthetic_close(list(close))

    pos = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=200,
    )
    # close at every bar after position-200 must be < SMA(200) (declining)
    sma_200 = df["close"].rolling(200, min_periods=200).mean()
    assert (df["close"].iloc[200:] < sma_200.iloc[200:]).all(), \
        "synthetic test setup failed: close not below SMA(200) in the tail"
    # No long position should be opened in the tail (filter must block).
    assert (pos.iloc[200:] == 0).all(), \
        "filter failed to block entries when close < SMA(200)"


def test_filter_is_subset_of_unfiltered_signal():
    """Filter can only RESTRICT entries, never add them.

    For every bar t, position_filtered[t] = 1 must IMPLY
    position_unfiltered[t] = 1. The gate cannot create new long entries.
    Equivalently, position_filtered − position_unfiltered ≤ 0 everywhere.
    """
    rng = np.random.default_rng(1)
    n = 800
    rets = rng.normal(0.0008, 0.011, size=n)  # mild long-term drift
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _synthetic_close(list(close))

    pos_filtered = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=200,
    )
    pos_unfiltered = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=None,
    )
    # filter is monotone restriction: pos_f ≤ pos_u everywhere
    assert (pos_filtered <= pos_unfiltered).all(), \
        "filter created entries that did not exist in the unfiltered signal"
    # And the unfiltered version must have produced at least SOME entries
    # so the comparison is meaningful (sanity check on synthetic).
    assert pos_unfiltered.sum() > 0, "synthetic produced zero unfiltered entries"


def test_filter_strictly_restricts_when_in_downtrend():
    """During a sustained downtrend (close < SMA(200)), filter must be
    strictly more restrictive than the unfiltered signal — i.e., produce
    fewer entries (this is the WHOLE POINT of adding the gate).

    We construct a deterministic 350-bar series that ramps up for the first
    150 bars (so SMA(200) becomes computable and bars are above it) and
    then declines steadily for the next 200 bars. In the declining tail,
    RSI(2)<5 fires occasionally on bounces, the unfiltered signal opens
    longs, and the filtered signal must NOT.
    """
    # 150 bars ramp 100 → 130, then 200 bars decline 130 → 60 with small
    # oscillations to give RSI(2) opportunities to dip < 5.
    n_up = 150
    n_down = 200
    rng = np.random.default_rng(7)
    up = np.linspace(100.0, 130.0, n_up)
    down_trend = np.linspace(130.0, 60.0, n_down)
    # Add small noise to create RSI(2) dips
    down = down_trend * (1.0 + rng.normal(0.0, 0.012, n_down))
    close = np.concatenate([up, down])
    df = _synthetic_close(list(close))

    pos_filtered = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=200,
    )
    pos_unfiltered = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=None,
    )
    # In the declining tail, unfiltered opens entries (RSI(2)<5 fires
    # repeatedly); filtered must open strictly fewer.
    sma_200 = df["close"].rolling(200, min_periods=200).mean()
    in_downtrend = (df["close"] < sma_200).fillna(False)
    n_unfilt_in_down = int(pos_unfiltered[in_downtrend].sum())
    n_filt_in_down = int(pos_filtered[in_downtrend].sum())
    assert n_unfilt_in_down > n_filt_in_down, (
        f"filter did not restrict during downtrend "
        f"(unfiltered={n_unfilt_in_down}, filtered={n_filt_in_down})"
    )


def test_no_entry_in_first_sma_trend_warmup_bars():
    """SMA(N_trend) is NaN for first N_trend-1 bars; no entry must fire then."""
    rng = np.random.default_rng(2)
    n = 250
    rets = rng.normal(0.0005, 0.012, size=n)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _synthetic_close(list(close))

    pos = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=200,
    )
    # No position can be 1 before bar 200 (SMA(200) is NaN before then).
    assert (pos.iloc[:200] == 0).all(), \
        "filter allowed entries before SMA(200) warmup completed"


def test_position_values_are_binary_long_only():
    """Position must be in {0, 1}; never short, never fractional."""
    rng = np.random.default_rng(3)
    rets = rng.normal(0.0005, 0.012, size=600)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _synthetic_close(list(close))

    pos = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=200,
    )
    unique_vals = set(pos.unique().tolist())
    assert unique_vals.issubset({0.0, 1.0}), \
        f"position must be binary {{0,1}}; got {unique_vals}"


def test_no_lookahead_position_only_uses_past_or_current_close():
    """Truncating the dataframe at any t must not change pos[≤t-1]."""
    rng = np.random.default_rng(4)
    rets = rng.normal(0.0005, 0.012, size=400)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _synthetic_close(list(close))

    pos_full = connors_rsi2_signal_with_trend_filter(
        df, rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=200,
    )
    # Truncate at bar 350; recompute; first 349 positions must match
    # exactly (i.e., bar 349's pos doesn't depend on bars 350..399).
    pos_trunc = connors_rsi2_signal_with_trend_filter(
        df.iloc[:350], rsi_period=2, rsi_threshold=5.0, sma_period=5,
        sma_trend_period=200,
    )
    np.testing.assert_array_equal(pos_full.iloc[:350].values, pos_trunc.values)
