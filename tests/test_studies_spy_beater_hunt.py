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
# EMA gate
# ---------------------------------------------------------------------------


def test_ema_gate_no_peek_ahead():
    """EMA gate at time t uses signal at t-1 (T+1 lag enforced)."""
    from studies.spy_beater_hunt.lrs_engine import ema_gate

    # Constant 100 then jump to 200; EMA reacts faster than SMA
    n_pre = 100
    prices = pd.Series(
        [100.0] * n_pre + [200.0] * 30,
        index=pd.date_range("2020-01-02", periods=n_pre + 30, freq="B"),
    )
    gate = ema_gate(prices, window=50, lag_days=1)
    # Pre-window: gate False (NaN EMA)
    assert gate.iloc[10] == False  # noqa: E712
    # Post-jump: gate flips to True after 1-2 days (EMA fast-reacts)
    assert gate.iloc[n_pre + 5] == True  # noqa: E712


def test_ema_gate_smoother_than_sma():
    """EMA differs from SMA: react faster on trend changes."""
    from studies.spy_beater_hunt.lrs_engine import ema_gate, gayed_200d_sma_gate

    rng = np.random.default_rng(42)
    # Synthetic uptrend with noise
    n = 500
    drift = np.linspace(100, 200, n)
    noise = rng.normal(0, 5, n)
    prices = pd.Series(
        drift + noise,
        index=pd.date_range("2020-01-02", periods=n, freq="B"),
    )
    sma_gate = gayed_200d_sma_gate(prices, window=100, lag_days=1)
    e_gate = ema_gate(prices, window=100, lag_days=1)
    # Both should be True for the dominant uptrend portion (last 200 days)
    assert sma_gate.iloc[300:].mean() > 0.7
    assert e_gate.iloc[300:].mean() > 0.7


# ---------------------------------------------------------------------------
# Threshold band gate (hysteresis)
# ---------------------------------------------------------------------------


def test_threshold_band_no_flip_within_buffer():
    """Hysteresis: small fluctuations within the buffer band do NOT flip state."""
    from studies.spy_beater_hunt.lrs_engine import threshold_band_gate

    # Prices oscillate ±1.5% around 100 (buffer 2%) → no flips after initial
    n_pre = 100  # warm-up for SMA window=50
    rng = np.random.default_rng(0)
    base = np.full(n_pre + 50, 100.0)
    noise = rng.uniform(-1.5, 1.5, n_pre + 50)  # ±1.5% < 2% buffer
    prices = pd.Series(
        base + noise,
        index=pd.date_range("2020-01-02", periods=n_pre + 50, freq="B"),
    )
    gate = threshold_band_gate(
        prices, window=50, buffer_pct=0.02, lag_days=1, filter_type="sma"
    )
    # State should be stable (mostly one value) after warm-up
    post_warmup = gate.iloc[n_pre:]
    flip_count = (post_warmup.diff().abs().sum())
    # Expect very few flips (≤ 5) given noise stays within buffer
    assert flip_count <= 5


def test_threshold_band_flips_on_breakout():
    """When price breaks above MA*(1+buffer), gate flips ON."""
    from studies.spy_beater_hunt.lrs_engine import threshold_band_gate

    # 100 days at $100, then jump to $110 (10% > 2% buffer)
    n_pre = 100
    prices = pd.Series(
        [100.0] * n_pre + [110.0] * 30,
        index=pd.date_range("2020-01-02", periods=n_pre + 30, freq="B"),
    )
    gate = threshold_band_gate(
        prices, window=50, buffer_pct=0.02, lag_days=1, filter_type="sma"
    )
    # After the jump + 1 day lag, gate should be ON
    assert gate.iloc[n_pre + 2] == True  # noqa: E712


def test_threshold_band_holds_state_in_band():
    """Once ON, stay ON until price drops below MA*(1-buffer)."""
    from studies.spy_beater_hunt.lrs_engine import threshold_band_gate

    # Step up then sit slightly below MA but inside band → stay ON
    idx = pd.date_range("2020-01-02", periods=200, freq="B")
    prices = pd.Series(np.concatenate([
        np.full(100, 100.0),    # warm-up
        np.full(20, 110.0),     # break above (state → ON)
        np.full(80, 105.0),     # slightly below MA (which is now ~108)
                                # but within ±2% buffer → HOLD ON
    ]), index=idx)
    gate = threshold_band_gate(
        prices, window=50, buffer_pct=0.02, lag_days=1, filter_type="sma"
    )
    # Tail should still be ON (held state)
    # We pick a sample point well after the step
    assert gate.iloc[125] == True  # noqa: E712 — within hysteresis hold


