"""Unit tests for strategies/single_letf_gayed.py per spec §2.2 T1."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_gayed_binary_rotation_basic():
    """ON when signal=1: hold LETF; OFF when signal=0: hold OFF asset."""
    from studies.letf_rotation_hunt.strategies.single_letf_gayed import build_positions

    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    signal = pd.Series([1, 1, 1, 0, 0, 0, 1, 1, 0, 0], index=dates).astype(float)

    positions = build_positions(
        signal=signal,
        on_asset="UPRO",
        off_asset="BIL",
    )

    # ON days: 100% UPRO, 0% BIL
    assert positions.loc[dates[0], "UPRO"] == 1.0
    assert positions.loc[dates[0], "BIL"] == 0.0
    # OFF days: 100% BIL
    assert positions.loc[dates[3], "UPRO"] == 0.0
    assert positions.loc[dates[3], "BIL"] == 1.0


def test_gayed_weights_sum_to_one():
    """All daily weights sum to 1.0 ± 1e-6."""
    from studies.letf_rotation_hunt.strategies.single_letf_gayed import build_positions

    dates = pd.date_range("2020-01-01", periods=20, freq="B")
    signal = pd.Series(np.random.RandomState(42).choice([0, 1], 20), index=dates).astype(float)

    positions = build_positions(signal=signal, on_asset="UPRO", off_asset="BIL")
    sums = positions.sum(axis=1)
    assert sums.sub(1.0).abs().max() < 1e-6


def test_gayed_warmup_nan_skipped():
    """NaN signal during warmup → 100% OFF asset (defensive)."""
    from studies.letf_rotation_hunt.strategies.single_letf_gayed import build_positions

    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    signal = pd.Series([np.nan, np.nan, np.nan, 1, 1, 1, 0, 0, 1, 1], index=dates)

    positions = build_positions(signal=signal, on_asset="UPRO", off_asset="BIL")

    # Warmup: 100% OFF
    assert positions.iloc[0]["BIL"] == 1.0
    assert positions.iloc[0]["UPRO"] == 0.0
    # Post-warmup: per signal
    assert positions.iloc[3]["UPRO"] == 1.0
