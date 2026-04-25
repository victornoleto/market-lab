"""TDD spec for iter 070 — continuous T10Y3M z-score inner-weight blend.

Verifies:

* Parameter validation (bounds, signs, range checks).
* Total exposure ≡ 1.0 every bar (NO leverage).
* w_qqqt[t] ∈ [w_min, w_max] always.
* α=0 → w_qqqt constant at midpoint (regime gate disabled).
* Monotonicity: for α > 0, low z → high w_qqqt (more trend in
  flat/inverted curve, recession risk).
* No peeking on T10Y3M (must use shift(1) on the spread itself
  AND on the rolling mean/std of the spread).
* Warmup: the first ``lookback_z`` bars where rolling stats are
  undefined fall back to z=0 (midpoint weight) — never NaN.
* Flip cost applied as 5bp · |Δw_qqqt|.
* Cross-lib parity (pandas vs numpy reference) within 1e-12 per bar.
* Output series has correct index, name, and length.

Citations
---------

* `[advances_fin_ml, p.162-164]` — strict shift(1) on regime signal.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, ch.17-18]` — regime detection methodology.
* Estrella & Mishkin (1998) RES 80(1) — T10Y3M as recession leading
  indicator.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from t10y3m_cont_inner_weight import combine_with_t10y3m_cont_inner_weight
from numpy_reference_iter070 import combine_with_t10y3m_cont_inner_weight_np


def _make_synthetic_inputs(seed: int = 42, n: int = 1500):
    """Build a deterministic 3-stream synthetic test fixture.

    n=1500 (~6 years business days) ensures the 1260-bar (5y) z-score
    rolling window is well-populated for the bulk of the series.
    """
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2010-01-04", periods=n, freq="B")
    r046 = pd.Series(rng.normal(0.0005, 0.010, n), index=idx, name="r_046")
    rqqqt = pd.Series(rng.normal(0.0006, 0.014, n), index=idx, name="r_qqqt")
    # T10Y3M oscillates with realistic dynamics: ranges roughly -1 to +3.
    t = np.arange(n)
    base = 1.5 + 1.2 * np.sin(t / 200.0) + 0.4 * np.sin(t / 50.0) + rng.normal(0, 0.1, n)
    spread = pd.Series(base, index=idx, name="term_spread")
    return r046, rqqqt, spread


def test_param_validation():
    """Invalid inputs raise ValueError."""
    r046, rqqqt, spread = _make_synthetic_inputs(n=100)
    with pytest.raises(ValueError):
        combine_with_t10y3m_cont_inner_weight(r046, rqqqt, spread, w_min=-0.01)
    with pytest.raises(ValueError):
        combine_with_t10y3m_cont_inner_weight(r046, rqqqt, spread, w_max=1.5)
    with pytest.raises(ValueError):
        # w_min > w_max is invalid
        combine_with_t10y3m_cont_inner_weight(r046, rqqqt, spread, w_min=0.30, w_max=0.10)
    with pytest.raises(ValueError):
        combine_with_t10y3m_cont_inner_weight(r046, rqqqt, spread, alpha=-0.01)
    with pytest.raises(ValueError):
        combine_with_t10y3m_cont_inner_weight(r046, rqqqt, spread, lookback_z=0)
    with pytest.raises(ValueError):
        combine_with_t10y3m_cont_inner_weight(r046, rqqqt, spread, cost_bps=-1.0)


def test_total_exposure_invariant_strict_one():
    """w_046[t] + w_qqqt[t] ≡ 1.0 every bar."""
    r046, rqqqt, spread = _make_synthetic_inputs()
    out = combine_with_t10y3m_cont_inner_weight(
        r046, rqqqt, spread, return_diagnostics=True
    )
    diag = out.attrs["diagnostics"]
    total = diag["w_046"] + diag["w_qqqt"]
    max_dev = float(np.max(np.abs(total - 1.0)))
    assert max_dev < 1e-12, (
        f"total exposure must be ≡ 1.0; got max |Σw - 1| = {max_dev:.2e}"
    )


def test_w_qqqt_within_bounds():
    """w_qqqt[t] ∈ [w_min, w_max] every bar — clip must work even at extreme z."""
    r046, rqqqt, _ = _make_synthetic_inputs()
    # Pathological spread series: huge swings → ensures z-scores can be far
    # outside the typical ±2σ band, so the clip in f(z) gets exercised.
    n = len(r046)
    rng = np.random.default_rng(7)
    spread = pd.Series(
        np.concatenate([np.zeros(500), 10.0 * np.ones(500), -10.0 * np.ones(n - 1000)]),
        index=r046.index,
        name="term_spread",
    )
    spread = spread + rng.normal(0, 0.01, n)
    out = combine_with_t10y3m_cont_inner_weight(
        r046, rqqqt, spread,
        w_min=0.05, w_max=0.20, alpha=0.25, lookback_z=252,
        return_diagnostics=True,
    )
    w_qqqt = out.attrs["diagnostics"]["w_qqqt"]
    assert w_qqqt.min() >= 0.05 - 1e-12, f"w_qqqt below w_min: {w_qqqt.min()}"
    assert w_qqqt.max() <= 0.20 + 1e-12, f"w_qqqt above w_max: {w_qqqt.max()}"


def test_alpha_zero_means_constant_midpoint_weight():
    """α=0 → w_qqqt is constant at midpoint = (w_min + w_max) / 2.

    With α=0, the regime gate is disabled and the strategy degenerates
    to a static weight — same total exposure, no flips.
    """
    r046, rqqqt, spread = _make_synthetic_inputs()
    out = combine_with_t10y3m_cont_inner_weight(
        r046, rqqqt, spread,
        w_min=0.05, w_max=0.20, alpha=0.0,
        return_diagnostics=True,
    )
    diag = out.attrs["diagnostics"]
    expected_mid = (0.05 + 0.20) / 2.0  # 0.125
    np.testing.assert_allclose(diag["w_qqqt"], expected_mid, atol=0.0)
    # No flips when α=0: cost must be all zeros.
    np.testing.assert_array_equal(diag["cost"], np.zeros_like(diag["cost"]))


def test_monotonicity_low_z_means_high_qqqt_weight():
    """For α > 0, low z (curve flat/inverted) → HIGH w_qqqt; high z → LOW w_qqqt.

    This direction matches iter 069's reverse-direction empirical
    finding (calm-light, stress-heavy) and the macro intuition:
    yield-curve inversion ⇒ recession risk ⇒ trend-following more
    valuable.
    """
    r046, rqqqt, _ = _make_synthetic_inputs()
    n = len(r046)
    # Build two extreme spread series with same volatility but DIFFERENT means.
    # First half: spread very low (z negative), second half: spread very high.
    spread_low = pd.Series(np.full(n, -2.0), index=r046.index, name="term_spread")
    spread_high = pd.Series(np.full(n, +2.0), index=r046.index, name="term_spread")
    # Add tiny noise so std > 0 in the rolling window (avoids /0).
    rng = np.random.default_rng(11)
    spread_low = spread_low + rng.normal(0, 0.05, n)
    spread_high = spread_high + rng.normal(0, 0.05, n)

    # Mix: train z-stats on a "normal" range, then inject extreme values.
    spread_normal = pd.Series(
        np.concatenate([np.zeros(800), -3.0 * np.ones(700)]) + rng.normal(0, 0.05, n),
        index=r046.index,
        name="term_spread",
    )

    out_normal = combine_with_t10y3m_cont_inner_weight(
        r046, rqqqt, spread_normal,
        w_min=0.05, w_max=0.20, alpha=0.25, lookback_z=252,
        return_diagnostics=True,
    )
    diag = out_normal.attrs["diagnostics"]
    z = diag["z"]
    w_qqqt = diag["w_qqqt"]
    # Restrict to bars where z != 0 (i.e. past warmup with non-trivial dispersion).
    valid = np.abs(z) > 0.1
    if valid.sum() < 50:
        pytest.skip("synthetic fixture didn't produce enough non-trivial z bars")
    # Check correlation: corr(z, w_qqqt) should be strongly NEGATIVE (low z → high w).
    z_sub = z[valid]
    w_sub = w_qqqt[valid]
    corr = np.corrcoef(z_sub, w_sub)[0, 1]
    assert corr < -0.5, f"expected strong negative corr(z, w_qqqt); got {corr:.3f}"


def test_no_peek_shift1_on_spread():
    """w_qqqt[t] must depend on T10Y3M[t-1], NOT on T10Y3M[t].

    Test by perturbing only the last bar of the spread: the output for
    bar t < n-1 must be identical to the unperturbed case. Only bar
    n-1's w_qqqt is allowed to depend on bar n-2's spread (which is
    unchanged), so it should also be identical. Bar n is the perturbed
    bar's value... but since there's no bar n, the perturbation only
    affects what would be bar n+1 in a longer series.

    To make the test concrete: perturb bar t=N-2 of the spread, then
    output bars 0..N-3 must be identical (bar N-2 only affects bar N-1
    via shift(1)).
    """
    r046, rqqqt, spread = _make_synthetic_inputs()
    out_a = combine_with_t10y3m_cont_inner_weight(
        r046, rqqqt, spread, lookback_z=252,
    )
    spread_perturbed = spread.copy()
    n = len(spread_perturbed)
    # Perturb bar n-2 by +5 stdev — huge change.
    spread_perturbed.iloc[n - 2] = spread_perturbed.iloc[n - 2] + 5.0 * spread.std()
    out_b = combine_with_t10y3m_cont_inner_weight(
        r046, rqqqt, spread_perturbed, lookback_z=252,
    )
    # Bars 0..N-3 must be unchanged (perturbation at N-2 only affects N-1
    # via shift(1) on spread; rolling stats up to N-3 don't see it either).
    np.testing.assert_array_equal(out_a.iloc[:-2].to_numpy(), out_b.iloc[:-2].to_numpy())


def test_warmup_falls_back_to_zero_z():
    """Within the warmup window, rolling stats are undefined → z=0 fallback
    means w_qqqt = midpoint, NOT NaN. Output must be free of NaNs.
    """
    r046, rqqqt, spread = _make_synthetic_inputs(n=300)
    out = combine_with_t10y3m_cont_inner_weight(
        r046, rqqqt, spread,
        lookback_z=252,
        return_diagnostics=True,
    )
    assert not out.isna().any(), "output must not contain NaNs (warmup must use z=0 fallback)"
    diag = out.attrs["diagnostics"]
    # The rolling window with min_periods=lookback_z=252 first becomes
    # complete at bar index lookback_z-1=251 (window covers bars 0..251).
    # So bars 0..250 are warmup (z=0); bar 251+ may have non-zero z.
    assert np.allclose(diag["z"][:251], 0.0, atol=1e-12), (
        "warmup region (first lookback_z - 1 bars) should use z=0 fallback"
    )


def test_flip_cost_applied_to_continuous_w_changes():
    """cost_bps · |Δw_qqqt[t]| applied per bar — works for continuous
    weight changes, not only step changes.
    """
    n = 10
    idx = pd.bdate_range("2020-01-06", periods=n, freq="B")
    r046 = pd.Series(np.zeros(n), index=idx)
    rqqqt = pd.Series(np.zeros(n), index=idx)
    # Construct spread series so z varies smoothly bar-to-bar (with no
    # warmup issue, use lookback_z=2).
    spread = pd.Series(
        [1.0, 1.0, 1.5, 0.5, 1.5, 1.0, 0.5, 1.0, 1.5, 1.0],
        index=idx,
        name="term_spread",
    )
    out = combine_with_t10y3m_cont_inner_weight(
        r046, rqqqt, spread,
        w_min=0.05, w_max=0.20, alpha=0.25,
        lookback_z=2, cost_bps=5.0,
        return_diagnostics=True,
    )
    diag = out.attrs["diagnostics"]
    delta_w = diag["delta_w"]
    cost = diag["cost"]
    # cost must equal cost_bps * 1e-4 * |Δw_qqqt| identically.
    np.testing.assert_allclose(cost, 5.0 * 1e-4 * delta_w, atol=1e-15)
    # And the per-bar return = w_046 * 0 + w_qqqt * 0 - cost = -cost (since both inputs are 0).
    np.testing.assert_allclose(out.to_numpy(), -cost, atol=1e-15)


def test_crosslib_parity_pandas_vs_numpy():
    """Pandas engine and numpy reference produce identical outputs
    bar-by-bar within 1e-12 (G7 satisfied trivially)."""
    r046, rqqqt, spread = _make_synthetic_inputs(seed=99)
    pd_out = combine_with_t10y3m_cont_inner_weight(
        r046, rqqqt, spread,
        w_min=0.05, w_max=0.20, alpha=0.25, lookback_z=252, cost_bps=5.0,
    )
    common = pd_out.index
    a = r046.loc[common].to_numpy()
    b = rqqqt.loc[common].to_numpy()
    s_aligned = spread.reindex(common).ffill().bfill().to_numpy()
    np_out = combine_with_t10y3m_cont_inner_weight_np(
        a, b, s_aligned,
        w_min=0.05, w_max=0.20, alpha=0.25, lookback_z=252, cost_bps=5.0,
    )
    np.testing.assert_allclose(pd_out.to_numpy(), np_out, atol=1e-12)


def test_output_has_correct_index_and_name():
    """Output must be a pd.Series indexed on r_046 ∩ r_qqqt with name
    'iter070_t10y3m_cont'."""
    r046, rqqqt, spread = _make_synthetic_inputs(n=300)
    out = combine_with_t10y3m_cont_inner_weight(r046, rqqqt, spread)
    assert isinstance(out, pd.Series)
    assert out.name == "iter070_t10y3m_cont"
    assert out.index.equals(r046.index.intersection(rqqqt.index))


def test_default_alpha_is_positive():
    """Default alpha is 0.25 (positive, monotonic-decreasing in z direction).
    Guard against accidental copy-paste of α=0 default."""
    import inspect
    sig = inspect.signature(combine_with_t10y3m_cont_inner_weight)
    assert sig.parameters["alpha"].default == pytest.approx(0.25)
    assert sig.parameters["w_min"].default == pytest.approx(0.05)
    assert sig.parameters["w_max"].default == pytest.approx(0.20)
    assert sig.parameters["lookback_z"].default == 1260
    assert sig.parameters["cost_bps"].default == pytest.approx(5.0)
