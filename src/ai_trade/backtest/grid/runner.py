"""GridRunner — iterates configs, runs trials, persists checkpoints.

Single-threaded in this commit; parallelism lands in the next commit along
with logging/progress UX. The ``trial_fn`` contract isolates GridRunner from
strategy-construction details: callers pass a closure that knows how to
build and run one trial given a config.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ai_trade.backtest.engine.runner import BacktestResult
from ai_trade.backtest.grid.config import ClenowGridConfig
from ai_trade.backtest.grid.result import (
    GridResult,
    TrialResult,
    trial_from_dir,
    trial_to_dir,
)
from ai_trade.backtest.metrics.performance import (
    cagr,
    max_drawdown,
    returns_from_equity,
    sharpe,
)


_log = logging.getLogger("ai_trade.grid.runner")


TrialFn = Callable[[ClenowGridConfig], BacktestResult]
ProgressCb = Callable[[int, int, TrialResult], None]


@dataclass
class GridRunner:
    """Run a list of grid configs, checkpointing each trial to disk.

    ``checkpoint_dir`` is the root under which run-specific subdirectories
    appear as ``{checkpoint_dir}/{run_id}/trial_{id}/``. A re-run with the
    same ``run_id`` reuses any trial directories already present.
    """

    checkpoint_dir: Path = field(default_factory=lambda: Path(".cache/grid_runs"))
    n_jobs: int = 1           # parallelism enabled in the next commit
    periods_per_year: int = 252

    def run(
        self,
        *,
        configs: list[ClenowGridConfig],
        trial_fn: TrialFn,
        run_id: str,
        progress_cb: ProgressCb | None = None,
    ) -> GridResult:
        run_dir = Path(self.checkpoint_dir) / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        trials: list[TrialResult] = []
        total = len(configs)

        for idx, config in enumerate(configs):
            trial_dir = run_dir / f"trial_{idx}"
            if (trial_dir / "meta.json").exists():
                trial = trial_from_dir(trial_dir)
                _log.info(
                    "trial %d resumed from checkpoint (status=%s)", idx, trial.status,
                )
            else:
                trial = self._run_trial(idx, config, trial_fn)
                trial_to_dir(trial, trial_dir)

            trials.append(trial)
            if progress_cb is not None:
                progress_cb(idx + 1, total, trial)

        return GridResult(trials=trials, run_id=run_id)

    def _run_trial(
        self,
        config_id: int,
        config: ClenowGridConfig,
        trial_fn: TrialFn,
    ) -> TrialResult:
        try:
            result = trial_fn(config)
        except Exception as exc:  # noqa: BLE001 — we want the stringified error
            _log.warning("trial %d failed: %s", config_id, exc, exc_info=True)
            return TrialResult(
                config_id=config_id,
                config=config,
                result=None,
                sharpe=float("nan"),
                cagr=float("nan"),
                max_drawdown=float("nan"),
                status="error",
                error_msg=str(exc),
            )

        return TrialResult(
            config_id=config_id,
            config=config,
            result=result,
            sharpe=_safe_sharpe(result.equity_curve, self.periods_per_year),
            cagr=_safe_cagr(result.equity_curve, self.periods_per_year),
            max_drawdown=_safe_max_dd(result.equity_curve),
            status="ok",
        )


def _safe_sharpe(equity, periods_per_year: int) -> float:
    if len(equity) < 2:
        return 0.0
    return float(sharpe(returns_from_equity(equity), periods_per_year=periods_per_year))


def _safe_cagr(equity, periods_per_year: int) -> float:
    if len(equity) < 2:
        return 0.0
    return float(cagr(equity, periods_per_year=periods_per_year))


def _safe_max_dd(equity) -> float:
    if len(equity) < 2:
        return 0.0
    return float(max_drawdown(equity))
