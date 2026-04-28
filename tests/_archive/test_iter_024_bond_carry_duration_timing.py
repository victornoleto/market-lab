"""Iter 024 — TDD specs for bond-carry duration timing.

Locks the semantics of the carry-as-allocation primitive BEFORE
implementation. Each spec encodes one structural invariant.

Citations
---------
* `[ilmanen_expected_returns, ch.6-7]` — term premium / roll-down carry.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "024-2026-04-24-2033-bond-carry-duration-timing"
sys.path.insert(0, str(ITER_DIR))

from bond_carry_duration_timing import (  # noqa: E402
    apply_bond_carry_duration_timing,
    compute_carry_allocation,
)
from numpy_reference_bcdt import (  # noqa: E402
    apply_bond_carry_duration_timing_np,
)


def _make_streams(
    n: int = 252,
    seed: int = 7,
    sig_const: float | None = None,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_eq = pd.Series(rng.normal(0.0005, 0.012, n), index=idx, name="SPY")
    r_tlt = pd.Series(rng.normal(0.0001, 0.008, n), index=idx, name="TLT")
    r_shv = pd.Series(rng.normal(0.00005, 0.0002, n), index=idx, name="SHV")
    if sig_const is not None:
        sig = pd.Series(np.full(n, sig_const), index=idx, name="T10Y3M")
    else:
        # Realistic-ish T10Y3M wandering between -0.5% and +2.5%
        signal_path = np.cumsum(rng.normal(0.0, 0.05, n)) + 1.0
        sig = pd.Series(np.clip(signal_path, -0.5, 2.5), index=idx, name="T10Y3M")
    return r_eq, r_tlt, r_shv, sig


# ---------------------------------------------------------------------------
# Carry signal mapping
# ---------------------------------------------------------------------------


def test_compute_alloc_steep_curve_saturates_at_one():
    """T10Y3M = 200 bps (= 2.00 percent) → alloc_TLT == 1.0 after warm-up."""
    n = 60
    sig = pd.Series(
        [2.00] * n,
        index=pd.date_range("2010-01-04", periods=n, freq="B"),
    )
    alloc = compute_carry_allocation(
        sig, smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
    )
    valid = alloc.dropna()
    assert (valid == 1.0).all(), \
        f"steep curve must give alloc_TLT=1; got range [{valid.min()},{valid.max()}]"


def test_compute_alloc_inverted_curve_floors_at_zero():
    """T10Y3M = -50 bps → alloc_TLT == 0.0 (clipped from below)."""
    n = 60
    sig = pd.Series(
        [-0.50] * n,
        index=pd.date_range("2010-01-04", periods=n, freq="B"),
    )
    alloc = compute_carry_allocation(
        sig, smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
    )
    valid = alloc.dropna()
    assert (valid == 0.0).all(), \
        f"inverted curve must give alloc_TLT=0; got range [{valid.min()},{valid.max()}]"


def test_compute_alloc_linear_ramp_at_midpoint():
    """T10Y3M = 50 bps with ramp_max=100bps → alloc_TLT == 0.5."""
    n = 60
    sig = pd.Series(
        [0.50] * n,
        index=pd.date_range("2010-01-04", periods=n, freq="B"),
    )
    alloc = compute_carry_allocation(
        sig, smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
    )
    valid = alloc.dropna()
    assert np.allclose(valid.to_numpy(), 0.5, atol=1e-12)


def test_compute_alloc_lag_blocks_lookahead():
    """Mutating signal at bar t+5 must NOT change alloc at bar t."""
    r_eq, r_tlt, r_shv, sig = _make_streams(60, seed=11)
    a1 = compute_carry_allocation(
        sig, smoothing_days=5, lag_bars=1, ramp_max_bps=100.0,
    )
    sig2 = sig.copy()
    sig2.iloc[-5:] = 5.0  # extreme spike at the end
    a2 = compute_carry_allocation(
        sig2, smoothing_days=5, lag_bars=1, ramp_max_bps=100.0,
    )
    # alloc on bars [..-(5+5+1)] should be identical (smoothing 5 + lag 1
    # means bar t depends on signal[t-5..t-1] only)
    np.testing.assert_allclose(
        a1.iloc[:-5].to_numpy(), a2.iloc[:-5].to_numpy(),
        atol=1e-15, equal_nan=True,
    )


# ---------------------------------------------------------------------------
# Three-leg static-equity / dynamic-bond stack — invariants
# ---------------------------------------------------------------------------


def test_total_leverage_equals_eq_w_plus_bd_w_at_every_bar():
    """pos_EQ + pos_TLT + pos_SHV ≡ eq_w + bd_w (constant total notional)."""
    r_eq, r_tlt, r_shv, sig = _make_streams(80, seed=13)
    _, positions, scale, _ = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0,
    )
    total = positions["EQ"] + positions["TLT"] + positions["SHV"]
    assert np.allclose(total.to_numpy(), 1.5, atol=1e-12), \
        f"positions must sum to 1.5; got [{total.min()},{total.max()}]"
    assert np.allclose(scale.to_numpy(), 1.5, atol=1e-12)


def test_equity_position_is_constant():
    """pos_EQ must equal eq_w at every bar (no equity timing)."""
    r_eq, r_tlt, r_shv, sig = _make_streams(60, seed=17)
    _, positions, _, _ = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0,
    )
    assert np.allclose(positions["EQ"].to_numpy(), 0.9, atol=1e-12)


def test_bond_legs_sum_to_bd_w_at_every_bar():
    """pos_TLT + pos_SHV ≡ bd_w (the bond-leg notional is constant)."""
    r_eq, r_tlt, r_shv, sig = _make_streams(80, seed=19)
    _, positions, _, alloc = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0,
    )
    bd_total = positions["TLT"] + positions["SHV"]
    assert np.allclose(bd_total.to_numpy(), 0.6, atol=1e-12)
    # Allocations bounded.
    assert (alloc.dropna() >= 0).all() and (alloc.dropna() <= 1).all()


def test_steep_curve_routes_all_bond_to_TLT():
    """T10Y3M ≡ +200 bps → alloc_TLT=1 → pos_TLT=bd_w, pos_SHV=0."""
    r_eq, r_tlt, r_shv, sig = _make_streams(80, seed=23, sig_const=2.0)
    _, positions, _, alloc = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0,
    )
    assert np.allclose(alloc.to_numpy(), 1.0, atol=1e-12)
    assert np.allclose(positions["TLT"].to_numpy(), 0.6, atol=1e-12)
    assert np.allclose(positions["SHV"].to_numpy(), 0.0, atol=1e-12)


def test_inverted_curve_routes_all_bond_to_SHV():
    """T10Y3M ≡ -50 bps → alloc_TLT=0 → pos_TLT=0, pos_SHV=bd_w."""
    r_eq, r_tlt, r_shv, sig = _make_streams(80, seed=29, sig_const=-0.5)
    _, positions, _, alloc = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0,
    )
    assert np.allclose(alloc.to_numpy(), 0.0, atol=1e-12)
    assert np.allclose(positions["TLT"].to_numpy(), 0.0, atol=1e-12)
    assert np.allclose(positions["SHV"].to_numpy(), 0.6, atol=1e-12)


def test_monthly_rebalance_holds_alloc_constant_within_window():
    """Within each 21-bar block the alloc must be CONSTANT (forward-fill)."""
    r_eq, r_tlt, r_shv, sig = _make_streams(120, seed=31)
    _, _, _, alloc = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=5, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0,
    )
    # First 21-bar block must be constant.
    block = alloc.dropna().iloc[:21]
    assert block.nunique() == 1, \
        f"alloc must be constant within rebalance window; got {block.unique()}"


def test_no_lookahead_changing_signal_at_t_does_not_affect_alloc_before_t():
    """Mutating signal at bar t must NOT change alloc at bar < t."""
    r_eq, r_tlt, r_shv, sig = _make_streams(80, seed=37)
    _, _, _, a1 = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=5, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0,
    )
    sig2 = sig.copy()
    sig2.iloc[-10:] = 5.0  # extreme spike at the end
    _, _, _, a2 = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig2,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=5, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0,
    )
    # First 65 bars must be unaffected (warm-up + lag protect against
    # lookahead in the early region).
    np.testing.assert_allclose(
        a1.iloc[:-10].to_numpy(),
        a2.iloc[:-10].to_numpy(),
        atol=1e-15, equal_nan=True,
    )


# ---------------------------------------------------------------------------
# Cross-library parity (G7 prerequisite)
# ---------------------------------------------------------------------------


def test_numpy_reference_matches_pandas_engine():
    """Hand-rolled numpy reference must match the pandas engine to 1e-10."""
    r_eq, r_tlt, r_shv, sig = _make_streams(500, seed=42)
    net_pd, positions_pd, scale_pd, alloc_pd = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0002,
    )
    net_np, positions_np, scale_np, alloc_np = apply_bond_carry_duration_timing_np(
        r_eq.to_numpy(), r_tlt.to_numpy(), r_shv.to_numpy(), sig.to_numpy(),
        eq_w=0.9, bd_w=0.6,
        smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(net_pd.to_numpy(), net_np, atol=1e-10)
    np.testing.assert_allclose(positions_pd["EQ"].to_numpy(), positions_np[:, 0], atol=1e-10)
    np.testing.assert_allclose(positions_pd["TLT"].to_numpy(), positions_np[:, 1], atol=1e-10)
    np.testing.assert_allclose(positions_pd["SHV"].to_numpy(), positions_np[:, 2], atol=1e-10)
    np.testing.assert_allclose(scale_pd.to_numpy(), scale_np, atol=1e-10)
    np.testing.assert_allclose(alloc_pd.to_numpy(), alloc_np, atol=1e-10)


# ---------------------------------------------------------------------------
# Domain smoke test
# ---------------------------------------------------------------------------


def test_realistic_run_produces_finite_metrics():
    """Smoke: 4y of synthetic returns produces a finite Sharpe / CAGR."""
    r_eq, r_tlt, r_shv, sig = _make_streams(252 * 4, seed=11)
    net, _, _, _ = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=0.9, bd_w=0.6,
        smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
        rebalance_bars=21, cost_bps_per_leg=0.0002,
    )
    assert len(net) > 200
    assert np.isfinite(net).all()
    # 0.9 SPY + 0.6 dynamic-bond on a synthetic positive-drift series → +Sharpe.
    sigma = net.std(ddof=0)
    assert sigma > 0
    assert net.mean() > 0


def test_input_alignment_required():
    """Reject mis-aligned indices (no silent NaN propagation)."""
    n = 60
    idx_a = pd.date_range("2010-01-04", periods=n, freq="B")
    idx_b = pd.date_range("2010-04-04", periods=n, freq="B")
    z_a = pd.Series(np.zeros(n), index=idx_a)
    z_b = pd.Series(np.zeros(n), index=idx_b)
    z_c = pd.Series(np.zeros(n), index=idx_b)
    sig = pd.Series(np.ones(n), index=idx_a)
    # No overlap of all 4 streams → expect ValueError or empty inner-join.
    with pytest.raises((ValueError,)):
        apply_bond_carry_duration_timing(
            z_a, z_b, z_c, sig,
            eq_w=0.9, bd_w=0.6,
            smoothing_days=21, lag_bars=1, ramp_max_bps=100.0,
            rebalance_bars=21, cost_bps_per_leg=0.0,
        )
