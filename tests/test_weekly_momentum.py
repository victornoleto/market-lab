"""Tests for studies.weekly_momentum.

The strategy is intentionally simple: cross-sectional trailing-return ranking
`[stocks_on_the_move, p.60]` with weekly review `[stocks_on_the_move, p.98-99]`.
"""
from __future__ import annotations

import pandas as pd
import pytest

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from studies.weekly_momentum.core import (
    WeeklyMomentumConfig,
    market_filter_allows_risk,
    momentum_scores,
    simulate_weekly_momentum,
    target_symbols,
    top_symbols,
)
from studies.weekly_momentum import data as weekly_data
from studies.weekly_momentum.data import list_universe
from studies.weekly_momentum.reporting import config_slug, write_run_outputs


def test_momentum_scores_rank_by_trailing_return() -> None:
    idx = pd.bdate_range("2024-01-01", periods=6)
    prices = pd.DataFrame(
        {
            "AAA": [100, 100, 100, 100, 100, 110],
            "BBB": [100, 100, 100, 100, 100, 105],
        },
        index=idx,
    )

    scores = momentum_scores(prices, idx[-1], lookback_days=5)

    assert scores["AAA"] == pytest.approx(0.10)
    assert scores["BBB"] == pytest.approx(0.05)
    assert top_symbols(scores, top_k=1) == ["AAA"]


def test_same_winner_is_not_sold_on_second_review() -> None:
    idx = pd.bdate_range("2024-01-01", periods=18)
    prices = pd.DataFrame(
        {
            "AAA": [
                100, 101, 102, 103, 100, 105, 110, 115, 120,
                121, 122, 123, 124, 130, 131, 132, 133, 134,
            ],
            "BBB": [
                100, 100, 100, 100, 100, 101, 102, 103, 104,
                104, 105, 106, 107, 108, 109, 110, 111, 112,
            ],
        },
        index=idx,
    )

    result = simulate_weekly_momentum(
        prices,
        WeeklyMomentumConfig(lookback_days=4, settlement_delay_days=0),
    )

    assert result.trades["action"].tolist() == ["buy"]
    assert result.trades["symbols"].tolist() == ["AAA"]
    assert result.trades["date"].tolist() == [pd.Timestamp("2024-01-15")]


def test_thursday_signal_sells_friday_and_buys_monday() -> None:
    idx = pd.bdate_range("2024-01-01", periods=18)
    prices = pd.DataFrame(
        {
            # AAA wins the first Thursday signal, then loses the second one.
            "AAA": [
                100, 101, 102, 103, 100, 105, 110, 115, 120,
                121, 122, 123, 124, 100, 100, 100, 100, 100,
            ],
            # BBB wins the second Thursday signal.
            "BBB": [
                100, 100, 100, 100, 100, 101, 102, 103, 104,
                104, 110, 120, 130, 140, 141, 142, 143, 144,
            ],
        },
        index=idx,
    )

    result = simulate_weekly_momentum(
        prices,
        WeeklyMomentumConfig(lookback_days=4, settlement_delay_days=0),
    )

    friday_sale = pd.Timestamp("2024-01-19")
    monday_after_sale = pd.Timestamp("2024-01-22")
    assert result.trades["action"].tolist() == ["buy", "sell", "buy"]
    assert result.trades["symbols"].tolist() == ["AAA", "AAA", "BBB"]
    assert result.trades["date"].tolist() == [
        pd.Timestamp("2024-01-15"),
        friday_sale,
        monday_after_sale,
    ]
    assert result.weights.loc[friday_sale, "AAA"] == 1.0
    assert result.weights.loc[monday_after_sale, "BBB"] == 1.0


def test_settlement_delay_skips_monday_after_friday_sale() -> None:
    idx = pd.bdate_range("2024-01-01", periods=18)
    prices = pd.DataFrame(
        {
            "AAA": [
                100, 101, 102, 103, 100, 105, 110, 115, 120,
                121, 122, 123, 124, 100, 100, 100, 100, 100,
            ],
            "BBB": [
                100, 100, 100, 100, 100, 101, 102, 103, 104,
                104, 110, 120, 130, 140, 141, 142, 143, 144,
            ],
        },
        index=idx,
    )

    result = simulate_weekly_momentum(
        prices,
        WeeklyMomentumConfig(lookback_days=4, settlement_delay_days=1),
    )

    monday_after_sale = pd.Timestamp("2024-01-22")
    tuesday_after_sale = pd.Timestamp("2024-01-23")
    assert result.trades["action"].tolist() == ["buy", "sell", "buy"]
    assert result.trades["symbols"].tolist() == ["AAA", "AAA", "BBB"]
    assert result.weights.loc[monday_after_sale].sum() == 0.0
    assert result.weights.loc[tuesday_after_sale, "BBB"] == 1.0


