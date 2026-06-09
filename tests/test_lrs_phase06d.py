from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lrs.phases.phase06d_inverse_sleeve.run import (
    INVERSE_FEE_ANNUAL,
    blend_risk_off,
    crisis_window_stats,
    synthesize_inverse_returns,
)


def test_synthesize_inverse_sign_and_fee_drag() -> None:
    idx = pd.bdate_range("2020-01-01", periods=3)
    rets = pd.Series([0.01, -0.02, 0.0], index=idx)

    inv = synthesize_inverse_returns(rets)

    fee_daily = INVERSE_FEE_ANNUAL / 252.0
    assert abs(inv.iloc[0] - (-0.01 - fee_daily)) < 1e-15
    assert abs(inv.iloc[1] - (0.02 - fee_daily)) < 1e-15
    # Flat day still bleeds the fee.
    assert abs(inv.iloc[2] - (-fee_daily)) < 1e-15
    assert (inv.index == rets.index).all()


def test_blend_risk_off_sums_to_one_and_caps() -> None:
    base = {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25}

    blended = blend_risk_off(base, "SPYINVSIM", 0.15)

    assert abs(sum(blended.values()) - 1.0) < 1e-12
    assert blended["SPYINVSIM"] == 0.15
    assert abs(blended["ZROZSIM"] - 0.50 * 0.85) < 1e-12

    # f=0 reproduces the base sleeve exactly (sanity-check contract).
    assert blend_risk_off(base, "SPYINVSIM", 0.0) == base

    with pytest.raises(ValueError):
        blend_risk_off(base, "SPYINVSIM", -0.01)
    with pytest.raises(ValueError):
        blend_risk_off(base, "SPYINVSIM", 0.26)


def test_crisis_window_stats_on_toy_series() -> None:
    idx = pd.bdate_range("2020-02-19", "2020-03-23")
    rets = pd.Series(-0.01, index=idx)

    stats = crisis_window_stats(rets, [("covid", "2020-02-19", "2020-03-23")])

    n = len(idx)
    expected_ret = (1.0 - 0.01) ** n - 1.0
    assert abs(stats["crisis_covid_ret"] - expected_ret) < 1e-12
    # Monotonic decline -> peak is the first day's equity, so the window MDD
    # spans n-1 further down-days (negative).
    expected_mdd = (1.0 - 0.01) ** (n - 1) - 1.0
    assert abs(stats["crisis_covid_mdd"] - expected_mdd) < 1e-12


def test_crisis_window_stats_outside_window_is_nan() -> None:
    idx = pd.bdate_range("1990-01-01", periods=10)
    rets = pd.Series(0.001, index=idx)

    stats = crisis_window_stats(rets, [("covid", "2020-02-19", "2020-03-23")])

    assert np.isnan(stats["crisis_covid_ret"])
    assert np.isnan(stats["crisis_covid_mdd"])
