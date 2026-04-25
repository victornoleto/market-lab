"""TDD specs for iter 062 — internal-LETF UPRO substitution preserving equity exposure.

Three modules under test:

1. ``synth_letf_3leg.synth_upro_returns`` — synth UPRO daily returns
   from SPY at rf=0 convention (formula: 3·r_SPY − expense/252).
2. ``synth_letf_3leg.join_real_and_synth_letf`` — join real LETF data
   with synth LETF derived from SPY pre-inception.
3. ``synth_letf_3leg.apply_static_stack_3leg`` — vendored verbatim
   from iter 037; tested with new defaults (0.20/0.65/0.65) plus
   regression check that calling with iter 037 weights reproduces
   iter 037 stream.

Citations
---------
* `[leverage_for_the_long_run, p.20-25]` — Hsiao-Williams 2017 daily-reset LETF.
* `[risk_parity, ch.5]` — multi-leg risk-parity static stack.
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

from synth_letf_3leg import (  # noqa: E402
    apply_static_stack_3leg,
    join_real_and_synth_letf,
    synth_upro_returns,
    UPRO_EXPENSE_RATIO_DEFAULT,
    LETF_LEVERAGE_DEFAULT,
)
from numpy_reference_iter062 import (  # noqa: E402
    apply_static_stack_3leg_np,
    synth_upro_returns_np,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_returns(n: int = 300, seed: int = 11, scale: float = 0.011) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2005-01-03", periods=n, freq="B")
    return pd.Series(rng.normal(0.0005, scale, size=n), index=idx)


def _make_3stream(n: int = 250, seeds=(31, 37, 41)) -> tuple[pd.Series, pd.Series, pd.Series]:
    a = _make_returns(n, seed=seeds[0], scale=0.011)
    b = _make_returns(n, seed=seeds[1], scale=0.004)
    c = _make_returns(n, seed=seeds[2], scale=0.009)
    a.name, b.name, c.name = "EQ", "BD_S", "BD_L"
    return a, b, c


# ---------------------------------------------------------------------------
# 1. synth_upro_returns
# ---------------------------------------------------------------------------


def test_synth_upro_default_constants():
    """Defaults match ProShares 2024-25 prospectus (0.91% / yr, 3×)."""
    assert UPRO_EXPENSE_RATIO_DEFAULT == 0.0091
    assert LETF_LEVERAGE_DEFAULT == 3.0


def test_synth_upro_formula_is_lev_minus_daily_expense():
    """r_synth = leverage·r_spy − expense/252 (rf=0 convention)."""
    r_spy = _make_returns(100, seed=7)
    out = synth_upro_returns(r_spy, leverage=3.0, expense_ratio=0.0091)
    expected = 3.0 * r_spy - (0.0091 / 252.0)
    np.testing.assert_allclose(out.values, expected.values, atol=1e-15)
    assert out.index.equals(r_spy.index)


def test_synth_upro_zero_expense_is_pure_levered():
    """At expense_ratio=0, synth = leverage · r_spy exactly."""
    r_spy = _make_returns(50)
    out = synth_upro_returns(r_spy, leverage=3.0, expense_ratio=0.0)
    np.testing.assert_allclose(out.values, 3.0 * r_spy.values, atol=1e-15)


def test_synth_upro_supports_2x_letf():
    """Same formula works for SSO/QLD with leverage=2 default expense."""
    r_spy = _make_returns(50)
    out = synth_upro_returns(r_spy, leverage=2.0, expense_ratio=0.0089)
    expected = 2.0 * r_spy - (0.0089 / 252.0)
    np.testing.assert_allclose(out.values, expected.values, atol=1e-15)


def test_synth_upro_rejects_invalid_leverage():
    r_spy = _make_returns(20)
    with pytest.raises(ValueError):
        synth_upro_returns(r_spy, leverage=0.0)
    with pytest.raises(ValueError):
        synth_upro_returns(r_spy, leverage=-1.0)


def test_synth_upro_rejects_negative_expense():
    r_spy = _make_returns(20)
    with pytest.raises(ValueError):
        synth_upro_returns(r_spy, expense_ratio=-0.001)


def test_synth_upro_sharpe_matches_spy_modulo_expense_drag():
    """At expense_ratio=0, synth Sharpe equals SPY Sharpe exactly
    (mean and std both scale by leverage; ratio invariant)."""
    rng = np.random.default_rng(101)
    idx = pd.date_range("2005-01-03", periods=2520, freq="B")  # 10 years
    r_spy = pd.Series(rng.normal(0.0004, 0.011, size=len(idx)), index=idx)
    out = synth_upro_returns(r_spy, leverage=3.0, expense_ratio=0.0)
    sharpe_spy = (r_spy.mean() / r_spy.std()) * np.sqrt(252)
    sharpe_synth = (out.mean() / out.std()) * np.sqrt(252)
    np.testing.assert_allclose(sharpe_synth, sharpe_spy, atol=1e-10)


# ---------------------------------------------------------------------------
# 2. join_real_and_synth_letf
# ---------------------------------------------------------------------------


def test_join_uses_real_data_from_inception_onward():
    """Boundary day uses real, not synth."""
    r_spy = _make_returns(60, seed=3)
    real_start = r_spy.index[20]
    rng = np.random.default_rng(99)
    r_real = pd.Series(
        rng.normal(0.0006, 0.025, size=40), index=r_spy.index[20:],
    )
    joined = join_real_and_synth_letf(r_spy, r_real, expense_ratio=0.0091)
    np.testing.assert_allclose(
        joined.loc[r_spy.index[20:]].values, r_real.values, atol=1e-15,
    )
    assert joined.loc[real_start] == r_real.iloc[0]


def test_join_uses_synth_data_pre_inception():
    """Pre-inception dates use synth formula."""
    r_spy = _make_returns(60, seed=3)
    real_start = r_spy.index[20]
    rng = np.random.default_rng(99)
    r_real = pd.Series(
        rng.normal(0.0006, 0.025, size=40), index=r_spy.index[20:],
    )
    joined = join_real_and_synth_letf(r_spy, r_real, expense_ratio=0.0091)
    pre = joined.loc[joined.index < real_start]
    expected_pre = 3.0 * r_spy.loc[r_spy.index < real_start] - (0.0091 / 252.0)
    np.testing.assert_allclose(pre.values, expected_pre.values, atol=1e-15)


def test_join_no_overlap_or_duplicates():
    r_spy = _make_returns(60, seed=3)
    rng = np.random.default_rng(99)
    r_real = pd.Series(
        rng.normal(0.0006, 0.025, size=40), index=r_spy.index[20:],
    )
    joined = join_real_and_synth_letf(r_spy, r_real)
    assert joined.index.is_unique
    assert joined.index.is_monotonic_increasing


def test_join_rejects_empty_real_series():
    r_spy = _make_returns(20)
    empty = pd.Series([], dtype=float, index=pd.DatetimeIndex([]))
    with pytest.raises(ValueError):
        join_real_and_synth_letf(r_spy, empty)


def test_join_rejects_real_starting_before_spy():
    r_spy = _make_returns(20)  # starts 2005-01-03
    early = pd.date_range("2004-01-05", periods=10, freq="B")
    r_real = pd.Series([0.001] * 10, index=early)
    with pytest.raises(ValueError):
        join_real_and_synth_letf(r_spy, r_real)


# ---------------------------------------------------------------------------
# 3. 3-leg static stack with iter 062 defaults
# ---------------------------------------------------------------------------


def test_iter062_default_weights_are_020_065_065():
    """Default eq_w=0.20, bd_short_w=0.65, bd_long_w=0.65, total=1.50."""
    a, b, c = _make_3stream()
    net, positions, scale = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=0.0)
    np.testing.assert_allclose(positions["EQ"].values, 0.20)
    np.testing.assert_allclose(positions["BD_S"].values, 0.65)
    np.testing.assert_allclose(positions["BD_L"].values, 0.65)
    np.testing.assert_allclose(scale.values, 1.50)


def test_iter062_returns_match_weighted_sum():
    """net = 0.20·r_eq + 0.65·r_bd_s + 0.65·r_bd_l (zero cost)."""
    a, b, c = _make_3stream()
    net, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=0.0)
    expected = 0.20 * a + 0.65 * b + 0.65 * c
    np.testing.assert_allclose(net.values, expected.values, atol=1e-12)


def test_iter062_reduces_to_iter037_with_canonical_weights():
    """Calling with iter 037's weights (0.60, 0.45, 0.45) → iter 037 stream."""
    a, b, c = _make_3stream()
    net, positions, scale = apply_static_stack_3leg(
        a, b, c,
        eq_w=0.60, bd_short_w=0.45, bd_long_w=0.45, cost_bps_per_leg=0.0,
    )
    expected = 0.60 * a + 0.45 * b + 0.45 * c
    np.testing.assert_allclose(net.values, expected.values, atol=1e-12)
    np.testing.assert_allclose(scale.values, 1.50)


