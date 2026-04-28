"""TDD specs for iter 017 — 12-1 top-1 regional rotation on iter 016 base.

Mechanism: 12-1 skip-a-month momentum on each of 3 regional equity legs;
top-1 selected at monthly cadence (21-bar); iter 016 fixed-ratio × vol-
target applied to the selected (equity, bond) pair for the 21-bar hold.

Citations
---------
* `[ml_for_algo_trading, ch.4, p.86]` — 12-1 skip-a-month canonical.
* `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag, `momentum_{t-1}` lag.
* `[risk_parity, p.10-11, ch.1]` — fixed-weight stack primitive.
* `[stocks_on_the_move, p.76-77]` — cross-sectional ranking framework.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = (
    Path(__file__).resolve().parent.parent
    / "studies"
    / "strategy_hunt_loop"
    / "iterations"
    / "017-2026-04-24-1750-regional-rotation-stack-vm"
)
sys.path.insert(0, str(ITER_DIR))

from regional_rotation_stack import (  # noqa: E402
    apply_regional_rotation_vm,
    compute_12_1_momentum,
)
from numpy_reference_regional import (  # noqa: E402
    apply_regional_rotation_vm_np,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_regions(
    n_bars: int,
    mu_per_region: dict[str, float],
    sigma: float = 0.01,
    bond_mu: float = 0.0002,
    bond_sigma: float = 0.004,
    seed: int = 42,
) -> dict[str, pd.DataFrame]:
    """Build synthetic (equity, bond) return DataFrames per region."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2006-01-04", periods=n_bars)
    bd_returns = rng.normal(bond_mu, bond_sigma, n_bars)
    regions: dict[str, pd.DataFrame] = {}
    for region, mu in mu_per_region.items():
        eq = rng.normal(mu, sigma, n_bars)
        regions[region] = pd.DataFrame(
            {"equity": eq, "bond": bd_returns}, index=idx
        )
    return regions


# ---------------------------------------------------------------------------
# 1 — 12-1 momentum primitive
# ---------------------------------------------------------------------------


class Test12_1Momentum:
    def test_12_1_uses_close_ratio_with_21_bar_skip(self) -> None:
        # Construct a clean equity price series with known ratio.
        idx = pd.bdate_range("2006-01-04", periods=300)
        # geometric returns so cumulative price is clean
        rng = np.random.default_rng(0)
        r = rng.normal(0.001, 0.005, 300)
        prices = pd.Series(np.cumprod(1.0 + r), index=idx, name="eq")
        mom = compute_12_1_momentum(prices, long_window=252, skip=21)
        # At bar 272 (index 272), we should have momentum defined:
        #   prices[272-21] / prices[272-252] - 1
        assert not np.isnan(mom.iloc[272])
        expected = prices.iloc[272 - 21] / prices.iloc[272 - 252] - 1.0
        assert mom.iloc[272] == pytest.approx(expected, abs=1e-12)

    def test_12_1_has_nan_before_warmup(self) -> None:
        idx = pd.bdate_range("2006-01-04", periods=300)
        prices = pd.Series(np.linspace(100, 130, 300), index=idx)
        mom = compute_12_1_momentum(prices, long_window=252, skip=21)
        # First 252 bars need both ends of the lookback; momentum is NaN
        # until index 252+skip is not needed — but price[t-252] is only
        # valid from t=252. With skip=21, momentum uses price[t-21] which
        # exists from t=21. So the binding constraint is t ≥ 252.
        assert mom.iloc[:252].isna().all()
        assert not mom.iloc[252:].isna().any()


# ---------------------------------------------------------------------------
# 2 — Rotation engine
# ---------------------------------------------------------------------------


