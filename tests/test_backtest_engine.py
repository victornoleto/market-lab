"""Unit + integration tests for the backtest engine (Portfolio, Execution, Runner).

Scope:
    TestPortfolio    — P&L accounting, cash flows, equity curve
    TestExecution    — spread/slippage/commission fills, overnight swap
    TestRunner       — end-to-end bar loop with a trivial buy-and-hold strategy

Design: synthetic inputs, numbers verifiable by hand. No network, no real market
data. All prices/volumes chosen so arithmetic stays integer-clean.
"""

from __future__ import annotations

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

class TestPortfolio:
    def test_starts_flat_with_initial_cash(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        assert p.cash == 10_000.0
        assert p.positions == {}
        assert p.realized_pnl == 0.0
        assert p.equity == 10_000.0

    def test_open_long_position_debits_cash_and_creates_position(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="long", volume=10, price=150.0, timestamp=ts)

        assert p.cash == pytest.approx(10_000.0 - 10 * 150.0)
        assert "AAPL" in p.positions
        pos = p.positions["AAPL"]
        assert pos.side == "long"
        assert pos.volume == 10
        assert pos.avg_entry_price == 150.0
        assert pos.mark_price == 150.0  # mark defaults to entry

    def test_open_short_position_credits_cash_and_creates_position(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="short", volume=10, price=150.0, timestamp=ts)

        # Short sale credits proceeds to cash (financing-agnostic, standard accounting).
        assert p.cash == pytest.approx(10_000.0 + 10 * 150.0)
        assert p.positions["AAPL"].side == "short"

    def test_open_same_side_position_updates_weighted_avg_price(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=100_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="long", volume=10, price=100.0, timestamp=ts)
        p.open_position("AAPL", side="long", volume=10, price=120.0, timestamp=ts)

        pos = p.positions["AAPL"]
        assert pos.volume == 20
        assert pos.avg_entry_price == pytest.approx(110.0)

    def test_open_opposite_side_raises_without_closing_first(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="long", volume=10, price=150.0, timestamp=ts)

        with pytest.raises(ValueError, match="opposite side"):
            p.open_position("AAPL", side="short", volume=5, price=150.0, timestamp=ts)

    def test_close_full_long_position_realizes_pnl(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        t_open = pd.Timestamp("2024-01-02")
        t_close = pd.Timestamp("2024-01-10")

        p.open_position("AAPL", side="long", volume=10, price=150.0, timestamp=t_open)
        trade = p.close_position("AAPL", volume=10, price=160.0, timestamp=t_close)

        # Realized PnL = 10 * (160 - 150) = 100
        assert trade.pnl == pytest.approx(100.0)
        assert trade.entry_price == 150.0
        assert trade.exit_price == 160.0
        assert trade.entry_time == t_open
        assert trade.exit_time == t_close
        assert "AAPL" not in p.positions
        assert p.realized_pnl == pytest.approx(100.0)
        # Cash: 10_000 - 10*150 + 10*160 = 10_100
        assert p.cash == pytest.approx(10_100.0)

    def test_close_full_short_position_realizes_pnl(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="short", volume=10, price=150.0, timestamp=ts)
        trade = p.close_position("AAPL", volume=10, price=140.0, timestamp=ts)

        # Short profits when price falls: 10 * (150 - 140) = 100
        assert trade.pnl == pytest.approx(100.0)
        assert p.realized_pnl == pytest.approx(100.0)
        # Cash flow: +1500 on open, -1400 on close = net +100 on top of initial
        assert p.cash == pytest.approx(10_100.0)

    def test_partial_close_is_proportional(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="long", volume=10, price=150.0, timestamp=ts)
        trade = p.close_position("AAPL", volume=4, price=160.0, timestamp=ts)

        # Realized = 4 * (160 - 150) = 40
        assert trade.pnl == pytest.approx(40.0)
        assert trade.volume == 4
        # Remaining 6 shares at avg 150
        assert p.positions["AAPL"].volume == 6
        assert p.positions["AAPL"].avg_entry_price == 150.0

    def test_close_more_than_open_raises(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="long", volume=10, price=150.0, timestamp=ts)

        with pytest.raises(ValueError, match="exceeds"):
            p.close_position("AAPL", volume=11, price=150.0, timestamp=ts)

    def test_update_mark_drives_unrealized_pnl(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="long", volume=10, price=150.0, timestamp=ts)
        p.update_mark("AAPL", price=160.0)

        pos = p.positions["AAPL"]
        assert pos.mark_price == 160.0
        assert pos.unrealized_pnl == pytest.approx(100.0)
        # Equity = cash + signed_position_value. cash = 10_000 - 1500 = 8500;
        # long position value = 10 × 160 = 1600 → equity = 10_100.
        # Equivalently: initial 10_000 + unrealized 100 = 10_100.
        assert p.equity == pytest.approx(10_100.0)

    def test_equity_equals_cash_plus_unrealized_sum(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=100_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="long", volume=10, price=150.0, timestamp=ts)
        p.open_position("MSFT", side="short", volume=5, price=300.0, timestamp=ts)
        p.update_mark("AAPL", price=155.0)  # +50 unrealized
        p.update_mark("MSFT", price=290.0)  # short: +50 unrealized

        # cash = 100_000 - 1500 + 1500 = 100_000
        # unrealized = 50 + 50 = 100
        assert p.equity == pytest.approx(100_100.0)

    def test_apply_cash_flow_changes_cash_only(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        p.apply_cash_flow(-5.0, reason="commission")
        assert p.cash == pytest.approx(9_995.0)
        assert p.realized_pnl == 0.0  # commissions don't touch realized pnl
        assert p.equity == pytest.approx(9_995.0)

    def test_record_equity_appends_timestamped_point(self):
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        t1 = pd.Timestamp("2024-01-02")
        t2 = pd.Timestamp("2024-01-03")
        p.record_equity(t1)
        p.open_position("AAPL", side="long", volume=10, price=150.0, timestamp=t1)
        p.update_mark("AAPL", price=160.0)
        p.record_equity(t2)

        curve = p.equity_curve
        assert isinstance(curve, pd.Series)
        assert list(curve.index) == [t1, t2]
        assert curve.loc[t1] == pytest.approx(10_000.0)
        # After open: cash = 8_500, position value (mark 160) = 1_600 → equity = 10_100.
        assert curve.loc[t2] == pytest.approx(10_100.0)


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def _bar(symbol: str = "AAPL", close: float = 100.0, ts: str = "2024-01-02"):
    from market_lab.backtest.engine.execution import Bar

    price = close
    return Bar(
        symbol=symbol,
        timestamp=pd.Timestamp(ts),
        open=price,
        high=price,
        low=price,
        close=price,
        volume=1_000_000,
    )


class TestExecution:
    def test_market_buy_fills_at_close_when_no_costs(self):
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
            Order,
        )

        sim = ExecutionSimulator(ExecutionConfig())
        fill = sim.simulate_fill(Order("AAPL", side="buy", volume=10), _bar(close=150.0))

        assert fill is not None
        assert fill.fill_price == pytest.approx(150.0)
        assert fill.commission == 0.0
        assert fill.slippage_cost == 0.0

    def test_market_sell_fills_at_close_when_no_costs(self):
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
            Order,
        )

        sim = ExecutionSimulator(ExecutionConfig())
        fill = sim.simulate_fill(Order("AAPL", side="sell", volume=10), _bar(close=150.0))

        assert fill.fill_price == pytest.approx(150.0)

    def test_market_buy_pays_half_spread_and_slippage(self):
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
            Order,
        )

        # Half-spread and slippage both in price units, adverse direction on buy.
        sim = ExecutionSimulator(ExecutionConfig(half_spread=0.05, slippage=0.02))
        fill = sim.simulate_fill(Order("AAPL", side="buy", volume=10), _bar(close=150.0))

        assert fill.fill_price == pytest.approx(150.07)
        # slippage_cost is the premium over mid (half_spread + slippage) × volume
        assert fill.slippage_cost == pytest.approx((0.05 + 0.02) * 10)

    def test_market_sell_receives_close_minus_half_spread_minus_slippage(self):
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
            Order,
        )

        sim = ExecutionSimulator(ExecutionConfig(half_spread=0.05, slippage=0.02))
        fill = sim.simulate_fill(Order("AAPL", side="sell", volume=10), _bar(close=150.0))

        assert fill.fill_price == pytest.approx(149.93)
        assert fill.slippage_cost == pytest.approx((0.05 + 0.02) * 10)

    def test_commission_per_unit_multiplied_by_volume(self):
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
            Order,
        )

        sim = ExecutionSimulator(ExecutionConfig(commission_per_unit=0.01))
        fill = sim.simulate_fill(Order("AAPL", side="buy", volume=100), _bar(close=150.0))
        assert fill.commission == pytest.approx(1.0)

    def test_simulate_fill_rejects_zero_volume(self):
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
            Order,
        )

        sim = ExecutionSimulator(ExecutionConfig())
        with pytest.raises(ValueError, match="volume"):
            sim.simulate_fill(Order("AAPL", side="buy", volume=0), _bar())

    def test_swap_model_debits_long_at_configured_rate(self):
        from market_lab.backtest.engine.execution import SwapModel
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="long", volume=10, price=100.0, timestamp=ts)
        p.update_mark("AAPL", price=100.0)
        cash_before = p.cash

        swap = SwapModel(long_rate_per_day=0.0001)  # 1 bp/day cost on notional
        swap.charge(p, timestamp=ts)

        # notional = 10 * 100 = 1000; charge = 1000 * 0.0001 = 0.10
        assert p.cash == pytest.approx(cash_before - 0.10)

    def test_swap_model_debits_short_at_configured_rate(self):
        from market_lab.backtest.engine.execution import SwapModel
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        ts = pd.Timestamp("2024-01-02")
        p.open_position("AAPL", side="short", volume=10, price=100.0, timestamp=ts)
        p.update_mark("AAPL", price=100.0)
        cash_before = p.cash

        swap = SwapModel(short_rate_per_day=0.0002)
        swap.charge(p, timestamp=ts)

        assert p.cash == pytest.approx(cash_before - 10 * 100 * 0.0002)

    def test_swap_model_is_noop_on_flat_portfolio(self):
        from market_lab.backtest.engine.execution import SwapModel
        from market_lab.backtest.engine.portfolio import Portfolio

        p = Portfolio(initial_cash=10_000.0)
        SwapModel(long_rate_per_day=0.01, short_rate_per_day=0.01).charge(
            p, timestamp=pd.Timestamp("2024-01-02")
        )
        assert p.cash == 10_000.0


