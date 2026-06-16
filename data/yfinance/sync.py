#!/usr/bin/env python3
"""Sync yfinance daily OHLCV into a local Postgres database.

This is a research data cache, not a survivorship-free market-data master. The
US universe is built from current Nasdaq Trader symbol directories, BR stocks
come from ``data/yfinance/br.txt``, and crypto is a curated USD-quoted list.
Current-universe yfinance data remains screen-only until point-in-time and
delisted coverage are audited `[advances_fin_ml, p.208-211]`.
"""

from __future__ import annotations

import argparse
import csv
import io
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BR_FILE = REPO_ROOT / "data" / "yfinance" / "br.txt"
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/stocks"
DEFAULT_SCHEMA = "public"

NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
USER_AGENT = "market-lab/0.1 (research yfinance postgres sync)"

VALID_ASSET_CLASSES = {"stock", "etf", "crypto"}
VALID_COUNTRIES = {"us", "br", "global"}

CANONICAL_PRICE_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "adj_close",
    "volume",
    "dividends",
    "stock_splits",
]

YF_RENAME_MAP = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
    "Dividends": "dividends",
    "Stock Splits": "stock_splits",
}

BR_ETF_TICKERS: tuple[str, ...] = (
    "BOVA11.SA",
    "BOVV11.SA",
    "PIBB11.SA",
    "SMAL11.SA",
    "DIVO11.SA",
    "FIND11.SA",
    "MATB11.SA",
    "GOVE11.SA",
    "ECOO11.SA",
    "ISUS11.SA",
    "IVVB11.SA",
    "SPXI11.SA",
    "NASD11.SA",
    "WRLD11.SA",
    "ACWI11.SA",
    "EURP11.SA",
    "GOLD11.SA",
    "B5P211.SA",
    "IMAB11.SA",
    "IRFM11.SA",
    "FIXA11.SA",
    "XFIX11.SA",
    "HASH11.SA",
    "QBTC11.SA",
    "QETH11.SA",
    "ETHE11.SA",
    "META11.SA",
)

CRYPTO_TICKERS: tuple[tuple[str, str], ...] = (
    ("BTC-USD", "Bitcoin"),
    ("ETH-USD", "Ethereum"),
    ("BNB-USD", "BNB"),
    ("SOL-USD", "Solana"),
    ("XRP-USD", "XRP"),
    ("ADA-USD", "Cardano"),
    ("DOGE-USD", "Dogecoin"),
    ("AVAX-USD", "Avalanche"),
    ("LINK-USD", "Chainlink"),
    ("DOT-USD", "Polkadot"),
    ("LTC-USD", "Litecoin"),
    ("BCH-USD", "Bitcoin Cash"),
)

log = logging.getLogger("market_lab.yfinance_sync")


@dataclass(frozen=True)
class TickerSpec:
    """Ticker metadata staged before Postgres upsert.

    ``country`` intentionally means listing/data market for stocks and ETFs,
    not legal issuer domicile. Crypto has no issuer country, so it uses
    ``global``.
    """

    yf_symbol: str
    asset_class: str
    country: str
    name: str | None = None
    exchange: str | None = None
    currency: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        symbol = self.yf_symbol.strip().upper()
        asset_class = self.asset_class.strip().lower()
        country = self.country.strip().lower()
        if not symbol:
            raise ValueError("yf_symbol cannot be empty")
        if asset_class not in VALID_ASSET_CLASSES:
            raise ValueError(f"invalid asset_class={self.asset_class!r}")
        if country not in VALID_COUNTRIES:
            raise ValueError(f"invalid country={self.country!r}")
        object.__setattr__(self, "yf_symbol", symbol)
        object.__setattr__(self, "asset_class", asset_class)
        object.__setattr__(self, "country", country)