def test_iter062_rejects_negative_weights():
    a, b, c = _make_3stream()
    with pytest.raises(ValueError):
        apply_static_stack_3leg(a, b, c, eq_w=-0.1)
    with pytest.raises(ValueError):
        apply_static_stack_3leg(a, b, c, bd_short_w=-0.1)
    with pytest.raises(ValueError):
        apply_static_stack_3leg(a, b, c, bd_long_w=-0.1)


def test_iter062_rejects_unaligned_indexes():
    a, b, c = _make_3stream()
    b_short = b.iloc[5:]
    with pytest.raises(ValueError):
        apply_static_stack_3leg(a, b_short, c)


def test_iter062_setup_cost_at_t0():
    """Static weights → ∆=0 for t>0, but t=0 setup cost = (0.20+0.65+0.65)·bps."""
    a, b, c = _make_3stream(n=10)
    bps = 0.0002
    net_with, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=bps)
    net_no, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=0.0)
    cost_t0 = (net_no.iloc[0] - net_with.iloc[0])
    np.testing.assert_allclose(cost_t0, (0.20 + 0.65 + 0.65) * bps, atol=1e-15)


def test_iter062_zero_turnover_after_t0():
    """For t > 0, static weights mean ∆=0 → no incremental cost."""
    a, b, c = _make_3stream(n=20)
    bps = 0.001
    net_with, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=bps)
    net_no, _, _ = apply_static_stack_3leg(a, b, c, cost_bps_per_leg=0.0)
    np.testing.assert_allclose(net_with.iloc[1:].values, net_no.iloc[1:].values, atol=1e-15)


