"""Tests for V2-L1 TSMOM multi-asset simulator.

Covers the weekday-only calendar regression (weekend crypto/FX bars
used to pollute ``shift(lookback)`` semantics for equity assets and
freeze the portfolio flat post-2014) and basic signal/cost sanity.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.tsmom_multi_asset import (
    DEFAULT_ROUND_TRIP_BPS_BY_CLASS,
    TSMOMMultiAssetConfig,
    default_asset_class,
    simulate_tsmom_multi_asset,
)


def _weekday_series(
    start: str, n: int, start_price: float = 100.0, drift: float = 0.0005
) -> pd.Series:
    idx = pd.bdate_range(start=start, periods=n, freq="B")
    values = start_price * (1.0 + drift) ** np.arange(n)
    return pd.Series(values, index=idx, name="close")


def _all_days_series(
    start: str, n: int, start_price: float = 100.0, drift: float = 0.001
) -> pd.Series:
    idx = pd.date_range(start=start, periods=n, freq="D")
    values = start_price * (1.0 + drift) ** np.arange(n)
    return pd.Series(values, index=idx, name="close")


def _panel(series_map: dict[str, pd.Series]) -> dict[str, pd.DataFrame]:
    return {t: s.to_frame("close") for t, s in series_map.items()}


def test_master_calendar_drops_weekend_bars_from_crypto():
    """Regression: weekends in a crypto series must not leak into the
    master index; otherwise equity ``shift(lookback)`` lands on NaN
    weekend bars and freezes the portfolio flat.
    """
    spy = _weekday_series("2010-01-04", n=400)
    btc = _all_days_series("2010-01-04", n=560)  # includes weekends

    config = TSMOMMultiAssetConfig(
        lookback_days=21,
        vol_target_annual=0.10,
        vol_lookback_days=60,
        min_active_instruments=1,
    )
    result = simulate_tsmom_multi_asset(
        _panel({"SPY": spy, "BTCUSD": btc}), config
    )

    # Every bar in the returned index must be a weekday.
    assert all(d.dayofweek < 5 for d in result.daily_returns.index)
    # The portfolio must actually trade past the warmup (regression: used
    # to stay flat for most of the post-2014 window).
    post_warmup = result.daily_returns.iloc[80:]
    assert (post_warmup != 0.0).sum() > 10, (
        "portfolio stayed flat post-warmup — weekday calendar fix broken"
    )


def test_positive_drift_triggers_long_signal():
    """With a single asset and strictly upward drift, the binary TSMOM
    signal should go long after warmup and stay long (vol is positive
    and past return is positive every month-end)."""
    spy = _weekday_series("2010-01-04", n=500, drift=0.001)
    efa = _weekday_series("2010-01-04", n=500, drift=0.0005)
    iwm = _weekday_series("2010-01-04", n=500, drift=0.0008)

    config = TSMOMMultiAssetConfig(
        lookback_days=21,
        vol_target_annual=0.10,
        vol_lookback_days=60,
        min_active_instruments=3,
    )
    result = simulate_tsmom_multi_asset(
        _panel({"SPY": spy, "EFA": efa, "IWM": iwm}), config
    )

    # After the warmup bar, all three assets carry positive weight on
    # at least one rebalance.
    last_rebalance = result.rebalance_dates[-1]
    w = result.weights.loc[last_rebalance]
    assert (w > 0).sum() == 3
    # Portfolio compounded positively — monotone drift is a winning
    # regime for a binary long-only TSMOM.
    assert result.equity.iloc[-1] > 1.0


def test_below_min_active_portfolio_is_flat():
    """If only 1 asset passes warmup but ``min_active_instruments=3``,
    the portfolio must stay flat (zero daily return on rebalance bars).
    """
    spy = _weekday_series("2010-01-04", n=500)
    config = TSMOMMultiAssetConfig(
        lookback_days=21,
        vol_target_annual=0.10,
        vol_lookback_days=60,
        min_active_instruments=3,
    )
    result = simulate_tsmom_multi_asset(_panel({"SPY": spy}), config)

    # Exactly zero weight across the entire run (min_active not met).
    assert (result.weights.to_numpy() == 0.0).all()
    # No costs accumulated — no trades happened.
    assert result.cum_cost_pct == 0.0


def test_transaction_cost_applied_on_weight_change():
    """A weight change from 0 → positive must incur round-trip cost
    proportional to the asset-class bps and the delta."""
    spy = _weekday_series("2010-01-04", n=400, drift=0.001)
    efa = _weekday_series("2010-01-04", n=400, drift=0.001)
    iwm = _weekday_series("2010-01-04", n=400, drift=0.001)

    config = TSMOMMultiAssetConfig(
        lookback_days=21,
        vol_target_annual=0.10,
        vol_lookback_days=60,
        min_active_instruments=3,
    )
    result = simulate_tsmom_multi_asset(
        _panel({"SPY": spy, "EFA": efa, "IWM": iwm}), config
    )

    assert result.cum_cost_pct > 0.0
    # Sanity upper bound: no single rebalance can turn over more than
    # gross leverage cap × ETF bps / 10000.
    max_single_turnover = config.max_leverage_per_asset * (
        DEFAULT_ROUND_TRIP_BPS_BY_CLASS["etf"] / 10_000.0
    )
    assert result.cum_cost_pct < max_single_turnover * result.n_rebalances


def test_default_asset_class_classification():
    assert default_asset_class("SPY") == "etf"
    assert default_asset_class("GLD") == "commodity_etf"
    assert default_asset_class("BTCUSD") == "crypto"
    assert default_asset_class("EURUSD") == "forex"
    assert default_asset_class("eurusd") == "forex"


def test_config_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        TSMOMMultiAssetConfig(lookback_days=1, vol_target_annual=0.10)
    with pytest.raises(ValueError):
        TSMOMMultiAssetConfig(lookback_days=21, vol_target_annual=0.0)
    with pytest.raises(ValueError):
        TSMOMMultiAssetConfig(
            lookback_days=21, vol_target_annual=0.10, vol_lookback_days=5
        )
    with pytest.raises(ValueError):
        TSMOMMultiAssetConfig(
            lookback_days=21, vol_target_annual=0.10, swap_daily_bps=-1.0
        )
