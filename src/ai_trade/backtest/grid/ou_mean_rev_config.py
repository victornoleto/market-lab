"""OU Mean-Reversion parameter grid definition.

Grid axes (2 × 2 = 4 configs, N=4 for DSR):

* ``lookback`` ∈ (60, 120): window for z-score and ADF regression.
  60 bars ≈ 2.5 trading days on 1h, 120 ≈ 5 days. Guided by typical
  half-life of SPY intraday mean-reversion
  ``[algo_trading_chan, p.47-48, ch.2]``.
* ``z_entry`` ∈ (1.5, 2.0): z-score threshold for entry. 1.5σ for
  more trades vs. 2.0σ for higher conviction
  ``[quant_trading_chan, p.140-142]``.

Fixed params:
* ``z_exit = 0.0``: exit at z-score mean.
* ``stop_pct = 0.02``: tight 2% stop ``[machine_trading, p.126, ch.4]``.
* ``max_hold = 24``: 1 trading day on 1h. Short-hold for Pepperstone CFDs.
* ``risk_pct_of_equity = 0.95``: single-instrument, near-full deployment.

Pre-selection rationale: lookback and z_entry are the two free
parameters. lookback determines the characteristic time scale for
mean-reversion (should match half-life). z_entry is the entry
sensitivity. All other params are risk-management settings fixed by
policy ``[algo_trading_chan, p.269, ch.2]``.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


LOOKBACK = (60, 120)
Z_ENTRY = (1.5, 2.0)


@dataclass(frozen=True)
class OUMeanRevGridConfig:
    """Parameter bundle for one OU MR trial."""

    lookback: int
    z_entry: float

    # Fixed params — not varied in the grid.
    z_exit: float = 0.0
    stop_pct: float = 0.02
    max_hold: int = 24
    risk_pct_of_equity: float = 0.95


def ou_mean_rev_grid_configs() -> list[OUMeanRevGridConfig]:
    """Return the 4 grid configs in cartesian-product order.

    With N=4 and T≈8000 (5y hourly), DSR threshold ≈ 0.36 annualized.
    ``[advances_fin_ml, p.208-211, ch.14]``.
    """
    return [
        OUMeanRevGridConfig(lookback=lb, z_entry=ze)
        for lb, ze in itertools.product(LOOKBACK, Z_ENTRY)
    ]
