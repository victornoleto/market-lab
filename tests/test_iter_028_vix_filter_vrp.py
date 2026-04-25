"""Iter 028 — TDD specs for VIX-filter VRP-primary (V-3).

Locks the semantics BEFORE implementation:

  At every natural roll bar, if ``vix[i] >= vix_threshold``, **skip
  the open**: the strategy holds T-bills (return = ``rf_daily``) for
  the next ``dte_days`` bars, then re-evaluates at the next roll bar.
  Otherwise, the engine is identical to iter 026.

Citations
---------
* `[volatility_trading, p.217]` — Sinclair VIX < 35 entry rule for
  short index-vol harvest strategies.
* `[volatility_trading, ch.3]` — VRP mechanics (unchanged from iter 026).
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ITER_028_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "028-2026-04-24-2207-vix-filter-vrp-primary"
ITER_026_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "026-2026-04-24-2122-vrp-primary-portfolio"
for p in (ITER_028_DIR, ITER_026_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _make_synthetic_inputs(
    n: int = 200,
    drift: float = 0.0,
    vol: float = 0.20,
    iv_pct: float = 20.0,
    seed: int = 7,
) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    dt = 1.0 / 252.0
    z = rng.standard_normal(n)
    log_rets = (drift - 0.5 * vol * vol) * dt + vol * np.sqrt(dt) * z
    prices = 100.0 * np.exp(np.cumsum(log_rets))
    idx = pd.bdate_range("2010-01-04", periods=n)
    return (
        pd.Series(prices, index=idx, name="price"),
        pd.Series(np.full(n, iv_pct), index=idx, name="vix"),
    )


def test_filter_off_at_high_threshold_matches_iter026() -> None:
    """vix_threshold = 1e9 → engine identical to iter 026 (no opens skipped)."""
    from vrp_filtered import compute_vrp_filtered_returns
    from vrp_primary import compute_vrp_primary_returns

    prices, iv = _make_synthetic_inputs(n=120, vol=0.22, iv_pct=21.0)
    r_filtered = compute_vrp_filtered_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
        vix_threshold=1e9,  # never triggers
    )
    r_iter026 = compute_vrp_primary_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    np.testing.assert_allclose(r_filtered.values, r_iter026.values, atol=1e-14)


def test_filter_skips_open_when_vix_above_threshold_at_initial_open() -> None:
    """If VIX[0] >= threshold, day 0 should NOT pay opening cost.

    Iter 026 charges -cost_frac at bar 0 unconditionally (initial open).
    Iter 028 must skip that open if VIX[0] >= threshold; instead bar 0
    returns rf_daily (no position held).
    """
    from vrp_filtered import compute_vrp_filtered_returns

    n = 60
    prices = pd.Series(
        100.0 * np.exp(np.cumsum(np.full(n, 0.0))),
        index=pd.bdate_range("2010-01-04", periods=n),
    )
    iv = pd.Series(np.full(n, 50.0), index=prices.index)  # always >= 35
    r = compute_vrp_filtered_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
        vix_threshold=35.0,
    )
    rf_daily = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    np.testing.assert_allclose(r.values, rf_daily, atol=1e-14)


def test_filter_skips_intermediate_roll_when_vix_above_threshold() -> None:
    """If VIX < threshold at open but >= threshold at next roll bar,
    the position completes its life, then the next roll is skipped:
    the next dte_days bars are pure rf_daily.
    """
    from vrp_filtered import compute_vrp_filtered_returns

    # 60 bars, dte=20: roll bars at 0, 20, 40
    n = 60
    dte = 20
    prices = pd.Series(
        100.0 * np.exp(np.cumsum(np.full(n, 0.0))),
        index=pd.bdate_range("2010-01-04", periods=n),
    )
    # Low VIX at bar 0, high at bar 20 (next roll), low again at bar 40
    iv_arr = np.full(n, 20.0)
    iv_arr[20:40] = 50.0  # forces skip on roll at bar 20
    iv = pd.Series(iv_arr, index=prices.index)

    r = compute_vrp_filtered_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=dte,
        cost_bps_per_roll=5.0,
        vix_threshold=35.0,
    )
    rf_daily = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    # Bars 21..39 (after the skipped roll, before the next eligible roll
    # at bar 40) should be pure rf_daily because no position is held.
    np.testing.assert_allclose(r.values[21:40], rf_daily, atol=1e-14)


def test_filter_engine_pandas_numpy_parity() -> None:
    """G7: pandas vs numpy engine must match to 1e-10."""
    from vrp_filtered import compute_vrp_filtered_returns
    from numpy_reference_filtered import compute_vrp_filtered_returns_np

    rng = np.random.default_rng(11)
    n = 250
    log_rets = -0.5 * 0.22**2 / 252.0 + 0.22 * np.sqrt(1 / 252.0) * rng.standard_normal(n)
    prices_arr = 100.0 * np.exp(np.cumsum(log_rets))
    iv_arr = 18.0 + 12.0 * np.abs(rng.standard_normal(n))  # mean ~28, occasional > 35
    idx = pd.bdate_range("2008-01-02", periods=n)
    prices = pd.Series(prices_arr, index=idx)
    iv = pd.Series(iv_arr, index=idx)

    r_pd = compute_vrp_filtered_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
        vix_threshold=35.0,
    )
    r_np = compute_vrp_filtered_returns_np(
        prices.to_numpy(),
        iv.to_numpy(),
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
        vix_threshold=35.0,
    )
    np.testing.assert_allclose(r_pd.values, r_np, atol=1e-10)


def test_returns_index_matches_aligned_input() -> None:
    """Output index = aligned (price ∩ iv) index — no surprises."""
    from vrp_filtered import compute_vrp_filtered_returns

    prices, iv = _make_synthetic_inputs(n=40)
    r = compute_vrp_filtered_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
        vix_threshold=35.0,
    )
    pd.testing.assert_index_equal(r.index, prices.index)


def test_negative_threshold_raises() -> None:
    """vix_threshold < 0 raises (defensive guard against sign flip mistakes)."""
    from vrp_filtered import compute_vrp_filtered_returns
    import pytest

    prices, iv = _make_synthetic_inputs()
    with pytest.raises(ValueError, match="vix_threshold"):
        compute_vrp_filtered_returns(
            prices, iv,
            rf=0.02,
            harvest_notional=1.0,
            k_long_pct=0.95,
            k_short_pct=0.90,
            dte_days=21,
            cost_bps_per_roll=5.0,
            vix_threshold=-1.0,
        )


def test_filter_at_threshold_zero_returns_pure_rf() -> None:
    """vix_threshold = 0 → every open is filtered out → pure rf_daily."""
    from vrp_filtered import compute_vrp_filtered_returns

    prices, iv = _make_synthetic_inputs(n=80, vol=0.20, iv_pct=20.0)
    r = compute_vrp_filtered_returns(
        prices, iv,
        rf=0.04,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
        vix_threshold=0.0,
    )
    rf_daily = (1.0 + 0.04) ** (1.0 / 252.0) - 1.0
    np.testing.assert_allclose(r.values, rf_daily, atol=1e-14)