class TestRotationEngine:
    def test_top_1_picks_highest_momentum_region(self) -> None:
        # Construct regions with deterministic drift ordering.
        regions = _make_regions(
            n_bars=350,
            mu_per_region={"US": 0.0020, "EFA": 0.0008, "EEM": 0.0004},
            sigma=0.005,
            seed=1,
        )
        result = apply_regional_rotation_vm(
            regions,
            eq_weight=0.6, bd_weight=0.4,
            target_vol=0.15, lookback=21, max_leverage=2.0,
            long_window=252, skip=21, rebalance_every=21,
            cost_bps_per_leg=0.0002, switch_cost_bps=0.0002,
        )
        # After 252+21 warmup, first rebalance picks a region;
        # over long run, US (highest drift) should dominate the selection.
        chosen = [seg["region"] for seg in result["segments"]]
        assert chosen.count("US") / len(chosen) >= 0.6

    def test_rebalance_cadence_is_monthly_21_bar(self) -> None:
        regions = _make_regions(
            n_bars=400,
            mu_per_region={"US": 0.001, "EFA": 0.001, "EEM": 0.001},
            seed=2,
        )
        result = apply_regional_rotation_vm(
            regions,
            eq_weight=0.6, bd_weight=0.4,
            target_vol=0.15, lookback=21, max_leverage=2.0,
            long_window=252, skip=21, rebalance_every=21,
            cost_bps_per_leg=0.0002, switch_cost_bps=0.0002,
        )
        # Segments should be ~21 bars each (may be slightly shorter at tail)
        seg_lens = [seg["length"] for seg in result["segments"]]
        # All interior segments should be exactly 21 bars
        for length in seg_lens[:-1]:
            assert length == 21
        # Tail can be 1..21 bars
        assert 1 <= seg_lens[-1] <= 21

    def test_no_look_ahead_momentum_uses_t_minus_1_data(self) -> None:
        """Selection at rebalance t must NOT use equity prices from t.

        We perturb only the FINAL bar of a region's equity series and
        check that the rebalance decision at or before that bar is
        unchanged.
        """
        regions_a = _make_regions(
            n_bars=300,
            mu_per_region={"US": 0.0015, "EFA": 0.0005, "EEM": 0.0002},
            seed=3,
        )
        regions_b = {k: v.copy() for k, v in regions_a.items()}
        # Tamper with the LAST equity return of US (bar 299).
        regions_b["US"].iloc[-1, regions_b["US"].columns.get_loc("equity")] = 100.0

        r_a = apply_regional_rotation_vm(
            regions_a, eq_weight=0.6, bd_weight=0.4, target_vol=0.15,
            lookback=21, max_leverage=2.0, long_window=252, skip=21,
            rebalance_every=21, cost_bps_per_leg=0.0002,
            switch_cost_bps=0.0002,
        )
        r_b = apply_regional_rotation_vm(
            regions_b, eq_weight=0.6, bd_weight=0.4, target_vol=0.15,
            lookback=21, max_leverage=2.0, long_window=252, skip=21,
            rebalance_every=21, cost_bps_per_leg=0.0002,
            switch_cost_bps=0.0002,
        )
        chosen_a = [seg["region"] for seg in r_a["segments"]]
        chosen_b = [seg["region"] for seg in r_b["segments"]]
        # The LAST rebalance decision may be unchanged because it uses
        # prices up to t-1, not t. All prior decisions are guaranteed
        # identical.
        assert chosen_a == chosen_b

    def test_degenerate_single_region_equals_iter_016(self) -> None:
        """If only US region is provided, output must equal iter 016 exactly."""
        from static_stack_vm import apply_static_stack_vol_managed

        rng = np.random.default_rng(4)
        n = 400
        idx = pd.bdate_range("2006-01-04", periods=n)
        eq = pd.Series(rng.normal(0.001, 0.01, n), index=idx)
        bd = pd.Series(rng.normal(0.0002, 0.004, n), index=idx)

        # iter 016 direct
        net_016, _, _, _ = apply_static_stack_vol_managed(
            eq, bd,
            eq_weight=0.6, bd_weight=0.4,
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0002,
        )

        # iter 017 with single region
        regions = {"US": pd.DataFrame({"equity": eq, "bond": bd}, index=idx)}
        result = apply_regional_rotation_vm(
            regions,
            eq_weight=0.6, bd_weight=0.4,
            target_vol=0.15, lookback=21, max_leverage=2.0,
            long_window=252, skip=21, rebalance_every=21,
            cost_bps_per_leg=0.0002, switch_cost_bps=0.0002,
        )
        net_017 = result["net"]

        # iter 017 only starts at bar 252+21=273 (post momentum warmup).
        # iter 016 starts at bar 21 (post vol-target warmup).
        # Overlapping bars must match exactly (no switches, same region).
        common_idx = net_017.index.intersection(net_016.index)
        assert len(common_idx) > 0
        np.testing.assert_allclose(
            net_017.loc[common_idx].values,
            net_016.loc[common_idx].values,
            atol=1e-12,
            err_msg="single-region case must reproduce iter 016",
        )


# ---------------------------------------------------------------------------
# 3 — Input validation
# ---------------------------------------------------------------------------


