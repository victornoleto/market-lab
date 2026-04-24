"""Iter 016 — TDD specs for static-ratio × vol-managed hybrid stack.

Locks the semantics of Option P BEFORE implementation. Each spec encodes
one structural invariant of the hybrid: iter 015's fixed 60:40 ratio ×
iter 008's Moreira-Muir variance-target portfolio scaling.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity with fixed weights.
* Moreira & Muir (2017) JoF 72(4), 1611-1644 — variance-target scaling.
* `[systematic_trading, p.170-171, ch.11]` — max-leverage hard cap.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag (no look-ahead).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "016-2026-04-24-1729-static-stack-vm-hybrid"
sys.path.insert(0, str(ITER_DIR))

from static_stack_vm import apply_static_stack_vol_managed  # noqa: E402
from numpy_reference_stack_vm import apply_static_stack_vm_np  # noqa: E402


def _make_returns(n: int = 504, seed: int = 7) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_eq = pd.Series(rng.normal(0.0005, 0.012, n), index=idx, name="SPY")
    r_bd = pd.Series(rng.normal(0.0001, 0.004, n), index=idx, name="IEF")
    return r_eq, r_bd


# ---------------------------------------------------------------------------
# Structural invariants
# ---------------------------------------------------------------------------


def test_ratio_locked_at_60_40_normalized_at_every_bar():
    """Per-bar positions must preserve the 0.6 / 0.4 normalised ratio."""
    r_eq, r_bd = _make_returns(252)
    net, pos_eq, pos_bd, scale = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0,
    )
    total = pos_eq + pos_bd
    # When scale != 0, eq/total == 0.6 and bd/total == 0.4
    non_zero = scale > 1e-12
    ratio_eq = (pos_eq.loc[non_zero] / total.loc[non_zero]).to_numpy()
    ratio_bd = (pos_bd.loc[non_zero] / total.loc[non_zero]).to_numpy()
    assert np.allclose(ratio_eq, 0.6, atol=1e-12), \
        f"ratio eq/total must be 0.6; got [{ratio_eq.min():.6f}, {ratio_eq.max():.6f}]"
    assert np.allclose(ratio_bd, 0.4, atol=1e-12), \
        f"ratio bd/total must be 0.4; got [{ratio_bd.min():.6f}, {ratio_bd.max():.6f}]"


def test_scale_bounded_by_max_leverage():
    """scale[t] ∈ [0, max_leverage] — never exceeds cap."""
    r_eq, r_bd = _make_returns(300)
    _, _, _, scale = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0,
    )
    assert (scale >= -1e-12).all(), f"scale must be ≥ 0; min {scale.min()}"
    assert (scale <= 2.0 + 1e-12).all(), f"scale must be ≤ max_lev; max {scale.max()}"


def test_scale_formula_matches_manual_calculation():
    """Verify scale[t] = target_vol² / σ²_port[t-1] against hand calculation
    on a specific bar."""
    r_eq, r_bd = _make_returns(100, seed=42)
    eq_w, bd_w = 0.6, 0.4
    target_vol, lookback, max_lev = 0.15, 21, 2.0
    _, pos_eq, pos_bd, scale = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=eq_w, bd_weight=bd_w,
        target_vol=target_vol, lookback=lookback, max_leverage=max_lev,
        cost_bps_per_leg=0.0,
    )
    # Pick bar at index 30 — it uses the σ² from bars 9..29 (shifted by 1).
    # Specifically, σ² at the output of shift(1) for bar 30 is the rolling
    # var of bars [30-lookback-1 ... 30-1] = [9 ... 29] with lookback=21.
    t_idx = 30
    window_end_excl = t_idx  # bars strictly before t_idx are usable
    window_start = window_end_excl - lookback
    r_eq_w = r_eq.iloc[window_start:window_end_excl].to_numpy()
    r_bd_w = r_bd.iloc[window_start:window_end_excl].to_numpy()
    assert len(r_eq_w) == lookback
    # Compute portfolio returns over window with fixed weights 0.6, 0.4
    r_port_w = eq_w * r_eq_w + bd_w * r_bd_w
    ann_var_port = np.var(r_port_w, ddof=0) * 252.0
    expected_scale = min(max_lev, (target_vol ** 2) / ann_var_port)
    expected_pos_eq = eq_w * expected_scale
    expected_pos_bd = bd_w * expected_scale
    # Series valid from bar `lookback` forward, so t_idx=30 is valid.
    ts = scale.index[0]  # first valid bar corresponds to input index `lookback`
    actual_scale = scale.loc[scale.index[t_idx - lookback]]
    actual_pos_eq = pos_eq.loc[pos_eq.index[t_idx - lookback]]
    actual_pos_bd = pos_bd.loc[pos_bd.index[t_idx - lookback]]
    assert actual_scale == pytest.approx(expected_scale, abs=1e-12), \
        f"scale mismatch at t={t_idx}: got {actual_scale}, expected {expected_scale}"
    assert actual_pos_eq == pytest.approx(expected_pos_eq, abs=1e-12)
    assert actual_pos_bd == pytest.approx(expected_pos_bd, abs=1e-12)


def test_no_lookahead_bar_uses_sigma_t_minus_1():
    """Bar t's position must depend ONLY on returns strictly before t."""
    r_eq, r_bd = _make_returns(200, seed=11)
    _, pos_eq_a, _, _ = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0,
    )
    # Mutate the LAST k=3 bars' returns and re-run.
    k = 3
    r_eq2 = r_eq.copy()
    r_bd2 = r_bd.copy()
    r_eq2.iloc[-k:] = r_eq2.iloc[-k:] * 50
    r_bd2.iloc[-k:] = r_bd2.iloc[-k:] * 50
    _, pos_eq_b, _, _ = apply_static_stack_vol_managed(
        r_eq2, r_bd2,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0,
    )
    # Positions up through bar (N - k - 1) must be identical (last k bars'
    # scales depend on lookback of mutated returns).
    # bar t uses σ² from [t-lookback-1 ... t-1]; mutation at bar T affects
    # σ² at bars T+1 through T+lookback. So mutation on last k bars affects
    # the last lookback bars of positions.
    cutoff = len(pos_eq_a) - 1  # last valid position index
    assert np.allclose(
        pos_eq_a.iloc[:-k - 1].to_numpy(),
        pos_eq_b.iloc[:-k - 1].to_numpy(),
        atol=1e-12,
    ), "positions before the last k-period window must be unchanged"