def test_threshold_band_zero_buffer_matches_naive_gate():
    """buffer_pct=0 with hysteresis still has slightly different behavior at exact-cross days,
    but should match SMA gate within 5% of bars."""
    from studies.spy_beater_hunt.lrs_engine import (
        gayed_200d_sma_gate,
        threshold_band_gate,
    )

    rng = np.random.default_rng(1)
    n = 500
    prices = pd.Series(
        100.0 + rng.normal(0, 5, n).cumsum() * 0.1,
        index=pd.date_range("2020-01-02", periods=n, freq="B"),
    )
    naive = gayed_200d_sma_gate(prices, window=50, lag_days=1)
    band = threshold_band_gate(
        prices, window=50, buffer_pct=0.0, lag_days=1, filter_type="sma"
    )
    # Should agree on most days (>= 95%) — the hysteresis with 0 buffer
    # only differs on exact-equality bars (price == MA), which are rare.
    agreement = (naive == band).mean()
    assert agreement > 0.95


def test_threshold_band_ema_filter():
    """EMA filter type works without raising and produces sensible state."""
    from studies.spy_beater_hunt.lrs_engine import threshold_band_gate

    n = 200
    prices = pd.Series(
        np.linspace(100, 200, n),  # steady uptrend
        index=pd.date_range("2020-01-02", periods=n, freq="B"),
    )
    gate = threshold_band_gate(
        prices, window=50, buffer_pct=0.02, lag_days=1, filter_type="ema"
    )
    # In a clear uptrend, gate should be ON for the bulk of post-warmup days
    assert gate.iloc[100:].mean() > 0.8


def test_threshold_band_invalid_filter_raises():
    """filter_type other than 'sma'/'ema' raises ValueError."""
    from studies.spy_beater_hunt.lrs_engine import threshold_band_gate

    prices = pd.Series([100.0] * 100, index=pd.date_range("2020-01-02", periods=100, freq="B"))
    with pytest.raises(ValueError, match="filter_type"):
        threshold_band_gate(prices, filter_type="rsi")


# ---------------------------------------------------------------------------
# Time-series momentum (TSMOM) gate
# Citation: Moskowitz/Ooi/Pedersen (2012) "Time Series Momentum"
# ---------------------------------------------------------------------------


def test_momentum_gate_no_peek_ahead():
    """TSMOM gate at time t uses signal at t-1 (T+1 lag enforced).

    Build a series where price drops below its lookback-ago value on a
    known day; gate should flip OFF one day AFTER (lag=1), not on cross day.
    """
    from studies.spy_beater_hunt.lrs_engine import momentum_gate

    # 100d rising trend (TSMOM ON), then 60d decline (TSMOM OFF after lookback)
    n = 200
    lookback = 60
    prices = pd.Series(
        list(np.linspace(100.0, 200.0, 100)) + list(np.linspace(200.0, 80.0, 100)),
        index=pd.date_range("2020-01-02", periods=n, freq="B"),
    )
    gate = momentum_gate(prices, lookback_days=lookback, lag_days=1)

    # Rising portion (post-lookback warmup): True
    assert gate.iloc[lookback + 30] == True  # noqa: E712
    # Declining portion deep enough that price[t] < price[t-lookback]: False
    assert gate.iloc[180] == False  # noqa: E712


def test_momentum_gate_initial_lookback_false():
    """First `lookback_days` days have NaN past → gate fills False (defensive)."""
    from studies.spy_beater_hunt.lrs_engine import momentum_gate

    prices = pd.Series(
        np.linspace(100.0, 150.0, 30),
        index=pd.date_range("2020-01-02", periods=30, freq="B"),
    )
    gate = momentum_gate(prices, lookback_days=126, lag_days=1)
    # All 30 days are pre-lookback → gate should be all False
    assert (gate == False).all()  # noqa: E712


