"""Tests for ai_trade.backtest.data.spx_tr_loader."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.data.spx_tr_loader import (
    DEFAULT_TIINGO_CUTOFF,
    compute_market_total_return,
    fetch_ken_french_daily,
    load_spx_tr_daily,
    parse_ken_french_csv,
)


_SAMPLE_KF_CSV = """\
This file was created by using the 202602 CRSP database.
Some other header garbage line.

,Mkt-RF,SMB,HML,RF
19260701,    0.09,   -0.25,   -0.27,    0.01
19260702,    0.45,   -0.33,   -0.06,    0.01
19960101,    1.50,    0.10,   -0.30,    0.02
20010511,   -0.20,    0.05,    0.00,    0.01
20010514,    0.30,    0.00,    0.00,    0.01
20260227,   -0.51,   -0.44,   -1.25,    0.01

Copyright 2026 Eugene F. Fama and Kenneth R. French
"""


def test_parse_csv_extracts_data_block_only():
    df = parse_ken_french_csv(_SAMPLE_KF_CSV)
    # 6 valid YYYYMMDD rows in the sample
    assert len(df) == 6
    assert list(df.columns) == ["mkt_rf", "smb", "hml", "rf"]
    assert df.index.is_monotonic_increasing
    assert df.index.name == "date"
    assert df.index[0] == pd.Timestamp("1926-07-01")
    assert df.index[-1] == pd.Timestamp("2026-02-27")


def test_parse_csv_converts_percent_to_decimal():
    df = parse_ken_french_csv(_SAMPLE_KF_CSV)
    # KF ships 0.09 = 0.09% = 0.0009 decimal
    assert df.loc["1926-07-01", "mkt_rf"] == pytest.approx(0.0009)
    assert df.loc["1926-07-01", "rf"] == pytest.approx(0.0001)
    assert df.loc["1996-01-01", "mkt_rf"] == pytest.approx(0.015)


def test_parse_csv_skips_blank_and_footer_lines():
    df = parse_ken_french_csv(_SAMPLE_KF_CSV)
    # If we'd swallowed the Copyright line we'd choke; just ensure no
    # spurious row at the tail.
    assert df.index[-1] == pd.Timestamp("2026-02-27")


def test_parse_csv_raises_on_no_data():
    with pytest.raises(ValueError, match="no parseable data rows"):
        parse_ken_french_csv("Just a header.\nNo data here.\n")


def test_compute_market_total_return_is_mkt_rf_plus_rf():
    df = parse_ken_french_csv(_SAMPLE_KF_CSV)
    series = compute_market_total_return(df)
    assert series.name == "spx_tr_proxy"
    expected = df["mkt_rf"] + df["rf"]
    pd.testing.assert_series_equal(
        series, expected.rename("spx_tr_proxy"), check_names=True
    )


def test_compute_market_total_return_requires_columns():
    bad = pd.DataFrame({"mkt_rf": [0.01]}, index=[pd.Timestamp("2020-01-01")])
    with pytest.raises(ValueError, match="missing required column 'rf'"):
        compute_market_total_return(bad)


def test_fetch_ken_french_uses_cache_when_present(tmp_path: Path):
    cache_dir = tmp_path / "ken_french"
    cache_dir.mkdir()
    csv_path = cache_dir / "F-F_Research_Data_Factors_daily.csv"
    csv_path.write_text(_SAMPLE_KF_CSV)
    # No network call — should read from cache.
    df = fetch_ken_french_daily(cache_dir=cache_dir, force=False)
    assert len(df) == 6


# --- Stitching tests use a synthetic Tiingo storage to avoid live deps ---


def _make_synthetic_tiingo_storage(
    tmp_path: Path,
    spy_dates: list[pd.Timestamp],
    spy_adj_close: list[float],
) -> Path:
    root = tmp_path / "tiingo"
    daily_prices = root / "daily" / "prices"
    daily_prices.mkdir(parents=True)
    df = pd.DataFrame(
        {
            "open": spy_adj_close,
            "high": spy_adj_close,
            "low": spy_adj_close,
            "close": spy_adj_close,
            "adj_close": spy_adj_close,
            "volume": [1.0] * len(spy_adj_close),
        },
        index=pd.DatetimeIndex(spy_dates, name="date"),
    )
    df.to_parquet(daily_prices / "SPY.parquet")
    manifest = root / "manifest.json"
    manifest.write_text(
        '{"SPY": {"daily": {"asset_class": "etf", '
        '"first_dt": "' + spy_dates[0].isoformat() + '", '
        '"last_dt": "' + spy_dates[-1].isoformat() + '", '
        '"n_bars": ' + str(len(spy_dates)) + ', '
        '"fetched_at": "2026-04-16T00:00:00", '
        '"requested_start": "' + spy_dates[0].isoformat() + '", '
        '"requested_end": "' + spy_dates[-1].isoformat() + '"}}}'
    )
    return root


def test_load_spx_tr_daily_stitches_pre_and_post(tmp_path: Path):
    # KF cache (pre-cutoff covers 1970+ in real data, here just our 6 sample rows).
    cache_dir = tmp_path / "ken_french"
    cache_dir.mkdir()
    (cache_dir / "F-F_Research_Data_Factors_daily.csv").write_text(_SAMPLE_KF_CSV)
    # Tiingo SPY post-cutoff: 3 days starting at the cutoff itself.
    cutoff = pd.Timestamp("2001-05-14")
    spy_dates = [cutoff, cutoff + pd.Timedelta(days=1), cutoff + pd.Timedelta(days=2)]
    spy_close = [100.0, 101.0, 99.99]
    storage_root = _make_synthetic_tiingo_storage(tmp_path, spy_dates, spy_close)

    series = load_spx_tr_daily(
        start="1900-01-01",
        end="2030-01-01",
        cutoff_date=cutoff,
        tiingo_storage_root=storage_root,
        cache_dir=cache_dir,
    )
    # Pre-cutoff (<= cutoff): 5 KF rows (1926-07-01, 1926-07-02, 1996-01-01,
    # 2001-05-11, 2001-05-14 — cutoff itself is sourced from KF because
    # SPY pct_change[cutoff] is NaN). Post (> cutoff): 2 SPY pct_change rows.
    assert series.index.is_monotonic_increasing
    assert series.name == "spx_tr_daily"
    assert series.notna().all()
    pre_idx = series.index[series.index <= cutoff]
    post_idx = series.index[series.index > cutoff]
    assert pre_idx[-1] == cutoff  # KF supplies the cutoff day
    assert post_idx[0] == cutoff + pd.Timedelta(days=1)  # first SPY pct_change
    assert series.index.is_unique


def test_load_spx_tr_daily_post_uses_pct_change(tmp_path: Path):
    cache_dir = tmp_path / "ken_french"
    cache_dir.mkdir()
    (cache_dir / "F-F_Research_Data_Factors_daily.csv").write_text(_SAMPLE_KF_CSV)
    cutoff = pd.Timestamp("2001-05-14")
    spy_dates = [cutoff, cutoff + pd.Timedelta(days=1), cutoff + pd.Timedelta(days=2)]
    spy_close = [100.0, 110.0, 121.0]  # +10% / +10% (deterministic)
    storage_root = _make_synthetic_tiingo_storage(tmp_path, spy_dates, spy_close)

    series = load_spx_tr_daily(
        start="2001-05-13",
        end="2001-05-20",
        cutoff_date=cutoff,
        tiingo_storage_root=storage_root,
        cache_dir=cache_dir,
    )
    # Tiingo supplies returns strictly AFTER cutoff_date.
    post = series.loc[series.index > cutoff]
    assert len(post) == 2
    assert post.iloc[0] == pytest.approx(0.10)
    assert post.iloc[1] == pytest.approx(0.10)


def test_load_spx_tr_daily_rejects_inverted_window(tmp_path: Path):
    cache_dir = tmp_path / "ken_french"
    cache_dir.mkdir()
    (cache_dir / "F-F_Research_Data_Factors_daily.csv").write_text(_SAMPLE_KF_CSV)
    storage_root = _make_synthetic_tiingo_storage(
        tmp_path,
        [pd.Timestamp("2001-05-14")],
        [100.0],
    )
    with pytest.raises(ValueError, match="must be >"):
        load_spx_tr_daily(
            start="2020-01-01",
            end="2010-01-01",
            cutoff_date=pd.Timestamp("2001-05-14"),
            tiingo_storage_root=storage_root,
            cache_dir=cache_dir,
        )


def test_default_cutoff_matches_tiingo_manifest():
    # Anchor: if Tiingo SPY first_dt ever changes, this constant must too.
    assert DEFAULT_TIINGO_CUTOFF == pd.Timestamp("2001-05-14")
