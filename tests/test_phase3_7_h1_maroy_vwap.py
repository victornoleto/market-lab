"""Smoke tests for Phase 3.7 H1.b Maróy-VWAP intraday strategy.

Scope: verify (1) engine produces a MaroyVwapResult with sane invariants on
a tiny synthetic 1-min fixture, and (2) the prev_weight × ret alignment
has zero look-ahead (today's entry cannot earn today's bar return).

Keep fast: these are smoke tests, not the full 13-gate pipeline (which
runs via ``scripts/phase3_7/run_h1_maroy_vwap.py`` and takes ~60s).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.phase3_7_h1_maroy_vwap import (
    MaroyVwapConfig,
    MaroyVwapResult,
    simulate_h1_maroy_vwap,
)


def _make_synthetic_1min(
    n_days: int = 30, bars_per_day: int = 60, seed: int = 7
) -> pd.DataFrame:
    """Create an OHLC 1-min fixture over ``n_days`` regular-session days.

    Uses a small GBM with intraday drift toggled by day parity so both
    upper and lower noise-boundary branches get exercised.
    """
    rng = np.random.default_rng(seed)
    rows = []
    base = 100.0
    start = pd.Timestamp("2020-01-06 14:30:00", tz="UTC")  # Monday 9:30 ET
    for d in range(n_days):
        day_start = start + pd.Timedelta(days=d)
        if day_start.tz_convert("America/New_York").weekday() >= 5:
            continue
        drift_sign = 1.0 if d % 2 == 0 else -1.0
        sigma = 0.0008
        mu = 0.00005 * drift_sign
        c_prev = base
        for b in range(bars_per_day):
            ts = day_start + pd.Timedelta(minutes=b)
            ret = rng.normal(mu, sigma)
            c_new = c_prev * (1 + ret)
            h = max(c_prev, c_new) * (1 + abs(rng.normal(0, sigma / 2)))
            l_ = min(c_prev, c_new) * (1 - abs(rng.normal(0, sigma / 2)))
            rows.append((ts, c_prev, h, l_, c_new))
            c_prev = c_new
        base = c_prev
    df = pd.DataFrame(
        rows, columns=["ts", "open", "high", "low", "close"]
    ).set_index("ts")
    return df


def test_simulate_returns_result_with_clean_invariants():
    df = _make_synthetic_1min(n_days=40, bars_per_day=60)
    cfg = MaroyVwapConfig(ma_lookback_days=5, min_bar_idx_for_entry=1)
    res = simulate_h1_maroy_vwap(df, cfg)

    assert isinstance(res, MaroyVwapResult)
    # Daily returns: one per trading day present in the fixture
    assert isinstance(res.daily_returns, pd.Series)
    assert len(res.daily_returns) > 0, "expected at least one daily return"
    # No nan in daily returns
    assert res.daily_returns.isna().sum() == 0
    # Positions take values in {-1, 0, 1}
    pos_vals = np.unique(res.positions.to_numpy())
    assert set(pos_vals.tolist()).issubset({-1.0, 0.0, 1.0})
    # n_trades non-negative; at least one trade on a 40-day fixture
    assert res.n_trades > 0
    # Cumulative spread cost ≥ 0
    assert res.cum_spread_pct >= 0


def test_flat_at_close_means_no_overnight_carry():
    """With flat_at_close=True, the first bar of each subsequent day
    must have zero prev-bar contribution (no overnight carry).

    The ``positions`` series records the weight HELD DURING each bar
    (which earns that bar's return via prev_weight × ret at the next
    step). Flat-at-close means the weight held during the LAST bar of
    day d is realized, cost is paid to close, and the FIRST bar of
    day d+1 starts from zero regardless of what day d ended with.

    This test verifies the no-overnight-carry invariant: for every
    first-bar-of-day (other than the first day), the 'effective
    prev-bar position crossing the day boundary' is zero — i.e., the
    strategy does not earn day d+1's first-bar return from day d's
    position.
    """
    df = _make_synthetic_1min(n_days=20, bars_per_day=60)
    cfg = MaroyVwapConfig(
        ma_lookback_days=3, flat_at_close=True, min_bar_idx_for_entry=1
    )
    res = simulate_h1_maroy_vwap(df, cfg)

    idx_et = res.positions.index.tz_convert("America/New_York")
    date_v = np.array(list(idx_et.date))
    pos = res.positions.to_numpy()
    # First bar of a new day: where date differs from previous.
    new_day = np.concatenate([[True], date_v[1:] != date_v[:-1]])
    # On a new-day bar, the per_bar return should equal prev_weight × ret,
    # where prev_weight across a day boundary is forced to 0 by construction.
    # Equivalently: for any new-day bar i, the contribution
    #   per_bar_returns[i] = (0 or -cost_if_entry_flag) only; it cannot
    # have earned the prior day's final-bar position's overnight move.
    per_bar = res.per_bar_returns.to_numpy()

    # A bar that is (a) first of day AND (b) no entry flag should have
    # per_bar_returns == 0 exactly (no gross ret, no cost).
    # We reconstruct entry_flag as "prev-same-day pos was 0 and this bar
    # has pos != 0".
    same_day = np.concatenate([[False], date_v[1:] == date_v[:-1]])
    prev_pos = np.concatenate([[0.0], pos[:-1]])
    prev_pos_sd = np.where(same_day, prev_pos, 0.0)
    entry_flag = (prev_pos_sd == 0.0) & (pos != 0.0)

    first_bar_noentry = new_day & ~entry_flag
    assert np.allclose(per_bar[first_bar_noentry], 0.0, atol=1e-12), (
        "new-day bar without entry earned non-zero return (overnight carry bug)"
    )


def test_prev_weight_times_ret_has_no_lookahead():
    """Today's entry bar must not earn today's bar return on that bar.

    Invariant: if an entry flag fires at bar t (position flips 0 → ±1),
    then the bar's contribution to per_bar_returns comes from
    prev_weight × bar_ret = 0 × bar_ret_t minus the flip cost
    = -spread. So per_bar_returns[t] at an entry bar with no prior
    position must be ≤ 0 (purely the cost). This is the AFML p.31-34
    alignment contract.
    """
    df = _make_synthetic_1min(n_days=30, bars_per_day=60)
    cfg = MaroyVwapConfig(ma_lookback_days=5, min_bar_idx_for_entry=1)
    res = simulate_h1_maroy_vwap(df, cfg)

    # An entry bar is where position jumps from 0 to ±1 (prev bar in
    # same day, or new day). Check per_bar_returns on those bars ≤ 0
    # within numerical tolerance (they reflect only the spread cost).
    pos = res.positions.to_numpy()
    per_bar = res.per_bar_returns.to_numpy()
    idx_et = res.positions.index.tz_convert("America/New_York")
    date_v = np.array(list(idx_et.date))
    same_day = np.concatenate([[False], date_v[1:] == date_v[:-1]])

    # prev_pos_same_day: pos[t-1] if same day else 0
    prev_pos = np.concatenate([[0.0], pos[:-1]])
    prev_pos_sd = np.where(same_day, prev_pos, 0.0)

    entry_bars = (prev_pos_sd == 0.0) & (pos != 0.0)
    # On entry bars, per_bar_returns ≤ 0 (only the cost, no gross PnL).
    if entry_bars.any():
        assert (per_bar[entry_bars] <= 1e-9).all(), (
            "entry bar earned positive per-bar return (look-ahead bug)"
        )
