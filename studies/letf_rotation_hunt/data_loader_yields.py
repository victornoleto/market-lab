"""Yield data sources for T5b carry forecast.

Loads constant-maturity Treasury yields (^IRX/^TNX/^TYX) and trailing
12m dividend yields for equity ETFs. Caches as parquet under
data/external/yields/.

Citations
---------
* spec §3.2 (docs/specs/2026-05-08-t5-expansion-design.md)
* yfinance ticker symbols ^IRX/^TNX/^TYX = 13w/10y/30y CMT
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_CACHE_DIR = Path("data/external/yields")
_TENOR_TO_TICKER = {"3m": "^IRX", "10y": "^TNX", "30y": "^TYX"}


def load_constant_maturity_yield(tenor: str) -> pd.Series:
    """Daily constant-maturity Treasury yield (decimal annual).

    Cache: data/external/yields/cmt_{tenor}.parquet.
    Source: yfinance ^IRX (3m) / ^TNX (10y) / ^TYX (30y).
    """
    if tenor not in _TENOR_TO_TICKER:
        raise ValueError(f"tenor must be one of {list(_TENOR_TO_TICKER)}, got {tenor!r}")
    ticker = _TENOR_TO_TICKER[tenor]
    cache_path = _CACHE_DIR / f"cmt_{tenor}.parquet"
    if cache_path.exists():
        return pd.read_parquet(cache_path).iloc[:, 0]
    series = _yfinance_fetch_yield(ticker).rename(tenor)
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    series.to_frame(name=tenor).to_parquet(cache_path)
    return series


def _yfinance_fetch_yield(ticker: str) -> pd.Series:
    """Fetch CMT yield from yfinance (decimal annual)."""
    import yfinance as yf  # local import: keep top-level light
    hist = yf.Ticker(ticker).history(period="max", auto_adjust=False)
    if hist.empty:
        raise RuntimeError(f"yfinance returned empty for {ticker}")
    # ^TNX etc. quote yield * 100 (e.g., 4.4 = 4.4%); convert to decimal
    return (hist["Close"] / 100.0).rename(ticker)
