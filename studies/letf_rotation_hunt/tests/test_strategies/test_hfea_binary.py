"""Unit tests for strategies/hfea_binary.py per spec §2.3 T2."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_hfea_classic_full_off():
    """HFEA classic 55/45 UPRO+TMF, full-off mode → 100% cash when signal=0."""
    from studies.letf_rotation_hunt.core.strategies.hfea_binary import build_positions

    dates = pd.date_range("2020-01-01", periods=4, freq="B")
    signal = pd.Series([1, 1, 0, 0], index=dates).astype(float)

    positions = build_positions(
        signal=signal,
        on_basket={"UPRO": 0.55, "TMF": 0.45},
        off_asset="BIL",
        off_mode="full_off",
    )

    # ON: 55% UPRO, 45% TMF, 0% BIL
    assert positions.iloc[0]["UPRO"] == pytest.approx(0.55)
    assert positions.iloc[0]["TMF"] == pytest.approx(0.45)
    assert positions.iloc[0]["BIL"] == 0.0

    # OFF: 100% BIL
    assert positions.iloc[2]["UPRO"] == 0.0
    assert positions.iloc[2]["TMF"] == 0.0
    assert positions.iloc[2]["BIL"] == 1.0


def test_hfea_half_off_keeps_bond_sleeve():
    """HFEA half-off: zero LETF, KEEP bond sleeve when signal=0."""
    from studies.letf_rotation_hunt.core.strategies.hfea_binary import build_positions

    dates = pd.date_range("2020-01-01", periods=4, freq="B")
    signal = pd.Series([1, 1, 0, 0], index=dates).astype(float)

    positions = build_positions(
        signal=signal,
        on_basket={"UPRO": 0.55, "TMF": 0.45},
        off_asset="BIL",
        off_mode="half_off",
        bond_sleeve_assets=["TMF"],  # bond sleeve remains during off
    )

    # ON: 55% UPRO, 45% TMF
    assert positions.iloc[0]["UPRO"] == pytest.approx(0.55)
    assert positions.iloc[0]["TMF"] == pytest.approx(0.45)

    # OFF half-off: 0% UPRO, 100% TMF (keep bond sleeve at full weight)
    assert positions.iloc[2]["UPRO"] == 0.0
    assert positions.iloc[2]["TMF"] == 1.0
    assert positions.iloc[2]["BIL"] == 0.0


def test_hfea_basket_weights_must_sum_to_one():
    """Invalid basket → raises ValueError."""
    from studies.letf_rotation_hunt.core.strategies.hfea_binary import build_positions

    dates = pd.date_range("2020-01-01", periods=2, freq="B")
    signal = pd.Series([1, 1], index=dates).astype(float)

    with pytest.raises(ValueError, match="weights must sum to 1.0"):
        build_positions(
            signal=signal,
            on_basket={"UPRO": 0.5, "TMF": 0.4},  # sums to 0.9
            off_asset="BIL",
        )
