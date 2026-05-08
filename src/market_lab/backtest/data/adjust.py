"""Total-return adjustment for OHLC series.

Both yfinance and Tiingo expose ``adj_close`` alongside raw ``close``:
``adj_close`` folds dividends and splits back into price history, so a 2-for-1
split no longer looks like a 50% crash and a $0.50 ex-div day no longer looks
like a shock. Strategies that detect cycles (Ehlers) or run regressions on
log-price (Clenow) MUST consume a total-return series — otherwise the
discontinuity at each corporate action fires spurious signals.

Ratio approach — preserves intra-bar shape, no-op when there are no events:

    ratio = adj_close / close          # == 1 when no div/split in period
    open, high, low, close = (o, h, l, c) * ratio
    adj_close untouched, volume untouched

Tolerance — when ``adj_close`` is absent (synthetic test fixtures), the
function returns the input unchanged. Production data always carries
``adj_close`` via the canonical loaders.
"""

from __future__ import annotations

import pandas as pd

_OHLC = ("open", "high", "low", "close")


def adjust_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with OHLC rescaled to the ``adj_close`` base.

    If ``adj_close`` is missing or identical to ``close`` the function
    returns a plain copy — the strategy's later reads of ``close`` then
    simply get the raw series, unchanged.
    """
    if df.empty or "adj_close" not in df.columns or "close" not in df.columns:
        return df.copy()
    out = df.copy()
    ratio = out["adj_close"] / out["close"].replace(0, pd.NA)
    ratio = ratio.fillna(1.0)
    for col in _OHLC:
        if col in out.columns:
            out[col] = (out[col].astype(float) * ratio).astype(float)
    return out
