"""GridRunner — iterates configs, runs trials, persists checkpoints.

Generic over the config type: the ``config_cls`` field is the dataclass
used for both *trial_fn* typing (implicit) and checkpoint rehydration
(explicit — ``trial_from_dir`` needs the class to reconstruct instances).
Default ``ClenowGridConfig`` preserves backward compatibility; pass
``EhlersGridConfig`` (or any other frozen dataclass) for other strategies.

The ``trial_fn`` contract isolates GridRunner from strategy-construction
details: callers pass a closure that knows how to build and run one
trial given a config.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Generic, TypeVar

from joblib import Parallel, delayed

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


ConfigT = TypeVar("ConfigT")

TrialFn = Callable[[ConfigT], BacktestResult]
ProgressCb = Callable[[int, int, TrialResult], None]


@dataclass
class GridRunner(Generic[ConfigT]):
    """Run a list of grid configs, checkpointing each trial to disk.

    ``checkpoint_dir`` is the root under which run-specific subdirectories
    appear as ``{checkpoint_dir}/{run_id}/trial_{id}/``. A re-run with the
    same ``run_id`` reuses any trial directories already present.

    ``config_cls`` is the dataclass used to rehydrate checkpoints from
    disk. It defaults to :class:`ClenowGridConfig` so pre-existing
    Clenow call sites don't need to change; new strategies (Ehlers,
    future AFML/Chan) pass their own config class.
    """

    checkpoint_dir: Path = field(default_factory=lambda: Path(".cache/grid_runs"))
    n_jobs: int = 1
    periods_per_year: int = 252
    config_cls: type = ClenowGridConfig

    def run(
        self,
        *,
        configs: list[ConfigT],
        trial_fn: TrialFn[ConfigT],
        run_id: str,
        progress_cb: ProgressCb | None = None,
    ) -> GridResult[ConfigT]:
        run_dir = Path(self.checkpoint_dir) / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        total = len(configs)

        # Load any pre-existing checkpoints first so resume skips re-run.
        # Compute which configs still need to run.
        preloaded: dict[int, TrialResult[ConfigT]] = {}
        pending: list[tuple[int, ConfigT]] = []
        for idx, config in enumerate(configs):
            trial_dir = run_dir / f"trial_{idx}"
            if (trial_dir / "meta.json").exists():
                preloaded[idx] = trial_from_dir(trial_dir, config_cls=self.config_cls)
                _log.info(
                    "trial %d resumed from checkpoint (status=%s)",
                    idx, preloaded[idx].status,
                )
            else:
                pending.append((idx, config))

        if self.n_jobs == 1 or len(pending) <= 1:
            new_trials = self._run_sequential(pending, trial_fn)
        else:
            new_trials = self._run_parallel(pending, trial_fn)

        # Merge preloaded + newly computed, persist new ones, and invoke
        # progress_cb in config-order so observers see a stable sequence.
        trials: list[TrialResult[ConfigT]] = []
        completed_count = 0
        for idx, _cfg in enumerate(configs):
            if idx in preloaded:
                trial = preloaded[idx]
            else:
                trial = new_trials[idx]
                trial_to_dir(trial, run_dir / f"trial_{idx}")
            trials.append(trial)
            completed_count += 1
            if progress_cb is not None:
                progress_cb(completed_count, total, trial)

        return GridResult(trials=trials, run_id=run_id)

    def _run_sequential(
        self,
        pending: list[tuple[int, ConfigT]],
        trial_fn: TrialFn[ConfigT],
    ) -> dict[int, TrialResult[ConfigT]]:
        return {
            idx: self._run_trial(idx, config, trial_fn)
            for idx, config in pending
        }

    def _run_parallel(
        self,
        pending: list[tuple[int, ConfigT]],
        trial_fn: TrialFn[ConfigT],
    ) -> dict[int, TrialResult[ConfigT]]:
        """Dispatch pending trials across ``n_jobs`` workers via joblib.

        Backend ``loky`` (default) uses processes, which is safe for CPU-bound
        strategy runs under the GIL. The trial_fn closure must be picklable —
        callers usually pass a top-level function or a closure over picklable
        objects.
        """
        results = Parallel(n_jobs=self.n_jobs, backend="loky", return_as="list")(
            delayed(self._run_trial)(idx, config, trial_fn)
            for idx, config in pending
        )
        return {idx: trial for (idx, _cfg), trial in zip(pending, results)}

    def _run_trial(
        self,
        config_id: int,
        config: ConfigT,
        trial_fn: TrialFn[ConfigT],
    ) -> TrialResult[ConfigT]:
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