def test_friday_close_is_not_used_for_friday_sale_decision() -> None:
    idx = pd.bdate_range("2024-01-01", periods=12)
    prices = pd.DataFrame(
        {
            # BBB is better through Thursday. AAA only explodes on Friday,
            # which must be too late for a Friday sale decision using daily bars.
            "AAA": [100, 100, 100, 100, 100, 101, 102, 103, 104, 200, 201, 202],
            "BBB": [100, 100, 100, 100, 100, 105, 110, 115, 120, 121, 122, 123],
        },
        index=idx,
    )

    result = simulate_weekly_momentum(
        prices,
        WeeklyMomentumConfig(lookback_days=4, settlement_delay_days=0),
    )

    assert result.trades["action"].tolist() == ["buy"]
    assert result.trades["symbols"].tolist() == ["BBB"]
    assert result.trades["date"].tolist() == [pd.Timestamp("2024-01-15")]


def test_universe_by_date_filters_signal_ranking() -> None:
    idx = pd.bdate_range("2024-01-01", periods=12)
    prices = pd.DataFrame(
        {
            "AAA": [100, 100, 100, 100, 100, 120, 130, 140, 150, 151, 152, 153],
            "BBB": [100, 100, 100, 100, 100, 105, 110, 115, 120, 121, 122, 123],
        },
        index=idx,
    )

    result = simulate_weekly_momentum(
        prices,
        WeeklyMomentumConfig(lookback_days=4),
        universe_by_date=lambda _ts: {"BBB"},
    )

    assert result.trades["action"].tolist() == ["buy"]
    assert result.trades["symbols"].tolist() == ["BBB"]


def test_stale_held_symbol_sleeve_moves_to_cash() -> None:
    idx = pd.bdate_range("2024-01-01", periods=18)
    prices = pd.DataFrame(
        {
            "AAA": [100, 100, 100, 100, 100, 120, 130, 140, 150, 151, 152, 153, 154, None, None, None, None, None],
            "BBB": [100, 100, 100, 100, 100, 105, 110, 115, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129],
        },
        index=idx,
    )

    result = simulate_weekly_momentum(
        prices,
        WeeklyMomentumConfig(lookback_days=4, top_k=2),
    )

    stale_day = pd.Timestamp("2024-01-18")
    assert result.weights.loc[stale_day, "AAA"] == 0.0
    assert result.weights.loc[stale_day, "BBB"] == pytest.approx(0.5)
    assert result.weights.loc[stale_day].sum() == pytest.approx(0.5)


def test_list_universe_filters_tiingo_asset_class(tmp_path) -> None:
    storage = TiingoStorage(root=tmp_path / "tiingo")
    idx = pd.bdate_range("2024-01-01", periods=3)
    df = pd.DataFrame(
        {
            "open": [1.0, 1.0, 1.0],
            "high": [1.0, 1.0, 1.0],
            "low": [1.0, 1.0, 1.0],
            "close": [1.0, 1.0, 1.0],
            "adj_close": [1.0, 1.0, 1.0],
            "volume": [100.0, 100.0, 100.0],
        },
        index=idx,
    )
    storage.write("AAA", df, asset_class="equity")
    storage.write("SPY", df, asset_class="etf")

    assert list_universe("stocks", storage_root=tmp_path / "tiingo", stock_universe="all") == ["AAA"]
    assert list_universe("etfs", storage_root=tmp_path / "tiingo") == ["SPY"]


def test_list_universe_filters_stocks_to_sp500(tmp_path, monkeypatch) -> None:
    storage = TiingoStorage(root=tmp_path / "tiingo")
    idx = pd.bdate_range("2024-01-01", periods=3)
    df = pd.DataFrame(
        {
            "open": [1.0, 1.0, 1.0],
            "high": [1.0, 1.0, 1.0],
            "low": [1.0, 1.0, 1.0],
            "close": [1.0, 1.0, 1.0],
            "adj_close": [1.0, 1.0, 1.0],
            "volume": [100.0, 100.0, 100.0],
        },
        index=idx,
    )
    storage.write("AAA", df, asset_class="equity")
    storage.write("BBB", df, asset_class="equity")
    monkeypatch.setattr(weekly_data, "_current_sp500_tickers", lambda: {"AAA"})

    assert list_universe("stocks", storage_root=tmp_path / "tiingo") == ["AAA"]


def test_config_slug_is_stable() -> None:
    config = WeeklyMomentumConfig(
        lookback_days=4,
        signal_weekday=3,
        sell_delay_days=1,
        settlement_delay_days=0,
        top_k=1,
    )

    assert config_slug(config) == "lb4_sig3_sell1_sd0_k1_neg0_defcash_mf0"


def test_all_negative_scores_target_cash_by_default() -> None:
    scores = pd.Series({"AAA": -0.01, "BBB": -0.02})

    assert target_symbols(scores, top_k=1, require_positive_momentum=True) == []


def test_all_negative_scores_can_target_defensive_asset() -> None:
    scores = pd.Series({"AAA": -0.01, "BBB": -0.02})

    assert target_symbols(
        scores,
        top_k=1,
        require_positive_momentum=True,
        defensive_asset="ZROZ",
        available_symbols={"AAA", "BBB", "ZROZ"},
    ) == ["ZROZ"]


def test_all_negative_scores_can_buy_least_bad() -> None:
    scores = pd.Series({"AAA": -0.01, "BBB": -0.02})

    assert target_symbols(scores, top_k=1, allow_negative_momentum=True) == ["AAA"]


