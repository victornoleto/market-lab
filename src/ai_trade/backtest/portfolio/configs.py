"""PortfolioConfig + portfolio_configs() — 9 configs from top-3 × top-3.

Top-3 configs are sourced from the two existing diagnostic reports:

* Clenow (Run 3 Tiingo SPX 2015-2023): top-3 by Sharpe from
  ``reports/grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md``.
* Ehlers BP Swing (long-history SPY 2005-2023): top-3 by Sharpe from
  ``reports/grid_ehlers_20260415-1353/diagnostic.md``.

The choice of "top-3 by Sharpe" (rather than just top-1) honours
:class:`DSR` deflation semantics — see
``docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md``
§3.1 "N_trials = 9 portfolios".
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass


# ---- Top-3 Clenow by Sharpe (Run 3 Tiingo SPX 2015-2023) ----
# Source: reports/grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md
_CLENOW_TOP3 = (
    # (config_id, lookback_regression, top_pct, risk_factor, sharpe_from_report)
    (8, 75, 0.20, 0.001, 0.618),
    (19, 105, 0.10, 0.002, 0.581),
    (10, 75, 0.30, 0.001, 0.517),
)

# ---- Top-3 Ehlers BP Swing by Sharpe (long-history SPY 2005-2023) ----
# Source: reports/grid_ehlers_20260415-1353/diagnostic.md
_EHLERS_TOP3 = (
    # (config_id, hp_period, lp_period, pct_of_dcp, stop_pct, sharpe_from_report)
    (6, 48, 20, 0.80, 0.02, 0.639),
    (18, 80, 20, 0.80, 0.02, 0.606),
    (19, 80, 20, 0.80, 0.05, 0.603),
)


@dataclass(frozen=True)
class PortfolioConfig:
    """Parameter bundle for one F3.D portfolio trial.

    Fields identify which top-3 config of each sub-strategy is paired
    AND inline the parameters so the dataclass is self-contained
    (readable in diagnostic reports without cross-referencing).
    """

    clenow_config_id: int
    ehlers_config_id: int

    # Clenow parameters (mirrored from ClenowGridConfig).
    clenow_lookback: int
    clenow_top_pct: float
    clenow_risk_factor: float

    # Ehlers parameters (mirrored from EhlersGridConfig).
    ehlers_hp: int
    ehlers_lp: int
    ehlers_pct_of_dcp: float
    ehlers_stop_pct: float


def portfolio_configs() -> list[PortfolioConfig]:
    """Return the 9 portfolio configs (3 × 3 cartesian product).

    Order: outer loop = Clenow rank (1, 2, 3), inner loop = Ehlers
    rank (1, 2, 3). This gives a deterministic mapping
    ``config_id = i`` for checkpoint/report stability.
    """
    return [
        PortfolioConfig(
            clenow_config_id=c[0],
            ehlers_config_id=e[0],
            clenow_lookback=c[1],
            clenow_top_pct=c[2],
            clenow_risk_factor=c[3],
            ehlers_hp=e[1],
            ehlers_lp=e[2],
            ehlers_pct_of_dcp=e[3],
            ehlers_stop_pct=e[4],
        )
        for c, e in itertools.product(_CLENOW_TOP3, _EHLERS_TOP3)
    ]


def clenow_top3_grid_configs():
    """Return the 3 top-3 Clenow configs as ClenowGridConfig instances.

    Public helper for script callers — keeps the ``_CLENOW_TOP3`` tuple
    encoding private to this module.
    """
    from ai_trade.backtest.grid.config import ClenowGridConfig
    return [
        ClenowGridConfig(
            lookback_regression=c[1], top_pct=c[2], risk_factor=c[3],
        )
        for c in _CLENOW_TOP3
    ]


def ehlers_top3_grid_configs():
    """Return the 3 top-3 Ehlers configs as EhlersGridConfig instances."""
    from ai_trade.backtest.grid.ehlers_config import EhlersGridConfig
    return [
        EhlersGridConfig(
            hp_period=e[1], lp_period=e[2], pct_of_dcp=e[3], stop_pct=e[4],
        )
        for e in _EHLERS_TOP3
    ]
