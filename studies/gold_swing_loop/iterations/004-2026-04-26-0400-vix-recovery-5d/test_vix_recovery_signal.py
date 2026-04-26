"""TDD tests for `vix_recovery_signal` — iter 004.

Strategy: long gold for fixed 5 trading days when VIX z-score crosses
*down* through +1 from above, with a recent (≤30 d) peak > +2σ. After
exit, a 10-day cooldown blocks new entries.

Citations
---------
* `[leverage_for_the_long_run, p.13]` — Gayed VIX flight-to-quality regime
* `[advances_fin_ml, p.31-34]` — verifying simulator behavior in tests first
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))

from run_backtest import vix_recovery_signal, vix_zscore  # noqa: E402


def _ohlc(values: list[float], start: str = "2020-01-06") -> pd.DataFrame:
    """Build a daily-business-day OHLC dataframe from a close series."""
    idx = pd.date_range(start=start, periods=len(values), freq="B")
    s = pd.Series(values, index=idx, dtype=float)
    return pd.DataFrame({"open": s, "high": s, "low": s, "close": s,
                         "adj_close": s, "volume": 0.0})


def test_zscore_warmup_returns_nan_before_lookback():
    """First (lookback - 1) bars of z-score must be NaN (insufficient data)."""
    n = 80
    rng = np.random.default_rng(0)
    vix = pd.Series(15.0 + rng.normal(0, 3, size=n),
                    index=pd.date_range("2020-01-01", periods=n, freq="B"))
    z = vix_zscore(vix, lookback=60)
    assert z.iloc[:59].isna().all(), "z-score must be NaN during warmup"
    assert z.iloc[59:].notna().all(), "z-score must be defined after warmup"


def test_position_values_are_binary_long_only():
    """Position must be in {0, 1}; never short, never fractional."""
    rng = np.random.default_rng(1)
    n = 400
    rets = rng.normal(0.0005, 0.012, size=n)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _ohlc(list(close))
    vix = pd.Series(15.0 + rng.normal(0, 5, size=n),
                    index=df.index).clip(lower=8.0)

    pos = vix_recovery_signal(df, vix)
    unique = set(pos.unique().tolist())
    assert unique.issubset({0.0, 1.0}), f"position must be {{0,1}}; got {unique}"


def test_no_entry_during_zscore_warmup():
    """No entry can fire before z-score is defined (first 60 bars)."""
    rng = np.random.default_rng(2)
    n = 200
    rets = rng.normal(0.0005, 0.012, size=n)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _ohlc(list(close))
    # Construct VIX that would TRIGGER aggressively if z-score were defined
    # (huge swings) but the warmup must still hold.
    vix_vals = np.concatenate([
        np.full(30, 50.0),  # high
        np.full(30, 10.0),  # low (would create big z-swing)
        np.full(140, 20.0),
    ])
    vix = pd.Series(vix_vals, index=df.index)

    pos = vix_recovery_signal(df, vix, zscore_lookback=60)
    assert (pos.iloc[:60] == 0).all(), "entries fired during z-score warmup"


def test_holds_for_exactly_hold_days_after_trigger():
    """A trigger must produce hold_days consecutive 1s, then return to 0."""
    # Construct a VIX path that:
    #   - 60 days flat ~15 (warmup)
    #   - jump to 40 for 5 days (z spike well above +2σ)
    #   - drop to 14 (z back below +1) at day 70 → this is the trigger bar
    n = 120
    vix_vals = np.concatenate([
        np.full(60, 15.0),    # warmup
        np.full(5, 40.0),     # spike (creates big peak in z)
        np.full(55, 14.0),    # collapse (z down-cross +1 happens at first low bar)
    ])
    rng = np.random.default_rng(3)
    rets = rng.normal(0.0, 0.001, size=n)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _ohlc(list(close))
    vix = pd.Series(vix_vals, index=df.index)

    pos = vix_recovery_signal(
        df, vix,
        z_peak_threshold=2.0, z_exit_threshold=1.0,
        peak_window=30, hold_days=5, cooldown_days=10,
        zscore_lookback=60,
    )
    # Find first bar where position becomes 1
    first_long = int(np.argmax(pos.values > 0))
    assert pos.iloc[first_long] == 1.0
    assert first_long >= 60, "entry fired before warmup completed"
    # Next 5 bars (including first_long) must all be 1, then 0 immediately after
    assert (pos.iloc[first_long:first_long + 5] == 1).all(), \
        f"hold did not last 5 bars from {first_long}"
    if first_long + 5 < n:
        assert pos.iloc[first_long + 5] == 0.0, "position did not exit at T+5"


def test_cooldown_blocks_immediate_retrigger():
    """A second trigger within `cooldown_days` of an exit must NOT enter."""
    # VIX path:
    #   - 60 d flat (warmup)
    #   - 65: spike to 40 for 3 days
    #   - 68: drop to 14 → first trigger
    #   - 73: trade exits (after 5d hold)
    #   - 75: another spike (3 days)
    #   - 78: drop to 14 → would trigger but cooldown=10 still active
    #   - 83: cooldown ends; another spike+drop → re-eligible
    n = 200
    vix_vals = np.full(n, 14.0)
    vix_vals[:60] = 15.0           # warmup
    vix_vals[60:65] = 40.0         # 1st spike
    # 65 onwards stays at 14 → 1st trigger at bar 65 (z down-cross from spike)
    vix_vals[80:83] = 40.0         # 2nd spike (within cooldown of trade [65-69])
    # Should NOT trigger at 83 (cooldown blocks)
    rng = np.random.default_rng(4)
    rets = rng.normal(0.0, 0.001, size=n)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _ohlc(list(close))
    vix = pd.Series(vix_vals, index=df.index)

    pos = vix_recovery_signal(
        df, vix,
        z_peak_threshold=2.0, z_exit_threshold=1.0,
        peak_window=30, hold_days=5, cooldown_days=20,  # extra-long cooldown
        zscore_lookback=60,
    )

    # Identify trade start indices
    diffs = pos.diff().fillna(pos.iloc[0])
    starts = list(np.where(diffs.values == 1)[0])
    assert len(starts) >= 1, "no trades entered"
    if len(starts) >= 2:
        gap = starts[1] - starts[0]
        # Trade exit is at start+5; cooldown_days=20 → next eligible at start+25
        assert gap >= 5 + 20, \
            f"cooldown failed: 2nd trigger only {gap} bars after 1st (need ≥25)"


def test_requires_recent_peak_for_trigger():
    """A VIX z down-cross of +1 with NO peak > +2σ in the last `peak_window`
    days must NOT trigger an entry (the recovery context is missing)."""
    n = 250
    # Construct VIX that oscillates within ±1.5σ but never spikes above 2σ.
    # Result: z-score mostly stays in [-1.5, +1.5]; many crosses of ±1 happen
    # but no peak triggers.
    rng = np.random.default_rng(5)
    base = 18.0
    noise = rng.normal(0.0, 1.5, size=n)  # std ~1.5 in raw VIX terms
    vix_vals = np.clip(base + noise, 8.0, 50.0)
    # Sanity check: z-score should not exceed +2 for sustained periods
    rets = rng.normal(0.0, 0.001, size=n)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _ohlc(list(close))
    vix = pd.Series(vix_vals, index=df.index)

    z = vix_zscore(vix, lookback=60)
    # Verify the synthetic does not produce sustained z>2 (test setup integrity)
    assert (z[60:].max() < 3.0), "synthetic test failure: z exceeded 3σ"

    pos = vix_recovery_signal(
        df, vix,
        z_peak_threshold=2.0, z_exit_threshold=1.0,
        peak_window=30, hold_days=5, cooldown_days=10,
        zscore_lookback=60,
    )
    # If max z never reached +2, no trigger should fire (peak gate fails)
    if z[60:].max() <= 2.0:
        assert (pos == 0).all(), \
            "trigger fired even though no peak > 2σ existed in the window"


def test_no_lookahead_position_only_uses_past_or_current():
    """Truncating the dataframe at any t must not change pos[≤t-1]."""
    rng = np.random.default_rng(6)
    n = 200
    # Use a VIX path that produces some trades, otherwise the assertion is empty
    vix_vals = np.full(n, 15.0)
    vix_vals[80:85] = 35.0
    vix_vals[85:200] = 14.0
    rets = rng.normal(0.0, 0.001, size=n)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _ohlc(list(close))
    vix = pd.Series(vix_vals, index=df.index)

    pos_full = vix_recovery_signal(df, vix)
    pos_trunc = vix_recovery_signal(df.iloc[:150], vix.iloc[:150])
    np.testing.assert_array_equal(pos_full.iloc[:150].values, pos_trunc.values)


def test_vix_index_misalignment_is_forward_filled():
    """If VIX is missing some gold trading days (calendar mismatch), the
    function must forward-fill VIX onto the gold index without raising."""
    n_gold = 150
    rng = np.random.default_rng(7)
    rets = rng.normal(0.0, 0.001, size=n_gold)
    close = 100.0 * np.exp(np.cumsum(rets))
    df = _ohlc(list(close))

    # VIX is sparser than gold (every other day)
    vix_idx = df.index[::2]
    vix = pd.Series(np.full(len(vix_idx), 15.0), index=vix_idx)

    pos = vix_recovery_signal(df, vix)
    assert len(pos) == len(df), "output index must match the price df index"
    assert (pos >= 0).all() and (pos <= 1).all()
