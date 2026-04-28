"""Iter 042 — TDD specs for combined regime modulation (lev × weights).

Locks the semantics of the iter 042 CFG BEFORE running backtests. The
arithmetic is identical to iter 041's `apply_regime_weights_3leg`; what
changes is that each regime's weight tuple is rescaled so that total
leverage matches iter 038's regime-differential targets (1.700× calm
vs 1.000× stress). The relative composition within each regime
(eq:bd:gld ratios) is preserved verbatim from iter 041.

Specs:
    1. CFG total leverage matches iter 038 targets (calm 1.700, stress 1.000).
    2. CFG composition ratios match iter 041 within each regime.
    3. Identity reduction — equal calm and stress weights collapse to a
       single static stack.
    4. Cross-lib parity — pandas vs numpy reference identical to FP precision.
    5. Calm-only fallback equals single-stack at calm weights.
    6. Stress-only fallback equals single-stack at stress weights.
    7. Determinism — same inputs → same outputs idempotently.
    8. Asymmetry vs iter 041 — at the realised 65/35 calm/stress mix, the
       iter 042 average leverage is approximately equal to iter 041's,
       but conditional leverages differ (1.7 vs 1.5 calm, 1.0 vs 1.4 stress).

Citations
---------
* `[risk_parity, ch.5]` — dual-axis regime modulation.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* `[advances_fin_ml, p.162-164]` — VIX_{t-1} lag rule (no look-ahead).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_042_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "042-2026-04-25-0422-combined-regime-lev-weights"
ITER_041_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "041-2026-04-25-0358-regime-weights-vix-static-stack"
for p in (ITER_042_DIR, ITER_041_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from combined_regime_static_stack import apply_regime_weights_3leg  # noqa: E402
from numpy_reference_combined_regime import (  # noqa: E402
    apply_regime_weights_3leg_np,
)


# ---------------------------------------------------------------------------
# CFG fixtures (mirrors run_backtests.CFG)
# ---------------------------------------------------------------------------

CALM_WEIGHTS_042 = {"eq_w": 0.79333, "bd_w": 0.45333, "gld_w": 0.45333}
STRESS_WEIGHTS_042 = {"eq_w": 0.21429, "bd_w": 0.39286, "gld_w": 0.39286}

CALM_WEIGHTS_041 = {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40}
STRESS_WEIGHTS_041 = {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55}

VIX_THRESHOLD = 20.0


def _make_returns(n: int, seed: int = 17) -> tuple[pd.Series, pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_eq = pd.Series(rng.normal(0.0006, 0.012, n), index=idx, name="EQ")
    r_bd = pd.Series(rng.normal(0.0002, 0.004, n), index=idx, name="BD")
    r_gld = pd.Series(rng.normal(0.0003, 0.010, n), index=idx, name="GLD")
    return r_eq, r_bd, r_gld


def _make_vix(idx: pd.DatetimeIndex, seed: int = 17) -> pd.Series:
    rng = np.random.default_rng(seed + 1)
    base = 18.0 + 8.0 * np.abs(rng.standard_normal(len(idx))) * 0.5
    return pd.Series(base, index=idx, name="VIX")


# ---------------------------------------------------------------------------
# Spec 1 — CFG total leverage matches iter 038 targets
# ---------------------------------------------------------------------------


def test_calm_total_leverage_matches_iter038_lev_lo():
    total = sum(CALM_WEIGHTS_042.values())
    assert abs(total - 1.700) < 1e-3, f"calm total = {total}, expected 1.700"


def test_stress_total_leverage_matches_iter038_lev_hi():
    total = sum(STRESS_WEIGHTS_042.values())
    assert abs(total - 1.000) < 1e-3, f"stress total = {total}, expected 1.000"


# ---------------------------------------------------------------------------
# Spec 2 — composition ratios match iter 041 (eq:bd, eq:gld preserved)
# ---------------------------------------------------------------------------


def test_calm_composition_ratios_match_iter041():
    r042_eq_bd = CALM_WEIGHTS_042["eq_w"] / CALM_WEIGHTS_042["bd_w"]
    r041_eq_bd = CALM_WEIGHTS_041["eq_w"] / CALM_WEIGHTS_041["bd_w"]
    assert abs(r042_eq_bd - r041_eq_bd) < 1e-3
    r042_eq_gld = CALM_WEIGHTS_042["eq_w"] / CALM_WEIGHTS_042["gld_w"]
    r041_eq_gld = CALM_WEIGHTS_041["eq_w"] / CALM_WEIGHTS_041["gld_w"]
    assert abs(r042_eq_gld - r041_eq_gld) < 1e-3


def test_stress_composition_ratios_match_iter041():
    r042 = STRESS_WEIGHTS_042["eq_w"] / STRESS_WEIGHTS_042["bd_w"]
    r041 = STRESS_WEIGHTS_041["eq_w"] / STRESS_WEIGHTS_041["bd_w"]
    assert abs(r042 - r041) < 1e-3
    r042g = STRESS_WEIGHTS_042["bd_w"] / STRESS_WEIGHTS_042["gld_w"]
    r041g = STRESS_WEIGHTS_041["bd_w"] / STRESS_WEIGHTS_041["gld_w"]
    assert abs(r042g - r041g) < 1e-3


# ---------------------------------------------------------------------------
# Spec 3 — identity reduction (equal weights collapse to a single static stack)
# ---------------------------------------------------------------------------


def test_identity_reduction_when_calm_equals_stress():
    n = 200
    r_eq, r_bd, r_gld = _make_returns(n)
    vix = _make_vix(r_eq.index)
    same_w = {"eq_w": 0.79333, "bd_w": 0.45333, "gld_w": 0.45333}
    net, positions, scale, regime = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=same_w,
        stress_weights=same_w,
        vix_threshold=VIX_THRESHOLD,
        cost_bps_per_leg=0.0002,
    )
    expected_gross = (
        same_w["eq_w"] * r_eq + same_w["bd_w"] * r_bd + same_w["gld_w"] * r_gld
    )
    assert (positions["EQ"] == same_w["eq_w"]).all()
    assert (positions["BD"] == same_w["bd_w"]).all()
    assert (positions["GLD"] == same_w["gld_w"]).all()
    assert np.allclose(scale.values, sum(same_w.values()))
    initial_cost = (
        same_w["eq_w"] + same_w["bd_w"] + same_w["gld_w"]
    ) * 0.0002
    assert net.iloc[0] == pytest.approx(expected_gross.iloc[0] - initial_cost, abs=1e-12)
    assert np.allclose(net.iloc[1:].values, expected_gross.iloc[1:].values, atol=1e-12)


# ---------------------------------------------------------------------------
# Spec 4 — cross-lib parity (G7 propagated forward from iter 041)
# ---------------------------------------------------------------------------


def test_pandas_numpy_parity_floating_point():
    n = 600
    r_eq, r_bd, r_gld = _make_returns(n, seed=23)
    vix = _make_vix(r_eq.index, seed=23)
    net_pd, positions_pd, scale_pd, regime_pd = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=CALM_WEIGHTS_042,
        stress_weights=STRESS_WEIGHTS_042,
        vix_threshold=VIX_THRESHOLD,
        cost_bps_per_leg=0.0002,
    )
    regime_np = regime_pd.to_numpy().astype(int)
    net_np, positions_np, scale_np = apply_regime_weights_3leg_np(
        r_eq.to_numpy(), r_bd.to_numpy(), r_gld.to_numpy(), regime_np,
        calm_weights=CALM_WEIGHTS_042,
        stress_weights=STRESS_WEIGHTS_042,
        cost_bps_per_leg=0.0002,
    )
    assert np.allclose(net_pd.to_numpy(), net_np, atol=1e-12)
    assert np.allclose(positions_pd.to_numpy(), positions_np, atol=1e-12)
    assert np.allclose(scale_pd.to_numpy(), scale_np, atol=1e-12)


# ---------------------------------------------------------------------------
# Spec 5 — calm-only fallback (VIX always below threshold)
# ---------------------------------------------------------------------------


def test_calm_only_fallback_uses_calm_weights():
    n = 100
    r_eq, r_bd, r_gld = _make_returns(n, seed=5)
    idx = r_eq.index
    vix = pd.Series(10.0, index=idx, name="VIX")
    net, positions, scale, regime = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=CALM_WEIGHTS_042,
        stress_weights=STRESS_WEIGHTS_042,
        vix_threshold=VIX_THRESHOLD,
        cost_bps_per_leg=0.0002,
    )
    assert (regime == 1).all()
    assert np.allclose(positions["EQ"].values, CALM_WEIGHTS_042["eq_w"])
    assert np.allclose(positions["BD"].values, CALM_WEIGHTS_042["bd_w"])
    assert np.allclose(positions["GLD"].values, CALM_WEIGHTS_042["gld_w"])
    assert np.allclose(scale.values, sum(CALM_WEIGHTS_042.values()), atol=1e-9)


# ---------------------------------------------------------------------------
# Spec 6 — stress-only fallback (VIX always at/above threshold)
# ---------------------------------------------------------------------------


def test_stress_only_fallback_uses_stress_weights():
    n = 100
    r_eq, r_bd, r_gld = _make_returns(n, seed=9)
    idx = r_eq.index
    vix = pd.Series(40.0, index=idx, name="VIX")
    net, positions, scale, regime = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=CALM_WEIGHTS_042,
        stress_weights=STRESS_WEIGHTS_042,
        vix_threshold=VIX_THRESHOLD,
        cost_bps_per_leg=0.0002,
    )
    assert (regime == 0).all()
    assert np.allclose(positions["EQ"].values, STRESS_WEIGHTS_042["eq_w"])
    assert np.allclose(positions["BD"].values, STRESS_WEIGHTS_042["bd_w"])
    assert np.allclose(positions["GLD"].values, STRESS_WEIGHTS_042["gld_w"])
    assert np.allclose(scale.values, sum(STRESS_WEIGHTS_042.values()), atol=1e-9)


# ---------------------------------------------------------------------------
# Spec 7 — determinism (idempotent under repeated calls)
# ---------------------------------------------------------------------------


def test_determinism_idempotent():
    n = 250
    r_eq, r_bd, r_gld = _make_returns(n, seed=42)
    vix = _make_vix(r_eq.index, seed=42)
    out1 = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=CALM_WEIGHTS_042,
        stress_weights=STRESS_WEIGHTS_042,
        vix_threshold=VIX_THRESHOLD,
        cost_bps_per_leg=0.0002,
    )
    out2 = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, vix,
        calm_weights=CALM_WEIGHTS_042,
        stress_weights=STRESS_WEIGHTS_042,
        vix_threshold=VIX_THRESHOLD,
        cost_bps_per_leg=0.0002,
    )
    for a, b in zip(out1, out2):
        if isinstance(a, pd.DataFrame):
            assert a.equals(b)
        else:
            assert a.equals(b)


# ---------------------------------------------------------------------------
# Spec 8 — asymmetry vs iter 041 (avg lev preserved, conditional differs)
# ---------------------------------------------------------------------------


def test_iter042_amplifies_conditional_leverage_asymmetry_vs_iter041():
    """Conditional leverage range is amplified vs iter 041; expected
    average leverage at typical 65/35 calm/stress mix is preserved."""
    calm_lev_042 = sum(CALM_WEIGHTS_042.values())
    stress_lev_042 = sum(STRESS_WEIGHTS_042.values())
    calm_lev_041 = sum(CALM_WEIGHTS_041.values())
    stress_lev_041 = sum(STRESS_WEIGHTS_041.values())

    range_042 = calm_lev_042 - stress_lev_042
    range_041 = calm_lev_041 - stress_lev_041
    assert range_042 > range_041 * 5, (
        f"conditional range must be amplified vs iter 041; "
        f"042={range_042:.3f}, 041={range_041:.3f}"
    )

    calm_frac = 0.65
    stress_frac = 0.35
    avg_042 = calm_frac * calm_lev_042 + stress_frac * stress_lev_042
    avg_041 = calm_frac * calm_lev_041 + stress_frac * stress_lev_041
    assert abs(avg_042 - avg_041) < 0.05, (
        f"average leverage at 65/35 calm/stress mix should be ≈ preserved; "
        f"042={avg_042:.3f}, 041={avg_041:.3f}"
    )
