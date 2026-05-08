"""Iter 039 — TDD specs for cross-asset VRP basket portfolio.

Locks the semantics of the basket harvester BEFORE implementation:

  ``r_strategy[t] = rf_daily
                    + harvest_notional * sum_i ( weights[i] * (-overlay_i[t]) )``

where ``overlay_i`` is iter 020's `compute_put_spread_daily_returns`
applied to ticker ``i`` with iv_scales[i].

Citations
---------
* `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP harvest.
* `[volatility_trading, ch.3, p.41, p.217]` — VRP mechanics.
* Bondarenko (2014) QJF 4(3); Carr-Wu (2009) RFS 22(3); Driessen et al
  (2009) JoF 64(4); Bakshi-Madan (2006) JFE 81(2); AMP (2013) JoF 68(3).
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
    "039-2026-04-25-0313-vrp-basket-3etf"
ITER_026_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "026-2026-04-24-2122-vrp-primary-portfolio"
ITER_020_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "020-2026-04-24-1850-put-spread-tail-hedge"
for p in (ITER_DIR, ITER_026_DIR, ITER_020_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from vrp_basket import compute_vrp_basket_returns  # noqa: E402
from numpy_reference_basket import (  # noqa: E402
    compute_vrp_basket_returns_np,
)
from vrp_primary import compute_vrp_primary_returns  # noqa: E402


def _make_synthetic(
    n: int = 100,
    drift: float = 0.0,
    vol: float = 0.20,
    iv_pct: float = 20.0,
    seed: int = 7,
    start_price: float = 100.0,
) -> tuple[pd.Series, pd.Series]:
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
    """harvest_notional=0 → strategy return == rf_daily exactly each bar."""
    p_spy, iv = _make_synthetic(seed=1)
    p_qqq, _ = _make_synthetic(seed=2, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=3, start_price=150.0)
    rf = 0.03
    r = compute_vrp_basket_returns(
        prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        rf=rf,
        harvest_notional=0.0,
    )
    rf_daily_expected = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    assert np.allclose(r.to_numpy(), rf_daily_expected)


def test_single_leg_reduction_matches_iter_026() -> None:
    """weights=(1, 0, 0) + iv_scale=1.0 → matches iter 026 single-asset."""
    p_spy, iv = _make_synthetic(seed=11)
    p_qqq, _ = _make_synthetic(seed=12, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=13, start_price=150.0)
    rf = 0.02
    h = 1.0

    basket = compute_vrp_basket_returns(
        prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        rf=rf,
        harvest_notional=h,
        weights={"SPY": 1.0, "QQQ": 0.0, "IWM": 0.0},
        iv_scales={"SPY": 1.0, "QQQ": 1.0, "IWM": 1.0},
    )
    single = compute_vrp_primary_returns(
        p_spy, iv,
        rf=rf,
        harvest_notional=h,
        iv_scale=1.0,
    )
    common = basket.index.intersection(single.index)
    assert len(common) > 50
    np.testing.assert_allclose(
        basket.loc[common].to_numpy(),
        single.loc[common].to_numpy(),
        atol=1e-12,
    )


def test_basket_equals_weighted_sum_of_single_overlays() -> None:
    """Basket return ≡ rf + h * sum_i(w_i * (-overlay_i)) on raw inputs."""
    p_spy, iv = _make_synthetic(seed=21)
    p_qqq, _ = _make_synthetic(seed=22, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=23, start_price=150.0)
    rf = 0.02
    h = 1.0
    weights = {"SPY": 1.0 / 3, "QQQ": 1.0 / 3, "IWM": 1.0 / 3}
    iv_scales = {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25}

    basket = compute_vrp_basket_returns(
        prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        rf=rf,
        harvest_notional=h,
        weights=weights,
        iv_scales=iv_scales,
    )

    legs = {}
    for tk, px in {"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm}.items():
        legs[tk] = compute_vrp_primary_returns(
            px, iv, rf=rf, harvest_notional=1.0,
            iv_scale=iv_scales[tk],
        )
    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    overlays = {tk: (legs[tk] - rf_daily) for tk in legs}
    expected = rf_daily + h * sum(
        weights[tk] * overlays[tk] for tk in legs
    )
    common = basket.index.intersection(expected.index)
    np.testing.assert_allclose(
        basket.loc[common].to_numpy(),
        expected.loc[common].to_numpy(),
        atol=1e-12,
    )


def test_pandas_numpy_parity() -> None:
    """G7 cross-library parity at floating-point precision (synthetic)."""
    p_spy, iv = _make_synthetic(seed=31)
    p_qqq, _ = _make_synthetic(seed=32, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=33, start_price=150.0)

    basket_pd = compute_vrp_basket_returns(
        prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
        iv_series=iv,
        rf=0.02,
        harvest_notional=1.0,
        weights={"SPY": 1.0 / 3, "QQQ": 1.0 / 3, "IWM": 1.0 / 3},
        iv_scales={"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    )

    aligned = pd.concat(
        {"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm, "v": iv},
        axis=1, join="inner",
    ).dropna()
    arr_spy = aligned["SPY"].to_numpy(float)
    arr_qqq = aligned["QQQ"].to_numpy(float)
    arr_iwm = aligned["IWM"].to_numpy(float)
    arr_iv = aligned["v"].to_numpy(float)

    basket_np = compute_vrp_basket_returns_np(
        prices={"SPY": arr_spy, "QQQ": arr_qqq, "IWM": arr_iwm},
        iv_raw=arr_iv,
        rf=0.02,
        harvest_notional=1.0,
        weights={"SPY": 1.0 / 3, "QQQ": 1.0 / 3, "IWM": 1.0 / 3},
        iv_scales={"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    )

    np.testing.assert_allclose(
        basket_pd.to_numpy(), basket_np, atol=1e-12,
    )


def test_negative_harvest_raises() -> None:
    p_spy, iv = _make_synthetic(seed=41)
    p_qqq, _ = _make_synthetic(seed=42, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=43, start_price=150.0)
    with pytest.raises(ValueError, match="harvest_notional"):
        compute_vrp_basket_returns(
            prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
            iv_series=iv,
            harvest_notional=-0.1,
        )


def test_negative_weight_raises() -> None:
    p_spy, iv = _make_synthetic(seed=51)
    p_qqq, _ = _make_synthetic(seed=52, start_price=200.0)
    p_iwm, _ = _make_synthetic(seed=53, start_price=150.0)
    with pytest.raises(ValueError, match=r"weights\[QQQ\]"):
        compute_vrp_basket_returns(
            prices={"SPY": p_spy, "QQQ": p_qqq, "IWM": p_iwm},
            iv_series=iv,
            weights={"SPY": 0.5, "QQQ": -0.1, "IWM": 0.6},
        )
