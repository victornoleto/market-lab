"""Smoke tests for Phase 3.8 B5 — Faber 10-mo GTAA single-asset SPY.

Four smoke tests enforce the Phase 3.8-1 Wave 3 plan requirements:

1. ``test_b5_monthly_signal_no_lookahead`` — monthly SMA regime at bar
   t uses only data strictly before ``t``; execution is shifted to the
   first trading day after the signal month-end.
2. ``test_b5_single_asset_unleveraged_invariant`` — exposure is always
   0 or 1 (never 2x/3x), and no UPRO/SSO ever enters the weights.
3. ``test_b5_uses_shared_darf_helper`` — B5 imports/uses B1's helper
   identity (no re-implementation) and produces tax deduction on a
   profitable run.
4. ``test_b5_smoke_10y_run_turnover_below_3`` — a 10-year smoke run on
   a slow-drift synthetic SPY series yields < 3 regime switches per
   year (Faber low-turnover budget).

Citations
---------

* ``[phase3_7_literature_sprint §T3]`` — Faber 2007 canonical reference.
* ``[trading_evolved, p.211-212]`` — 10-month SMA filter thesis.
* ``[leverage_for_the_long_run, p.13-14]`` — SMA-200 ≈ SMA-10-month daily.
* ``[advances_fin_ml, p.31-34]`` — F2-alignment prev_weight × ret.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ai_trade.backtest.strategies import (
    phase3_8_b5_faber_gtaa_single as b5_mod,
)
from ai_trade.backtest.strategies.phase3_8_b5_faber_gtaa_single import (
    B5Config,
    compute_daily_regime,
    compute_monthly_regime,
    simulate_b5,
)


def _price_from_returns(r: pd.Series, start: float = 100.0) -> pd.Series:
    return (1.0 + r).cumprod() * start


def test_b5_monthly_signal_no_lookahead():
    """The monthly-variant regime at day ``t`` must be fit on data
    strictly through the **most recent past month-end**.

    Strategy of the test:

    1. Build a deterministic 4-year daily price series.
    2. Compute the monthly regime.
    3. For a sample of days strictly inside a month (not the month-end
       itself), verify that the active regime equals the regime
       computed from monthly closes ending at the **previous** month-end.
    4. Poison the future — zero out all data in a month AFTER an audit
       date ``t_audit`` and confirm the regime at ``t_audit`` is
       unchanged (no reliance on the future).
    """
    rng = np.random.default_rng(seed=7)
    n = 4 * 252 + 50  # ~4+ years of daily bars, long enough for 10-month warmup
    idx = pd.bdate_range("2015-01-02", periods=n)
    # Mildly drifty series with noise — enough to cross the 10-month SMA.
    drift = np.linspace(0, 0.5, n)
    noise = rng.standard_normal(n) * 0.008
    r = 0.00015 + 0.003 * np.sin(drift * 8.0) + noise
    returns = pd.Series(r, index=idx)
    price = _price_from_returns(returns)

    sma_months = 10
    regime = compute_monthly_regime(price, sma_months=sma_months)

    # Identify month-end positions.
    s = pd.Series(idx, index=idx)
    me = s.groupby([s.index.year, s.index.month]).last()
    me_idx = pd.DatetimeIndex(me.values).sort_values()
    monthly_close = price.reindex(me_idx)
    monthly_sma = monthly_close.rolling(
        window=sma_months, min_periods=sma_months
    ).mean()
    raw_me = (monthly_close > monthly_sma).astype(float).where(
        monthly_sma.notna(), other=np.nan
    )

    # For several days strictly inside a month, check the active
    # regime == raw_me at the **previous** month-end.
    sample_days = [
        idx[3 * 21 + 5],   # inside month 3
        idx[12 * 21 + 5],  # inside month 12
        idx[24 * 21 + 5],  # inside month 24 (post-warmup)
        idx[36 * 21 + 5],  # inside month 36
    ]
    for t in sample_days:
        prev_me = me_idx[me_idx < t]
        if len(prev_me) == 0:
            continue
        last_me = prev_me[-1]
        raw_val = raw_me.loc[last_me]
        if pd.isna(raw_val):
            # Still in warmup — regime must be 0.
            assert int(regime.loc[t]) == 0
            continue
        assert int(regime.loc[t]) == int(raw_val), (
            f"lookahead/alignment violation at t={t.date()}: "
            f"regime={int(regime.loc[t])} expected={int(raw_val)} "
            f"(from month-end {last_me.date()})"
        )

    # Poison-the-future test: poisoning data AFTER an audit day must not
    # change the regime at that audit day.
    t_audit = idx[30 * 21 + 5]  # month 30, mid-month
    returns_poisoned = returns.copy()
    # Find the month-end right after t_audit and poison everything from
    # the NEXT trading day onward.
    next_me = me_idx[me_idx >= t_audit]
    assert len(next_me) > 0
    poison_start_pos = idx.get_loc(t_audit) + 1
    returns_poisoned.iloc[poison_start_pos:] = -0.99  # catastrophe from next bar
    price_poisoned = _price_from_returns(returns_poisoned)
    regime_p = compute_monthly_regime(price_poisoned, sma_months=sma_months)

    # Regime at t_audit must be identical — it is set by the previous
    # month-end, which is strictly before t_audit.
    assert int(regime.loc[t_audit]) == int(regime_p.loc[t_audit]), (
        f"look-ahead detected: poisoning returns after {t_audit.date()} "
        f"changed regime at {t_audit.date()}"
    )


def test_b5_single_asset_unleveraged_invariant():
    """Exposure must be a {0, 1} series on any B5 run — UNLEVERAGED by
    construction. No UPRO/SSO weights, no scaling above 1.
    """
    rng = np.random.default_rng(seed=1)
    n = 3 * 252 + 50  # ~3+ years
    idx = pd.bdate_range("2018-01-02", periods=n)
    r = 0.0004 + rng.standard_normal(n) * 0.006
    returns = pd.Series(r, index=idx)
    price = _price_from_returns(returns)

    for rebal in ("monthly", "daily"):
        cfg = B5Config(sma_months=10, rebal=rebal, tax_rate=0.15)
        res = simulate_b5(returns, price, cfg)
        expo = res.exposure.astype(float)
        # Unleveraged invariant: exposure ∈ {0.0, 1.0} at every bar.
        uniq = np.unique(expo.to_numpy())
        allowed = np.array([0.0, 1.0])
        for u in uniq:
            assert u in allowed, (
                f"exposure outside {{0, 1}} detected for rebal={rebal!r}: "
                f"value={u}"
            )
        # Minimum & maximum bounds — must be tight.
        assert float(expo.min()) >= 0.0
        assert float(expo.max()) <= 1.0

        # Regime is also strictly binary.
        reg = res.regime.astype(int)
        assert set(np.unique(reg.to_numpy())).issubset({0, 1})


def test_b5_uses_shared_darf_helper():
    """B5 must reuse B1's ``apply_darf_year_end`` — zero code duplication.

    Both audit (import identity) and behavior (tax deduction on a
    profitable run).
    """
    from ai_trade.backtest.strategies import (
        phase3_8_b1_gayed_canonical as b1_mod,
    )

    # (1) Audit — same function object.
    assert b5_mod.apply_darf_year_end is b1_mod.apply_darf_year_end, (
        "B5 must import apply_darf_year_end from B1 — detected divergent "
        "function object (possible re-implementation)"
    )

    # (2) Behavior — profitable run pays DARF; no-tax run has higher
    # terminal equity.
    idx = pd.bdate_range("2018-01-02", "2022-12-31")
    n = len(idx)
    # Strongly positive drift so the regime stays mostly ON after
    # warmup, generating realized gains each year.
    r = np.full(n, 0.0006)
    returns = pd.Series(r, index=idx)
    price = _price_from_returns(returns)

    cfg = B5Config(sma_months=10, rebal="monthly", tax_rate=0.15)
    res = simulate_b5(returns, price, cfg)
    assert len(res.equity) == n
    assert res.cum_tax_pct > 0.0, (
        "profitable run must pay some DARF; "
        f"got cum_tax_pct={res.cum_tax_pct}"
    )

    cfg_notax = B5Config(sma_months=10, rebal="monthly", tax_rate=0.0)
    res_notax = simulate_b5(returns, price, cfg_notax)
    assert float(res_notax.equity.iloc[-1]) > float(res.equity.iloc[-1]), (
        "no-tax path must exceed taxed path on a profitable run"
    )


def test_b5_smoke_10y_run_turnover_below_3():
    """A slow-drift SPY-like series must yield < 3 monthly regime switches
    per year (Faber low-turnover budget; prompt halt threshold).
    """
    rng = np.random.default_rng(seed=42)
    n = 10 * 252
    idx = pd.bdate_range("2010-01-04", periods=n)
    # Mild trend with moderate noise; not pathological — this simulates
    # a realistic SPY-like low-turnover path with a couple of regime
    # changes over 10 years.
    t_axis = np.linspace(0, 2 * np.pi, n)
    r = 0.0003 + 0.002 * np.sin(t_axis) + rng.standard_normal(n) * 0.005
    returns = pd.Series(r, index=idx)
    price = _price_from_returns(returns)

    cfg = B5Config(sma_months=10, rebal="monthly", tax_rate=0.15)
    res = simulate_b5(returns, price, cfg)

    years = n / 252.0
    n_switches = int(res.switches.sum())
    switches_per_yr = n_switches / years
    assert switches_per_yr < 3.0, (
        f"B5 monthly-variant turnover must stay below 3/yr (Faber budget). "
        f"got {switches_per_yr:.2f}/yr over {years:.1f}y ({n_switches} switches)"
    )

    # Equity finite, positive, starts near 1.
    assert res.equity.isna().sum() == 0
    assert (res.equity > 0).all()
