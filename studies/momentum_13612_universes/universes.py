"""Universe definitions and price loaders for the 13612 universe study.

US stock/ETF screens can use the existing Tiingo manifest/cache or explicit
yfinance fetches. BR stocks can read the user's 1-minute Postgres database and
collapse it to daily closes; BR ETFs use a curated current list through yfinance.
Any yfinance/current-list result remains screen-only because current membership
and missing delisted tickers create survivorship bias `[advances_fin_ml,
p.208-211]`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

import pandas as pd

from market_lab.backtest.data.br_tickers import IBRX100_TICKERS
from market_lab.backtest.data.wikipedia_spx import WikipediaSPX, constituents_on
from market_lab.backtest.data.yfinance_source import YFinanceSource


US_LIQUID_ETFS: tuple[str, ...] = (
    "SPY", "IVV", "VOO", "VTI", "QQQ", "DIA", "IWM", "RSP", "MDY", "IJR",
    "EFA", "VEA", "EEM", "VWO", "ACWI", "VT", "IEMG", "IEFA", "EWJ", "EWU",
    "EWG", "EWQ", "EWC", "FXI", "INDA", "EWZ", "ILF", "VNQ", "IYR", "XLK",
    "XLF", "XLV", "XLY", "XLP", "XLI", "XLE", "XLU", "XLB", "XLRE", "XLC",
    "SMH", "SOXX", "IBB", "XBI", "KRE", "IYT", "TLT", "IEF", "SHY", "IEI",
    "AGG", "BND", "LQD", "HYG", "TIP", "GLD", "IAU", "SLV", "DBC", "PDBC",
    "USO", "UUP", "DBMF", "KMLM",
)

BR_CURATED_ETFS: tuple[str, ...] = (
    "BOVA11.SA", "BOVV11.SA", "PIBB11.SA", "SMAL11.SA", "DIVO11.SA",
    "FIND11.SA", "MATB11.SA", "GOVE11.SA", "ECOO11.SA", "ISUS11.SA",
    "IVVB11.SA", "SPXI11.SA", "NASD11.SA", "WRLD11.SA", "ACWI11.SA",
    "EURP11.SA", "GOLD11.SA", "B5P211.SA", "IMAB11.SA", "IRFM11.SA",
    "FIXA11.SA", "XFIX11.SA", "HASH11.SA", "QBTC11.SA", "QETH11.SA",
    "ETHE11.SA", "META11.SA",
)


@dataclass(frozen=True)
class PostgresDailyCloseConfig:
    """Configurable adapter for a BR 1-minute OHLCV table.

    The default column names are intentionally conventional only. Override them
    with the runner CLI flags when the local schema differs. The loader uses the
    last intraday bar per ticker/calendar day as the daily close.
    """

    database_url: str
    table: str = "quotes_1m"
    ticker_column: str = "ticker"
    timestamp_column: str = "ts"
    close_column: str = "close"
    strip_sa_suffix: bool = True


def manifest_tickers_by_asset_class(root: Path = Path("data/tiingo")) -> dict[str, list[str]]:
    """Read Tiingo manifest and group tickers by asset class."""
    import json

    manifest_path = Path(root) / "manifest.json"
    if not manifest_path.exists():
        return {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    grouped: dict[str, list[str]] = {}
    for ticker, entries in manifest.items():
        daily = entries.get("daily", {}) if isinstance(entries, dict) else {}
        asset_class = daily.get("asset_class")
        if asset_class:
            grouped.setdefault(str(asset_class), []).append(str(ticker).upper())
    return {key: sorted(set(values)) for key, values in grouped.items()}


def normalize_yfinance_us_ticker(ticker: str) -> str:
    """Map dotted US share classes to Yahoo's dashed convention."""
    return ticker.strip().upper().replace(".", "-")


def current_sp500_tickers() -> list[str]:
    """Current S&P 500 fallback universe for US stock screens."""
    raw = WikipediaSPX().current_tickers(use_cache=True)
    return sorted({normalize_yfinance_us_ticker(ticker) for ticker in raw})


