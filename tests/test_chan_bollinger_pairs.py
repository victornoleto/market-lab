"""Tests for ChanBollingerPairsStrategy [algo_trading_chan, ch.3]."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.chan_bollinger_pairs import (
    ChanBollingerPairsStrategy,
)


def _synth_ohlcv(
    n: int = 2000,
    start: str = "2022-01-03 09:30",
    freq: str = "1h",
    seed: int = 0,
) -> pd.DataFrame:
    """Build a synthetic OHLCV frame with index of length ``n``."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start=start, periods=n, freq=freq)
    close = 100 + np.cumsum(rng.normal(0, 0.1, n))
    return pd.DataFrame(
        {
            "open": close,
            "high": close + 0.05,
            "low": close - 0.05,
            "close": close,
            "volume": 1_000_000,
            "adj_close": close,
        },
        index=idx,
    )


def test_instantiation_with_both_symbols_succeeds():
    # Cointegrated OU synth (same pattern as test_ols_recovers_known_beta):
    # y = 2.5·x + OU noise with half-life ≈ 20 bars → OLS + OU succeed.
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
        long_symbol="GLD",
        short_symbol="SLV",
    )
    assert strat.long_symbol == "GLD"
    assert strat.short_symbol == "SLV"


def test_missing_long_symbol_raises_keyerror():
    df = _synth_ohlcv(seed=1)
    with pytest.raises(KeyError, match="GLD"):
        ChanBollingerPairsStrategy(
            data={"SLV": df},
            long_symbol="GLD",
            short_symbol="SLV",
        )


def test_missing_short_symbol_raises_keyerror():
    df = _synth_ohlcv(seed=1)
    with pytest.raises(KeyError, match="SLV"):
        ChanBollingerPairsStrategy(
            data={"GLD": df},
            long_symbol="GLD",
            short_symbol="SLV",
        )


def test_misaligned_timestamps_raises_valueerror():
    df_long = _synth_ohlcv(n=2000, start="2022-01-03 09:30", seed=1)
    df_short = _synth_ohlcv(n=2000, start="2022-01-04 09:30", seed=2)
    with pytest.raises(ValueError, match="timestamps"):
        ChanBollingerPairsStrategy(
            data={"GLD": df_long, "SLV": df_short},
            long_symbol="GLD",
            short_symbol="SLV",
        )


def test_ols_recovers_known_beta():
    """Synthetic pair with y = 2.5 x + OU noise → β ≈ 2.5."""
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    # OU noise around 2.5·x (mean-reverting spread): half-life ≈ 20 bars
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
    )
    assert abs(strat._beta - 2.5) < 0.1, f"β recovered = {strat._beta}"


def test_ou_recovers_known_half_life():
    """OU synth with λ = -log(2)/20 → half-life bars ≈ 20."""
    rng = np.random.default_rng(7)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    target_hl = 20
    lam = -np.log(2) / target_hl
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
    )
    # Allow a ±50% envelope — OU estimation is noisy on finite samples.
    assert 10 <= strat._half_life_bars <= 40, (
        f"half-life recovered = {strat._half_life_bars}"
    )


def test_ou_rejects_random_walk():
    """Pure random walk spread (no mean reversion) → RuntimeError."""
    rng = np.random.default_rng(99)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.1, n))
    y = 50 + np.cumsum(rng.normal(0, 0.1, n))  # independent RW — no cointegration
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    with pytest.raises(RuntimeError, match=r"(cointegrated|t[-_]stat|half[-_]life)"):
        ChanBollingerPairsStrategy(
            data={"GLD": df_long, "SLV": df_short},
        )


def test_half_life_clamp_rejects_too_slow():
    """OU synth with half-life = 200 bars (> 60 max) → RuntimeError."""
    rng = np.random.default_rng(13)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 200.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    with pytest.raises(RuntimeError, match=r"half[-_]life"):
        ChanBollingerPairsStrategy(
            data={"GLD": df_long, "SLV": df_short},
        )


def test_precomputed_indicators_present_and_shaped():
    """After __post_init__, indicators must be precomputed with shape = len(data)."""
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
        lookback_multiplier=2,
    )
    ind = strat._indicators
    for col in ("spread", "spread_ma", "spread_std", "zscore"):
        assert col in ind.columns, f"missing column {col}"
        assert len(ind) == n, f"indicator len={len(ind)} != data len={n}"
    # After enough warmup (2× half_life + 1), z-score must be finite and centered
    warmup = 2 * strat._half_life_bars + 1
    z_tail = ind["zscore"].iloc[warmup:].dropna()
    assert len(z_tail) > 0
    assert abs(z_tail.mean()) < 0.5, f"z-score mean = {z_tail.mean()}"
    # z-score std on well-formed pair should be close to 1 (by construction)
    assert 0.5 < z_tail.std() < 1.5, f"z-score std = {z_tail.std()}"


from ai_trade.backtest.engine.execution import Bar
from ai_trade.backtest.engine.portfolio import Portfolio


