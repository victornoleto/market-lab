"""Verdict engine tests — table-driven."""
from __future__ import annotations

import pandas as pd
import pytest

from reports.phase_3_5c.cross_lib.types import RunResult
from reports.phase_3_5c.cross_lib.verdict import (
    TOL_CONFIRM,
    TOL_STRONG,
    AggregateVerdict,
    Baseline,
    Tier,
    aggregate_verdict,
    classify_tier,
)


@pytest.fixture
def baseline_v4() -> Baseline:
    return Baseline(cagr=0.3919, sharpe=2.609, max_dd=-0.1222)


def _make_run(cagr: float, sharpe: float, max_dd: float, monthly_rho: float = 1.0) -> RunResult:
    idx = pd.date_range("2020-01-31", periods=12, freq="ME")
    monthly = pd.Series([0.01] * 12, index=idx)
    return RunResult(
        variant_id="plano_b_v4_threshold_10",
        lib="test",
        window=("2004-10-01", "2026-04-18"),
        stage=1,
        equity_curve=pd.Series([1.0]),
        monthly_returns=monthly,
        trade_dates=[],
        cagr=cagr,
        sharpe=sharpe,
        max_dd=max_dd,
        wf_splits_8=[sharpe] * 8,
        dsr_pval=0.01,
        outcome="OK",
        error_detail=None,
    )


def test_identity_near_match_is_confirms_strong(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.3920, sharpe=2.608, max_dd=-0.1221)
    tier = classify_tier(run, baseline_v4, monthly_rho_override=1.0)
    assert tier == Tier.CONFIRMS_STRONG


def test_small_diff_is_confirms(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.38, sharpe=2.55, max_dd=-0.13)
    tier = classify_tier(run, baseline_v4, monthly_rho_override=0.97)
    assert tier == Tier.CONFIRMS


def test_larger_diff_is_warning(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.30, sharpe=2.30, max_dd=-0.20)
    tier = classify_tier(run, baseline_v4, monthly_rho_override=0.80)
    assert tier == Tier.WARNING


def test_gate_flip_is_refutes(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.05, sharpe=-0.2, max_dd=-0.40)
    tier = classify_tier(run, baseline_v4, monthly_rho_override=0.1)
    assert tier == Tier.REFUTES


def test_maxdd_gate_flip_is_refutes(baseline_v4: Baseline) -> None:
    run = _make_run(cagr=0.20, sharpe=1.0, max_dd=-0.30)  # MaxDD > 25% gate
    tier = classify_tier(run, baseline_v4, monthly_rho_override=0.9)
    assert tier == Tier.REFUTES


def test_tol_strong_bands() -> None:
    assert TOL_STRONG.cagr_pp == 0.5
    assert TOL_STRONG.sharpe == 0.05
    assert TOL_STRONG.max_dd_pp == 1.0
    assert TOL_STRONG.monthly_rho == 0.99


def test_tol_confirm_bands() -> None:
    assert TOL_CONFIRM.cagr_pp == 2.0
    assert TOL_CONFIRM.sharpe == 0.15
    assert TOL_CONFIRM.max_dd_pp == 3.0
    assert TOL_CONFIRM.monthly_rho == 0.95


def test_aggregate_all_strong_is_validated() -> None:
    stage1 = {
        "bt": Tier.CONFIRMS_STRONG,
        "vectorbt": Tier.CONFIRMS_STRONG,
        "backtrader": Tier.CONFIRMS,
    }
    stage2 = {
        "bt": Tier.CONFIRMS,
        "vectorbt": Tier.CONFIRMS,
        "backtrader": Tier.CONFIRMS,
    }
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.VALIDATED


def test_aggregate_stage2_warning_is_caveats() -> None:
    stage1 = {
        "bt": Tier.CONFIRMS_STRONG,
        "vectorbt": Tier.CONFIRMS_STRONG,
        "backtrader": Tier.CONFIRMS,
    }
    stage2 = {
        "bt": Tier.CONFIRMS,
        "vectorbt": Tier.WARNING,
        "backtrader": Tier.WARNING,
    }
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.VALIDATED_WITH_CAVEATS


def test_aggregate_any_refutes_is_blocked() -> None:
    stage1 = {
        "bt": Tier.CONFIRMS_STRONG,
        "vectorbt": Tier.CONFIRMS_STRONG,
        "backtrader": Tier.REFUTES,
    }
    stage2 = {"bt": Tier.CONFIRMS}
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.BLOCKED_INVESTIGATE


def test_aggregate_insufficient_libs_is_inconclusive() -> None:
    stage1 = {"bt": Tier.CONFIRMS_STRONG}
    stage2: dict[str, Tier] = {}
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.INCONCLUSIVE


def test_aggregate_stage1_weak_is_blocked() -> None:
    stage1 = {"bt": Tier.CONFIRMS, "vectorbt": Tier.CONFIRMS}  # 0 STRONG
    stage2 = {
        "bt": Tier.CONFIRMS,
        "vectorbt": Tier.CONFIRMS,
        "backtrader": Tier.CONFIRMS,
    }
    assert aggregate_verdict(stage1, stage2) == AggregateVerdict.BLOCKED_INVESTIGATE
