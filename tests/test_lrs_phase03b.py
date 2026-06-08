from __future__ import annotations

import pandas as pd

from lrs.lib.backtest import build_sma_signal
from lrs.lib.indicators import ema_gate


def _idx(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2020-01-01", periods=n, freq="D")


def test_ema_gate_true_in_uptrend_lagged_and_warmup_false() -> None:
    # Strictly increasing prices: the EMA lags a rising series, so price sits
    # above its EMA at every valid bar. min_periods=span -> NaN warmup -> False;
    # raw bool then .shift(1) for no lookahead.
    prices = pd.Series([float(i) for i in range(1, 8)], index=_idx(7))  # 1..7

    gate = ema_gate(prices, span=3)

    # EMA(span=3, adjust=False, min_periods=3): valid from t2 (=2.25), price>EMA
    # from t2 on. raw = [F,F,T,T,T,T,T]; shift(1) -> [F,F,F,T,T,T,T].
    assert gate.dtype == bool
    assert gate.iloc[0] == False  # noqa: E712 - warmup must be risk-off
    assert gate.tolist() == [False, False, False, True, True, True, True]


def test_ema_gate_false_in_downtrend() -> None:
    prices = pd.Series([float(i) for i in range(8, 1, -1)], index=_idx(7))  # 8..2

    gate = ema_gate(prices, span=3)

    # A falling series sits below its EMA at every valid bar -> all risk-off.
    assert not gate.any()


def test_sma200_form_reproduces_base_sma_signal() -> None:
    # The SMA control form must dispatch to exactly build_sma_signal, so the
    # SMA200 rows reproduce the Phase 2/3A base signal byte-for-byte.
    from lrs.phases.phase03b_regime_signals.run import build_regime_gate

    prices = pd.Series([float(i) for i in range(1, 30)], index=_idx(29))
    gate = build_regime_gate(prices, {"kind": "sma", "lookback": 5})
    expected = build_sma_signal(prices, 5)

    pd.testing.assert_series_equal(gate, expected, check_names=False)


def test_hysteresis_replacement_extends_risk_on_below_sma() -> None:
    # As a REPLACEMENT gate, hysteresis can stay risk-on on a day the plain SMA
    # gate is risk-off (holding through a dip below the SMA but inside the band).
    # Phase 3A showed the AND framing made hysteresis identical to `none`; this
    # proves the replacement framing recovers the distinct behaviour.
    from lrs.lib.indicators import trend_hysteresis_gate

    prices = pd.Series([10.0, 10.0, 10.0, 13.0, 11.0, 11.0], index=_idx(6))
    sma_gate = build_sma_signal(prices, lookback=3)
    hyst = trend_hysteresis_gate(prices, lookback=3, band=0.20)

    assert (hyst & ~sma_gate).any()
    # at the dip bar (t5) hysteresis holds risk-on while the SMA gate drops out.
    assert bool(hyst.iloc[5]) is True
    assert bool(sma_gate.iloc[5]) is False


def test_build_regime_gate_unknown_kind_raises() -> None:
    from lrs.phases.phase03b_regime_signals.run import build_regime_gate

    prices = pd.Series([1.0, 2.0, 3.0], index=_idx(3))
    try:
        build_regime_gate(prices, {"kind": "nope"})
    except ValueError as exc:
        assert "regime form" in str(exc)
    else:  # pragma: no cover - the call must raise
        raise AssertionError("expected ValueError for unknown regime kind")