# ---------------------------------------------------------------------------
# Runner — end-to-end bar loop
# ---------------------------------------------------------------------------

def _ohlcv(prices: list[float], start: str = "2024-01-02") -> pd.DataFrame:
    """Build a synthetic OHLCV frame where OHLC == close (clean arithmetic)."""
    idx = pd.bdate_range(start=start, periods=len(prices), name="date")
    return pd.DataFrame(
        {
            "open": prices,
            "high": prices,
            "low": prices,
            "close": prices,
            "adj_close": prices,
            "volume": [1_000_000] * len(prices),
        },
        index=idx,
    )


class _BuyOnceHoldStrategy:
    """Trivial fixture strategy: buy ``volume`` shares of ``symbol`` on the first bar, hold."""

    def __init__(self, symbol: str, volume: float):
        self.symbol = symbol
        self.volume = volume
        self._bought = False

    def on_bar(self, bars, portfolio, context):
        from market_lab.backtest.engine.execution import Order

        if self._bought or self.symbol not in bars:
            return []
        self._bought = True
        return [Order(symbol=self.symbol, side="buy", volume=self.volume)]


class _BuyThenSellStrategy:
    """Fixture: buy on bar 0, sell on bar N-1 (last bar)."""

    def __init__(self, symbol: str, volume: float, n_bars: int):
        self.symbol = symbol
        self.volume = volume
        self.n_bars = n_bars
        self._seen = 0

    def on_bar(self, bars, portfolio, context):
        from market_lab.backtest.engine.execution import Order

        if self.symbol not in bars:
            return []
        orders: list = []
        if self._seen == 0:
            orders.append(Order(self.symbol, side="buy", volume=self.volume))
        elif self._seen == self.n_bars - 1:
            orders.append(Order(self.symbol, side="sell", volume=self.volume))
        self._seen += 1
        return orders


