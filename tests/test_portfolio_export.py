"""Unit tests for the momentum_v2 portfolio export builders (synthetic data)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
for _c in (REPO_ROOT, REPO_ROOT / "src"):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from studies.momentum_v2.portfolio_export import (  # noqa: E402
    build_contribution,
    build_current,
    build_history,
    build_series,
)


def _rebalance_frame() -> pd.DataFrame:
    idx = pd.to_datetime(["2020-01-31", "2020-02-29", "2020-03-31"])
    return pd.DataFrame(
        [[0.5, 0.5, 0.0], [0.5, 0.0, 0.5], [1.0, 0.0, 0.0]],
        index=idx, columns=["A", "B", "C"],
    )


def test_current_is_last_rebalance_row():
    rw = _rebalance_frame()
    cur = build_current(rw)
    assert cur["as_of"] == "2020-03-31"
    assert cur["holdings"] == [{"ticker": "A", "weight": 1.0}]


def test_history_entries_and_exits():
    hist = build_history(_rebalance_frame())
    assert [h["date"] for h in hist] == ["2020-01-31", "2020-02-29", "2020-03-31"]
    assert hist[0]["entered"] == ["A", "B"] and hist[0]["exited"] == []
    assert hist[1]["entered"] == ["C"] and hist[1]["exited"] == ["B"]
    assert hist[2]["entered"] == [] and hist[2]["exited"] == ["C"]


def test_contribution_sums_to_arithmetic_total():
    idx = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])
    daily_w = pd.DataFrame([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]], index=idx, columns=["A", "B"])
    asset_ret = pd.DataFrame([[0.10, 0.20], [0.05, -0.10], [0.02, 0.03]], index=idx, columns=["A", "B"])
    contrib = build_contribution(daily_w, asset_ret)
    total = sum(c["contribution"] for c in contrib)
    expected = float((daily_w.shift(1).fillna(0.0) * asset_ret).sum(axis=1).sum())
    assert abs(total - expected) < 1e-12
    # A held days 1-2 (weight applies next day): day2 contrib = w_day1(1)*r_day2(0.05)=0.05;
    # day3 A weight from day2 (1)*r_day3(0.02)=0.02 -> A total 0.07
    a = next(c for c in contrib if c["ticker"] == "A")
    assert abs(a["contribution"] - 0.07) < 1e-12


def test_series_equity_is_cumprod_and_has_benchmark():
    idx = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])
    after = pd.Series([0.0, 0.10, -0.05], index=idx)
    gross = pd.Series([0.0, 0.12, -0.05], index=idx)
    bench = pd.Series([0.0, 0.01, 0.02], index=idx)
    df = build_series(after, gross, {"spy": bench})
    assert list(df.columns) == ["ret_after_tax", "equity_after_tax", "ret_gross", "equity_gross", "spy_ret", "spy_equity"]
    assert abs(df["equity_after_tax"].iloc[-1] - (1.10 * 0.95)) < 1e-12
    assert abs(df["spy_equity"].iloc[-1] - (1.01 * 1.02)) < 1e-12
