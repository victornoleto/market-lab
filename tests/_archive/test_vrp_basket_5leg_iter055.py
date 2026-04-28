"""Iter 055 — TDD spec for 5-leg cross-region VRP basket.

Verifies that iter 039's ``compute_vrp_basket_returns`` (generic over
leg count) produces sensible results when extended to 5 tickers and
that key invariants hold.

Citations
---------
* `[volatility_trading, p.218]` — cross-asset VRP harvest discipline.
* `[advances_fin_ml, p.31-34]` — cross-library parity.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_039 = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "039-2026-04-25-0313-vrp-basket-3etf"
if str(ITER_039) not in sys.path:
    sys.path.insert(0, str(ITER_039))

from vrp_basket import compute_vrp_basket_returns  # noqa: E402
from numpy_reference_basket import compute_vrp_basket_returns_np  # noqa: E402


def _synthetic_prices(seed: int, n: int = 1500) -> pd.Series:
    """Geometric-Brownian-motion price series (no real data) for tests."""
    rng = np.random.default_rng(seed)
    daily_drift = 0.10 / 252.0
    daily_vol = 0.18 / np.sqrt(252.0)
    log_ret = rng.normal(daily_drift, daily_vol, size=n)
    eq = 100.0 * np.exp(np.cumsum(log_ret))
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    return pd.Series(eq, index=idx, name="adj_close")


def _synthetic_vix(idx: pd.DatetimeIndex, seed: int = 42) -> pd.Series:
    rng = np.random.default_rng(seed)
    base = 18.0 + 4.0 * np.sin(np.linspace(0, 12 * np.pi, len(idx)))
    noise = rng.normal(0, 1.5, size=len(idx))
    vix = np.clip(base + noise, 9.0, 80.0)
    return pd.Series(vix, index=idx, name="VIX")


# --------------------------------------------------------------------------
# Test 1: 5-leg basket produces a non-empty Series with expected length
# --------------------------------------------------------------------------


def test_5leg_basket_returns_shape() -> None:
    tickers = ["SPY", "QQQ", "IWM", "EFA", "EEM"]
    prices = {t: _synthetic_prices(seed=i) for i, t in enumerate(tickers)}
    common = prices["SPY"].index
    for t in tickers:
        common = common.intersection(prices[t].index)
    prices = {t: s.loc[common] for t, s in prices.items()}
    vix = _synthetic_vix(common)

    weights = {t: 1.0 / 5 for t in tickers}
    iv_scales = {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25, "EFA": 1.05, "EEM": 1.30}

    out = compute_vrp_basket_returns(
        prices, vix,
        rf=0.02,
        harvest_notional=1.0,
        weights=weights,
        iv_scales=iv_scales,
        k_long_pct=0.95,
        k_short_pct=0.90,
        dte_days=21,
        cost_bps_per_roll=5.0,
    )
    assert isinstance(out, pd.Series)
    assert len(out) >= 1400  # ~1500 - small alignment trim
    assert out.notna().all()
    assert out.std() > 0  # non-trivial variance


# --------------------------------------------------------------------------
# Test 2: 5-leg with one weight = 1, others = 0 ≡ single-asset case
# --------------------------------------------------------------------------


def test_5leg_single_asset_reduction() -> None:
    """weights = (1, 0, 0, 0, 0) reduces to single-asset SPY VRP overlay."""
    tickers = ["SPY", "QQQ", "IWM", "EFA", "EEM"]
    prices = {t: _synthetic_prices(seed=i) for i, t in enumerate(tickers)}
    common = prices["SPY"].index
    for t in tickers:
        common = common.intersection(prices[t].index)
    prices = {t: s.loc[common] for t, s in prices.items()}
    vix = _synthetic_vix(common)
    iv_scales = {"SPY": 1.0, "QQQ": 1.0, "IWM": 1.0, "EFA": 1.0, "EEM": 1.0}

    weights_5 = {"SPY": 1.0, "QQQ": 0.0, "IWM": 0.0, "EFA": 0.0, "EEM": 0.0}
    out_5 = compute_vrp_basket_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        weights=weights_5, iv_scales=iv_scales,
    )

    weights_1 = {"SPY": 1.0}
    prices_1 = {"SPY": prices["SPY"]}
    iv_scales_1 = {"SPY": 1.0}
    out_1 = compute_vrp_basket_returns(
        prices_1, vix,
        rf=0.02, harvest_notional=1.0,
        weights=weights_1, iv_scales=iv_scales_1,
    )

    common_idx = out_5.index.intersection(out_1.index)
    assert len(common_idx) > 0
    diff = (out_5.loc[common_idx] - out_1.loc[common_idx]).abs().max()
    assert diff < 1e-12, f"single-asset reduction broken; max abs diff {diff}"


# --------------------------------------------------------------------------
# Test 3: pandas vs numpy parity (G7 micro-test on 5 legs)
# --------------------------------------------------------------------------


def test_5leg_crosslib_parity() -> None:
    """Pandas and numpy implementations must agree to numerical noise."""
    tickers = ["SPY", "QQQ", "IWM", "EFA", "EEM"]
    prices = {t: _synthetic_prices(seed=i) for i, t in enumerate(tickers)}
    common = prices["SPY"].index
    for t in tickers:
        common = common.intersection(prices[t].index)
    prices = {t: s.loc[common] for t, s in prices.items()}
    vix = _synthetic_vix(common)
    weights = {t: 1.0 / 5 for t in tickers}
    iv_scales = {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25, "EFA": 1.05, "EEM": 1.30}

    out_pd = compute_vrp_basket_returns(
        prices, vix,
        rf=0.02, harvest_notional=1.0,
        weights=weights, iv_scales=iv_scales,
    )
    aligned = pd.concat({**prices, "v": vix}, axis=1, join="inner").dropna()
    arrs = {tk: aligned[tk].to_numpy(float) for tk in tickers}
    arr_v = aligned["v"].to_numpy(float)
    out_np = compute_vrp_basket_returns_np(
        arrs, arr_v,
        rf=0.02, harvest_notional=1.0,
        weights=weights, iv_scales=iv_scales,
    )

    diff = float(np.max(np.abs(out_pd.values - out_np)))
    assert diff < 1e-12, f"cross-lib parity broken; max abs diff {diff}"


# --------------------------------------------------------------------------
# Test 4: harvest_notional sign-flip identity
# --------------------------------------------------------------------------


def test_5leg_signflip_identity() -> None:
    """Doubling harvest_notional doubles the active overlay component."""
    tickers = ["SPY", "QQQ", "IWM", "EFA", "EEM"]
    prices = {t: _synthetic_prices(seed=i + 7) for i, t in enumerate(tickers)}
    common = prices["SPY"].index
    for t in tickers:
        common = common.intersection(prices[t].index)
    prices = {t: s.loc[common] for t, s in prices.items()}
    vix = _synthetic_vix(common, seed=99)
    weights = {t: 1.0 / 5 for t in tickers}
    iv_scales = {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25, "EFA": 1.05, "EEM": 1.30}

    out_h1 = compute_vrp_basket_returns(
        prices, vix, rf=0.02, harvest_notional=1.0,
        weights=weights, iv_scales=iv_scales,
    )
    out_h2 = compute_vrp_basket_returns(
        prices, vix, rf=0.02, harvest_notional=2.0,
        weights=weights, iv_scales=iv_scales,
    )

    rf_daily = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    overlay_1 = out_h1 - rf_daily
    overlay_2 = out_h2 - rf_daily
    common_idx = overlay_1.index.intersection(overlay_2.index)
    diff = (overlay_2.loc[common_idx] - 2.0 * overlay_1.loc[common_idx]).abs().max()
    assert diff < 1e-12, f"sign-flip / scaling identity broken; max abs diff {diff}"


# --------------------------------------------------------------------------
# Test 5: weights validation — sum of negative weight raises
# --------------------------------------------------------------------------


def test_5leg_negative_weight_rejected() -> None:
    tickers = ["SPY", "QQQ", "IWM", "EFA", "EEM"]
    prices = {t: _synthetic_prices(seed=i) for i, t in enumerate(tickers)}
    common = prices["SPY"].index
    for t in tickers:
        common = common.intersection(prices[t].index)
    prices = {t: s.loc[common] for t, s in prices.items()}
    vix = _synthetic_vix(common)
    weights = {"SPY": 1.2, "QQQ": -0.2, "IWM": 0.0, "EFA": 0.0, "EEM": 0.0}
    iv_scales = {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25, "EFA": 1.05, "EEM": 1.30}

    with pytest.raises(ValueError, match="weights"):
        compute_vrp_basket_returns(
            prices, vix, rf=0.02, harvest_notional=1.0,
            weights=weights, iv_scales=iv_scales,
        )
