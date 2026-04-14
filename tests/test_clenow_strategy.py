"""Tests for Clenow ``stocks_on_the_move`` replication.

Scope:

* **Math helpers** — annualized exponential regression slope × R², ATR, max gap.
  Unit-level; numbers chosen so results are verifiable by hand or against a
  known closed-form identity.
* **Rebalance logic** — Wednesday-only cadence, regime filter, sell criteria,
  buy ordering + sizing + cash stop.

All tests use synthetic deterministic data; no network, no Wikipedia, no
yfinance. Universe is supplied via a stub callable.
"""

from __future__ import annotations

import math
from datetime import date

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------


class TestAdjustedSlope:
    def test_pure_exponential_is_perfect_fit(self):
        """log(P) linear in t → R² = 1; annualized slope = exp(m)^250 - 1."""
        from ai_trade.backtest.strategies.clenow_momentum import adjusted_slope

        # 90 bars of pure exponential: P_t = exp(m·t) with m = 0.001 (~28% ann).
        m = 0.001
        prices = pd.Series(np.exp(m * np.arange(90)))

        ann_slope, r2 = adjusted_slope(prices, lookback=90)

        expected_ann = math.exp(m) ** 250 - 1
        assert ann_slope == pytest.approx(expected_ann, rel=1e-9)
        assert r2 == pytest.approx(1.0, rel=1e-9)

    def test_negative_slope_returns_negative_annualized(self):
        from ai_trade.backtest.strategies.clenow_momentum import adjusted_slope

        m = -0.002
        prices = pd.Series(np.exp(m * np.arange(90)))
        ann_slope, r2 = adjusted_slope(prices, lookback=90)

        assert ann_slope < 0
        assert ann_slope == pytest.approx(math.exp(m) ** 250 - 1, rel=1e-9)
        assert r2 == pytest.approx(1.0, rel=1e-9)

    def test_noisy_series_has_lower_r2(self):
        """Noise around a trend reduces R² below 1."""
        from ai_trade.backtest.strategies.clenow_momentum import adjusted_slope

        rng = np.random.default_rng(42)
        m = 0.001
        noise = rng.normal(0, 0.02, 90)
        prices = pd.Series(np.exp(m * np.arange(90) + noise))

        _, r2 = adjusted_slope(prices, lookback=90)
        assert 0.0 <= r2 < 0.95

    def test_uses_last_lookback_bars_only(self):
        """Function must slice the tail; earlier data doesn't affect result."""
        from ai_trade.backtest.strategies.clenow_momentum import adjusted_slope

        m = 0.001
        # Prepend 30 irrelevant bars; last 90 are the pure exponential.
        head = np.ones(30) * 100.0
        tail = np.exp(m * np.arange(90))
        prices = pd.Series(np.concatenate([head, tail]))

        ann_slope, r2 = adjusted_slope(prices, lookback=90)
        assert r2 == pytest.approx(1.0, rel=1e-9)
        assert ann_slope == pytest.approx(math.exp(m) ** 250 - 1, rel=1e-9)

    def test_raises_on_insufficient_history(self):
        from ai_trade.backtest.strategies.clenow_momentum import adjusted_slope

        prices = pd.Series(np.exp(0.001 * np.arange(50)))  # only 50 bars
        with pytest.raises(ValueError, match="lookback"):
            adjusted_slope(prices, lookback=90)


class TestATR:
    def test_constant_range_returns_that_range(self):
        """If every bar has TR=R, ATR over N bars = R."""
        from ai_trade.backtest.strategies.clenow_momentum import atr

        # 30 bars with H-L=2, no gap overnight (open == prev close).
        n = 30
        close = pd.Series(np.full(n, 100.0))
        high = pd.Series(np.full(n, 101.0))
        low = pd.Series(np.full(n, 99.0))
        value = atr(high, low, close, lookback=20)
        assert value == pytest.approx(2.0)

    def test_uses_prev_close_in_tr_when_there_is_a_gap(self):
        """TR[t] = max(H-L, |H-C_prev|, |L-C_prev|); gap expands TR."""
        from ai_trade.backtest.strategies.clenow_momentum import atr

        # 21 bars. Bar 0 close=100. Bars 1..19 close=100 flat. Bar 20 gaps up:
        # prev close 100, today open/low=108, high=110, close=109.
        # TR[20] = max(110-108=2, |110-100|=10, |108-100|=8) = 10.
        # TRs[1..19] = H-L on flat bars. Build: H=101 L=99 close=100 on bars 1..19.
        highs = [100.0] + [101.0] * 19 + [110.0]
        lows = [100.0] + [99.0] * 19 + [108.0]
        closes = [100.0] * 20 + [109.0]
        value = atr(
            pd.Series(highs),
            pd.Series(lows),
            pd.Series(closes),
            lookback=20,
        )
        # Last 20 TRs: 19 bars of TR=2, plus the gap bar TR=10.
        # mean = (19*2 + 10) / 20 = 48 / 20 = 2.4
        assert value == pytest.approx(2.4)


