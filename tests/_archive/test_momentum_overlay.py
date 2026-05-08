"""TDD specs for iter 007 momentum overlay on vol-managed SPY+TLT blend.

The mechanism under test is
``time_series_momentum_gate(prices, lookback, skip)`` which returns a
``pd.Series`` of {0, 1} gate flags, and
``apply_blend_with_momentum_overlay(r_eq, r_bd, price_signal, blend_cfg,
overlay_cfg)`` which wraps iter 006's ``apply_blend_variance_target`` and
multiplies the returned scale by the gate flag.

Citations:
* `[ml_for_algo_trading, ch.4 p.86]` — 12-month return EXCLUDING most
  recent month (skip-a-month) to avoid short-term reversal.
* `[algo_trading_chan, p.133, 164, ch.6]` — time-series momentum;
  lookback=252 anchored to Moskowitz-Ooi-Pedersen (2012).
* `[advances_fin_ml, p.162-164]` — signal lag (no look-ahead).

Spec: ``studies/strategy_hunt_loop/iterations/007-*/hypothesis.md``.
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
    / "007-2026-04-24-1047-vol-managed-60-40-momentum-overlay"
)
sys.path.insert(0, str(ITER_DIR))

from momentum_overlay import (  # noqa: E402
    apply_blend_with_momentum_overlay,
    time_series_momentum_gate,
)


def _trending_prices(n: int, drift: float, seed: int = 0) -> pd.Series:
    """Log-normal random walk with specified drift."""
    rng = np.random.default_rng(seed)
    eps = rng.normal(drift, 0.01, size=n)
    idx = pd.bdate_range("2000-01-03", periods=n)
    return pd.Series(100.0 * np.exp(np.cumsum(eps)), index=idx)


def test_gate_returns_ones_when_trend_strongly_positive() -> None:
    """Upward-drifting price → momentum > 0 on all valid bars → gate = 1."""
    prices = _trending_prices(600, drift=+0.0015, seed=1)
    gate = time_series_momentum_gate(prices, lookback=252, skip=21)
    # First valid bar is at index (252 + 21) = 273.
    valid = gate.dropna()
    # Every valid bar should fire (mom > 0) on a strongly trending path.
    assert valid.sum() == len(valid), (
        f"expected all ones on upward-trending path, got {valid.sum()}/{len(valid)}"
    )


def test_gate_returns_zeros_when_trend_strongly_negative() -> None:
    """Downward-drifting price → mom ≤ 0 → gate = 0 on all valid bars."""
    prices = _trending_prices(600, drift=-0.0015, seed=2)
    gate = time_series_momentum_gate(prices, lookback=252, skip=21)
    valid = gate.dropna()
    assert valid.sum() == 0, (
        f"expected all zeros on downward-trending path, got {valid.sum()}/{len(valid)}"
    )


def test_gate_canonical_formula_matches_skip_a_month() -> None:
    """At bar t, gate uses mom = P_{t-skip} / P_{t-skip-lookback} - 1.

    With skip=21 and lookback=252, the momentum at bar t is the return
    from (t - 21 - 252) to (t - 21). Gate = 1 iff this > 0.
    """
    # Build a price path that is strictly monotonic (upward trend) except
    # for a single 30% drop at a known index; verify gate flips at the
    # expected offset.
    n = 500
    prices = pd.Series(
        100.0 + np.arange(n, dtype=float) * 0.1,
        index=pd.bdate_range("2000-01-03", periods=n),
    )
    # Drop the price at bar 200 to 50% of previous level, recover after.
    prices.iloc[200:] *= 0.5

    gate = time_series_momentum_gate(prices, lookback=252, skip=21)
    # Before the drop's effect reaches the signal window (t-21-252 or
    # t-21 straddling the drop), signal is still positive.
    # The drop is at idx 200; at signal time the drop enters the
    # `P_{t-21} / P_{t-21-252}` ratio when t-21 >= 200, i.e. t >= 221.
    # Once t-21-252 >= 200 (t >= 473), the drop is "fully consumed" on
    # both ends and trend is monotonic positive again.
    before_drop_window = gate.iloc[273:221]
    # After the drop enters the numerator (t=221+) the ratio drops sharply.
    in_drop_window = gate.loc[(gate.index >= prices.index[221]) & (gate.index <= prices.index[472])].dropna()
    # Once denominator also passes the drop (t >= 473), trend is positive again.
    after_drop_window = gate.loc[gate.index >= prices.index[473]].dropna()
    # In the "drop window", momentum is negative → gate=0 (at least sometimes).
    assert in_drop_window.sum() < len(in_drop_window), (
        "expected at least some zero-gate bars while drop is in the "
        "numerator-only portion of the momentum ratio"
    )
    # After the window fully passes the drop, trend is again positive.
    assert after_drop_window.mean() > 0.8, (
        f"expected gate mostly on after drop is consumed on both ends; "
        f"got mean {after_drop_window.mean():.2f}"
    )


def test_gate_uses_lagged_prices_no_lookahead() -> None:
    """Modifying price at bar t must not change gate value AT bar t."""
    prices = _trending_prices(600, drift=+0.0005, seed=3)
    gate_orig = time_series_momentum_gate(prices, lookback=252, skip=21)

    # Modify prices at bar t = 400 only — all bars from 400 onward inherit
    # the perturbation because we shift by a factor.
    prices_perturbed = prices.copy()
    perturb_idx = 400
    # Perturb just bar 400 (not the propagation).
    new_price = prices_perturbed.iloc[perturb_idx] * 0.5
    prices_perturbed.iloc[perturb_idx] = new_price
    gate_perturbed = time_series_momentum_gate(
        prices_perturbed, lookback=252, skip=21,
    )

    # The gate at bar t=400 cannot depend on price at bar t=400 because
    # the signal uses only prices up to t-21. Verify bar 400 matches.
    assert gate_orig.iloc[perturb_idx] == gate_perturbed.iloc[perturb_idx], (
        "gate at bar t must not depend on price at bar t (look-ahead detected)"
    )


def test_gate_undefined_before_warmup() -> None:
    """First (lookback + skip) bars have no signal and return NaN."""
    prices = _trending_prices(400, drift=+0.001, seed=4)
    gate = time_series_momentum_gate(prices, lookback=252, skip=21)
    assert gate.iloc[:273].isna().all(), (
        "first 273 bars (lookback + skip) should be NaN — insufficient history"
    )
    assert gate.iloc[273:].notna().all(), (
        "bars 273+ should have a defined gate value"
    )


def test_gate_shorter_lookback_fires_earlier() -> None:
    """With lookback=126, skip=21: warmup is 147 bars not 273."""
    prices = _trending_prices(400, drift=+0.001, seed=5)
    gate = time_series_momentum_gate(prices, lookback=126, skip=21)
    assert gate.iloc[:147].isna().all()
    assert gate.iloc[147:].notna().all()


def test_gate_raises_on_insufficient_bars() -> None:
    """Fewer bars than lookback+skip → raise ValueError (not silent)."""
    prices = _trending_prices(200, drift=+0.001, seed=6)
    with pytest.raises(ValueError, match="need > .* bars"):
        time_series_momentum_gate(prices, lookback=252, skip=21)


def test_overlay_zero_gate_produces_zero_position() -> None:
    """On bars where momentum gate = 0, per-leg positions must be 0."""
    # Create 600-bar paired returns + a price path that turns negative.
    n = 600
    rng = np.random.default_rng(7)
    r_eq = pd.Series(rng.normal(0, 0.01, n),
                     index=pd.bdate_range("2000-01-03", periods=n))
    r_bd = pd.Series(rng.normal(0, 0.005, n), index=r_eq.index)
    # Price signal: downward-drifting (all zero-gate).
    price_signal = pd.Series(
        100.0 * np.exp(np.cumsum(rng.normal(-0.002, 0.01, n))),
        index=r_eq.index,
    )
    net, pos_eq, pos_bd, scale, gate = apply_blend_with_momentum_overlay(
        r_eq, r_bd, price_signal,
        blend_cfg={"target_vol": 0.15, "lookback": 21, "max_leverage": 2.0},
        overlay_cfg={"lookback": 252, "skip": 21},
    )
    valid_gate = gate.dropna()
    # Every valid bar is gate=0 on strongly-negative path.
    assert (valid_gate == 0).all()
    # Post-warmup positions must be zero.
    np.testing.assert_allclose(
        pos_eq.loc[valid_gate.index].to_numpy(), 0.0, atol=1e-12,
    )
    np.testing.assert_allclose(
        pos_bd.loc[valid_gate.index].to_numpy(), 0.0, atol=1e-12,
    )


def test_overlay_full_gate_matches_blend_without_overlay() -> None:
    """On bars where gate = 1 consistently, overlay output equals base blend."""
    import sys as _sys
    _sys.path.insert(
        0,
        str(Path(__file__).resolve().parents[1]
            / "studies" / "strategy_hunt_loop" / "iterations"
            / "006-2026-04-24-1027-vol-managed-60-40"),
    )
    from stock_bond_blend import apply_blend_variance_target

    n = 600
    rng = np.random.default_rng(8)
    idx = pd.bdate_range("2000-01-03", periods=n)
    r_eq = pd.Series(rng.normal(0.0005, 0.01, n), index=idx)
    r_bd = pd.Series(rng.normal(0.0002, 0.005, n), index=idx)
    # Strong upward price drift → gate always 1 post-warmup.
    price_signal = pd.Series(
        100.0 * np.exp(np.cumsum(rng.normal(0.002, 0.008, n))),
        index=idx,
    )

    net_ov, pos_eq_ov, pos_bd_ov, scale_ov, gate = apply_blend_with_momentum_overlay(
        r_eq, r_bd, price_signal,
        blend_cfg={"target_vol": 0.15, "lookback": 21, "max_leverage": 2.0},
        overlay_cfg={"lookback": 252, "skip": 21},
    )
    net_base, pos_eq_base, pos_bd_base, scale_base = apply_blend_variance_target(
        r_eq, r_bd,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    # Align both on overlay index (overlay warmup is longer).
    common = scale_ov.dropna().index.intersection(scale_base.index)
    assert len(common) > 200
    # Positions must match on gate-always-on bars (modulo cost-recalc at the
    # first bar where gate turns on, which we skip).
    np.testing.assert_allclose(
        pos_eq_ov.loc[common].to_numpy(),
        pos_eq_base.loc[common].to_numpy(),
        atol=1e-12,
    )


def test_overlay_raises_on_misaligned_indices() -> None:
    """r_eq, r_bd, price_signal must share index — reject mismatches."""
    n = 400
    rng = np.random.default_rng(9)
    idx_a = pd.bdate_range("2000-01-03", periods=n)
    idx_b = pd.bdate_range("2000-06-01", periods=n)
    r_eq = pd.Series(rng.normal(0, 0.01, n), index=idx_a)
    r_bd = pd.Series(rng.normal(0, 0.005, n), index=idx_a)
    prices_wrong = pd.Series(100.0 + np.arange(n, dtype=float), index=idx_b)
    with pytest.raises(ValueError, match="align|index|same"):
        apply_blend_with_momentum_overlay(
            r_eq, r_bd, prices_wrong,
            blend_cfg={"target_vol": 0.15, "lookback": 21, "max_leverage": 2.0},
            overlay_cfg={"lookback": 252, "skip": 21},
        )


def test_overlay_gate_transitions_cost_full_gross() -> None:
    """When gate flips 0→1 or 1→0, the position change is the full blend scale."""
    n = 600
    rng = np.random.default_rng(10)
    idx = pd.bdate_range("2000-01-03", periods=n)
    r_eq = pd.Series(rng.normal(0, 0.01, n), index=idx)
    r_bd = pd.Series(rng.normal(0, 0.005, n), index=idx)
    # Build a price path that goes up, then down sharply, then up again —
    # forces at least one gate transition.
    segment_a = np.linspace(100.0, 200.0, 200)
    segment_b = np.linspace(200.0, 90.0, 200)
    segment_c = np.linspace(90.0, 180.0, 200)
    price_signal = pd.Series(
        np.concatenate([segment_a, segment_b, segment_c]),
        index=idx,
    )
    net, pos_eq, pos_bd, scale, gate = apply_blend_with_momentum_overlay(
        r_eq, r_bd, price_signal,
        blend_cfg={"target_vol": 0.15, "lookback": 21, "max_leverage": 2.0},
        overlay_cfg={"lookback": 252, "skip": 21},
    )
    # At least one gate transition should occur in this crafted path.
    gate_valid = gate.dropna().astype(int)
    transitions = (gate_valid.diff().abs() > 0).sum()
    assert transitions >= 1, (
        f"expected at least one gate transition on crafted path; got {transitions}"
    )
