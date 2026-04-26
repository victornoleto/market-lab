"""DXY trend-slope macro stream — gold long-only regime gate.

Gold's persistent inverse coupling with the trade-weighted USD is well
documented; the relationship is *regime-dependent* (Pukthuanthong-Roll
2011 *J Banking Finance*) and strengthens during sustained USD downtrends
(Capie-Mills-Wood 2005 *J Int Fin Markets*). This module exposes a
binary gate that fires when DXY's 200-day moving average has fallen over
the past 20 trading days — a slope-based "DXY in sustained falling
regime" indicator distinct from the level-vs-MA grammar that GS-5
closed.

Signal grammar:
  flag[t] = 1  iff  SMA_200(DXY)[t]  <  SMA_200(DXY)[t - 20]

Used by `studies/gold_swing_loop/iterations/015-*/run_backtest.py`.

Citations
---------
* `[stocks_on_the_move, p.100]` — 200-day SMA canonical trend filter
* `[trading_systems_methods, p.13-14]` — gold/USD inverse coupling
* `[ilmanen_expected_returns, ch.10]` — gold as USD-cycle hedge
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def dxy_sma_falling_flag(
    dxy: pd.Series,
    *,
    sma_window: int = 200,
    slope_lookback: int = 20,
) -> pd.Series:
    """Binary flag: 1 iff SMA_w(DXY)[t] < SMA_w(DXY)[t - slope_lookback].

    Warmup spans ``sma_window + slope_lookback - 1`` bars (filled with 0).
    Equality returns 0 (strict less-than per hypothesis).
    """
    sma = dxy.rolling(window=sma_window, min_periods=sma_window).mean()
    lagged = sma.shift(slope_lookback)
    flag = (sma < lagged).astype(int)
    flag = flag.where(lagged.notna(), 0).astype(int)
    flag.name = "dxy_sma_falling_flag"
    return flag


def dxy_sma_falling_flag_numpy(
    dxy: np.ndarray,
    *,
    sma_window: int = 200,
    slope_lookback: int = 20,
) -> np.ndarray:
    """Hand-rolled numpy reference for cross-lib parity (G7 gate)."""
    n = len(dxy)
    out = np.zeros(n, dtype=np.int64)
    if n < sma_window + slope_lookback:
        return out
    cumsum = np.concatenate(([0.0], np.cumsum(dxy)))
    for i in range(sma_window - 1, n):
        sma_now = (cumsum[i + 1] - cumsum[i + 1 - sma_window]) / sma_window
        j = i - slope_lookback
        if j < sma_window - 1:
            continue
        sma_lag = (cumsum[j + 1] - cumsum[j + 1 - sma_window]) / sma_window
        out[i] = 1 if sma_now < sma_lag else 0
    return out


def align_signal_to_index(
    signal: pd.Series, target_index: pd.DatetimeIndex
) -> pd.Series:
    """Reindex a daily signal to a target bar index using forward-fill.

    Pre-signal bars (target dates before the first signal date) are filled
    with 0 (no signal yet, no position).
    """
    if not isinstance(target_index, pd.DatetimeIndex):
        target_index = pd.DatetimeIndex(target_index)
    signal = signal.sort_index()
    aligned = signal.reindex(target_index, method="ffill")
    aligned = aligned.fillna(0).astype(int)
    aligned.name = signal.name or "signal"
    return aligned


def dxy_position(
    dxy: pd.Series,
    target_index: pd.DatetimeIndex,
    *,
    sma_window: int = 200,
    slope_lookback: int = 20,
) -> pd.Series:
    """Long-only position vector aligned to ``target_index``.

    1.0 when DXY's SMA is in falling regime, else 0.0.
    """
    flag_daily = dxy_sma_falling_flag(
        dxy, sma_window=sma_window, slope_lookback=slope_lookback
    )
    flag_aligned = align_signal_to_index(flag_daily, target_index)
    return flag_aligned.astype(float).rename("position")


__all__ = [
    "dxy_sma_falling_flag",
    "dxy_sma_falling_flag_numpy",
    "align_signal_to_index",
    "dxy_position",
]