def load_env_file(path: Path = REPO_ROOT / ".env") -> None:
    """Best-effort dotenv reader that does not override process env vars."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key or key in os.environ:
            continue
        os.environ[key] = value.strip().strip('"').strip("'")


def env_or_default(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def database_url_from_env(cli_value: str | None = None) -> str:
    if cli_value:
        return cli_value
    return (
        os.getenv("YFINANCE_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or DEFAULT_DATABASE_URL
    )


def setup_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper())
    log_dir = REPO_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "yfinance_sync.log", mode="a", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def parse_br_ticker_file(path: Path) -> list[TickerSpec]:
    """Read one BR ticker per line from ``br.txt``.

    The file may contain quoted symbols, plain symbols, optional trailing commas,
    blank lines and comments. Symbols without ``.SA`` get the suffix added.
    """
    specs: list[TickerSpec] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        symbol = line.rstrip(",").strip().strip('"').strip("'").upper()
        if not symbol:
            continue
        if "." not in symbol:
            symbol = f"{symbol}.SA"
        specs.append(
            TickerSpec(
                yf_symbol=symbol,
                asset_class="stock",
                country="br",
                exchange="B3",
                currency="BRL",
                metadata={"source": "data/yfinance/br.txt"},
            )
        )
    return dedupe_specs(specs)


def br_etf_specs() -> list[TickerSpec]:
    return [
        TickerSpec(
            yf_symbol=ticker,
            asset_class="etf",
            country="br",
            exchange="B3",
            currency="BRL",
            metadata={"source": "curated_br_etf_list"},
        )
        for ticker in BR_ETF_TICKERS
    ]


def crypto_specs() -> list[TickerSpec]:
    return [
        TickerSpec(
            yf_symbol=symbol,
            asset_class="crypto",
            country="global",
            name=name,
            exchange="Yahoo Finance",
            currency="USD",
            metadata={"source": "curated_crypto_usd_pairs"},
        )
        for symbol, name in CRYPTO_TICKERS
    ]


def normalize_us_symbol_for_yahoo(raw_symbol: str) -> str:
    """Map Nasdaq Trader notation to Yahoo's common symbol notation."""
    symbol = raw_symbol.strip().upper()
    symbol = symbol.replace("/", "-").replace(".", "-")
    # Nasdaq Trader often writes preferred shares as BAC$B; Yahoo uses BAC-PB.
    if "$" in symbol:
        base, _, suffix = symbol.partition("$")
        symbol = f"{base}-P{suffix}"
    return symbol


def parse_nasdaq_symbol_directory(text: str, source: str) -> list[TickerSpec]:
    """Parse Nasdaq Trader ``nasdaqlisted.txt`` or ``otherlisted.txt`` content."""
    reader = csv.DictReader(io.StringIO(text), delimiter="|")
    specs: list[TickerSpec] = []
    for row in reader:
        if not row:
            continue
        first_value = next(iter(row.values()))
        if first_value is None or first_value.startswith("File Creation Time"):
            continue

        raw_symbol = row.get("Symbol") or row.get("ACT Symbol") or row.get("NASDAQ Symbol")
        if not raw_symbol:
            continue
        if (row.get("Test Issue") or "N").strip().upper() == "Y":
            continue

        etf_flag = (row.get("ETF") or "N").strip().upper()
        asset_class = "etf" if etf_flag == "Y" else "stock"
        name = (row.get("Security Name") or "").strip() or None
        symbol = normalize_us_symbol_for_yahoo(raw_symbol)
        if not symbol:
            continue

        specs.append(
            TickerSpec(
                yf_symbol=symbol,
                asset_class=asset_class,
                country="us",
                name=name,
                exchange=(row.get("Exchange") or "NASDAQ").strip() or None,
                currency="USD",
                metadata={
                    "source": source,
                    "raw_symbol": raw_symbol.strip().upper(),
                    "nasdaq_etf_flag": etf_flag,
                },
            )
        )
    return dedupe_specs(specs)


def fetch_us_symbol_specs(timeout: float = 30.0) -> list[TickerSpec]:
    specs: list[TickerSpec] = []
    for url, source in (
        (NASDAQ_LISTED_URL, "nasdaq_trader_nasdaqlisted"),
        (OTHER_LISTED_URL, "nasdaq_trader_otherlisted"),
    ):
        log.info("fetching US symbol directory: %s", url)
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        response.raise_for_status()
        specs.extend(parse_nasdaq_symbol_directory(response.text, source=source))
    return dedupe_specs(specs)


def dedupe_specs(specs: Iterable[TickerSpec]) -> list[TickerSpec]:
    """Deduplicate by Yahoo symbol while preserving first occurrence."""
    out: list[TickerSpec] = []
    seen: set[str] = set()
    for spec in specs:
        if spec.yf_symbol in seen:
            continue
        out.append(spec)
        seen.add(spec.yf_symbol)
    return out


