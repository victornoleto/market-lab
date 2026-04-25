"""Iter 041 — TDD specs for VIX-regime-conditional WEIGHTS on iter 037 base.

Locks the semantics of the regime-weight modulation BEFORE
implementation. The mechanism keeps total leverage constant at
``calm_leverage = sum(calm_weights)`` (or ``stress_leverage = sum(
stress_weights)``) within each regime, but shifts allocation across
the three legs based on a 1-day lagged VIX threshold:

    regime[t] = 1 if VIX_{t-1} < threshold else 0
    weight[t] = calm_weights if regime[t] == 1 else stress_weights

    pos_eq[t]  = weight[t]["eq_w"]
    pos_bd[t]  = weight[t]["bd_w"]
    pos_gld[t] = weight[t]["gld_w"]

    gross[t] = pos_eq*r_eq + pos_bd*r_bd + pos_gld*r_gld
    cost[t]  = (|∆pos_eq| + |∆pos_bd| + |∆pos_gld|) * cost_bps_per_leg
    net[t]   = gross - cost

Citations
---------
* `[risk_parity, ch.5]` — regime-conditional weight tilts.
* `[advances_fin_ml, ch.17-18]` — regime detection.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag rule (no look-ahead).
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "041-2026-04-25-0358-regime-weights-vix-static-stack"
ITER_037_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "037-2026-04-25-0224-ntsx-3leg-preserved-lev"
for p in (ITER_DIR, ITER_037_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from regime_weights_static_stack import apply_regime_weights_3leg  # noqa: E402
from numpy_reference_regime_weights import (  # noqa: E402
    apply_regime_weights_3leg_np,
)
from synth_stacked_etf_3leg import apply_static_stack_3leg  # noqa: E402


CALM = {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40}
STRESS = {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55}
COST_BPS = 0.0002


def _make_synth(n: int = 300, seed: int = 7) -> tuple[
    pd.Series, pd.Series, pd.Series, pd.Series,
]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_eq = pd.Series(rng.normal(0.0006, 0.012, n), index=idx, name="SPY")
    r_bd = pd.Series(rng.normal(0.00015, 0.004, n), index=idx, name="IEF")
    r_gld = pd.Series(rng.normal(0.00025, 0.010, n), index=idx, name="GLD")
    vix = pd.Series(15.0 + 8.0 * rng.random(n), index=idx, name="VIX")
    return r_eq, r_bd, r_gld, vix


# ---------------------------------------------------------------------------
# 1. Identity reduction — when calm and stress weights are identical the
#    output equals iter 037's static stack at those weights.
# ---------------------------------------------------------------------------


def test_identity_reduction_when_calm_equals_stress() -> None:
    r_eq, r_bd, r_gld, vix = _make_synth()
    same = {"eq_w": 0.60, "bd_w": 0.45, "gld_w": 0.45}
    net_regime, _, _, _ = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=same, stress_weights=same,
        vix_threshold=20.0, cost_bps_per_leg=COST_BPS,
    )
    net_static, _, _ = apply_static_stack_3leg(
        r_eq, r_bd, r_gld,
        eq_w=same["eq_w"], bd_short_w=same["bd_w"], bd_long_w=same["gld_w"],
        cost_bps_per_leg=COST_BPS,
    )
    np.testing.assert_allclose(
        net_regime.to_numpy(), net_static.to_numpy(), atol=1e-12, rtol=0.0,
        err_msg="identity reduction failed: regime engine ≠ static stack when weights are identical",
    )


# ---------------------------------------------------------------------------
# 2. No look-ahead — shifting VIX by 1 bar leaves NO bar's weight depending
#    on its own VIX value (regime[t] depends on VIX[t-1] only).
# ---------------------------------------------------------------------------


def test_lag_is_one_bar_strictly() -> None:
    r_eq, r_bd, r_gld, vix = _make_synth()
    # Construct a VIX that crosses threshold exactly at bar 50 (rises from 15 to 30).
    vix_step = vix.copy()
    vix_step.iloc[:50] = 15.0
    vix_step.iloc[50:] = 30.0
    _, positions, _, regime = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix_step,
        calm_weights=CALM, stress_weights=STRESS,
        vix_threshold=20.0, cost_bps_per_leg=0.0,
    )
    # bar 50 still uses VIX[49]=15 → regime=1 (calm) → eq_w=0.70
    assert regime.iloc[50] == 1, f"bar 50 regime should still be calm (uses VIX[49]=15); got {regime.iloc[50]}"
    assert positions["EQ"].iloc[50] == pytest.approx(CALM["eq_w"])
    # bar 51 uses VIX[50]=30 → regime=0 (stress) → eq_w=0.30
    assert regime.iloc[51] == 0, f"bar 51 regime should be stress (uses VIX[50]=30); got {regime.iloc[51]}"
    assert positions["EQ"].iloc[51] == pytest.approx(STRESS["eq_w"])


# ---------------------------------------------------------------------------
# 3. Calm-only fallback — when VIX[:] always below threshold, output equals
#    static stack at calm_weights.
# ---------------------------------------------------------------------------


def test_calm_only_fallback_equals_static_stack_calm() -> None:
    r_eq, r_bd, r_gld, vix = _make_synth()
    vix_low = vix.copy()
    vix_low[:] = 12.0
    net_regime, _, _, regime = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix_low,
        calm_weights=CALM, stress_weights=STRESS,
        vix_threshold=20.0, cost_bps_per_leg=COST_BPS,
    )
    net_calm, _, _ = apply_static_stack_3leg(
        r_eq, r_bd, r_gld,
        eq_w=CALM["eq_w"], bd_short_w=CALM["bd_w"], bd_long_w=CALM["gld_w"],
        cost_bps_per_leg=COST_BPS,
    )
    assert (regime == 1).all(), "every bar should be calm regime"
    np.testing.assert_allclose(
        net_regime.to_numpy(), net_calm.to_numpy(), atol=1e-12, rtol=0.0,
    )


# ---------------------------------------------------------------------------
# 4. Stress-only fallback — VIX always above threshold, output equals static
#    stack at stress_weights.
# ---------------------------------------------------------------------------


def test_stress_only_fallback_equals_static_stack_stress() -> None:
    r_eq, r_bd, r_gld, vix = _make_synth()
    vix_high = vix.copy()
    vix_high[:] = 35.0
    net_regime, _, _, regime = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix_high,
        calm_weights=CALM, stress_weights=STRESS,
        vix_threshold=20.0, cost_bps_per_leg=COST_BPS,
    )
    net_stress, _, _ = apply_static_stack_3leg(
        r_eq, r_bd, r_gld,
        eq_w=STRESS["eq_w"], bd_short_w=STRESS["bd_w"], bd_long_w=STRESS["gld_w"],
        cost_bps_per_leg=COST_BPS,
    )
    assert (regime == 0).all(), "every bar should be stress regime"
    np.testing.assert_allclose(
        net_regime.to_numpy(), net_stress.to_numpy(), atol=1e-12, rtol=0.0,
    )


# ---------------------------------------------------------------------------
# 5. Cross-library parity — pandas engine vs numpy reference (G7).
# ---------------------------------------------------------------------------


def test_cross_lib_parity_pandas_vs_numpy() -> None:
    r_eq, r_bd, r_gld, vix = _make_synth(n=500)
    net_pd, _, _, regime_pd = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=CALM, stress_weights=STRESS,
        vix_threshold=20.0, cost_bps_per_leg=COST_BPS,
    )
    # Build the same regime mask externally for numpy.
    vix_lag = vix.shift(1)
    vix_lag.iloc[0] = vix.iloc[0]
    regime_np = (vix_lag < 20.0).astype(int).to_numpy()
    np.testing.assert_array_equal(
        regime_pd.to_numpy(), regime_np,
        err_msg="regime mask mismatch between pandas engine and external numpy build",
    )
    net_np, _, _ = apply_regime_weights_3leg_np(
        r_eq.to_numpy(), r_bd.to_numpy(), r_gld.to_numpy(), regime_np,
        calm_weights=CALM, stress_weights=STRESS,
        cost_bps_per_leg=COST_BPS,
    )
    np.testing.assert_allclose(
        net_pd.to_numpy(), net_np, atol=1e-12, rtol=0.0,
        err_msg="pandas engine ≠ numpy reference at floating-point precision",
    )


# ---------------------------------------------------------------------------
# 6. Param-domain errors — negative weights, mismatched indices.
# ---------------------------------------------------------------------------


def test_negative_weight_raises() -> None:
    r_eq, r_bd, r_gld, vix = _make_synth()
    bad = {"eq_w": -0.10, "bd_w": 0.40, "gld_w": 0.40}
    with pytest.raises(ValueError, match="non-negative"):
        apply_regime_weights_3leg(
            r_eq, r_bd, r_gld, vix,
            calm_weights=bad, stress_weights=STRESS,
            vix_threshold=20.0,
        )


def test_index_mismatch_raises() -> None:
    r_eq, r_bd, r_gld, vix = _make_synth()
    r_bd_off = r_bd.iloc[:-5]
    with pytest.raises(ValueError, match="identical indices"):
        apply_regime_weights_3leg(
            r_eq, r_bd_off, r_gld, vix,
            calm_weights=CALM, stress_weights=STRESS,
            vix_threshold=20.0,
        )


# ---------------------------------------------------------------------------
# 7. Regime determinism — given fixed inputs, regime mask is deterministic
#    and idempotent under repeated calls.
# ---------------------------------------------------------------------------


def test_regime_assignment_is_deterministic() -> None:
    r_eq, r_bd, r_gld, vix = _make_synth()
    _, _, _, regime_a = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=CALM, stress_weights=STRESS,
        vix_threshold=20.0, cost_bps_per_leg=COST_BPS,
    )
    _, _, _, regime_b = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=CALM, stress_weights=STRESS,
        vix_threshold=20.0, cost_bps_per_leg=COST_BPS,
    )
    pd.testing.assert_series_equal(regime_a, regime_b)
