from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lrs.phases.phase06b_vol_target_continuous.run import (
    continuous_leverage_series,
    ladder_weights_any,
)


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("1990-01-01", periods=n)


def _branch() -> dict[str, str]:
    return {"branch": "SPY", "underlying": "SPYSIM", "lev2": "SSOSIM", "lev3": "UPROSIM"}


def test_leverage_caps_at_lmax_when_sigma_target_huge() -> None:
    rng = np.random.default_rng(0)
    rets = pd.Series(0.01 * rng.standard_normal(300), index=_days(300))

    lev = continuous_leverage_series(rets, rv_window=21, sigma_target=100.0, l_max=2.0)

    # After RV warmup the scalar is astronomically high -> always capped.
    assert (lev.iloc[30:] == 2.0).all()
    assert lev.min() >= 0.0


def test_leverage_floors_at_zero_and_quantizes() -> None:
    rng = np.random.default_rng(1)
    rets = pd.Series(0.01 * rng.standard_normal(500), index=_days(500))

    lev = continuous_leverage_series(rets, rv_window=21, sigma_target=0.10, l_max=2.0)

    assert lev.min() >= 0.0
    assert lev.max() <= 2.0
    # Every held level sits on the 0.25 ladder grid.
    remainders = (lev / 0.25) - (lev / 0.25).round()
    assert remainders.abs().max() < 1e-9


def test_leverage_inertia_skips_small_changes() -> None:
    # Constant vol -> constant raw scalar -> exactly one move off the initial 0.
    rets = pd.Series([0.01, -0.01] * 250, index=_days(500), dtype=float)

    lev = continuous_leverage_series(rets, rv_window=21, sigma_target=0.16, l_max=2.0)

    changes = int((lev.diff().fillna(0.0).abs() > 1e-12).sum())
    assert changes == 1


def test_leverage_has_no_lookahead() -> None:
    rng = np.random.default_rng(2)
    base = 0.01 * rng.standard_normal(300)
    rets_a = pd.Series(base.copy(), index=_days(300))
    rets_b = pd.Series(base.copy(), index=_days(300))
    rets_b.iloc[-1] = 0.50  # shock today must not change today's leverage

    lev_a = continuous_leverage_series(rets_a, rv_window=21, sigma_target=0.20, l_max=2.0)
    lev_b = continuous_leverage_series(rets_b, rv_window=21, sigma_target=0.20, l_max=2.0)

    assert lev_a.iloc[-1] == lev_b.iloc[-1]


def test_ladder_weights_any_full_range() -> None:
    branch = _branch()
    for level in [0.0, 0.25, 0.50, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0]:
        weights = ladder_weights_any(branch, level)
        assert all(w > 0.0 for w in weights.values())
        if weights:
            assert abs(sum(weights.values()) - 1.0) < 1e-12
    # Below 1x the remainder sits in cash.
    half = ladder_weights_any(branch, 0.5)
    assert half == {"SPYSIM": 0.5, "CASHX": 0.5}
    # At exactly 2x the sleeve is pure 2x ETF (Phase 4 ladder).
    assert ladder_weights_any(branch, 2.0) == {"SSOSIM": 1.0}


def test_ladder_weights_any_rejects_out_of_range() -> None:
    branch = _branch()
    with pytest.raises(ValueError):
        ladder_weights_any(branch, -0.1)
    with pytest.raises(ValueError):
        ladder_weights_any(branch, 3.1)
