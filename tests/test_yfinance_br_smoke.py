"""Smoke test: yfinance ``.SA`` tickers return canonical OHLCV.

Network-dependent. Skipped by default; opt-in via ``AI_TRADE_RUN_NETWORK_TESTS=1``
environment variable. Run locally:

    AI_TRADE_RUN_NETWORK_TESTS=1 .venv/bin/python -m pytest tests/test_yfinance_br_smoke.py -v

Goal: verify the existing ``YFinanceSource`` works unchanged for Brazilian
tickers (``PETR4.SA``, ``VALE3.SA``, ``ITUB4.SA``) — no source changes are
needed for Strategy D OHLCV, the suffix alone routes to B3 data on Yahoo.

A documented limitation (also present for US tickers): yfinance does not
return delisted tickers. For Strategy D this is mitigated by limiting the
universe to the ``IBRX100_TICKERS`` list (current-member proxy).
"""

from __future__ import annotations

import os
import tempfile
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from market_lab.backtest.data.yfinance_source import YFinanceSource


_SKIP_NETWORK = os.getenv("AI_TRADE_RUN_NETWORK_TESTS") != "1"
_SKIP_REASON = (
    "Network smoke test; set AI_TRADE_RUN_NETWORK_TESTS=1 to run locally."
)


@pytest.fixture
def isolated_cache(tmp_path: Path) -> YFinanceSource:
    return YFinanceSource(cache_dir=tmp_path / "yf")


# ---------------------------------------------------------------------------
# Smoke tests (network, opt-in)
# ---------------------------------------------------------------------------
@pytest.mark.skipif(_SKIP_NETWORK, reason=_SKIP_REASON)
class TestYFinanceBRSmoke:
    """Fetch real data from Yahoo for three canonical B3 large caps."""

    @pytest.mark.parametrize("ticker", ["PETR4.SA", "VALE3.SA", "ITUB4.SA"])
    def test_canonical_schema(self, ticker: str, isolated_cache: YFinanceSource):
        df = isolated_cache.fetch(ticker, date(2022, 1, 1), date(2023, 12, 31))
        assert not df.empty, f"{ticker}: empty DataFrame from yfinance"
        assert list(df.columns) == [
            "open", "high", "low", "close", "adj_close", "volume",
        ], f"{ticker}: unexpected columns {list(df.columns)}"
        assert df.index.name == "date"
        assert df.index.tz is None, f"{ticker}: index should be tz-naive"
        # BR trading calendar: ~250 days/yr × 2 yrs ≈ 500 bars minimum
        assert len(df) >= 400, f"{ticker}: only {len(df)} bars; < 400"

    def test_prices_are_positive(self, isolated_cache: YFinanceSource):
        df = isolated_cache.fetch("PETR4.SA", date(2022, 1, 1), date(2023, 12, 31))
        assert (df["close"] > 0).all()
        assert (df["high"] >= df["low"]).all()
        assert (df["volume"] >= 0).all()

    def test_cache_prevents_second_network_call(
        self, isolated_cache: YFinanceSource, monkeypatch
    ):
        """Second fetch strictly inside the cached window must skip the network.

        YFinanceSource uses a conservative cache-hit rule: ``c_start <= start
        AND c_end >= end`` (see ``yfinance_source.py``). Because yfinance
        trims to trading days, a request for ``2023-01-01..2023-12-31`` stores
        ``c_start=2023-01-02, c_end=2023-12-29``. Asking for the same
        calendar bounds again fails the rule (``2023-01-02 <= 2023-01-01`` is
        False) and triggers a re-download — that's the source being honest
        about coverage, not a bug. So the test asks for a strictly-inside
        window on the second call.
        """
        df1 = isolated_cache.fetch("ITUB4.SA", date(2023, 1, 1), date(2023, 12, 31))
        assert not df1.empty

        import yfinance as yf

        def _explode(*args, **kwargs):
            raise AssertionError("yf.download called on cached fetch")

        monkeypatch.setattr(yf, "download", _explode)
        df2 = isolated_cache.fetch("ITUB4.SA", date(2023, 2, 1), date(2023, 11, 30))
        assert not df2.empty
        # df2 is a slice of df1's window — should contain only rows in range
        assert df2.index.min() >= pd.Timestamp(2023, 2, 1)
        assert df2.index.max() <= pd.Timestamp(2023, 11, 30)


# ---------------------------------------------------------------------------
# Integration with br_tickers (offline — uses mock OHLCV)
# ---------------------------------------------------------------------------
def test_ibrx100_tickers_suffix_matches_yfinance_convention():
    """Sanity: every IBRX100_TICKERS entry ends with .SA, which yfinance
    dispatches to B3 (no code change in YFinanceSource needed).
    """
    from market_lab.backtest.data.br_tickers import IBRX100_TICKERS

    assert all(t.endswith(".SA") for t in IBRX100_TICKERS)
    assert all("/" not in t for t in IBRX100_TICKERS)  # cache path safety


def test_yfinance_source_cache_path_handles_sa_suffix(tmp_path: Path):
    """Cache filename uses ``<TICKER>.parquet`` — ``.SA`` is part of the
    filename so ``PETR4.SA.parquet`` sits alongside US caches without
    collision. Verify no sanitization drops the suffix.
    """
    source = YFinanceSource(cache_dir=tmp_path)
    path = source._cache_path("PETR4.SA")
    assert path.name == "PETR4.SA.parquet"
    assert path.parent == tmp_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
