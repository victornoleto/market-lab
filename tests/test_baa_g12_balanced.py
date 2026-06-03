from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


MODULE_PATH = (
    Path(__file__).parents[1]
    / "studies/return_stacked_core/legacy_algorithms/baa_g12.py"
)
spec = importlib.util.spec_from_file_location("baa_g12_iter001", MODULE_PATH)
baa = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(baa)


def _monthly_prices(rates: dict[str, float], n_months: int = 18) -> pd.DataFrame:
    dates = pd.date_range("2020-01-31", periods=n_months, freq="ME")
    data = {}
    for asset in sorted(set(baa.CANARY_ASSETS + baa.OFFENSIVE_ASSETS + baa.DEFENSIVE_ASSETS)):
        rate = rates.get(asset, 0.0)
        data[asset] = [100.0 * ((1.0 + rate) ** i) for i in range(n_months)]
    return pd.DataFrame(data, index=dates)


def test_offensive_mode_selects_top_six_equal_weight() -> None:
    rates = {asset: 0.01 for asset in baa.CANARY_ASSETS}
    for i, asset in enumerate(baa.OFFENSIVE_ASSETS):
        rates[asset] = 0.001 + i * 0.002
    prices = _monthly_prices(rates)

    weights = baa.baa_monthly_weights(prices).iloc[-1]
    expected = set(baa.OFFENSIVE_ASSETS[-6:])

    assert set(weights[weights > 0].index) == expected
    assert np.allclose(weights.loc[list(expected)].to_numpy(), np.full(6, 1.0 / 6.0))
    assert np.isclose(weights.sum(), 1.0)


def test_defensive_mode_replaces_assets_below_cash() -> None:
    rates = {asset: -0.02 for asset in baa.CANARY_ASSETS}
    rates.update({
        "IEFSIM": 0.020,
        "BNDSIM": 0.010,
        "TLTSIM": 0.000,
        "GLDSIM": -0.010,
        "KMLMSIM": -0.020,
        "CASHX": 0.015,
    })
    prices = _monthly_prices(rates)

    weights = baa.baa_monthly_weights(prices).iloc[-1]

    assert np.isclose(weights["IEFSIM"], 1.0 / 3.0)
    assert np.isclose(weights["CASHX"], 2.0 / 3.0)
    assert np.isclose(weights.sum(), 1.0)


def test_numpy_reference_stays_close_to_pandas_gross_cagr() -> None:
    dates = pd.bdate_range("2018-01-01", "2022-12-30")
    data = {}
    for i, asset in enumerate(sorted(set(baa.CANARY_ASSETS + baa.OFFENSIVE_ASSETS + baa.DEFENSIVE_ASSETS))):
        daily = 0.00005 + i * 0.000002
        seasonal = 0.0002 * np.sin(np.arange(len(dates)) / (19.0 + i))
        data[asset] = 100.0 * np.cumprod(1.0 + daily + seasonal)
    prices = pd.DataFrame(data, index=dates)

    pandas_rets, _ = baa.simulate_baa_g12_gross(prices)
    pandas_cagr = (1.0 + pandas_rets).prod() ** (252 / len(pandas_rets)) - 1.0
    numpy_rets = baa.simulate_baa_g12_numpy(prices)
    numpy_cagr = (1.0 + numpy_rets).prod() ** (252 / len(numpy_rets)) - 1.0

    assert abs(float(pandas_cagr - numpy_cagr)) < 0.03
