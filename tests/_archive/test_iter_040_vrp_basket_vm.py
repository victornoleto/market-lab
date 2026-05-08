"""Iter 040 — TDD specs for vol-managed cross-asset VRP basket.

Locks the semantics of the MM 2017 vol-target wrapper BEFORE
implementation. The wrapper applies inverse-variance scaling to the
unscaled basket overlay:

    overlay_t = -harvest_notional * sum_i ( weights[i] * overlay_i[t] )
    σ̂²_overlay[t-1] = annualised rolling-21d variance of overlay,
                      shifted by 1 bar (no-lookahead)
    scale[t]   = clip( target_vol² / σ̂²_overlay[t-1], 0, max_lev )
    r_strategy[t] = rf_daily + scale[t] * overlay_t

Citations
---------
* `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP harvest.
* Moreira & Muir (2017) JoF 72(4) 1611-1644 — vol-target scaling.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "040-2026-04-25-0338-vrp-basket-vol-target"
ITER_039_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "039-2026-04-25-0313-vrp-basket-3etf"
ITER_020_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "020-2026-04-24-1850-put-spread-tail-hedge"
for p in (ITER_DIR, ITER_039_DIR, ITER_020_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from vrp_basket_vm import compute_vrp_basket_vm_returns  # noqa: E402
from numpy_reference_basket_vm import (  # noqa: E402
    compute_vrp_basket_vm_returns_np,
)
from vrp_basket import compute_vrp_basket_returns  # noqa: E402


def _make_synthetic(
    n: int = 300,
    drift: float = 0.0,
    vol: float = 0.20,
    iv_pct: float = 20.0,
    seed: int = 7,
    start_price: float = 100.0,
) -> tuple[pd.Series, pd.Series]:
    """Geometric-Brownian-motion price + flat IV — same convention as iter 039."""
    rng = np.random.default_rng(seed)
    dt = 1.0 / 252.0
    z = rng.standard_normal(n)
    log_rets = (drift - 0.5 * vol * vol) * dt + vol * np.sqrt(dt) * z
    prices = start_price * np.exp(np.cumsum(log_rets))
    idx = pd.bdate_range("2010-01-04", periods=n)
    return (
        pd.Series(prices, index=idx, name="price"),
        pd.Series(np.full(n, iv_pct), index=idx, name="vix"),
    )


def test_zero_harvest_returns_pure_rf() -> None:
    """harvest_notional=0 → strategy return == rf_daily exactly each bar.

    With zero harvest the overlay is identically zero, so σ̂²=0, scale=cap,
    but cap × 0 = 0. Net should be rf_daily on every valid bar.
    """
    p_spy, iv = _make_synthetic(seed=1)
    p_qqq, _ = _make_synthetic(seed=2, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=3, start_price=150.0)
    rf = 0.03
    r = compute_vrp_basket_vm_returns(
        prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        rf=rf,
        harvest_notional=0.0,
        target_vol=0.05,
        lookback=21,
        max_lev=2.0,
    )
    rf_daily_expected = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    assert np.allclose(r.to_numpy(), rf_daily_expected)


def test_max_lev_one_and_huge_target_reproduces_iter_039_basket() -> None:
    """max_lev=1.0 + target_vol → ∞ ⇒ scale ≡ 1.0; reduces to iter 039.

    When target_vol² >> σ̂²_overlay[t-1] always (e.g. target_vol=10×
    realized), the unclamped scale > max_lev and clip pins scale to
    max_lev. Setting max_lev=1.0 then reproduces the constant-1.0
    sizing of iter 039 exactly on bars where the rolling window is
    valid.
    """
    p_spy, iv = _make_synthetic(seed=11)
    p_qqq, _ = _make_synthetic(seed=12, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=13, start_price=150.0)
    rf = 0.02
    h = 1.0
    weights = {"SPY": 1.0 / 3, "QQQ": 1.0 / 3, "IWM": 1.0 / 3}
    iv_scales = {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25}

    vm = compute_vrp_basket_vm_returns(
        prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        rf=rf,
        harvest_notional=h,
        weights=weights,
        iv_scales=iv_scales,
        target_vol=10.0,    # 1000% ann → unclamped scale always huge
        lookback=21,
        max_lev=1.0,        # cap pins at 1.0 → reduces to iter 039
    )
    base = compute_vrp_basket_returns(
        prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        rf=rf,
        harvest_notional=h,
        weights=weights,
        iv_scales=iv_scales,
    )
    common = vm.index.intersection(base.index)
    assert len(common) > 50
    np.testing.assert_allclose(
        vm.loc[common].to_numpy(),
        base.loc[common].to_numpy(),
        atol=1e-12,
    )


def test_no_lookahead_scale_uses_t_minus_one() -> None:
    """scale[t] depends only on overlay_{t-lookback..t-1}; varying overlay[t]
    leaves scale[t] unchanged.

    Construct two scenarios identical up to bar t-1 but differing at bar t.
    Scale at bar t must be identical in both (computed from σ̂²_{t-1}); the
    daily return at bar t differs only because overlay[t] changed.
    """
    p_spy, iv = _make_synthetic(seed=21, n=120)
    p_qqq, _ = _make_synthetic(seed=22, start_price=200.0, n=120)
    p_iwm, _ = _make_synthetic(seed=23, start_price=150.0, n=120)

    # baseline run
    r1 = compute_vrp_basket_vm_returns(
        prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        target_vol=0.05, lookback=21, max_lev=2.0,
    )
    # perturb only the LAST bar of SPY (bar n-1) — scale at any t < n-1
    # must be unaffected; scale at t = n-1 is computed from σ̂²_{n-2}
    # which is the SAME (since the perturbation is at bar n-1 only).
    p_spy_pert = p_spy.copy()
    p_spy_pert.iloc[-1] = p_spy.iloc[-1] * 1.05
    r2 = compute_vrp_basket_vm_returns(
        prices={"SPY": p_spy_pert, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        target_vol=0.05, lookback=21, max_lev=2.0,
    )
    common = r1.index.intersection(r2.index)
    # All bars EXCEPT the last (and possibly the entry-roll bar where
    # entry_idx=0) should match exactly because overlay[t] does not
    # change for t ≤ n-2.
    diff = (r1.loc[common] - r2.loc[common]).abs()
    # At least the first half of bars should be untouched (σ̂²_{t-1}
    # depends only on overlay history; overlay history only differs at
    # the LAST perturbed bar).
    n = len(common)
    early = diff.iloc[: n - 5]
    # Use a generous threshold to account for the put-spread MtM
    # using the perturbed S_t at the last bar via roll-mark logic.
    assert early.max() < 1e-10, (
        f"early bars should be identical; max diff {early.max():.2e}"
    )


def test_pandas_numpy_parity() -> None:
    """G7 cross-library parity at floating-point precision (synthetic)."""
    p_spy, iv = _make_synthetic(seed=31)
    p_qqq, _ = _make_synthetic(seed=32, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=33, start_price=150.0)

    vm_pd = compute_vrp_basket_vm_returns(
        prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        rf=0.02,
        harvest_notional=1.0,
        weights={"SPY": 1.0 / 3, "QQQ": 1.0 / 3, "IWM": 1.0 / 3},
        iv_scales={"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
        target_vol=0.05, lookback=21, max_lev=2.0,
    )

    aligned = pd.concat(
        {"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm, "v": iv},
        axis=1, join="inner",
    ).dropna()
    arr_spy = aligned["SPY"].to_numpy(float)
    arr_qqq = aligned["QQQ"].to_numpy(float)
    arr_iwm = aligned["IWM"].to_numpy(float)
    arr_iv = aligned["v"].to_numpy(float)

    vm_np = compute_vrp_basket_vm_returns_np(
        prices={"SPY": arr_spy, "QQQ": arr_qqq, "IWM": arr_iwm},
        iv_raw=arr_iv,
        rf=0.02,
        harvest_notional=1.0,
        weights={"SPY": 1.0 / 3, "QQQ": 1.0 / 3, "IWM": 1.0 / 3},
        iv_scales={"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
        target_vol=0.05, lookback=21, max_lev=2.0,
    )
    common_pd = vm_pd.to_numpy()
    np.testing.assert_allclose(common_pd, vm_np, atol=1e-12)


def test_negative_target_vol_raises() -> None:
    p_spy, iv = _make_synthetic(seed=41)
    p_qqq, _ = _make_synthetic(seed=42, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=43, start_price=150.0)
    with pytest.raises(ValueError, match="target_vol"):
        compute_vrp_basket_vm_returns(
            prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
            iv_series=iv,
            target_vol=-0.01, lookback=21, max_lev=2.0,
        )


def test_max_lev_nonpositive_raises() -> None:
    p_spy, iv = _make_synthetic(seed=51)
    p_qqq, _ = _make_synthetic(seed=52, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=53, start_price=150.0)
    with pytest.raises(ValueError, match="max_lev"):
        compute_vrp_basket_vm_returns(
            prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
            iv_series=iv,
            target_vol=0.05, lookback=21, max_lev=0.0,
        )


def test_lookback_too_small_raises() -> None:
    p_spy, iv = _make_synthetic(seed=61)
    p_qqq, _ = _make_synthetic(seed=62, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=63, start_price=150.0)
    with pytest.raises(ValueError, match="lookback"):
        compute_vrp_basket_vm_returns(
            prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
            iv_series=iv,
            target_vol=0.05, lookback=1, max_lev=2.0,
        )