def test_momentum_gate_lookback_param():
    """Verify lookback_days parameter is honoured (price > price[t-lookback])."""
    from studies.spy_beater_hunt.lrs_engine import momentum_gate

    # 30 flat days at 100, then 1 jump to 150, then 30 flat at 150
    n = 61
    prices = pd.Series(
        [100.0] * 30 + [150.0] * 31,
        index=pd.date_range("2020-01-02", periods=n, freq="B"),
    )
    # With lookback=20, at idx 50: price=150, price[t-20]=price[30]=150 → not >
    # At idx 50, price[t-21]=100 → with lookback=21, gate ON (lagged to idx 51)
    gate_lb20 = momentum_gate(prices, lookback_days=20, lag_days=1)
    gate_lb40 = momentum_gate(prices, lookback_days=40, lag_days=1)
    # At idx 51: lookback=20 sees price[31]=150 vs current=150 → False
    assert gate_lb20.iloc[51] == False  # noqa: E712
    # At idx 51: lookback=40 sees price[11]=100 vs current=150 → True
    assert gate_lb40.iloc[51] == True  # noqa: E712


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
    """MDD criterion: 20 × clamp((0.70 - mean_mdd) / (0.70 - 0.15), 0, 1).

    Post-2026-04-29 refactor: MDD floor 15%, ceiling 70% (was 10%/50%).
    SPY mean (0.5517) → (0.70 - 0.5517) / 0.55 = 0.2696 → 20 × 0.2696 = 5.39 → 5 pts.
    """
    from studies.spy_beater_hunt.scoring import compute_mdd_points

    pts = compute_mdd_points(mean_mdd=0.5517)
    assert pts == 5


def test_scoring_mdd_above_ceiling_zero():
    """MDD ≥ 70% → 0 points (post-refactor ceiling)."""
    from studies.spy_beater_hunt.scoring import compute_mdd_points

    assert compute_mdd_points(mean_mdd=0.75) == 0


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


# ---------------------------------------------------------------------------
# TMFSIM routing in _resolve_tickers_to_returns (HFEA backbone)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Vol-target engine (Carver canonical, [systematic_trading, ch.10])
# ---------------------------------------------------------------------------


def test_realized_vol_formula():
    """Annualised rolling std with sqrt(252) scaling (default annualization)."""
    from studies.spy_beater_hunt.vol_target_engine import realized_vol

    returns = pd.Series(
        [0.01, 0.02, -0.01, 0.005, 0.0],
        index=pd.date_range("2024-01-02", periods=5, freq="B"),
    )
    rv = realized_vol(returns, window=3, annualization=252)

    expected = float(np.std([0.01, 0.02, -0.01], ddof=1)) * np.sqrt(252)
    assert abs(rv.iloc[2] - expected) < 1e-10
    assert pd.isna(rv.iloc[0])  # window not yet filled
    assert pd.isna(rv.iloc[1])


def test_vol_target_weight_no_peek():
    """Weight at time t is shifted by lag_days from the realised vol input."""
    from studies.spy_beater_hunt.vol_target_engine import vol_target_weight

    rv = pd.Series(
        [0.20, 0.10, 0.40, 0.20],
        index=pd.date_range("2024-01-02", periods=4, freq="B"),
    )
    w = vol_target_weight(
        rv, target_vol_annual=0.20, underlying_factor=1.0,
        weight_min=0.0, weight_max=1.0, lag_days=1,
    )

    # First day: NaN (lagged) → fills weight_min=0.0
    assert w.iloc[0] == 0.0
    # Day 1 reflects rv from day 0 = 0.20 → weight = 0.20/0.20 = 1.0
    assert abs(w.iloc[1] - 1.0) < 1e-10
    # Day 2 reflects rv from day 1 = 0.10 → raw 2.0, clipped to 1.0
    assert abs(w.iloc[2] - 1.0) < 1e-10
    # Day 3 reflects rv from day 2 = 0.40 → 0.20/0.40 = 0.5
    assert abs(w.iloc[3] - 0.5) < 1e-10


