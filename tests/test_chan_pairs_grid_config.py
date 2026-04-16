"""Tests for the Chan Pairs grid config [algo_trading_chan p.71-73]."""

from ai_trade.backtest.grid.chan_pairs_config import (
    ChanPairsGridConfig,
    chan_pairs_grid_configs,
)


def test_grid_returns_4_configs():
    configs = chan_pairs_grid_configs()
    assert len(configs) == 4


def test_grid_covers_full_cartesian_2x2():
    configs = chan_pairs_grid_configs()
    combos = {(c.lookback_multiplier, c.entry_z) for c in configs}
    assert combos == {(1, 1.0), (1, 1.5), (2, 1.0), (2, 1.5)}


def test_grid_config_is_frozen_and_hashable():
    from dataclasses import FrozenInstanceError

    c = ChanPairsGridConfig(lookback_multiplier=2, entry_z=1.0)
    # Frozen dataclass is hashable
    _ = hash(c)
    try:
        c.lookback_multiplier = 99  # type: ignore[misc]
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("expected FrozenInstanceError")
