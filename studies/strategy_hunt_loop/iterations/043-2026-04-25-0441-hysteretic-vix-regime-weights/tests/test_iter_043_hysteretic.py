"""TDD specs for iter 043 — hysteretic VIX-regime weight stack.

The engine reduces to iter 041 when ``low_threshold == high_threshold``;
otherwise the Schmitt trigger introduces state persistence inside the
[low, high) band. These tests are written FIRST per Stage 3 of
PROMPT.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
ITER041_DIR = ITER_DIR.parent / "041-2026-04-25-0358-regime-weights-vix-static-stack"

sys.path.insert(0, str(ITER_DIR))
sys.path.insert(0, str(ITER041_DIR))

from regime_weights_hysteretic import (  # noqa: E402
    apply_regime_weights_hysteretic_3leg,
)
from numpy_reference_hysteretic import (  # noqa: E402
    apply_regime_weights_hysteretic_3leg_np,
    build_hysteretic_regime_np,
)
from regime_weights_static_stack import apply_regime_weights_3leg  # noqa: E402


CALM_W = {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40}
STRESS_W = {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55}


@pytest.fixture
def sample_returns():
    """500-bar synthetic returns with deterministic VIX path."""
    n = 500
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2010-01-04", periods=n)
    r_eq = pd.Series(rng.normal(0.0005, 0.012, n), index=idx)
    r_bd = pd.Series(rng.normal(0.0002, 0.005, n), index=idx)
    r_gld = pd.Series(rng.normal(0.0003, 0.010, n), index=idx)
    return r_eq, r_bd, r_gld


@pytest.fixture
def whipsaw_vix():
    """VIX path with multiple crossings of 18/20/22 — designed to
    distinguish hysteresis from binary gate."""
    n = 500
    idx = pd.bdate_range("2010-01-04", periods=n)
    # base ~17, sinusoidal sweep into the [18, 22] band so a binary
    # gate flips often and a hysteretic gate persists.
    t = np.arange(n)
    base = 17.0 + 4.0 * np.sin(t * 0.05) + 0.5 * np.sin(t * 0.7)
    return pd.Series(base, index=idx, name="VIX")


# ---------------------------------------------------------------------------
# 1. Identity reduction — low == high reduces to iter 041's binary gate
# ---------------------------------------------------------------------------


def test_identity_reduction_when_low_equals_high(sample_returns, whipsaw_vix):
    r_eq, r_bd, r_gld = sample_returns
    threshold = 20.0
    net_hys, _, _, regime_hys = apply_regime_weights_hysteretic_3leg(
        r_eq, r_bd, r_gld, whipsaw_vix,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=threshold, high_threshold=threshold,
    )
    net_bin, _, _, regime_bin = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, whipsaw_vix,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        vix_threshold=threshold,
    )
    np.testing.assert_array_equal(regime_hys.to_numpy(), regime_bin.to_numpy())
    np.testing.assert_allclose(net_hys.to_numpy(), net_bin.to_numpy(), atol=1e-12)


# ---------------------------------------------------------------------------
# 2. Hysteresis halves crossings — flips on whipsaw VIX strictly fewer
# ---------------------------------------------------------------------------


def test_hysteresis_reduces_flip_count(sample_returns, whipsaw_vix):
    r_eq, r_bd, r_gld = sample_returns
    _, _, _, regime_bin = apply_regime_weights_3leg(
        r_eq, r_bd, r_gld, whipsaw_vix,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        vix_threshold=20.0,
    )
    flips_bin = int(regime_bin.diff().abs().fillna(0).sum())

    _, _, _, regime_hys = apply_regime_weights_hysteretic_3leg(
        r_eq, r_bd, r_gld, whipsaw_vix,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=18.0, high_threshold=22.0,
    )
    flips_hys = int(regime_hys.diff().abs().fillna(0).sum())

    assert flips_hys <= flips_bin, (
        f"hysteresis must not increase crossings (binary={flips_bin}, hys={flips_hys})"
    )
    # On the whipsaw fixture the hysteretic gate flips strictly fewer.
    assert flips_hys < flips_bin, (
        f"on the whipsaw fixture, hysteresis should strictly reduce crossings "
        f"(binary={flips_bin}, hys={flips_hys})"
    )


# ---------------------------------------------------------------------------
# 3. State persistence inside the band — VIX in [18, 22) holds prior state
# ---------------------------------------------------------------------------


def test_state_persists_inside_band():
    """Construct a VIX that enters calm, drifts inside the band, then
    bumps above high — the regime must stay calm until the high crossing."""
    n = 30
    idx = pd.bdate_range("2010-01-04", periods=n)
    vix_path = [16.0] * 5 + [19.0, 19.5, 20.0, 20.5, 21.0, 21.5] + [21.9] * 9 + [23.0] * 10
    vix = pd.Series(vix_path, index=idx, name="VIX")
    r0 = pd.Series([0.0] * n, index=idx)

    _, _, _, regime = apply_regime_weights_hysteretic_3leg(
        r0, r0, r0, vix,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=18.0, high_threshold=22.0,
    )

    # Bars 0-4: vix=16 < low=18 → calm (1).
    assert regime.iloc[0:5].tolist() == [1, 1, 1, 1, 1]
    # Bars 5-19 (vix in [19, 21.9]): regime persists at calm.
    assert regime.iloc[5:20].tolist() == [1] * 15
    # Bar 20+: vix=23 ≥ 22 → stress (0). With the 1-bar lag the
    # transition observed at bar t depends on VIX at bar t-1.
    assert regime.iloc[21:].tolist() == [0] * (n - 21)


# ---------------------------------------------------------------------------
# 4. Calm → stress transition only via high threshold
# ---------------------------------------------------------------------------


def test_calm_to_stress_only_via_high():
    """In a pure-calm history (VIX always < high), the regime must
    never flip to stress, even if VIX briefly enters [low, high)."""
    n = 50
    idx = pd.bdate_range("2010-01-04", periods=n)
    vix = pd.Series([15.0, 16.0, 19.0, 21.5, 18.5, 17.0] + [16.5] * (n - 6),
                    index=idx, name="VIX")
    r0 = pd.Series([0.0] * n, index=idx)
    _, _, _, regime = apply_regime_weights_hysteretic_3leg(
        r0, r0, r0, vix,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=18.0, high_threshold=22.0,
    )
    assert (regime == 1).all(), f"regime should stay calm, got {regime.unique()}"


# ---------------------------------------------------------------------------
# 5. Stress → calm transition only via low threshold
# ---------------------------------------------------------------------------


def test_stress_to_calm_only_via_low():
    """If VIX starts at 30 (stress) and decays into [low, high), the
    regime must stay stress until VIX < low."""
    n = 50
    idx = pd.bdate_range("2010-01-04", periods=n)
    vix = pd.Series([30.0, 28.0, 25.0, 22.5, 20.0, 19.0] + [18.5] * (n - 6),
                    index=idx, name="VIX")
    r0 = pd.Series([0.0] * n, index=idx)
    _, _, _, regime = apply_regime_weights_hysteretic_3leg(
        r0, r0, r0, vix,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=18.0, high_threshold=22.0,
    )
    assert (regime == 0).all(), f"regime should stay stress, got {regime.unique()}"


# ---------------------------------------------------------------------------
# 6. No look-ahead — using VIX_t (not VIX_{t-1}) yields different result
# ---------------------------------------------------------------------------


def test_no_lookahead_causality(sample_returns, whipsaw_vix):
    """Regime[t] must depend only on VIX[<=t-1]. Mutating VIX[t] (today's
    value) should not change regime[s] for any s ≤ t."""
    r_eq, r_bd, r_gld = sample_returns

    _, _, _, regime_baseline = apply_regime_weights_hysteretic_3leg(
        r_eq, r_bd, r_gld, whipsaw_vix,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=18.0, high_threshold=22.0,
    )

    # Mutate a future bar (bar 100) by injecting a huge VIX spike there.
    t_mutate = 100
    vix_mutated = whipsaw_vix.copy()
    vix_mutated.iloc[t_mutate] = 80.0

    _, _, _, regime_mutated = apply_regime_weights_hysteretic_3leg(
        r_eq, r_bd, r_gld, vix_mutated,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=18.0, high_threshold=22.0,
    )
    # Bars 0..t_mutate must be identical (causality) — VIX[t_mutate] only
    # influences regime[t_mutate+1] onward through the 1-bar lag.
    np.testing.assert_array_equal(
        regime_baseline.iloc[: t_mutate + 1].to_numpy(),
        regime_mutated.iloc[: t_mutate + 1].to_numpy(),
    )
    # And the mutation should change at least one downstream bar.
    diffs = (
        regime_baseline.iloc[t_mutate + 1:] != regime_mutated.iloc[t_mutate + 1:]
    ).sum()
    assert diffs > 0, (
        "VIX mutation must propagate to ≥ 1 downstream regime bar via the lag"
    )


# ---------------------------------------------------------------------------
# 7. Cross-lib parity — pandas vs numpy reference identical to fp precision
# ---------------------------------------------------------------------------


def test_cross_lib_parity(sample_returns, whipsaw_vix):
    r_eq, r_bd, r_gld = sample_returns

    net_pd, _, _, regime_pd = apply_regime_weights_hysteretic_3leg(
        r_eq, r_bd, r_gld, whipsaw_vix,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=18.0, high_threshold=22.0,
    )

    vix_aligned = whipsaw_vix.reindex(r_eq.index, method="ffill").fillna(22.0)
    vix_lag = vix_aligned.shift(1)
    vix_lag.iloc[0] = vix_aligned.iloc[0]
    regime_np = build_hysteretic_regime_np(
        vix_lag.to_numpy(), low_threshold=18.0, high_threshold=22.0,
    )
    np.testing.assert_array_equal(regime_pd.to_numpy(), regime_np)

    net_np, _, _ = apply_regime_weights_hysteretic_3leg_np(
        r_eq.to_numpy(), r_bd.to_numpy(), r_gld.to_numpy(),
        regime_np,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(net_pd.to_numpy(), net_np, atol=1e-12, rtol=0)


# ---------------------------------------------------------------------------
# 8. Threshold ordering — low > high raises
# ---------------------------------------------------------------------------


def test_threshold_ordering_raises(sample_returns, whipsaw_vix):
    r_eq, r_bd, r_gld = sample_returns
    with pytest.raises(ValueError, match="low_threshold must be"):
        apply_regime_weights_hysteretic_3leg(
            r_eq, r_bd, r_gld, whipsaw_vix,
            calm_weights=CALM_W, stress_weights=STRESS_W,
            low_threshold=22.0, high_threshold=18.0,
        )


# ---------------------------------------------------------------------------
# 9. Calm-only fallback — VIX always < low collapses to single static stack
# ---------------------------------------------------------------------------


def test_calm_only_fallback(sample_returns):
    r_eq, r_bd, r_gld = sample_returns
    n = len(r_eq)
    idx = r_eq.index
    vix_low = pd.Series([10.0] * n, index=idx, name="VIX")

    net, positions, scale, regime = apply_regime_weights_hysteretic_3leg(
        r_eq, r_bd, r_gld, vix_low,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=18.0, high_threshold=22.0,
    )
    assert (regime == 1).all()
    np.testing.assert_allclose(positions["EQ"].to_numpy(), CALM_W["eq_w"])
    np.testing.assert_allclose(positions["BD"].to_numpy(), CALM_W["bd_w"])
    np.testing.assert_allclose(positions["GLD"].to_numpy(), CALM_W["gld_w"])
    expected_scale = sum(CALM_W.values())
    np.testing.assert_allclose(scale.to_numpy(), expected_scale)


# ---------------------------------------------------------------------------
# 10. Stress-only fallback — VIX always > high collapses to stress stack
# ---------------------------------------------------------------------------


def test_stress_only_fallback(sample_returns):
    r_eq, r_bd, r_gld = sample_returns
    n = len(r_eq)
    idx = r_eq.index
    vix_high = pd.Series([35.0] * n, index=idx, name="VIX")

    net, positions, scale, regime = apply_regime_weights_hysteretic_3leg(
        r_eq, r_bd, r_gld, vix_high,
        calm_weights=CALM_W, stress_weights=STRESS_W,
        low_threshold=18.0, high_threshold=22.0,
    )
    assert (regime == 0).all()
    np.testing.assert_allclose(positions["EQ"].to_numpy(), STRESS_W["eq_w"])
    np.testing.assert_allclose(positions["BD"].to_numpy(), STRESS_W["bd_w"])
    np.testing.assert_allclose(positions["GLD"].to_numpy(), STRESS_W["gld_w"])
    expected_scale = sum(STRESS_W.values())
    np.testing.assert_allclose(scale.to_numpy(), expected_scale)
