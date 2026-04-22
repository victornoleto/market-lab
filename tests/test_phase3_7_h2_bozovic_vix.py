"""Smoke tests for Phase 3.7 H2.a — Božović VIX-scaled SPY/cash rebalance.

Tests three invariants:

1. Signal spec: ``exposure = clip(20/VIX_ma, 0, 1)`` — when VIX_ma = 20,
   exposure = 1.0; when VIX_ma = 40, exposure = 0.5; when VIX_ma = 80,
   exposure = 0.25; when VIX_ma = 10, exposure clipped to 1.0.
2. Lookahead audit: VIX_ma_{t-1} never uses day t's own VIX value — when
   VIX jumps on day D, exposure on day D is unchanged (uses prior days).
3. End-to-end simulator runs, weights sum to 1.0, tax events are recorded
   at year-end, daily returns are finite.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.phase3_7_h2_bozovic_vix_scaling import (
    H2BozovicVixScalingConfig,
    compute_vix_exposure,
    simulate_h2_bozovic_vix_scaling,
)


def _make_synthetic(n_days: int = 300, seed: int = 42) -> dict:
    """Generate SPY / SHV / VIX series aligned on a business-day calendar."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-02", periods=n_days)
    spy = pd.Series(rng.normal(0.0003, 0.01, n_days), index=idx, name="SPY")
    shv = pd.Series(rng.normal(0.00015, 0.0005, n_days), index=idx, name="SHV")
    # VIX: mean-reverting around 20 with shocks.
    vix_vals = 20.0 + 5.0 * rng.standard_normal(n_days).cumsum() / np.sqrt(n_days)
    vix_vals = np.clip(vix_vals, 10, 60)
    vix = pd.Series(vix_vals, index=idx, name="VIX")
    return {"spy": spy, "shv": shv, "vix": vix}


def test_signal_spec_exposure_clipped_and_scaled() -> None:
    """Exact VIX scaling: VIX=20 → 1.0; VIX=40 → 0.5; VIX=10 → clipped to 1.0."""
    idx = pd.bdate_range("2020-01-02", periods=60)
    # Constant VIX series at different values; verify the rolling MA becomes
    # that value and exposure = 20/value clipped.
    cfg = H2BozovicVixScalingConfig(vix_baseline=20.0, vix_ma_days=21)

    # Case 1: constant VIX = 20 → exposure = 1.0 (post-warmup).
    vix20 = pd.Series(20.0, index=idx)
    exp20 = compute_vix_exposure(vix20, cfg)
    # First 21 bars NaN (rolling + shift), rest finite.
    assert exp20.iloc[:21].isna().all()
    assert (exp20.iloc[22:] == 1.0).all()

    # Case 2: constant VIX = 40 → exposure = 0.5.
    vix40 = pd.Series(40.0, index=idx)
    exp40 = compute_vix_exposure(vix40, cfg)
    assert np.isclose(exp40.iloc[22:], 0.5).all()

    # Case 3: constant VIX = 10 → raw 20/10=2.0, clipped to cap=1.0.
    vix10 = pd.Series(10.0, index=idx)
    exp10 = compute_vix_exposure(vix10, cfg)
    assert (exp10.iloc[22:] == 1.0).all()

    # Case 4: constant VIX = 80 → exposure = 0.25.
    vix80 = pd.Series(80.0, index=idx)
    exp80 = compute_vix_exposure(vix80, cfg)
    assert np.isclose(exp80.iloc[22:], 0.25).all()


def test_signal_no_lookahead() -> None:
    """On day D, VIX jumps 10 → 60. Exposure on day D must use prior MA only;
    next-day exposure absorbs the jump."""
    idx = pd.bdate_range("2020-01-02", periods=60)
    vix = pd.Series(10.0, index=idx)
    # Shock at bar 30: VIX becomes 60 on that bar ONLY.
    vix.iloc[30] = 60.0
    cfg = H2BozovicVixScalingConfig(vix_baseline=20.0, vix_ma_days=21)
    exp = compute_vix_exposure(vix, cfg)

    # Day 30 exposure uses rolling mean of days [9..29] (all VIX=10) → MA=10 →
    # raw=2.0 → clip to 1.0. Day 30 exposure is unchanged by the day-30 jump.
    assert exp.iloc[30] == 1.0
    # Day 31 exposure uses rolling mean of days [10..30] which includes the
    # shock: MA = (20·10 + 60) / 21 = 260/21 ≈ 12.38; exposure = 20/12.38 ≈
    # 1.615 clipped to 1.0. So still 1.0.
    assert exp.iloc[31] == 1.0

    # Construct a stronger shock so the post-shock MA > 20 (exposure < 1).
    # Use 80 days so we have plenty of post-warmup runway.
    idx80 = pd.bdate_range("2020-01-02", periods=80)
    vix2 = pd.Series(10.0, index=idx80)
    # 30 consecutive shocks at VIX=60 starting at bar 30 (indices 30..59).
    vix2.iloc[30:60] = 60.0
    exp2 = compute_vix_exposure(vix2, cfg)
    # Day 30 (first shock bar) exposure uses rolling mean of days [9..29] (all
    # pre-shock VIX=10) → raw = 20/10 = 2.0, clipped to 1.0. The day-30 shock
    # is NOT seen on day 30 — this is the shift(1) lookahead audit.
    assert exp2.iloc[30] == 1.0
    # Day 52 uses rolling(21).shift(1) → window of bar 52 is [31..51] (21 vals)
    # all shock → MA = 60 → exposure = 20/60 ≈ 0.333.
    assert np.isclose(exp2.iloc[52], 20.0 / 60.0, atol=1e-6)


def test_simulator_end_to_end_runs() -> None:
    """End-to-end: weights sum to 1, daily returns finite, tax event recorded
    at year-end when year ends profitably."""
    d = _make_synthetic(n_days=260, seed=7)
    cfg = H2BozovicVixScalingConfig()
    res = simulate_h2_bozovic_vix_scaling(
        d["spy"], d["shv"], d["vix"], cfg
    )
    # Weights rowsum == 1.
    assert np.allclose(res.weights.sum(axis=1), 1.0, atol=1e-9)
    # Daily returns finite.
    assert res.daily_returns.notna().all()
    assert res.daily_returns.abs().max() < 1.0
    # Equity positive.
    assert (res.equity > 0).all()
    # At least one year-end tax event attempted (we span one full calendar year).
    # (May be zero if YTD ended negative — document.)
    # Check invariant: cum_tax_pct is sum of tax_events.
    if res.tax_events:
        assert np.isclose(
            res.cum_tax_pct, sum(t for _, t in res.tax_events), atol=1e-9
        )


def test_simulator_no_tax_when_rate_zero() -> None:
    """With tax_rate=0, cum_tax_pct must be exactly 0."""
    d = _make_synthetic(n_days=260, seed=8)
    cfg = H2BozovicVixScalingConfig(tax_rate=0.0)
    res = simulate_h2_bozovic_vix_scaling(
        d["spy"], d["shv"], d["vix"], cfg
    )
    assert res.cum_tax_pct == 0.0
    assert res.tax_events == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
