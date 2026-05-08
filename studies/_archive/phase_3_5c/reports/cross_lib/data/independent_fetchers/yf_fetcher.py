"""yfinance fetcher for Stage 2 independent-data runs.

Returns long-format DataFrame with same schema as reference_prices.parquet:
columns = [date, ticker, open, high, low, close, volume].
"""
from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_yf(
    tickers: list[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    """Download daily OHLCV via yfinance. Raises FileNotFoundError if missing."""
    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
    )
    if data.empty:
        raise FileNotFoundError(f"yfinance returned empty for {tickers} {start}:{end}")

    frames = []
    for ticker in tickers:
        if ticker not in data.columns.levels[0]:
            continue
        sub = data[ticker].reset_index().rename(columns={"Date": "date"})
        sub.columns = [c.lower() for c in sub.columns]
        sub["ticker"] = ticker
        frames.append(sub[["date", "ticker", "open", "high", "low", "close", "volume"]])

    if not frames:
        raise FileNotFoundError(f"yfinance returned no rows for tickers {tickers}")
    return pd.concat(frames, ignore_index=True)
