"""ai_trade.backtest.grid — parameter-grid backtest + gate evaluation.

Phase 2.5/3 module: runs a strategy grid across N≥20 configs and
exercises the PBO/DSR/walk-forward gates in production. See
``specs/backtest_phase2.md`` §"Post-Phase 2 reassessment" and
``specs/backtest_phase2_5_ehlers.md`` for motivation (single-trial
strategies never activate the gates; a grid does).

The runner/result layer is generic over the config dataclass —
:class:`ClenowGridConfig` for Run 1, :class:`EhlersGridConfig` for
Run 2, future strategies plug in by adding their own frozen
dataclass.
"""

from ai_trade.backtest.grid.bollinger_mr_config import (
    BollingerMRGridConfig,
    bollinger_mr_grid_configs,
)
from ai_trade.backtest.grid.config import ClenowGridConfig, grid_configs
from ai_trade.backtest.grid.diagnostic import (
    DiagnosticAnalyzer,
    DiagnosticReport,
    FailureMode,
)
from ai_trade.backtest.grid.ehlers_config import (
    EhlersGridConfig,
    ehlers_grid_configs,
    ehlers_reduced_1h_configs,
    ehlers_regime_daily_configs,
)
from ai_trade.backtest.grid.ehlers_meta_config import (
    EhlersMetaGridConfig,
    ehlers_meta_grid_configs,
)
from ai_trade.backtest.grid.chan_pairs_config import (
    ChanPairsGridConfig,
    chan_pairs_grid_configs,
)
from ai_trade.backtest.grid.kalman_pairs_config import (
    KalmanPairsGridConfig,
    kalman_pairs_grid_configs,
)
from ai_trade.backtest.grid.vol_expansion_config import (
    VolExpansionGridConfig,
    vol_expansion_grid_configs,
)
from ai_trade.backtest.grid.gates import GateEvaluator, GateVerdict
from ai_trade.backtest.grid.report import GridReportGenerator
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
    "BollingerMRGridConfig",
    "ChanPairsGridConfig",
    "KalmanPairsGridConfig",
    "ClenowGridConfig",
    "VolExpansionGridConfig",
    "DiagnosticAnalyzer",
    "DiagnosticReport",
    "EhlersGridConfig",
    "EhlersMetaGridConfig",
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
    "chan_pairs_grid_configs",
    "kalman_pairs_grid_configs",
    "vol_expansion_grid_configs",
    "compose_observers",
    "ehlers_grid_configs",
    "ehlers_reduced_1h_configs",
    "ehlers_regime_daily_configs",
    "ehlers_meta_grid_configs",
    "grid_configs",
    "setup_grid_logging",
    "trial_from_dir",
    "trial_to_dir",
    "wf_for_config",
    "wf_for_grid",
]
