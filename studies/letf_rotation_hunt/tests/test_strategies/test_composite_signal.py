"""Unit tests for strategies/composite_signal.py per spec §2.4 T3."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_composite_basket_with_continuous_weight():
    """Composite signal can produce continuous weight (e.g., VIX scaling)."""
    from studies.letf_rotation_hunt.core.strategies.composite_signal import build_positions

    dates = pd.date_range("2020-01-01", periods=4, freq="B")
    # Continuous weight 0.5 → 50% basket, 50% off
    weight = pd.Series([1.0, 0.5, 0.0, 0.0], index=dates)

    positions = build_positions(
        weight=weight,
        on_basket={"UPRO": 0.55, "TMF": 0.45},
        off_asset="BIL",
    )

    # weight=1.0: full basket
    assert positions.iloc[0]["UPRO"] == pytest.approx(0.55)
    assert positions.iloc[0]["TMF"] == pytest.approx(0.45)
    assert positions.iloc[0]["BIL"] == 0.0

    # weight=0.5: half basket, half cash
    assert positions.iloc[1]["UPRO"] == pytest.approx(0.275)
    assert positions.iloc[1]["TMF"] == pytest.approx(0.225)
    assert positions.iloc[1]["BIL"] == pytest.approx(0.5)

    # weight=0: full cash
    assert positions.iloc[2]["UPRO"] == 0.0
    assert positions.iloc[2]["BIL"] == 1.0


def test_composite_weights_sum_to_one():
    """All composite weights sum to 1.0."""
    from studies.letf_rotation_hunt.core.strategies.composite_signal import build_positions

    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    rng = np.random.RandomState(42)
    weight = pd.Series(rng.uniform(0, 1, 10), index=dates)

    positions = build_positions(
        weight=weight,
        on_basket={"UPRO": 0.55, "TMF": 0.45},
        off_asset="BIL",
    )
    sums = positions.sum(axis=1)
    assert sums.sub(1.0).abs().max() < 1e-6