class TestRunner:
    def test_buy_and_hold_no_costs_equity_matches_position_value(self):
        from market_lab.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
        from market_lab.backtest.engine.runner import Runner

        data = {"AAPL": _ohlcv([100.0, 110.0, 120.0])}
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        result = runner.run(
            strategy=_BuyOnceHoldStrategy("AAPL", volume=10),
            data=data,
            initial_cash=10_000.0,
        )

        # Buy 10 @ 100 on day 1. Hold. Mark goes 100 → 110 → 120.
        # Final equity = cash (10_000 - 1000) + position (10 * 120) = 10_200.
        assert result.final_equity == pytest.approx(10_200.0)
        assert len(result.equity_curve) == 3
        assert result.equity_curve.iloc[0] == pytest.approx(10_000.0)
        assert result.equity_curve.iloc[-1] == pytest.approx(10_200.0)
        assert len(result.fills) == 1
        assert result.fills[0].order.side == "buy"
        assert result.trades == []  # never closed, so no closed trades

    def test_buy_then_sell_realizes_pnl_and_emits_trade(self):
        from market_lab.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
        from market_lab.backtest.engine.runner import Runner

        data = {"AAPL": _ohlcv([100.0, 110.0, 120.0])}
        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        result = runner.run(
            strategy=_BuyThenSellStrategy("AAPL", volume=10, n_bars=3),
            data=data,
            initial_cash=10_000.0,
        )

        assert len(result.trades) == 1
        assert result.trades[0].pnl == pytest.approx(200.0)  # 10 * (120 - 100)
        assert result.final_equity == pytest.approx(10_200.0)
        assert len(result.fills) == 2

    def test_half_spread_reduces_final_equity_by_spread_cost(self):
        from market_lab.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
        from market_lab.backtest.engine.runner import Runner

        data = {"AAPL": _ohlcv([100.0, 110.0, 120.0])}
        runner = Runner(
            executor=ExecutionSimulator(ExecutionConfig(half_spread=0.10))
        )
        result = runner.run(
            strategy=_BuyOnceHoldStrategy("AAPL", volume=10),
            data=data,
            initial_cash=10_000.0,
        )
        # Buy fills at 100.10, position marked to close (100). Cash = 10_000 - 1001 = 8_999.
        # Final: cash 8_999 + position (10 * 120) = 10_199. Net spread cost = 1.00.
        assert result.final_equity == pytest.approx(10_199.0)

    def test_commission_is_deducted_as_cash_flow(self):
        from market_lab.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
        from market_lab.backtest.engine.runner import Runner

        data = {"AAPL": _ohlcv([100.0, 110.0, 120.0])}
        runner = Runner(
            executor=ExecutionSimulator(ExecutionConfig(commission_per_unit=0.01))
        )
        result = runner.run(
            strategy=_BuyOnceHoldStrategy("AAPL", volume=100),
            data=data,
            initial_cash=10_000.0,
        )
        # Buy 100 @ 100 no spread; commission = 100 * 0.01 = 1.00.
        # Cash = 10_000 - 10_000 - 1 = -1. Position value = 100 * 120 = 12_000.
        # Equity = -1 + 12_000 = 11_999. No-cost baseline would be 12_000.
        assert result.final_equity == pytest.approx(11_999.0)
        assert result.fills[0].commission == pytest.approx(1.0)

    def test_runner_raises_on_order_for_missing_bar(self):
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
            Order,
        )
        from market_lab.backtest.engine.runner import Runner

        data = {"AAPL": _ohlcv([100.0, 110.0])}

        class OrdersForMSFT:
            def on_bar(self, bars, portfolio, context):
                return [Order("MSFT", side="buy", volume=1)]

        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        with pytest.raises(ValueError, match="MSFT"):
            runner.run(strategy=OrdersForMSFT(), data=data, initial_cash=10_000.0)

    def test_swap_model_debits_each_bar_for_open_position(self):
        from market_lab.backtest.engine.execution import (
            ExecutionConfig,
            ExecutionSimulator,
            SwapModel,
        )
        from market_lab.backtest.engine.runner import Runner

        # 3 bars at price 100. Hold 10 shares → notional 1000/day. Swap 0.001 = $1/day.
        data = {"AAPL": _ohlcv([100.0, 100.0, 100.0])}
        runner = Runner(
            executor=ExecutionSimulator(ExecutionConfig()),
            swap_model=SwapModel(long_rate_per_day=0.001),
        )
        result = runner.run(
            strategy=_BuyOnceHoldStrategy("AAPL", volume=10),
            data=data,
            initial_cash=10_000.0,
        )
        # Day 1: buy @ 100. Swap charged same day (held at EOD). Cash = 9_000 - 1 = 8_999.
        # Day 2: swap again = 8_998. Day 3: swap again = 8_997.
        # Position value = 10*100 = 1000. Equity = 8_997 + 1000 = 9_997.
        assert result.final_equity == pytest.approx(9_997.0)

    def test_runner_skips_timestamps_with_no_bars(self):
        """Symbol A has bar at T1, symbol B at T2 — Runner calls strategy for both ts."""
        from market_lab.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
        from market_lab.backtest.engine.runner import Runner

        df_a = _ohlcv([100.0], start="2024-01-02")  # just T1
        df_b = _ohlcv([200.0], start="2024-01-03")  # just T2
        data = {"A": df_a, "B": df_b}

        seen_ts: list = []

        class RecordTs:
            def on_bar(self, bars, portfolio, context):
                seen_ts.append((list(bars.keys()), len(bars)))
                return []

        runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
        runner.run(strategy=RecordTs(), data=data, initial_cash=10_000.0)

        # Two distinct timestamps, each has one bar.
        assert len(seen_ts) == 2
        assert seen_ts[0] == (["A"], 1)
        assert seen_ts[1] == (["B"], 1)
