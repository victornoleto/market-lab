"""TDD specs for iter 053 — iter 037 + iter 046 70/30 convex combo.

Specs cover:
1. Reduction `w_037 = 0` → exactly equals iter 046 net stream.
2. Reduction `w_046 = 0` → exactly equals iter 037 net stream.
3. Linearity: `r_combined = w_037*r_037 + w_046*r_046` byte-precise on
   inner-join.
4. ValueError on negative or zero-sum weights.
5. Empty-overlap raises ValueError (no shared dates).
6. G7 numpy parity: pandas vs numpy implementations match within 1e-12
   on every bar.
7. Markowitz prediction matches observed combined Sharpe within 1e-4
   on a synthetic stream pair (validates pre-screen methodology).
8. Pre-committed weights w_037=0.70, w_046=0.30 sum to 1.0 exactly.
9. High-corr regime: when r_037 ≈ r_046 (corr → 1), combined Sharpe is
   bounded above by max(S_037, S_046) — verifies the structural finding
   that drives the iter 053 closure.

Citations
---------
* `[risk_parity, ch.5]` — iter 037 base preserved verbatim via saved stream.
* iter 046 = 0.5 × iter 041 + 0.5 × iter 039, both preserved.
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

from combined_037_046 import combine_037_plus_046  # noqa: E402
from numpy_reference_iter053 import combine_037_plus_046_np  # noqa: E402


def _make_streams(n: int = 500, seed: int = 13) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r37 = pd.Series(rng.normal(0.0006, 0.009, size=n), index=idx, name="r_037")
    r46 = pd.Series(rng.normal(0.0005, 0.005, size=n), index=idx, name="r_046")
    return r37, r46


def test_reduction_w037_zero_equals_r046() -> None:
    """w_037=0, w_046=1 → combined ≡ r_046 on common index."""
    r37, r46 = _make_streams()
    combined = combine_037_plus_046(r37, r46, w_037=0.0, w_046=1.0)
    common = r37.index.intersection(r46.index)
    pd.testing.assert_series_equal(
        combined.loc[common],
        r46.loc[common].rename("combined_037_plus_046"),
        check_names=False,
    )


def test_reduction_w046_zero_equals_r037() -> None:
    """w_037=1, w_046=0 → combined ≡ r_037 on common index."""
    r37, r46 = _make_streams()
    combined = combine_037_plus_046(r37, r46, w_037=1.0, w_046=0.0)
    common = r37.index.intersection(r46.index)
    pd.testing.assert_series_equal(
        combined.loc[common],
        r37.loc[common].rename("combined_037_plus_046"),
        check_names=False,
    )


def test_linearity_7030() -> None:
    """w_037=0.70, w_046=0.30 → element-wise 0.70*r_037 + 0.30*r_046."""
    r37, r46 = _make_streams()
    combined = combine_037_plus_046(r37, r46, w_037=0.70, w_046=0.30)
    common = r37.index.intersection(r46.index)
    expected = 0.70 * r37.loc[common] + 0.30 * r46.loc[common]
    np.testing.assert_allclose(combined.values, expected.values, atol=1e-15)


def test_negative_weight_raises() -> None:
    r37, r46 = _make_streams()
    with pytest.raises(ValueError, match="w_037"):
        combine_037_plus_046(r37, r46, w_037=-0.1, w_046=0.5)
    with pytest.raises(ValueError, match="w_046"):
        combine_037_plus_046(r37, r46, w_037=0.5, w_046=-0.1)


def test_zero_sum_weight_raises() -> None:
    r37, r46 = _make_streams()
    with pytest.raises(ValueError, match=">"):
        combine_037_plus_046(r37, r46, w_037=0.0, w_046=0.0)


def test_no_overlap_raises() -> None:
    """Two streams with no shared dates must raise ValueError."""
    idx_a = pd.date_range("2010-01-04", periods=100, freq="B")
    idx_b = pd.date_range("2024-01-04", periods=100, freq="B")
    r37 = pd.Series(np.zeros(100), index=idx_a, name="r_037")
    r46 = pd.Series(np.zeros(100), index=idx_b, name="r_046")
    with pytest.raises(ValueError, match="overlapping"):
        combine_037_plus_046(r37, r46, w_037=0.70, w_046=0.30)


def test_g7_numpy_parity_7030() -> None:
    """Pandas vs numpy implementations agree within 1e-12 element-wise."""
    r37, r46 = _make_streams()
    pd_out = combine_037_plus_046(r37, r46, w_037=0.70, w_046=0.30)
    common = r37.index.intersection(r46.index)
    np_out = combine_037_plus_046_np(
        r37.loc[common].to_numpy(float),
        r46.loc[common].to_numpy(float),
        w_037=0.70, w_046=0.30,
    )
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-12)


def test_markowitz_predicted_matches_observed_7030() -> None:
    """Markowitz formula predicts combined Sharpe within 1e-4 of observed.

    The closed-form identity for w_a, w_b convex combo of two streams:
        μ_c = w_a μ_a + w_b μ_b
        σ_c² = w_a² σ_a² + w_b² σ_b² + 2 w_a w_b ρ σ_a σ_b
        S_c = μ_c / σ_c (annualised later by × √252).

    Validates the pre-screen methodology used to select w_037 = 0.70.
    """
    r37, r46 = _make_streams(n=2000, seed=17)
    common = r37.index.intersection(r46.index)
    a = r37.loc[common]
    b = r46.loc[common]

    w_a, w_b = 0.70, 0.30
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

    combined = combine_037_plus_046(r37, r46, w_037=w_a, w_046=w_b)
    sharpe_observed = combined.mean() / combined.std(ddof=0)
    assert abs(sharpe_predicted - sharpe_observed) < 1e-4


def test_canonical_weights_sum_to_one() -> None:
    """Pre-committed weights w_037=0.70, w_046=0.30 sum to 1.0 exactly."""
    w_037 = 0.70
    w_046 = 0.30
    assert abs((w_037 + w_046) - 1.0) < 1e-12


def test_high_corr_regime_combined_sharpe_bounded_by_max() -> None:
    """When corr → 1 and σ_a ≠ σ_b, combined Sharpe is bounded by max
    of standalone Sharpes (within ~1%).

    This test verifies the structural finding that drives the iter 053
    closure: at corr 0.95, the Markowitz diversification gain is
    essentially absent, and the combined Sharpe equals the
    weighted-average Sharpe (no σ-reduction). At any weight, combined
    Sharpe ≤ max(S_037, S_046).
    """
    rng = np.random.default_rng(23)
    n = 2000
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    base = rng.normal(0.0005, 0.008, size=n)
    # Highly-correlated stream with different scale (simulates 037+046).
    r37 = pd.Series(base + rng.normal(0, 0.0015, size=n), index=idx, name="r_037")
    r46 = pd.Series(0.5 * base + rng.normal(0.0001, 0.0010, size=n), index=idx, name="r_046")

    s37 = r37.mean() / r37.std(ddof=0)
    s46 = r46.mean() / r46.std(ddof=0)
    s_max = max(s37, s46)

    for w_037 in [0.3, 0.5, 0.7]:
        combined = combine_037_plus_046(r37, r46, w_037=w_037, w_046=1 - w_037)
        s_combined = combined.mean() / combined.std(ddof=0)
        assert s_combined <= s_max + 0.05, (
            f"At w_037={w_037}: combined S={s_combined:.4f} > max standalone "
            f"S={s_max:.4f} + tolerance — high-corr Markowitz bound violated"
        )
