"""Smoke tests for Phase 3.7 H3.a — BTC Donchian ensemble independent signal.

Invariants covered:

1. ``compute_donchian_bands`` produces strict-past-only bands (the
   ensemble upper/lower at bar ``t`` cannot depend on high/low at ``t``).
2. ``simulate_h3_btc_donchian`` enforces the 2-day time stop: no trade
   can remain open beyond ``max_hold_days`` bars.
3. ATR trailing stop fires when price reverts through the trail level
   on a synthetic monotone-up-then-dump fixture.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.phase3_7_h3_btc_donchian import (
    H3BTCDonchianConfig,
    compute_atr_wilder_daily,
    compute_donchian_bands,
    simulate_h3_btc_donchian,
)


def _synthetic_ohlc(close_path: list[float], start: str = "2020-01-01") -> pd.DataFrame:
    """Minimal OHLC frame with high/low flanking the close."""
    idx = pd.DatetimeIndex(pd.date_range(start=start, periods=len(close_path), freq="D"))
    c = np.asarray(close_path, dtype=float)
    # Synthetic H/L: ±0.5% of close, O = prior C (or same as close on bar 0).
    h = c * 1.005
    low = c * 0.995
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame(
        {"open": o, "high": h, "low": low, "close": c, "adj_close": c, "volume": 1e3},
        index=idx,
    )


def test_donchian_bands_strict_past():
    """The upper/lower ensemble at bar t must use only bars strictly before t."""
    # Rising-then-falling high: bar 4 is the local max at 110.
    highs = pd.Series(
        [100.0, 102.0, 105.0, 108.0, 110.0, 109.0, 107.0, 106.0],
        index=pd.date_range("2020-01-01", periods=8),
    )
    lows = highs * 0.98
    # With lookbacks=(3,), the upper band at t uses max over [t-3..t-1].
    upper, lower = compute_donchian_bands(highs, lows, lookbacks=(3,))
    # Warmup: first 3 bars NaN (rolling needs 3) + shift(1) → first 4 NaN.
    assert upper.iloc[:3].isna().all()
    # Bar 3 (index 3) upper = max over high[0..2] = max(100, 102, 105) = 105.
    assert upper.iloc[3] == pytest.approx(105.0)
    # Bar 4 upper = max(high[1..3]) = max(102, 105, 108) = 108.
    assert upper.iloc[4] == pytest.approx(108.0)
    # Bar 5 upper = max(high[2..4]) = max(105, 108, 110) = 110.
    assert upper.iloc[5] == pytest.approx(110.0)
    # Critical: bar 5's high is 109.0, but upper[5] depends ONLY on [2..4].
    # Lower symmetric sanity: bar 5 lower = min(low[2..4]).
    assert lower.iloc[5] == pytest.approx(105.0 * 0.98)


def test_time_stop_two_day_max_hold():
    """No open trade may last longer than config.max_hold_days bars.

    Synthetic: monotone uptrend for 80 bars to trigger long entries, then
    assert all hold_lengths ≤ 2.
    """
    # 80-day monotone uptrend with small noise so Donchian breaks trigger.
    n = 200
    rng = np.random.default_rng(0)
    # Create enough warm-up (≥40 bars) for the (10,20,40) ensemble to arm.
    ramp = np.linspace(100.0, 100.0, 50).tolist()  # flat 50 bars warmup
    ramp += (np.linspace(100.0, 200.0, n - 50) * (1.0 + rng.normal(0.0, 1e-3, n - 50))).tolist()
    df = _synthetic_ohlc(ramp)
    cfg = H3BTCDonchianConfig(
        lookbacks=(10, 20, 40), max_hold_days=2,
        risk_per_trade=0.01, max_leverage=1.0, allow_short=False,
        spread_bps_per_side=0.0, commission_bps=0.0,
        swap_long_daily=0.0, swap_short_daily=0.0,
    )
    res = simulate_h3_btc_donchian(df, cfg)
    # At least one trade should trigger on the uptrend portion.
    assert res.n_trades >= 1
    # Every recorded hold length must respect the 2-day cap.
    assert all(h <= 2 for h in res.hold_lengths), (
        f"found holds > 2 days: {res.hold_lengths}"
    )
    # And none zero (each trade must have at least 1 bar of exposure).
    assert all(h >= 1 for h in res.hold_lengths)


def test_atr_trailing_stop_fires_on_dump():
    """An ATR-magnitude drop during an open long must trigger an ATR-trail
    exit before the time stop.

    Construction:
    * Long warmup (50 bars flat) so (10,20,40) Donchian bands arm.
    * Short monotone ramp (5 bars) that breaks the 10/20/40 Donchian
      upper (breakout on bar ~55).
    * Price at bar 56 = +1.0 relative to entry; ATR ≈ 0.5 × 2 = 1.0 ⇒
      trail stop ≈ entry − 1.0, but peak-tracking keeps moving.
    * Bar 57: single-bar dump of −8% that blows through the ATR trail.
    * Set ``max_hold_days`` to a large number (50) so the 2-day time
      stop cannot fire first.
    """
    # 50 flat bars → 5-bar small ramp → 1 breakout bar → 1 massive dump
    # → stable low. Breakout happens once the 10-day Donchian high
    # (warmup max 100.0) is exceeded; ramp peaks at 102.5 on bar 54.
    warmup = [100.0] * 50
    ramp = [100.5, 101.0, 101.5, 102.0, 102.5]
    # bar 55: still climbing slightly, so entry fires
    continued = [103.0, 104.0]
    # bar 57: violent dump to 90 (far below any ATR-based trail)
    dump = [90.0]
    tail = [88.0, 88.0, 88.0, 88.0, 88.0]
    close_path = warmup + ramp + continued + dump + tail
    df = _synthetic_ohlc(close_path)
    cfg = H3BTCDonchianConfig(
        lookbacks=(10, 20, 40), atr_period=20, atr_multiplier=2.0,
        max_hold_days=50,  # large enough that time-stop can't pre-empt ATR
        risk_per_trade=0.01, max_leverage=1.0, allow_short=False,
        spread_bps_per_side=0.0, commission_bps=0.0,
        swap_long_daily=0.0, swap_short_daily=0.0,
    )
    res = simulate_h3_btc_donchian(df, cfg)
    assert res.n_trades >= 1, "no trade triggered — fixture does not exercise test"
    assert "atr_trail" in set(res.exit_reason.unique()), (
        f"no ATR-trail exits recorded; got reasons: "
        f"{set(res.exit_reason.unique())}"
    )


def test_atr_wilder_warmup_and_smoothing():
    """ATR must be NaN during warm-up and positive+finite after period-1 bars."""
    close = pd.Series(
        [100, 101, 99, 102, 103, 101, 104, 106, 105, 107, 108, 110],
        index=pd.date_range("2020-01-01", periods=12), dtype=float,
    )
    high = close + 1.0
    low = close - 1.0
    atr = compute_atr_wilder_daily(high, low, close, period=5)
    # First 4 values NaN (warmup = period - 1 = 4).
    assert atr.iloc[:4].isna().all()
    # Bar 4 onward should be finite, positive.
    assert np.isfinite(atr.iloc[4:]).all()
    assert (atr.iloc[4:] > 0).all()
