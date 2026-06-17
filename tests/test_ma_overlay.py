"""MA entry/exit overlay primitives: stock_above_ma (SMA/EMA) + gate/stop exit logic."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for _c in (REPO_ROOT, REPO_ROOT / "src"):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from studies.momentum_v2.ma_overlay_test import _apply_exit  # noqa: E402
from studies.momentum_v2.overlays import stock_above_ma  # noqa: E402


def test_stock_above_ma_sma():
    idx = pd.date_range("2020-01-01", periods=5, freq="D")
    up = pd.DataFrame({"A": [10.0, 11, 12, 13, 14]}, index=idx)
    assert stock_above_ma(up, window_days=3, kind="sma")["A"].tolist() == [False, False, True, True, True]
    down = pd.DataFrame({"A": [14.0, 13, 12, 11, 10]}, index=idx)
    assert stock_above_ma(down, 3, "sma")["A"].tolist() == [False, False, False, False, False]


def test_stock_above_ma_ema_and_invalid_kind():
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    up = pd.DataFrame({"A": [10.0 + i for i in range(10)]}, index=idx)
    ok = stock_above_ma(up, window_days=3, kind="ema")
    assert ok["A"].dtype == bool and bool(ok["A"].iloc[-1]) is True  # rising -> above lagging EMA
    with pytest.raises(ValueError):
        stock_above_ma(up, 3, "wma")


def test_apply_exit_gate_vs_stop_single_segment():
    idx = pd.date_range("2020-01-01", periods=6, freq="D")
    dw = pd.DataFrame({"A": [1.0] * 6}, index=idx)
    ok = pd.DataFrame({"A": [True, True, False, True, True, False]}, index=idx)
    monthly_index = pd.DatetimeIndex([idx[0]])  # single holding segment
    assert _apply_exit(dw, ok, monthly_index, "gate")["A"].tolist() == [1, 1, 0, 1, 1, 0]  # re-enters
    assert _apply_exit(dw, ok, monthly_index, "stop")["A"].tolist() == [1, 1, 0, 0, 0, 0]  # latches


def test_apply_exit_stop_resets_at_rebalance():
    idx = pd.date_range("2020-01-01", periods=6, freq="D")
    dw = pd.DataFrame({"A": [1.0] * 6}, index=idx)
    ok = pd.DataFrame({"A": [True, True, False, True, False, True]}, index=idx)
    monthly_index = pd.DatetimeIndex([idx[0], idx[3]])  # rebalances at d0 and d3
    assert _apply_exit(dw, ok, monthly_index, "stop")["A"].tolist() == [1, 1, 0, 1, 0, 0]  # resets at d3
    assert _apply_exit(dw, ok, monthly_index, "gate")["A"].tolist() == [1, 1, 0, 1, 0, 1]


def test_apply_exit_invalid_mode():
    idx = pd.date_range("2020-01-01", periods=2, freq="D")
    dw = pd.DataFrame({"A": [1.0, 1.0]}, index=idx)
    ok = pd.DataFrame({"A": [True, True]}, index=idx)
    with pytest.raises(ValueError):
        _apply_exit(dw, ok, pd.DatetimeIndex([idx[0]]), "xxx")