class TestMaxGap:
    def test_flat_series_has_zero_max_gap(self):
        from ai_trade.backtest.strategies.clenow_momentum import max_gap

        close = pd.Series(np.full(100, 100.0))
        assert max_gap(close, lookback=90) == pytest.approx(0.0)

    def test_detects_large_single_day_jump(self):
        """A +20% one-day return shows up as max_gap = 0.20."""
        from ai_trade.backtest.strategies.clenow_momentum import max_gap

        close = [100.0] * 50 + [120.0] + [120.0] * 49  # 100 bars
        value = max_gap(pd.Series(close), lookback=90)
        assert value == pytest.approx(0.20, rel=1e-9)

    def test_detects_large_negative_move(self):
        from ai_trade.backtest.strategies.clenow_momentum import max_gap

        close = [100.0] * 50 + [75.0] + [75.0] * 49  # −25% jump
        value = max_gap(pd.Series(close), lookback=90)
        assert value == pytest.approx(0.25, rel=1e-9)

    def test_only_considers_last_lookback_returns(self):
        """Gap older than ``lookback`` must be ignored."""
        from ai_trade.backtest.strategies.clenow_momentum import max_gap

        # 200 bars; gap at bar 10, rest flat. Use lookback=90 → gap out of window.
        close = [100.0] * 10 + [200.0] + [200.0] * 189
        value = max_gap(pd.Series(close), lookback=90)
        assert value == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Rebalance scheduling (Wednesday-only)
# ---------------------------------------------------------------------------


def _ohlcv_flat(prices: list[float], start: str = "2023-01-02") -> pd.DataFrame:
    idx = pd.bdate_range(start=start, periods=len(prices), name="date")
    return pd.DataFrame(
        {
            "open": prices,
            "high": [p * 1.01 for p in prices],
            "low": [p * 0.99 for p in prices],
            "close": prices,
            "adj_close": prices,
            "volume": [1_000_000] * len(prices),
        },
        index=idx,
    )


def _bar_at(df: pd.DataFrame, symbol: str, ts: pd.Timestamp):
    from ai_trade.backtest.engine.execution import Bar

    row = df.loc[ts]
    return Bar(
        symbol=symbol,
        timestamp=ts,
        open=float(row["open"]),
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
        volume=float(row["volume"]),
    )


class TestRebalanceSchedule:
    def test_rebalances_only_on_wednesday(self):
        """``should_rebalance`` returns True exactly when weekday == 2."""
        from ai_trade.backtest.strategies.clenow_momentum import (
            ClenowMomentumStrategy,
        )

        # Pick known weekdays:
        #   2024-01-02 = Tuesday
        #   2024-01-03 = Wednesday
        #   2024-01-04 = Thursday
        strat = ClenowMomentumStrategy(
            data={},
            constituents_provider=lambda d: set(),
            index_symbol="SPX",
        )
        assert strat.should_rebalance(pd.Timestamp("2024-01-02"), {}) is False
        assert strat.should_rebalance(pd.Timestamp("2024-01-03"), {}) is True
        assert strat.should_rebalance(pd.Timestamp("2024-01-04"), {}) is False


# ---------------------------------------------------------------------------
# End-to-end rebalance logic
# ---------------------------------------------------------------------------


def _linear_log_prices(start_price: float, daily_ret: float, n: int) -> list[float]:
    """n bars of ``start_price × exp(daily_ret × t)``; perfectly smooth trend."""
    return [start_price * math.exp(daily_ret * t) for t in range(n)]


def _build_ohlcv_from_close(close: list[float], start="2023-01-02") -> pd.DataFrame:
    idx = pd.bdate_range(start=start, periods=len(close), name="date")
    return pd.DataFrame(
        {
            "open": close,
            "high": [c * 1.005 for c in close],
            "low": [c * 0.995 for c in close],
            "close": close,
            "adj_close": close,
            "volume": [1_000_000] * len(close),
        },
        index=idx,
    )