def test_vol_target_weight_underlying_factor():
    """Weight inversely scales with underlying_factor (SPY-equivalent target)."""
    from studies.spy_beater_hunt.vol_target_engine import vol_target_weight

    rv = pd.Series([0.16] * 5, index=pd.date_range("2024-01-02", periods=5, freq="B"))

    # Factor 1 (raw SPY): weight = 0.16/0.16 = 1.0
    w_spy = vol_target_weight(
        rv, target_vol_annual=0.16, underlying_factor=1.0, lag_days=1
    )
    assert abs(w_spy.iloc[2] - 1.0) < 1e-10

    # Factor 2 (SSO): weight = 0.16/(2*0.16) = 0.5
    w_sso = vol_target_weight(
        rv, target_vol_annual=0.16, underlying_factor=2.0, lag_days=1
    )
    assert abs(w_sso.iloc[2] - 0.5) < 1e-10

    # Factor 3 (UPRO): weight = 0.16/(3*0.16) = 1/3
    w_upro = vol_target_weight(
        rv, target_vol_annual=0.16, underlying_factor=3.0, lag_days=1
    )
    assert abs(w_upro.iloc[2] - 1.0 / 3.0) < 1e-10


def test_vol_target_weight_clipping():
    """Weight clipped to [weight_min, weight_max]."""
    from studies.spy_beater_hunt.vol_target_engine import vol_target_weight

    # Very low rv → high raw weight, clipped UP to weight_max
    rv_low = pd.Series([0.05] * 5, index=pd.date_range("2024-01-02", periods=5, freq="B"))
    w = vol_target_weight(
        rv_low, target_vol_annual=0.20, underlying_factor=1.0,
        weight_min=0.0, weight_max=1.0, lag_days=1,
    )
    # Raw = 0.20/0.05 = 4.0 → clipped to 1.0
    assert abs(w.iloc[2] - 1.0) < 1e-10

    # Very high rv → low raw weight, clipped DOWN to weight_min if specified
    rv_high = pd.Series([0.80] * 5, index=pd.date_range("2024-01-02", periods=5, freq="B"))
    w_floor = vol_target_weight(
        rv_high, target_vol_annual=0.20, underlying_factor=1.0,
        weight_min=0.5, weight_max=1.0, lag_days=1,
    )
    # Raw = 0.20/0.80 = 0.25 → clipped UP to weight_min=0.5
    assert abs(w_floor.iloc[2] - 0.5) < 1e-10


def test_vol_target_strategy_returns_formula():
    """Strategy returns = weight × underlying + (1 − weight) × cash."""
    from studies.spy_beater_hunt.vol_target_engine import vol_target_strategy_returns

    idx = pd.date_range("2024-01-02", periods=4, freq="B")
    underlying = pd.Series([0.01, 0.02, -0.01, 0.005], index=idx)
    cash = pd.Series([0.0001, 0.0001, 0.0001, 0.0001], index=idx)
    weight = pd.Series([0.5, 1.0, 0.0, 0.75], index=idx)

    result = vol_target_strategy_returns(underlying, cash, weight)

    expected = [
        0.5 * 0.01 + 0.5 * 0.0001,
        1.0 * 0.02 + 0.0 * 0.0001,
        0.0 * -0.01 + 1.0 * 0.0001,
        0.75 * 0.005 + 0.25 * 0.0001,
    ]
    np.testing.assert_allclose(result.values, expected, atol=1e-10)


