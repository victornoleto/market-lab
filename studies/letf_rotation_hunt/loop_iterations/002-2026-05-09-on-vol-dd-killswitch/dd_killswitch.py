"""Vol-adjusted drawdown master-gate (kill switch) helper.

Local to iter 002 — not promoted to studies/letf_rotation_hunt/signals.py.

Mechanic [systematic_trading, p.212 ch.13]:
    sigma_price(t) = price(t) * sigma_21d_annual(t) * sqrt(21/252)
    rolling_peak(t) = price.rolling(window=252).max()
    drawdown_dollars(t) = rolling_peak(t) - price(t)
    raw_kill(t) = drawdown_dollars(t) > X * sigma_price(t)

Hysteresis (re-arm rule): once raw_kill fires, stay killed until
drawdown_dollars(t) <= 0.5 * X * sigma_price(t) (half-recovery), then re-arm.

For the absolute-percent variant (config 6):
    raw_kill(t) = (rolling_peak - price) / rolling_peak > pct_threshold
    re-arm when DD/peak <= 0.5 * pct_threshold.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def _realized_vol_annual(returns: pd.Series, window: int = 21) -> pd.Series:
    """Annualised realised vol from daily returns (rolling std × sqrt(252))."""
    return returns.rolling(window=window, min_periods=window).std() * np.sqrt(TRADING_DAYS)


def vol_adjusted_dd_killswitch(
    prices: pd.Series,
    returns: pd.Series,
    x_sigma: float,
    peak_window: int = 252,
    vol_window: int = 21,
    rearm_fraction: float = 0.5,
) -> pd.Series:
    """Return a 1.0/0.0 Series where 1.0 = "kill switch FIRED, force OFF".

    Sigma_price is per-21d (sigma_annual * sqrt(21/252)) per Carver
    [systematic_trading p.212]. Re-arm is hysteretic: once the kill fires,
    it stays fired until drawdown is below rearm_fraction * threshold.
    """
    aligned = pd.concat({"price": prices, "ret": returns}, axis=1).ffill().dropna()
    sigma_annual = _realized_vol_annual(aligned["ret"], window=vol_window)
    sigma_price = aligned["price"] * sigma_annual * np.sqrt(vol_window / TRADING_DAYS)
    rolling_peak = aligned["price"].rolling(window=peak_window, min_periods=peak_window).max()
    dd_dollars = rolling_peak - aligned["price"]
    threshold = x_sigma * sigma_price
    rearm = rearm_fraction * threshold

    out = pd.Series(0.0, index=aligned.index)
    state = 0.0  # 0 = armed (not killed), 1 = killed
    for t in aligned.index:
        thr_t = threshold.loc[t]
        rearm_t = rearm.loc[t]
        dd_t = dd_dollars.loc[t]
        if not (np.isfinite(thr_t) and np.isfinite(dd_t)):
            out.loc[t] = state
            continue
        if state == 0.0:
            if dd_t > thr_t:
                state = 1.0
        else:
            if dd_t <= rearm_t:
                state = 0.0
        out.loc[t] = state
    return out.rename(f"dd_kill_x{x_sigma:g}_pk{peak_window}_v{vol_window}")


def absolute_pct_dd_killswitch(
    prices: pd.Series,
    pct_threshold: float,
    peak_window: int = 252,
    rearm_fraction: float = 0.5,
) -> pd.Series:
    """Absolute-percent drawdown kill switch (config 6 sanity-check variant).

    raw_kill(t) = (peak - price) / peak > pct_threshold
    re-arm when (peak - price) / peak <= rearm_fraction * pct_threshold.
    """
    p = prices.ffill().dropna()
    rolling_peak = p.rolling(window=peak_window, min_periods=peak_window).max()
    dd_pct = (rolling_peak - p) / rolling_peak
    rearm = rearm_fraction * pct_threshold

    out = pd.Series(0.0, index=p.index)
    state = 0.0
    for t in p.index:
        dd_t = dd_pct.loc[t]
        if not np.isfinite(dd_t):
            out.loc[t] = state
            continue
        if state == 0.0:
            if dd_t > pct_threshold:
                state = 1.0
        else:
            if dd_t <= rearm:
                state = 0.0
        out.loc[t] = state
    return out.rename(f"dd_kill_pct{int(pct_threshold * 100):02d}_pk{peak_window}")