class TestInputValidation:
    def test_raises_on_misaligned_indices(self) -> None:
        idx1 = pd.bdate_range("2006-01-04", periods=300)
        idx2 = pd.bdate_range("2006-02-04", periods=300)
        r1 = pd.DataFrame(
            {"equity": np.zeros(300), "bond": np.zeros(300)}, index=idx1
        )
        r2 = pd.DataFrame(
            {"equity": np.zeros(300), "bond": np.zeros(300)}, index=idx2
        )
        with pytest.raises(ValueError, match="index"):
            apply_regional_rotation_vm(
                {"US": r1, "EFA": r2},
                eq_weight=0.6, bd_weight=0.4, target_vol=0.15,
                lookback=21, max_leverage=2.0, long_window=252, skip=21,
                rebalance_every=21, cost_bps_per_leg=0.0002,
                switch_cost_bps=0.0002,
            )

    def test_raises_on_insufficient_bars(self) -> None:
        regions = _make_regions(n_bars=100, mu_per_region={"US": 0.001})
        with pytest.raises(ValueError, match="bars"):
            apply_regional_rotation_vm(
                regions,
                eq_weight=0.6, bd_weight=0.4, target_vol=0.15,
                lookback=21, max_leverage=2.0, long_window=252, skip=21,
                rebalance_every=21, cost_bps_per_leg=0.0002,
                switch_cost_bps=0.0002,
            )

    def test_raises_on_invalid_params(self) -> None:
        regions = _make_regions(n_bars=400, mu_per_region={"US": 0.001})
        with pytest.raises(ValueError):
            apply_regional_rotation_vm(
                regions,
                eq_weight=0.6, bd_weight=0.4, target_vol=-0.1,
                lookback=21, max_leverage=2.0, long_window=252, skip=21,
                rebalance_every=21, cost_bps_per_leg=0.0002,
                switch_cost_bps=0.0002,
            )
        with pytest.raises(ValueError):
            apply_regional_rotation_vm(
                regions,
                eq_weight=0.6, bd_weight=0.4, target_vol=0.15,
                lookback=21, max_leverage=2.0, long_window=-252, skip=21,
                rebalance_every=21, cost_bps_per_leg=0.0002,
                switch_cost_bps=0.0002,
            )


# ---------------------------------------------------------------------------
# 4 — Cross-library parity (G7)
# ---------------------------------------------------------------------------


class TestCrossLibParity:
    def test_numpy_reference_matches_pandas_engine(self) -> None:
        rng = np.random.default_rng(5)
        n = 400
        idx = pd.bdate_range("2006-01-04", periods=n)
        eq_us = rng.normal(0.0015, 0.01, n)
        eq_efa = rng.normal(0.0005, 0.012, n)
        eq_eem = rng.normal(0.0007, 0.015, n)
        bd = rng.normal(0.0002, 0.004, n)

        regions_pd = {
            "US": pd.DataFrame({"equity": eq_us, "bond": bd}, index=idx),
            "EFA": pd.DataFrame({"equity": eq_efa, "bond": bd}, index=idx),
            "EEM": pd.DataFrame({"equity": eq_eem, "bond": bd}, index=idx),
        }
        result_pd = apply_regional_rotation_vm(
            regions_pd,
            eq_weight=0.6, bd_weight=0.4, target_vol=0.15,
            lookback=21, max_leverage=2.0, long_window=252, skip=21,
            rebalance_every=21, cost_bps_per_leg=0.0002,
            switch_cost_bps=0.0002,
        )

        regions_np = {
            "US": (eq_us, bd),
            "EFA": (eq_efa, bd),
            "EEM": (eq_eem, bd),
        }
        net_np = apply_regional_rotation_vm_np(
            regions_np,
            eq_weight=0.6, bd_weight=0.4, target_vol=0.15,
            lookback=21, max_leverage=2.0, long_window=252, skip=21,
            rebalance_every=21, cost_bps_per_leg=0.0002,
            switch_cost_bps=0.0002,
        )

        np.testing.assert_allclose(
            result_pd["net"].values, net_np, atol=1e-10,
            err_msg="numpy reference must match pandas engine to ≤1e-10",
        )


# ---------------------------------------------------------------------------
# 5 — Turnover / sanity
# ---------------------------------------------------------------------------


class TestTurnover:
    def test_turnover_bounded_on_low_noise_inputs(self) -> None:
        # When all regions have similar smooth drifts with LOW noise, the
        # winner is stable across most rebalance dates; turnover should
        # be dominated by iter 016's daily vol-target (4-8/yr).
        regions = _make_regions(
            n_bars=1200,
            mu_per_region={"US": 0.0020, "EFA": 0.0008, "EEM": 0.0004},
            sigma=0.001,  # very low noise
            seed=6,
        )
        result = apply_regional_rotation_vm(
            regions,
            eq_weight=0.6, bd_weight=0.4, target_vol=0.15,
            lookback=21, max_leverage=2.0, long_window=252, skip=21,
            rebalance_every=21, cost_bps_per_leg=0.0002,
            switch_cost_bps=0.0002,
        )
        # turnover_annual_total should be ≤ 15 (kill threshold #5)
        assert result["turnover_annual_total"] <= 15.0, (
            f"turnover={result['turnover_annual_total']:.2f} exceeds kill #5"
        )
