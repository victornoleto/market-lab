"""Offline tests for the yfinance -> Postgres sync helper."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from data.yfinance import sync as yf_sync


def test_parse_br_ticker_file_handles_quotes_suffix_and_duplicates(tmp_path: Path):
    path = tmp_path / "br.txt"
    path.write_text(
        "\n".join(
            [
                '"PETR4.SA"',
                "VALE3,",
                "# comment",
                "PETR4.SA",
                "",
            ]
        ),
        encoding="utf-8",
    )

    specs = yf_sync.parse_br_ticker_file(path)

    assert [spec.yf_symbol for spec in specs] == ["PETR4.SA", "VALE3.SA"]
    assert {spec.asset_class for spec in specs} == {"stock"}
    assert {spec.country for spec in specs} == {"br"}
    assert {spec.exchange for spec in specs} == {"B3"}


def test_parse_nasdaq_symbol_directory_classifies_stocks_and_etfs():
    text = "\n".join(
        [
            "Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares",
            "AAPL|Apple Inc. - Common Stock|Q|N|N|100|N|N",
            "SPY|SPDR S&P 500 ETF Trust|P|N|N|100|Y|N",
            "TEST|Test Issue Inc.|Q|Y|N|100|N|N",
            "File Creation Time: 0615202618|||||||",
        ]
    )

    specs = yf_sync.parse_nasdaq_symbol_directory(text, source="fixture")

    assert [(spec.yf_symbol, spec.asset_class, spec.country) for spec in specs] == [
        ("AAPL", "stock", "us"),
        ("SPY", "etf", "us"),
    ]
    assert specs[0].metadata["source"] == "fixture"


def test_parse_otherlisted_symbol_directory_uses_act_symbol_and_yahoo_preferred_format():
    text = "\n".join(
        [
            "ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol",
            "BRK.B|Berkshire Hathaway Inc.|N|BRK.B|N|100|N|BRK.B",
            "BAC$B|Bank of America Depositary Shares|N|BAC PR B|N|100|N|BAC$B",
            "QQQ|Invesco QQQ Trust|Q|QQQ|Y|100|N|QQQ",
            "File Creation Time: 0615202618|||||||",
        ]
    )

    specs = yf_sync.parse_nasdaq_symbol_directory(text, source="fixture")

    assert [spec.yf_symbol for spec in specs] == ["BRK-B", "BAC-PB", "QQQ"]
    assert specs[-1].asset_class == "etf"
    assert specs[-1].exchange == "Q"


def test_normalize_yfinance_history_fills_adjusted_close_and_actions():
    raw = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1000, 1200],
        },
        index=pd.DatetimeIndex(["2024-01-02", "2024-01-03"], tz="America/New_York"),
    )

    out = yf_sync.normalize_yfinance_history(raw)

    assert list(out.columns) == yf_sync.CANONICAL_PRICE_COLUMNS
    assert out.index.name == "date"
    assert out.index.tz is None
    assert out.loc[pd.Timestamp("2024-01-02"), "adj_close"] == 101.0
    assert out["dividends"].tolist() == [0.0, 0.0]
    assert out["stock_splits"].tolist() == [0.0, 0.0]


def test_price_rows_from_frame_converts_dates_and_volume_to_sql_scalars():
    frame = pd.DataFrame(
        {
            "open": [10.0],
            "high": [11.0],
            "low": [9.0],
            "close": [10.5],
            "adj_close": [10.4],
            "volume": [1234.0],
            "dividends": [0.1],
            "stock_splits": [0.0],
        },
        index=pd.DatetimeIndex(["2024-01-02"], name="date"),
    )

    rows = yf_sync.price_rows_from_frame(42, frame)

    assert len(rows) == 1
    row = rows[0]
    assert row[:10] == (
        42,
        pd.Timestamp("2024-01-02").date(),
        10.0,
        11.0,
        9.0,
        10.5,
        10.4,
        1234,
        0.1,
        0.0,
    )


def test_summarize_specs_groups_by_country_and_asset_class():
    specs = [
        yf_sync.TickerSpec("AAPL", "stock", "us"),
        yf_sync.TickerSpec("SPY", "etf", "us"),
        yf_sync.TickerSpec("PETR4.SA", "stock", "br"),
        yf_sync.TickerSpec("BTC-USD", "crypto", "global"),
    ]

    assert yf_sync.summarize_specs(specs) == {
        "br/stock": 1,
        "global/crypto": 1,
        "us/etf": 1,
        "us/stock": 1,
    }
