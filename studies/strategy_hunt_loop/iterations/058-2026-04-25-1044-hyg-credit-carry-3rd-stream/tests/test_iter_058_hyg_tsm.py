"""TDD specs for iter 058 — HYG TSM 90d + iter 046 combo at w=0.10.

Mechanism: r_hyg_tsm[t] = pos[t] * r_hyg[t] + (1 - pos[t]) * rf_d - cost[t]
where pos[t] ∈ {0, 1} is computed from sign of (price[t-1] / price[t-1-L] - 1)
(no-lookahead 1-day shift).

Combined: r_combined[t] = w_046 * r_046[t] + w_hyg * r_hyg_tsm[t].

Citations
---------
* Asvanunt-Richardson 2017 JPM 43(2) — credit risk premium thesis.
* `[systematic_trading]` (Carver) — TSM rule (single-asset return-sign).
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from hyg_tsm import compute_hyg_tsm_returns  # noqa: E402
from numpy_reference_iter058 import compute_hyg_tsm_returns_np  # noqa: E402
from combined_046_plus_hyg import combine_046_plus_hyg  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_prices(n: int = 300, drift: float = 0.0002, seed: int = 7) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    rets = rng.normal(loc=drift, scale=0.008, size=n)
    return pd.Series(np.cumprod(1.0 + rets) * 90.0, index=idx, name="HYG")


def _make_returns(n: int = 300, seed: int = 11) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    return pd.Series(rng.normal(0.0005, 0.011, size=n), index=idx, name="r_046")


# ---------------------------------------------------------------------------
# 1. HYG TSM core engine
# ---------------------------------------------------------------------------


def test_hyg_tsm_returns_indexed_to_returns():
    """Output index = price.index[1:] (one bar lost to pct_change)."""
    px = _make_prices(120)
    out = compute_hyg_tsm_returns(px, lookback=90)
    assert len(out) == len(px) - 1
    assert out.index.equals(px.index[1:])


def test_hyg_tsm_warmup_period_is_cash():
    """First `lookback` bars have no signal yet → position = 0 (cash)."""
    px = _make_prices(150)
    out = compute_hyg_tsm_returns(px, lookback=90, rf=0.02)
    rf_d = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    np.testing.assert_allclose(
        out.iloc[:90].values, np.full(90, rf_d), atol=1e-12
    )


def test_hyg_tsm_always_long_when_uptrend():
    """Strictly increasing prices → after warmup, always long → returns ≈ HYG returns."""
    n = 200
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    px = pd.Series(np.cumprod(np.full(n, 1.003)) * 90.0, index=idx, name="HYG")
    out = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=0.0)
    np.testing.assert_allclose(out.iloc[90:].values, 0.003, atol=1e-9)


def test_hyg_tsm_always_cash_when_downtrend():
    """Strictly decreasing prices → after warmup, always cash → returns = rf_d."""
    n = 200
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    px = pd.Series(np.cumprod(np.full(n, 0.997)) * 90.0, index=idx, name="HYG")
    rf = 0.02
    out = compute_hyg_tsm_returns(px, lookback=90, rf=rf, cost_bps=0.0)
    rf_d = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    np.testing.assert_allclose(out.iloc[90:].values, rf_d, atol=1e-9)


def test_hyg_tsm_no_lookahead():
    """Position at t depends only on prices ≤ t-1 (signal computed on lagged data)."""
    n = 200
    px = _make_prices(n)
    out_full = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=0.0)
    px_modified = px.copy()
    px_modified.iloc[-1] = px.iloc[-1] * 2.0
    out_modified = compute_hyg_tsm_returns(px_modified, lookback=90, rf=0.02, cost_bps=0.0)
    np.testing.assert_array_equal(out_full.iloc[:-1].values, out_modified.iloc[:-1].values)


def test_hyg_tsm_cost_charged_on_position_change():
    """Cost in bps applied on |Δposition| (transition between long and cash)."""
    n = 250
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    arr = np.ones(n)
    arr[:n // 2] = 1.003
    arr[n // 2:] = 0.997
    prices = np.cumprod(arr) * 90.0
    px = pd.Series(prices, index=idx, name="HYG")
    out_with_cost = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    out_no_cost = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=0.0)
    diff = (out_no_cost - out_with_cost).sum()
    assert diff > 0
    assert 1e-5 < diff < 1e-2


# ---------------------------------------------------------------------------
# 2. Combined w_046=0.9 + w_hyg=0.1
# ---------------------------------------------------------------------------


def test_combined_reduces_to_iter046_when_w_hyg_zero():
    """w_046 = 1.0, w_hyg = 0.0 → combined == r_046 on the inner-join index."""
    r_046 = _make_returns(300, seed=11)
    px = _make_prices(300, seed=22)
    r_hyg = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    combined = combine_046_plus_hyg(r_046, r_hyg, w_046=1.0, w_hyg=0.0)
    common = r_046.index.intersection(r_hyg.index)
    np.testing.assert_allclose(combined.values, r_046.loc[common].values, atol=1e-12)


def test_combined_reduces_to_hyg_when_w_046_zero():
    """w_046 = 0.0, w_hyg = 1.0 → combined == r_hyg_tsm."""
    r_046 = _make_returns(300, seed=11)
    px = _make_prices(300, seed=22)
    r_hyg = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    combined = combine_046_plus_hyg(r_046, r_hyg, w_046=0.0, w_hyg=1.0)
    common = r_046.index.intersection(r_hyg.index)
    np.testing.assert_allclose(combined.values, r_hyg.loc[common].values, atol=1e-12)


def test_combined_w090_w010_is_correct_weighted_sum():
    """w_046 = 0.9, w_hyg = 0.1 → combined = 0.9*r_046 + 0.1*r_hyg."""
    r_046 = _make_returns(300, seed=11)
    px = _make_prices(300, seed=22)
    r_hyg = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    combined = combine_046_plus_hyg(r_046, r_hyg, w_046=0.9, w_hyg=0.1)
    common = r_046.index.intersection(r_hyg.index)
    expected = 0.9 * r_046.loc[common] + 0.1 * r_hyg.loc[common]
    np.testing.assert_allclose(combined.values, expected.values, atol=1e-12)


def test_combined_inner_joins_indexes():
    """Combined index is intersection of the two input indexes."""
    r_046 = _make_returns(300, seed=11)
    r_046 = r_046.iloc[10:200]
    px = _make_prices(300, seed=22)
    r_hyg = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    combined = combine_046_plus_hyg(r_046, r_hyg, w_046=0.9, w_hyg=0.1)
    expected_idx = r_046.index.intersection(r_hyg.index)
    assert combined.index.equals(expected_idx)


def test_combined_rejects_negative_weights():
    """Negative weights raise ValueError."""
    r_046 = _make_returns(100)
    px = _make_prices(100)
    r_hyg = compute_hyg_tsm_returns(px, lookback=30)
    with pytest.raises(ValueError):
        combine_046_plus_hyg(r_046, r_hyg, w_046=-0.1, w_hyg=1.1)
    with pytest.raises(ValueError):
        combine_046_plus_hyg(r_046, r_hyg, w_046=1.1, w_hyg=-0.1)


# ---------------------------------------------------------------------------
# 3. Cross-library parity (G7)
# ---------------------------------------------------------------------------


def test_numpy_reference_matches_pandas_engine():
    """Pure-numpy reference yields identical net returns to pandas engine."""
    px = _make_prices(300, seed=42)
    pd_out = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    np_out = compute_hyg_tsm_returns_np(
        px.values, lookback=90, rf=0.02, cost_bps=5.0,
    )
    assert len(pd_out) == len(np_out)
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-12)


def test_numpy_cagr_matches_pandas_to_within_3pp():
    """G7: cumulative CAGR difference between libs must be ≤ 3 pp."""
    px = _make_prices(300, seed=42)
    pd_out = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    np_out = compute_hyg_tsm_returns_np(
        px.values, lookback=90, rf=0.02, cost_bps=5.0,
    )
    eq_pd = np.cumprod(1.0 + pd_out.values)
    eq_np = np.cumprod(1.0 + np_out)
    n = len(eq_pd)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np_val = float(eq_np[-1]) ** (252.0 / n) - 1.0
    assert abs(cagr_pd - cagr_np_val) * 100.0 < 3.0


# ---------------------------------------------------------------------------
# 4. Lookback parameter validation
# ---------------------------------------------------------------------------


def test_invalid_lookback_raises():
    px = _make_prices(100)
    with pytest.raises(ValueError):
        compute_hyg_tsm_returns(px, lookback=0)
    with pytest.raises(ValueError):
        compute_hyg_tsm_returns(px, lookback=-5)


def test_lookback_longer_than_history_yields_all_cash():
    """If lookback >= n_returns, all bars are still in warmup → all cash."""
    px = _make_prices(100)
    rf = 0.02
    rf_d = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    out = compute_hyg_tsm_returns(px, lookback=99, rf=rf, cost_bps=0.0)
    np.testing.assert_allclose(out.values, rf_d, atol=1e-12)