def filter_specs_for_universe(specs: Iterable[TickerSpec], universe: str) -> list[TickerSpec]:
    specs = list(specs)
    if universe == "all":
        return specs
    if universe == "us":
        return [s for s in specs if s.country == "us"]
    if universe == "us-stocks":
        return [s for s in specs if s.country == "us" and s.asset_class == "stock"]
    if universe == "us-etfs":
        return [s for s in specs if s.country == "us" and s.asset_class == "etf"]
    if universe == "br":
        return [s for s in specs if s.country == "br"]
    if universe == "br-stocks":
        return [s for s in specs if s.country == "br" and s.asset_class == "stock"]
    if universe == "br-etfs":
        return [s for s in specs if s.country == "br" and s.asset_class == "etf"]
    if universe == "crypto":
        return [s for s in specs if s.asset_class == "crypto"]
    raise ValueError(f"unknown universe={universe!r}")


def resolve_universe(universe: str, br_file: Path, include_us: bool = True) -> list[TickerSpec]:
    specs: list[TickerSpec] = []
    wants_us = universe in {"all", "us", "us-stocks", "us-etfs"}
    wants_br = universe in {"all", "br", "br-stocks", "br-etfs"}
    wants_crypto = universe in {"all", "crypto"}

    if include_us and wants_us:
        specs.extend(fetch_us_symbol_specs())
    if wants_br and universe != "br-etfs":
        specs.extend(parse_br_ticker_file(br_file))
    if wants_br and universe != "br-stocks":
        specs.extend(br_etf_specs())
    if wants_crypto:
        specs.extend(crypto_specs())
    return filter_specs_for_universe(dedupe_specs(specs), universe)


