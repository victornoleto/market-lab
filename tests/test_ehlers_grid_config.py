"""Tests for ``ai_trade.backtest.grid.ehlers_config`` — Ehlers BP Swing grid.

The grid varies four Ehlers parameters defensible per
``knowledge/books/cycle_analytics.md``:

* ``hp_period``   ∈ {48, 80}         — text example vs. Code Listing 7-3 default
* ``lp_period``   ∈ {10, 20}         — universal SS cutoff vs. slower
* ``pct_of_dcp``  ∈ {0.80, 0.90, 1.00} — around the 60° phase-lead tuning
* ``stop_pct``    ∈ {0.02, 0.05}     — within the 2–5% stock stop range

2 × 2 × 3 × 2 = 24 unique configs. Respects ``knowledge/SKILL.md``
Rule #2 (≤ 4 params varied per strategy — the maximum allowed).
"""

from __future__ import annotations

import pytest


def test_grid_configs_returns_twentyfour_unique_entries():
    from ai_trade.backtest.grid.ehlers_config import ehlers_grid_configs

    configs = ehlers_grid_configs()
    assert len(configs) == 24
    assert len(set(configs)) == 24, "all grid entries must be unique"


def test_grid_configs_covers_all_hp_period_values():
    from ai_trade.backtest.grid.ehlers_config import ehlers_grid_configs

    configs = ehlers_grid_configs()
    hps = {c.hp_period for c in configs}
    assert hps == {48, 80}


def test_grid_configs_covers_all_lp_period_values():
    from ai_trade.backtest.grid.ehlers_config import ehlers_grid_configs

    configs = ehlers_grid_configs()
    lps = {c.lp_period for c in configs}
    assert lps == {10, 20}


def test_grid_configs_covers_all_pct_of_dcp_values():
    from ai_trade.backtest.grid.ehlers_config import ehlers_grid_configs

    configs = ehlers_grid_configs()
    pcts = {c.pct_of_dcp for c in configs}
    assert pcts == {0.80, 0.90, 1.00}


def test_grid_configs_covers_all_stop_pct_values():
    from ai_trade.backtest.grid.ehlers_config import ehlers_grid_configs

    configs = ehlers_grid_configs()
    stops = {c.stop_pct for c in configs}
    assert stops == {0.02, 0.05}


def test_grid_config_is_frozen_dataclass():
    """Frozen so configs are hashable (used as dict keys / set members)."""
    from ai_trade.backtest.grid.ehlers_config import EhlersGridConfig

    cfg = EhlersGridConfig(hp_period=48, lp_period=10, pct_of_dcp=0.90, stop_pct=0.05)
    with pytest.raises((AttributeError, Exception)):
        cfg.hp_period = 80  # type: ignore[misc]


def test_grid_config_default_fixed_params():
    """Non-varied params keep literature defaults."""
    from ai_trade.backtest.grid.ehlers_config import EhlersGridConfig

    cfg = EhlersGridConfig(hp_period=48, lp_period=10, pct_of_dcp=0.90, stop_pct=0.05)
    # These are not part of the 4-dim grid — they stay constant.
    assert cfg.bandwidth == 0.30            # [p.53, ch.5]
    assert cfg.upper_threshold == 0.70      # [p.220-221, ch.17]
    assert cfg.lower_threshold == -0.70
    assert cfg.agc_decay == 0.991           # [p.54-55, ch.5]
    assert cfg.risk_pct_of_equity == 0.95
    assert cfg.period_min == 6              # [p.82, ch.7]
    assert cfg.period_max == 50


def test_grid_config_id_is_stable_by_insertion_order():
    """Deterministic iteration order → ``config_id = i`` is stable for
    checkpoint/resume semantics in the grid runner.
    """
    from ai_trade.backtest.grid.ehlers_config import ehlers_grid_configs

    first_run = ehlers_grid_configs()
    second_run = ehlers_grid_configs()
    assert first_run == second_run


def test_first_grid_config_is_smallest_values():
    """Cartesian product is iterated in the declared tuple order."""
    from ai_trade.backtest.grid.ehlers_config import ehlers_grid_configs

    first = ehlers_grid_configs()[0]
    assert first.hp_period == 48
    assert first.lp_period == 10
    assert first.pct_of_dcp == pytest.approx(0.80)
    assert first.stop_pct == pytest.approx(0.02)
