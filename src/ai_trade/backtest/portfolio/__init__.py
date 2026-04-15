"""Portfolio combination primitives — offline equity-curve merge.

See ``docs/superpowers/specs/2026-04-15-f3d-portfolio-clenow-ehlers-design.md``
for the F3.D hypothesis. This package does NOT modify the engine: sub-
strategies run as standalone grids, then their equity curves are combined
by weighted daily returns. The result is wrapped in a synthetic
``GridResult`` so the existing PBO/DSR/walk-forward evaluators apply.
"""

from ai_trade.backtest.portfolio.combined import (
    combine_equity_curves,
    compute_portfolio_metrics,
    make_portfolio_trial,
)
from ai_trade.backtest.portfolio.configs import (
    PortfolioConfig,
    clenow_top3_grid_configs,
    ehlers_top3_grid_configs,
    portfolio_configs,
)

__all__ = [
    "PortfolioConfig",
    "clenow_top3_grid_configs",
    "combine_equity_curves",
    "compute_portfolio_metrics",
    "ehlers_top3_grid_configs",
    "make_portfolio_trial",
    "portfolio_configs",
]
