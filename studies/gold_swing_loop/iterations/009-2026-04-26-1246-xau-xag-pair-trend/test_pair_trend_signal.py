"""TDD tests for iter 009 — XAU/XAG pair TREND-FOLLOW signal sign-flip.

Validates that ``pair_trend_signal`` is the exact sign-flip of iter 008's
``pair_mr_signal`` — same z thresholds, same exit rules, but entry
direction reversed (z>+entry → +1 instead of −1).

Plus the pre-val sign-flip: signed_fwd = +sign(z) × Δlog_ratio (vs
iter 008's −sign(z)).

Citations
---------
* `[algo_trading_chan, p.133, ch.6]` — TS momentum (entry direction)
* DEAD_ENDS GS-8 — empirical sign-flip evidence drives this iter
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))

from run_backtest import (  # noqa: E402
    cost_aware_pre_val_gate,
    pair_trend_signal,
    rolling_zscore,
    run_pre_val_for_dataset,
)


# ---------------------------------------------------------------------------
# pair_trend_signal — sign-flip vs iter 008 MR
# ---------------------------------------------------------------------------


def test_trend_signal_enters_long_at_high_z():
    """z > +z_entry → state = +1 (LONG ratio, opposite of iter 008 MR which goes -1)."""
    idx = pd.date_range("2024-01-01", periods=8, freq="D")
    z = pd.Series([np.nan, np.nan, 0.0, 2.5, 2.5, 2.5, 2.5, 0.0],
                  index=idx, name="zscore")
    pos = pair_trend_signal(z, z_entry=2.0, z_exit=-1.0, timeout=10)
    # Bar 3: z crosses to 2.5 > +z_entry → enter LONG ratio (pos=+1).
    # Bars 4-7: still in trade (timeout=10 not yet hit, |z| never <= -1).
    assert pos.iloc[3] == +1.0, f"expected +1 LONG ratio at z=+2.5, got {pos.iloc[3]}"
    assert pos.iloc[4] == +1.0
    assert pos.iloc[7] == +1.0  # still held; timeout=10 > 5 bars elapsed


def test_trend_signal_enters_short_at_low_z():
    """z < -z_entry → state = -1 (SHORT ratio)."""
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    z = pd.Series([np.nan, np.nan, 0.0, -2.5, -2.0, -1.5],
                  index=idx, name="zscore")
    pos = pair_trend_signal(z, z_entry=2.0, z_exit=-1.0, timeout=10)
    assert pos.iloc[3] == -1.0, f"expected -1 SHORT ratio at z=-2.5, got {pos.iloc[3]}"


def test_trend_signal_timeout_only_exit():
    """With z_exit=-1.0, exit ONLY on bars_held > timeout. Single-trade isolation:
    enter once at bar 2, force flat after by setting z back to 0."""
    idx = pd.date_range("2024-01-01", periods=15, freq="D")
    # Bar 2: z=2.5 enters. Bars 3-6: still high but won't matter for trade #1.
    # Bar 7+: z=0 prevents re-entry and proves no early exit happened.
    z = pd.Series([np.nan, np.nan, 2.5, 2.5, 2.5, 2.5, 2.5, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  index=idx, name="zscore")
    pos = pair_trend_signal(z, z_entry=2.0, z_exit=-1.0, timeout=5)
    # Enter at bar 2 with bars_held=1. Subsequent bars: bars_held=2,3,4,5 (still in).
    # Bar 7: bars_held=6 > 5 → exit; pos[7]=0. Bars 2-6 in-trade = 5 bars.
    in_trade_bars = (pos != 0).sum()
    assert in_trade_bars == 5, (
        f"expected exactly 5 in-trade bars (timeout=5), got {in_trade_bars}: {pos.values}"
    )
    # Bars 7-14 must all be flat (no re-entry once z drops to 0).
    assert (pos.iloc[7:] == 0).all()


def test_trend_signal_no_z_exit_when_z_exit_negative():
    """z_exit=-1.0 means |z|<=-1 never holds (|z|>=0 always); proves timeout-only."""
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    # z drops from 2.5 to 0.0 — would trigger z_exit=0.5 in iter 008's MR engine,
    # but with z_exit=-1.0 it should NOT trigger an early exit.
    z = pd.Series([np.nan, 2.5, 1.0, 0.5, 0.0], index=idx, name="zscore")
    pos = pair_trend_signal(z, z_entry=2.0, z_exit=-1.0, timeout=10)
    # Enter at bar 1 (z=2.5). Stay in until timeout=10. All bars 1-4 in-trade.
    assert (pos.iloc[1:] == +1.0).all(), (
        f"expected to stay LONG even as z reverts toward 0; got {pos.values}"
    )


def test_trend_signal_handles_nan_z():
    """NaN z bars don't trigger entry or affect existing position."""
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    z = pd.Series([np.nan, np.nan, np.nan, np.nan, 2.5, np.nan],
                  index=idx, name="zscore")
    pos = pair_trend_signal(z, z_entry=2.0, z_exit=-1.0, timeout=10)
    assert (pos.iloc[:4] == 0.0).all()
    assert pos.iloc[4] == +1.0
    # Bar 5: NaN doesn't exit (mean_revert is False due to is-nan check),
    # bars_held=2 < timeout, so still in trade.
    assert pos.iloc[5] == +1.0


