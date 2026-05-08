"""Tests for ``ai_trade.backtest.grid.diagnostic`` — DiagnosticAnalyzer.

When the gate evaluator reports ``overall_pass=False``, DiagnosticAnalyzer
classifies the failure mode and surfaces enough structured data for the
user (you) to decide the next move without re-running anything:

* **PBO_HIGH** — PBO ≥ 0.5 (rule #3): the grid looks overfit; even if
  individual Sharpes look good, IS-best configs don't keep their rank OOS.
* **DSR_ALL_FAIL** — no config has DSR p < 0.05 (rule #4): after deflating
  for multiple trials, no edge is statistically significant.
* **WF_INSUFFICIENT** — no config has walk-forward verdict "pass" (rule #5):
  OOS generalization broke in ≥3 windows.
* **COMBINED** — two or more of the above.

The diagnostic also identifies the ``best_config`` (highest Sharpe among
OK trials — **ignores gates**, useful for "closest-to-passing" analysis)
and a per-config metrics DataFrame with columns ready for the report.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _mk_grid(sharpes: list[float]):
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import GridResult, TrialResult

    trials = []
    rng = np.random.default_rng(42)
    for i, s in enumerate(sharpes):
        # Synthetic equity — values don't matter for diagnostic tests that
        # focus on cached metrics, only for those that read equity_curve.
        idx = pd.date_range("2020-01-01", periods=30, freq="B")
        eq = pd.Series(
            100_000.0 * np.cumprod(1.0 + rng.normal(0.001, 0.005, 30)),
            index=idx,
        )
        result = BacktestResult(
            equity_curve=eq, trades=[], fills=[],
            initial_cash=100_000.0, final_equity=float(eq.iloc[-1]),
        )
        cfg = BollingerMRGridConfig(window=20, std_mult=2.0)
        trials.append(
            TrialResult(
                config_id=i, config=cfg, result=result,
                sharpe=s, cagr=0.1, max_drawdown=0.05, status="ok",
            )
        )
    return GridResult(trials=trials, run_id="diag")


def _mk_verdict(
    pbo_pass: bool,
    dsr_pass_ids: list[int],
    wf_pass_ids: list[int],
    pbo_value: float = 0.3,
    n_configs: int = 3,
):
    from ai_trade.backtest.grid.gates import GateVerdict
    from ai_trade.backtest.validation.pbo import PBOResult

    pbo_result = PBOResult(
        pbo=pbo_value, logits=np.zeros(10), n_blocks=10, n_combinations=252,
    )
    wf_verdicts = {
        i: "pass" if i in wf_pass_ids else "reject"
        for i in range(n_configs)
    }
    return GateVerdict(
        pbo_result=pbo_result,
        pbo_pass=pbo_pass,
        dsr_results={},  # not used by diagnostic
        dsr_pass_ids=dsr_pass_ids,
        wf_verdicts=wf_verdicts,
        wf_pass_ids=wf_pass_ids,
        overall_pass=False,
        best_config_id=None,
    )


def _mk_wf_results(config_ids: list[int]):
    from ai_trade.backtest.grid.walk_forward import WFResult

    return {
        i: WFResult(
            config_id=i, n_windows=8,
            n_profitable=3 if i == 0 else 7,
            max_drawdown=0.10,
            verdict="reject" if i == 0 else "pass",
        )
        for i in config_ids
    }


def test_diagnostic_pbo_high_mode():
    from ai_trade.backtest.grid.diagnostic import DiagnosticAnalyzer

    grid = _mk_grid([0.5, 1.2, 0.8])
    verdict = _mk_verdict(
        pbo_pass=False, pbo_value=0.7,
        dsr_pass_ids=[0, 1, 2],
        wf_pass_ids=[0, 1, 2],
    )
    wf_results = _mk_wf_results([0, 1, 2])
    report = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=wf_results,
    )
    labels = [mode.label for mode in report.failure_modes]
    assert "PBO_HIGH" in labels
    assert "DSR_ALL_FAIL" not in labels


def test_diagnostic_dsr_all_fail_mode():
    from ai_trade.backtest.grid.diagnostic import DiagnosticAnalyzer

    grid = _mk_grid([0.5, 0.8, 1.2])
    verdict = _mk_verdict(
        pbo_pass=True, pbo_value=0.3,
        dsr_pass_ids=[],
        wf_pass_ids=[0, 1, 2],
    )
    report = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=_mk_wf_results([0, 1, 2]),
    )
    labels = [mode.label for mode in report.failure_modes]
    assert "DSR_ALL_FAIL" in labels


def test_diagnostic_wf_insufficient_mode():
    from ai_trade.backtest.grid.diagnostic import DiagnosticAnalyzer

    grid = _mk_grid([0.5, 0.8, 1.2])
    verdict = _mk_verdict(
        pbo_pass=True, pbo_value=0.3,
        dsr_pass_ids=[0, 1, 2],
        wf_pass_ids=[],
    )
    report = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=_mk_wf_results([0, 1, 2]),
    )
    labels = [mode.label for mode in report.failure_modes]
    assert "WF_INSUFFICIENT" in labels


def test_diagnostic_combined_mode_tagged_when_multiple_gates_fail():
    from ai_trade.backtest.grid.diagnostic import DiagnosticAnalyzer

    grid = _mk_grid([0.5, 0.8, 1.2])
    verdict = _mk_verdict(
        pbo_pass=False, pbo_value=0.8,
        dsr_pass_ids=[],
        wf_pass_ids=[],
    )
    report = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=_mk_wf_results([0, 1, 2]),
    )
    labels = [mode.label for mode in report.failure_modes]
    assert "COMBINED" in labels


def test_diagnostic_best_config_has_highest_sharpe_regardless_of_gates():
    """best_config is selected by cached Sharpe, independent of gate verdicts.
    Useful to surface "how close did we get?" even when everything fails.
    """
    from ai_trade.backtest.grid.diagnostic import DiagnosticAnalyzer

    grid = _mk_grid([0.5, 0.8, 1.9])
    verdict = _mk_verdict(
        pbo_pass=False, pbo_value=0.7,
        dsr_pass_ids=[],
        wf_pass_ids=[],
    )
    report = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=_mk_wf_results([0, 1, 2]),
    )
    assert report.best_config.config_id == 2
    assert report.best_config.sharpe == pytest.approx(1.9)


def test_diagnostic_per_config_metrics_has_expected_columns():
    from ai_trade.backtest.grid.diagnostic import DiagnosticAnalyzer

    grid = _mk_grid([0.5, 0.8, 1.2])
    verdict = _mk_verdict(
        pbo_pass=False, pbo_value=0.7,
        dsr_pass_ids=[2],
        wf_pass_ids=[1, 2],
    )
    report = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=_mk_wf_results([0, 1, 2]),
    )
    df = report.per_config_metrics
    for col in (
        "config_id", "window", "std_mult",
        "sharpe", "cagr", "max_drawdown", "dsr_pass", "wf_verdict",
    ):
        assert col in df.columns
    assert len(df) == 3


def test_diagnostic_recommendation_text_is_nonempty_and_cites_failure_modes():
    from ai_trade.backtest.grid.diagnostic import DiagnosticAnalyzer

    grid = _mk_grid([0.5, 0.8, 1.2])
    verdict = _mk_verdict(
        pbo_pass=False, pbo_value=0.7,
        dsr_pass_ids=[],
        wf_pass_ids=[1, 2],
    )
    report = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=_mk_wf_results([0, 1, 2]),
    )
    assert len(report.recommendation) > 50
    # Must reference at least one failure mode label
    assert any(
        mode.label in report.recommendation for mode in report.failure_modes
    )


def test_diagnostic_handles_grid_with_error_trials_gracefully():
    """Error trials (status='error') appear in per_config_metrics as NaN rows."""
    from ai_trade.backtest.engine.runner import BacktestResult
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.diagnostic import DiagnosticAnalyzer
    from ai_trade.backtest.grid.result import GridResult, TrialResult

    idx = pd.date_range("2020-01-01", periods=30, freq="B")
    eq = pd.Series(100_000.0 + np.arange(30, dtype=float) * 10.0, index=idx)
    ok_trial = TrialResult(
        config_id=0,
        config=BollingerMRGridConfig(window=20, std_mult=2.0),
        result=BacktestResult(
            equity_curve=eq, trades=[], fills=[],
            initial_cash=100_000.0, final_equity=float(eq.iloc[-1]),
        ),
        sharpe=0.5, cagr=0.1, max_drawdown=0.02, status="ok",
    )
    err_trial = TrialResult(
        config_id=1,
        config=BollingerMRGridConfig(window=20, std_mult=2.0),
        result=None,
        sharpe=float("nan"), cagr=float("nan"), max_drawdown=float("nan"),
        status="error", error_msg="boom",
    )
    grid = GridResult(trials=[ok_trial, err_trial], run_id="err-diag")
    verdict = _mk_verdict(
        pbo_pass=True, pbo_value=0.3, dsr_pass_ids=[], wf_pass_ids=[0],
        n_configs=2,
    )
    wf_results = _mk_wf_results([0])
    report = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=wf_results,
    )
    assert len(report.per_config_metrics) == 2
    err_row = report.per_config_metrics[report.per_config_metrics.config_id == 1]
    assert err_row["sharpe"].isna().all()


def _mk_grid_all_errored(n: int = 4):
    """Grid where ALL trials errored upstream of the backtest (no equity curve)."""
    from ai_trade.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from ai_trade.backtest.grid.result import GridResult, TrialResult

    trials = []
    for i in range(n):
        cfg = BollingerMRGridConfig(window=20, std_mult=2.0)
        trials.append(
            TrialResult(
                config_id=i, config=cfg, result=None,
                sharpe=float("nan"), cagr=float("nan"), max_drawdown=float("nan"),
                status="error",
                error_msg=(
                    f"trial {i} failed: pair not cointegrated "
                    f"(t_stat_OU=-2.5 > -3.4)"
                ),
            )
        )
    return GridResult(trials=trials, run_id="diag_all_err")


def _mk_verdict_no_pbo(n_configs: int = 4):
    """Verdict for grids where PBO/DSR/WF couldn't be computed."""
    from ai_trade.backtest.grid.gates import GateVerdict

    return GateVerdict(
        pbo_result=None,
        pbo_pass=False,
        dsr_results={},
        dsr_pass_ids=[],
        wf_verdicts={},
        wf_pass_ids=[],
        overall_pass=False,
        best_config_id=None,
    )


