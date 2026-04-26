"""TDD tests for iter 020's 3-stream IC-7 Markowitz tangency composition.

Extends iter 019's 2-stream tests with the 3-asset tangency solver,
3-pair rolling-ρ pre-val, 3-stream linear composition, and corner-clamp
fallback for negative weights.

Citations
---------
* `[advances_fin_ml, p.222-223]` — DSR + combined-Sharpe upper bound;
  multi-asset tangency formula `w ∝ Σ⁻¹μ`.
* `[risk_parity, ch.2]` — multi-asset efficient frontier generalization.
* IC-6 pre-val (sister loop iter 014/019; gold loop GS-9 corollary).
* IC-8 single cfg per iter (n_trials discipline; 1 tangency, no grid).
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
    compose_returns_3stream,
    load_component_returns_schema_a,
    load_component_returns_schema_b,
    markowitz_tangency_weights_3asset,
    rolling_pearson,
)


# ---------------------------------------------------------------------------
# 3-asset Markowitz tangency
# ---------------------------------------------------------------------------


def test_tangency_3asset_equal_mu_identity_cov_returns_equal_weights() -> None:
    """μ = [m, m, m], Σ = I → w = [1/3, 1/3, 1/3]."""
    mu = np.array([0.001, 0.001, 0.001])
    sigma = np.array([1.0, 1.0, 1.0])  # σ=1 → diagonal covariance is identity
    rho = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ])
    w = markowitz_tangency_weights_3asset(mu=mu, sigma=sigma, rho=rho)
    assert sum(w) == pytest.approx(1.0, abs=1e-9)
    for wi in w:
        assert wi == pytest.approx(1.0 / 3.0, abs=1e-9)


def test_tangency_3asset_proportional_to_sharpe_when_uncorrelated() -> None:
    """ρ = 0 with σ_i = σ: w_i ∝ μ_i (i.e., proportional to expected return)."""
    mu = np.array([0.0010, 0.0005, 0.0002])
    sigma = np.array([0.01, 0.01, 0.01])
    rho = np.zeros((3, 3))
    np.fill_diagonal(rho, 1.0)
    w = markowitz_tangency_weights_3asset(mu=mu, sigma=sigma, rho=rho)
    assert sum(w) == pytest.approx(1.0, abs=1e-9)
    # Expected: w_i ∝ μ_i → normalize μ
    expected = mu / mu.sum()
    for wi, exp in zip(w, expected):
        assert wi == pytest.approx(exp, abs=1e-9)


def test_tangency_3asset_solves_sigma_w_proportional_to_mu() -> None:
    """`Σ·w_unnormalized ∝ μ` is the defining tangency identity."""
    mu = np.array([0.0008, 0.0006, 0.0004])
    sigma = np.array([0.012, 0.015, 0.010])
    rho = np.array([
        [1.0, 0.20, 0.05],
        [0.20, 1.0, 0.10],
        [0.05, 0.10, 1.0],
    ])
    w = markowitz_tangency_weights_3asset(mu=mu, sigma=sigma, rho=rho)
    # Reconstruct covariance
    cov = np.outer(sigma, sigma) * rho
    # The unnormalized solution Σ⁻¹μ scales by some k > 0
    raw = np.linalg.solve(cov, mu)
    # Normalize to sum 1 and compare
    expected = raw / raw.sum()
    np.testing.assert_allclose(np.array(w), expected, atol=1e-12)
    # Sum invariant
    assert sum(w) == pytest.approx(1.0, abs=1e-12)


def test_tangency_3asset_corner_clamp_when_one_weight_negative() -> None:
    """If unconstrained tangency yields w_i < 0, drop that asset, re-solve 2-asset."""
    # Construct: stream 3 has high σ + correlated with stream 1 → negative weight expected
    mu = np.array([0.0010, 0.0005, 0.0001])  # 3rd has tiny edge
    sigma = np.array([0.010, 0.012, 0.020])
    rho = np.array([
        [1.0, 0.0, 0.7],   # 3 strongly correlated with 1 → 3 redundant
        [0.0, 1.0, 0.0],
        [0.7, 0.0, 1.0],
    ])
    w = markowitz_tangency_weights_3asset(
        mu=mu, sigma=sigma, rho=rho, allow_negative=False,
    )
    assert sum(w) == pytest.approx(1.0, abs=1e-9)
    # No weight negative
    assert all(wi >= -1e-12 for wi in w)


def test_tangency_3asset_no_clamp_when_solver_natural_positive() -> None:
    """If unconstrained tangency is naturally positive, allow_negative=False is no-op."""
    mu = np.array([0.0010, 0.0010, 0.0010])
    sigma = np.array([0.01, 0.01, 0.01])
    rho = np.array([
        [1.0, 0.1, 0.1],
        [0.1, 1.0, 0.1],
        [0.1, 0.1, 1.0],
    ])
    w_open = markowitz_tangency_weights_3asset(mu, sigma, rho, allow_negative=True)
    w_clamp = markowitz_tangency_weights_3asset(mu, sigma, rho, allow_negative=False)
    np.testing.assert_allclose(np.array(w_open), np.array(w_clamp), atol=1e-12)


# ---------------------------------------------------------------------------
# 3-stream linear composition (drops bars not present in all 3)
# ---------------------------------------------------------------------------


def test_compose_returns_3stream_inner_join() -> None:
    """Triple inner-join: only bars present in all 3 streams contribute."""
    idx_full = pd.date_range("2024-01-01", periods=5, freq="D")
    a = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05], index=idx_full)
    b = pd.Series([0.10, 0.20, 0.30, 0.40], index=idx_full[1:])  # 4 bars
    c = pd.Series([1.00, 2.00, 3.00], index=idx_full[2:])  # 3 bars
    out = compose_returns_3stream(a, b, c, w_a=0.5, w_b=0.3, w_c=0.2)
    # Intersection of all 3: indices 2024-01-03..05 → 3 entries
    assert len(out) == 3
    # First common date 2024-01-03: a=0.03, b=0.20, c=1.00
    expected = 0.5 * 0.03 + 0.3 * 0.20 + 0.2 * 1.00
    assert out.iloc[0] == pytest.approx(expected, abs=1e-12)


def test_compose_returns_3stream_dropna_handles_missing() -> None:
    """NaN bars in any stream are dropped on triple inner-join."""
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    a = pd.Series([0.01, np.nan, 0.03, 0.04], index=idx)
    b = pd.Series([0.10, 0.20, np.nan, 0.40], index=idx)
    c = pd.Series([1.00, 2.00, 3.00, 4.00], index=idx)
    out = compose_returns_3stream(a, b, c, w_a=1 / 3, w_b=1 / 3, w_c=1 / 3)
    # Only Jan-1 and Jan-4 are non-NaN in all three
    assert len(out) == 2


def test_compose_returns_3stream_identity_invariance() -> None:
    """If a == b == c and w_a + w_b + w_c = 1, composed = a."""
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    s = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05], index=idx)
    out = compose_returns_3stream(s, s, s, w_a=0.5, w_b=0.3, w_c=0.2)
    pd.testing.assert_series_equal(out.rename(s.name), s, check_names=False)


# ---------------------------------------------------------------------------
# Loader regression (Schema A + Schema B preserved from iter 019)
# ---------------------------------------------------------------------------


def test_load_component_returns_schema_a_iter003(tmp_path: Path) -> None:
    """iter 003 / 015 schema: returns_series[ds][cfg_id] = {index, net_returns}."""
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


def test_load_component_returns_schema_b_iter018(tmp_path: Path) -> None:
    """iter 018 schema: datasets[ds].returns_series = {index, net_returns}."""
    fake_results = {
        "datasets": {
            "gld_long": {
                "returns_series": {
                    "index": ["2024-01-01", "2024-01-02"],
                    "net_returns": [0.02, -0.01],
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


# ---------------------------------------------------------------------------
# Rolling Pearson ρ (IC-6 pre-val) — uncorrelated random walks should stay low
# ---------------------------------------------------------------------------


def test_rolling_pearson_uncorrelated_random_walks_stays_low() -> None:
    rng = np.random.default_rng(seed=42)
    n = 1000
    a = pd.Series(
        rng.standard_normal(n),
        index=pd.date_range("2020-01-01", periods=n, freq="D"),
    )
    b = pd.Series(
        rng.standard_normal(n),
        index=pd.date_range("2020-01-01", periods=n, freq="D"),
    )
    rho = rolling_pearson(a, b, window=60)
    valid = rho.dropna()
    exceed_frac = (valid.abs() > 0.30).mean()
    assert exceed_frac < 0.25


def test_rolling_pearson_perfectly_correlated_is_one() -> None:
    rng = np.random.default_rng(seed=42)
    n = 200
    s = pd.Series(
        rng.standard_normal(n),
        index=pd.date_range("2020-01-01", periods=n, freq="D"),
    )
    rho = rolling_pearson(s, s, window=60)
    valid = rho.dropna()
    assert (valid > 0.9999).all()
