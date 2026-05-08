"""Cross-lib parity tests (G7) — pure-numpy vs vectorised pandas.

These guard against look-ahead / alignment bugs in the overlay
simulators. Requirement: CAGR diff ≤ 3 pp across a variety of
config / overlay combinations. ``[advances_fin_ml, p.31-34]``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.metrics.performance import cagr as _cagr
from market_lab.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
)
from market_lab.backtest.strategies.stop_loss_and_risk_signals import (
    RiskSignalConfig,
    StopLossConfig,
    simulate_with_stop_and_risk,
)
from market_lab.backtest.strategies.stop_loss_and_risk_signals_numpy import (
    simulate_with_stop_and_risk_numpy,
)


def _synthetic_dataset(seed: int = 1, n: int = 1000) -> tuple[pd.Series, pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2000-01-03", periods=n, freq="B")
    drift = 0.0004
    vol = 0.012
    rets = pd.Series(rng.normal(drift, vol, n), index=idx)
    prices = (1.0 + rets).cumprod() * 100.0
    cash = pd.Series(0.0, index=idx)
    return prices, rets, cash


def _cfg() -> EMASMAThresholdConfig:
    return EMASMAThresholdConfig(
        filter="EMA", lookback=100, threshold_pct=0.05,
        buy_leverage=3.0, sell_leverage=0.0,
        fee=0.0095, switch_cost_bps=15.0,
    )


def _synth_buy_leg(rets: pd.Series, leverage: float, fee: float) -> pd.Series:
    return leverage * rets - fee / 252.0


def _compare_cagr(ref_eq, np_eq, tolerance: float = 0.03) -> tuple[float, float, float]:
    ref_cagr = float(_cagr(ref_eq, 252))
    np_cagr = float(_cagr(np_eq, 252))
    return ref_cagr, np_cagr, abs(ref_cagr - np_cagr)


@pytest.mark.parametrize(
    "stop_cfg, lam, risk_value",
    [
        # No overlay: plain baseline equivalence.
        (StopLossConfig(stop_loss_pct=None), 0.0, 0.0),
        # Stop-only.
        (
            StopLossConfig(
                stop_loss_pct=0.25, reentry_mode="time_cooldown",
                reentry_param=21,
            ),
            0.0, 0.0,
        ),
        (
            StopLossConfig(
                stop_loss_pct=0.30, reentry_mode="next_signal",
            ),
            0.0, 0.0,
        ),
        (
            StopLossConfig(
                stop_loss_pct=0.20, reentry_mode="recovery_trigger",
                reentry_param=0.10,
            ),
            0.0, 0.0,
        ),
        # Signal-only.
        (StopLossConfig(stop_loss_pct=None), 0.5, 0.3),
        (StopLossConfig(stop_loss_pct=None), 0.7, 0.6),
        # Combined.
        (
            StopLossConfig(
                stop_loss_pct=0.20, reentry_mode="time_cooldown",
                reentry_param=21,
            ),
            0.5, 0.4,
        ),
        (
            StopLossConfig(
                stop_loss_pct=0.30, reentry_mode="recovery_trigger",
                reentry_param=0.10,
            ),
            0.5, 0.4,
        ),
    ],
)
def test_cross_lib_parity_cagr_within_3pp(stop_cfg, lam, risk_value):
    prices, rets, cash = _synthetic_dataset(seed=7, n=1500)
    cfg = _cfg()
    buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)
    risk = pd.Series(risk_value, index=rets.index)
    risk_cfg = RiskSignalConfig(indicator_type="composite", lambda_de_lever=lam)

    ref = simulate_with_stop_and_risk(
        signal_prices=prices, buy_leg_returns=buy,
        sell_leg_returns=cash, cfg=cfg,
        stop_cfg=stop_cfg, risk_series=risk, risk_cfg=risk_cfg,
    )
    np_eq = simulate_with_stop_and_risk_numpy(
        signal_prices=prices, buy_leg_returns=buy,
        sell_leg_returns=cash, cfg=cfg,
        stop_cfg=stop_cfg, risk_series=risk, risk_cfg=risk_cfg,
    )

    ref_c, np_c, diff = _compare_cagr(ref.equity, np_eq)
    assert diff <= 0.03, (
        f"cross-lib CAGR diff {diff:.4f} exceeds 3pp tolerance. "
        f"ref CAGR={ref_c:.4f}, numpy CAGR={np_c:.4f}, "
        f"stop={stop_cfg}, lam={lam}, risk={risk_value}"
    )


def test_cross_lib_parity_is_tight_for_baseline():
    """With no overlays the two implementations should match to ~0."""
    prices, rets, cash = _synthetic_dataset(seed=3, n=1200)
    cfg = _cfg()
    buy = _synth_buy_leg(rets, cfg.buy_leverage, cfg.fee)
    risk = pd.Series(0.0, index=rets.index)
    ref = simulate_with_stop_and_risk(
        signal_prices=prices, buy_leg_returns=buy,
        sell_leg_returns=cash, cfg=cfg,
        stop_cfg=StopLossConfig(stop_loss_pct=None),
        risk_series=risk,
        risk_cfg=RiskSignalConfig(indicator_type="composite", lambda_de_lever=0.0),
    )
    np_eq = simulate_with_stop_and_risk_numpy(
        signal_prices=prices, buy_leg_returns=buy,
        sell_leg_returns=cash, cfg=cfg,
        stop_cfg=StopLossConfig(stop_loss_pct=None),
        risk_series=risk,
        risk_cfg=RiskSignalConfig(indicator_type="composite", lambda_de_lever=0.0),
    )
    ref_c, np_c, diff = _compare_cagr(ref.equity, np_eq)
    # Baseline path goes through identical arithmetic once MA is computed
    # the same way → tolerance tighter than 0.5 pp.
    assert diff < 0.005, (
        f"baseline cross-lib diff {diff:.5f} is larger than expected "
        f"(ref={ref_c:.4f}, numpy={np_c:.4f})"
    )
