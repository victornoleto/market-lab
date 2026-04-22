"""Tests for ``backtest.data.br_tickers``: IBrX-100 list + B3 calendar + universe."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.data.br_tickers import (
    IBRX100_TICKERS,
    SECTOR_MAP,
    UniverseConfig,
    b3_calendar,
    get_universe_on,
    sector_of,
)


# ---------------------------------------------------------------------------
# Static config tests
# ---------------------------------------------------------------------------
class TestIBrXTickers:
    def test_size_roughly_one_hundred(self):
        """IBrX-100 composition has 95-105 tickers depending on quadrimestre."""
        assert 95 <= len(IBRX100_TICKERS) <= 105, (
            f"Expected ~100 tickers, got {len(IBRX100_TICKERS)}"
        )

    def test_all_have_sa_suffix(self):
        """yfinance convention for B3 stocks is ``.SA`` suffix."""
        assert all(t.endswith(".SA") for t in IBRX100_TICKERS)

    def test_no_duplicates(self):
        assert len(set(IBRX100_TICKERS)) == len(IBRX100_TICKERS)

    def test_top_five_include_known_blue_chips(self):
        """PETR4, VALE3, ITUB4 are canonical B3 top-liquidity names."""
        top_five = set(IBRX100_TICKERS[:5])
        assert "PETR4.SA" in top_five
        assert "VALE3.SA" in top_five
        assert "ITUB4.SA" in top_five


class TestSectorMap:
    def test_known_sectors(self):
        assert sector_of("PETR4.SA") == "Energy"
        assert sector_of("VALE3.SA") == "Materials"
        assert sector_of("ITUB4.SA") == "Financials"
        assert sector_of("WEGE3.SA") == "Industrials"
        assert sector_of("ABEV3.SA") == "Consumer Staples"

    def test_unknown_returns_default(self):
        assert sector_of("XYZ99.SA") == "Unknown"

    def test_most_ibrx_mapped(self):
        """Sanity: ≥ 90% of IBrX-100 tickers should have a sector mapping."""
        mapped = [t for t in IBRX100_TICKERS if t in SECTOR_MAP]
        assert len(mapped) / len(IBRX100_TICKERS) >= 0.90


# ---------------------------------------------------------------------------
# B3 calendar tests
# ---------------------------------------------------------------------------
class TestB3Calendar:
    def test_excludes_carnaval_2024(self):
        """Carnaval Monday/Tuesday 2024 = 2024-02-12/13, no B3 trading."""
        cal = b3_calendar(date(2024, 2, 1), date(2024, 2, 29))
        dates = [ts.date() for ts in cal]
        assert date(2024, 2, 12) not in dates
        assert date(2024, 2, 13) not in dates
        # Regular weekday before Carnaval should be present
        assert date(2024, 2, 9) in dates  # Friday

    def test_excludes_corpus_christi_2024(self):
        """Corpus Christi 2024 = 2024-05-30 (Thursday), no B3 trading."""
        cal = b3_calendar(date(2024, 5, 27), date(2024, 6, 3))
        dates = [ts.date() for ts in cal]
        assert date(2024, 5, 30) not in dates

    def test_excludes_good_friday(self):
        """Good Friday 2024 = 2024-03-29."""
        cal = b3_calendar(date(2024, 3, 25), date(2024, 4, 1))
        dates = [ts.date() for ts in cal]
        assert date(2024, 3, 29) not in dates

    def test_excludes_christmas_eve_post_2020(self):
        """From 2020 onwards B3 is fully closed Dec 24 and Dec 31."""
        cal = b3_calendar(date(2024, 12, 20), date(2024, 12, 31))
        dates = [ts.date() for ts in cal]
        assert date(2024, 12, 24) not in dates
        assert date(2024, 12, 31) not in dates

    def test_weekends_excluded(self):
        cal = b3_calendar(date(2024, 4, 6), date(2024, 4, 7))  # Sat + Sun
        assert len(cal) == 0

    def test_empty_range_returns_empty(self):
        cal = b3_calendar(date(2024, 5, 2), date(2024, 5, 1))
        assert len(cal) == 0

    def test_sp_state_holiday_july_9(self):
        """São Paulo state holiday (Revolução Constitucionalista) excluded."""
        cal = b3_calendar(date(2024, 7, 8), date(2024, 7, 10))
        dates = [ts.date() for ts in cal]
        assert date(2024, 7, 9) not in dates


# ---------------------------------------------------------------------------
# Dynamic universe tests
# ---------------------------------------------------------------------------
def _synthetic_ohlcv(
    start: str, end: str, close: float, volume: float, n_days: int = 80
) -> pd.DataFrame:
    """Minimal OHLCV frame with constant close + volume."""
    idx = pd.bdate_range(start=start, end=end)[:n_days]
    df = pd.DataFrame(
        {
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "adj_close": close,
            "volume": volume,
        },
        index=idx,
    )
    df.index.name = "date"
    return df


class TestGetUniverseOn:
    def test_filters_low_volume(self):
        """Ticker with median notional < threshold is dropped."""
        ohlcv = {
            "LIQUID.SA": _synthetic_ohlcv("2024-01-01", "2024-04-30", close=50.0, volume=500_000),
            "ILLIQUID.SA": _synthetic_ohlcv("2024-01-01", "2024-04-30", close=10.0, volume=1_000),
        }
        config = UniverseConfig(lookback_days=60, min_median_notional_brl=1_000_000.0, n_top=100)
        universe = get_universe_on(date(2024, 4, 30), ohlcv, config)
        assert "LIQUID.SA" in universe  # 50 × 500k = R$25M/day
        assert "ILLIQUID.SA" not in universe  # 10 × 1k = R$10k/day

    def test_ranks_by_median_notional_descending(self):
        ohlcv = {
            "MEDIUM.SA": _synthetic_ohlcv("2024-01-01", "2024-04-30", close=20.0, volume=1_000_000),
            "HIGH.SA": _synthetic_ohlcv("2024-01-01", "2024-04-30", close=50.0, volume=1_000_000),
        }
        universe = get_universe_on(
            date(2024, 4, 30), ohlcv,
            UniverseConfig(min_median_notional_brl=1_000_000.0),
        )
        assert universe == ["HIGH.SA", "MEDIUM.SA"]

    def test_respects_n_top_cap(self):
        ohlcv = {
            f"T{i:03d}.SA": _synthetic_ohlcv("2024-01-01", "2024-04-30", close=50.0, volume=1_000_000)
            for i in range(20)
        }
        universe = get_universe_on(
            date(2024, 4, 30), ohlcv,
            UniverseConfig(n_top=5, min_median_notional_brl=1_000_000.0),
        )
        assert len(universe) == 5

    def test_insufficient_data_ticker_skipped(self):
        """Ticker with < lookback/4 bars in window is dropped."""
        ohlcv = {
            "NEW.SA": _synthetic_ohlcv(
                "2024-04-28", "2024-04-30", close=50.0, volume=1_000_000, n_days=3
            ),
            "OLD.SA": _synthetic_ohlcv(
                "2024-01-01", "2024-04-30", close=50.0, volume=1_000_000
            ),
        }
        universe = get_universe_on(
            date(2024, 4, 30), ohlcv,
            UniverseConfig(lookback_days=60, min_median_notional_brl=1_000_000.0),
        )
        assert "NEW.SA" not in universe
        assert "OLD.SA" in universe

    def test_empty_ohlcv_returns_empty(self):
        assert get_universe_on(date(2024, 4, 30), {}) == []

    def test_missing_columns_skipped(self):
        """Frame without 'close' or 'volume' is silently dropped."""
        idx = pd.bdate_range("2024-01-01", "2024-04-30")
        bad = pd.DataFrame({"price": np.arange(len(idx), dtype=float)}, index=idx)
        good = _synthetic_ohlcv("2024-01-01", "2024-04-30", close=50.0, volume=1_000_000)
        universe = get_universe_on(
            date(2024, 4, 30),
            {"BAD.SA": bad, "GOOD.SA": good},
            UniverseConfig(min_median_notional_brl=1_000_000.0),
        )
        assert universe == ["GOOD.SA"]


# ---------------------------------------------------------------------------
# Module import sanity
# ---------------------------------------------------------------------------
def test_data_subpackage_reexports():
    """Re-exports in ``backtest.data.__init__`` should match module exports."""
    from ai_trade.backtest import data as data_pkg

    assert data_pkg.IBRX100_TICKERS == IBRX100_TICKERS
    assert data_pkg.sector_of("PETR4.SA") == "Energy"
    assert callable(data_pkg.b3_calendar)
    assert callable(data_pkg.get_universe_on)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
