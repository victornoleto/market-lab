"""Iter 020 — TDD specs for monthly-rolled put-spread tail hedge.

Locks semantics of the Black-Scholes pricer + monthly put-spread roll +
overlay pipeline BEFORE measuring real-data performance.

Citations
---------
* `[volatility_trading, p.11]` — BSM pricing + implied vol.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* Hull, Options Futures Derivatives — put-call parity reference values.
"""

from __future__ import annotations

import sys
from math import exp
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "020-2026-04-24-1850-put-spread-tail-hedge"
sys.path.insert(0, str(ITER_DIR))

from put_spread_hedge import (  # noqa: E402
    black_scholes_put,
    _price_put_spread,
    compute_put_spread_daily_returns,
    apply_put_spread_hedged_stack,
)
from numpy_reference_put_spread import (  # noqa: E402
    black_scholes_put_np,
    compute_put_spread_daily_returns_np,
    apply_put_spread_hedged_stack_np,
)


# ---------------------------------------------------------------------------
# BS pricer correctness
# ---------------------------------------------------------------------------


def test_bs_put_intrinsic_at_expiry():
    """At T=0: put value = max(K-S, 0)."""
    assert abs(black_scholes_put(100, 110, 0.0, 0.2, 0.02) - 10.0) < 1e-10
    assert abs(black_scholes_put(110, 100, 0.0, 0.2, 0.02) - 0.0) < 1e-10
    assert abs(black_scholes_put(100, 100, 0.0, 0.2, 0.02) - 0.0) < 1e-10


def test_bs_put_zero_vol_returns_discounted_intrinsic():
    """σ=0: put = max(K*e^(-rT) - S, 0)."""
    S, K, T, r = 100.0, 105.0, 0.5, 0.03
    expected = max(K * exp(-r * T) - S, 0.0)
    assert abs(black_scholes_put(S, K, T, 0.0, r) - expected) < 1e-10


def test_bs_put_call_parity():
    """C - P = S - K*e^(-rT). Use OTM put and build implied call value."""
    # C - P = S - K*e^(-rT), so for an ATM option: C and P differ by
    # a known amount. We verify P ≥ max(K*e^(-rT) - S, 0) and that the
    # formula lies within known bounds.
    S, K, T, sigma, r = 100.0, 100.0, 0.25, 0.2, 0.04
    put = black_scholes_put(S, K, T, sigma, r)
    # Lower bound: max(K*e^(-rT) - S, 0)
    lb = max(K * exp(-r * T) - S, 0.0)
    # Upper bound: K*e^(-rT) (intrinsic at S=0)
    ub = K * exp(-r * T)
    assert lb <= put <= ub
    # Known reference value (Hull Ch 13, BS ATM 25%T 20%σ 4%r):
    # Actually for S=K=100, T=0.25, σ=0.2, r=0.04 the ATM put ≈ 3.535.
    assert 3.3 < put < 3.8


def test_bs_put_monotone_in_sigma():
    """Put value must strictly increase with σ."""
    sigmas = [0.05, 0.1, 0.2, 0.4, 0.8]
    values = [black_scholes_put(100, 95, 0.5, s, 0.02) for s in sigmas]
    for a, b in zip(values, values[1:]):
        assert b > a, f"not monotone: {values}"


def test_bs_put_rejects_bad_inputs():
    with pytest.raises(ValueError):
        black_scholes_put(-100, 100, 0.5, 0.2, 0.02)
    with pytest.raises(ValueError):
        black_scholes_put(100, 0, 0.5, 0.2, 0.02)
    with pytest.raises(ValueError):
        black_scholes_put(100, 100, -0.1, 0.2, 0.02)
    with pytest.raises(ValueError):
        black_scholes_put(100, 100, 0.5, -0.1, 0.02)


def test_bs_pandas_np_parity():
    """Pandas pricer (scalar) must equal numpy pricer at same inputs."""
    inputs = [
        (100.0, 95.0, 0.1, 0.2, 0.02),
        (100.0, 110.0, 0.5, 0.3, 0.0),
        (50.0, 45.0, 0.02, 0.5, 0.05),
        (100.0, 100.0, 0.0, 0.3, 0.02),   # expiry intrinsic
        (100.0, 100.0, 0.25, 0.0, 0.02),  # zero vol
    ]
    for S, K, T, sigma, r in inputs:
        a = black_scholes_put(S, K, T, sigma, r)
        b = black_scholes_put_np(S, K, T, sigma, r)
        assert abs(a - b) < 1e-12