def test_trend_signal_is_sign_flip_of_mr_signal():
    """Cross-import test against iter 008's pair_mr_signal via importlib
    (both files happen to be named ``run_backtest.py``)."""
    import importlib.util

    iter_008_path = (
        ITER_DIR.parents[0] / "008-2026-04-26-1223-xau-xag-pair-mr" / "run_backtest.py"
    )
    spec = importlib.util.spec_from_file_location("iter008_runbt", iter_008_path)
    assert spec is not None and spec.loader is not None
    iter008_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(iter008_mod)
    mr_signal_iter008 = iter008_mod.pair_mr_signal

    idx = pd.date_range("2024-01-01", periods=12, freq="D")
    # Z trace: warmup, hi entry, hold, drop to 0 (no z-exit on either with z_exit=-1),
    # low entry, hold, drop to 0, hi entry. Timeout=10 keeps both signals in trade.
    z = pd.Series(
        [np.nan, np.nan, 2.5, 2.5, 0.0, 0.0, -2.5, -2.5, 0.0, 0.0, 2.5, 2.5],
        index=idx, name="zscore",
    )
    pos_trend = pair_trend_signal(z, z_entry=2.0, z_exit=-1.0, timeout=10)
    pos_mr = mr_signal_iter008(z, z_entry=2.0, z_exit=-1.0, timeout=10)
    # Sign-flip identity: pos_trend == -pos_mr at every bar.
    assert np.array_equal(pos_trend.values, -pos_mr.values), (
        f"expected sign-flip; trend={pos_trend.values}, mr={pos_mr.values}"
    )


# ---------------------------------------------------------------------------
# run_pre_val_for_dataset — sign-flip on signed_fwd
# ---------------------------------------------------------------------------


def test_pre_val_sign_flip_yields_positive_mean_when_trend_continues():
    """Synthetic: persistent upward drift after bar 60 → high z AND continued
    upward log_ratio movement → trend-follow signed_fwd > 0.

    Differs from a one-shot jump (where z spikes high then mean-reverts as
    rolling mean catches up): we want CONTINUED drift while z remains > +2,
    which is the regime the trend-follow hypothesis targets.
    """
    idx = pd.date_range("2024-01-01", periods=400, freq="D")
    rng = np.random.default_rng(seed=42)
    base = np.cumsum(rng.normal(0, 0.003, 400))
    # Strong continuous trend after bar 60 (after lookback warmup).
    base[60:] += np.linspace(0, 1.0, 340)
    log_ratio = pd.Series(base, index=idx, name="log_ratio")

    pv = run_pre_val_for_dataset(
        log_ratio, lookback=60, timeout=10, z_entry=2.0,
    )
    assert pv["cost_aware"]["n_events"] >= 30, (
        f"need enough events for stat power; got {pv['cost_aware']['n_events']}"
    )
    # Continued upward drift while z>+2 → trend-follow signed_fwd is positive.
    assert pv["cost_aware"]["mean_fwd_bps"] > 0, (
        f"expected positive trend-follow signed_fwd; got {pv['cost_aware']['mean_fwd_bps']:.2f}"
    )


# ---------------------------------------------------------------------------
# cost_aware_pre_val_gate — same logic as iter 008 (re-export sanity)
# ---------------------------------------------------------------------------


def test_cost_gate_passes_at_high_magnitude():
    rng = np.random.default_rng(seed=42)
    fwd = 50.0 + rng.normal(0, 5.0, 100)  # 50 bps mean with realistic noise
    res = cost_aware_pre_val_gate(
        fwd, cost_floor_bps=30.0, margin=1.5, min_t_stat=1.0,
        min_hit_rate=0.50, min_events=30,
    )
    assert res["passed"] is True, f"unexpected fail reason: {res['reason']}"
    assert abs(res["mean_fwd_bps"] - 50.0) < 5.0  # within noise band


def test_cost_gate_fails_at_low_magnitude():
    fwd = np.full(100, 10.0)  # 10 bps < 45 bps required
    res = cost_aware_pre_val_gate(
        fwd, cost_floor_bps=30.0, margin=1.5, min_t_stat=1.0,
        min_hit_rate=0.50, min_events=30,
    )
    assert res["passed"] is False
    assert "magnitude below cost floor" in res["reason"]


def test_cost_gate_fails_on_negative_mean():
    """Trend-follow direction inversion (mean fwd < 0) → fail."""
    fwd = np.full(100, -50.0)
    res = cost_aware_pre_val_gate(
        fwd, cost_floor_bps=30.0, margin=1.5, min_t_stat=1.0,
        min_hit_rate=0.50, min_events=30,
    )
    assert res["passed"] is False
    assert "directional inversion" in res["reason"]
