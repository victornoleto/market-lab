"""market_lab.backtest.grid — parameter-grid backtest + gate evaluation.

Phase 2.5/3 module: runs a strategy grid across N≥20 configs and
exercises the PBO/DSR/walk-forward gates in production.

The runner/result layer is generic over the config dataclass — pass
your own frozen dataclass to plug in a new strategy. After the
2026-04-16 post-winners cleanup only :class:`BollingerMRGridConfig`
remains here (the ETF rotation winner runs without a grid config —
see ``scripts/run_etf_rotation.py``).
"""

from market_lab.backtest.grid.bollinger_mr_config import (
    BollingerMRGridConfig,
    bollinger_mr_grid_configs,
)
from market_lab.backtest.grid.diagnostic import (
    DiagnosticAnalyzer,
    DiagnosticReport,
    FailureMode,
)
from market_lab.backtest.grid.gates import GateEvaluator, GateVerdict
from market_lab.backtest.grid.report import GridReportGenerator
from market_lab.backtest.grid.observers import (
    JsonlTrialObserver,
    StatusFileObserver,
    compose_observers,
    setup_grid_logging,
)
from market_lab.backtest.grid.result import (
    GridResult,
    TrialResult,
    trial_from_dir,
    trial_to_dir,
)
from market_lab.backtest.grid.runner import GridRunner
from market_lab.backtest.grid.walk_forward import WFResult, wf_for_config, wf_for_grid

__all__ = [
    "BollingerMRGridConfig",
    "DiagnosticAnalyzer",
    "DiagnosticReport",
    "FailureMode",
    "GateEvaluator",
    "GateVerdict",
    "GridReportGenerator",
    "GridResult",
    "GridRunner",
    "JsonlTrialObserver",
    "StatusFileObserver",
    "TrialResult",
    "WFResult",
    "bollinger_mr_grid_configs",
    "compose_observers",
    "setup_grid_logging",
    "trial_from_dir",
    "trial_to_dir",
    "wf_for_config",
    "wf_for_grid",
]
