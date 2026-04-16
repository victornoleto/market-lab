"""Tests for VolExpansionGridConfig [spec §3.5]."""
from __future__ import annotations
import pytest
from ai_trade.backtest.grid.vol_expansion_config import (
    VolExpansionGridConfig, vol_expansion_grid_configs,
)

def test_grid_returns_4_configs() -> None:
    assert len(vol_expansion_grid_configs()) == 4

def test_grid_axes_are_n_entry_and_n_exit() -> None:
    pairs = {(c.n_entry, c.n_exit) for c in vol_expansion_grid_configs()}
    assert pairs == {(20, 10), (20, 20), (55, 10), (55, 20)}

def test_grid_fixed_constants() -> None:
    c = vol_expansion_grid_configs()[0]
    assert c.k_filter == 33.0
    assert c.target_vol_annual == 0.10
    assert c.disaster_n_sigma == 4.0
    assert c.ref_hold_bars == 24
    assert c.cone_lookback == 1700
    assert c.yz_window == 20
    assert c.max_hold_hours == 48.0
