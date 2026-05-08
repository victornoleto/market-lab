"""Vol-targeted leverage scaling — Carver canonical formulation.

Compute realised annualised vol of a signal asset (e.g., SPY) and scale
exposure to a leveraged underlying (SSO, UPRO) so that portfolio vol
tracks a target level. Bounded weights in [weight_min, weight_max] with
T+1 execution lag (no peek-ahead).

Citations:
  - [systematic_trading, ch.10] Carver — vol-targeting canonical:
    ``position_size = target_vol / realised_vol``.
  - [advances_fin_ml, p.31-34] factor framework — vol as a state
    variable distinct from trend signal.
  - [risk_parity, ch.5, p.10] Carlson — capital-efficient stacking
    achievable via dynamic weight on leveraged underlying.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def realized_vol(
    returns: pd.Series,
    window: int = 60,
    annualization: int = 252,
) -> pd.Series:
    """Annualised rolling standard deviation of returns.

    Args:
        returns: daily returns Series of the signal asset (e.g., SPY).
        window: lookback in trading days (default 60).
        annualization: trading days per year for sqrt-time scaling.

    Returns:
        Series of annualised vol; pre-window observations are NaN.
    """
    return returns.rolling(window=window, min_periods=window).std() * np.sqrt(
        annualization
    )


def vol_target_weight(
    realised_vol_signal: pd.Series,
    target_vol_annual: float,
    underlying_factor: float = 1.0,
    weight_min: float = 0.0,
    weight_max: float = 1.0,
    lag_days: int = 1,
) -> pd.Series:
    """Carver canonical weight on the underlying for vol-targeting.

    ``weight_t = clip(target_vol / (underlying_factor × realised_vol_t),
    weight_min, weight_max)``, then shifted by ``lag_days`` for T+1
    execution.

    Carver canonical (`[systematic_trading, ch.10]`) defines
    ``leverage = target_vol / realised_vol``. Because our underlying is
    a leveraged ETF (SSO 2×, UPRO 3×), we translate that leverage to a
    portfolio weight by dividing by the underlying's nominal leverage
    factor: ``weight = leverage / factor``. The remaining
    ``(1 − weight)`` goes to cash.

    Args:
        realised_vol_signal: annualised realised vol of the signal asset
            (e.g., SPY). Computed with :func:`realized_vol`.
        target_vol_annual: target portfolio vol level (e.g., 0.20 = 20%).
        underlying_factor: leverage factor of the underlying asset
            (1.0 raw, 2.0 SSO, 3.0 UPRO).
        weight_min: minimum weight on underlying (default 0.0).
        weight_max: maximum weight on underlying (default 1.0).
        lag_days: T+1 execution lag (default 1).

    Returns:
        Series of weights aligned to ``realised_vol_signal.index``.
        Pre-window NaN (not yet observable) is filled with ``weight_min``.
    """
    raw_weight = target_vol_annual / (realised_vol_signal * underlying_factor)
    clipped = raw_weight.clip(lower=weight_min, upper=weight_max)
    return clipped.shift(lag_days).fillna(weight_min)


def vol_target_strategy_returns(
    underlying_returns: pd.Series,
    cash_returns: pd.Series,
    weight: pd.Series,
) -> pd.Series:
    """Daily strategy returns: weight × underlying + (1 − weight) × cash.

    Args:
        underlying_returns: daily returns of the leveraged underlying
            (e.g., SSO synth, UPRO synth).
        cash_returns: daily returns of the cash sleeve (e.g., IEF synth).
        weight: weight on underlying, T+1 lagged, in [0, 1].

    Returns:
        Daily strategy returns on the intersection of the three indices.
    """
    aligned = pd.concat(
        {"u": underlying_returns, "c": cash_returns, "w": weight},
        axis=1,
        sort=True,
    ).dropna()
    return aligned["w"] * aligned["u"] + (1.0 - aligned["w"]) * aligned["c"]
