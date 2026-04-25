"""Iter 043 — Hysteretic VIX-regime-conditional WEIGHTS on iter 041 stack.

Schmitt-trigger state machine over a lagged VIX series::

    state[t] = state[t-1]                                         # default
    if state[t-1] == calm and VIX[t-1] >= high_threshold:         # exit calm
        state[t] = stress
    if state[t-1] == stress and VIX[t-1] <  low_threshold:        # enter calm
        state[t] = calm

When ``low_threshold == high_threshold`` the engine reduces *exactly*
to iter 041's binary VIX gate (TDD spec
``test_identity_reduction_when_low_equals_high``). For
``low_threshold < high_threshold`` the regime persists inside the band
[low, high), so total crossings of the regime label fall by ~50% on
the 2004-2026 VIX path.

The 1-day VIX lag is structural: ``regime[t]`` uses ``VIX[t-1]``
(yesterday's close known at today's open) — see
``[advances_fin_ml, p.162-164]``.

Citations
---------
* `[advances_fin_ml, ch.17-18]` — regime detection with whipsaw cost.
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (the variance-penalty term that motivates this iteration).
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity
  framework (legs/weights identical to iter 041).
* Hamilton (1989), Econometrica 57(2), DOI 10.2307/1912559 —
  Markov regime-switching with state persistence.
* Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098.
* Bekaert-Hoerova (2014), J Econometrics 183(2), SSRN 2294327.
"""

from __future__ import annotations

from typing import Mapping

import pandas as pd


def _validate_weights(name: str, w: Mapping[str, float]) -> None:
    for k in ("eq_w", "bd_w", "gld_w"):
        if k not in w:
            raise ValueError(f"{name} missing key {k!r}; got {dict(w)}")
        if w[k] < 0:
            raise ValueError(
                f"{name} weights must be non-negative; got {k}={w[k]}"
            )


def _validate_thresholds(low: float, high: float) -> None:
    if not (low <= high):
        raise ValueError(
            f"low_threshold must be <= high_threshold; got low={low}, high={high}"
        )


def apply_regime_weights_hysteretic_3leg(
    r_eq: pd.Series,
    r_bd: pd.Series,
    r_gld: pd.Series,
    vix: pd.Series,
    *,
    calm_weights: Mapping[str, float],
    stress_weights: Mapping[str, float],
    low_threshold: float,
    high_threshold: float,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    """Three-leg static stack with hysteretic VIX-regime weight modulation.

    Parameters
    ----------
    r_eq, r_bd, r_gld : pd.Series
        Aligned daily simple-return streams (DatetimeIndex). Must share
        identical indices.
    vix : pd.Series
        Daily VIX close. Must overlap with the returns index; ffilled
        on the return calendar.
    calm_weights, stress_weights : Mapping[str, float]
        Dicts with keys "eq_w", "bd_w", "gld_w" and non-negative values.
        Calm weights apply when ``state == calm``; stress when ``stress``.
    low_threshold : float
        VIX level below which the state transitions stress → calm.
    high_threshold : float
        VIX level at/above which the state transitions calm → stress.
        Must satisfy ``low_threshold <= high_threshold``.
    cost_bps_per_leg : float
        Linear cost per unit per-leg ∆position. Default 2 bps.

    Returns
    -------
    (net, positions, scale, regime)
        ``net`` : pd.Series of net daily returns (after cost).
        ``positions`` : pd.DataFrame with columns ["EQ", "BD", "GLD"].
        ``scale`` : pd.Series of total gross exposure per bar.
        ``regime`` : pd.Series int 0/1 (1=calm, 0=stress). Built from
        VIX[t-1] under the Schmitt-trigger rule. Bar 0 bootstraps from
        VIX[0] vs the band midpoint.

    Raises
    ------
    ValueError
        If any weight is negative, low > high, indices mismatch, or no
        bars overlap.
    """
    _validate_weights("calm_weights", calm_weights)
    _validate_weights("stress_weights", stress_weights)
    _validate_thresholds(low_threshold, high_threshold)

    if not (r_eq.index.equals(r_bd.index) and r_eq.index.equals(r_gld.index)):
        raise ValueError(
            "return streams must share identical indices "
            f"(eq={len(r_eq)}, bd={len(r_bd)}, gld={len(r_gld)})"
        )

    a = r_eq.astype(float)
    b = r_bd.astype(float)
    c = r_gld.astype(float)
    rmask = a.notna() & b.notna() & c.notna()
    a = a.loc[rmask]
    b = b.loc[rmask]
    c = c.loc[rmask]
    if len(a) == 0:
        raise ValueError("no overlapping non-NaN bars across the three return streams")

    vix_aligned = vix.reindex(a.index, method="ffill")
    if vix_aligned.isna().any():
        # Pre-history bars — fall back to band midpoint (regime=0 stress
        # if midpoint < low, calm if > high; here defaults to high → stress).
        vix_aligned = vix_aligned.fillna(high_threshold)
    vix_lag = vix_aligned.shift(1)
    vix_lag.iloc[0] = vix_aligned.iloc[0]

    # Bootstrap state at bar 0 from VIX[0] vs band midpoint so that
    # low == high reduces exactly to iter 041's `< threshold` rule.
    midpoint = 0.5 * (low_threshold + high_threshold)
    initial_state = 1 if vix_lag.iloc[0] < midpoint else 0

    n = len(a)
    regime_arr = [0] * n
    state = initial_state
    for t in range(n):
        v = vix_lag.iloc[t]
        if state == 1 and v >= high_threshold:
            state = 0
        elif state == 0 and v < low_threshold:
            state = 1
        regime_arr[t] = state
    regime = pd.Series(regime_arr, index=a.index, name="regime", dtype=int)

    pos_eq = pd.Series(stress_weights["eq_w"], index=a.index, dtype=float)
    pos_bd = pd.Series(stress_weights["bd_w"], index=a.index, dtype=float)
    pos_gld = pd.Series(stress_weights["gld_w"], index=a.index, dtype=float)
    pos_eq.loc[regime == 1] = calm_weights["eq_w"]
    pos_bd.loc[regime == 1] = calm_weights["bd_w"]
    pos_gld.loc[regime == 1] = calm_weights["gld_w"]

    scale = pos_eq + pos_bd + pos_gld
    scale.name = "scale"

    gross = pos_eq * a + pos_bd * b + pos_gld * c

    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_bd = pos_bd.diff().abs().fillna(pos_bd.iloc[0])
    dpos_gld = pos_gld.diff().abs().fillna(pos_gld.iloc[0])
    cost = (dpos_eq + dpos_bd + dpos_gld) * cost_bps_per_leg

    net = (gross - cost).astype(float)
    net.name = "net"

    positions = pd.DataFrame(
        {"EQ": pos_eq, "BD": pos_bd, "GLD": pos_gld}, index=a.index,
    )
    return net, positions, scale, regime
