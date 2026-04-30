"""TDD tests for studies.spy_beater_hunt + TMF synth in long_term_portfolio.synths.

Covers:
- TMF synth formula (3x TLT - daily decay) + cache loader
- Gayed 200d SMA gate (no peek-ahead via T+1 lag)
- LRS strategy returns (alternates on/off based on gate)
- spy_beater scoring (CAGR-anchored rubric per WINNER_AND_RANKING.md)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# TMF synth (lives in long_term_portfolio.synths for reuse)
# ---------------------------------------------------------------------------


def test_tmf_synth_formula():
    """TMF = 3 * TLT - (1.5%/y / 252) per day."""
    from studies.long_term_portfolio.synths import tmf_synth_returns

    tlt = pd.Series(
        [0.01, 0.0, -0.005, 0.002],
        index=pd.date_range("2024-01-02", periods=4, freq="B"),
    )
    result = tmf_synth_returns(tlt, leverage=3.0, daily_reset_decay_annual=0.015)

    expected_day1 = 3.0 * 0.01 - 0.015 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-10
    expected_day2 = 3.0 * 0.0 - 0.015 / 252
    assert abs(result.iloc[1] - expected_day2) < 1e-10
    assert len(result) == 4


def test_tmf_synth_from_cache_smoke():
    """TMF synth from cache: should produce 1962+ daily series (TLTSIM window)."""
    from studies.long_term_portfolio.synths import tmf_synth_returns_from_cache

    s = tmf_synth_returns_from_cache()
    assert isinstance(s, pd.Series)
    assert isinstance(s.index, pd.DatetimeIndex)
    # TLTSIM cache starts 1962-01-02
    assert s.index[0] <= pd.Timestamp("1962-12-31")
    # 60+ years of daily data
    assert len(s) > 15_000


def test_tmf_synth_realistic_amplification():
    """TMF daily returns should be ~3x TLT in magnitude on the active days."""
    from studies.long_term_portfolio.synths import tmf_synth_returns_from_cache
    from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_series

    tlt = load_testfolio_series("TLTSIM").pct_change().dropna()
    tmf = tmf_synth_returns_from_cache()
    aligned = pd.concat({"tlt": tlt, "tmf": tmf}, axis=1).dropna()
    # Std ratio should be very close to 3x (decay is constant, doesn't add vol)
    ratio = aligned["tmf"].std() / aligned["tlt"].std()
    assert 2.95 < ratio < 3.05


# ---------------------------------------------------------------------------
# Gayed LRS gate (200d SMA, T+1 lag — no peek-ahead)
# ---------------------------------------------------------------------------


def test_gayed_gate_no_peek_ahead():
    """Gate at time t uses signal at t-1 (T+1 lag enforced).

    Build a synthetic price series that crosses its SMA on a known day.
    Verify that the gate flips one day AFTER the cross.
    """
    from studies.spy_beater_hunt.lrs_engine import gayed_200d_sma_gate

    # 250 days of constant 100, then a sharp jump up.
    # SMA on day 250 = 100; price = 200 → cross. Gate should flip True on day 251.
    n_pre = 250
    prices = pd.Series(
        [100.0] * n_pre + [200.0] * 50,
        index=pd.date_range("2020-01-02", periods=n_pre + 50, freq="B"),
    )
    gate = gayed_200d_sma_gate(prices, window=200, lag_days=1)

    # On day n_pre (the cross day), gate should still reflect signal from t-1
    # (which was 100 == 100, not > SMA, so False).
    cross_idx = prices.index[n_pre]
    assert gate.loc[cross_idx] == False  # noqa: E712

    # On day n_pre + 1, gate should reflect signal from cross day (price > SMA → True).
    next_day = prices.index[n_pre + 1]
    assert gate.loc[next_day] == True  # noqa: E712


def test_gayed_gate_initial_window_false():
    """First `window` days have NaN SMA → gate fills False (defensive default)."""
    from studies.spy_beater_hunt.lrs_engine import gayed_200d_sma_gate

    prices = pd.Series(
        np.linspace(100.0, 150.0, 100),
        index=pd.date_range("2020-01-02", periods=100, freq="B"),
    )
    gate = gayed_200d_sma_gate(prices, window=200, lag_days=1)
    # All 100 days are pre-window → gate should be all False
    assert (gate == False).all()  # noqa: E712


def test_gayed_gate_window_and_lag_param():
    """Verify window and lag_days are honoured."""
    from studies.spy_beater_hunt.lrs_engine import gayed_200d_sma_gate

    # 50d window
    prices = pd.Series(
        [100.0] * 60 + [200.0] * 20,
        index=pd.date_range("2020-01-02", periods=80, freq="B"),
    )
    gate = gayed_200d_sma_gate(prices, window=50, lag_days=1)
    # Cross at idx 60. With T+1 lag, gate flips True at idx 61.
    assert gate.iloc[59] == False  # noqa: E712 (signal at 58 < SMA at 58)
    assert gate.iloc[61] == True  # noqa: E712 (signal at 60 > SMA at 60)


# ---------------------------------------------------------------------------
# LRS strategy returns
# ---------------------------------------------------------------------------


def test_lrs_returns_alternate_on_off():
    """LRS returns equal on_returns when gate=True, off_returns when gate=False."""
    from studies.spy_beater_hunt.lrs_engine import lrs_strategy_returns

    idx = pd.date_range("2020-01-02", periods=5, freq="B")
    on_returns = pd.Series([0.02, 0.01, 0.03, -0.01, 0.02], index=idx)
    off_returns = pd.Series([0.001, 0.001, 0.001, 0.001, 0.001], index=idx)
    gate = pd.Series([True, False, True, False, True], index=idx)

    result = lrs_strategy_returns(on_returns, off_returns, gate)

    expected = [0.02, 0.001, 0.03, 0.001, 0.02]
    np.testing.assert_allclose(result.values, expected, atol=1e-10)


def test_lrs_returns_alignment_drops_misaligned_dates():
    """When inputs have different index coverage, LRS aligns on intersection."""
    from studies.spy_beater_hunt.lrs_engine import lrs_strategy_returns

    on_returns = pd.Series(
        [0.01, 0.02], index=pd.to_datetime(["2020-01-02", "2020-01-03"])
    )
    off_returns = pd.Series(
        [0.001, 0.001, 0.001],
        index=pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"]),
    )
    gate = pd.Series(
        [True, False, True],
        index=pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"]),
    )

    result = lrs_strategy_returns(on_returns, off_returns, gate)
    # Only first two dates have all three series; third date misses on_returns.
    assert len(result) == 2
    np.testing.assert_allclose(result.values, [0.01, 0.001], atol=1e-10)


# ---------------------------------------------------------------------------
# spy_beater scoring (CAGR-anchored)
# ---------------------------------------------------------------------------


def test_scoring_cagr_at_spy_mean_yields_30_proportional_pts():
    """CAGR criterion: 30 × clamp((mean_cagr - 0.05) / 0.15, 0, 1).

    SPY mean (0.1380) → (0.1380 - 0.05) / 0.15 = 0.5867 → 30 × 0.5867 = 17.6 → 18 pts (round).
    """
    from studies.spy_beater_hunt.scoring import compute_cagr_points

    pts = compute_cagr_points(mean_cagr=0.1380)
    assert pts == 18  # round(17.6) = 18


def test_scoring_cagr_below_floor_zero_pts():
    """CAGR ≤ 5% → 0 points."""
    from studies.spy_beater_hunt.scoring import compute_cagr_points

    assert compute_cagr_points(mean_cagr=0.04) == 0
    assert compute_cagr_points(mean_cagr=0.00) == 0


def test_scoring_cagr_above_ceiling_max_pts():
    """CAGR ≥ 20% → 30 points."""
    from studies.spy_beater_hunt.scoring import compute_cagr_points

    assert compute_cagr_points(mean_cagr=0.20) == 30
    assert compute_cagr_points(mean_cagr=0.25) == 30


def test_scoring_mdd_at_spy_mean_yields_proportional_pts():
    """MDD criterion: 20 × clamp((0.50 - mean_mdd) / 0.40, 0, 1).

    SPY mean (0.4085) → (0.50 - 0.4085) / 0.40 = 0.2287 → 20 × 0.2287 = 4.6 → 4 pts.
    """
    from studies.spy_beater_hunt.scoring import compute_mdd_points

    pts = compute_mdd_points(mean_mdd=0.4085)
    assert pts == 4


def test_scoring_mdd_above_ceiling_zero():
    """MDD ≥ 50% → 0 points."""
    from studies.spy_beater_hunt.scoring import compute_mdd_points

    assert compute_mdd_points(mean_mdd=0.55) == 0


def test_scoring_winner_requires_all_three_bars():
    """WINNER conditions: cagr_bar AND mdd_bar AND gates_bar all true."""
    from studies.spy_beater_hunt.scoring import score_strategy_spy_beater
    from studies.long_term_portfolio.scoring import DatasetMetrics, Gates

    # All bars met scenario
    metrics = {
        "lh_56y": DatasetMetrics(sharpe=1.2, cagr=0.14, mdd=0.40, dsr_p_value=0.01),
        "vt_real": DatasetMetrics(sharpe=1.3, cagr=0.16, mdd=0.35, dsr_p_value=0.01),
        "ndx_real": DatasetMetrics(sharpe=1.4, cagr=0.18, mdd=0.30, dsr_p_value=0.01),
    }
    all_pass = Gates(True, True, True, True, True, True, True)
    gates = {"lh_56y": all_pass, "vt_real": all_pass, "ndx_real": all_pass}

    result = score_strategy_spy_beater(metrics, gates, cumulative_n_trials=4)
    assert result["bars"]["cagr_bar"] is True  # mean = 0.16 ≥ 0.1380
    assert result["bars"]["mdd_bar"] is True   # mean = 0.35 ≤ 0.4085
    assert result["bars"]["gates_bar"] is True
    assert result["winner_conditions_met"] is True


def test_scoring_winner_blocked_by_cagr_bar():
    """Mean CAGR < 13.80% blocks WINNER even if other bars met."""
    from studies.spy_beater_hunt.scoring import score_strategy_spy_beater
    from studies.long_term_portfolio.scoring import DatasetMetrics, Gates

    metrics = {
        "lh_56y": DatasetMetrics(sharpe=0.9, cagr=0.10, mdd=0.30, dsr_p_value=0.04),
        "vt_real": DatasetMetrics(sharpe=0.9, cagr=0.10, mdd=0.30, dsr_p_value=0.04),
        "ndx_real": DatasetMetrics(sharpe=0.9, cagr=0.10, mdd=0.30, dsr_p_value=0.04),
    }
    all_pass = Gates(True, True, True, True, True, True, True)
    gates = {"lh_56y": all_pass, "vt_real": all_pass, "ndx_real": all_pass}

    result = score_strategy_spy_beater(metrics, gates, cumulative_n_trials=4)
    assert result["bars"]["cagr_bar"] is False  # 0.10 < 0.1380
    assert result["winner_conditions_met"] is False
    assert result["tier"] != "WINNER"


def test_scoring_score_clamped_0_100():
    """Score is clamped to [0, 100] even with extreme inputs + bonuses."""
    from studies.spy_beater_hunt.scoring import score_strategy_spy_beater
    from studies.long_term_portfolio.scoring import DatasetMetrics, Gates

    metrics = {
        "lh_56y": DatasetMetrics(sharpe=2.5, cagr=0.30, mdd=0.05, dsr_p_value=0.001),
        "vt_real": DatasetMetrics(sharpe=2.5, cagr=0.30, mdd=0.05, dsr_p_value=0.001),
        "ndx_real": DatasetMetrics(sharpe=2.5, cagr=0.30, mdd=0.05, dsr_p_value=0.001),
    }
    all_pass = Gates(True, True, True, True, True, True, True)
    gates = {"lh_56y": all_pass, "vt_real": all_pass, "ndx_real": all_pass}

    result = score_strategy_spy_beater(
        metrics, gates, cumulative_n_trials=4, robustness_bonus=10, extra_bonus=5
    )
    assert 0 <= result["total_score"] <= 100
