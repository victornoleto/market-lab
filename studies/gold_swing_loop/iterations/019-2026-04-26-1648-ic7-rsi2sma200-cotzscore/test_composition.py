"""TDD tests for iter 019's IC-7 003+018 Markowitz tangency composition.

Tests cover:
- Schema-aware return loaders (Schema A from iter 003, Schema B from iter 018).
- Markowitz tangency weights at ρ=0 (analytical closed form).
- Linear composition on inner-joined indices.
- Rolling 60d ρ helper (IC-6 pre-val).

Citations
---------
* `[advances_fin_ml, p.222-223]` — DSR + combined-Sharpe upper bound.
* IC-6 pre-val (sister loop iter 007/008/009-corollary GS-9).
* IC-8 single cfg per iter (n_trials discipline).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))

from run_backtest import (  # noqa: E402
    compose_returns,
    load_component_returns_schema_a,
    load_component_returns_schema_b,
    markowitz_tangency_weights,
    rolling_pearson,
)


# ---------------------------------------------------------------------------
# Markowitz tangency
# ---------------------------------------------------------------------------


def test_markowitz_tangency_uncorrelated_proportional_to_sharpe_ratio() -> None:
    """At ρ=0 with σ_A = σ_B, w_A / w_B = μ_A / μ_B (∝ Sharpe ratio)."""
    mu = np.array([0.0010, 0.0005])
    sigma = np.array([0.010, 0.010])
    w_a, w_b = markowitz_tangency_weights(mu=mu, sigma=sigma, rho=0.0)
    # Expected: ratio of μ since σ are equal and ρ=0 → Σ⁻¹μ_i = μ_i/σ²
    # Normalized to sum 1: w_a = 2/3, w_b = 1/3.
    assert w_a + w_b == pytest.approx(1.0, abs=1e-9)
    assert w_a / w_b == pytest.approx(mu[0] / mu[1], rel=1e-9)
    assert w_a == pytest.approx(2.0 / 3.0, abs=1e-9)
    assert w_b == pytest.approx(1.0 / 3.0, abs=1e-9)


def test_markowitz_tangency_unequal_sigma_uncorrelated() -> None:
    """At ρ=0, w_A ∝ μ_A / σ_A² (signal-to-variance)."""
    mu = np.array([0.0006, 0.0006])
    sigma = np.array([0.010, 0.020])
    w_a, w_b = markowitz_tangency_weights(mu=mu, sigma=sigma, rho=0.0)
    assert w_a + w_b == pytest.approx(1.0, abs=1e-9)
    raw_a = mu[0] / (sigma[0] ** 2)
    raw_b = mu[1] / (sigma[1] ** 2)
    expected_a = raw_a / (raw_a + raw_b)
    assert w_a == pytest.approx(expected_a, abs=1e-9)
    assert w_a > w_b  # tighter-σ stream gets more weight


def test_markowitz_tangency_correlated_blends_in_covariance() -> None:
    """ρ ≠ 0 changes weights via the off-diagonal."""
    mu = np.array([0.0010, 0.0005])
    sigma = np.array([0.010, 0.010])
    w_a_uncorr, w_b_uncorr = markowitz_tangency_weights(mu, sigma, rho=0.0)
    w_a_pos, w_b_pos = markowitz_tangency_weights(mu, sigma, rho=0.5)
    # Positive correlation reduces the diversification benefit; the weight
    # on the lower-Sharpe stream falls (or even goes negative).
    assert w_b_pos < w_b_uncorr
    assert (w_a_pos + w_b_pos) == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# compose_returns (linear weighted sum on inner-join)
# ---------------------------------------------------------------------------


def test_compose_returns_inner_join_simple() -> None:
    """Weighted-sum on intersection of two pd.Series indices."""
    idx_a = pd.date_range("2024-01-01", periods=5, freq="D")
    idx_b = pd.date_range("2024-01-03", periods=5, freq="D")
    a = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05], index=idx_a)
    b = pd.Series([0.10, 0.20, 0.30, 0.40, 0.50], index=idx_b)
    out = compose_returns(a=a, b=b, w_a=0.5, w_b=0.5)
    # Intersection: 2024-01-03, 04, 05 → 3 entries
    assert len(out) == 3
    # First common date 2024-01-03: a=0.03, b=0.10 → 0.5*0.03 + 0.5*0.10 = 0.065
    assert out.iloc[0] == pytest.approx(0.065, abs=1e-12)
    # Second: a=0.04, b=0.20 → 0.5*0.04 + 0.5*0.20 = 0.12
    assert out.iloc[1] == pytest.approx(0.12, abs=1e-12)


def test_compose_returns_dropna_handles_missing() -> None:
    """NaN bars on either side are dropped (no spurious zeros)."""
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    a = pd.Series([0.01, np.nan, 0.03, 0.04], index=idx)
    b = pd.Series([0.10, 0.20, np.nan, 0.40], index=idx)
    out = compose_returns(a=a, b=b, w_a=0.5, w_b=0.5)
    # Only Jan-1 and Jan-4 have both → 2 entries
    assert len(out) == 2


def test_compose_returns_weights_sum_to_one_invariant() -> None:
    """If A == B exactly and w_a+w_b=1, composed = A."""
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    s = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05], index=idx)
    out = compose_returns(a=s, b=s, w_a=0.6, w_b=0.4)
    pd.testing.assert_series_equal(
        out.rename(s.name),
        s,
        check_names=False,
    )


# ---------------------------------------------------------------------------
# Loader: schema A (iter 003) — top-level returns_series[ds][cfg_id]
# ---------------------------------------------------------------------------


def test_load_component_returns_schema_a_iter003(tmp_path: Path) -> None:
    """iter 003 stores returns at returns_series[ds][cfg_id] = {index,net_returns}."""
    fake_results = {
        "config_id": "fake_cfg",
        "returns_series": {
            "gld_long": {
                "fake_cfg": {
                    "index": ["2024-01-01", "2024-01-02", "2024-01-03"],
                    "net_returns": [0.01, -0.005, 0.015],
                }
            }
        },
    }
    iter_dir = tmp_path / "iter003"
    iter_dir.mkdir()
    (iter_dir / "results.json").write_text(json.dumps(fake_results))
    out = load_component_returns_schema_a(iter_dir, "gld_long", "fake_cfg")
    assert len(out) == 3
    assert out.iloc[0] == pytest.approx(0.01)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_load_component_returns_schema_a_missing_cfg(tmp_path: Path) -> None:
    """Missing cfg_id raises KeyError."""
    fake_results = {
        "returns_series": {
            "gld_long": {"other_cfg": {"index": [], "net_returns": []}}
        }
    }
    iter_dir = tmp_path / "iter003"
    iter_dir.mkdir()
    (iter_dir / "results.json").write_text(json.dumps(fake_results))
    with pytest.raises(KeyError, match="missing_cfg"):
        load_component_returns_schema_a(iter_dir, "gld_long", "missing_cfg")


# ---------------------------------------------------------------------------
# Loader: schema B (iter 018) — datasets[ds].returns_series = {index,net_returns}
# ---------------------------------------------------------------------------


def test_load_component_returns_schema_b_iter018(tmp_path: Path) -> None:
    """iter 018 stores returns at datasets[ds].returns_series = {index,net_returns}."""
    fake_results = {
        "datasets": {
            "gld_long": {
                "returns_series": {
                    "index": ["2024-01-01", "2024-01-02"],
                    "net_returns": [0.02, -0.01],
                    "position": [1, 1],
                }
            }
        }
    }
    iter_dir = tmp_path / "iter018"
    iter_dir.mkdir()
    (iter_dir / "results.json").write_text(json.dumps(fake_results))
    out = load_component_returns_schema_b(iter_dir, "gld_long")
    assert len(out) == 2
    assert out.iloc[0] == pytest.approx(0.02)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_load_component_returns_schema_b_missing_dataset(tmp_path: Path) -> None:
    """Missing dataset raises KeyError."""
    fake_results = {"datasets": {"gld_long": {"returns_series": {"index": [], "net_returns": []}}}}
    iter_dir = tmp_path / "iter018"
    iter_dir.mkdir()
    (iter_dir / "results.json").write_text(json.dumps(fake_results))
    with pytest.raises(KeyError, match="xauusd_intraday"):
        load_component_returns_schema_b(iter_dir, "xauusd_intraday")


# ---------------------------------------------------------------------------
# Rolling Pearson ρ (IC-6 pre-val)
# ---------------------------------------------------------------------------


def test_rolling_pearson_uncorrelated_random_walks_stays_low() -> None:
    """Independent random series → most rolling ρ within ±0.30."""
    rng = np.random.default_rng(seed=42)
    n = 1000
    a = pd.Series(rng.standard_normal(n), index=pd.date_range("2020-01-01", periods=n, freq="D"))
    b = pd.Series(rng.standard_normal(n), index=pd.date_range("2020-01-01", periods=n, freq="D"))
    rho = rolling_pearson(a, b, window=60)
    valid = rho.dropna()
    # Most bars should have |ρ| < 0.30 (independent series); allow up to 25%
    # for finite-sample sampling noise on a 60-bar window.
    exceed_frac = (valid.abs() > 0.30).mean()
    assert exceed_frac < 0.25


def test_rolling_pearson_perfectly_correlated_is_one() -> None:
    """If a == b exactly, rolling ρ ≈ 1 once warmup completes."""
    rng = np.random.default_rng(seed=42)
    n = 200
    s = pd.Series(rng.standard_normal(n), index=pd.date_range("2020-01-01", periods=n, freq="D"))
    rho = rolling_pearson(s, s, window=60)
    valid = rho.dropna()
    assert (valid > 0.9999).all()


def test_rolling_pearson_inner_join_intersection() -> None:
    """Index mismatch: only common dates are returned."""
    a = pd.Series([1.0, 2.0, 3.0], index=pd.date_range("2024-01-01", periods=3, freq="D"))
    b = pd.Series([1.0, 2.0, 3.0], index=pd.date_range("2024-01-02", periods=3, freq="D"))
    rho = rolling_pearson(a, b, window=2)
    # Intersection length = 2 → only one valid bar after warmup
    assert len(rho) == 2
