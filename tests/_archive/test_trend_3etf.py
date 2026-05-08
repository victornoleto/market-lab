"""Tests for iter 023 time-series trend-following on 3-asset basket.

Primitive: ``studies/strategy_hunt_loop/iterations/023-.../trend_3etf.py``

Coverage (TDD — 9 specs covering the mechanism changes vs iter 016/022):
1. Trend signal = sign of 12-1 cumulative return (lookback=252, skip=21)
2. Per-asset vol-target scaling (each leg independently, not σ²_port)
3. Short positions allowed when signal is negative
4. Total-leverage cap enforced via proportional shrink across legs
5. Zero signal → zero position on that leg
6. Net returns aggregate linearly across legs (Σ pos_i · r_i − cost)
7. G7 cross-lib parity with numpy hand-roll (CAGR ±3 pp)
8. Bars before (lookback + skip) produce NaN signal (dropped from output)
9. Transaction cost is linear in per-leg ∆position (2 bps/leg)

Structural difference vs iter 016 tested implicitly:
- Identity: no test that reproduces iter 016 (mechanism differs — short
  handling, per-asset vol, no portfolio σ²). The fact that reducing this
  primitive to a 1-asset always-long constant-signal case does NOT match
  iter 004's Carver σ⁻¹ form verifies the geometric difference.

Citations
---------
* `[algo_trading_chan, p.164, ch.6]` — Moskowitz-Yao-Pedersen 2012 / 12-1 lookback.
* `[systematic_trading, p.40, ch.2]` — per-asset vol standardisation primitive.
* `[systematic_trading, p.159-160, ch.10]` — volatility scalar per instrument.
* `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 leverage cap.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = (
    ROOT
    / "studies"
    / "strategy_hunt_loop"
    / "iterations"
    / "023-2026-04-24-2007-time-series-trend-3etf"
)
sys.path.insert(0, str(ITER_DIR))

from trend_3etf import (  # noqa: E402
    apply_trend_3etf,
    compute_trend_signal,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_3etf():
    """Deterministic 3-asset daily returns, 5+ years for trend signal coverage."""
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2015-01-02", "2021-12-31")
    n = len(idx)
    # SPY-like: positive drift, ~15% annual vol
    r0 = pd.Series(rng.normal(0.0004, 0.010, size=n), index=idx, name="A")
    # TLT-like: tiny drift, ~13% annual vol, slight negative corr to r0
    r1 = pd.Series(
        -0.25 * r0.to_numpy() + rng.normal(0.00015, 0.0085, size=n),
        index=idx,
        name="B",
    )
    # GLD-like: small drift, ~17% annual vol, low correlation
    r2 = pd.Series(rng.normal(0.00018, 0.011, size=n), index=idx, name="C")
    return pd.concat([r0, r1, r2], axis=1)


@pytest.fixture
def always_uptrend_3etf():
    """3 assets with strict uptrend + tiny noise for σ̂ > 0."""
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2015-01-02", "2021-12-31")
    n = len(idx)
    daily_drift = 0.0006  # ~15%/yr positive drift
    noise = rng.normal(0.0, 1e-5, size=(n, 3))  # micro-jitter to keep σ̂ > 0
    r = pd.DataFrame(
        {
            "A": np.full(n, daily_drift) + noise[:, 0],
            "B": np.full(n, daily_drift * 0.6) + noise[:, 1],
            "C": np.full(n, daily_drift * 0.4) + noise[:, 2],
        },
        index=idx,
    )
    return r


# ---------------------------------------------------------------------------
# 1. Signal semantics
# ---------------------------------------------------------------------------


def test_signal_sign_tracks_12_1_cumulative_return(always_uptrend_3etf):
    """Strict uptrend → signal = +1 on all assets after (lookback + skip) warmup."""
    sig = compute_trend_signal(always_uptrend_3etf, lookback=252, skip=21)
    # Rolling(252) first valid at index 251; .shift(21) pushes first valid to 272.
    # So indices [0, 272) are NaN; index 272+ carry the signal.
    warmup = 252 + 21 - 1  # = 272 (first-valid index)
    assert sig.iloc[:warmup].isna().all().all(), (
        "signal must be NaN for bars before lookback+skip warmup"
    )
    # All subsequent bars: signal must be +1 on every asset (cumret > 0).
    active = sig.iloc[warmup:]
    assert (active == 1.0).all().all(), "strict uptrend must produce +1 on all bars"


def test_signal_flips_on_negative_trend():
    """Strict downtrend → signal = -1 after warmup."""
    rng = np.random.default_rng(5)
    idx = pd.bdate_range("2015-01-02", "2021-12-31")
    n = len(idx)
    noise = rng.normal(0.0, 1e-5, size=(n, 3))
    r = pd.DataFrame(
        {
            "A": np.full(n, -0.0006) + noise[:, 0],
            "B": np.full(n, -0.0004) + noise[:, 1],
            "C": np.full(n, -0.0002) + noise[:, 2],
        },
        index=idx,
    )
    sig = compute_trend_signal(r, lookback=252, skip=21)
    warmup = 252 + 21
    active = sig.iloc[warmup:]
    assert (active == -1.0).all().all(), "strict downtrend must produce -1 on all bars"


def test_signal_has_no_lookahead():
    """Modifying r[t] must NOT change signal at or before bar t+skip."""
    rng = np.random.default_rng(11)
    idx = pd.bdate_range("2015-01-02", "2021-12-31")
    n = len(idx)
    r = pd.DataFrame(
        {
            "A": rng.normal(0.0004, 0.010, size=n),
            "B": rng.normal(0.0002, 0.008, size=n),
            "C": rng.normal(0.00018, 0.011, size=n),
        },
        index=idx,
    )
    sig_orig = compute_trend_signal(r, lookback=252, skip=21)

    # Flip the sign of r at bar 500 with a huge perturbation.
    r_mut = r.copy()
    r_mut.iloc[500] = [1.0, 1.0, 1.0]  # +100 % day
    sig_mut = compute_trend_signal(r_mut, lookback=252, skip=21)

    # Signal at bar 500 + skip and earlier must be identical (skip=21).
    common = sig_orig.index[: 500 + 21]
    pd.testing.assert_frame_equal(
        sig_orig.loc[common].dropna(how="all"),
        sig_mut.loc[common].dropna(how="all"),
        check_dtype=False,
    )


# ---------------------------------------------------------------------------
# 2. Per-asset vol target
# ---------------------------------------------------------------------------


def test_per_asset_vol_target_scales_inverse_vol(synthetic_3etf):
    """|pos_i[t]| × σ_i[t-1] ≈ target_vol_per_asset (before leverage cap)."""
    net, positions, scale, sig = apply_trend_3etf(
        synthetic_3etf,
        signal_lookback=252,
        signal_skip=21,
        vol_lookback=21,
        target_vol_per_asset=0.10,
        max_leverage=100.0,  # disable cap to test raw per-leg sizing
        cost_bps_per_leg=0.0,
    )
    # After cap is effectively disabled, |pos_i[t]| = target_vol / σ_i[t-1].
    # Compute rolling σ_i with the same discipline as the primitive.
    r = synthetic_3etf.loc[positions.index]
    ann_sigma = r.rolling(21).std(ddof=0).shift(1) * np.sqrt(252)
    ann_sigma = ann_sigma.loc[positions.index]

    for col in positions.columns:
        implied = positions[col].abs() * ann_sigma[col]
        ok = implied.dropna()
        # With signal in {-1, 0, +1} and no cap, |pos| * σ should be
        # either 0 (no signal yet) or 0.10 (target_vol).
        nonzero = ok[ok > 1e-6]
        if len(nonzero) > 0:
            np.testing.assert_allclose(
                nonzero.to_numpy(), 0.10, atol=1e-10,
                err_msg=f"per-asset vol-target broken on leg {col}",
            )


# ---------------------------------------------------------------------------
# 3. Short positions allowed
# ---------------------------------------------------------------------------


def test_short_position_when_signal_negative():
    """pos[t] must be negative when signal[t] = -1."""
    rng = np.random.default_rng(17)
    idx = pd.bdate_range("2015-01-02", "2021-12-31")
    n = len(idx)
    noise = rng.normal(0.0, 1e-5, size=(n, 3))
    # Asset A: strict downtrend; asset B, C: strict uptrend. Tiny noise → σ̂ > 0.
    r = pd.DataFrame(
        {
            "A": np.full(n, -0.0006) + noise[:, 0],
            "B": np.full(n, 0.0005) + noise[:, 1],
            "C": np.full(n, 0.0004) + noise[:, 2],
        },
        index=idx,
    )
    net, positions, scale, sig = apply_trend_3etf(
        r,
        signal_lookback=252,
        signal_skip=21,
        vol_lookback=21,
        target_vol_per_asset=0.10,
        max_leverage=100.0,
        cost_bps_per_leg=0.0,
    )
    # After warmup, asset A must be SHORT (pos < 0), B and C LONG (pos > 0).
    after_warmup = positions.iloc[252 + 21 + 5 :]
    assert (after_warmup["A"] < 0).all(), "downtrend asset A must produce short position"
    assert (after_warmup["B"] > 0).all(), "uptrend asset B must produce long position"
    assert (after_warmup["C"] > 0).all(), "uptrend asset C must produce long position"


# ---------------------------------------------------------------------------
# 4. Leverage cap
# ---------------------------------------------------------------------------


def test_total_leverage_cap_enforced_by_proportional_shrink(synthetic_3etf):
    """Σ |pos_i[t]| ≤ max_leverage on every bar."""
    net, positions, scale, sig = apply_trend_3etf(
        synthetic_3etf,
        signal_lookback=252,
        signal_skip=21,
        vol_lookback=21,
        target_vol_per_asset=0.10,
        max_leverage=0.15,  # tight cap to force shrink
        cost_bps_per_leg=0.0,
    )
    # Sum of absolute positions ≤ cap + tiny float noise.
    gross = positions.abs().sum(axis=1)
    assert (gross.dropna() <= 0.15 + 1e-10).all(), (
        f"leverage cap violated; max gross = {gross.max()}"
    )


def test_proportional_shrink_preserves_ratios(synthetic_3etf):
    """When cap binds, per-leg sign is preserved and |pos_i|/gross ratios unchanged."""
    # Two runs: one with loose cap (cap=100), one tight cap (cap=0.05).
    _, pos_loose, _, _ = apply_trend_3etf(
        synthetic_3etf,
        signal_lookback=252, signal_skip=21,
        vol_lookback=21, target_vol_per_asset=0.10,
        max_leverage=100.0, cost_bps_per_leg=0.0,
    )
    _, pos_tight, _, _ = apply_trend_3etf(
        synthetic_3etf,
        signal_lookback=252, signal_skip=21,
        vol_lookback=21, target_vol_per_asset=0.10,
        max_leverage=0.05, cost_bps_per_leg=0.0,
    )
    common = pos_loose.index.intersection(pos_tight.index)
    loose = pos_loose.loc[common]
    tight = pos_tight.loc[common]
    # On bars where loose raw gross > 0.05, tight should be loose × (0.05 / loose_gross).
    loose_gross = loose.abs().sum(axis=1)
    bind = (loose_gross > 0.05 + 1e-12)
    if bind.any():
        ratio_expected = 0.05 / loose_gross[bind]
        # Per-leg: tight / loose = ratio_expected (preserves signs).
        tight_bind = tight[bind]
        loose_bind = loose[bind]
        for col in loose.columns:
            nonzero = loose_bind[col].abs() > 1e-12
            if nonzero.any():
                ratios = tight_bind.loc[nonzero, col] / loose_bind.loc[nonzero, col]
                np.testing.assert_allclose(
                    ratios.to_numpy(),
                    ratio_expected.loc[nonzero].to_numpy(),
                    atol=1e-10,
                )


# ---------------------------------------------------------------------------
# 5. Zero signal → zero position
# ---------------------------------------------------------------------------


def test_zero_signal_forces_zero_leg_position(synthetic_3etf):
    """Wherever signals[t][i] == 0 exactly, positions[t][i] must be 0 exactly.

    Float-precision-resilient test: assert the invariant on whatever bars
    the random fixture happens to produce (vacuously true if none, which
    is acceptable — the algebraic invariant ``pos = signal × scale``
    guarantees it by construction).
    """
    _, positions, _, signals = apply_trend_3etf(
        synthetic_3etf,
        signal_lookback=252, signal_skip=21,
        vol_lookback=21, target_vol_per_asset=0.10,
        max_leverage=2.0, cost_bps_per_leg=0.0,
    )
    for col in positions.columns:
        zero_mask = signals[col] == 0.0
        if zero_mask.any():
            assert positions.loc[zero_mask, col].abs().max() < 1e-12, (
                f"zero-signal bars on {col} produced non-zero position"
            )


# ---------------------------------------------------------------------------
# 6. Net returns aggregation
# ---------------------------------------------------------------------------


def test_net_returns_aggregate_across_legs(synthetic_3etf):
    """net[t] = Σ pos_i[t] · r_i[t] (when cost=0)."""
    net, positions, scale, sig = apply_trend_3etf(
        synthetic_3etf,
        signal_lookback=252, signal_skip=21,
        vol_lookback=21, target_vol_per_asset=0.10,
        max_leverage=2.0, cost_bps_per_leg=0.0,
    )
    r_v = synthetic_3etf.loc[positions.index]
    gross = (positions * r_v).sum(axis=1)
    np.testing.assert_allclose(net.to_numpy(), gross.to_numpy(), atol=1e-12)


def test_cost_linear_in_position_change(synthetic_3etf):
    """|net_no_cost - net_with_cost| equals Σ_i |Δpos_i| × cost_bps."""
    _, pos_a, _, _ = apply_trend_3etf(
        synthetic_3etf,
        signal_lookback=252, signal_skip=21,
        vol_lookback=21, target_vol_per_asset=0.10,
        max_leverage=2.0, cost_bps_per_leg=0.0,
    )
    net_b, pos_b, _, _ = apply_trend_3etf(
        synthetic_3etf,
        signal_lookback=252, signal_skip=21,
        vol_lookback=21, target_vol_per_asset=0.10,
        max_leverage=2.0, cost_bps_per_leg=0.0002,
    )
    # Positions should be identical when cost doesn't alter signal.
    pd.testing.assert_frame_equal(pos_a, pos_b)
    # Compute expected cost stream.
    dpos = pos_b.diff().abs().fillna(pos_b.iloc[0].abs())
    expected_cost = dpos.sum(axis=1) * 0.0002
    r_v = synthetic_3etf.loc[pos_b.index]
    expected_net = (pos_b * r_v).sum(axis=1) - expected_cost
    np.testing.assert_allclose(net_b.to_numpy(), expected_net.to_numpy(), atol=1e-12)


# ---------------------------------------------------------------------------
# 7. G7 cross-lib parity
# ---------------------------------------------------------------------------


def test_numpy_reference_parity(synthetic_3etf):
    """Hand-rolled numpy version must agree with pandas version within 3 pp CAGR."""
    from numpy_reference_3etf import trend_3etf_numpy
    from market_lab.backtest.metrics.performance import cagr as _cagr

    net_pd, _, _, _ = apply_trend_3etf(
        synthetic_3etf,
        signal_lookback=252, signal_skip=21,
        vol_lookback=21, target_vol_per_asset=0.10,
        max_leverage=2.0, cost_bps_per_leg=0.0002,
    )
    net_np = trend_3etf_numpy(
        synthetic_3etf.to_numpy(),
        index=synthetic_3etf.index,
        signal_lookback=252, signal_skip=21,
        vol_lookback=21, target_vol_per_asset=0.10,
        max_leverage=2.0, cost_bps_per_leg=0.0002,
    )
    eq_pd = (1.0 + net_pd).cumprod()
    eq_np = (1.0 + pd.Series(net_np, index=net_pd.index)).cumprod()
    cagr_pd = _cagr(eq_pd)
    cagr_np = _cagr(eq_np)
    assert abs(cagr_pd - cagr_np) < 0.03, (
        f"G7 cross-lib parity violated: |pd - np| = {abs(cagr_pd - cagr_np):.5f}"
    )


# ---------------------------------------------------------------------------
# 8. Validation / error paths
# ---------------------------------------------------------------------------


def test_misaligned_columns_raise():
    """apply_trend_3etf requires DataFrame with 3 columns."""
    idx = pd.bdate_range("2015-01-02", "2020-12-31")
    r = pd.DataFrame({"A": np.zeros(len(idx)), "B": np.zeros(len(idx))}, index=idx)
    with pytest.raises(ValueError, match="3 asset columns"):
        apply_trend_3etf(
            r,
            signal_lookback=252, signal_skip=21,
            vol_lookback=21, target_vol_per_asset=0.10,
            max_leverage=2.0, cost_bps_per_leg=0.0002,
        )


def test_short_series_raises():
    """Must have > lookback + skip bars."""
    idx = pd.bdate_range("2015-01-02", "2015-12-31")  # ~260 bars
    r = pd.DataFrame(
        {"A": np.zeros(len(idx)), "B": np.zeros(len(idx)), "C": np.zeros(len(idx))},
        index=idx,
    )
    with pytest.raises(ValueError, match="overlapping"):
        apply_trend_3etf(
            r,
            signal_lookback=252, signal_skip=21,
            vol_lookback=21, target_vol_per_asset=0.10,
            max_leverage=2.0, cost_bps_per_leg=0.0002,
        )
