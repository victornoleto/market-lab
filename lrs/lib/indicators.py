"""Risk-on confirmation gates for the LRS Phase 3A sparse vote.

Each gate is an *additional* boolean filter ANDed onto the Phase 2 base signal
(`underlying.shift(1) > SMA200.shift(1)` plus a realized-vol throttle). The goal
is to test, one structurally distinct mechanism family at a time, whether a
single confirmation filter improves the risk/return frontier without opening a
broad multi-indicator grid `[trading_systems_methods, p.939]`,
`[advances_fin_ml, p.208-211]`.

Conventions (shared with `lrs/lib/backtest.build_sma_signal` and the Phase 2
`vol_gate`):
  - Every gate returns a daily ``pd.Series[bool]`` aligned to the price index.
  - The decision on day ``t`` uses information known at the *previous* close: the
    raw indicator is computed on prices through ``t`` then ``.shift(1)``-lagged so
    no same-bar lookahead leaks into execution `[testing_tuning, p.327-335]`.
  - Warmup (and any NaN) maps to ``False`` (risk-off), matching the base signal.

This module is intentionally self-contained (no import from ``studies/``) so the
``lrs/`` restart stays independent. ``clenow_score`` mirrors the implementation in
``studies/_shared/signals.py`` (same book formula).

Citations:
  - SMA regime base: `[leverage_for_the_long_run, p.13]`
  - Clenow adjusted slope (annualized exp-regression slope x R^2):
    `[stocks_on_the_move, p.70-77, p.82, p.98]`
  - Simple momentum / ROC (momentum effect): `[stocks_on_the_move, p.58, p.60]`
  - Hysteresis band (asymmetric entry/exit to filter whipsaws):
    `[trading_systems_methods, p.383]`
  - ADX / Wilder Directional Movement (trend strength):
    `[trading_systems_methods, p.387]`
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _lagged_bool(series: pd.Series, index: pd.Index) -> pd.Series:
    """Shift one bar (no lookahead), reindex to ``index``, warmup/NaN -> False."""
    return series.shift(1).reindex(index).fillna(False).astype(bool)


def clenow_score(prices: pd.Series, window: int = 90) -> pd.Series:
    """Clenow ranking score = annualized exp-regression slope x R^2.

    Per `[stocks_on_the_move, p.70-77, p.98]`: linear regression of ``log(price)``
    over ``window`` days; ``slope`` is annualized as ``(exp(slope))**250 - 1`` and
    multiplied by R^2 so choppy/gappy trends are penalized. Higher = cleaner,
    stronger uptrend. ``250`` matches Clenow's Excel form `[p.77]`.
    """

    def _score(x: np.ndarray) -> float:
        if len(x) < window or np.any(x <= 0):
            return np.nan
        log_x = np.log(x)
        t = np.arange(len(log_x), dtype=float)
        slope, intercept = np.polyfit(t, log_x, 1)
        y_pred = slope * t + intercept
        ss_res = float(np.sum((log_x - y_pred) ** 2))
        ss_tot = float(np.sum((log_x - log_x.mean()) ** 2))
        if ss_tot == 0.0:
            return 0.0
        r_squared = 1.0 - ss_res / ss_tot
        annualized = (np.exp(slope)) ** 250 - 1.0
        return float(annualized * r_squared)

    return prices.rolling(window=window, min_periods=window).apply(_score, raw=True)


def clenow_gate(prices: pd.Series, window: int = 90) -> pd.Series:
    """Risk-on only when the underlying's Clenow trend score is positive.

    Confirms a positive, well-fit (slope x R^2) trend before taking levered
    exposure `[stocks_on_the_move, p.76, p.98]`.
    """
    score = clenow_score(prices, window)
    return _lagged_bool(score > 0.0, prices.index)


def roc_gate(prices: pd.Series, lookback: int = 126) -> pd.Series:
    """Risk-on only when ``lookback``-day rate of change is positive.

    Simple medium-term momentum confirmation; the momentum effect (a rising
    series tends to keep rising) is documented in `[stocks_on_the_move, p.58,
    p.60]`. Structurally distinct from the SMA *level* gate.
    """
    roc = prices.pct_change(lookback)
    return _lagged_bool(roc > 0.0, prices.index)


def trend_hysteresis_gate(
    prices: pd.Series,
    lookback: int = 200,
    band: float = 0.05,
) -> pd.Series:
    """Asymmetric SMA band to damp whipsaw at the trend boundary.

    State machine: enter the trend when ``price > SMA(lookback)``; stay in the
    trend until ``price < SMA(lookback) * (1 - band)``. The wider exit threshold
    requires price to penetrate the opposite side before flipping, the classic
    whipsaw filter `[trading_systems_methods, p.383]`. The base SMA level is
    Gayed's regime rule `[leverage_for_the_long_run, p.13]`.

    The raw state is computed on same-bar values then ``.shift(1)``-lagged, so
    execution never uses the current close.
    """
    if not 0.0 <= band < 1.0:
        raise ValueError(f"band must be in [0, 1); got {band}")
    sma = prices.rolling(window=lookback, min_periods=lookback).mean()
    upper = sma.to_numpy(dtype=float)
    lower = (sma * (1.0 - band)).to_numpy(dtype=float)
    px = prices.to_numpy(dtype=float)
    state = np.zeros(len(px), dtype=bool)
    in_trend = False
    for i in range(len(px)):
        if np.isnan(upper[i]):
            in_trend = False
            state[i] = False
            continue
        if in_trend:
            if px[i] < lower[i]:
                in_trend = False
        elif px[i] > upper[i]:
            in_trend = True
        state[i] = in_trend
    raw = pd.Series(state, index=prices.index)
    return _lagged_bool(raw, prices.index)


def adx_close_only(prices: pd.Series, window: int = 14) -> pd.Series:
    """Close-only approximation of Wilder's ADX trend-strength indicator.

    LIMITATION: a true Wilder ADX `[trading_systems_methods, p.387]` needs the
    intraday high/low/close. The Testfol.io cache stores a single close-equivalent
    equity curve per ticker, so this is a DEGRADED PROXY. With ``high = low =
    close`` the true range collapses to ``|dclose|`` and +DM/-DM become the
    positive/negative parts of the close-to-close change. The result reduces to a
    Wilder-smoothed directional-efficiency measure,
    ``ADX = EWMA( 100 * |EWMA(dclose)| / EWMA(|dclose|) )`` (range 0-100): high
    when moves persist in one direction, low when they alternate. Useful as a
    relative trend-strength confirmation, but any ADX-driven conclusion is weaker
    than the gates that do not need OHLC.
    """
    close = prices.astype(float)
    delta = close.diff()
    true_range = delta.abs()
    plus_dm = delta.clip(lower=0.0)
    minus_dm = (-delta).clip(lower=0.0)
    alpha = 1.0 / window  # Wilder smoothing (RMA)
    atr = true_range.ewm(alpha=alpha, min_periods=window, adjust=False).mean()
    plus_sm = plus_dm.ewm(alpha=alpha, min_periods=window, adjust=False).mean()
    minus_sm = minus_dm.ewm(alpha=alpha, min_periods=window, adjust=False).mean()
    atr_safe = atr.replace(0.0, np.nan)
    plus_di = 100.0 * plus_sm / atr_safe
    minus_di = 100.0 * minus_sm / atr_safe
    di_sum = (plus_di + minus_di).replace(0.0, np.nan)
    dx = 100.0 * (plus_di - minus_di).abs() / di_sum
    return dx.ewm(alpha=alpha, min_periods=window, adjust=False).mean()


def adx_gate(prices: pd.Series, window: int = 14, threshold: float = 20.0) -> pd.Series:
    """Risk-on only when close-only ADX exceeds ``threshold``.

    Trend-strength confirmation layered on the directional SMA gate (price is
    already above SMA200 when this is evaluated), so a high ADX means the existing
    uptrend is strong `[trading_systems_methods, p.387]`. See ``adx_close_only``
    for the close-only data caveat.
    """
    adx = adx_close_only(prices, window)
    return _lagged_bool(adx > threshold, prices.index)
