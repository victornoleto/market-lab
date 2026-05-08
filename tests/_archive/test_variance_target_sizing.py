"""TDD specs for Moreira-Muir variance-scaling position sizing.

The mechanism under test is `apply_variance_target(returns, target_vol,
lookback, max_leverage)` which scales daily returns by
``s_t = target_vol**2 / sigma_hat**2_{t-1}`` clipped to ``[0, cap]``.
This is the canonical formulation from Moreira & Muir (2017) *JoF* 72(4),
distinct from the vol-scaling (`σ^{-1}`) form already shipped in
`market_lab.backtest.metrics.vol_target.apply_vol_target`.

Citations:
* Moreira & Muir (2017), *Journal of Finance* 72(4), 1611-1644.
* `[systematic_trading, p.107-111]` — vol standardisation family (iter 004
  used the first-order form).
* `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag (no look-ahead).

Spec: `studies/strategy_hunt_loop/iterations/005-2026-04-24-1008-variance-managed-spy/hypothesis.md`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = (
    Path(__file__).resolve().parents[1]
    / "studies"
    / "strategy_hunt_loop"
    / "iterations"
    / "005-2026-04-24-1008-variance-managed-spy"
)
sys.path.insert(0, str(ITER_DIR))

from variance_target import apply_variance_target  # noqa: E402


def _ar1_returns(n: int, sigma: float, seed: int = 0) -> pd.Series:
    rng = np.random.default_rng(seed)
    eps = rng.normal(0.0, sigma, size=n)
    idx = pd.bdate_range("2000-01-03", periods=n)
    return pd.Series(eps, index=idx, name="r")


def test_variance_scaling_matches_squared_denominator_formula() -> None:
    """scale_t == target_vol**2 / sigma_hat**2_{t-1} (pre-clip)."""
    r = _ar1_returns(500, sigma=0.01)
    target_vol = 0.15
    lookback = 21
    scaled, scale = apply_variance_target(
        r, target_vol=target_vol, lookback=lookback, max_leverage=100.0
    )
    # Reconstruct σ̂_{t-1}² manually from the lagged rolling std.
    ann_vol = r.rolling(lookback, min_periods=lookback).std(ddof=0) * np.sqrt(252)
    ann_vol_prev = ann_vol.shift(1)
    expected_scale = (target_vol ** 2) / (ann_vol_prev ** 2)
    expected_scale = expected_scale.reindex(scale.index)
    assert np.allclose(scale.to_numpy(), expected_scale.to_numpy(), rtol=1e-9, atol=1e-12)


def test_no_look_ahead_first_valid_bar_uses_lagged_window() -> None:
    """The first valid scale bar must sit at index `lookback`, not `lookback-1`.

    ``σ̂_{t-1}`` computed over [t-L, t-1] needs the rolling window to have
    at least `lookback` past points, so the first valid scale is on bar
    index ``lookback``.
    """
    r = _ar1_returns(50, sigma=0.01)
    lookback = 10
    scaled, scale = apply_variance_target(
        r, target_vol=0.15, lookback=lookback, max_leverage=3.0
    )
    first_valid = scale.index[0]
    first_valid_pos = r.index.get_loc(first_valid)
    assert first_valid_pos >= lookback, (
        f"variance-scaling leaked look-ahead: first valid scale at position "
        f"{first_valid_pos}, need ≥ {lookback}"
    )


def test_scale_clipped_to_max_leverage() -> None:
    """Scales above `max_leverage` must be clipped (low-vol regime guard)."""
    # Build a returns series with very low realised variance — raw scale blows up.
    n = 200
    idx = pd.bdate_range("2020-01-02", periods=n)
    r = pd.Series(np.full(n, 1e-6), index=idx)  # near-zero returns → near-zero vol
    r.iloc[::20] = 1e-4  # slight perturbation so std > 0
    target_vol = 0.20
    cap = 2.0
    _, scale = apply_variance_target(
        r, target_vol=target_vol, lookback=20, max_leverage=cap
    )
    assert scale.max() <= cap + 1e-12, (
        f"scale exceeded max_leverage {cap}: max = {scale.max()}"
    )
    # And at least some bars should actually hit the cap — otherwise the
    # test universe wasn't extreme enough to exercise the clip.
    assert (scale >= cap - 1e-9).any()


def test_zero_variance_degenerate_case_clips_to_cap() -> None:
    """If σ̂_{t-1}**2 == 0, scale is defined as max_leverage (infinite demand)."""
    n = 100
    idx = pd.bdate_range("2020-01-02", periods=n)
    r = pd.Series(np.zeros(n), index=idx)  # all-zero returns → σ̂ = 0
    # First value needs to be non-zero so there's at least one bar to yield
    # a scaled output; otherwise the function should still behave cleanly.
    r.iloc[0] = 1e-4
    cap = 3.0
    scaled, scale = apply_variance_target(
        r, target_vol=0.15, lookback=20, max_leverage=cap
    )
    # All valid scales should equal the cap (σ² ≈ 0 → raw scale → ∞ → clipped).
    assert (scale <= cap + 1e-12).all()
    # Most should equal the cap; allow 1-bar tolerance for the perturbation edge.
    at_cap_frac = np.isclose(scale, cap, atol=1e-9).mean()
    assert at_cap_frac >= 0.8, f"expected ≥ 80% scales at cap, got {at_cap_frac:.2%}"


def test_variance_scaling_stronger_than_vol_scaling_on_vol_shock() -> None:
    """For a 2× vol shock, variance-scaling halves the scale relative to vol-scaling.

    Concretely: if bar t-1 realised vol is 2× the target vol, vol-scaling
    gives ``s=0.5``; variance-scaling gives ``s=0.25``. This encodes the
    core Moreira-Muir claim (2× responsiveness exponent).
    """
    from market_lab.backtest.metrics.vol_target import apply_vol_target

    # Build a returns series whose rolling vol is ≈ 2× target_vol for a stretch.
    n = 100
    idx = pd.bdate_range("2020-01-02", periods=n)
    target_vol = 0.15
    # Vol target is 0.15/sqrt(252) ≈ 0.00945 per-bar. Make returns 2× that.
    per_bar_target = target_vol / np.sqrt(252)
    r = pd.Series(
        np.where(np.arange(n) % 2 == 0, 2 * per_bar_target, -2 * per_bar_target),
        index=idx,
        dtype=float,
    )
    lookback = 10
    _, scale_vol = apply_vol_target(
        r, target_vol=target_vol, lookback=lookback, max_leverage=100.0
    )
    _, scale_var = apply_variance_target(
        r, target_vol=target_vol, lookback=lookback, max_leverage=100.0
    )
    # The realised ann-vol for a ±2×per_bar_target sawtooth ≈ 2 × target_vol.
    # So scale_vol ≈ target / (2*target) = 0.5; scale_var ≈ target² / (2*target)² = 0.25.
    # Pick a mid-series point to avoid edge effects.
    mid = len(scale_vol) // 2
    assert abs(scale_vol.iloc[mid] - 0.5) < 0.05, (
        f"vol-scaling gave {scale_vol.iloc[mid]:.3f}, expected ≈ 0.5"
    )
    assert abs(scale_var.iloc[mid] - 0.25) < 0.05, (
        f"variance-scaling gave {scale_var.iloc[mid]:.3f}, expected ≈ 0.25"
    )
    # The critical inequality: variance-scaling < vol-scaling (stronger de-levering).
    assert scale_var.iloc[mid] < scale_vol.iloc[mid]


@pytest.mark.parametrize("bad_target_vol", [0.0, -0.1])
def test_rejects_nonpositive_target_vol(bad_target_vol: float) -> None:
    with pytest.raises(ValueError, match="target_vol"):
        apply_variance_target(
            _ar1_returns(100, 0.01),
            target_vol=bad_target_vol,
            lookback=20,
            max_leverage=2.0,
        )


@pytest.mark.parametrize("bad_lookback", [0, 1])
def test_rejects_invalid_lookback(bad_lookback: int) -> None:
    with pytest.raises(ValueError, match="lookback"):
        apply_variance_target(
            _ar1_returns(100, 0.01),
            target_vol=0.15,
            lookback=bad_lookback,
            max_leverage=2.0,
        )


def test_rejects_nonpositive_max_leverage() -> None:
    with pytest.raises(ValueError, match="max_leverage"):
        apply_variance_target(
            _ar1_returns(100, 0.01),
            target_vol=0.15,
            lookback=20,
            max_leverage=0.0,
        )
