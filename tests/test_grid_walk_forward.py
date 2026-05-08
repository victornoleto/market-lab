"""Tests for ``ai_trade.backtest.grid.walk_forward`` — per-config WF gate.

Design choice: for fixed-config strategies (Clenow is one — no per-window
re-optimization) running the full backtest once and slicing the equity curve
into contiguous OOS chunks is mathematically equivalent to running each
window independently. ``wf_for_config`` implements this: it takes the
already-computed equity curve, splits it into ``n_windows`` chunks, and
applies ``walk_forward_gate``.

This matches the pattern in ``scripts/run_clenow_replication.py:100-133``
which the single-trial CLI already uses. The grid version differs only in
carrying a ``config_id`` through the result for downstream aggregation by
:class:`GateEvaluator`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _equity_from_window_returns(window_returns: list[float], periods_per_window: int = 50) -> pd.Series:
    """Build an equity curve that hits exactly the supplied per-window returns.

    Each window lasts ``periods_per_window`` business days; daily return
    within a window is constant (compounds to the target window return).
    """
    start_equity = 100_000.0
    values = [start_equity]
    for r in window_returns:
        daily = (1.0 + r) ** (1.0 / periods_per_window) - 1.0
        for _ in range(periods_per_window):
            values.append(values[-1] * (1.0 + daily))
    idx = pd.date_range("2020-01-01", periods=len(values), freq="B")
    return pd.Series(values, index=idx)


def test_wf_for_config_returns_verdict_pass_for_trending_equity():
    """8 windows all positive → 8/8 profitable, no DD → verdict pass."""
    from ai_trade.backtest.grid.walk_forward import wf_for_config

    equity = _equity_from_window_returns([0.02] * 8, periods_per_window=30)
    wf = wf_for_config(equity_curve=equity, config_id=7, n_windows=8)
    assert wf.verdict == "pass"
    assert wf.n_windows == 8
    assert wf.n_profitable == 8
    assert wf.config_id == 7
    assert wf.max_drawdown == pytest.approx(0.0, abs=1e-6)


def test_wf_for_config_rejects_when_too_few_profitable():
    """4/8 profitable fails the ≥6/8 rule."""
    from ai_trade.backtest.grid.walk_forward import wf_for_config

    equity = _equity_from_window_returns(
        [0.02, -0.02, 0.02, -0.02, 0.02, -0.02, 0.02, -0.02],
        periods_per_window=30,
    )
    wf = wf_for_config(equity_curve=equity, config_id=0, n_windows=8)
    assert wf.verdict == "reject"
    assert wf.n_profitable < 6


def test_wf_for_config_rejects_when_drawdown_exceeds_25_percent():
    """Any window with DD > 25% → reject regardless of profitability."""
    from ai_trade.backtest.grid.walk_forward import wf_for_config

    # One window with a 40% loss (way over the 25% DD gate)
    equity = _equity_from_window_returns(
        [0.02, 0.02, 0.02, -0.40, 0.02, 0.02, 0.02, 0.02],
        periods_per_window=30,
    )
    wf = wf_for_config(equity_curve=equity, config_id=1, n_windows=8)
    assert wf.verdict == "reject"
    assert wf.max_drawdown > 0.25


def test_wf_for_config_captures_per_window_breakdown():
    """Result carries OOS returns + drawdowns per window for diagnostics."""
    from ai_trade.backtest.grid.walk_forward import wf_for_config

    equity = _equity_from_window_returns([0.01] * 8, periods_per_window=30)
    wf = wf_for_config(equity_curve=equity, config_id=2, n_windows=8)
    assert len(wf.oos_returns) == 8
    assert len(wf.oos_drawdowns) == 8
    # Each per-window return should be close to 0.01 (small rounding from compounding)
    for r in wf.oos_returns:
        assert abs(r - 0.01) < 1e-3


def test_wf_for_config_handles_equity_too_short_for_8_windows():
    """< 80 bars (8 windows × 10 bars) → verdict reject, n_windows may be 0."""
    from ai_trade.backtest.grid.walk_forward import wf_for_config

    idx = pd.date_range("2020-01-01", periods=20, freq="B")
    equity = pd.Series(np.linspace(100_000.0, 101_000.0, 20), index=idx)
    wf = wf_for_config(equity_curve=equity, config_id=5, n_windows=8)
    assert wf.verdict == "reject"


def test_wf_for_config_respects_custom_n_windows():
    """Caller can request a different window count (10 windows, for example)."""
    from ai_trade.backtest.grid.walk_forward import wf_for_config

    equity = _equity_from_window_returns([0.01] * 10, periods_per_window=30)
    wf = wf_for_config(equity_curve=equity, config_id=0, n_windows=10)
    assert wf.n_windows == 10
    assert len(wf.oos_returns) == 10


def test_wf_for_config_over_all_grid_delegates_to_single_config_impl():
    """wf_for_grid runs wf_for_config per trial in parallel (via joblib or
    sequential) and returns dict[config_id, WFResult]. We test the shape.
    """
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import GridResult, TrialResult
    from ai_trade.backtest.grid.walk_forward import wf_for_grid

    equities = [
        _equity_from_window_returns([0.01] * 8, periods_per_window=30),
        _equity_from_window_returns([0.02] * 8, periods_per_window=30),
    ]
    trials = []
    for i, eq in enumerate(equities):
        result = BacktestResult(
            equity_curve=eq, trades=[], fills=[],
            initial_cash=100_000.0, final_equity=float(eq.iloc[-1]),
        )
        cfg = BollingerMRGridConfig(window=20, std_mult=2.0)
        trials.append(
            TrialResult(
                config_id=i, config=cfg, result=result,
                sharpe=0.5, cagr=0.1, max_drawdown=0.0, status="ok",
            )
        )
    grid = GridResult(trials=trials, run_id="grid-wf")
    results = wf_for_grid(grid, n_windows=8, n_jobs=1)
    assert set(results.keys()) == {0, 1}
    assert all(r.verdict == "pass" for r in results.values())
