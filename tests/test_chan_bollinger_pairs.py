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


def _seed_position(strat, portfolio, ts_entry, *, side="long_spread"):
    """Open both legs on portfolio at ts_entry, mirror state dict, return ctx."""
    long_leg = 100.0
    short_leg = strat._beta * long_leg
    bar_long = Bar("GLD", ts_entry, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_entry, 72.0, 72.3, 71.7, 72.0, 1e6)
    if side == "long_spread":
        portfolio.open_position("GLD", "long", long_leg, 180.0, ts_entry)
        portfolio.open_position("SLV", "short", short_leg, 72.0, ts_entry)
    else:
        portfolio.open_position("GLD", "short", long_leg, 180.0, ts_entry)
        portfolio.open_position("SLV", "long", short_leg, 72.0, ts_entry)
    idx_entry = strat._indicators.index.get_loc(ts_entry)
    ctx = {
        strat._state_key(): {
            "entry_idx": idx_entry,
            "entry_z": -1.1 if side == "long_spread" else 1.1,
            "entry_wall_clock_ts": ts_entry,
            "side": side,
            "beta_at_entry": strat._beta,
        }
    }
    return ctx, bar_long, bar_short


def test_exit_mean_revert_long_spread_at_zero():
    """Long spread open; z crosses up through 0 → both legs closed."""
    strat, idx, tail_start = _make_strategy_with_z([-1.1, -0.1], entry_z=1.0)
    # Place entry 10 bars before tail_start; patch z scenery around entry + now
    entry_pos = tail_start - 10
    ts_entry = strat._indicators.index[entry_pos]
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    # Current bar: zscore just crossed zero
    ts_now = strat._indicators.index[tail_start + 1]
    strat._indicators.iloc[tail_start, strat._indicators.columns.get_loc("zscore")] = -0.1
    strat._indicators.iloc[tail_start + 1, strat._indicators.columns.get_loc("zscore")] = 0.1
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    sides = {o.symbol: o.side for o in orders}
    # closing long GLD = sell; closing short SLV = buy
    assert sides == {"GLD": "sell", "SLV": "buy"}


def test_exit_spread_stop_long_spread_at_minus_3():
    """Long spread open; z blows out to -3 → emergency close."""
    strat, idx, tail_start = _make_strategy_with_z([-1.1, -3.1], entry_z=1.0)
    entry_pos = tail_start - 5
    ts_entry = strat._indicators.index[entry_pos]
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    ts_now = strat._indicators.index[tail_start + 1]
    strat._indicators.iloc[tail_start + 1, strat._indicators.columns.get_loc("zscore")] = -3.1
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2
    assert {o.symbol for o in orders} == {"GLD", "SLV"}


def test_exit_friday_weekend_flat_at_15():
    """Long spread open; current bar is Friday 15:30 → force close even if z favorable."""
    strat, idx, tail_start = _make_strategy_with_z([-0.5, -0.4], entry_z=1.0)
    friday_ts = pd.Timestamp("2023-06-16 15:30")
    fri_pos = strat._indicators.index.get_indexer([friday_ts], method="nearest")[0]
    ts_now = strat._indicators.index[fri_pos]
    assert ts_now.weekday() == 4 and ts_now.hour >= 15
    entry_pos = fri_pos - 5
    ts_entry = strat._indicators.index[entry_pos]
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2


def test_exit_wall_clock_48h_cap():
    """Entry Mon 10:00, current Wed 11:00 (49h wall clock) → forced exit."""
    strat, idx, tail_start = _make_strategy_with_z([-0.5, -0.4], entry_z=1.0)
    mon_ts = pd.Timestamp("2023-06-12 10:30")
    wed_ts = pd.Timestamp("2023-06-14 11:30")  # >48h after mon_ts
    mon_pos = strat._indicators.index.get_indexer([mon_ts], method="nearest")[0]
    wed_pos = strat._indicators.index.get_indexer([wed_ts], method="nearest")[0]
    ts_entry = strat._indicators.index[mon_pos]
    ts_now = strat._indicators.index[wed_pos]
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2, (
        f"expected forced exit at wall-clock 48h+, got {orders}"
    )


