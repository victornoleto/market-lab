"""Iter 041 — VIX-regime-conditional WEIGHTS on iter 037's 3-leg stack.

Mechanism::

    regime[t] = 1 if VIX_{t-1} < threshold else 0   (1=calm, 0=stress)

    pos_eq[t]  = calm_weights["eq_w"]   if regime[t]=1 else stress_weights["eq_w"]
    pos_bd[t]  = calm_weights["bd_w"]   if regime[t]=1 else stress_weights["bd_w"]
    pos_gld[t] = calm_weights["gld_w"]  if regime[t]=1 else stress_weights["gld_w"]

    gross[t] = pos_eq*r_eq + pos_bd*r_bd + pos_gld*r_gld
    cost[t]  = (|∆pos_eq| + |∆pos_bd| + |∆pos_gld|) * cost_bps_per_leg
    net[t]   = gross - cost

Difference from iter 038 (`apply_regime_lev_stack_3leg`):

    Iter 038 modulates a **scalar leverage** that scales the *same*
    base weights, so all three legs co-move proportionally with the
    regime. Iter 041 modulates a **per-leg weight vector**, so the
    legs move independently across regimes — equity is reduced 0.40
    while bond and gold are *increased* 0.15 each in stress. Total
    leverage stays in a tight band (1.50 calm vs 1.40 stress, all
    achieved through composition rather than scaling).

The 1-day VIX lag is structural: ``regime[t]`` uses ``VIX[t-1]``
(yesterday's close known at today's open) so this primitive is
causal and look-ahead free. Bar 0 has no "yesterday" — bootstrap
with VIX[0] (the standard convention; introduces at most one bar of
"current-bar" use of VIX, negligible in a 4000+ bar series, identical
to iter 038's convention).

When the calm and stress weights coincide, the function reduces to
iter 037's `apply_static_stack_3leg` (see TDD spec
`test_identity_reduction_when_calm_equals_stress`).

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
  with regime-conditional weight tilts at preserved leverage.
* `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching.
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (1-day shift).
* Whaley (2009), JPM 35(3), 98-105, DOI 10.3905/JPM.2009.35.3.098
  — VIX as ex-ante risk regime indicator.
* Bekaert-Hoerova (2014), J Econometrics 183(2), 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
* Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold strategic role.
* Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021 — orthogonality.
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


def apply_regime_weights_3leg(
    r_eq: pd.Series,
    r_bd: pd.Series,
    r_gld: pd.Series,
    vix: pd.Series,
    *,
    calm_weights: Mapping[str, float],
    stress_weights: Mapping[str, float],
    vix_threshold: float = 20.0,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    """Three-leg static stack with binary VIX-regime weight modulation.

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
        Calm weights apply when VIX_{t-1} < threshold; stress weights
        apply otherwise.
    vix_threshold : float
        VIX level dividing calm from stress regime. Default 20.0.
    cost_bps_per_leg : float
        Linear cost per unit per-leg ∆position. Default 2 bps.

    Returns
    -------
    (net, positions, scale, regime)
        ``net`` : pd.Series of net daily returns (after cost).
        ``positions`` : pd.DataFrame with columns ["EQ", "BD", "GLD"].
        ``scale`` : pd.Series of total gross exposure per bar.
        ``regime`` : pd.Series int 0/1 (1=calm, 0=stress). Built from
        VIX[t-1]; the first bar uses VIX[0] as fallback.

    Raises
    ------
    ValueError
        If any weight is negative, indices mismatch, or no bars overlap.
    """
    _validate_weights("calm_weights", calm_weights)
    _validate_weights("stress_weights", stress_weights)

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
        # Pre-history bars — fall back to threshold (regime=0 stress).
        vix_aligned = vix_aligned.fillna(vix_threshold)
    vix_lag = vix_aligned.shift(1)
    vix_lag.iloc[0] = vix_aligned.iloc[0]

    regime = (vix_lag < vix_threshold).astype(int)
    regime.name = "regime"

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
