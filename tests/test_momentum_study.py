"""Offline tests for the Postgres-backed momentum study scaffold."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from studies.momentum.config import load_config, merged_filter_config
from studies.momentum.data import parse_date
from studies.momentum.features import canonicalize_prices, precompute_features
from studies.momentum.filters import FilterConfig, apply_filters
from studies.momentum.grid import build_strategy_grid
from studies.momentum.plots import plot_strategy_panel, select_finalists, write_aggregate_plots
from studies.momentum.strategies import simulate_strategy
from studies.momentum.validation import bootstrap_sharpe_ci_low, pbo_summary, result_row


def sample_prices(n_days: int = 900) -> pd.DataFrame:
    idx = pd.bdate_range("2020-01-01", periods=n_days)
    base = np.linspace(1.0, 2.0, n_days)
    return pd.DataFrame(
        {
            "AAA": 10.0 * base,
            "BBB": 20.0 * np.linspace(1.0, 1.4, n_days),
            "CCC": 30.0 * np.linspace(1.0, 0.8, n_days),
            "DDD": 40.0 * np.linspace(1.0, 1.1, n_days),
            "EEE": 50.0 * np.linspace(1.0, 1.3, n_days),
        },
        index=idx,
    )


def sample_volumes(prices: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(100_000, index=prices.index, columns=prices.columns)


def sample_metadata(symbols: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": list(range(1, len(symbols) + 1)),
            "yf_symbol": symbols,
            "asset_class": ["stock"] * len(symbols),
            "country": ["us"] * len(symbols),
        }
    )


def test_default_config_loads_and_merges_filters():
    config = load_config("studies/momentum/config/default.yaml")
    us_only = load_config("studies/momentum/config/us_stocks.yaml")
    merged = merged_filter_config(config, "br", "stock")

    assert "grid" in config
    assert merged["min_price"] == 2.0
    assert merged["min_history_months"] == 36
    assert us_only["grid"]["universes"] == ["us_stocks"]


def test_parse_date_accepts_yaml_date_objects_and_strings():
    assert parse_date("2020-01-01") == date(2020, 1, 1)
    assert parse_date(date(2020, 1, 1)) == date(2020, 1, 1)
    assert parse_date(None) is None


def test_filters_keep_liquid_long_history_and_drop_bad_names():
    prices = sample_prices()
    volumes = sample_volumes(prices)
    prices["LOWP"] = 0.5
    volumes["LOWP"] = 100_000
    prices["STALE"] = prices["AAA"]
    prices.loc[prices.index[-30]:, "STALE"] = np.nan
    volumes["STALE"] = 100_000
    metadata = sample_metadata(list(prices.columns))
    cfg = FilterConfig(
        min_history_months=24,
        min_price=5.0,
        min_median_dollar_volume=100_000,
        max_stale_days=10,
    )

    result = apply_filters(prices, volumes, metadata, cfg)

    assert "AAA" in result.prices.columns
    assert "LOWP" not in result.prices.columns
    assert "STALE" not in result.prices.columns
    lowp = result.diagnostics[result.diagnostics["yf_symbol"] == "LOWP"].iloc[0]
    assert "price" in lowp["reason"]


def test_precompute_features_builds_requested_score_modes():
    prices = sample_prices()

    bundle = precompute_features(
        prices,
        score_modes=["raw_13612", "mom_12_1", "clenow_trend", "vol_adjusted"],
        vol_window_days=63,
        trend_window_days=63,
    )

    assert set(bundle.scores) == {"raw_13612", "mom_12_1", "clenow_trend", "vol_adjusted"}
    assert not bundle.monthly_prices.empty
    assert bundle.scores["raw_13612"].shape == bundle.monthly_prices.shape


def test_build_strategy_grid_expands_offsets_and_staggered_configs():
    config = {
        "grid": {
            "universes": ["us_stocks"],
            "top_n": [2],
            "rebalance_months": [3],
            "rebalance_offsets": "all",
            "staggered_offsets": [False, True],
            "score_modes": ["raw_13612"],
            "weight_modes": ["equal"],
            "absolute_filter": [False],
        }
    }

    grid = build_strategy_grid(config, {"us_stocks": ("AAA", "BBB", "CCC")})

    assert len(grid) == 4
    assert sum(1 for item in grid if item.staggered_offsets) == 1
    assert {item.rebalance_offset for item in grid if not item.staggered_offsets} == {0, 1, 2}


def test_simulate_strategy_uses_previous_weights_and_returns_nonempty_series():
    prices = sample_prices()
    bundle = precompute_features(prices, score_modes=["raw_13612"], vol_window_days=63)
    config = build_strategy_grid(
        {
            "grid": {
                "universes": ["us_stocks"],
                "top_n": [2],
                "rebalance_months": [1],
                "rebalance_offsets": "all",
                "staggered_offsets": [False],
                "score_modes": ["raw_13612"],
                "weight_modes": ["equal"],
                "absolute_filter": [False],
            }
        },
        {"us_stocks": tuple(prices.columns)},
    )[0]

    simulation = simulate_strategy(prices, bundle, config)

    assert not simulation.returns.empty
    assert simulation.daily_weights.shift(1).iloc[1:].sum(axis=1).max() <= 1.0
    assert simulation.turnover["n_rebalances"] > 0


def test_simulate_strategy_fast_path_matches_default_path():
    prices = sample_prices()
    bundle = precompute_features(prices, score_modes=["raw_13612"], vol_window_days=63)
    config = build_strategy_grid(
        {
            "grid": {
                "universes": ["us_stocks"],
                "top_n": [2],
                "rebalance_months": [3],
                "rebalance_offsets": "all",
                "staggered_offsets": [True],
                "score_modes": ["raw_13612"],
                "weight_modes": ["equal"],
                "absolute_filter": [False],
            }
        },
        {"us_stocks": tuple(prices.columns)},
    )[0]
    daily = canonicalize_prices(prices)
    daily_returns = daily.pct_change(fill_method=None).fillna(0.0)

    baseline = simulate_strategy(prices, bundle, config)
    optimized = simulate_strategy(
        prices,
        bundle,
        config,
        daily_prices=daily,
        daily_returns=daily_returns,
    )

    pd.testing.assert_series_equal(baseline.returns, optimized.returns)


def test_result_row_contains_core_validation_metrics():
    prices = sample_prices()
    bundle = precompute_features(prices, score_modes=["raw_13612"], vol_window_days=63)
    config = build_strategy_grid(
        {
            "grid": {
                "universes": ["us_stocks"],
                "top_n": [2],
                "rebalance_months": [1],
                "rebalance_offsets": "all",
                "staggered_offsets": [False],
                "score_modes": ["raw_13612"],
                "weight_modes": ["equal"],
                "absolute_filter": [False],
            }
        },
        {"us_stocks": tuple(prices.columns)},
    )[0]
    simulation = simulate_strategy(prices, bundle, config)
    benchmark = prices[["AAA"]].rename(columns={"AAA": "SPY"})

    row = result_row(
        config,
        simulation,
        benchmark,
        n_trials=2,
        validation_config={
            "wf_min_windows": 4,
            "wf_min_positive": 3,
            "bootstrap_resamples": 20,
            "bootstrap_block_days": 21,
            "bootstrap_ci_low_pct": 5,
            "rolling_years": [1],
        },
        xlib_cagr_delta_pp=0.0,
    )

    assert row["name"] == config.name
    assert "dsr_p_value" in row
    assert "rolling_1y_min_return" in row
    assert row["promotion_eligible"] is False


def test_broad_validation_helpers_skip_bootstrap_and_mark_sampled_pbo():
    idx = pd.bdate_range("2020-01-01", periods=300)
    returns_by_name = {
        f"cfg_{i}": pd.Series(0.001 + i * 0.00001, index=idx) for i in range(5)
    }
    groups = pd.DataFrame(
        {
            "name": list(returns_by_name),
            "universe": ["us_stocks"] * len(returns_by_name),
            "mechanism": ["raw"] * len(returns_by_name),
        }
    )

    summary = pbo_summary(returns_by_name, groups, n_blocks=4, max_configs=4)

    assert np.isnan(bootstrap_sharpe_ci_low(next(iter(returns_by_name.values())), 0, 21, 5))
    assert summary["rows"][0]["sampled"] is True
    assert summary["rows"][0]["n_configs"] == 4
    assert summary["rows"][0]["n_configs_total"] == 5


def test_plot_helpers_create_manifest_ready_pngs(tmp_path):
    idx = pd.bdate_range("2020-01-01", periods=300)
    returns = pd.Series(0.001, index=idx, name="cfg_a")
    benchmark = pd.DataFrame({"SPY": 100.0 * (1.0005 ** np.arange(len(idx)))}, index=idx)
    results = pd.DataFrame(
        [
            {
                "name": "cfg_a",
                "universe": "us_stocks",
                "sharpe": 1.0,
                "calmar": 0.7,
                "excess_cagr": 0.05,
                "terminal": 1.2,
                "mdd": -0.10,
                "cagr": 0.18,
                "top_n": 3,
                "rebalance_months": 3,
            },
            {
                "name": "cfg_b",
                "universe": "us_etfs",
                "sharpe": 0.7,
                "calmar": 0.4,
                "excess_cagr": 0.02,
                "terminal": 1.1,
                "mdd": -0.08,
                "cagr": 0.12,
                "top_n": 5,
                "rebalance_months": 6,
            },
        ]
    )

    selected = select_finalists(results, max_finalists=1)
    aggregate_paths = write_aggregate_plots(results, tmp_path / "plots", tmp_path)
    panel_path = plot_strategy_panel(
        "cfg_a",
        returns,
        benchmark,
        "SPY",
        tmp_path / "plots" / "finalists",
        tmp_path,
    )

    assert list(selected["name"]) == ["cfg_a"]
    assert aggregate_paths
    assert panel_path is not None
    for rel_path in [*aggregate_paths, panel_path]:
        assert (tmp_path / rel_path).exists()
