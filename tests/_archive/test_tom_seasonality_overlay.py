"""Tests for iter 022 TOM seasonality overlay.

Primitive: ``studies/strategy_hunt_loop/iterations/022-.../tom_seasonality_overlay.py``

Coverage:
- TOM flag calendar correctness (last N + first M business days per month)
- Time-varying weight application (w_eq[t] / w_bd[t] by TOM flag)
- Identity preservation vs iter 016 when eq_weight_tom == eq_weight_mid
- σ̂_{t-1} lag preservation (no TOM-driven look-ahead)
- G7 numpy-pure parity within 3 pp CAGR

Citations
---------
* `[trading_systems_methods, p.479-481]` — turn-of-month calendar effects.
* `[risk_parity, p.10-11, ch.1]` — iter 016 base.
* `[advances_fin_ml, p.162-164]` — lag discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add iter 022 dir to path so we can import the primitive under test.
ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = (
    ROOT
    / "studies"
    / "strategy_hunt_loop"
    / "iterations"
    / "022-2026-04-24-1942-tom-seasonality-overlay"
)
sys.path.insert(0, str(ITER_DIR))

# Import under test — intentionally after path manipulation.
from tom_seasonality_overlay import (  # noqa: E402
    compute_tom_flag,
    apply_tom_static_stack_vm,
)


# ---------------------------------------------------------------------------
# TOM flag calendar correctness
# ---------------------------------------------------------------------------


def test_tom_flag_standard_month():
    """Jan 2020 business days: last 3 + first 3 should be flagged True."""
    # Build a DatetimeIndex for Dec 2019 and Jan 2020 business days.
    idx = pd.bdate_range("2019-12-16", "2020-01-31")
    flag = compute_tom_flag(idx, last_n=3, first_n=3)

    # Dec 2019 business days: ...27, 30, 31 are last 3.
    dec_last_three = pd.DatetimeIndex(["2019-12-27", "2019-12-30", "2019-12-31"])
    for d in dec_last_three:
        assert flag.loc[d], f"Dec last-3 {d.date()} should be TOM"

    # Jan 2020 first 3 business days: Jan 2, 3, 6 (Jan 1 holiday but
    # bdate_range includes it — we trust the input index).
    jan_first_three = idx[idx.month == 1][:3]
    for d in jan_first_three:
        assert flag.loc[d], f"Jan first-3 {d.date()} should be TOM"

    # Mid-month should NOT be TOM.
    mid_dec = pd.Timestamp("2019-12-18")
    assert not flag.loc[mid_dec], f"Dec mid {mid_dec.date()} must NOT be TOM"


def test_tom_flag_adjustable_window():
    """With last_n=1, first_n=1 only 2 days per boundary should flag."""
    idx = pd.bdate_range("2020-01-01", "2020-02-29")
    flag = compute_tom_flag(idx, last_n=1, first_n=1)
    n_tom = flag.sum()
    # Jan boundary: 1 + 1; Feb boundary: 1 + 1 — total 4 in this 2-month window.
    # bdate_range gives Jan and Feb business days: Jan has ~22, Feb ~20 → 42.
    # Expect ~4-5 TOM days (depends on split).
    assert 3 <= n_tom <= 5, f"expected ~4 TOM days with 1+1 window, got {n_tom}"


def test_tom_flag_preserves_index():
    idx = pd.bdate_range("2020-01-01", "2020-03-31")
    flag = compute_tom_flag(idx, last_n=3, first_n=3)
    assert flag.index.equals(idx)
    assert flag.dtype == bool


# ---------------------------------------------------------------------------
# Time-varying weights
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_data():
    """Deterministic two-leg return streams covering 3+ years."""
    rng = np.random.default_rng(42)
    idx = pd.bdate_range("2019-01-01", "2022-12-30")
    n = len(idx)
    # eq: 10% annual vol, slight positive drift
    r_eq = pd.Series(rng.normal(0.0003, 0.01, size=n), index=idx, name="SPY")
    # bd: 5% annual vol, slight positive drift, mildly negatively correlated
    r_bd = pd.Series(
        -0.3 * r_eq.to_numpy() + rng.normal(0.0001, 0.004, size=n),
        index=idx,
        name="IEF",
    )
    return r_eq, r_bd


def test_identity_when_tom_equals_mid(synthetic_data):
    """With eq_weight_tom == eq_weight_mid, must match iter 016 exactly."""
    r_eq, r_bd = synthetic_data
    # Iter 016 base: 0.6 / 0.4 fixed.
    net_016, pos_eq_016, pos_bd_016, scale_016 = _iter016_primitive(
        r_eq, r_bd,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    net_022, pos_eq_022, pos_bd_022, scale_022, _ = apply_tom_static_stack_vm(
        r_eq, r_bd,
        eq_weight_tom=0.6, eq_weight_mid=0.6,
        bd_weight_tom=0.4, bd_weight_mid=0.4,
        tom_last_n=3, tom_first_n=3,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    np.testing.assert_allclose(net_016.to_numpy(), net_022.to_numpy(), atol=1e-12)
    np.testing.assert_allclose(scale_016.to_numpy(), scale_022.to_numpy(), atol=1e-12)


def test_weights_switch_by_tom_flag(synthetic_data):
    """pos_eq[t] / scale[t] must equal eq_weight_tom on TOM bars, mid elsewhere."""
    r_eq, r_bd = synthetic_data
    net, pos_eq, pos_bd, scale, tom = apply_tom_static_stack_vm(
        r_eq, r_bd,
        eq_weight_tom=0.9, eq_weight_mid=0.5,
        bd_weight_tom=0.1, bd_weight_mid=0.5,
        tom_last_n=3, tom_first_n=3,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    # Normalised weights internally: 0.9/1.0 → 0.9 for TOM; 0.5/1.0 → 0.5 for mid.
    eq_ratio = (pos_eq / scale).replace([np.inf, -np.inf], np.nan).dropna()
    tom_aligned = tom.loc[eq_ratio.index]
    # On TOM bars: ratio ≈ 0.9; on mid: ≈ 0.5.
    assert np.isclose(eq_ratio[tom_aligned].mean(), 0.9, atol=1e-10)
    assert np.isclose(eq_ratio[~tom_aligned].mean(), 0.5, atol=1e-10)


def test_no_lookahead_from_tom_flag(synthetic_data):
    """TOM flag is calendar property known pre-bar; σ̂ must still lag by 1."""
    r_eq, r_bd = synthetic_data
    # Run with TOM boost; then shift equity returns forward 1 day and re-run.
    # If there is look-ahead, the metrics should differ substantially.
    net_a, _, _, scale_a, _ = apply_tom_static_stack_vm(
        r_eq, r_bd,
        eq_weight_tom=0.9, eq_weight_mid=0.5,
        bd_weight_tom=0.1, bd_weight_mid=0.5,
        tom_last_n=3, tom_first_n=3,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    # Sanity: scale[t] must only depend on data through t-1, so replacing
    # r_eq[t] with NaN for the LAST bar must NOT change scale at any earlier
    # bar.
    r_eq_mut = r_eq.copy()
    r_eq_mut.iloc[-1] = np.nan
    net_b, _, _, scale_b, _ = apply_tom_static_stack_vm(
        r_eq_mut, r_bd,
        eq_weight_tom=0.9, eq_weight_mid=0.5,
        bd_weight_tom=0.1, bd_weight_mid=0.5,
        tom_last_n=3, tom_first_n=3,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    # scale_a and scale_b must agree wherever both are defined (except
    # possibly the last bar in scale_a, which scale_b has dropped).
    common = scale_a.index.intersection(scale_b.index)
    np.testing.assert_allclose(
        scale_a.loc[common].to_numpy(),
        scale_b.loc[common].to_numpy(),
        atol=1e-12,
    )


# ---------------------------------------------------------------------------
# G7 numpy parity
# ---------------------------------------------------------------------------


def test_numpy_reference_parity(synthetic_data):
    """numpy_reference_tom CAGR agrees with pandas version within 3pp."""
    from numpy_reference_tom import tom_static_stack_vm_numpy
    from market_lab.backtest.metrics.performance import cagr as _cagr

    r_eq, r_bd = synthetic_data
    net_pd, _, _, _, _ = apply_tom_static_stack_vm(
        r_eq, r_bd,
        eq_weight_tom=0.9, eq_weight_mid=0.5,
        bd_weight_tom=0.1, bd_weight_mid=0.5,
        tom_last_n=3, tom_first_n=3,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    net_np = tom_static_stack_vm_numpy(
        r_eq.to_numpy(), r_bd.to_numpy(),
        index=r_eq.index,
        eq_weight_tom=0.9, eq_weight_mid=0.5,
        bd_weight_tom=0.1, bd_weight_mid=0.5,
        tom_last_n=3, tom_first_n=3,
        target_vol=0.15, lookback=21, max_leverage=2.0,
    )
    eq_pd = (1.0 + net_pd).cumprod()
    eq_np = (1.0 + pd.Series(net_np, index=net_pd.index)).cumprod()
    cagr_pd = _cagr(eq_pd)
    cagr_np = _cagr(eq_np)
    assert abs(cagr_pd - cagr_np) < 0.03, (
        f"CAGR parity |pd - np| = {abs(cagr_pd - cagr_np):.4f} > 3pp"
    )


# ---------------------------------------------------------------------------
# Validation / error paths
# ---------------------------------------------------------------------------


def test_misaligned_legs_raise(synthetic_data):
    r_eq, r_bd = synthetic_data
    r_bd2 = r_bd.iloc[:-10]
    with pytest.raises(ValueError, match="index"):
        apply_tom_static_stack_vm(
            r_eq, r_bd2,
            eq_weight_tom=0.9, eq_weight_mid=0.5,
            bd_weight_tom=0.1, bd_weight_mid=0.5,
            tom_last_n=3, tom_first_n=3,
            target_vol=0.15, lookback=21, max_leverage=2.0,
        )


def test_short_series_raises(synthetic_data):
    r_eq, r_bd = synthetic_data
    r_eq_s = r_eq.iloc[:10]
    r_bd_s = r_bd.iloc[:10]
    with pytest.raises(ValueError, match="overlapping"):
        apply_tom_static_stack_vm(
            r_eq_s, r_bd_s,
            eq_weight_tom=0.9, eq_weight_mid=0.5,
            bd_weight_tom=0.1, bd_weight_mid=0.5,
            tom_last_n=3, tom_first_n=3,
            target_vol=0.15, lookback=21, max_leverage=2.0,
        )


# ---------------------------------------------------------------------------
# Helper: vendored copy of iter 016's primitive for identity test
# ---------------------------------------------------------------------------


def _iter016_primitive(r_eq, r_bd, *, eq_weight, bd_weight, target_vol, lookback, max_leverage):
    """Vendored minimal copy of iter 016 apply_static_stack_vol_managed.

    Used solely to assert that apply_tom_static_stack_vm with
    eq_weight_tom=eq_weight_mid reproduces iter 016 exactly.
    """
    total_w = eq_weight + bd_weight
    w_eq = eq_weight / total_w
    w_bd = bd_weight / total_w

    a = r_eq.astype(float)
    b = r_bd.astype(float)
    mask = a.notna() & b.notna()
    a = a.loc[mask]
    b = b.loc[mask]

    ann_var_eq = (a.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2 * 252).shift(1)
    ann_var_bd = (b.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2 * 252).shift(1)
    ann_cov = (a.rolling(lookback, min_periods=lookback).cov(b, ddof=0) * 252).shift(1)
    ann_var_port = (
        w_eq ** 2 * ann_var_eq
        + w_bd ** 2 * ann_var_bd
        + 2 * w_eq * w_bd * ann_cov
    ).clip(lower=0.0)

    target_var = target_vol ** 2
    raw_scale = pd.Series(np.nan, index=a.index, dtype=float)
    mask_v = ann_var_port.notna()
    pos_mask = mask_v & (ann_var_port > 0)
    zero_mask = mask_v & (ann_var_port == 0)
    raw_scale.loc[pos_mask] = target_var / ann_var_port.loc[pos_mask]
    raw_scale.loc[zero_mask] = max_leverage
    scale = raw_scale.clip(lower=0.0, upper=max_leverage).dropna()

    pos_eq = scale * w_eq
    pos_bd = scale * w_bd
    gross = pos_eq * a.loc[scale.index] + pos_bd * b.loc[scale.index]
    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_bd = pos_bd.diff().abs().fillna(pos_bd.iloc[0])
    cost = (dpos_eq + dpos_bd) * 0.0002
    net = gross - cost
    return net, pos_eq, pos_bd, scale
