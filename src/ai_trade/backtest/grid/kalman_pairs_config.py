"""Kalman Pairs parameter grid [algo_trading_chan, p.76-80, ch.3].

Grid axes
---------

* ``delta`` ∈ (1e-5, 1e-4) — process-noise scalar ``Q = δ·I``.
  Chan's worked example uses δ ≈ 1e-4 [p.77]; smaller δ → slower drift,
  larger δ → faster adaptation.
* ``entry_z`` ∈ (1.0, 1.5) — z-threshold for the standardized
  innovation [p.79]. Same grid as ``ChanPairsGridConfig`` for
  comparability.

Total: **4 configs** — same parsimony justification as chan_pairs_config:
DSR deflation ``Z(N)/√(T−1)`` stays tractable at N=4.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


DELTA = (1e-5, 1e-4)
ENTRY_Z = (1.0, 1.5)


@dataclass(frozen=True)
class KalmanPairsGridConfig:
    """Parameter bundle for one Kalman Pairs trial."""

    delta: float
    entry_z: float

    # Fixed constants (cited in strategy docstring).
    exit_z: float = 0.0
    spread_stop_z: float = 3.0
    obs_noise_r: float = 1.0
    init_train_bars: int = 500
    risk_pct_of_equity: float = 0.95
    max_hold_hours: float = 48.0
    entry_hour_cutoff: int = 14
    friday_flat_hour: int = 15
    friday_no_entry_hour: int = 13


def kalman_pairs_grid_configs() -> list[KalmanPairsGridConfig]:
    """Return the 4 grid configs in cartesian-product order."""
    return [
        KalmanPairsGridConfig(delta=d, entry_z=ez)
        for d, ez in itertools.product(DELTA, ENTRY_Z)
    ]
