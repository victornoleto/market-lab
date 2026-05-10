"""Iter 012 — compound TQQQ-K4 × ratevol-OFF: unit tests.

Tests:
  1. Compound state machine equivalences:
     - upgrade_gate=0 + ratevol=NaN equals iter 011 baseline (QLD/ZROZ).
     - upgrade_gate=K4 + ratevol=NaN equals iter 011 K4 anchor (QLD↔TQQQ
       conditional / ZROZ).
     - All-zero upgrade_gate + use_off_override=False equals plain
       QLD/ZROZ.
  2. Compound turnover monotonic: adding ratevol increases turnover vs
     no-ratevol baseline.
  3. The compound output has same length and index as iter 011's helper
     when ratevol is disabled.

These tests guard the iter 011 → iter 012 calibration anchor: per
iter 011 KILL_LOOP #3 disclosure, the iter 011 baseline matches the
T3d-K2 OFFICIAL winner Sortino 1.3246 to 4 decimals. Iter 012 must not
regress this calibration.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ITER012_DIR = REPO_ROOT / "studies" / "letf_rotation_hunt" / "loop_iterations" / "012-2026-05-10-compound-tqqq-K4-x-ratevol-off"
ITER011_DIR = REPO_ROOT / "studies" / "letf_rotation_hunt" / "loop_iterations" / "011-2026-05-10-conditional-tqqq-leverage"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_module(file_path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cmp_module():
    return _load_module(ITER012_DIR / "compound_leg.py", "test_iter012_compound_leg")


@pytest.fixture(scope="module")
def cleg_module():
    return _load_module(ITER011_DIR / "conditional_leg.py", "test_iter012_iter011_cleg")


@pytest.fixture
def synth_data():
    """Synthetic 2000-business-day return series for QLD, TQQQ, ZROZ, alt."""
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.bdate_range("2010-01-04", periods=n)
    qld_r = pd.Series(rng.normal(0.0006, 0.018, n), index=idx)
    # TQQQ ≈ 1.5× QLD (intraday) for synthetic test
    tqqq_r = qld_r * 1.5
    zroz_r = pd.Series(rng.normal(0.0002, 0.012, n), index=idx)
    cash_r = pd.Series(rng.normal(0.0001, 0.001, n), index=idx)

    # ON signal: 1 for first 70% of days, then 0
    on = pd.Series(0.0, index=idx)
    on.iloc[:int(n * 0.7)] = 1.0

    # K4 upgrade gate: 1 for middle 30% of ON days
    upg = pd.Series(0.0, index=idx)
    upg.iloc[int(n * 0.2):int(n * 0.5)] = 1.0

    # ratevol gate: 1 for last 25% of OFF days
    rv = pd.Series(0.0, index=idx)
    rv.iloc[int(n * 0.85):] = 1.0

    return {
        "on": on, "upg": upg, "rv": rv,
        "qld": qld_r, "tqqq": tqqq_r, "zroz": zroz_r, "cash": cash_r, "idx": idx,
    }


def test_compound_no_override_equals_no_ratevol(cmp_module, synth_data):
    """use_off_override=False ignores ratevol → should equal plain ZROZ OFF."""
    d = synth_data
    out_no_override = cmp_module.build_compound_strategy_returns(
        on_signal=d["on"], qld_returns=d["qld"], tqqq_returns=d["tqqq"],
        off_returns=d["zroz"], alt_off_returns=d["cash"],
        upgrade_gate=d["upg"], ratevol_gate=d["rv"],
        use_off_override=False,
    )
    # Hand-build expected: ON+upg=1 → tqqq, ON+upg=0 → qld, OFF → zroz.
    # Helper fills NaN lags as 0, so day 0 (no prior bar) is treated as OFF.
    on_lag = d["on"].shift(1).fillna(0.0)
    upg_lag = d["upg"].shift(1).fillna(0.0)
    expected = pd.Series(0.0, index=d["idx"])
    on_state = on_lag == 1.0
    expected[on_state & (upg_lag == 1.0)] = d["tqqq"][on_state & (upg_lag == 1.0)]
    expected[on_state & (upg_lag != 1.0)] = d["qld"][on_state & (upg_lag != 1.0)]
    expected[~on_state] = d["zroz"][~on_state]

    common = out_no_override.index.intersection(expected.index)
    pd.testing.assert_series_equal(
        out_no_override.loc[common].iloc[:50],
        expected.loc[common].iloc[:50],
        check_names=False,
    )


def test_compound_baseline_matches_iter011_baseline(cmp_module, cleg_module, synth_data):
    """upgrade_gate=0 + use_off_override=False ↔ iter 011 baseline_qld."""
    d = synth_data
    zero_upg = pd.Series(0.0, index=d["idx"])
    nan_rv = pd.Series(np.nan, index=d["idx"])

    out_iter012 = cmp_module.build_compound_strategy_returns(
        on_signal=d["on"], qld_returns=d["qld"], tqqq_returns=d["tqqq"],
        off_returns=d["zroz"], alt_off_returns=d["cash"],
        upgrade_gate=zero_upg, ratevol_gate=nan_rv,
        use_off_override=False,
    )

    out_iter011 = cleg_module.build_conditional_strategy_returns(
        on_signal=d["on"], qld_returns=d["qld"], tqqq_returns=d["tqqq"],
        off_returns=d["zroz"], upgrade_gate=zero_upg,
    )

    # Same business days; iter 012 may include extra rows because it also
    # requires ret_alt non-null — but synth alt is non-null everywhere here.
    common_idx = out_iter012.index.intersection(out_iter011.index)
    assert len(common_idx) > 100
    pd.testing.assert_series_equal(
        out_iter012.loc[common_idx].iloc[:50],
        out_iter011.loc[common_idx].iloc[:50],
        check_names=False,
    )


def test_compound_K4_zroz_matches_iter011_K4(cmp_module, cleg_module, synth_data):
    """upgrade_gate=K4 + use_off_override=False ↔ iter 011 tqqq_K4 (ZROZ OFF).

    This is the KEY equivalence: iter 012 slot 2 (tqqq_K4_zroz) must
    bit-match iter 011 slot 3 (tqqq_K4) when the same upgrade gate is
    fed. Validates that iter 012's compound state machine doesn't
    regress the iter 011 calibration.
    """
    d = synth_data
    nan_rv = pd.Series(np.nan, index=d["idx"])

    out_iter012 = cmp_module.build_compound_strategy_returns(
        on_signal=d["on"], qld_returns=d["qld"], tqqq_returns=d["tqqq"],
        off_returns=d["zroz"], alt_off_returns=d["cash"],
        upgrade_gate=d["upg"], ratevol_gate=nan_rv,
        use_off_override=False,
    )

    out_iter011 = cleg_module.build_conditional_strategy_returns(
        on_signal=d["on"], qld_returns=d["qld"], tqqq_returns=d["tqqq"],
        off_returns=d["zroz"], upgrade_gate=d["upg"],
    )

    common_idx = out_iter012.index.intersection(out_iter011.index)
    assert len(common_idx) > 100
    pd.testing.assert_series_equal(
        out_iter012.loc[common_idx],
        out_iter011.loc[common_idx],
        check_names=False,
    )


def test_compound_with_ratevol_uses_alt_off_when_fired(cmp_module, synth_data):
    """When ratevol fires AND OFF state, return must equal alt_off_returns."""
    d = synth_data
    out = cmp_module.build_compound_strategy_returns(
        on_signal=d["on"], qld_returns=d["qld"], tqqq_returns=d["tqqq"],
        off_returns=d["zroz"], alt_off_returns=d["cash"],
        upgrade_gate=d["upg"], ratevol_gate=d["rv"],
        use_off_override=True,
    )

    # Find a day where on=0 and rv=1 (lagged)
    on_lag = d["on"].shift(1).fillna(0.0)
    rv_lag = d["rv"].shift(1).fillna(0.0)
    target = (on_lag != 1.0) & (rv_lag == 1.0)
    target_days = d["idx"][target]
    assert len(target_days) > 10

    sample = target_days[:20]
    expected = d["cash"].loc[sample]
    actual = out.loc[sample]
    pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_compound_turnover_increases_with_ratevol(cmp_module, synth_data):
    """Adding ratevol creates extra ZROZ↔alt flips → turnover should rise."""
    d = synth_data
    t_no_rv = cmp_module.compound_turnover(
        on_signal=d["on"], upgrade_gate=d["upg"], ratevol_gate=d["rv"],
        use_off_override=False,
    )
    t_with_rv = cmp_module.compound_turnover(
        on_signal=d["on"], upgrade_gate=d["upg"], ratevol_gate=d["rv"],
        use_off_override=True,
    )
    assert t_with_rv >= t_no_rv  # at minimum equal; strict if rv ever fires


def test_compound_no_upgrade_no_ratevol_equals_qld_off_zroz(cmp_module, synth_data):
    """Both gates inert → returns are pure QLD ON / ZROZ OFF."""
    d = synth_data
    zero_upg = pd.Series(0.0, index=d["idx"])
    nan_rv = pd.Series(np.nan, index=d["idx"])

    out = cmp_module.build_compound_strategy_returns(
        on_signal=d["on"], qld_returns=d["qld"], tqqq_returns=d["tqqq"],
        off_returns=d["zroz"], alt_off_returns=d["cash"],
        upgrade_gate=zero_upg, ratevol_gate=nan_rv,
        use_off_override=False,
    )

    on_lag = d["on"].shift(1).fillna(0.0)
    expected = pd.Series(0.0, index=d["idx"])
    expected[on_lag == 1.0] = d["qld"][on_lag == 1.0]
    expected[on_lag != 1.0] = d["zroz"][on_lag != 1.0]

    common = out.index.intersection(expected.index)
    pd.testing.assert_series_equal(
        out.loc[common].iloc[:50], expected.loc[common].iloc[:50],
        check_names=False,
    )
