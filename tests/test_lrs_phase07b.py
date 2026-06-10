from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lrs.lib.backtest import synth_leveraged_returns
from lrs.phases.phase07b_multiasset_portfolio.run import (
    leg_risk_on_weights,
    portfolio_frame,
)


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("1995-01-01", periods=n)


def test_synth_leverage_formula() -> None:
    idx = _days(4)
    underlying = pd.Series([0.01, -0.02, 0.00, 0.03], index=idx)
    cash = pd.Series([0.0002] * 4, index=idx)

    synth = synth_leveraged_returns(underlying, 2.0, cash, fee_annual=0.0095)

    expected = 2.0 * underlying - 1.0 * cash - 0.0095 / 252.0
    assert np.allclose(synth.to_numpy(), expected.to_numpy())


def test_synth_leverage_one_is_underlying_minus_fee() -> None:
    idx = _days(3)
    underlying = pd.Series([0.01, -0.01, 0.02], index=idx)
    cash = pd.Series([0.01] * 3, index=idx)  # must NOT matter at L=1

    synth = synth_leveraged_returns(underlying, 1.0, cash, fee_annual=0.0095)

    expected = underlying - 0.0095 / 252.0
    assert np.allclose(synth.to_numpy(), expected.to_numpy())


def test_synth_leverage_rejects_below_one() -> None:
    idx = _days(3)
    series = pd.Series([0.0, 0.0, 0.0], index=idx)
    with pytest.raises(ValueError):
        synth_leveraged_returns(series, 0.5, series)


def test_leg_risk_on_weights_ladder() -> None:
    assert leg_risk_on_weights("SPY", 2.00) == {"SSOSIM": 1.0}
    assert leg_risk_on_weights("SPY", 1.75) == {"SPYSIM": 0.25, "SSOSIM": 0.75}
    assert leg_risk_on_weights("IWM", 1.75) == {"IWMSIM": 0.25, "IWM2XSYN": 0.75}
    with pytest.raises(ValueError):
        leg_risk_on_weights("SPY", 2.5)


def test_portfolio_frame_equal_weights_and_column_union() -> None:
    idx = _days(3)
    leg_a = pd.DataFrame({"SPYSIM": [1.0, 0.0, 1.0], "ZROZSIM": [0.0, 1.0, 0.0]}, index=idx)
    leg_b = pd.DataFrame({"GLDSIM": [1.0, 1.0, 0.0], "ZROZSIM": [0.0, 0.0, 1.0]}, index=idx)

    port = portfolio_frame([leg_a, leg_b])

    assert sorted(port.columns) == ["GLDSIM", "SPYSIM", "ZROZSIM"]
    # Rows always sum to 1 (each leg frame sums to 1).
    assert np.allclose(port.sum(axis=1).to_numpy(), 1.0)
    assert port.loc[idx[0], "SPYSIM"] == 0.5
    assert port.loc[idx[1], "ZROZSIM"] == 0.5