def normalize_yfinance_history(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize yfinance ``Ticker.history`` output to canonical daily columns."""
    if raw.empty:
        return pd.DataFrame(columns=CANONICAL_PRICE_COLUMNS)

    df = raw.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=YF_RENAME_MAP)
    if "adj_close" not in df.columns and "close" in df.columns:
        df["adj_close"] = df["close"]
    for optional in ("dividends", "stock_splits"):
        if optional not in df.columns:
            df[optional] = 0.0

    required = ("open", "high", "low", "close", "adj_close", "volume")
    missing = [column for column in required if column not in df]
    if missing:
        raise ValueError(f"yfinance output missing expected columns: {missing}")

    df = df[CANONICAL_PRICE_COLUMNS].copy()
    for column in CANONICAL_PRICE_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    index = pd.to_datetime(df.index)
    if index.tz is not None:
        index = index.tz_localize(None)
    df.index = pd.DatetimeIndex(index.date, name="date")
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df.dropna(subset=["close", "adj_close"], how="all")
    return df


def fetch_yfinance_history(
    symbol: str,
    *,
    period: str = "max",
    start: date | None = None,
    end: date | None = None,
) -> pd.DataFrame:
    """Fetch one ticker from yfinance and normalize the result."""
    import yfinance as yf

    ticker = yf.Ticker(symbol)
    kwargs: dict[str, Any] = {
        "interval": "1d",
        "auto_adjust": False,
        "actions": True,
    }
    if start is not None or end is not None:
        kwargs["start"] = start.isoformat() if start is not None else None
        # yfinance treats end as exclusive; add one day for an inclusive CLI end.
        kwargs["end"] = (end + timedelta(days=1)).isoformat() if end is not None else None
    else:
        kwargs["period"] = period
    raw = ticker.history(**kwargs)
    return normalize_yfinance_history(raw)


def scalar_or_none(value: object, *, integer: bool = False) -> float | int | None:
    if pd.isna(value):
        return None
    if integer:
        return int(float(value))
    return float(value)


def price_rows_from_frame(ticker_id: int, frame: pd.DataFrame) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    fetched_at = datetime.now(timezone.utc)
    for ts, row in frame.iterrows():
        rows.append(
            (
                ticker_id,
                pd.Timestamp(ts).date(),
                scalar_or_none(row["open"]),
                scalar_or_none(row["high"]),
                scalar_or_none(row["low"]),
                scalar_or_none(row["close"]),
                scalar_or_none(row["adj_close"]),
                scalar_or_none(row["volume"], integer=True),
                scalar_or_none(row["dividends"]),
                scalar_or_none(row["stock_splits"]),
                fetched_at,
            )
        )
    return rows


def create_schema(conn: Any, schema: str) -> None:
    """Create yfinance tables and query-oriented indexes."""
    from psycopg import sql

    ticker_table = sql.Identifier(schema, "yf_tickers")
    price_table = sql.Identifier(schema, "yf_daily_prices")

    conn.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema)))
    conn.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {ticker_table} (
                id BIGSERIAL PRIMARY KEY,
                yf_symbol TEXT NOT NULL UNIQUE,
                asset_class TEXT NOT NULL CHECK (asset_class IN ('stock', 'etf', 'crypto')),
                country TEXT NOT NULL CHECK (country IN ('us', 'br', 'global')),
                name TEXT,
                exchange TEXT,
                currency TEXT,
                active BOOLEAN NOT NULL DEFAULT TRUE,
                first_date DATE,
                last_date DATE,
                last_synced_at TIMESTAMPTZ,
                last_error TEXT,
                metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        ).format(ticker_table=ticker_table)
    )
    conn.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {price_table} (
                ticker_id BIGINT NOT NULL REFERENCES {ticker_table}(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                adj_close DOUBLE PRECISION,
                volume BIGINT,
                dividends DOUBLE PRECISION,
                stock_splits DOUBLE PRECISION,
                fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                PRIMARY KEY (ticker_id, date)
            )
            """
        ).format(price_table=price_table, ticker_table=ticker_table)
    )
    conn.execute(
        sql.SQL(
            """
            CREATE INDEX IF NOT EXISTS yf_tickers_country_class_active_idx
            ON {ticker_table} (country, asset_class, active)
            """
        ).format(ticker_table=ticker_table)
    )
    conn.execute(
        sql.SQL(
            """
            CREATE INDEX IF NOT EXISTS yf_daily_prices_date_ticker_idx
            ON {price_table} (date, ticker_id) INCLUDE (adj_close, close, volume)
            """
        ).format(price_table=price_table)
    )
    conn.execute(
        sql.SQL(
            """
            CREATE INDEX IF NOT EXISTS yf_daily_prices_ticker_date_desc_idx
            ON {price_table} (ticker_id, date DESC)
            """
        ).format(price_table=price_table)
    )
    conn.execute(
        sql.SQL(
            """
            CREATE INDEX IF NOT EXISTS yf_daily_prices_date_brin_idx
            ON {price_table} USING BRIN (date)
            """
        ).format(price_table=price_table)
    )


def upsert_ticker(conn: Any, schema: str, spec: TickerSpec) -> int:
    from psycopg import sql
    from psycopg.types.json import Jsonb

    ticker_table = sql.Identifier(schema, "yf_tickers")
    query = sql.SQL(
        """
        INSERT INTO {ticker_table} AS t
            (yf_symbol, asset_class, country, name, exchange, currency, active, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE, %s)
        ON CONFLICT (yf_symbol) DO UPDATE SET
            asset_class = EXCLUDED.asset_class,
            country = EXCLUDED.country,
            name = COALESCE(EXCLUDED.name, t.name),
            exchange = COALESCE(EXCLUDED.exchange, t.exchange),
            currency = COALESCE(EXCLUDED.currency, t.currency),
            active = TRUE,
            metadata = EXCLUDED.metadata,
            updated_at = now()
        RETURNING id
        """
    ).format(ticker_table=ticker_table)
    row = conn.execute(
        query,
        (
            spec.yf_symbol,
            spec.asset_class,
            spec.country,
            spec.name,
            spec.exchange,
            spec.currency,
            Jsonb(spec.metadata),
        ),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"failed to upsert ticker {spec.yf_symbol}")
    return int(row[0])


def latest_date_for_ticker(conn: Any, schema: str, ticker_id: int) -> date | None:
    from psycopg import sql

    ticker_table = sql.Identifier(schema, "yf_tickers")
    row = conn.execute(
        sql.SQL("SELECT last_date FROM {ticker_table} WHERE id = %s").format(
            ticker_table=ticker_table
        ),
        (ticker_id,),
    ).fetchone()
    if row is None or row[0] is None:
        return None
    return row[0]


