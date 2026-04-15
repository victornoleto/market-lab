"""Tests for the Ehlers Band-Pass Swing Trader strategy.

Strategy rules verbatim from [cycle_analytics, ch.17, p.220-226]:

1. Preprocessing: ``close → roofing_filter(hp, lp)`` [p.88-89].
2. DCP: ``dominant_cycle_period(roofed)`` [p.82-83].
3. Band-pass: ``band_pass(roofed, dcp, pct_of_dcp)`` [p.152-153].
4. AGC-normalize the BP to ±1 for the oscillator [p.54-55, ch.5].
5. Entry (anticipatory, [p.220-221]): long when osc crosses below
   ``lower_threshold``; short when osc crosses above ``upper_threshold``.
6. Exit safety valve ([p.224-225]): close beyond a SuperSmoother-smoothed
   trend; time-stop at ½·DCP bars if not profitable.
7. Stop-loss ([p.225-226]): fixed % guard against extreme losses.

All tests use synthetic OHLCV; no network.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _ohlcv_from_close(close: pd.Series, spread_bps: float = 1.0) -> pd.DataFrame:
    """Build a tight OHLCV frame from a close series.

    Open = prior close; High/Low = ±spread around close; Volume constant.
    Keeps the backtest engine happy without drifting the signal.
    """
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
    period: int = 20,
    amplitude: float = 5.0,
    baseline: float = 100.0,
    freq: str = "B",
) -> pd.Series:
    idx = pd.date_range("2020-01-01", periods=n, freq=freq)
    t = np.arange(n)
    return pd.Series(baseline + amplitude * np.sin(2 * np.pi * t / period), index=idx)


def _trend_close(n: int = 1000, slope: float = 0.05) -> pd.Series:
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.Series(100.0 + slope * np.arange(n), index=idx)


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
        from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

        close = _sine_close(n=500, period=20)
        data = {"^GSPC": _ohlcv_from_close(close)}

        strat = EhlersBPSwingStrategy(data=data, symbol="^GSPC")

        ind = strat._indicators["^GSPC"]
        assert set(ind.columns) >= {"smooth", "dcp", "bp", "osc", "trend"}
        assert len(ind) == len(close)
        # AGC-normalized oscillator is bounded in [-1, 1].
        assert ind["osc"].abs().max() <= 1.0 + 1e-9

    def test_rejects_invalid_thresholds(self):
        from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

        close = _sine_close(n=200)
        data = {"^GSPC": _ohlcv_from_close(close)}
        with pytest.raises(ValueError):
            EhlersBPSwingStrategy(
                data=data, symbol="^GSPC",
                upper_threshold=0.5, lower_threshold=0.6,  # inverted
            )

    def test_rejects_invalid_stop_pct(self):
        from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

        close = _sine_close(n=200)
        data = {"^GSPC": _ohlcv_from_close(close)}
        with pytest.raises(ValueError):
            EhlersBPSwingStrategy(data=data, symbol="^GSPC", stop_pct=-0.01)


# ---------------------------------------------------------------------------
# Signal behavior
# ---------------------------------------------------------------------------


class TestSignals:
    def test_pure_sine_generates_trades(self):
        """A clean cyclic signal must trigger at least some long/short entries."""
        from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

        close = _sine_close(n=2000, period=20, amplitude=5.0)
        data = {"^GSPC": _ohlcv_from_close(close)}

        strat = EhlersBPSwingStrategy(data=data, symbol="^GSPC")
        result = _run_strategy(strat, data)

        assert len(result.trades) > 5, (
            f"expected multiple round-trips on clean 20-bar sine, got "
            f"{len(result.trades)}"
        )
        sides = {t.side for t in result.trades}
        # Both long and short should fire for a symmetric sine.
        assert "long" in sides
        assert "short" in sides

    def test_pure_trend_generates_no_entries(self):
        """Spectral Dilation rejection: a DC+trend input should not trade.

        The roofing filter strips DC and low-frequency trend; the BPF sees
        near-zero input → osc stays near zero → no threshold crosses.
        """
        from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

        close = _trend_close(n=1200, slope=0.1)
        data = {"^GSPC": _ohlcv_from_close(close)}

        strat = EhlersBPSwingStrategy(data=data, symbol="^GSPC")
        result = _run_strategy(strat, data)

        # A couple of warm-up transients are tolerable; a real trend should
        # produce far fewer trades than a cyclic regime.
        assert len(result.trades) <= 2

    def test_stop_loss_fires_on_adverse_move(self):
        """After long entry, a ≥ stop_pct drop triggers exit next bar.

        Construct a regime that (1) generates a long entry at some ts, then
        (2) drops below ``entry_price · (1 - stop_pct)``. Verify the
        resulting trade's loss ≈ stop_pct (within slippage).
        """
        from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

        # 1000 bars of sine (cycles → entries), then a hard drop.
        cycle = 100 + 5 * np.sin(2 * np.pi * np.arange(1000) / 20)
        drop = np.linspace(cycle[-1], cycle[-1] * 0.80, 200)  # -20% over 200 bars
        close = pd.Series(
            np.concatenate([cycle, drop]),
            index=pd.date_range("2020-01-01", periods=1200, freq="B"),
        )
        data = {"^GSPC": _ohlcv_from_close(close)}

        strat = EhlersBPSwingStrategy(
            data=data, symbol="^GSPC", stop_pct=0.05,
        )
        result = _run_strategy(strat, data)

        longs = [t for t in result.trades if t.side == "long"]
        assert longs, "expected at least one long trade"
        # If any long was held into the drop, its exit price should not be
        # worse than stop_pct below the entry — modulo one-bar slippage.
        worst = min(longs, key=lambda t: t.pnl)
        loss_pct = (worst.exit_price - worst.entry_price) / worst.entry_price
        # Stop-loss engages when close < entry·(1-stop_pct); exit on the
        # bar AFTER the trigger, so the realized loss can exceed -stop_pct
        # by at most one bar's decline — we allow 3× headroom conservatively.
        assert loss_pct >= -3 * 0.05


class TestHoldingTime:
    def test_median_holding_not_ridiculous_on_cyclic_data(self):
        """Sanity: on a 20-bar sine, holding time should be a few bars,
        not hundreds. This catches regression where exits stop firing.
        """
        from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

        close = _sine_close(n=2000, period=20)
        data = {"^GSPC": _ohlcv_from_close(close)}

        strat = EhlersBPSwingStrategy(data=data, symbol="^GSPC")
        result = _run_strategy(strat, data)

        if not result.trades:
            pytest.skip("no trades — other tests already cover the case")

        holdings = [
            (t.exit_time - t.entry_time).days for t in result.trades
        ]
        # One DCP is 20 bars ≈ 28 calendar days (weekday-only). Trades
        # longer than 3× DCP would mean the exit logic is broken.
        median_held = float(np.median(holdings))
        assert median_held < 3 * 28


# ---------------------------------------------------------------------------
# Total-return adjustment (regression — adj_close fix)
# ---------------------------------------------------------------------------


class TestTotalReturnAdjustment:
    def test_dividend_drops_absorbed_in_indicator_input(self):
        """Pre-fix: quarterly ex-dividend drops appear as price shocks that
        the Roofing Filter cannot fully cancel, spiking the AGC oscillator.
        Post-fix: ``adjust_ohlc`` rescales OHLC to the adj_close base, so a
        constant-price-with-dividends stock has a flat indicator series.
        """
        from ai_trade.backtest.strategies.ehlers_bp_swing import (
            EhlersBPSwingStrategy,
        )

        n = 400
        idx = pd.date_range("2020-01-01", periods=n, freq="B")
        base = 400.0
        raw_close = np.full(n, base, dtype=float)
        for d in (60, 125, 190, 255, 320):
            raw_close[d:] -= 1.50  # quarterly $1.50 dividend
        adj_close = np.full(n, base)  # adjusted series is flat

        df = pd.DataFrame(
            {
                "open": raw_close,
                "high": raw_close + 0.5,
                "low": raw_close - 0.5,
                "close": raw_close,
                "adj_close": adj_close,
                "volume": np.full(n, 1e8),
            },
            index=idx,
        )
        strat = EhlersBPSwingStrategy(data={"SPY": df}, symbol="SPY")
        osc = strat._indicators["SPY"]["osc"].dropna()
        # Flat adjusted price → near-zero oscillator. Allow some numerical
        # ringing from the IIR filters but nowhere near ±0.7 entry thresholds.
        assert osc.abs().max() < 0.3, f"osc spike at {osc.abs().max():.3f}"

    def test_fixture_without_adj_close_still_works(self):
        """Synthetic fixtures built via ``_ohlcv_from_close`` (no adj_close
        column) must keep functioning — adjust_ohlc no-ops on missing column.
        """
        from ai_trade.backtest.strategies.ehlers_bp_swing import (
            EhlersBPSwingStrategy,
        )

        close = _sine_close(n=500, period=20)
        data = {"^GSPC": _ohlcv_from_close(close)}  # no adj_close
        strat = EhlersBPSwingStrategy(data=data, symbol="^GSPC")

        # Indicators computed successfully; close series unchanged.
        pd.testing.assert_series_equal(
            strat.data["^GSPC"]["close"].reset_index(drop=True),
            close.reset_index(drop=True),
            check_names=False,
        )
