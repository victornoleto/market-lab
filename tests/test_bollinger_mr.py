"""Tests for the Bollinger Mean-Reversion strategy.

Strategy rules from [algo_trading_chan, p.28-30, ch.2] and
[machine_trading, p.204-205, ch.7]:

1. Compute MA(window) and rolling σ(window).
2. Lower band = MA - mult × σ.
3. Long entry when close < lower band.
4. Exit when close ≥ MA, or after max_hold bars, or stop-loss hit.
5. Long-only (no shorts) per [algo_trading_chan, p.30, ch.2].

All tests use synthetic OHLCV; no network.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _ohlcv_from_close(close: pd.Series, spread_bps: float = 1.0) -> pd.DataFrame:
    close = close.astype(float)
    half = close * spread_bps * 1e-4
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame(
        {
            "open": open_,
            "high": close + half,
            "low": close - half,
            "close": close,
            "volume": 1_000_000.0,
        },
        index=close.index,
    )


def _sine_close(
    n: int = 1500,
    period: int = 40,
    amplitude: float = 5.0,
    baseline: float = 100.0,
    freq: str = "h",
) -> pd.Series:
    idx = pd.date_range("2021-01-01", periods=n, freq=freq)
    t = np.arange(n)
    return pd.Series(baseline + amplitude * np.sin(2 * np.pi * t / period), index=idx)


def _trend_close(n: int = 1000, slope: float = 0.05, freq: str = "h") -> pd.Series:
    idx = pd.date_range("2021-01-01", periods=n, freq=freq)
    return pd.Series(100.0 + slope * np.arange(n), index=idx)


def _dip_and_recover(
    n_warmup: int = 100,
    n_dip: int = 10,
    n_recover: int = 50,
    baseline: float = 100.0,
    dip_depth: float = 8.0,
    freq: str = "h",
) -> pd.Series:
    """Flat → sharp dip → recover to baseline."""
    warmup = np.full(n_warmup, baseline)
    dip = np.linspace(baseline, baseline - dip_depth, n_dip)
    recover = np.linspace(baseline - dip_depth, baseline, n_recover)
    values = np.concatenate([warmup, dip, recover])
    idx = pd.date_range("2021-01-01", periods=len(values), freq=freq)
    return pd.Series(values, index=idx)


def _run_strategy(strategy, data: dict[str, pd.DataFrame], cash: float = 100_000.0):
    from ai_trade.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
    from ai_trade.backtest.engine.runner import Runner

    executor = ExecutionSimulator(ExecutionConfig())
    runner = Runner(executor=executor)
    return runner.run(strategy, data, initial_cash=cash)


# ---------------------------------------------------------------------------
# Construction / basic contract
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_precomputes_indicators_on_init(self):
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=500, period=40)
        data = {"SPY": _ohlcv_from_close(close)}

        strat = BollingerMRStrategy(data=data, symbol="SPY", window=20)

        ind = strat._indicators["SPY"]
        assert set(ind.columns) >= {"ma", "std", "lower_band"}
        assert len(ind) == len(close)

    def test_rejects_invalid_stop_pct(self):
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=200)
        data = {"SPY": _ohlcv_from_close(close)}
        with pytest.raises(ValueError):
            BollingerMRStrategy(data=data, symbol="SPY", stop_pct=-0.01)

    def test_rejects_invalid_window(self):
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=200)
        data = {"SPY": _ohlcv_from_close(close)}
        with pytest.raises(ValueError):
            BollingerMRStrategy(data=data, symbol="SPY", window=1)

    def test_rejects_invalid_std_mult(self):
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=200)
        data = {"SPY": _ohlcv_from_close(close)}
        with pytest.raises(ValueError):
            BollingerMRStrategy(data=data, symbol="SPY", std_mult=0)

    def test_rejects_missing_symbol(self):
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=200)
        data = {"SPY": _ohlcv_from_close(close)}
        with pytest.raises(KeyError):
            BollingerMRStrategy(data=data, symbol="MISSING")


# ---------------------------------------------------------------------------
# Signal behavior
# ---------------------------------------------------------------------------


class TestSignals:
    def test_cyclic_data_generates_long_trades(self):
        """A sine wave dipping below the lower band should trigger long entries."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=2000, period=40, amplitude=5.0)
        data = {"SPY": _ohlcv_from_close(close)}

        strat = BollingerMRStrategy(data=data, symbol="SPY", window=20, std_mult=1.5)
        result = _run_strategy(strat, data)

        assert len(result.trades) > 3, (
            f"expected multiple round-trips on cyclic data, got {len(result.trades)}"
        )
        # Long-only strategy: all trades should be long.
        sides = {t.side for t in result.trades}
        assert sides == {"long"}, f"expected only long trades, got {sides}"

    def test_pure_uptrend_generates_no_entries(self):
        """A monotonic uptrend never dips below the lower band → no trades."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _trend_close(n=1200, slope=0.1)
        data = {"SPY": _ohlcv_from_close(close)}

        strat = BollingerMRStrategy(data=data, symbol="SPY", window=20, std_mult=2.0)
        result = _run_strategy(strat, data)

        assert len(result.trades) == 0

    def test_dip_and_recover_triggers_profitable_trade(self):
        """A dip below the lower band followed by recovery should produce
        at least one profitable long trade."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _dip_and_recover(
            n_warmup=100, n_dip=10, n_recover=50,
            baseline=100.0, dip_depth=8.0,
        )
        data = {"SPY": _ohlcv_from_close(close)}

        strat = BollingerMRStrategy(
            data=data, symbol="SPY", window=20, std_mult=1.5,
        )
        result = _run_strategy(strat, data)

        profitable = [t for t in result.trades if t.pnl > 0]
        assert len(profitable) >= 1, (
            f"expected at least one profitable trade on dip+recover, "
            f"got {len(profitable)} profitable out of {len(result.trades)} total"
        )

    def test_stop_loss_fires_on_continued_decline(self):
        """After long entry on a dip, continued decline triggers stop-loss."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        # Warm up then crash continuously — no recovery.
        n_warmup = 100
        n_crash = 200
        warmup = np.full(n_warmup, 100.0)
        crash = np.linspace(100.0, 70.0, n_crash)  # -30% crash
        values = np.concatenate([warmup, crash])
        idx = pd.date_range("2021-01-01", periods=len(values), freq="h")
        close = pd.Series(values, index=idx)
        data = {"SPY": _ohlcv_from_close(close)}

        strat = BollingerMRStrategy(
            data=data, symbol="SPY", window=20, std_mult=1.5, stop_pct=0.02,
        )
        result = _run_strategy(strat, data)

        if result.trades:
            # Any trade entered during the crash should be stopped out.
            worst = min(result.trades, key=lambda t: t.pnl)
            loss_pct = (worst.exit_price - worst.entry_price) / worst.entry_price
            # Stop-loss at 2% — allow 3× headroom for one-bar slippage.
            assert loss_pct >= -3 * 0.02


class TestHoldingTime:
    def test_time_stop_limits_holding(self):
        """Trades should never exceed max_hold bars."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=2000, period=40, amplitude=5.0)
        data = {"SPY": _ohlcv_from_close(close)}

        max_hold = 24
        strat = BollingerMRStrategy(
            data=data, symbol="SPY", window=20, std_mult=1.5, max_hold=max_hold,
        )
        result = _run_strategy(strat, data)

        if not result.trades:
            pytest.skip("no trades — other tests already cover the case")

        for trade in result.trades:
            # On 1h data, each bar = 1 hour. Allow slight overshoot due to
            # the exit happening on the bar AFTER the condition is met.
            held_bars = (trade.exit_time - trade.entry_time).total_seconds() / 3600
            assert held_bars <= max_hold + 2, (
                f"trade held {held_bars:.0f} bars, exceeds max_hold={max_hold}"
            )