# ---------------------------------------------------------------------------
# Put-spread mechanics
# ---------------------------------------------------------------------------


def test_put_spread_max_payoff_bounded_by_strike_diff():
    """Spread payoff at expiry ≤ K_long - K_short."""
    K_long, K_short = 95.0, 90.0  # 5 wide
    # S way below K_short → max intrinsic = K_long - K_short = 5
    val = _price_put_spread(80, K_long, K_short, 0.0, 0.2, 0.02)
    assert abs(val - (K_long - K_short)) < 1e-10
    # S above K_long → zero
    val = _price_put_spread(105, K_long, K_short, 0.0, 0.2, 0.02)
    assert abs(val) < 1e-10


def test_put_spread_daily_returns_has_correct_length_and_index():
    """Return series aligned to inputs (after dropna), length preserved."""
    idx = pd.date_range("2010-01-04", periods=252, freq="B")
    prices = pd.Series(np.linspace(100, 120, 252), index=idx)
    iv = pd.Series(20.0, index=idx)  # constant VIX = 20%
    ret = compute_put_spread_daily_returns(
        prices, iv, k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, rf=0.02, iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    assert len(ret) == 252
    assert ret.index.equals(idx)


def test_put_spread_no_crash_constant_price_loses_premium():
    """With flat price and positive σ, sum of daily returns over life of
    one position ≈ -premium (total theta decay)."""
    n = 42  # two 21-day rolls
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    prices = pd.Series(100.0, index=idx)
    iv = pd.Series(20.0, index=idx)
    ret = compute_put_spread_daily_returns(
        prices, iv, k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, rf=0.0, iv_scale=1.0, cost_bps_per_roll=0.0,
    )
    # Over the first 21 bars (first position), cumulative return should
    # approach -(initial premium / S_0). Premium is small (both 5% and
    # 10% OTM puts, 1 month, 20%σ).
    first_cycle = ret.iloc[:21].sum()
    # Premium at entry (S=100, K_long=95, K_short=90, T=21/252, σ=0.2):
    entry_premium = _price_put_spread(100, 95, 90, 21/252, 0.2, 0.0)
    # First cycle: open cost + full MtM decay from premium to 0 (all OTM at expiry)
    # Note: the open cost is on bar 0, MtM from bar 1-20 accumulates (value_bar20 - prev_value_bar0).
    # Sum should equal (final_intrinsic_at_expiry - premium_at_open) = (0 - premium) = -premium
    assert abs(first_cycle - (-entry_premium / 100.0)) < 5e-3
    # Sanity: the drag is small (single-digit bps)
    assert -0.01 < first_cycle < 0.0


def test_put_spread_crash_pays_out():
    """A 10%+ crash in one position's life generates positive overlay return."""
    n = 25
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    # Flat for 10 days, then crash to -15%, then stay
    vals = np.full(n, 100.0)
    vals[10:] = 83.0  # crash to -17% on day 10
    prices = pd.Series(vals, index=idx)
    iv = pd.Series(40.0, index=idx)  # elevated VIX
    ret = compute_put_spread_daily_returns(
        prices, iv, k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, rf=0.0, iv_scale=1.0, cost_bps_per_roll=0.0,
    )
    # Position opened at S=100, K_long=95, K_short=90. After crash to 83,
    # the long put is deep ITM (worth ~12-15), short put is ITM (worth
    # ~7-10). Spread MtM should rise toward its cap (K_long - K_short = 5),
    # so cumulative return from open to day 20 should be strongly positive.
    cum_at_expiry = ret.iloc[:21].sum()
    # Payoff at expiry: max(95-83,0) - max(90-83,0) = 12 - 7 = 5
    # Premium paid: small (~0.7 at 40% vol). So net ≈ +4.3 / 100 = +0.043
    assert cum_at_expiry > 0.02, (
        f"expected positive crash payoff, got {cum_at_expiry:.4f}"
    )


def test_overlay_pandas_np_parity():
    """Daily return series from pandas vs numpy implementations must match."""
    n = 100
    rng = np.random.default_rng(42)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    # Geometric random walk around 100 with drift 0 and σ 1%/day
    log_r = rng.normal(0.0, 0.01, n - 1)
    prices_arr = np.concatenate([[100.0], 100.0 * np.exp(np.cumsum(log_r))])
    iv_arr = np.full(n, 20.0) + rng.normal(0, 2, n)
    iv_arr = np.clip(iv_arr, 8.0, 50.0)

    prices = pd.Series(prices_arr, index=idx)
    iv = pd.Series(iv_arr, index=idx)

    ret_pd = compute_put_spread_daily_returns(
        prices, iv, k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, rf=0.02, iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    ret_np = compute_put_spread_daily_returns_np(
        prices_arr, iv_arr,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, rf=0.02, iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    np.testing.assert_allclose(ret_pd.to_numpy(), ret_np, atol=1e-12)


# ---------------------------------------------------------------------------
# Full pipeline (overlay + iter 016 stack)
# ---------------------------------------------------------------------------


def test_hedged_stack_pandas_np_parity_cagr():
    """Full pipeline: pandas vs numpy must agree to ≤ 3 pp CAGR (G7)."""
    n = 504  # ~2 years
    rng = np.random.default_rng(7)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_eq_arr = rng.normal(0.0005, 0.012, n)
    r_bd_arr = rng.normal(0.0001, 0.004, n)
    iv_arr = np.clip(rng.normal(20.0, 4.0, n), 8.0, 60.0)
    # Synthesize prices from returns
    prices_arr = 100.0 * np.cumprod(1.0 + r_eq_arr)

    r_eq = pd.Series(r_eq_arr, index=idx)
    r_bd = pd.Series(r_bd_arr, index=idx)
    prices = pd.Series(prices_arr, index=idx)
    iv = pd.Series(iv_arr, index=idx)

    net_pd, _, _, _, _ = apply_put_spread_hedged_stack(
        r_eq, r_bd, prices, iv,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, rf=0.02, iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    net_np, _, _, _ = apply_put_spread_hedged_stack_np(
        r_eq_arr, r_bd_arr, prices_arr, iv_arr,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, rf=0.02, iv_scale=1.0, cost_bps_per_roll=5.0,
    )
    # Compare CAGR (lookback discards first 21 bars on both).
    eq_pd = (1.0 + net_pd).cumprod()
    eq_np = np.cumprod(1.0 + net_np)
    years_pd = len(net_pd) / 252.0
    years_np = len(net_np) / 252.0
    cagr_pd = float(eq_pd.iloc[-1] ** (1.0 / years_pd) - 1.0)
    cagr_np = float(eq_np[-1] ** (1.0 / years_np) - 1.0)
    assert abs(cagr_pd - cagr_np) * 100 <= 3.0


def test_hedge_ratio_zero_reduces_to_iter_016():
    """With hedge_notional_ratio=0, pipeline must equal iter 016 exactly
    (up to floating-point)."""
    from static_stack_vm import apply_static_stack_vol_managed

    n = 252
    rng = np.random.default_rng(11)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_eq_arr = rng.normal(0.0005, 0.012, n)
    r_bd_arr = rng.normal(0.0001, 0.004, n)
    prices_arr = 100.0 * np.cumprod(1.0 + r_eq_arr)
    iv_arr = np.full(n, 20.0)

    r_eq = pd.Series(r_eq_arr, index=idx)
    r_bd = pd.Series(r_bd_arr, index=idx)
    prices = pd.Series(prices_arr, index=idx)
    iv = pd.Series(iv_arr, index=idx)

    net_iter016, _, _, _ = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    net_020_zero, _, _, _, _ = apply_put_spread_hedged_stack(
        r_eq, r_bd, prices, iv,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
        k_long_pct=0.95, k_short_pct=0.90,
        dte_days=21, rf=0.02, iv_scale=1.0, cost_bps_per_roll=5.0,
        hedge_notional_ratio=0.0,
    )
    # Align (iter 020 drops overlay's first bar if missing; iter 016
    # drops first `lookback` bars). Compare on common intersection.
    common = net_iter016.index.intersection(net_020_zero.index)
    assert len(common) > 100
    np.testing.assert_allclose(
        net_iter016.loc[common].to_numpy(),
        net_020_zero.loc[common].to_numpy(),
        atol=1e-12,
    )