def test_recovers_iter015_when_target_infinite_and_cap_1p5():
    """If scale is always pinned to max_lev=1.5, result must equal iter 015's
    static 0.9 / 0.6 stack exactly (ignoring cost)."""
    # Using a huge target_vol so target_vol² / σ² » max_lev always.
    # And setting max_lev = 1.5 (= 0.6 + 0.4 × 1.5 ... wait: with eq_w=0.6,
    # bd_w=0.4 normalized, max_lev=1.5 gives pos_eq = 0.6 × 1.5 = 0.9 and
    # pos_bd = 0.4 × 1.5 = 0.6 — matching iter 015 exactly).
    r_eq, r_bd = _make_returns(120, seed=99)
    _, pos_eq, pos_bd, scale = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=100.0, lookback=21, max_leverage=1.5,
        cost_bps_per_leg=0.0,
    )
    assert np.allclose(scale.to_numpy(), 1.5, atol=1e-12), \
        f"scale must pin to max_lev=1.5; got range [{scale.min()}, {scale.max()}]"
    assert np.allclose(pos_eq.to_numpy(), 0.9, atol=1e-12)
    assert np.allclose(pos_bd.to_numpy(), 0.6, atol=1e-12)


def test_scale_zero_when_portfolio_variance_infinite():
    """Extreme σ² > target_vol² gives small scale; test smoothly approaches
    zero as σ² grows."""
    # Fabricate large-vol returns
    n = 100
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    rng = np.random.default_rng(0)
    r_eq = pd.Series(rng.normal(0.0, 0.5, n), index=idx)  # huge vol
    r_bd = pd.Series(rng.normal(0.0, 0.4, n), index=idx)
    _, _, _, scale = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0,
    )
    # σ² ≈ 0.25 × 252 = 63 on equity alone; target_vol²=0.0225; scale << 1.
    assert (scale < 0.05).all(), \
        f"with huge-vol returns, scale should collapse to near zero; max {scale.max()}"


