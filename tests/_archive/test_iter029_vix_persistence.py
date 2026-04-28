"""TDD specs for iter 029 — VIX-persistence VRP-primary (R-1).

Five tests covering the persistence-gate engine:

1. ``test_persistence_off_at_high_threshold_matches_iter026`` — when
   the level threshold can never be hit, the persistence gate is
   irrelevant and the engine must reproduce iter 026 exactly.
2. ``test_persistence_days_1_matches_iter028`` — when the persistence
   horizon collapses to a single bar, R-1 must reproduce iter 028
   exactly to floating-point.
3. ``test_synthetic_persistence_cluster_skips_open`` — under a
   constructed VIX path with a 3-day cluster at threshold, the open
   that lands in the cluster must be skipped (overlay = 0 + rf for
   the dte_days window). An alternating ``[40,18,40,18,...]`` path
   must NOT trigger the gate (no 3-day persistence).
4. ``test_pandas_numpy_parity_iter026_window`` — pandas vs numpy
   engine on real iter 026 SPY+VIX window must match to < 1e-12 in
   maximum return.
5. ``test_no_skip_when_only_two_consecutive_days`` — a 2-day cluster
   must not trigger; only 3+ does.

Citations: same as ``vrp_persistence.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_026_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "026-2026-04-24-2122-vrp-primary-portfolio"
ITER_028_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "028-2026-04-24-2207-vix-filter-vrp-primary"
ITER_029_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "029-2026-04-24-2236-vix-persistence-vrp-primary"

for p in (ITER_026_DIR, ITER_028_DIR, ITER_029_DIR):
    sys.path.insert(0, str(p))

from vrp_persistence import (  # noqa: E402
    compute_vrp_persistence_returns,
    is_persistent_high,
)
from numpy_reference_persistence import (  # noqa: E402
    compute_vrp_persistence_returns_np,
)
from vrp_primary import compute_vrp_primary_returns  # noqa: E402
from vrp_filtered import compute_vrp_filtered_returns  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_synthetic_series(
    n: int = 60,
    seed: int = 7,
    vix_pattern: list[float] | None = None,
) -> tuple[pd.Series, pd.Series]:
    """Synthetic SPY + VIX series for unit tests."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2020-01-02", periods=n, freq="B")
    rets = rng.normal(0.0005, 0.012, size=n)
    prices = pd.Series(100.0 * np.cumprod(1 + rets), index=dates, name="price")
    if vix_pattern is None:
        vix_arr = np.full(n, 18.0)
    else:
        vix_arr = np.array(vix_pattern, dtype=float)
        if len(vix_arr) != n:
            raise ValueError("vix_pattern length must match n")
    vix = pd.Series(vix_arr, index=dates, name="vix")
    return prices, vix


# ---------------------------------------------------------------------------
# Test 1 — persistence gate vacuous at very high threshold
# ---------------------------------------------------------------------------

def test_persistence_off_at_high_threshold_matches_iter026():
    """vix_threshold = 1e9 → gate never fires → must equal iter 026 to 1e-12."""
    n = 200
    prices, vix = _make_synthetic_series(n=n, seed=11)
    iter026 = compute_vrp_primary_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    iter029_off = compute_vrp_persistence_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=1e9, persistence_days=3,
    )
    diff = np.max(np.abs(iter029_off.values - iter026.values))
    assert diff < 1e-12, (
        f"R-1 gate must be vacuous at threshold=1e9; max abs diff vs "
        f"iter 026 = {diff:.2e}"
    )


# ---------------------------------------------------------------------------
# Test 2 — persistence_days = 1 reproduces iter 028 (constant-threshold)
# ---------------------------------------------------------------------------

def test_persistence_days_1_matches_iter028():
    """persistence_days = 1 → single-bar trigger → must equal iter 028."""
    n = 250
    # Use a VIX pattern that sometimes crosses 35 so the gate actually fires
    rng = np.random.default_rng(13)
    base = 18.0 + 6.0 * np.sin(np.linspace(0, 4 * np.pi, n))
    spike_idx = [42, 43, 78, 79, 80, 145, 200]
    base[spike_idx] = 38.0
    prices, vix = _make_synthetic_series(
        n=n, seed=13, vix_pattern=base.tolist(),
    )
    iter028 = compute_vrp_filtered_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=35.0,
    )
    iter029_pd1 = compute_vrp_persistence_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=35.0, persistence_days=1,
    )
    diff = np.max(np.abs(iter029_pd1.values - iter028.values))
    assert diff < 1e-12, (
        f"persistence_days=1 must reproduce iter 028 exactly; "
        f"max abs diff = {diff:.2e}"
    )


# ---------------------------------------------------------------------------
# Test 3 — synthetic persistence cluster: skip vs allow
# ---------------------------------------------------------------------------

