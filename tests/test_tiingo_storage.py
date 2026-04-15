"""Tests for ``ai_trade.backtest.data.tiingo_storage``.

TiingoStorage is the persistent layer that survives Tiingo subscription
cancellation. Layout under ``root/``:

    prices/{ticker}.parquet     # OHLCV daily, canonical 6-column shape
    meta/{ticker}.json          # optional metadata (sector, exchange, ...)
    manifest.json               # {ticker → {first_date, last_date, n_bars,
                                #            asset_class, fetched_at}}

All tests are offline (no network); they exercise the parquet+manifest
layer directly with synthetic DataFrames.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _mk_df(start: str = "2023-01-02", n: int = 10) -> pd.DataFrame:
    """Build a canonical 6-col OHLCV frame."""
    idx = pd.date_range(start, periods=n, freq="B", name="date")
    rng = np.random.default_rng(seed=42)
    base = 100.0 + rng.normal(scale=0.5, size=n).cumsum()
    return pd.DataFrame(
        {
            "open": base,
            "high": base + 0.5,
            "low": base - 0.5,
            "close": base + 0.1,
            "adj_close": base + 0.1,
            "volume": rng.integers(1_000_000, 5_000_000, size=n).astype(float),
        },
        index=idx,
    )


# ---------------------------------------------------------------------------
# Layout + initialization
# ---------------------------------------------------------------------------


class TestLayout:
    def test_init_creates_subdirs(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path / "tiingo")
        assert (tmp_path / "tiingo" / "prices").is_dir()
        assert (tmp_path / "tiingo" / "meta").is_dir()
        # manifest does not exist until first write
        assert storage.manifest == {}


# ---------------------------------------------------------------------------
# Read / write round-trip
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_write_then_read_returns_same_frame(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        df = _mk_df(start="2023-01-02", n=5)

        storage.write("KR", df, asset_class="equity")

        read = storage.read("KR")
        # check_freq=False — parquet round-trip drops DatetimeIndex.freq;
        # we don't depend on the freq attribute downstream.
        pd.testing.assert_frame_equal(
            read.sort_index(), df.sort_index(), check_freq=False,
        )

    def test_write_creates_parquet_file(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(), asset_class="equity")

        assert (tmp_path / "prices" / "KR.parquet").exists()

    def test_manifest_records_metadata(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        df = _mk_df(start="2020-06-01", n=20)
        storage.write("ANDV", df, asset_class="equity")

        entry = storage.manifest["ANDV"]
        assert entry["first_date"] == df.index.min().date().isoformat()
        assert entry["last_date"] == df.index.max().date().isoformat()
        assert entry["n_bars"] == 20
        assert entry["asset_class"] == "equity"
        assert "fetched_at" in entry  # ISO timestamp

    def test_manifest_persists_to_disk(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(), asset_class="equity")

        # Re-instantiate — manifest should be loaded from disk
        storage2 = TiingoStorage(root=tmp_path)
        assert "KR" in storage2.manifest


# ---------------------------------------------------------------------------
# Range queries
# ---------------------------------------------------------------------------


class TestRangeQuery:
    def test_has_returns_true_when_range_covered(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(start="2023-01-02", n=20), "equity")

        # Range fully inside cached
        assert storage.has("KR", date(2023, 1, 5), date(2023, 1, 20))

    def test_has_returns_false_when_range_extends(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(start="2023-01-02", n=20), "equity")

        # Past the cached end
        assert not storage.has("KR", date(2023, 1, 5), date(2024, 12, 31))

    def test_has_returns_false_for_unknown_ticker(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        assert not storage.has("BOGUS", date(2023, 1, 1), date(2023, 12, 31))

    def test_read_with_date_range_slices(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        df = _mk_df(start="2023-01-02", n=20)
        storage.write("KR", df, "equity")

        sliced = storage.read("KR", start=date(2023, 1, 9), end=date(2023, 1, 13))
        # Slice is by the trading-day index of _mk_df
        assert sliced.index.min().date() >= date(2023, 1, 9)
        assert sliced.index.max().date() <= date(2023, 1, 13)
        assert len(sliced) <= 5

    def test_read_unknown_ticker_raises(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        with pytest.raises(KeyError, match="BOGUS"):
            storage.read("BOGUS")


# ---------------------------------------------------------------------------
# Append / merge semantics
# ---------------------------------------------------------------------------


class TestMerge:
    def test_second_write_extends_existing_range(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        a = _mk_df(start="2023-01-02", n=5)
        b = _mk_df(start="2023-01-09", n=5)  # contiguous next week

        storage.write("KR", a, "equity")
        storage.write("KR", b, "equity")

        merged = storage.read("KR")
        assert len(merged) == 10
        assert merged.index.is_monotonic_increasing
        assert not merged.index.has_duplicates

    def test_overlap_keeps_latest_values(self, tmp_path: Path):
        """If two writes overlap on a date, the second one wins."""
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        a = _mk_df(start="2023-01-02", n=5)
        b = a.copy()
        b["close"] = a["close"] + 99.0  # easy to detect

        storage.write("KR", a, "equity")
        storage.write("KR", b, "equity")

        merged = storage.read("KR")
        # All values should reflect the second write (b)
        assert (merged["close"].values == b["close"].values).all()
        assert len(merged) == 5  # no row duplication


# ---------------------------------------------------------------------------
# Listing / asset-class filter
# ---------------------------------------------------------------------------


class TestListing:
    def test_list_tickers_returns_all(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(), "equity")
        storage.write("SPY", _mk_df(), "equity")
        storage.write("BTCUSD", _mk_df(), "crypto")

        assert set(storage.list_tickers()) == {"KR", "SPY", "BTCUSD"}

    def test_list_tickers_filters_by_asset_class(self, tmp_path: Path):
        from ai_trade.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(), "equity")
        storage.write("BTCUSD", _mk_df(), "crypto")

        assert set(storage.list_tickers(asset_class="equity")) == {"KR"}
        assert set(storage.list_tickers(asset_class="crypto")) == {"BTCUSD"}