def test_all_negative_signal_sells_to_cash() -> None:
    idx = pd.bdate_range("2024-01-01", periods=18)
    prices = pd.DataFrame(
        {
            "AAA": [
                100, 101, 102, 103, 100, 105, 110, 115, 120,
                121, 110, 105, 100, 95, 94, 93, 92, 91,
            ],
            "BBB": [
                100, 100, 100, 100, 100, 101, 102, 103, 104,
                104, 103, 102, 101, 100, 99, 98, 97, 96,
            ],
        },
        index=idx,
    )

    result = simulate_weekly_momentum(prices, WeeklyMomentumConfig(lookback_days=4))

    assert result.trades["action"].tolist() == ["buy", "sell"]
    assert result.trades["symbols"].tolist() == ["AAA", "AAA"]
    assert result.weights.loc[pd.Timestamp("2024-01-22")].sum() == 0.0


def test_market_filter_blocks_risk_when_below_sma() -> None:
    idx = pd.bdate_range("2024-01-01", periods=12)
    prices = pd.DataFrame(
        {
            "AAA": [100, 100, 100, 100, 100, 105, 110, 115, 120, 121, 122, 123],
            "BBB": [100] * 12,
        },
        index=idx,
    )
    market = pd.Series([100, 100, 100, 100, 100, 90, 90, 90, 90, 89, 88, 87], index=idx)

    result = simulate_weekly_momentum(
        prices,
        WeeklyMomentumConfig(lookback_days=4, market_filter_type="sma", market_filter_days=3),
        market_filter_prices=market,
    )

    assert result.trades.empty
    assert result.weights.sum(axis=1).max() == 0.0


def test_market_filter_allows_risk_above_sma() -> None:
    idx = pd.bdate_range("2024-01-01", periods=4)
    market = pd.Series([100, 100, 100, 110], index=idx)
    sma = market.rolling(3).mean()

    assert market_filter_allows_risk(market, sma, idx[-1])


def test_ema_market_filter_allows_risk() -> None:
    idx = pd.bdate_range("2024-01-01", periods=12)
    prices = pd.DataFrame(
        {
            "AAA": [100, 100, 100, 100, 100, 105, 110, 115, 120, 121, 122, 123],
            "BBB": [100] * 12,
        },
        index=idx,
    )
    market = pd.Series([100, 100, 100, 100, 100, 105, 110, 115, 120, 121, 122, 123], index=idx)

    result = simulate_weekly_momentum(
        prices,
        WeeklyMomentumConfig(lookback_days=4, market_filter_type="ema", market_filter_days=3),
        market_filter_prices=market,
    )

    assert not result.trades.empty


def test_write_run_outputs_creates_report_bundle(tmp_path) -> None:
    idx = pd.bdate_range("2024-01-01", periods=30)
    prices = pd.DataFrame(
        {
            "AAA": [100 + i for i in range(30)],
            "BBB": [100 + i * 0.5 for i in range(30)],
        },
        index=idx,
    )
    spy = pd.DataFrame(
        {
            "open": [100 + i * 0.2 for i in range(30)],
            "high": [100 + i * 0.2 for i in range(30)],
            "low": [100 + i * 0.2 for i in range(30)],
            "close": [100 + i * 0.2 for i in range(30)],
            "adj_close": [100 + i * 0.2 for i in range(30)],
            "volume": [1_000_000.0] * 30,
        },
        index=idx,
    )
    spy_path = tmp_path / "SPY.parquet"
    spy.to_parquet(spy_path)

    config = WeeklyMomentumConfig()
    result = simulate_weekly_momentum(prices, config)
    out_dir = tmp_path / "results" / "stocks" / config_slug(config)

    payload = write_run_outputs(
        out_dir=out_dir,
        variation="stocks",
        config=config,
        result=result,
        n_assets=2,
        universe_label="sp500",
        spy_path=spy_path,
    )

    assert payload["config_slug"] == "lb4_sig3_sell1_sd0_k1_neg0_defcash_mf0"
    for name in [
        "config.json",
        "metrics.csv",
        "metrics.json",
        "equity.csv",
        "returns.csv",
        "weights.csv",
        "trades.csv",
        "benchmark_spy.csv",
        "report.md",
    ]:
        assert (out_dir / name).exists()
    for name in [
        "equity_vs_spy.png",
        "drawdown_vs_spy.png",
        "relative_to_spy.png",
        "rolling_252d_sharpe.png",
        "rolling_windows_1_3_5_10y.png",
    ]:
        assert (out_dir / "plots" / name).exists()

    metrics = pd.read_csv(out_dir / "metrics.csv", index_col=0)
    assert "sortino" in metrics.index
    report = (out_dir / "report.md").read_text(encoding="utf-8")
    for section in ["## Strategy", "## Result Summary", "## Metrics", "## Plots", "## Trades", "## Caveats", "## Review Notes"]:
        assert section in report
    assert "plots/equity_vs_spy.png" in report
    assert "plots/rolling_windows_1_3_5_10y.png" in report
