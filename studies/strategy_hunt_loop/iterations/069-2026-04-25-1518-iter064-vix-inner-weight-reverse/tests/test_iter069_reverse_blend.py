"""TDD spec for iter 069 reverse-direction VIX-conditional inner-weight blend.

Verifies:

* Calm bars (VIX[t-1] < threshold) get w_qqqt = 0.05 (REVERSED from iter 068).
* Stress bars (VIX[t-1] >= threshold) get w_qqqt = 0.20.
* Total exposure ≡ 1.0 every bar (no leverage).
* Bit-identity: iter 069's combiner with calm=0.05/stress=0.20 produces
  the same numerical output as iter 068's combiner CALLED WITH SWAPPED
  WEIGHTS — proves engine is unchanged.
* Cross-lib parity vs the iter 068 numpy reference.
* Flip cost charged correctly on regime transitions.

Citations
---------

* iter 068 final report — empirical KILL I conditional-Sharpe finding.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

ITER_068_DIR = ITER_DIR.parents[0] / "068-2026-04-25-1758-iter064-vix-inner-weight-swap"
sys.path.insert(0, str(ITER_068_DIR))

from iter069_reverse_blend import combine_reverse
from vix_inner_weight import combine_with_vix_inner_weight  # iter 068's engine
from numpy_reference_iter068 import combine_with_vix_inner_weight_np  # iter 068's numpy ref


def _make_synthetic_inputs(seed: int = 42, n: int = 1000):
    """Build a deterministic 3-stream synthetic test fixture."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2010-01-04", periods=n, freq="B")
    # Two distinct return streams with different vols.
    r046 = pd.Series(rng.normal(0.0005, 0.010, n), index=idx, name="r_046")
    rqqqt = pd.Series(rng.normal(0.0006, 0.014, n), index=idx, name="r_qqqt")
    # VIX path: oscillates ~15-30 with regime-style persistence.
    base = 15 + 8 * np.sin(np.arange(n) / 80.0) + rng.normal(0, 1.5, n)
    base = np.clip(base, 10.0, 45.0)
    vix = pd.Series(base, index=idx, name="VIX")
    return r046, rqqqt, vix


def test_calm_bars_get_low_qqqt_weight():
    """REVERSED direction: when VIX[t-1] < 20 (calm), w_qqqt = 0.05."""
    r046, rqqqt, vix = _make_synthetic_inputs()
    out = combine_reverse(r046, rqqqt, vix,
                          w_qqqt_calm=0.05, w_qqqt_stress=0.20,
                          vix_threshold=20.0, return_diagnostics=True)
    diag = out.attrs["diagnostics"]
    is_stress = diag["is_stress"]
    w_qqqt = diag["w_qqqt"]

    # Calm bars (~ ~70% of synthetic series) must carry the LOW weight.
    calm_mask = ~is_stress
    assert calm_mask.sum() > 100, "fixture must produce some calm bars"
    np.testing.assert_allclose(w_qqqt[calm_mask], 0.05, atol=0.0)


def test_stress_bars_get_high_qqqt_weight():
    """REVERSED direction: when VIX[t-1] >= 20 (stress), w_qqqt = 0.20."""
    r046, rqqqt, vix = _make_synthetic_inputs()
    out = combine_reverse(r046, rqqqt, vix,
                          w_qqqt_calm=0.05, w_qqqt_stress=0.20,
                          vix_threshold=20.0, return_diagnostics=True)
    diag = out.attrs["diagnostics"]
    is_stress = diag["is_stress"]
    w_qqqt = diag["w_qqqt"]

    assert is_stress.sum() > 100, "fixture must produce some stress bars"
    np.testing.assert_allclose(w_qqqt[is_stress], 0.20, atol=0.0)


def test_total_exposure_invariant_strict_one():
    """w_046[t] + w_qqqt[t] ≡ 1.0 every bar."""
    r046, rqqqt, vix = _make_synthetic_inputs()
    out = combine_reverse(r046, rqqqt, vix, return_diagnostics=True)
    diag = out.attrs["diagnostics"]
    total = diag["w_046"] + diag["w_qqqt"]
    assert np.max(np.abs(total - 1.0)) == 0.0, (
        f"total exposure must be strictly 1.0; got max |Σw - 1| = "
        f"{np.max(np.abs(total - 1.0)):.2e}"
    )


