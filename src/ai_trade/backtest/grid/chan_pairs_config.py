"""Chan Bollinger Pairs parameter grid [algo_trading_chan p.71-73, ch.3].

Grid axes
---------

* ``lookback_multiplier`` ∈ (1, 2) — multiple of OU half-life used as
  Bollinger lookback [p.47, ch.2].
* ``entry_z`` ∈ (1.0, 1.5) — Chan uses 1.0 in the canonical example
  [p.71-72], acknowledges it as a free parameter.

Total: 2 × 2 = **4 configs**. Deliberately parsimonious — 5 prior Phase 2.5
runs (N=24, N=30) all failed DSR; cutting N_trials to 4 lets the deflation
factor ``Z(N)/√(T−1)`` shrink to roughly half of Run 2's.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


LOOKBACK_MULTIPLIER = (1, 2)
ENTRY_Z = (1.0, 1.5)


@dataclass(frozen=True)
class ChanPairsGridConfig:
    """Parameter bundle for one Chan Bollinger Pairs trial."""

    lookback_multiplier: int
    entry_z: float

    # Fixed constants (cited in strategy docstring).
    exit_z: float = 0.0
    spread_stop_z: float = 3.0
    train_bars: int = 1250
    half_life_min: int = 4
    half_life_max: int = 60
    risk_pct_of_equity: float = 0.95
    max_hold_hours: float = 48.0
    entry_hour_cutoff: int = 14
    friday_flat_hour: int = 15
    friday_no_entry_hour: int = 13


def chan_pairs_grid_configs() -> list[ChanPairsGridConfig]:
    """Return the 4 grid configs in cartesian-product order.

    Order: (lookback_multiplier, entry_z) — outer-most first. Stable
    across invocations so ``config_id = i`` is a deterministic key for
    checkpoint/resume.
    """
    return [
        ChanPairsGridConfig(lookback_multiplier=lm, entry_z=ez)
        for lm, ez in itertools.product(LOOKBACK_MULTIPLIER, ENTRY_Z)
    ]
