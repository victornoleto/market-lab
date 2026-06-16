from __future__ import annotations

import numpy as np
import pandas as pd

from studies.momentum_13612_universes.core import (
    Momentum13612Config,
    daily_weights_from_monthly,
    momentum_13612u,
    monthly_top_n_weights,
    simulate_momentum_gross,
    simulate_momentum_holdings_loop,
)
from studies.momentum_13612_universes.extensive import (
    ExtensiveConfig,
    ScoreBundle,
    apply_br_foreign_annual_tax,
    composite_momentum_lowvol,
    extensive_monthly_weights,
    is_rebalance_month,
    rolling_relative_equity_metrics,
    rolling_relative_equity_windows,
    simulate_extensive_config,
    simulate_staggered_offsets,
)
from studies.momentum_13612_universes.run import json_safe
from studies.momentum_13612_universes.run_stocks_evolution import monthly_weights_with_overlay
from studies.momentum_13612_universes.universes import (
    br_etf_tickers,
    br_stock_tickers,
    drop_extreme_return_tickers,
    normalize_yfinance_us_ticker,
    sp500_pit_membership_from_changes,
)


def _monthly_prices(rates: dict[str, float], n_months: int = 18) -> pd.DataFrame:
    dates = pd.date_range("2020-01-31", periods=n_months, freq="ME")
    assets = sorted(rates)
    data = {
        asset: [100.0 * ((1.0 + rate) ** i) for i in range(n_months)]
        for asset, rate in rates.items()
    }
    return pd.DataFrame(data, index=dates, columns=assets)


def _daily_prices(rates: dict[str, float], n_days: int = 560) -> pd.DataFrame:
    dates = pd.bdate_range("2020-01-01", periods=n_days)
    data = {}
    for i, (asset, rate) in enumerate(sorted(rates.items())):
        seasonal = 0.0001 * np.sin(np.arange(n_days) / (19.0 + i))
        data[asset] = 100.0 * np.cumprod(1.0 + rate + seasonal)
    return pd.DataFrame(data, index=dates)


def test_momentum_13612u_requires_full_12_month_history() -> None:
    prices = _monthly_prices({"A": 0.01}, n_months=14)

    scores = momentum_13612u(prices, ["A"])

    assert pd.isna(scores["A"].iloc[11])
    assert scores["A"].iloc[12] > 0.0


def test_pure_top_n_holds_least_bad_assets_when_all_scores_negative() -> None:
    prices = _monthly_prices({"A": -0.01, "B": -0.02, "C": -0.03}, n_months=18)
    config = Momentum13612Config(name="fixture", assets=("A", "B", "C"), top_n=2)

    weights = monthly_top_n_weights(prices, config).iloc[-1]

    assert np.isclose(weights["A"], 0.5)
    assert np.isclose(weights["B"], 0.5)
    assert np.isclose(weights["C"], 0.0)
    assert np.isclose(weights.sum(), 1.0)


def test_tie_breaking_is_alphabetical() -> None:
    prices = _monthly_prices({"A": 0.01, "B": 0.01, "C": 0.005}, n_months=18)
    config = Momentum13612Config(name="fixture", assets=("B", "A", "C"), top_n=1)

    weights = monthly_top_n_weights(prices, config).iloc[-1]

    assert np.isclose(weights["A"], 1.0)
    assert np.isclose(weights["B"], 0.0)


def test_daily_simulation_does_not_use_same_day_signal_return() -> None:
    prices = _daily_prices({"A": 0.0004, "B": 0.0001}, n_days=560)
    config = Momentum13612Config(name="fixture", assets=("A", "B"), top_n=1)

    monthly_weights = monthly_top_n_weights(prices, config)
    daily_weights = daily_weights_from_monthly(prices, monthly_weights)
    gross, _weights = simulate_momentum_gross(prices, config)
    first_signal = daily_weights.sum(axis=1).gt(0.0).idxmax()

    assert np.isclose(gross.loc[first_signal], 0.0)


