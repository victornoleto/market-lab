"""Smoke tests for Phase 3.7 H2.c — VIX term-structure regime rotation.

Invariants covered:

1. ``compute_vix_regime_signal`` produces a strict-past signal (the
   regime at day D cannot depend on close[D]).
2. ``simulate_h2_vix_term_structure`` runs end-to-end on a tiny
   synthetic fixture and produces a sane equity path + regime series.
3. Degenerate feed (monotonic VIXY) → regime always risk-on; result
   reduces to buy-and-hold SPY modulo costs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.phase3_7_h2_vix_term_structure import (
    H2VixTermConfig,
    compute_vix_regime_signal,
    simulate_h2_vix_term_structure,
)


def _make_series(values: list[float], start: str = "2020-01-02") -> pd.Series:
    idx = pd.bdate_range(start=start, periods=len(values))
    return pd.Series(values, index=idx, dtype=float, name="close")


def test_compute_vix_regime_signal_strict_past():
    """Regime at day t must not depend on close[t] — only close[t-1] & earlier."""
    vals = [100.0, 102.0, 101.0, 103.0, 99.0, 97.0, 95.0, 96.0, 94.0, 93.0]
    s = _make_series(vals)
    reg = compute_vix_regime_signal(s, lookback=3, threshold=0.0)
    # Warmup: lookback=3 + shift(1) means first 4 values are NaN.
    assert reg.iloc[:4].isna().all()
    # Day t=4 (index 4) reads close[t-1]=s[3]=103 and s[3-3]=s[0]=100.
    # trail_ret[3] = 103/100 - 1 = +0.03 > 0 → regime[4] = 0 (risk-off).
    assert reg.iloc[4] == 0.0
    # Day t=5 reads s[4]=99 and s[4-3]=s[1]=102; ret=99/102-1=-0.029 < 0 → on.
    assert reg.iloc[5] == 1.0
    # Monotonic feed DOWN → regime always risk-on for subsequent days.
    vals_down = [100.0 - i for i in range(20)]
    s_down = _make_series(vals_down)
    reg_down = compute_vix_regime_signal(s_down, lookback=5, threshold=0.0)
    # After warmup (first 6 NaN), every day the trailing 5d return is negative.
    assert (reg_down.iloc[6:] == 1.0).all()


def test_simulator_smoke_and_buy_hold_degenerate():
    """Tiny synthetic: monotonic VIXY DOWN → always risk-on → SPY buy-hold modulo costs."""
    rng = np.random.default_rng(0)
    n = 120
    # SPY path: random walk ~+8%/yr drift.
    spy_ret = rng.normal(8e-4, 1e-2, size=n)
    spy = pd.Series((1.0 + spy_ret).cumprod() * 400.0,
                    index=pd.bdate_range("2018-01-02", periods=n))
    tlt = pd.Series((1.0 + rng.normal(0.0, 5e-3, size=n)).cumprod() * 100.0,
                    index=spy.index)
    vixy_down = pd.Series(np.linspace(80.0, 40.0, n), index=spy.index)
    vxx_dummy = pd.Series(np.linspace(80.0, 40.0, n), index=spy.index)
    cfg = H2VixTermConfig(lookback=10, signal_feed="VIXY", long_asset="SPY",
                          tax_rate=0.0, spread_bps=0.0, commission_bps=0.0)
    res = simulate_h2_vix_term_structure(
        spy, tlt, vixy_down, vxx_dummy, cfg, sso_close=None
    )
    # Post-warmup, regime should be 1.0 uniformly.
    mask = res.regime.notna()
    assert (res.regime[mask] == 1.0).all()
    # No switches (all risk-on).
    assert res.n_switches == 0
    # Equity path must be finite and positive.
    assert res.equity.iloc[-1] > 0.0
    assert np.isfinite(res.equity).all()
    # Since tax/cost are 0 and we are 100% long SPY post-warmup, the
    # equity should track SPY closely (within 0.5% absolute). Not an
    # exact match because the first risk-on day uses ret from bar-0 →
    # bar-1 while the SPY buy-hold would start at bar-1.
    spy_post = spy.loc[res.regime[mask].index]
    spy_bh = float(spy_post.iloc[-1] / spy_post.iloc[0])
    assert res.equity.iloc[-1] == pytest.approx(spy_bh, rel=5e-3)


def test_simulator_switches_and_tlt_leg():
    """VIXY oscillation → regime flips → TLT leg used on risk-off days."""
    rng = np.random.default_rng(1)
    n = 200
    spy = pd.Series((1.0 + rng.normal(5e-4, 1e-2, size=n)).cumprod() * 400.0,
                    index=pd.bdate_range("2019-01-02", periods=n))
    # TLT delivers +50 bps/day on risk-off days (so we can distinguish from cash).
    tlt_ret = np.full(n, 5e-3)
    tlt = pd.Series((1.0 + tlt_ret).cumprod() * 100.0, index=spy.index)
    # Oscillating VIXY — up 10 days, down 10 days, repeat.
    vixy_vals = []
    cur = 80.0
    for i in range(n):
        if (i // 10) % 2 == 0:
            cur *= 1.01
        else:
            cur *= 0.99
        vixy_vals.append(cur)
    vixy = pd.Series(vixy_vals, index=spy.index)
    vxx = vixy.copy()
    cfg = H2VixTermConfig(lookback=5, signal_feed="VIXY", long_asset="SPY",
                          off_asset_return="TLT", tax_rate=0.0,
                          spread_bps=0.0, commission_bps=0.0)
    res = simulate_h2_vix_term_structure(spy, tlt, vixy, vxx, cfg)
    # Expect several regime switches + positive long_days AND off_days.
    assert res.n_switches > 2
    assert res.long_days > 0
    assert res.off_days > 0
    # Because off leg is positive every day, total return > pure SPY
    # losers (can't easily bound analytically; just assert finite + sane).
    assert np.isfinite(res.equity).all()
    assert res.equity.iloc[-1] > 0.0
