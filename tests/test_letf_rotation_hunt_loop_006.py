"""Tests for iter 006 (bond-ratevol-regime) helper module.

Validates rolling realised vol, rolling percentile rank, and the binary
ratevol regime gate against deterministic toy series.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = (
    Path(__file__).resolve().parents[1]
    / "studies/letf_rotation_hunt/runs/post_close/006-2026-05-09-bond-ratevol-regime"
)


def _load_rv_module():
    spec = importlib.util.spec_from_file_location(
        "iter006_rate_vol_gate", ITER_DIR / "rate_vol_gate.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RV = _load_rv_module()


def test_rolling_realised_vol_constant_returns_zero():
    n = 200
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    r = pd.Series(np.full(n, 0.001), index=idx)
    sigma = RV.rolling_realised_vol(r, window=60)
    valid = sigma.dropna()
    assert (valid.abs() < 1e-12).all()


def test_rolling_realised_vol_matches_pandas_std():
    n = 200
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(42)
    r = pd.Series(rng.normal(scale=0.01, size=n), index=idx)
    sigma = RV.rolling_realised_vol(r, window=60, annualise=False)
    expected = r.rolling(window=60, min_periods=60).std(ddof=1)
    pd.testing.assert_series_equal(sigma, expected, check_names=False)


def test_rolling_realised_vol_annualisation_factor():
    n = 200
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(7)
    r = pd.Series(rng.normal(scale=0.01, size=n), index=idx)
    raw = RV.rolling_realised_vol(r, window=60, annualise=False).dropna()
    ann = RV.rolling_realised_vol(r, window=60, annualise=True).dropna()
    ratio = (ann / raw).dropna()
    assert np.allclose(ratio, np.sqrt(252.0))


def test_rolling_realised_vol_invalid_window():
    r = pd.Series(np.random.default_rng(0).normal(size=100))
    with pytest.raises(ValueError, match="window"):
        RV.rolling_realised_vol(r, window=1)


def test_rolling_percentile_rank_warmup_nan():
    n = 100
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(0)
    s = pd.Series(rng.normal(size=n), index=idx)
    pct = RV.rolling_percentile_rank(s, window=30)
    assert pct.iloc[:29].isna().all()
    assert pct.iloc[29:].notna().all()


def test_rolling_percentile_rank_max_value_top():
    n = 100
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    s = pd.Series(np.arange(n, dtype=float), index=idx)  # strictly increasing
    pct = RV.rolling_percentile_rank(s, window=30).dropna()
    # Latest value of each rolling window is always the max → rank=1.0
    assert (pct == 1.0).all()


def test_rolling_percentile_rank_min_value_bottom():
    n = 100
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    s = pd.Series(-np.arange(n, dtype=float), index=idx)  # strictly decreasing
    pct = RV.rolling_percentile_rank(s, window=30).dropna()
    # Latest value of each rolling window is always the min → rank=0.0
    assert (pct == 0.0).all()


def test_ratevol_regime_gate_binary_output():
    n = 1500
    idx = pd.date_range("2018-01-01", periods=n, freq="B")
    rng = np.random.default_rng(11)
    r = pd.Series(rng.normal(scale=0.01, size=n), index=idx)
    gate = RV.ratevol_regime_gate(r, vol_window=60, pct_window=1260, threshold=0.80)
    valid = gate.dropna()
    assert set(valid.unique()).issubset({0.0, 1.0})


def test_ratevol_regime_gate_threshold_zero_one_invalid():
    r = pd.Series(np.random.default_rng(0).normal(size=100))
    with pytest.raises(ValueError, match="threshold"):
        RV.ratevol_regime_gate(r, threshold=0.0)
    with pytest.raises(ValueError, match="threshold"):
        RV.ratevol_regime_gate(r, threshold=1.0)


def test_ratevol_regime_gate_warmup_nan_until_pct_window_plus_vol_window():
    n = 1500
    idx = pd.date_range("2018-01-01", periods=n, freq="B")
    rng = np.random.default_rng(99)
    r = pd.Series(rng.normal(scale=0.01, size=n), index=idx)
    gate = RV.ratevol_regime_gate(r, vol_window=60, pct_window=1260, threshold=0.70)
    # sigma is first non-NaN at index vol_window-1 (=59). pct_rank needs
    # pct_window non-NaN sigmas → first non-NaN gate at index
    # (vol_window - 1) + (pct_window - 1) = vol_window + pct_window - 2.
    first_valid_idx = 60 + 1260 - 2
    assert gate.iloc[:first_valid_idx].isna().all()
    assert gate.iloc[first_valid_idx:].notna().all()