def test_vectorized_and_holdings_loop_simulations_match() -> None:
    prices = _daily_prices({"A": 0.0004, "B": 0.0003, "C": 0.0002}, n_days=620)
    config = Momentum13612Config(name="fixture", assets=("A", "B", "C"), top_n=2)

    vectorized, _weights = simulate_momentum_gross(prices, config)
    loop = simulate_momentum_holdings_loop(prices, config)
    aligned = pd.concat({"vectorized": vectorized, "loop": loop}, axis=1).dropna()

    assert not aligned.empty
    assert np.allclose(aligned["vectorized"], aligned["loop"], atol=1e-12)


def test_universe_helpers_include_curated_br_etfs_and_sa_stocks() -> None:
    assert "BOVA11.SA" in br_etf_tickers()
    assert "IVVB11.SA" in br_etf_tickers()
    assert all(ticker.endswith(".SA") for ticker in br_stock_tickers(limit=10))


def test_us_yfinance_share_class_normalization() -> None:
    assert normalize_yfinance_us_ticker("BRK.B") == "BRK-B"


def test_drop_extreme_return_tickers_removes_bad_adjusted_series() -> None:
    prices = pd.DataFrame(
        {
            "GOOD": [100.0, 101.0, 102.0],
            "BAD": [100.0, 10_000.0, 101.0],
        },
        index=pd.date_range("2020-01-01", periods=3),
    )

    filtered, dropped = drop_extreme_return_tickers(prices, max_abs_daily_return=10.0)

    assert dropped == ["BAD"]
    assert list(filtered.columns) == ["GOOD"]


def test_sp500_pit_membership_walks_back_and_normalizes_tickers() -> None:
    dates = pd.DatetimeIndex(["2020-12-31", "2021-01-31"])
    changes = pd.DataFrame(
        {
            "date": pd.to_datetime(["2021-01-05"]),
            "added": ["AAPL"],
            "removed": ["OLD.B"],
        }
    )

    tickers, membership = sp500_pit_membership_from_changes(dates, {"AAPL", "BRK.B"}, changes)

    assert tickers == ["AAPL", "BRK-B", "OLD-B"]
    assert membership[pd.Timestamp("2020-12-31")] == {"BRK-B", "OLD-B"}
    assert membership[pd.Timestamp("2021-01-31")] == {"AAPL", "BRK-B"}


def test_json_safe_converts_non_finite_numbers_to_null() -> None:
    payload = {"pbo": np.nan, "nested": [np.inf, -np.inf, np.float64(1.25), np.int64(2)]}

    cleaned = json_safe(payload)

    assert cleaned == {"pbo": None, "nested": [None, None, 1.25, 2]}


def test_rebalance_month_offsets_are_calendar_based() -> None:
    dates = pd.date_range("2020-01-31", periods=12, freq="ME")

    offset_zero = [date.month for date in dates if is_rebalance_month(date, 3, 0)]
    offset_one = [date.month for date in dates if is_rebalance_month(date, 3, 1)]

    assert offset_zero == [1, 4, 7, 10]
    assert offset_one == [2, 5, 8, 11]


def test_extensive_weights_respect_rebalance_frequency() -> None:
    dates = pd.date_range("2020-01-31", periods=12, freq="ME")
    monthly = pd.DataFrame({"A": range(12), "B": range(1, 13)}, index=dates)
    scores = pd.DataFrame({"A": 0.2, "B": 0.1}, index=dates)
    bundle = ScoreBundle(monthly_prices=monthly, scores={"raw_13612": scores}, monthly_vol=scores + 1.0)
    config = ExtensiveConfig(
        name="fixture",
        universe="us_stocks",
        assets=("A", "B"),
        top_n=1,
        rebalance_months=6,
        rebalance_offset=3,
        score_mode="raw_13612",
    )

    weights = extensive_monthly_weights(bundle, config)

    assert [date.month for date in weights.index] == [4, 10]
    assert (weights["A"] == 1.0).all()


