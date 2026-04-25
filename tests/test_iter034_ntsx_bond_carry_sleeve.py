"""Iter 034 — TDD specs for NTSX bond-carry sleeve (3-leg static stack).

Iter 034 generalises iter 015's 2-leg static stacker to 3 legs to
support a zero-net-notional duration spread inside the bond sleeve.
These specs lock the iter-034-specific configuration AND verify the
3-leg primitive reduces exactly to iter 015's 2-leg case when
``bd_long_w == 0``.

Citations
---------
* Hypothesis: `iterations/034-2026-04-25-0120-ntsx-bond-carry-sleeve/hypothesis.md`
* `[risk_parity, ch.5]` — bond term-premium decomposition.
* `[risk_parity, p.5, p.10-11, ch.1]` — risk-parity static stack.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* Koijen-Moskowitz-Pedersen-Vrugt (2018), JFE 127(2) — cross-sectional
  bond carry premium.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER034_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "034-2026-04-25-0120-ntsx-bond-carry-sleeve"
ITER015_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "015-2026-04-24-1704-return-stacked-static-ntsx"


# ---------------------------------------------------------------------------
# 3-leg primitive — equivalence with iter 015 when long-bond weight is zero
# ---------------------------------------------------------------------------


def _make_synth_returns(seed: int = 42, n: int = 1500) -> pd.DataFrame:
    """Build 3-stream synthetic correlated returns for primitive tests."""
    rng = np.random.default_rng(seed)
    n = int(n)
    idx = pd.bdate_range("2010-01-04", periods=n)
    eq = rng.normal(0.0004, 0.012, n)
    bd_short = rng.normal(0.00012, 0.0035, n)
    bd_long = (
        0.85 * (bd_short / 0.0035) * 0.0070
        + 0.527 * rng.normal(0.0, 0.0070, n)
        + 0.00018
    )
    return pd.DataFrame({"EQ": eq, "BD_S": bd_short, "BD_L": bd_long}, index=idx)


def test_3leg_stack_returns_match_2leg_when_alpha_zero():
    """With ``bd_long_w == 0``, iter 034's 3-leg stacker must produce the
    SAME net returns as iter 015's 2-leg stacker. No spurious math."""
    sys.path.insert(0, str(ITER034_DIR))
    sys.path.insert(0, str(ITER015_DIR))
    from synth_stacked_etf_3leg import apply_static_stack_3leg
    from synth_stacked_etf import apply_static_stack

    r = _make_synth_returns()
    net2, _, _ = apply_static_stack(
        r["EQ"], r["BD_S"], eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002,
    )
    net3, _, _ = apply_static_stack_3leg(
        r["EQ"], r["BD_S"], r["BD_L"],
        eq_w=0.9, bd_short_w=0.6, bd_long_w=0.0, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(net2.to_numpy(), net3.to_numpy(), atol=1e-15)


def test_3leg_stack_preserves_total_bond_notional_at_alpha_0p2():
    """At α=0.2 the bond sleeve must split 0.4 IEF + 0.2 TLT for total 0.6
    bond notional (matches iter 015 verbatim)."""
    sys.path.insert(0, str(ITER034_DIR))
    from synth_stacked_etf_3leg import apply_static_stack_3leg

    r = _make_synth_returns(n=300)
    _, positions, _ = apply_static_stack_3leg(
        r["EQ"], r["BD_S"], r["BD_L"],
        eq_w=0.9, bd_short_w=0.4, bd_long_w=0.2, cost_bps_per_leg=0.0002,
    )
    bond_notional = positions["BD_S"] + positions["BD_L"]
    np.testing.assert_allclose(bond_notional.to_numpy(), 0.6, atol=1e-15)


def test_3leg_stack_total_leverage_invariant_matches_iter015_iter033():
    """Total leverage (eq_w + bd_short_w + bd_long_w) must == 1.5 to match
    iter 015 / iter 033 verbatim — no leverage drift."""
    sys.path.insert(0, str(ITER034_DIR))
    from synth_stacked_etf_3leg import apply_static_stack_3leg

    r = _make_synth_returns(n=300)
    _, _, scale = apply_static_stack_3leg(
        r["EQ"], r["BD_S"], r["BD_L"],
        eq_w=0.9, bd_short_w=0.4, bd_long_w=0.2, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(scale.to_numpy(), 1.5, atol=1e-15)


# ---------------------------------------------------------------------------
# Cross-library parity (G7 spec)
# ---------------------------------------------------------------------------


def test_3leg_stack_cross_lib_parity_pandas_vs_numpy():
    """pandas engine and pure-numpy reference must agree to floating-point
    tolerance on synthetic data — G7 cross-lib parity at the engine level."""
    sys.path.insert(0, str(ITER034_DIR))
    from synth_stacked_etf_3leg import apply_static_stack_3leg
    from numpy_reference_stacked_3leg import apply_static_stack_3leg_np

    r = _make_synth_returns()
    net_pd, _, _ = apply_static_stack_3leg(
        r["EQ"], r["BD_S"], r["BD_L"],
        eq_w=0.9, bd_short_w=0.4, bd_long_w=0.2, cost_bps_per_leg=0.0002,
    )
    net_np, _, _ = apply_static_stack_3leg_np(
        r["EQ"].to_numpy(), r["BD_S"].to_numpy(), r["BD_L"].to_numpy(),
        eq_w=0.9, bd_short_w=0.4, bd_long_w=0.2, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(net_pd.to_numpy(), net_np, atol=1e-15)


# ---------------------------------------------------------------------------
# Configuration invariants
# ---------------------------------------------------------------------------


def test_iter034_loads_ief_and_tlt_for_all_datasets():
    """All 3 datasets must load BOTH IEF (short-duration) and TLT (long-duration)."""
    sys.path.insert(0, str(ITER034_DIR))
    from run_backtests import DATASETS  # noqa: WPS433
    for ds_name, ds in DATASETS.items():
        assert ds["bond_short_symbol"] == "IEF", (
            f"{ds_name} bond_short must be IEF; got {ds['bond_short_symbol']!r}"
        )
        assert ds["bond_long_symbol"] == "TLT", (
            f"{ds_name} bond_long must be TLT; got {ds['bond_long_symbol']!r}"
        )


def test_iter034_preserves_ntsx_total_leverage_invariant():
    """Iter 034 cfg must have total leverage 1.5 (matches iter 015/033 NTSX
    prospectus weight) AND total bond notional 0.6 (preserves iter 015 weight)."""
    sys.path.insert(0, str(ITER034_DIR))
    from run_backtests import CFG  # noqa: WPS433
    assert CFG["eq_w"] == 0.90, f"equity weight must be 0.90 verbatim; got {CFG['eq_w']}"
    assert CFG["bd_short_w"] == 0.40, f"bd_short_w must be 0.40 (=0.6×0.667); got {CFG['bd_short_w']}"
    assert CFG["bd_long_w"] == 0.20, f"bd_long_w must be 0.20 (=0.6×0.333); got {CFG['bd_long_w']}"
    bond_notional = CFG["bd_short_w"] + CFG["bd_long_w"]
    assert abs(bond_notional - 0.60) < 1e-12, (
        f"total bond notional must be 0.60 (matches iter 015); got {bond_notional}"
    )
    total_lev = CFG["eq_w"] + bond_notional
    assert abs(total_lev - 1.50) < 1e-12, (
        f"total leverage must be 1.50 (matches iter 015/033); got {total_lev}"
    )


def test_iter034_load_triple_returns_returns_three_columns():
    """load_triple_returns must produce a DataFrame with EQ + IEF + TLT columns."""
    sys.path.insert(0, str(ITER034_DIR))
    from run_backtests import load_triple_returns  # noqa: WPS433
    r = load_triple_returns("SPY", "IEF", "TLT", "2015-01-01", "2015-06-30")
    assert "SPY" in r.columns, f"expected SPY; got {list(r.columns)}"
    assert "IEF" in r.columns, f"expected IEF; got {list(r.columns)}"
    assert "TLT" in r.columns, f"expected TLT; got {list(r.columns)}"
    assert len(r) >= 100, f"expected ≥100 bars in 6 months; got {len(r)}"
