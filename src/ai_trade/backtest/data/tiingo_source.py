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

_BASE = "https://api.tiingo.com"
_BASE_DAILY = f"{_BASE}/tiingo/daily"

# v1 whitelist: (asset_class, frequency) pairs Tiingo-backed source accepts.
# Index intraday is intentionally excluded — Tiingo IEX doesn't cover indices
# directly; use an ETF proxy (SPY, QQQ, DIA, IWM) per §6.6 of the spec.
_WHITELIST_ASSET_FREQ: frozenset[tuple[str, str]] = frozenset({
    ("equity", "daily"),
    ("etf",    "daily"),
    ("index",  "daily"),
    ("crypto", "daily"),
    ("crypto", "1hour"),
    ("forex",  "daily"),
    ("forex",  "1hour"),
    ("equity", "1hour"),
    ("etf",    "1hour"),
})

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
    """Tiingo JSON list → canonical 6-col OHLCV DataFrame.

    Defensive on ``adj_close`` and ``volume`` because the IEX endpoint
    (equity/etf 1h) omits both — it only returns ``date/open/high/low/close``.
    When absent:
      * ``adj_close`` falls back to ``close`` (raw; split-adjust is applied
        later by ``_apply_split_adjust_from_daily`` for equity/etf 1h);
      * ``volume`` fills with 0.0 — IEX intraday doesn't publish volume
        and downstream strategies that require it will surface the gap
        explicitly. See spec §6.5 v3.1 caveat.
    """
    if not payload:
        return pd.DataFrame(columns=_CANONICAL_COLUMNS)

    df = pd.DataFrame(payload)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df = df.set_index("date").sort_index()

    close = df["close"].astype(float)
    # Map Tiingo names → canonical (defensive for IEX intraday).
    canonical = pd.DataFrame(
        {
            "open": df["open"].astype(float),
            "high": df["high"].astype(float),
            "low": df["low"].astype(float),
            "close": close,
            "adj_close": (
                df["adjClose"].astype(float) if "adjClose" in df.columns else close
            ),
            "volume": (
                df["volume"].astype(float)
                if "volume" in df.columns
                else pd.Series(0.0, index=df.index)
            ),
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


def _check_whitelist(asset_class: str, frequency: str) -> None:
    """Gate (asset_class, frequency) against the v1 whitelist.

    Raises ``NotImplementedError`` with an actionable hint for the two common
    mistakes: (1) index intraday (point to ETF proxy) and (2) unsupported
    frequency (remind the spec §6.6 unblock path).
    """
    if (asset_class, frequency) in _WHITELIST_ASSET_FREQ:
        return
    if asset_class == "index" and frequency == "1hour":
        raise NotImplementedError(
            "Tiingo IEX não cobre índices diretamente. Use um ETF proxy "
            "(SPY, QQQ, DIA, IWM). v1 whitelist: {equity, etf, crypto, forex} "
            "× {daily, 1hour}."
        )
    raise NotImplementedError(
        f"frequency={frequency!r} com asset_class={asset_class!r} fora do v1 "
        f"whitelist. v1 aceita: {{daily, 1hour}} para equity/etf/crypto/forex; "
        f"index só daily. Seguir §6.6 do spec para unblock path."
    )


def _build_url(ticker: str, asset_class: str, frequency: str = "daily") -> str:
    """Pick the Tiingo endpoint for (asset_class, frequency).

    Routing (v1 whitelist):

    * equity/etf + daily  → ``/tiingo/daily/{ticker}/prices``
    * equity/etf + 1hour  → ``/iex/{ticker}/prices``
    * index      + daily  → ``/tiingo/daily/{ticker}/prices`` (intraday blocked)
    * crypto     + any    → ``/tiingo/crypto/prices`` (ticker via query param)
    * forex      + any    → ``/tiingo/fx/{ticker}/prices``
    """
    _check_whitelist(asset_class, frequency)
    api_ticker = _normalize_ticker(ticker, asset_class)
    if asset_class in ("equity", "etf") and frequency == "1hour":
        return f"{_BASE}/iex/{api_ticker}/prices"
    if asset_class in ("equity", "etf", "index") and frequency == "daily":
        return f"{_BASE_DAILY}/{api_ticker}/prices"
    if asset_class == "crypto":
        return f"{_BASE}/tiingo/crypto/prices"
    if asset_class == "forex":
        return f"{_BASE}/tiingo/fx/{api_ticker}/prices"
    raise NotImplementedError(f"unhandled: {asset_class=} {frequency=}")


def _build_params(
    ticker: str,
    start: date,
    end: date,
    asset_class: str,
    frequency: str = "daily",
) -> dict:
    """Query params for (asset_class, frequency). Intraday routes add
    ``resampleFreq``; crypto always needs ``tickers`` as a query param.
    """
    params: dict[str, str] = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
    }
    if asset_class == "crypto":
        # Crypto endpoint takes a `tickers` query param, not a path segment.
        params["tickers"] = _normalize_ticker(ticker, asset_class)
        params["resampleFreq"] = "1hour" if frequency == "1hour" else "1day"
    elif frequency == "1hour":
        params["resampleFreq"] = "1hour"
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
        frequency: str = "daily",
    ) -> pd.DataFrame:
        url = _build_url(ticker, asset_class, frequency)
        params = _build_params(ticker, start, end, asset_class, frequency)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self._api_key()}",
        }
        log.info(
            "HTTP fetch %s [%s..%s] (%s freq=%s)",
            ticker, start, end, asset_class, frequency,
        )
        resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        # 404 = Tiingo doesn't serve this ticker (delisted, renamed, or never
        # covered). Return an empty frame so the caller can skip the ticker
        # — this matches yfinance's behaviour for missing symbols, and
        # keeps long-running universe fetches resilient.
        if resp.status_code == 404:
            log.warning(
                "tiingo 404 for %s (%s freq=%s) — returning empty frame",
                ticker, asset_class, frequency,
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

    def _apply_split_adjust_from_daily(
        self, ticker: str, df_intraday: pd.DataFrame,
    ) -> pd.DataFrame:
        """Apply daily-derived adjust ratio to intraday bars.

        Caller (`fetch()`) decides when to invoke this (only equity/etf 1h).
        Fórmula per spec §3.3: ratio_D = adj_close_daily[D] / close_daily[D];
        aplica ratio_D a bars intraday do mesmo dia calendário. Resultado:
        adj_close_intraday[t] é o total-return-adjusted close no bar t.

        Raises NotImplementedError se o ticker não está no daily cache (vide
        spec §3.3 — sem fallback silencioso para close raw).

        Citações: [quant_trading_chan, p.37] (multiplier preserva returns
        ao embutir o desconto de dividendo no próprio multiplier, não como
        termo separado); [trading_systems_methods, Kaufman, p.914]
        (split-adjusted stocks perdem vol characteristics);
        [ml_for_algo_trading, ch.2, p.35-40] (dollar bars + price-level
        adjustment).
        """
        if df_intraday.empty:
            return df_intraday

        intraday_dates = [ts.date() for ts in df_intraday.index]
        first_intra = min(intraday_dates)
        last_intra = max(intraday_dates)

        try:
            df_daily = self.storage.read(
                ticker, start=first_intra, end=last_intra, frequency="daily",
            )
        except KeyError:
            raise NotImplementedError(
                f"Ticker {ticker!r} não está no daily cache. "
                f"Baixe o daily primeiro para obter adj_close, ou pré-autorize "
                f"via flag --skip-adjust se você sabe o que está fazendo. "
                f"Vide spec §3.3."
            )

        daily_ratio = df_daily["adj_close"] / df_daily["close"]
        daily_dates = [ts.date() for ts in df_daily.index]
        date_to_ratio: dict[date, float] = dict(zip(daily_dates, daily_ratio.values))

        ratios = pd.Series(
            [date_to_ratio.get(d, 1.0) for d in intraday_dates],
            index=df_intraday.index,
        )

        out = df_intraday.copy()
        for col in ("open", "high", "low", "close"):
            if col in out.columns:
                out[col] = (out[col].astype(float) * ratios).astype(float)
        out["adj_close"] = out["close"]
        return out

    def fetch(
        self,
        ticker: str,
        start: date,
        end: date,
        asset_class: str = "equity",
        frequency: str = "daily",
    ) -> pd.DataFrame:
        """Return OHLCV for ``(ticker, frequency)`` in ``[start, end]``.

        Storage-first: hits the API only when the manifest does not cover
        the requested range for the given ``(ticker, frequency)``. New data
        is persisted to storage, so the next call hits the disk.
        """
        if self.storage.has(ticker, start, end, frequency=frequency):
            log.debug(
                "storage hit: %s freq=%s [%s..%s]",
                ticker, frequency, start, end,
            )
            return self.storage.read(ticker, start, end, frequency=frequency)

        df = self._http_fetch(ticker, start, end, asset_class, frequency)
        if df.empty:
            return df

        # Split adjust para IEX 1h (equity/etf) se daily cache disponível.
        # Crypto/forex 1h já vêm com adj_close := close via _normalize.
        if frequency == "1hour" and asset_class in ("equity", "etf"):
            df = self._apply_split_adjust_from_daily(ticker, df)

        self.storage.write(
            ticker, df,
            asset_class=asset_class,
            frequency=frequency,
            requested_start=start,
            requested_end=end,
        )
        return self.storage.read(ticker, start, end, frequency=frequency)

    def fetch_many(
        self,
        tickers: list[str],
        start: date,
        end: date,
        asset_class: str = "equity",
        frequency: str = "daily",
    ) -> dict[str, pd.DataFrame]:
        """Sequential fetch for each ticker. Storage hits skip the API."""
        return {
            t: self.fetch(t, start, end, asset_class=asset_class, frequency=frequency)
            for t in tickers
        }
