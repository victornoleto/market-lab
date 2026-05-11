"""TDD tests for iter 011 — conditional TQQQ leverage upgrade.

Verifies the new helper `conditional_leg.py`:
  - upgrade_signal_K4 (vote count = 4 of {SMA250, SMA100, vol<40%, AR1>0})
  - upgrade_signal_lowvol25 (vol_21d trailing-5y percentile < 0.25)
  - build_conditional_strategy_returns (QLD/TQQQ swap conditional on upgrade)

Citations
---------
- [leverage_for_the_long_run, ch.4-5, p.40-60] LRS leverage scaling.
- [stocks_on_the_move, p.98] Clenow trend-strength filter (K=4).
- [volatility_trading, p.58-60] Sinclair vol cone (low percentile = pump
  leverage).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = (
    Path("studies/letf_rotation_hunt/runs/post_close/")
    / "011-2026-05-10-conditional-tqqq-leverage"
)


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cleg():
    return _load_module(ITER_DIR / "conditional_leg.py", "iter011_cleg")


def _make_synth_series(n_days: int = 2000, seed: int = 42) -> pd.Series:
    rng = np.random.default_rng(seed)
    daily_log_ret = rng.normal(0.0005, 0.012, size=n_days)
    prices = np.exp(np.cumsum(daily_log_ret))
    idx = pd.bdate_range("2010-01-01", periods=n_days)
    return pd.Series(prices, index=idx, name="SYNTH")


def test_upgrade_signal_K4_returns_binary(cleg):
    prices = _make_synth_series(1500)
    returns = prices.pct_change().dropna()
    sig = cleg.upgrade_signal_K4(prices, returns)
    valid = sig.dropna()
    assert set(valid.unique()).issubset({0.0, 1.0})


def test_upgrade_signal_K4_warmup_is_nan(cleg):
    prices = _make_synth_series(1500)
    returns = prices.pct_change().dropna()
    sig = cleg.upgrade_signal_K4(prices, returns)
    # First 250 bars are warmup (longest of {SMA250, SMA100, vol_21d, AR1_30d})
    head = sig.iloc[:249]
    assert head.isna().all()


def test_upgrade_signal_K4_strictly_subset_of_K2(cleg):
    """K=4 should always be a (non-strict) subset of K=2 — when all 4 are
    bullish (K=4 ON), at least 2 are bullish (K=2 ON).
    """
    prices = _make_synth_series(2000)
    returns = prices.pct_change().dropna()
    k4 = cleg.upgrade_signal_K4(prices, returns)
    k2 = cleg.entry_signal_K2(prices, returns)
    aligned = pd.concat({"k4": k4, "k2": k2}, axis=1).dropna()
    # Where K4=1 we must have K2=1.
    k4_on_with_k2_off = aligned[(aligned["k4"] == 1.0) & (aligned["k2"] == 0.0)]
    assert len(k4_on_with_k2_off) == 0


def test_upgrade_signal_lowvol25_returns_binary(cleg):
    returns = _make_synth_series(2500).pct_change().dropna()
    sig = cleg.upgrade_signal_lowvol25(returns)
    valid = sig.dropna()
    assert set(valid.unique()).issubset({0.0, 1.0})


def test_upgrade_signal_lowvol25_warmup_is_nan(cleg):
    returns = _make_synth_series(2500).pct_change().dropna()
    sig = cleg.upgrade_signal_lowvol25(returns, vol_window=21, pct_window=1260)
    # warmup = vol_window + pct_window - 1 ≈ 1280 bars; first 1259 must be NaN
    head = sig.iloc[:1258]
    assert head.isna().all()


def test_upgrade_signal_lowvol25_fires_about_25pct(cleg):
    returns = _make_synth_series(3500, seed=7).pct_change().dropna()
    sig = cleg.upgrade_signal_lowvol25(returns, vol_window=21, pct_window=1260)
    post_warmup = sig.dropna()
    assert len(post_warmup) > 1000, "synth needs enough post-warmup samples"
    # The lowest 25% of trailing-5y rolling sigma should fire ~25% of the time
    # in a stationary GBM. Tolerance ±10pp for finite sample.
    fired_pct = float((post_warmup == 1.0).mean())
    assert 0.15 <= fired_pct <= 0.35, f"lowvol25 fired {fired_pct:.1%}, expected ~25%"


def test_build_conditional_returns_qld_when_upgrade_off(cleg):
    n = 500
    idx = pd.bdate_range("2015-01-01", periods=n)
    on_signal = pd.Series([1.0] * n, index=idx)
    qld_ret = pd.Series(np.linspace(0.001, 0.002, n), index=idx)
    tqqq_ret = pd.Series(np.linspace(0.003, 0.004, n), index=idx)
    upgrade = pd.Series([0.0] * n, index=idx)
    off_ret = pd.Series([0.0] * n, index=idx)

    result = cleg.build_conditional_strategy_returns(
        on_signal=on_signal,
        qld_returns=qld_ret,
        tqqq_returns=tqqq_ret,
        off_returns=off_ret,
        upgrade_gate=upgrade,
    )
    # Lag-1: result.iloc[1:] should equal qld_ret.iloc[1:]
    np.testing.assert_array_almost_equal(result.iloc[1:].values, qld_ret.iloc[1:].values)


def test_build_conditional_returns_tqqq_when_upgrade_on(cleg):
    n = 500
    idx = pd.bdate_range("2015-01-01", periods=n)
    on_signal = pd.Series([1.0] * n, index=idx)
    qld_ret = pd.Series(np.linspace(0.001, 0.002, n), index=idx)
    tqqq_ret = pd.Series(np.linspace(0.003, 0.004, n), index=idx)
    upgrade = pd.Series([1.0] * n, index=idx)
    off_ret = pd.Series([0.0] * n, index=idx)

    result = cleg.build_conditional_strategy_returns(
        on_signal=on_signal,
        qld_returns=qld_ret,
        tqqq_returns=tqqq_ret,
        off_returns=off_ret,
        upgrade_gate=upgrade,
    )
    np.testing.assert_array_almost_equal(result.iloc[1:].values, tqqq_ret.iloc[1:].values)


def test_build_conditional_returns_off_when_on_signal_zero(cleg):
    n = 500
    idx = pd.bdate_range("2015-01-01", periods=n)
    on_signal = pd.Series([0.0] * n, index=idx)
    qld_ret = pd.Series([0.001] * n, index=idx)
    tqqq_ret = pd.Series([0.002] * n, index=idx)
    off_ret = pd.Series([0.0005] * n, index=idx)
    upgrade = pd.Series([1.0] * n, index=idx)  # upgrade ON but on_signal OFF

    result = cleg.build_conditional_strategy_returns(
        on_signal=on_signal,
        qld_returns=qld_ret,
        tqqq_returns=tqqq_ret,
        off_returns=off_ret,
        upgrade_gate=upgrade,
    )
    # Defensive: when on_signal=0, must route to off regardless of upgrade.
    np.testing.assert_array_almost_equal(result.iloc[1:].values, off_ret.iloc[1:].values)


def test_build_conditional_returns_signal_lag_1(cleg):
    """Same lag convention as iters 005/006/007/009/010: signals lagged 1 day."""
    n = 100
    idx = pd.bdate_range("2015-01-01", periods=n)
    # Switch upgrade from 0 to 1 at day 50
    upgrade = pd.Series([0.0] * 50 + [1.0] * 50, index=idx)
    on_signal = pd.Series([1.0] * n, index=idx)
    qld_ret = pd.Series([0.001] * n, index=idx)
    tqqq_ret = pd.Series([0.005] * n, index=idx)
    off_ret = pd.Series([0.0] * n, index=idx)

    result = cleg.build_conditional_strategy_returns(
        on_signal=on_signal,
        qld_returns=qld_ret,
        tqqq_returns=tqqq_ret,
        off_returns=off_ret,
        upgrade_gate=upgrade,
    )
    # Lag-1: upgrade flips 0→1 at index 50, so result switches to TQQQ
    # at index 51, not 50 (the upgrade decision evaluated at close of t-1
    # is applied at open of t).
    assert result.iloc[50] == pytest.approx(0.001)  # last day with upgrade-lag 0
    assert result.iloc[51] == pytest.approx(0.005)  # first day with upgrade-lag 1


def test_combine_AND_OR(cleg):
    n = 100
    idx = pd.bdate_range("2015-01-01", periods=n)
    a = pd.Series([0.0, 0.0, 1.0, 1.0] * 25, index=idx)
    b = pd.Series([0.0, 1.0, 0.0, 1.0] * 25, index=idx)
    expected_and = pd.Series([0.0, 0.0, 0.0, 1.0] * 25, index=idx)
    expected_or = pd.Series([0.0, 1.0, 1.0, 1.0] * 25, index=idx)
    pd.testing.assert_series_equal(cleg.combine_AND(a, b), expected_and, check_names=False)
    pd.testing.assert_series_equal(cleg.combine_OR(a, b), expected_or, check_names=False)


def test_combine_propagates_nan(cleg):
    idx = pd.date_range("2015-01-01", periods=4)
    a = pd.Series([np.nan, 1.0, 0.0, 1.0], index=idx)
    b = pd.Series([1.0, 1.0, np.nan, 0.0], index=idx)
    out_and = cleg.combine_AND(a, b)
    out_or = cleg.combine_OR(a, b)
    assert out_and.isna().tolist() == [True, False, True, False]
    assert out_or.isna().tolist() == [True, False, True, False]


def test_upgrade_signal_K4_reduces_to_zero_when_no_indicator_bullish(cleg):
    """A monotonic-down series should never have K=4 ON (vol may be low but
    SMA250 and SMA100 will be 0)."""
    n = 1500
    idx = pd.bdate_range("2010-01-01", periods=n)
    # Monotonic decline
    prices = pd.Series(np.exp(-np.linspace(0, 1, n)), index=idx)
    returns = prices.pct_change().dropna()
    sig = cleg.upgrade_signal_K4(prices, returns)
    post_warmup = sig.dropna()
    # In strict downtrend, SMA250 and SMA100 gates should be off (price < SMA),
    # so K=4 must always be 0 post-warmup.
    assert (post_warmup == 1.0).sum() == 0
