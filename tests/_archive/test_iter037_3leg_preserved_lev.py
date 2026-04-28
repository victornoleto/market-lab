"""Iter 037 — TDD specs for leverage-preserved 3-leg static stack.

Iter 037 vendors iter 036's `apply_static_stack_3leg` verbatim (asset-
agnostic 3-leg primitive) and adapts the run-config to **redistribute**
weights from iter 036's 0.90 / 0.60 / 0.30 (total 1.80×) to
**0.60 / 0.45 / 0.45 (total 1.50×)** — preserving iter 015's leverage
budget while adding a 3rd diversifier leg via 33% equity-weight cut.

These specs lock the iter 037 configuration AND verify the simulator
identities required for cross-leg-count comparison: when the gold
weight is 0, the 3-leg primitive must reduce to a 2-leg case
algebraically identical to the same-weights 2-leg simulator (a
mechanism check that protects the iter 015 ↔ iter 037 comparison).

Citations
---------
* Hypothesis: `iterations/037-2026-04-25-0224-ntsx-3leg-preserved-lev/hypothesis.md`
* `[risk_parity, ch.5]` — multi-leg risk-parity decomposition.
* Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021 — cross-asset orthogonality.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ITER037_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "037-2026-04-25-0224-ntsx-3leg-preserved-lev"


def _import_iter037(name: str):
    """Defensive import — pops cached module first so iter-NNN tests
    that share a module name (e.g., `run_backtests`) don't poison each
    other's `sys.modules` cache when run in the same pytest session."""
    sys.modules.pop(name, None)
    sys.path.insert(0, str(ITER037_DIR))
    return __import__(name)


# ---------------------------------------------------------------------------
# Configuration invariants
# ---------------------------------------------------------------------------


def test_iter037_loads_spy_ief_gld_for_all_datasets():
    """All 3 datasets must use SPY/QQQ as equity, IEF as bond, GLD as gold."""
    DATASETS = _import_iter037("run_backtests").DATASETS
    for ds_name, ds in DATASETS.items():
        assert ds["bond_symbol"] == "IEF", (
            f"{ds_name} bond must be IEF; got {ds['bond_symbol']!r}"
        )
        assert ds["gold_symbol"] == "GLD", (
            f"{ds_name} gold must be GLD; got {ds['gold_symbol']!r}"
        )
        assert ds["equity_symbol"] in ("SPY", "QQQ"), (
            f"{ds_name} equity must be SPY or QQQ; got {ds['equity_symbol']!r}"
        )


def test_iter037_weights_redistribute_to_preserve_iter015_leverage():
    """Iter 037 must use eq=0.60, bd=0.45, gld=0.45 — total leverage 1.50
    (matches iter 015) — NOT 1.80 like iter 036. This is the structural
    novelty: 3 legs at iter 015's leverage budget."""
    CFG = _import_iter037("run_backtests").CFG
    assert CFG["eq_w"] == 0.60, (
        f"equity weight must be 0.60 (cut from iter 036's 0.90); got {CFG['eq_w']}"
    )
    assert CFG["bd_short_w"] == 0.45, (
        f"bond weight must be 0.45 (vs iter 015/036's 0.60); got {CFG['bd_short_w']}"
    )
    assert CFG["bd_long_w"] == 0.45, (
        f"gold weight must be 0.45 (vs iter 036's 0.30); got {CFG['bd_long_w']}"
    )
    total_lev = CFG["eq_w"] + CFG["bd_short_w"] + CFG["bd_long_w"]
    assert abs(total_lev - 1.50) < 1e-12, (
        f"total leverage must be 1.50 (preserved at iter 015 budget); got {total_lev}"
    )
    # Diversifier-sleeve notional preserved at 0.90 vs iter 036's 0.90 too,
    # but via a 50/50 split rather than 67/33.
    diversifier_notional = CFG["bd_short_w"] + CFG["bd_long_w"]
    assert abs(diversifier_notional - 0.90) < 1e-12, (
        f"diversifier sleeve must be 0.90 (vs iter 015's 0.60 IEF); got {diversifier_notional}"
    )


def test_iter037_load_triple_returns_returns_three_columns_post_gld_inception():
    """load_triple_returns must produce a DataFrame with SPY + IEF + GLD
    columns on a sub-window after GLD inception (2004-11-19)."""
    load_triple_returns = _import_iter037("run_backtests").load_triple_returns
    r = load_triple_returns("SPY", "IEF", "GLD", "2015-01-01", "2015-06-30")
    assert "SPY" in r.columns, f"expected SPY; got {list(r.columns)}"
    assert "IEF" in r.columns, f"expected IEF; got {list(r.columns)}"
    assert "GLD" in r.columns, f"expected GLD; got {list(r.columns)}"
    assert len(r) >= 100, f"expected ≥100 bars in 6 months; got {len(r)}"


