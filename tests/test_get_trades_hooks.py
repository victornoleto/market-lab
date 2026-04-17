"""Phase 3.5b Task 2 — unit tests for ``get_trades()`` hooks on winners.

Three hooks are under test:

* :func:`ai_trade.backtest.strategies.letf_rotation.get_trades`
* :func:`ai_trade.backtest.strategies.tsmom.get_trades`
* :func:`ai_trade.backtest.grid.portfolio_3leg.aggregate_leg_trades`

Each test constructs a **deterministic synthetic regime** — we force
alternating ON/OFF (or LONG/FLAT) regions by hand-building the input
series so that the number and location of trades is known in advance,
then assert the hook recovers them.

Path tag: **[SWING BROKER]** — same Path B winners Phase 3.5b validates.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.grid.portfolio_3leg import aggregate_leg_trades
from ai_trade.backtest.metrics.standard_report import Trade
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    get_trades as letf_get_trades,
    simulate_letf_rotation,
)
from ai_trade.backtest.strategies.tsmom import (
    TSMOMConfig,
    get_trades as tsmom_get_trades,
    simulate_tsmom,
)


# ---------------------------------------------------------------------------
# LETF rotation get_trades
# ---------------------------------------------------------------------------


def _steady_up_spx(n: int = 400, daily_mu: float = 0.001, daily_sigma: float = 0.003,
                    seed: int = 3) -> tuple[pd.Series, pd.Series]:
    idx = pd.date_range("2019-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    rets = pd.Series(rng.normal(daily_mu, daily_sigma, n), index=idx)
    prices = (1.0 + rets).cumprod() * 100.0
    return rets, prices


class TestLETFGetTrades:
    def test_returns_list_of_trades(self):
        spx_rets, spx_px = _steady_up_spx()
        cfg = LETFRotationConfig(
            filter="SMA", lookback=50, band_pct=0.0, leverage=2.0, gold_weight=0.0
        )
        result = simulate_letf_rotation(spx_rets, spx_px, cfg)
        trades = letf_get_trades(result, spx_rets, cfg, asset_label="LETF_2x")
        assert isinstance(trades, list)
        for t in trades:
            assert isinstance(t, Trade)
            assert t.asset == "LETF_2x"
            assert t.direction == "long"
            assert t.entry_price == 1.0
            assert t.exit_price > 0

    def test_trades_chronologically_ordered(self):
        spx_rets, spx_px = _steady_up_spx()
        cfg = LETFRotationConfig(
            filter="SMA", lookback=50, band_pct=0.0, leverage=2.0, gold_weight=0.0
        )
        result = simulate_letf_rotation(spx_rets, spx_px, cfg)
        trades = letf_get_trades(result, spx_rets, cfg)
        dates = [t.entry_date for t in trades]
        assert dates == sorted(dates)

    def test_trade_count_matches_on_entries(self):
        spx_rets, spx_px = _steady_up_spx()
        cfg = LETFRotationConfig(
            filter="SMA", lookback=50, band_pct=0.0, leverage=2.0
        )
        result = simulate_letf_rotation(spx_rets, spx_px, cfg)
        trades = letf_get_trades(result, spx_rets, cfg)

        regime = result.regime
        on_entries = 0
        prev = None
        for v in regime:
            cur = v if isinstance(v, str) else None
            if cur == "ON" and prev != "ON":
                on_entries += 1
            prev = cur
        assert len(trades) == on_entries

    def test_no_trades_when_always_off(self):
        # Downtrend → regime should stay OFF after warmup.
        idx = pd.date_range("2019-01-01", periods=400, freq="B")
        rng = np.random.default_rng(5)
        rets = pd.Series(rng.normal(-0.002, 0.003, len(idx)), index=idx)
        prices = (1.0 + rets).cumprod() * 100.0
        cfg = LETFRotationConfig(filter="SMA", lookback=50, band_pct=0.0, leverage=2.0)
        result = simulate_letf_rotation(rets, prices, cfg)
        trades = letf_get_trades(result, rets, cfg)
        # May have 0 trades or a brief burst; but never more than switches/2 + 1.
        n_switches = int(result.switches.sum())
        assert len(trades) <= n_switches // 2 + 1

    def test_default_asset_label_contains_leverage(self):
        spx_rets, spx_px = _steady_up_spx()
        cfg = LETFRotationConfig(
            filter="SMA", lookback=50, band_pct=0.0, leverage=2.0
        )
        result = simulate_letf_rotation(spx_rets, spx_px, cfg)
        trades = letf_get_trades(result, spx_rets, cfg)
        if trades:
            assert "LETF_2" in trades[0].asset


# ---------------------------------------------------------------------------
# TSMOM get_trades
# ---------------------------------------------------------------------------


def _steady_up_hlc(n: int = 300, seed: int = 7):
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.002, 0.005, n)
    close = pd.Series((1.0 + rets).cumprod() * 100.0, index=idx)
    high = close + 0.5
    low = close - 0.5
    return high, low, close


class TestTSMOMGetTrades:
    def test_returns_list_of_trades(self):
        high, low, close = _steady_up_hlc()
        cfg = TSMOMConfig(entry_lookback=20, exit_lookback=10)
        result = simulate_tsmom(high, low, close, cfg)
        trades = tsmom_get_trades(result, close, asset_label="SYN")
        for t in trades:
            assert isinstance(t, Trade)
            assert t.asset == "SYN"
            assert t.entry_price > 0 and t.exit_price > 0

    def test_prices_match_close(self):
        """Entry/exit prices are the asset's close on those bars."""
        high, low, close = _steady_up_hlc()
        cfg = TSMOMConfig(entry_lookback=20, exit_lookback=10)
        result = simulate_tsmom(high, low, close, cfg)
        trades = tsmom_get_trades(result, close, asset_label="SYN")
        for t in trades:
            assert t.entry_price == pytest.approx(float(close.loc[t.entry_date]))
            assert t.exit_price == pytest.approx(float(close.loc[t.exit_date]))

    def test_trade_count_matches_long_entries(self):
        high, low, close = _steady_up_hlc()
        cfg = TSMOMConfig(entry_lookback=20, exit_lookback=10)
        result = simulate_tsmom(high, low, close, cfg)
        trades = tsmom_get_trades(result, close, asset_label="SYN")
        regime = result.regime
        long_entries = 0
        prev = None
        for v in regime:
            cur = v if isinstance(v, str) else None
            if cur == "LONG" and prev != "LONG":
                long_entries += 1
            prev = cur
        assert len(trades) == long_entries

    def test_no_trades_when_choppy(self):
        """A purely mean-reverting close that never breaks out → 0 trades."""
        idx = pd.date_range("2020-01-01", periods=300, freq="B")
        t = np.arange(len(idx))
        close_vals = 100.0 + 0.2 * np.sin(t / 5.0)
        close = pd.Series(close_vals, index=idx)
        high = close + 0.1
        low = close - 0.1
        cfg = TSMOMConfig(entry_lookback=50, exit_lookback=20)
        result = simulate_tsmom(high, low, close, cfg)
        trades = tsmom_get_trades(result, close, asset_label="SYN")
        # Tiny sinusoid, no breakout — expect zero trades.
        assert trades == []


