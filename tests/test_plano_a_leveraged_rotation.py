"""Tests for V2-L2 Plano A Leveraged Rotation strategy.

Covers regime signal correctness, leverage application, swap cost on
the levered notional, off-regime asset switching, and intersection-
calendar handling.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.plano_a_leveraged_rotation import (
    PlanoALeveragedRotationConfig,
    compute_regime_signal,
    simulate_plano_a_rotation,
)


def _weekday_series(
    start: str, n: int, start_price: float = 100.0, drift: float = 0.0005
) -> pd.Series:
    idx = pd.bdate_range(start=start, periods=n, freq="B")
    values = start_price * (1.0 + drift) ** np.arange(n)
    return pd.Series(values, index=idx, name="close")


def _panel(series_map: dict[str, pd.Series]) -> dict[str, pd.DataFrame]:
    return {t: s.to_frame("close") for t, s in series_map.items()}


def test_regime_signal_sma200_strict_cross():
    """SMA200: close above MA → ON, below → OFF, first 199 bars NaN."""
    # 300 bars of slightly-up drift → all post-warmup ON.
    px = _weekday_series("2010-01-04", n=300, drift=0.001)
    signal = compute_regime_signal(px, kind="sma200")
    assert signal.iloc[:199].isna().all()
    assert (signal.iloc[199:] == "ON").all()


def test_regime_signal_ema100_faster_warmup():
    """EMA100 uses min_periods=100 → first 99 bars NaN."""
    px = _weekday_series("2010-01-04", n=200, drift=0.001)
    signal = compute_regime_signal(px, kind="ema100")
    assert signal.iloc[:99].isna().all()
    assert signal.iloc[99:].notna().all()


def test_regime_signal_lrs_composite():
    """LRS votes across {SMA100, SMA200, EMA100}; strict rise → ON post-warmup."""
    px = _weekday_series("2010-01-04", n=250, drift=0.001)
    signal = compute_regime_signal(px, kind="lrs")
    # Warmup ends when slowest (SMA200) is ready.
    assert signal.iloc[199:].notna().all()
    assert (signal.iloc[199:] == "ON").all()


def test_regime_signal_downtrend_flips_off():
    """Sustained downtrend → signal stays OFF post-warmup."""
    px = _weekday_series("2010-01-04", n=300, drift=-0.0005)
    signal = compute_regime_signal(px, kind="sma200")
    tail = signal.iloc[250:]
    assert (tail == "OFF").sum() > 40, (
        f"downtrend should yield mostly OFF; got {tail.value_counts().to_dict()}"
    )


def test_leverage_applied_when_risk_on():
    """On risk-on days, daily portfolio return ≈ L * asset_return (ignoring tiny costs)."""
    spy = _weekday_series("2010-01-04", n=260, drift=0.001)
    qqq = _weekday_series("2010-01-04", n=260, drift=0.001)
    cfg = PlanoALeveragedRotationConfig(
        regime_signal="ema100",
        leverage=2.0,
        off_regime_asset="cash",
        risk_on_tickers=("SPY", "QQQ"),
    )
    result = simulate_plano_a_rotation(_panel({"SPY": spy, "QQQ": qqq}), cfg)
    # After EMA100 warms up (~100 bars), both tickers go ON.
    # Each asset's spot return is ~0.1%/day → 2x leverage → ~0.2%/day
    # (minus swap, which is ~-0.5bps/day on levered notional = -0.0005%/day net ≈ neg).
    tail = result.daily_returns.iloc[150:]
    mean_daily = float(tail.mean())
    # Expected ~0.002 * 2 = 0.004 minus small costs; tolerate a broad band.
    assert 0.0015 < mean_daily < 0.0030, (
        f"mean daily ret with 2x leverage ≈ 0.2% expected, got {mean_daily:.4f}"
    )


def test_swap_drag_negative_when_long():
    """Swap is negative on levered longs — `cum_swap_pct` < 0 after any ON block."""
    spy = _weekday_series("2010-01-04", n=260, drift=0.001)
    qqq = _weekday_series("2010-01-04", n=260, drift=0.001)
    cfg = PlanoALeveragedRotationConfig(
        regime_signal="ema100",
        leverage=2.0,
        off_regime_asset="cash",
        risk_on_tickers=("SPY", "QQQ"),
        swap_daily_pct_long=-0.005,
    )
    result = simulate_plano_a_rotation(_panel({"SPY": spy, "QQQ": qqq}), cfg)
    assert result.cum_swap_pct < 0


def test_off_regime_asset_requires_panel():
    """TLT/GLD off-regime must be supplied via off_regime_panel."""
    spy = _weekday_series("2010-01-04", n=260)
    qqq = _weekday_series("2010-01-04", n=260)
    cfg = PlanoALeveragedRotationConfig(
        off_regime_asset="tlt",
        risk_on_tickers=("SPY", "QQQ"),
    )
    with pytest.raises(ValueError, match="off_regime_panel required"):
        simulate_plano_a_rotation(_panel({"SPY": spy, "QQQ": qqq}), cfg)


def test_off_regime_tlt_contributes_to_return():
    """Off-regime TLT return shows up when an asset is OFF.

    Build: SPY downtrend (OFF regime), QQQ downtrend (OFF), TLT uptrend.
    Portfolio should pick up TLT return on OFF days, not cash.
    """
    spy = _weekday_series("2010-01-04", n=260, drift=-0.001)
    qqq = _weekday_series("2010-01-04", n=260, drift=-0.001)
    tlt = _weekday_series("2010-01-04", n=260, drift=0.0005)
    cfg = PlanoALeveragedRotationConfig(
        regime_signal="ema100",
        leverage=2.0,
        off_regime_asset="tlt",
        risk_on_tickers=("SPY", "QQQ"),
    )
    result = simulate_plano_a_rotation(
        _panel({"SPY": spy, "QQQ": qqq}),
        cfg,
        off_regime_panel=_panel({"tlt": tlt}),
    )
    # With both risk-on OFF post-warmup, weights collapse to 100% TLT.
    tail_weights = result.weights.iloc[-10:]
    assert (tail_weights["SPY"] == 0).all()
    assert (tail_weights["QQQ"] == 0).all()
    assert (tail_weights["off_tlt"] > 0.99).all()
    # Mean daily return should track TLT drift (~0.0005).
    mean_tail = float(result.daily_returns.iloc[-20:].mean())
    assert 0.0001 < mean_tail < 0.001


def test_config_validation():
    """Invalid config params raise ValueError."""
    with pytest.raises(ValueError, match="regime_signal"):
        PlanoALeveragedRotationConfig(regime_signal="invalid")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="leverage"):
        PlanoALeveragedRotationConfig(leverage=-1.0)
    with pytest.raises(ValueError, match="off_regime_asset"):
        PlanoALeveragedRotationConfig(off_regime_asset="bonds")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="risk_on_tickers"):
        PlanoALeveragedRotationConfig(risk_on_tickers=())


def test_roundtrip_cost_pct_formula():
    """round_trip_cost_pct = (2*spread_half + commission + slippage) / 1e4."""
    cfg = PlanoALeveragedRotationConfig(
        spread_half_bps=2.0,
        commission_round_trip_bps=6.6,
        slippage_bps_round_trip=3.0,
    )
    expected = (2 * 2.0 + 6.6 + 3.0) / 10_000.0
    assert cfg.round_trip_cost_pct == pytest.approx(expected)


def test_swap_daily_frac_percent_to_fraction():
    """swap_daily_pct_long is a percent; swap_daily_frac = pct/100."""
    cfg = PlanoALeveragedRotationConfig(swap_daily_pct_long=-0.005)
    assert cfg.swap_daily_frac == pytest.approx(-0.00005)


def test_longest_window_intersection_weekdays_only():
    """Common calendar is weekday-only intersection of inputs."""
    spy = _weekday_series("2010-01-04", n=260)  # weekdays only
    # QQQ has a longer history starting earlier.
    qqq = _weekday_series("2009-01-05", n=520)
    cfg = PlanoALeveragedRotationConfig(
        regime_signal="ema100",
        leverage=2.0,
        risk_on_tickers=("SPY", "QQQ"),
    )
    result = simulate_plano_a_rotation(_panel({"SPY": spy, "QQQ": qqq}), cfg)
    # Intersection ⇒ result calendar is bounded by SPY's shorter index.
    assert result.daily_returns.index.min() >= pd.Timestamp("2010-01-04")
    assert all(d.dayofweek < 5 for d in result.daily_returns.index)
