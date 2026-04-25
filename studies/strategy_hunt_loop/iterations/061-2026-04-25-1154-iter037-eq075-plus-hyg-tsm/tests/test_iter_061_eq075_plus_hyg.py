"""TDD specs for iter 061 — equity-overweight 3-leg stack (0.75/0.40/0.40)
+ HYG TSM at w=0.10.

Three modules under test:

1. ``synth_stacked_etf_3leg_eq075.apply_static_stack_3leg`` — vendored
   verbatim from iter 037; tested with new default weights (0.75/0.40/0.40)
   plus reduces-to-iter037-weights regression check.
2. ``hyg_tsm.compute_hyg_tsm_returns`` — vendored from iter 058/059;
   re-tests engine invariants in this iter's namespace.
3. ``combined_eq075_plus_hyg.combine_eq075_plus_hyg`` — convex combiner
   structurally identical to iter 058/059's combiner.

Citations
---------
* `[risk_parity, ch.5]` — multi-leg risk-parity (eq075 base).
* Asvanunt-Richardson 2017 JPM 43(2) — credit risk premium thesis.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* Markowitz (1952) JoF 7(1) — closed-form Sharpe identity.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from synth_stacked_etf_3leg_eq075 import apply_static_stack_3leg  # noqa: E402
from hyg_tsm import compute_hyg_tsm_returns  # noqa: E402
from numpy_reference_iter061 import compute_hyg_tsm_returns_np  # noqa: E402
from combined_eq075_plus_hyg import combine_eq075_plus_hyg  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_prices(n: int = 300, drift: float = 0.0002, seed: int = 7) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    rets = rng.normal(loc=drift, scale=0.008, size=n)
    return pd.Series(np.cumprod(1.0 + rets) * 90.0, index=idx, name="HYG")


def _make_returns(n: int = 300, seed: int = 11, scale: float = 0.011) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    return pd.Series(rng.normal(0.0005, scale, size=n), index=idx)


def _make_3stream(n: int = 250, seeds=(31, 37, 41)) -> tuple[pd.Series, pd.Series, pd.Series]:
    a = _make_returns(n, seed=seeds[0], scale=0.011)
    b = _make_returns(n, seed=seeds[1], scale=0.004)
    c = _make_returns(n, seed=seeds[2], scale=0.009)
    a.name, b.name, c.name = "EQ", "BD_S", "BD_L"
    return a, b, c


# ---------------------------------------------------------------------------
# 1. eq075 3-leg stack
# ---------------------------------------------------------------------------


def test_eq075_default_weights_match_spec():
    """Default eq_w=0.75, bd_short_w=0.40, bd_long_w=0.40, total=1.55."""
    a, b, c = _make_3stream()
    net, positions, scale = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=0.0)
    np.testing.assert_allclose(positions["EQ"].values, 0.75)
    np.testing.assert_allclose(positions["BD_S"].values, 0.40)
    np.testing.assert_allclose(positions["BD_L"].values, 0.40)
    np.testing.assert_allclose(scale.values, 1.55)


def test_eq075_returns_match_weighted_sum():
    """net = 0.75*r_eq + 0.40*r_bd_s + 0.40*r_bd_l (zero cost)."""
    a, b, c = _make_3stream()
    net, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=0.0)
    expected = 0.75 * a + 0.40 * b + 0.40 * c
    np.testing.assert_allclose(net.values, expected.values, atol=1e-12)


def test_eq075_reduces_to_iter037_with_canonical_weights():
    """Calling with iter 037's weights should give iter 037's stream."""
    a, b, c = _make_3stream()
    net, positions, scale = apply_static_stack_3leg(
        a, b, c,
        eq_w=0.60, bd_short_w=0.45, bd_long_w=0.45, cost_bps_per_leg=0.0,
    )
    expected = 0.60 * a + 0.45 * b + 0.45 * c
    np.testing.assert_allclose(net.values, expected.values, atol=1e-12)
    np.testing.assert_allclose(scale.values, 1.50)


def test_eq075_rejects_negative_weights():
    a, b, c = _make_3stream()
    with pytest.raises(ValueError):
        apply_static_stack_3leg(a, b, c, eq_w=-0.1)
    with pytest.raises(ValueError):
        apply_static_stack_3leg(a, b, c, bd_short_w=-0.1)
    with pytest.raises(ValueError):
        apply_static_stack_3leg(a, b, c, bd_long_w=-0.1)


def test_eq075_rejects_unaligned_indexes():
    a, b, c = _make_3stream()
    b_shifted = b.iloc[5:]  # different index length
    with pytest.raises(ValueError):
        apply_static_stack_3leg(a, b_shifted, c)


def test_eq075_charges_setup_cost_at_t0():
    """Static weights → ∆=0 for t>0, but t=0 setup cost = (0.75+0.40+0.40)*bps."""
    a, b, c = _make_3stream(n=10)
    bps = 0.0002
    net_with, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=bps)
    net_no, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=0.0)
    cost_t0 = (net_no.iloc[0] - net_with.iloc[0])
    np.testing.assert_allclose(cost_t0, (0.75 + 0.40 + 0.40) * bps, atol=1e-15)


def test_eq075_zero_turnover_after_t0():
    """For t > 0, static weights mean ∆=0 → no incremental cost."""
    a, b, c = _make_3stream(n=20)
    bps = 0.001
    net_with, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=bps)
    net_no, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=0.0)
    np.testing.assert_allclose(net_with.iloc[1:].values, net_no.iloc[1:].values, atol=1e-15)


# ---------------------------------------------------------------------------
# 2. HYG TSM core engine (vendored — re-test invariants)
# ---------------------------------------------------------------------------


def test_hyg_tsm_returns_indexed_to_returns():
    px = _make_prices(120)
    out = compute_hyg_tsm_returns(px, lookback=90)
    assert len(out) == len(px) - 1
    assert out.index.equals(px.index[1:])


def test_hyg_tsm_warmup_period_is_cash():
    px = _make_prices(150)
    out = compute_hyg_tsm_returns(px, lookback=90, rf=0.02)
    rf_d = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    np.testing.assert_allclose(out.iloc[:90].values, np.full(90, rf_d), atol=1e-12)


def test_hyg_tsm_no_lookahead():
    n = 200
    px = _make_prices(n)
    out_full = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=0.0)
    px_modified = px.copy()
    px_modified.iloc[-1] = px.iloc[-1] * 2.0
    out_modified = compute_hyg_tsm_returns(px_modified, lookback=90, rf=0.02, cost_bps=0.0)
    np.testing.assert_array_equal(out_full.iloc[:-1].values, out_modified.iloc[:-1].values)


def test_invalid_lookback_raises():
    px = _make_prices(100)
    with pytest.raises(ValueError):
        compute_hyg_tsm_returns(px, lookback=0)
    with pytest.raises(ValueError):
        compute_hyg_tsm_returns(px, lookback=-5)


# ---------------------------------------------------------------------------
# 3. Combined eq075 + HYG_TSM
# ---------------------------------------------------------------------------


def test_combined_w090_w010_is_correct_weighted_sum():
    """w_eq075=0.9, w_hyg=0.1 → combined = 0.9*r_eq075 + 0.1*r_hyg."""
    r_eq075 = _make_returns(300, seed=11)
    px = _make_prices(300, seed=22)
    r_hyg = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    combined = combine_eq075_plus_hyg(r_eq075, r_hyg, w_eq075=0.9, w_hyg=0.1)
    common = r_eq075.index.intersection(r_hyg.index)
    expected = 0.9 * r_eq075.loc[common] + 0.1 * r_hyg.loc[common]
    np.testing.assert_allclose(combined.values, expected.values, atol=1e-12)


def test_combined_reduces_to_eq075_when_w_hyg_zero():
    r_eq075 = _make_returns(300, seed=11)
    px = _make_prices(300, seed=22)
    r_hyg = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    combined = combine_eq075_plus_hyg(r_eq075, r_hyg, w_eq075=1.0, w_hyg=0.0)
    common = r_eq075.index.intersection(r_hyg.index)
    np.testing.assert_allclose(combined.values, r_eq075.loc[common].values, atol=1e-12)


def test_combined_inner_joins_indexes():
    r_eq075 = _make_returns(300, seed=11).iloc[10:200]
    px = _make_prices(300, seed=22)
    r_hyg = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    combined = combine_eq075_plus_hyg(r_eq075, r_hyg, w_eq075=0.9, w_hyg=0.1)
    expected_idx = r_eq075.index.intersection(r_hyg.index)
    assert combined.index.equals(expected_idx)


def test_combined_rejects_negative_weights():
    r_eq075 = _make_returns(100)
    px = _make_prices(100)
    r_hyg = compute_hyg_tsm_returns(px, lookback=30)
    with pytest.raises(ValueError):
        combine_eq075_plus_hyg(r_eq075, r_hyg, w_eq075=-0.1, w_hyg=1.1)
    with pytest.raises(ValueError):
        combine_eq075_plus_hyg(r_eq075, r_hyg, w_eq075=1.1, w_hyg=-0.1)


# ---------------------------------------------------------------------------
# 4. Cross-library parity (G7)
# ---------------------------------------------------------------------------


def test_numpy_reference_matches_pandas_engine():
    px = _make_prices(300, seed=42)
    pd_out = compute_hyg_tsm_returns(px, lookback=90, rf=0.02, cost_bps=5.0)
    np_out = compute_hyg_tsm_returns_np(
        px.values, lookback=90, rf=0.02, cost_bps=5.0,
    )
    assert len(pd_out) == len(np_out)
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-12)


def test_numpy_cagr_matches_pandas_to_within_3pp():
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
