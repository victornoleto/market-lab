"""Daily OHLCV via yfinance (unofficial Yahoo Finance client).

Known limitations — document in every backtest report that uses this source:

* **Current ticker membership only.** Delisted tickers return empty DataFrames.
  Combined with a current-only universe this produces severe survivorship bias.
  See README §"Universo Clenow e survivorship bias". Migrate to Tiingo/EOD/
  Norgate when edge detection from research justifies the cost (ROADMAP
  §"Decisões adiadas").
* **Yahoo ToS gray zone.** yfinance README states "intended for personal
  use only" — this is research infrastructure, not a redistributable service.
* **Unofficial rate limit.** The parquet cache in this module prevents
  repeated calls for the same (ticker, window).
* **Adjustments.** Uses Yahoo's adjusted close (`adj_close`) alongside raw
  `close`; strategies that need total-return should use `adj_close`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CACHE_DIR = _PROJECT_ROOT / ".cache" / "yfinance"

_CANONICAL_COLUMNS = ["open", "high", "low", "close", "adj_close", "volume"]
_RENAME_MAP = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
}


def _normalize(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize yfinance output to the canonical shape.

    Canonical shape:
        index: DatetimeIndex, tz-naive, name="date"
        columns: [open, high, low, close, adj_close, volume]

    yfinance returns different column shapes across versions (single-level
    strings, MultiIndex with ticker level, etc.); this isolates that mess.
    """
    if raw.empty:
        return raw

    df = raw.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=_RENAME_MAP)

    missing = [c for c in _CANONICAL_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"yfinance output missing expected columns: {missing}")

    df = df[_CANONICAL_COLUMNS].copy()

    idx = pd.to_datetime(df.index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    df.index = idx
    df.index.name = "date"
    return df


@dataclass
class YFinanceSource:
    """Fetcher with an on-disk parquet cache per ticker.

    Cache is keyed by ticker filename; each file stores the full range ever
    fetched. Subsequent fetches with a narrower window read from cache.
    """

    cache_dir: Path = field(default_factory=lambda: DEFAULT_CACHE_DIR)

    def __post_init__(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, ticker: str) -> Path:
        safe = ticker.replace("/", "_")
        return self.cache_dir / f"{safe}.parquet"

    def fetch(
        self,
        ticker: str,
        start: date,
        end: date,
        interval: str = "1d",
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """Return daily OHLCV for `ticker` between `start` and `end` (inclusive).

        Empty DataFrame if Yahoo returns no data (typical for delisted tickers).
        """
        cache_path = self._cache_path(ticker)
        if use_cache and cache_path.exists():
            cached = pd.read_parquet(cache_path)
            if not cached.empty:
                c_start = cached.index.min().date()
                c_end = cached.index.max().date()
                if c_start <= start and c_end >= end:
                    log.debug("cache hit: %s [%s..%s]", ticker, start, end)
                    mask = (cached.index >= pd.Timestamp(start)) & (
                        cached.index <= pd.Timestamp(end)
                    )
                    return cached.loc[mask]

        import yfinance as yf  # lazy import — network-bound, heavy

        log.info("fetching %s [%s..%s] from yfinance", ticker, start, end)
        raw = yf.download(
            ticker,
            start=start.isoformat(),
            end=end.isoformat(),
            interval=interval,
            progress=False,
            auto_adjust=False,
        )
        df = _normalize(raw)
        if df.empty:
            log.warning("yfinance returned no data for %s [%s..%s]", ticker, start, end)
            return df

        if use_cache:
            df.to_parquet(cache_path)
        return df

    def fetch_many(
        self,
        tickers: list[str],
        start: date,
        end: date,
        interval: str = "1d",
        use_cache: bool = True,
    ) -> dict[str, pd.DataFrame]:
        """Sequential fetch — one (ticker, window) at a time, cached individually.

        Sequential (not concurrent) on purpose: Yahoo rate-limits aggressively,
        and the cache makes a warm re-run fast anyway.
        """
        return {t: self.fetch(t, start, end, interval, use_cache) for t in tickers}
