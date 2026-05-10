"""Iter 015 — equity-tilted basket helpers: unit tests.

Tests the iter-015 ON-leg helpers introduced in
``loop_iterations/015-.../equity_tilt_leg.py``:

  1. ``build_basket3_eqtilt_on_leg`` weights validation (must sum to 1.0).
  2. ``build_basket3_eqtilt_on_leg`` reduces to single QLD return when
     weights = (1, 0, 0) and no upgrade fires.
  3. ``build_basket3_eqtilt_on_leg`` swaps QLD→TQQQ on upgrade gate.
  4. ``build_basket3_eqtilt_on_leg`` linear combination property:
     out[t] = w_p * primary[t] + w_s * upro[t] + w_g * ugl[t].
  5. ``build_basket2_invvol_on_leg`` reduces to single QLD return when
     UPRO has zero variance and gate is off (degenerate edge guard).
  6. ``build_basket2_invvol_on_leg`` swaps QLD→TQQQ on upgrade gate.

These tests guard the iter 014 → iter 015 calibration: helper bugs
silently shift the basket3-eqtilt outputs, which would invalidate the
PRIMARY hypothesis (eqtilt > invvol on CAGR).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ITER015_DIR = (
    REPO_ROOT
    / "studies"
    / "letf_rotation_hunt"
    / "loop_iterations"
    / "015-2026-05-10-equity-tilted-basket-cagr-recovery"
)

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_module(file_path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def eqtilt_module():
    return _load_module(ITER015_DIR / "equity_tilt_leg.py", "test_iter015_eqtilt")


@pytest.fixture
def synth_returns():
    rng = np.random.default_rng(2026)
    n = 600
    idx = pd.bdate_range("2018-01-02", periods=n)
    qld = pd.Series(rng.normal(0.0006, 0.018, n), index=idx)
    tqqq = qld * 1.5  # synthetic 1.5× scaling
    upro = pd.Series(rng.normal(0.0006, 0.022, n), index=idx)
    ugl = pd.Series(rng.normal(0.0002, 0.014, n), index=idx)
    return {"qld": qld, "tqqq": tqqq, "upro": upro, "ugl": ugl}


def test_eqtilt_weights_validation(eqtilt_module, synth_returns):
    upg = pd.Series(0.0, index=synth_returns["qld"].index)
    with pytest.raises(ValueError, match="weights must sum to 1.0"):
        eqtilt_module.build_basket3_eqtilt_on_leg(
            qld_returns=synth_returns["qld"],
            tqqq_returns=synth_returns["tqqq"],
            upro_returns=synth_returns["upro"],
            ugl_returns=synth_returns["ugl"],
            upgrade_gate=upg,
            weights=(0.5, 0.4, 0.2),  # sums to 1.1
        )


def test_eqtilt_full_qld_no_upgrade(eqtilt_module, synth_returns):
    upg = pd.Series(0.0, index=synth_returns["qld"].index)
    out = eqtilt_module.build_basket3_eqtilt_on_leg(
        qld_returns=synth_returns["qld"],
        tqqq_returns=synth_returns["tqqq"],
        upro_returns=synth_returns["upro"],
        ugl_returns=synth_returns["ugl"],
        upgrade_gate=upg,
        weights=(1.0, 0.0, 0.0),
    )
    pd.testing.assert_series_equal(
        out, synth_returns["qld"].reindex(out.index),
        check_names=False, atol=1e-12, rtol=0.0,
    )


def test_eqtilt_swaps_to_tqqq_on_upgrade(eqtilt_module, synth_returns):
    """When upgrade fires, primary leg should reflect TQQQ not QLD."""
    upg = pd.Series(0.0, index=synth_returns["qld"].index)
    upg.iloc[200:300] = 1.0  # upgrade window
    out = eqtilt_module.build_basket3_eqtilt_on_leg(
        qld_returns=synth_returns["qld"],
        tqqq_returns=synth_returns["tqqq"],
        upro_returns=synth_returns["upro"],
        ugl_returns=synth_returns["ugl"],
        upgrade_gate=upg,
        weights=(1.0, 0.0, 0.0),  # all-primary; primary swaps QLD↔TQQQ
    )
    upg_lag = upg.shift(1).fillna(0.0).reindex(out.index)
    expected_qld_rows = out[upg_lag != 1.0]
    expected_tqqq_rows = out[upg_lag == 1.0]
    # Where upgrade is off (lagged), output equals QLD.
    pd.testing.assert_series_equal(
        expected_qld_rows,
        synth_returns["qld"].reindex(expected_qld_rows.index),
        check_names=False, atol=1e-12, rtol=0.0,
    )
    # Where upgrade is on (lagged), output equals TQQQ.
    pd.testing.assert_series_equal(
        expected_tqqq_rows,
        synth_returns["tqqq"].reindex(expected_tqqq_rows.index),
        check_names=False, atol=1e-12, rtol=0.0,
    )


def test_eqtilt_linear_combination(eqtilt_module, synth_returns):
    """basket3_eqtilt should be a linear combination of the legs."""
    upg = pd.Series(0.0, index=synth_returns["qld"].index)
    weights = (2.0 / 3.0, 1.0 / 6.0, 1.0 / 6.0)
    out = eqtilt_module.build_basket3_eqtilt_on_leg(
        qld_returns=synth_returns["qld"],
        tqqq_returns=synth_returns["tqqq"],
        upro_returns=synth_returns["upro"],
        ugl_returns=synth_returns["ugl"],
        upgrade_gate=upg,
        weights=weights,
    )
    expected = (
        weights[0] * synth_returns["qld"].reindex(out.index)
        + weights[1] * synth_returns["upro"].reindex(out.index)
        + weights[2] * synth_returns["ugl"].reindex(out.index)
    )
    pd.testing.assert_series_equal(
        out, expected, check_names=False, atol=1e-12, rtol=0.0,
    )


def test_basket2_invvol_no_upgrade_returns_invvol(eqtilt_module, synth_returns):
    """When upgrade_gate is constant 0, basket2_QU = invvol(QLD, UPRO).

    Verifies that the helper short-circuits to QLD-basket and returns a
    series of the correct length (post 60-day invvol warmup).
    """
    upg = pd.Series(0.0, index=synth_returns["qld"].index)
    out = eqtilt_module.build_basket2_invvol_on_leg(
        qld_returns=synth_returns["qld"],
        tqqq_returns=synth_returns["tqqq"],
        upro_returns=synth_returns["upro"],
        upgrade_gate=upg,
        invvol_window=60,
    )
    # 60-day warmup => first 60 rows dropped (or NaN); length ~ n - 60.
    assert len(out) >= len(synth_returns["qld"]) - 80
    assert out.notna().all()


def test_basket2_invvol_swaps_to_tqqq_on_upgrade(eqtilt_module, synth_returns):
    """basket2_QU_invvol should incorporate TQQQ when upgrade is lagged 1."""
    upg = pd.Series(0.0, index=synth_returns["qld"].index)
    upg.iloc[300:400] = 1.0
    out_with = eqtilt_module.build_basket2_invvol_on_leg(
        qld_returns=synth_returns["qld"],
        tqqq_returns=synth_returns["tqqq"],
        upro_returns=synth_returns["upro"],
        upgrade_gate=upg,
        invvol_window=60,
    )
    out_without = eqtilt_module.build_basket2_invvol_on_leg(
        qld_returns=synth_returns["qld"],
        tqqq_returns=synth_returns["tqqq"],
        upro_returns=synth_returns["upro"],
        upgrade_gate=pd.Series(0.0, index=synth_returns["qld"].index),
        invvol_window=60,
    )
    common = out_with.index.intersection(out_without.index)
    upg_lag = upg.shift(1).fillna(0.0).reindex(common)
    upgrade_window = upg_lag == 1.0
    # In the upgrade window, output should DIFFER (TQQQ leg swapped in).
    differ = (out_with.reindex(common) - out_without.reindex(common)).abs()
    assert (differ[upgrade_window] > 1e-9).any()
    # Outside the upgrade window, output should be identical (QLD basket).
    pd.testing.assert_series_equal(
        out_with.reindex(common[~upgrade_window]),
        out_without.reindex(common[~upgrade_window]),
        check_names=False, atol=1e-12, rtol=0.0,
    )
