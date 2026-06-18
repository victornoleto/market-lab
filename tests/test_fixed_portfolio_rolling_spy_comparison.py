from __future__ import annotations

import math

import pandas as pd
import pytest

from studies.return_stacked_core.us_core.fixed_portfolio_rolling_spy_comparison.run import (
    HORIZON_WEIGHTS,
    PortfolioSpec,
    TestfolioClient,
    WindowSpec,
    build_rolling_windows,
    evaluate_window,
    exposure_breakdown,
    portfolio_specs,
    simulate_monthly_rebalanced_equity,
    summarize_weighted_final,
)


def test_single_ticker_payload_is_public_and_preserves_custom_expression() -> None:
    payload = TestfolioClient.build_single_ticker_payload("SPYSIM?L=3&E=0.91")

    assert "authorization" not in str(payload).lower()
    assert payload["backtests"][0]["allocation"] == {"SPYSIM?L=3&E=0.91": 100}


def test_requested_and_sso_portfolios_sum_to_one_and_close_equity() -> None:
    specs = {spec.name: spec for spec in portfolio_specs()}

    for spec in specs.values():
        assert sum(spec.weights.values()) == pytest.approx(1.0)

    upro = exposure_breakdown(specs["p16_upro_29_zroz_25_rsst_30_gde"].weights)
    assert upro["effective_equity"] == pytest.approx(1.0)
    assert upro["effective_zroz"] == pytest.approx(0.29)

    for name in (
        "sso_proportional_scaled_core",
        "sso_keep_rsst_gde_reduce_zroz",
        "sso_keep_zroz_scale_rsst_gde",
    ):
        exposures = exposure_breakdown(specs[name].weights)
        assert exposures["effective_equity"] == pytest.approx(1.0)
        assert specs[name].weights["SSO_E091"] > 0.0

    proportional = specs["sso_proportional_scaled_core"].weights
    assert proportional["SSO_E091"] == pytest.approx(0.27586206896551724)
    assert proportional["ZROZ"] == pytest.approx(0.25)


def test_build_rolling_windows_uses_month_starts_and_month_exclusive_end() -> None:
    index = pd.bdate_range("2020-01-01", "2025-01-10")

    windows = build_rolling_windows(index, horizons=(3,))

    assert windows[0].start_date == pd.Timestamp("2020-01-01")
    assert windows[0].end_exclusive_date == pd.Timestamp("2023-01-02")
    assert windows[-1].start_date == pd.Timestamp("2022-01-03")
    assert windows[-1].end_exclusive_date == pd.Timestamp("2025-01-01")


def test_simulate_monthly_rebalanced_equity_rebalances_on_month_boundary() -> None:
    idx = pd.to_datetime(["2024-01-30", "2024-01-31", "2024-02-01"])
    returns = pd.DataFrame({"A": [0.10, 0.00, 0.00], "B": [0.00, 0.00, 0.10]}, index=idx)

    equity = simulate_monthly_rebalanced_equity(returns, {"A": 0.5, "B": 0.5})

    assert equity.iloc[0] == pytest.approx(1.05)
    assert equity.iloc[1] == pytest.approx(1.05)
    assert equity.iloc[2] == pytest.approx(1.1025)


def test_evaluate_window_identical_asset_matches_spy() -> None:
    idx = pd.bdate_range("2024-01-02", "2024-04-01")
    spy_returns = pd.Series(0.001, index=idx)
    returns = pd.DataFrame({"SPY": spy_returns, "ALT": spy_returns}, index=idx)
    portfolio = PortfolioSpec("alt", {"ALT": 1.0}, "identical to SPY")
    window = WindowSpec(
        horizon_years=0,
        start_date=pd.Timestamp("2024-01-02"),
        end_exclusive_date=pd.Timestamp("2024-04-01"),
    )

    row = evaluate_window(returns, portfolio, window)

    assert row is not None
    assert row["terminal_ratio_vs_spy"] == pytest.approx(1.0)
    assert row["log_terminal_ratio_vs_spy"] == pytest.approx(0.0)
    assert row["time_above_spy_pct"] == pytest.approx(0.0)
    assert row["final_hit_vs_spy"] is False


def test_weighted_final_uses_duration_weights_and_geo_ratio() -> None:
    rows = []
    for horizon, weight in HORIZON_WEIGHTS.items():
        rows.append(
            {
                "portfolio": "A",
                "horizon_years": horizon,
                "horizon_weight": weight,
                "mean_log_terminal_ratio": math.log(2.0),
                "hit_rate": 1.0,
                "mean_time_above_spy_pct": 0.75,
                "p10_terminal_ratio": 1.5,
                "p25_terminal_ratio": 1.6,
                "median_terminal_ratio": 2.0,
                "mean_relative_mdd_vs_spy": -0.10,
                "worst_relative_mdd_vs_spy": -0.20,
                "mean_longest_under_spy_days": 20.0,
                "mean_excess_cagr": 0.02,
            }
        )
        rows.append(
            {
                "portfolio": "B",
                "horizon_years": horizon,
                "horizon_weight": weight,
                "mean_log_terminal_ratio": 0.0,
                "hit_rate": 0.5,
                "mean_time_above_spy_pct": 0.25,
                "p10_terminal_ratio": 0.8,
                "p25_terminal_ratio": 0.9,
                "median_terminal_ratio": 1.0,
                "mean_relative_mdd_vs_spy": -0.20,
                "worst_relative_mdd_vs_spy": -0.40,
                "mean_longest_under_spy_days": 40.0,
                "mean_excess_cagr": 0.00,
            }
        )

    final = summarize_weighted_final(pd.DataFrame(rows))

    assert final.iloc[0]["portfolio"] == "A"
    assert final.iloc[0]["weighted_geo_terminal_ratio"] == pytest.approx(2.0)
    assert final.iloc[0]["weighted_hit_rate"] == pytest.approx(1.0)
