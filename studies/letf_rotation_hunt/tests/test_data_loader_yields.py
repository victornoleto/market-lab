"""Tests for data_loader_yields (yields data fetcher).

T5 expansion adds yield data sources (CMT and dividend yield) backing
the Carver carry forecast in signals_carry.

Citations: spec docs/specs/2026-05-08-t5-expansion-design.md §3.2.
"""
from __future__ import annotations

import pandas as pd
import pytest

from studies.letf_rotation_hunt import data_loader_yields as dly


def test_load_cmt_known_tenors_return_series(monkeypatch, tmp_path):
    monkeypatch.setattr(dly, "_CACHE_DIR", tmp_path)
    fake = pd.Series(
        [0.044, 0.045, 0.046],
        index=pd.date_range("2024-01-02", periods=3, freq="D"),
        name="^TNX",
    )
    monkeypatch.setattr(dly, "_yfinance_fetch_yield", lambda ticker: fake)
    s = dly.load_constant_maturity_yield("10y")
    assert isinstance(s, pd.Series)
    assert (s == fake).all()
    # Series name must be the tenor string, not the internal ticker symbol
    assert s.name == "10y"


def test_load_cmt_uses_cache_on_second_call(monkeypatch, tmp_path):
    """Second call must read from parquet and not invoke yfinance again."""
    monkeypatch.setattr(dly, "_CACHE_DIR", tmp_path)
    fake = pd.Series(
        [0.044, 0.045, 0.046],
        index=pd.date_range("2024-01-02", periods=3, freq="D"),
        name="^TNX",
    )
    call_count = {"n": 0}

    def counting_fetch(ticker: str) -> pd.Series:
        call_count["n"] += 1
        if call_count["n"] > 1:
            raise AssertionError("_yfinance_fetch_yield called more than once — cache not used")
        return fake

    monkeypatch.setattr(dly, "_yfinance_fetch_yield", counting_fetch)

    s1 = dly.load_constant_maturity_yield("10y")  # cache-miss: writes parquet
    s2 = dly.load_constant_maturity_yield("10y")  # cache-hit: must NOT call yfinance

    assert call_count["n"] == 1, "yfinance should only be called once (cache-miss path)"
    assert s1.name == s2.name == "10y"
    assert (s1 == s2).all()


def test_load_cmt_unknown_tenor_raises():
    with pytest.raises(ValueError, match="tenor"):
        dly.load_constant_maturity_yield("7y")


def _make_div_fixture():
    dates = pd.date_range("2024-01-01", periods=400, freq="D")
    dividends = pd.Series(0.0, index=dates)
    for d in [dates[60], dates[150], dates[240], dates[330]]:
        dividends[d] = 0.50
    prices = pd.Series(100.0, index=dates)
    return dates, dividends, prices


def test_load_dividend_yield_trailing_12m(monkeypatch, tmp_path):
    monkeypatch.setattr(dly, "_CACHE_DIR", tmp_path)
    _dates, dividends, prices = _make_div_fixture()
    # 4 quarterly dividends of $0.50 each → $2/yr
    monkeypatch.setattr(dly, "_yfinance_fetch_dividends", lambda t: dividends)
    monkeypatch.setattr(dly, "_yfinance_fetch_adj_close", lambda t: prices)
    s = dly.load_dividend_yield("SPY")
    assert isinstance(s, pd.Series)
    # After full year of dividends, trailing 12m sum = $2 / $100 = 0.02
    last_year_yield = s.iloc[-1]
    assert 0.018 < last_year_yield < 0.022, last_year_yield


def test_load_dividend_yield_uses_cache_on_second_call(monkeypatch, tmp_path):
    """Second call must read from parquet and not invoke yfinance again."""
    monkeypatch.setattr(dly, "_CACHE_DIR", tmp_path)
    _dates, dividends, prices = _make_div_fixture()
    call_count = {"n": 0}

    def counting_divs(ticker: str) -> pd.Series:
        call_count["n"] += 1
        if call_count["n"] > 1:
            raise AssertionError("_yfinance_fetch_dividends called more than once — cache not used")
        return dividends

    monkeypatch.setattr(dly, "_yfinance_fetch_dividends", counting_divs)
    monkeypatch.setattr(dly, "_yfinance_fetch_adj_close", lambda t: prices)

    s1 = dly.load_dividend_yield("SPY")  # cache-miss: writes parquet
    s2 = dly.load_dividend_yield("SPY")  # cache-hit: must NOT call yfinance

    assert call_count["n"] == 1, "yfinance should only be called once (cache-miss path)"
    assert s1.name == s2.name == "SPY_divyield"
    assert (s1 == s2).all()


def test_load_dividend_yield_handles_yfinance_timestamp_skew(monkeypatch, tmp_path):
    """Regression: yfinance returns dividend index with 09:30 ET tz-aware
    timestamps and price index with midnight tz-naive timestamps. The loader
    must align both at the date level so the intersection is non-empty.
    """
    monkeypatch.setattr(dly, "_CACHE_DIR", tmp_path)
    # Real-shape: dividend timestamps with 09:30 ET, tz-aware
    div_dates = pd.DatetimeIndex(
        ["2024-01-15 09:30", "2024-04-15 09:30", "2024-07-15 09:30", "2024-10-15 09:30"],
        tz="America/New_York",
    )
    raw_dividends = pd.Series([0.50, 0.50, 0.50, 0.50], index=div_dates)
    # Real-shape: tz-naive midnight prices, daily over the year
    price_dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    raw_prices = pd.Series(100.0, index=price_dates)

    # Bypass _yfinance_fetch_* and mock at the network boundary instead, so the
    # tz_localize/normalize logic inside the helpers is what's under test.
    class _FakeTicker:
        def __init__(self, t): self.t = t
        @property
        def dividends(self): return raw_dividends
        def history(self, period, auto_adjust):
            return pd.DataFrame({"Close": raw_prices})

    import yfinance as yf
    monkeypatch.setattr(yf, "Ticker", _FakeTicker)

    s = dly.load_dividend_yield("FAKE")
    assert isinstance(s, pd.Series)
    assert len(s) > 0, "intersection between dividend and price dates was empty"
    # Last value should reflect ~$2/yr on $100 = ~2%
    last = s.iloc[-1]
    assert 0.018 < last < 0.022, last
