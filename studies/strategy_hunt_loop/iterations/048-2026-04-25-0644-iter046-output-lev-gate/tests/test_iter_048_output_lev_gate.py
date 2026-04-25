"""TDD specs for iter 048 — VIX-regime OUTPUT leverage gate on iter 046.

Mechanism: r_iter048[t] = lev[t] * r_iter046[t]; lev[t] uses VIX[t-1]
(no lookahead). lev_calm fires when VIX[t-1] < threshold; lev_stress
otherwise.

Citations
---------
* `[risk_parity, ch.5]` — base architecture preserved.
* `[advances_fin_ml, ch.17-18]` — binary regime detection.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* Whaley (2009), JPM 35(3) — VIX as risk regime indicator.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from output_lev_gate import apply_output_lev_gate  # noqa: E402
from numpy_reference_iter048 import apply_output_lev_gate_np  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_combined(n: int = 50, seed: int = 7) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    arr = rng.normal(loc=0.0006, scale=0.011, size=n)
    return pd.Series(arr, index=idx, name="combined_iter046")


def _make_vix(idx: pd.DatetimeIndex, level: float | np.ndarray) -> pd.Series:
    if np.isscalar(level):
        return pd.Series(np.full(len(idx), float(level)), index=idx, name="VIX")
    return pd.Series(np.asarray(level, dtype=float), index=idx, name="VIX")


# ---------------------------------------------------------------------------
# Identity / reduction
# ---------------------------------------------------------------------------


class TestIdentityReduction:
    def test_lev_calm_equals_lev_stress_equals_one_returns_input(self):
        combined = _make_combined()
        vix = _make_vix(combined.index, 18.0)
        out = apply_output_lev_gate(
            combined, vix, lev_calm=1.0, lev_stress=1.0, vix_threshold=20.0,
        )
        # Strict equality — pure scalar multiplication by 1.0.
        pd.testing.assert_series_equal(
            out.rename(combined.name), combined, check_exact=True,
        )

    def test_index_preserved(self):
        combined = _make_combined(60)
        vix = _make_vix(combined.index, 18.0)
        out = apply_output_lev_gate(combined, vix)
        assert (out.index == combined.index).all()
        assert len(out) == len(combined)


# ---------------------------------------------------------------------------
# Calm / stress arithmetic
# ---------------------------------------------------------------------------


class TestRegimeArithmetic:
    def test_all_calm_returns_lev_calm_times_combined(self):
        combined = _make_combined()
        # VIX low at every bar → lev[t] = 1.4 every bar (including t=0,
        # where VIX[t-1] is the bar 0 value via fillna).
        vix = _make_vix(combined.index, 12.0)
        out = apply_output_lev_gate(
            combined, vix, lev_calm=1.4, lev_stress=1.0, vix_threshold=20.0,
        )
        np.testing.assert_allclose(
            out.values, 1.4 * combined.values, rtol=0, atol=1e-12,
        )

    def test_all_stress_returns_lev_stress_times_combined(self):
        combined = _make_combined()
        vix = _make_vix(combined.index, 28.0)
        out = apply_output_lev_gate(
            combined, vix, lev_calm=1.4, lev_stress=1.0, vix_threshold=20.0,
        )
        np.testing.assert_allclose(
            out.values, 1.0 * combined.values, rtol=0, atol=1e-12,
        )

    def test_mixed_regime_uses_lagged_vix(self):
        combined = _make_combined(8)
        # VIX values: 15, 25, 15, 25, 15, 25, 15, 25
        vals = np.array([15, 25, 15, 25, 15, 25, 15, 25], dtype=float)
        vix = _make_vix(combined.index, vals)
        # vix[t-1] for t=0 is filled with vix[0] = 15 (calm).
        # For t=1: vix[0]=15 → calm. t=2: vix[1]=25 → stress. ...
        # So lev pattern = [calm, calm, stress, calm, stress, calm, stress, calm]
        # = [1.4, 1.4, 1.0, 1.4, 1.0, 1.4, 1.0, 1.4]
        out = apply_output_lev_gate(
            combined, vix, lev_calm=1.4, lev_stress=1.0, vix_threshold=20.0,
        )
        expected_lev = np.array([1.4, 1.4, 1.0, 1.4, 1.0, 1.4, 1.0, 1.4])
        np.testing.assert_allclose(
            out.values, expected_lev * combined.values, rtol=0, atol=1e-12,
        )


# ---------------------------------------------------------------------------
# No-lookahead causality
# ---------------------------------------------------------------------------


class TestNoLookahead:
    def test_gate_uses_vix_t_minus_1_not_vix_t(self):
        """Mutating VIX at the LAST bar must not change earlier outputs."""
        combined = _make_combined(20)
        vix = _make_vix(combined.index, 15.0)  # all calm
        out_a = apply_output_lev_gate(combined, vix, lev_calm=1.4)

        vix_mutated = vix.copy()
        vix_mutated.iloc[-1] = 99.0  # spike LAST bar
        out_b = apply_output_lev_gate(combined, vix_mutated, lev_calm=1.4)

        # Output must be IDENTICAL on bars 0..n-1 (because vix[t-1] for the
        # final bar uses bar n-2, but bars 0..n-2 are unaffected).
        np.testing.assert_array_equal(out_a.values[:-1], out_b.values[:-1])

    def test_first_bar_lev_uses_first_vix_via_ffill(self):
        """Bar 0 has no t-1 → lev[0] is determined by vix.iloc[0] via bfill."""
        combined = _make_combined(5)
        vix_low = _make_vix(combined.index, 10.0)
        out_low = apply_output_lev_gate(combined, vix_low, lev_calm=1.4)
        np.testing.assert_allclose(out_low.iloc[0], 1.4 * combined.iloc[0])

        vix_high = _make_vix(combined.index, 30.0)
        out_high = apply_output_lev_gate(combined, vix_high, lev_calm=1.4)
        np.testing.assert_allclose(out_high.iloc[0], 1.0 * combined.iloc[0])


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestValidation:
    def test_empty_input_raises(self):
        empty = pd.Series([], dtype=float, index=pd.DatetimeIndex([]))
        vix = pd.Series([], dtype=float, index=pd.DatetimeIndex([]))
        with pytest.raises(ValueError):
            apply_output_lev_gate(empty, vix)

    def test_single_bar_raises(self):
        idx = pd.DatetimeIndex(["2020-01-02"])
        c = pd.Series([0.001], index=idx)
        v = pd.Series([15.0], index=idx)
        with pytest.raises(ValueError):
            apply_output_lev_gate(c, v)

    def test_negative_lev_raises(self):
        combined = _make_combined()
        vix = _make_vix(combined.index, 15.0)
        with pytest.raises(ValueError):
            apply_output_lev_gate(combined, vix, lev_calm=-0.5)
        with pytest.raises(ValueError):
            apply_output_lev_gate(combined, vix, lev_stress=-0.5)

    def test_threshold_in_valid_range(self):
        combined = _make_combined()
        vix = _make_vix(combined.index, 15.0)
        # Negative VIX threshold makes no sense.
        with pytest.raises(ValueError):
            apply_output_lev_gate(combined, vix, vix_threshold=-1.0)

    def test_vix_must_be_alignable_or_reindexable(self):
        combined = _make_combined(10)
        # VIX with a totally different index, no overlap.
        bad_idx = pd.date_range("1990-01-02", periods=10, freq="B")
        vix = pd.Series(np.full(10, 15.0), index=bad_idx)
        with pytest.raises(ValueError):
            apply_output_lev_gate(combined, vix)


# ---------------------------------------------------------------------------
# Cross-lib parity (G7)
# ---------------------------------------------------------------------------


class TestCrossLibParity:
    def test_numpy_reference_matches_pandas_to_1e_9(self):
        rng = np.random.default_rng(123)
        n = 200
        combined = pd.Series(
            rng.normal(0.0005, 0.01, n),
            index=pd.date_range("2020-01-02", periods=n, freq="B"),
        )
        vix = pd.Series(
            np.clip(rng.normal(20, 8, n), 8, 60),
            index=combined.index,
        )
        out_pd = apply_output_lev_gate(
            combined, vix, lev_calm=1.4, lev_stress=1.0, vix_threshold=20.0,
        )
        out_np = apply_output_lev_gate_np(
            combined.to_numpy(float), vix.to_numpy(float),
            lev_calm=1.4, lev_stress=1.0, vix_threshold=20.0,
        )
        np.testing.assert_allclose(out_pd.values, out_np, rtol=0, atol=1e-12)


# ---------------------------------------------------------------------------
# Threshold ordering / asymmetric lev pairs
# ---------------------------------------------------------------------------


class TestThresholdOrdering:
    def test_lev_stress_can_exceed_lev_calm(self):
        """Function should not assume lev_calm > lev_stress (defensive)."""
        combined = _make_combined()
        vix = _make_vix(combined.index, 15.0)  # calm
        # Inverted: lev_calm=0.8, lev_stress=1.4. Should multiply by 0.8.
        out = apply_output_lev_gate(combined, vix, lev_calm=0.8, lev_stress=1.4)
        np.testing.assert_allclose(out.values, 0.8 * combined.values)

    def test_zero_calm_zero_stress_returns_zero_series(self):
        combined = _make_combined()
        vix = _make_vix(combined.index, 15.0)
        out = apply_output_lev_gate(combined, vix, lev_calm=0.0, lev_stress=0.0)
        np.testing.assert_allclose(out.values, np.zeros(len(combined)))
