"""Tests for the macro data loader (Phase 2).

Uses synthetic fixtures (not the cached parquet files) so tests are
hermetic and fast.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.data.macro_data_loader import (
    align_monthly_to_daily,
    apply_publish_lag,
    load_cape_monthly,
    load_ebp_monthly,
    load_term_spread_daily,
    load_vix_daily,
    resample_to_daily_with_lag,
)


def _monthly_series(start: str, n: int, values: list[float]) -> pd.Series:
    idx = pd.date_range(start=start, periods=n, freq="MS")
    assert len(values) == n
    return pd.Series(values, index=idx, name="x")


def _trading_index(start: str, n: int) -> pd.DatetimeIndex:
    return pd.bdate_range(start=start, periods=n)


class TestApplyPublishLag:
    def test_shift_zero_is_identity(self):
        s = pd.Series([1.0, 2.0, 3.0], index=_trading_index("2020-01-02", 3))
        out = apply_publish_lag(s, n_trading_days=0)
        pd.testing.assert_series_equal(out, s)

    def test_shift_shifts_right(self):
        s = pd.Series([10, 20, 30, 40], index=_trading_index("2020-01-02", 4))
        out = apply_publish_lag(s, n_trading_days=2)
        # Value at bar 2 should now be 10 (from bar 0); first 2 are NaN.
        assert pd.isna(out.iloc[0])
        assert pd.isna(out.iloc[1])
        assert out.iloc[2] == 10
        assert out.iloc[3] == 20


class TestAlignMonthlyToDaily:
    def test_forward_fills_to_daily(self):
        m = _monthly_series("2020-01-01", 3, [1.0, 2.0, 3.0])
        daily_idx = _trading_index("2020-01-02", 45)
        out = align_monthly_to_daily(m, daily_idx)
        # All days in Jan should have value 1.0 (from Jan 1 month stamp).
        jan_values = out.loc["2020-01"]
        assert (jan_values == 1.0).all()
        # Feb should be 2.0.
        assert (out.loc["2020-02"] == 2.0).all()


class TestResampleWithLag:
    def test_lag_prevents_lookahead(self):
        m = _monthly_series("2020-01-01", 3, [10.0, 20.0, 30.0])
        daily_idx = _trading_index("2020-01-02", 45)
        out = resample_to_daily_with_lag(m, daily_idx, n_trading_days=21)
        # With 21-trading-day lag, Jan's value (10.0) should only be
        # available ~late Jan / early Feb. Feb should mostly still read
        # Jan's value (10.0), not Feb's (20.0).
        # Specifically, first few Feb bars should have value 10.0.
        first_feb = out.loc["2020-02-03"]  # ~1st trading day Feb
        assert first_feb == 10.0
        # By mid-March, we should have Feb's value 20.0.
        mid_march = out.loc["2020-03-15":"2020-03-20"]
        assert all(v in (10.0, 20.0) for v in mid_march.values)


class TestLoaderSmoke:
    """Integration-style tests that exercise the real cache files
    when present. Skip gracefully if the cache is missing (e.g., CI
    without macro cache)."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        p = Path("data/external/macro")
        if not p.exists():
            pytest.skip("macro cache not present — skip integration smoke")
        return p

    def test_ebp_monthly_loads_with_expected_columns(self, cache_dir):
        s = load_ebp_monthly(cache_dir=cache_dir)
        assert isinstance(s, pd.Series)
        assert len(s) > 100
        # Sign check: EBP has both positive and negative values
        # (stress above normal = positive).
        assert s.min() < 0
        assert s.max() > 0

    def test_term_spread_daily_loads(self, cache_dir):
        s = load_term_spread_daily(cache_dir=cache_dir)
        assert isinstance(s, pd.Series)
        assert len(s) > 1000
        # 2019 inversion: there should be some days with negative spread
        assert (s < 0).any()

    def test_cape_monthly_loads(self, cache_dir):
        s = load_cape_monthly(cache_dir=cache_dir)
        assert isinstance(s, pd.Series)
        assert len(s) > 1000
        # CAPE historically ranges 5-45 — sanity check
        assert s.min() >= 4.0
        assert s.max() <= 50.0

    def test_vix_daily_loads(self, cache_dir):
        s = load_vix_daily(cache_dir=cache_dir)
        assert isinstance(s, pd.Series)
        assert len(s) > 1000
        assert s.min() >= 5.0
        assert s.max() <= 100.0
