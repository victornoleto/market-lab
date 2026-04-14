"""ai_trade.backtest.grid — parameter-grid backtest + gate evaluation.

Fase 2.5/3 module: runs a Clenow momentum grid across N≥20 configs and
exercises the PBO/DSR/walk-forward gates in production. See
``specs/backtest_phase2.md`` §"Reavaliação pós-Fase 2" for the motivation
(single-trial Clenow never activates the gates; a grid does).
"""

from ai_trade.backtest.grid.config import ClenowGridConfig, grid_configs
from ai_trade.backtest.grid.gates import GateEvaluator, GateVerdict
from ai_trade.backtest.grid.observers import (
    JsonlTrialObserver,
    StatusFileObserver,
    compose_observers,
    setup_grid_logging,
)
from ai_trade.backtest.grid.result import (
    GridResult,
    TrialResult,
    trial_from_dir,
    trial_to_dir,
)
from ai_trade.backtest.grid.runner import GridRunner
from ai_trade.backtest.grid.walk_forward import WFResult, wf_for_config, wf_for_grid

__all__ = [
    "ClenowGridConfig",
    "GateEvaluator",
    "GateVerdict",
    "GridResult",
    "GridRunner",
    "JsonlTrialObserver",
    "StatusFileObserver",
    "TrialResult",
    "WFResult",
    "compose_observers",
    "grid_configs",
    "setup_grid_logging",
    "trial_from_dir",
    "trial_to_dir",
    "wf_for_config",
    "wf_for_grid",
]
