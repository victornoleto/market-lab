"""Ehlers Band-Pass Swing parameter grid definition.

The grid varies four Ehlers parameters that are defensible to sweep per
``knowledge/books/cycle_analytics.md`` — the maximum allowed by
``knowledge/SKILL.md`` Rule #2 (≤ 4 params per strategy).

Grid axes
---------

* ``hp_period`` ∈ (48, 80): text example [p.77, ch.7] vs Code Listing 7-3
  default [p.82, ch.7]. Trades off sensitivity to medium-term swings.
* ``lp_period`` ∈ (10, 20): universal SS cutoff [p.36, ch.3] vs a slower
  alternative. Affects whipsaw filtering vs latency.
* ``pct_of_dcp`` ∈ (0.80, 0.90, 1.00): around the 60°-phase-lead tuning
  recommendation [p.152-153, ch.11]. 1.00 = tune exactly on DCP (zero
  lag but no lead).
* ``stop_pct`` ∈ (0.02, 0.05): span of the "2-5% for stocks" range
  [p.225-226, ch.17].

Total: 2 × 2 × 3 × 2 = **24 configs**. Fixed params (bandwidth,
thresholds, AGC decay, risk_pct_of_equity, period clamps) mirror the
literature defaults and stay constant across the grid.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


HP_PERIOD = (48, 80)
LP_PERIOD = (10, 20)
PCT_OF_DCP = (0.80, 0.90, 1.00)
STOP_PCT = (0.02, 0.05)


@dataclass(frozen=True)
class EhlersGridConfig:
    """Parameter bundle for one Ehlers BP Swing trial.

    The four grid dimensions are the leading fields; the rest are fixed
    literature defaults, documented in ``ehlers_bp_swing.py``.
    """

    hp_period: int
    lp_period: int
    pct_of_dcp: float
    stop_pct: float

    # Fixed params — not varied in the grid.
    bandwidth: float = 0.30                  # [p.53, ch.5]
    upper_threshold: float = 0.70            # [p.220-221, ch.17]
    lower_threshold: float = -0.70           # [p.220-221, ch.17]
    agc_decay: float = 0.991                 # [p.54-55, ch.5]
    risk_pct_of_equity: float = 0.95         # single-instrument swing trader
    period_min: int = 6                      # [p.82, ch.7]
    period_max: int = 50                     # [p.82, ch.7]


def ehlers_grid_configs() -> list[EhlersGridConfig]:
    """Return the 24 grid configs in cartesian-product iteration order.

    Order is: ``(hp_period, lp_period, pct_of_dcp, stop_pct)`` — outer-
    most first. Stable across invocations so ``config_id = i`` is a
    deterministic key for checkpoint/resume in the grid runner.
    """
    return [
        EhlersGridConfig(
            hp_period=hp,
            lp_period=lp,
            pct_of_dcp=pct,
            stop_pct=sp,
        )
        for hp, lp, pct, sp in itertools.product(
            HP_PERIOD, LP_PERIOD, PCT_OF_DCP, STOP_PCT
        )
    ]
