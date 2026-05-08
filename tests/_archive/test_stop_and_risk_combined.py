"""Tests for the combined stop-loss + risk-signal overlay simulator (Phase 3)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from market_lab.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
    simulate_regime_threshold_with_legs,
)
from market_lab.backtest.strategies.stop_loss_and_risk_signals import (
    RiskSignalConfig,
    StopLossConfig,
    StopAndRiskResult,
    simulate_with_risk_signal,
    simulate_with_stop_and_risk,
    simulate_with_stop_loss,
)


def _bull_path(n: int = 400) -> tuple[pd.Series, pd.Series, pd.Series]:
    idx = pd.date_range("2005-01-03", periods=n, freq="B")
    prices = np.linspace(100.0, 300.0, n)
    prices_s = pd.Series(prices, index=idx, name="price")
    rets = prices_s.pct_change().fillna(0.0)
    cash = pd.Series(0.0, index=idx)
    return prices_s, rets, cash


def _bull_then_crash(
    n_bull: int = 300, n_crash: int = 20, n_recovery: int = 300,
    crash_pct: float = -0.50,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    n_total = n_bull + n_crash + n_recovery
    idx = pd.date_range("2005-01-03", periods=n_total, freq="B")
    prices = np.empty(n_total)
    prices[:n_bull] = np.linspace(100.0, 200.0, n_bull)
    crash_bottom = 200.0 * (1.0 + crash_pct)
    prices[n_bull:n_bull + n_crash] = np.linspace(200.0, crash_bottom, n_crash)
    prices[n_bull + n_crash:] = np.linspace(
        crash_bottom, crash_bottom * 3.0, n_recovery
    )
    prices_s = pd.Series(prices, index=idx, name="price")
    rets = prices_s.pct_change().fillna(0.0)
    cash = pd.Series(0.0, index=idx)
    return prices_s, rets, cash


def _base_cfg() -> EMASMAThresholdConfig:
    return EMASMAThresholdConfig(
        filter="EMA", lookback=50, threshold_pct=0.05,
        buy_leverage=3.0, sell_leverage=0.0,
        fee=0.0095, switch_cost_bps=15.0,
    )


def _synth_buy_leg(returns: pd.Series, leverage: float, fee: float) -> pd.Series:
    return leverage * returns - fee / 252.0


class TestBaselineEquivalence:
    def test_no_overlays_matches_base_sim(self):
        prices, rets, cash = _bull_path()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)
        risk = pd.Series(0.5, index=rets.index)

        base = simulate_regime_threshold_with_legs(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
        )
        combined = simulate_with_stop_and_risk(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(stop_loss_pct=None),
            risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.0,
            ),
        )
        pd.testing.assert_series_equal(base.equity, combined.equity, check_names=False)


class TestStopDominatesRiskSignal:
    def test_stop_forces_position_zero_even_with_lambda_zero(self):
        prices, rets, cash = _bull_then_crash()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)
        risk = pd.Series(0.0, index=rets.index)  # no de-lever from signal

        # Stop-only reference
        stop_only = simulate_with_stop_loss(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.25, reentry_mode="time_cooldown",
                reentry_param=21,
            ),
        )
        combined = simulate_with_stop_and_risk(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.25, reentry_mode="time_cooldown",
                reentry_param=21,
            ),
            risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.0,
            ),
        )
        # λ=0 → risk signal inert → combined equals stop-only.
        pd.testing.assert_series_equal(
            stop_only.equity, combined.equity, check_names=False,
        )


class TestRiskSignalOnlyEquivalence:
    def test_stop_none_plus_lambda_matches_signal_only(self):
        prices, rets, cash = _bull_path()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)
        risk = pd.Series(0.6, index=rets.index)

        signal_only = simulate_with_risk_signal(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg, risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.5,
            ),
        )
        combined = simulate_with_stop_and_risk(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(stop_loss_pct=None),
            risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.5,
            ),
        )
        pd.testing.assert_series_equal(
            signal_only.equity, combined.equity, check_names=False,
        )


class TestBothOverlaysReduceMDD:
    def test_combined_beats_baseline_mdd(self):
        prices, rets, cash = _bull_then_crash()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        # Elevated risk throughout so signal de-leverages even before stop fires.
        risk = pd.Series(0.7, index=rets.index)

        base = simulate_regime_threshold_with_legs(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
        )
        combined = simulate_with_stop_and_risk(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.25, reentry_mode="time_cooldown",
                reentry_param=21,
            ),
            risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.5,
            ),
        )

        def _mdd(eq: pd.Series) -> float:
            peak = eq.cummax()
            return float((1.0 - eq / peak).max())

        assert _mdd(combined.equity) < _mdd(base.equity)


class TestResultExposesBothTraces:
    def test_stop_events_and_effective_position_both_present(self):
        prices, rets, cash = _bull_then_crash()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)
        risk = pd.Series(0.5, index=rets.index)

        combined = simulate_with_stop_and_risk(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
            stop_cfg=StopLossConfig(
                stop_loss_pct=0.20, reentry_mode="next_signal",
            ),
            risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.4,
            ),
        )
        assert isinstance(combined, StopAndRiskResult)
        assert combined.n_stops_triggered >= 1
        assert len(combined.stop_events) == combined.n_stops_triggered
        # Position trace non-empty
        assert len(combined.effective_position) == len(combined.equity)
        # When stopped, effective position should be 0.
        if combined.n_stops_triggered >= 1:
            ev = combined.stop_events[0]
            # Position at stop bar (right after trigger) must be 0.
            if ev.reentry_bar is not None:
                stopped_slice = combined.effective_position.iloc[
                    ev.stop_bar + 1 : ev.reentry_bar
                ]
                assert (stopped_slice == 0.0).all()
