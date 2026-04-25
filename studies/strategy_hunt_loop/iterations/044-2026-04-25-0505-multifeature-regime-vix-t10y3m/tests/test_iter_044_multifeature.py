"""Iter 044 — TDD specs for multi-feature composite regime gate.

These specs MUST pass before the backtest runs (ensures engine is
correct before measurements). Mirrors iter 041/043 testing patterns.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ITER_DIR))

from multifeature_regime_gate import (  # noqa: E402
    apply_multifeature_regime_3leg,
    build_composite_regime,
    rolling_zscore,
)
from numpy_reference_multifeature import (  # noqa: E402
    apply_multifeature_regime_3leg_np,
    build_composite_regime_np,
    rolling_zscore_np,
)

CALM = {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40}
STRESS = {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55}


def _make_index(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2020-01-02", periods=n, freq="B")


def _make_returns(n: int, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = _make_index(n)
    df = pd.DataFrame(
        {
            "EQ":  rng.normal(0.0005, 0.012, n),
            "BD":  rng.normal(0.0001, 0.004, n),
            "GLD": rng.normal(0.0002, 0.010, n),
        },
        index=idx,
    )
    return df


# ---------------------------------------------------------------------------
# 1. rolling z-score causal expanding warm-up
# ---------------------------------------------------------------------------

def test_rolling_zscore_expanding_warmup():
    """For t < window-1, expanding window from index 0 to t+1."""
    s = pd.Series([10.0, 12.0, 14.0, 16.0, 18.0],
                  index=_make_index(5))
    z = rolling_zscore(s, window=10)
    # Bar 0 has window size 1 → no std → z=0
    assert z.iloc[0] == 0.0
    # Bar 1 has window [10, 12]: mean=11 std=1 → z = (12-11)/1 = 1.0
    assert z.iloc[1] == pytest.approx(1.0)
    # Bar 4 has window [10..18]: mean=14 std=sqrt(8)=2.828 → z=(18-14)/2.828
    assert z.iloc[4] == pytest.approx(4.0 / np.sqrt(8.0), rel=1e-9)


def test_rolling_zscore_pandas_numpy_parity():
    """Pandas + numpy rolling-zscore agree on the same input."""
    rng = np.random.default_rng(7)
    x = rng.normal(20.0, 5.0, 600)
    s = pd.Series(x, index=_make_index(600))
    z_pd = rolling_zscore(s, window=252)
    z_np = rolling_zscore_np(x, window=252)
    np.testing.assert_allclose(z_pd.to_numpy(), z_np, atol=1e-10)


# ---------------------------------------------------------------------------
# 2. causality / look-ahead
# ---------------------------------------------------------------------------

def test_regime_uses_only_past_features():
    """regime[t] must depend only on (vix, ts) bars [..., t-1].

    Mutating bar t of the inputs must NOT change regime[t] or any
    earlier regime label.
    """
    rng = np.random.default_rng(1)
    n = 400
    idx = _make_index(n)
    vix = pd.Series(rng.uniform(10, 30, n), index=idx)
    ts  = pd.Series(rng.uniform(-1, 3, n), index=idx)

    reg_a, _ = build_composite_regime(vix, ts, z_window=60)
    vix_b = vix.copy()
    vix_b.iloc[300] += 100.0  # massive perturbation at bar 300
    reg_b, _ = build_composite_regime(vix_b, ts, z_window=60)

    # bars 0..300 must be unchanged (regime at bar 300 uses ≤299 inputs)
    np.testing.assert_array_equal(
        reg_a.iloc[: 301].to_numpy(), reg_b.iloc[: 301].to_numpy(),
    )


def test_one_day_lag_exact():
    """Shifting BOTH features back by 1 day shifts regime trace by 1 day."""
    rng = np.random.default_rng(2)
    n = 400
    idx = _make_index(n)
    vix = pd.Series(rng.uniform(10, 30, n), index=idx)
    ts  = pd.Series(rng.uniform(-1, 3, n), index=idx)
    reg_a, _ = build_composite_regime(vix, ts, z_window=60, lag_days=1)
    reg_b, _ = build_composite_regime(vix, ts, z_window=60, lag_days=2)
    # lag=2 regime at bar t equals lag=1 regime at bar t-1
    # (excluding the initial bootstrap bar where the fallback kicks in)
    np.testing.assert_array_equal(
        reg_b.iloc[5:].to_numpy(), reg_a.iloc[4:-1].to_numpy(),
    )


# ---------------------------------------------------------------------------
# 3. identity reductions
# ---------------------------------------------------------------------------

def test_identity_reduction_when_only_vix_weight():
    """Setting feature_weights={vix:1, neg_t10y3m:0} reduces composite
    to a pure VIX z-score gate — independent of T10Y3M."""
    rng = np.random.default_rng(3)
    n = 500
    idx = _make_index(n)
    vix = pd.Series(rng.uniform(10, 30, n), index=idx)
    ts_a = pd.Series(rng.uniform(-1, 3, n), index=idx)
    ts_b = pd.Series(rng.uniform(-1, 3, n) + 5.0, index=idx)
    fw = {"vix": 1.0, "neg_t10y3m": 0.0}
    reg_a, _ = build_composite_regime(vix, ts_a, z_window=60, feature_weights=fw)
    reg_b, _ = build_composite_regime(vix, ts_b, z_window=60, feature_weights=fw)
    np.testing.assert_array_equal(reg_a.to_numpy(), reg_b.to_numpy())


def test_identity_reduction_when_calm_equals_stress():
    """When calm_weights == stress_weights, regime label has no effect."""
    rng = np.random.default_rng(4)
    n = 400
    rets = _make_returns(n, seed=4)
    vix = pd.Series(rng.uniform(10, 35, n), index=rets.index)
    ts  = pd.Series(rng.uniform(-1, 3, n), index=rets.index)
    same = {"eq_w": 0.7, "bd_w": 0.4, "gld_w": 0.4}
    net, _, _, _, _ = apply_multifeature_regime_3leg(
        rets["EQ"], rets["BD"], rets["GLD"], vix, ts,
        calm_weights=same, stress_weights=same,
    )
    # Should equal the static stack net returns (within float rounding)
    expected_gross = (
        same["eq_w"] * rets["EQ"]
        + same["bd_w"] * rets["BD"]
        + same["gld_w"] * rets["GLD"]
    )
    # No leg flips → no turnover beyond the bar-0 ramp-up cost
    diff = (net - expected_gross).abs()
    # All bars after bar 0 should have zero turnover → diff = 0
    assert diff.iloc[1:].max() < 1e-12


# ---------------------------------------------------------------------------
# 4. cost accounting
# ---------------------------------------------------------------------------

def test_cost_equals_turnover_times_bps():
    """Sum cost over all bars equals sum |Δposition| * cost_bps_per_leg."""
    rng = np.random.default_rng(5)
    n = 300
    rets = _make_returns(n, seed=5)
    # Construct VIX/TS that flip composite multiple times
    vix = pd.Series(np.linspace(15, 30, n) + rng.normal(0, 3, n),
                    index=rets.index)
    ts  = pd.Series(np.linspace(2, -1, n) + rng.normal(0, 0.5, n),
                    index=rets.index)
    cost_bps = 0.0005
    net, positions, _, _, _ = apply_multifeature_regime_3leg(
        rets["EQ"], rets["BD"], rets["GLD"], vix, ts,
        calm_weights=CALM, stress_weights=STRESS,
        cost_bps_per_leg=cost_bps, z_window=60,
    )
    gross = (
        positions["EQ"] * rets["EQ"]
        + positions["BD"] * rets["BD"]
        + positions["GLD"] * rets["GLD"]
    )
    cost_implied = (gross - net).sum()
    dpos_eq = positions["EQ"].diff().abs().fillna(positions["EQ"].iloc[0])
    dpos_bd = positions["BD"].diff().abs().fillna(positions["BD"].iloc[0])
    dpos_gld = positions["GLD"].diff().abs().fillna(positions["GLD"].iloc[0])
    cost_expected = (dpos_eq + dpos_bd + dpos_gld).sum() * cost_bps
    assert abs(cost_implied - cost_expected) < 1e-10


# ---------------------------------------------------------------------------
# 5. regime → weights mapping
# ---------------------------------------------------------------------------

def test_regime_to_weights_mapping_is_binary():
    """positions[t] equals calm_weights iff regime[t]=1 else stress."""
    rng = np.random.default_rng(6)
    n = 300
    rets = _make_returns(n, seed=6)
    vix = pd.Series(rng.uniform(10, 35, n), index=rets.index)
    ts  = pd.Series(rng.uniform(-1, 3, n), index=rets.index)
    _, positions, _, regime, _ = apply_multifeature_regime_3leg(
        rets["EQ"], rets["BD"], rets["GLD"], vix, ts,
        calm_weights=CALM, stress_weights=STRESS, z_window=60,
    )
    calm_mask = regime == 1
    assert (positions.loc[calm_mask, "EQ"] == CALM["eq_w"]).all()
    assert (positions.loc[calm_mask, "BD"] == CALM["bd_w"]).all()
    assert (positions.loc[calm_mask, "GLD"] == CALM["gld_w"]).all()
    stress_mask = regime == 0
    assert (positions.loc[stress_mask, "EQ"] == STRESS["eq_w"]).all()
    assert (positions.loc[stress_mask, "BD"] == STRESS["bd_w"]).all()
    assert (positions.loc[stress_mask, "GLD"] == STRESS["gld_w"]).all()


# ---------------------------------------------------------------------------
# 6. Pandas vs numpy parity
# ---------------------------------------------------------------------------

def test_pandas_numpy_engine_parity():
    """Net returns from pandas engine and numpy reference must match."""
    rng = np.random.default_rng(7)
    n = 800
    rets = _make_returns(n, seed=7)
    vix = pd.Series(rng.uniform(10, 35, n), index=rets.index)
    ts  = pd.Series(rng.uniform(-1, 3, n), index=rets.index)
    net_pd, _, _, regime_pd, _ = apply_multifeature_regime_3leg(
        rets["EQ"], rets["BD"], rets["GLD"], vix, ts,
        calm_weights=CALM, stress_weights=STRESS, z_window=120,
    )
    regime_np, _ = build_composite_regime_np(
        vix.to_numpy(), ts.to_numpy(), z_window=120,
    )
    np.testing.assert_array_equal(regime_pd.to_numpy(), regime_np)
    net_np, _, _ = apply_multifeature_regime_3leg_np(
        rets["EQ"].to_numpy(),
        rets["BD"].to_numpy(),
        rets["GLD"].to_numpy(),
        regime_np,
        calm_weights=CALM, stress_weights=STRESS,
    )
    np.testing.assert_allclose(net_pd.to_numpy(), net_np, atol=1e-12)


# ---------------------------------------------------------------------------
# 7. Composite symmetry — swapping (feature, weight) leaves regime unchanged
# ---------------------------------------------------------------------------

def test_composite_swap_invariance():
    """Swapping feature labels while applying corresponding swap on
    weights must leave regime unchanged. Concretely, if VIX and -T10Y3M
    are swapped via injecting the same array under both names, weights
    can be permuted freely without touching the gate."""
    rng = np.random.default_rng(8)
    n = 400
    idx = _make_index(n)
    same = pd.Series(rng.normal(0, 1, n), index=idx)
    fw_a = {"vix": 0.7, "neg_t10y3m": 0.3}
    fw_b = {"vix": 0.3, "neg_t10y3m": 0.7}
    # When VIX==-T10Y3M (so z(VIX) = z(-(-VIX)) = z(VIX) = z(-T10Y3M) since T = -VIX)
    vix = same
    ts  = -same  # so -T10Y3M = same → z_neg_T = z_vix exactly
    reg_a, _ = build_composite_regime(vix, ts, z_window=60, feature_weights=fw_a)
    reg_b, _ = build_composite_regime(vix, ts, z_window=60, feature_weights=fw_b)
    np.testing.assert_array_equal(reg_a.to_numpy(), reg_b.to_numpy())


# ---------------------------------------------------------------------------
# 8. Threshold monotonicity — raising τ shrinks the stress count
# ---------------------------------------------------------------------------

def test_threshold_monotonicity():
    """Higher stress_threshold → fewer (or equal) stress bars."""
    rng = np.random.default_rng(9)
    n = 600
    idx = _make_index(n)
    vix = pd.Series(rng.uniform(10, 40, n), index=idx)
    ts  = pd.Series(rng.uniform(-1, 3, n), index=idx)
    counts = []
    for tau in [-2.0, -1.0, 0.0, 1.0, 2.0]:
        reg, _ = build_composite_regime(
            vix, ts, z_window=120, stress_threshold=tau,
        )
        counts.append(int((reg == 0).sum()))
    # As τ rises, stress count must be monotonically non-increasing
    for i in range(len(counts) - 1):
        assert counts[i] >= counts[i + 1], (
            f"stress count not monotone with tau: {counts}"
        )


# ---------------------------------------------------------------------------
# 9. Sanity: with all-zero composite, regime is all-stress (τ=0)
# ---------------------------------------------------------------------------

def test_all_zero_composite_at_tau_zero():
    """When VIX and TS are constant (composite z = 0 everywhere) and
    τ=0, the gate condition `s < 0` is FALSE everywhere → all stress."""
    n = 100
    idx = _make_index(n)
    vix = pd.Series(20.0, index=idx)
    ts  = pd.Series(1.5, index=idx)
    reg, _ = build_composite_regime(vix, ts, z_window=20, stress_threshold=0.0)
    assert (reg == 0).all()


# ---------------------------------------------------------------------------
# 10. Net returns are deterministic given inputs
# ---------------------------------------------------------------------------

def test_deterministic_net_returns():
    """Two runs with identical inputs produce identical outputs."""
    rng = np.random.default_rng(10)
    n = 500
    rets = _make_returns(n, seed=10)
    vix = pd.Series(rng.uniform(10, 35, n), index=rets.index)
    ts  = pd.Series(rng.uniform(-1, 3, n), index=rets.index)
    net1, _, _, _, _ = apply_multifeature_regime_3leg(
        rets["EQ"], rets["BD"], rets["GLD"], vix, ts,
        calm_weights=CALM, stress_weights=STRESS, z_window=120,
    )
    net2, _, _, _, _ = apply_multifeature_regime_3leg(
        rets["EQ"], rets["BD"], rets["GLD"], vix, ts,
        calm_weights=CALM, stress_weights=STRESS, z_window=120,
    )
    np.testing.assert_allclose(net1.to_numpy(), net2.to_numpy(), atol=0.0)
