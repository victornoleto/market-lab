"""Tests for ``ai_trade.backtest.grid.result`` — trial + grid containers + I/O.

Two concerns:

1. **Shape of TrialResult / GridResult** — a TrialResult bundles a config with
   the BacktestResult it produced (plus scalar metrics cached for fast gate
   evaluation). A GridResult stacks trials + exposes the ``returns_matrix``
   (T, N) aligned on a common DatetimeIndex, which is the input to
   :func:`ai_trade.backtest.validation.pbo.pbo`.

2. **Safe serialization** — checkpoint/resume uses parquet (for pandas
   structures) + JSON (for scalars). Crash mid-run → re-run reads completed
   trials from disk and continues.

``_align_returns`` must handle configs that produce equity curves of
different lengths (configs with larger lookbacks start trading later).
The intersection of DatetimeIndexes + ``ffill`` yields a no-NaN matrix.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _make_equity(start: str, periods: int, start_value: float = 100_000.0) -> pd.Series:
    idx = pd.date_range(start=start, periods=periods, freq="B")
    values = start_value + np.arange(periods, dtype=float) * 10.0
    return pd.Series(values, index=idx, name="equity")


def test_align_returns_with_three_equity_curves_of_different_lengths():
    """Configs with larger lookbacks start later — intersection picks the
    overlapping window. No NaN in the final matrix.
    """
    from ai_trade.backtest.grid.result import _align_returns

    eq_a = _make_equity("2020-01-01", 100)
    eq_b = _make_equity("2020-02-10", 60)
    eq_c = _make_equity("2020-01-20", 80)

    matrix = _align_returns([eq_a, eq_b, eq_c])

    assert isinstance(matrix, np.ndarray)
    assert matrix.ndim == 2
    assert matrix.shape[1] == 3
    assert matrix.shape[0] > 0
    assert not np.isnan(matrix).any()


def test_align_returns_single_series_returns_two_dim_matrix():
    from ai_trade.backtest.grid.result import _align_returns

    matrix = _align_returns([_make_equity("2020-01-01", 30)])
    assert matrix.ndim == 2
    assert matrix.shape[1] == 1
    assert matrix.shape[0] > 0


def test_align_returns_rejects_empty_input():
    from ai_trade.backtest.grid.result import _align_returns

    with pytest.raises(ValueError):
        _align_returns([])


def test_trial_result_carries_config_and_scalar_metrics():
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import TrialResult

    equity = _make_equity("2020-01-01", 50)
    result = BacktestResult(
        equity_curve=equity,
        trades=[],
        fills=[],
        initial_cash=100_000.0,
        final_equity=float(equity.iloc[-1]),
    )
    config = BollingerMRGridConfig(window=20, std_mult=2.0)

    trial = TrialResult(
        config_id=7,
        config=config,
        result=result,
        sharpe=0.82,
        cagr=0.14,
        max_drawdown=0.05,
        status="ok",
    )
    assert trial.status == "ok"
    assert trial.error_msg is None
    assert trial.config_id == 7
    assert trial.sharpe == pytest.approx(0.82)


def test_trial_result_error_status_stores_error_message():
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import TrialResult

    config = BollingerMRGridConfig(window=20, std_mult=2.0)
    trial = TrialResult(
        config_id=0,
        config=config,
        result=None,
        sharpe=float("nan"),
        cagr=float("nan"),
        max_drawdown=float("nan"),
        status="error",
        error_msg="insufficient data",
    )
    assert trial.status == "error"
    assert trial.error_msg == "insufficient data"
    assert trial.result is None


def test_trial_to_dir_writes_expected_files(tmp_path: Path):
    """Checkpoint layout: trial_N/ with equity.parquet, trades.parquet,
    fills.parquet, meta.json.
    """
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import TrialResult, trial_to_dir

    equity = _make_equity("2020-01-01", 10)
    result = BacktestResult(
        equity_curve=equity,
        trades=[],
        fills=[],
        initial_cash=100_000.0,
        final_equity=float(equity.iloc[-1]),
    )
    config = BollingerMRGridConfig(window=20, std_mult=2.0)
    trial = TrialResult(
        config_id=3,
        config=config,
        result=result,
        sharpe=0.5,
        cagr=0.1,
        max_drawdown=0.02,
        status="ok",
    )
    trial_dir = tmp_path / "trial_3"
    trial_to_dir(trial, trial_dir)

    assert (trial_dir / "equity.parquet").exists()
    assert (trial_dir / "trades.parquet").exists()
    assert (trial_dir / "fills.parquet").exists()
    assert (trial_dir / "meta.json").exists()

    meta = json.loads((trial_dir / "meta.json").read_text())
    assert meta["config_id"] == 3
    assert meta["status"] == "ok"
    assert meta["sharpe"] == pytest.approx(0.5)
    assert meta["config"]["window"] == 20


def test_trial_round_trip_to_and_from_dir(tmp_path: Path):
    """Round-trip preserves config, metrics, status, equity curve values."""
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import (
        TrialResult,
        trial_from_dir,
        trial_to_dir,
    )

    equity = _make_equity("2020-01-01", 15)
    result = BacktestResult(
        equity_curve=equity,
        trades=[],
        fills=[],
        initial_cash=100_000.0,
        final_equity=float(equity.iloc[-1]),
    )
    config = BollingerMRGridConfig(window=20, std_mult=2.0)
    trial = TrialResult(
        config_id=23,
        config=config,
        result=result,
        sharpe=1.42,
        cagr=0.18,
        max_drawdown=0.07,
        status="ok",
    )
    trial_dir = tmp_path / "trial_23"
    trial_to_dir(trial, trial_dir)

    restored = trial_from_dir(trial_dir)
    assert restored.config_id == 23
    assert restored.status == "ok"
    assert restored.config == config
    assert restored.sharpe == pytest.approx(1.42)
    assert restored.result is not None
    pd.testing.assert_series_equal(
        restored.result.equity_curve, equity, check_names=False, check_freq=False,
    )


def test_trial_from_dir_on_error_trial_reconstructs_without_result(tmp_path: Path):
    """Error trials have result=None; meta.json still persists config + error_msg."""
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import (
        TrialResult,
        trial_from_dir,
        trial_to_dir,
    )

    config = BollingerMRGridConfig(window=20, std_mult=2.0)
    trial = TrialResult(
        config_id=0,
        config=config,
        result=None,
        sharpe=float("nan"),
        cagr=float("nan"),
        max_drawdown=float("nan"),
        status="error",
        error_msg="warmup insufficient",
    )
    trial_dir = tmp_path / "trial_0"
    trial_to_dir(trial, trial_dir)

    restored = trial_from_dir(trial_dir)
    assert restored.status == "error"
    assert restored.error_msg == "warmup insufficient"
    assert restored.result is None
    assert restored.config == config


def test_grid_result_exposes_returns_matrix_and_configs():
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import GridResult, TrialResult

    trials = []
    for i, (lb, tp, rf) in enumerate([(60, 0.10, 0.001), (90, 0.20, 0.001)]):
        equity = _make_equity("2020-01-01", 50)
        result = BacktestResult(
            equity_curve=equity,
            trades=[],
            fills=[],
            initial_cash=100_000.0,
            final_equity=float(equity.iloc[-1]),
        )
        config = BollingerMRGridConfig(window=20, std_mult=2.0)
        trials.append(
            TrialResult(
                config_id=i,
                config=config,
                result=result,
                sharpe=0.5 + 0.1 * i,
                cagr=0.1,
                max_drawdown=0.02,
                status="ok",
            )
        )

    grid = GridResult(trials=trials, run_id="20260414-1200")
    matrix = grid.returns_matrix
    assert matrix.shape[1] == 2
    assert grid.run_id == "20260414-1200"
    assert len(grid.configs) == 2


def test_grid_result_returns_matrix_excludes_error_trials():
    """Error trials (status='error') must NOT appear in the returns matrix
    (``pbo`` would otherwise crash on the NaN column / missing curve).
    """
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import GridResult, TrialResult

    equity = _make_equity("2020-01-01", 50)
    result = BacktestResult(
        equity_curve=equity, trades=[], fills=[],
        initial_cash=100_000.0, final_equity=float(equity.iloc[-1]),
    )
    cfg_ok = BollingerMRGridConfig(window=20, std_mult=2.0)
    cfg_bad = BollingerMRGridConfig(window=20, std_mult=2.0)

    ok_trial = TrialResult(
        config_id=0, config=cfg_ok, result=result,
        sharpe=0.5, cagr=0.1, max_drawdown=0.02, status="ok",
    )
    bad_trial = TrialResult(
        config_id=29, config=cfg_bad, result=None,
        sharpe=float("nan"), cagr=float("nan"), max_drawdown=float("nan"),
        status="error", error_msg="boom",
    )
    grid = GridResult(trials=[ok_trial, bad_trial], run_id="xxx")
    assert grid.returns_matrix.shape[1] == 1
