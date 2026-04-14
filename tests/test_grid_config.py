"""Tests for ``ai_trade.backtest.grid.config`` — parameter grid definitions.

The grid is the cartesian product of three Clenow parameters that are
defensible to vary per ``[stocks_on_the_move, p.73, p.95, p.88]``:

* ``lookback_regression`` ∈ {60, 75, 90, 105, 120}
* ``top_pct`` ∈ {0.10, 0.20, 0.30}
* ``risk_factor`` ∈ {0.001, 0.002}

30 unique configs total. Respects ``knowledge/SKILL.md`` Rule #2
(≤ 4 params varied per strategy).
"""

from __future__ import annotations

import pytest


def test_grid_configs_returns_thirty_unique_entries():
    from ai_trade.backtest.grid.config import grid_configs

    configs = grid_configs()
    assert len(configs) == 30
    assert len(set(configs)) == 30, "all grid entries must be unique"


def test_grid_configs_covers_all_lookback_regression_values():
    from ai_trade.backtest.grid.config import grid_configs

    configs = grid_configs()
    lookbacks = {c.lookback_regression for c in configs}
    assert lookbacks == {60, 75, 90, 105, 120}


def test_grid_configs_covers_all_top_pct_values():
    from ai_trade.backtest.grid.config import grid_configs

    configs = grid_configs()
    tops = {c.top_pct for c in configs}
    assert tops == {0.10, 0.20, 0.30}


def test_grid_configs_covers_all_risk_factor_values():
    from ai_trade.backtest.grid.config import grid_configs

    configs = grid_configs()
    risks = {c.risk_factor for c in configs}
    assert risks == {0.001, 0.002}


def test_grid_config_is_frozen_dataclass():
    """Frozen so configs are hashable (used as dict keys / set members)."""
    from ai_trade.backtest.grid.config import ClenowGridConfig

    cfg = ClenowGridConfig(lookback_regression=90, top_pct=0.20, risk_factor=0.001)
    with pytest.raises((AttributeError, Exception)):
        cfg.lookback_regression = 120  # type: ignore[misc]


def test_grid_config_default_fixed_params_match_clenow_book():
    """Fixed params come from Clenow ``stocks_on_the_move``."""
    from ai_trade.backtest.grid.config import ClenowGridConfig

    cfg = ClenowGridConfig(lookback_regression=90, top_pct=0.20, risk_factor=0.001)
    assert cfg.rebalance_weekday == 2      # Wednesday, p.99
    assert cfg.lookback_trend == 100        # 100-day MA filter on stocks
    assert cfg.lookback_index_trend == 200  # SPX 200d MA regime, p.66-67
    assert cfg.lookback_atr == 20           # ATR20, p.82
    assert cfg.lookback_gap == 90           # 90-day gap filter
    assert cfg.gap_threshold == 0.15        # 15% max gap


def test_grid_config_config_id_is_stable_by_insertion_order():
    """The ``grid_configs()`` order is insertion order of the cartesian product,
    so callers can assign ``config_id = i`` deterministically and expect the
    same i → config mapping across runs (critical for checkpoint resume).
    """
    from ai_trade.backtest.grid.config import grid_configs

    first_run = grid_configs()
    second_run = grid_configs()
    assert first_run == second_run  # identical sequence, not just same set


def test_first_grid_config_is_smallest_lookback_smallest_top_smallest_risk():
    """Sanity: cartesian product is iterated in the declared order."""
    from ai_trade.backtest.grid.config import grid_configs

    first = grid_configs()[0]
    assert first.lookback_regression == 60
    assert first.top_pct == 0.10
    assert first.risk_factor == 0.001
