"""Offline tests for the shared PostgresSource (no live database).

A fake connection records the SQL it receives and returns canned rows, so we
can assert query shaping, pivoting, normalization and connection lifecycle
without psycopg or a running Postgres.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd
import pytest

from market_lab.backtest.data.postgres_source import (
    UNIVERSE_SQL,
    PostgresSource,
    audit_database,
    load_price_panel,
    load_symbols_price_frame,
    load_universe_metadata,
)


class _Cursor:
    def __init__(self, rows: list[tuple]):
        self._rows = rows

    def fetchall(self) -> list[tuple]:
        return self._rows


class FakeConn:
    """Routes queries to canned rows based on the SQL text."""

    def __init__(self) -> None:
        self.queries: list[tuple[str, list]] = []
        self.closed = False

    def execute(self, query: str, params: list | None = None) -> _Cursor:
        self.queries.append((query, list(params or [])))
        if "GROUP BY country" in query:
            return _Cursor(
                [("us", "stock", 3, dt.date(1990, 1, 2), dt.date(2026, 1, 2), 3, 1)]
            )
        if "SELECT id," in query and "yf_tickers" in query:
            return _Cursor(
                [
                    (1, "aapl", "stock", "us", "Apple", "NASDAQ", "USD",
                     dt.date(1990, 1, 2), dt.date(2026, 1, 2), True, None),
                    (2, "msft", "stock", "us", "Microsoft", "NASDAQ", "USD",
                     dt.date(1990, 1, 2), dt.date(2026, 1, 2), True, None),
                ]
            )
        if "p.volume" in query:  # price panel
            return _Cursor(
                [
                    ("aapl", dt.date(2020, 1, 2), 100.0, 1000),
                    ("msft", dt.date(2020, 1, 2), 200.0, 2000),
                    ("aapl", dt.date(2020, 1, 3), 101.0, 1100),
                    ("msft", dt.date(2020, 1, 3), 201.0, 2100),
                ]
            )
        # symbol frame (benchmark): SELECT t.yf_symbol, p.date, p.<col> AS price
        return _Cursor(
            [
                ("spy", dt.date(2020, 1, 2), 300.0),
                ("spy", dt.date(2020, 1, 3), 301.0),
            ]
        )

    def close(self) -> None:
        self.closed = True


def test_universe_sql_keys_cover_all_eight_universes():
    assert set(UNIVERSE_SQL) == {
        "us_stocks", "us_etfs", "br_stocks", "br_etfs",
        "crypto", "us_mixed", "br_mixed", "global_mixed",
    }


def test_load_universe_metadata_filters_and_uppercases():
    conn = FakeConn()
    frame = load_universe_metadata(conn, schema="public", universe="us_stocks")
    query, _ = conn.queries[-1]
    assert UNIVERSE_SQL["us_stocks"] in query
    assert '"public".yf_tickers' in query
    assert frame["yf_symbol"].tolist() == ["AAPL", "MSFT"]


def test_load_universe_metadata_rejects_unknown_universe():
    with pytest.raises(ValueError, match="unknown universe"):
        load_universe_metadata(FakeConn(), schema="public", universe="nope")


def test_load_universe_metadata_applies_limit():
    conn = FakeConn()
    load_universe_metadata(conn, schema="public", universe="us_stocks", max_symbols=10)
    query, params = conn.queries[-1]
    assert "LIMIT %s" in query
    assert params == [10]


def test_load_price_panel_pivots_prices_and_volumes():
    conn = FakeConn()
    panel = load_price_panel(
        conn, schema="public", universe="us_stocks", start="2020-01-01", end="2020-12-31"
    )
    assert list(panel.prices.columns) == ["AAPL", "MSFT"]
    assert panel.prices.loc[pd.Timestamp("2020-01-03"), "MSFT"] == 201.0
    assert panel.volumes.loc[pd.Timestamp("2020-01-02"), "AAPL"] == 1000.0
    # start/end bind as date params on the price query
    _, params = conn.queries[-1]
    assert dt.date(2020, 1, 1) in params and dt.date(2020, 12, 31) in params


def test_load_price_panel_rejects_bad_price_column():
    with pytest.raises(ValueError, match="unsupported price column"):
        load_price_panel(FakeConn(), schema="public", universe="us_stocks", price_column="vwap")


def test_load_symbols_price_frame_for_benchmark():
    conn = FakeConn()
    frame = load_symbols_price_frame(conn, schema="public", symbols=("SPY",))
    assert list(frame.columns) == ["SPY"]
    assert frame.loc[pd.Timestamp("2020-01-03"), "SPY"] == 301.0


def test_load_symbols_price_frame_empty_symbols_returns_empty():
    assert load_symbols_price_frame(FakeConn(), schema="public", symbols=()).empty


def test_audit_database_summarizes_coverage():
    frame = audit_database(FakeConn(), schema="public")
    assert frame.loc[0, "country"] == "us"
    assert frame.loc[0, "n_active"] == 3


def test_source_resolve_url_precedence(monkeypatch):
    monkeypatch.delenv("YFINANCE_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert PostgresSource(database_url="postgresql://x").resolve_url() == "postgresql://x"
    monkeypatch.setenv("DATABASE_URL", "postgresql://env-fallback")
    assert PostgresSource().resolve_url() == "postgresql://env-fallback"
    monkeypatch.setenv("YFINANCE_DATABASE_URL", "postgresql://env-primary")
    assert PostgresSource().resolve_url() == "postgresql://env-primary"


def test_source_fetch_panel_uses_factory_and_closes_connection():
    conn = FakeConn()
    source = PostgresSource(
        database_url="postgresql://x",
        connection_factory=lambda url: conn,
    )
    panel = source.fetch_panel("us_stocks", start="2020-01-01")
    assert list(panel.prices.columns) == ["AAPL", "MSFT"]
    assert conn.closed is True


def test_source_audit_uses_connection():
    conn = FakeConn()
    source = PostgresSource(connection_factory=lambda url: conn)
    frame = source.audit()
    assert frame.loc[0, "asset_class"] == "stock"
    assert conn.closed is True
