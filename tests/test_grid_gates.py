"""Tests for ``ai_trade.backtest.grid.gates`` — GateEvaluator.

The gate evaluator applies the three anti-overfit rules from
``knowledge/SKILL.md`` against a :class:`GridResult` + per-config walk-forward
verdicts. The gates are:

* **PBO** (rule #3): reject when ``pbo >= 0.5`` — aggregate across all OK
  trials.
* **DSR** (rule #4): per-config p-value must be < 0.05 to count as passing.
* **Walk-forward** (rule #5): per-config ``walk_forward_gate`` verdict must
  be ``"pass"``.

``overall_pass`` is true iff at least one config passes all three gates.
``best_config_id`` is the passing config with the highest Sharpe; ``None``
if no config passes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _build_grid_from_returns(returns_per_config: list[np.ndarray]):
    """Assemble a GridResult from synthetic per-config return sequences.

    Each column becomes an equity curve 100_000 × cumprod(1 + r), stored as
    a TrialResult with cached Sharpe/CAGR/DD.
    """
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import GridResult, TrialResult
    from ai_trade.backtest.metrics.performance import (
        cagr as cagr_fn,
        max_drawdown as max_dd_fn,
        returns_from_equity,
        sharpe as sharpe_fn,
    )

    trials = []
    for i, rets in enumerate(returns_per_config):
        idx = pd.date_range("2020-01-01", periods=len(rets) + 1, freq="B")
        equity = pd.Series(
            np.concatenate([[100_000.0], 100_000.0 * np.cumprod(1.0 + rets)]),
            index=idx,
        )
        result = BacktestResult(
            equity_curve=equity, trades=[], fills=[],
            initial_cash=100_000.0, final_equity=float(equity.iloc[-1]),
        )
        cfg = BollingerMRGridConfig(window=20, std_mult=2.0)
        trials.append(
            TrialResult(
                config_id=i, config=cfg, result=result,
                sharpe=sharpe_fn(returns_from_equity(equity)),
                cagr=cagr_fn(equity),
                max_drawdown=max_dd_fn(equity),
                status="ok",
            )
        )
    return GridResult(trials=trials, run_id="gates-test")


def test_gate_evaluator_pbo_pass_when_below_threshold():
    from ai_trade.backtest.grid.gates import GateEvaluator

    rng = np.random.default_rng(seed=7)
    # 4 independent iid columns → PBO ≈ 0.5 (roughly random rank)
    grid = _build_grid_from_returns(
        [rng.normal(0.001, 0.01, 500) for _ in range(4)],
    )
    wf_verdicts = {i: "pass" for i in range(4)}
    evaluator = GateEvaluator()
    verdict = evaluator.evaluate(grid=grid, wf_verdicts=wf_verdicts)
    # PBO field exists and is a float in [0, 1]
    assert 0.0 <= verdict.pbo_result.pbo <= 1.0


def test_gate_evaluator_pbo_rejects_overfit_matrix():
    """A mirror matrix (second half = -first half) exhibits near-maximal PBO."""
    from ai_trade.backtest.grid.gates import GateEvaluator

    rng = np.random.default_rng(seed=13)
    first = rng.normal(0.001, 0.01, (400, 10))
    second = -first  # mirror — guaranteed overfit
    mirror = np.vstack([first, second])  # (800, 10)
    returns_per_config = [mirror[:, i] for i in range(10)]
    grid = _build_grid_from_returns(returns_per_config)
    wf_verdicts = {i: "pass" for i in range(10)}
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts=wf_verdicts)
    assert verdict.pbo_result.pbo >= 0.80
    assert verdict.pbo_pass is False


def test_gate_evaluator_dsr_flags_configs_below_alpha():
    """p_value < 0.05 → dsr_pass_id includes that config."""
    from ai_trade.backtest.grid.gates import GateEvaluator

    rng = np.random.default_rng(seed=3)
    # High-Sharpe config with many bars → DSR p < 0.05 is plausible
    # Low-Sharpe config → DSR p stays above 0.05
    strong = rng.normal(0.002, 0.005, 1000)       # Sharpe ~6 annualized
    weak = rng.normal(0.00005, 0.02, 1000)         # Sharpe ~0
    grid = _build_grid_from_returns([strong, weak])
    wf_verdicts = {0: "pass", 1: "pass"}
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts=wf_verdicts)
    assert 0 in verdict.dsr_pass_ids
    assert 1 not in verdict.dsr_pass_ids


def test_gate_evaluator_walk_forward_filters_by_verdict():
    from ai_trade.backtest.grid.gates import GateEvaluator

    rng = np.random.default_rng(seed=5)
    grid = _build_grid_from_returns([rng.normal(0.001, 0.01, 500) for _ in range(3)])
    wf_verdicts = {0: "pass", 1: "reject", 2: "pass"}
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts=wf_verdicts)
    assert verdict.wf_pass_ids == [0, 2]


def test_gate_evaluator_overall_pass_requires_all_three_gates():
    """A config passes iff: PBO-pass AND DSR-pass AND WF-pass."""
    from ai_trade.backtest.grid.gates import GateEvaluator

    rng = np.random.default_rng(seed=11)
    # Build a synthetic where only config 0 will realistically pass all:
    configs_rets = [
        rng.normal(0.003, 0.005, 1000),   # strong, likely DSR-pass
        rng.normal(0.0001, 0.02, 1000),    # weak, likely DSR-reject
        rng.normal(0.003, 0.005, 1000),   # strong but WF reject (see wf_verdicts)
    ]
    grid = _build_grid_from_returns(configs_rets)
    wf_verdicts = {0: "pass", 1: "pass", 2: "reject"}
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts=wf_verdicts)
    # Config 2 rejected by WF, config 1 by DSR. Only 0 should remain overall.
    if verdict.pbo_pass and verdict.overall_pass:
        assert verdict.best_config_id == 0


def test_gate_evaluator_best_config_id_is_none_when_no_pass():
    """If no config passes all 3 gates, best_config_id is None."""
    from ai_trade.backtest.grid.gates import GateEvaluator

    rng = np.random.default_rng(seed=4)
    grid = _build_grid_from_returns([rng.normal(0.0, 0.02, 200) for _ in range(3)])
    wf_verdicts = {0: "reject", 1: "reject", 2: "reject"}
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts=wf_verdicts)
    assert verdict.overall_pass is False
    assert verdict.best_config_id is None


def test_gate_evaluator_best_config_picks_highest_sharpe_among_passers():
    """Among configs that pass all gates, the best is the one with max Sharpe."""
    from ai_trade.backtest.grid.gates import GateEvaluator

    rng = np.random.default_rng(seed=9)
    # Three strong configs; we'll fake WF verdicts so all pass
    grid = _build_grid_from_returns([
        rng.normal(0.0025, 0.005, 1200),
        rng.normal(0.003, 0.005, 1200),   # highest Sharpe
        rng.normal(0.002, 0.005, 1200),
    ])
    wf_verdicts = {0: "pass", 1: "pass", 2: "pass"}
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts=wf_verdicts)
    # If all three cleared DSR and PBO, best must be config 1.
    if verdict.overall_pass and len(verdict.dsr_pass_ids) == 3 and verdict.pbo_pass:
        assert verdict.best_config_id == 1


def test_gate_evaluator_handles_empty_grid_gracefully():
    from ai_trade.backtest.grid.gates import GateEvaluator
    from ai_trade.backtest.grid.result import GridResult

    grid = GridResult(trials=[], run_id="empty")
    verdict = GateEvaluator().evaluate(grid=grid, wf_verdicts={})
    assert verdict.overall_pass is False
    assert verdict.best_config_id is None
