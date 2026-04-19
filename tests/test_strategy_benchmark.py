"""Tests for :mod:`ai_trade.backtest.grid.strategy_benchmark` (Phase 3 Lead B2)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.grid.strategy_benchmark import (
    TRADING_DAYS,
    align_returns,
    cagr_from_returns,
    compute_blend,
    decide_blend_vs_replace,
    diversification_ratio,
    inverse_vol_weights,
    mar_from_returns,
    max_drawdown_from_returns,
    rolling_correlation,
    run_benchmark,
    sharpe_from_returns,
)


def _mk_returns(n: int, mu: float, sigma: float, seed: int) -> pd.Series:
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    return pd.Series(rng.normal(mu, sigma, size=n), index=idx)


class TestSharpeAndCAGR:
    def test_positive_drift_positive_sharpe_and_cagr(self) -> None:
        r = _mk_returns(2_500, mu=0.0005, sigma=0.01, seed=1)
        assert sharpe_from_returns(r) > 0.5
        assert cagr_from_returns(r) > 0.0

    def test_zero_vol_zero_sharpe(self) -> None:
        r = pd.Series(np.zeros(500))
        assert sharpe_from_returns(r) == 0.0

    def test_short_series_returns_zero(self) -> None:
        assert sharpe_from_returns(pd.Series([0.01])) == 0.0
        assert cagr_from_returns(pd.Series([0.01])) == 0.0

    def test_negative_equity_returns_minus_one(self) -> None:
        r = pd.Series([-0.5, -0.6, -0.8, -0.95])
        assert cagr_from_returns(r) == -1.0


class TestMaxDDAndMAR:
    def test_drawdown_is_non_positive(self) -> None:
        r = _mk_returns(1_000, mu=0.0, sigma=0.01, seed=2)
        mdd = max_drawdown_from_returns(r)
        assert mdd <= 0.0

    def test_mar_zero_dd_positive_cagr_is_inf(self) -> None:
        r = pd.Series([0.001] * 300)
        assert mar_from_returns(r) == float("inf")

    def test_mar_matches_manual_cagr_over_absdd(self) -> None:
        r = _mk_returns(1_500, mu=0.0003, sigma=0.01, seed=3)
        cagr = cagr_from_returns(r)
        mdd = max_drawdown_from_returns(r)
        expected = cagr / abs(mdd)
        assert mar_from_returns(r) == pytest.approx(expected, rel=1e-9)


class TestAlignReturns:
    def test_inner_join_drops_non_overlapping(self) -> None:
        a = pd.Series([0.01] * 200, index=pd.date_range("2020-01-01", periods=200))
        b = pd.Series([0.02] * 200, index=pd.date_range("2020-02-01", periods=200))
        df = align_returns({"a": a, "b": b})
        assert set(df.columns) == {"a", "b"}
        assert df.index.min() >= a.index.min()
        assert df.index.min() >= b.index.min()
        assert not df.isna().any().any()

    def test_too_few_bars_raises(self) -> None:
        a = pd.Series([0.01] * 30, index=pd.date_range("2020-01-01", periods=30))
        b = pd.Series([0.02] * 30, index=pd.date_range("2020-01-01", periods=30))
        with pytest.raises(ValueError, match="too few overlapping"):
            align_returns({"a": a, "b": b})

    def test_empty_mapping_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            align_returns({})


class TestInverseVolWeights:
    def test_higher_vol_gets_lower_weight(self) -> None:
        idx = pd.date_range("2020-01-01", periods=300)
        low = pd.Series(np.random.default_rng(0).normal(0, 0.005, 300), index=idx)
        high = pd.Series(np.random.default_rng(1).normal(0, 0.02, 300), index=idx)
        df = pd.DataFrame({"low": low, "high": high})
        w = inverse_vol_weights(df)
        assert w["low"] > w["high"]
        assert w.sum() == pytest.approx(1.0, abs=1e-9)

    def test_all_zero_vol_raises(self) -> None:
        idx = pd.date_range("2020-01-01", periods=50)
        df = pd.DataFrame({"a": np.zeros(50), "b": np.zeros(50)}, index=idx)
        with pytest.raises(ValueError, match="zero volatility"):
            inverse_vol_weights(df)


class TestDiversificationRatio:
    def test_perfect_correlation_diversification_is_one(self) -> None:
        idx = pd.date_range("2020-01-01", periods=500)
        rng = np.random.default_rng(0)
        r = pd.Series(rng.normal(0, 0.01, 500), index=idx)
        df = pd.DataFrame({"a": r, "b": r})
        w = pd.Series({"a": 0.5, "b": 0.5})
        d = diversification_ratio(df, w)
        assert d == pytest.approx(1.0, rel=1e-6)

    def test_uncorrelated_diversification_above_one(self) -> None:
        idx = pd.date_range("2020-01-01", periods=500)
        rng = np.random.default_rng(0)
        a = pd.Series(rng.normal(0, 0.01, 500), index=idx)
        b = pd.Series(rng.normal(0, 0.01, 500), index=idx)
        df = pd.DataFrame({"a": a, "b": b})
        w = pd.Series({"a": 0.5, "b": 0.5})
        assert diversification_ratio(df, w) > 1.2


class TestComputeBlend:
    def test_blend_weights_sum_to_one(self) -> None:
        idx = pd.date_range("2020-01-01", periods=500)
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {"a": rng.normal(0.0005, 0.008, 500), "b": rng.normal(0.0003, 0.012, 500)},
            index=idx,
        )
        blend = compute_blend(df)
        assert sum(blend.weights.values()) == pytest.approx(1.0, abs=1e-9)
        assert len(blend.daily_returns) == 500

    def test_blend_reduces_max_dd_when_uncorrelated(self) -> None:
        idx = pd.date_range("2020-01-01", periods=1_200)
        rng = np.random.default_rng(7)
        a = pd.Series(rng.normal(0.0005, 0.01, 1200), index=idx)
        b = pd.Series(rng.normal(0.0005, 0.01, 1200), index=idx)
        df = pd.DataFrame({"a": a, "b": b})
        blend = compute_blend(df)
        dd_single_worst = min(
            max_drawdown_from_returns(df["a"]),
            max_drawdown_from_returns(df["b"]),
        )
        # Blend MaxDD should be shallower (closer to zero) than the worst leg.
        assert blend.max_drawdown > dd_single_worst


class TestRollingCorrelation:
    def test_constant_ratio_gives_perfect_rolling_corr(self) -> None:
        idx = pd.date_range("2020-01-01", periods=400)
        rng = np.random.default_rng(0)
        a = pd.Series(rng.normal(0, 0.01, 400), index=idx)
        b = a * 2.0  # perfectly correlated
        roll = rolling_correlation(a, b, window=60).dropna()
        assert (roll.round(6) == 1.0).all()


class TestDecideBlendVsReplace:
    def test_high_corr_dominant_b_returns_replace_a_with_b(self) -> None:
        decision, _ = decide_blend_vs_replace(
            pearson=0.85, sharpe_a=0.6, sharpe_b=1.2, blend_sharpe=0.9,
            diversification=1.02,
        )
        assert decision == "REPLACE_A_WITH_B"

    def test_high_corr_dominant_a_returns_replace_b_with_a(self) -> None:
        decision, _ = decide_blend_vs_replace(
            pearson=0.9, sharpe_a=1.5, sharpe_b=0.7, blend_sharpe=1.1,
            diversification=1.0,
        )
        assert decision == "REPLACE_B_WITH_A"

    def test_low_corr_and_blend_lift_returns_coexist(self) -> None:
        decision, reasons = decide_blend_vs_replace(
            pearson=0.1, sharpe_a=1.0, sharpe_b=1.1, blend_sharpe=1.3,
            diversification=1.25,
        )
        assert decision == "COEXIST"
        assert len(reasons) == 1

    def test_middling_corr_returns_independent_lanes(self) -> None:
        decision, reasons = decide_blend_vs_replace(
            pearson=0.5, sharpe_a=1.0, sharpe_b=1.05, blend_sharpe=1.1,
            diversification=1.15,
        )
        assert decision == "INDEPENDENT_LANES"
        assert reasons  # at least one failure reason

    def test_strict_dominance_replaces_regardless_of_corr(self) -> None:
        # A dominates on Sharpe + MAR + shallower MaxDD; blend hurts Sharpe.
        decision, reasons = decide_blend_vs_replace(
            pearson=0.44,  # below replace_corr=0.7 but dominance wins
            sharpe_a=1.90, sharpe_b=0.75,
            blend_sharpe=1.56,
            diversification=1.18,
            mar_a=2.72, mar_b=0.41,
            max_dd_a=-0.18, max_dd_b=-0.29,
        )
        assert decision == "REPLACE_B_WITH_A"
        assert any("strict dominance" in r for r in reasons)

    def test_strict_dominance_not_applied_when_blend_helps(self) -> None:
        # Even though A dominates, blend improves on max_single → keep coexist
        # path (strict-dominance rule must not fire).
        decision, _ = decide_blend_vs_replace(
            pearson=0.1,
            sharpe_a=1.20, sharpe_b=0.80,
            blend_sharpe=1.30,  # above max_single
            diversification=1.25,
            mar_a=1.5, mar_b=0.6,
            max_dd_a=-0.10, max_dd_b=-0.20,
        )
        assert decision == "COEXIST"

    def test_strict_dominance_skipped_when_mar_missing(self) -> None:
        # Without mar/max_dd, the rule must silently fall through to rules 2-4.
        decision, _ = decide_blend_vs_replace(
            pearson=0.44,
            sharpe_a=1.90, sharpe_b=0.75,
            blend_sharpe=1.56,
            diversification=1.18,
        )
        assert decision == "INDEPENDENT_LANES"


class TestRunBenchmark:
    def test_returns_full_verdict_with_decision(self) -> None:
        idx = pd.date_range("2015-01-02", periods=1_500, freq="B")
        rng = np.random.default_rng(0)
        a = pd.Series(rng.normal(0.0004, 0.010, 1500), index=idx)
        b = pd.Series(rng.normal(0.0003, 0.012, 1500), index=idx)
        verdict = run_benchmark("LETF", a, "ETFRot", b)
        assert verdict.strat_a == "LETF"
        assert verdict.strat_b == "ETFRot"
        assert verdict.n_bars == 1500
        assert -1.0 <= verdict.pearson <= 1.0
        assert verdict.decision in {
            "REPLACE_A_WITH_B", "REPLACE_B_WITH_A",
            "COEXIST", "INDEPENDENT_LANES",
        }
        d = verdict.to_dict()
        assert d["decision"] == verdict.decision
        assert "weights" in d["blend"]

    def test_same_name_raises(self) -> None:
        idx = pd.date_range("2020-01-01", periods=300)
        a = pd.Series([0.001] * 300, index=idx)
        with pytest.raises(ValueError, match="must differ"):
            run_benchmark("same", a, "same", a)


def test_trading_days_constant_matches_letf_module() -> None:
    # B2 and B1c must share the same annualization constant.
    from ai_trade.backtest.grid.letf_rotation_b1c import TRADING_DAYS as B1C_TD
    assert TRADING_DAYS == B1C_TD
