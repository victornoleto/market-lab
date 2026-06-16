"""Postgres-backed daily price/universe source.

Reads from the local ``stocks`` database synced from yfinance by
``data/yfinance/sync.py`` (tables ``yf_tickers`` and ``yf_daily_prices``).
Promoted from ``studies/momentum/data.py`` so any study can share one tested
data source alongside :class:`YFinanceSource` / :class:`TiingoSource`.

Known limitations — document in every backtest report that uses this source:

* **Survivorship / non point-in-time.** The DB caches the *current* yfinance
  universe plus whatever delisted tickers Yahoo still serves; companies that
  fully vanished were never synced. There is no point-in-time membership table,
  so current-universe look-ahead remains ``[advances_fin_ml, p.208-211]``. Pair
  with survivorship filters and treat results as research-only until a PIT
  membership feed exists.
* **Adjustments.** ``adj_close`` is Yahoo's total-return adjusted close; raw
  ``close`` is also available. Splits/dividends are as synced by yfinance.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

import pandas as pd

# country/asset-class WHERE clauses keyed by universe name. These match the
# `yf_tickers` columns populated by data/yfinance/sync.py.
UNIVERSE_SQL: dict[str, str] = {
    "us_stocks": "country = 'us' AND asset_class = 'stock'",
    "us_etfs": "country = 'us' AND asset_class = 'etf'",
    "br_stocks": "country = 'br' AND asset_class = 'stock'",
    "br_etfs": "country = 'br' AND asset_class = 'etf'",
    "crypto": "asset_class = 'crypto'",
    "us_mixed": "country = 'us' AND asset_class IN ('stock', 'etf')",
    "br_mixed": "country = 'br' AND asset_class IN ('stock', 'etf')",
    "global_mixed": "asset_class IN ('stock', 'etf', 'crypto')",
}
PRICE_COLUMNS = {"open", "high", "low", "close", "adj_close"}

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/stocks"
_URL_ENV_VARS = ("YFINANCE_DATABASE_URL", "DATABASE_URL")


@dataclass(frozen=True)
class PricePanel:
    """Price/volume panel plus ticker metadata for one universe."""

    universe: str
    prices: pd.DataFrame
    volumes: pd.DataFrame
    metadata: pd.DataFrame


def _ident(name: str) -> str:
    """Quote a (possibly dotted) SQL identifier safely."""
    parts = [part for part in name.split(".") if part]
    if not parts:
        raise ValueError("SQL identifier cannot be empty")
    return ".".join(f'"{part}"' for part in parts)


def parse_date(value: str | date | datetime | pd.Timestamp | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, pd.Timestamp):
        return value.date()
    return date.fromisoformat(str(value))


def connect(database_url: str):
    """Open a psycopg connection (lazy import keeps psycopg optional)."""
    import psycopg

    return psycopg.connect(database_url)


# --- pure SQL helpers (take an open `conn`; unit-testable with a fake conn) ---

def load_universe_metadata(
    conn: Any,
    *,
    schema: str,
    universe: str,
    max_symbols: int | None = None,
) -> pd.DataFrame:
    """Load active ticker metadata for a configured universe."""
    if universe not in UNIVERSE_SQL:
        raise ValueError(f"unknown universe={universe!r}")
    limit_sql = " LIMIT %s" if max_symbols is not None else ""
    params: list[object] = []
    if max_symbols is not None:
        params.append(max_symbols)
    query = f"""
        SELECT id, yf_symbol, asset_class, country, name, exchange, currency,
               first_date, last_date, active, last_error
        FROM {_ident(schema)}.yf_tickers
        WHERE active = TRUE AND ({UNIVERSE_SQL[universe]})
        ORDER BY yf_symbol
        {limit_sql}
    """
    rows = conn.execute(query, params).fetchall()
    columns = [
        "id",
        "yf_symbol",
        "asset_class",
        "country",
        "name",
        "exchange",
        "currency",
        "first_date",
        "last_date",
        "active",
        "last_error",
    ]
    frame = pd.DataFrame(rows, columns=columns)
    if frame.empty:
        return frame
    frame["yf_symbol"] = frame["yf_symbol"].astype(str).str.upper()
    return frame


def load_price_panel(
    conn: Any,
    *,
    schema: str,
    universe: str,
    price_column: str = "adj_close",
    start: str | None = None,
    end: str | None = None,
    max_symbols: int | None = None,
) -> PricePanel:
    """Load adjusted prices and volumes for one universe from Postgres."""
    if price_column not in PRICE_COLUMNS:
        raise ValueError(f"unsupported price column: {price_column!r}")
    metadata = load_universe_metadata(
        conn,
        schema=schema,
        universe=universe,
        max_symbols=max_symbols,
    )
    if metadata.empty:
        return PricePanel(universe, pd.DataFrame(), pd.DataFrame(), metadata)

    ticker_ids = metadata["id"].astype(int).tolist()
    params: list[object] = [ticker_ids]
    where = ["p.ticker_id = ANY(%s)"]
    if start is not None:
        where.append("p.date >= %s")
        params.append(parse_date(start))
    if end is not None:
        where.append("p.date <= %s")
        params.append(parse_date(end))
    where_sql = " AND ".join(where)
    query = f"""
        SELECT t.yf_symbol, p.date, p.{price_column} AS price, p.volume
        FROM {_ident(schema)}.yf_daily_prices p
        JOIN {_ident(schema)}.yf_tickers t ON t.id = p.ticker_id
        WHERE {where_sql}
        ORDER BY p.date, t.yf_symbol
    """
    rows = conn.execute(query, params).fetchall()
    if not rows:
        return PricePanel(universe, pd.DataFrame(), pd.DataFrame(), metadata)
    data = pd.DataFrame(rows, columns=["yf_symbol", "date", "price", "volume"])
    data["yf_symbol"] = data["yf_symbol"].astype(str).str.upper()
    data["date"] = pd.to_datetime(data["date"])
    data["price"] = pd.to_numeric(data["price"], errors="coerce")
    data["volume"] = pd.to_numeric(data["volume"], errors="coerce")
    prices = data.pivot(index="date", columns="yf_symbol", values="price").sort_index()
    volumes = data.pivot(index="date", columns="yf_symbol", values="volume").sort_index()
    return PricePanel(universe, prices, volumes, metadata)


def load_symbols_price_frame(
    conn: Any,
    *,
    schema: str,
    symbols: tuple[str, ...],
    price_column: str = "adj_close",
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """Load a small explicit symbol price frame, typically for benchmarks."""
    if price_column not in PRICE_COLUMNS:
        raise ValueError(f"unsupported price column: {price_column!r}")
    if not symbols:
        return pd.DataFrame()
    upper = [symbol.upper() for symbol in symbols]
    params: list[object] = [upper]
    where = ["upper(t.yf_symbol) = ANY(%s)"]
    if start is not None:
        where.append("p.date >= %s")
        params.append(parse_date(start))
    if end is not None:
        where.append("p.date <= %s")
        params.append(parse_date(end))
    query = f"""
        SELECT t.yf_symbol, p.date, p.{price_column} AS price
        FROM {_ident(schema)}.yf_daily_prices p
        JOIN {_ident(schema)}.yf_tickers t ON t.id = p.ticker_id
        WHERE {' AND '.join(where)}
        ORDER BY p.date, t.yf_symbol
    """
    rows = conn.execute(query, params).fetchall()
    if not rows:
        return pd.DataFrame()
    data = pd.DataFrame(rows, columns=["yf_symbol", "date", "price"])
    data["yf_symbol"] = data["yf_symbol"].astype(str).str.upper()
    data["date"] = pd.to_datetime(data["date"])
    data["price"] = pd.to_numeric(data["price"], errors="coerce")
    return data.pivot(index="date", columns="yf_symbol", values="price").sort_index()


def audit_database(conn: Any, *, schema: str) -> pd.DataFrame:
    """Summarize DB coverage by country and asset class."""
    query = f"""
        SELECT country, asset_class, count(*) AS n_tickers,
               min(first_date) AS first_date, max(last_date) AS last_date,
               count(*) FILTER (WHERE active) AS n_active,
               count(*) FILTER (WHERE last_error IS NOT NULL) AS n_with_error
        FROM {_ident(schema)}.yf_tickers
        GROUP BY country, asset_class
        ORDER BY country, asset_class
    """
    rows = conn.execute(query).fetchall()
    return pd.DataFrame(
        rows,
        columns=[
            "country",
            "asset_class",
            "n_tickers",
            "first_date",
            "last_date",
            "n_active",
            "n_with_error",
        ],
    )


# --- connection-managing wrapper (mirrors YFinanceSource/TiingoSource) ---

@dataclass
class PostgresSource:
    """Daily price/universe fetcher backed by the local ``stocks`` Postgres DB.

    ``database_url`` resolves from the constructor arg, then ``YFINANCE_DATABASE_URL``
    / ``DATABASE_URL`` env vars, then a localhost default. A fresh connection is
    opened and closed per call. ``connection_factory`` is injectable for tests.
    """

    database_url: str | None = None
    schema: str = "public"
    price_column: str = "adj_close"
    connection_factory: Callable[[str], Any] = field(default=connect)

    def resolve_url(self) -> str:
        if self.database_url:
            return self.database_url
        for env in _URL_ENV_VARS:
            value = os.environ.get(env)
            if value:
                return value
        return DEFAULT_DATABASE_URL

    @contextmanager
    def _connection(self) -> Iterator[Any]:
        conn = self.connection_factory(self.resolve_url())
        try:
            yield conn
        finally:
            close = getattr(conn, "close", None)
            if callable(close):
                close()

    def fetch_panel(
        self,
        universe: str,
        *,
        start: str | None = None,
        end: str | None = None,
        price_column: str | None = None,
        max_symbols: int | None = None,
    ) -> PricePanel:
        """Load prices/volumes/metadata for one universe."""
        with self._connection() as conn:
            return load_price_panel(
                conn,
                schema=self.schema,
                universe=universe,
                price_column=price_column or self.price_column,
                start=start,
                end=end,
                max_symbols=max_symbols,
            )

    def fetch_symbols(
        self,
        symbols: tuple[str, ...],
        *,
        start: str | None = None,
        end: str | None = None,
        price_column: str | None = None,
    ) -> pd.DataFrame:
        """Load a small explicit symbol price frame (e.g. benchmarks)."""
        with self._connection() as conn:
            return load_symbols_price_frame(
                conn,
                schema=self.schema,
                symbols=symbols,
                price_column=price_column or self.price_column,
                start=start,
                end=end,
            )

    def audit(self) -> pd.DataFrame:
        """Summarize DB coverage by country and asset class."""
        with self._connection() as conn:
            return audit_database(conn, schema=self.schema)
