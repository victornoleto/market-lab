"""Tests for YangZhangCone + RegimeReading [volatility_trading, p.22-23, p.58-60]."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.vol_expansion_breakout import (
    RegimeReading,
    YangZhangCone,
)


def test_regime_reading_dataclass_fields() -> None:
    r = RegimeReading(
        is_quiet=True,
        sigma_yz_annual=0.20,
        sigma_yz_percentile=12.0,
        bars_in_history=1700,
    )
    assert r.is_quiet is True
    assert r.sigma_yz_annual == pytest.approx(0.20)
    assert r.sigma_yz_percentile == pytest.approx(12.0)
    assert r.bars_in_history == 1700
