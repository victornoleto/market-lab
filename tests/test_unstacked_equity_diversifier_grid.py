from __future__ import annotations

import math

import pandas as pd
import pytest

from studies.return_stacked_core.us_core.unstacked_equity_diversifier_grid.run import (
    Scenario,
    TestfolioClient,
    alias_from_ticker,
    build_daily_returns,
    carrier_weights,
    exposure_breakdown,
    generate_candidate_table,
    rebalanced_returns,
)


def test_single_ticker_payload_is_public_and_preserves_custom_expression() -> None:
    payload = TestfolioClient.build_single_ticker_payload("SPYSIM?L=2&E=0.91")

    assert "authorization" not in str(payload).lower()
    assert payload["backtests"] == [
        {
            "invest_dividends": True,
            "rebalance_freq": "Yearly",
            "rebalance_offset": 0,
            "allocation": {"SPYSIM?L=2&E=0.91": 100},
            "drag": 0,
            "absolute_dev": 0,
            "relative_dev": 0,
        }
    ]


def test_alias_from_ticker_is_filesystem_safe() -> None:
    assert alias_from_ticker("SPYSIM?L=2&E=0.91") == "spysim_l_2_e_0_91"
    assert alias_from_ticker("CASHX?E=-2") == "cashx_e_2"


@pytest.mark.parametrize("leverage", [2.0, 2.5, 3.0])
def test_carrier_weights_keep_effective_equity_at_one(leverage: float) -> None:
    weights = carrier_weights(leverage)
    effective = 2.0 * weights["SSO_E091"] + 3.0 * weights["UPRO_E091"]
    capital = weights["SSO_E091"] + weights["UPRO_E091"]

    assert effective == pytest.approx(1.0)
    assert capital == pytest.approx(1.0 / leverage)


def test_generate_candidate_table_sums_to_one_and_effective_equity() -> None:
    scenario = Scenario("toy", ("CASH", "GOLD"), "toy")
    meta, weights, asset_cols = generate_candidate_table(
        scenario, leverage_step=0.5, diversifier_step_pct=50
    )

    assert asset_cols == ["SSO_E091", "UPRO_E091", "CASH", "GOLD"]
    assert len(meta) == 9
    assert weights.shape == (9, 4)
    assert (abs(weights.sum(axis=1) - 1.0) < 1e-12).all()
    assert meta["effective_equity"].sub(1.0).abs().max() < 1e-12


def test_rebalanced_returns_resets_on_month_boundary() -> None:
    idx = pd.to_datetime(["2024-01-30", "2024-01-31", "2024-02-01"])
    returns = pd.DataFrame({"A": [0.10, 0.00, 0.00], "B": [0.00, 0.00, 0.10]}, index=idx)

    result = rebalanced_returns(returns, {"A": 0.5, "B": 0.5}, freq="M")

    equity = (1.0 + result).cumprod()

    assert equity.iloc[0] == pytest.approx(1.05)
    assert equity.iloc[1] == pytest.approx(1.05)
    assert equity.iloc[2] == pytest.approx(1.1025)


def test_build_daily_returns_adds_mf_blend_and_rsst_proxy() -> None:
    idx = pd.date_range("2024-01-01", periods=3, freq="B")
    prices = pd.DataFrame(
        {
            "SPY": [100.0, 101.0, 102.0],
            "DBMF": [100.0, 102.0, 104.0],
            "KMLM": [100.0, 99.0, 98.0],
            "CASH_E_MINUS_2": [100.0, 100.01, 100.02],
        },
        index=idx,
    )

    returns = build_daily_returns(prices)
    expected_mf = 0.70 * returns["DBMF"] + 0.30 * returns["KMLM"]
    expected_rsst = returns["SPY"] + expected_mf - returns["CASH_E_MINUS_2"]

    pd.testing.assert_series_equal(returns["MF70DBMF30KMLM"], expected_mf, check_names=False)
    pd.testing.assert_series_equal(returns["RSST70_30"], expected_rsst, check_names=False)
    assert math.isfinite(float(returns["RSST70_30"].dropna().iloc[0]))


def test_exposure_breakdown_for_gde_rsst_upro_proposal() -> None:
    exposures = exposure_breakdown(
        {"ZROZ": 0.25, "RSST70_30": 0.25, "GDE": 0.30, "UPRO_E091": 0.16, "CASH": 0.04}
    )

    assert exposures["effective_equity"] == pytest.approx(1.00)
    assert exposures["effective_mf"] == pytest.approx(0.25)
    assert exposures["effective_gold"] == pytest.approx(0.27)
    assert exposures["effective_zroz"] == pytest.approx(0.25)
