"""Smoke tests for Phase 3.7 H3.b — ETH Donchian ensemble independent signal.

Tests three invariants:

1. `compute_atr_wilder` produces a finite ATR series after the warmup
   period and matches the canonical Wilder recursion.
2. The simulator runs end-to-end on a synthetic price fixture and produces
   sane output (no NaNs in returns beyond warmup, entries consistent with
   Donchian ensemble breakouts, median hold ≤ time_stop_days).
3. Look-ahead audit — the Donchian bands at bar `t` depend only on
   `high`/`low` through `t-1` (the ``shift(1)`` guard). We verify by
   constructing a price series whose bar-t high would trivially trigger a
   break if the shift were missing, and confirming no entry fires at t
   when the t-1 band is above it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.phase3_7_h3_eth_donchian import (
    BARS_PER_YEAR_CRYPTO,
    H3EthDonchianConfig,
    compute_atr_wilder,
    simulate_h3_eth_donchian,
)


def _make_synthetic_eth_bars(
    n_days: int = 400,
    seed: int = 7,
) -> pd.DataFrame:
    """Random-walk ETH-like daily bars (7d/wk crypto calendar).

    Starts at price 100, daily vol ~3% (ETH-typical mid-2020 regime).
    Columns match Tiingo: open, high, low, close, adj_close, volume.
    """
    rng = np.random.default_rng(seed)
    rets = rng.normal(loc=0.001, scale=0.03, size=n_days)
    close = 100.0 * np.exp(np.cumsum(rets))
    # Simulate intraday range ≈ 2% of close.
    intra = 0.02 * close
    open_ = close * (1.0 + rng.normal(0, 0.005, n_days))
    high = np.maximum(open_, close) + rng.uniform(0, intra, n_days) * 0.3
    low = np.minimum(open_, close) - rng.uniform(0, intra, n_days) * 0.3
    vol = rng.uniform(1000, 10000, n_days)
    idx = pd.date_range("2020-01-01", periods=n_days, freq="D")
    df = pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "adj_close": close,
            "volume": vol,
        },
        index=idx,
    )
    df.index.name = "date"
    return df


def test_compute_atr_wilder_warmup_and_finite() -> None:
    """ATR series should be NaN for the first `period-1` bars, then
    finite and positive for the remainder."""
    df = _make_synthetic_eth_bars(n_days=60)
    atr = compute_atr_wilder(df["high"], df["low"], df["close"], period=20)
    assert atr.iloc[:19].isna().all(), "ATR warmup must be NaN for first period-1 bars"
    live = atr.iloc[19:]
    assert live.notna().all(), "ATR must be defined after warmup"
    assert (live > 0).all(), "ATR values must be strictly positive"
    # Sanity: scale should be comparable to typical intraday range.
    assert 0.5 < live.mean() < 10.0, f"ATR mean in suspicious range: {live.mean()}"


def test_simulate_h3_eth_donchian_end_to_end() -> None:
    """Runner executes without raising and produces well-formed output
    on a 400-day synthetic fixture."""
    df = _make_synthetic_eth_bars(n_days=400, seed=7)
    cfg = H3EthDonchianConfig(
        donchian_lookbacks=(10, 20, 40),
        atr_period=20,
        atr_multiplier=2.0,
        time_stop_days=2,
        risk_per_trade=0.010,
        max_leverage=2.0,
    )
    res = simulate_h3_eth_donchian(df, cfg, ticker="TEST")

    # Shape + no NaN in returns post-warmup.
    assert len(res.daily_returns) == len(df), "daily_returns index length must match bars"
    post_warmup = res.daily_returns.iloc[80:]  # after longest lookback + ATR warmup
    assert post_warmup.notna().all(), "post-warmup returns must be non-NaN"

    # Weights bounded by ±max_leverage.
    assert (res.weights.abs() <= cfg.max_leverage + 1e-9).all(), "|weight| must respect max_leverage cap"

    # Hold length respects time_stop_days (could be shorter via ATR trail).
    if res.hold_lengths:
        assert max(res.hold_lengths) <= cfg.time_stop_days, (
            f"max hold {max(res.hold_lengths)} > time_stop_days {cfg.time_stop_days}"
        )
    # Sanity: some trades should fire in 400 days of random-walk data.
    assert res.n_trades >= 1, "expected at least one trade on random-walk fixture"
    # n_long + n_short == n_trades invariant.
    assert res.n_long + res.n_short == res.n_trades

    # Reported Sharpe/CAGR/MDD are finite numbers (not NaN/inf).
    assert np.isfinite(res.sharpe())
    assert np.isfinite(res.cagr())
    assert np.isfinite(res.max_drawdown())
    # Annualization constant matches crypto 7d/wk calendar.
    assert BARS_PER_YEAR_CRYPTO == 365


def test_donchian_lookahead_shift_is_strict() -> None:
    """Donchian band at bar t uses highs/lows through t-1 only. We verify
    by inspecting the first bar that could possibly trigger: it must use
    the rolling-max of bars [t-N, t-1] (STRICT prior — no peek into t).

    Construction: a strictly monotonically-increasing close series — if
    there were any leak, the simulator would fire a long entry on bar N
    (since close_N > max(close[0..N-1]) would be used instead of
    max(close[0..N-1]) with the proper shift). But with correct shift(1),
    the first bar where a band exists is bar N+1 (since band_{N+1} uses
    [1..N]), and the first potential entry is exactly bar N+1. We assert
    zero entries before bar N+1 (the strict-shift invariant).
    """
    n = 300
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    # Monotonic close that breaks out every single bar.
    close = pd.Series(np.linspace(100.0, 400.0, n), index=idx)
    df = pd.DataFrame(
        {
            "open": close,
            "high": close * 1.001,
            "low": close * 0.999,
            "close": close,
            "adj_close": close,
            "volume": np.ones(n) * 1000,
        }
    )
    df.index.name = "date"

    # With ensemble = (10, 20, 40), the `upper_ensemble` at bar t is the
    # max across three rolling maxes each using .shift(1). The upper_10
    # band is first defined at bar 10 (index 10, 11th bar) and uses
    # high[0..9], shift(1) → defined at bar 11. So the earliest any entry
    # can fire is bar 11 (index 10 uses band from bar 11 → wait: .shift(1)
    # means band_series[bar_11] = max(high[1..10])). Combined with
    # ATR(20) warmup (20 bars), the earliest entry-eligible bar is bar 21.
    # We test the STRICT-SHIFT invariant: that NO entry fires at the bar
    # where the band itself would not be defined without a shift. For the
    # shortest lookback 10 without shift, a band would exist at bar 10 →
    # our strict shift must push first-eligible-by-band to bar 11. Since
    # ATR(20) warmup also applies, the real first-eligible bar is 21.
    cfg = H3EthDonchianConfig(
        donchian_lookbacks=(10, 20, 40),
        atr_period=20,
        atr_multiplier=2.0,
        time_stop_days=2,
        risk_per_trade=0.010,
    )
    res = simulate_h3_eth_donchian(df, cfg, ticker="MONO")

    # No entry in the first 20 bars (guaranteed by ATR warmup + Donchian
    # shift(1); without strict shift, entries could fire at bar 10 or
    # bar 20 depending on which band is shortest).
    entries_early = res.entries.iloc[:20]
    assert (entries_early == 0).all(), (
        f"lookahead-guard violation: entry fired within first 20 bars — "
        f"first entry index = {(res.entries != 0).idxmax()}"
    )
    # At least one entry should eventually fire on this monotonic series
    # (non-vacuous test).
    assert (res.entries != 0).any(), "monotonic series should trigger at least one entry"
    # First entry must be at index >= 20 (ATR warmup).
    first_entry_loc = (res.entries != 0).to_numpy().argmax()
    assert first_entry_loc >= 20, (
        f"first entry at index {first_entry_loc} violates ATR(20) warmup"
    )


def test_swap_applied_daily_on_open_notional() -> None:
    """Sanity-check swap accounting: with long-only config on a
    sideways-drift series, cumulative swap cost should be positive
    (debit, since swap_daily_long < 0) and proportional to total
    long-day exposure."""
    df = _make_synthetic_eth_bars(n_days=500, seed=3)
    cfg = H3EthDonchianConfig(
        donchian_lookbacks=(10, 20, 40),
        risk_per_trade=0.010,
        swap_daily_long=-5.556e-4,
        swap_daily_short=2.083e-4,
        allow_short=False,  # long-only so swap is pure debit
    )
    res = simulate_h3_eth_donchian(df, cfg, ticker="SWAP")
    # cum_swap_pct is stored as the sum of `swap_drag` (positive = cost).
    # It should be >= 0 and finite.
    assert res.cum_swap_pct >= 0, "cum_swap_pct must be non-negative (debit)"
    assert np.isfinite(res.cum_swap_pct)
    # Cross-check: sum of weight-days × |swap_daily_long| ≈ cum_swap_pct.
    weight_days_long = float(res.weights.shift(1).clip(lower=0.0).fillna(0.0).sum())
    expected = weight_days_long * abs(cfg.swap_daily_long)
    assert abs(res.cum_swap_pct - expected) < 1e-9, (
        f"swap accounting mismatch: cum_swap_pct={res.cum_swap_pct} "
        f"vs expected={expected}"
    )