def test_bit_identity_to_iter068_engine_with_swapped_weights():
    """iter 069 combine_reverse must produce numerically identical output
    to iter 068's `combine_with_vix_inner_weight` called with the same
    swapped weights — proves no engine drift.
    """
    r046, rqqqt, vix = _make_synthetic_inputs(seed=123)
    out_069 = combine_reverse(
        r046, rqqqt, vix,
        w_qqqt_calm=0.05, w_qqqt_stress=0.20,
        vix_threshold=20.0, cost_bps=5.0,
    )
    out_068_with_swap = combine_with_vix_inner_weight(
        r046, rqqqt, vix,
        w_qqqt_calm=0.05, w_qqqt_stress=0.20,
        vix_threshold=20.0, cost_bps=5.0,
    )
    np.testing.assert_array_equal(out_069.to_numpy(), out_068_with_swap.to_numpy())


def test_crosslib_parity_vs_numpy_reference():
    """iter 069 (pandas) vs iter 068's numpy reference, both with reversed
    weights, must produce CAGR within 3 pp (G7 standard) and per-bar
    return diff < 1e-12.
    """
    r046, rqqqt, vix = _make_synthetic_inputs(seed=7)
    pd_out = combine_reverse(
        r046, rqqqt, vix,
        w_qqqt_calm=0.05, w_qqqt_stress=0.20,
        vix_threshold=20.0, cost_bps=5.0,
    )
    common = pd_out.index
    a = r046.loc[common].to_numpy()
    b = rqqqt.loc[common].to_numpy()
    v_aligned = vix.reindex(common).ffill().bfill().to_numpy()

    np_out = combine_with_vix_inner_weight_np(
        a, b, v_aligned,
        w_qqqt_calm=0.05, w_qqqt_stress=0.20,
        vix_threshold=20.0, cost_bps=5.0,
    )

    np.testing.assert_allclose(pd_out.to_numpy(), np_out, atol=1e-12)


def test_flip_cost_charged_on_regime_transition():
    """When regime flips between calm (0.05) and stress (0.20), the flip
    cost = cost_bps * 1e-4 * |Δw_qqqt| = 5e-4 * 0.15 = 7.5e-5 must
    appear as a single-bar drag.
    """
    n = 5
    idx = pd.bdate_range("2020-01-06", periods=n, freq="B")
    r046 = pd.Series(np.zeros(n), index=idx)
    rqqqt = pd.Series(np.zeros(n), index=idx)
    # VIX path: 10, 10, 30, 30, 10 → bar-2 (stress entry, calm→stress flip)
    # and bar-4 (calm re-entry, stress→calm flip) carry the flip cost.
    vix = pd.Series([10.0, 10.0, 30.0, 30.0, 10.0], index=idx)

    out = combine_reverse(
        r046, rqqqt, vix,
        w_qqqt_calm=0.05, w_qqqt_stress=0.20,
        vix_threshold=20.0, cost_bps=5.0,
        return_diagnostics=True,
    )
    cost = out.attrs["diagnostics"]["cost"]
    delta_w = out.attrs["diagnostics"]["delta_w"]

    # bar 0: prior weight assumed = current → no flip
    # bar 1: VIX[t-1]=10<20 calm; prior bar calm → no flip
    # bar 2: VIX[t-1]=10<20 calm; prior bar calm → STILL no flip (lag!)
    # bar 3: VIX[t-1]=30>=20 stress; prior bar calm → FLIP (Δ=0.15)
    # bar 4: VIX[t-1]=30>=20 stress; prior bar stress → no flip
    expected_flip_cost = 5.0 * 1e-4 * 0.15  # = 7.5e-5
    assert delta_w[3] == pytest.approx(0.15)
    assert cost[3] == pytest.approx(expected_flip_cost)
    # The other bars must carry zero cost (no |Δw_qqqt|).
    np.testing.assert_array_equal(cost[[0, 1, 2, 4]], np.zeros(4))


def test_combiner_param_validation():
    """Defensive checks on bad inputs (preserved from iter 068)."""
    r046, rqqqt, vix = _make_synthetic_inputs(n=100)
    with pytest.raises(ValueError):
        combine_reverse(r046, rqqqt, vix, w_qqqt_calm=-0.01)
    with pytest.raises(ValueError):
        combine_reverse(r046, rqqqt, vix, w_qqqt_stress=1.5)
    with pytest.raises(ValueError):
        combine_reverse(r046, rqqqt, vix, vix_threshold=-1.0)
    with pytest.raises(ValueError):
        combine_reverse(r046, rqqqt, vix, cost_bps=-1.0)


def test_default_weights_are_reversed_from_iter068():
    """iter 069's default weights are the REVERSE of iter 068's defaults.

    iter 068 default: calm=0.20, stress=0.05.
    iter 069 default: calm=0.05, stress=0.20.

    This test guards against accidental copy-paste regression.
    """
    import inspect
    sig = inspect.signature(combine_reverse)
    assert sig.parameters["w_qqqt_calm"].default == 0.05
    assert sig.parameters["w_qqqt_stress"].default == 0.20
