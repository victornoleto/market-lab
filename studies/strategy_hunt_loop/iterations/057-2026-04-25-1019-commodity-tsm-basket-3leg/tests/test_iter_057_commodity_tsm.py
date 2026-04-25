"""TDD specs for iter 057 — commodity TSM basket (USO+UNG+SLV) + iter 046.

Per-asset boolean TSM (same rule as iter 049 gold TSM):
    pos_i[t] = 1 if (price_i[t-1] / price_i[t-1-L] - 1) > 0 else 0
    r_i_tsm[t] = pos_i[t] * r_i[t] + (1 - pos_i[t]) * rf_d - cost_i[t]
    r_basket[t] = (1/N) * sum_i r_i_tsm[t]

Combined: r_combined[t] = w_046 * r_046[t] + w_csm * r_basket[t].

Citations
---------
* `[systematic_trading]` — Carver TSM rule.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* MOP 2012 (TSM across asset classes) — TSM positive Sharpe on commodities.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from commodity_tsm import (  # noqa: E402
    compute_single_asset_tsm_returns,
    compute_commodity_basket_tsm_returns,
)
from numpy_reference_iter057 import (  # noqa: E402
    compute_single_asset_tsm_np,
    compute_commodity_basket_np,
)
from combined_046_plus_csm import combine_046_plus_csm  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_prices(n: int = 300, drift: float = 0.0003, seed: int = 7,
                 name: str = "ASSET") -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    rets = rng.normal(loc=drift, scale=0.012, size=n)
    return pd.Series(np.cumprod(1.0 + rets) * 100.0, index=idx, name=name)


def _make_returns(n: int = 300, seed: int = 11) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    return pd.Series(rng.normal(0.0005, 0.011, size=n), index=idx, name="r_046")


# ---------------------------------------------------------------------------
# 1. Single-asset TSM core engine (sanity layer; basket is built on top)
# ---------------------------------------------------------------------------


def test_single_asset_tsm_indexed_to_returns():
    px = _make_prices(120, name="USO")
    out = compute_single_asset_tsm_returns(px, lookback=90)
    assert len(out) == len(px) - 1
    assert out.index.equals(px.index[1:])


def test_single_asset_tsm_warmup_is_cash():
    px = _make_prices(150, name="USO")
    rf = 0.02
    out = compute_single_asset_tsm_returns(px, lookback=90, rf=rf)
    rf_d = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    np.testing.assert_allclose(out.iloc[:90].values, np.full(90, rf_d), atol=1e-12)


def test_single_asset_tsm_no_lookahead():
    """Position at t depends only on prices ≤ t-1 (signal computed on lagged data)."""
    px = _make_prices(200, name="USO")
    out_full = compute_single_asset_tsm_returns(px, lookback=90, rf=0.02, cost_bps=0.0)
    px_modified = px.copy()
    px_modified.iloc[-1] = px.iloc[-1] * 2.0
    out_modified = compute_single_asset_tsm_returns(
        px_modified, lookback=90, rf=0.02, cost_bps=0.0,
    )
    np.testing.assert_array_equal(
        out_full.iloc[:-1].values, out_modified.iloc[:-1].values,
    )


def test_single_asset_tsm_long_in_uptrend():
    n = 200
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    px = pd.Series(np.cumprod(np.full(n, 1.005)) * 100.0, index=idx, name="USO")
    out = compute_single_asset_tsm_returns(px, lookback=90, rf=0.02, cost_bps=0.0)
    np.testing.assert_allclose(out.iloc[90:].values, 0.005, atol=1e-9)


# ---------------------------------------------------------------------------
# 2. Basket aggregation
# ---------------------------------------------------------------------------


def test_basket_single_asset_reduces_to_single():
    """Universe = {GLD} → basket equals the single-asset TSM stream exactly."""
    px = _make_prices(300, seed=33, name="GLD")
    single = compute_single_asset_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    basket = compute_commodity_basket_tsm_returns(
        {"GLD": px}, lookback=90, rf=0.02, cost_bps=5.0,
    )
    np.testing.assert_allclose(basket.values, single.values, atol=1e-12)


def test_basket_three_asset_is_arithmetic_mean():
    """3-asset basket equals 1/3 sum of individual TSM streams (inner-join)."""
    pxa = _make_prices(300, seed=11, name="USO")
    pxb = _make_prices(300, seed=22, name="UNG")
    pxc = _make_prices(300, seed=33, name="SLV")
    a = compute_single_asset_tsm_returns(pxa, lookback=90, rf=0.02, cost_bps=5.0)
    b = compute_single_asset_tsm_returns(pxb, lookback=90, rf=0.02, cost_bps=5.0)
    c = compute_single_asset_tsm_returns(pxc, lookback=90, rf=0.02, cost_bps=5.0)
    common = a.index.intersection(b.index).intersection(c.index)
    expected = (a.loc[common] + b.loc[common] + c.loc[common]) / 3.0
    basket = compute_commodity_basket_tsm_returns(
        {"USO": pxa, "UNG": pxb, "SLV": pxc},
        lookback=90, rf=0.02, cost_bps=5.0,
    )
    np.testing.assert_allclose(basket.loc[common].values, expected.values, atol=1e-12)


def test_basket_inner_joins_indexes():
    """Basket inner-joins assets with non-overlapping start dates."""
    long_px = _make_prices(300, seed=11, name="USO")
    # SLV starts 50 bars later
    short_px = _make_prices(250, seed=22, name="SLV").shift(freq="50B")
    short_px.index = pd.date_range(
        long_px.index[50], periods=250, freq="B",
    )
    short_px.name = "SLV"
    basket = compute_commodity_basket_tsm_returns(
        {"USO": long_px, "SLV": short_px},
        lookback=30, rf=0.02, cost_bps=5.0,
    )
    # Basket index must lie inside both individual return indexes
    long_ret = compute_single_asset_tsm_returns(long_px, lookback=30, rf=0.02, cost_bps=5.0)
    short_ret = compute_single_asset_tsm_returns(short_px, lookback=30, rf=0.02, cost_bps=5.0)
    expected_idx = long_ret.index.intersection(short_ret.index)
    assert basket.index.equals(expected_idx)


def test_basket_empty_universe_raises():
    with pytest.raises(ValueError):
        compute_commodity_basket_tsm_returns({}, lookback=90)


# ---------------------------------------------------------------------------
# 3. Combined w iter 046
# ---------------------------------------------------------------------------


def test_combined_reduces_to_iter046_when_w_csm_zero():
    r_046 = _make_returns(300, seed=11)
    pxa = _make_prices(300, seed=22, name="USO")
    pxb = _make_prices(300, seed=33, name="UNG")
    pxc = _make_prices(300, seed=44, name="SLV")
    r_csm = compute_commodity_basket_tsm_returns(
        {"USO": pxa, "UNG": pxb, "SLV": pxc},
        lookback=90, rf=0.02, cost_bps=5.0,
    )
    combined = combine_046_plus_csm(r_046, r_csm, w_046=1.0, w_csm=0.0)
    common = r_046.index.intersection(r_csm.index)
    np.testing.assert_allclose(combined.values, r_046.loc[common].values, atol=1e-12)


def test_combined_reduces_to_csm_when_w_046_zero():
    r_046 = _make_returns(300, seed=11)
    pxa = _make_prices(300, seed=22, name="USO")
    pxb = _make_prices(300, seed=33, name="UNG")
    pxc = _make_prices(300, seed=44, name="SLV")
    r_csm = compute_commodity_basket_tsm_returns(
        {"USO": pxa, "UNG": pxb, "SLV": pxc},
        lookback=90, rf=0.02, cost_bps=5.0,
    )
    combined = combine_046_plus_csm(r_046, r_csm, w_046=0.0, w_csm=1.0)
    common = r_046.index.intersection(r_csm.index)
    np.testing.assert_allclose(combined.values, r_csm.loc[common].values, atol=1e-12)


def test_combined_8020_is_correct_weighted_average():
    r_046 = _make_returns(300, seed=11)
    pxa = _make_prices(300, seed=22, name="USO")
    pxb = _make_prices(300, seed=33, name="UNG")
    pxc = _make_prices(300, seed=44, name="SLV")
    r_csm = compute_commodity_basket_tsm_returns(
        {"USO": pxa, "UNG": pxb, "SLV": pxc},
        lookback=90, rf=0.02, cost_bps=5.0,
    )
    combined = combine_046_plus_csm(r_046, r_csm, w_046=0.80, w_csm=0.20)
    common = r_046.index.intersection(r_csm.index)
    expected = 0.80 * r_046.loc[common] + 0.20 * r_csm.loc[common]
    np.testing.assert_allclose(combined.values, expected.values, atol=1e-12)


def test_combined_rejects_negative_weights():
    r_046 = _make_returns(100)
    pxa = _make_prices(100, seed=22, name="USO")
    r_csm = compute_commodity_basket_tsm_returns(
        {"USO": pxa}, lookback=30, rf=0.02, cost_bps=5.0,
    )
    with pytest.raises(ValueError):
        combine_046_plus_csm(r_046, r_csm, w_046=-0.1, w_csm=1.1)
    with pytest.raises(ValueError):
        combine_046_plus_csm(r_046, r_csm, w_046=1.1, w_csm=-0.1)


# ---------------------------------------------------------------------------
# 4. Cross-library parity (G7)
# ---------------------------------------------------------------------------


def test_numpy_single_asset_matches_pandas():
    px = _make_prices(300, seed=42, name="USO")
    pd_out = compute_single_asset_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    np_out = compute_single_asset_tsm_np(
        px.values, lookback=90, rf=0.02, cost_bps=5.0,
    )
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-12)


def test_numpy_basket_matches_pandas():
    """Basket numpy ref ≡ pandas basket on aligned input."""
    pxa = _make_prices(300, seed=11, name="USO")
    pxb = _make_prices(300, seed=22, name="UNG")
    pxc = _make_prices(300, seed=33, name="SLV")
    pd_basket = compute_commodity_basket_tsm_returns(
        {"USO": pxa, "UNG": pxb, "SLV": pxc},
        lookback=90, rf=0.02, cost_bps=5.0,
    )
    aligned = np.column_stack([pxa.values, pxb.values, pxc.values])
    np_basket = compute_commodity_basket_np(
        aligned, lookback=90, rf=0.02, cost_bps=5.0,
    )
    np.testing.assert_allclose(pd_basket.values, np_basket, atol=1e-12)


def test_basket_cagr_matches_within_3pp():
    """G7 spec — Δ CAGR ≤ 3pp between pandas and numpy basket."""
    pxa = _make_prices(300, seed=11, name="USO")
    pxb = _make_prices(300, seed=22, name="UNG")
    pxc = _make_prices(300, seed=33, name="SLV")
    pd_basket = compute_commodity_basket_tsm_returns(
        {"USO": pxa, "UNG": pxb, "SLV": pxc},
        lookback=90, rf=0.02, cost_bps=5.0,
    )
    aligned = np.column_stack([pxa.values, pxb.values, pxc.values])
    np_basket = compute_commodity_basket_np(
        aligned, lookback=90, rf=0.02, cost_bps=5.0,
    )
    eq_pd = np.cumprod(1.0 + pd_basket.values)
    eq_np = np.cumprod(1.0 + np_basket)
    n = len(eq_pd)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np_val = float(eq_np[-1]) ** (252.0 / n) - 1.0
    assert abs(cagr_pd - cagr_np_val) * 100.0 < 3.0


# ---------------------------------------------------------------------------
# 5. Lookback parameter validation
# ---------------------------------------------------------------------------


def test_invalid_lookback_raises():
    px = _make_prices(100, name="USO")
    with pytest.raises(ValueError):
        compute_single_asset_tsm_returns(px, lookback=0)
    with pytest.raises(ValueError):
        compute_commodity_basket_tsm_returns({"USO": px}, lookback=-5)
