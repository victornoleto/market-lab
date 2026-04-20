"""Tests for cross-lib core types."""
from __future__ import annotations

import pandas as pd
import pytest

from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    Outcome,
    RebalanceConfig,
    RunResult,
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


def test_run_result_ok_outcome() -> None:
    eq = pd.Series(
        [1.0, 1.01, 1.02], index=pd.date_range("2020-01-01", periods=3, freq="D")
    )
    mr = pd.Series([0.01, 0.01], index=pd.date_range("2020-01-31", periods=2, freq="ME"))
    result = RunResult(
        variant_id="x",
        lib="bt",
        window=("2020-01-01", "2020-12-31"),
        stage=1,
        equity_curve=eq,
        monthly_returns=mr,
        trade_dates=[pd.Timestamp("2020-03-01")],
        cagr=0.25,
        sharpe=1.5,
        max_dd=-0.10,
        wf_splits_8=[1.4, 1.5, 1.6, 1.5, 1.4, 1.5, 1.6, 1.5],
        dsr_pval=0.02,
        outcome="OK",
        error_detail=None,
    )
    assert result.outcome == "OK"
    assert len(result.wf_splits_8) == 8


def test_run_result_skipped_outcome() -> None:
    eq = pd.Series(dtype=float)
    result = RunResult(
        variant_id="x",
        lib="bt",
        window=("2020-01-01", "2020-12-31"),
        stage=1,
        equity_curve=eq,
        monthly_returns=eq,
        trade_dates=[],
        cagr=float("nan"),
        sharpe=float("nan"),
        max_dd=float("nan"),
        wf_splits_8=[],
        dsr_pval=float("nan"),
        outcome="SKIPPED",
        error_detail="bt not installed",
    )
    assert result.outcome == "SKIPPED"
    assert result.error_detail == "bt not installed"


def test_outcome_literal_values() -> None:
    allowed: tuple[Outcome, ...] = ("OK", "SKIPPED", "DATA_UNAVAILABLE", "ERROR")
    assert len(allowed) == 4