def _find_wednesday(df: pd.DataFrame) -> pd.Timestamp:
    for ts in df.index:
        if ts.weekday() == 2:
            return ts
    raise AssertionError("no Wednesday in fixture")


class TestRegimeFilter:
    def test_no_buys_when_index_below_200ma(self):
        """SPX < 200MA on the rebalance date → zero buy orders."""
        from ai_trade.backtest.engine.portfolio import Portfolio
        from ai_trade.backtest.strategies.clenow_momentum import (
            ClenowMomentumStrategy,
        )

        # 300 bars for index: first 200 at 1000, then decline to below 200MA.
        index_close = [1000.0] * 200 + _linear_log_prices(1000.0, -0.002, 100)
        # Single constituent with strong trend.
        aapl_close = _linear_log_prices(100.0, 0.001, 300)

        data = {
            "SPX": _build_ohlcv_from_close(index_close),
            "AAPL": _build_ohlcv_from_close(aapl_close),
        }

        strat = ClenowMomentumStrategy(
            data=data,
            constituents_provider=lambda d: {"AAPL"},
            index_symbol="SPX",
            top_pct=1.0,  # allow all held
        )
        # Pick a rebalance Wednesday near the end (index well below its 200MA).
        last_wed = max(ts for ts in data["AAPL"].index if ts.weekday() == 2)

        bars = {sym: _bar_at(df, sym, last_wed) for sym, df in data.items()}
        portfolio = Portfolio(initial_cash=10_000.0)
        orders = strat.on_rebalance(last_wed, bars, portfolio, {})

        # No holdings → no sells. Regime off → no buys either.
        assert orders == []


