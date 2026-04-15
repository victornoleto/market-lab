"""Tiingo EOD/crypto/fx data source — storage-first, API on miss.

Auth: ``Authorization: Token <key>`` header, key from ``TIINGO_API_KEY``
env var. Endpoints (Tiingo API):

* equity / etf / index → ``/tiingo/daily/{ticker}/prices``
* crypto              → ``/tiingo/crypto/prices?tickers={ticker}``
* forex               → ``/tiingo/fx/{ticker}/prices``

Behavior::

    fetch(ticker, start, end, asset_class)
        if storage.has(ticker, start, end):
            return storage.read(ticker, start, end)
        else:
            df = _http_fetch(ticker, start, end, asset_class)
            storage.write(ticker, df, asset_class)
            return df.loc[start:end]

This makes the backtest source-agnostic — once the bulk download has
populated the storage, the API is no longer required (subscription can
be cancelled). New tickers or extended ranges trigger a single API call,
gracefully.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from ai_trade.backtest.data.tiingo_storage import TiingoStorage

log = logging.getLogger(__name__)

_BASE = "https://api.tiingo.com/tiingo"

_CANONICAL_COLUMNS = ["open", "high", "low", "close", "adj_close", "volume"]


def _read_env_file(name: str) -> str:
    """Best-effort .env reader for callers that didn't ``source .env``.

    Looks for the project-root .env (4 levels up from this file) and parses
    ``KEY=VALUE`` lines, stripping quotes. Returns "" if the file is absent
    or the key is missing — the caller is responsible for raising.
    """
    env_path = Path(__file__).resolve().parents[4] / ".env"
    if not env_path.exists():
        return ""
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == name:
            return v.strip().strip('"').strip("'")
    return ""


def _normalize(payload: list[dict]) -> pd.DataFrame:
    """Tiingo JSON list → canonical 6-col OHLCV DataFrame."""
    if not payload:
        return pd.DataFrame(columns=_CANONICAL_COLUMNS)

    df = pd.DataFrame(payload)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df = df.set_index("date").sort_index()

    # Map Tiingo names → canonical
    canonical = pd.DataFrame(
        {
            "open": df["open"].astype(float),
            "high": df["high"].astype(float),
            "low": df["low"].astype(float),
            "close": df["close"].astype(float),
            "adj_close": df.get("adjClose", df["close"]).astype(float),
            "volume": df["volume"].astype(float),
        },
        index=df.index,
    )
    canonical.index.name = "date"
    return canonical


def _normalize_ticker(ticker: str, asset_class: str) -> str:
    """Map Yahoo-style ticker → Tiingo-style for the URL.

    Tiingo follows the Bloomberg class-share convention (``BF-B``,
    ``BRK-B``); Yahoo uses dots (``BF.B``, ``BRK.B``). Only equities
    need the swap — ETFs, indices, crypto and forex have no dotted
    tickers.

    The local storage key remains the ORIGINAL (Yahoo-style) ticker
    so it stays consistent with WikipediaSPX and the rest of the
    pipeline; only the outbound HTTP URL uses the swapped form.
    """
    if asset_class == "equity" and "." in ticker:
        return ticker.replace(".", "-")
    return ticker


def _build_url(ticker: str, asset_class: str) -> str:
    """Pick the Tiingo endpoint for the given asset class."""
    api_ticker = _normalize_ticker(ticker, asset_class)
    if asset_class in ("equity", "etf", "index"):
        return f"{_BASE}/daily/{api_ticker}/prices"
    if asset_class == "crypto":
        return f"{_BASE}/crypto/prices"
    if asset_class == "forex":
        return f"{_BASE}/fx/{api_ticker}/prices"
    raise ValueError(f"unknown asset_class: {asset_class!r}")


def _build_params(
    ticker: str, start: date, end: date, asset_class: str,
) -> dict:
    params = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
    }
    if asset_class == "crypto":
        # Crypto endpoint takes a `tickers` query param, not a path segment.
        params["tickers"] = _normalize_ticker(ticker, asset_class)
        params["resampleFreq"] = "1day"
    return params


@dataclass
class TiingoSource:
    """Storage-first Tiingo client.

    Parameters
    ----------
    storage : TiingoStorage
        Persistent layer. Reads first; writes on API success.
    timeout : float
        HTTP timeout in seconds (default 30).
    """

    storage: TiingoStorage
    timeout: float = 30.0

    def _api_key(self) -> str:
        key = os.environ.get("TIINGO_API_KEY", "") or _read_env_file("TIINGO_API_KEY")
        if not key:
            raise RuntimeError(
                "TIINGO_API_KEY not set (env or .env file at project root)."
            )
        return key

    def _http_fetch(
        self,
        ticker: str,
        start: date,
        end: date,
        asset_class: str,
    ) -> pd.DataFrame:
        url = _build_url(ticker, asset_class)
        params = _build_params(ticker, start, end, asset_class)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self._api_key()}",
        }
        log.info("HTTP fetch %s [%s..%s] (%s)", ticker, start, end, asset_class)
        resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        # 404 = Tiingo doesn't serve this ticker (delisted, renamed, or never
        # covered). Return an empty frame so the caller can skip the ticker
        # — this matches yfinance's behaviour for missing symbols, and
        # keeps long-running universe fetches resilient.
        if resp.status_code == 404:
            log.warning(
                "tiingo 404 for %s (%s) — returning empty frame",
                ticker, asset_class,
            )
            return _normalize([])
        resp.raise_for_status()
        body = resp.json()

        # Crypto returns [{ticker, baseCurrency, ..., priceData: [...]}].
        if asset_class == "crypto":
            if not body or not isinstance(body, list):
                return _normalize([])
            return _normalize(body[0].get("priceData", []))
        return _normalize(body)

    def fetch(
        self,
        ticker: str,
        start: date,
        end: date,
        asset_class: str = "equity",
    ) -> pd.DataFrame:
        """Return OHLCV for ``ticker`` in ``[start, end]``.

        Storage-first: hits the API only when the manifest does not cover
        the requested range. New data is persisted to storage, so the next
        call hits the disk.
        """
        if self.storage.has(ticker, start, end):
            log.debug("storage hit: %s [%s..%s]", ticker, start, end)
            return self.storage.read(ticker, start, end)

        df = self._http_fetch(ticker, start, end, asset_class)
        if df.empty:
            return df

        self.storage.write(ticker, df, asset_class=asset_class)
        return self.storage.read(ticker, start, end)

    def fetch_many(
        self,
        tickers: list[str],
        start: date,
        end: date,
        asset_class: str = "equity",
    ) -> dict[str, pd.DataFrame]:
        """Sequential fetch for each ticker. Storage hits skip the API."""
        return {
            t: self.fetch(t, start, end, asset_class=asset_class)
            for t in tickers
        }
