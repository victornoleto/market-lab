"""Data helpers for ``studies.weekly_momentum``.

The study reads the existing Tiingo parquet cache through ``TiingoStorage`` and
uses adjusted close when available. Universes are current-cache universes, so any
report using them must disclose survivorship bias unless a point-in-time source
is substituted.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from collections.abc import Callable

import pandas as pd

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from market_lab.backtest.data.wikipedia_spx import WikipediaSPX, constituents_on

VARIATION_TO_ASSET_CLASS = {
    "stocks": "equity",
    "etfs": "etf",
}


def list_universe(
    variation: str,
    storage_root: str | Path = "data/tiingo",
    stock_universe: str = "sp500",
    only_sp500: bool | None = None,
) -> list[str]:
    """List cached Tiingo tickers for ``stocks`` or ``etfs`` variation.

    ``stocks`` defaults to the current S&P 500 constituent list as a liquidity
    and listing-quality filter. This is still not point-in-time and reports must
    disclose survivorship bias. S&P 500 membership source caveats follow the
    Wikipedia adapter docstring.
    """
    asset_class = VARIATION_TO_ASSET_CLASS.get(variation)
    if asset_class is None:
        raise ValueError("variation must be 'stocks' or 'etfs'")
    storage = TiingoStorage(root=Path(storage_root))
    tickers = storage.list_tickers(asset_class=asset_class)
    if only_sp500 is not None:
        stock_universe = "sp500" if only_sp500 else "all"
    if variation != "stocks":
        return tickers
    if stock_universe == "all":
        return tickers
    if stock_universe != "sp500":
        raise ValueError("stock_universe must be 'sp500' or 'all'")
    sp500 = _current_sp500_tickers()
    return [ticker for ticker in tickers if ticker in sp500]


def load_price_frame(
    tickers: list[str],
    storage_root: str | Path = "data/tiingo",
    start: date | None = None,
    end: date | None = None,
    min_bars: int = 30,
) -> pd.DataFrame:
    """Load adjusted-close prices for the requested tickers from Tiingo cache."""
    storage = TiingoStorage(root=Path(storage_root))
    series: dict[str, pd.Series] = {}
    for ticker in tickers:
        try:
            df = storage.read(ticker, start=start, end=end, frequency="daily")
        except (FileNotFoundError, KeyError):
            continue
        if df.empty or len(df) < min_bars:
            continue
        column = "adj_close" if "adj_close" in df.columns else "close"
        if column not in df.columns:
            continue
        s = pd.to_numeric(df[column], errors="coerce").dropna()
        if len(s) >= min_bars:
            series[ticker] = s.rename(ticker)
    if not series:
        return pd.DataFrame()
    return pd.concat(series.values(), axis=1, sort=True).sort_index()


def load_variation_prices(
    variation: str,
    storage_root: str | Path = "data/tiingo",
    start: date | None = None,
    end: date | None = None,
    min_bars: int = 30,
    max_tickers: int | None = None,
    stock_universe: str = "sp500",
    only_sp500: bool | None = None,
) -> pd.DataFrame:
    """Load prices for all cached tickers in one study variation."""
    tickers = list_universe(
        variation,
        storage_root=storage_root,
        stock_universe=stock_universe,
        only_sp500=only_sp500,
    )
    if max_tickers is not None:
        tickers = tickers[:max_tickers]
    return load_price_frame(
        tickers,
        storage_root=storage_root,
        start=start,
        end=end,
        min_bars=min_bars,
    )


def sp500_pit_universe_provider() -> Callable[[pd.Timestamp], set[str]]:
    """Return cached callable for approximate point-in-time S&P 500 membership.

    This uses Wikipedia's current constituents plus selected historical changes.
    It is an improvement over current-only membership, but still not a paid
    survivorship-free/delisted feed `[advances_fin_ml, p.208-211]`.
    """
    source = WikipediaSPX()
    current = source.current_tickers(use_cache=True)
    _, changes = source.fetch_tables(use_cache=True)
    cache: dict[date, set[str]] = {}

    def provider(ts: pd.Timestamp) -> set[str]:
        day = pd.Timestamp(ts).date()
        if day not in cache:
            raw = constituents_on(day, current, changes)
            out: set[str] = set()
            for ticker in raw:
                t = ticker.strip().upper()
                out.add(t)
                out.add(t.replace(".", "-"))
            cache[day] = out
        return cache[day]

    return provider


def _current_sp500_tickers() -> set[str]:
    """Current S&P 500 tickers normalized to Tiingo/cache symbols.

    Wikipedia uses dotted share classes (e.g. BRK.B), and this cache currently
    stores the same dotted form, so both dotted and dashed variants are accepted.
    """
    raw = WikipediaSPX().current_tickers(use_cache=True)
    out: set[str] = set()
    for ticker in raw:
        t = ticker.strip().upper()
        out.add(t)
        out.add(t.replace(".", "-"))
    return out
