"""ai_trade.backtest.grid — parameter-grid backtest + gate evaluation.

Fase 2.5/3 module: runs a Clenow momentum grid across N≥20 configs and
exercises the PBO/DSR/walk-forward gates in production. See
``specs/backtest_phase2.md`` §"Reavaliação pós-Fase 2" for the motivation
(single-trial Clenow never activates the gates; a grid does).
"""

from ai_trade.backtest.grid.config import ClenowGridConfig, grid_configs

__all__ = [
    "ClenowGridConfig",
    "grid_configs",
]
