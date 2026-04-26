"""Iter 074 — TDD specs for the iter 016 + iter 064 saved-stream ensemble.

Mechanism: convex weighted blend of two pre-validated daily net return
streams. The blend math is::

    r_074[t] = w_016 * r_016[t] + w_064 * r_064[t]    on inner-join index

Specs cover:
  1. boundary cases (w=0/1 reduce to single legs)
  2. inner-join correctness
  3. weight invariants (negatives, both-zero raise)
  4. linearity (combine of combine == combine of sum)
  5. cross-lib parity (pandas == numpy within 1e-12)
  6. determinism (same input → same output)
  7. order-invariance (commutative on swapped weights)

Citations
---------
* Markowitz (1952) — convex combination of return streams.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from iter074_ensemble import combine_iter016_iter064  # noqa: E402
from numpy_reference_iter074 import combine_iter016_iter064_np  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _toy_streams() -> tuple[pd.Series, pd.Series]:
    """Two overlapping toy streams with known properties."""
    rng = np.random.default_rng(42)
    idx_016 = pd.date_range("2010-01-01", periods=10, freq="B")
    idx_064 = pd.date_range("2010-01-04", periods=10, freq="B")  # offset by 1 bday
    r_016 = pd.Series(rng.normal(0.001, 0.01, 10), index=idx_016, name="r_016")
    r_064 = pd.Series(rng.normal(0.0008, 0.012, 10), index=idx_064, name="r_064")
    return r_016, r_064


# ---------------------------------------------------------------------------
# Boundary specs
# ---------------------------------------------------------------------------


def test_w016_zero_reduces_to_r064_on_inner_join() -> None:
    """w_016=0, w_064=1 → output == r_064.loc[inner_join_index]."""
    r_016, r_064 = _toy_streams()
    out = combine_iter016_iter064(r_016, r_064, w_016=0.0, w_064=1.0)
    common = r_016.index.intersection(r_064.index)
    expected = r_064.loc[common]
    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_w064_zero_reduces_to_r016_on_inner_join() -> None:
    """w_016=1, w_064=0 → output == r_016.loc[inner_join_index]."""
    r_016, r_064 = _toy_streams()
    out = combine_iter016_iter064(r_016, r_064, w_016=1.0, w_064=0.0)
    common = r_016.index.intersection(r_064.index)
    expected = r_016.loc[common]
    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_equal_weights_arithmetic_mean() -> None:
    """w=0.5/0.5 → output == 0.5*(r_016 + r_064) on inner-join."""
    r_016, r_064 = _toy_streams()
    out = combine_iter016_iter064(r_016, r_064, w_016=0.5, w_064=0.5)
    common = r_016.index.intersection(r_064.index)
    expected = 0.5 * (r_016.loc[common] + r_064.loc[common])
    np.testing.assert_allclose(out.values, expected.values, atol=1e-15)


# ---------------------------------------------------------------------------
# Inner-join specs
# ---------------------------------------------------------------------------


def test_output_index_is_intersection() -> None:
    """Output index must equal r_016.index ∩ r_064.index."""
    r_016, r_064 = _toy_streams()
    out = combine_iter016_iter064(r_016, r_064, w_016=0.5, w_064=0.5)
    expected_idx = r_016.index.intersection(r_064.index)
    pd.testing.assert_index_equal(out.index, expected_idx)


def test_disjoint_indices_raises() -> None:
    """If overlap < 2 bars, raise ValueError."""
    idx_a = pd.date_range("2010-01-01", periods=5, freq="B")
    idx_b = pd.date_range("2020-01-01", periods=5, freq="B")
    r_a = pd.Series(np.zeros(5), index=idx_a)
    r_b = pd.Series(np.zeros(5), index=idx_b)
    with pytest.raises(ValueError, match="overlap"):
        combine_iter016_iter064(r_a, r_b, w_016=0.5, w_064=0.5)


# ---------------------------------------------------------------------------
# Weight-invariant specs
# ---------------------------------------------------------------------------


def test_negative_w016_raises() -> None:
    r_016, r_064 = _toy_streams()
    with pytest.raises(ValueError, match=r"w_016.*>=\s*0"):
        combine_iter016_iter064(r_016, r_064, w_016=-0.1, w_064=1.1)


def test_negative_w064_raises() -> None:
    r_016, r_064 = _toy_streams()
    with pytest.raises(ValueError, match=r"w_064.*>=\s*0"):
        combine_iter016_iter064(r_016, r_064, w_016=1.1, w_064=-0.1)


def test_both_weights_zero_raises() -> None:
    r_016, r_064 = _toy_streams()
    with pytest.raises(ValueError, match=r"sum\s*>?\s*0|must be > 0"):
        combine_iter016_iter064(r_016, r_064, w_016=0.0, w_064=0.0)


# ---------------------------------------------------------------------------
# Linearity specs
# ---------------------------------------------------------------------------


def test_linearity_in_w016() -> None:
    """f(w, 1-w) is linear in w on the inner-join indices."""
    r_016, r_064 = _toy_streams()
    out_03 = combine_iter016_iter064(r_016, r_064, w_016=0.3, w_064=0.7)
    out_07 = combine_iter016_iter064(r_016, r_064, w_016=0.7, w_064=0.3)
    out_05 = combine_iter016_iter064(r_016, r_064, w_016=0.5, w_064=0.5)
    np.testing.assert_allclose(out_05.values, 0.5 * (out_03.values + out_07.values), atol=1e-15)


def test_scaling_invariance() -> None:
    """f(2*w_016, 2*w_064) == 2 * f(w_016, w_064)."""
    r_016, r_064 = _toy_streams()
    out_unit = combine_iter016_iter064(r_016, r_064, w_016=0.6, w_064=0.4)
    out_scaled = combine_iter016_iter064(r_016, r_064, w_016=1.2, w_064=0.8)
    np.testing.assert_allclose(out_scaled.values, 2.0 * out_unit.values, atol=1e-15)


# ---------------------------------------------------------------------------
# Determinism + cross-lib parity
# ---------------------------------------------------------------------------


def test_determinism_repeated_call() -> None:
    """Same inputs → same output (no hidden RNG)."""
    r_016, r_064 = _toy_streams()
    a = combine_iter016_iter064(r_016, r_064, w_016=0.4, w_064=0.6)
    b = combine_iter016_iter064(r_016, r_064, w_016=0.4, w_064=0.6)
    pd.testing.assert_series_equal(a, b, check_names=False)


def test_pandas_numpy_parity() -> None:
    """G7 cross-lib: pandas vs numpy reference match within 1e-12."""
    r_016, r_064 = _toy_streams()
    out_pd = combine_iter016_iter064(r_016, r_064, w_016=0.5, w_064=0.5)
    common = r_016.index.intersection(r_064.index)
    a_arr = r_016.loc[common].values
    b_arr = r_064.loc[common].values
    out_np = combine_iter016_iter064_np(a_arr, b_arr, w_016=0.5, w_064=0.5)
    np.testing.assert_allclose(out_pd.values, out_np, atol=1e-12)


def test_pandas_numpy_parity_asymmetric_weights() -> None:
    """G7 with asymmetric weights — match within 1e-12."""
    r_016, r_064 = _toy_streams()
    out_pd = combine_iter016_iter064(r_016, r_064, w_016=0.30, w_064=0.70)
    common = r_016.index.intersection(r_064.index)
    a_arr = r_016.loc[common].values
    b_arr = r_064.loc[common].values
    out_np = combine_iter016_iter064_np(a_arr, b_arr, w_016=0.30, w_064=0.70)
    np.testing.assert_allclose(out_pd.values, out_np, atol=1e-12)


# ---------------------------------------------------------------------------
# Output naming + dtype
# ---------------------------------------------------------------------------


def test_output_name_set() -> None:
    """Output series has informative name attribute."""
    r_016, r_064 = _toy_streams()
    out = combine_iter016_iter064(r_016, r_064, w_016=0.5, w_064=0.5)
    assert out.name == "combined_iter016_iter064"


def test_output_dtype_float() -> None:
    """Output preserves float dtype."""
    r_016, r_064 = _toy_streams()
    out = combine_iter016_iter064(r_016, r_064, w_016=0.5, w_064=0.5)
    assert np.issubdtype(out.values.dtype, np.floating)