def test_diagnostic_handles_all_trials_errored():
    """All trials errored at __post_init__ (gate upstream of backtest).

    DiagnosticAnalyzer must NOT raise; must surface a GATE_UPSTREAM_FAIL
    failure mode and a degenerate best_config that the report layer can
    handle gracefully (per existing report.py:263 defensive check).
    """
    from ai_trade.backtest.grid.diagnostic import DiagnosticAnalyzer

    grid = _mk_grid_all_errored(n=4)
    verdict = _mk_verdict_no_pbo(n_configs=4)
    wf_results = {}  # WF can't run on errored trials

    report = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=wf_results,
    )

    labels = {m.label for m in report.failure_modes}
    assert "GATE_UPSTREAM_FAIL" in labels, (
        f"expected GATE_UPSTREAM_FAIL in failure modes, got {labels}"
    )
    # When upstream fails, other modes shouldn't be classified — they're misleading
    assert "PBO_HIGH" not in labels
    assert "DSR_ALL_FAIL" not in labels

    # Degenerate best_config: first trial's config dims, no result, error status
    assert report.best_config.result is None
    assert report.best_config.status == "error"
    assert report.best_config.config_id == 0
    assert report.best_config.error_msg is not None
    assert "cointegrated" in report.best_config.error_msg

    # Recommendation must mention the upstream fail and the actual error
    rec_lower = report.recommendation.lower()
    assert "gate_upstream_fail" in rec_lower or "all trials" in rec_lower