def us_stock_tickers(
    tiingo_root: Path,
    limit: int | None = None,
    universe: str = "sp500",
) -> list[str]:
    """US stock universe for screens.

    ``sp500`` is the yfinance-friendly default. ``tiingo_manifest`` is available
    when the restored local cache should define the broader historical universe.
    ``sp500_wikipedia_pit`` must be loaded through
    :func:`us_stock_tickers_with_membership` because it needs date-specific
    eligibility to avoid treating today's S&P 500 as a historical universe
    `[advances_fin_ml, p.208-211]`.
    """
    if universe == "sp500":
        tickers = current_sp500_tickers()
    elif universe == "tiingo_manifest":
        grouped = manifest_tickers_by_asset_class(tiingo_root)
        tickers = grouped.get("equity") or current_sp500_tickers()
    elif universe == "sp500_wikipedia_pit":
        raise ValueError("sp500_wikipedia_pit requires us_stock_tickers_with_membership")
    else:
        raise ValueError("US stock universe must be 'sp500', 'tiingo_manifest' or 'sp500_wikipedia_pit'")
    out = [normalize_yfinance_us_ticker(ticker) for ticker in tickers]
    return sorted(set(out))[:limit] if limit is not None else sorted(set(out))


def month_end_dates_for_range(start: str | None, end: str | None) -> pd.DatetimeIndex:
    """Month-end labels used for date-specific constituent reconstruction."""
    start_ts = pd.Timestamp(start) if start else pd.Timestamp("1927-01-01")
    end_ts = pd.Timestamp(end) if end else pd.Timestamp(date.today())
    dates = list(pd.date_range(start_ts, end_ts, freq="ME"))
    final_month_end = end_ts.to_period("M").to_timestamp("M")
    if not dates or pd.Timestamp(final_month_end) not in dates:
        dates.append(pd.Timestamp(final_month_end))
    return pd.DatetimeIndex(sorted(set(pd.Timestamp(value) for value in dates)))


def sp500_pit_membership_from_changes(
    month_ends: Iterable[pd.Timestamp],
    current: set[str],
    changes: pd.DataFrame,
    limit: int | None = None,
) -> tuple[list[str], dict[pd.Timestamp, set[str]]]:
    """Build a Wikipedia S&P 500 PIT-ish membership map.

    Wikipedia's selected-changes table is not a delisted-price feed. It only
    reduces the current-constituent look-ahead by restricting each rebalance to
    constituents reconstructed for that date `[advances_fin_ml, p.208-211]`.
    """
    membership: dict[pd.Timestamp, set[str]] = {}
    all_tickers: set[str] = set()
    for raw_date in pd.DatetimeIndex(month_ends).sort_values().unique():
        ts = pd.Timestamp(raw_date)
        members = {
            normalize_yfinance_us_ticker(ticker)
            for ticker in constituents_on(ts.date(), current, changes)
        }
        membership[ts] = members
        all_tickers.update(members)

    tickers = sorted(all_tickers)
    if limit is not None:
        allowed = set(tickers[:limit])
        tickers = sorted(allowed)
        membership = {date_key: members & allowed for date_key, members in membership.items()}
    return tickers, membership


def wikipedia_sp500_pit_tickers(
    start: str | None,
    end: str | None,
    limit: int | None = None,
    use_cache: bool = True,
) -> tuple[list[str], dict[pd.Timestamp, set[str]]]:
    """Return union tickers and month-end eligibility for Wikipedia SPX PIT-ish runs."""
    source = WikipediaSPX()
    current, changes = source.fetch_tables(use_cache=use_cache)
    symbol_col = next(
        (column for column in current.columns if str(column).lower() in {"symbol", "ticker"}),
        None,
    )
    if symbol_col is None:
        raise ValueError(f"Expected Symbol/Ticker column in current table; got {list(current.columns)}")
    current_tickers = set(current[symbol_col].dropna().astype(str))
    return sp500_pit_membership_from_changes(
        month_end_dates_for_range(start, end),
        current_tickers,
        changes,
        limit=limit,
    )


def us_stock_tickers_with_membership(
    tiingo_root: Path,
    limit: int | None = None,
    universe: str = "sp500",
    start: str | None = None,
    end: str | None = None,
) -> tuple[list[str], dict[pd.Timestamp, set[str]] | None]:
    """Return US stock tickers plus optional date-specific eligibility.

    The PIT-ish Wikipedia mode uses selected historical S&P 500 changes to avoid
    ranking against today's constituents in old rebalance dates. It remains
    research-only because Wikipedia is incomplete and yfinance still lacks a true
    delisted-price/return feed `[advances_fin_ml, p.208-211]`.
    """
    if universe == "sp500_wikipedia_pit":
        tickers, membership = wikipedia_sp500_pit_tickers(start, end, limit=limit)
        return tickers, membership
    return us_stock_tickers(tiingo_root, limit=limit, universe=universe), None


