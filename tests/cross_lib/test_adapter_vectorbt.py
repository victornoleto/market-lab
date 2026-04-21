"""Unit tests for vectorbt adapter."""
from __future__ import annotations

import pytest

vbt = pytest.importorskip("vectorbt")

from reports.phase_3_5c.cross_lib.adapters.vectorbt_adapter import (
    VectorbtAdapter,
)
from reports.phase_3_5c.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)

SHORT_WINDOW = ("2020-01-01", "2020-12-31")


def _leg_variant() -> VariantConfig:
    return VariantConfig(
        variant_id="leg_sso_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(SHORT_WINDOW,),
    )


def test_adapter_returns_run_result() -> None:
    result = VectorbtAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.outcome == "OK"
    assert result.lib == "vectorbt"
    assert result.cagr == result.cagr
    assert len(result.equity_curve) > 100


def test_adapter_sharpe_is_finite() -> None:
    result = VectorbtAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.sharpe == result.sharpe  # not NaN


def test_adapter_skipped_when_vbt_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "vectorbt", None)
    result = VectorbtAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.outcome in ("SKIPPED", "ERROR")


def test_3leg_portfolio_runs() -> None:
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
        windows=(SHORT_WINDOW,),
    )
    result = VectorbtAdapter().run(variant, SHORT_WINDOW, stage=1)
    assert result.outcome == "OK"
    assert len(result.equity_curve) > 100
