"""Tests for studies/letf_rotation_hunt/data_loader.py.

Coverage
--------
* test_load_testfolio_series_known_ticker — SPYSIM always in cache
* test_load_ffr_series — CASHX daily returns in expected range
* test_load_tiingo_real_etf — UPRO (skip if not in Tiingo cache)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from studies.letf_rotation_hunt.data_loader import (
    load_ffr_daily,
    load_testfolio_series,
    load_tiingo_real_etf,
)

_TIINGO_DIR = Path("data/tiingo/daily/prices")


class TestLoadTestfolioSeries:
    """load_testfolio_series: SPYSIM smoke test."""

    def test_load_testfolio_series_known_ticker(self) -> None:
        """SPYSIM must be in the committed testfolio cache.

        The wide parquet frame includes all tickers on a shared index, so
        tickers with a later inception date (SPYSIM starts 1986-01-02) will
        have NaN rows before that date. Checks are applied after dropna().

        Verifies:
        - returns pd.Series
        - at least 100 non-null observations (1986-present is ~10 000 bars)
        - DatetimeIndex, monotonically increasing
        - all non-null values > 0 (equity curve, never negative)
        """
        series = load_testfolio_series("SPYSIM")
        assert isinstance(series, pd.Series), "expected pd.Series"
        non_null = series.dropna()
        assert len(non_null) >= 100, f"expected ≥100 non-null obs, got {len(non_null)}"
        assert isinstance(series.index, pd.DatetimeIndex), "expected DatetimeIndex"
        assert series.index.is_monotonic_increasing, "index must be sorted ascending"
        assert (non_null > 0).all(), "non-null equity curve values must be positive"

    def test_load_testfolio_series_case_insensitive(self) -> None:
        """Ticker lookup must be case-insensitive."""
        s1 = load_testfolio_series("SPYSIM")
        s2 = load_testfolio_series("spysim")
        pd.testing.assert_series_equal(s1, s2)

    def test_load_testfolio_series_unknown_ticker_raises(self) -> None:
        """Unknown ticker must raise KeyError."""
        with pytest.raises(KeyError):
            load_testfolio_series("NONEXISTENT_TICKER_XYZ")


class TestLoadFFRDaily:
    """load_ffr_daily: CASHX daily return range."""

    def test_load_ffr_series(self) -> None:
        """CASHX daily returns must lie in a sensible range.

        FFR is non-negative in normal regimes and < 1 bps/day even at
        peak (5%+ annualised ≈ 0.02%/day). A daily return outside
        (-0.001, 0.01) would indicate a data corruption or wrong series.
        [testfol.io: CASHX = daily-compounded FFR proxy]
        """
        ffr = load_ffr_daily()
        assert isinstance(ffr, pd.Series), "expected pd.Series"
        assert len(ffr) >= 100, f"expected ≥100 obs, got {len(ffr)}"
        assert isinstance(ffr.index, pd.DatetimeIndex), "expected DatetimeIndex"
        # All daily rates must be within reasonable FFR bounds
        assert (ffr > -0.001).all(), "daily FFR rate below -0.001 is suspicious"
        assert (ffr < 0.01).all(), "daily FFR rate above 0.01 is suspicious"

    def test_load_ffr_daily_no_nan(self) -> None:
        """FFR series must have no NaN values after dropna."""
        ffr = load_ffr_daily()
        assert not ffr.isna().any(), "FFR series must not contain NaN"


class TestLoadTiingoRealETF:
    """load_tiingo_real_etf: UPRO post-inception data."""

    def test_load_tiingo_real_etf(self) -> None:
        """UPRO post-inception data from Tiingo bulk cache.

        Skip cleanly if UPRO.parquet is not in the local Tiingo cache
        (CI / fresh checkout without full Tiingo download).

        When available:
        - returns pd.Series with DatetimeIndex
        - inception year ≥ 2009 (UPRO launched 2009-06-25)
        - all values > 0 (adjusted close)
        - at least 100 observations
        """
        upro_path = _TIINGO_DIR / "UPRO.parquet"
        if not upro_path.exists():
            pytest.skip("UPRO.parquet not in Tiingo cache — skipping")

        series = load_tiingo_real_etf("UPRO")
        assert isinstance(series, pd.Series), "expected pd.Series"
        assert isinstance(series.index, pd.DatetimeIndex), "expected DatetimeIndex"
        assert series.index.is_monotonic_increasing, "index must be sorted ascending"
        assert len(series) >= 100, f"expected ≥100 obs, got {len(series)}"
        assert (series > 0).all(), "adjusted close must be positive"
        # UPRO inception was 2009-06-25 [ProShares prospectus]
        assert series.index[0].year >= 2009, (
            f"UPRO inception year must be ≥ 2009, got {series.index[0].year}"
        )

    def test_load_tiingo_real_etf_missing_raises(self) -> None:
        """FileNotFoundError for a ticker not in Tiingo cache."""
        with pytest.raises(FileNotFoundError):
            load_tiingo_real_etf("DEFINITELY_NOT_IN_CACHE_XYZ123")
