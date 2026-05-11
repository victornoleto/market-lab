"""Tests for build_positions with external_weights (T5d HRP/ERC integration).

Citation: spec §3.3 (docs/specs/2026-05-08-t5-expansion-design.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.strategies.vol_targeted import build_positions


def _frame(value: float, idx, cols):
    return pd.DataFrame(value, index=idx, columns=cols)


def test_external_weights_replaces_idm_uniform_allocation():
    idx = pd.date_range("2010-01-04", periods=20, freq="B")
    pool = ["A", "B", "C", "D"]
    forecasts = _frame(10.0, idx, pool)
    vols = _frame(0.01, idx, pool)
    # Skewed weights favoring asset A
    weights = pd.DataFrame(
        np.tile([0.5, 0.2, 0.2, 0.1], (len(idx), 1)),
        index=idx, columns=pool,
    )
    pos = build_positions(
        forecasts=forecasts, vol_per_asset=vols,
        sigma_target=0.25, idm=1.0, position_inertia=0.0,
        off_asset="OFF", external_weights=weights,
    )
    last = pos.iloc[-1].drop("OFF")
    # Asset A should have largest weight (after renormalization to ≤1)
    assert last["A"] > last["B"]
    assert last["A"] > last["D"]


def test_no_external_weights_matches_baseline_behavior():
    idx = pd.date_range("2010-01-04", periods=20, freq="B")
    pool = ["A", "B", "C"]
    forecasts = _frame(10.0, idx, pool)
    vols = _frame(0.01, idx, pool)
    pos_baseline = build_positions(
        forecasts=forecasts, vol_per_asset=vols, sigma_target=0.25,
        idm=2.5, position_inertia=0.0, off_asset="OFF",
    )
    pos_explicit_none = build_positions(
        forecasts=forecasts, vol_per_asset=vols, sigma_target=0.25,
        idm=2.5, position_inertia=0.0, off_asset="OFF",
        external_weights=None,
    )
    pd.testing.assert_frame_equal(pos_baseline, pos_explicit_none)