def test_extensive_weights_respect_date_specific_eligibility() -> None:
    dates = pd.date_range("2020-01-31", periods=3, freq="ME")
    monthly = pd.DataFrame({"A": [1.0, 2.0, 3.0], "B": [1.0, 1.5, 2.0]}, index=dates)
    scores = pd.DataFrame({"A": 1.0, "B": 0.5}, index=dates)
    bundle = ScoreBundle(monthly_prices=monthly, scores={"raw_13612": scores}, monthly_vol=scores + 1.0)
    config = ExtensiveConfig(
        name="fixture",
        universe="us_stocks",
        assets=("A", "B"),
        top_n=1,
        rebalance_months=1,
        rebalance_offset=0,
        score_mode="raw_13612",
    )
    eligible = {dates[0]: {"B"}, dates[1]: {"A", "B"}, dates[2]: {"A", "B"}}

    weights = extensive_monthly_weights(bundle, config, eligible_by_date=eligible)

    assert np.isclose(weights.loc[dates[0], "B"], 1.0)
    assert np.isclose(weights.loc[dates[1], "A"], 1.0)


def test_evolution_overlay_weights_only_emit_rebalance_rows() -> None:
    dates = pd.date_range("2020-01-31", periods=12, freq="ME")
    monthly = pd.DataFrame({"A": range(12), "B": range(1, 13)}, index=dates)
    scores = pd.DataFrame({"A": 0.2, "B": 0.1}, index=dates)
    bundle = ScoreBundle(monthly_prices=monthly, scores={"raw_13612": scores}, monthly_vol=scores + 1.0)
    config = ExtensiveConfig(
        name="fixture",
        universe="us_stocks",
        assets=("A", "B"),
        top_n=1,
        rebalance_months=3,
        rebalance_offset=0,
        score_mode="raw_13612",
    )

    weights = monthly_weights_with_overlay(
        bundle,
        config,
        "none",
        monthly_market_ok=pd.Series(True, index=dates),
        monthly_stock_ok=pd.DataFrame(True, index=dates, columns=["A", "B"]),
    )

    assert [date.month for date in weights.index] == [1, 4, 7, 10]
    assert (weights["A"] == 1.0).all()


def test_evolution_overlay_weights_respect_date_specific_eligibility() -> None:
    dates = pd.date_range("2020-01-31", periods=3, freq="ME")
    monthly = pd.DataFrame({"A": [1.0, 2.0, 3.0], "B": [1.0, 1.5, 2.0]}, index=dates)
    scores = pd.DataFrame({"A": 1.0, "B": 0.5}, index=dates)
    bundle = ScoreBundle(monthly_prices=monthly, scores={"raw_13612": scores}, monthly_vol=scores + 1.0)
    config = ExtensiveConfig(
        name="fixture",
        universe="us_stocks",
        assets=("A", "B"),
        top_n=1,
        rebalance_months=1,
        rebalance_offset=0,
        score_mode="raw_13612",
    )
    eligible = {dates[0]: {"B"}, dates[1]: {"A", "B"}, dates[2]: {"A", "B"}}

    weights = monthly_weights_with_overlay(
        bundle,
        config,
        "none",
        monthly_market_ok=pd.Series(True, index=dates),
        monthly_stock_ok=pd.DataFrame(True, index=dates, columns=["A", "B"]),
        eligible_by_date=eligible,
    )

    assert np.isclose(weights.loc[dates[0], "B"], 1.0)
    assert np.isclose(weights.loc[dates[1], "A"], 1.0)


def test_staggered_offsets_average_all_offset_sleeves() -> None:
    prices = _daily_prices({"A": 0.0004, "B": 0.0002}, n_days=520)
    monthly = prices.resample("ME").last()
    scores = pd.DataFrame(index=monthly.index, columns=["A", "B"], dtype=float)
    scores["A"] = [1.0 if i % 2 == 0 else 0.0 for i in range(len(scores))]
    scores["B"] = 1.0 - scores["A"]
    bundle = ScoreBundle(
        monthly_prices=monthly,
        scores={"raw_13612": scores},
        monthly_vol=pd.DataFrame(1.0, index=monthly.index, columns=["A", "B"]),
    )
    base = ExtensiveConfig(
        name="fixture_staggered",
        universe="us_etfs",
        assets=("A", "B"),
        top_n=1,
        rebalance_months=2,
        rebalance_offset=0,
        score_mode="raw_13612",
    )

    staggered = simulate_staggered_offsets(prices, bundle, base)
    sleeve_zero = simulate_extensive_config(prices, bundle, base)
    sleeve_one = simulate_extensive_config(
        prices,
        bundle,
        ExtensiveConfig(
            name="fixture_sleeve_one",
            universe="us_etfs",
            assets=("A", "B"),
            top_n=1,
            rebalance_months=2,
            rebalance_offset=1,
            score_mode="raw_13612",
        ),
    )
    expected = (
        sleeve_zero.daily_weights.reindex(staggered.daily_weights.index, columns=["A", "B"]).fillna(0.0)
        + sleeve_one.daily_weights.reindex(staggered.daily_weights.index, columns=["A", "B"]).fillna(0.0)
    ) / 2.0

    assert np.allclose(staggered.daily_weights[["A", "B"]], expected)
    assert np.isclose(staggered.daily_weights.sum(axis=1).iloc[0], 1.0)


