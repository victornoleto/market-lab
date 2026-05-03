"""Dukascopy 1m OHLC fetcher with per-pair / per-month parquet cache.

Provides `fetch_ohlc(pair, start, end, freq)` — DataFrame indexed by UTC
timestamp with [open, high, low, close, volume] columns. Cache layout:

    data/ohlc/<PAIR>/<YYYY-MM>.parquet

Idempotent: if a month parquet already exists it is loaded; otherwise the
month is fetched from Dukascopy and persisted.

Pair convention:
- Internal/myfxbook: "EURUSD" (no slash)
- Dukascopy API: "EUR/USD" (with slash)

Citations:
- [evidence_based_ta, Aronson, p.367-380] — session/hour FX bias requires 1m
  bars to localize entry windows.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from . import config

# dukascopy-python is in the optional myfxbook_decoder dep group. We import lazily
# so importing this module on a fresh checkout (or inside a test environment that
# only needs paths) doesn't crash.
_DUKAS_PAIR_MAP = {
    # FX majors
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDCAD": "USD/CAD",
    "USDCHF": "USD/CHF",
    "USDJPY": "USD/JPY",
    "AUDUSD": "AUD/USD",
    "NZDUSD": "NZD/USD",
    # FX crosses
    "EURGBP": "EUR/GBP",
    "EURCHF": "EUR/CHF",
    "EURJPY": "EUR/JPY",
    "EURAUD": "EUR/AUD",
    "EURCAD": "EUR/CAD",
    "GBPJPY": "GBP/JPY",
    "GBPCHF": "GBP/CHF",
    "GBPAUD": "GBP/AUD",
    "GBPCAD": "GBP/CAD",
    "AUDJPY": "AUD/JPY",
    "AUDCHF": "AUD/CHF",
    "AUDCAD": "AUD/CAD",
    "AUDNZD": "AUD/NZD",
    "NZDJPY": "NZD/JPY",
    "NZDCHF": "NZD/CHF",
    "CADCHF": "CAD/CHF",
    "CADJPY": "CAD/JPY",
    "CHFJPY": "CHF/JPY",
    # Commodities
    "XAUUSD": "XAU/USD",
    "XAGUSD": "XAG/USD",
    # Crypto (Dukascopy coverage starts ~2017)
    "BTCUSD": "BTC/USD",
    "ETHUSD": "ETH/USD",
}


@dataclass(frozen=True)
class OhlcRequest:
    pair: str
    start: datetime
    end: datetime
    freq: str = "M1"


def _load_dukascopy():
    try:
        import dukascopy_python as dk
    except ImportError as e:
        raise RuntimeError(
            "dukascopy-python not installed. Run: uv pip install -e '.[myfxbook_decoder]'"
        ) from e
    return dk


def _interval(dk, freq: str) -> str:
    mapping = {
        "M1": dk.INTERVAL_MIN_1,
        "M5": dk.INTERVAL_MIN_5,
        "M15": dk.INTERVAL_MIN_15,
        "M30": dk.INTERVAL_MIN_30,
        "H1": dk.INTERVAL_HOUR_1,
        "H4": dk.INTERVAL_HOUR_4,
        "D1": dk.INTERVAL_DAY_1,
    }
    if freq not in mapping:
        raise ValueError(f"Unsupported freq {freq!r}. Allowed: {sorted(mapping)}")
    return mapping[freq]


def _to_dukas_pair(pair: str) -> str:
    p = pair.replace("/", "").upper()
    if p not in _DUKAS_PAIR_MAP:
        raise ValueError(f"Unknown FX pair {pair!r}. Add to _DUKAS_PAIR_MAP.")
    return _DUKAS_PAIR_MAP[p]


def _normalize_pair(pair: str) -> str:
    return pair.replace("/", "").upper()


def _month_path(pair: str, year: int, month: int, freq: str) -> Path:
    p = _normalize_pair(pair)
    return config.OHLC_ROOT / p / freq / f"{year:04d}-{month:02d}.parquet"


def _month_iter(start: datetime, end: datetime):
    """Yield (year, month, month_start_utc, month_end_utc) for each month overlapping [start,end]."""
    y, m = start.year, start.month
    while True:
        ms = datetime(y, m, 1, tzinfo=timezone.utc)
        nm_y, nm_m = (y + 1, 1) if m == 12 else (y, m + 1)
        me = datetime(nm_y, nm_m, 1, tzinfo=timezone.utc)
        clipped_start = max(ms, start.astimezone(timezone.utc))
        clipped_end = min(me, end.astimezone(timezone.utc))
        if clipped_start < clipped_end:
            yield y, m, clipped_start, clipped_end
        if me >= end.astimezone(timezone.utc):
            break
        y, m = nm_y, nm_m


def _fetch_month(dk, dukas_pair: str, freq_const: str, start: datetime, end: datetime) -> pd.DataFrame:
    """Fetch a single window (≤ 1 month) from Dukascopy. BID side."""
    df = dk.fetch(
        dukas_pair,
        freq_const,
        dk.OFFER_SIDE_BID,
        start,
        end,
    )
    if df.empty:
        return df
    df = df[["open", "high", "low", "close", "volume"]].copy()
    df.index.name = "timestamp"
    return df


def fetch_ohlc(pair: str, start: datetime, end: datetime, *, freq: str = "M1") -> pd.DataFrame:
    """Return DataFrame [open, high, low, close, volume] for [start, end), UTC.

    Caches per (pair, freq, year-month) parquet. Subsequent calls reuse cache.
    Re-fetches only months not present on disk.
    """
    dk = _load_dukascopy()
    freq_const = _interval(dk, freq)
    dukas_pair = _to_dukas_pair(pair)
    pair_norm = _normalize_pair(pair)

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    parts: list[pd.DataFrame] = []
    for y, m, ws, we in _month_iter(start, end):
        path = _month_path(pair_norm, y, m, freq)
        if path.exists():
            parts.append(pd.read_parquet(path))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        # Fetch the FULL month (so cache is reusable), then later we slice [start,end].
        full_ms = datetime(y, m, 1, tzinfo=timezone.utc)
        full_me = datetime(y + 1, 1, 1, tzinfo=timezone.utc) if m == 12 else datetime(y, m + 1, 1, tzinfo=timezone.utc)
        df_month = _fetch_month(dk, dukas_pair, freq_const, full_ms, full_me)
        if not df_month.empty:
            df_month.to_parquet(path)
        parts.append(df_month)

    if not parts:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    df = pd.concat(parts).sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = df.loc[(df.index >= start) & (df.index < end)]
    return df


class OhlcLoader:
    """Lazy multi-pair loader with in-memory dataframe cache.

    Use one instance per stage1/stage3 run. The first time a (pair, freq) is
    requested, a wide range is fetched (covering all known trades for that pair)
    and held in memory. Subsequent feature lookups slice the in-memory frame.
    """

    def __init__(self, freq: str = "M1") -> None:
        self.freq = freq
        self._cache: dict[str, pd.DataFrame] = {}

    def _key(self, pair: str, freq: str) -> str:
        return f"{_normalize_pair(pair)}|{freq}"

    def load(self, pair: str, start: datetime, end: datetime, *, freq: str | None = None) -> pd.DataFrame:
        f = freq or self.freq
        key = self._key(pair, f)
        df = self._cache.get(key)
        if df is None or df.index.min() > start or df.index.max() < end:
            new = fetch_ohlc(pair, start, end, freq=f)
            if df is not None and not df.empty:
                df = pd.concat([df, new]).sort_index()
                df = df[~df.index.duplicated(keep="first")]
            else:
                df = new
            self._cache[key] = df
        return df.loc[(df.index >= start) & (df.index < end)]

    def lookback(self, pair: str, anchor: datetime, n_bars: int, *, freq: str | None = None) -> pd.DataFrame:
        """Return last `n_bars` bars strictly BEFORE `anchor`. No look-ahead."""
        f = freq or self.freq
        # Conservative window: pad by 5x to handle weekends / market closures.
        bar_minutes = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 24 * 60}[f]
        pad = timedelta(minutes=bar_minutes * n_bars * 5 + 60)
        start = anchor - pad
        df = self.load(pair, start, anchor, freq=f)
        df = df.loc[df.index < anchor]
        return df.tail(n_bars)
