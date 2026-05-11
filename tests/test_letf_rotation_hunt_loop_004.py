"""Tests for iter 004 (corr-regime-stockbond) helper module.

Validates the rolling correlation indicator and the binary RORO gate against
deterministic toy series.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = (
    Path(__file__).resolve().parents[1]
    / "studies/letf_rotation_hunt/runs/post_close/004-2026-05-09-corr-regime-stockbond"
)


def _load_corr_module():
    spec = importlib.util.spec_from_file_location(
        "iter004_correlation_gate", ITER_DIR / "correlation_gate.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CORR = _load_corr_module()


def test_rolling_correlation_perfect_positive():
    n = 200
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(42)
    a = pd.Series(rng.normal(size=n), index=idx)
    rho = CORR.rolling_correlation(a, a, window=60)
    valid = rho.dropna()
    assert len(valid) == n - 59
    assert (valid > 0.999).all()


def test_rolling_correlation_perfect_negative():
    n = 200
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(7)
    a = pd.Series(rng.normal(size=n), index=idx)
    b = -a
    rho = CORR.rolling_correlation(a, b, window=60)
    valid = rho.dropna()
    assert (valid < -0.999).all()


def test_rolling_correlation_warmup_nan():
    n = 100
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(0)
    a = pd.Series(rng.normal(size=n), index=idx)
    b = pd.Series(rng.normal(size=n), index=idx)
    rho = CORR.rolling_correlation(a, b, window=30)
    assert rho.iloc[:29].isna().all()
    assert rho.iloc[29:].notna().all()


def test_corr_regime_gate_threshold_zero():
    n = 200
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(123)
    a = pd.Series(rng.normal(size=n), index=idx)
    gate = CORR.corr_regime_gate(a, a, threshold=0.0, window=60)
    valid = gate.dropna()
    assert (valid == 1.0).all()


def test_corr_regime_gate_threshold_high_no_fire():
    n = 200
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(321)
    a = pd.Series(rng.normal(size=n), index=idx)
    b = -a
    gate = CORR.corr_regime_gate(a, b, threshold=0.0, window=60)
    valid = gate.dropna()
    assert (valid == 0.0).all()


def test_corr_regime_gate_invalid_window():
    a = pd.Series(np.random.default_rng(0).normal(size=100))
    b = pd.Series(np.random.default_rng(1).normal(size=100))
    with pytest.raises(ValueError, match="window"):
        CORR.rolling_correlation(a, b, window=1)


def test_corr_regime_gate_warmup_nan_propagates():
    n = 100
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(55)
    a = pd.Series(rng.normal(size=n), index=idx)
    b = pd.Series(rng.normal(size=n), index=idx)
    gate = CORR.corr_regime_gate(a, b, threshold=0.5, window=30)
    assert gate.iloc[:29].isna().all()
