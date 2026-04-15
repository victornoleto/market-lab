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
