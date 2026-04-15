"""Tests for ai_trade.backtest.portfolio.configs."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ai_trade.backtest.portfolio.configs import (
    PortfolioConfig,
    portfolio_configs,
)


def test_portfolio_config_is_frozen():
    cfg = PortfolioConfig(
        clenow_config_id=8,
        ehlers_config_id=6,
        clenow_lookback=75,
        clenow_top_pct=0.20,
        clenow_risk_factor=0.001,
        ehlers_hp=48,
        ehlers_lp=20,
        ehlers_pct_of_dcp=0.80,
        ehlers_stop_pct=0.02,
    )
    with pytest.raises(FrozenInstanceError):
        cfg.clenow_config_id = 999  # type: ignore[misc]


def test_portfolio_configs_returns_9_unique_pairs():
    configs = portfolio_configs()
    assert len(configs) == 9
    # All pairs (clenow_config_id, ehlers_config_id) distinct.
    pairs = [(c.clenow_config_id, c.ehlers_config_id) for c in configs]
    assert len(set(pairs)) == 9


def test_portfolio_configs_top_3_clenow_ids_are_8_19_10():
    """Top-3 by Sharpe from grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md."""
    configs = portfolio_configs()
    clenow_ids = sorted({c.clenow_config_id for c in configs})
    assert clenow_ids == [8, 10, 19]


def test_portfolio_configs_top_3_ehlers_ids_are_6_18_19():
    """Top-3 by Sharpe from grid_ehlers_20260415-1353/diagnostic.md."""
    configs = portfolio_configs()
    ehlers_ids = sorted({c.ehlers_config_id for c in configs})
    assert ehlers_ids == [6, 18, 19]


def test_portfolio_configs_parameter_values_match_reports():
    """Verify the hardcoded parameter values match the reports exactly."""
    configs = portfolio_configs()

    # Pick the (clenow=8, ehlers=6) pair — Sharpe rank 1 × rank 1.
    cfg = next(
        c for c in configs
        if c.clenow_config_id == 8 and c.ehlers_config_id == 6
    )
    # Clenow rank-1 (config_id=8): lookback=75, top_pct=0.20, risk=0.001.
    assert cfg.clenow_lookback == 75
    assert cfg.clenow_top_pct == pytest.approx(0.20)
    assert cfg.clenow_risk_factor == pytest.approx(0.001)
    # Ehlers rank-1 (config_id=6): hp=48, lp=20, pct=0.80, stop=0.02.
    assert cfg.ehlers_hp == 48
    assert cfg.ehlers_lp == 20
    assert cfg.ehlers_pct_of_dcp == pytest.approx(0.80)
    assert cfg.ehlers_stop_pct == pytest.approx(0.02)


def test_clenow_top3_grid_configs_returns_3_ClenowGridConfigs():
    from ai_trade.backtest.grid.config import ClenowGridConfig
    from ai_trade.backtest.portfolio.configs import (
        clenow_top3_grid_configs,
    )
    configs = clenow_top3_grid_configs()
    assert len(configs) == 3
    assert all(isinstance(c, ClenowGridConfig) for c in configs)
    # Rank 1: lookback=75, top_pct=0.20, risk_factor=0.001.
    assert configs[0].lookback_regression == 75
    assert configs[0].top_pct == pytest.approx(0.20)
    assert configs[0].risk_factor == pytest.approx(0.001)


def test_ehlers_top3_grid_configs_returns_3_EhlersGridConfigs():
    from ai_trade.backtest.grid.ehlers_config import EhlersGridConfig
    from ai_trade.backtest.portfolio.configs import (
        ehlers_top3_grid_configs,
    )
    configs = ehlers_top3_grid_configs()
    assert len(configs) == 3
    assert all(isinstance(c, EhlersGridConfig) for c in configs)
    # Rank 1: hp=48, lp=20, pct=0.80, stop=0.02.
    assert configs[0].hp_period == 48
    assert configs[0].lp_period == 20
    assert configs[0].pct_of_dcp == pytest.approx(0.80)
    assert configs[0].stop_pct == pytest.approx(0.02)
