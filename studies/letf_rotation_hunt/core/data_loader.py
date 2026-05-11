"""Data loaders for letf_rotation_hunt.

Sources:
  - testfolio cache: data/testfolio/cache/history.parquet
    (SPYSIM, NDXSIM, GLDSIM, ZROZSIM, CASHX, ...)
  - Tiingo daily: data/tiingo/daily/prices/{TICKER}.parquet
    (real ETF post-inception; adj_close column)
  - CASHX (FFR proxy): testfolio CASHX series

Citations
---------
* testfol.io as long-history source: Phase 3.5b Task 7a
  (cross-check UPROSIM vs synthesize_letf_returns)
* Tiingo bulk cache: project_tiingo_bulk_in_progress.md (2026-04-14)
* CASHX as FFR proxy: testfol.io documentation — CASHX = daily-compounded
  Federal Funds Rate, suitable as risk-free rate proxy.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_series as _load_testfolio

_TIINGO_DIR = Path("data/tiingo/daily/prices")


def load_testfolio_series(ticker: str) -> pd.Series:
    """Load synthetic price series from testfolio cache.

    Returns a pd.Series with DatetimeIndex of equity-curve values
    (normalised to $10,000 at first bar).

    Parameters
    ----------
    ticker:
        Case-insensitive ticker label, e.g. ``"SPYSIM"``, ``"CASHX"``.

    Raises
    ------
    FileNotFoundError
        If the testfolio cache parquet does not exist.
    KeyError
        If ``ticker`` is not found in the cache.
    """
    return _load_testfolio(ticker)


def load_ffr_daily() -> pd.Series:
    """Load Federal Funds Rate as daily return from CASHX testfolio series.

    CASHX in testfol.io = FFR proxy (daily compounded equity curve).
    Returns daily percentage returns (pct_change, first bar dropped).

    Typical range: (-0.001, 0.01) per day — i.e. near-zero but positive
    in non-ZIRP regimes. [testfol.io docs: CASHX tracks the daily FFR.]

    Returns
    -------
    pd.Series
        Daily return values indexed by date.
    """
    cashx = _load_testfolio("CASHX")
    return cashx.pct_change().dropna()


def load_tiingo_real_etf(ticker: str) -> pd.Series:
    """Load real ETF daily adj_close from Tiingo bulk cache.

    Reads ``data/tiingo/daily/prices/{TICKER}.parquet``. The Tiingo
    parquet schema uses column ``adj_close`` with a DatetimeIndex on
    the ``date`` level. [project_tiingo_bulk_in_progress.md, 2026-04-14]

    Parameters
    ----------
    ticker:
        ETF ticker, e.g. ``"UPRO"``, ``"SSO"``, ``"TMF"``.
        Case-insensitive — normalised to uppercase internally.

    Returns
    -------
    pd.Series
        Daily adjusted close prices sorted by ascending date.

    Raises
    ------
    FileNotFoundError
        If the ticker parquet is not present in the Tiingo cache.
    """
    path = _TIINGO_DIR / f"{ticker.upper()}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Tiingo file not found: {path}")
    df = pd.read_parquet(path)
    # Tiingo bulk schema: adj_close is the adjusted-close column.
    # Fallback order: adj_close → adjClose → close (legacy)
    if "adj_close" in df.columns:
        col = "adj_close"
    elif "adjClose" in df.columns:
        col = "adjClose"
    else:
        col = "close"
    series = df[col].copy()
    # Index is already DatetimeIndex in the Tiingo bulk cache, but
    # guard against string-index edge cases.
    if not isinstance(series.index, pd.DatetimeIndex):
        date_col = "date" if "date" in df.columns else df.index.name
        if date_col and date_col in df.columns:
            series.index = pd.to_datetime(df[date_col])
        else:
            series.index = pd.to_datetime(series.index)
    series.name = ticker.upper()
    return series.sort_index()