def us_etf_tickers(
    tiingo_root: Path,
    limit: int | None = None,
    universe: str = "curated",
) -> list[str]:
    """US ETF universe for screens."""
    if universe == "curated":
        tickers = list(US_LIQUID_ETFS)
    elif universe == "tiingo_manifest":
        grouped = manifest_tickers_by_asset_class(tiingo_root)
        tickers = grouped.get("etf") or list(US_LIQUID_ETFS)
    else:
        raise ValueError("US ETF universe must be 'curated' or 'tiingo_manifest'")
    out = [normalize_yfinance_us_ticker(ticker) for ticker in tickers]
    return sorted(set(out))[:limit] if limit is not None else sorted(set(out))


def br_stock_tickers(limit: int | None = None) -> list[str]:
    """Current IBrX-100 proxy tickers for BR stock screens."""
    tickers = sorted({ticker.upper() for ticker in IBRX100_TICKERS})
    return tickers[:limit] if limit is not None else tickers


def br_etf_tickers(limit: int | None = None) -> list[str]:
    """Curated current BR ETF list for screen-only yfinance runs."""
    tickers = sorted({ticker.upper() for ticker in BR_CURATED_ETFS})
    return tickers[:limit] if limit is not None else tickers


def load_tiingo_price_frame(
    tickers: Iterable[str],
    root: Path = Path("data/tiingo"),
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """Load adjusted-close prices from local Tiingo parquets only."""
    prices_dir = Path(root) / "daily" / "prices"
    if not prices_dir.exists():
        raise FileNotFoundError(
            f"Tiingo price directory not found: {prices_dir}. Restore parquets before use."
        )

    frames: dict[str, pd.Series] = {}
    missing: list[str] = []
    for ticker in sorted({str(t).upper() for t in tickers}):
        path = prices_dir / f"{ticker}.parquet"
        if not path.exists():
            missing.append(ticker)
            continue
        df = pd.read_parquet(path)
        column = (
            "adj_close"
            if "adj_close" in df.columns
            else "adjClose"
            if "adjClose" in df.columns
            else "close"
        )
        if column not in df.columns:
            raise KeyError(f"{path} has no adj_close/adjClose/close column")
        series = pd.to_numeric(df[column], errors="coerce").dropna().astype(float).sort_index()
        series.index = pd.DatetimeIndex(series.index).tz_localize(None)
        frames[ticker] = series.rename(ticker)

    if missing:
        suffix = "..." if len(missing) > 25 else ""
        raise FileNotFoundError(f"Missing Tiingo parquet files for: {missing[:25]}{suffix}")
    if not frames:
        raise FileNotFoundError(f"No Tiingo parquets loaded from {prices_dir}")
    return _slice_price_frame(pd.DataFrame(frames).sort_index(), start, end)


def load_yfinance_price_frame(
    tickers: Iterable[str],
    start: str | None = None,
    end: str | None = None,
    allow_missing: bool = True,
) -> pd.DataFrame:
    """Load adjusted-close prices from yfinance for explicit biased screens."""
    fetcher = YFinanceSource()
    start_date = pd.Timestamp(start).date() if start else date(1927, 1, 1)
    end_date = pd.Timestamp(end).date() + timedelta(days=1) if end else date.today() + timedelta(days=1)

    frames: dict[str, pd.Series] = {}
    missing: list[str] = []
    for ticker in sorted({str(t).upper() for t in tickers}):
        df = fetcher.fetch(ticker, start=start_date, end=end_date, use_cache=True)
        if df.empty:
            missing.append(ticker)
            continue
        series = pd.to_numeric(df["adj_close"], errors="coerce").dropna().astype(float).sort_index()
        series.index = pd.DatetimeIndex(series.index).tz_localize(None)
        frames[ticker] = series.rename(ticker)

    if missing and not allow_missing:
        suffix = "..." if len(missing) > 25 else ""
        raise FileNotFoundError(f"yfinance returned no data for: {missing[:25]}{suffix}")
    if not frames:
        raise FileNotFoundError("No yfinance prices loaded")
    out = pd.DataFrame(frames).sort_index()
    out.attrs["missing_tickers"] = sorted(missing)
    return _slice_price_frame(out, start, end)


def drop_extreme_return_tickers(
    prices: pd.DataFrame,
    max_abs_daily_return: float | None,
) -> tuple[pd.DataFrame, list[str]]:
    """Drop tickers with impossible adjusted-close jumps.

    This is a data-quality guard for yfinance/PIT-ish diagnostics, not a strategy
    filter. It catches stale ticker reuse, bad split adjustments and delisted
    symbols with broken adjusted closes before they contaminate momentum ranks
    `[advances_fin_ml, p.31-34]`, `[advances_fin_ml, p.208-211]`.
    """
    if max_abs_daily_return is None:
        return prices, []
    if max_abs_daily_return <= 0.0:
        raise ValueError("max_abs_daily_return must be positive")
    returns = prices.astype(float).pct_change(fill_method=None)
    bad = sorted(
        str(column)
        for column in returns.columns
        if returns[column].abs().max(skipna=True) > max_abs_daily_return
    )
    if not bad:
        return prices, []
    return prices.drop(columns=bad, errors="ignore"), bad


def load_postgres_daily_close_frame(
    tickers: Iterable[str],
    config: PostgresDailyCloseConfig,
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """Load BR daily closes from a 1-minute Postgres quote table.

    The query selects the last intraday close per ticker/day. It does not assume
    adjusted prices; reports using it must disclose that corporate-action quality
    is not audited until the local database schema/source is documented.
    """
    import psycopg
    from psycopg import sql

    requested = [str(ticker).upper() for ticker in tickers]
    db_symbols = [_postgres_symbol(ticker, config.strip_sa_suffix) for ticker in requested]
    output_by_db_symbol = dict(zip(db_symbols, requested, strict=False))
    params: list[object] = [db_symbols]

    table = _sql_identifier(config.table)
    ticker_col = sql.Identifier(config.ticker_column)
    ts_col = sql.Identifier(config.timestamp_column)
    close_col = sql.Identifier(config.close_column)

    ticker_expr = sql.SQL("upper({}::text)").format(ticker_col)
    where_parts = [sql.SQL("{} = ANY(%s)").format(ticker_expr)]
    if start is not None:
        where_parts.append(sql.SQL("{} >= %s").format(ts_col))
        params.append(pd.Timestamp(start).to_pydatetime())
    if end is not None:
        where_parts.append(sql.SQL("{} <= %s").format(ts_col))
        params.append(pd.Timestamp(end).to_pydatetime())

    query = sql.SQL(
        """
        WITH last_bar AS (
            SELECT DISTINCT ON ({ticker_col}, date_trunc('day', {ts_col}))
                upper({ticker_col}::text) AS ticker,
                date_trunc('day', {ts_col})::date AS session_date,
                {close_col}::double precision AS close
            FROM {table}
            WHERE {where_clause}
            ORDER BY {ticker_col}, date_trunc('day', {ts_col}), {ts_col} DESC
        )
        SELECT ticker, session_date, close
        FROM last_bar
        ORDER BY session_date, ticker
        """
    ).format(
        ticker_col=ticker_col,
        ts_col=ts_col,
        close_col=close_col,
        table=table,
        where_clause=sql.SQL(" AND ").join(where_parts),
    )

    with psycopg.connect(config.database_url) as conn:
        rows = conn.execute(query, params).fetchall()
    if not rows:
        raise FileNotFoundError("Postgres returned no BR quote rows for requested tickers")

    df = pd.DataFrame(rows, columns=["ticker", "date", "close"])
    df["ticker"] = df["ticker"].map(output_by_db_symbol).fillna(df["ticker"].astype(str).str.upper())
    df["date"] = pd.to_datetime(df["date"])
    out = df.pivot(index="date", columns="ticker", values="close").sort_index()
    out.attrs["source"] = "postgres_1m_last_bar_daily_close"
    return _slice_price_frame(out, start, end)


def masked_database_url(database_url: str) -> str:
    """Return a report-safe database URL label."""
    if "@" not in database_url:
        return database_url
    scheme, rest = database_url.split("://", 1) if "://" in database_url else ("", database_url)
    host_part = rest.split("@", 1)[1]
    return f"{scheme}://***:***@{host_part}" if scheme else f"***:***@{host_part}"


def env_or_default(name: str, default: str) -> str:
    """Read an environment override without leaking env handling into run.py."""
    return os.getenv(name, default)


def _slice_price_frame(frame: pd.DataFrame, start: str | None, end: str | None) -> pd.DataFrame:
    out = frame.sort_index()
    if start is not None:
        out = out.loc[pd.Timestamp(start):]
    if end is not None:
        out = out.loc[:pd.Timestamp(end)]
    return out


def _postgres_symbol(ticker: str, strip_sa_suffix: bool) -> str:
    out = str(ticker).upper()
    if strip_sa_suffix and out.endswith(".SA"):
        return out[:-3]
    return out


def _sql_identifier(name: str):
    from psycopg import sql

    parts = [part for part in name.split(".") if part]
    if not parts:
        raise ValueError("SQL identifier cannot be empty")
    return sql.Identifier(*parts)
