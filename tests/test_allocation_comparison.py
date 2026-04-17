"""Tests for :mod:`ai_trade.backtest.metrics.allocation_comparison` (Phase 3.5b Task 7d)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.metrics.allocation_comparison import (
    AllocationComparison,
    AllocationRow,
    blend_min_variance_3,
    blend_risk_parity_3,
    compare_allocations_3,
    erc_weights,
    min_variance_weights,
    render_allocation_comparison_markdown,
    select_default_allocation,
)


# ---------------------------------------------------------------------------
# erc_weights — fixed-point / mathematical properties
# ---------------------------------------------------------------------------


class TestErcWeights:
    def test_diagonal_cov_collapses_to_inverse_volatility(self) -> None:
        # ERC on a diagonal Σ degenerates to inverse-volatility weighting.
        cov = np.diag([0.04, 0.01, 0.0025])  # σ = {0.20, 0.10, 0.05}
        w = erc_weights(cov)
        inv_sigma = 1.0 / np.sqrt(np.diag(cov))
        expected = inv_sigma / inv_sigma.sum()
        np.testing.assert_allclose(w, expected, atol=1e-8)

    def test_equal_risk_contributions(self) -> None:
        rng = np.random.default_rng(0)
        x = rng.normal(size=(500, 4)) @ np.array(
            [
                [1.0, 0.3, 0.0, 0.1],
                [0.3, 1.5, 0.2, 0.0],
                [0.0, 0.2, 0.7, 0.4],
                [0.1, 0.0, 0.4, 1.2],
            ]
        )
        cov = np.cov(x, rowvar=False)
        w = erc_weights(cov)
        # ERC: w_i * (Σw)_i must be (almost) constant across i.
        contribs = w * (cov @ w)
        np.testing.assert_allclose(
            contribs, contribs.mean(), rtol=1e-4, atol=1e-8
        )
        np.testing.assert_allclose(w.sum(), 1.0, atol=1e-12)

    def test_rejects_non_psd(self) -> None:
        bad = np.array([[1.0, 0.0], [0.0, -0.5]])
        with pytest.raises(ValueError):
            erc_weights(bad)

    def test_rejects_non_square(self) -> None:
        with pytest.raises(ValueError, match="square"):
            erc_weights(np.zeros((2, 3)))


# ---------------------------------------------------------------------------
# min_variance_weights
# ---------------------------------------------------------------------------


class TestMinVarianceWeights:
    def test_diagonal_cov_collapses_to_inverse_variance(self) -> None:
        # For diagonal Σ, the unconstrained interior min-var solution is
        # the inverse-variance portfolio (sum-to-one), not a corner.
        cov = np.diag([0.04, 0.01, 0.09])
        w = min_variance_weights(cov)
        inv_var = 1.0 / np.diag(cov)
        expected = inv_var / inv_var.sum()
        np.testing.assert_allclose(w, expected, atol=1e-5)

    def test_equal_variance_collapses_to_equal_weight(self) -> None:
        # Equal σ², zero correlation → MV is the equal-weight point.
        cov = np.eye(3) * 0.02
        w = min_variance_weights(cov)
        np.testing.assert_allclose(w, [1 / 3] * 3, atol=1e-6)

    def test_long_only_constraint_respected(self) -> None:
        # An asset with negative correlation could pull weight negative
        # without bounds; the long-only constraint must hold.
        cov = np.array([
            [0.04, -0.02, 0.0],
            [-0.02, 0.04, 0.0],
            [0.0, 0.0, 0.10],
        ])
        w = min_variance_weights(cov)
        assert (w >= -1e-9).all()
        assert (w <= 1.0 + 1e-9).all()
        np.testing.assert_allclose(w.sum(), 1.0, atol=1e-9)


# ---------------------------------------------------------------------------
# Blenders
# ---------------------------------------------------------------------------


def _mk_returns(seed: int, n: int = 600, mu: float = 0.0005, sigma: float = 0.01):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    return pd.Series(rng.normal(mu, sigma, size=n), index=idx)


class TestBlenders:
    def test_risk_parity_blend_attrs_and_normalisation(self) -> None:
        a = _mk_returns(1, sigma=0.005)
        b = _mk_returns(2, sigma=0.020)
        c = _mk_returns(3, sigma=0.010)
        is_end = a.index[300]
        blended = blend_risk_parity_3(a, b, c, is_end)
        weights = blended.attrs["weights"]
        assert len(weights) == 3
        np.testing.assert_allclose(sum(weights), 1.0, atol=1e-9)
        # Lowest-vol asset should get the largest ERC weight in this
        # uncorrelated synthetic setup.
        assert weights[0] > weights[2] > weights[1]
        assert "risk_parity_3" in blended.name
        assert len(blended) == len(a)

    def test_min_variance_blend_attrs_and_lower_full_vol(self) -> None:
        a = _mk_returns(11, sigma=0.005)
        b = _mk_returns(12, sigma=0.020)
        c = _mk_returns(13, sigma=0.030)
        is_end = a.index[300]
        blended = blend_min_variance_3(a, b, c, is_end)
        weights = blended.attrs["weights"]
        np.testing.assert_allclose(sum(weights), 1.0, atol=1e-9)
        # Min-variance must produce a portfolio σ no larger than the lowest
        # individual σ across legs (within numerical tolerance).
        port_vol = float(blended.std(ddof=1))
        leg_vols = [float(s.std(ddof=1)) for s in (a, b, c)]
        assert port_vol <= min(leg_vols) + 1e-12
        assert "min_variance_3" in blended.name


# ---------------------------------------------------------------------------
# compare_allocations_3 + select_default_allocation
# ---------------------------------------------------------------------------


def _three_legs_for_compare():
    a = _mk_returns(101, mu=0.0006, sigma=0.008)
    b = _mk_returns(102, mu=0.0004, sigma=0.014)
    c = _mk_returns(103, mu=0.0003, sigma=0.020)
    is_end = a.index[400]
    return a, b, c, is_end


class TestCompareAllocations:
    def test_emits_five_methods_in_fixed_order(self) -> None:
        a, b, c, is_end = _three_legs_for_compare()
        verdict = compare_allocations_3(
            a, b, c, is_end=is_end, leg_names=("LETF", "QQQ", "GLD")
        )
        assert isinstance(verdict, AllocationComparison)
        assert tuple(r.method for r in verdict.rows) == (
            "equal_weight",
            "ivp_static",
            "hrp",
            "risk_parity",
            "min_variance",
        )

    def test_to_dict_round_trip_keys(self) -> None:
        a, b, c, is_end = _three_legs_for_compare()
        v = compare_allocations_3(a, b, c, is_end=is_end, leg_names=("L", "Q", "G"))
        d = v.to_dict()
        assert d["leg_names"] == ["L", "Q", "G"]
        assert d["default_method"] in {
            "equal_weight",
            "ivp_static",
            "hrp",
            "risk_parity",
            "min_variance",
        }
        assert len(d["rows"]) == 5
        for row in d["rows"]:
            for key in (
                "method",
                "weights",
                "full_sharpe",
                "is_sharpe",
                "oos_sharpe",
                "diversification_ratio",
                "final_equity",
            ):
                assert key in row

    def test_render_markdown_contains_decision_block(self) -> None:
        a, b, c, is_end = _three_legs_for_compare()
        v = compare_allocations_3(a, b, c, is_end=is_end, leg_names=("LETF", "QQQ", "GLD"))
        md = render_allocation_comparison_markdown(v)
        assert "## Decision" in md
        assert "Default allocation" in md
        assert "equal_weight" in md
        assert "min_variance" in md
        # All 3 leg names must be referenced in the weight strings.
        for name in ("LETF", "QQQ", "GLD"):
            assert name in md


class TestSelectDefaultAllocation:
    def _mk_row(self, method: str, oos: float, dr: float) -> AllocationRow:
        return AllocationRow(
            method=method,
            weights=(1 / 3, 1 / 3, 1 / 3),
            bars=100,
            full_sharpe=0.0,
            full_cagr_pct=0.0,
            full_volatility_ann_pct=0.0,
            full_max_drawdown_pct=0.0,
            is_sharpe=0.0,
            oos_sharpe=oos,
            diversification_ratio=dr,
            final_equity=1.0,
        )

    def test_keeps_ew_when_no_challenger_beats_both(self) -> None:
        rows = [
            self._mk_row("equal_weight", oos=1.50, dr=1.40),
            self._mk_row("hrp", oos=1.60, dr=1.41),  # only Sharpe better
            self._mk_row("min_variance", oos=1.51, dr=1.50),  # only DR better
        ]
        method, rationale = select_default_allocation(rows)
        assert method == "equal_weight"
        assert "kept" in rationale.lower()

    def test_promotes_challenger_when_both_margins_exceeded(self) -> None:
        rows = [
            self._mk_row("equal_weight", oos=1.50, dr=1.40),
            self._mk_row("hrp", oos=1.61, dr=1.46),  # +0.11 / +0.06 — passes
        ]
        method, rationale = select_default_allocation(rows)
        assert method == "hrp"
        assert "promoted" in rationale.lower()

    def test_raises_when_incumbent_missing(self) -> None:
        rows = [self._mk_row("hrp", 1.0, 1.0)]
        with pytest.raises(ValueError, match="incumbent"):
            select_default_allocation(rows)
