"""TDD specs for iter 051 — iter 037 + iter 026 80/20 convex combo.

Specs cover:
1. Reduction `w_037 = 0` → exactly equals iter 026 net stream.
2. Reduction `w_026 = 0` → exactly equals iter 037 net stream.
3. Linearity: `r_combined = w_037*r_037 + w_026*r_026` byte-precise on
   inner-join.
4. ValueError on negative or zero-sum weights.
5. Empty-overlap raises ValueError (no shared dates).
6. G7 numpy parity: pandas vs numpy implementations match within 1e-12
   on every bar.
7. Markowitz prediction matches observed combined Sharpe within 1e-4
   (validates pre-screen methodology).

Citations
---------
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 037 + iter
  026 base streams preserved verbatim.
* Markowitz (1952), JoF 7(1) — closed-form Sharpe identity.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ITER_DIR))

from combined_037_026 import combine_037_plus_026  # noqa: E402
from numpy_reference_iter051 import combine_037_plus_026_np  # noqa: E402


def _make_streams(n: int = 500, seed: int = 7) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r37 = pd.Series(rng.normal(0.0006, 0.009, size=n), index=idx, name="r_037")
    r26 = pd.Series(rng.normal(0.0002, 0.003, size=n), index=idx, name="r_026")
    return r37, r26


def test_reduction_w037_zero_equals_r026() -> None:
    """w_037=0, w_026=1 → combined ≡ r_026 on common index."""
    r37, r26 = _make_streams()
    combined = combine_037_plus_026(r37, r26, w_037=0.0, w_026=1.0)
    common = r37.index.intersection(r26.index)
    pd.testing.assert_series_equal(
        combined.loc[common],
        r26.loc[common].rename("combined_037_plus_026"),
        check_names=False,
    )


def test_reduction_w026_zero_equals_r037() -> None:
    """w_037=1, w_026=0 → combined ≡ r_037 on common index."""
    r37, r26 = _make_streams()
    combined = combine_037_plus_026(r37, r26, w_037=1.0, w_026=0.0)
    common = r37.index.intersection(r26.index)
    pd.testing.assert_series_equal(
        combined.loc[common],
        r37.loc[common].rename("combined_037_plus_026"),
        check_names=False,
    )


def test_linearity_8020() -> None:
    """w_037=0.80, w_026=0.20 → element-wise 0.8*r_037 + 0.2*r_026."""
    r37, r26 = _make_streams()
    combined = combine_037_plus_026(r37, r26, w_037=0.80, w_026=0.20)
    common = r37.index.intersection(r26.index)
    expected = 0.80 * r37.loc[common] + 0.20 * r26.loc[common]
    np.testing.assert_allclose(combined.values, expected.values, atol=1e-15)


def test_negative_weight_raises() -> None:
    r37, r26 = _make_streams()
    with pytest.raises(ValueError, match="w_037"):
        combine_037_plus_026(r37, r26, w_037=-0.1, w_026=0.5)
    with pytest.raises(ValueError, match="w_026"):
        combine_037_plus_026(r37, r26, w_037=0.5, w_026=-0.1)


def test_zero_sum_weight_raises() -> None:
    r37, r26 = _make_streams()
    with pytest.raises(ValueError, match=">"):
        combine_037_plus_026(r37, r26, w_037=0.0, w_026=0.0)


def test_no_overlap_raises() -> None:
    """Two streams with no shared dates must raise ValueError."""
    idx_a = pd.date_range("2010-01-04", periods=100, freq="B")
    idx_b = pd.date_range("2024-01-04", periods=100, freq="B")
    r37 = pd.Series(np.zeros(100), index=idx_a, name="r_037")
    r26 = pd.Series(np.zeros(100), index=idx_b, name="r_026")
    with pytest.raises(ValueError, match="overlapping"):
        combine_037_plus_026(r37, r26, w_037=0.8, w_026=0.2)


def test_g7_numpy_parity_8020() -> None:
    """Pandas vs numpy implementations agree within 1e-12 element-wise."""
    r37, r26 = _make_streams()
    pd_out = combine_037_plus_026(r37, r26, w_037=0.80, w_026=0.20)
    common = r37.index.intersection(r26.index)
    np_out = combine_037_plus_026_np(
        r37.loc[common].to_numpy(float),
        r26.loc[common].to_numpy(float),
        w_037=0.80, w_026=0.20,
    )
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-12)


def test_markowitz_predicted_matches_observed_8020() -> None:
    """Markowitz formula predicts combined Sharpe within 1e-4 of observed.

    The closed-form identity for w_a, w_b convex combo of two streams:
        μ_c = w_a μ_a + w_b μ_b
        σ_c² = w_a² σ_a² + w_b² σ_b² + 2 w_a w_b ρ σ_a σ_b
        S_c = μ_c / σ_c (annualized later by × √252).

    Validates iter 050's empirical 4-decimal match on a synthetic stream.
    """
    r37, r26 = _make_streams(n=2000, seed=11)
    common = r37.index.intersection(r26.index)
    a = r37.loc[common]
    b = r26.loc[common]

    w_a, w_b = 0.80, 0.20
    mu_a, sigma_a = a.mean(), a.std(ddof=0)
    mu_b, sigma_b = b.mean(), b.std(ddof=0)
    rho = a.corr(b)
    mu_c = w_a * mu_a + w_b * mu_b
    var_c = (
        w_a ** 2 * sigma_a ** 2
        + w_b ** 2 * sigma_b ** 2
        + 2 * w_a * w_b * rho * sigma_a * sigma_b
    )
    sharpe_predicted = mu_c / np.sqrt(var_c)

    combined = combine_037_plus_026(r37, r26, w_037=w_a, w_026=w_b)
    sharpe_observed = combined.mean() / combined.std(ddof=0)
    assert abs(sharpe_predicted - sharpe_observed) < 1e-4
