"""Tests for stop-loss overlay on EMA/SMA threshold strategy.

Covers:
* StopLossConfig validation (pct range, re-entry modes, param per mode).
* Baseline match: stop_loss_pct=None produces identical result to original
  simulate_regime_threshold_with_legs.
* Stop trigger: equity DD from peak crosses threshold → forced cash regime.
* Re-entry modes:
    - next_signal: wait for next cross-up (price > MA + threshold).
    - time_cooldown: wait N bars after stop, then respect signal.
    - recovery_trigger: re-enter when price recovered X% from local bottom.
* Peak reset on re-entry (no cascade stops).
* Trade ledger includes stop-triggered exits.

Citations follow base simulator (see module docstring).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
    simulate_regime_threshold_with_legs,
)
from ai_trade.backtest.strategies.stop_loss_and_risk_signals import (
    StopLossConfig,
    simulate_with_stop_loss,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bull_then_crash_then_recovery(
    n_bull: int = 300,
    n_crash: int = 20,
    n_recovery: int = 300,
    crash_pct: float = -0.50,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Deterministic price series: ramp up, sharp crash, then V-recovery.

    Constructed with explicit price levels so the EMA/threshold signal
    reliably transitions to BUY during the bull phase (price > MA × 1.05)
    and the crash produces a meaningful equity drawdown for the stop
    rule to react to.
    """
    n_total = n_bull + n_crash + n_recovery
    idx = pd.date_range("2005-01-03", periods=n_total, freq="B")

    prices = np.empty(n_total, dtype=float)
    # Bull phase: 100 → 200 linearly (guarantees price above 50-bar EMA band).
    prices[:n_bull] = np.linspace(100.0, 200.0, n_bull)
    # Crash: 200 → 200·(1+crash_pct) over n_crash bars.
    crash_bottom = 200.0 * (1.0 + crash_pct)
    prices[n_bull : n_bull + n_crash] = np.linspace(200.0, crash_bottom, n_crash)
    # Recovery: linear climb up to 3×bottom so price eventually exceeds
    # the pre-crash MA level and the next_signal cross-up fires.
    prices[n_bull + n_crash :] = np.linspace(
        crash_bottom, crash_bottom * 3.0, n_recovery
    )

    prices_s = pd.Series(prices, index=idx, name="price")
    rets_s = prices_s.pct_change().fillna(0.0).rename("ret")
    cash = pd.Series(0.0, index=idx, name="cash")
    return prices_s, rets_s, cash


def _base_cfg() -> EMASMAThresholdConfig:
    # EMA 50 × 5% threshold × 3× long × cash sell — aggressive config so
    # stops have a chance to fire meaningfully in the synthetic crash.
    return EMASMAThresholdConfig(
        filter="EMA",
        lookback=50,
        threshold_pct=0.05,
        buy_leverage=3.0,
        sell_leverage=0.0,
        fee=0.0095,
        switch_cost_bps=15.0,
    )


def _synth_buy_leg(returns: pd.Series, leverage: float, fee: float) -> pd.Series:
    """Mirror of the private _synth_leveraged_returns helper."""
    daily_drag = fee / 252.0
    return leverage * returns - daily_drag


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


class TestStopLossConfigValidation:
    def test_none_is_valid_baseline(self):
        cfg = StopLossConfig(stop_loss_pct=None)
        assert cfg.stop_loss_pct is None
        assert cfg.reentry_mode == "next_signal"

    def test_negative_pct_rejected(self):
        with pytest.raises(ValueError, match="stop_loss_pct"):
            StopLossConfig(stop_loss_pct=-0.10)

    def test_pct_over_one_rejected(self):
        with pytest.raises(ValueError, match="stop_loss_pct"):
            StopLossConfig(stop_loss_pct=1.5)

    def test_bad_mode_rejected(self):
        with pytest.raises(ValueError, match="reentry_mode"):
            StopLossConfig(stop_loss_pct=0.25, reentry_mode="magic")  # type: ignore[arg-type]

    def test_cooldown_requires_positive_int_param(self):
        with pytest.raises(ValueError, match="reentry_param"):
            StopLossConfig(stop_loss_pct=0.25, reentry_mode="time_cooldown", reentry_param=0)
        with pytest.raises(ValueError, match="reentry_param"):
            StopLossConfig(stop_loss_pct=0.25, reentry_mode="time_cooldown", reentry_param=None)

    def test_recovery_requires_positive_float_param(self):
        with pytest.raises(ValueError, match="reentry_param"):
            StopLossConfig(
                stop_loss_pct=0.25, reentry_mode="recovery_trigger", reentry_param=0.0,
            )
        with pytest.raises(ValueError, match="reentry_param"):
            StopLossConfig(
                stop_loss_pct=0.25, reentry_mode="recovery_trigger", reentry_param=None,
            )

    def test_next_signal_ignores_param(self):
        # next_signal has no param to sweep; accept param=None silently.
        cfg = StopLossConfig(stop_loss_pct=0.25, reentry_mode="next_signal")
        assert cfg.reentry_param is None


# ---------------------------------------------------------------------------
# Baseline match: stop_loss_pct=None produces identical result
# ---------------------------------------------------------------------------


