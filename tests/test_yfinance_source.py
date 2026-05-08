"""Unit tests for yfinance source — pure-logic, no network."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from market_lab.backtest.data.yfinance_source import YFinanceSource, _normalize


def _make_raw_yf(tz: str | None = None, multiindex: bool = False) -> pd.DataFrame:
    idx = pd.DatetimeIndex(["2024-01-02", "2024-01-03"], tz=tz)
    data = [
        [100.0, 101.0, 99.5, 100.5, 100.4, 1_000_000],
        [100.5, 102.0, 100.0, 101.8, 101.7, 1_200_000],
    ]
    cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    df = pd.DataFrame(data, index=idx, columns=cols)
    if multiindex:
        df.columns = pd.MultiIndex.from_product([cols, ["AAPL"]])
    return df


def test_normalize_renames_to_canonical_columns():
    out = _normalize(_make_raw_yf())
    assert list(out.columns) == ["open", "high", "low", "close", "adj_close", "volume"]


def test_normalize_strips_timezone():
    out = _normalize(_make_raw_yf(tz="UTC"))
    assert out.index.tz is None
    assert out.index.name == "date"


def test_normalize_flattens_multiindex_columns():
    raw = _make_raw_yf(multiindex=True)
    assert isinstance(raw.columns, pd.MultiIndex)  # sanity — input really has MultiIndex
    out = _normalize(raw)
    assert list(out.columns) == ["open", "high", "low", "close", "adj_close", "volume"]
    assert not isinstance(out.columns, pd.MultiIndex)


def test_normalize_passes_through_empty_frame():
    empty = pd.DataFrame()
    out = _normalize(empty)
    assert out.empty


def test_normalize_raises_on_missing_column():
    bad = _make_raw_yf().drop(columns=["Volume"])
    with pytest.raises(ValueError, match="missing expected columns"):
        _normalize(bad)


def test_fetch_reads_from_cache_when_window_covered(tmp_path: Path):
    source = YFinanceSource(cache_dir=tmp_path)

    cached = _normalize(_make_raw_yf())
    # Extend cached data to ensure window [2024-01-02, 2024-01-03] is fully inside.
    source._cache_path("AAPL")
    cache_file = source.cache_dir / "AAPL.parquet"
    cached.to_parquet(cache_file)

    out = source.fetch("AAPL", date(2024, 1, 2), date(2024, 1, 3))
    assert not out.empty
    assert list(out.columns) == ["open", "high", "low", "close", "adj_close", "volume"]
    assert len(out) == 2


def test_cache_path_sanitizes_slashes(tmp_path: Path):
    source = YFinanceSource(cache_dir=tmp_path)
    p = source._cache_path("BRK/B")
    assert p.name == "BRK_B.parquet"
    assert p.parent == tmp_path
