"""Iter 015 — TDD specs for synthetic NTSX (90/60 SPY+IEF stack).

Locks the semantics of the static return-stacking primitive BEFORE
implementation. Each spec encodes one structural invariant.

Citations
---------
* `[risk_parity, p.5, p.10-11, ch.1]` — risk-parity / fixed-weight stack.
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
    "015-2026-04-24-1704-return-stacked-static-ntsx"
sys.path.insert(0, str(ITER_DIR))

from synth_stacked_etf import apply_static_stack  # noqa: E402
from numpy_reference_stacked import apply_static_stack_np  # noqa: E402


def _make_returns(n: int = 252, seed: int = 7) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_eq = pd.Series(rng.normal(0.0005, 0.012, n), index=idx, name="SPY")
    r_bd = pd.Series(rng.normal(0.0001, 0.004, n), index=idx, name="IEF")
    return r_eq, r_bd


# ---------------------------------------------------------------------------
# Static-weight invariants
# ---------------------------------------------------------------------------


def test_static_weights_sum_to_total_leverage():
    """At every bar, equity_pos + bond_pos == eq_w + bd_w (= 1.5)."""
    r_eq, r_bd = _make_returns(60)
    net, positions, scale = apply_static_stack(
        r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0,
    )
    total = positions["EQ"] + positions["BD"]
    assert np.allclose(total.to_numpy(), 1.5, atol=1e-12), \
        f"positions must sum to 1.5 at every bar; got range [{total.min():.6f}, {total.max():.6f}]"
    assert np.allclose(scale.to_numpy(), 1.5, atol=1e-12), \
        "scale must equal eq_w+bd_w (no vol-management here)"


def test_position_components_match_input_weights():
    """Per-leg positions must equal exact pre-committed weights."""
    r_eq, r_bd = _make_returns(40)
    _, positions, _ = apply_static_stack(
        r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0,
    )
    assert np.allclose(positions["EQ"].to_numpy(), 0.9, atol=1e-12)
    assert np.allclose(positions["BD"].to_numpy(), 0.6, atol=1e-12)


# ---------------------------------------------------------------------------
# Returns / cost / lookahead
# ---------------------------------------------------------------------------


def test_zero_returns_produce_zero_net():
    """If both legs are constant-zero return, net must be zero (modulo costs)."""
    n = 100
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    z = pd.Series(np.zeros(n), index=idx)
    net, _, _ = apply_static_stack(z, z, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0)
    assert np.allclose(net.to_numpy(), 0.0, atol=1e-15)


def test_equity_only_recovers_input_at_eq_weight_one():
    """Degenerate eq_w=1, bd_w=0 → net == r_eq exactly (no cost)."""
    r_eq, r_bd = _make_returns(80)
    net, positions, _ = apply_static_stack(
        r_eq, r_bd, eq_w=1.0, bd_w=0.0, cost_bps_per_leg=0.0,
    )
    assert np.allclose(positions["EQ"].to_numpy(), 1.0, atol=1e-12)
    assert np.allclose(positions["BD"].to_numpy(), 0.0, atol=1e-12)
    assert np.allclose(net.to_numpy(), r_eq.to_numpy(), atol=1e-15)


def test_no_lookahead_position_at_t_uses_no_future_data():
    """Position at bar t must be deterministic from weights only (no signal),
    so altering returns at bar t+k must not affect positions at bar < t+k."""
    r_eq, r_bd = _make_returns(50)
    _, positions_a, _ = apply_static_stack(
        r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0,
    )
    # Mutate the LAST 5 bars of returns.
    r_eq2 = r_eq.copy()
    r_bd2 = r_bd.copy()
    r_eq2.iloc[-5:] = r_eq2.iloc[-5:] * 100
    r_bd2.iloc[-5:] = r_bd2.iloc[-5:] * 100
    _, positions_b, _ = apply_static_stack(
        r_eq2, r_bd2, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0,
    )
    # Positions on first 45 bars must be identical (no lookahead).
    assert np.allclose(
        positions_a.iloc[:-5].to_numpy(),
        positions_b.iloc[:-5].to_numpy(),
        atol=1e-15,
    )


def test_cost_charged_only_on_initial_setup_when_static():
    """Static fixed weights mean ∆pos == 0 every bar after t=0; total cost
    equals (eq_w + bd_w) × cost_bps_per_leg, independent of n_bars."""
    r_eq, r_bd = _make_returns(252)
    cost_bps = 0.0002
    net_with_cost, _, _ = apply_static_stack(
        r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=cost_bps,
    )
    net_no_cost, _, _ = apply_static_stack(
        r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0,
    )
    diff = (net_no_cost - net_with_cost).sum()
    expected_total_cost = (0.9 + 0.6) * cost_bps  # only the t=0 setup leg
    assert diff == pytest.approx(expected_total_cost, abs=1e-15), \
        f"static stack cost should equal one-time setup; got {diff:.10f} vs {expected_total_cost:.10f}"


# ---------------------------------------------------------------------------
# Cross-library parity (G7 prerequisite)
# ---------------------------------------------------------------------------


def test_numpy_reference_matches_pandas_engine():
    """Hand-rolled numpy reference must match the pandas engine to 1e-12."""
    r_eq, r_bd = _make_returns(500, seed=42)
    net_pd, positions_pd, scale_pd = apply_static_stack(
        r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
    )
    net_np, positions_np, scale_np = apply_static_stack_np(
        r_eq.to_numpy(), r_bd.to_numpy(),
        eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
    )
    assert net_np.shape == (len(r_eq),)
    np.testing.assert_allclose(net_pd.to_numpy(), net_np, atol=1e-12)
    np.testing.assert_allclose(positions_pd["EQ"].to_numpy(), positions_np[:, 0], atol=1e-12)
    np.testing.assert_allclose(positions_pd["BD"].to_numpy(), positions_np[:, 1], atol=1e-12)
    np.testing.assert_allclose(scale_pd.to_numpy(), scale_np, atol=1e-12)


# ---------------------------------------------------------------------------
# Domain-level smoke test
# ---------------------------------------------------------------------------


def test_realistic_run_produces_finite_metrics():
    """Smoke test: 4y of synthetic returns produces a finite Sharpe / CAGR."""
    r_eq, r_bd = _make_returns(252 * 4, seed=11)
    net, _, _ = apply_static_stack(
        r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
    )
    eq_curve = (1.0 + net).cumprod()
    sharpe_val = net.mean() / net.std(ddof=0) * np.sqrt(252)
    cagr_val = eq_curve.iloc[-1] ** (252.0 / len(net)) - 1.0
    assert np.isfinite(sharpe_val)
    assert np.isfinite(cagr_val)
    # 0.9 SPY + 0.6 IEF synthetic returns should have positive expected return
    # given the drift baked into _make_returns.
    assert net.mean() > 0


def test_input_index_alignment_required():
    """Must reject mis-aligned indices (no silent NaN propagation)."""
    n = 50
    r_eq = pd.Series(np.zeros(n), index=pd.date_range("2010-01-04", periods=n, freq="B"))
    r_bd = pd.Series(np.zeros(n), index=pd.date_range("2010-02-01", periods=n, freq="B"))
    with pytest.raises((ValueError, KeyError)):
        apply_static_stack(r_eq, r_bd, eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0)
