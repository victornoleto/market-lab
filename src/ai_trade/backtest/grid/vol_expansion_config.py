"""Vol-Expansion Breakout parameter grid [spec §3.5].

Grid axes (gridded):
* n_entry in (20, 55) — Turtles canonical vs Donchian original [trading_systems_methods, p.353]
* n_exit  in (10, 20) — Turtles canonical (5/20) vs symmetric with entry

Total: 2 × 2 = 4 configs. Per-asset → 12 trials in the full grid.
"""
from __future__ import annotations
import itertools
from dataclasses import dataclass

N_ENTRY = (20, 55)
N_EXIT = (10, 20)

@dataclass(frozen=True)
class VolExpansionGridConfig:
    n_entry: int
    n_exit: int
    k_filter: float = 33.0
    target_vol_annual: float = 0.10
    disaster_n_sigma: float = 4.0
    ref_hold_bars: int = 24
    cone_lookback: int = 1700
    yz_window: int = 20
    max_hold_hours: float = 48.0

def vol_expansion_grid_configs() -> list[VolExpansionGridConfig]:
    return [VolExpansionGridConfig(n_entry=ne, n_exit=nx)
            for ne, nx in itertools.product(N_ENTRY, N_EXIT)]