def test_vol_target_strategy_returns_alignment():
    """Aligns inputs on intersection of indices (drops misaligned dates)."""
    from studies.spy_beater_hunt.vol_target_engine import vol_target_strategy_returns

    underlying = pd.Series(
        [0.01, 0.02, 0.03],
        index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
    )
    cash = pd.Series(
        [0.0001, 0.0001],
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    weight = pd.Series(
        [0.5, 1.0],
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )

    result = vol_target_strategy_returns(underlying, cash, weight)
    # Only 2024-01-02 and 2024-01-03 have all three series.
    assert len(result) == 2


def test_returns_from_spec_routes_vol_target_type():
    """``returns_from_spec`` dispatches type='vol_target' to the engine."""
    from studies.spy_beater_hunt.run_iter import returns_from_spec

    spec = {
        "type": "vol_target",
        "underlying_weights": {"SSOSIM": 1.0},
        "cash_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "target_vol_annual": 0.20,
        "underlying_leverage_factor": 2.0,
        "vol_window": 60,
        "vol_lag_days": 1,
        "weight_min": 0.0,
        "weight_max": 1.0,
    }
    returns = returns_from_spec(spec, "spy_real")
    assert isinstance(returns, pd.Series)
    # spy_real spans 2003-08-20 → 2026-04-14 (~22.7y); vol-target consumes 60d
    # warm-up plus 1 trading day lag, so length should be 5500+ daily bars.
    assert len(returns) > 5_000
    # Ann std should be in a sensible band for a 1.25× SPY-effective strategy
    ann_std = float(returns.std() * (252 ** 0.5))
    assert 0.10 < ann_std < 0.30


def test_resolve_tickers_routes_tmfsim_to_synth():
    """`portfolio_returns_from_config` must route TMFSIM to tmf_synth_returns_from_cache.

    iter 008 introduces HFEA (UPRO + TMF). TMFSIM is NOT in the testfolio
    parquet cache; the synth lives at studies.long_term_portfolio.synths
    .tmf_synth_returns_from_cache (3× TLT − 1.5%/y daily-reset decay).
    The dispatcher in studies.long_term_portfolio.run_iter must wire
    'TMFSIM' to that synth — without it, HFEA configs raise FileNotFoundError.
    """
    from studies.long_term_portfolio.run_iter import portfolio_returns_from_config

    # 100% TMFSIM portfolio: returns equal the synth output (within window).
    returns = portfolio_returns_from_config({"TMFSIM": 1.0}, "lh_56y")
    assert isinstance(returns, pd.Series)
    assert len(returns) > 8000  # 1986+ ~40y, ~252/y trading days
    # Std is bounded by 3× TLT vol (~12-15% → 36-45% annualised)
    ann_std = float(returns.std() * (252 ** 0.5))
    assert 0.30 < ann_std < 0.50

    # 55/45 HFEA: weights sum to 1.0, no error raised.
    hfea_returns = portfolio_returns_from_config(
        {"UPROSIM": 0.55, "TMFSIM": 0.45}, "lh_56y"
    )
    assert isinstance(hfea_returns, pd.Series)
    assert len(hfea_returns) > 8000


# ---------------------------------------------------------------------------
# Iter 018 — meta-portfolio "blend" spec type
# ---------------------------------------------------------------------------


def test_blend_spec_50_50_static_constituents():
    """blend type: weighted sum of two static constituents at daily-return level.

    Iter 018 H1 META-ENSEMBLE introduces "blend" as a 4th spec type alongside
    static / lrs / vol_target. A blend composes daily portfolio returns from
    multiple sub-specs, weighted at the strategy level (not asset level).

    On dates where both constituents have data, blend_t = sum_i w_i * r_i_t.
    """
    from studies.spy_beater_hunt.run_iter import returns_from_spec

    spec_a = {"type": "static", "weights": {"SPYSIM": 1.0}}
    spec_b = {"type": "static", "weights": {"IEFSIM": 1.0}}
    blend_spec = {
        "type": "blend",
        "constituents": [
            {"weight": 0.5, "spec": spec_a},
            {"weight": 0.5, "spec": spec_b},
        ],
    }

    r_a = returns_from_spec(spec_a, "spy_real")
    r_b = returns_from_spec(spec_b, "spy_real")
    r_blend = returns_from_spec(blend_spec, "spy_real")

    assert isinstance(r_blend, pd.Series)
    aligned = pd.concat({"a": r_a, "b": r_b, "blend": r_blend}, axis=1).dropna()
    expected = 0.5 * aligned["a"] + 0.5 * aligned["b"]
    diff = (aligned["blend"] - expected).abs().max()
    assert diff < 1e-10, f"blend mismatch: max abs diff {diff}"


def test_blend_spec_validates_weight_sum():
    """blend type must validate constituent weights sum to 1.0 (sanity guard)."""
    from studies.spy_beater_hunt.run_iter import returns_from_spec

    bad_spec = {
        "type": "blend",
        "constituents": [
            {"weight": 0.4, "spec": {"type": "static", "weights": {"SPYSIM": 1.0}}},
            {"weight": 0.4, "spec": {"type": "static", "weights": {"IEFSIM": 1.0}}},
        ],
    }
    with pytest.raises(ValueError, match="must sum to 1.0"):
        returns_from_spec(bad_spec, "spy_real")


def test_blend_spec_supports_nested_lrs_constituent():
    """blend type composes LRS sub-specs (meta-portfolio of strategies).

    Iter 018 specifically blends iter-006 A2 (LRS QQQ-gated) with iter-017
    G2 IEF (LRS SPY-gated) and iter-015 F1 stack (static always-on). This
    test verifies that nested LRS constituents resolve via returns_from_spec
    recursion.
    """
    from studies.spy_beater_hunt.run_iter import returns_from_spec

    a2_spec = {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {"TQQQSIM": 0.5, "QLDSIM": 0.5},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "lag_days": 1,
    }
    f1_spec = {
        "type": "static",
        "weights": {"SPYSIM": 0.5, "TLTSIM": 0.5},
    }
    blend_spec = {
        "type": "blend",
        "constituents": [
            {"weight": 0.6, "spec": a2_spec},
            {"weight": 0.4, "spec": f1_spec},
        ],
    }

    r = returns_from_spec(blend_spec, "spy_real")
    assert isinstance(r, pd.Series)
    assert len(r) > 5_000
    ann_std = float(r.std() * (252 ** 0.5))
    assert 0.05 < ann_std < 0.50, f"blended ann std out of range: {ann_std}"


# ---------------------------------------------------------------------------
# Net-of-tax layer (Lei 14.754/2023 — DARF anual)
# ---------------------------------------------------------------------------


def test_classify_for_tax_per_spec_type():
    """static -> buy_hold; lrs/vol_target -> annual_realize; blend inherits."""
    from studies.spy_beater_hunt.tax_layer import (
        TaxClassification,
        classify_for_tax,
    )

    assert classify_for_tax({"type": "static"}) == TaxClassification.BUY_HOLD
    assert classify_for_tax({"type": "lrs"}) == TaxClassification.ANNUAL_REALIZE
    assert classify_for_tax({"type": "vol_target"}) == TaxClassification.ANNUAL_REALIZE

    # blend with all-static constituents -> buy_hold
    blend_static = {
        "type": "blend",
        "constituents": [{"spec": {"type": "static"}}, {"spec": {"type": "static"}}],
    }
    assert classify_for_tax(blend_static) == TaxClassification.BUY_HOLD

    # blend with any non-static constituent -> annual_realize
    blend_mixed = {
        "type": "blend",
        "constituents": [{"spec": {"type": "static"}}, {"spec": {"type": "lrs"}}],
    }
    assert classify_for_tax(blend_mixed) == TaxClassification.ANNUAL_REALIZE


def test_net_returns_buy_hold_drag_smaller_than_annual_realize():
    """For positive constant returns, buy_hold drag < annual_realize drag.

    Rationale: buy_hold defers all DARF to terminal liquidation -> tax-deferred
    compounding benefit. annual_realize pays DARF every year -> loses
    compounding on the tax money.
    """
    from studies.spy_beater_hunt.tax_layer import net_returns_from_spec

    n_days = 10 * 252
    daily = (1.12) ** (1.0 / 252.0) - 1.0
    idx = pd.date_range("2010-01-04", periods=n_days, freq="B")
    gross = pd.Series([daily] * n_days, index=idx)

    static_spec = {"type": "static", "weights": {"X": 1.0}}
    lrs_spec = {"type": "lrs", "on_weights": {}, "off_weights": {}}

    _, summary_static = net_returns_from_spec(static_spec, gross)
    _, summary_lrs = net_returns_from_spec(lrs_spec, gross)

    assert summary_static.classification == "buy_hold"
    assert summary_lrs.classification == "annual_realize"
    assert summary_static.drag_pct_pts > 0  # any tax > 0 drag
    assert summary_lrs.drag_pct_pts > summary_static.drag_pct_pts
    # Sanity: 10y / 12% gross / 15% DARF -> drag should land in [0.5, 3.0] pp
    assert 0.5 < summary_static.drag_pct_pts < 1.5
    assert 1.0 < summary_lrs.drag_pct_pts < 3.0


def test_net_returns_zero_gain_zero_darf():
    """If gross returns sum to zero gain, terminal DARF is zero."""
    from studies.spy_beater_hunt.tax_layer import net_returns_from_spec

    n_days = 252
    # alternating +1% / -1% (approximately zero net)
    idx = pd.date_range("2020-01-02", periods=n_days, freq="B")
    arr = np.array([0.01 if i % 2 == 0 else -0.01 for i in range(n_days)])
    gross = pd.Series(arr, index=idx)

    static_spec = {"type": "static", "weights": {"X": 1.0}}
    _, summary = net_returns_from_spec(static_spec, gross)

    assert summary.terminal_darf == 0.0
    assert summary.total_darf_paid == 0.0