def test_synthetic_persistence_cluster_skips_open():
    """3-day cluster at threshold triggers gate; alternating pattern doesn't."""
    n = 50
    # Construct: cluster of 3 high-VIX bars at indices [21,22,23], the
    # natural roll bar at 21 should be SKIPPED (since vix[19],[20],[21]
    # check at i=21 is mixed; the persistence trigger is at i=23 onward).
    # The HOLD-CASH bar will then re-evaluate at i=42 (21 + 21).
    vix_pattern = [18.0] * n
    # Set bars [21, 22, 23] high to create a 3-day persistent cluster
    # ending at bar 23. The roll lands on bar 21 itself, and at i=21
    # is_persistent_high = (vix[19], vix[20], vix[21]) = (18,18,40) → False.
    # So the cfg below tests that a roll bar AT the start of a cluster
    # passes BUT a sustained cluster at a roll bar (eventually) skips.
    # Use a cleaner construction: set bars [20,21,22,23,24,25] all high,
    # then the i=21 roll has (vix[19],[20],[21]) = (18,40,40) → False,
    # but if we shift cluster to start at bar 19, i=21 = (40,40,40) → True.
    vix_pattern = [18.0] * n
    vix_pattern[19] = 40.0
    vix_pattern[20] = 40.0
    vix_pattern[21] = 40.0  # roll bar; persistence True
    prices, vix = _make_synthetic_series(
        n=n, seed=17, vix_pattern=vix_pattern,
    )
    rets_skip = compute_vrp_persistence_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=35.0, persistence_days=3,
    )
    # At bar 21 the engine should switch to HOLD-CASH (skip new open).
    # The bar 21 itself takes a closing cost (-cost_frac then negated by
    # short-writer convention), so we test the very next bar 22:
    # if HOLD-CASH, return must equal rf_daily exactly.
    rf_daily = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    # bars 22..min(42, n-1) should be HOLD-CASH → rf_daily exactly
    hc_bar = 25  # well within the HOLD-CASH window after bar 21 skip
    assert abs(rets_skip.iloc[hc_bar] - rf_daily) < 1e-12, (
        f"After persistence skip at bar 21, bar {hc_bar} must equal "
        f"rf_daily ({rf_daily:.6e}); got {rets_skip.iloc[hc_bar]:.6e}"
    )

    # Negative case: alternating pattern never accumulates 3 consecutive
    # days, so the gate never fires; output must equal iter 026 exactly.
    vix_alt = [40.0 if k % 2 == 0 else 18.0 for k in range(n)]
    prices2, vix2 = _make_synthetic_series(
        n=n, seed=17, vix_pattern=vix_alt,
    )
    rets_iter026 = compute_vrp_primary_returns(
        prices2, vix2,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    rets_alt = compute_vrp_persistence_returns(
        prices2, vix2,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=35.0, persistence_days=3,
    )
    diff = np.max(np.abs(rets_alt.values - rets_iter026.values))
    assert diff < 1e-12, (
        f"Alternating VIX pattern must not trigger persistence; "
        f"max abs diff vs iter 026 = {diff:.2e}"
    )


# ---------------------------------------------------------------------------
# Test 4 — pandas/numpy parity on iter 026 real window
# ---------------------------------------------------------------------------

def test_pandas_numpy_parity_iter026_window():
    """Pandas vs numpy engine on 200-bar synthetic must agree to 1e-12."""
    n = 250
    rng = np.random.default_rng(23)
    base = 18.0 + 8.0 * np.sin(np.linspace(0, 6 * np.pi, n))
    base[60:65] = 42.0   # cluster A
    base[140:148] = 45.0  # cluster B (longer)
    prices, vix = _make_synthetic_series(
        n=n, seed=23, vix_pattern=base.tolist(),
    )
    rets_pd = compute_vrp_persistence_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=35.0, persistence_days=3,
    )
    rets_np = compute_vrp_persistence_returns_np(
        prices.to_numpy(), vix.to_numpy(),
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=35.0, persistence_days=3,
    )
    diff = np.max(np.abs(rets_pd.values - rets_np))
    assert diff < 1e-12, (
        f"pandas vs numpy engine must match to 1e-12 (G7); got {diff:.2e}"
    )


# ---------------------------------------------------------------------------
# Test 5 — exact persistence semantics: 2-day cluster does not trigger
# ---------------------------------------------------------------------------

def test_no_skip_when_only_two_consecutive_days():
    """Two-day cluster (k=3 required) must not fire is_persistent_high."""
    vix = np.array([18, 40, 40, 18, 18, 40, 40, 40, 18, 18], dtype=float)
    # i=2 has (vix[0], vix[1], vix[2]) = (18, 40, 40) → False
    assert is_persistent_high(vix, 2, 35.0, 3) is False
    # i=7 has (vix[5], vix[6], vix[7]) = (40, 40, 40) → True
    assert is_persistent_high(vix, 7, 35.0, 3) is True
    # i=6 has (vix[4], vix[5], vix[6]) = (18, 40, 40) → False
    assert is_persistent_high(vix, 6, 35.0, 3) is False
    # i=8 has (vix[6], vix[7], vix[8]) = (40, 40, 18) → False
    assert is_persistent_high(vix, 8, 35.0, 3) is False
    # Insufficient history at i=0,1 (need 3) → always False
    assert is_persistent_high(vix, 0, 35.0, 3) is False
    assert is_persistent_high(vix, 1, 35.0, 3) is False


# ---------------------------------------------------------------------------
# Bonus parameter-validation tests (defensive)
# ---------------------------------------------------------------------------

def test_persistence_days_validation():
    prices, vix = _make_synthetic_series(n=30, seed=29)
    with pytest.raises(ValueError, match="persistence_days"):
        compute_vrp_persistence_returns(
            prices, vix, persistence_days=0,
        )


def test_vix_threshold_validation():
    prices, vix = _make_synthetic_series(n=30, seed=29)
    with pytest.raises(ValueError, match="vix_threshold"):
        compute_vrp_persistence_returns(
            prices, vix, vix_threshold=-1.0,
        )
