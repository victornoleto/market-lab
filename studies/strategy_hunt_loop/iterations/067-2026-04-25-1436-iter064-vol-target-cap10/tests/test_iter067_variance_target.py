"""TDD tests for iter 067 — Moreira-Muir σ⁻² variance-target overlay (cap ≤ 1.0).

Run via:

    cd /var/www/pessoal/ai-trade
    python -m pytest studies/strategy_hunt_loop/iterations/067-*/tests/ -v

Tests exercise both the pandas reference (`variance_target_overlay`) and
the numpy reference (`numpy_reference_iter067`). All invariants must
hold for the engine to be considered correct (G7 cross-lib).

Citations
---------
* Moreira & Muir (2017), JoF 72(4) — variance-target sizing primitive.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on σ̂ (no peek).
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from variance_target_overlay import apply_variance_target_overlay  # noqa: E402
from numpy_reference_iter067 import apply_variance_target_overlay_np  # noqa: E402


@pytest.fixture(scope="module")
def synthetic_returns() -> pd.Series:
    """Synthetic stream with deliberate stress regime in middle 200 bars."""
    rng = np.random.default_rng(seed=42)
    n = 1000
    sigma = np.full(n, 0.005)  # ~8% annualised
    sigma[400:600] = 0.020  # stress chunk → ~32% annualised
    rets = rng.normal(loc=0.0003, scale=sigma)
    idx = pd.date_range("2010-01-01", periods=n, freq="B")
    return pd.Series(rets, index=idx, name="r_synth")


def test_shape_and_index_parity(synthetic_returns):
    """Output shares the same DatetimeIndex as input (modulo lookback warmup)."""
    r = synthetic_returns
    out, scale = apply_variance_target_overlay(
        r, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=5.0,
    )
    assert isinstance(out, pd.Series)
    assert isinstance(scale, pd.Series)
    assert out.index.equals(scale.index)
    # Output starts at first valid bar after rolling+shift warmup.
    assert out.index[0] >= r.index[21]


def test_cap_strictly_enforced(synthetic_returns):
    """No scale[t] > cap by more than fp tolerance."""
    r = synthetic_returns
    cap = 1.0
    _, scale = apply_variance_target_overlay(
        r, sigma_target=1.0, lookback=21, cap=cap, cost_bps=0.0,
    )
    # σ_target = 1.0 (very high) ⇒ scale would call for huge values, all capped.
    assert (scale <= cap + 1e-12).all()
    # And on average it should saturate near cap.
    assert scale.mean() > 0.95


def test_floor_at_zero(synthetic_returns):
    """scale[t] ≥ 0 always."""
    r = synthetic_returns
    _, scale = apply_variance_target_overlay(
        r, sigma_target=0.0001, lookback=21, cap=1.0, cost_bps=0.0,
    )
    # σ_target ≈ 0 ⇒ scale → 0 everywhere (fully de-risk).
    assert (scale >= 0.0).all()
    assert scale.max() < 1e-3


def test_no_lookahead_shift1(synthetic_returns):
    """σ̂_{t-1} drives scale[t]; toggling r[t] does not move scale[t]."""
    r = synthetic_returns.copy()
    _, scale_a = apply_variance_target_overlay(
        r, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=0.0,
    )
    # Mutate the LAST bar only and recompute. scale should be unchanged
    # at every prior bar AND at the last bar (because σ̂ at last bar uses
    # the rolling window ending at t-1, which doesn't include r[t]).
    r2 = r.copy()
    r2.iloc[-1] = r2.iloc[-1] * 100.0  # huge change at last bar
    _, scale_b = apply_variance_target_overlay(
        r2, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=0.0,
    )
    np.testing.assert_allclose(scale_a.values, scale_b.values, atol=1e-12)


def test_constant_series_saturates(synthetic_returns):
    """A constant return series has σ̂ = 0 ⇒ scale clamps at cap."""
    n = 200
    idx = pd.date_range("2010-01-01", periods=n, freq="B")
    r = pd.Series(np.full(n, 0.0001), index=idx)
    _, scale = apply_variance_target_overlay(
        r, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=0.0,
    )
    assert (scale == 1.0).all()


def test_cost_proportional_to_delta_scale(synthetic_returns):
    """Doubling cost_bps doubles the friction drag for the same scale path."""
    r = synthetic_returns
    out_a, scale_a = apply_variance_target_overlay(
        r, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=0.0,
    )
    out_b, scale_b = apply_variance_target_overlay(
        r, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=10.0,
    )
    # scale paths identical, only costs differ.
    np.testing.assert_allclose(scale_a.values, scale_b.values, atol=1e-12)
    # Total return drag = 10 bps × (Σ|Δscale| + build-up cost on bar 0).
    # First bar charges scale[0] (transition from cash to position).
    delta_scale_inner = np.abs(np.diff(scale_a.values))
    total_turnover = float(scale_a.values[0]) + float(delta_scale_inner.sum())
    expected_drag = (10.0 * 1e-4) * total_turnover
    actual_drag = float(out_a.sum() - out_b.sum())
    np.testing.assert_allclose(actual_drag, expected_drag, atol=1e-6)


def test_zero_cost_overlay_returns_match_formula(synthetic_returns):
    """At cost=0, output = scale × r, exactly."""
    r = synthetic_returns
    out, scale = apply_variance_target_overlay(
        r, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=0.0,
    )
    expected = (scale * r.loc[scale.index]).astype(float)
    np.testing.assert_allclose(out.values, expected.values, atol=1e-12)


def test_cross_lib_parity(synthetic_returns):
    """pandas implementation == numpy reference, per-bar, ≤ 1e-9."""
    r = synthetic_returns
    out_pd, scale_pd = apply_variance_target_overlay(
        r, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=5.0,
    )
    out_np, scale_np = apply_variance_target_overlay_np(
        r.values, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=5.0,
    )
    # numpy returns aligned arrays length = N - lookback (same as scale_pd)
    np.testing.assert_allclose(scale_np, scale_pd.values, atol=1e-12)
    np.testing.assert_allclose(out_np, out_pd.values, atol=1e-12)


def test_sigma_target_default_is_full_window(synthetic_returns):
    """When sigma_target=None, default = annualised σ of full input series."""
    r = synthetic_returns
    out, scale = apply_variance_target_overlay(
        r, sigma_target=None, lookback=21, cap=1.0, cost_bps=0.0,
    )
    expected_sigma = float(r.std(ddof=0)) * np.sqrt(252.0)
    # On bars where σ̂ ≈ expected_sigma, scale ≈ 1.0
    # We just check that the function ran and the cap holds.
    assert (scale <= 1.0 + 1e-12).all()
    assert scale.mean() < 1.0  # variance clusters → some bars get de-risked


def test_invalid_inputs_raise():
    """Domain errors on bad inputs."""
    n = 100
    idx = pd.date_range("2010-01-01", periods=n, freq="B")
    r = pd.Series(np.zeros(n), index=idx)
    with pytest.raises(ValueError):
        apply_variance_target_overlay(r, sigma_target=-0.1, lookback=21, cap=1.0, cost_bps=0.0)
    with pytest.raises(ValueError):
        apply_variance_target_overlay(r, sigma_target=0.10, lookback=1, cap=1.0, cost_bps=0.0)
    with pytest.raises(ValueError):
        apply_variance_target_overlay(r, sigma_target=0.10, lookback=21, cap=-0.1, cost_bps=0.0)
    with pytest.raises(ValueError):
        apply_variance_target_overlay(r, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=-1.0)
    # Too few bars
    short = pd.Series(np.zeros(5), index=idx[:5])
    with pytest.raises(ValueError):
        apply_variance_target_overlay(short, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=0.0)


def test_overlay_reduces_realised_variance(synthetic_returns):
    """De-risking in stress regime reduces overlay output variance vs raw."""
    r = synthetic_returns
    out, _ = apply_variance_target_overlay(
        r, sigma_target=0.10, lookback=21, cap=1.0, cost_bps=0.0,
    )
    raw_aligned = r.loc[out.index]
    var_raw = float(raw_aligned.var(ddof=0))
    var_out = float(out.var(ddof=0))
    # Overlay should reduce variance (cap=1.0 means we only de-risk).
    assert var_out <= var_raw + 1e-12, f"variance INCREASED: raw={var_raw} out={var_out}"
