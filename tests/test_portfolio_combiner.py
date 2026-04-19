"""Tests for :mod:`ai_trade.backtest.grid.portfolio_combiner` (Phase 3 Lead A3c)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.grid.portfolio_combiner import (
    A3cGateVerdict,
    BlendEvaluation,
    align_returns,
    blend_equal_weight,
    blend_ivp_rolling,
    blend_ivp_static,
    blend_mvp_static,
    diversification_ratio,
    evaluate_a3c_gates,
)


def _mk_returns(seed: int, n: int, mu: float, sigma: float) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2001-05-14", periods=n, freq="B")
    return pd.Series(rng.normal(mu, sigma, size=n), index=idx)


class TestAlignReturns:
    def test_intersects_indices(self) -> None:
        a = pd.Series(
            [0.01, 0.02, 0.03],
            index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
        )
        b = pd.Series(
            [0.04, 0.05],
            index=pd.to_datetime(["2020-01-02", "2020-01-03"]),
        )
        aa, bb = align_returns(a, b)
        assert len(aa) == 2
        assert list(aa.index) == list(bb.index)

    def test_raises_on_empty_overlap(self) -> None:
        a = pd.Series([0.01], index=pd.to_datetime(["2020-01-01"]))
        b = pd.Series([0.02], index=pd.to_datetime(["2021-01-01"]))
        with pytest.raises(ValueError, match="no common"):
            align_returns(a, b)

    def test_drops_nan_rows(self) -> None:
        idx = pd.date_range("2020-01-01", periods=4, freq="D")
        a = pd.Series([0.01, np.nan, 0.03, 0.04], index=idx)
        b = pd.Series([0.02, 0.03, np.nan, 0.05], index=idx)
        aa, bb = align_returns(a, b)
        assert len(aa) == 2
        assert aa.index[0] == pd.Timestamp("2020-01-01")
        assert aa.index[1] == pd.Timestamp("2020-01-04")


class TestBlendEqualWeight:
    def test_averages_returns(self) -> None:
        a = _mk_returns(0, 200, 0.0005, 0.01)
        b = _mk_returns(1, 200, 0.0003, 0.015)
        blended = blend_equal_weight(a, b)
        assert len(blended) == 200
        # Each value should be exactly the average.
        expected = 0.5 * a + 0.5 * b
        pd.testing.assert_series_equal(
            blended.reset_index(drop=True),
            expected.reset_index(drop=True),
            check_names=False,
        )


class TestBlendIvpStatic:
    def test_inverse_variance_weights(self) -> None:
        # Leg A has higher variance → should receive lower weight.
        a = _mk_returns(0, 500, 0.0, 0.02)
        b = _mk_returns(1, 500, 0.0, 0.005)
        is_end = a.index[-1]
        blended = blend_ivp_static(a, b, is_end)
        w1, w2 = blended.attrs["weights"]
        assert w1 < w2
        assert pytest.approx(w1 + w2, rel=1e-9) == 1.0
        # Analytic check: w1 = σ²₂ / (σ²₁ + σ²₂)
        v1 = float(a.std(ddof=1) ** 2)
        v2 = float(b.std(ddof=1) ** 2)
        assert w1 == pytest.approx(v2 / (v1 + v2), rel=1e-12)

    def test_uses_only_is_window(self) -> None:
        # Build series where IS σ differs sharply from post-IS σ.
        idx = pd.date_range("2020-01-01", periods=400, freq="B")
        is_cut = idx[199]
        a = pd.Series(
            np.concatenate([
                np.random.default_rng(0).normal(0.0, 0.005, 200),
                np.random.default_rng(1).normal(0.0, 0.05, 200),
            ]),
            index=idx,
        )
        b = pd.Series(
            np.random.default_rng(2).normal(0.0, 0.01, 400),
            index=idx,
        )
        blended = blend_ivp_static(a, b, is_cut)
        w1_is, _ = blended.attrs["weights"]
        # IS σ_a (~0.005) << σ_b (~0.01) → w_a > w_b.
        assert w1_is > 0.5


class TestBlendIvpRolling:
    def test_returns_same_index(self) -> None:
        a = _mk_returns(0, 300, 0.0, 0.01)
        b = _mk_returns(1, 300, 0.0, 0.02)
        blended = blend_ivp_rolling(a, b, lookback=63)
        assert list(blended.index) == list(a.index)
        assert not blended.isna().any()

    def test_no_look_ahead_warmup_is_equal_weight(self) -> None:
        a = _mk_returns(0, 100, 0.0, 0.01)
        b = _mk_returns(1, 100, 0.0, 0.02)
        blended = blend_ivp_rolling(a, b, lookback=63)
        # First ~63 bars should use 50/50 fallback (no rolling σ yet).
        early = blended.iloc[:50]
        expected_early = 0.5 * a.iloc[:50] + 0.5 * b.iloc[:50]
        assert np.allclose(early.values, expected_early.values)

    def test_requires_lookback_ge_2(self) -> None:
        a = _mk_returns(0, 50, 0.0, 0.01)
        b = _mk_returns(1, 50, 0.0, 0.01)
        with pytest.raises(ValueError, match="lookback"):
            blend_ivp_rolling(a, b, lookback=1)


class TestBlendMvpStatic:
    def test_weights_sum_to_one(self) -> None:
        a = _mk_returns(0, 500, 0.0, 0.01)
        b = _mk_returns(1, 500, 0.0, 0.02)
        blended = blend_mvp_static(a, b, a.index[-1])
        w1, w2 = blended.attrs["weights"]
        assert w1 + w2 == pytest.approx(1.0, rel=1e-12)
        assert 0.0 <= w1 <= 1.0

    def test_long_only_clip(self) -> None:
        # Highly-correlated legs where unconstrained MVP would short one.
        idx = pd.date_range("2020-01-01", periods=500, freq="B")
        rng = np.random.default_rng(0)
        base = rng.normal(0.0, 0.01, 500)
        a = pd.Series(base + rng.normal(0.0, 0.0005, 500), index=idx)
        b = pd.Series(2.0 * base + rng.normal(0.0, 0.0005, 500), index=idx)
        blended = blend_mvp_static(a, b, idx[-1], long_only=True)
        w1, w2 = blended.attrs["weights"]
        assert 0.0 <= w1 <= 1.0
        assert 0.0 <= w2 <= 1.0


class TestDiversificationRatio:
    def test_perfect_positive_corr_is_one(self) -> None:
        base = pd.Series(
            np.random.default_rng(0).normal(0.0, 0.01, 500),
            index=pd.date_range("2020-01-01", periods=500, freq="B"),
        )
        a = base.copy()
        b = base.copy()
        dr = diversification_ratio(a, b, 0.5, 0.5)
        assert dr == pytest.approx(1.0, abs=1e-10)

    def test_zero_corr_is_greater_than_one(self) -> None:
        idx = pd.date_range("2020-01-01", periods=2000, freq="B")
        a = pd.Series(
            np.random.default_rng(0).normal(0.0, 0.01, 2000), index=idx
        )
        b = pd.Series(
            np.random.default_rng(1).normal(0.0, 0.01, 2000), index=idx
        )
        dr = diversification_ratio(a, b, 0.5, 0.5)
        # Uncorrelated equal-sigma equal-weight DR → sqrt(2) ≈ 1.414.
        assert dr > 1.2
        assert dr == pytest.approx(np.sqrt(2), rel=0.1)

    def test_negative_corr_increases_dr(self) -> None:
        idx = pd.date_range("2020-01-01", periods=2000, freq="B")
        rng = np.random.default_rng(0)
        base = rng.normal(0.0, 0.01, 2000)
        a = pd.Series(base, index=idx)
        b = pd.Series(-base + rng.normal(0.0, 0.001, 2000), index=idx)
        dr = diversification_ratio(a, b, 0.5, 0.5)
        # Near-perfect negative corr → huge DR.
        assert dr > 3.0


class TestEvaluateA3cGates:
    def _make_pair(self, n: int = 2000) -> tuple[pd.Series, pd.Series]:
        idx = pd.date_range("2005-01-03", periods=n, freq="B")
        rng = np.random.default_rng(0)
        # Two uncorrelated streams with positive drift (gate should be
        # computable even if not all blends pass).
        a = pd.Series(rng.normal(0.0006, 0.01, n), index=idx)
        b = pd.Series(
            np.random.default_rng(42).normal(0.0004, 0.015, n),
            index=idx,
        )
        return a, b

    def _ranges(
        self, idx: pd.DatetimeIndex
    ) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
        start = idx.min()
        end = idx.max()
        total = (end - start).days
        is_end = start + pd.Timedelta(days=int(total * 0.60))
        oos_end = start + pd.Timedelta(days=int(total * 0.85))
        to_iso = lambda t: t.strftime("%Y-%m-%d")  # noqa: E731
        return (
            (to_iso(start), to_iso(is_end)),
            (to_iso(is_end + pd.Timedelta(days=1)), to_iso(oos_end)),
            (to_iso(oos_end + pd.Timedelta(days=1)), to_iso(end)),
        )

    def test_all_blends_evaluated(self) -> None:
        a, b = self._make_pair()
        is_r, oos_r, st_r = self._ranges(a.index)
        verdict = evaluate_a3c_gates(
            a, b, leg_names=("A", "B"),
            is_range=is_r, oos_range=oos_r, stress_range=st_r,
            bootstrap_n_resamples=200,
        )
        assert isinstance(verdict, A3cGateVerdict)
        names = [e.name for e in verdict.blends]
        assert names == ["equal_weight", "ivp_static", "ivp_rolling", "mvp_static"]
        # Each blend has OOS metrics and attempts all gates.
        for e in verdict.blends:
            assert e.verdict in {"PASS", "FAIL"}
            assert e.diversification_ratio_full > 0

    def test_baseline_is_max_of_legs(self) -> None:
        a, b = self._make_pair()
        is_r, oos_r, st_r = self._ranges(a.index)
        verdict = evaluate_a3c_gates(
            a, b, leg_names=("A", "B"),
            is_range=is_r, oos_range=oos_r, stress_range=st_r,
            bootstrap_n_resamples=200,
        )
        leg_a_oos = verdict.leg_metrics["A"]["oos"]["sharpe"]
        leg_b_oos = verdict.leg_metrics["B"]["oos"]["sharpe"]
        assert verdict.baseline_sharpe_oos == max(leg_a_oos, leg_b_oos)
        assert verdict.baseline_leg_name in ("A", "B")

    def test_fails_primary_gate_when_blend_sharpe_below_baseline(self) -> None:
        # Strong leg A, weak leg B → blends likely dilute Sharpe of A.
        idx = pd.date_range("2005-01-03", periods=2000, freq="B")
        rng = np.random.default_rng(0)
        a = pd.Series(rng.normal(0.002, 0.01, 2000), index=idx)
        b = pd.Series(
            np.random.default_rng(1).normal(0.0001, 0.02, 2000),
            index=idx,
        )
        is_r, oos_r, st_r = self._ranges(idx)
        verdict = evaluate_a3c_gates(
            a, b, leg_names=("A", "B"),
            is_range=is_r, oos_range=oos_r, stress_range=st_r,
            bootstrap_n_resamples=200,
        )
        # At least the equal-weight blend should fail the Sharpe-vs-baseline
        # gate in this setup.
        ew = next(e for e in verdict.blends if e.name == "equal_weight")
        assert any("SHARPE_LE_BASELINE" in g for g in ew.failed_gates)

    def test_verdict_serializes_to_dict(self) -> None:
        a, b = self._make_pair(n=800)
        is_r, oos_r, st_r = self._ranges(a.index)
        verdict = evaluate_a3c_gates(
            a, b, leg_names=("A", "B"),
            is_range=is_r, oos_range=oos_r, stress_range=st_r,
            bootstrap_n_resamples=200,
        )
        d = verdict.to_dict()
        assert "blends" in d
        assert "baseline_sharpe_oos" in d
        assert "leg_metrics" in d
        assert len(d["blends"]) == 4
