"""TDD tests for studies.long_term_portfolio.synths.

Each synth function gets:
- a smoke test (returns non-empty Series with DatetimeIndex)
- a formula test (sample input -> sample output with known math)
- where applicable, a no-free-lunch sanity test (Sharpe should not be implausibly inflated)
"""
import numpy as np
import pandas as pd

from studies.long_term_portfolio.synths import _annual_drag_to_daily


def test_annual_drag_to_daily_75bps():
    """75bps/y annual drag = 75/(252*10000) decimal/day."""
    result = _annual_drag_to_daily(0.0075)
    assert abs(result - 0.0000297619) < 1e-8


def test_ntsd_synth_formula():
    """NTSD = 0.90 * SPYSIM + 0.60 * VEASIM - (75bps/y / 252) per day."""
    from studies.long_term_portfolio.synths import ntsd_synth_returns

    spy = pd.Series([0.01, 0.0, -0.005], index=pd.date_range("2024-01-02", periods=3, freq="B"))
    vea = pd.Series([0.005, 0.001, -0.002], index=pd.date_range("2024-01-02", periods=3, freq="B"))

    result = ntsd_synth_returns(spy, vea, financing_drag_annual=0.0075)

    expected_day1 = 0.90 * 0.01 + 0.60 * 0.005 - 0.0075 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-8
    assert len(result) == 3


def test_ntsd_synth_inception_window():
    """NTSD synth real cache: should produce 1986+ daily series ~10000 rows."""
    from studies.long_term_portfolio.synths import ntsd_synth_returns_from_cache

    s = ntsd_synth_returns_from_cache()
    assert isinstance(s, pd.Series)
    assert isinstance(s.index, pd.DatetimeIndex)
    assert s.index[0].year <= 1987
    assert s.index[-1].year >= 2025
    assert len(s) > 9000
