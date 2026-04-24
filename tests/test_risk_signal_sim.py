"""Tests for the risk-signal de-leveraging overlay simulator (Phase 2)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
    simulate_regime_threshold_with_legs,
)
from ai_trade.backtest.strategies.stop_loss_and_risk_signals import (
    RiskSignalConfig,
    RiskSignalResult,
    simulate_with_risk_signal,
)


def _bull_path(n: int = 400) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Monotone bull — regime stays +1 the whole time."""
    idx = pd.date_range("2005-01-03", periods=n, freq="B")
    prices = np.linspace(100.0, 300.0, n)
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
    daily = fee / 252.0
    return leverage * returns - daily


class TestRiskSignalConfigValidation:
    def test_lambda_in_unit_interval(self):
        RiskSignalConfig(indicator_type="composite", lambda_de_lever=0.0)
        RiskSignalConfig(indicator_type="composite", lambda_de_lever=1.0)
        with pytest.raises(ValueError, match="lambda_de_lever"):
            RiskSignalConfig(indicator_type="composite", lambda_de_lever=-0.1)
        with pytest.raises(ValueError, match="lambda_de_lever"):
            RiskSignalConfig(indicator_type="composite", lambda_de_lever=1.5)

    def test_indicator_type_must_be_known(self):
        for name in ("ebp", "term_spread", "cape", "vix", "composite"):
            RiskSignalConfig(indicator_type=name, lambda_de_lever=0.3)
        with pytest.raises(ValueError, match="indicator_type"):
            RiskSignalConfig(indicator_type="moon_phase", lambda_de_lever=0.3)


class TestLambdaZeroMatchesBaseline:
    def test_no_delever_equals_base_sim(self):
        prices, rets, cash = _bull_path()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        risk = pd.Series(0.5, index=rets.index)  # non-zero risk, but λ=0 zeros it

        base = simulate_regime_threshold_with_legs(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
        )
        out = simulate_with_risk_signal(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg, risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.0,
            ),
        )
        pd.testing.assert_series_equal(base.equity, out.equity, check_names=False)


class TestDeleveringReducesExposure:
    def test_constant_high_risk_reduces_bull_cagr(self):
        """With λ=0.5 and risk=0.8, effective leverage = 0.6 × base on every bar.

        In a monotone bull, equity should grow less than baseline.
        """
        prices, rets, cash = _bull_path()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        risk = pd.Series(0.8, index=rets.index)

        base = simulate_regime_threshold_with_legs(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
        )
        out = simulate_with_risk_signal(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg, risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.5,
            ),
        )
        assert out.equity.iloc[-1] < base.equity.iloc[-1], (
            f"de-levered equity should be lower than baseline in a bull; "
            f"got base={base.equity.iloc[-1]:.3f} vs de-levered={out.equity.iloc[-1]:.3f}"
        )


class TestWarmupRiskIsHandledAsZero:
    def test_nan_risk_treated_as_no_delever(self):
        prices, rets, cash = _bull_path()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)

        # Risk series: NaN for first 200 bars, then 0.0 (no risk).
        risk = pd.Series(np.nan, index=rets.index)
        risk.iloc[200:] = 0.0

        base = simulate_regime_threshold_with_legs(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg,
        )
        out = simulate_with_risk_signal(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg, risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.8,
            ),
        )
        # Both risk=NaN (warmup) and risk=0 (active) leave leverage unchanged
        # → result must match baseline.
        pd.testing.assert_series_equal(base.equity, out.equity, check_names=False)


class TestEffectivePositionTrace:
    def test_result_exposes_effective_position(self):
        prices, rets, cash = _bull_path()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)
        risk = pd.Series(0.5, index=rets.index)

        out = simulate_with_risk_signal(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg, risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=0.4,
            ),
        )
        # At each bar during bull, effective_position should be
        # max(0, 1 − 0.4 × 0.5) = 0.8.
        # Only after warmup where regime is established.
        post_warmup = out.effective_position.dropna()
        bull_bars = post_warmup[out.regime.loc[post_warmup.index] == 1]
        # Allow NaN from initial warmup; in bull bars, pos must equal 0.8.
        assert abs(bull_bars.iloc[-1] - 0.8) < 1e-9


class TestFullDeleverageFloorsAtZero:
    def test_lambda_one_and_risk_one_gives_zero_position(self):
        """Position must be clamped to 0, never negative."""
        prices, rets, cash = _bull_path()
        cfg = _base_cfg()
        buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)
        risk = pd.Series(1.0, index=rets.index)

        out = simulate_with_risk_signal(
            signal_prices=prices, buy_leg_returns=buy,
            sell_leg_returns=cash, cfg=cfg, risk_series=risk,
            risk_cfg=RiskSignalConfig(
                indicator_type="composite", lambda_de_lever=1.0,
            ),
        )
        bull_bars = out.effective_position.dropna()
        assert (bull_bars >= 0).all()
        assert abs(bull_bars.iloc[-1] - 0.0) < 1e-9
