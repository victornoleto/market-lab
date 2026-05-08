"""Per-asset volatility / liquidity metrics for the universe screener.

All functions take an OHLCV DataFrame with columns
``open, high, low, close, volume`` (the storage layout from
:class:`TiingoStorage`) and return a single float.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..helpers.momentum import atr as _atr_scalar

__all__ = [
    "atr_pct",
    "dollar_volume",
    "realized_vol_annualized",
]


def atr_pct(df: pd.DataFrame, *, lookback: int = 20) -> float:
    """Mean ATR(``lookback``) over the last ``lookback`` bars divided by
    mean close. Returned as a *fraction* (0.012 = 1.2%).

    Reuses :func:`ai_trade.backtest.helpers.momentum.atr` (Clenow's simple-mean
    ATR) so the screener stays consistent with sizing logic.

    Citation: ``[stocks_on_the_move, p.88]`` (Clenow uses ATR(20) as the
    canonical volatility proxy for sizing).
    """
    if len(df) < lookback + 1:
        raise ValueError(
            f"atr_pct: need >= {lookback + 1} bars, got {len(df)}"
        )
    a = _atr_scalar(df["high"], df["low"], df["close"], lookback=lookback)
    tail_close = df["close"].iloc[-lookback:].mean()
    if tail_close <= 0 or not np.isfinite(tail_close):
        raise ValueError("atr_pct: non-positive mean close")
    return float(a / tail_close)


def realized_vol_annualized(
    df: pd.DataFrame,
    *,
    lookback: int = 252,
    bars_per_year: int = 252,
) -> float:
    """Annualized std of log-returns over the last ``lookback`` bars.

    ``bars_per_year`` defaults to 252 for daily; override to 252*6.5≈1638
    for hourly equity if needed. Returned as a fraction (0.18 = 18%/yr).

    Citation: ``[volatility_trading]`` (Sinclair — close-to-close realized
    vol estimator, the simplest baseline).
    """
    if len(df) < lookback + 1:
        raise ValueError(
            f"realized_vol_annualized: need >= {lookback + 1} bars, got {len(df)}"
        )
    close = df["close"].iloc[-(lookback + 1):].astype(float)
    log_ret = np.diff(np.log(close.to_numpy()))
    sd = float(np.std(log_ret, ddof=1))
    return sd * float(np.sqrt(bars_per_year))


def dollar_volume(df: pd.DataFrame, *, lookback: int = 252) -> float:
    """Mean ``close * volume`` over the last ``lookback`` bars.

    Returns 0.0 when the volume column is identically zero or NaN (some
    Tiingo crypto/FX rows ship without a meaningful volume — the screener
    treats them as ``rank by vol = NaN`` and falls back to ATR%).

    Citation: ``[stocks_on_the_move, p.81]`` — Clenow filters S&P 500
    constituents by tradable dollar volume so impact stays bounded.
    """
    if len(df) < lookback:
        raise ValueError(
            f"dollar_volume: need >= {lookback} bars, got {len(df)}"
        )
    close = df["close"].iloc[-lookback:].astype(float)
    vol = df["volume"].iloc[-lookback:].astype(float).fillna(0.0)
    dv = (close * vol).mean()
    if not np.isfinite(dv):
        return 0.0
    return float(dv)
