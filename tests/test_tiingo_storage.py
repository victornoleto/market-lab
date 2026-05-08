"""Tests for ``market_lab.backtest.data.tiingo_storage``.

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
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path / "tiingo")
        # Nested layout: root/{frequency}/{prices,meta}/. `daily` is created
        # eagerly on init; other freqs get their subdirs on first write.
        assert (tmp_path / "tiingo" / "daily" / "prices").is_dir()
        assert (tmp_path / "tiingo" / "daily" / "meta").is_dir()
        # manifest does not exist until first write
        assert storage.manifest == {}


# ---------------------------------------------------------------------------
# Read / write round-trip
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_write_then_read_returns_same_frame(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

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
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(), asset_class="equity")

        # New layout: root/{frequency}/prices/{ticker}.parquet
        assert (tmp_path / "daily" / "prices" / "KR.parquet").exists()

    def test_manifest_records_metadata(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        df = _mk_df(start="2020-06-01", n=20)
        storage.write("ANDV", df, asset_class="equity")

        # Nested manifest: {ticker: {frequency: entry}}; entry has
        # first_dt/last_dt as ISO datetime strings (not first_date).
        entry = storage.manifest["ANDV"]["daily"]
        assert entry["first_dt"].startswith(df.index.min().date().isoformat())
        assert entry["last_dt"].startswith(df.index.max().date().isoformat())
        assert entry["n_bars"] == 20
        assert entry["asset_class"] == "equity"
        assert "fetched_at" in entry  # ISO timestamp

    def test_manifest_persists_to_disk(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

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
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(start="2023-01-02", n=20), "equity")

        # Range fully inside cached
        assert storage.has("KR", date(2023, 1, 5), date(2023, 1, 20))

    def test_has_returns_false_when_range_extends(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(start="2023-01-02", n=20), "equity")

        # Past the cached end
        assert not storage.has("KR", date(2023, 1, 5), date(2024, 12, 31))

    def test_has_returns_false_for_unknown_ticker(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        assert not storage.has("BOGUS", date(2023, 1, 1), date(2023, 12, 31))

    def test_has_tolerates_weekend_holiday_slack(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        # Data begins 2014-01-02 (first trading day; 2014-01-01 is New Year).
        # 20 business days → last = 2014-01-29.
        storage.write("AAPL", _mk_df(start="2014-01-02", n=20), "equity")

        # Request [2014-01-01, 2014-01-30] — both edges fall on non-trading
        # days but are within the 7-day slack → should be covered.
        assert storage.has("AAPL", date(2014, 1, 1), date(2014, 1, 30))
        # Beyond the 7-day slack — must still miss.
        assert not storage.has("AAPL", date(2014, 1, 1), date(2014, 2, 10))

    def test_read_with_date_range_slices(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        df = _mk_df(start="2023-01-02", n=20)
        storage.write("KR", df, "equity")

        sliced = storage.read("KR", start=date(2023, 1, 9), end=date(2023, 1, 13))
        # Slice is by the trading-day index of _mk_df
        assert sliced.index.min().date() >= date(2023, 1, 9)
        assert sliced.index.max().date() <= date(2023, 1, 13)
        assert len(sliced) <= 5

    def test_read_unknown_ticker_raises(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        with pytest.raises(KeyError, match="BOGUS"):
            storage.read("BOGUS")


# ---------------------------------------------------------------------------
# Append / merge semantics
# ---------------------------------------------------------------------------


class TestMerge:
    def test_second_write_extends_existing_range(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

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
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

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
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(), "equity")
        storage.write("SPY", _mk_df(), "equity")
        storage.write("BTCUSD", _mk_df(), "crypto")

        assert set(storage.list_tickers()) == {"KR", "SPY", "BTCUSD"}

    def test_list_tickers_filters_by_asset_class(self, tmp_path: Path):
        from market_lab.backtest.data.tiingo_storage import TiingoStorage

        storage = TiingoStorage(root=tmp_path)
        storage.write("KR", _mk_df(), "equity")
        storage.write("BTCUSD", _mk_df(), "crypto")

        assert set(storage.list_tickers(asset_class="equity")) == {"KR"}
        assert set(storage.list_tickers(asset_class="crypto")) == {"BTCUSD"}


# ---------------------------------------------------------------------------
# Nested manifest schema (freq-aware) — tiingo_service lazy cache refactor
# ---------------------------------------------------------------------------


def test_manifest_nested_schema_roundtrip(tmp_path: Path):
    """Manifest grava e carrega formato nested {ticker: {freq: entry}}."""
    from market_lab.backtest.data.tiingo_storage import TiingoStorage

    storage = TiingoStorage(root=tmp_path)
    df = pd.DataFrame(
        {
            "open": [1.0], "high": [2.0], "low": [0.5],
            "close": [1.5], "adj_close": [1.5], "volume": [100.0],
        },
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-02T09:30")], name="date"),
    )

    storage.write("AAPL", df, asset_class="equity", frequency="1hour")

    # Manifest nested
    assert "AAPL" in storage.manifest
    assert "1hour" in storage.manifest["AAPL"]
    entry = storage.manifest["AAPL"]["1hour"]
    assert entry["first_dt"].startswith("2024-01-02")
    assert entry["last_dt"].startswith("2024-01-02")
    assert entry["n_bars"] == 1
    assert entry["asset_class"] == "equity"
    assert "requested_start" in entry
    assert "requested_end" in entry

    # Round-trip via nova instância
    storage2 = TiingoStorage(root=tmp_path)
    assert storage2.manifest == storage.manifest


def test_has_with_frequency_kwarg(tmp_path: Path):
    """has() respeita frequency isolado (AAPL daily ≠ AAPL 1hour)."""
    from market_lab.backtest.data.tiingo_storage import TiingoStorage

    storage = TiingoStorage(root=tmp_path)
    df_daily = pd.DataFrame(
        {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
         "adj_close": [1.0], "volume": [100.0]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-02")], name="date"),
    )
    storage.write("AAPL", df_daily, asset_class="equity", frequency="daily")

    # AAPL daily existe, 1hour não
    assert storage.has("AAPL", date(2024, 1, 2), date(2024, 1, 2), frequency="daily")
    assert not storage.has("AAPL", date(2024, 1, 2), date(2024, 1, 2), frequency="1hour")


def test_has_accepts_date_or_datetime(tmp_path: Path):
    """has() aceita date e datetime sem crash."""
    from datetime import datetime

    from market_lab.backtest.data.tiingo_storage import TiingoStorage

    storage = TiingoStorage(root=tmp_path)
    df = pd.DataFrame(
        {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
         "adj_close": [1.0], "volume": [100.0]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-02T14:00")], name="date"),
    )
    storage.write("SPY", df, asset_class="equity", frequency="1hour")

    assert storage.has("SPY", date(2024, 1, 2), date(2024, 1, 2), frequency="1hour")
    assert storage.has(
        "SPY",
        datetime(2024, 1, 2, 10, 0),
        datetime(2024, 1, 2, 20, 0),
        frequency="1hour",
    )


def test_slack_per_asset_class_and_freq(tmp_path: Path):
    """Crypto 1h slack é menor que equity 1h (24/7 vs RTH)."""
    from datetime import datetime

    from market_lab.backtest.data.tiingo_storage import TiingoStorage

    storage = TiingoStorage(root=tmp_path)

    # Equity 1h — slack 12h
    df = pd.DataFrame(
        {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
         "adj_close": [1.0], "volume": [100.0]},
        index=pd.DatetimeIndex(
            [pd.Timestamp("2024-01-02T14:00")], name="date",
        ),
    )
    storage.write("SPY", df, asset_class="equity", frequency="1hour")

    # Request 10h antes de first_dt: slack 12h permite
    assert storage.has(
        "SPY",
        datetime(2024, 1, 2, 4, 0),  # 10h antes → slack 12h permite
        datetime(2024, 1, 2, 14, 0),
        frequency="1hour",
    )
    # 24h+ antes de first_dt → slack 12h NÃO cobre (2024-01-01 00:00 é 38h antes)
    assert not storage.has(
        "SPY",
        datetime(2024, 1, 1, 0, 0),
        datetime(2024, 1, 2, 14, 0),
        frequency="1hour",
    )

    # Crypto 1h — slack 6h (mais apertado)
    storage.write(
        "BTCUSD",
        pd.DataFrame(
            {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
             "adj_close": [1.0], "volume": [100.0]},
            index=pd.DatetimeIndex([pd.Timestamp("2024-01-02T14:00")], name="date"),
        ),
        asset_class="crypto",
        frequency="1hour",
    )
    # 10h antes — slack 6h NÃO permite
    assert not storage.has(
        "BTCUSD",
        datetime(2024, 1, 2, 4, 0),
        datetime(2024, 1, 2, 14, 0),
        frequency="1hour",
    )
    # 4h antes — slack 6h permite
    assert storage.has(
        "BTCUSD",
        datetime(2024, 1, 2, 10, 0),
        datetime(2024, 1, 2, 14, 0),
        frequency="1hour",
    )


def test_init_raises_on_lockfile_present(tmp_path: Path):
    """TiingoStorage(__post_init__) raise se lockfile .migration.lock existe."""
    from market_lab.backtest.data.tiingo_storage import TiingoStorage

    (tmp_path / ".migration.lock").write_text("in-progress\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="migração incompleta"):
        TiingoStorage(root=tmp_path)


def test_write_stores_requested_range_when_provided(tmp_path: Path):
    """write() aceita requested_start/end e grava no manifest."""
    from datetime import datetime

    from market_lab.backtest.data.tiingo_storage import TiingoStorage

    storage = TiingoStorage(root=tmp_path)
    df = pd.DataFrame(
        {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
         "adj_close": [1.0], "volume": [100.0]},
        index=pd.DatetimeIndex(
            [pd.Timestamp("2024-04-15T14:00")], name="date"
        ),
    )
    storage.write(
        "SPY", df,
        asset_class="equity",
        frequency="1hour",
        requested_start=datetime(2020, 1, 1),
        requested_end=datetime(2024, 4, 15),
    )

    entry = storage.manifest["SPY"]["1hour"]
    assert entry["requested_start"].startswith("2020-01-01")
    assert entry["requested_end"].startswith("2024-04-15")
    # first_dt/last_dt refletem o que veio (o returned range)
    assert entry["first_dt"].startswith("2024-04-15")
    assert entry["last_dt"].startswith("2024-04-15")
