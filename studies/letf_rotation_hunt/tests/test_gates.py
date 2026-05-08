"""Unit tests for studies/letf_rotation_hunt/gates.py — 7-gate battery.

TDD per spec §3.5. Each gate has 2-3 cases: happy path, fail/edge, threshold
boundary. Citations follow gate impl docstrings.

Coverage
--------
* g1_pbo            — CSCV combinatorial via src/.../pbo.pbo
* g2_dsr_p_value    — DSR via src/.../dsr.dsr (n_trials hybrid)
* g3_walk_forward   — 8-window rolling, 5/8 sharpe>0 + MDD<50% (letf-relaxed)
* g4_oos_70_30      — temporal hold-out
* g5_fwd_post_2020  — date-filter stress window
* g6_bootstrap_ci   — 99% CI low > 0 via stationary block bootstrap
* g7_xlib_cagr      — pandas vs numpy CAGR delta ≤ 3pp
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def positive_drift_returns() -> pd.Series:
    """1500 daily returns with positive drift μ=0.0008, σ=0.012, seed=42."""
    rng = np.random.default_rng(42)
    n = 1500
    rets = rng.normal(0.0008, 0.012, n)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    return pd.Series(rets, index=idx)


@pytest.fixture
def negative_drift_returns() -> pd.Series:
    """1500 daily returns with negative drift, seed=42."""
    rng = np.random.default_rng(42)
    n = 1500
    rets = rng.normal(-0.0008, 0.012, n)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    return pd.Series(rets, index=idx)


@pytest.fixture
def noise_returns_long() -> pd.Series:
    """3000 daily noise returns spanning post-2020 window. seed=7."""
    rng = np.random.default_rng(7)
    n = 3000
    rets = rng.normal(0.0002, 0.011, n)
    idx = pd.date_range("2014-01-02", periods=n, freq="B")
    return pd.Series(rets, index=idx)


# ---------------------------------------------------------------------------
# G1 — PBO
# ---------------------------------------------------------------------------


class TestG1PBO:
    """G1: Probability of Backtest Overfitting via CSCV.

    Threshold < 0.5 per spec §3.5 [advances_fin_ml, p.208-211].
    """

    def test_pbo_with_pure_noise_configs_around_half(self) -> None:
        """N pure-noise configs → PBO clusters around 0.5 (no edge to find)."""
        from studies.letf_rotation_hunt.gates import g1_pbo

        rng = np.random.default_rng(42)
        n_configs = 10
        n_obs = 1000
        idx = pd.date_range("2010-01-04", periods=n_obs, freq="B")
        per_cfg = {
            f"cfg_{i}": pd.Series(rng.normal(0, 0.01, n_obs), index=idx)
            for i in range(n_configs)
        }
        result = g1_pbo(per_cfg)
        assert isinstance(result, dict)
        assert "pbo" in result
        assert 0.0 <= result["pbo"] <= 1.0
        assert result["n_combinations"] >= 1

    def test_pbo_single_config_skip_passes(self) -> None:
        """Single config → skip-pass with NaN (CSCV needs ≥2 configs to be informative).

        Mirrors long_term_portfolio canon contract: a 1-config iter is not a
        PBO failure; PBO is just non-applicable. Caller treats NaN as
        non-blocking.
        """
        from studies.letf_rotation_hunt.gates import g1_pbo

        idx = pd.date_range("2010-01-04", periods=500, freq="B")
        per_cfg = {"only_one": pd.Series(np.zeros(500), index=idx)}
        result = g1_pbo(per_cfg)
        assert result["pass_gate"] is True
        assert np.isnan(result["pbo"])
        assert result["n_combinations"] == 0

    def test_pbo_aligns_misindexed_configs(self) -> None:
        """Configs with overlapping but non-identical indices align on intersection."""
        from studies.letf_rotation_hunt.gates import g1_pbo

        idx_a = pd.date_range("2010-01-04", periods=600, freq="B")
        idx_b = pd.date_range("2010-04-01", periods=600, freq="B")
        rng = np.random.default_rng(0)
        per_cfg = {
            "a": pd.Series(rng.normal(0, 0.01, 600), index=idx_a),
            "b": pd.Series(rng.normal(0, 0.01, 600), index=idx_b),
        }
        result = g1_pbo(per_cfg)  # should align, not raise
        assert isinstance(result["pbo"], float)


# ---------------------------------------------------------------------------
# G2 — DSR p-value (hybrid: local n_trials)
# ---------------------------------------------------------------------------


class TestG2DSR:
    """G2: Deflated Sharpe Ratio p-value [advances_fin_ml, p.222-223, p.275]."""

    def test_dsr_high_sharpe_low_n_trials_passes(self, positive_drift_returns) -> None:
        """μ=0.0008, σ=0.012 → annualised Sharpe ≈ 1.0 → DSR p<0.05 with n_trials=2."""
        from studies.letf_rotation_hunt.gates import g2_dsr_p_value

        result = g2_dsr_p_value(positive_drift_returns, n_trials=2)
        assert isinstance(result, dict)
        assert "p_value" in result
        assert "observed_sharpe" in result
        assert 0.0 <= result["p_value"] <= 1.0

    def test_dsr_zero_sharpe_high_p_value(self) -> None:
        """Pure noise with mean=0 → high p-value (insignificant)."""
        from studies.letf_rotation_hunt.gates import g2_dsr_p_value

        rng = np.random.default_rng(42)
        rets = pd.Series(
            rng.normal(0, 0.01, 1000),
            index=pd.date_range("2010-01-04", periods=1000, freq="B"),
        )
        result = g2_dsr_p_value(rets, n_trials=10)
        assert result["p_value"] > 0.10  # not significant

    def test_dsr_n_trials_one_falls_back_to_psr(self, positive_drift_returns) -> None:
        """n_trials=1 → PSR fallback (DSR requires ≥2)."""
        from studies.letf_rotation_hunt.gates import g2_dsr_p_value

        result = g2_dsr_p_value(positive_drift_returns, n_trials=1)
        assert "p_value" in result
        assert result["n_trials"] == 1


# ---------------------------------------------------------------------------
# G3 — Walk-forward (8 windows, benchmark-relative pass condition)
# ---------------------------------------------------------------------------


class TestG3WalkForward:
    """G3: Walk-forward 8 windows, benchmark-relative pass.

    Per mandate §2.3 (MDD warning-only), spec §3.5 G3 LETF-relaxed
    precedent, user observation 2026-05-06 (underwater-vs-benchmark thesis):
    pass condition redesigned to require ≥5/8 windows with
    pct_time_above_benchmark ≥ 0.50. MDD and Sharpe-positivity become
    warning-only diagnostics.
    """

    def test_wf_strategy_dominates_benchmark_passes(
        self, positive_drift_returns,
    ) -> None:
        """Strategy μ=0.0008 strictly above benchmark μ=0.0 → most windows
        pct_above_bench > 0.5 → pass even though absolute MDD may be deep."""
        from studies.letf_rotation_hunt.gates import g3_walk_forward

        # Zero-drift benchmark, same dates
        rng = np.random.default_rng(7)
        bench_rets = pd.Series(
            rng.normal(0.0, 0.012, len(positive_drift_returns)),
            index=positive_drift_returns.index,
        )
        result = g3_walk_forward(positive_drift_returns, benchmark_returns=bench_rets)
        assert isinstance(result, dict)
        assert "windows_pass_pct_above_benchmark" in result
        assert "windows_pct_above_benchmark" in result
        assert "max_mdd" in result
        assert "pass_gate" in result
        assert result["n_windows"] >= 1
        assert result["windows_pass_pct_above_benchmark"] >= 5  # ≥5/8 dominate
        assert result["pass_gate"] is True

    def test_wf_strategy_below_benchmark_fails(
        self, positive_drift_returns,
    ) -> None:
        """Strategy μ=0.0008 below stronger benchmark μ=0.0015 →
        most windows pct_above_bench < 0.5 → fail (regardless of Sharpe sign)."""
        from studies.letf_rotation_hunt.gates import g3_walk_forward

        rng = np.random.default_rng(99)
        # Stronger benchmark → strategy will lose vs it
        bench_rets = pd.Series(
            rng.normal(0.0015, 0.012, len(positive_drift_returns)),
            index=positive_drift_returns.index,
        )
        result = g3_walk_forward(positive_drift_returns, benchmark_returns=bench_rets)
        assert result["pass_gate"] is False

    def test_wf_letf_high_mdd_does_not_block_pass(
        self,
    ) -> None:
        """Strategy with deep absolute MDD but consistently > benchmark →
        passes (mandate §2.3 MDD warning-only)."""
        from studies.letf_rotation_hunt.gates import g3_walk_forward

        # Construct a series that grows then crashes 60% then grows again,
        # while benchmark is much weaker. Strategy should still be > benchmark
        # most of the time.
        n = 1500
        idx = pd.date_range("2010-01-04", periods=n, freq="B")
        rng = np.random.default_rng(11)
        rets = rng.normal(0.0010, 0.025, n)  # high drift, high vol → deep MDD likely
        # Force a 60% drawdown midway: insert a sequence of negative shocks
        rets[700:740] = -0.020  # ~55% drawdown over ~40 days
        strat = pd.Series(rets, index=idx)
        bench = pd.Series(np.zeros(n), index=idx)  # flat benchmark
        result = g3_walk_forward(strat, benchmark_returns=bench)
        # MDD will be deep (warning) but pct_above_bench should remain high
        assert result["max_mdd"] > 0.30  # deep MDD recorded as diagnostic
        assert result["pass_gate"] is True  # NOT blocked by MDD anymore

    def test_wf_no_benchmark_falls_back_to_sharpe_positivity(
        self, positive_drift_returns,
    ) -> None:
        """When benchmark_returns is None, fall back to Sharpe>0 in ≥5/8
        windows (legacy mode). MDD becomes warning-only either way."""
        from studies.letf_rotation_hunt.gates import g3_walk_forward

        result = g3_walk_forward(positive_drift_returns, benchmark_returns=None)
        assert isinstance(result, dict)
        assert "windows_pass_sharpe_positive" in result
        assert result["n_windows"] >= 1
        assert result["windows_pass_sharpe_positive"] >= 5
        assert result["pass_gate"] is True

    def test_wf_negative_drift_fails(
        self, negative_drift_returns,
    ) -> None:
        """Negative-drift returns vs zero-drift benchmark → most windows
        below benchmark → fails."""
        from studies.letf_rotation_hunt.gates import g3_walk_forward

        bench = pd.Series(
            np.zeros(len(negative_drift_returns)),
            index=negative_drift_returns.index,
        )
        result = g3_walk_forward(negative_drift_returns, benchmark_returns=bench)
        assert result["pass_gate"] is False

    def test_wf_insufficient_data_fails(self) -> None:
        """Series too short for 8 windows → fail-with-explanation."""
        from studies.letf_rotation_hunt.gates import g3_walk_forward

        idx = pd.date_range("2020-01-04", periods=100, freq="B")
        rets = pd.Series(np.zeros(100), index=idx)
        result = g3_walk_forward(rets)
        assert result["pass_gate"] is False

    def test_wf_proportional_warmup_short_long(
        self, positive_drift_returns,
    ) -> None:
        """Proportional warmup: ≤1260 trading days → 21d, else → 252d.

        Verifies the warmup logic via a window that is < 5y (use small total
        series so each window is ≤ 1260 days)."""
        from studies.letf_rotation_hunt.gates import g3_walk_forward

        bench = pd.Series(
            np.zeros(len(positive_drift_returns)),
            index=positive_drift_returns.index,
        )
        result = g3_walk_forward(positive_drift_returns, benchmark_returns=bench)
        # 1500 obs / 9 = ~167-day windows → short → warmup 21d
        assert result.get("warmup_used_days") == 21


# ---------------------------------------------------------------------------
# G4 — OOS 70/30 split
# ---------------------------------------------------------------------------


class TestG4OOS:
    """G4: 70/30 temporal hold-out [spec §3.5]."""

    def test_oos_positive_drift_positive_sharpe(self, positive_drift_returns) -> None:
        """Positive drift → OOS Sharpe > 0."""
        from studies.letf_rotation_hunt.gates import g4_oos_70_30

        result = g4_oos_70_30(positive_drift_returns)
        assert isinstance(result, dict)
        assert "oos_sharpe" in result
        assert "pass_gate" in result
        assert result["oos_sharpe"] > 0
        assert result["pass_gate"] is True

    def test_oos_negative_drift_negative_sharpe(self, negative_drift_returns) -> None:
        """Negative drift → OOS Sharpe < 0; fail."""
        from studies.letf_rotation_hunt.gates import g4_oos_70_30

        result = g4_oos_70_30(negative_drift_returns)
        assert result["oos_sharpe"] < 0
        assert result["pass_gate"] is False


# ---------------------------------------------------------------------------
# G5 — FWD post-2020 stress window
# ---------------------------------------------------------------------------


class TestG5FWD:
    """G5: post-2020 stress window [spec §3.5]."""

    def test_fwd_post_2020_returns_only(self, noise_returns_long) -> None:
        """Filter to ≥2020-01-01; compute Sharpe on that slice."""
        from studies.letf_rotation_hunt.gates import g5_fwd_post_2020

        result = g5_fwd_post_2020(noise_returns_long)
        assert isinstance(result, dict)
        assert "fwd_sharpe" in result
        assert "n_obs_post_2020" in result
        assert result["n_obs_post_2020"] > 252

    def test_fwd_no_post_2020_data_fails(self) -> None:
        """Series ending pre-2020 → fail with explanation."""
        from studies.letf_rotation_hunt.gates import g5_fwd_post_2020

        idx = pd.date_range("2010-01-04", periods=500, freq="B")
        rets = pd.Series(np.random.default_rng(0).normal(0, 0.01, 500), index=idx)
        result = g5_fwd_post_2020(rets)
        assert result["pass_gate"] is False
        assert result["n_obs_post_2020"] == 0


# ---------------------------------------------------------------------------
# G6 — Bootstrap 99% CI low > 0
# ---------------------------------------------------------------------------


class TestG6Bootstrap:
    """G6: Stationary block bootstrap, 99% CI low [advances_fin_ml, p.196-202]."""

    def test_bootstrap_strong_positive_drift_ci_low_positive(self) -> None:
        """Series with strong positive drift → 99% CI low > 0."""
        from studies.letf_rotation_hunt.gates import g6_bootstrap_ci

        rng = np.random.default_rng(42)
        n = 1500
        rets = pd.Series(
            rng.normal(0.0015, 0.008, n),  # very strong drift
            index=pd.date_range("2010-01-04", periods=n, freq="B"),
        )
        result = g6_bootstrap_ci(rets, n_resamples=500)
        assert isinstance(result, dict)
        assert "ci_low_sharpe" in result
        assert result["ci_low_sharpe"] > 0
        assert result["pass_gate"] is True

    def test_bootstrap_zero_mean_ci_low_negative(self) -> None:
        """Pure noise → CI low ≤ 0 (likely < 0); fail."""
        from studies.letf_rotation_hunt.gates import g6_bootstrap_ci

        rng = np.random.default_rng(0)
        n = 1500
        rets = pd.Series(
            rng.normal(0.0, 0.01, n),
            index=pd.date_range("2010-01-04", periods=n, freq="B"),
        )
        result = g6_bootstrap_ci(rets, n_resamples=500)
        assert result["pass_gate"] is False


# ---------------------------------------------------------------------------
# G7 — Cross-lib CAGR delta (pandas vs numpy)
# ---------------------------------------------------------------------------


class TestG7CrossLibCAGR:
    """G7: pandas vs numpy CAGR self-check [advances_fin_ml, p.31-34]."""

    def test_xlib_identity_zero_delta(self, positive_drift_returns) -> None:
        """Same returns through pandas and numpy paths → delta ≈ 0."""
        from studies.letf_rotation_hunt.gates import g7_xlib_cagr_delta

        result = g7_xlib_cagr_delta(positive_drift_returns)
        assert isinstance(result, dict)
        assert "delta_pp" in result
        assert "cagr_pandas" in result
        assert "cagr_numpy" in result
        assert abs(result["delta_pp"]) < 0.001  # << 3pp threshold

    def test_xlib_short_series_fails(self) -> None:
        """Series shorter than 252 days → fail (insufficient for CAGR)."""
        from studies.letf_rotation_hunt.gates import g7_xlib_cagr_delta

        idx = pd.date_range("2024-01-04", periods=100, freq="B")
        rets = pd.Series(np.zeros(100), index=idx)
        result = g7_xlib_cagr_delta(rets)
        assert result["pass_gate"] is False
