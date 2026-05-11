"""Unit tests for strategies/cross_sectional.py per spec §2.5 T4."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_top_k_selection():
    """Pick top-K by ranking score."""
    from studies.letf_rotation_hunt.core.strategies.cross_sectional import build_positions

    dates = pd.date_range("2020-01-01", periods=2, freq="B")
    # 4 assets, scores per day
    scores = pd.DataFrame(
        {"UPRO": [1.0, 0.5], "QLD": [0.5, 1.0], "UGL": [0.2, 0.8], "TMF": [0.1, 0.0]},
        index=dates,
    )
    # Master gate: SPY > SMA200 (always ON for this test)
    master_gate = pd.Series([1, 1], index=dates).astype(float)

    positions = build_positions(
        scores=scores,
        master_gate=master_gate,
        top_k=2,
        off_asset="BIL",
    )

    # Day 0: top-2 = UPRO + QLD (scores 1.0, 0.5) → 50/50
    assert positions.iloc[0]["UPRO"] == pytest.approx(0.5)
    assert positions.iloc[0]["QLD"] == pytest.approx(0.5)
    assert positions.iloc[0]["UGL"] == 0.0
    assert positions.iloc[0]["TMF"] == 0.0
    assert positions.iloc[0]["BIL"] == 0.0

    # Day 1: top-2 = QLD + UGL (scores 1.0, 0.8) → 50/50
    assert positions.iloc[1]["QLD"] == pytest.approx(0.5)
    assert positions.iloc[1]["UGL"] == pytest.approx(0.5)


def test_master_gate_off_holds_cash():
    """When master_gate=0 (SPY < SMA200): hold cash."""
    from studies.letf_rotation_hunt.core.strategies.cross_sectional import build_positions

    dates = pd.date_range("2020-01-01", periods=2, freq="B")
    scores = pd.DataFrame(
        {"UPRO": [1.0, 0.5], "QLD": [0.5, 1.0], "UGL": [0.2, 0.8], "TMF": [0.1, 0.0]},
        index=dates,
    )
    master_gate = pd.Series([1, 0], index=dates).astype(float)

    positions = build_positions(
        scores=scores,
        master_gate=master_gate,
        top_k=2,
        off_asset="BIL",
    )

    # Day 1: master_gate=0 → 100% BIL
    assert positions.iloc[1]["BIL"] == 1.0
    assert positions.iloc[1]["UPRO"] == 0.0
