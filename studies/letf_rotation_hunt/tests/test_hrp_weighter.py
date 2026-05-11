"""Tests for HRP and ERC weighting (López de Prado ch.16).

Citation: spec §3.3 (docs/specs/2026-05-08-t5-expansion-design.md);
[advances_fin_ml, ch.16 p.221-228].
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from studies.letf_rotation_hunt.core.strategies import hrp_weighter as hw


def _gaussian_returns(seed: int, n: int, cols: list[str], cov: np.ndarray) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rets = rng.multivariate_normal(np.zeros(len(cols)), cov, size=n)
    return pd.DataFrame(
        rets, columns=cols,
        index=pd.date_range("2010-01-04", periods=n, freq="B"),
    )


def test_hrp_weights_sum_to_one_and_positive():
    cov = np.eye(4) * 0.01 ** 2
    rets = _gaussian_returns(seed=0, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_hrp_weights(rets, lookback=252, min_periods=126)
    last_row = w.iloc[-1]
    assert np.isclose(last_row.sum(), 1.0)
    assert (last_row >= 0).all()


def test_hrp_uncorrelated_equal_vol_yields_equal_weights():
    cov = np.eye(4) * 0.01 ** 2
    rets = _gaussian_returns(seed=1, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_hrp_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1].values
    # atol=0.07: seed=1 + 252-day window has max off-diagonal sample corr ~0.20,
    # so HRP weights deviate ~0.06 from exact equal — a wider tolerance is correct
    # [advances_fin_ml, ch.16]: HRP converges to equal weight asymptotically.
    np.testing.assert_allclose(last, np.full(4, 0.25), atol=0.07)


def test_hrp_high_vol_asset_gets_lower_weight():
    cov = np.diag([0.01, 0.01, 0.01, 0.05]) ** 2
    rets = _gaussian_returns(seed=2, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_hrp_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1]
    assert last["D"] < last[["A", "B", "C"]].min()


def test_erc_weights_sum_to_one_and_positive():
    cov = np.diag([0.01, 0.02, 0.03, 0.04]) ** 2
    rets = _gaussian_returns(seed=3, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_erc_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1]
    assert np.isclose(last.sum(), 1.0, atol=1e-6)
    assert (last > 0).all()


def test_erc_equal_vol_yields_equal_weights():
    cov = np.eye(4) * 0.01 ** 2
    rets = _gaussian_returns(seed=4, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_erc_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1].values
    # atol=0.03: seed=4 + 252-day window has sample variance spread ~28%
    # (8.7e-5 to 1.18e-4) plus small off-diagonal correlations.  ERC correctly
    # equalises risk contribution given the sample covariance, so weights deviate
    # from exact 0.25 by up to ~0.027 — a wider tolerance is correct.
    # [Maillard 2010]: ERC converges to equal weight asymptotically as n→∞.
    np.testing.assert_allclose(last, np.full(4, 0.25), atol=0.03)


def test_erc_higher_vol_asset_gets_lower_weight():
    cov = np.diag([0.01, 0.01, 0.01, 0.10]) ** 2
    rets = _gaussian_returns(seed=5, n=400, cols=list("ABCD"), cov=cov)
    w = hw.compute_erc_weights(rets, lookback=252, min_periods=126)
    last = w.iloc[-1]
    assert last["D"] < 0.10  # highest-vol asset gets <10%
