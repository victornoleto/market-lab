"""TDD tests for loop iter 005 helper module (basket_sizer).

Per LOOP_PROTOCOL §"Scope limits": new helpers introduced by an iter live
INSIDE the iter dir. Tests for new modules go in
tests/test_letf_rotation_hunt_loop_NNN.py (mandate §3 ≥ 813 baseline).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
ITER_DIR = (
    REPO_ROOT
    / "studies"
    / "letf_rotation_hunt"
    / "loop_iterations"
    / "005-2026-05-09-multi-asset-on-invvol"
)


def _load_basket_module():
    spec = importlib.util.spec_from_file_location(
        "iter005_basket_sizer", ITER_DIR / "basket_sizer.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def basket():
    return _load_basket_module()


@pytest.fixture
def synthetic_returns():
    rng = np.random.default_rng(42)
    n = 500
    idx = pd.bdate_range("2010-01-01", periods=n)
    high_vol = pd.Series(rng.normal(0.0, 0.04, n), index=idx)
    low_vol = pd.Series(rng.normal(0.0, 0.01, n), index=idx)
    med_vol = pd.Series(rng.normal(0.0, 0.02, n), index=idx)
    return {"HIGH": high_vol, "LOW": low_vol, "MED": med_vol}


def test_realised_vol_warmup_is_nan(basket, synthetic_returns):
    s = basket.realised_vol(synthetic_returns["HIGH"], window=60)
    assert s.iloc[:59].isna().all(), "Warmup must be NaN until window full"
    assert s.iloc[60:].notna().all(), "Post-warmup vol must be defined"


def test_realised_vol_is_annualised(basket):
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2010-01-01", periods=300)
    daily_sigma = 0.02
    returns = pd.Series(rng.normal(0.0, daily_sigma, len(idx)), index=idx)
    annual_vol = basket.realised_vol(returns, window=60)
    expected = daily_sigma * np.sqrt(252.0)
    median = annual_vol.iloc[60:].median()
    assert abs(median - expected) / expected < 0.20, (
        f"Annualised vol off: {median} vs expected {expected}"
    )


def test_inverse_vol_weights_sum_to_one_post_warmup(basket, synthetic_returns):
    weights = basket.inverse_vol_weights(synthetic_returns, window=60)
    post_warmup = weights.iloc[80:]
    row_sums = post_warmup.sum(axis=1)
    assert (np.abs(row_sums - 1.0) < 1e-9).all(), "Weights must sum to 1.0"


def test_inverse_vol_assigns_higher_weight_to_lower_vol(basket, synthetic_returns):
    weights = basket.inverse_vol_weights(synthetic_returns, window=60)
    last = weights.iloc[-1]
    assert last["LOW"] > last["MED"] > last["HIGH"], (
        f"inverse-vol weights must rank inverse to vol; got {last.to_dict()}"
    )


def test_inverse_vol_warmup_is_nan(basket, synthetic_returns):
    weights = basket.inverse_vol_weights(synthetic_returns, window=60)
    assert weights.iloc[:59].isna().all().all(), "Pre-warmup rows must be NaN"


def test_equal_weights_are_constant(basket):
    idx = pd.bdate_range("2010-01-01", periods=100)
    w = basket.equal_weights(["A", "B", "C"], idx)
    assert w.shape == (100, 3)
    assert (np.abs(w.values - 1.0 / 3.0) < 1e-12).all()


def test_basket_returns_match_weighted_sum(basket, synthetic_returns):
    weights = basket.inverse_vol_weights(synthetic_returns, window=60)
    basket_ret = basket.basket_returns_from_weights(weights, synthetic_returns)
    # Manual compute on a single post-warmup day
    t = weights.index[100]
    expected = sum(
        weights.loc[t, a] * synthetic_returns[a].loc[t]
        for a in synthetic_returns
    )
    assert abs(basket_ret.loc[t] - expected) < 1e-12


def test_basket_returns_warmup_is_nan(basket, synthetic_returns):
    weights = basket.inverse_vol_weights(synthetic_returns, window=60)
    basket_ret = basket.basket_returns_from_weights(weights, synthetic_returns)
    assert basket_ret.iloc[:59].isna().all(), "Pre-warmup basket return must be NaN"
