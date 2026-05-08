"""Smoke tests for plot_helper.py — generates plot files; verifies no exceptions."""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def test_plot_equity_curves_generates_png(tmp_path):
    """Equity curves plot saves PNG without errors."""
    from studies.letf_rotation_hunt.plot_helper import plot_equity_curves

    dates = pd.date_range("2020-01-01", periods=200, freq="B")
    equity_curves = {
        "UPRO_SMA200": pd.Series(np.linspace(10000, 25000, 200), index=dates),
        "SPY 1× b&h": pd.Series(np.linspace(10000, 18000, 200), index=dates),
        "Gayed canon": pd.Series(np.linspace(10000, 22000, 200), index=dates),
    }

    out_path = tmp_path / "equity.png"
    plot_equity_curves(equity_curves, out_path, title="Test iter")

    assert out_path.exists()
    assert out_path.stat().st_size > 0
    assert out_path.stat().st_size < 200_000  # ≤ 200KB per spec §5.7


def test_plot_drawdown_curves(tmp_path):
    """Drawdown plot saves PNG."""
    from studies.letf_rotation_hunt.plot_helper import plot_drawdown_curves

    dates = pd.date_range("2020-01-01", periods=200, freq="B")
    rng = np.random.RandomState(42)
    equity_curves = {
        "Strategy": pd.Series(np.cumprod(1 + rng.normal(0.0005, 0.01, 200)) * 10000, index=dates),
    }

    out_path = tmp_path / "dd.png"
    plot_drawdown_curves(equity_curves, out_path, title="DD test")

    assert out_path.exists()
