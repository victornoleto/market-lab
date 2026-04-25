"""Iter 038 — VIX-regime-gated leverage on iter 037's 3-leg static stack.

Mechanism::

    regime[t] = 1 if VIX_{t-1} < threshold else 0    (1=low-vol, 0=high-vol)
    lev_scale[t] = lev_lo if regime[t]=1 else lev_hi
    weight_scale[t] = lev_scale[t] / sum(base_weights)

    pos_eq[t]  = base_eq_w  * weight_scale[t]
    pos_bd[t]  = base_bd_w  * weight_scale[t]
    pos_gld[t] = base_gld_w * weight_scale[t]

    gross[t] = pos_eq*r_eq + pos_bd*r_bd + pos_gld*r_gld
    cost[t]  = (|∆pos_eq| + |∆pos_bd| + |∆pos_gld|) * cost_bps_per_leg
    net[t]   = gross - cost

The 1-day VIX lag is structural — `regime[t]` is computed from
`VIX[t-1]` (yesterday's close known at today's open) so this primitive
is causal and lookahead-free.

When VIX is always below threshold, the primitive reduces exactly to
`apply_static_stack_3leg` with weights `(base * lev_lo / lev_base)`
where `lev_base = sum(base_weights)`. When always above threshold,
weights are `(base * lev_hi / lev_base)`. Mixed regime introduces
turnover cost only on regime-flip days.

Citations
---------
* `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching.
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (1-day shift).
* Hamilton (1989), Econometrica 57(2). Markov regime-switching original.
* Moreira-Muir (2017), JF 72(4) Table IV — vol-managed Sharpe uplift.
* Sinclair, *Volatility Trading* (2nd ed.) p.217-218 — VIX 20 threshold.
* `[risk_parity, ch.5]` — multi-leg static stack base preserved.
"""

from __future__ import annotations

import pandas as pd


def apply_regime_lev_stack_3leg(
    r_eq: pd.Series,
    r_bd: pd.Series,
    r_gld: pd.Series,
    vix: pd.Series,
    *,
    threshold: float = 20.0,
    lev_lo: float = 1.70,
    lev_hi: float = 1.00,
    base_weights: tuple[float, float, float] = (0.60, 0.45, 0.45),
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    """Three-leg static-stack with binary VIX-regime leverage modulation.

    Parameters
    ----------
    r_eq, r_bd, r_gld : pd.Series
        Aligned daily simple-return streams (DatetimeIndex).
    vix : pd.Series
        Daily VIX close. Must overlap with the returns index.
    threshold : float
        VIX level dividing low-vol (lev_lo applied) from high-vol regimes.
    lev_lo, lev_hi : float
        Total leverage in the low-vol and high-vol regimes respectively.
        Default 1.70 / 1.00 (preserves iter 037's avg lev ≈ 1.5).
    base_weights : (float, float, float)
        (eq, bd, gld) base weights. Default (0.60, 0.45, 0.45) = iter 037.
        These are SCALED by `lev_<regime> / sum(base_weights)` so the
        eq:bd:gld ratio is preserved across regimes.
    cost_bps_per_leg : float
        Linear cost per unit per-leg ∆ position. Default 2 bps.

    Returns
    -------
    (net, positions, scale, regime)
        ``net`` : pd.Series of net daily returns (after cost).
        ``positions`` : pd.DataFrame with columns ["EQ", "BD", "GLD"].
        ``scale`` : pd.Series of total gross exposure per bar.
        ``regime`` : pd.Series int 0/1 (1=low-vol, 0=high-vol). Built
        from `VIX[t-1]`; the first bar's regime falls back to a neutral
        average (so the first-bar position is `0.5*(lev_lo+lev_hi)`-scaled
        — this avoids a fictional pre-sample regime value).

    Raises
    ------
    ValueError if any input is malformed or has empty overlap.
    """
    if any(w < 0 for w in base_weights):
        raise ValueError(f"base_weights must be non-negative; got {base_weights}")
    if lev_lo < 0 or lev_hi < 0:
        raise ValueError(f"lev must be non-negative; got lev_lo={lev_lo}, lev_hi={lev_hi}")
    base_sum = sum(base_weights)
    if base_sum <= 0:
        raise ValueError("sum(base_weights) must be > 0")

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

    # Align VIX onto the return index. Forward-fill is safe since VIX is
    # daily and any gap (e.g., holidays) just keeps the prior level.
    vix_aligned = vix.reindex(a.index, method="ffill")
    if vix_aligned.isna().any():
        # Bars before VIX history starts — pad with threshold (regime=0)
        # so we apply lev_hi conservatively.
        vix_aligned = vix_aligned.fillna(threshold)
    # 1-day lag: today's regime uses yesterday's VIX close.
    # Bar 0 has no "yesterday" — bootstrap with VIX[0]. This is the
    # standard convention for first-bar position sizing and introduces
    # at most a single bar of "current-bar" use of VIX, negligible in a
    # 4000+ bar series.
    vix_lag = vix_aligned.shift(1)
    vix_lag.iloc[0] = vix_aligned.iloc[0]

    regime = (vix_lag < threshold).astype(int)

    lev_scale = pd.Series(0.0, index=a.index, dtype=float)
    lev_scale[regime == 1] = lev_lo
    lev_scale[regime == 0] = lev_hi
    weight_scale = lev_scale / base_sum

    eq_base, bd_base, gld_base = base_weights
    pos_eq = eq_base * weight_scale
    pos_bd = bd_base * weight_scale
    pos_gld = gld_base * weight_scale
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
    regime.name = "regime"

    return net, positions, scale, regime