class TestSellCriteria:
    def test_sells_holding_that_left_universe(self):
        """Held stock drops from constituents → emit sell."""
        from ai_trade.backtest.engine.portfolio import Portfolio
        from ai_trade.backtest.strategies.clenow_momentum import (
            ClenowMomentumStrategy,
        )

        # Index trending up; AAPL trending up too (so not sold for other reasons).
        index_close = _linear_log_prices(1000.0, 0.0008, 300)
        aapl_close = _linear_log_prices(100.0, 0.001, 300)
        data = {
            "SPX": _build_ohlcv_from_close(index_close),
            "AAPL": _build_ohlcv_from_close(aapl_close),
        }

        # Stub: AAPL NOT in universe on rebalance date.
        strat = ClenowMomentumStrategy(
            data=data,
            constituents_provider=lambda d: set(),
            index_symbol="SPX",
            top_pct=1.0,
        )

        last_wed = max(ts for ts in data["AAPL"].index if ts.weekday() == 2)
        portfolio = Portfolio(initial_cash=10_000.0)
        # Seed an open long in AAPL.
        portfolio.open_position(
            "AAPL", side="long", volume=10, price=100.0,
            timestamp=pd.Timestamp("2023-01-03"),
        )

        bars = {sym: _bar_at(df, sym, last_wed) for sym, df in data.items()}
        orders = strat.on_rebalance(last_wed, bars, portfolio, {})

        assert any(o.symbol == "AAPL" and o.side == "sell" for o in orders)

    def test_sells_holding_below_100ma(self):
        """AAPL drops below 100MA → emitted sell."""
        from ai_trade.backtest.engine.portfolio import Portfolio
        from ai_trade.backtest.strategies.clenow_momentum import (
            ClenowMomentumStrategy,
        )

        index_close = _linear_log_prices(1000.0, 0.0008, 300)
        # AAPL: 200 bars at $100, then collapse for last 100 bars.
        aapl_close = [100.0] * 200 + _linear_log_prices(100.0, -0.005, 100)
        data = {
            "SPX": _build_ohlcv_from_close(index_close),
            "AAPL": _build_ohlcv_from_close(aapl_close),
        }

        strat = ClenowMomentumStrategy(
            data=data,
            constituents_provider=lambda d: {"AAPL"},
            index_symbol="SPX",
            top_pct=1.0,
        )

        last_wed = max(ts for ts in data["AAPL"].index if ts.weekday() == 2)
        portfolio = Portfolio(initial_cash=10_000.0)
        portfolio.open_position(
            "AAPL", side="long", volume=10, price=100.0,
            timestamp=pd.Timestamp("2023-01-03"),
        )

        bars = {sym: _bar_at(df, sym, last_wed) for sym, df in data.items()}
        orders = strat.on_rebalance(last_wed, bars, portfolio, {})

        assert any(o.symbol == "AAPL" and o.side == "sell" for o in orders)

    def test_sells_holding_with_large_gap(self):
        """Recent >15% single-day move → sell (gap filter, p.82)."""
        from ai_trade.backtest.engine.portfolio import Portfolio
        from ai_trade.backtest.strategies.clenow_momentum import (
            ClenowMomentumStrategy,
        )

        index_close = _linear_log_prices(1000.0, 0.0008, 300)
        # Inject a 20% jump 50 bars before the last Wednesday.
        aapl_close = [100.0] * 245 + [120.0] + [120.0] * 54  # 300 bars
        data = {
            "SPX": _build_ohlcv_from_close(index_close),
            "AAPL": _build_ohlcv_from_close(aapl_close),
        }

        strat = ClenowMomentumStrategy(
            data=data,
            constituents_provider=lambda d: {"AAPL"},
            index_symbol="SPX",
            top_pct=1.0,
            gap_threshold=0.15,
        )

        last_wed = max(ts for ts in data["AAPL"].index if ts.weekday() == 2)
        portfolio = Portfolio(initial_cash=10_000.0)
        portfolio.open_position(
            "AAPL", side="long", volume=10, price=100.0,
            timestamp=pd.Timestamp("2023-01-03"),
        )

        bars = {sym: _bar_at(df, sym, last_wed) for sym, df in data.items()}
        orders = strat.on_rebalance(last_wed, bars, portfolio, {})

        assert any(o.symbol == "AAPL" and o.side == "sell" for o in orders)

    def test_skips_sell_for_delisted_symbol_with_no_bar_today(self):
        """Regression: a held position whose symbol has no bar at `ts`
        (delisted within the backtest window, e.g. ANDV merged into MPC
        in 2018-10) must NOT emit a sell order — Runner would crash
        trying to fill an order with no bar. The position waits until
        data returns or the backtest ends.

        The bug manifests when ``_should_sell`` returns True for a delisted
        holding (universe membership lost, MA broken, etc.) and the strategy
        previously emitted an Order without checking ``bars``.
        """
        from ai_trade.backtest.engine.portfolio import Portfolio
        from ai_trade.backtest.strategies.clenow_momentum import (
            ClenowMomentumStrategy,
        )

        # SPX has full 300 bars; ANDV has 200 bars then stops.
        index_close = _linear_log_prices(1000.0, 0.0008, 300)
        andv_close = _linear_log_prices(100.0, 0.001, 200)
        data = {
            "SPX": _build_ohlcv_from_close(index_close),
            "ANDV": _build_ohlcv_from_close(andv_close),
        }

        strat = ClenowMomentumStrategy(
            data=data,
            # ANDV no longer in SPX (delisted — universe reflects that).
            # Without universe membership, _should_sell returns True.
            constituents_provider=lambda d: set(),
            index_symbol="SPX",
            top_pct=1.0,
        )

        # Rebalance Wednesday AFTER ANDV's last bar — no bar for ANDV today.
        last_wed = max(ts for ts in data["SPX"].index if ts.weekday() == 2)
        assert last_wed not in data["ANDV"].index  # sanity: ANDV delisted

        portfolio = Portfolio(initial_cash=10_000.0)
        portfolio.open_position(
            "ANDV", side="long", volume=10, price=100.0,
            timestamp=pd.Timestamp("2023-01-03"),
        )

        bars = {"SPX": _bar_at(data["SPX"], "SPX", last_wed)}
        orders = strat.on_rebalance(last_wed, bars, portfolio, {})

        # No sell order for ANDV — can't trade a symbol without a bar.
        andv_sells = [o for o in orders if o.symbol == "ANDV" and o.side == "sell"]
        assert andv_sells == []


