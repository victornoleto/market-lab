"""Tests for TSMOM A3b gate aggregator."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.grid.tsmom_a3b import (
    A3bGateVerdict,
    default_tsmom_grid,
    evaluate_tsmom_gates,
)
from ai_trade.backtest.strategies.tsmom import (
    TSMOMConfig,
    simulate_tsmom,
)


def _trending_ohlc(
    n: int, daily_mu: float, daily_sigma: float, seed: int
) -> tuple[pd.Series, pd.Series, pd.Series]:
    idx = pd.date_range("2000-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    rets = rng.normal(daily_mu, daily_sigma, n)
    close = pd.Series((1.0 + rets).cumprod() * 100.0, index=idx)
    intra = rng.normal(0, 0.003, n) * close.values
    high = close + np.abs(intra) + 0.001 * close
    low = close - np.abs(intra) - 0.001 * close
    return high, low, close


class TestDefaultGrid:
    def test_only_valid_pairs(self):
        grid = default_tsmom_grid(
            entry_lookbacks=(20, 40), exit_lookbacks=(10, 20, 50)
        )
        # (20,50) should be excluded because exit > entry
        for cfg in grid:
            assert cfg.exit_lookback <= cfg.entry_lookback
        assert all(isinstance(c, TSMOMConfig) for c in grid)

    def test_tax_applied_to_all(self):
        grid = default_tsmom_grid(tax_rate=0.10)
        assert all(c.tax_rate == 0.10 for c in grid)


class TestEvaluateTSMOMGates:
    def test_unequal_configs_results_raises(self):
        high, low, close = _trending_ohlc(n=400, daily_mu=0.001, daily_sigma=0.01, seed=3)
        cfg = TSMOMConfig(entry_lookback=20, exit_lookback=10)
        res = simulate_tsmom(high, low, close, cfg)
        with pytest.raises(ValueError, match="equal length"):
            evaluate_tsmom_gates(
                "X",
                [cfg, cfg],
                [res],
                is_range=("2000-01-01", "2000-06-30"),
                oos_range=("2000-07-01", "2001-01-01"),
                stress_range=("2001-01-02", "2001-06-30"),
            )

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            evaluate_tsmom_gates(
                "X",
                [],
                [],
                is_range=("2000-01-01", "2000-06-30"),
                oos_range=("2000-07-01", "2001-01-01"),
                stress_range=("2001-01-02", "2001-06-30"),
            )

    def test_misaligned_indices_raise(self):
        high1, low1, close1 = _trending_ohlc(400, 0.001, 0.01, 3)
        high2, low2, close2 = _trending_ohlc(380, 0.001, 0.01, 5)
        cfg = TSMOMConfig(entry_lookback=20, exit_lookback=10)
        r1 = simulate_tsmom(high1, low1, close1, cfg)
        r2 = simulate_tsmom(high2, low2, close2, cfg)
        with pytest.raises(ValueError, match="same daily index"):
            evaluate_tsmom_gates(
                "X", [cfg, cfg], [r1, r2],
                is_range=("2000-01-01", "2000-06-30"),
                oos_range=("2000-07-01", "2001-01-01"),
                stress_range=("2001-01-02", "2001-06-30"),
            )

    def test_returns_verdict_with_sensible_fields(self):
        high, low, close = _trending_ohlc(
            n=800, daily_mu=0.002, daily_sigma=0.01, seed=17
        )
        grid = default_tsmom_grid(
            entry_lookbacks=(20, 40), exit_lookbacks=(10, 20)
        )
        results = [simulate_tsmom(high, low, close, c) for c in grid]
        verdict = evaluate_tsmom_gates(
            "SYN",
            grid,
            results,
            is_range=("2000-01-01", "2001-06-30"),
            oos_range=("2001-07-01", "2002-06-30"),
            stress_range=("2002-07-01", "2003-06-30"),
            pbo_n_blocks=4,
            bootstrap_n_resamples=200,
        )
        assert isinstance(verdict, A3bGateVerdict)
        assert verdict.asset == "SYN"
        assert verdict.n_configs == len(grid)
        assert 0 <= verdict.n_passing_configs <= len(grid)
        for ev in verdict.evaluations:
            assert ev.is_metrics.n_bars > 0
            assert ev.oos_metrics.n_bars > 0
            assert ev.verdict in {"PASS", "FAIL"}

    def test_choppy_synthetic_fails_gates(self):
        """A truly zero-drift process should NOT produce a winner."""
        idx = pd.date_range("2000-01-01", periods=800, freq="B")
        rng = np.random.default_rng(42)
        rets = rng.normal(0.0, 0.005, 800)
        close = pd.Series((1.0 + rets).cumprod() * 100.0, index=idx)
        intra = rng.normal(0, 0.003, 800) * close.values
        high = close + np.abs(intra) + 0.001 * close
        low = close - np.abs(intra) - 0.001 * close

        grid = default_tsmom_grid(
            entry_lookbacks=(20, 40), exit_lookbacks=(10, 20)
        )
        results = [simulate_tsmom(high, low, close, c) for c in grid]
        verdict = evaluate_tsmom_gates(
            "NOISE",
            grid,
            results,
            is_range=("2000-01-01", "2001-06-30"),
            oos_range=("2001-07-01", "2002-06-30"),
            stress_range=("2002-07-01", "2003-01-01"),
            pbo_n_blocks=4,
            bootstrap_n_resamples=100,
        )
        # Random-drift should not yield a gate-passing config.
        assert verdict.winner_config_id is None

    def test_to_dict_roundtrip(self):
        high, low, close = _trending_ohlc(600, 0.001, 0.01, 9)
        grid = default_tsmom_grid(
            entry_lookbacks=(20,), exit_lookbacks=(10,)
        )
        results = [simulate_tsmom(high, low, close, c) for c in grid]
        # Grid of size 1 → DSR needs n_trials>=2; expect NaN DSR_p.
        verdict = evaluate_tsmom_gates(
            "X",
            grid,
            results,
            is_range=("2000-01-01", "2001-01-01"),
            oos_range=("2001-01-02", "2001-12-31"),
            stress_range=("2002-01-01", "2002-06-30"),
            pbo_n_blocks=4,
            bootstrap_n_resamples=100,
        )
        d = verdict.to_dict()
        assert d["asset"] == "X"
        assert d["n_configs"] == 1
        assert isinstance(d["evaluations"], list)
