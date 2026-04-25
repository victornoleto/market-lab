"""TDD tests for iter 063 — internal-LETF UPRO substitution on iter 058 anchor.

Covers:
* Identity reduction at leverage=1, expense=0, calm=stress=iter041
  canonical → iter 041 stream reproducible.
* Synth UPRO formula (vendored from iter 062 — sanity).
* Equity-exposure preservation at iter 063 weights.
* combine_iter046_letf reduces to inputs at edge weights.
* combine_iter058_letf reduces to inputs at edge weights.
* G7 cross-lib: pandas wrapper vs pure-numpy reference, ≤ 3 pp parity.
* iter 058 reproduction at leverage=1 (sanity check the engine
  matches iter 058's combine pattern).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
ITER_062_DIR = ITER_DIR.parents[0] / "062-2026-04-25-1220-iter037-upro-substitution-internal-letf"
ITER_041_DIR = ITER_DIR.parents[0] / "041-2026-04-25-0358-regime-weights-vix-static-stack"
for _p in (ITER_DIR, ITER_062_DIR, ITER_041_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from iter041_letf import (  # noqa: E402
    ITER063_CALM_WEIGHTS,
    ITER063_STRESS_WEIGHTS,
    build_letf_returns,
    compute_iter041_letf_returns,
)
from combine_iter058_letf import (  # noqa: E402
    combine_iter046_letf,
    combine_iter058_letf,
)
from numpy_reference_iter063 import (  # noqa: E402
    apply_regime_weights_3leg_np,
    combine_three_streams_np,
    combine_two_streams_np,
    synth_letf_returns_np,
)
from synth_letf_3leg import synth_upro_returns  # noqa: E402
from regime_weights_static_stack import apply_regime_weights_3leg  # noqa: E402


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def small_returns_window():
    """30-bar synthetic window with realistic drift + vol."""
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-02", periods=30, freq="B")
    r_spy = pd.Series(rng.normal(0.0006, 0.012, 30), index=idx, name="r_spy")
    r_bd = pd.Series(rng.normal(0.00015, 0.0035, 30), index=idx, name="r_bd")
    r_gld = pd.Series(rng.normal(0.0004, 0.010, 30), index=idx, name="r_gld")
    vix = pd.Series(
        np.clip(15 + rng.normal(0, 5, 30), 8, 50), index=idx, name="vix",
    )
    return r_spy, r_bd, r_gld, vix


# -----------------------------------------------------------------------------
# Synth-UPRO formula sanity (vendored)
# -----------------------------------------------------------------------------


def test_synth_letf_zero_expense_is_3x_spy(small_returns_window):
    r_spy, *_ = small_returns_window
    out = synth_upro_returns(r_spy, leverage=3.0, expense_ratio=0.0)
    np.testing.assert_allclose(out.values, 3.0 * r_spy.values, atol=1e-15)


def test_synth_letf_numpy_pandas_parity(small_returns_window):
    r_spy, *_ = small_returns_window
    pd_out = synth_upro_returns(r_spy, leverage=3.0, expense_ratio=0.0091)
    np_out = synth_letf_returns_np(r_spy.values, leverage=3.0, expense_ratio=0.0091)
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-15)


# -----------------------------------------------------------------------------
# Equity-exposure preservation
# -----------------------------------------------------------------------------


def test_iter063_calm_weights_preserve_equity_exposure():
    """0.2333... × 3 = 0.70 SPY-equiv (iter 041's calm equity)."""
    spy_equiv = ITER063_CALM_WEIGHTS["eq_w"] * 3.0
    assert spy_equiv == pytest.approx(0.70, abs=1e-12)


def test_iter063_stress_weights_preserve_equity_exposure():
    """0.10 × 3 = 0.30 SPY-equiv (iter 041's stress equity)."""
    spy_equiv = ITER063_STRESS_WEIGHTS["eq_w"] * 3.0
    assert spy_equiv == pytest.approx(0.30, abs=1e-12)


def test_iter063_calm_total_nav_is_1_50():
    """Calm regime total NAV = 1.50 (matches iter 041 canonical)."""
    s = sum(ITER063_CALM_WEIGHTS.values())
    assert s == pytest.approx(1.50, abs=1e-12)


def test_iter063_stress_total_nav_is_1_40():
    """Stress regime total NAV = 1.40 (matches iter 041 canonical)."""
    s = sum(ITER063_STRESS_WEIGHTS.values())
    assert s == pytest.approx(1.40, abs=1e-12)


# -----------------------------------------------------------------------------
# build_letf_returns behavior
# -----------------------------------------------------------------------------


def test_build_letf_returns_pure_synth_when_no_real(small_returns_window):
    """real_letf_returns=None → pure synth output over the SPY window."""
    r_spy, *_ = small_returns_window
    out = build_letf_returns(r_spy, real_letf_returns=None,
                             leverage=3.0, expense_ratio=0.0091)
    expected = synth_upro_returns(r_spy, leverage=3.0, expense_ratio=0.0091)
    np.testing.assert_allclose(out.values, expected.values, atol=1e-15)


def test_build_letf_returns_splices_real_after_synth(small_returns_window):
    """When real LETF inception falls inside the SPY window, splice cleanly."""
    r_spy, *_ = small_returns_window
    real_idx = r_spy.index[10:]   # real LETF starts at bar 10
    rng = np.random.default_rng(11)
    r_real = pd.Series(rng.normal(0.0015, 0.035, len(real_idx)),
                       index=real_idx, name="r_real_letf")
    out = build_letf_returns(r_spy, real_letf_returns=r_real,
                             leverage=3.0, expense_ratio=0.0091)
    # First 10 are synth, rest are real
    expected_synth = synth_upro_returns(r_spy.iloc[:10], leverage=3.0,
                                        expense_ratio=0.0091)
    np.testing.assert_allclose(out.iloc[:10].values, expected_synth.values, atol=1e-15)
    np.testing.assert_allclose(out.iloc[10:].values, r_real.values, atol=1e-15)


# -----------------------------------------------------------------------------
# Identity reduction: when leverage=1 and expense=0 and weights match
# iter 041 canonical, the LETF stream IS the SPY stream and the regime
# stack reduces to iter 041 verbatim.
# -----------------------------------------------------------------------------


def test_iter041_letf_reduces_to_iter041_at_leverage_1(small_returns_window):
    r_spy, r_bd, r_gld, vix = small_returns_window
    # Build a pseudo-LETF with leverage=1, expense=0 → equals SPY.
    r_letf = synth_upro_returns(r_spy, leverage=1.0, expense_ratio=0.0)
    np.testing.assert_allclose(r_letf.values, r_spy.values, atol=1e-15)

    canonical_calm = {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40}
    canonical_stress = {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55}

    net_letf, *_ = compute_iter041_letf_returns(
        r_letf, r_bd, r_gld, vix,
        calm_weights=canonical_calm, stress_weights=canonical_stress,
        vix_threshold=20.0,
    )
    net_canonical, *_ = apply_regime_weights_3leg(
        r_spy, r_bd, r_gld, vix,
        calm_weights=canonical_calm, stress_weights=canonical_stress,
        vix_threshold=20.0,
    )
    np.testing.assert_allclose(net_letf.values, net_canonical.values, atol=1e-15)


# -----------------------------------------------------------------------------
# combine_iter046_letf reductions
# -----------------------------------------------------------------------------


def test_combine_iter046_letf_zero_039_returns_letf_only(small_returns_window):
    r_spy, r_bd, r_gld, vix = small_returns_window
    r_letf = build_letf_returns(r_spy, real_letf_returns=None)
    iter041_letf, *_ = compute_iter041_letf_returns(r_letf, r_bd, r_gld, vix)
    r_039_dummy = pd.Series(np.zeros_like(iter041_letf.values),
                            index=iter041_letf.index, name="r_039_zero")
    combined = combine_iter046_letf(iter041_letf, r_039_dummy, w_041=1.0, w_039=0.0)
    np.testing.assert_allclose(combined.values, iter041_letf.values, atol=1e-15)


def test_combine_iter046_letf_50_50_is_arithmetic_mean(small_returns_window):
    r_spy, r_bd, r_gld, vix = small_returns_window
    r_letf = build_letf_returns(r_spy, real_letf_returns=None)
    a, *_ = compute_iter041_letf_returns(r_letf, r_bd, r_gld, vix)
    rng = np.random.default_rng(7)
    b = pd.Series(rng.normal(0.0003, 0.008, len(a)), index=a.index, name="r_039")
    combined = combine_iter046_letf(a, b, w_041=0.5, w_039=0.5)
    np.testing.assert_allclose(combined.values, 0.5 * a.values + 0.5 * b.values, atol=1e-15)


# -----------------------------------------------------------------------------
# combine_iter058_letf reductions
# -----------------------------------------------------------------------------


def test_combine_iter058_letf_zero_hyg_returns_inner_only(small_returns_window):
    r_spy, r_bd, r_gld, vix = small_returns_window
    r_letf = build_letf_returns(r_spy, real_letf_returns=None)
    a, *_ = compute_iter041_letf_returns(r_letf, r_bd, r_gld, vix)
    rng = np.random.default_rng(9)
    b = pd.Series(rng.normal(0.0003, 0.008, len(a)), index=a.index, name="r_039")
    inner = combine_iter046_letf(a, b, w_041=0.5, w_039=0.5)
    h = pd.Series(np.zeros_like(inner.values), index=inner.index, name="r_hyg_zero")
    combined = combine_iter058_letf(inner, h, w_046=1.0, w_hyg=0.0)
    np.testing.assert_allclose(combined.values, inner.values, atol=1e-15)


def test_combine_iter058_letf_canonical_weights_explicit(small_returns_window):
    r_spy, r_bd, r_gld, vix = small_returns_window
    r_letf = build_letf_returns(r_spy, real_letf_returns=None)
    a, *_ = compute_iter041_letf_returns(r_letf, r_bd, r_gld, vix)
    rng = np.random.default_rng(13)
    b = pd.Series(rng.normal(0.0003, 0.008, len(a)), index=a.index, name="r_039")
    h = pd.Series(rng.normal(0.0001, 0.005, len(a)), index=a.index, name="r_hyg")
    inner = combine_iter046_letf(a, b, w_041=0.5, w_039=0.5)
    out = combine_iter058_letf(inner, h, w_046=0.9, w_hyg=0.1)
    expected = 0.9 * (0.5 * a.values + 0.5 * b.values) + 0.1 * h.values
    np.testing.assert_allclose(out.values, expected, atol=1e-15)


# -----------------------------------------------------------------------------
# G7 cross-library parity: pandas wrappers vs pure-numpy reference.
# -----------------------------------------------------------------------------


def test_g7_iter041_letf_pandas_vs_numpy_parity(small_returns_window):
    r_spy, r_bd, r_gld, vix = small_returns_window
    r_letf = build_letf_returns(r_spy, real_letf_returns=None,
                                leverage=3.0, expense_ratio=0.0091)
    pd_net, *_ = compute_iter041_letf_returns(
        r_letf, r_bd, r_gld, vix,
        calm_weights=ITER063_CALM_WEIGHTS,
        stress_weights=ITER063_STRESS_WEIGHTS,
        vix_threshold=20.0,
    )
    np_net = apply_regime_weights_3leg_np(
        r_letf.values, r_bd.values, r_gld.values, vix.values,
        calm_weights=ITER063_CALM_WEIGHTS,
        stress_weights=ITER063_STRESS_WEIGHTS,
        vix_threshold=20.0,
    )
    np.testing.assert_allclose(pd_net.values, np_net, atol=1e-15)


def test_g7_three_stream_combine_pandas_vs_numpy(small_returns_window):
    r_spy, r_bd, r_gld, vix = small_returns_window
    r_letf = build_letf_returns(r_spy, real_letf_returns=None)
    pd_a, *_ = compute_iter041_letf_returns(r_letf, r_bd, r_gld, vix)
    rng = np.random.default_rng(101)
    pd_b = pd.Series(rng.normal(0.0003, 0.008, len(pd_a)),
                     index=pd_a.index, name="r_039")
    pd_h = pd.Series(rng.normal(0.0001, 0.005, len(pd_a)),
                     index=pd_a.index, name="r_hyg")
    inner_pd = combine_iter046_letf(pd_a, pd_b, w_041=0.5, w_039=0.5)
    out_pd = combine_iter058_letf(inner_pd, pd_h, w_046=0.9, w_hyg=0.1)
    out_np = combine_three_streams_np(
        pd_a.values, pd_b.values, pd_h.values,
        w_a=0.5, w_b=0.5, w_outer_ab=0.9, w_outer_c=0.1,
    )
    np.testing.assert_allclose(out_pd.values, out_np, atol=1e-15)


# -----------------------------------------------------------------------------
# Validation guards
# -----------------------------------------------------------------------------


def test_combine_iter046_negative_weight_raises():
    a = pd.Series([0.001, 0.002], index=pd.date_range("2020-01-02", periods=2))
    b = a.copy()
    with pytest.raises(ValueError):
        combine_iter046_letf(a, b, w_041=-0.1, w_039=0.5)


def test_combine_iter058_negative_weight_raises():
    a = pd.Series([0.001, 0.002], index=pd.date_range("2020-01-02", periods=2))
    b = a.copy()
    with pytest.raises(ValueError):
        combine_iter058_letf(a, b, w_046=0.9, w_hyg=-0.1)


def test_combine_iter058_nonoverlapping_indexes_raises():
    a = pd.Series([0.001, 0.002], index=pd.date_range("2020-01-02", periods=2))
    b = pd.Series([0.001, 0.002], index=pd.date_range("2025-01-02", periods=2))
    with pytest.raises(ValueError):
        combine_iter058_letf(a, b, w_046=0.9, w_hyg=0.1)
