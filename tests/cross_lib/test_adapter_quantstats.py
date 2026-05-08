"""Unit tests for quantstats adapter."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

qs = pytest.importorskip("quantstats")

from studies._archive.phase_3_5c.reports.cross_lib.adapters.quantstats_adapter import (
    QuantstatsAdapter,
)
from studies._archive.phase_3_5c.reports.cross_lib.types import (
    LegConfig,
    RebalanceConfig,
    VariantConfig,
)


def _variant() -> VariantConfig:
    return VariantConfig(
        variant_id="leg_sso_only",
        family="plano_b",
        execution_model="letf_synthetic",
        legs=(LegConfig("ema_regime", {"lookback": 100}, "SPY", "SSO"),),
        rebalance=RebalanceConfig(mode="daily", threshold_pp=None),
        target_weights=(1.0,),
        windows=(("2020-01-01", "2020-12-31"),),
    )


def test_run_on_equity_returns_finite() -> None:
    eq = pd.Series(
        np.cumprod(1 + np.random.RandomState(42).normal(0.0005, 0.01, 252)),
        index=pd.date_range("2020-01-01", periods=252, freq="B"),
    )
    adapter = QuantstatsAdapter()
    result = adapter.run_on_equity(_variant(), ("2020-01-01", "2020-12-31"), 1, eq, "synthetic")
    assert result.outcome == "OK"
    assert np.isfinite(result.cagr)
    assert np.isfinite(result.sharpe)


def test_run_standalone_is_data_unavailable() -> None:
    result = QuantstatsAdapter().run(_variant(), ("2020-01-01", "2020-12-31"), 1)
    assert result.outcome == "DATA_UNAVAILABLE"