# ---------------------------------------------------------------------------
# 4. Cross-library parity (G7)
# ---------------------------------------------------------------------------


def test_numpy_synth_letf_matches_pandas_engine():
    """G7 G7 — synth-UPRO numpy reference = pandas engine to 1e-12."""
    r_spy = _make_returns(500, seed=42)
    pd_out = synth_upro_returns(r_spy, leverage=3.0, expense_ratio=0.0091)
    np_out = synth_upro_returns_np(r_spy.values, leverage=3.0, expense_ratio=0.0091)
    np.testing.assert_allclose(pd_out.values, np_out, atol=1e-15)


def test_numpy_3leg_stack_matches_pandas_engine():
    """G7 — 3-leg stack numpy reference = pandas engine to 1e-12."""
    a, b, c = _make_3stream(n=400)
    pd_net, _, _ = apply_static_stack_3leg(
        a, b, c,
        eq_w=0.20, bd_short_w=0.65, bd_long_w=0.65, cost_bps_per_leg=0.0002,
    )
    np_net = apply_static_stack_3leg_np(
        a.values, b.values, c.values,
        eq_w=0.20, bd_short_w=0.65, bd_long_w=0.65, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(pd_net.values, np_net, atol=1e-15)


def test_numpy_full_pipeline_synth_then_stack():
    """Full pipeline parity: synth-UPRO → 3-leg stack on numpy = pandas to 1e-12."""
    r_spy = _make_returns(400, seed=17)
    r_bd_s = _make_returns(400, seed=23, scale=0.004)
    r_bd_l = _make_returns(400, seed=29, scale=0.009)
    r_synth_pd = synth_upro_returns(r_spy)
    r_synth_pd.index = r_spy.index
    pd_net, _, _ = apply_static_stack_3leg(
        r_synth_pd, r_bd_s, r_bd_l, cost_bps_per_leg=0.0002,
    )
    r_synth_np = synth_upro_returns_np(r_spy.values)
    np_net = apply_static_stack_3leg_np(
        r_synth_np, r_bd_s.values, r_bd_l.values, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(pd_net.values, np_net, atol=1e-15)


def test_numpy_cagr_within_3pp_of_pandas_engine():
    """G7 cross-lib parity threshold (≤ 3 pp annualized CAGR diff)."""
    r_spy = _make_returns(2520, seed=42)
    r_bd_s = _make_returns(2520, seed=43, scale=0.004)
    r_bd_l = _make_returns(2520, seed=44, scale=0.009)

    r_synth_pd = synth_upro_returns(r_spy)
    r_synth_pd.index = r_spy.index
    pd_net, _, _ = apply_static_stack_3leg(
        r_synth_pd, r_bd_s, r_bd_l, cost_bps_per_leg=0.0002,
    )
    r_synth_np = synth_upro_returns_np(r_spy.values)
    np_net = apply_static_stack_3leg_np(
        r_synth_np, r_bd_s.values, r_bd_l.values, cost_bps_per_leg=0.0002,
    )

    n = len(pd_net)
    eq_pd = float(np.cumprod(1.0 + pd_net.values)[-1])
    eq_np = float(np.cumprod(1.0 + np_net)[-1])
    cagr_pd = eq_pd ** (252.0 / n) - 1.0
    cagr_np = eq_np ** (252.0 / n) - 1.0
    assert abs(cagr_pd - cagr_np) * 100.0 < 3.0
