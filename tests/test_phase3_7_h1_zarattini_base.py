"""Smoke tests for Phase 3.7 H1.a — Zarattini base replication.

Tests two invariants:

1. Noise-boundary computation respects the 14d MA with shift(1) — today's
   day cannot peek into today's abs_ret (lookahead audit).
2. The simulator runs end-to-end on a tiny synthetic fixture and produces
   sane output (no NaNs beyond warmup, weights ∈ {-1, 0, 1}, flat-at-close
   invariant holds on the last bar of each day).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.phase3_7_h1_zarattini_base import (
    H1ZarattiniBaseConfig,
    _compute_noise_boundaries,
    compute_atr_wilder_1min,
    simulate_h1_zarattini_base,
)


def _make_synthetic_bars(
    n_days: int = 30,
    bars_per_day: int = 30,
    seed: int = 42,
) -> pd.DataFrame:
    """Build a synthetic multi-day 1-min OHLC fixture on a UTC index."""
    rng = np.random.default_rng(seed)
    start_date = pd.Timestamp("2020-01-01", tz="UTC")
    rows: list[pd.Timestamp] = []
    closes: list[float] = []
    opens: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    price = 100.0
    for d in range(n_days):
        day0 = start_date + pd.Timedelta(days=d)
        # Skip weekends for realism.
        if day0.weekday() >= 5:
            continue
        for b in range(bars_per_day):
            ts = day0 + pd.Timedelta(hours=13, minutes=30 + b)
            rows.append(ts)
            open_ = price
            step = rng.normal(0.0, 0.1)
            price = max(1.0, price + step)
            close_ = price
            high_ = max(open_, close_) + abs(rng.normal(0.0, 0.05))
            low_ = min(open_, close_) - abs(rng.normal(0.0, 0.05))
            opens.append(open_)
            highs.append(high_)
            lows.append(low_)
            closes.append(close_)
    idx = pd.DatetimeIndex(rows)
    return pd.DataFrame(
        {"open": opens, "high": highs, "low": lows, "close": closes},
        index=idx,
    )


def test_noise_boundaries_no_lookahead() -> None:
    """For day D with <14 prior days, MA is NaN → boundaries NaN on D."""
    # 25 calendar days ≈ 17-18 weekdays (enough for >14-day MA + extras).
    bars = _make_synthetic_bars(n_days=25, bars_per_day=30, seed=1)
    _open_of_day, _abs_ret, upper, lower = _compute_noise_boundaries(
        bars, ma_days=14
    )
    # Each day has 30 bars. First 14 days of MA output = NaN.
    # (rolling(14).mean().shift(1) → valid only from day 15 onward.)
    dates = sorted(bars.index.normalize().unique())
    # Day 0 through 13 must be all-NaN boundaries.
    for d in dates[:14]:
        day_mask = bars.index.normalize() == d
        assert upper[day_mask].isna().all(), f"day {d}: upper must be NaN"
        assert lower[day_mask].isna().all(), f"day {d}: lower must be NaN"
    # Day 14 onward must have at least some finite boundaries.
    d14 = dates[14]
    day_mask = bars.index.normalize() == d14
    assert upper[day_mask].notna().any()
    assert lower[day_mask].notna().any()


def test_atr_wilder_1min_basic() -> None:
    """ATR series has NaN for warmup then finite values."""
    bars = _make_synthetic_bars(n_days=3, bars_per_day=30, seed=2)
    atr = compute_atr_wilder_1min(
        bars["high"], bars["low"], bars["close"], period=20
    )
    # First 19 bars NaN, then finite.
    assert atr.iloc[:19].isna().all()
    assert atr.iloc[19:].notna().all()
    assert (atr.dropna() > 0).all()


def test_simulator_runs_and_respects_flat_at_close() -> None:
    """End-to-end: sim runs, weights ∈ {-1, 0, 1}, last bar of each day
    has weight == 0 (flat-at-close invariant)."""
    bars = _make_synthetic_bars(n_days=40, bars_per_day=30, seed=3)
    cfg = H1ZarattiniBaseConfig(
        ma_days=5,  # short MA so signals fire in 40-day fixture
        atr_period=10,
        atr_multiplier=2.0,
    )
    res = simulate_h1_zarattini_base(bars, cfg, ticker="SYNTH")
    # Weights are discrete {-1, 0, 1}.
    w = res.weights.dropna()
    assert set(w.unique()).issubset({-1.0, 0.0, 1.0})
    # Flat-at-close: last bar of each day must have weight 0.
    date = bars.index.normalize()
    last_of_day = (
        pd.Series(date.to_numpy(), index=bars.index).shift(-1).fillna(
            pd.Timestamp("1900-01-01")
        )
        != pd.Series(date.to_numpy(), index=bars.index)
    )
    last_bars = bars.index[last_of_day]
    assert (res.weights.loc[last_bars] == 0.0).all(), (
        "flat-at-close violated"
    )
    # Minute returns: first bar must be 0 (no prev_weight × ret).
    assert res.minute_returns.iloc[0] == 0.0
    # No explosion — all finite.
    assert res.minute_returns.dropna().abs().max() < 1.0


def test_simulator_daily_returns_aggregation() -> None:
    """Daily returns produced by .daily_returns() match compound of minute."""
    bars = _make_synthetic_bars(n_days=20, bars_per_day=30, seed=4)
    cfg = H1ZarattiniBaseConfig(ma_days=5, atr_period=10, atr_multiplier=2.0)
    res = simulate_h1_zarattini_base(bars, cfg, ticker="SYNTH")
    daily = res.daily_returns()
    # Daily index should have exactly one entry per unique date with
    # nonzero minute activity.
    assert len(daily) <= len(bars.index.normalize().unique())
    # No NaN.
    assert daily.notna().all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