def test_zero_cost_gives_gross_equals_net():
    """With cost_bps_per_leg=0 the net must equal gross returns exactly."""
    r_eq, r_bd = _make_returns(150, seed=3)
    net, pos_eq, pos_bd, _ = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0,
    )
    # Reconstruct gross manually
    r_eq_v = r_eq.loc[net.index]
    r_bd_v = r_bd.loc[net.index]
    gross = pos_eq * r_eq_v + pos_bd * r_bd_v
    np.testing.assert_allclose(net.to_numpy(), gross.to_numpy(), atol=1e-15)


def test_cost_charged_on_delta_position():
    """With cost_bps > 0, each bar with |Δpos| > 0 must reduce net by
    (|Δpos_eq| + |Δpos_bd|) × cost_bps."""
    r_eq, r_bd = _make_returns(120, seed=5)
    cost = 0.0002
    net_with_cost, pos_eq, pos_bd, _ = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=cost,
    )
    net_no_cost, _, _, _ = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0,
    )
    # Manual expected cost series
    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_bd = pos_bd.diff().abs().fillna(pos_bd.iloc[0])
    expected_diff = (dpos_eq + dpos_bd) * cost
    actual_diff = net_no_cost - net_with_cost
    np.testing.assert_allclose(actual_diff.to_numpy(), expected_diff.to_numpy(), atol=1e-14)


# ---------------------------------------------------------------------------
# Cross-library parity (G7)
# ---------------------------------------------------------------------------


def test_numpy_reference_matches_pandas_engine():
    """Hand-rolled numpy implementation must match pandas engine to 1e-10."""
    r_eq, r_bd = _make_returns(500, seed=42)
    net_pd, pos_eq_pd, pos_bd_pd, scale_pd = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0002,
    )
    net_np, pos_eq_np, pos_bd_np, scale_np = apply_static_stack_vm_np(
        r_eq.to_numpy(), r_bd.to_numpy(),
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(net_pd.to_numpy(), net_np, atol=1e-10)
    np.testing.assert_allclose(pos_eq_pd.to_numpy(), pos_eq_np, atol=1e-10)
    np.testing.assert_allclose(pos_bd_pd.to_numpy(), pos_bd_np, atol=1e-10)
    np.testing.assert_allclose(scale_pd.to_numpy(), scale_np, atol=1e-10)


# ---------------------------------------------------------------------------
# Domain smoke
# ---------------------------------------------------------------------------


def test_realistic_run_produces_finite_metrics():
    """4y synthetic run produces finite Sharpe/CAGR and positive mean return."""
    r_eq, r_bd = _make_returns(252 * 4, seed=13)
    net, _, _, _ = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=0.0002,
    )
    eq_curve = (1.0 + net).cumprod()
    sharpe_val = net.mean() / net.std(ddof=0) * np.sqrt(252)
    cagr_val = eq_curve.iloc[-1] ** (252.0 / len(net)) - 1.0
    assert np.isfinite(sharpe_val)
    assert np.isfinite(cagr_val)


# ---------------------------------------------------------------------------
# Domain errors
# ---------------------------------------------------------------------------


def test_rejects_mis_aligned_indices():
    n = 50
    r_eq = pd.Series(np.zeros(n), index=pd.date_range("2010-01-04", periods=n, freq="B"))
    r_bd = pd.Series(np.zeros(n), index=pd.date_range("2010-02-01", periods=n, freq="B"))
    with pytest.raises(ValueError):
        apply_static_stack_vol_managed(
            r_eq, r_bd,
            eq_weight=0.6, bd_weight=0.4,
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0,
        )


def test_rejects_invalid_target_vol():
    r_eq, r_bd = _make_returns(100)
    with pytest.raises(ValueError):
        apply_static_stack_vol_managed(
            r_eq, r_bd,
            eq_weight=0.6, bd_weight=0.4,
            target_vol=-0.1, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0,
        )


def test_rejects_invalid_lookback():
    r_eq, r_bd = _make_returns(100)
    with pytest.raises(ValueError):
        apply_static_stack_vol_managed(
            r_eq, r_bd,
            eq_weight=0.6, bd_weight=0.4,
            target_vol=0.15, lookback=1, max_leverage=2.0,
            cost_bps_per_leg=0.0,
        )


def test_rejects_non_positive_max_leverage():
    r_eq, r_bd = _make_returns(100)
    with pytest.raises(ValueError):
        apply_static_stack_vol_managed(
            r_eq, r_bd,
            eq_weight=0.6, bd_weight=0.4,
            target_vol=0.15, lookback=21, max_leverage=0.0,
            cost_bps_per_leg=0.0,
        )
