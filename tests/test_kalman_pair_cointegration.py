"""Tests for the V2-L5 Kalman pair cointegration strategy module."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.kalman_pair_cointegration import (
    KalmanPairConfig,
    KalmanPairResult,
    _engle_granger,
    _kalman_alpha_beta,
    run_kalman_pair_pipeline,
)


def _synth_cointegrated(
    n: int = 1000,
    beta_true: float = 1.5,
    seed: int = 7,
    shock_std: float = 0.05,
) -> tuple[pd.Series, pd.Series]:
    """Generate a mean-reverting spread + random-walk x; y = a + b*x + spread.

    ``shock_std`` sized so the Kalman innovation z-score regularly crosses
    2sigma, which is the V2-L5 trading threshold.
    """
    rng = np.random.default_rng(seed)
    x_log = np.cumsum(rng.normal(0.0, 0.01, size=n)) + 4.0  # log prices around 4
    # AR(1) mean-reverting spread
    phi = 0.8
    spread = np.zeros(n)
    for t in range(1, n):
        spread[t] = phi * spread[t - 1] + rng.normal(0.0, shock_std)
    y_log = 0.2 + beta_true * x_log + spread
    idx = pd.date_range("2015-01-01", periods=n, freq="B")
    return (
        pd.Series(np.exp(y_log), index=idx, name="Y"),
        pd.Series(np.exp(x_log), index=idx, name="X"),
    )


def _synth_noncointegrated(
    n: int = 504,
    seed: int = 11,
) -> tuple[pd.Series, pd.Series]:
    """Two independent random walks (non-cointegrated)."""
    rng = np.random.default_rng(seed)
    x_log = np.cumsum(rng.normal(0.0, 0.01, size=n)) + 4.0
    y_log = np.cumsum(rng.normal(0.0, 0.01, size=n)) + 4.0
    idx = pd.date_range("2015-01-01", periods=n, freq="B")
    return (
        pd.Series(np.exp(y_log), index=idx, name="Y"),
        pd.Series(np.exp(x_log), index=idx, name="X"),
    )


# ---------------------------------------------------------------------------
# Unit — Engle-Granger gate
# ---------------------------------------------------------------------------


def test_engle_granger_accepts_cointegrated_pair():
    y, x = _synth_cointegrated()
    res = _engle_granger(y, x, alpha=0.05)
    assert res["pass"] is True
    assert res["adf_p_value"] < 0.05
    assert abs(res["ols_beta"] - 1.5) < 0.2  # beta recovered


def test_engle_granger_rejects_independent_random_walks():
    y, x = _synth_noncointegrated()
    res = _engle_granger(y, x, alpha=0.05)
    assert res["pass"] is False
    assert res["adf_p_value"] >= 0.01  # independent RW usually >> 0.05


def test_engle_granger_rejects_short_series():
    y, x = _synth_cointegrated(n=10)
    res = _engle_granger(y, x, alpha=0.05)
    assert res["pass"] is False
    assert "30" in res["reason"]


# ---------------------------------------------------------------------------
# Unit — Kalman filter
# ---------------------------------------------------------------------------


def test_kalman_recovers_true_beta_on_cointegrated_pair():
    # Weak spread noise so the filter can converge cleanly to the true beta.
    y, x = _synth_cointegrated(beta_true=1.5, n=1200, shock_std=0.005)
    y_log = np.log(y.to_numpy())
    x_log = np.log(x.to_numpy())
    _, beta, _, _ = _kalman_alpha_beta(
        y_log, x_log, delta=1e-5, observation_variance=1e-3
    )
    # Kalman converges slowly with small delta; tolerance 0.3 is fine for
    # validating the filter "tracks" the true beta without runaway.
    final = beta[-200:].mean()
    assert abs(final - 1.5) < 0.3, f"kalman beta did not track true beta (final={final:.3f})"


def test_kalman_returns_arrays_of_matching_length():
    y, x = _synth_cointegrated(n=200)
    alpha, beta, innov, innov_var = _kalman_alpha_beta(
        np.log(y.to_numpy()), np.log(x.to_numpy()), delta=1e-5, observation_variance=1e-3
    )
    assert alpha.shape == (200,)
    assert beta.shape == (200,)
    assert innov.shape == (200,)
    assert innov_var.shape == (200,)
    assert np.all(innov_var > 0)


# ---------------------------------------------------------------------------
# Integration — run_kalman_pair_pipeline
# ---------------------------------------------------------------------------


def test_pipeline_returns_zero_series_when_not_cointegrated():
    y, x = _synth_noncointegrated()
    result = run_kalman_pair_pipeline(y, x, pair_name="RW_RW")
    assert isinstance(result, KalmanPairResult)
    assert result.cointegration["pass"] is False
    assert result.daily_returns.abs().sum() == 0.0
    assert result.n_events_total == 0
    assert result.trade_ledger == []


def test_pipeline_trades_cointegrated_pair_with_finite_pnl():
    y, x = _synth_cointegrated()
    result = run_kalman_pair_pipeline(y, x, pair_name="SYN_COINT")
    assert result.cointegration["pass"] is True
    # Must produce at least one trade given the strong synthetic edge
    assert len(result.trade_ledger) >= 1
    # Daily return series must be finite everywhere
    assert np.all(np.isfinite(result.daily_returns.to_numpy()))
    # Trade ledger entries have the required structure
    tr0 = result.trade_ledger[0]
    for key in ("entry_bar", "exit_bar", "hold_bars", "direction", "exit_reason"):
        assert key in tr0


def test_pipeline_respects_hold_cap_days():
    y, x = _synth_cointegrated()
    cfg = KalmanPairConfig(hold_cap_days=5)
    result = run_kalman_pair_pipeline(y, x, cfg=cfg, pair_name="SYN")
    assert result.cointegration["pass"] is True
    # No closed round-trip should exceed the cap
    closed = [tr for tr in result.trade_ledger if tr["exit_reason"] != "end_of_data"]
    assert closed, "synthetic cointegrated pair should produce at least one closed trade"
    assert all(tr["hold_bars"] <= cfg.hold_cap_days for tr in closed)


def test_pipeline_no_lookahead_signals_act_on_next_bar():
    """Position must be zero on the first bar — no signal can trade bar 0."""
    y, x = _synth_cointegrated()
    result = run_kalman_pair_pipeline(y, x, pair_name="SYN")
    assert result.daily_returns.iloc[0] == 0.0


def test_pipeline_drops_non_overlapping_dates():
    y, x = _synth_cointegrated(n=200)
    # Chop 10 leading bars off y and 5 trailing bars off x -> common window
    y_short = y.iloc[10:]
    x_short = x.iloc[:-5]
    result = run_kalman_pair_pipeline(y_short, x_short, pair_name="SYN")
    # Inner-joined index is the overlap of the two
    expected_n = len(y.index[10:-5])
    assert len(result.daily_returns) == expected_n


# ---------------------------------------------------------------------------
# Unit — cost model invariants
# ---------------------------------------------------------------------------


def test_pipeline_accumulates_positive_transaction_cost():
    y, x = _synth_cointegrated()
    result = run_kalman_pair_pipeline(y, x, pair_name="SYN")
    assert result.cum_transaction_cost_pct > 0.0


def test_pipeline_accumulates_positive_swap_cost():
    y, x = _synth_cointegrated()
    result = run_kalman_pair_pipeline(y, x, pair_name="SYN")
    # At least one day held => non-zero swap
    assert result.cum_swap_cost_pct > 0.0


def test_kalman_pair_config_canonical_defaults():
    cfg = KalmanPairConfig()
    assert cfg.entry_z == 2.0
    assert cfg.exit_z == 0.0
    assert cfg.stop_z == 4.0
    assert cfg.hold_cap_days == 30
    assert cfg.adf_alpha == 0.05
    assert cfg.delta == 1e-5
    assert cfg.observation_variance == 1e-3
