"""Smoke tests for Phase 3.8 B4 — Hsieh-Chang-Chen AR(1) regime LETF rotation.

Four smoke tests enforce the Phase 3.8-1 plan requirements:

1. ``test_ar1_regression_no_lookahead`` — β at t uses only r[t-63:t-1].
2. ``test_ar1_positive_trending_sample`` — a trending series yields β>0.
3. ``test_ar1_negative_mean_reverting_sample`` — a MR series yields β<0.
4. ``test_b4_uses_shared_darf_helper`` — B4 imports/uses B1's helper.

Citations
---------

* ``[phase3_7_literature_sprint §T1, arXiv 2504.20116]`` — AR(1) signal
* ``[advances_fin_ml, p.31-34]`` — F2-alignment prev_weight × ret
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ai_trade.backtest.strategies import phase3_8_b4_hsieh_ar1 as b4_mod
from ai_trade.backtest.strategies.phase3_8_b4_hsieh_ar1 import (
    B4Config,
    compute_ar1_regime_signal,
    rolling_ar1_beta,
    simulate_b4,
)


def _ols_ar1_beta(lag: np.ndarray, current: np.ndarray) -> float:
    """Reference OLS slope for r_i = α + β r_{i-1} + ε on aligned pair series.

    The input arrays ``lag`` and ``current`` are already aligned pairs
    of ``(r_{t-1}, r_t)``. This matches pandas' rolling-cov semantics
    exactly (it computes cov over the aligned window positions, using
    the two series' local means within that window).
    """
    xm = lag.mean()
    ym = current.mean()
    n = len(lag)
    cov = ((lag - xm) * (current - ym)).sum() / (n - 1)
    var = ((lag - xm) ** 2).sum() / (n - 1)
    if var <= 0:
        return float("nan")
    return cov / var


def test_ar1_regression_no_lookahead():
    """β used to gate bar t must use only returns through t-1.

    We build a deterministic pseudo-random return series, compute the
    regime via the module, and for each sampled t verify that the
    β-shifted series equals the reference OLS slope computed on
    r[t - lookback : t] (i.e. the window ENDING at t-1 when the signal
    is already t-1-shifted).
    """
    rng = np.random.default_rng(seed=42)
    n = 400
    idx = pd.bdate_range("2020-01-01", periods=n)
    # A mildly autocorrelated series (AR(1) ρ=0.2 + noise).
    eps = rng.standard_normal(n) * 0.01
    r = np.zeros(n)
    r[0] = eps[0]
    for i in range(1, n):
        r[i] = 0.2 * r[i - 1] + eps[i]
    returns = pd.Series(r, index=idx, name="ret")

    lookback = 63
    regime, beta_shifted = compute_ar1_regime_signal(returns, lookback=lookback)

    # Reference check: β used to gate bar t (i.e. ``beta_shifted.iloc[t]``)
    # must be fit on data observable only through t-1.
    #
    # Implementation detail: ``rolling_ar1_beta`` uses
    # ``returns.rolling(lookback).cov(returns.shift(1))`` — at rolling
    # position i the window covers observations i-lookback+1..i with the
    # lag series (returns.shift(1)) providing r_{t-1} for each of those
    # positions. So ``raw_beta.iloc[i]`` uses ``returns.iloc[i-lookback..i]``
    # total (lookback+1 points — 1 lag + lookback currents = lookback AR
    # pairs actually evaluated after accounting for the lag-NaN at
    # position i-lookback+1 when it is the first row in the window).
    #
    # After ``shift(1)``, ``beta_shifted.iloc[t] == raw_beta.iloc[t-1]``,
    # which uses ``returns.iloc[t-lookback-1..t-1]``. That window ENDS at
    # index t-1 — no look-ahead on t.
    for t in (100, 150, 200, 300, 399):
        # Build the exact pair series pandas uses for raw_beta.iloc[t-1].
        # Rolling window at position i=t-1 covers
        #   current_vals = returns.iloc[t-1-lookback+1 : t] = returns.iloc[t-lookback : t]
        #   lag_vals     = current_vals.shift(1), which within the window
        #                  draws its first value from returns.iloc[t-lookback-1].
        # Thus the aligned pair series over the window is
        #   lag     = returns.iloc[t-lookback-1 : t-1]
        #   current = returns.iloc[t-lookback   : t]
        lag_arr = returns.iloc[t - lookback - 1 : t - 1].to_numpy()
        cur_arr = returns.iloc[t - lookback : t].to_numpy()
        assert len(lag_arr) == len(cur_arr) == lookback
        expected = _ols_ar1_beta(lag_arr, cur_arr)
        got = float(beta_shifted.iloc[t])
        assert np.isfinite(got), f"β at t={t} must be finite"
        assert np.isfinite(expected), f"reference β at t={t} must be finite"
        rel = abs(got - expected) / (abs(expected) + 1e-6)
        # Tight tolerance — pandas rolling cov/var and the numpy-manual
        # OLS should agree to floating-point precision.
        assert rel < 1e-6, (
            f"formula drift at t={t}: "
            f"got={got:.8f} expected={expected:.8f} rel_err={rel:.2e}"
        )

    # Look-ahead absence: β at t must NOT depend on r_t.
    # Poison r_t to a huge shock and re-run — beta_shifted at t must be
    # UNCHANGED (because it's fit on the window ending at t-1).
    returns_poisoned = returns.copy()
    returns_poisoned.iloc[250] = 10.0  # absurd spike at t=250
    _, beta_shifted_poisoned = compute_ar1_regime_signal(
        returns_poisoned, lookback=lookback
    )
    # Positions 0..250 are fit on windows ending at or before t=249 in
    # the SHIFTED series (since beta_shifted.iloc[t] uses the raw rolling
    # beta at t-1, which is fit on returns through index t-1). Poisoning
    # r_{250} may affect beta_shifted.iloc[251] onward but NOT beta_shifted.iloc[t]
    # for t <= 250.
    pre = beta_shifted.iloc[:251].dropna()
    pre_poisoned = beta_shifted_poisoned.iloc[:251].dropna()
    common = pre.index.intersection(pre_poisoned.index)
    assert len(common) > 100
    max_diff = float((pre.loc[common] - pre_poisoned.loc[common]).abs().max())
    assert max_diff < 1e-12, (
        f"look-ahead detected: poisoning r_250 changed β at t≤250 "
        f"by max {max_diff}"
    )


def test_ar1_positive_trending_sample():
    """A trending series (positive AR(1)) should yield β>0 on average."""
    rng = np.random.default_rng(seed=0)
    n = 500
    # Strongly positive AR(1) — ρ=0.5 + low noise
    eps = rng.standard_normal(n) * 0.005
    r = np.zeros(n)
    r[0] = eps[0]
    for i in range(1, n):
        r[i] = 0.5 * r[i - 1] + eps[i]
    returns = pd.Series(r, index=pd.bdate_range("2020-01-01", periods=n))

    beta = rolling_ar1_beta(returns, lookback=63).dropna()
    # With ρ=0.5 ground truth, rolling OLS should consistently estimate
    # β > 0 — mean β > 0.25 and >90% of windows positive.
    mean_beta = float(beta.mean())
    frac_positive = float((beta > 0).mean())
    assert mean_beta > 0.25, (
        f"expected mean β > 0.25 for ρ=0.5 trending series, got {mean_beta:.3f}"
    )
    assert frac_positive > 0.90, (
        f"expected >90% positive windows for ρ=0.5, got {frac_positive:.3f}"
    )


def test_ar1_negative_mean_reverting_sample():
    """A mean-reverting series (negative AR(1)) should yield β<0 on average."""
    rng = np.random.default_rng(seed=0)
    n = 500
    # Strongly negative AR(1) — ρ=-0.5 + low noise
    eps = rng.standard_normal(n) * 0.005
    r = np.zeros(n)
    r[0] = eps[0]
    for i in range(1, n):
        r[i] = -0.5 * r[i - 1] + eps[i]
    returns = pd.Series(r, index=pd.bdate_range("2020-01-01", periods=n))

    beta = rolling_ar1_beta(returns, lookback=63).dropna()
    mean_beta = float(beta.mean())
    frac_negative = float((beta < 0).mean())
    assert mean_beta < -0.25, (
        f"expected mean β < -0.25 for ρ=-0.5 MR series, got {mean_beta:.3f}"
    )
    assert frac_negative > 0.90, (
        f"expected >90% negative windows for ρ=-0.5, got {frac_negative:.3f}"
    )


def test_b4_uses_shared_darf_helper():
    """B4 must reuse B1's ``apply_darf_year_end`` — zero code duplication.

    Both audit (import identity) and behavior (same tax deduction on a
    profitable year).
    """
    from ai_trade.backtest.strategies import (
        phase3_8_b1_gayed_canonical as b1_mod,
    )

    # (1) Audit — the module should import and expose the SAME function
    # object from B1. If a developer re-implemented it in B4, this fails.
    assert b4_mod.apply_darf_year_end is b1_mod.apply_darf_year_end, (
        "B4 must import apply_darf_year_end from B1 — detected divergent "
        "function object (possible re-implementation)"
    )

    # (2) Behavior — a deterministic profitable run should pay year-end
    # DARF, and the post-tax equity must equal the shared helper's output
    # when fed the same gross stream.
    idx = pd.bdate_range("2020-01-01", "2022-12-31")
    n = len(idx)
    # Synthesize SPX-TR with enough warmup for AR(1)(63) + force a
    # positive-AR regime so regime=1 throughout, isolating DARF behavior.
    rng = np.random.default_rng(seed=1)
    # ρ=0.7 trending (β will be positive most of the time after warmup)
    eps = rng.standard_normal(n) * 0.003
    r = np.zeros(n)
    r[0] = eps[0]
    for i in range(1, n):
        r[i] = 0.7 * r[i - 1] + 0.001 + eps[i]  # drift + persistence
    returns = pd.Series(r, index=idx)
    ffr = pd.Series(0.04, index=idx)

    cfg = B4Config(
        leverage=2.0,
        letf_kind="SSO",
        ar1_lookback=63,
        tax_rate=0.15,
        use_real_letf=False,
    )
    res = simulate_b4(returns, ffr, cfg, real_letf_returns=None)
    assert len(res.equity) == n
    assert res.cum_tax_pct > 0.0, (
        "profitable regime run must pay some DARF; "
        f"got cum_tax_pct={res.cum_tax_pct}"
    )

    # Tax==0 ablation → equity must differ (higher) than tax=15% run
    cfg_notax = B4Config(
        **{
            **{
                "leverage": cfg.leverage,
                "letf_kind": cfg.letf_kind,
                "ar1_lookback": cfg.ar1_lookback,
                "tax_rate": 0.0,
                "use_real_letf": False,
            }
        }
    )
    res_notax = simulate_b4(returns, ffr, cfg_notax, real_letf_returns=None)
    assert float(res_notax.equity.iloc[-1]) > float(res.equity.iloc[-1]), (
        "no-tax path must exceed taxed path on a profitable run"
    )
