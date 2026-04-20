"""Tests for cross-lib core types."""
from __future__ import annotations

import pytest

from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)


def test_leg_config_ema_regime() -> None:
    leg = LegConfig(
        signal_type="ema_regime",
        signal_params={"lookback": 100},
        signal_ticker="SPY",
        execution_ticker="SSO",
    )
    assert leg.signal_type == "ema_regime"
    assert leg.signal_params["lookback"] == 100
    assert leg.signal_ticker == "SPY"
    assert leg.execution_ticker == "SSO"


def test_leg_config_donchian() -> None:
    leg = LegConfig(
        signal_type="donchian",
        signal_params={"entry": 20, "exit": 10},
        signal_ticker="QQQ",
        execution_ticker="QLD",
    )
    assert leg.signal_params == {"entry": 20, "exit": 10}


def test_rebalance_threshold_requires_pp() -> None:
    with pytest.raises(ValueError, match="threshold_pp required"):
        RebalanceConfig(mode="threshold", threshold_pp=None)


def test_rebalance_daily_no_pp() -> None:
    rb = RebalanceConfig(mode="daily", threshold_pp=None)
    assert rb.mode == "daily"


def test_variant_config_plano_b_v4() -> None:
    variant = VariantConfig(
        variant_id="plano_b_v4_threshold_10",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(
            LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),
            LegConfig("donchian", {"entry": 20, "exit": 10}, "QQQ", "QLD"),
            LegConfig("donchian", {"entry": 40, "exit": 20}, "GLD", "UGL"),
        ),
        rebalance=RebalanceConfig(mode="threshold", threshold_pp=10.0),
        target_weights=(1 / 3, 1 / 3, 1 / 3),
        windows=(("2004-10-01", "2026-04-18"), ("1986-01-02", "2026-04-18")),
    )
    assert variant.family == "plano_b"
    assert len(variant.legs) == 3
    assert sum(variant.target_weights) == pytest.approx(1.0)


def test_variant_config_is_frozen() -> None:
    variant = VariantConfig(
        variant_id="x",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(),
        windows=(),
    )
    with pytest.raises(AttributeError):
        variant.variant_id = "y"  # type: ignore[misc]
