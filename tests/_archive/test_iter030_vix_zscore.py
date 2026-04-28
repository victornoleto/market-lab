"""TDD specs for iter 030 — VIX z-score VRP-primary (R-2).

Six tests covering the z-score-gate engine + helper:

1. ``test_zscore_threshold_inf_matches_iter026`` — when z_threshold can
   never be reached (1e9), the gate is irrelevant and the engine must
   reproduce iter 026 exactly to floating-point.
2. ``test_zscore_helper_correctness_on_synthetic_vix`` — the z-score
   helper produces (x - rolling_mean) / rolling_std with the spec-ed
   60d window; first 59 bars are NaN.
3. ``test_zscore_warmup_first_59_bars_no_skip`` — when the z series is
   NaN at a roll bar (insufficient warmup history), the engine must
   NOT skip the open (default-to-open behavior, mirroring iter 029).
4. ``test_pandas_numpy_parity_synthetic`` — pandas vs numpy engines
   match to 1e-12 on a synthetic VIX path.
5. ``test_zscore_skip_at_high_z_synthetic`` — when the precomputed
   z-series has z >= 2.0 at a roll bar, the engine must transition
   to HOLD-CASH; subsequent bars in the cash window must equal
   rf_daily exactly.
6. ``test_zscore_threshold_validation`` — invalid threshold rejected.

Citations: same as ``vrp_zscore.py``.
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
ITER_030_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "030-2026-04-24-2259-vix-zscore-vrp-primary"

for p in (ITER_026_DIR, ITER_030_DIR):
    sys.path.insert(0, str(p))

from vrp_zscore import (  # noqa: E402
    compute_vrp_zscore_returns,
    rolling_zscore,
)
from numpy_reference_zscore import (  # noqa: E402
    compute_vrp_zscore_returns_np,
)
from vrp_primary import compute_vrp_primary_returns  # noqa: E402


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
# Test 1 — z-score gate vacuous at unreachable threshold
# ---------------------------------------------------------------------------

def test_zscore_threshold_inf_matches_iter026():
    """z_threshold = 1e9 → gate never fires → must equal iter 026 to 1e-12."""
    n = 200
    prices, vix = _make_synthetic_series(n=n, seed=11)
    # Pre-compute a z-series for the test (any values work since gate is off)
    vix_z = rolling_zscore(vix, window=60)
    iter026 = compute_vrp_primary_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    iter030_off = compute_vrp_zscore_returns(
        prices, vix, vix_z,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        z_threshold=1e9,
    )
    diff = np.max(np.abs(iter030_off.values - iter026.values))
    assert diff < 1e-12, (
        f"R-2 gate must be vacuous at z_threshold=1e9; max abs diff vs "
        f"iter 026 = {diff:.2e}"
    )


# ---------------------------------------------------------------------------
# Test 2 — z-score helper correctness
# ---------------------------------------------------------------------------

def test_zscore_helper_correctness_on_synthetic_vix():
    """Rolling z-score helper produces (x - mean) / std with first w-1 NaN."""
    n = 100
    window = 60
    rng = np.random.default_rng(31)
    raw = 18.0 + 4.0 * rng.standard_normal(n)
    raw[80] = 50.0  # plant an obvious shock at index 80
    dates = pd.date_range("2020-01-02", periods=n, freq="B")
    vix = pd.Series(raw, index=dates, name="vix")

    z = rolling_zscore(vix, window=window)

    # Indices 0..58 must be NaN
    assert z.iloc[:window - 1].isna().all(), (
        f"first {window - 1} indices must be NaN; got non-NaN at "
        f"{z.iloc[:window - 1].dropna()}"
    )
    # Index 59 onwards must be valid
    assert z.iloc[window - 1:].notna().all(), (
        "z must be defined from index window-1 onwards"
    )
    # Spot-check: at index 59, z = (vix[59] - mean(vix[0:60])) / std(vix[0:60])
    expected_mu = raw[:60].mean()
    expected_sigma = raw[:60].std(ddof=1)
    expected_z = (raw[59] - expected_mu) / expected_sigma
    assert abs(z.iloc[59] - expected_z) < 1e-12, (
        f"z[59] expected {expected_z:.6f}; got {z.iloc[59]:.6f}"
    )
    # Spot-check at index 80 (the shock): should produce a high z
    expected_mu_80 = raw[21:81].mean()
    expected_sigma_80 = raw[21:81].std(ddof=1)
    expected_z_80 = (raw[80] - expected_mu_80) / expected_sigma_80
    assert abs(z.iloc[80] - expected_z_80) < 1e-12, (
        f"z[80] expected {expected_z_80:.6f}; got {z.iloc[80]:.6f}"
    )
    assert z.iloc[80] > 2.0, (
        f"planted shock at idx 80 should produce z > 2; got {z.iloc[80]:.3f}"
    )


# ---------------------------------------------------------------------------
# Test 3 — engine does not skip when z is NaN in warmup window
# ---------------------------------------------------------------------------

def test_zscore_warmup_first_59_bars_no_skip():
    """During z-warmup (first 59 bars), engine must default to OPEN."""
    n = 100
    # Construct a VIX path with a constant value so z-score is defined +
    # zero-valued from index 59 onwards. The engine should open at bar 0
    # and the first 5 rolls must NOT be skipped.
    prices, vix = _make_synthetic_series(
        n=n, seed=37, vix_pattern=[20.0] * n,
    )
    z = rolling_zscore(vix, window=60)
    # All defined z values are 0 (constant series); NaN in first 59 bars.
    rets = compute_vrp_zscore_returns(
        prices, vix, z,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        z_threshold=2.0,
    )
    # iter 026 baseline (no gate at all) — must match exactly because:
    # bars 0..58 don't skip (z is NaN; default-to-open)
    # bars 59..n don't skip (z = 0 < 2.0)
    iter026 = compute_vrp_primary_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    diff = np.max(np.abs(rets.values - iter026.values))
    assert diff < 1e-12, (
        f"Z=NaN warmup + Z=0 main range must match iter 026; "
        f"max abs diff = {diff:.2e}"
    )


# ---------------------------------------------------------------------------
# Test 4 — pandas/numpy parity (G7)
# ---------------------------------------------------------------------------

def test_pandas_numpy_parity_synthetic():
    """Pandas vs numpy engine match to 1e-12 on synthetic VIX with shocks."""
    n = 250
    rng = np.random.default_rng(43)
    base = 18.0 + 6.0 * rng.standard_normal(n)
    # Plant a few shocks
    base[60] = 45.0
    base[120:124] = 50.0
    base[200] = 55.0
    base = np.clip(base, 5.0, 80.0)
    prices, vix = _make_synthetic_series(
        n=n, seed=43, vix_pattern=base.tolist(),
    )
    z = rolling_zscore(vix, window=60)

    rets_pd = compute_vrp_zscore_returns(
        prices, vix, z,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        z_threshold=2.0,
    )
    rets_np = compute_vrp_zscore_returns_np(
        prices.to_numpy(), vix.to_numpy(), z.to_numpy(),
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        z_threshold=2.0,
    )
    diff = np.max(np.abs(rets_pd.values - rets_np))
    assert diff < 1e-12, (
        f"pandas vs numpy engine must match to 1e-12 (G7); got {diff:.2e}"
    )


# ---------------------------------------------------------------------------
# Test 5 — gate fires at high-z roll bar; HOLD-CASH yields rf_daily
# ---------------------------------------------------------------------------

def test_zscore_skip_at_high_z_synthetic():
    """When z >= threshold at a natural roll bar, switch to HOLD-CASH."""
    n = 120
    # Build a low-VIX background then a single big spike at the natural
    # roll bar (index = 21 in a dte_days=21 schedule) — but the z-score
    # at index 21 is NaN (warmup), so the gate doesn't fire. We need to
    # put the spike at a natural roll bar AFTER the 60-bar warmup. With
    # dte_days=21, natural rolls are at 0, 21, 42, 63, 84, 105 — the
    # first post-warmup roll is at index 63.
    vix_pattern = [18.0] * n
    vix_pattern[63] = 60.0   # spike at the post-warmup roll bar
    # To produce z > 2 at i=63, the surrounding 60 bars must have small
    # std. They're all 18.0 here, so std = 0 — z would be inf. Add tiny
    # variation via a deterministic ramp:
    for k in range(n):
        vix_pattern[k] = 18.0 + 0.001 * k
    vix_pattern[63] = 60.0
    prices, vix = _make_synthetic_series(
        n=n, seed=53, vix_pattern=vix_pattern,
    )
    z = rolling_zscore(vix, window=60)
    # Sanity: z at index 63 should be very high
    assert z.iloc[63] > 2.0, (
        f"engineered spike at idx 63 must give z > 2; got {z.iloc[63]:.3f}"
    )
    rets = compute_vrp_zscore_returns(
        prices, vix, z,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, iv_scale=1.0, cost_bps_per_roll=5.0,
        z_threshold=2.0,
    )
    rf_daily = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    # After bar 63 skip, bars 64..min(83, n-1) are HOLD-CASH → rf_daily.
    hc_bar = 70
    assert abs(rets.iloc[hc_bar] - rf_daily) < 1e-12, (
        f"After z-skip at bar 63, bar {hc_bar} must equal rf_daily "
        f"({rf_daily:.6e}); got {rets.iloc[hc_bar]:.6e}"
    )


# ---------------------------------------------------------------------------
# Test 6 — parameter validation
# ---------------------------------------------------------------------------

def test_zscore_threshold_validation():
    prices, vix = _make_synthetic_series(n=80, seed=29)
    z = rolling_zscore(vix, window=60)
    # Negative threshold is invalid (z is always positive after abs/sign)
    with pytest.raises(ValueError, match="z_threshold"):
        compute_vrp_zscore_returns(
            prices, vix, z, z_threshold=-1.0,
        )


def test_zscore_window_validation():
    vix_arr = pd.Series(np.full(60, 18.0))
    with pytest.raises(ValueError, match="window"):
        rolling_zscore(vix_arr, window=1)
    with pytest.raises(ValueError, match="window"):
        rolling_zscore(vix_arr, window=0)
