"""Tests for signals_carry (Carver per-asset carry forecast).

Citation: spec §3.1 (docs/specs/2026-05-08-t5-expansion-design.md);
[systematic_trading, ch.9 p.180-190].
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from studies.letf_rotation_hunt.core import signals_carry as sc


def _const_series(value: float, n: int = 500) -> pd.Series:
    return pd.Series(value, index=pd.date_range("2010-01-04", periods=n, freq="B"))


def test_equity_carry_positive_when_div_yield_exceeds_financing(monkeypatch):
    # SPY div yield 2% (annual), FFR 0.5% annual → 0.005/252 daily.
    # UPRO leverage 3 → carry_raw = 0.02 - 3*0.005 = +0.005 → positive forecast.
    monkeypatch.setattr(
        sc, "_load_yield_for_asset",
        lambda asset: _const_series(0.02),
    )
    ffr = _const_series(0.005 / 252.0)
    prices = _const_series(100.0)
    f = sc.compute_carry_forecast("UPRO", prices, ffr)
    assert (f.dropna() > 0).all(), "expected positive forecast when div yield > 3*FFR"


def test_equity_carry_negative_when_financing_exceeds_div_yield(monkeypatch):
    # Div yield 1% annual, FFR 5% annual = 0.05/252 daily, leverage 3 → carry_raw = 0.01 - 0.15 < 0.
    monkeypatch.setattr(
        sc, "_load_yield_for_asset",
        lambda asset: _const_series(0.01),
    )
    ffr = _const_series(0.05 / 252.0)  # high rate regime
    prices = _const_series(100.0)
    f = sc.compute_carry_forecast("UPRO", prices, ffr)
    assert (f.dropna() < 0).all(), "expected negative forecast when 3*FFR > div yield"


def test_carry_clipped_at_pm_20(monkeypatch):
    monkeypatch.setattr(
        sc, "_load_yield_for_asset",
        lambda asset: _const_series(0.50),
    )
    ffr = _const_series(0.0)
    prices = _const_series(100.0)
    f = sc.compute_carry_forecast("UPRO", prices, ffr).dropna()
    assert (f.abs() <= 20.0).all()


def test_bond_carry_uses_30y_cmt(monkeypatch):
    monkeypatch.setattr(
        sc, "_load_yield_for_asset",
        lambda asset: _const_series(0.045),  # 30y at 4.5%
    )
    # FFR 0.5% annual → 0.005/252 daily (matches Task 4 daily-FFR convention)
    ffr = _const_series(0.005 / 252.0)
    prices = _const_series(100.0)
    f = sc.compute_carry_forecast("TMF", prices, ffr)
    # carry_raw = 0.045 - 3*0.005 = 0.030 > 0 → forecast positive
    assert (f.dropna() > 0).all()


def test_gold_carry_returns_zero():
    prices = _const_series(100.0)
    ffr = _const_series(0.02 / 252.0)
    f = sc.compute_carry_forecast("UGL", prices, ffr)
    assert (f == 0.0).all()


def test_unknown_asset_raises():
    prices = _const_series(100.0)
    ffr = _const_series(0.01 / 252.0)
    with pytest.raises(ValueError, match="not in carry map"):
        sc.compute_carry_forecast("XYZ", prices, ffr)


def test_compose_ewmac_carry_50_50_blend_with_fdm():
    idx = pd.date_range("2010-01-04", periods=10, freq="B")
    ewmac = pd.Series(10.0, index=idx)
    carry = pd.Series(2.0, index=idx)
    composed = sc.compose_ewmac_carry(ewmac, carry, fdm=1.41)
    expected = ((10.0 + 2.0) / 2.0) * 1.41  # = 8.46
    np.testing.assert_allclose(composed.values, expected, rtol=1e-9)


def test_compose_ewmac_carry_clipped_at_pm_20():
    idx = pd.date_range("2010-01-04", periods=5, freq="B")
    ewmac = pd.Series(20.0, index=idx)
    carry = pd.Series(20.0, index=idx)
    composed = sc.compose_ewmac_carry(ewmac, carry, fdm=2.0)
    # ((20+20)/2)*2 = 40 → clip to 20
    assert (composed == 20.0).all()
