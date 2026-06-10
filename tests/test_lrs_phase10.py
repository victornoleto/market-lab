from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lrs.phases.phase10_dip_leverage_ladder.run import dip_state


def _series(values: list[float]) -> pd.Series:
    return pd.Series(values, index=pd.bdate_range("2000-01-03", periods=len(values)), dtype=float)


def test_state_escalates_on_trigger_and_exits_at_ath() -> None:
    # 100 -> dips to 75 (-25%) -> recovers to 90 (-10%) -> new high 101.
    prices = _series([100, 90, 75, 80, 90, 95, 101, 102])

    state = dip_state(prices, trigger=0.20, exit_rule="ath")

    # Raw state: escalated from the -25% bar until (but not including) the new ATH bar.
    # Lagged one bar: True starting the bar AFTER the -25% close.
    assert not state.iloc[0] and not state.iloc[1] and not state.iloc[2]
    assert state.iloc[3] and state.iloc[4] and state.iloc[5] and state.iloc[6]
    assert not state.iloc[7]  # ATH was hit at bar 6 -> lagged exit at bar 7


def test_half_exit_leaves_earlier_than_ath() -> None:
    prices = _series([100, 75, 85, 92, 95, 99, 101])

    ath = dip_state(prices, trigger=0.20, exit_rule="ath")
    half = dip_state(prices, trigger=0.20, exit_rule="half")

    # -10% recovery level (half of 20%) is reached at 90+: bar 3 (92).
    assert half.sum() < ath.sum()
    assert not half.iloc[4]  # exited (lagged) once DD >= -10%
    assert ath.iloc[4]  # still in dip until the new ATH at bar 6


def test_no_lookahead_in_state() -> None:
    base = [100, 90, 79, 85, 88, 90]
    a = _series(base)
    b = _series(base)
    b.iloc[-1] = 200.0  # huge recovery today must not change today's state

    sa = dip_state(a, trigger=0.20, exit_rule="ath")
    sb = dip_state(b, trigger=0.20, exit_rule="ath")

    assert sa.iloc[-1] == sb.iloc[-1]


def test_never_triggers_when_threshold_above_max_dd() -> None:
    rng = np.random.default_rng(0)
    rets = 0.0005 + 0.005 * rng.standard_normal(500)
    prices = pd.Series(
        100.0 * np.exp(np.cumsum(rets)),
        index=pd.bdate_range("2000-01-03", periods=500),
    )
    # Max DD of this gentle series is far above -100%.
    state = dip_state(prices, trigger=1.00, exit_rule="ath")
    assert not state.any()


def test_unknown_exit_rule_rejected() -> None:
    prices = _series([100, 90, 80])
    with pytest.raises(ValueError):
        dip_state(prices, trigger=0.2, exit_rule="bogus")