class TestBuyLogic:
    def test_buys_top_ranked_when_regime_on(self):
        """SPX > 200MA + strong stock → emit a buy at top of ranking."""
        from ai_trade.backtest.engine.portfolio import Portfolio
        from ai_trade.backtest.strategies.clenow_momentum import (
            ClenowMomentumStrategy,
        )

        # Index trending up for 300 bars (well above any 200MA).
        index_close = _linear_log_prices(1000.0, 0.0008, 300)
        # Two symbols: AAPL strong trend, MSFT weak trend.
        aapl_close = _linear_log_prices(100.0, 0.0015, 300)
        msft_close = _linear_log_prices(100.0, 0.0002, 300)

        data = {
            "SPX": _build_ohlcv_from_close(index_close),
            "AAPL": _build_ohlcv_from_close(aapl_close),
            "MSFT": _build_ohlcv_from_close(msft_close),
        }
        strat = ClenowMomentumStrategy(
            data=data,
            constituents_provider=lambda d: {"AAPL", "MSFT"},
            index_symbol="SPX",
            top_pct=0.50,  # allow both in the top 50%
            risk_factor=0.001,
        )

        last_wed = max(ts for ts in data["AAPL"].index if ts.weekday() == 2)
        portfolio = Portfolio(initial_cash=100_000.0)
        bars = {sym: _bar_at(df, sym, last_wed) for sym, df in data.items()}
        orders = strat.on_rebalance(last_wed, bars, portfolio, {})

        buys = [o for o in orders if o.side == "buy"]
        assert len(buys) >= 1
        # AAPL (stronger trend) must appear before MSFT in the order list.
        buy_symbols = [o.symbol for o in buys]
        if "AAPL" in buy_symbols and "MSFT" in buy_symbols:
            assert buy_symbols.index("AAPL") < buy_symbols.index("MSFT")

    def test_position_size_matches_clenow_formula(self):
        """shares = floor(equity × risk_factor / ATR20). Verify the rounding."""
        from ai_trade.backtest.engine.portfolio import Portfolio
        from ai_trade.backtest.strategies.clenow_momentum import (
            ClenowMomentumStrategy,
            atr,
        )

        index_close = _linear_log_prices(1000.0, 0.0008, 300)
        aapl_close = _linear_log_prices(100.0, 0.0015, 300)

        data = {
            "SPX": _build_ohlcv_from_close(index_close),
            "AAPL": _build_ohlcv_from_close(aapl_close),
        }
        strat = ClenowMomentumStrategy(
            data=data,
            constituents_provider=lambda d: {"AAPL"},
            index_symbol="SPX",
            top_pct=1.0,
            risk_factor=0.001,
            lookback_atr=20,
        )

        last_wed = max(ts for ts in data["AAPL"].index if ts.weekday() == 2)
        portfolio = Portfolio(initial_cash=100_000.0)
        bars = {sym: _bar_at(df, sym, last_wed) for sym, df in data.items()}
        orders = strat.on_rebalance(last_wed, bars, portfolio, {})

        # Expected ATR on AAPL @ last_wed:
        aapl_df = data["AAPL"].loc[:last_wed]
        atr_value = atr(
            aapl_df["high"],
            aapl_df["low"],
            aapl_df["close"],
            lookback=20,
        )
        expected_shares = int((100_000.0 * 0.001) / atr_value)

        aapl_buys = [o for o in orders if o.symbol == "AAPL" and o.side == "buy"]
        assert len(aapl_buys) == 1
        assert aapl_buys[0].volume == expected_shares

    def test_cash_stop_limits_buys(self):
        """When equity is tiny, buys stop after cash runs out."""
        from ai_trade.backtest.engine.portfolio import Portfolio
        from ai_trade.backtest.strategies.clenow_momentum import (
            ClenowMomentumStrategy,
        )

        index_close = _linear_log_prices(1000.0, 0.0008, 300)
        # Four symbols, all strong, all ~price 100 → each buy ~$100-$1_000.
        data = {
            "SPX": _build_ohlcv_from_close(index_close),
            "A": _build_ohlcv_from_close(_linear_log_prices(100.0, 0.0015, 300)),
            "B": _build_ohlcv_from_close(_linear_log_prices(100.0, 0.0013, 300)),
            "C": _build_ohlcv_from_close(_linear_log_prices(100.0, 0.0011, 300)),
            "D": _build_ohlcv_from_close(_linear_log_prices(100.0, 0.0009, 300)),
        }
        strat = ClenowMomentumStrategy(
            data=data,
            constituents_provider=lambda d: {"A", "B", "C", "D"},
            index_symbol="SPX",
            top_pct=1.0,
            risk_factor=0.01,  # oversized so each position eats a big share of cash
        )

        last_wed = max(ts for ts in data["A"].index if ts.weekday() == 2)
        # Small cash: cannot fit all four at risk_factor=0.01 → oversized positions.
        portfolio = Portfolio(initial_cash=5_000.0)
        bars = {sym: _bar_at(df, sym, last_wed) for sym, df in data.items()}
        orders = strat.on_rebalance(last_wed, bars, portfolio, {})

        buys = [o for o in orders if o.side == "buy"]
        assert len(buys) < 4  # at least one symbol must be skipped for lack of cash