def upsert_prices(conn: Any, schema: str, rows: list[tuple[Any, ...]], batch_size: int) -> None:
    if not rows:
        return
    from psycopg import sql

    price_table = sql.Identifier(schema, "yf_daily_prices")
    query = sql.SQL(
        """
        INSERT INTO {price_table}
            (ticker_id, date, open, high, low, close, adj_close, volume,
             dividends, stock_splits, fetched_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker_id, date) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            adj_close = EXCLUDED.adj_close,
            volume = EXCLUDED.volume,
            dividends = EXCLUDED.dividends,
            stock_splits = EXCLUDED.stock_splits,
            fetched_at = EXCLUDED.fetched_at
        """
    ).format(price_table=price_table)
    for start in range(0, len(rows), batch_size):
        with conn.cursor() as cur:
            cur.executemany(query, rows[start : start + batch_size])


def refresh_ticker_coverage(conn: Any, schema: str, ticker_id: int) -> None:
    from psycopg import sql

    ticker_table = sql.Identifier(schema, "yf_tickers")
    price_table = sql.Identifier(schema, "yf_daily_prices")
    conn.execute(
        sql.SQL(
            """
            UPDATE {ticker_table} t
            SET first_date = p.first_date,
                last_date = p.last_date,
                last_synced_at = now(),
                last_error = NULL,
                active = TRUE,
                updated_at = now()
            FROM (
                SELECT ticker_id, min(date) AS first_date, max(date) AS last_date
                FROM {price_table}
                WHERE ticker_id = %s
                GROUP BY ticker_id
            ) p
            WHERE t.id = p.ticker_id
            """
        ).format(ticker_table=ticker_table, price_table=price_table),
        (ticker_id,),
    )


def mark_ticker_error(conn: Any, schema: str, ticker_id: int, error: str, *, active: bool) -> None:
    from psycopg import sql

    ticker_table = sql.Identifier(schema, "yf_tickers")
    conn.execute(
        sql.SQL(
            """
            UPDATE {ticker_table}
            SET active = %s,
                last_synced_at = now(),
                last_error = %s,
                updated_at = now()
            WHERE id = %s
            """
        ).format(ticker_table=ticker_table),
        (active, error[:1000], ticker_id),
    )


def sync_one_ticker(
    conn: Any,
    schema: str,
    spec: TickerSpec,
    *,
    period: str,
    start: date | None,
    end: date | None,
    incremental: bool,
    overlap_days: int,
    batch_size: int,
) -> tuple[str, int]:
    """Sync a single ticker and return (status, n_rows)."""
    ticker_id = upsert_ticker(conn, schema, spec)
    fetch_start = start
    fetch_end = end
    fetch_period = period
    if incremental:
        last_date = latest_date_for_ticker(conn, schema, ticker_id)
        if last_date is not None:
            fetch_start = last_date - timedelta(days=overlap_days)
            fetch_period = ""
        fetch_end = fetch_end or date.today()

    frame = fetch_yfinance_history(
        spec.yf_symbol,
        period=fetch_period or period,
        start=fetch_start,
        end=fetch_end,
    )
    if frame.empty:
        mark_ticker_error(conn, schema, ticker_id, "empty yfinance response", active=False)
        return "empty", 0

    rows = price_rows_from_frame(ticker_id, frame)
    upsert_prices(conn, schema, rows, batch_size=batch_size)
    refresh_ticker_coverage(conn, schema, ticker_id)
    return "synced", len(rows)


def parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def summarize_specs(specs: Iterable[TickerSpec]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for spec in specs:
        key = f"{spec.country}/{spec.asset_class}"
        summary[key] = summary.get(key, 0) + 1
    return dict(sorted(summary.items()))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync yfinance daily OHLCV into Postgres.")
    parser.add_argument(
        "--universe",
        choices=[
            "all",
            "us",
            "us-stocks",
            "us-etfs",
            "br",
            "br-stocks",
            "br-etfs",
            "crypto",
        ],
        default=env_or_default("YFINANCE_UNIVERSE", "all"),
        help="Ticker universe to sync (default: all).",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Overrides YFINANCE_DATABASE_URL/DATABASE_URL.",
    )
    parser.add_argument("--schema", default=env_or_default("YFINANCE_SCHEMA", DEFAULT_SCHEMA))
    parser.add_argument(
        "--br-file",
        type=Path,
        default=Path(env_or_default("YFINANCE_BR_TICKERS_FILE", str(DEFAULT_BR_FILE))),
    )
    parser.add_argument("--period", default=env_or_default("YFINANCE_PERIOD", "max"))
    parser.add_argument("--start", default=os.getenv("YFINANCE_START"))
    parser.add_argument("--end", default=os.getenv("YFINANCE_END"))
    parser.add_argument("--limit", type=int, default=None, help="Limit tickers for smoke runs.")
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Resolve universe and exit without DB/network price sync.",
    )
    parser.add_argument(
        "--init-schema",
        dest="init_schema",
        action="store_true",
        default=True,
        help="Create tables/indexes before syncing (default).",
    )
    parser.add_argument("--no-init-schema", dest="init_schema", action="store_false")
    parser.add_argument("--incremental", action="store_true", help="Fetch from last_date minus overlap.")
    parser.add_argument(
        "--overlap-days",
        type=int,
        default=int(env_or_default("YFINANCE_OVERLAP_DAYS", "7")),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(env_or_default("YFINANCE_BATCH_SIZE", "1000")),
    )
    parser.add_argument(
        "--throttle-ms",
        type=int,
        default=int(env_or_default("YFINANCE_THROTTLE_MS", "250")),
    )
    parser.add_argument("--log-level", default=env_or_default("YFINANCE_LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    load_env_file()
    args = parse_args(argv)
    setup_logging(args.log_level)

    start = parse_date(args.start)
    end = parse_date(args.end)
    if start is not None and end is not None and start > end:
        raise ValueError("--start cannot be after --end")
    if not args.br_file.exists() and args.universe in {"all", "br", "br-stocks"}:
        raise FileNotFoundError(f"BR ticker file not found: {args.br_file}")

    specs = resolve_universe(args.universe, args.br_file)
    if args.limit is not None:
        specs = specs[: args.limit]
    summary = summarize_specs(specs)
    log.info("resolved %d tickers: %s", len(specs), summary)

    if args.list_only:
        print(f"Resolved {len(specs)} tickers")
        for key, count in summary.items():
            print(f"{key}: {count}")
        return 0

    import psycopg

    database_url = database_url_from_env(args.database_url)
    counts = {"synced": 0, "empty": 0, "error": 0}
    rows_written = 0
    with psycopg.connect(database_url) as conn:
        if args.init_schema:
            create_schema(conn, args.schema)
            conn.commit()

        for index, spec in enumerate(specs, start=1):
            log.info(
                "[%d/%d] sync %s (%s/%s)",
                index,
                len(specs),
                spec.yf_symbol,
                spec.country,
                spec.asset_class,
            )
            try:
                status, n_rows = sync_one_ticker(
                    conn,
                    args.schema,
                    spec,
                    period=args.period,
                    start=start,
                    end=end,
                    incremental=args.incremental,
                    overlap_days=args.overlap_days,
                    batch_size=args.batch_size,
                )
                conn.commit()
                counts[status] = counts.get(status, 0) + 1
                rows_written += n_rows
                log.info("%s %s rows=%d", status.upper(), spec.yf_symbol, n_rows)
            except Exception as exc:  # noqa: BLE001 - long-running sync should continue.
                conn.rollback()
                counts["error"] += 1
                log.warning("ERROR %s: %s", spec.yf_symbol, exc)
                try:
                    ticker_id = upsert_ticker(conn, args.schema, spec)
                    mark_ticker_error(conn, args.schema, ticker_id, str(exc), active=True)
                    conn.commit()
                except Exception as mark_exc:  # noqa: BLE001
                    conn.rollback()
                    log.error("failed to mark error for %s: %s", spec.yf_symbol, mark_exc)
            if args.throttle_ms > 0:
                time.sleep(args.throttle_ms / 1000.0)

    log.info("done counts=%s rows_written=%d", counts, rows_written)
    print(f"Done: {counts}; rows_written={rows_written}")
    return 0 if counts.get("error", 0) == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
