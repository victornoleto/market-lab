"""Tests for ``ai_trade.backtest.grid.observers`` — JSONL + status.md.

Observers are callables with signature ``(completed, total, trial) -> None``,
matching :data:`ai_trade.backtest.grid.runner.ProgressCb`. The CLI wires
them in parallel: after each trial completes, the runner calls every
registered observer. The runner core itself stays unaware of file layouts.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _mk_trial(config_id: int, status: str = "ok", sharpe: float = 0.82):
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.config import ClenowGridConfig
    from ai_trade.backtest.grid.result import TrialResult

    cfg = ClenowGridConfig(
        lookback_regression=60 + config_id, top_pct=0.20, risk_factor=0.001,
    )
    if status == "error":
        return TrialResult(
            config_id=config_id, config=cfg, result=None,
            sharpe=float("nan"), cagr=float("nan"), max_drawdown=float("nan"),
            status="error", error_msg="synthetic failure",
        )
    idx = pd.date_range("2020-01-01", periods=30, freq="B")
    eq = pd.Series(100_000.0 + np.arange(30, dtype=float) * 100.0, index=idx)
    result = BacktestResult(
        equity_curve=eq, trades=[], fills=[],
        initial_cash=100_000.0, final_equity=float(eq.iloc[-1]),
    )
    return TrialResult(
        config_id=config_id, config=cfg, result=result,
        sharpe=sharpe, cagr=0.14, max_drawdown=0.05, status="ok",
    )


def test_jsonl_trial_observer_writes_one_line_per_trial(tmp_path: Path):
    from ai_trade.backtest.grid.observers import JsonlTrialObserver

    path = tmp_path / "trials.jsonl"
    obs = JsonlTrialObserver(path=path, run_id="run-A")
    obs(1, 3, _mk_trial(0, status="ok"))
    obs(2, 3, _mk_trial(1, status="error"))
    obs(3, 3, _mk_trial(2, status="ok", sharpe=1.2))

    lines = path.read_text().strip().splitlines()
    assert len(lines) == 3
    first = json.loads(lines[0])
    assert first["run_id"] == "run-A"
    assert first["config_id"] == 0
    assert first["status"] == "ok"
    assert first["sharpe"] == pytest.approx(0.82)
    assert "lookback_regression" in first["config"]
    assert first["completed"] == 1
    assert first["total"] == 3


def test_jsonl_trial_observer_encodes_nan_as_string(tmp_path: Path):
    """Error trials have sharpe=NaN — JSON can't represent NaN natively,
    so we emit "nan" / "inf" / "-inf" strings for consistency.
    """
    from ai_trade.backtest.grid.observers import JsonlTrialObserver

    path = tmp_path / "trials.jsonl"
    obs = JsonlTrialObserver(path=path, run_id="nan-run")
    obs(1, 1, _mk_trial(0, status="error"))
    parsed = json.loads(path.read_text().strip())
    assert parsed["sharpe"] == "nan"
    assert parsed["status"] == "error"
    assert parsed["error_msg"] == "synthetic failure"


def test_status_file_observer_writes_markdown_snapshot(tmp_path: Path):
    """After each trial the observer overwrites status.md with the latest
    aggregate: completed/total, best Sharpe so far, ETA.
    """
    from ai_trade.backtest.grid.observers import StatusFileObserver

    path = tmp_path / "status.md"
    obs = StatusFileObserver(path=path, run_id="status-run")
    obs(1, 3, _mk_trial(0, status="ok", sharpe=0.5))
    obs(2, 3, _mk_trial(1, status="ok", sharpe=1.1))
    obs(3, 3, _mk_trial(2, status="error"))

    content = path.read_text()
    assert "status-run" in content
    assert "3/3" in content
    # Best Sharpe so far should mention the 1.1 value
    assert "1.1" in content or "1.10" in content
    # Error count surfaces
    assert "Errors:** 1" in content or "1 error" in content.lower()


def test_status_file_observer_overwrites_each_call(tmp_path: Path):
    """Only the latest snapshot must be on disk (no append)."""
    from ai_trade.backtest.grid.observers import StatusFileObserver

    path = tmp_path / "status.md"
    obs = StatusFileObserver(path=path, run_id="overwrite-run")
    obs(1, 2, _mk_trial(0, status="ok"))
    first_size = path.stat().st_size
    obs(2, 2, _mk_trial(1, status="ok"))
    second_content = path.read_text()
    # Must show 2/2, not still show 1/2
    assert "2/2" in second_content
    # Size may differ; the key is the content is updated.
    assert "1/2" not in second_content


def test_multiple_observers_can_be_composed(tmp_path: Path):
    """CLI wires multiple observers — runner calls each one per trial."""
    from ai_trade.backtest.grid.observers import (
        JsonlTrialObserver,
        StatusFileObserver,
        compose_observers,
    )

    jsonl_path = tmp_path / "trials.jsonl"
    status_path = tmp_path / "status.md"
    obs = compose_observers(
        JsonlTrialObserver(path=jsonl_path, run_id="compose"),
        StatusFileObserver(path=status_path, run_id="compose"),
    )
    obs(1, 1, _mk_trial(0))
    assert jsonl_path.exists()
    assert status_path.exists()


def test_setup_grid_logging_installs_four_handlers(tmp_path: Path):
    """setup_grid_logging attaches 4 handlers to the ai_trade.grid logger:
    console, per-run debug file, per-run JSONL (not used directly — that's
    what the observer is for), and unified append log.
    """
    import logging
    from ai_trade.backtest.grid.observers import setup_grid_logging

    run_dir = tmp_path / "run-logs"
    unified = tmp_path / "unified.log"

    handlers_before = list(logging.getLogger("ai_trade.grid").handlers)
    try:
        setup_grid_logging(
            run_id="abc",
            run_dir=run_dir,
            unified_log_path=unified,
            level=logging.INFO,
        )
        logger = logging.getLogger("ai_trade.grid")
        logger.info("hello grid")
        # Per-run debug file should exist after a log
        assert (run_dir / "debug.log").exists()
        # Unified file should exist after a log
        assert unified.exists()
        # Unified log entry carries the run_id prefix
        unified_text = unified.read_text()
        assert "abc" in unified_text
        assert "hello grid" in unified_text
    finally:
        # Remove the handlers we added so other tests aren't affected.
        for h in list(logging.getLogger("ai_trade.grid").handlers):
            if h not in handlers_before:
                logging.getLogger("ai_trade.grid").removeHandler(h)
                h.close()
