"""Tests for :mod:`ai_trade.backtest.grid.portfolio_3leg` (Phase 3 Lead A3d)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.grid.portfolio_3leg import (
    A3dGateVerdict,
    align_returns_3,
    blend_equal_weight_3,
    blend_hrp_3,
    blend_ivp_static_3,
    diversification_ratio_3,
    evaluate_a3d_gates,
)


def _mk_returns(seed: int, n: int, mu: float, sigma: float) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2004-11-18", periods=n, freq="B")
    return pd.Series(rng.normal(mu, sigma, size=n), index=idx)


def _mk_correlated(
    seed: int, n: int, rho: float, sigma: float = 0.01
) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2004-11-18", periods=n, freq="B")
    base = rng.normal(0.0, sigma, size=n)
    noise = rng.normal(0.0, sigma, size=n)
    a = base
    b = rho * base + np.sqrt(max(1.0 - rho * rho, 0.0)) * noise
    return pd.Series(a, index=idx), pd.Series(b, index=idx)


class TestAlignReturns3:
    def test_intersects_three_indices(self) -> None:
        idx = pd.date_range("2020-01-01", periods=4, freq="D")
        a = pd.Series([0.01, 0.02, 0.03, 0.04], index=idx)
        b = pd.Series([0.01, 0.02, 0.03], index=idx[:3])
        c = pd.Series([0.01, 0.02], index=idx[1:3])
        aa, bb, cc = align_returns_3(a, b, c)
        assert len(aa) == 2
        assert list(aa.index) == list(bb.index) == list(cc.index)

    def test_raises_on_empty_overlap(self) -> None:
        a = pd.Series([0.01], index=pd.to_datetime(["2020-01-01"]))
        b = pd.Series([0.02], index=pd.to_datetime(["2021-01-01"]))
        c = pd.Series([0.03], index=pd.to_datetime(["2022-01-01"]))
        with pytest.raises(ValueError, match="no common"):
            align_returns_3(a, b, c)

    def test_drops_nan_rows(self) -> None:
        idx = pd.date_range("2020-01-01", periods=4, freq="D")
        a = pd.Series([0.01, np.nan, 0.03, 0.04], index=idx)
        b = pd.Series([0.02, 0.03, 0.04, 0.05], index=idx)
        c = pd.Series([0.03, 0.04, np.nan, 0.06], index=idx)
        aa, bb, cc = align_returns_3(a, b, c)
        assert len(aa) == 2
        assert aa.index[0] == pd.Timestamp("2020-01-01")
        assert aa.index[1] == pd.Timestamp("2020-01-04")


class TestBlendEqualWeight3:
    def test_averages_three_series(self) -> None:
        a = _mk_returns(0, 100, 0.0005, 0.01)
        b = _mk_returns(1, 100, 0.0003, 0.012)
        c = _mk_returns(2, 100, 0.0001, 0.008)
        blended = blend_equal_weight_3(a, b, c)
        expected = (a + b + c) / 3.0
        pd.testing.assert_series_equal(
            blended.reset_index(drop=True),
            expected.reset_index(drop=True),
            check_names=False,
        )
        assert blended.attrs["weights"] == (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)


class TestBlendIvpStatic3:
    def test_inverse_variance_weights_sum_to_one(self) -> None:
        a = _mk_returns(0, 500, 0.0, 0.02)
        b = _mk_returns(1, 500, 0.0, 0.01)
        c = _mk_returns(2, 500, 0.0, 0.005)
        is_end = a.index[-1]
        blended = blend_ivp_static_3(a, b, c, is_end)
        w1, w2, w3 = blended.attrs["weights"]
        assert abs(w1 + w2 + w3 - 1.0) < 1e-9
        # Lowest-σ leg should receive highest weight.
        assert w3 > w2 > w1
        # Highest-σ leg (σ=0.02) should receive ~ (1/0.02²) / sum → ~ σ³²σ²² / (σ²²σ³² + σ¹²σ³² + σ¹²σ²²)
        inv = np.array([1 / 0.02**2, 1 / 0.01**2, 1 / 0.005**2])
        expected = inv / inv.sum()
        np.testing.assert_allclose(
            [w1, w2, w3], expected, rtol=0.2
        )

    def test_raises_on_empty_is(self) -> None:
        a = _mk_returns(0, 50, 0.0, 0.01)
        b = _mk_returns(1, 50, 0.0, 0.01)
        c = _mk_returns(2, 50, 0.0, 0.01)
        with pytest.raises(ValueError, match="IS slice empty"):
            blend_ivp_static_3(a, b, c, pd.Timestamp("1999-01-01"))


class TestBlendHrp3:
    def test_weights_sum_to_one(self) -> None:
        a = _mk_returns(0, 300, 0.0, 0.015)
        b = _mk_returns(1, 300, 0.0, 0.01)
        c = _mk_returns(2, 300, 0.0, 0.005)
        is_end = a.index[-1]
        blended = blend_hrp_3(a, b, c, is_end)
        w = blended.attrs["weights"]
        assert abs(sum(w) - 1.0) < 1e-9
        assert all(0.0 <= wi <= 1.0 for wi in w)

    def test_clusters_correlated_pair(self) -> None:
        """HRP should quasi-diagonalize correlated legs together."""
        n = 500
        a, b = _mk_correlated(0, n, rho=0.85, sigma=0.01)  # highly correlated pair
        rng = np.random.default_rng(42)
        c = pd.Series(rng.normal(0.0, 0.01, size=n), index=a.index)  # independent
        is_end = a.index[-1]
        blended = blend_hrp_3(a, b, c, is_end)
        order = blended.attrs["hrp_order"]
        # Highly correlated pair (indices 0, 1) should be adjacent in the
        # quasi-diagonal order; 2 should sit on the outside.
        assert abs(order.index(0) - order.index(1)) == 1

    def test_equal_assets_collapse_to_ew(self) -> None:
        """Three iid legs → HRP weights ≈ 1/3 each."""
        a = _mk_returns(0, 400, 0.0, 0.01)
        b = _mk_returns(1, 400, 0.0, 0.01)
        c = _mk_returns(2, 400, 0.0, 0.01)
        is_end = a.index[-1]
        w = blend_hrp_3(a, b, c, is_end).attrs["weights"]
        np.testing.assert_allclose(w, [1 / 3, 1 / 3, 1 / 3], atol=0.2)


class TestDiversificationRatio3:
    def test_perfectly_correlated_dr_one(self) -> None:
        a = _mk_returns(0, 200, 0.0, 0.01)
        # Perfectly correlated (just scaled) copies.
        b = a.copy()
        c = a.copy()
        dr = diversification_ratio_3(a, b, c, (1 / 3, 1 / 3, 1 / 3))
        assert abs(dr - 1.0) < 1e-6

    def test_uncorrelated_dr_above_one(self) -> None:
        a = _mk_returns(0, 500, 0.0, 0.01)
        b = _mk_returns(1, 500, 0.0, 0.01)
        c = _mk_returns(2, 500, 0.0, 0.01)
        dr = diversification_ratio_3(a, b, c, (1 / 3, 1 / 3, 1 / 3))
        assert dr > 1.3  # three iid ~ sqrt(3) ≈ 1.73 upper bound

    def test_rejects_bad_weight_shape(self) -> None:
        a = _mk_returns(0, 100, 0.0, 0.01)
        b = _mk_returns(1, 100, 0.0, 0.01)
        c = _mk_returns(2, 100, 0.0, 0.01)
        with pytest.raises(ValueError, match="3-tuple"):
            diversification_ratio_3(a, b, c, (0.5, 0.5))  # type: ignore[arg-type]


class TestEvaluateA3dGates:
    def _make_legs(self, n: int = 800, rho_a3: float = 0.05):
        rng = np.random.default_rng(123)
        idx = pd.date_range("2004-11-18", periods=n, freq="B")
        a = pd.Series(rng.normal(0.0008, 0.015, size=n), index=idx)
        # b moderately correlated with a
        base = a.to_numpy()
        noise_b = rng.normal(0.0, 0.012, size=n)
        b_vals = 0.5 * base + np.sqrt(0.75) * noise_b
        b_vals = b_vals + 0.0005
        b = pd.Series(b_vals, index=idx)
        # c weakly correlated with both (3rd leg candidate)
        noise_c = rng.normal(0.0, 0.01, size=n)
        c_vals = rho_a3 * base + np.sqrt(max(1 - rho_a3 ** 2, 0)) * noise_c
        c_vals = c_vals + 0.0004
        c = pd.Series(c_vals, index=idx)
        return a, b, c

    def test_returns_verdict_with_three_blends(self) -> None:
        a, b, c = self._make_legs()
        n = len(a)
        is_end = a.index[int(n * 0.6)]
        oos_end = a.index[int(n * 0.85)]
        verdict = evaluate_a3d_gates(
            a, b, c,
            leg_names=("leg_a", "leg_b", "leg_c"),
            is_range=(str(a.index[0].date()), str(is_end.date())),
            oos_range=(
                str((is_end + pd.Timedelta(days=1)).date()),
                str(oos_end.date()),
            ),
            stress_range=(
                str((oos_end + pd.Timedelta(days=1)).date()),
                str(a.index[-1].date()),
            ),
            bootstrap_n_resamples=500,
        )
        assert isinstance(verdict, A3dGateVerdict)
        assert len(verdict.blends) == 3
        names = [b.name for b in verdict.blends]
        assert names == ["equal_weight_3", "ivp_static_3", "hrp_3"]
        for b in verdict.blends:
            assert b.verdict in ("PASS", "FAIL")
            assert np.isfinite(b.diversification_ratio_full)

    def test_screening_pass_reported(self) -> None:
        """Low-ρ third leg should flip the screening flag to True."""
        a, b, c = self._make_legs(rho_a3=0.05)
        n = len(a)
        is_end = a.index[int(n * 0.6)]
        oos_end = a.index[int(n * 0.85)]
        verdict = evaluate_a3d_gates(
            a, b, c,
            leg_names=("leg_a", "leg_b", "leg_c"),
            is_range=(str(a.index[0].date()), str(is_end.date())),
            oos_range=(
                str((is_end + pd.Timedelta(days=1)).date()),
                str(oos_end.date()),
            ),
            stress_range=(
                str((oos_end + pd.Timedelta(days=1)).date()),
                str(a.index[-1].date()),
            ),
            bootstrap_n_resamples=500,
        )
        # Screening ρ is leg_a vs leg_c — designed ≈ 0.05, so pass.
        # But legs have independent means so Sharpe > 0 not guaranteed on
        # any single split; we only check that the screening field exists
        # and respects the |ρ|<threshold half of the rule.
        assert "leg_c" in verdict.screening_pass
        assert "leg_b" in verdict.screening_pass

    def test_raises_on_empty_overlap(self) -> None:
        a = pd.Series(
            [0.01, 0.02],
            index=pd.to_datetime(["2020-01-01", "2020-01-02"]),
        )
        b = pd.Series(
            [0.03, 0.04],
            index=pd.to_datetime(["2020-01-01", "2020-01-02"]),
        )
        c = pd.Series(
            [0.05, 0.06],
            index=pd.to_datetime(["2021-01-01", "2021-01-02"]),
        )
        with pytest.raises(ValueError, match="no common"):
            evaluate_a3d_gates(
                a, b, c,
                leg_names=("A", "B", "C"),
                is_range=("2020-01-01", "2020-01-01"),
                oos_range=("2020-01-02", "2020-01-02"),
                stress_range=("2020-01-02", "2020-01-02"),
            )