def test_absolute_filter_leaves_cash_when_selected_score_is_negative() -> None:
    dates = pd.date_range("2020-01-31", periods=2, freq="ME")
    monthly = pd.DataFrame({"A": [100, 90], "B": [100, 80]}, index=dates)
    scores = pd.DataFrame({"A": [-0.1, -0.2], "B": [-0.3, -0.4]}, index=dates)
    bundle = ScoreBundle(monthly_prices=monthly, scores={"raw_13612": scores}, monthly_vol=scores.abs())
    config = ExtensiveConfig(
        name="fixture",
        universe="us_stocks",
        assets=("A", "B"),
        top_n=1,
        rebalance_months=1,
        rebalance_offset=0,
        score_mode="raw_13612",
        absolute_filter=True,
    )

    weights = extensive_monthly_weights(bundle, config)

    assert weights.empty


def test_composite_momentum_lowvol_prefers_momentum_and_low_vol_rank() -> None:
    idx = pd.DatetimeIndex(["2020-01-31"])
    raw = pd.DataFrame({"A": [0.30], "B": [0.20], "C": [0.10]}, index=idx)
    vol = pd.DataFrame({"A": [0.50], "B": [0.10], "C": [0.20]}, index=idx)

    score = composite_momentum_lowvol(raw, vol).iloc[0]

    assert score["A"] > score["C"]
    assert score["B"] > score["C"]


def test_br_foreign_annual_tax_nets_realized_gain_next_year() -> None:
    dates = pd.to_datetime(["2020-12-30", "2020-12-31", "2021-01-04"])
    returns = pd.Series([0.10, 0.0, 0.0], index=dates, name="fixture")
    weights = pd.DataFrame({"A": [1.0, 0.0, 0.0]}, index=dates)

    taxed = apply_br_foreign_annual_tax(returns, weights, initial_value=10_000.0)

    assert np.isclose(taxed.summary["total_tax_paid"], 150.0)
    assert np.isclose(taxed.summary["terminal_value"], 10_850.0)
    assert taxed.summary["years_taxed"] == 1
    assert taxed.returns.iloc[-1] < 0.0


def test_rolling_relative_equity_windows_reset_at_window_start() -> None:
    dates = pd.bdate_range("2010-01-01", "2017-12-31")
    strategy = pd.Series(0.0, index=dates, name="strategy")
    benchmark = pd.Series(0.0, index=dates, name="benchmark")
    strategy.loc[:"2010-12-31"] = 0.005
    benchmark.loc["2011-01-03":] = 0.0005

    windows = rolling_relative_equity_windows(strategy, benchmark, horizon_years=3)
    late = windows[windows["start"] >= pd.Timestamp("2011-01-31")]

    assert not late.empty
    assert (late["terminal_relative"] < 1.0).all()
    assert (late["min_relative_equity"] < 1.0).all()


def test_rolling_relative_equity_metrics_use_configured_horizons_only() -> None:
    dates = pd.bdate_range("1995-01-02", "2021-12-31")
    strategy = pd.Series(0.0004, index=dates, name="strategy")
    benchmark = pd.Series(0.0, index=dates, name="benchmark")

    metrics = rolling_relative_equity_metrics(strategy, benchmark)

    assert np.isclose(metrics["rolling_rel_score"], 1.0)
    assert np.isclose(metrics["rolling_rel_p25_score"], 1.0)
    assert np.isclose(metrics["rolling_rel_min_score"], 1.0)
    assert metrics["rel_20y_windows"] > 0.0
    assert "rel_30y_windows" not in metrics
