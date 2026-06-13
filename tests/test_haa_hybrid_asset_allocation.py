from __future__ import annotations

import numpy as np
import pandas as pd

from studies.haa_hybrid_asset_allocation.haa import (
    HAAConfig,
    haa_monthly_weights,
    load_testfolio_price_frame,
    momentum_13612u,
    simulate_haa_gross,
    simulate_haa_holdings_loop,
)
from studies.haa_hybrid_asset_allocation.run import adapt_config_to_available_prices, json_safe


def _monthly_prices(rates: dict[str, float], n_months: int = 18) -> pd.DataFrame:
    dates = pd.date_range("2020-01-31", periods=n_months, freq="ME")
    assets = sorted({"TIP", "BIL", "IEF", "A", "B", "C", "D", "E"})
    data = {}
    for asset in assets:
        rate = rates.get(asset, 0.0)
        data[asset] = [100.0 * ((1.0 + rate) ** i) for i in range(n_months)]
    return pd.DataFrame(data, index=dates)


def _daily_prices(rates: dict[str, float], n_days: int = 520) -> pd.DataFrame:
    dates = pd.bdate_range("2020-01-01", periods=n_days)
    assets = sorted({"TIP", "BIL", "IEF", "A", "B", "C", "D", "E"})
    data = {}
    for i, asset in enumerate(assets):
        base = rates.get(asset, 0.0001 + i * 0.00001)
        seasonal = 0.0002 * np.sin(np.arange(n_days) / (23.0 + i))
        data[asset] = 100.0 * np.cumprod(1.0 + base + seasonal)
    return pd.DataFrame(data, index=dates)


def test_momentum_13612u_requires_full_12_month_history() -> None:
    prices = _monthly_prices({"A": 0.01}, n_months=14)

    scores = momentum_13612u(prices, ["A"])

    assert scores["A"].iloc[11] != scores["A"].iloc[11]
    assert scores["A"].iloc[12] > 0.0


def test_canary_negative_allocates_all_to_best_defensive() -> None:
    rates = {
        "TIP": -0.02,
        "BIL": 0.001,
        "IEF": 0.01,
        "A": 0.05,
        "B": 0.04,
        "C": 0.03,
        "D": 0.02,
    }
    prices = _monthly_prices(rates)
    config = HAAConfig(name="fixture", offensive_assets=("A", "B", "C", "D"))

    weights = haa_monthly_weights(prices, config).iloc[-1]

    assert np.isclose(weights["IEF"], 1.0)
    assert np.isclose(weights.sum(), 1.0)


def test_canary_positive_selects_top_four_and_replaces_negative_slot() -> None:
    rates = {
        "TIP": 0.01,
        "BIL": 0.001,
        "IEF": 0.010,
        "A": 0.050,
        "B": 0.040,
        "C": 0.030,
        "D": -0.010,
        "E": -0.020,
    }
    prices = _monthly_prices(rates)
    config = HAAConfig(name="fixture", offensive_assets=("A", "B", "C", "D", "E"))

    weights = haa_monthly_weights(prices, config).iloc[-1]

    assert np.isclose(weights["A"], 0.25)
    assert np.isclose(weights["B"], 0.25)
    assert np.isclose(weights["C"], 0.25)
    assert np.isclose(weights["IEF"], 0.25)
    assert np.isclose(weights.sum(), 1.0)


def test_vectorized_and_holdings_loop_simulations_match() -> None:
    rates = {
        "TIP": 0.0002,
        "BIL": 0.00001,
        "IEF": 0.00008,
        "A": 0.0004,
        "B": 0.0003,
        "C": 0.0002,
        "D": 0.0001,
    }
    prices = _daily_prices(rates)
    config = HAAConfig(name="fixture", offensive_assets=("A", "B", "C", "D"))

    vectorized, _weights = simulate_haa_gross(prices, config)
    loop = simulate_haa_holdings_loop(prices, config)
    aligned = pd.concat({"vectorized": vectorized, "loop": loop}, axis=1).dropna()

    assert not aligned.empty
    assert np.allclose(aligned["vectorized"], aligned["loop"], atol=1e-12)


def test_json_safe_converts_non_finite_numbers_to_null() -> None:
    payload = {"pbo": np.nan, "nested": [np.inf, -np.inf, np.float64(1.25), np.int64(2)]}

    cleaned = json_safe(payload)

    assert cleaned == {"pbo": None, "nested": [None, None, 1.25, 2]}


def test_testfolio_loader_maps_bil_to_cashx(tmp_path) -> None:
    dates = pd.date_range("2020-01-01", periods=3, freq="B")
    cache = tmp_path / "history.parquet"
    pd.DataFrame(
        {
            "CASHX": [10_000.0, 10_001.0, 10_002.0],
            "IEFSIM": [10_000.0, 10_010.0, 10_020.0],
        },
        index=dates,
    ).to_parquet(cache)

    prices = load_testfolio_price_frame(["BIL", "IEF"], path=cache)

    assert list(prices.columns) == ["BIL", "IEF"]
    assert prices["BIL"].iloc[-1] == 10_002.0


def test_yfinance_adaptation_drops_missing_offensive_assets() -> None:
    config = HAAConfig(name="fixture", offensive_assets=("A", "B", "C", "D"), top_n=2)
    prices = pd.DataFrame(index=pd.date_range("2020-01-01", periods=3, freq="B"))
    prices.attrs["missing_tickers"] = ["C"]

    adapted = adapt_config_to_available_prices(config, prices)

    assert adapted.name == "fixture_yf_available3"
    assert adapted.offensive_assets == ("A", "B", "D")
    assert adapted.top_n == 2
