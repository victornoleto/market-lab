"""TDD tests for iter 008 — XAU/XAG pair MR signal & pair P&L arithmetic.

Tests the small algorithmic primitives in ``run_backtest.py``:

* ``pair_log_ratio`` — log(gold/silver) on inner-joined series
* ``rolling_zscore`` — windowed z-score with NaN warmup
* ``pair_mr_signal`` — state machine: enter ±1 on |z|>z_entry, exit on
  |z|≤z_exit OR bars_held > timeout
* ``pair_gross_returns`` — dollar-neutral pair P&L
* ``compute_mean_hold`` — bar→trading-day conversion (signed positions)
* ``cost_aware_pre_val_gate`` — magnitude + t-stat + hit-rate + n-events

These are the moving parts that are most likely to mis-fire if I confuse
the direction convention or off-by-one the rolling window. Tests run
fast (no parquet I/O); reserved for the engine sanity layer separate
from the integration backtest.

Citations:
* `[algo_trading_chan, p.71-73, ch.3]` — z-score MR grammar
* `[advances_fin_ml, p.31-34]` — engine cleanliness as backtest precondition
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
    compute_mean_hold,
    pair_gross_returns,
    pair_log_ratio,
    pair_mr_signal,
    rolling_zscore,
)


# ---------------------------------------------------------------------------
# pair_log_ratio
# ---------------------------------------------------------------------------


def test_pair_log_ratio_basic():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    gold = pd.Series([2000.0, 2100.0, 2050.0, 2200.0, 2150.0], index=idx, name="close")
    silver = pd.Series([25.0, 26.0, 25.5, 27.0, 26.5], index=idx, name="close")
    out = pair_log_ratio(gold, silver)
    expected = np.log(gold.values / silver.values)
    assert np.allclose(out.values, expected, atol=1e-12)
    assert out.name == "log_ratio"


def test_pair_log_ratio_inner_join_drops_unaligned_dates():
    idx_gold = pd.date_range("2024-01-01", periods=5, freq="D")
    idx_silver = pd.date_range("2024-01-02", periods=5, freq="D")  # offset by 1
    gold = pd.Series([2000, 2100, 2050, 2200, 2150], index=idx_gold, dtype=float)
    silver = pd.Series([25, 26, 25.5, 27, 26.5], index=idx_silver, dtype=float)
    out = pair_log_ratio(gold, silver)
    assert len(out) == 4  # 4 dates overlap (Jan 2-5)
    assert out.index[0] == pd.Timestamp("2024-01-02")


# ---------------------------------------------------------------------------
# rolling_zscore
# ---------------------------------------------------------------------------


def test_rolling_zscore_warmup_nan():
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    s = pd.Series(np.arange(10, dtype=float), index=idx)
    z = rolling_zscore(s, lookback=5)
    # First 4 bars should be NaN (need 5 obs for std with ddof=1).
    assert z.iloc[:4].isna().all()
    # 5th bar onwards should be finite.
    assert z.iloc[4:].notna().all()


def test_rolling_zscore_value_at_known_point():
    # Constant + step → predictable z-score on the step bar.
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    s = pd.Series([10, 10, 10, 10, 10, 20], index=idx, dtype=float)
    z = rolling_zscore(s, lookback=5)
    # On bar 5 (index 5): mean of [10,10,10,10,20] = 12, std (ddof=1) of those =
    # sqrt(((10-12)^2 * 4 + (20-12)^2)/4) = sqrt((16+64)/4) = sqrt(20) ≈ 4.472
    # z = (20 - 12) / 4.472 ≈ 1.789
    assert abs(z.iloc[5] - 1.7889) < 1e-3


# ---------------------------------------------------------------------------
# pair_mr_signal — state machine
# ---------------------------------------------------------------------------


def test_pair_mr_signal_enters_short_ratio_on_z_high():
    """z > +z_entry → SHORT ratio → position = -1."""
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    # Construct fake z series that goes z<−2 (long entry) then crosses 0 then z>+2 (short entry)
    z = pd.Series([np.nan, np.nan, -2.5, -1.0, 0.0, +1.0, +2.5, +1.0, 0.0, -0.5], index=idx)
    pos = pair_mr_signal(z, z_entry=2.0, z_exit=0.5, timeout=20)
    # Bar 2: z=-2.5 → enter long ratio (pos = +1)
    assert pos.iloc[2] == +1.0
    # Bar 4: z=0.0, |z|<=0.5 → exit (pos = 0)
    assert pos.iloc[4] == 0.0
    # Bar 6: z=+2.5 → enter short ratio (pos = -1)
    assert pos.iloc[6] == -1.0
    # Bar 8: z=0.0 → exit (pos = 0)
    assert pos.iloc[8] == 0.0


def test_pair_mr_signal_timeout_exit():
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    # Enter long at bar 2, then |z| stays > 0.5 through end → timeout exit.
    z = pd.Series([np.nan, np.nan, -2.5, -2.0, -1.5, -1.2, -1.0, -0.8, -0.7, -0.6], index=idx)
    pos = pair_mr_signal(z, z_entry=2.0, z_exit=0.5, timeout=3)
    # Enter at bar 2 (bars_held=1 at entry).
    assert pos.iloc[2] == +1.0
    # bars_held 1..3 → in position. After bar_held > 3 (i.e., bar 5 has bars_held=4)
    # the state machine exits.
    # Position trail: bar 2 (held=1), bar 3 (held=2), bar 4 (held=3), bar 5 (held=4 → exit).
    assert pos.iloc[3] == +1.0
    assert pos.iloc[4] == +1.0
    assert pos.iloc[5] == 0.0  # timeout fires


def test_pair_mr_signal_no_pyramid():
    """Once in position, stay in position even if signal re-fires."""
    idx = pd.date_range("2024-01-01", periods=8, freq="D")
    z = pd.Series([np.nan, np.nan, -2.5, -2.5, -2.5, -2.5, -2.5, -0.5], index=idx)
    pos = pair_mr_signal(z, z_entry=2.0, z_exit=0.5, timeout=100)
    # Single entry; position stays +1 through bar 6; exits at bar 7 (z=-0.5, |z|<=0.5).
    assert (pos.iloc[2:7] == +1.0).all()
    assert pos.iloc[7] == 0.0


def test_pair_mr_signal_flat_warmup_when_z_nan():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    z = pd.Series([np.nan, np.nan, np.nan, np.nan, np.nan], index=idx)
    pos = pair_mr_signal(z, z_entry=2.0, z_exit=0.5, timeout=20)
    assert (pos == 0.0).all()


# ---------------------------------------------------------------------------
# pair_gross_returns
# ---------------------------------------------------------------------------


def test_pair_gross_returns_long_ratio_profits_when_gold_outperforms():
    """LONG ratio (pos=+1, long gold + short silver) profits when gold_ret > silver_ret."""
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    gold_ret = pd.Series([0.0, 0.02, -0.01, 0.005], index=idx)  # +2%, -1%, +0.5%
    silver_ret = pd.Series([0.0, 0.01, 0.01, 0.0], index=idx)   # +1%, +1%, 0%
    pos = pd.Series([0.0, +1.0, +1.0, 0.0], index=idx)
    pnl = pair_gross_returns(pos, gold_ret, silver_ret)
    # Pos at t-1: bar 0 = NaN/fillna(0); bar 1 = 0; bar 2 = +1; bar 3 = +1.
    # Bar 0: 0 × (0 − 0) = 0
    # Bar 1: 0 × (0.02 − 0.01) = 0
    # Bar 2: +1 × (-0.01 − 0.01) = -0.02 (gold underperformed silver)
    # Bar 3: +1 × (0.005 − 0.0) = +0.005
    assert pnl.iloc[0] == 0.0
    assert pnl.iloc[1] == 0.0
    assert abs(pnl.iloc[2] - (-0.02)) < 1e-12
    assert abs(pnl.iloc[3] - 0.005) < 1e-12


def test_pair_gross_returns_short_ratio_profits_when_silver_outperforms():
    """SHORT ratio (pos=-1, short gold + long silver) profits when silver_ret > gold_ret."""
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    gold_ret = pd.Series([0.0, -0.01, 0.0], index=idx)
    silver_ret = pd.Series([0.0, +0.02, 0.0], index=idx)
    pos = pd.Series([0.0, -1.0, -1.0], index=idx)
    pnl = pair_gross_returns(pos, gold_ret, silver_ret)
    # Pos at t-1: bar 1 has prev=0; bar 2 has prev=-1.
    # Bar 0: 0.
    # Bar 1: 0 × (-0.01 - 0.02) = 0.
    # Bar 2: -1 × (0.0 - 0.0) = 0.
    # Hmm — not the most illustrative test. Make t-1 transition earlier.
    pos = pd.Series([-1.0, -1.0, -1.0], index=idx)
    pnl = pair_gross_returns(pos, gold_ret, silver_ret)
    # Bar 1: -1 × (-0.01 - 0.02) = -1 × -0.03 = +0.03 (silver outperformed → short ratio profits)
    assert abs(pnl.iloc[1] - 0.03) < 1e-12


# ---------------------------------------------------------------------------
# compute_mean_hold (signed positions)
# ---------------------------------------------------------------------------


def test_compute_mean_hold_signed_positions():
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    # 2 trades: bars 0-2 long (3 bars), bars 5-6 short (2 bars), then flat.
    pos = pd.Series([+1, +1, +1, 0, 0, -1, -1, 0, 0, 0], index=idx, dtype=float)
    mean_days, n_trades, mean_bars = compute_mean_hold(pos, ann=252)
    assert n_trades == 2
    assert abs(mean_bars - 2.5) < 1e-9  # (3 + 2) / 2
    # ann=252 (daily) → bars_per_trading_day = 1.0 → mean_days == mean_bars
    assert abs(mean_days - 2.5) < 1e-9


def test_compute_mean_hold_handles_open_trade_at_end():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    pos = pd.Series([0, 0, +1, +1, +1], index=idx, dtype=float)
    mean_days, n_trades, mean_bars = compute_mean_hold(pos, ann=252)
    assert n_trades == 1
    # Trade open from bar 2 to end (3 bars).
    assert abs(mean_bars - 3.0) < 1e-9


def test_compute_mean_hold_intraday_conversion():
    """1h bars: ann=5119 → bars_per_trading_day = 5119/252 ≈ 20.31."""
    idx = pd.date_range("2024-01-01", periods=50, freq="h")
    pos = pd.Series(np.zeros(50), index=idx, dtype=float)
    pos.iloc[10:30] = +1  # 20 bars long
    mean_days, n_trades, mean_bars = compute_mean_hold(pos, ann=5119)
    assert n_trades == 1
    assert abs(mean_bars - 20.0) < 1e-9
    # 20 bars / (5119/252) ≈ 20 / 20.314 ≈ 0.985 trading days
    assert abs(mean_days - 20.0 / (5119 / 252)) < 1e-9


# ---------------------------------------------------------------------------
# cost_aware_pre_val_gate
# ---------------------------------------------------------------------------


def test_cost_aware_pre_val_passes_with_strong_signal():
    rng = np.random.default_rng(42)
    fwd_bps = 80.0 + 50.0 * rng.standard_normal(200)  # mean +80 bps, std 50
    res = cost_aware_pre_val_gate(
        fwd_bps, cost_floor_bps=30.0, margin=1.5,
        min_t_stat=1.0, min_hit_rate=0.50, min_events=30,
    )
    # Expected: mean ≈ 80, t ≈ 80/(50/sqrt(200)) ≈ 22.6 (huge), hit ≈ 0.94, n=200.
    assert res["passed"] is True
    assert res["n_events"] == 200
    assert res["mean_fwd_bps"] > 45.0


def test_cost_aware_pre_val_rejects_below_cost_floor():
    """Iter 007 trap: positive but too small magnitude is REJECTED by augmented pre-val."""
    # Deterministic: 200 values clustered tightly around +10 bps (positive, but ≪ 45 bps).
    fwd_bps = np.full(200, 10.0)
    fwd_bps[::2] = 12.0  # tiny variance so mean=11 stably > 0 with hit_rate=1.0
    res = cost_aware_pre_val_gate(
        fwd_bps, cost_floor_bps=30.0, margin=1.5,
        min_t_stat=1.0, min_hit_rate=0.50, min_events=30,
    )
    assert res["passed"] is False
    # Mean +11 bps > 0 (passes inversion check) but below 45-bps required edge.
    assert res["mean_fwd_bps"] > 0
    assert res["mean_fwd_bps"] < res["required_edge_bps"]
    assert "magnitude" in res["reason"].lower() or "below cost floor" in res["reason"].lower()


def test_cost_aware_pre_val_rejects_directional_inversion():
    rng = np.random.default_rng(13)
    fwd_bps = -50.0 + 50.0 * rng.standard_normal(200)  # mean -50 bps
    res = cost_aware_pre_val_gate(
        fwd_bps, cost_floor_bps=30.0, margin=1.5,
        min_t_stat=1.0, min_hit_rate=0.50, min_events=30,
    )
    assert res["passed"] is False


def test_cost_aware_pre_val_rejects_insufficient_events():
    fwd_bps = np.array([100.0, 80.0, 90.0, 110.0, 120.0])  # n=5 << min_events=30
    res = cost_aware_pre_val_gate(
        fwd_bps, cost_floor_bps=30.0, margin=1.5,
        min_t_stat=1.0, min_hit_rate=0.50, min_events=30,
    )
    assert res["passed"] is False
    assert "events" in res["reason"].lower() or "insufficient" in res["reason"].lower()