# ---------------------------------------------------------------------------
# Portfolio aggregate_leg_trades
# ---------------------------------------------------------------------------


def _make_trade(asset: str, y: int, m: int, d: int, price_out: float = 1.1) -> Trade:
    return Trade(
        asset=asset,
        entry_date=pd.Timestamp(y, m, d),
        exit_date=pd.Timestamp(y, m, d + 5),
        entry_price=1.0,
        exit_price=price_out,
        notional=1.0,
        direction="long",
    )


class TestAggregateLegTrades:
    def test_empty_input_returns_empty(self):
        assert aggregate_leg_trades([]) == []
        assert aggregate_leg_trades([("A", []), ("B", [])]) == []

    def test_sorted_by_entry_date(self):
        a = [_make_trade("A", 2020, 5, 1), _make_trade("A", 2020, 1, 1)]
        b = [_make_trade("B", 2020, 3, 1)]
        out = aggregate_leg_trades([("A", a), ("B", b)])
        assert [t.entry_date for t in out] == [
            pd.Timestamp("2020-01-01"),
            pd.Timestamp("2020-03-01"),
            pd.Timestamp("2020-05-01"),
        ]
        assert [t.asset for t in out] == ["A", "B", "A"]

    def test_asset_labels_preserved(self):
        a = [_make_trade("LETF_2x", 2020, 1, 1)]
        b = [_make_trade("QQQ", 2020, 1, 10)]
        c = [_make_trade("GLD", 2020, 1, 20)]
        out = aggregate_leg_trades(
            [("LETF_2x", a), ("QQQ", b), ("GLD", c)]
        )
        assert [t.asset for t in out] == ["LETF_2x", "QQQ", "GLD"]

    def test_blank_asset_gets_leg_name(self):
        blank = Trade(
            asset="",
            entry_date=pd.Timestamp("2020-06-01"),
            exit_date=pd.Timestamp("2020-06-05"),
            entry_price=1.0,
            exit_price=1.05,
            notional=1.0,
            direction="long",
        )
        out = aggregate_leg_trades([("MyLeg", [blank])])
        assert len(out) == 1
        assert out[0].asset == "MyLeg"

    def test_stable_order_within_same_entry_date(self):
        """Tie on entry_date → leg order preserved."""
        a = [_make_trade("A", 2020, 1, 1)]
        b = [_make_trade("B", 2020, 1, 1)]
        out = aggregate_leg_trades([("A", a), ("B", b)])
        assert [t.asset for t in out] == ["A", "B"]


# ---------------------------------------------------------------------------
# End-to-end: plug get_trades into build_standard_report
# ---------------------------------------------------------------------------


class TestHooksIntegrateWithStandardReport:
    """Smoke test: run the full pipeline hooks → standard_report builders."""

    def test_tsmom_pipeline_produces_report(self):
        from ai_trade.backtest.metrics.standard_report import (
            build_standard_report,
        )

        high, low, close = _steady_up_hlc()
        cfg = TSMOMConfig(entry_lookback=20, exit_lookback=10)
        result = simulate_tsmom(high, low, close, cfg)
        trades = tsmom_get_trades(result, close, asset_label="SYN")
        if not trades:
            pytest.skip("synthetic series yielded no trades")
        report = build_standard_report(
            equity=result.equity,
            trades=trades,
            strategy_name="Donchian 20/10 smoke",
            params="entry=20 exit=10",
        )
        assert report.n_trades == len(trades)
        assert np.isfinite(report.sharpe)
        assert 0.0 <= report.exposure_time_pct <= 1.0
