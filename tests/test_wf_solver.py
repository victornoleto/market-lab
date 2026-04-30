"""Tests for ``studies/_shared/wf_solver``."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studies"))

from _shared.wf_solver import WFResult, walk_forward_solve  # noqa: E402


@pytest.fixture
def synthetic_5_sleeve() -> pd.DataFrame:
    np.random.seed(42)
    n = 6 * 252
    idx = pd.bdate_range("2010-01-01", periods=n)
    daily_sigma = 1.0 / np.sqrt(252)
    return pd.DataFrame(
        {
            "S1_dominant": np.random.normal(0.10 / 252, 0.10 * daily_sigma, n),
            "S2": np.random.normal(0.04 / 252, 0.15 * daily_sigma, n),
            "S3": np.random.normal(0.05 / 252, 0.18 * daily_sigma, n),
            "S4": np.random.normal(0.03 / 252, 0.16 * daily_sigma, n),
            "S5": np.random.normal(0.06 / 252, 0.20 * daily_sigma, n),
        },
        index=idx,
    )


def test_constraints_respected(synthetic_5_sleeve: pd.DataFrame) -> None:
    res = walk_forward_solve(synthetic_5_sleeve, lookback_months=36, max_weight=0.40)

    assert isinstance(res, WFResult)
    assert len(res.weights) > 0
    sums = res.weights.sum(axis=1)
    assert np.allclose(sums.values, 1.0, atol=1e-4)
    assert (res.weights.values >= -1e-6).all()
    assert (res.weights.values <= 0.40 + 1e-6).all()
    assert not res.weights.isna().any().any()
    assert not res.portfolio_returns.isna().any()


def test_dominant_sleeve_gets_high_weight(synthetic_5_sleeve: pd.DataFrame) -> None:
    """Sharpe-dominant sleeve should average >=30% under max-Sharpe."""
    res = walk_forward_solve(
        synthetic_5_sleeve, lookback_months=36, max_weight=0.40, objective="sharpe"
    )
    avg_dom = float(res.weights["S1_dominant"].mean())
    assert avg_dom >= 0.30, f"dominant avg weight {avg_dom:.3f} < 0.30"


def test_embargo_changes_weights() -> None:
    np.random.seed(0)
    idx = pd.bdate_range("2018-01-01", "2024-01-01")
    df = pd.DataFrame(
        {
            "A": np.random.normal(0.0003, 0.01, len(idx)),
            "B": np.random.normal(0.0002, 0.012, len(idx)),
        },
        index=idx,
    )
    r0 = walk_forward_solve(df, lookback_months=12, max_weight=0.6, embargo_days=0)
    r30 = walk_forward_solve(df, lookback_months=12, max_weight=0.6, embargo_days=30)
    common = r0.weights.index.intersection(r30.weights.index)
    assert len(common) > 30, "expected substantial overlap of rebal dates"
    diff_total = float(
        np.abs(r0.weights.loc[common].values - r30.weights.loc[common].values).sum()
    )
    assert diff_total > 1e-3, "embargo should perturb weights probabilistically"


def test_cagr_objective_runs(synthetic_5_sleeve: pd.DataFrame) -> None:
    res = walk_forward_solve(
        synthetic_5_sleeve, lookback_months=36, max_weight=0.40, objective="cagr"
    )
    assert len(res.weights) > 0
    sums = res.weights.sum(axis=1)
    assert np.allclose(sums.values, 1.0, atol=1e-4)
    assert (res.weights.values <= 0.40 + 1e-6).all()


def test_warmup_skipped() -> None:
    np.random.seed(1)
    idx = pd.bdate_range("2020-01-01", "2024-01-01")
    df = pd.DataFrame(
        {
            "A": np.random.normal(0.0001, 0.01, len(idx)),
            "B": np.random.normal(0.0001, 0.01, len(idx)),
        },
        index=idx,
    )
    res = walk_forward_solve(df, lookback_months=36, max_weight=1.0)
    if len(res.weights) > 0:
        first_rebal = res.weights.index[0]
        assert first_rebal >= idx[0] + pd.DateOffset(months=36) - pd.Timedelta(days=15)
