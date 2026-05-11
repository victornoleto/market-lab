"""Unit tests for strategies/vol_targeted.py per spec §2.6 T5."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_carver_position_basic():
    """Carver position = vol_scalar × forecast / 10."""
    from studies.letf_rotation_hunt.core.strategies.vol_targeted import build_positions

    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    # Forecasts in [-20, +20]
    forecasts = pd.DataFrame(
        {"UPRO": [10.0] * 10, "QLD": [5.0] * 10, "UGL": [-5.0] * 10},
        index=dates,
    )
    # Daily vol of returns ~1%
    vol_per_asset = pd.DataFrame(
        {"UPRO": [0.01] * 10, "QLD": [0.012] * 10, "UGL": [0.008] * 10},
        index=dates,
    )

    positions = build_positions(
        forecasts=forecasts,
        vol_per_asset=vol_per_asset,
        sigma_target=0.25,
        idm=1.5,
        position_inertia=0.1,
        off_asset="BIL",
    )

    # Sanity: positive forecast → long position; negative forecast → 0 (long-only)
    assert positions["UGL"].sum() == 0.0  # negative forecast → no long position
    assert positions["UPRO"].iloc[-1] > 0  # positive → long


def test_carver_weights_sum_to_one():
    """Total weights (long + cash) sum to 1.0."""
    from studies.letf_rotation_hunt.core.strategies.vol_targeted import build_positions

    dates = pd.date_range("2020-01-01", periods=5, freq="B")
    forecasts = pd.DataFrame(
        {"UPRO": [10.0] * 5, "TMF": [5.0] * 5},
        index=dates,
    )
    vol_per_asset = pd.DataFrame(
        {"UPRO": [0.01] * 5, "TMF": [0.015] * 5},
        index=dates,
    )

    positions = build_positions(
        forecasts=forecasts,
        vol_per_asset=vol_per_asset,
        sigma_target=0.25,
        idm=1.5,
        position_inertia=0.1,
        off_asset="BIL",
    )
    sums = positions.sum(axis=1)
    assert sums.sub(1.0).abs().max() < 1e-6