def _make_strategy_with_z(
    z_series: list[float],
    *,
    entry_z: float = 1.0,
    start_ts: str = "2023-01-03 09:30",
):
    """Build a strategy whose precomputed zscore matches ``z_series`` exactly.

    We short-circuit the fit by feeding crafted data: GLD - β·SLV = z_series
    scaled + windowed so the rolling zscore sits at the requested values.
    For surgical unit testing, we instead patch _indicators post-hoc.
    """
    # n must be large enough to (a) pass cointegration fit on the training
    # slice (train_bars=1250) and (b) cover June 2023 timestamps used by
    # the session-gate tests. 2023-01-03 09:30 + 6000h ≈ 2023-09-10.
    n = max(len(z_series) + 100, 6000)
    idx = pd.date_range(start_ts, periods=n, freq="1h")
    rng = np.random.default_rng(0)
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    df_long = pd.DataFrame(
        {"open": y, "high": y, "low": y, "close": y, "volume": 1e6, "adj_close": y},
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
        entry_z=entry_z,
    )
    # Patch the last len(z_series) rows of zscore for deterministic tests
    tail_start = n - len(z_series)
    strat._indicators.loc[idx[tail_start:], "zscore"] = z_series
    return strat, idx, tail_start


def test_entry_long_spread_on_crossing_below_minus_entry_z():
    """z crosses from -0.9 to -1.1 (entry_z=1.0) → 2 orders."""
    strat, idx, tail_start = _make_strategy_with_z(
        [-0.9, -1.1], entry_z=1.0, start_ts="2023-01-03 09:30"
    )
    # crossing happens at idx[tail_start + 1]
    ts = idx[tail_start + 1]
    bar_long = Bar(
        symbol="GLD", timestamp=ts,
        open=180.0, high=180.5, low=179.5, close=180.0, volume=1e6,
    )
    bar_short = Bar(
        symbol="SLV", timestamp=ts,
        open=72.0, high=72.3, low=71.7, close=72.0, volume=1e6,
    )
    pf = Portfolio(initial_cash=100_000.0)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, {})
    assert len(orders) == 2
    long_order = next(o for o in orders if o.symbol == "GLD")
    short_order = next(o for o in orders if o.symbol == "SLV")
    assert long_order.side == "buy"
    assert short_order.side == "sell"
    # sizing: long_leg = notional / (price_long + β·price_short); short_leg = β × long_leg
    total_notional = 100_000.0 * strat.risk_pct_of_equity
    expected_long = total_notional / (180.0 + strat._beta * 72.0)
    expected_short = strat._beta * expected_long
    assert abs(long_order.volume - expected_long) / expected_long < 1e-6
    assert abs(short_order.volume - expected_short) / expected_short < 1e-6


def test_entry_short_spread_on_crossing_above_plus_entry_z():
    """z crosses from +0.9 to +1.1 → 2 orders (sell GLD, buy SLV)."""
    strat, idx, tail_start = _make_strategy_with_z(
        [0.9, 1.1], entry_z=1.0, start_ts="2023-01-03 09:30"
    )
    ts = idx[tail_start + 1]
    bar_long = Bar("GLD", ts, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts, 72.0, 72.3, 71.7, 72.0, 1e6)
    pf = Portfolio(initial_cash=100_000.0)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, {})
    sides = {o.symbol: o.side for o in orders}
    assert sides == {"GLD": "sell", "SLV": "buy"}


def test_entry_ignored_after_hour_cutoff_14():
    """Same crossing but at 15:30 local → no orders."""
    strat, idx, tail_start = _make_strategy_with_z(
        [-0.9, -1.1], entry_z=1.0, start_ts="2023-01-03 09:30"
    )
    # Find an idx at 15:30 (or later); patch zscore there
    late_ts = pd.Timestamp("2023-06-15 15:30")
    late_idx_pos = strat._indicators.index.get_indexer([late_ts], method="nearest")[0]
    strat._indicators.iloc[late_idx_pos - 1, strat._indicators.columns.get_loc("zscore")] = -0.9
    strat._indicators.iloc[late_idx_pos, strat._indicators.columns.get_loc("zscore")] = -1.1
    ts = strat._indicators.index[late_idx_pos]
    bar_long = Bar("GLD", ts, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts, 72.0, 72.3, 71.7, 72.0, 1e6)
    pf = Portfolio(initial_cash=100_000.0)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, {})
    assert orders == [], f"expected no orders at 15:30, got {orders}"


def test_entry_ignored_friday_after_no_entry_hour_13():
    """Friday 13:30 crossing → no orders (weekend-swap protection)."""
    strat, idx, tail_start = _make_strategy_with_z(
        [-0.9, -1.1], entry_z=1.0, start_ts="2023-01-03 09:30"
    )
    # Friday 2023-06-16 at 13:30
    friday_ts = pd.Timestamp("2023-06-16 13:30")
    pos = strat._indicators.index.get_indexer([friday_ts], method="nearest")[0]
    strat._indicators.iloc[pos - 1, strat._indicators.columns.get_loc("zscore")] = -0.9
    strat._indicators.iloc[pos, strat._indicators.columns.get_loc("zscore")] = -1.1
    ts = strat._indicators.index[pos]
    assert ts.weekday() == 4, f"expected Friday, got weekday={ts.weekday()}"
    bar_long = Bar("GLD", ts, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts, 72.0, 72.3, 71.7, 72.0, 1e6)
    pf = Portfolio(initial_cash=100_000.0)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, {})
    assert orders == [], f"expected no orders Fri 13:30, got {orders}"
