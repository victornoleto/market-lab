"""Iter 026 — TDD specs for VRP-primary stand-alone portfolio.

Locks the semantics of the stand-alone VRP harvester BEFORE
implementation:

  ``r_strategy[t] = rf_daily + harvest_notional * (-overlay[t])``

where ``overlay[t]`` is iter 020's `compute_put_spread_daily_returns`
(the long-holder's daily P&L as fraction of S_entry). The strategy
holds T-bills as collateral and SHORTS a 5/10% OTM put credit spread
on SPY/QQQ each month.

Citations
---------
* `[volatility_trading, ch.3]` — VRP mechanics (Sinclair 2013).
* `[volatility_trading, p.41]` — capped-tail justification (SPX
  kurtosis 21.3 makes naked short put unsuitable).
* `[volatility_trading, p.217]` — short index vol harvest rule.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "026-2026-04-24-2122-vrp-primary-portfolio"
ITER_020_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "020-2026-04-24-1850-put-spread-tail-hedge"
for p in (ITER_DIR, ITER_020_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from vrp_primary import compute_vrp_primary_returns  # noqa: E402
from numpy_reference_vrp import (  # noqa: E402
    compute_vrp_primary_returns_np,
)
from put_spread_hedge import compute_put_spread_daily_returns  # noqa: E402


def _make_synthetic_inputs(
    n: int = 100,
    drift: float = 0.0,
    vol: float = 0.20,
    iv_pct: float = 20.0,
    seed: int = 7,
) -> tuple[pd.Series, pd.Series]:
    """Build (price, iv) for a synthetic horizon."""
    rng = np.random.default_rng(seed)
    dt = 1.0 / 252.0
    z = rng.standard_normal(n)
    log_rets = (drift - 0.5 * vol * vol) * dt + vol * np.sqrt(dt) * z
    prices = 100.0 * np.exp(np.cumsum(log_rets))
    idx = pd.bdate_range("2010-01-04", periods=n)
    return (
        pd.Series(prices, index=idx, name="price"),
        pd.Series(np.full(n, iv_pct), index=idx, name="vix"),
    )


def test_zero_harvest_returns_pure_rf() -> None:
    """harvest_notional=0 → daily return == rf_daily exactly each bar."""
    prices, iv = _make_synthetic_inputs()
    rf = 0.04
    r = compute_vrp_primary_returns(
        prices, iv,
        rf=rf,
        harvest_notional=0.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    rf_daily_expected = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    np.testing.assert_allclose(r.values, rf_daily_expected, atol=1e-14)


def test_negative_harvest_raises() -> None:
    """harvest_notional<0 raises ValueError (sign flip is internal)."""
    prices, iv = _make_synthetic_inputs()
    with pytest.raises(ValueError, match="harvest_notional"):
        compute_vrp_primary_returns(
            prices, iv,
            rf=0.02,
            harvest_notional=-1.0,
            k_long_pct=0.95,
            k_short_pct=0.90,
            dte_days=21,
        )


def test_pure_overlay_when_rf_zero_matches_iter_021_signs() -> None:
    """rf=0, harvest_notional=1.0 → strategy returns = -overlay (iter 021).

    Floating-point parity: stand-alone short writer with rf=0 is
    exactly the negated overlay stream from iter 020's pricer.
    """
    prices, iv = _make_synthetic_inputs(n=80, vol=0.18, iv_pct=22.0)
    overlay = compute_put_spread_daily_returns(
        prices, iv,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        rf=0.0,
        cost_bps_per_roll=5.0,
    )
    r = compute_vrp_primary_returns(
        prices, iv,
        rf=0.0,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    np.testing.assert_allclose(r.values, -overlay.values, atol=1e-14)


def test_pipeline_runs_end_to_end_50_bars() -> None:
    """50-bar synthetic dataset produces a finite Sharpe + correct length."""
    prices, iv = _make_synthetic_inputs(n=50, vol=0.20, iv_pct=20.0)
    r = compute_vrp_primary_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    assert len(r) == 50
    assert np.isfinite(r.values).all()


def test_harvest_scales_linearly() -> None:
    """harvest_notional scales the overlay portion linearly.

    For two harvest values h1 and h2:
        r(h1) - rf_daily = (h1/h2) * (r(h2) - rf_daily)
    """
    prices, iv = _make_synthetic_inputs(n=60, vol=0.25, iv_pct=22.0)
    r1 = compute_vrp_primary_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    r2 = compute_vrp_primary_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=2.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    rf_daily = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    overlay_h1 = r1.values - rf_daily
    overlay_h2 = r2.values - rf_daily
    np.testing.assert_allclose(overlay_h2, 2.0 * overlay_h1, atol=1e-12)


def test_numpy_reference_parity() -> None:
    """G7 parity check: pandas-engine and pure-numpy reference agree."""
    prices, iv = _make_synthetic_inputs(n=200, vol=0.22, iv_pct=21.0)
    r_pd = compute_vrp_primary_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    r_np = compute_vrp_primary_returns_np(
        prices.to_numpy(),
        iv.to_numpy(),
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    np.testing.assert_allclose(r_pd.values, r_np, atol=1e-10)


def test_returns_index_matches_aligned_input() -> None:
    """Output index = aligned (price ∩ iv) index, no surprises."""
    prices, iv = _make_synthetic_inputs(n=30)
    r = compute_vrp_primary_returns(
        prices, iv,
        rf=0.02,
        harvest_notional=1.0,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    pd.testing.assert_index_equal(r.index, prices.index)


def test_dte_validation_propagates() -> None:
    """dte_days<2 should raise (delegated to compute_put_spread_daily_returns)."""
    prices, iv = _make_synthetic_inputs()
    with pytest.raises(ValueError):
        compute_vrp_primary_returns(
            prices, iv,
            rf=0.02,
            harvest_notional=1.0,
            k_long_pct=0.95,
            k_short_pct=0.90,
            dte_days=1,
            cost_bps_per_roll=5.0,
        )


def test_strike_validation_propagates() -> None:
    """k_short_pct >= k_long_pct should raise."""
    prices, iv = _make_synthetic_inputs()
    with pytest.raises(ValueError):
        compute_vrp_primary_returns(
            prices, iv,
            rf=0.02,
            harvest_notional=1.0,
            k_long_pct=0.90,
            k_short_pct=0.95,
            dte_days=21,
            cost_bps_per_roll=5.0,
        )
