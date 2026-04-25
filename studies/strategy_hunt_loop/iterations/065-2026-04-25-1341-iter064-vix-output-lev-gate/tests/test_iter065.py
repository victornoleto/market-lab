"""TDD tests for iter 065 VIX-conditional output leverage gate.

Verifies:
- No-lookahead (lev[t] uses vix[t-1])
- Stress regime (lev=1.0, no drag, returns unchanged)
- Calm regime (lev=lev_calm, drag = (lev-1)*borrow/252)
- Pandas vs numpy reference parity (G7 prerequisite)
- Pre-VIX warmup handled via bfill
- Input validation (negative lev/threshold/borrow rejected)

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity tests.
* `[advances_fin_ml, p.162-164]` — no-lookahead test for shift(1).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

THIS_DIR = Path(__file__).resolve().parent
ITER_DIR = THIS_DIR.parent
sys.path.insert(0, str(ITER_DIR))

from output_lev_gate import apply_vix_lev_gate
from numpy_reference_iter065 import apply_vix_lev_gate_np


def _make_vix(idx: pd.DatetimeIndex, values: list[float]) -> pd.Series:
    return pd.Series(values, index=idx, name="VIX")


def _make_combined(idx: pd.DatetimeIndex, values: list[float]) -> pd.Series:
    return pd.Series(values, index=idx, name="combined")


@pytest.fixture
def daily_index() -> pd.DatetimeIndex:
    return pd.date_range("2020-01-02", periods=10, freq="B")


def test_lev_unchanged_when_all_vix_above_threshold(daily_index):
    """Stress regime everywhere: lev=1.0, drag=0, output equals input."""
    combined = _make_combined(daily_index, [0.001] * 10)
    vix = _make_vix(daily_index, [25.0] * 10)
    out = apply_vix_lev_gate(
        combined, vix, lev_calm=1.5, lev_stress=1.0,
        vix_threshold=20.0, borrow_annual=0.0225,
    )
    np.testing.assert_array_almost_equal(out.values, combined.values, decimal=15)


def test_lev_calm_scales_and_applies_drag(daily_index):
    """Calm regime everywhere: lev=1.5, drag=0.5*0.0225/252 per bar."""
    combined = _make_combined(daily_index, [0.001] * 10)
    vix = _make_vix(daily_index, [10.0] * 10)
    out = apply_vix_lev_gate(
        combined, vix, lev_calm=1.5, lev_stress=1.0,
        vix_threshold=20.0, borrow_annual=0.0225,
    )
    expected_drag = 0.5 * 0.0225 / 252
    expected = 1.5 * 0.001 - expected_drag
    np.testing.assert_array_almost_equal(
        out.values, np.full(10, expected), decimal=15,
    )


def test_no_lookahead_uses_vix_t_minus_1(daily_index):
    """lev[t] depends on VIX[t-1] only, not VIX[t]."""
    combined = _make_combined(daily_index, [0.001] * 10)
    # Construct VIX so that day 5 has VIX=10 (calm) and day 4 has VIX=30
    # (stress). Day 5's lev should reflect day 4's VIX (stress → lev=1.0),
    # NOT day 5's own VIX.
    vix_values = [15.0] * 10
    vix_values[4] = 30.0  # stress on day 4
    vix_values[5] = 10.0  # calm on day 5
    vix = _make_vix(daily_index, vix_values)
    out = apply_vix_lev_gate(
        combined, vix, lev_calm=1.5, lev_stress=1.0,
        vix_threshold=20.0, borrow_annual=0.0225,
    )
    # Day 5's lev = stress (because VIX[t-1]=VIX[day 4]=30 ≥ 20).
    expected_day5 = 1.0 * 0.001 - 0.0
    assert abs(out.iloc[5] - expected_day5) < 1e-15
    # Day 4's lev = calm (because VIX[t-1]=VIX[day 3]=15 < 20).
    expected_day4 = 1.5 * 0.001 - (0.5 * 0.0225 / 252)
    assert abs(out.iloc[4] - expected_day4) < 1e-15


def test_warmup_bfill_seeds_bar_0(daily_index):
    """Bar 0 has no t-1 — seeded via bfill from VIX[0]."""
    combined = _make_combined(daily_index, [0.001] * 10)
    vix_values = [10.0] + [25.0] * 9  # bar 0 calm, 1-9 stress
    vix = _make_vix(daily_index, vix_values)
    out = apply_vix_lev_gate(
        combined, vix, lev_calm=1.5, lev_stress=1.0,
        vix_threshold=20.0, borrow_annual=0.0225,
    )
    # Bar 0: lev[0] uses bfill seed (VIX[0]=10 < 20 → calm).
    expected_bar0 = 1.5 * 0.001 - (0.5 * 0.0225 / 252)
    assert abs(out.iloc[0] - expected_bar0) < 1e-15


def test_g7_parity_pandas_vs_numpy(daily_index):
    """Pandas vs numpy reference produce identical values."""
    rng = np.random.default_rng(42)
    combined = _make_combined(daily_index, rng.normal(0.0005, 0.012, size=10).tolist())
    vix_values = rng.uniform(8.0, 35.0, size=10).tolist()
    vix = _make_vix(daily_index, vix_values)
    out_pd = apply_vix_lev_gate(
        combined, vix, lev_calm=1.5, lev_stress=1.0,
        vix_threshold=20.0, borrow_annual=0.0225,
    )
    # Replicate the pandas alignment (reindex+ffill+bfill+shift(1)+bfill)
    vix_aligned = vix.reindex(combined.index).ffill().bfill().to_numpy()
    out_np = apply_vix_lev_gate_np(
        combined.to_numpy(), vix_aligned,
        lev_calm=1.5, lev_stress=1.0,
        vix_threshold=20.0, borrow_annual=0.0225,
    )
    np.testing.assert_array_almost_equal(out_pd.values, out_np, decimal=15)


def test_g7_parity_realistic_window():
    """Larger realistic window — pandas vs numpy parity."""
    idx = pd.date_range("2010-01-04", periods=500, freq="B")
    rng = np.random.default_rng(7)
    combined = _make_combined(idx, rng.normal(0.0006, 0.011, size=500).tolist())
    vix = _make_vix(idx, rng.uniform(10.0, 40.0, size=500).tolist())
    out_pd = apply_vix_lev_gate(
        combined, vix, lev_calm=1.5, lev_stress=1.0,
        vix_threshold=20.0, borrow_annual=0.0225,
    )
    vix_aligned = vix.reindex(combined.index).ffill().bfill().to_numpy()
    out_np = apply_vix_lev_gate_np(
        combined.to_numpy(), vix_aligned,
        lev_calm=1.5, lev_stress=1.0,
        vix_threshold=20.0, borrow_annual=0.0225,
    )
    max_diff = float(np.max(np.abs(out_pd.values - out_np)))
    assert max_diff < 1e-15, f"max diff {max_diff} ≥ 1e-15"


def test_invalid_inputs_raise(daily_index):
    """Negative lev / threshold / borrow / too-short input → ValueError."""
    combined = _make_combined(daily_index, [0.001] * 10)
    vix = _make_vix(daily_index, [15.0] * 10)
    with pytest.raises(ValueError, match="lev_calm"):
        apply_vix_lev_gate(combined, vix, lev_calm=-0.1)
    with pytest.raises(ValueError, match="lev_stress"):
        apply_vix_lev_gate(combined, vix, lev_stress=-0.1)
    with pytest.raises(ValueError, match="vix_threshold"):
        apply_vix_lev_gate(combined, vix, vix_threshold=-1.0)
    with pytest.raises(ValueError, match="borrow_annual"):
        apply_vix_lev_gate(combined, vix, borrow_annual=-0.001)
    too_short = _make_combined(daily_index[:1], [0.001])
    too_short_vix = _make_vix(daily_index[:1], [15.0])
    with pytest.raises(ValueError, match="≥ 2"):
        apply_vix_lev_gate(too_short, too_short_vix)


def test_vix_no_overlap_raises():
    """VIX completely disjoint from combined → ValueError."""
    idx_combined = pd.date_range("2020-01-02", periods=10, freq="B")
    idx_vix = pd.date_range("2025-01-02", periods=10, freq="B")
    combined = _make_combined(idx_combined, [0.001] * 10)
    vix = _make_vix(idx_vix, [15.0] * 10)
    with pytest.raises(ValueError, match="overlap"):
        apply_vix_lev_gate(combined, vix)


def test_average_lev_with_70_percent_calm(daily_index):
    """With ~70% calm bars, average effective lev ≈ 1.35× (1.5*.7 + 1.0*.3)."""
    rng = np.random.default_rng(13)
    combined = _make_combined(daily_index, rng.normal(0.0005, 0.011, size=10).tolist())
    # 7 calm + 3 stress
    vix_values = [10.0] * 7 + [25.0] * 3
    vix = _make_vix(daily_index, vix_values)
    out = apply_vix_lev_gate(
        combined, vix, lev_calm=1.5, lev_stress=1.0,
        vix_threshold=20.0, borrow_annual=0.0,  # zero borrow for clean check
    )
    # Bar 0 uses VIX[0]=10 (calm → lev=1.5)
    # Bar 1 uses VIX[0]=10 (calm) ... actually bar t uses VIX[t-1]
    # vix[0]=10 (calm), vix[1..6]=10 (calm), vix[7..9]=25 (stress)
    # lev_lag aligned: lev_t uses vix[t-1] (with bfill: vix_lag[0]=vix[0]=10)
    # vix_lag = [10, 10, 10, 10, 10, 10, 10, 10, 25, 25] (8 calm, 2 stress)
    expected_lev = np.array([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.0, 1.0])
    expected_out = expected_lev * combined.to_numpy() - 0.0
    np.testing.assert_array_almost_equal(out.values, expected_out, decimal=15)
