"""Tests for VolTargetSizer [systematic_trading, p.144, p.159, ch.9-10]."""
from __future__ import annotations
import logging
import pytest
from ai_trade.backtest.strategies.vol_expansion_breakout import VolTargetSizer


def test_sizer_canonical_carver_formula() -> None:
    sizer = VolTargetSizer(target_vol_annual=0.10)
    notional, shares = sizer.size(equity=100_000.0, sigma_yz_annual=0.20, entry_price=500.0)
    assert notional == pytest.approx(50_000.0)
    assert shares == pytest.approx(100.0)


def test_sizer_sigma_floor_zero_returns_zero(caplog) -> None:
    sizer = VolTargetSizer(target_vol_annual=0.10)
    with caplog.at_level(logging.WARNING):
        notional, shares = sizer.size(equity=100_000.0, sigma_yz_annual=1e-9, entry_price=500.0)
    assert notional == 0.0
    assert shares == 0.0
    assert any("sigma" in rec.message.lower() for rec in caplog.records)


def test_sizer_consumes_annualized_input_directly() -> None:
    sizer = VolTargetSizer(target_vol_annual=0.10)
    n1, _ = sizer.size(equity=100_000.0, sigma_yz_annual=0.20, entry_price=100.0)
    n2, _ = sizer.size(equity=100_000.0, sigma_yz_annual=0.40, entry_price=100.0)
    assert n2 == pytest.approx(n1 / 2.0)


def test_sizer_equity_scaling_linear() -> None:
    sizer = VolTargetSizer(target_vol_annual=0.10)
    n1, _ = sizer.size(equity=100_000.0, sigma_yz_annual=0.20, entry_price=100.0)
    n2, _ = sizer.size(equity=200_000.0, sigma_yz_annual=0.20, entry_price=100.0)
    assert n2 == pytest.approx(n1 * 2.0)


def test_sizer_shares_scales_inversely_with_price() -> None:
    sizer = VolTargetSizer(target_vol_annual=0.10)
    _, sh1 = sizer.size(equity=100_000.0, sigma_yz_annual=0.20, entry_price=100.0)
    _, sh2 = sizer.size(equity=100_000.0, sigma_yz_annual=0.20, entry_price=200.0)
    assert sh2 == pytest.approx(sh1 / 2.0)
