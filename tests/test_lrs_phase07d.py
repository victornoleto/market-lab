from __future__ import annotations

import numpy as np
import pandas as pd

from lrs.phases.phase06b_vol_target_continuous.run import continuous_leverage_series
from lrs.phases.phase07d_vol_target_quadratic.run import quadratic_leverage_series


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("1990-01-01", periods=n)


def test_quadratic_caps_at_lmax_when_sigma_target_huge() -> None:
    rng = np.random.default_rng(0)
    rets = pd.Series(0.01 * rng.standard_normal(300), index=_days(300))

    lev = quadratic_leverage_series(rets, rv_window=21, sigma_target=100.0, l_max=2.0)

    assert (lev.iloc[30:] == 2.0).all()
    assert lev.min() >= 0.0


def test_quadratic_floors_at_zero_and_quantizes() -> None:
    rng = np.random.default_rng(1)
    rets = pd.Series(0.01 * rng.standard_normal(500), index=_days(500))

    lev = quadratic_leverage_series(rets, rv_window=21, sigma_target=0.10, l_max=2.0)

    assert lev.min() >= 0.0
    assert lev.max() <= 2.0
    remainders = (lev / 0.25) - (lev / 0.25).round()
    assert remainders.abs().max() < 1e-9


def test_quadratic_cuts_harder_than_linear_in_high_vol() -> None:
    # Realized vol ~32% > sigma_target 20%: scalar < 1, so squaring shrinks it.
    rng = np.random.default_rng(2)
    rets = pd.Series(0.02 * rng.standard_normal(600), index=_days(600))

    lin = continuous_leverage_series(rets, rv_window=21, sigma_target=0.20, l_max=3.0)
    quad = quadratic_leverage_series(rets, rv_window=21, sigma_target=0.20, l_max=3.0)

    assert quad.iloc[50:].mean() < lin.iloc[50:].mean()


def test_quadratic_has_no_lookahead() -> None:
    rng = np.random.default_rng(3)
    base = 0.01 * rng.standard_normal(300)
    rets_a = pd.Series(base.copy(), index=_days(300))
    rets_b = pd.Series(base.copy(), index=_days(300))
    rets_b.iloc[-1] = 0.50

    lev_a = quadratic_leverage_series(rets_a, rv_window=21, sigma_target=0.30, l_max=2.0)
    lev_b = quadratic_leverage_series(rets_b, rv_window=21, sigma_target=0.30, l_max=2.0)

    assert lev_a.iloc[-1] == lev_b.iloc[-1]
