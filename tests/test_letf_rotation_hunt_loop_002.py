"""Tests for iter 002 dd_killswitch helpers."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import importlib.util
from pathlib import Path

ITER_DIR = Path(__file__).parent.parent / "studies" / "letf_rotation_hunt" / "loop_iterations" / "002-2026-05-09-on-vol-dd-killswitch"


def _load_module():
    spec = importlib.util.spec_from_file_location("dd_killswitch", ITER_DIR / "dd_killswitch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load_module()


def _make_drawdown_series(n_warmup: int = 260, n_drop: int = 10) -> tuple[pd.Series, pd.Series]:
    """Synthetic series: flat then sharp drop. Returns (prices, returns)."""
    flat = np.full(n_warmup, 100.0)
    drop = np.linspace(100.0, 70.0, n_drop)  # 30% drawdown over n_drop days
    prices = pd.Series(
        np.concatenate([flat, drop]),
        index=pd.bdate_range("2000-01-03", periods=n_warmup + n_drop),
    )
    rets = prices.pct_change().fillna(0.0)
    return prices, rets


def test_killswitch_inactive_during_flat_period(mod):
    prices, rets = _make_drawdown_series()
    flag = mod.vol_adjusted_dd_killswitch(prices, rets, x_sigma=4.0, peak_window=252)
    # During the first 260 flat days the switch must remain unarmed (=0)
    assert flag.iloc[:259].sum() == 0


def test_killswitch_fires_during_sharp_drop(mod):
    prices, rets = _make_drawdown_series()
    flag = mod.vol_adjusted_dd_killswitch(prices, rets, x_sigma=2.0, peak_window=252)
    # By the end of the drop the switch should have fired at least once
    assert flag.iloc[-3:].max() == 1.0


def test_killswitch_hysteresis_reentry(mod):
    """Once killed, the switch must NOT re-arm until DD < 0.5 * threshold.

    Build a realistic series: flat warmup, then a long drawdown that builds
    enough realised vol for the kill to fire, then a recovery that crosses
    the half-threshold rearm boundary.
    """
    rng = np.random.default_rng(42)
    n_warmup = 260
    # Phase 1: flat with tiny noise so realised vol is non-zero
    flat = 100.0 + rng.normal(0, 0.1, n_warmup)
    # Phase 2: gradual 30-day drawdown (~30% peak-to-trough)
    drop = np.linspace(100.0, 70.0, 30)
    # Phase 3: gradual 30-day recovery back to peak
    rec = np.linspace(70.0, 100.0, 30)
    prices = pd.Series(
        np.concatenate([flat, drop, rec]),
        index=pd.bdate_range("2000-01-03", periods=n_warmup + 60),
    )
    rets = prices.pct_change().fillna(0.0)
    flag = mod.vol_adjusted_dd_killswitch(prices, rets, x_sigma=2.0)
    # Switch must fire somewhere in the drawdown (phase 2)
    drawdown_phase = flag.iloc[n_warmup : n_warmup + 30]
    assert drawdown_phase.max() == 1.0
    # Switch must re-arm by the time prices recover near the peak
    final = flag.iloc[-1]
    assert final == 0.0


def test_absolute_pct_killswitch_threshold(mod):
    prices = pd.Series(
        np.concatenate([np.full(252, 100.0), [80.0, 70.0, 90.0, 95.0]]),
        index=pd.bdate_range("2000-01-03", periods=252 + 4),
    )
    flag_25 = mod.absolute_pct_dd_killswitch(prices, pct_threshold=0.25)
    flag_30 = mod.absolute_pct_dd_killswitch(prices, pct_threshold=0.30)
    # Price 80 → DD=20% (no fire @ 25%), price 70 → DD=30% (fires @ 25%, NOT @ 30%)
    assert flag_25.iloc[252] == 0.0
    assert flag_25.iloc[253] == 1.0
    # 30% threshold uses strict ">", so DD=30% does NOT fire
    assert flag_30.max() == 0.0


def test_killswitch_returns_zero_during_warmup(mod):
    """First peak_window days must be 0 (no rolling peak yet)."""
    prices, rets = _make_drawdown_series(n_warmup=260, n_drop=0)
    flag = mod.vol_adjusted_dd_killswitch(prices, rets, x_sigma=4.0, peak_window=252)
    assert (flag.iloc[:251] == 0.0).all()
