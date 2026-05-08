"""Tests for ``ai_trade.backtest.grid.runner`` — GridRunner orchestration.

GridRunner iterates a list of configs, calls a caller-provided ``trial_fn``
for each, captures exceptions as error trials, persists completed trials
to disk (checkpoint), and resumes from disk on re-run. Single-threaded
default; parallelism comes in the next commit.

The ``trial_fn`` contract:

    trial_fn(config) -> BacktestResult

raises to signal failure. GridRunner wraps the call so the caller does not
need to worry about checkpoint layout or try/except plumbing.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest


def _synthetic_equity(
    periods: int = 30, drift: float = 0.001, noise_seed: int = 42,
) -> pd.Series:
    """Deterministic equity curve that trends up with small Gaussian noise
    (so Sharpe isn't vacuously 0 from zero-volatility returns).
    """
    idx = pd.date_range("2020-01-01", periods=periods, freq="B")
    rng = np.random.default_rng(noise_seed)
    rets = drift + rng.normal(0.0, 0.005, periods)
    values = 100_000.0 * np.cumprod(1.0 + rets)
    return pd.Series(values, index=idx)


def _fake_result(periods: int = 30) -> "object":
    from ai_trade.backtest.engine.runner import BacktestResult

    eq = _synthetic_equity(periods)
    return BacktestResult(
        equity_curve=eq,
        trades=[],
        fills=[],
        initial_cash=100_000.0,
        final_equity=float(eq.iloc[-1]),
    )


def test_grid_runner_produces_trial_per_config(tmp_path: Path):
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.runner import GridRunner

    configs = [
        BollingerMRGridConfig(window=20, std_mult=2.0),
        BollingerMRGridConfig(window=20, std_mult=2.0),
    ]
    trial_fn = MagicMock(side_effect=lambda _cfg: _fake_result(30))
    runner = GridRunner(checkpoint_dir=tmp_path, n_jobs=1)

    grid = runner.run(configs=configs, trial_fn=trial_fn, run_id="test-run")

    assert len(grid.trials) == 2
    assert grid.run_id == "test-run"
    assert all(t.status == "ok" for t in grid.trials)
    assert trial_fn.call_count == 2


def test_grid_runner_catches_exception_and_stores_error_trial(tmp_path: Path):
    """A failing trial must NOT abort the grid — just recorded as error."""
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.runner import GridRunner

    configs = [
        BollingerMRGridConfig(window=20, std_mult=2.0),
        BollingerMRGridConfig(window=40, std_mult=2.0),
        BollingerMRGridConfig(window=20, std_mult=1.5),
    ]

    def _trial_fn(cfg):
        if cfg.window == 40:
            raise RuntimeError("insufficient warmup")
        return _fake_result(30)

    runner = GridRunner(checkpoint_dir=tmp_path, n_jobs=1)
    grid = runner.run(configs=configs, trial_fn=_trial_fn, run_id="err-run")

    assert len(grid.trials) == 3
    statuses = [t.status for t in grid.trials]
    assert statuses.count("ok") == 2
    assert statuses.count("error") == 1
    err_trial = next(t for t in grid.trials if t.status == "error")
    assert "insufficient warmup" in (err_trial.error_msg or "")
    assert err_trial.result is None


def test_grid_runner_computes_scalar_metrics_from_equity_curve(tmp_path: Path):
    """Sharpe / CAGR / max_dd must be cached per trial — gate evaluation relies
    on these without touching the original equity curve.
    """
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.runner import GridRunner

    configs = [BollingerMRGridConfig(window=20, std_mult=2.0)]
    runner = GridRunner(checkpoint_dir=tmp_path, n_jobs=1)
    grid = runner.run(
        configs=configs,
        trial_fn=lambda _cfg: _fake_result(252),  # 1 year
        run_id="metric-run",
    )
    trial = grid.trials[0]
    assert trial.sharpe > 0.0               # trending up with positive drift
    assert trial.cagr > 0.0                  # drift compounds up
    assert trial.max_drawdown >= 0.0         # positive magnitude, may be nonzero with noise


def test_grid_runner_resumes_from_checkpoint(tmp_path: Path):
    """Re-run of a run_id with an existing trial directory must skip the
    trial_fn call (loaded from disk instead).
    """
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import TrialResult, trial_to_dir
    from ai_trade.backtest.grid.runner import GridRunner

    configs = [
        BollingerMRGridConfig(window=20, std_mult=2.0),
        BollingerMRGridConfig(window=20, std_mult=2.0),
    ]

    # Pre-seed trial_0/ as a completed checkpoint.
    run_dir = tmp_path / "resume-run"
    pre_trial = TrialResult(
        config_id=0,
        config=configs[0],
        result=_fake_result(50),
        sharpe=0.77,
        cagr=0.12,
        max_drawdown=0.03,
        status="ok",
    )
    trial_to_dir(pre_trial, run_dir / "trial_0")

    trial_fn = MagicMock(side_effect=lambda _cfg: _fake_result(30))
    runner = GridRunner(checkpoint_dir=tmp_path, n_jobs=1)
    grid = runner.run(configs=configs, trial_fn=trial_fn, run_id="resume-run")

    # trial_fn should have been called only for config 1 (trial 0 was loaded).
    assert trial_fn.call_count == 1
    assert len(grid.trials) == 2
    # Loaded trial retained its pre-seeded metrics (not recomputed).
    loaded = next(t for t in grid.trials if t.config_id == 0)
    assert loaded.sharpe == pytest.approx(0.77)


def test_grid_runner_writes_checkpoint_per_trial(tmp_path: Path):
    """After a run completes, each trial has a directory on disk."""
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.runner import GridRunner

    configs = [
        BollingerMRGridConfig(window=20, std_mult=2.0),
        BollingerMRGridConfig(window=20, std_mult=2.0),
    ]
    runner = GridRunner(checkpoint_dir=tmp_path, n_jobs=1)
    runner.run(
        configs=configs,
        trial_fn=lambda _cfg: _fake_result(30),
        run_id="ckpt-run",
    )
    run_dir = tmp_path / "ckpt-run"
    assert (run_dir / "trial_0" / "meta.json").exists()
    assert (run_dir / "trial_1" / "meta.json").exists()


def test_grid_runner_invokes_progress_callback_after_each_trial(tmp_path: Path):
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.runner import GridRunner

    configs = [
        BollingerMRGridConfig(window=20, std_mult=2.0),
        BollingerMRGridConfig(window=20, std_mult=2.0),
    ]
    callback = MagicMock()
    runner = GridRunner(checkpoint_dir=tmp_path, n_jobs=1)
    runner.run(
        configs=configs,
        trial_fn=lambda _cfg: _fake_result(30),
        run_id="cb-run",
        progress_cb=callback,
    )
    assert callback.call_count == 2
    # Signature: progress_cb(completed, total, trial)
    first_call_args = callback.call_args_list[0].args
    assert len(first_call_args) == 3
    assert first_call_args[1] == 2   # total


def test_grid_runner_parallel_produces_same_results_as_sequential(tmp_path: Path):
    """n_jobs=2 must yield the same TrialResult set as n_jobs=1.

    joblib workers serialize the trial_fn via its loky backend; results come
    back in completion order but we re-sort by config_id downstream. Checkpoint
    dir differs between runs so outputs are independent.
    """
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.runner import GridRunner

    configs = [
        BollingerMRGridConfig(window=20, std_mult=2.0),
        BollingerMRGridConfig(window=20, std_mult=2.0),
        BollingerMRGridConfig(window=20, std_mult=2.0),
    ]

    def _trial_fn(cfg):
        return _fake_result(periods=50 + cfg.window)

    seq_grid = GridRunner(checkpoint_dir=tmp_path / "seq", n_jobs=1).run(
        configs=configs, trial_fn=_trial_fn, run_id="r",
    )
    par_grid = GridRunner(checkpoint_dir=tmp_path / "par", n_jobs=2).run(
        configs=configs, trial_fn=_trial_fn, run_id="r",
    )

    seq_sorted = sorted(seq_grid.trials, key=lambda t: t.config_id)
    par_sorted = sorted(par_grid.trials, key=lambda t: t.config_id)
    for a, b in zip(seq_sorted, par_sorted):
        assert a.config_id == b.config_id
        assert a.status == b.status
        assert a.sharpe == pytest.approx(b.sharpe)
        assert a.cagr == pytest.approx(b.cagr)


def test_grid_runner_resumes_with_error_checkpoint(tmp_path: Path):
    """Pre-existing error checkpoint loads as error trial, no retry."""
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import TrialResult, trial_to_dir
    from ai_trade.backtest.grid.runner import GridRunner

    configs = [
        BollingerMRGridConfig(window=20, std_mult=2.0),
    ]
    run_dir = tmp_path / "err-resume"
    trial_to_dir(
        TrialResult(
            config_id=0,
            config=configs[0],
            result=None,
            sharpe=float("nan"),
            cagr=float("nan"),
            max_drawdown=float("nan"),
            status="error",
            error_msg="previous failure",
        ),
        run_dir / "trial_0",
    )
    trial_fn = MagicMock()
    runner = GridRunner(checkpoint_dir=tmp_path, n_jobs=1)
    grid = runner.run(configs=configs, trial_fn=trial_fn, run_id="err-resume")
    trial_fn.assert_not_called()
    assert grid.trials[0].status == "error"
    assert grid.trials[0].error_msg == "previous failure"
