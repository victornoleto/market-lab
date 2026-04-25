"""TDD specs for iter 073 — Gayed-MA gate × vol-managed stack.

Specs verify (i) weight invariants on/off market, (ii) no-peek shift(1)
on both σ²_{t-1} and SMA_{t-1}, (iii) cost accounting linear in
Σ|Δpos|, (iv) cfg-collapse to iter 016 when gate_on always True,
(v) cfg-collapse to 100% bond when gate_on always False, (vi) gate
fraction in plausible range on real data, (vii) cross-library numpy
parity, (viii) ma_period parameter behaviour.

Citations
---------
* `[advances_fin_ml, p.162-164]` — strict shift(1) on signal (no peek).
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
* `[leverage_for_the_long_run, p.16]` — 200-day SMA as canonical.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "073-2026-04-25-1659-gayed-ma-gate-on-iter016"
sys.path.insert(0, str(ITER_DIR))

from gayed_gate_stack import apply_gayed_gate_stack  # noqa: E402
from numpy_reference_gayed import apply_gayed_gate_stack_np  # noqa: E402


# ---------------------------------------------------------------------------
# Synthetic data fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synth_data() -> tuple[pd.Series, pd.Series, pd.Series]:
    """Build a deterministic 800-bar synthetic series with a clear regime
    shift around bar 400 (bull → bear → recovery)."""
    rng = np.random.default_rng(7)
    n = 800
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    # Regime 1: bull (mean +0.0005, σ 0.008) for 400 bars
    # Regime 2: bear (mean -0.0008, σ 0.020) for 200 bars
    # Regime 3: recovery (mean +0.0006, σ 0.010) for 200 bars
    r_eq = np.concatenate([
        rng.normal(0.0005, 0.008, 400),
        rng.normal(-0.0008, 0.020, 200),
        rng.normal(0.0006, 0.010, 200),
    ])
    r_bd = np.concatenate([
        rng.normal(0.0001, 0.003, 400),
        rng.normal(0.0004, 0.005, 200),  # safe-haven rally
        rng.normal(0.0002, 0.004, 200),
    ])
    px_eq = (1.0 + pd.Series(r_eq, index=idx)).cumprod() * 100.0
    return (
        pd.Series(r_eq, index=idx, name="r_eq"),
        pd.Series(r_bd, index=idx, name="r_bd"),
        px_eq,
    )


@pytest.fixture
def real_spy_data() -> tuple[pd.Series, pd.Series, pd.Series]:
    """Real Tiingo SPY+IEF returns + price for the iter 016 spy_real
    window. Used by the gate-fraction-in-plausible-range and cross-lib
    parity specs."""
    spy = pd.read_parquet(ROOT / "data" / "tiingo" / "daily" / "prices" / "SPY.parquet")
    ief = pd.read_parquet(ROOT / "data" / "tiingo" / "daily" / "prices" / "IEF.parquet")
    p_eq = spy["adj_close"]
    p_bd = ief["adj_close"]
    df = pd.concat({"eq": p_eq, "bd": p_bd}, axis=1, join="inner").dropna()
    df = df.loc["2009-06-25":"2026-04-15"]
    r = df.pct_change().dropna()
    px = df["eq"].loc[r.index]
    return r["eq"].rename("r_eq"), r["bd"].rename("r_bd"), px.rename("px_eq")


# ---------------------------------------------------------------------------
# 1. Weight invariants: on-market & off-market
# ---------------------------------------------------------------------------


def test_off_market_weights_sum_to_one(synth_data):
    r_eq, r_bd, px_eq = synth_data
    net, pos_eq, pos_bd, scale, gate_on = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.18, lookback=21, max_leverage=2.5,
        ma_period=200,
    )
    off_bars = ~gate_on
    assert off_bars.sum() > 0, "synthetic data should produce off-market bars"
    sums_off = (pos_eq + pos_bd).loc[off_bars]
    assert (sums_off == 1.0).all(), "off-market gross exposure must be exactly 1.0"
    # And equity must be exactly zero off-market.
    assert (pos_eq.loc[off_bars] == 0.0).all()


def test_on_market_weights_respect_max_leverage(synth_data):
    r_eq, r_bd, px_eq = synth_data
    max_lev = 2.5
    _, pos_eq, pos_bd, scale, gate_on = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq,
        eq_weight=0.6, bd_weight=0.4,
        target_vol=0.18, lookback=21, max_leverage=max_lev,
        ma_period=200,
    )
    on_bars = gate_on
    sums_on = (pos_eq + pos_bd).loc[on_bars]
    assert (sums_on <= max_lev + 1e-12).all()
    assert (sums_on == scale.loc[on_bars]).all()  # on-market exposure equals scale


# ---------------------------------------------------------------------------
# 2. No-peek discipline (shift(1) on both σ² and SMA)
# ---------------------------------------------------------------------------


def test_gate_uses_lagged_price_only(synth_data):
    r_eq, r_bd, px_eq = synth_data
    # Inject a gigantic positive return at the LAST bar — gate at the same
    # bar must NOT see it, since the gate is computed off price[t-1].
    px_eq_corrupted = px_eq.copy()
    px_eq_corrupted.iloc[-1] = px_eq_corrupted.iloc[-1] * 100.0
    _, _, _, _, gate_clean = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq,
        eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    _, _, _, _, gate_corrupt = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq_corrupted,
        eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    # All bars except possibly the FINAL one must match (last bar's
    # corrupted price never reaches a gate decision because shift(1)
    # would only feed it to t = len + 1).
    pd.testing.assert_series_equal(gate_clean, gate_corrupt)


def test_scale_uses_lagged_variance_only(synth_data):
    r_eq, r_bd, px_eq = synth_data
    # Inject a giant return at last bar — scale at that bar must not see it.
    r_eq_corrupted = r_eq.copy()
    r_eq_corrupted.iloc[-1] = 5.0
    _, _, _, scale_clean, _ = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq,
        eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    _, _, _, scale_corrupt, _ = apply_gayed_gate_stack(
        r_eq_corrupted, r_bd, px_eq,
        eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    pd.testing.assert_series_equal(scale_clean, scale_corrupt)


# ---------------------------------------------------------------------------
# 3. Cost accounting
# ---------------------------------------------------------------------------


def test_cost_linear_in_position_change(synth_data):
    r_eq, r_bd, px_eq = synth_data
    cost_a = 0.0001  # 1 bp
    cost_b = 0.0002  # 2 bp
    net_a, pos_eq_a, pos_bd_a, _, _ = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq, eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
        cost_bps_per_leg=cost_a,
    )
    net_b, pos_eq_b, pos_bd_b, _, _ = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq, eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
        cost_bps_per_leg=cost_b,
    )
    # Same position trajectory regardless of cost.
    pd.testing.assert_series_equal(pos_eq_a, pos_eq_b)
    pd.testing.assert_series_equal(pos_bd_a, pos_bd_b)
    # Cost difference equals (cost_b - cost_a) × Σ|Δpos|.
    dpos_eq = pos_eq_a.diff().abs().fillna(pos_eq_a.iloc[0])
    dpos_bd = pos_bd_a.diff().abs().fillna(pos_bd_a.iloc[0])
    expected_cost_diff = (dpos_eq + dpos_bd) * (cost_b - cost_a)
    actual_cost_diff = net_a - net_b
    np.testing.assert_allclose(
        actual_cost_diff.values, expected_cost_diff.values, atol=1e-12,
    )


# ---------------------------------------------------------------------------
# 4. Cfg collapses
# ---------------------------------------------------------------------------


def test_collapse_gate_always_on_recovers_iter016(synth_data):
    """When gate_on ≡ True, iter 073 must reproduce iter 016 exactly."""
    r_eq, r_bd, px_eq = synth_data
    # Force gate_on ≡ True by feeding a monotonically rising price.
    n = len(r_eq)
    px_rising = pd.Series(
        np.linspace(100.0, 1000.0, n), index=r_eq.index, name="px_eq",
    )
    net073, pos_eq073, pos_bd073, scale073, gate073 = apply_gayed_gate_stack(
        r_eq, r_bd, px_rising, eq_weight=0.6, bd_weight=0.4,
        target_vol=0.18, lookback=21, max_leverage=2.5, ma_period=200,
    )
    assert gate073.all(), "with monotone-rising price, gate_on must be ≡ True"

    # Compare to iter 016 directly.
    sys.path.insert(
        0,
        str(ROOT / "studies" / "strategy_hunt_loop" / "iterations"
            / "016-2026-04-24-1729-static-stack-vm-hybrid"),
    )
    from static_stack_vm import apply_static_stack_vol_managed  # noqa: E402

    net016, pos_eq016, pos_bd016, scale016 = apply_static_stack_vol_managed(
        r_eq, r_bd, eq_weight=0.6, bd_weight=0.4,
        target_vol=0.18, lookback=21, max_leverage=2.5,
    )
    common = scale073.index.intersection(scale016.index)
    # Skip the FIRST bar of iter 073's stream: iter 073's longer
    # warm-up (200 vs 21 bars) makes bar 200 a "first bar" for the
    # cost diff (charges full turn-on cost = pos_eq[0]), whereas
    # iter 016 sees that same bar as a regular bar with diff vs
    # bar 199. Bars 201+ are identical to within fp noise.
    common_skip_first = common[1:]
    np.testing.assert_allclose(
        net073.loc[common_skip_first].values,
        net016.loc[common_skip_first].values,
        atol=1e-12,
    )


def test_collapse_gate_always_off_yields_pure_bond(synth_data):
    """When gate_on ≡ False, iter 073 must equal pure r_bd minus
    one-time turn-on cost."""
    r_eq, r_bd, px_eq = synth_data
    n = len(r_eq)
    px_falling = pd.Series(
        np.linspace(1000.0, 100.0, n), index=r_eq.index, name="px_eq",
    )
    net073, pos_eq073, pos_bd073, scale073, gate073 = apply_gayed_gate_stack(
        r_eq, r_bd, px_falling, eq_weight=0.6, bd_weight=0.4,
        target_vol=0.18, lookback=21, max_leverage=2.5, ma_period=200,
    )
    assert (~gate073).all(), "with monotone-falling price, gate_on must be ≡ False"
    # Off-market: pos_eq = 0, pos_bd = 1 → daily return = r_bd
    # First bar pays a 1.0 bond turn-on cost (Δpos_bd = 1 from zero baseline).
    bd_v = r_bd.loc[scale073.index]
    cost = pd.Series(0.0, index=scale073.index)
    cost.iloc[0] = 1.0 * 0.0002  # cost_bps_per_leg default
    expected = bd_v - cost
    np.testing.assert_allclose(net073.values, expected.values, atol=1e-12)


# ---------------------------------------------------------------------------
# 5. Gate fraction in plausible range
# ---------------------------------------------------------------------------


def test_gate_fraction_in_range_real_spy(real_spy_data):
    r_eq, r_bd, px_eq = real_spy_data
    _, _, _, _, gate_on = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq, eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    frac_on = float(gate_on.mean())
    # Gayed (2016): SPY > SMA(200) ~70-80% of bars during expansions
    # since 1928, ~60-70% in this post-GFC bull window. The spec
    # demands [0.55, 0.92].
    assert 0.55 <= frac_on <= 0.92, f"gate-on fraction {frac_on:.3f} out of plausible range"


# ---------------------------------------------------------------------------
# 6. Cross-library parity (G7 echo)
# ---------------------------------------------------------------------------


def test_pandas_numpy_parity_synth(synth_data):
    r_eq, r_bd, px_eq = synth_data
    net_pd, pos_eq_pd, pos_bd_pd, scale_pd, gate_pd = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq, eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    net_np, pos_eq_np, pos_bd_np, scale_np, gate_np = apply_gayed_gate_stack_np(
        r_eq.to_numpy(), r_bd.to_numpy(), px_eq.to_numpy(),
        eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    np.testing.assert_allclose(net_pd.values, net_np, atol=1e-9)
    np.testing.assert_allclose(pos_eq_pd.values, pos_eq_np, atol=1e-12)
    np.testing.assert_allclose(pos_bd_pd.values, pos_bd_np, atol=1e-12)
    np.testing.assert_allclose(scale_pd.values, scale_np, atol=1e-12)
    np.testing.assert_array_equal(gate_pd.values, gate_np)


def test_pandas_numpy_parity_real_spy(real_spy_data):
    r_eq, r_bd, px_eq = real_spy_data
    net_pd, _, _, _, _ = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq, eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    net_np, _, _, _, _ = apply_gayed_gate_stack_np(
        r_eq.to_numpy(), r_bd.to_numpy(), px_eq.to_numpy(),
        eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    np.testing.assert_allclose(net_pd.values, net_np, atol=1e-9)


# ---------------------------------------------------------------------------
# 7. ma_period parameter behaviour
# ---------------------------------------------------------------------------


def test_ma_period_50_yields_more_flips_than_200(real_spy_data):
    """Shorter MA → more regime flips (Gayed [p.14])."""
    r_eq, r_bd, px_eq = real_spy_data
    _, _, _, _, gate_50 = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq, eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=50,
    )
    _, _, _, _, gate_200 = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq, eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    flips_50 = int(gate_50.astype(int).diff().abs().fillna(0).sum())
    flips_200 = int(gate_200.astype(int).diff().abs().fillna(0).sum())
    assert flips_50 > flips_200


def test_invalid_ma_period_raises():
    rng = np.random.default_rng(0)
    n = 300
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_eq = pd.Series(rng.normal(0.0005, 0.01, n), index=idx)
    r_bd = pd.Series(rng.normal(0.0001, 0.003, n), index=idx)
    px = (1.0 + r_eq).cumprod() * 100.0
    with pytest.raises(ValueError):
        apply_gayed_gate_stack(
            r_eq, r_bd, px, eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
            lookback=21, max_leverage=2.5, ma_period=1,
        )


def test_warmup_drops_correct_number_of_bars(synth_data):
    """Warm-up dropped = max(lookback, ma_period) + 1 bars."""
    r_eq, r_bd, px_eq = synth_data
    n = len(r_eq)
    net, _, _, _, gate_on = apply_gayed_gate_stack(
        r_eq, r_bd, px_eq, eq_weight=0.6, bd_weight=0.4, target_vol=0.18,
        lookback=21, max_leverage=2.5, ma_period=200,
    )
    # Warm-up: σ²_{t-1} needs lookback bars + shift(1) = 21 NaN bars,
    # SMA_{t-1} needs ma_period bars + shift(1) = 200 NaN bars.
    # Combined drop = max(lookback, ma_period) = 200 bars.
    assert len(net) == n - 200
    assert len(gate_on) == n - 200