def test_iter037_3leg_primitive_total_leverage_at_150():
    """The 3-leg primitive must scale total exposure to 1.50 with iter 037
    weights (0.60 + 0.45 + 0.45) on every bar — preserved-lev stack, no drift."""
    import pandas as pd
    apply_static_stack_3leg = _import_iter037(
        "synth_stacked_etf_3leg"
    ).apply_static_stack_3leg

    rng = np.random.default_rng(37)
    n = 500
    idx = pd.bdate_range("2010-01-04", periods=n)
    eq = rng.normal(0.0004, 0.012, n)
    bd = rng.normal(0.00012, 0.0035, n)
    gld = rng.normal(0.00015, 0.0085, n)
    r_eq = pd.Series(eq, index=idx)
    r_bd = pd.Series(bd, index=idx)
    r_gld = pd.Series(gld, index=idx)
    _, _, scale = apply_static_stack_3leg(
        r_eq, r_bd, r_gld,
        eq_w=0.60, bd_short_w=0.45, bd_long_w=0.45, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(scale.to_numpy(), 1.50, atol=1e-15)


def test_iter037_3leg_primitive_pandas_vs_numpy_parity_at_iter037_weights():
    """G7 cross-lib spec: at iter 037's specific weights (0.60 / 0.45 / 0.45)
    the pandas engine and pure-numpy reference must agree to floating-point
    tolerance on synthetic data."""
    import pandas as pd
    apply_static_stack_3leg = _import_iter037(
        "synth_stacked_etf_3leg"
    ).apply_static_stack_3leg
    apply_static_stack_3leg_np = _import_iter037(
        "numpy_reference_stacked_3leg"
    ).apply_static_stack_3leg_np

    rng = np.random.default_rng(37)
    n = 1500
    idx = pd.bdate_range("2010-01-04", periods=n)
    eq = rng.normal(0.0004, 0.012, n)
    bd = rng.normal(0.00012, 0.0035, n)
    gld = rng.normal(0.00015, 0.0085, n)
    r_eq = pd.Series(eq, index=idx)
    r_bd = pd.Series(bd, index=idx)
    r_gld = pd.Series(gld, index=idx)

    net_pd, _, _ = apply_static_stack_3leg(
        r_eq, r_bd, r_gld,
        eq_w=0.60, bd_short_w=0.45, bd_long_w=0.45, cost_bps_per_leg=0.0002,
    )
    net_np, _, _ = apply_static_stack_3leg_np(
        r_eq.to_numpy(), r_bd.to_numpy(), r_gld.to_numpy(),
        eq_w=0.60, bd_short_w=0.45, bd_long_w=0.45, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(net_pd.to_numpy(), net_np, atol=1e-15)


def test_iter037_3leg_reduces_to_2leg_when_gld_weight_zero():
    """Architectural identity: setting `bd_long_w=0` (gold weight) must
    reproduce the 2-leg behaviour at the same eq/bd weights — locking the
    asset-agnosticism of the primitive and the legitimacy of the
    iter 015 ↔ iter 037 comparison."""
    import pandas as pd
    apply_static_stack_3leg = _import_iter037(
        "synth_stacked_etf_3leg"
    ).apply_static_stack_3leg

    rng = np.random.default_rng(115)
    n = 750
    idx = pd.bdate_range("2010-01-04", periods=n)
    r_eq = pd.Series(rng.normal(0.0004, 0.012, n), index=idx)
    r_bd = pd.Series(rng.normal(0.00012, 0.0035, n), index=idx)
    r_gld_dummy = pd.Series(rng.normal(0.00015, 0.0085, n), index=idx)

    # 3-leg call with gold-weight = 0 must equal a hand-computed 2-leg result
    # at the same equity/bond weights and cost.
    net_3leg_zero_gld, _, scale = apply_static_stack_3leg(
        r_eq, r_bd, r_gld_dummy,
        eq_w=0.9, bd_short_w=0.6, bd_long_w=0.0, cost_bps_per_leg=0.0002,
    )
    # Hand-rolled 2-leg reference at iter 015 weights.
    eq_w, bd_w, c = 0.9, 0.6, 0.0002
    gross_2leg = eq_w * r_eq + bd_w * r_bd
    # Static positions: cost = (eq_w + bd_w) * c on bar 0, 0 thereafter.
    cost_2leg = pd.Series(0.0, index=idx)
    cost_2leg.iloc[0] = (eq_w + bd_w) * c
    net_2leg_ref = gross_2leg - cost_2leg

    np.testing.assert_allclose(
        net_3leg_zero_gld.to_numpy(),
        net_2leg_ref.to_numpy(),
        atol=1e-15,
    )
    np.testing.assert_allclose(scale.to_numpy(), 1.50, atol=1e-15)
