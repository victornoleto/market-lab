"""Iter 038 — TDD specs for VIX-regime-gated 3-leg static stack.

Iter 038 vendors iter 037's 3-leg primitive concept and adds a
**binary VIX-level regime gate** modulating total leverage between
``lev_lo=1.70`` (when VIX_{t-1} < threshold) and ``lev_hi=1.00``
(otherwise). Base weights (eq:bd:gld = 0.60:0.45:0.45) are preserved;
the regime scales all 3 legs proportionally so the eq:bd:gld ratio is
constant across regimes.

These specs pin the simulator identities required for cross-iter
comparison and the lookahead-free behavior:

* All-low-vol VIX history → primitive reduces to a static stack with
  weights ``base * lev_lo / sum(base)``.
* All-high-vol VIX history → primitive reduces to ``base * lev_hi /
  sum(base)``.
* Mixed regime → cost only on regime-flip days; positions constant
  within a regime.
* 1-day signal lag → bar t uses VIX_{t-1} (causal).
* Pandas engine and pure-numpy reference produce identical net returns
  to within 1e-10.

Citations
---------
* Hypothesis: `iterations/038-2026-04-25-0246-regime-lev-vix/hypothesis.md`
* `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching.
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
* Moreira-Muir (2017), JF 72(4) Table IV — vol-managed Sharpe uplift.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ITER038_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "038-2026-04-25-0246-regime-lev-vix"


def _import_iter038(name: str):
    """Defensive import — pops cached module first to avoid poisoning
    sys.modules across iter-NNN tests that share filenames."""
    sys.modules.pop(name, None)
    sys.path.insert(0, str(ITER038_DIR))
    return __import__(name)


# ---------------------------------------------------------------------------
# Synthetic fixtures — short, deterministic
# ---------------------------------------------------------------------------


def _synth_inputs(n: int = 200, seed: int = 7) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Three return streams + a VIX series, daily index."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_eq = pd.Series(rng.normal(0.0005, 0.012, n), index=idx)
    r_bd = pd.Series(rng.normal(0.00015, 0.005, n), index=idx)
    r_gld = pd.Series(rng.normal(0.00020, 0.010, n), index=idx)
    # VIX synthetic: oscillating below/above 20 to exercise both regimes
    vix = pd.Series(15.0 + 10.0 * np.sin(np.linspace(0, 6 * np.pi, n)), index=idx)
    return r_eq, r_bd, r_gld, vix


# ---------------------------------------------------------------------------
# Reduction identities
# ---------------------------------------------------------------------------


def test_all_low_vol_reduces_to_static_stack_at_lev_lo():
    """When VIX is always far below threshold, every bar uses lev_lo and
    positions equal base * lev_lo / sum(base)."""
    rls = _import_iter038("regime_lev_stack_3leg")
    r_eq, r_bd, r_gld, _ = _synth_inputs(n=120)
    vix_low = pd.Series(5.0, index=r_eq.index)  # always < 20
    net, positions, scale, regime = rls.apply_regime_lev_stack_3leg(
        r_eq, r_bd, r_gld, vix_low,
        threshold=20.0, lev_lo=1.70, lev_hi=1.00,
        base_weights=(0.60, 0.45, 0.45),
        cost_bps_per_leg=0.0002,
    )
    assert (regime.iloc[1:] == 1).all(), "all bars (after first) must be low-vol"
    expected_eq = 0.60 * (1.70 / 1.50)
    expected_bd = 0.45 * (1.70 / 1.50)
    expected_gld = 0.45 * (1.70 / 1.50)
    assert np.isclose(positions["EQ"].iloc[1:], expected_eq).all()
    assert np.isclose(positions["BD"].iloc[1:], expected_bd).all()
    assert np.isclose(positions["GLD"].iloc[1:], expected_gld).all()
    assert np.isclose(scale.iloc[1:], 1.70).all()


def test_all_high_vol_reduces_to_static_stack_at_lev_hi():
    """When VIX is always far above threshold, every bar (after first)
    uses lev_hi and positions equal base * lev_hi / sum(base)."""
    rls = _import_iter038("regime_lev_stack_3leg")
    r_eq, r_bd, r_gld, _ = _synth_inputs(n=120)
    vix_high = pd.Series(50.0, index=r_eq.index)
    net, positions, scale, regime = rls.apply_regime_lev_stack_3leg(
        r_eq, r_bd, r_gld, vix_high,
        threshold=20.0, lev_lo=1.70, lev_hi=1.00,
        base_weights=(0.60, 0.45, 0.45),
        cost_bps_per_leg=0.0002,
    )
    assert (regime.iloc[1:] == 0).all(), "all bars (after first) must be high-vol"
    expected_eq = 0.60 * (1.00 / 1.50)
    expected_bd = 0.45 * (1.00 / 1.50)
    expected_gld = 0.45 * (1.00 / 1.50)
    assert np.isclose(positions["EQ"].iloc[1:], expected_eq).all()
    assert np.isclose(positions["BD"].iloc[1:], expected_bd).all()
    assert np.isclose(positions["GLD"].iloc[1:], expected_gld).all()
    assert np.isclose(scale.iloc[1:], 1.00).all()


# ---------------------------------------------------------------------------
# Lookahead-free signal lag
# ---------------------------------------------------------------------------


def test_regime_uses_vix_lagged_one_day():
    """Bar t's regime must depend on VIX_{t-1}, not VIX_t. Concretely:
    flip VIX from low to high on bar k; regime should flip on bar k+1."""
    rls = _import_iter038("regime_lev_stack_3leg")
    r_eq, r_bd, r_gld, _ = _synth_inputs(n=30)
    # Construct a VIX history that is low until bar 15, then jumps to 30.
    vix = pd.Series(10.0, index=r_eq.index)
    vix.iloc[15:] = 30.0
    net, positions, scale, regime = rls.apply_regime_lev_stack_3leg(
        r_eq, r_bd, r_gld, vix,
        threshold=20.0, lev_lo=1.70, lev_hi=1.00,
    )
    # VIX[14]=10 → regime[15] should still be low-vol (1)
    # VIX[15]=30 → regime[16] should be high-vol (0)
    assert regime.iloc[15] == 1, "regime[15] uses VIX[14]=10 → low-vol"
    assert regime.iloc[16] == 0, "regime[16] uses VIX[15]=30 → high-vol"


# ---------------------------------------------------------------------------
# Cost is zero within a regime, non-zero on flip days
# ---------------------------------------------------------------------------


def test_cost_only_on_regime_flip_days():
    """Within a regime, positions are constant → no rebalance cost.
    Cost > 0 only on the flip day (and the t=0 setup baseline)."""
    rls = _import_iter038("regime_lev_stack_3leg")
    r_eq, r_bd, r_gld, _ = _synth_inputs(n=30)
    vix = pd.Series(10.0, index=r_eq.index)
    vix.iloc[15:] = 30.0
    net, positions, scale, regime = rls.apply_regime_lev_stack_3leg(
        r_eq, r_bd, r_gld, vix,
        threshold=20.0, lev_lo=1.70, lev_hi=1.00,
        cost_bps_per_leg=0.0002,
    )
    dpos = positions.diff().abs().sum(axis=1)
    # Bars 1..15 within low-vol → ∆=0
    assert np.allclose(dpos.iloc[1:16], 0.0)
    # Bar 16 = first high-vol → ∆ > 0 (the regime flip from VIX[15]=30)
    assert dpos.iloc[16] > 0
    # Bars 17..29 within high-vol → ∆=0
    assert np.allclose(dpos.iloc[17:], 0.0)


# ---------------------------------------------------------------------------
# Cross-library parity (G7)
# ---------------------------------------------------------------------------


def test_pandas_engine_matches_numpy_reference_within_1e10():
    """The pandas primitive and the pure-numpy reference must agree on
    net returns to within 1e-10 across a mixed-regime fixture."""
    rls = _import_iter038("regime_lev_stack_3leg")
    npref = _import_iter038("numpy_reference_regime_lev_stack_3leg")

    r_eq, r_bd, r_gld, vix = _synth_inputs(n=200)
    net_pd, _, _, regime = rls.apply_regime_lev_stack_3leg(
        r_eq, r_bd, r_gld, vix,
        threshold=20.0, lev_lo=1.70, lev_hi=1.00,
        base_weights=(0.60, 0.45, 0.45),
        cost_bps_per_leg=0.0002,
    )
    # Recompute regime independently for the numpy reference: it must
    # match the pandas regime exactly because both apply the same lag
    # and the same "bar 0 = VIX[0] bootstrap" convention.
    vix_aligned = vix.reindex(r_eq.index, method="ffill")
    vix_lag = vix_aligned.shift(1)
    vix_lag.iloc[0] = vix_aligned.iloc[0]
    reg_indep = (vix_lag < 20.0).astype(int)
    net_np, _, _ = npref.apply_regime_lev_stack_3leg_np(
        r_eq.to_numpy(), r_bd.to_numpy(), r_gld.to_numpy(),
        reg_indep.to_numpy(),
        lev_lo=1.70, lev_hi=1.00,
        base_weights=(0.60, 0.45, 0.45),
        cost_bps_per_leg=0.0002,
    )
    diff = np.abs(net_pd.to_numpy() - net_np)
    assert diff.max() < 1e-10, f"pandas-vs-numpy max abs diff {diff.max():.2e} > 1e-10"


# ---------------------------------------------------------------------------
# Configuration invariants (run-config pre-commitment)
# ---------------------------------------------------------------------------


def test_iter038_run_config_matches_hypothesis():
    """The pre-committed cfg must use VIX threshold 20, lev_lo 1.70,
    lev_hi 1.00, and base weights (0.60, 0.45, 0.45). No sweep allowed."""
    run = _import_iter038("run_backtests")
    cfg = run.CFG
    assert cfg["cfg_id"] == "regime_lev_vix_lt20_lo10_hi17", (
        f"cfg_id mismatch (locked by hypothesis): {cfg['cfg_id']}"
    )
    assert cfg["threshold"] == 20.0
    assert cfg["lev_lo"] == 1.70
    assert cfg["lev_hi"] == 1.00
    assert cfg["base_weights"] == (0.60, 0.45, 0.45)
    assert run.COST_BPS_PER_LEG == 0.0002


def test_iter038_datasets_match_iter037_windows():
    """Datasets must reuse iter 037's GLD-aligned windows (apples-to-apples)."""
    run = _import_iter038("run_backtests")
    expected = {
        "educational": ("SPY", "IEF", "GLD", "2004-11-19", "2026-04-15"),
        "spy_real":    ("SPY", "IEF", "GLD", "2009-06-25", "2026-04-15"),
        "ndx_real":    ("QQQ", "IEF", "GLD", "2010-02-12", "2026-04-15"),
    }
    for name, (eq, bd, gld, start, end) in expected.items():
        ds = run.DATASETS[name]
        assert ds["equity_symbol"] == eq
        assert ds["bond_symbol"] == bd
        assert ds["gold_symbol"] == gld
        assert ds["start"] == start
        assert ds["end"] == end


# ---------------------------------------------------------------------------
# Validation guards
# ---------------------------------------------------------------------------


def test_negative_lev_raises():
    rls = _import_iter038("regime_lev_stack_3leg")
    r_eq, r_bd, r_gld, vix = _synth_inputs(n=20)
    import pytest
    with pytest.raises(ValueError):
        rls.apply_regime_lev_stack_3leg(
            r_eq, r_bd, r_gld, vix,
            lev_lo=-0.1, lev_hi=1.0,
        )


def test_misaligned_returns_indices_raise():
    rls = _import_iter038("regime_lev_stack_3leg")
    r_eq, r_bd, r_gld, vix = _synth_inputs(n=20)
    import pytest
    with pytest.raises(ValueError):
        rls.apply_regime_lev_stack_3leg(
            r_eq, r_bd.iloc[1:], r_gld, vix,
        )
