from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lrs.lib.backtest import build_sma_signal
from lrs.lib.indicators import sma_ensemble_fraction


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("1990-01-01", periods=n)


def _trend_prices(n: int, seed: int = 0) -> pd.Series:
    rng = np.random.default_rng(seed)
    rets = 0.0005 + 0.01 * rng.standard_normal(n)
    return pd.Series(100.0 * np.exp(np.cumsum(rets)), index=_days(n))


def test_fraction_bounded_and_on_member_grid() -> None:
    prices = _trend_prices(800)
    windows = [100, 150, 200, 250, 300]

    frac = sma_ensemble_fraction(prices, windows)

    assert frac.min() >= 0.0
    assert frac.max() <= 1.0
    # Every value sits on the 1/N grid.
    remainders = (frac * len(windows)) - (frac * len(windows)).round()
    assert remainders.abs().max() < 1e-9


def test_degenerate_set_equals_build_sma_signal() -> None:
    prices = _trend_prices(700, seed=1)

    frac = sma_ensemble_fraction(prices, [200])
    binary = build_sma_signal(prices, 200)

    assert (frac.astype(bool) == binary).all()
    assert set(np.unique(frac.to_numpy())) <= {0.0, 1.0}


def test_fraction_has_no_lookahead() -> None:
    prices_a = _trend_prices(400, seed=2)
    prices_b = prices_a.copy()
    prices_b.iloc[-1] *= 2.0  # shock today must not change today's fraction

    frac_a = sma_ensemble_fraction(prices_a, [100, 200])
    frac_b = sma_ensemble_fraction(prices_b, [100, 200])

    assert frac_a.iloc[-1] == frac_b.iloc[-1]


def test_fraction_one_when_above_all_smas() -> None:
    # Strictly rising series: above every SMA after the longest warmup.
    prices = pd.Series(np.linspace(100.0, 200.0, 400), index=_days(400))

    frac = sma_ensemble_fraction(prices, [50, 100, 150])

    assert (frac.iloc[160:] == 1.0).all()
    # Warmup of the longest member maps to a partial (or zero) fraction, never NaN.
    assert not frac.isna().any()


def test_fraction_zero_on_warmup_and_downtrend() -> None:
    prices = pd.Series(np.linspace(200.0, 100.0, 400), index=_days(400))

    frac = sma_ensemble_fraction(prices, [50, 100])

    assert (frac == 0.0).all()


def test_empty_windows_rejected() -> None:
    with pytest.raises(ValueError):
        sma_ensemble_fraction(_trend_prices(300), [])
