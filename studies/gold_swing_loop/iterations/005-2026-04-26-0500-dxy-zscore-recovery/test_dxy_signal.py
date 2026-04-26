"""TDD tests for iter 005 — DXY z-score down-cross + 5-d fixed hold.

Three primitives are unit-tested before being wired into the full
backtest:

1. ``compute_dxy_proxy`` — equal-weighted log basket of usdcad/usdchf/
   usdjpy, formula: ``(log(usdcad) + log(usdchf) + log(usdjpy)) / 3``.
2. ``compute_zscore`` — rolling z-score with 60-bar window; NaN
   warmup; first valid bar at index 60.
3. ``dxy_downcross_signal`` — state machine: when z down-crosses
   through ``z_threshold`` from above (z[t] < threshold AND
   z[t-1] >= threshold), open long for ``hold_days``, then enforce
   ``cooldown_days`` cooldown before next eligibility. Long-only,
   binary {0, 1}.

Citations
---------
* `[advances_fin_ml, p.31-34]` — verifying simulator behavior in
  tests first
* `[ilmanen_expected_returns, ch.10]` — DXY proxy basket motivation
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))

from run_backtest import (  # noqa: E402
    compute_dxy_proxy,
    compute_zscore,
    dxy_downcross_signal,
)


def _idx(n: int, start: str = "2020-01-01") -> pd.DatetimeIndex:
    return pd.date_range(start=start, periods=n, freq="B")


def test_dxy_proxy_formula_equal_weighted_log_basket():
    """Verify the formula: mean(log(usdcad), log(usdchf), log(usdjpy))."""
    idx = _idx(5)
    usdcad = pd.Series([1.30, 1.31, 1.32, 1.31, 1.30], index=idx)
    usdchf = pd.Series([0.90, 0.91, 0.92, 0.91, 0.90], index=idx)
    usdjpy = pd.Series([110.0, 111.0, 112.0, 111.0, 110.0], index=idx)

    proxy = compute_dxy_proxy(usdcad, usdchf, usdjpy)

    expected = (np.log(usdcad) + np.log(usdchf) + np.log(usdjpy)) / 3.0
    pd.testing.assert_series_equal(
        proxy, expected, check_names=False, check_exact=False, rtol=1e-12
    )


def test_dxy_proxy_aligns_on_inner_join_dates():
    """Inputs with mismatched indices must inner-join (drop non-common dates)."""
    idx_a = _idx(10, start="2020-01-01")
    idx_b = _idx(10, start="2020-01-03")  # shifted +2 BD
    usdcad = pd.Series(np.linspace(1.30, 1.40, 10), index=idx_a)
    usdchf = pd.Series(np.linspace(0.90, 0.95, 10), index=idx_b)
    usdjpy = pd.Series(np.linspace(110.0, 115.0, 10), index=idx_a)

    proxy = compute_dxy_proxy(usdcad, usdchf, usdjpy)

    # Inner-join must be the intersection of all 3 indices:
    expected_idx = idx_a.intersection(idx_b)
    assert proxy.index.equals(expected_idx), \
        f"proxy index does not match inner-join; got {proxy.index}"
    # And no NaNs in the result
    assert not proxy.isna().any(), "proxy contains NaN after inner-join"


def test_zscore_uses_rolling_60_warmup():
    """First 59 bars are NaN; bar 60 (0-indexed: 59) is the first finite z."""
    n = 100
    rng = np.random.default_rng(0)
    s = pd.Series(rng.normal(0.0, 1.0, size=n), index=_idx(n))

    z = compute_zscore(s, lookback=60)

    # First 59 bars (indices 0..58) must be NaN; bar at index 59 is the
    # first valid z (60-bar rolling window completed).
    assert z.iloc[:59].isna().all(), "z-score has non-NaN values before warmup"
    assert not np.isnan(z.iloc[59]), "z-score is still NaN at first valid bar"


def test_zscore_value_at_known_point():
    """Verify the z-score formula on a deterministic linear series.

    For a linear ramp s[i] = i, the rolling 60-bar mean at i=59 is
    sum(0..59)/60 = 29.5; the rolling std uses ddof=0 (population) by
    pandas default, so std = sqrt(sum((i-29.5)^2)/60). z[59] = (59 - 29.5)
    / std.
    """
    s = pd.Series(np.arange(60, dtype=float), index=_idx(60))

    z = compute_zscore(s, lookback=60)

    rolling_mean = s.rolling(60, min_periods=60).mean().iloc[-1]
    rolling_std = s.rolling(60, min_periods=60).std(ddof=0).iloc[-1]
    expected_z = (s.iloc[-1] - rolling_mean) / rolling_std
    assert abs(z.iloc[-1] - expected_z) < 1e-10, \
        f"z[59]={z.iloc[-1]:.6f} vs expected {expected_z:.6f}"


def test_downcross_fires_once_at_cross_bar():
    """Manufactured z series with one explicit down-cross through −1.

    Place z = [0.5, 0.0, -0.5, -1.5, -2.0, -1.5, -0.5, 0.0, ...] starting
    at bar 60 (post-warmup). Down-cross is between bar 62 (z=-0.5) and
    bar 63 (z=-1.5): z[63] < -1 AND z[62] >= -1.

    Strategy: trigger at bar 63 → position[63..67] = 1 (5-day hold);
    cooldown bars 68..72 = 0; eligible again at bar 73.
    """
    # Synthetic z-score series; we'll mock compute_zscore via direct
    # injection by passing a pre-computed z to the state machine.
    n = 100
    z = pd.Series(np.zeros(n), index=_idx(n))
    # Pre-warmup: z is NaN
    z.iloc[:60] = np.nan
    # Post-warmup: deterministic pattern with one cross at index 63
    z.iloc[60] = 0.5
    z.iloc[61] = 0.0
    z.iloc[62] = -0.5
    z.iloc[63] = -1.5    # CROSS — z went from -0.5 → -1.5
    z.iloc[64] = -2.0
    z.iloc[65] = -1.5
    z.iloc[66] = -0.5
    z.iloc[67] = 0.0
    z.iloc[68:] = 0.5

    pos = dxy_downcross_signal(
        z, z_threshold=-1.0, hold_days=5, cooldown_days=5,
    )

    # Pre-warmup: position must be 0 (no z, no entry)
    assert (pos.iloc[:63] == 0).all(), "position fired before the cross bar"
    # Hold period: bars 63..67 inclusive = 5 bars long
    assert (pos.iloc[63:68] == 1).all(), \
        f"hold period not all 1: {pos.iloc[63:68].values}"
    # Cooldown: bars 68..72 = 0
    assert (pos.iloc[68:73] == 0).all(), \
        f"cooldown not all 0: {pos.iloc[68:73].values}"
    # No further triggers in this synthetic (z stays at +0.5)
    assert (pos.iloc[73:] == 0).all(), "spurious trigger after cooldown"


def test_no_re_entry_during_hold_or_cooldown():
    """If z stays below −1 across multiple bars, only the first cross fires.

    Build z = [+0.5, +0.5, ..., −1.5, −1.5, ..., −1.5] with z dropping
    below −1 at exactly bar 63 and STAYING below −1 for many bars. The
    state machine must enter once at bar 63, hold 5 days, cool down 5
    days, and only then become eligible again.
    """
    n = 100
    z = pd.Series(np.full(n, 0.5), index=_idx(n))
    z.iloc[:60] = np.nan
    z.iloc[60:63] = 0.5   # above −1
    z.iloc[63:] = -1.5    # below −1 forever

    pos = dxy_downcross_signal(
        z, z_threshold=-1.0, hold_days=5, cooldown_days=5,
    )

    # First entry: bars 63..67 (5-day hold)
    assert (pos.iloc[63:68] == 1).all(), "first hold period not all 1"
    # Cooldown: bars 68..72 (5-day cooldown)
    assert (pos.iloc[68:73] == 0).all(), "cooldown period not all 0"
    # After cooldown: z is still below −1 but z[t-1] is also below −1,
    # so the cross condition (z[t] < −1 AND z[t-1] >= −1) is FALSE at
    # bar 73 → no re-entry. Position must stay at 0 for the remainder.
    assert (pos.iloc[73:] == 0).all(), \
        "spurious re-entry after cooldown when no fresh down-cross"


def test_position_is_binary_long_only():
    """Position values must be in {0.0, 1.0}; never short, never fractional."""
    rng = np.random.default_rng(7)
    n = 500
    z = pd.Series(rng.normal(0.0, 1.0, size=n), index=_idx(n))
    z.iloc[:60] = np.nan

    pos = dxy_downcross_signal(
        z, z_threshold=-1.0, hold_days=5, cooldown_days=5,
    )

    unique = set(pos.unique().tolist())
    assert unique.issubset({0.0, 1.0}), \
        f"position must be binary; got {unique}"


def test_no_lookahead_truncation_invariance():
    """Truncating z at any bar T must not change pos[<T]."""
    rng = np.random.default_rng(11)
    n = 400
    z = pd.Series(rng.normal(0.0, 1.0, size=n), index=_idx(n))
    z.iloc[:60] = np.nan

    pos_full = dxy_downcross_signal(
        z, z_threshold=-1.0, hold_days=5, cooldown_days=5,
    )
    cut = 250
    pos_trunc = dxy_downcross_signal(
        z.iloc[:cut], z_threshold=-1.0, hold_days=5, cooldown_days=5,
    )
    np.testing.assert_array_equal(pos_full.iloc[:cut].values, pos_trunc.values)


def test_state_machine_handles_first_cross_at_warmup_boundary():
    """A cross at exactly bar 60 (first valid z) must be detected.

    Edge case: z[59]=NaN, z[60]=-1.5. The rule z[t] < -1 AND z[t-1] >= -1
    requires z[t-1] to be a real number. NaN >= -1 is False, so the
    cross does NOT fire at bar 60 by design. First eligible cross is
    bar 61 onward (where z[t-1] is a real number).
    """
    n = 100
    z = pd.Series(np.full(n, 0.5), index=_idx(n))
    z.iloc[:60] = np.nan
    z.iloc[60] = -1.5    # First valid z is already below −1
    z.iloc[61:] = -1.5   # And stays below

    pos = dxy_downcross_signal(
        z, z_threshold=-1.0, hold_days=5, cooldown_days=5,
    )

    # No entry must have fired (cross condition with NaN predecessor → False)
    assert (pos == 0).all(), \
        "state machine fired on warmup-boundary NaN→below cross"