# ---------------------------------------------------------------------------
# Total-return adjustment
# ---------------------------------------------------------------------------


class TestTotalReturnAdjustment:
    def test_fixture_without_adj_close_still_works(self):
        """Synthetic fixtures (no adj_close) must keep functioning."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=500, period=40)
        data = {"SPY": _ohlcv_from_close(close)}  # no adj_close
        strat = BollingerMRStrategy(data=data, symbol="SPY")

        pd.testing.assert_series_equal(
            strat.data["SPY"]["close"].reset_index(drop=True),
            close.reset_index(drop=True),
            check_names=False,
        )


# ---------------------------------------------------------------------------
# Grid config
# ---------------------------------------------------------------------------


class TestBollingerMRGridConfig:
    def test_grid_returns_4_configs(self):
        from ai_trade.backtest.grid.bollinger_mr_config import bollinger_mr_grid_configs

        configs = bollinger_mr_grid_configs()
        assert len(configs) == 4

    def test_configs_are_frozen(self):
        from ai_trade.backtest.grid.bollinger_mr_config import bollinger_mr_grid_configs

        cfg = bollinger_mr_grid_configs()[0]
        with pytest.raises(AttributeError):
            cfg.window = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Direction: short and both [machine_trading, p.204-205, ch.7]
# ---------------------------------------------------------------------------


def _spike_and_drop(
    n_warmup: int = 100,
    n_spike: int = 10,
    n_drop: int = 50,
    baseline: float = 100.0,
    spike_height: float = 8.0,
    freq: str = "h",
) -> pd.Series:
    """Flat → sharp spike → drop back to baseline. Mirrors _dip_and_recover."""
    warmup = np.full(n_warmup, baseline)
    spike = np.linspace(baseline, baseline + spike_height, n_spike)
    drop = np.linspace(baseline + spike_height, baseline, n_drop)
    values = np.concatenate([warmup, spike, drop])
    idx = pd.date_range("2021-01-01", periods=len(values), freq=freq)
    return pd.Series(values, index=idx)


class TestDirectionParam:
    def test_default_direction_is_long(self):
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=200)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = BollingerMRStrategy(data=data, symbol="SPY")
        assert strat.direction == "long"

    def test_rejects_invalid_direction(self):
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=200)
        data = {"SPY": _ohlcv_from_close(close)}
        with pytest.raises(ValueError, match="direction"):
            BollingerMRStrategy(data=data, symbol="SPY", direction="invalid")

    def test_upper_band_computed(self):
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=500, period=40)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = BollingerMRStrategy(data=data, symbol="SPY", window=20)
        ind = strat._indicators["SPY"]
        assert "upper_band" in ind.columns

    def test_short_direction_generates_short_trades_on_spike(self):
        """A spike above the upper band should trigger short entry."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _spike_and_drop(n_warmup=100, n_spike=10, n_drop=50,
                                baseline=100.0, spike_height=8.0)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = BollingerMRStrategy(
            data=data, symbol="SPY", window=20, std_mult=1.5, direction="short",
        )
        result = _run_strategy(strat, data)

        short_trades = [t for t in result.trades if t.side == "short"]
        assert len(short_trades) >= 1, (
            f"expected short trade on spike+drop, got {len(short_trades)}"
        )

    def test_short_direction_no_long_trades(self):
        """direction='short' must never produce long trades."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=2000, period=40, amplitude=5.0)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = BollingerMRStrategy(
            data=data, symbol="SPY", window=20, std_mult=1.5, direction="short",
        )
        result = _run_strategy(strat, data)
        long_trades = [t for t in result.trades if t.side == "long"]
        assert len(long_trades) == 0, f"short-only produced {len(long_trades)} long trades"

    def test_both_direction_generates_long_and_short(self):
        """direction='both' on cyclic data generates both long and short trades."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=2000, period=40, amplitude=5.0)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = BollingerMRStrategy(
            data=data, symbol="SPY", window=20, std_mult=1.5, direction="both",
        )
        result = _run_strategy(strat, data)

        sides = {t.side for t in result.trades}
        assert "long" in sides, "both should produce long trades on cyclic data"
        assert "short" in sides, "both should produce short trades on cyclic data"

    def test_long_direction_unchanged_behavior(self):
        """direction='long' must produce identical results to default."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        close = _sine_close(n=2000, period=40, amplitude=5.0)
        data = {"SPY": _ohlcv_from_close(close)}

        strat_default = BollingerMRStrategy(data=data, symbol="SPY", window=20, std_mult=1.5)
        strat_long = BollingerMRStrategy(
            data=data, symbol="SPY", window=20, std_mult=1.5, direction="long",
        )

        res_default = _run_strategy(strat_default, data)
        res_long = _run_strategy(strat_long, data)

        assert len(res_default.trades) == len(res_long.trades)
        assert abs(res_default.final_equity - res_long.final_equity) < 0.01

    def test_short_stop_loss_fires_on_continued_rise(self):
        """After short entry on a spike, continued rise should trigger stop-loss."""
        from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

        n_warmup = 100
        n_rise = 200
        warmup = np.full(n_warmup, 100.0)
        rise = np.linspace(100.0, 130.0, n_rise)  # +30% continuous rise
        values = np.concatenate([warmup, rise])
        idx = pd.date_range("2021-01-01", periods=len(values), freq="h")
        close = pd.Series(values, index=idx)
        data = {"SPY": _ohlcv_from_close(close)}

        strat = BollingerMRStrategy(
            data=data, symbol="SPY", window=20, std_mult=1.5,
            stop_pct=0.02, direction="short",
        )
        result = _run_strategy(strat, data)

        if result.trades:
            for trade in result.trades:
                assert trade.side == "short"
                # Short loss: entry < exit. Stop loss at 2%.
                loss_pct = (trade.exit_price - trade.entry_price) / trade.entry_price
                assert loss_pct <= 3 * 0.02, (
                    f"short stop loss exceeded 3× headroom: {loss_pct:.4f}"
                )
