from __future__ import annotations

import pandas as pd

from lrs.lib.indicators import (
    adx_close_only,
    adx_gate,
    clenow_gate,
    roc_gate,
    trend_hysteresis_gate,
)
from lrs.phases.phase03_sparse_risk_on_vote.run import build_filter_gate


def _idx(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2020-01-01", periods=n, freq="D")


def test_hysteresis_holds_through_shallow_dip_and_exits_below_band() -> None:
    # SMA(2) band 20%: enter when price > SMA, hold until price < SMA*0.8.
    prices = pd.Series([10.0, 10.0, 12.0, 11.0, 9.0, 5.0, 5.0], index=_idx(7))

    gate = trend_hysteresis_gate(prices, lookback=2, band=0.20)

    # raw state (same bar): [F,F,T,T,T,F,F] -> shift(1) for no lookahead.
    # t3 price 11 < SMA 11.5 but >= lower band 9.2 -> stays in trend (hysteresis).
    assert gate.tolist() == [False, False, False, True, True, True, False]


def test_hysteresis_no_entry_on_equality() -> None:
    prices = pd.Series([10.0, 10.0, 10.0, 10.0], index=_idx(4))

    gate = trend_hysteresis_gate(prices, lookback=2, band=0.10)

    assert gate.tolist() == [False, False, False, False]


def test_roc_gate_is_lagged_and_warmup_false() -> None:
    prices = pd.Series([1.0, 2.0, 3.0, 2.0, 2.0], index=_idx(5))

    gate = roc_gate(prices, lookback=2)

    # roc(2) = [NaN, NaN, +2.0, 0.0, -0.33]; >0 only at t2; shift(1) -> True at t3.
    assert gate.tolist() == [False, False, False, True, False]


def test_clenow_gate_true_for_clean_uptrend_false_for_downtrend() -> None:
    up = pd.Series([1.0, 2.0, 4.0, 8.0, 16.0], index=_idx(5))
    down = pd.Series([16.0, 8.0, 4.0, 2.0, 1.0], index=_idx(5))

    up_gate = clenow_gate(up, window=3)
    down_gate = clenow_gate(down, window=3)

    # score>0 from t2 on the log-linear uptrend; shift(1) -> True from t3.
    assert up_gate.tolist() == [False, False, False, True, True]
    assert down_gate.tolist() == [False, False, False, False, False]


def test_adx_high_for_monotonic_low_for_choppy() -> None:
    monotonic = pd.Series([float(i) for i in range(1, 9)], index=_idx(8))
    choppy = pd.Series([10.0, 11.0, 10.0, 11.0, 10.0, 11.0, 10.0, 11.0], index=_idx(8))

    adx_up = adx_close_only(monotonic, window=2)
    adx_chop = adx_close_only(choppy, window=2)

    # Pure one-directional moves -> +DI=100, -DI=0 -> DX=ADX=100.
    assert abs(float(adx_up.iloc[-1]) - 100.0) < 1e-6
    assert float(adx_chop.iloc[-1]) < float(adx_up.iloc[-1])


def test_adx_gate_is_lagged_boolean() -> None:
    monotonic = pd.Series([float(i) for i in range(1, 9)], index=_idx(8))

    gate = adx_gate(monotonic, window=2, threshold=20.0)

    assert gate.dtype == bool
    assert gate.iloc[0] == False  # noqa: E712 - warmup must be risk-off
    assert bool(gate.iloc[-1]) is True


def test_none_filter_gate_leaves_base_signal_unchanged() -> None:
    prices = pd.Series([1.0, 2.0, 3.0, 4.0], index=_idx(4))
    base_signal = pd.Series([False, True, True, False], index=prices.index)

    none_gate = build_filter_gate(prices, {"kind": "none"})

    assert none_gate.all()
    combined = base_signal & none_gate.reindex(prices.index).fillna(False).astype(bool)
    assert combined.tolist() == base_signal.tolist()
