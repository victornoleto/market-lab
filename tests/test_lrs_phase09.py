from __future__ import annotations

import numpy as np
import pandas as pd

from lrs.phases.phase06b_vol_target_continuous.run import ladder_weights_any
from lrs.phases.phase07d_vol_target_quadratic.run import quadratic_leverage_series
from lrs.phases.phase09_vol_target_3x_ceiling.run import (
    L_MAXES,
    N_TRIALS_ADDED,
    N_TRIALS_LEDGER_BEFORE,
    WINNER_7D,
)


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("1990-01-01", periods=n)


def test_ledger_accounting() -> None:
    assert N_TRIALS_LEDGER_BEFORE == 4377
    assert N_TRIALS_ADDED == 48


def test_winner_bars_match_phase7d_survivors() -> None:
    assert WINNER_7D["SPY"] == {"sigma_target": 0.40, "rv_window": 21, "lag_days": 3, "l_max": 2.00}
    assert WINNER_7D["QQQ"] == {"sigma_target": 0.40, "rv_window": 21, "lag_days": 2, "l_max": 1.75}


def test_quadratic_series_respects_3x_ceiling() -> None:
    rng = np.random.default_rng(0)
    # Very calm series (~3% annualized vol): scalar >> 3 -> pinned at the cap.
    rets = pd.Series(0.002 * rng.standard_normal(400), index=_days(400))

    lev = quadratic_leverage_series(rets, rv_window=21, sigma_target=0.40, l_max=3.0)

    assert lev.max() <= 3.0
    assert (lev.iloc[30:] == 3.0).all()


def test_ladder_reaches_pure_3x_sleeve_at_cap() -> None:
    branch = {"branch": "SPY", "underlying": "SPYSIM", "lev2": "SSOSIM", "lev3": "UPROSIM"}
    for l_max in L_MAXES:
        weights = ladder_weights_any(branch, l_max)
        assert abs(sum(weights.values()) - 1.0) < 1e-12
    # At 3.0 the risk-on sleeve is pure 3x ETF (UPRO/TQQQ rung actually used).
    assert ladder_weights_any(branch, 3.0) == {"UPROSIM": 1.0}
    assert ladder_weights_any(branch, 2.5) == {"SSOSIM": 0.5, "UPROSIM": 0.5}
