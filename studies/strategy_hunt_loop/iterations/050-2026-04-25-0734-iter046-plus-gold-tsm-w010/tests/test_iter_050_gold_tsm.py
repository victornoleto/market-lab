"""TDD specs for iter 050 — iter 046 + gold TSM at w_gold = 0.10.

Reuses iter 049's `gold_tsm.compute_gold_tsm_returns` and
`combined_046_plus_gold.combine_046_plus_gold` verbatim. Tests focus on
the **convex-combo weight invariants** (since the gold TSM engine
already had 15 specs in iter 049):

1. `w_gold = 0.0` reduces combined to iter 046 stream alone.
2. `w_gold = 1.0` reduces combined to gold TSM alone.
3. Linearity: combined = w_046 * r_046 + w_gold * r_gold on inner-join.
4. Sum-symmetry: combine(w_a=0.5, w_b=0.5) on identical streams = stream.
5. Cross-lib parity: pandas vs numpy gold TSM identical to 1e-9.
6. Markowitz prediction matches direct measurement (sanity formula).

Citations
---------
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from gold_tsm import compute_gold_tsm_returns  # noqa: E402
from numpy_reference_iter050 import compute_gold_tsm_returns_np  # noqa: E402
from combined_046_plus_gold import combine_046_plus_gold  # noqa: E402


@pytest.fixture
def synthetic_prices():
    """Reproducible synthetic price series with both up and down trends."""
    rng = np.random.default_rng(42)
    n = 600
    drift = np.concatenate(
        [np.full(200, 0.0008), np.full(200, -0.0008), np.full(200, 0.0008)]
    )
    rets = drift + rng.normal(0, 0.01, n)
    px = 100.0 * np.exp(np.cumsum(rets))
    idx = pd.date_range("2010-01-01", periods=n, freq="B")
    return pd.Series(px, index=idx, name="GLD_synth")


@pytest.fixture
def synthetic_iter046_returns():
    """A synthetic iter 046-like return stream (positive Sharpe)."""
    rng = np.random.default_rng(123)
    n = 599  # matches gold TSM output length on 600-day price series
    rets = 0.0004 + rng.normal(0, 0.007, n)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    return pd.Series(rets, index=idx, name="r_046")


def test_w_gold_zero_reduces_to_iter046_stream(
    synthetic_prices, synthetic_iter046_returns
):
    """w_gold = 0 → combined === iter 046 stream (on the inner-join)."""
    r_gold = compute_gold_tsm_returns(
        synthetic_prices, lookback=90, rf=0.02, cost_bps=5.0
    )
    combined = combine_046_plus_gold(
        synthetic_iter046_returns, r_gold, w_046=1.0, w_gold=0.0,
    )
    common = synthetic_iter046_returns.index.intersection(r_gold.index)
    expected = synthetic_iter046_returns.loc[common]
    assert combined.shape == expected.shape
    np.testing.assert_array_almost_equal(
        combined.values, expected.values, decimal=12,
    )


def test_w_046_zero_reduces_to_gold_tsm_stream(
    synthetic_prices, synthetic_iter046_returns
):
    """w_046 = 0 → combined === gold TSM stream alone."""
    r_gold = compute_gold_tsm_returns(
        synthetic_prices, lookback=90, rf=0.02, cost_bps=5.0
    )
    combined = combine_046_plus_gold(
        synthetic_iter046_returns, r_gold, w_046=0.0, w_gold=1.0,
    )
    common = synthetic_iter046_returns.index.intersection(r_gold.index)
    expected = r_gold.loc[common]
    np.testing.assert_array_almost_equal(
        combined.values, expected.values, decimal=12,
    )


def test_w_010_linearity_holds_on_inner_join(
    synthetic_prices, synthetic_iter046_returns
):
    """combined = 0.9 * r_046 + 0.1 * r_gold on inner-join, exactly."""
    r_gold = compute_gold_tsm_returns(
        synthetic_prices, lookback=90, rf=0.02, cost_bps=5.0
    )
    combined = combine_046_plus_gold(
        synthetic_iter046_returns, r_gold, w_046=0.90, w_gold=0.10,
    )
    common = synthetic_iter046_returns.index.intersection(r_gold.index)
    expected = (
        0.90 * synthetic_iter046_returns.loc[common]
        + 0.10 * r_gold.loc[common]
    )
    np.testing.assert_array_almost_equal(
        combined.values, expected.values, decimal=12,
    )


def test_identical_streams_at_50_50_equals_stream():
    """If r_a == r_b, then 50/50 combo == r_a (sum-symmetry)."""
    rng = np.random.default_rng(7)
    n = 100
    rets = rng.normal(0.0003, 0.008, n)
    idx = pd.date_range("2015-01-01", periods=n, freq="B")
    s = pd.Series(rets, index=idx)
    combined = combine_046_plus_gold(s, s, w_046=0.5, w_gold=0.5)
    np.testing.assert_array_almost_equal(combined.values, s.values, decimal=12)


def test_pandas_numpy_gold_tsm_parity(synthetic_prices):
    """G7-style: pandas and numpy implementations agree to 1e-9 per bar."""
    r_pd = compute_gold_tsm_returns(
        synthetic_prices, lookback=90, rf=0.02, cost_bps=5.0
    )
    r_np = compute_gold_tsm_returns_np(
        synthetic_prices.values, lookback=90, rf=0.02, cost_bps=5.0
    )
    assert len(r_pd) == len(r_np)
    np.testing.assert_array_almost_equal(r_pd.values, r_np, decimal=12)


def test_markowitz_formula_matches_observed_combined_sharpe(
    synthetic_prices, synthetic_iter046_returns
):
    """Validate the closed-form Markowitz Sharpe identity numerically.

    Compute (mu_a, sigma_a) and (mu_b, sigma_b) from the synthetic streams,
    derive predicted combined Sharpe at w = (0.9, 0.1), and compare to the
    direct measurement on the actual 90/10 combination. Should agree to
    within 0.005 Sharpe units (numerical noise + finite-sample effect).
    """
    r_gold = compute_gold_tsm_returns(
        synthetic_prices, lookback=90, rf=0.02, cost_bps=5.0
    )
    common = synthetic_iter046_returns.index.intersection(r_gold.index)
    a = synthetic_iter046_returns.loc[common]
    b = r_gold.loc[common]
    mu_a, sigma_a = a.mean(), a.std(ddof=0)
    mu_b, sigma_b = b.mean(), b.std(ddof=0)
    rho = float(a.corr(b))

    w_a, w_b = 0.90, 0.10
    sigma2_combined = (
        w_a ** 2 * sigma_a ** 2
        + w_b ** 2 * sigma_b ** 2
        + 2 * w_a * w_b * rho * sigma_a * sigma_b
    )
    sigma_combined = float(np.sqrt(sigma2_combined))
    mu_combined = w_a * mu_a + w_b * mu_b
    sharpe_predicted = (mu_combined / sigma_combined) * np.sqrt(252)

    combined = combine_046_plus_gold(
        synthetic_iter046_returns, r_gold, w_046=w_a, w_gold=w_b
    )
    sharpe_observed = (combined.mean() / combined.std(ddof=0)) * np.sqrt(252)

    assert abs(sharpe_predicted - sharpe_observed) < 1e-6, (
        f"Markowitz formula must equal direct measurement on identical "
        f"data: predicted={sharpe_predicted:.6f}, "
        f"observed={sharpe_observed:.6f}"
    )


def test_w_010_smaller_dilution_than_w_050(
    synthetic_prices, synthetic_iter046_returns
):
    """At unequal Sharpes, w=0.10 dilutes less than w=0.50.

    Sanity: when r_046 has higher Sharpe than r_gold, the combined
    Sharpe at w_gold=0.10 should be CLOSER to r_046's Sharpe than the
    combined Sharpe at w_gold=0.50 is. This is the iter 049 → iter 050
    structural prediction.
    """
    r_gold = compute_gold_tsm_returns(
        synthetic_prices, lookback=90, rf=0.02, cost_bps=5.0
    )
    common = synthetic_iter046_returns.index.intersection(r_gold.index)
    a = synthetic_iter046_returns.loc[common]
    b = r_gold.loc[common]
    if a.mean() / a.std(ddof=0) <= b.mean() / b.std(ddof=0):
        # Skip if the synthetic case violates the prerequisite.
        pytest.skip("Synthetic r_046 not higher-Sharpe than gold TSM in this seed.")

    sharpe_a_only = (a.mean() / a.std(ddof=0)) * np.sqrt(252)

    c10 = combine_046_plus_gold(
        synthetic_iter046_returns, r_gold, w_046=0.90, w_gold=0.10
    )
    c50 = combine_046_plus_gold(
        synthetic_iter046_returns, r_gold, w_046=0.50, w_gold=0.50
    )
    s10 = (c10.mean() / c10.std(ddof=0)) * np.sqrt(252)
    s50 = (c50.mean() / c50.std(ddof=0)) * np.sqrt(252)

    # Distance from r_046 Sharpe should be smaller at w=0.10
    assert abs(s10 - sharpe_a_only) < abs(s50 - sharpe_a_only), (
        f"Expected w=0.10 to dilute less than w=0.50: "
        f"s_a={sharpe_a_only:.4f}, s10={s10:.4f}, s50={s50:.4f}"
    )
