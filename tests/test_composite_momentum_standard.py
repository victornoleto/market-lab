from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


MODULE_PATH = (
    Path(__file__).parents[1]
    / "studies/long_term_portfolio/iterations/002-2026-04-28-0134-composite-momentum-standard/composite_momentum.py"
)
spec = importlib.util.spec_from_file_location("composite_momentum_iter002", MODULE_PATH)
cms = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cms)


def _daily_prices(rates: dict[str, float], n_days: int = 420) -> pd.DataFrame:
    dates = pd.bdate_range("2020-01-01", periods=n_days)
    data = {}
    for asset in sorted(set(cms.RISK_ASSETS + cms.DEFENSIVE_ASSETS)):
        rate = rates.get(asset, 0.0001)
        data[asset] = 100.0 * np.cumprod(np.full(n_days, 1.0 + rate))
    return pd.DataFrame(data, index=dates)


def test_risk_on_selects_positive_top_four_inverse_vol() -> None:
    rates = {
        "SPYSIM": 0.0010,
        "QQQSIM": 0.0013,
        "VEASIM": 0.0008,
        "TLTSIM": 0.0006,
        "IEFSIM": 0.0004,
        "GLDSIM": 0.0002,
        "KMLMSIM": -0.0003,
    }
    prices = _daily_prices(rates)

    weights = cms.composite_monthly_weights(prices).iloc[-1]
    expected = {"QQQSIM", "SPYSIM", "VEASIM", "TLTSIM"}

    assert set(weights[weights > 0].index) == expected
    assert np.isclose(weights.sum(), 1.0)
    assert weights["TLTSIM"] > 0.0


def test_risk_off_uses_ief_gold_defensive_sleeve() -> None:
    rates = {asset: 0.0002 for asset in cms.RISK_ASSETS}
    rates["SPYSIM"] = -0.0010
    prices = _daily_prices(rates)

    weights = cms.composite_monthly_weights(prices).iloc[-1]

    assert np.isclose(weights["IEFSIM"], 0.60)
    assert np.isclose(weights["GLDSIM"], 0.40)
    assert np.isclose(weights.sum(), 1.0)


def test_numpy_reference_stays_close_to_pandas_gross_cagr() -> None:
    dates = pd.bdate_range("2018-01-01", "2022-12-30")
    data = {}
    for i, asset in enumerate(sorted(set(cms.RISK_ASSETS + cms.DEFENSIVE_ASSETS))):
        daily = 0.00005 + i * 0.000002
        seasonal = 0.0002 * np.sin(np.arange(len(dates)) / (17.0 + i))
        data[asset] = 100.0 * np.cumprod(1.0 + daily + seasonal)
    prices = pd.DataFrame(data, index=dates)

    pandas_rets, _ = cms.simulate_composite_gross(prices)
    pandas_cagr = (1.0 + pandas_rets).prod() ** (252 / len(pandas_rets)) - 1.0
    numpy_rets = cms.simulate_composite_numpy(prices)
    numpy_cagr = (1.0 + numpy_rets).prod() ** (252 / len(numpy_rets)) - 1.0

    assert abs(float(pandas_cagr - numpy_cagr)) < 0.03