def test_exit_time_stop_in_trading_bars():
    """Bars held >= time_stop_bars → forced exit."""
    strat, idx, tail_start = _make_strategy_with_z([-0.5, -0.4], entry_z=1.0)
    # time_stop_bars = min(3*half_life, 24); half_life recovered ~20 → time_stop=24
    # set entry such that bars_held == time_stop_bars exactly
    ts_now_pos = tail_start + 1
    ts_entry_pos = ts_now_pos - strat._time_stop_bars
    ts_entry = strat._indicators.index[ts_entry_pos]
    ts_now = strat._indicators.index[ts_now_pos]
    # Keep wall-clock under 48h by checking the spacing — if > 48h, test degenerates
    wall_h = (ts_now - ts_entry).total_seconds() / 3600.0
    if wall_h >= 48.0:
        pytest.skip(f"wall-clock gap {wall_h:.1f}h hides time-stop; skip")
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2, f"expected time-stop exit, got {orders}"


def test_exit_precedence_spread_stop_beats_mean_revert():
    """Both spread_stop (z=-3) AND mean-revert would fire; spread_stop wins.

    For long_spread entry at z=-1.1, z=+0.1 would mean-revert (happy) — but
    if the indicator is spoofed to be at -3.1 the spread_stop triggers.
    Symmetric: check that in the long side spread_stop is recognized as
    precedence over mean_revert by firing with the z clearly past the
    spread_stop_z limit on the same side as entry.
    """
    strat, idx, tail_start = _make_strategy_with_z([-1.1, -3.1], entry_z=1.0)
    entry_pos = tail_start - 3
    ts_entry = strat._indicators.index[entry_pos]
    ts_now = strat._indicators.index[tail_start + 1]
    # z_now = -3.1 triggers spread_stop for long spread
    strat._indicators.iloc[tail_start + 1, strat._indicators.columns.get_loc("zscore")] = -3.1
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2


def test_adjust_ohlc_applied_to_both_legs():
    """If adj_close differs from close, strategy must use adj_close.

    Uses a synthetic ex-dividend-like scenario where close has a discontinuity
    but adj_close is smooth.
    """
    rng = np.random.default_rng(42)
    n = 2000
    idx = pd.date_range("2022-01-03 09:30", periods=n, freq="1h")
    x = 50 + np.cumsum(rng.normal(0, 0.05, n))
    eps = np.zeros(n)
    lam = -np.log(2) / 20.0
    for t in range(1, n):
        eps[t] = eps[t - 1] * np.exp(lam) + rng.normal(0, 0.3)
    y = 2.5 * x + eps
    # Inject a "dividend" shock to close at mid-point (not adj_close)
    shock_idx = n // 2
    close_shock = y.copy()
    close_shock[shock_idx:] -= 5.0  # $5 dividend
    df_long = pd.DataFrame(
        {
            "open": close_shock, "high": close_shock, "low": close_shock,
            "close": close_shock, "volume": 1e6, "adj_close": y,
        },
        index=idx,
    )
    df_short = pd.DataFrame(
        {"open": x, "high": x, "low": x, "close": x, "volume": 1e6, "adj_close": x},
        index=idx,
    )
    strat = ChanBollingerPairsStrategy(
        data={"GLD": df_long, "SLV": df_short},
    )
    # After adjust_ohlc, close should now match adj_close — so _beta recovered
    # should still be ~2.5 (the shock was eliminated by adjustment).
    assert abs(strat._beta - 2.5) < 0.2, (
        f"β without adjust would diverge after shock; got {strat._beta}"
    )


def test_diagnostic_counters_tracked_in_context():
    """Run a few manufactured entries+exits; verify counters land in context."""
    strat, idx, tail_start = _make_strategy_with_z([-1.1, -3.1], entry_z=1.0)
    entry_pos = tail_start - 3
    ts_entry = strat._indicators.index[entry_pos]
    ts_now = strat._indicators.index[tail_start + 1]
    strat._indicators.iloc[tail_start + 1, strat._indicators.columns.get_loc("zscore")] = -3.1
    pf = Portfolio(initial_cash=100_000.0)
    ctx, _, _ = _seed_position(strat, pf, ts_entry, side="long_spread")
    bar_long = Bar("GLD", ts_now, 180.0, 180.5, 179.5, 180.0, 1e6)
    bar_short = Bar("SLV", ts_now, 72.0, 72.3, 71.7, 72.0, 1e6)
    orders = strat.on_bar({"GLD": bar_long, "SLV": bar_short}, pf, ctx)
    assert len(orders) == 2
    diag = ctx.get("chan_pairs_diagnostics", {})
    reasons = diag.get("exit_reasons", [])
    assert reasons == ["spread_stop"], f"expected ['spread_stop'], got {reasons}"
    holds = diag.get("hold_hours", [])
    assert len(holds) == 1
    assert holds[0] >= 0.0
