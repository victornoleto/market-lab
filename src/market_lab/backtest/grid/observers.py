"""Progress observers + logging setup for grid runs.

Observers are plain callables with the :data:`market_lab.backtest.grid.runner.
ProgressCb` signature ``(completed, total, trial) -> None``. Composing a few
(JSONL, status.md, ...) is how the CLI wires per-run and cross-run
observability without entangling the core runner.

The four logging handlers:

1. ``console`` — INFO+ to stderr (so ``tqdm`` bars on stdout aren't scrambled)
2. ``per-run debug`` — DEBUG+ to ``{run_dir}/debug.log``
3. ``per-run JSONL`` — not a logging handler — the :class:`JsonlTrialObserver`
   writes this; included here for symmetry with the plan
4. ``unified append`` — INFO+ to a stable path (``logs/grid.log``) with the
   ``run_id`` in the prefix so the user can ``tail -f`` one file forever
   regardless of how many runs they launch
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from market_lab.backtest.grid.result import TrialResult


ProgressCb = Callable[[int, int, TrialResult], None]


def _trial_to_jsonl_record(
    completed: int, total: int, trial: TrialResult, run_id: str,
) -> dict:
    return {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "run_id": run_id,
        "completed": completed,
        "total": total,
        "config_id": trial.config_id,
        "config": dict(trial.config.__dict__),
        "status": trial.status,
        "sharpe": _safe_float(trial.sharpe),
        "cagr": _safe_float(trial.cagr),
        "max_drawdown": _safe_float(trial.max_drawdown),
        "error_msg": trial.error_msg,
    }


def _safe_float(x: float) -> float | str:
    if isinstance(x, float) and np.isnan(x):
        return "nan"
    if isinstance(x, float) and np.isposinf(x):
        return "inf"
    if isinstance(x, float) and np.isneginf(x):
        return "-inf"
    return float(x)


@dataclass
class JsonlTrialObserver:
    """Append one JSON line per trial completion."""

    path: Path
    run_id: str

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def __call__(self, completed: int, total: int, trial: TrialResult) -> None:
        record = _trial_to_jsonl_record(completed, total, trial, self.run_id)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")


@dataclass
class StatusFileObserver:
    """Overwrite a Markdown snapshot of run progress after each trial."""

    path: Path
    run_id: str
    _started_at: float | None = None
    _best_sharpe: float | None = None
    _n_errors: int = 0

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._started_at = time.time()

    def __call__(self, completed: int, total: int, trial: TrialResult) -> None:
        if trial.status == "error":
            self._n_errors += 1
        else:
            sh = float(trial.sharpe)
            if np.isfinite(sh):
                if self._best_sharpe is None or sh > self._best_sharpe:
                    self._best_sharpe = sh

        elapsed = time.time() - (self._started_at or time.time())
        if completed > 0 and completed < total:
            eta_s = elapsed * (total - completed) / completed
            eta_str = f"{int(eta_s // 60)}m{int(eta_s % 60)}s"
        else:
            eta_str = "—"

        best = (
            f"{self._best_sharpe:.3f}" if self._best_sharpe is not None else "—"
        )
        body = (
            f"# Grid run status — `{self.run_id}`\n\n"
            f"- **Progress:** {completed}/{total}\n"
            f"- **Elapsed:** {int(elapsed // 60)}m{int(elapsed % 60)}s\n"
            f"- **ETA:** {eta_str}\n"
            f"- **Best Sharpe so far:** {best}\n"
            f"- **Errors:** {self._n_errors}\n"
            f"- **Last trial:** config_id={trial.config_id}, status={trial.status}\n"
        )
        self.path.write_text(body)


def compose_observers(*observers: ProgressCb) -> ProgressCb:
    """Wrap multiple observers behind a single callable."""
    def _call(completed: int, total: int, trial: TrialResult) -> None:
        for obs in observers:
            obs(completed, total, trial)
    return _call


def setup_grid_logging(
    *,
    run_id: str,
    run_dir: Path,
    unified_log_path: Path,
    level: int = logging.INFO,
) -> None:
    """Attach 3 logging handlers to ``market_lab.grid``:

    * console (stderr) at ``level``
    * per-run debug file at DEBUG
    * unified append log with ``run_id`` in the record format so ``tail -f``
      can distinguish concurrent runs

    Safe to call multiple times — callers should remove handlers they added
    (see the test for a pattern). Idempotency isn't built in because the
    CLI only calls this once per run.
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    unified_log_path = Path(unified_log_path)
    unified_log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("market_lab.grid")
    logger.setLevel(logging.DEBUG)  # handlers filter per-handler

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(console)

    debug_fh = logging.FileHandler(run_dir / "debug.log", mode="a", encoding="utf-8")
    debug_fh.setLevel(logging.DEBUG)
    debug_fh.setFormatter(
        logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
        )
    )
    logger.addHandler(debug_fh)

    unified_fh = logging.FileHandler(
        unified_log_path, mode="a", encoding="utf-8",
    )
    unified_fh.setLevel(level)
    unified_fh.setFormatter(
        logging.Formatter(f"%(asctime)s [{run_id}] %(levelname)s %(message)s")
    )
    logger.addHandler(unified_fh)
