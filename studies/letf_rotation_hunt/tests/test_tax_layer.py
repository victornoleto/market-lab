"""Unit tests for tax_layer.py — wrapper over studies/_shared/tax_engine.py."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_apply_annual_darf_15pct():
    """Annual realize: 15% on realized gains per year (Lei 14.754)."""
    from studies.letf_rotation_hunt.core.tax_layer import apply_annual_darf

    dates = pd.date_range("2020-01-01", periods=252 * 2, freq="B")
    returns = pd.Series([0.001] * len(dates), index=dates)
    initial = 10000.0
    gross_equity = (1 + returns).cumprod() * initial

    net_equity = apply_annual_darf(gross_equity, returns, mode="annual_realize", initial=initial)

    # Net should be ≤ gross (DARF is a drag)
    assert net_equity.iloc[-1] < gross_equity.iloc[-1]
    # Gap should be roughly 15% of gross gains (tighter now that first-year base bug is fixed)
    gross_gain = gross_equity.iloc[-1] - initial
    net_gain = net_equity.iloc[-1] - initial
    drag_ratio = (gross_gain - net_gain) / gross_gain
    assert 0.13 < drag_ratio < 0.17  # tighter range: ~15% of gross gain


def test_apply_buyhold_zero_intra_year_tax():
    """Buy-hold mode: zero tax until terminal liquidation."""
    from studies.letf_rotation_hunt.core.tax_layer import apply_annual_darf

    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    returns = pd.Series([0.001] * len(dates), index=dates)
    initial = 10000.0
    gross_equity = (1 + returns).cumprod() * initial

    net_equity = apply_annual_darf(gross_equity, returns, mode="buy_hold_terminal", initial=initial)

    # Pre-terminal: net == gross
    assert net_equity.iloc[-2] == pytest.approx(gross_equity.iloc[-2], rel=1e-6)
    # Terminal: 15% on full gain from true initial
    expected_terminal = 0.85 * gross_equity.iloc[-1] + 0.15 * initial
    assert net_equity.iloc[-1] == pytest.approx(expected_terminal, rel=1e-6)


def test_apply_annual_darf_unknown_mode_raises():
    """Unknown mode raises ValueError."""
    from studies.letf_rotation_hunt.core.tax_layer import apply_annual_darf

    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    returns = pd.Series([0.001] * 10, index=dates)
    gross_equity = (1 + returns).cumprod() * 10000

    with pytest.raises(ValueError, match="Unknown mode"):
        apply_annual_darf(gross_equity, returns, mode="invalid", initial=10000.0)
