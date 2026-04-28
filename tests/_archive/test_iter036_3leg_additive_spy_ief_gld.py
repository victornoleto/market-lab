"""Iter 036 — TDD specs for 3-leg ADDITIVE static stack (SPY + IEF + GLD).

Iter 036 vendors iter 034's `apply_static_stack_3leg` verbatim (asset-
agnostic 3-leg primitive) and adapts the run-config to ADD gold (0.30 GLD)
as a third diversifier on top of iter 015's preserved 0.9 SPY + 0.6 IEF
base — total leverage 1.80 (vs iter 015's 1.50).

These specs lock the iter 036 configuration AND verify that loading
SPY / IEF / GLD parquet caches produces a non-empty triple-return frame
on a sub-window where all three series exist post-GLD-inception
(2004-11-19+).

Citations
---------
* Hypothesis: `iterations/036-2026-04-25-0206-ntsx-3leg-additive-spy-ief-gld/hypothesis.md`
* `[risk_parity, ch.5]` — multi-leg risk-parity decomposition.
* Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold diversification.
* Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021 — cross-asset orthogonality.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ITER036_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "036-2026-04-25-0206-ntsx-3leg-additive-spy-ief-gld"


def _import_iter036(name: str):
    """Defensive import — pops cached module first so iter-NNN tests
    that share a module name (e.g., `run_backtests`) don't poison each
    other's `sys.modules` cache when run in the same pytest session."""
    sys.modules.pop(name, None)
    sys.path.insert(0, str(ITER036_DIR))
    return __import__(name)


# ---------------------------------------------------------------------------
# Configuration invariants
# ---------------------------------------------------------------------------


def test_iter036_loads_spy_ief_gld_for_all_datasets():
    """All 3 datasets must use SPY/QQQ as equity, IEF as bond, GLD as gold."""
    DATASETS = _import_iter036("run_backtests").DATASETS
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


def test_iter036_preserves_iter015_equity_bond_sleeve_verbatim():
    """Iter 036 must preserve iter 015 equity + bond weights verbatim
    (eq=0.90, bd=0.60) and ADD gold as a third leg (gld=0.30); total
    leverage 1.80, NOT 1.50."""
    CFG = _import_iter036("run_backtests").CFG
    assert CFG["eq_w"] == 0.90, f"equity weight must be 0.90 verbatim; got {CFG['eq_w']}"
    assert CFG["bd_short_w"] == 0.60, (
        f"bond weight must be 0.60 verbatim from iter 015; got {CFG['bd_short_w']}"
    )
    assert CFG["bd_long_w"] == 0.30, (
        f"gold weight must be 0.30 (added as 3rd leg); got {CFG['bd_long_w']}"
    )
    total_lev = CFG["eq_w"] + CFG["bd_short_w"] + CFG["bd_long_w"]
    assert abs(total_lev - 1.80) < 1e-12, (
        f"total leverage must be 1.80 (additive, not preserved at 1.50); got {total_lev}"
    )


def test_iter036_load_triple_returns_returns_three_columns_post_gld_inception():
    """load_triple_returns must produce a DataFrame with SPY + IEF + GLD
    columns on a sub-window after GLD inception (2004-11-19)."""
    load_triple_returns = _import_iter036("run_backtests").load_triple_returns
    r = load_triple_returns("SPY", "IEF", "GLD", "2015-01-01", "2015-06-30")
    assert "SPY" in r.columns, f"expected SPY; got {list(r.columns)}"
    assert "IEF" in r.columns, f"expected IEF; got {list(r.columns)}"
    assert "GLD" in r.columns, f"expected GLD; got {list(r.columns)}"
    assert len(r) >= 100, f"expected ≥100 bars in 6 months; got {len(r)}"


def test_iter036_3leg_primitive_total_leverage_at_180():
    """The 3-leg primitive must scale total exposure to 1.80 with iter 036
    weights (0.9 + 0.6 + 0.3) on every bar — additive stack, no leverage drift."""
    import pandas as pd
    apply_static_stack_3leg = _import_iter036(
        "synth_stacked_etf_3leg"
    ).apply_static_stack_3leg

    rng = np.random.default_rng(36)
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
        eq_w=0.90, bd_short_w=0.60, bd_long_w=0.30, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(scale.to_numpy(), 1.80, atol=1e-15)


def test_iter036_3leg_primitive_pandas_vs_numpy_parity_at_iter036_weights():
    """G7 cross-lib spec: at iter 036's specific weights (0.9 / 0.6 / 0.3)
    the pandas engine and pure-numpy reference must agree to floating-point
    tolerance on synthetic data."""
    import pandas as pd
    apply_static_stack_3leg = _import_iter036(
        "synth_stacked_etf_3leg"
    ).apply_static_stack_3leg
    apply_static_stack_3leg_np = _import_iter036(
        "numpy_reference_stacked_3leg"
    ).apply_static_stack_3leg_np

    rng = np.random.default_rng(36)
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
        eq_w=0.90, bd_short_w=0.60, bd_long_w=0.30, cost_bps_per_leg=0.0002,
    )
    net_np, _, _ = apply_static_stack_3leg_np(
        r_eq.to_numpy(), r_bd.to_numpy(), r_gld.to_numpy(),
        eq_w=0.90, bd_short_w=0.60, bd_long_w=0.30, cost_bps_per_leg=0.0002,
    )
    np.testing.assert_allclose(net_pd.to_numpy(), net_np, atol=1e-15)
