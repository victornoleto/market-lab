"""Unit tests for backtrader adapter."""
from __future__ import annotations

import pytest

backtrader = pytest.importorskip("backtrader")

from reports.phase_3_5c.cross_lib.adapters.backtrader_adapter import (
    BacktraderAdapter,
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
    result = BacktraderAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.outcome == "OK"
    assert result.lib == "backtrader"
    assert len(result.equity_curve) > 100


def test_adapter_sharpe_not_zero() -> None:
    result = BacktraderAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert abs(result.sharpe) > 0.01


def test_adapter_skipped_when_bt_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "backtrader", None)
    result = BacktraderAdapter().run(_leg_variant(), SHORT_WINDOW, stage=1)
    assert result.outcome in ("SKIPPED", "ERROR")
