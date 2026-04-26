"""DFII10 (10y TIPS yield) macro stream — gold long-only regime gate.

Gold's primary fundamental driver is the real interest rate. When real
rates are *falling* (DFII10 today < DFII10 60 trading days ago), gold's
opportunity cost is dropping and the macro regime is bullish for gold.
This module exposes the binary signal builder + a numpy reference for
G7 cross-lib parity, plus an alignment helper that propagates the daily
signal onto each gold dataset's bar index.

Used by `studies/gold_swing_loop/iterations/014-*/run_backtest.py`.

Citations
---------
* `[trading_systems_methods, p.13]` — metals are low-noise → trend-following with macro driver
* `[trading_systems_methods, p.285]` — quarterly = 60-63 trading days; matches macro horizon
* `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def dfii10_falling_flag(dfii10: pd.Series, *, lookback: int = 60) -> pd.Series:
    """Binary flag: 1 iff DFII10[t] < DFII10[t - lookback bars] (strict).

    Warmup (first ``lookback`` bars) is filled with 0.
    Equality returns 0 (strict less-than per hypothesis).
    """
    lagged = dfii10.shift(lookback)
    flag = (dfii10 < lagged).astype(int)
    flag = flag.where(lagged.notna(), 0).astype(int)
    flag.name = "dfii10_falling_flag"
    return flag


def dfii10_falling_flag_numpy(dfii10: np.ndarray, *, lookback: int = 60) -> np.ndarray:
    """Hand-rolled numpy reference for cross-lib parity (G7 gate)."""
    n = len(dfii10)
    out = np.zeros(n, dtype=np.int64)
    for i in range(lookback, n):
        if not np.isnan(dfii10[i]) and not np.isnan(dfii10[i - lookback]):
            out[i] = 1 if dfii10[i] < dfii10[i - lookback] else 0
    return out


def align_signal_to_index(signal: pd.Series, target_index: pd.DatetimeIndex) -> pd.Series:
    """Reindex a daily signal to a target bar index using forward-fill.

    Pre-signal bars (target dates before first signal date) are filled
    with 0 (no signal yet, no position).
    """
    if not isinstance(target_index, pd.DatetimeIndex):
        target_index = pd.DatetimeIndex(target_index)
    signal = signal.sort_index()
    aligned = signal.reindex(target_index, method="ffill")
    aligned = aligned.fillna(0).astype(int)
    aligned.name = signal.name or "signal"
    return aligned


def dfii10_position(
    dfii10: pd.Series, target_index: pd.DatetimeIndex, *, lookback: int = 60
) -> pd.Series:
    """Long-only position vector aligned to ``target_index``.

    1.0 when DFII10 is falling on the lookback window, else 0.0.
    """
    flag_daily = dfii10_falling_flag(dfii10, lookback=lookback)
    flag_aligned = align_signal_to_index(flag_daily, target_index)
    return flag_aligned.astype(float).rename("position")


__all__ = [
    "dfii10_falling_flag",
    "dfii10_falling_flag_numpy",
    "align_signal_to_index",
    "dfii10_position",
]
