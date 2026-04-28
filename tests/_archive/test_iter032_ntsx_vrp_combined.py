"""TDD specs for iter 032 — NTSX 90/60 SPY+IEF base + iter 031 VRP+composite overlay.

Five tests covering the combined wrapper and its numpy parity:

1. ``test_combined_harvest_zero_matches_iter015`` — when ``harvest_notional=0``
   the harvest layer vanishes → combined must equal iter 015 NTSX exactly.
2. ``test_combined_eq_zero_bd_zero_matches_overlay_only`` — when both leg
   weights are zero, the combined return must equal the iter 031 overlay
   alone (= iter 026 minus rf_daily).
3. ``test_combined_pandas_numpy_parity_synthetic`` — pandas vs numpy engine
   match to 1e-10 on a synthetic 3-asset path (G7 anchor).
4. ``test_combined_inf_vix_threshold_matches_ntsx_plus_vrp026`` — when
   ``vix_threshold=1e9`` the AND-composite never fires → harvest equals
   iter 026's harvest (vrp_primary minus rf_daily) exactly.
5. ``test_combined_param_validation`` — invalid params rejected.

Citations
---------
* `[risk_parity, p.5, p.10-11, ch.1]` — NTSX risk-parity base.
* `[volatility_trading, p.217-218]` — VIX level + sustained gates.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_015_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "015-2026-04-24-1704-return-stacked-static-ntsx"
ITER_026_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "026-2026-04-24-2122-vrp-primary-portfolio"
ITER_030_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "030-2026-04-24-2259-vix-zscore-vrp-primary"
ITER_031_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "031-2026-04-24-2322-vix-and-composite-vrp-primary"
ITER_032_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "032-2026-04-25-0032-ntsx-vrp-and-composite"

for p in (ITER_015_DIR, ITER_026_DIR, ITER_030_DIR, ITER_031_DIR, ITER_032_DIR):
    sys.path.insert(0, str(p))

from synth_stacked_etf import apply_static_stack  # noqa: E402
from vrp_primary import compute_vrp_primary_returns  # noqa: E402
from vrp_zscore import rolling_zscore  # noqa: E402
from ntsx_vrp_combined import compute_ntsx_vrp_combined_returns  # noqa: E402
from numpy_reference_combined import compute_ntsx_vrp_combined_returns_np  # noqa: E402


def _make_synthetic_panel(
    n: int = 250,
    seed: int = 17,
    vix_pattern: list[float] | None = None,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Synthetic SPY-like + IEF-like + VIX series sharing a common index."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2020-01-02", periods=n, freq="B")
    eq_rets = rng.normal(0.0005, 0.012, size=n)
    bd_rets = rng.normal(0.00015, 0.004, size=n)
    eq = pd.Series(100.0 * np.cumprod(1.0 + eq_rets), index=dates, name="eq")
    bd = pd.Series(100.0 * np.cumprod(1.0 + bd_rets), index=dates, name="bd")
    if vix_pattern is None:
        vix_arr = 18.0 + 4.0 * rng.standard_normal(n)
        vix_arr = np.clip(vix_arr, 9.0, 80.0)
    else:
        vix_arr = np.array(vix_pattern, dtype=float)
        if len(vix_arr) != n:
            raise ValueError("vix_pattern length must match n")
    vix = pd.Series(vix_arr, index=dates, name="vix")
    return eq, bd, vix


def test_combined_harvest_zero_matches_iter015():
    """harvest_notional=0 → combined equals iter 015 NTSX exactly."""
    n = 250
    eq, bd, vix = _make_synthetic_panel(n=n, seed=3)
    z = rolling_zscore(vix, window=60)

    combined = compute_ntsx_vrp_combined_returns(
        eq, bd, vix, z,
        eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
        rf=0.02, harvest_notional=0.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=35.0, persistence_days=3, z_threshold=2.0,
    )

    r_eq = eq.pct_change().dropna()
    r_bd = bd.pct_change().dropna()
    ntsx_only, _, _ = apply_static_stack(
        r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
    )

    common = combined.index.intersection(ntsx_only.index)
    diff = float(np.max(np.abs(combined.loc[common].values - ntsx_only.loc[common].values)))
    assert diff < 1e-12, (
        f"harvest_notional=0 must reduce to iter 015 exactly; max abs diff={diff:.2e}"
    )


def test_combined_eq_zero_bd_zero_matches_overlay_only():
    """eq_w=bd_w=0 → combined equals iter 031 overlay (vrp minus rf_daily)."""
    n = 250
    eq, bd, vix = _make_synthetic_panel(n=n, seed=5)
    z = rolling_zscore(vix, window=60)

    combined = compute_ntsx_vrp_combined_returns(
        eq, bd, vix, z,
        eq_w=0.0, bd_w=0.0, cost_bps_per_leg=0.0002,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=1e9, persistence_days=3, z_threshold=2.0,
    )

    iter026_full = compute_vrp_primary_returns(
        eq, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    rf_daily = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    overlay_only = iter026_full - rf_daily

    common = combined.index.intersection(overlay_only.index)
    diff = float(np.max(np.abs(combined.loc[common].values - overlay_only.loc[common].values)))
    assert diff < 1e-12, (
        f"eq_w=bd_w=0, R-1 vacuous → overlay only; max abs diff={diff:.2e}"
    )


def test_combined_pandas_numpy_parity_synthetic():
    """G7: pandas vs numpy combined engine match to 1e-10 on synthetic data."""
    n = 250
    rng = np.random.default_rng(43)
    base = 18.0 + 6.0 * rng.standard_normal(n)
    base[60] = 45.0
    base[120:124] = 50.0
    base[200] = 55.0
    base = np.clip(base, 5.0, 80.0)
    eq, bd, vix = _make_synthetic_panel(n=n, seed=43, vix_pattern=base.tolist())
    z = rolling_zscore(vix, window=60)

    rets_pd = compute_ntsx_vrp_combined_returns(
        eq, bd, vix, z,
        eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=35.0, persistence_days=3, z_threshold=2.0,
    )
    rets_np = compute_ntsx_vrp_combined_returns_np(
        eq.to_numpy(), bd.to_numpy(), vix.to_numpy(), z.to_numpy(),
        eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=35.0, persistence_days=3, z_threshold=2.0,
    )
    assert len(rets_pd) == len(rets_np), (
        f"length mismatch: pd={len(rets_pd)}, np={len(rets_np)}"
    )
    diff = float(np.max(np.abs(rets_pd.values - rets_np)))
    assert diff < 1e-10, (
        f"pandas vs numpy engine must match to 1e-10 (G7); got {diff:.2e}"
    )


def test_combined_inf_vix_threshold_matches_ntsx_plus_vrp026():
    """vix_threshold=1e9 → AND vacuous → harvest = iter 026 - rf_daily.

    The combined return must equal iter 015 NTSX + (iter 026 - rf_daily).
    """
    n = 250
    eq, bd, vix = _make_synthetic_panel(n=n, seed=11)
    z = rolling_zscore(vix, window=60)

    combined = compute_ntsx_vrp_combined_returns(
        eq, bd, vix, z,
        eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        iv_scale=1.0, cost_bps_per_roll=5.0,
        vix_threshold=1e9, persistence_days=3, z_threshold=2.0,
    )

    r_eq = eq.pct_change().dropna()
    r_bd = bd.pct_change().dropna()
    ntsx_only, _, _ = apply_static_stack(
        r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
    )
    iter026_full = compute_vrp_primary_returns(
        eq, vix,
        rf=0.02, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    rf_daily = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    expected_overlay = iter026_full - rf_daily

    common = combined.index.intersection(ntsx_only.index).intersection(expected_overlay.index)
    expected = ntsx_only.loc[common] + expected_overlay.loc[common]
    diff = float(np.max(np.abs(combined.loc[common].values - expected.values)))
    assert diff < 1e-12, (
        f"AND vacuous → combined = NTSX + (iter026 - rf_daily); "
        f"max abs diff={diff:.2e}"
    )


def test_combined_param_validation():
    """Invalid params must raise ValueError."""
    n = 80
    eq, bd, vix = _make_synthetic_panel(n=n, seed=29)
    z = rolling_zscore(vix, window=60)

    with pytest.raises(ValueError, match="eq_w"):
        compute_ntsx_vrp_combined_returns(
            eq, bd, vix, z,
            eq_w=-0.1, bd_w=0.6,
            vix_threshold=35.0, persistence_days=3, z_threshold=2.0,
        )
    with pytest.raises(ValueError, match="harvest_notional"):
        compute_ntsx_vrp_combined_returns(
            eq, bd, vix, z,
            eq_w=0.9, bd_w=0.6, harvest_notional=-1.0,
            vix_threshold=35.0, persistence_days=3, z_threshold=2.0,
        )
    with pytest.raises(ValueError):
        compute_ntsx_vrp_combined_returns(
            eq, bd, vix, z,
            eq_w=0.9, bd_w=0.6,
            vix_threshold=-1.0, persistence_days=3, z_threshold=2.0,
        )
