"""Unit tests for synths.py — FFR-aware LETF synth wrappers per spec §4.2."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_letf_synth_basic_2x():
    """Basic 2× LETF: 2 × underlying - ER/252 - (L-1) × (FFR + spread)/252."""
    from studies.letf_rotation_hunt.synths import letf_synth_returns

    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    underlying_returns = pd.Series([0.01] * 10, index=dates)  # 1% daily
    ffr_returns = pd.Series([0.0001] * 10, index=dates)  # ~2.5% annual / 252

    synth_2x = letf_synth_returns(
        underlying_returns,
        leverage=2.0,
        expense_ratio_annual=0.0091,  # UPRO ER
        ffr_daily=ffr_returns,
        ffr_spread_annual=0.004,
    )

    # Daily: 2 * 0.01 - 0.0091/252 - 1 * (0.0001 + 0.004/252) ≈ 0.0199...
    expected_daily = 2 * 0.01 - 0.0091 / 252 - 1 * (0.0001 + 0.004 / 252)
    assert synth_2x.iloc[0] == pytest.approx(expected_daily, abs=1e-7)


def test_letf_synth_3x_higher_borrow():
    """3× LETF has 2× the borrow cost vs 2×."""
    from studies.letf_rotation_hunt.synths import letf_synth_returns

    dates = pd.date_range("2020-01-01", periods=5, freq="B")
    underlying_returns = pd.Series([0.0] * 5, index=dates)  # zero return → isolate cost
    ffr_returns = pd.Series([0.0001] * 5, index=dates)

    synth_2x = letf_synth_returns(underlying_returns, leverage=2.0,
                                   expense_ratio_annual=0.0091,
                                   ffr_daily=ffr_returns, ffr_spread_annual=0.004)
    synth_3x = letf_synth_returns(underlying_returns, leverage=3.0,
                                   expense_ratio_annual=0.0091,
                                   ffr_daily=ffr_returns, ffr_spread_annual=0.004)

    # 3× should have 2× the borrow cost (L-1 = 2 vs 1) → more negative
    assert synth_3x.iloc[0] < synth_2x.iloc[0]
