"""Ehlers BP Swing with AFML meta-labeling — parameter grid.

Extends the 4-axis Ehlers grid with a 5th axis: ``p_act_threshold``
from the secondary RandomForest classifier. Intent: explore whether a
non-trivial threshold filters out noise trades enough to lift the
Deflated Sharpe Ratio above p<0.05 [advances_fin_ml, §3.6, p.50-54].

Grid axes
---------

* ``hp_period`` ∈ (48, 80)         — same as baseline [cycle_analytics p.77, p.82].
* ``lp_period`` ∈ (10, 20)         — same as baseline [p.36, ch.3].
* ``pct_of_dcp`` ∈ (0.80, 0.90, 1.00) — same as baseline [p.152-153, ch.11].
* ``stop_pct`` ∈ (0.02, 0.05)      — same as baseline [p.225-226, ch.17].
* ``p_act_threshold`` ∈ (0.55, 0.65) — AFML secondary filter gate. 0.55
  is the minimum non-trivial precision lift over class prior; 0.65 is a
  stricter tilt on the secondary's confidence [AFML p.50-54].

Total: 2 × 2 × 3 × 2 × 2 = **48 configs**. Chosen to double baseline's
N=24 — the DSR deflation factor ``Z(N)/√(T−1)`` grows ≈ 20%, preserving
comparability while exposing the meta-label lift hypothesis.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


HP_PERIOD = (48, 80)
LP_PERIOD = (10, 20)
PCT_OF_DCP = (0.80, 0.90, 1.00)
STOP_PCT = (0.02, 0.05)
P_ACT_THRESHOLD = (0.55, 0.65)


@dataclass(frozen=True)
class EhlersMetaGridConfig:
    """Parameter bundle for one Ehlers BP Swing + Meta-label trial.

    The five grid dimensions are the leading fields; the rest are fixed
    literature defaults (Ehlers-primary) and meta-label hyperparameters
    (classifier-side).
    """

    hp_period: int
    lp_period: int
    pct_of_dcp: float
    stop_pct: float
    p_act_threshold: float

    # Fixed Ehlers (primary) params.
    bandwidth: float = 0.30
    upper_threshold: float = 0.70
    lower_threshold: float = -0.70
    agc_decay: float = 0.991
    risk_pct_of_equity: float = 0.95
    period_min: int = 6
    period_max: int = 50

    # Fixed meta-label (secondary) params.
    train_fraction: float = 0.5
    pt: float = 2.0
    sl: float = 2.0
    vertical_bars: int = 20
    atr_window: int = 20
    sma_regime_window: int = 200
    n_estimators: int = 100
    max_depth: int = 5
    min_train_events: int = 20
    random_state: int = 42


def ehlers_meta_grid_configs() -> list[EhlersMetaGridConfig]:
    """Return the 48 grid configs in cartesian-product iteration order.

    Order: ``(hp, lp, pct, stop, p_act)`` — outer-most first. Stable
    across invocations so ``config_id = i`` is a deterministic key for
    checkpoint/resume.
    """
    return [
        EhlersMetaGridConfig(
            hp_period=hp,
            lp_period=lp,
            pct_of_dcp=pct,
            stop_pct=sp,
            p_act_threshold=pa,
        )
        for hp, lp, pct, sp, pa in itertools.product(
            HP_PERIOD, LP_PERIOD, PCT_OF_DCP, STOP_PCT, P_ACT_THRESHOLD
        )
    ]
