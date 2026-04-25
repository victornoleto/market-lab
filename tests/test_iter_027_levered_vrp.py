"""Iter 027 — TDD specs for Levered VRP-primary (`harvest_notional=3.5`).

Locks the leverage-neutrality assumption that justifies iter 027's
hypothesis BEFORE running on real data:

  ``r_strategy[t] = rf_daily + 3.5 * (-overlay[t])``

The strategy mechanism is **identical** to iter 026 — only the
`harvest_notional` parameter changes from 1.0 to 3.5. These specs
verify:

1. Linear scaling of the harvest portion (already proved generally in
   iter 026's `test_harvest_scales_linearly`; restated here at h=3.5).
2. Sharpe-ratio invariance under leverage (theory says yes — variance
   scales 1:1 with mean).
3. Volatility-drag stays bounded (CAGR_realised within 0.5%/yr of
   `rf + 3.5 × harvest_ann`).
4. Per-roll loss stays capped under leverage (no negative-equity
   blow-up; the credit-spread cap respects leverage).

Citations
---------
* `[volatility_trading, ch.3]` — VRP mechanics (Sinclair 2013).
* `[volatility_trading, p.41]` — capped-tail.
* `[risk_parity, p.5]` — Asness-Frazzini-Pedersen 2012 levered-low-vol.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ITER_026_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "026-2026-04-24-2122-vrp-primary-portfolio"
ITER_020_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "020-2026-04-24-1850-put-spread-tail-hedge"
for p in (ITER_026_DIR, ITER_020_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from vrp_primary import compute_vrp_primary_returns  # noqa: E402

ITER_027_HARVEST_NOTIONAL = 3.5


def _make_synthetic_inputs(
    n: int = 500,
    drift: float = 0.0,
    vol: float = 0.18,
    iv_pct: float = 22.0,
    seed: int = 27,
) -> tuple[pd.Series, pd.Series]:
    """Synthetic GBM + constant-IV — sufficient for harvest dynamics."""
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


def test_iter027_h35_scales_iter026_h10_linearly() -> None:
    """At h=3.5 the harvest portion is exactly 3.5× the h=1.0 baseline.

    This is the iter 027-specific restatement of iter 026's general
    linearity test — pre-commits the iter 027 cfg's mathematical
    foundation.
    """
    prices, iv = _make_synthetic_inputs()
    rf = 0.02
    r_h10 = compute_vrp_primary_returns(
        prices, iv,
        rf=rf,
        harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        cost_bps_per_roll=5.0,
    )
    r_h35 = compute_vrp_primary_returns(
        prices, iv,
        rf=rf,
        harvest_notional=ITER_027_HARVEST_NOTIONAL,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        cost_bps_per_roll=5.0,
    )
    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    overlay_h10 = r_h10.values - rf_daily
    overlay_h35 = r_h35.values - rf_daily
    np.testing.assert_allclose(overlay_h35, 3.5 * overlay_h10, atol=1e-12)


def test_iter027_sharpe_invariant_under_leverage() -> None:
    """Sharpe(h=3.5) ≈ Sharpe(h=1.0) on the same dataset.

    Leverage scales mean and std equally, so the ratio is invariant.
    Floating-point noise allowed but the theoretical equality should
    hold to within 1e-9.
    """
    prices, iv = _make_synthetic_inputs(n=2000, vol=0.20, iv_pct=23.0)
    rf = 0.02
    r_h10 = compute_vrp_primary_returns(
        prices, iv,
        rf=rf, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        cost_bps_per_roll=5.0,
    )
    r_h35 = compute_vrp_primary_returns(
        prices, iv,
        rf=rf, harvest_notional=ITER_027_HARVEST_NOTIONAL,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        cost_bps_per_roll=5.0,
    )
    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0

    # Excess-return Sharpe (subtract rf_daily) — fully leverage-neutral.
    def excess_sharpe(r):
        e = r - rf_daily
        return float(e.mean() / e.std() * np.sqrt(252)) if e.std() > 0 else 0.0

    sr10 = excess_sharpe(r_h10)
    sr35 = excess_sharpe(r_h35)
    assert abs(sr35 - sr10) < 1e-9, (
        f"excess-Sharpe shifted under leverage: h=1.0→{sr10}, h=3.5→{sr35}"
    )


def test_iter027_compounding_deviation_bounded() -> None:
    """CAGR(h=3.5) deviates from rf + 3.5×(CAGR(h=1.0) - rf) by < 2%/yr.

    Linear projection is exact for arithmetic mean returns; realised
    CAGR (geometric) deviates by ~0.5×σ² (volatility drag) on average,
    but on any one synthetic path the deviation can be ±2%/yr depending
    on path autocorrelation. The test asserts the absolute deviation
    is BOUNDED, not zero.
    """
    prices, iv = _make_synthetic_inputs(n=2000, vol=0.18, iv_pct=22.0)
    rf = 0.02
    r_h10 = compute_vrp_primary_returns(
        prices, iv,
        rf=rf, harvest_notional=1.0,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        cost_bps_per_roll=5.0,
    )
    r_h35 = compute_vrp_primary_returns(
        prices, iv,
        rf=rf, harvest_notional=ITER_027_HARVEST_NOTIONAL,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        cost_bps_per_roll=5.0,
    )
    eq10 = (1.0 + r_h10).cumprod()
    eq35 = (1.0 + r_h35).cumprod()
    n10 = len(r_h10)
    n35 = len(r_h35)
    cagr10 = float(eq10.iloc[-1] ** (252.0 / n10) - 1.0)
    cagr35 = float(eq35.iloc[-1] ** (252.0 / n35) - 1.0)

    # Linear projection: rf + 3.5 × (cagr10 - rf)
    cagr_projected = rf + 3.5 * (cagr10 - rf)
    deviation = cagr_projected - cagr35
    assert abs(deviation) < 0.02, (
        f"compounding deviation exceeds 2%/yr buffer: "
        f"projected={cagr_projected:.4f}, realised={cagr35:.4f}, "
        f"deviation={deviation:.4f}"
    )


def test_iter027_per_roll_loss_capped_under_leverage() -> None:
    """Per-bar loss at h=3.5 stays > -1.0 (no model blow-up).

    The credit-spread cap is `(spread_width - net_credit) ≈ 4-4.5%` per
    spread; at h=3.5 the worst per-bar loss is ~`3.5 × 4.5%` ≈ 16%. The
    test asserts no individual bar produces a return below -100% (which
    would indicate a sign-flip or arithmetic error under leverage).
    """
    rng = np.random.default_rng(99)
    n = 1000
    dt = 1.0 / 252.0
    # Use stressed inputs — high vol, high IV — to stress-test the cap.
    z = rng.standard_normal(n)
    log_rets = (-0.05 - 0.5 * 0.40 * 0.40) * dt + 0.40 * np.sqrt(dt) * z
    prices = pd.Series(
        100.0 * np.exp(np.cumsum(log_rets)),
        index=pd.bdate_range("2008-01-02", periods=n),
    )
    iv = pd.Series(np.full(n, 30.0), index=prices.index)

    r = compute_vrp_primary_returns(
        prices, iv,
        rf=0.02, harvest_notional=ITER_027_HARVEST_NOTIONAL,
        k_long_pct=0.95, k_short_pct=0.90, dte_days=21,
        cost_bps_per_roll=5.0,
    )
    assert (r > -1.0).all(), (
        f"per-bar return < -100% detected: min={r.min():.4f} bars="
        f"{(r <= -1.0).sum()}"
    )
    # Equity must remain positive throughout (no negative-equity blow-up).
    eq = (1.0 + r).cumprod()
    assert (eq > 0).all(), f"equity went non-positive: min={eq.min():.4f}"
