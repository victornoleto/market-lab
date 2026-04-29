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


def test_avuv_synth_formula():
    """AVUV = VBRSIM + (75bps/y / 252) per day."""
    from studies.long_term_portfolio.synths import factor_tilt_synth_returns

    vbr = pd.Series([0.01, 0.0, -0.005], index=pd.date_range("2024-01-02", periods=3, freq="B"))
    result = factor_tilt_synth_returns(vbr, tilt_premium_annual=0.0075)

    expected_day1 = 0.01 + 0.0075 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-8


def test_avdv_synth_formula():
    """AVDV = VSSSIM + (100bps/y / 252)."""
    from studies.long_term_portfolio.synths import factor_tilt_synth_returns

    vss = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    result = factor_tilt_synth_returns(vss, tilt_premium_annual=0.0100)

    expected = 0.01 + 0.0100 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_avem_synth_formula():
    """AVEM = VWOSIM + (125bps/y / 252)."""
    from studies.long_term_portfolio.synths import factor_tilt_synth_returns

    vwo = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    result = factor_tilt_synth_returns(vwo, tilt_premium_annual=0.0125)

    expected = 0.01 + 0.0125 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_avuv_synth_from_cache():
    """AVUV synth from VBRSIM cache: 1926+ window."""
    from studies.long_term_portfolio.synths import avuv_synth_returns_from_cache

    s = avuv_synth_returns_from_cache()
    assert s.index[0].year <= 1927
    assert len(s) > 25000


def test_avem_synth_from_cache_window():
    """AVEM synth from VWOSIM cache: 1994+ window (32y bottleneck)."""
    from studies.long_term_portfolio.synths import avem_synth_returns_from_cache

    s = avem_synth_returns_from_cache()
    assert s.index[0].year >= 1994
    assert s.index[0].year <= 1995


def test_spmo_synth_formula():
    """SPMO = SPYSIM + 0.60 * UMD_KF - (35bps/y / 252)."""
    from studies.long_term_portfolio.synths import momentum_synth_returns

    spy = pd.Series([0.01, 0.0], index=pd.date_range("2024-01-02", periods=2, freq="B"))
    umd = pd.Series([0.005, -0.001], index=pd.date_range("2024-01-02", periods=2, freq="B"))

    result = momentum_synth_returns(
        spy, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0035
    )

    expected_day1 = 0.01 + 0.60 * 0.005 - 0.0035 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-8


def test_idmo_synth_formula():
    """IDMO = VEASIM + 0.60 * UMD_KF - (60bps/y / 252)."""
    from studies.long_term_portfolio.synths import momentum_synth_returns

    vea = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    umd = pd.Series([0.005], index=pd.date_range("2024-01-02", periods=1, freq="B"))

    result = momentum_synth_returns(
        vea, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0060
    )

    expected = 0.01 + 0.60 * 0.005 - 0.0060 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_spmo_synth_no_free_lunch_check():
    """KILL #3: SPMO standalone Sharpe must be < 1.5 vs literature ~0.6-0.8."""
    from studies.long_term_portfolio.synths import spmo_synth_returns_from_cache

    spmo = spmo_synth_returns_from_cache()
    annualized_sharpe = spmo.mean() / spmo.std() * np.sqrt(252)
    assert annualized_sharpe < 1.5, f"SPMO standalone Sharpe {annualized_sharpe:.2f} > 1.5; synth broken (KILL #3)"
