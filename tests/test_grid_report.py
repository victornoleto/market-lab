"""Tests for ``market_lab.backtest.grid.report`` — GridReportGenerator.

GridReportGenerator emits Markdown + PNG assets summarizing a grid run.
Two entry points:

* ``write_pass_report`` — when GateVerdict.overall_pass is True. Shows the
  best config, gate details, Sharpe heatmap, and "next step" pointer.
* ``write_fail_report`` — when gates failed. Shows failure modes from the
  DiagnosticReport, per-config breakdown, PBO logit distribution, and the
  textual recommendation.

Both reports carry the survivorship disclaimer when the data source is
biased (yfinance) — the mandatory rule from ``knowledge/SKILL.md``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _build_synthetic_world(n_configs: int = 3, seed: int = 0):
    """Assemble grid + verdict + wf_results + diagnostic for report tests."""
    from market_lab.backtest.engine.runner import BacktestResult
    from market_lab.backtest.grid.bollinger_mr_config import BollingerMRGridConfig
    from market_lab.backtest.grid.diagnostic import DiagnosticAnalyzer
    from market_lab.backtest.grid.gates import GateVerdict
    from market_lab.backtest.grid.result import GridResult, TrialResult
    from market_lab.backtest.grid.walk_forward import WFResult
    from market_lab.backtest.validation.dsr import DSRResult
    from market_lab.backtest.validation.pbo import PBOResult

    rng = np.random.default_rng(seed)
    trials = []
    for i in range(n_configs):
        idx = pd.date_range("2020-01-01", periods=500, freq="B")
        eq = pd.Series(
            100_000.0 * np.cumprod(1.0 + rng.normal(0.001, 0.01, 500)),
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
                sharpe=0.5 + 0.2 * i, cagr=0.1 + 0.02 * i,
                max_drawdown=0.05, status="ok",
            )
        )

    grid = GridResult(trials=trials, run_id="test-report")
    pbo_result = PBOResult(
        pbo=0.3, logits=rng.normal(0, 1, 50),
        n_blocks=10, n_combinations=252,
    )
    dsr_results = {
        i: DSRResult(
            dsr=0.98, p_value=0.02,
            observed_sharpe=0.05, benchmark_sharpe=0.02,
            n_trials=n_configs,
        )
        for i in range(n_configs)
    }
    verdict = GateVerdict(
        pbo_result=pbo_result,
        pbo_pass=True,
        dsr_results=dsr_results,
        dsr_pass_ids=list(range(n_configs)),
        wf_verdicts={i: "pass" for i in range(n_configs)},
        wf_pass_ids=list(range(n_configs)),
        overall_pass=True,
        best_config_id=n_configs - 1,
    )
    wf_results = {
        i: WFResult(
            config_id=i, n_windows=8, n_profitable=7,
            max_drawdown=0.08, verdict="pass",
            oos_returns=[0.01] * 8,
            oos_drawdowns=[0.05] * 8,
        )
        for i in range(n_configs)
    }
    diagnostic = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=verdict, wf_results=wf_results,
    )
    return grid, verdict, wf_results, diagnostic


def test_write_pass_report_creates_summary_markdown(tmp_path: Path):
    from market_lab.backtest.grid.report import GridReportGenerator

    grid, verdict, wf_results, _diagnostic = _build_synthetic_world(n_configs=3)
    path = GridReportGenerator().write_pass_report(
        grid=grid, verdict=verdict, wf_results=wf_results,
        output_dir=tmp_path, data_source="yfinance",
    )
    assert path.exists()
    assert path.name == "summary.md"
    content = path.read_text()
    assert "PASS" in content or "pass" in content.lower()
    assert "best" in content.lower()
    # Survivorship disclaimer is mandatory for yfinance
    assert "survivorship" in content.lower()


def test_write_pass_report_references_best_config(tmp_path: Path):
    from market_lab.backtest.grid.report import GridReportGenerator

    grid, verdict, wf_results, _diagnostic = _build_synthetic_world(n_configs=3)
    path = GridReportGenerator().write_pass_report(
        grid=grid, verdict=verdict, wf_results=wf_results,
        output_dir=tmp_path, data_source="yfinance",
    )
    content = path.read_text()
    # best_config_id=2 (last in synthetic_world); its Sharpe ≈ 0.9
    assert "config_id" in content.lower() or "Config" in content
    # Report lists each trial — should include all 3 config_ids
    for i in range(3):
        assert str(i) in content


def test_write_pass_report_creates_assets_directory(tmp_path: Path):
    from market_lab.backtest.grid.report import GridReportGenerator

    grid, verdict, wf_results, _diagnostic = _build_synthetic_world(n_configs=3)
    GridReportGenerator().write_pass_report(
        grid=grid, verdict=verdict, wf_results=wf_results,
        output_dir=tmp_path, data_source="yfinance",
    )
    assets = tmp_path / "assets"
    assert assets.exists()
    assert any(assets.iterdir()), "assets/ must contain at least one PNG chart"


def test_write_fail_report_creates_diagnostic_markdown(tmp_path: Path):
    from market_lab.backtest.grid.diagnostic import DiagnosticAnalyzer
    from market_lab.backtest.grid.gates import GateVerdict
    from market_lab.backtest.grid.report import GridReportGenerator
    from market_lab.backtest.validation.pbo import PBOResult

    grid, _verdict_ok, wf_results, _diag_ok = _build_synthetic_world(n_configs=3)
    # Build a failing verdict
    pbo_result = PBOResult(
        pbo=0.72, logits=np.zeros(20), n_blocks=10, n_combinations=252,
    )
    fail_verdict = GateVerdict(
        pbo_result=pbo_result,
        pbo_pass=False,
        dsr_results={},
        dsr_pass_ids=[],
        wf_verdicts={i: "reject" for i in range(3)},
        wf_pass_ids=[],
        overall_pass=False,
        best_config_id=None,
    )
    diagnostic = DiagnosticAnalyzer().analyze(
        grid=grid, verdict=fail_verdict, wf_results=wf_results,
    )

    path = GridReportGenerator().write_fail_report(
        grid=grid, verdict=fail_verdict, wf_results=wf_results,
        diagnostic=diagnostic,
        output_dir=tmp_path, data_source="yfinance",
    )
    assert path.exists()
    assert path.name == "diagnostic.md"
    content = path.read_text()
    assert "fail" in content.lower() or "reject" in content.lower()
    assert "PBO_HIGH" in content or "COMBINED" in content
    # Recommendation narrative
    assert "paid-data" in content or "Next step" in content
    # Survivorship disclaimer
    assert "survivorship" in content.lower()


def test_report_omits_survivorship_disclaimer_for_unbiased_source(tmp_path: Path):
    """If data source is marked ``_sf`` (survivorship-free) no disclaimer."""
    from market_lab.backtest.grid.report import GridReportGenerator

    grid, verdict, wf_results, _diagnostic = _build_synthetic_world(n_configs=3)
    path = GridReportGenerator().write_pass_report(
        grid=grid, verdict=verdict, wf_results=wf_results,
        output_dir=tmp_path, data_source="tiingo_sf",
    )
    content = path.read_text()
    assert "survivorship bias warning" not in content.lower()


def test_write_pass_report_includes_gate_summary_table(tmp_path: Path):
    from market_lab.backtest.grid.report import GridReportGenerator

    grid, verdict, wf_results, _diagnostic = _build_synthetic_world(n_configs=3)
    path = GridReportGenerator().write_pass_report(
        grid=grid, verdict=verdict, wf_results=wf_results,
        output_dir=tmp_path, data_source="yfinance",
    )
    content = path.read_text()
    assert "PBO" in content
    assert "DSR" in content
    assert "walk" in content.lower()
