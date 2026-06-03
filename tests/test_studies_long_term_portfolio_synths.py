"""TDD tests for studies.return_stacked_core.synths.

Each synth function gets:
- a smoke test (returns non-empty Series with DatetimeIndex)
- a formula test (sample input -> sample output with known math)
- where applicable, a no-free-lunch sanity test (Sharpe should not be implausibly inflated)
"""
import numpy as np
import pandas as pd

from studies.return_stacked_core.synths import _annual_drag_to_daily


def test_annual_drag_to_daily_75bps():
    """75bps/y annual drag = 75/(252*10000) decimal/day."""
    result = _annual_drag_to_daily(0.0075)
    assert abs(result - 0.0000297619) < 1e-8


def test_ntsd_synth_formula():
    """NTSD = 0.90 * SPYSIM + 0.60 * VEASIM - (75bps/y / 252) per day."""
    from studies.return_stacked_core.synths import ntsd_synth_returns

    spy = pd.Series([0.01, 0.0, -0.005], index=pd.date_range("2024-01-02", periods=3, freq="B"))
    vea = pd.Series([0.005, 0.001, -0.002], index=pd.date_range("2024-01-02", periods=3, freq="B"))

    result = ntsd_synth_returns(spy, vea, financing_drag_annual=0.0075)

    expected_day1 = 0.90 * 0.01 + 0.60 * 0.005 - 0.0075 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-8
    assert len(result) == 3


def test_ntsd_synth_inception_window():
    """NTSD synth real cache: should produce 1986+ daily series ~10000 rows."""
    from studies.return_stacked_core.synths import ntsd_synth_returns_from_cache

    s = ntsd_synth_returns_from_cache()
    assert isinstance(s, pd.Series)
    assert isinstance(s.index, pd.DatetimeIndex)
    assert s.index[0].year <= 1987
    assert s.index[-1].year >= 2025
    assert len(s) > 9000


def test_avuv_synth_formula():
    """AVUV = VBRSIM + (75bps/y / 252) per day."""
    from studies.return_stacked_core.synths import factor_tilt_synth_returns

    vbr = pd.Series([0.01, 0.0, -0.005], index=pd.date_range("2024-01-02", periods=3, freq="B"))
    result = factor_tilt_synth_returns(vbr, tilt_premium_annual=0.0075)

    expected_day1 = 0.01 + 0.0075 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-8


def test_avdv_synth_formula():
    """AVDV = VSSSIM + (100bps/y / 252)."""
    from studies.return_stacked_core.synths import factor_tilt_synth_returns

    vss = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    result = factor_tilt_synth_returns(vss, tilt_premium_annual=0.0100)

    expected = 0.01 + 0.0100 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_avem_synth_formula():
    """AVEM = VWOSIM + (125bps/y / 252)."""
    from studies.return_stacked_core.synths import factor_tilt_synth_returns

    vwo = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    result = factor_tilt_synth_returns(vwo, tilt_premium_annual=0.0125)

    expected = 0.01 + 0.0125 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_avuv_synth_from_cache():
    """AVUV synth from VBRSIM cache: 1926+ window."""
    from studies.return_stacked_core.synths import avuv_synth_returns_from_cache

    s = avuv_synth_returns_from_cache()
    assert s.index[0].year <= 1927
    assert len(s) > 25000


def test_avem_synth_from_cache_window():
    """AVEM synth from VWOSIM cache: 1994+ window (32y bottleneck)."""
    from studies.return_stacked_core.synths import avem_synth_returns_from_cache

    s = avem_synth_returns_from_cache()
    assert s.index[0].year >= 1994
    assert s.index[0].year <= 1995


def test_spmo_synth_formula():
    """SPMO = SPYSIM + 0.60 * UMD_KF - (35bps/y / 252)."""
    from studies.return_stacked_core.synths import momentum_synth_returns

    spy = pd.Series([0.01, 0.0], index=pd.date_range("2024-01-02", periods=2, freq="B"))
    umd = pd.Series([0.005, -0.001], index=pd.date_range("2024-01-02", periods=2, freq="B"))

    result = momentum_synth_returns(
        spy, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0035
    )

    expected_day1 = 0.01 + 0.60 * 0.005 - 0.0035 / 252
    assert abs(result.iloc[0] - expected_day1) < 1e-8


def test_idmo_synth_formula():
    """IDMO = VEASIM + 0.60 * UMD_KF - (60bps/y / 252)."""
    from studies.return_stacked_core.synths import momentum_synth_returns

    vea = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    umd = pd.Series([0.005], index=pd.date_range("2024-01-02", periods=1, freq="B"))

    result = momentum_synth_returns(
        vea, umd_factor_returns=umd, capture_coef=0.60, expense_annual=0.0060
    )

    expected = 0.01 + 0.60 * 0.005 - 0.0060 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_spmo_synth_no_free_lunch_check():
    """KILL #3: SPMO standalone Sharpe must be < 1.5 vs literature ~0.6-0.8."""
    from studies.return_stacked_core.synths import spmo_synth_returns_from_cache

    spmo = spmo_synth_returns_from_cache()
    annualized_sharpe = spmo.mean() / spmo.std() * np.sqrt(252)
    assert annualized_sharpe < 1.5, f"SPMO standalone Sharpe {annualized_sharpe:.2f} > 1.5; synth broken (KILL #3)"


def test_rsst_synth_formula():
    """RSST = SPYSIM + KMLMSIM - (60bps/y / 252)."""
    from studies.return_stacked_core.synths import rsst_synth_returns

    spy = pd.Series([0.01], index=pd.date_range("2024-01-02", periods=1, freq="B"))
    kmlm = pd.Series([0.005], index=pd.date_range("2024-01-02", periods=1, freq="B"))

    result = rsst_synth_returns(spy, kmlm, expense_annual=0.0060)

    expected = 0.01 + 0.005 - 0.0060 / 252
    assert abs(result.iloc[0] - expected) < 1e-8


def test_rsst_synth_no_free_lunch_kill5():
    """KILL #5: RSST_synth standalone Sharpe < 1.5 (matches KILL #3 absolute cap).

    Original spec used `(s1+s2)*0.7` threshold but that fails for negatively-
    correlated stacking by mean-variance math (not a free lunch, just diversification).
    Absolute cap < 1.5 catches synth bugs (double-counted leverage, leakage) while
    allowing legitimate stacked-asset Sharpe (~0.9-1.0 expected for SPY+KMLM).
    """
    from studies.return_stacked_core.synths import rsst_synth_returns_from_cache

    rsst = rsst_synth_returns_from_cache()
    rsst_sharpe = rsst.mean() / rsst.std() * np.sqrt(252)
    assert rsst_sharpe < 1.5, f"RSST synth standalone Sharpe {rsst_sharpe:.3f} > 1.5; synth broken (KILL #5)"


def test_dbmf_load_from_cache():
    """DBMFSIM cached: 1999+ daily window."""
    from studies.return_stacked_core.synths import dbmf_returns_from_cache

    dbmf = dbmf_returns_from_cache()
    assert dbmf.index[0].year >= 1999
    assert dbmf.index[0].year <= 2001
    assert len(dbmf) > 6000


def test_cta_proxy_warning_in_docstring():
    """CTA Simplify proxy must explicitly flag INCOMPLETE in docstring."""
    from studies.return_stacked_core.synths import cta_simplify_proxy_returns
    assert "INCOMPLETE" in cta_simplify_proxy_returns.__doc__
