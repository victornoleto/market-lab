"""TDD specs for iter 006 stock-bond blend sizing.

The mechanism under test is
``apply_blend_variance_target(r_spy, r_tlt, target_vol, lookback, max_leverage)``
which returns ``(net_returns, pos_spy, pos_tlt, scale)`` for a two-asset
inverse-variance-weighted blend with Moreira-Muir portfolio-level
variance-scaling applied on top.

Citations:
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity (inverse-vol /
  inverse-variance weighting is exact ERC for 2-asset portfolios).
* `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 cap.
* `[advances_fin_ml, p.162-164]` — ``σ̂_{t-1}`` lag (no look-ahead).

Spec: ``studies/strategy_hunt_loop/iterations/006-2026-04-24-1027-vol-managed-60-40/hypothesis.md``.
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
    / "006-2026-04-24-1027-vol-managed-60-40"
)
sys.path.insert(0, str(ITER_DIR))

from stock_bond_blend import apply_blend_variance_target  # noqa: E402


def _gaussian_returns(n: int, sigma: float, seed: int = 0) -> pd.Series:
    rng = np.random.default_rng(seed)
    eps = rng.normal(0.0, sigma, size=n)
    idx = pd.bdate_range("2002-07-26", periods=n)
    return pd.Series(eps, index=idx)


def test_inverse_variance_weights_sum_to_one() -> None:
    """Per-bar position_spy + position_tlt == scale (weights normalise)."""
    r_spy = _gaussian_returns(400, sigma=0.010, seed=1)
    r_tlt = _gaussian_returns(400, sigma=0.005, seed=2)
    net, pos_spy, pos_tlt, scale = apply_blend_variance_target(
        r_spy, r_tlt,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    total = pos_spy + pos_tlt
    # Total gross exposure == scale factor (weights sum to 1).
    np.testing.assert_allclose(total.to_numpy(), scale.to_numpy(), rtol=1e-12)


def test_equal_variance_legs_give_fifty_fifty_weights() -> None:
    """When σ²_spy == σ²_tlt exactly, w_spy == w_tlt == 0.5."""
    # Construct two independent streams with identical σ via different seeds.
    sigma = 0.012
    r_spy = _gaussian_returns(300, sigma=sigma, seed=11)
    r_tlt = _gaussian_returns(300, sigma=sigma, seed=22)
    # Force identical realised variance on every rolling window by using
    # the same series twice (trivial symmetric case).
    net, pos_spy, pos_tlt, scale = apply_blend_variance_target(
        r_spy, r_spy,  # same series both legs
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    # Weight per leg = scale / 2.
    np.testing.assert_allclose(pos_spy.to_numpy(), pos_tlt.to_numpy(), rtol=1e-12)
    np.testing.assert_allclose(
        pos_spy.to_numpy() + pos_tlt.to_numpy(),
        scale.to_numpy(),
        rtol=1e-12,
    )


def test_high_vol_leg_gets_smaller_weight() -> None:
    """w_spy < w_tlt when σ_spy >> σ_tlt (inverse-variance monotonicity)."""
    # SPY-leg vol 3× TLT-leg vol. Expected: w_spy ≈ 1/9 vs w_tlt ≈ 8/9.
    r_hi = _gaussian_returns(400, sigma=0.030, seed=5)
    r_lo = _gaussian_returns(400, sigma=0.010, seed=6)
    net, pos_spy, pos_tlt, scale = apply_blend_variance_target(
        r_hi, r_lo,
        target_vol=0.15, lookback=21, max_leverage=3.0,
    )
    # Drop first few bars where rolling stats may be noisy; use median
    # of last 100 bars (realised vol ratio stabilises).
    w_spy_med = (pos_spy / scale).iloc[-100:].median()
    w_tlt_med = (pos_tlt / scale).iloc[-100:].median()
    assert w_spy_med < w_tlt_med, (
        f"expected w_spy < w_tlt with σ_spy=3×σ_tlt, got "
        f"w_spy={w_spy_med:.3f} w_tlt={w_tlt_med:.3f}"
    )
    # Inverse-variance: ratio of weights = (σ_tlt/σ_spy)² ≈ 1/9.
    assert 0.05 < w_spy_med < 0.25, f"w_spy out of [0.05, 0.25]: {w_spy_med:.3f}"


def test_no_lookahead_in_portfolio_scale() -> None:
    """Swapping returns[t] for a different value should not change scale[t].

    The scale at bar t must only depend on [t-L, t-1]; swapping r[t] itself
    must leave scale[t] identical.
    """
    rng = np.random.default_rng(42)
    r_spy = pd.Series(
        rng.normal(0.0, 0.010, size=300),
        index=pd.bdate_range("2002-07-26", periods=300),
    )
    r_tlt = pd.Series(
        rng.normal(0.0, 0.005, size=300),
        index=r_spy.index,
    )
    _, _, _, scale_a = apply_blend_variance_target(
        r_spy, r_tlt, target_vol=0.15, lookback=21, max_leverage=2.0,
    )

    # Perturb ONLY the last bar's returns — scale should be identical
    # everywhere including the last bar (scale_t uses [t-L, t-1]).
    r_spy_b = r_spy.copy()
    r_tlt_b = r_tlt.copy()
    r_spy_b.iloc[-1] = 0.10  # huge shock on last bar
    r_tlt_b.iloc[-1] = -0.10
    _, _, _, scale_b = apply_blend_variance_target(
        r_spy_b, r_tlt_b, target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    np.testing.assert_allclose(scale_a.to_numpy(), scale_b.to_numpy(), rtol=1e-12)


def test_zero_portfolio_variance_goes_to_cap() -> None:
    """Degenerate σ²_port == 0 path sends scale to max_leverage."""
    # Constant-zero returns both legs → rolling var == 0 everywhere.
    n = 80
    idx = pd.bdate_range("2002-07-26", periods=n)
    r_spy = pd.Series(np.zeros(n), index=idx)
    r_tlt = pd.Series(np.zeros(n), index=idx)
    _, _, _, scale = apply_blend_variance_target(
        r_spy, r_tlt, target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    # After the lookback warmup, every bar should have scale == cap.
    assert np.allclose(scale.to_numpy(), 2.0, rtol=1e-12)


def test_cap_clipping_respects_max_leverage() -> None:
    """scale never exceeds max_leverage, even with tiny realised vol."""
    r_spy = _gaussian_returns(400, sigma=0.001, seed=9)  # very low vol
    r_tlt = _gaussian_returns(400, sigma=0.001, seed=10)
    _, pos_spy, pos_tlt, scale = apply_blend_variance_target(
        r_spy, r_tlt, target_vol=0.15, lookback=21, max_leverage=1.5,
    )
    assert scale.max() <= 1.5 + 1e-12
    assert (pos_spy + pos_tlt).max() <= 1.5 + 1e-12


def test_rejects_non_positive_target_vol() -> None:
    r_spy = _gaussian_returns(100, 0.01, seed=1)
    r_tlt = _gaussian_returns(100, 0.005, seed=2)
    with pytest.raises(ValueError):
        apply_blend_variance_target(
            r_spy, r_tlt, target_vol=0.0, lookback=21, max_leverage=2.0,
        )
    with pytest.raises(ValueError):
        apply_blend_variance_target(
            r_spy, r_tlt, target_vol=-0.05, lookback=21, max_leverage=2.0,
        )


def test_rejects_lookback_too_small() -> None:
    r_spy = _gaussian_returns(100, 0.01, seed=1)
    r_tlt = _gaussian_returns(100, 0.005, seed=2)
    with pytest.raises(ValueError):
        apply_blend_variance_target(
            r_spy, r_tlt, target_vol=0.15, lookback=1, max_leverage=2.0,
        )


def test_rejects_non_positive_max_leverage() -> None:
    r_spy = _gaussian_returns(100, 0.01, seed=1)
    r_tlt = _gaussian_returns(100, 0.005, seed=2)
    with pytest.raises(ValueError):
        apply_blend_variance_target(
            r_spy, r_tlt, target_vol=0.15, lookback=21, max_leverage=0.0,
        )


def test_mismatched_indices_fail() -> None:
    """Legs must be aligned on the same calendar."""
    r_spy = _gaussian_returns(100, 0.01, seed=1)
    r_tlt_shifted = pd.Series(
        r_spy.to_numpy(),
        index=pd.bdate_range("2003-07-26", periods=100),
    )
    with pytest.raises(ValueError):
        apply_blend_variance_target(
            r_spy, r_tlt_shifted, target_vol=0.15, lookback=21, max_leverage=2.0,
        )


def test_net_returns_match_gross_minus_cost() -> None:
    """net == scale·(w_spy·r_spy + w_tlt·r_tlt) − turnover·cost_bps."""
    r_spy = _gaussian_returns(200, sigma=0.010, seed=7)
    r_tlt = _gaussian_returns(200, sigma=0.006, seed=8)
    cost_bps = 0.0002  # 2 bps per unit of leg-scale change
    net, pos_spy, pos_tlt, scale = apply_blend_variance_target(
        r_spy, r_tlt,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        cost_bps_per_leg=cost_bps,
    )
    # Recompute gross from positions (constant intra-bar — pos_t applies to r_t).
    r_spy_aligned = r_spy.loc[pos_spy.index]
    r_tlt_aligned = r_tlt.loc[pos_tlt.index]
    gross = pos_spy * r_spy_aligned + pos_tlt * r_tlt_aligned
    # Turnover: sum |ΔPos_spy| + |ΔPos_tlt|; first bar charges full pos.
    dpos_spy = pos_spy.diff().abs().fillna(pos_spy.iloc[0])
    dpos_tlt = pos_tlt.diff().abs().fillna(pos_tlt.iloc[0])
    cost = (dpos_spy + dpos_tlt) * cost_bps
    expected_net = gross - cost
    np.testing.assert_allclose(net.to_numpy(), expected_net.to_numpy(), rtol=1e-12)
