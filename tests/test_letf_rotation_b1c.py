"""Tests for :mod:`ai_trade.backtest.grid.letf_rotation_b1c` (Phase 3 Lead B1c)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.grid.letf_rotation_b1c import (
    TRADING_DAYS,
    SplitMetrics,
    bootstrap_sharpe_ci,
    compute_split_metrics,
    evaluate_b1c_gates,
    split_into_windows,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    RotationResult,
)


def _mk_result(index: pd.DatetimeIndex, returns: np.ndarray) -> RotationResult:
    """Build a minimal :class:`RotationResult` from a returns vector."""
    s = pd.Series(returns, index=index, dtype=float)
    equity = (1.0 + s).cumprod()
    regime = pd.Series("ON", index=index, dtype=object)
    switches = pd.Series(False, index=index)
    return RotationResult(
        equity=equity,
        daily_returns=s,
        regime=regime,
        switches=switches,
    )


class TestComputeSplitMetrics:
    def test_positive_drift_positive_sharpe(self) -> None:
        rng = np.random.default_rng(0)
        r = pd.Series(rng.normal(0.0005, 0.01, size=2000))
        m = compute_split_metrics("IS", r)
        assert m.name == "IS"
        assert m.n_bars == 2000
        assert m.sharpe > 0
        assert m.cagr > 0
        assert m.max_drawdown <= 0

    def test_zero_vol_returns_zero_sharpe(self) -> None:
        r = pd.Series(np.zeros(500))
        m = compute_split_metrics("flat", r)
        assert m.sharpe == 0.0
        assert m.cagr == 0.0

    def test_empty_series_returns_zero(self) -> None:
        r = pd.Series([], dtype=float)
        m = compute_split_metrics("empty", r)
        assert m.n_bars == 0
        assert m.sharpe == 0.0


class TestSplitIntoWindows:
    def test_even_split(self) -> None:
        r = pd.Series(np.arange(800.0))
        wins = split_into_windows(r, n_windows=8)
        assert len(wins) == 8
        assert all(len(w) == 100 for w in wins)

    def test_uneven_split_remainder_to_last(self) -> None:
        r = pd.Series(np.arange(805.0))
        wins = split_into_windows(r, n_windows=8)
        assert sum(len(w) for w in wins) == 805
        # Last window absorbs 5 extra bars.
        assert len(wins[-1]) == 105

    def test_too_few_bars_raises(self) -> None:
        r = pd.Series(np.arange(3.0))
        with pytest.raises(ValueError, match="too few bars"):
            split_into_windows(r, n_windows=8)


class TestWalkForwardVerdict:
    def test_positive_drift_passes(self) -> None:
        rng = np.random.default_rng(1)
        r = pd.Series(rng.normal(0.0008, 0.008, size=2000))
        ratio, max_dd, passed = walk_forward_verdict_from_returns(r, n_windows=8)
        assert ratio >= 6 / 8
        assert passed

    def test_huge_drawdown_fails(self) -> None:
        # Steady gains then a -90% cliff in the middle.
        r = np.concatenate([
            np.full(800, 0.001),
            np.full(50, -0.1),
            np.full(800, 0.001),
        ])
        ratio, max_dd, passed = walk_forward_verdict_from_returns(
            pd.Series(r), n_windows=8
        )
        assert max_dd > 0.25
        assert not passed

    def test_negative_drift_fails_profitable_ratio(self) -> None:
        rng = np.random.default_rng(2)
        r = pd.Series(rng.normal(-0.001, 0.002, size=1600))
        ratio, _, passed = walk_forward_verdict_from_returns(r, n_windows=8)
        assert ratio < 6 / 8
        assert not passed


class TestBootstrapCI:
    def test_ci_brackets_point_estimate_for_benign_series(self) -> None:
        rng = np.random.default_rng(3)
        r = pd.Series(rng.normal(0.0005, 0.01, size=2000))
        lo, hi = bootstrap_sharpe_ci(
            r, alpha=0.05, n_resamples=500, seed=7
        )
        point = r.mean() / r.std(ddof=1) * np.sqrt(TRADING_DAYS)
        assert lo <= point <= hi
        assert hi - lo > 0

    def test_tiny_series_returns_nan(self) -> None:
        lo, hi = bootstrap_sharpe_ci(pd.Series([0.01, 0.02]))
        assert np.isnan(lo) and np.isnan(hi)


class TestEvaluateB1cGates:
    def _full_index(self, n: int = 1500) -> pd.DatetimeIndex:
        # 1500 bdays ≈ 2005-01 to 2011-01. Enough for 8 WF windows + splits.
        return pd.bdate_range("2005-01-03", periods=n)

    def _build_ranges(self, idx: pd.DatetimeIndex) -> tuple:
        # Split the synthetic window 60/25/15.
        n = len(idx)
        is_end = idx[int(n * 0.60)].strftime("%Y-%m-%d")
        oos_end = idx[int(n * 0.85)].strftime("%Y-%m-%d")
        return (
            (idx[0].strftime("%Y-%m-%d"), is_end),
            (idx[int(n * 0.60) + 1].strftime("%Y-%m-%d"), oos_end),
            (idx[int(n * 0.85) + 1].strftime("%Y-%m-%d"), idx[-1].strftime("%Y-%m-%d")),
        )

    def test_all_fail_when_returns_are_noise(self) -> None:
        idx = self._full_index()
        rng = np.random.default_rng(10)
        configs = [
            LETFRotationConfig(filter="SMA", lookback=100, band_pct=0.0, leverage=1.0),
            LETFRotationConfig(filter="SMA", lookback=200, band_pct=0.0, leverage=1.0),
        ]
        # Pure zero-mean noise → OOS Sharpe ~ 0, should fail.
        results = [
            _mk_result(idx, rng.normal(0.0, 0.01, size=len(idx)))
            for _ in configs
        ]
        is_r, oos_r, stress_r = self._build_ranges(idx)
        verdict = evaluate_b1c_gates(
            configs, results,
            is_range=is_r, oos_range=oos_r, stress_range=stress_r,
            bootstrap_n_resamples=200,
        )
        assert verdict.n_configs == 2
        assert verdict.winner_config_id is None
        assert all(e.verdict == "FAIL" for e in verdict.evaluations)

    def test_clear_winner_passes_all_gates(self) -> None:
        idx = self._full_index(n=2400)
        rng = np.random.default_rng(11)
        # 3 configs; config[0] has strong +drift, others are noise.
        configs = [
            LETFRotationConfig(filter="SMA", lookback=100, band_pct=0.0, leverage=1.0),
            LETFRotationConfig(filter="SMA", lookback=150, band_pct=0.0, leverage=1.0),
            LETFRotationConfig(filter="EMA", lookback=200, band_pct=0.0, leverage=1.0),
        ]
        winner_rets = rng.normal(0.0018, 0.004, size=len(idx))
        # Small noise for losers so DSR won't pass.
        noise_rets = rng.normal(0.0, 0.008, size=len(idx))
        noise_rets2 = rng.normal(0.0, 0.008, size=len(idx))
        results = [
            _mk_result(idx, winner_rets),
            _mk_result(idx, noise_rets),
            _mk_result(idx, noise_rets2),
        ]
        is_r, oos_r, stress_r = self._build_ranges(idx)
        verdict = evaluate_b1c_gates(
            configs, results,
            is_range=is_r, oos_range=oos_r, stress_range=stress_r,
            bootstrap_n_resamples=200,
            bootstrap_alpha=0.05,
        )
        assert verdict.pbo_pass  # 1 strong + 2 noise → IS-best stays best OOS.
        assert verdict.winner_config_id == 0
        assert verdict.evaluations[0].verdict == "PASS"
        assert verdict.evaluations[0].bootstrap_sharpe_lo is not None
        assert verdict.evaluations[0].bootstrap_sharpe_lo > 0

    def test_misaligned_indices_rejected(self) -> None:
        idx_a = self._full_index(n=500)
        idx_b = pd.bdate_range("2005-01-04", periods=500)
        configs = [
            LETFRotationConfig(filter="SMA", lookback=100, band_pct=0.0, leverage=1.0),
            LETFRotationConfig(filter="SMA", lookback=200, band_pct=0.0, leverage=1.0),
        ]
        results = [
            _mk_result(idx_a, np.zeros(500)),
            _mk_result(idx_b, np.zeros(500)),
        ]
        with pytest.raises(ValueError, match="same daily index"):
            evaluate_b1c_gates(
                configs, results,
                is_range=("2005-01-03", "2005-06-01"),
                oos_range=("2005-06-02", "2006-01-01"),
                stress_range=("2006-01-02", "2006-12-31"),
            )