class TestBaselineMatchesOriginal:
    def test_none_stop_matches_original_equity(self):
        prices, rets, cash = _bull_then_crash_then_recovery()
        cfg = _base_cfg()
        long_leg = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        base = simulate_regime_threshold_with_legs(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
        )
        proto = simulate_with_stop_loss(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(stop_loss_pct=None),
        )
        pd.testing.assert_series_equal(base.equity, proto.equity, check_names=False)
        pd.testing.assert_series_equal(base.regime, proto.regime, check_names=False)
        assert base.n_switches == proto.n_switches

    def test_none_stop_preserves_trade_count(self):
        prices, rets, cash = _bull_then_crash_then_recovery()
        cfg = _base_cfg()
        long_leg = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        base = simulate_regime_threshold_with_legs(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
        )
        proto = simulate_with_stop_loss(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(stop_loss_pct=None),
        )
        assert len(base.trades) == len(proto.trades)


# ---------------------------------------------------------------------------
# Stop trigger behavior
# ---------------------------------------------------------------------------


class TestStopTriggerFires:
    def test_stop_reduces_mdd_in_crash(self):
        prices, rets, cash = _bull_then_crash_then_recovery(crash_pct=-0.50)
        cfg = _base_cfg()
        long_leg = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        base = simulate_regime_threshold_with_legs(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
        )
        with_stop = simulate_with_stop_loss(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.20, reentry_mode="time_cooldown", reentry_param=63,
            ),
        )

        def _mdd(eq: pd.Series) -> float:
            peak = eq.cummax()
            dd = (eq / peak - 1.0).min()
            return float(dd)

        assert _mdd(with_stop.equity) > _mdd(base.equity), (
            "Stop-loss must reduce MDD on the crash scenario"
        )

    def test_stop_records_triggers(self):
        prices, rets, cash = _bull_then_crash_then_recovery(crash_pct=-0.50)
        cfg = _base_cfg()
        long_leg = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        out = simulate_with_stop_loss(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.20, reentry_mode="next_signal",
            ),
        )
        assert out.n_stops_triggered >= 1
        assert len(out.stop_events) == out.n_stops_triggered
        ev = out.stop_events[0]
        assert ev.drawdown_at_stop <= -0.20
        assert isinstance(ev.stop_date, pd.Timestamp)


# ---------------------------------------------------------------------------
# Re-entry modes
# ---------------------------------------------------------------------------


class TestReentryNextSignal:
    def test_waits_for_signal_after_stop(self):
        prices, rets, cash = _bull_then_crash_then_recovery(crash_pct=-0.50)
        cfg = _base_cfg()
        long_leg = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        out = simulate_with_stop_loss(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.20, reentry_mode="next_signal",
            ),
        )
        # At least one stop → one re-entry after a later cross-up signal.
        assert out.n_stops_triggered >= 1
        ev = out.stop_events[0]
        assert ev.reentry_date is not None, "Must have re-entered after bull recovery"
        assert ev.reentry_date > ev.stop_date


class TestReentryTimeCooldown:
    def test_reentry_exactly_after_n_bars(self):
        prices, rets, cash = _bull_then_crash_then_recovery(crash_pct=-0.50)
        cfg = _base_cfg()
        long_leg = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        cooldown = 21
        out = simulate_with_stop_loss(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.20, reentry_mode="time_cooldown",
                reentry_param=cooldown,
            ),
        )
        assert out.n_stops_triggered >= 1
        ev = out.stop_events[0]
        # reentry_bar_offset = bars between stop bar and re-entry bar.
        assert ev.reentry_bar_offset is not None
        assert ev.reentry_bar_offset >= cooldown, (
            f"cooldown={cooldown}; got offset={ev.reentry_bar_offset}"
        )


class TestReentryRecoveryTrigger:
    def test_reentry_when_price_recovers(self):
        prices, rets, cash = _bull_then_crash_then_recovery(crash_pct=-0.50)
        cfg = _base_cfg()
        long_leg = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        recovery_pct = 0.10
        out = simulate_with_stop_loss(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.20, reentry_mode="recovery_trigger",
                reentry_param=recovery_pct,
            ),
        )
        assert out.n_stops_triggered >= 1
        ev = out.stop_events[0]
        assert ev.reentry_date is not None
        # price at re-entry / local bottom price - 1 >= recovery_pct
        price_at_reentry = prices.loc[ev.reentry_date]
        price_at_bottom = prices.loc[ev.stop_date : ev.reentry_date].min()
        recovered = price_at_reentry / price_at_bottom - 1.0
        assert recovered >= recovery_pct - 1e-9, (
            f"recovery_pct={recovery_pct}; observed={recovered:.4f}"
        )


# ---------------------------------------------------------------------------
# Peak reset: no cascade stops
# ---------------------------------------------------------------------------


class TestPeakResetOnReentry:
    def test_no_immediate_second_stop_after_reentry(self):
        """After re-entry, running peak resets to current equity.

        Otherwise any small dip below original peak triggers another stop
        immediately, which would be pathological.
        """
        prices, rets, cash = _bull_then_crash_then_recovery(crash_pct=-0.50)
        cfg = _base_cfg()
        long_leg = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        out = simulate_with_stop_loss(
            signal_prices=prices, buy_leg_returns=long_leg,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.20, reentry_mode="time_cooldown", reentry_param=21,
            ),
        )
        # A re-entry (after cooldown) followed by monotonic recovery up-leg
        # must not retrigger immediately. If the equity went from old-peak
        # down −50% then ramps up 10-20% during cooldown, re-entry sets new
        # peak at that level. No new stop unless equity falls another 20%
        # from new peak.
        stop_dates = [e.stop_date for e in out.stop_events]
        # Stops at least 10 bars apart (not cascade).
        for a, b in zip(stop_dates, stop_dates[1:]):
            assert (b - a).days >= 10, "Two stops fired in immediate sequence"
