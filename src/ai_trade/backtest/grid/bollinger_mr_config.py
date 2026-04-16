"""Bollinger Mean-Reversion parameter grid definition.

Grid axes (2 × 2 = 4 configs, N=4 for DSR):

* ``window`` ∈ (20, 40): classic 20-bar Bollinger [machine_trading,
  p.204-205, ch.7] vs 40-bar for slower mean-reversion on 1h data
  [algo_trading_chan, p.28-30, ch.2].
* ``std_mult`` ∈ (1.5, 2.0): narrower band (1.5σ) for more entries vs
  classic 2.0σ [machine_trading, p.204-205, ch.7].

Fixed params:
* ``stop_pct = 0.02``: tight 2% stop for intraday [machine_trading,
  p.126, ch.4].
* ``max_hold = 24``: 24 bars = 1 trading day on 1h. Hard time-stop
  enforces short-hold constraint for Pepperstone CFDs.
* ``risk_pct_of_equity = 0.95``: single-instrument, near-full deployment.

Pre-selection rationale: window and std_mult are the only free
parameters in a Bollinger band strategy [algo_trading_chan, p.28, ch.2].
All other params (stop, time-stop, risk) are risk-management settings
that should be fixed by policy, not optimized.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


WINDOW = (20, 40)
STD_MULT = (1.5, 2.0)


@dataclass(frozen=True)
class BollingerMRGridConfig:
    """Parameter bundle for one Bollinger MR trial."""

    window: int
    std_mult: float

    # Fixed params — not varied in the grid.
    stop_pct: float = 0.02
    max_hold: int = 24
    risk_pct_of_equity: float = 0.95


def bollinger_mr_grid_configs() -> list[BollingerMRGridConfig]:
    """Return the 4 grid configs in cartesian-product order.

    With N=4 and T≈8000 (5y hourly), DSR threshold ≈ 0.36 annualized.
    ``[advances_fin_ml, p.208-211, ch.14]``.
    """
    return [
        BollingerMRGridConfig(window=w, std_mult=m)
        for w, m in itertools.product(WINDOW, STD_MULT)
    ]


def bollinger_mr_canonical_configs() -> list[BollingerMRGridConfig]:
    """Return the single canonical Bollinger Band configuration (N=1).

    The "20,2" Bollinger — 20-bar window, 2σ bands — is the specification
    explicitly described in ``[machine_trading, p.204-205, ch.7]`` as the
    standard for short-term scalping. Using N=1 is valid when the config is
    pre-specified by literature rather than selected from data.

    With N=1, DSR has no multiple-test deflation: the p-value tests whether
    the observed Sharpe is statistically > 0 at the 5% level
    ``[advances_fin_ml, p.208-211, ch.14]``.
    """
    return [BollingerMRGridConfig(window=20, std_mult=2.0)]
