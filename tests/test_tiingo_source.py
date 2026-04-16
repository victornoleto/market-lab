"""Tests for ``ai_trade.backtest.data.tiingo_source``.

TiingoSource is the storage-first fetcher. Behavior:

1. If ``storage.has(ticker, start, end)`` → return slice from storage; no API call.
2. Otherwise → call Tiingo API; ``storage.write(...)``; return slice.
3. Auth: ``Authorization: Token <key>`` from ``TIINGO_API_KEY`` env var.

Mocks the HTTP layer so tests are fast and offline. The smoke test in
``scripts/tiingo_smoke.py`` is the actual network probe.

Schema contract: ``TiingoSource`` returns DataFrames with the same
canonical shape as ``YFinanceSource``: index = tz-naive ``DatetimeIndex``
named ``"date"``, columns = ``[open, high, low, close, adj_close, volume]``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# URL routing + params (whitelist v1: {equity, etf, crypto, forex} × {daily, 1hour})
# ---------------------------------------------------------------------------


class TestUrlRouting:
    """Smoke tests for endpoint dispatch by (asset_class, frequency)."""

    def test_equity_daily_uses_tiingo_daily_endpoint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url
        url = _build_url("SPY", asset_class="equity", frequency="daily")
        assert url == "https://api.tiingo.com/tiingo/daily/SPY/prices"

    def test_equity_1hour_uses_iex_endpoint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url
        url = _build_url("SPY", asset_class="equity", frequency="1hour")
        assert url == "https://api.tiingo.com/iex/SPY/prices"

    def test_crypto_1hour_uses_tiingo_crypto_endpoint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url
        url = _build_url("BTCUSD", asset_class="crypto", frequency="1hour")
        assert url == "https://api.tiingo.com/tiingo/crypto/prices"

    def test_forex_1hour_uses_tiingo_fx_endpoint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url
        url = _build_url("EURUSD", asset_class="forex", frequency="1hour")
        assert url == "https://api.tiingo.com/tiingo/fx/EURUSD/prices"

    def test_rejects_frequency_not_in_whitelist(self):
        from ai_trade.backtest.data.tiingo_source import _build_url
        with pytest.raises(NotImplementedError, match="frequency='5min'"):
            _build_url("SPY", asset_class="equity", frequency="5min")

    def test_rejects_index_1hour_with_etf_hint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url
        with pytest.raises(NotImplementedError, match="ETF proxy"):
            _build_url("SPX", asset_class="index", frequency="1hour")


def test_build_params_adds_resample_freq_for_1hour():
    from ai_trade.backtest.data.tiingo_source import _build_params
    params = _build_params(
        "SPY", date(2024, 1, 1), date(2024, 12, 31),
        asset_class="equity", frequency="1hour",
    )
    assert params["resampleFreq"] == "1hour"
    assert params["startDate"] == "2024-01-01"
    assert params["endDate"] == "2024-12-31"


def test_build_params_crypto_1hour_has_tickers_and_resample():
    from ai_trade.backtest.data.tiingo_source import _build_params
    params = _build_params(
        "BTCUSD", date(2024, 1, 1), date(2024, 12, 31),
        asset_class="crypto", frequency="1hour",
    )
    assert params["tickers"] == "BTCUSD"
    assert params["resampleFreq"] == "1hour"


# Sample Tiingo EOD response — first 2 rows of a real fetch, trimmed.
_TIINGO_SAMPLE = [
    {
        "date": "2023-12-01T00:00:00.000Z",
        "close": 459.1, "high": 460.5, "low": 458.0, "open": 458.5,
        "volume": 1_234_567,
        "adjClose": 459.1, "adjHigh": 460.5, "adjLow": 458.0, "adjOpen": 458.5,
        "adjVolume": 1_234_567,
        "divCash": 0.0, "splitFactor": 1.0,
    },
    {
        "date": "2023-12-04T00:00:00.000Z",
        "close": 461.1, "high": 462.0, "low": 459.5, "open": 460.0,
        "volume": 1_500_000,
        "adjClose": 461.1, "adjHigh": 462.0, "adjLow": 459.5, "adjOpen": 460.0,
        "adjVolume": 1_500_000,
        "divCash": 0.0, "splitFactor": 1.0,
    },
]


@pytest.fixture
def tiingo_env(monkeypatch):
    monkeypatch.setenv("TIINGO_API_KEY", "test-token-deadbeef")


@pytest.fixture
def storage(tmp_path: Path):
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    return TiingoStorage(root=tmp_path)


def _mock_response(payload, status_code: int = 200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = payload
    mock.raise_for_status.return_value = None
    return mock


# ---------------------------------------------------------------------------
# _normalize — pure function, no I/O
# ---------------------------------------------------------------------------


class TestNormalize:
    def test_canonical_columns_and_index(self):
        from ai_trade.backtest.data.tiingo_source import _normalize

        df = _normalize(_TIINGO_SAMPLE)

        assert list(df.columns) == [
            "open", "high", "low", "close", "adj_close", "volume",
        ]
        assert df.index.name == "date"
        assert df.index.tz is None
        assert isinstance(df.index, pd.DatetimeIndex)
        assert len(df) == 2

    def test_values_round_trip_correctly(self):
        from ai_trade.backtest.data.tiingo_source import _normalize

        df = _normalize(_TIINGO_SAMPLE)
        first = df.iloc[0]
        assert first["open"] == 458.5
        assert first["close"] == 459.1
        assert first["adj_close"] == 459.1
        assert first["volume"] == 1_234_567

    def test_empty_payload_returns_empty_frame_with_canonical_columns(self):
        from ai_trade.backtest.data.tiingo_source import _normalize

        df = _normalize([])
        assert df.empty
        assert list(df.columns) == [
            "open", "high", "low", "close", "adj_close", "volume",
        ]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TestAuth:
    def test_fetch_sends_token_in_authorization_header(
        self, tiingo_env, storage, monkeypatch
    ):
        from ai_trade.backtest.data import tiingo_source

        captured: dict = {}

        def fake_get(url, params=None, headers=None, timeout=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["params"] = params
            return _mock_response(_TIINGO_SAMPLE)

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        src = tiingo_source.TiingoSource(storage=storage)
        src.fetch("SPY", date(2023, 12, 1), date(2023, 12, 4))

        assert captured["headers"]["Authorization"] == "Token test-token-deadbeef"
        assert "SPY" in captured["url"]
        assert captured["params"]["startDate"] == "2023-12-01"
        assert captured["params"]["endDate"] == "2023-12-04"

    def test_missing_api_key_raises(self, monkeypatch, storage):
        from ai_trade.backtest.data import tiingo_source

        monkeypatch.delenv("TIINGO_API_KEY", raising=False)
        # Also bypass the .env-file fallback so the test is hermetic.
        monkeypatch.setattr(tiingo_source, "_read_env_file", lambda _name: "")

        with pytest.raises(RuntimeError, match="TIINGO_API_KEY"):
            tiingo_source.TiingoSource(storage=storage).fetch(
                "SPY", date(2023, 12, 1), date(2023, 12, 4),
            )


# ---------------------------------------------------------------------------
# Storage-first behavior
# ---------------------------------------------------------------------------


class TestStorageFirst:
    def test_storage_hit_skips_api(self, tiingo_env, storage, monkeypatch):
        """If storage.has(...) is True, no network call should happen."""
        from ai_trade.backtest.data import tiingo_source

        # Pre-populate storage with the sample range
        df = tiingo_source._normalize(_TIINGO_SAMPLE)
        storage.write("SPY", df, asset_class="equity")

        called = {"n": 0}

        def fake_get(*args, **kwargs):
            called["n"] += 1
            return _mock_response(_TIINGO_SAMPLE)

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        src = tiingo_source.TiingoSource(storage=storage)
        out = src.fetch("SPY", date(2023, 12, 1), date(2023, 12, 4))

        assert called["n"] == 0
        assert len(out) == 2

    def test_storage_miss_calls_api_and_persists(
        self, tiingo_env, storage, monkeypatch
    ):
        from ai_trade.backtest.data import tiingo_source

        called = {"n": 0}

        def fake_get(*args, **kwargs):
            called["n"] += 1
            return _mock_response(_TIINGO_SAMPLE)

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        src = tiingo_source.TiingoSource(storage=storage)
        out = src.fetch("SPY", date(2023, 12, 1), date(2023, 12, 4))

        assert called["n"] == 1
        assert len(out) == 2
        # And it should now be in storage for next time
        assert "SPY" in storage.manifest

    def test_second_fetch_inside_window_is_storage_hit(
        self, tiingo_env, storage, monkeypatch
    ):
        from ai_trade.backtest.data import tiingo_source

        called = {"n": 0}

        def fake_get(*args, **kwargs):
            called["n"] += 1
            return _mock_response(_TIINGO_SAMPLE)

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        src = tiingo_source.TiingoSource(storage=storage)
        src.fetch("SPY", date(2023, 12, 1), date(2023, 12, 4))
        src.fetch("SPY", date(2023, 12, 1), date(2023, 12, 4))

        assert called["n"] == 1, "second call should hit storage"

    def test_empty_response_returns_empty_frame(
        self, tiingo_env, storage, monkeypatch
    ):
        from ai_trade.backtest.data import tiingo_source

        def fake_get(*args, **kwargs):
            return _mock_response([])

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        src = tiingo_source.TiingoSource(storage=storage)
        df = src.fetch("BOGUS", date(2023, 12, 1), date(2023, 12, 4))
        assert df.empty


# ---------------------------------------------------------------------------
# fetch_many
# ---------------------------------------------------------------------------


class TestFetchMany:
    def test_fetch_many_iterates_each_ticker(
        self, tiingo_env, storage, monkeypatch
    ):
        from ai_trade.backtest.data import tiingo_source

        seen = []

        def fake_get(url, params=None, headers=None, timeout=None):
            seen.append(url)
            return _mock_response(_TIINGO_SAMPLE)

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        src = tiingo_source.TiingoSource(storage=storage)
        result = src.fetch_many(
            ["SPY", "KR", "ANDV"], date(2023, 12, 1), date(2023, 12, 4),
        )

        assert set(result.keys()) == {"SPY", "KR", "ANDV"}
        assert len(seen) == 3
        assert all(isinstance(v, pd.DataFrame) for v in result.values())


# ---------------------------------------------------------------------------
# Asset class routing
# ---------------------------------------------------------------------------


class TestAssetClass:
    def test_dotted_equity_ticker_swapped_to_dash_in_url(
        self, tiingo_env, storage, monkeypatch
    ):
        """Yahoo BF.B → Tiingo BF-B in the outbound URL; storage key stays."""
        from ai_trade.backtest.data import tiingo_source

        captured: dict = {}

        def fake_get(url, params=None, headers=None, timeout=None):
            captured["url"] = url
            return _mock_response(_TIINGO_SAMPLE)

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        src = tiingo_source.TiingoSource(storage=storage)
        src.fetch("BF.B", date(2023, 12, 1), date(2023, 12, 4),
                  asset_class="equity")

        assert "/daily/BF-B/prices" in captured["url"]
        # Storage entry still under the original (Yahoo-style) key.
        assert "BF.B" in storage.manifest
        assert "BF-B" not in storage.manifest

    def test_crypto_asset_class_uses_crypto_endpoint(
        self, tiingo_env, storage, monkeypatch
    ):
        from ai_trade.backtest.data import tiingo_source

        captured: dict = {}

        def fake_get(url, params=None, headers=None, timeout=None):
            captured["url"] = url
            return _mock_response([])

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        src = tiingo_source.TiingoSource(storage=storage)
        src.fetch(
            "btcusd", date(2023, 12, 1), date(2023, 12, 4),
            asset_class="crypto",
        )

        assert "/crypto" in captured["url"]

    def test_forex_asset_class_uses_fx_endpoint(
        self, tiingo_env, storage, monkeypatch
    ):
        from ai_trade.backtest.data import tiingo_source

        captured: dict = {}

        def fake_get(url, params=None, headers=None, timeout=None):
            captured["url"] = url
            return _mock_response([])

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        src = tiingo_source.TiingoSource(storage=storage)
        src.fetch(
            "eurusd", date(2023, 12, 1), date(2023, 12, 4),
            asset_class="forex",
        )

        assert "/fx" in captured["url"]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class TestErrors:
    def test_401_unauthorized_raises_clear_error(
        self, tiingo_env, storage, monkeypatch
    ):
        from ai_trade.backtest.data import tiingo_source
        import requests as _r

        def fake_get(*args, **kwargs):
            mock = MagicMock()
            mock.status_code = 401
            mock.text = "Unauthorized"
            mock.raise_for_status.side_effect = _r.HTTPError("401 Unauthorized")
            mock.json.side_effect = ValueError("no json")
            return mock

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        with pytest.raises(_r.HTTPError):
            tiingo_source.TiingoSource(storage=storage).fetch(
                "SPY", date(2023, 12, 1), date(2023, 12, 4),
            )

    def test_404_not_found_returns_empty_frame(
        self, tiingo_env, storage, monkeypatch
    ):
        """Delisted/renamed tickers (Tiingo returns 404) must not crash a
        bulk universe fetch — graceful empty-frame return matches yfinance.
        """
        from ai_trade.backtest.data import tiingo_source

        def fake_get(*args, **kwargs):
            mock = MagicMock()
            mock.status_code = 404
            mock.text = "Not Found"
            # raise_for_status would raise — but the code path checks
            # status_code first and returns early, so this should never fire.
            mock.raise_for_status.side_effect = AssertionError(
                "should not raise on 404"
            )
            return mock

        monkeypatch.setattr(tiingo_source.requests, "get", fake_get)

        df = tiingo_source.TiingoSource(storage=storage).fetch(
            "ESV", date(2023, 1, 1), date(2023, 12, 4),
        )
        assert df.empty
        assert list(df.columns) == [
            "open", "high", "low", "close", "adj_close", "volume",
        ]


# ---------------------------------------------------------------------------
# frequency kwarg + split adjust v1 (spec §3.3)
# ---------------------------------------------------------------------------


def test_fetch_with_frequency_1hour_persists_and_serves_cache(
    tiingo_env, storage, monkeypatch,
):
    """Primeira call faz HTTP; segunda lê do cache."""
    from datetime import date
    import pandas as pd
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod

    # Pré-popular daily cache para permitir split adjust (ratio = 1.0 aqui)
    df_daily = pd.DataFrame(
        {"open": [100.0] * 3, "high": [101.0] * 3, "low": [99.0] * 3,
         "close": [100.0] * 3, "adj_close": [100.0] * 3, "volume": [1000.0] * 3},
        index=pd.DatetimeIndex(
            [pd.Timestamp("2024-01-02"),
             pd.Timestamp("2024-01-03"),
             pd.Timestamp("2024-01-04")],
            name="date",
        ),
    )
    storage.write("SPY", df_daily, asset_class="equity", frequency="daily")

    IEX_SAMPLE = [
        {"date": "2024-01-02T14:00:00.000Z",
         "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.2,
         "volume": 500},
        {"date": "2024-01-02T15:00:00.000Z",
         "open": 100.2, "high": 100.8, "low": 100.0, "close": 100.5,
         "volume": 600},
    ]

    call_count = {"n": 0}

    def fake_get(url, params=None, headers=None, timeout=None):
        call_count["n"] += 1
        return _mock_response(IEX_SAMPLE, 200)

    monkeypatch.setattr(ts_mod.requests, "get", fake_get)

    source = TiingoSource(storage=storage)
    df1 = source.fetch(
        "SPY", date(2024, 1, 2), date(2024, 1, 2),
        asset_class="equity", frequency="1hour",
    )
    assert not df1.empty
    assert call_count["n"] == 1

    df2 = source.fetch(
        "SPY", date(2024, 1, 2), date(2024, 1, 2),
        asset_class="equity", frequency="1hour",
    )
    assert not df2.empty
    assert call_count["n"] == 1  # cache hit, sem HTTP extra


def test_iex_applies_split_adjust_from_daily_cache(
    tiingo_env, storage, monkeypatch,
):
    """close_intraday × (adj_close_daily/close_daily) vira adj_close_intraday."""
    from datetime import date
    import pandas as pd
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod

    df_daily = pd.DataFrame(
        {"open": [100.0], "high": [100.0], "low": [100.0],
         "close": [100.0], "adj_close": [50.0], "volume": [1000.0]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-02")], name="date"),
    )
    storage.write("SPY", df_daily, asset_class="equity", frequency="daily")

    IEX_SAMPLE = [
        {"date": "2024-01-02T14:00:00.000Z",
         "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0,
         "volume": 500},
    ]

    def fake_get(url, params=None, headers=None, timeout=None):
        return _mock_response(IEX_SAMPLE, 200)

    monkeypatch.setattr(ts_mod.requests, "get", fake_get)

    source = TiingoSource(storage=storage)
    df = source.fetch(
        "SPY", date(2024, 1, 2), date(2024, 1, 2),
        asset_class="equity", frequency="1hour",
    )

    # Ratio = 50/100 = 0.5; close_intraday = 100 × 0.5 = 50
    assert abs(df["close"].iloc[0] - 50.0) < 1e-6
    assert abs(df["adj_close"].iloc[0] - 50.0) < 1e-6


def test_iex_raises_notimplemented_if_equity_not_in_daily_cache(
    tiingo_env, storage, monkeypatch,
):
    """equity/etf 1h sem daily cache para o ticker → NotImplementedError."""
    from datetime import date
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod
    import pytest

    IEX_SAMPLE = [
        {"date": "2024-01-02T14:00:00.000Z",
         "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0,
         "volume": 500},
    ]

    def fake_get(url, params=None, headers=None, timeout=None):
        return _mock_response(IEX_SAMPLE, 200)

    monkeypatch.setattr(ts_mod.requests, "get", fake_get)

    source = TiingoSource(storage=storage)
    with pytest.raises(NotImplementedError, match="daily primeiro"):
        source.fetch(
            "NVDA", date(2024, 1, 2), date(2024, 1, 2),
            asset_class="equity", frequency="1hour",
        )


def test_iex_filters_orphan_holiday_bars_with_warning(
    tiingo_env, storage, monkeypatch, caplog,
):
    """Tiingo IEX placeholder bars on US holidays (no daily counterpart)
    must be dropped before split-adjust, with a WARNING.

    Background: Tiingo IEX returns 6 fake hourly bars on US market-closed
    days with volume=0 and OHLC all identical at the RAW (unadjusted)
    price. For tickers with historical splits, these placeholders sit at
    2x+ surrounding adjusted bars and inflate backtest PnL by 90%+.
    Detected 2026-04-16 — see jornada/2026-04-16-13XX-data-bug.md.
    """
    import logging
    from datetime import date
    import pandas as pd
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod

    df_daily = pd.DataFrame(
        {
            "open":  [100.0, 100.0],
            "high":  [100.0, 100.0],
            "low":   [100.0, 100.0],
            "close": [100.0, 100.0],
            "adj_close": [50.0, 50.0],
            "volume": [1000.0, 1000.0],
        },
        index=pd.DatetimeIndex(
            [pd.Timestamp("2024-01-12"), pd.Timestamp("2024-01-16")], name="date",
        ),
    )
    storage.write("XLK", df_daily, asset_class="etf", frequency="daily")

    IEX_SAMPLE = [
        {"date": "2024-01-12T15:00:00.000Z",
         "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0,
         "volume": 500},
        {"date": "2024-01-15T15:00:00.000Z",
         "open": 200.0, "high": 200.0, "low": 200.0, "close": 200.0,
         "volume": 0},
        {"date": "2024-01-16T15:00:00.000Z",
         "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0,
         "volume": 500},
    ]

    monkeypatch.setattr(
        ts_mod.requests, "get",
        lambda *a, **kw: _mock_response(IEX_SAMPLE, 200),
    )

    caplog.set_level(logging.WARNING, logger="ai_trade.backtest.data.tiingo_source")
    source = TiingoSource(storage=storage)
    df = source.fetch(
        "XLK", date(2024, 1, 12), date(2024, 1, 16),
        asset_class="etf", frequency="1hour",
    )

    filter_warnings = [
        r for r in caplog.records
        if r.levelname == "WARNING" and "market-closed-day placeholders" in r.message
    ]
    assert filter_warnings, (
        "expected a placeholder-filtering warning when intraday includes a "
        f"day not in daily cache; got: {[(r.levelname, r.message) for r in caplog.records]}"
    )
    assert "2024-01-15" in filter_warnings[0].message
    assert "XLK" in filter_warnings[0].message

    bar_dates = sorted({ts.date() for ts in df.index})
    assert date(2024, 1, 15) not in bar_dates, "orphan bar must be dropped"
    assert date(2024, 1, 12) in bar_dates and date(2024, 1, 16) in bar_dates

    bar_12 = df.loc[df.index.date == date(2024, 1, 12)]
    bar_16 = df.loc[df.index.date == date(2024, 1, 16)]
    assert abs(bar_12["close"].iloc[0] - 50.0) < 1e-6, "2024-01-12 must be ratio-adjusted"
    assert abs(bar_16["close"].iloc[0] - 50.0) < 1e-6, "2024-01-16 must be ratio-adjusted"


def test_iex_no_filter_warning_when_all_intraday_dates_in_daily(
    tiingo_env, storage, monkeypatch, caplog,
):
    """When intraday calendar dates are fully covered by daily cache,
    no orphan-filtering warning should fire."""
    import logging
    from datetime import date
    import pandas as pd
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod

    df_daily = pd.DataFrame(
        {"open": [100.0, 100.0], "high": [100.0, 100.0], "low": [100.0, 100.0],
         "close": [100.0, 100.0], "adj_close": [100.0, 100.0],
         "volume": [1000.0, 1000.0]},
        index=pd.DatetimeIndex(
            [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")], name="date",
        ),
    )
    storage.write("SPY", df_daily, asset_class="etf", frequency="daily")

    IEX_SAMPLE = [
        {"date": "2024-01-02T14:00:00.000Z",
         "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 500},
        {"date": "2024-01-03T14:00:00.000Z",
         "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 500},
    ]

    monkeypatch.setattr(
        ts_mod.requests, "get",
        lambda *a, **kw: _mock_response(IEX_SAMPLE, 200),
    )

    caplog.set_level(logging.WARNING, logger="ai_trade.backtest.data.tiingo_source")
    source = TiingoSource(storage=storage)
    source.fetch(
        "SPY", date(2024, 1, 2), date(2024, 1, 3),
        asset_class="etf", frequency="1hour",
    )

    filter_warnings = [
        r for r in caplog.records
        if "market-closed-day placeholders" in r.message
    ]
    assert not filter_warnings, (
        f"unexpected filter warning when intraday is fully covered by daily: "
        f"{[r.message for r in filter_warnings]}"
    )


def test_crypto_and_forex_use_close_as_adj_close_no_split(
    tiingo_env, storage, monkeypatch,
):
    """Crypto/forex 1h não tem split — adj_close := close."""
    from datetime import date
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod

    CRYPTO_SAMPLE = [{
        "ticker": "btcusd",
        "priceData": [
            {"date": "2024-01-02T00:00:00.000Z",
             "open": 45000.0, "high": 45100.0, "low": 44900.0,
             "close": 45050.0, "volume": 100.0, "volumeNotional": 4500000.0,
             "tradesDone": 1000},
        ],
    }]

    def fake_get(url, params=None, headers=None, timeout=None):
        return _mock_response(CRYPTO_SAMPLE, 200)

    monkeypatch.setattr(ts_mod.requests, "get", fake_get)

    source = TiingoSource(storage=storage)
    df = source.fetch(
        "BTCUSD", date(2024, 1, 2), date(2024, 1, 2),
        asset_class="crypto", frequency="1hour",
    )
    assert abs(df["close"].iloc[0] - 45050.0) < 1e-6
    assert abs(df["adj_close"].iloc[0] - 45050.0) < 1e-6


def test_iex_payload_normalizes_without_adjclose():
    """IEX payload sem adjClose — _normalize usa close."""
    from ai_trade.backtest.data.tiingo_source import _normalize

    payload = [
        {"date": "2024-01-02T14:00:00.000Z",
         "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.2,
         "volume": 500},
    ]
    df = _normalize(payload)
    assert list(df.columns) == ["open", "high", "low", "close", "adj_close", "volume"]
    assert abs(df["adj_close"].iloc[0] - df["close"].iloc[0]) < 1e-6
