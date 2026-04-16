"""Integration tests for VolExpansionBreakoutStrategy [spec §1, §3]."""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.engine.execution import Bar
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.strategies.vol_expansion_breakout import VolExpansionBreakoutStrategy


def _synth_quiet_then_breakout(n: int, breakout_at: int, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    quiet = 100.0 + np.cumsum(rng.normal(0, 0.05, breakout_at))
    trend = quiet[-1] + np.cumsum(np.full(n - breakout_at, 0.5))
    closes = np.concatenate([quiet, trend])
    opens = closes + rng.normal(0, 0.02, n)
    highs = np.maximum(opens, closes) + 0.05
    lows = np.minimum(opens, closes) - 0.05
    ts = pd.date_range("2023-01-01 09:30", periods=n, freq="h", tz="UTC")
    return pd.DataFrame(
        {"open": opens, "high": highs, "low": lows, "close": closes,
         "adj_close": closes, "volume": [1000.0] * n}, index=ts)


def _bar(symbol: str, ts: pd.Timestamp, row: pd.Series) -> Bar:
    return Bar(
        symbol=symbol,
        timestamp=ts,
        open=float(row["open"]),
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
        volume=float(row.get("volume", 1000.0)),
    )


def test_quiet_regime_then_breakout_emits_long() -> None:
    """Strategy emits at least one long order after a prolonged quiet period + breakout."""
    df = _synth_quiet_then_breakout(n=1350, breakout_at=1300, seed=1)
    strat = VolExpansionBreakoutStrategy(
        data={"SPY": df},
        symbol_specs={"SPY": {"bars_per_year": 1638}},
        n_entry=20,
        n_exit=10,
        cone_lookback=800,
        yz_window=20,
        k_filter=33.0,
        target_vol_annual=0.10,
        max_hold_hours=48.0,
        disaster_n_sigma=4,
        ref_hold_bars=24,
    )
    # Portfolio uses initial_cash field [portfolio.py line 68]
    portfolio = Portfolio(initial_cash=100_000.0)
    context: dict = {}
    saw_long = False
    for ts, row in df.iterrows():
        bars = {"SPY": _bar("SPY", ts, row)}
        orders = strat.on_bar(bars, portfolio, context)
        if any(o.side == "buy" for o in orders):
            saw_long = True
            break
    assert saw_long, "Expected at least one 'buy' order after quiet regime + breakout"


def test_insufficient_warmup_emits_zero_orders() -> None:
    """Strategy emits no orders when the series is shorter than cone_lookback.

    When bars_in_history < cone_lookback, the regime filter never reaches a
    valid reading and always returns is_quiet=False.  No entry signals fire.

    cone_lookback=500, n=200 → history never fills the cone → 0 orders.
    """
    rng = np.random.default_rng(2)
    n = 200  # deliberately shorter than cone_lookback=500
    closes = 100.0 + np.cumsum(rng.normal(0, 2.0, n))
    opens = closes + rng.normal(0, 1.0, n)
    highs = np.maximum(opens, closes) + np.abs(rng.normal(0, 0.5, n))
    lows = np.minimum(opens, closes) - np.abs(rng.normal(0, 0.5, n))
    ts = pd.date_range("2023-01-01 09:30", periods=n, freq="h", tz="UTC")
    df = pd.DataFrame(
        {"open": opens, "high": highs, "low": lows, "close": closes,
         "adj_close": closes, "volume": [1000.0] * n}, index=ts)

    strat = VolExpansionBreakoutStrategy(
        data={"SPY": df},
        symbol_specs={"SPY": {"bars_per_year": 1638}},
        n_entry=20,
        n_exit=10,
        cone_lookback=500,  # requires 500 bars of YZ history → never reached
        yz_window=20,
        k_filter=33.0,
        target_vol_annual=0.10,
        max_hold_hours=48.0,
        disaster_n_sigma=4,
        ref_hold_bars=24,
    )
    portfolio = Portfolio(initial_cash=100_000.0)
    context: dict = {}
    total_orders = 0
    for ts_val, row in df.iterrows():
        orders = strat.on_bar({"SPY": _bar("SPY", ts_val, row)}, portfolio, context)
        total_orders += len(orders)
    assert total_orders == 0, f"Expected 0 orders before cone warmup, got {total_orders}"


def test_multi_symbol_independent_state() -> None:
    """Three symbols each get independent state; at least 2 should see trades."""
    df_a = _synth_quiet_then_breakout(n=1350, breakout_at=1300, seed=10)
    df_b = _synth_quiet_then_breakout(n=1350, breakout_at=1300, seed=20)
    df_c = _synth_quiet_then_breakout(n=1350, breakout_at=1300, seed=30)
    strat = VolExpansionBreakoutStrategy(
        data={"A": df_a, "B": df_b, "C": df_c},
        symbol_specs={
            "A": {"bars_per_year": 1638},
            "B": {"bars_per_year": 1638},
            "C": {"bars_per_year": 1638},
        },
        n_entry=20,
        n_exit=10,
        cone_lookback=800,
        yz_window=20,
        k_filter=33.0,
        target_vol_annual=0.10,
        max_hold_hours=48.0,
        disaster_n_sigma=4,
        ref_hold_bars=24,
    )
    portfolio = Portfolio(initial_cash=100_000.0)
    context: dict = {}
    symbols_with_trades: set[str] = set()
    for i, ts_val in enumerate(df_a.index):
        bars = {
            "A": _bar("A", ts_val, df_a.iloc[i]),
            "B": _bar("B", ts_val, df_b.iloc[i]),
            "C": _bar("C", ts_val, df_c.iloc[i]),
        }
        orders = strat.on_bar(bars, portfolio, context)
        for o in orders:
            symbols_with_trades.add(o.symbol)
    assert len(symbols_with_trades) >= 2, (
        f"Expected trades in at least 2 symbols, got: {symbols_with_trades}"
    )
