"""Tests for EhlersMetaStrategy (AFML meta-labeling wrapper on Ehlers BP).

Focus: the wiring between Ehlers primary events, triple-barrier labels,
and the RandomForest secondary model. Correctness of the individual
pieces is covered by :mod:`test_ehlers_bp_swing` and :mod:`test_meta_*`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.ehlers_meta import EhlersMetaStrategy


# ---------------------------------------------------------------------------
# Fixtures (mirror test_ehlers_bp_swing.py)
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
    period: int = 20,
    amplitude: float = 5.0,
    baseline: float = 100.0,
) -> pd.Series:
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    t = np.arange(n)
    return pd.Series(baseline + amplitude * np.sin(2 * np.pi * t / period), index=idx)


def _run(strategy, data, cash: float = 100_000.0):
    from ai_trade.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
    from ai_trade.backtest.engine.runner import Runner

    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    return runner.run(strategy, data, initial_cash=cash)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_rejects_invalid_p_act_threshold(self):
        close = _sine_close(n=600)
        data = {"SPY": _ohlcv_from_close(close)}
        with pytest.raises(ValueError):
            EhlersMetaStrategy(data=data, symbol="SPY", p_act_threshold=1.5)

    def test_rejects_invalid_train_fraction(self):
        close = _sine_close(n=600)
        data = {"SPY": _ohlcv_from_close(close)}
        with pytest.raises(ValueError):
            EhlersMetaStrategy(data=data, symbol="SPY", train_fraction=0.0)

    def test_events_detected_on_cyclic_data(self):
        close = _sine_close(n=1500, period=20, amplitude=5.0)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = EhlersMetaStrategy(data=data, symbol="SPY")
        # Clean 20-bar sine should produce a healthy batch of crossings.
        assert len(strat.events) >= 20

    def test_train_cutoff_respects_train_fraction(self):
        close = _sine_close(n=1500, period=20)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = EhlersMetaStrategy(data=data, symbol="SPY", train_fraction=0.5)
        events = strat.events
        assert strat.train_cutoff is not None
        n_train = int(len(events) * 0.5)
        assert strat.train_cutoff == events.iloc[:n_train].index[-1]


# ---------------------------------------------------------------------------
# Meta-label filter behavior
# ---------------------------------------------------------------------------


class TestFilterBehavior:
    def test_filter_active_reduces_trades_vs_threshold_zero(self):
        """Rising ``p_act_threshold`` monotonically cannot INCREASE trade count.

        Same data, same Ehlers params; only ``p_act_threshold`` varies.
        With threshold 0.0 every post-train event fires; with 0.99 almost
        nothing does. Number of trades strictly decreases or stays equal.
        """
        close = _sine_close(n=1500, period=20, amplitude=5.0)
        data = {"SPY": _ohlcv_from_close(close)}

        strat_open = EhlersMetaStrategy(
            data=data, symbol="SPY", p_act_threshold=0.0,
        )
        result_open = _run(strat_open, data)

        strat_strict = EhlersMetaStrategy(
            data=data, symbol="SPY", p_act_threshold=0.99,
        )
        result_strict = _run(strat_strict, data)

        assert len(result_strict.trades) <= len(result_open.trades)

    def test_p_act_series_is_aligned_with_events(self):
        close = _sine_close(n=1500, period=20)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = EhlersMetaStrategy(data=data, symbol="SPY")
        if not strat.filter_active:
            pytest.skip("filter disabled on this fixture — nothing to check")
        assert strat.p_act is not None
        assert strat.p_act.name == "p_act"
        assert (strat.p_act.index == strat.events.index).all()
        assert ((strat.p_act >= 0.0) & (strat.p_act <= 1.0)).all()

    def test_filter_disabled_when_events_too_few(self):
        """Short series → few events → filter bypasses and trades like primary."""
        close = _sine_close(n=300, period=20)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = EhlersMetaStrategy(
            data=data, symbol="SPY", min_train_events=10_000,
        )
        assert not strat.filter_active

    def test_no_trades_occur_inside_training_window(self):
        """All executed trades must start AFTER train_cutoff."""
        close = _sine_close(n=1500, period=20)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = EhlersMetaStrategy(
            data=data, symbol="SPY", p_act_threshold=0.0,
        )
        if not strat.filter_active:
            pytest.skip("filter disabled — training split not enforced")
        result = _run(strat, data)
        cutoff = strat.train_cutoff
        for trade in result.trades:
            assert pd.Timestamp(trade.entry_time) > cutoff


# ---------------------------------------------------------------------------
# Exit parity with primary (filter does NOT touch exits)
# ---------------------------------------------------------------------------


class TestExitParity:
    def test_stop_loss_still_fires_after_entry(self):
        """Filter controls entries only. Exit logic is the primary's —
        stop_loss must still kick in on an adverse move post-entry."""
        cycle = 100 + 5 * np.sin(2 * np.pi * np.arange(1200) / 20)
        drop = np.linspace(cycle[-1], cycle[-1] * 0.80, 200)
        close = pd.Series(
            np.concatenate([cycle, drop]),
            index=pd.date_range("2020-01-01", periods=1400, freq="B"),
        )
        data = {"SPY": _ohlcv_from_close(close)}

        strat = EhlersMetaStrategy(
            data=data, symbol="SPY",
            p_act_threshold=0.0,
            stop_pct=0.05,
        )
        result = _run(strat, data)

        if not result.trades:
            pytest.skip("no trades fired on this regime")
        longs = [t for t in result.trades if t.side == "long"]
        if longs:
            worst = min(longs, key=lambda t: t.pnl)
            loss_pct = (
                (worst.exit_price - worst.entry_price) / worst.entry_price
            )
            # Stop + one-bar slippage, give headroom.
            assert loss_pct >= -3 * 0.05


# ---------------------------------------------------------------------------
# adjust_ohlc pass-through (regression — same fix as primary)
# ---------------------------------------------------------------------------


class TestTotalReturnAdjustment:
    def test_fixture_without_adj_close_works(self):
        close = _sine_close(n=800, period=20)
        data = {"SPY": _ohlcv_from_close(close)}
        strat = EhlersMetaStrategy(data=data, symbol="SPY")
        # Smoke: no crash, indicators computed.
        ind = strat._indicators["SPY"]
        assert set(ind.columns) >= {"osc", "dcp", "atr20", "regime"}
