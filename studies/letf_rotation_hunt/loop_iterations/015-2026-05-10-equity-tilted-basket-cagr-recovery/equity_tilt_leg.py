"""Equity-tilted basket ON-leg helpers for iter 015.

Contributes two new basket weighting primitives on top of iter 014's
``mechanism_mix_leg`` framework:

1. ``build_basket3_eqtilt_on_leg`` — fixed-weight 3-asset basket
   (QLD/UPRO/UGL with QLD↔TQQQ swap on upgrade gate). Caller specifies
   weights as a tuple ``(w_eq_primary, w_eq_secondary, w_gold)``. Default
   convention: 2/3 + 1/6 + 1/6 (basket3-eqtilt66) or 0.85/0.075/0.075
   (basket3-eqtilt85). Daily-rebalanced (matches iter 007/014 invvol
   convention).
2. ``build_basket2_invvol_on_leg`` — invvol-weighted 2-asset basket
   (QLD/UPRO with QLD↔TQQQ swap on upgrade gate). No gold sleeve;
   pure-equity ablation.

These complement (do NOT replace) iter 014's
``build_basket3_on_leg`` (invvol60 QLD/UPRO/UGL — preserves the 5-gen
calibration anchor at Sortino 1.4637 / 1.4689).

Citations
---------
- [risk_parity, p.110, ch.5]: Qian diversification return for fixed-weight
  rebalanced basket (PRIMARY for fixed-weight tilt).
- [risk_parity, p.11, ch.1]: Qian — naïve risk parity over-allocates to
  lowest-vol asset (motivates the equity-tilt fix).
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking (preserved).
- [stocks_on_the_move, p.98]: Clenow vol-parity (basket3-invvol contrast).

Iter-local helper (`loop_iterations/015-.../`); does NOT modify shared
modules.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _realised_vol(returns: pd.Series, window: int) -> pd.Series:
    return returns.rolling(window=window, min_periods=window).std() * np.sqrt(252.0)


def _invvol_weights(
    returns_by_asset: dict[str, pd.Series],
    window: int,
) -> pd.DataFrame:
    """Daily inverse-volatility weights (lagged 1 day on sigma).

    Mirrors ``iter_014/mechanism_mix_leg._invvol_weights`` and
    ``iter_005/basket_sizer.inverse_vol_weights`` so basket2 invvol
    semantics are bit-comparable to basket3 invvol.
    """
    assets = list(returns_by_asset.keys())
    aligned = pd.DataFrame({a: returns_by_asset[a] for a in assets})
    sigmas = pd.DataFrame(
        {a: _realised_vol(aligned[a], window) for a in assets}
    ).shift(1)
    inv = 1.0 / sigmas
    inv = inv.where(inv.notna() & np.isfinite(inv) & (inv > 0))
    row_sum = inv.sum(axis=1)
    weights = inv.div(row_sum, axis=0)
    weights = weights.where(row_sum.notna() & (row_sum > 0))
    return weights


def _basket_returns_from_weights(
    weights: pd.DataFrame,
    returns_by_asset: dict[str, pd.Series],
) -> pd.Series:
    assets = list(weights.columns)
    aligned_r = pd.DataFrame(
        {a: returns_by_asset[a] for a in assets}
    ).reindex(weights.index)
    w = weights.fillna(0.0)
    out = (w.values * aligned_r.values).sum(axis=1)
    s = pd.Series(out, index=weights.index)
    s[w.sum(axis=1) <= 0.0] = np.nan
    return s


def build_basket3_eqtilt_on_leg(
    qld_returns: pd.Series,
    tqqq_returns: pd.Series,
    upro_returns: pd.Series,
    ugl_returns: pd.Series,
    upgrade_gate: pd.Series,
    weights: tuple[float, float, float] = (2.0 / 3.0, 1.0 / 6.0, 1.0 / 6.0),
) -> pd.Series:
    """Fixed-weight basket3-eqtilt with QLD↔TQQQ swap on upgrade gate.

    Daily-rebalanced fixed-weight basket. When upgrade_gate (lagged 1 day) == 1
    the primary leg weight goes to TQQQ instead of QLD; UPRO and UGL legs
    are unchanged.

    Parameters
    ----------
    weights : (w_eq_primary, w_eq_secondary, w_gold)
        Must sum to 1.0 (validated). Defaults to (2/3, 1/6, 1/6) — the
        basket3-eqtilt66 hypothesis primary in iter 015.

    Returns
    -------
    pd.Series
        Daily basket return aligned to the union of valid (non-NaN) row index
        across all three legs (any NaN row drops).
    """
    if not np.isclose(sum(weights), 1.0, atol=1e-9):
        raise ValueError(f"weights must sum to 1.0, got {weights} sum={sum(weights)}")
    w_primary, w_secondary, w_gold = weights

    upg_lag = upgrade_gate.shift(1)
    aligned = pd.concat({
        "q": qld_returns,
        "t": tqqq_returns,
        "u": upro_returns,
        "g": ugl_returns,
        "up": upg_lag,
    }, axis=1).dropna(subset=["q", "u", "g"])

    upg = aligned["up"].fillna(0.0)
    primary = aligned["q"].copy()
    swap_mask = (upg == 1.0) & aligned["t"].notna()
    primary[swap_mask] = aligned.loc[swap_mask, "t"]

    out = (
        w_primary * primary.values
        + w_secondary * aligned["u"].values
        + w_gold * aligned["g"].values
    )
    return pd.Series(out, index=aligned.index)


def build_basket2_invvol_on_leg(
    qld_returns: pd.Series,
    tqqq_returns: pd.Series,
    upro_returns: pd.Series,
    upgrade_gate: pd.Series,
    invvol_window: int = 60,
) -> pd.Series:
    """Invvol-weighted basket2 (QLD/UPRO; no gold) with QLD↔TQQQ swap.

    When upgrade_gate (lagged) == 1: basket = invvol(TQQQ, UPRO).
    Else:                            basket = invvol(QLD, UPRO).

    Window-alignment policy mirrors iter 014's basket3 helper for cross-
    iter calibration: TQQQ-basket is only computed if upgrade gate can
    fire; for rows where TQQQ-basket is NaN (pre-TQQQ inception), QLD-
    basket is used regardless of upgrade gate value.

    Returns
    -------
    pd.Series
        Daily basket return; rows where QLD-basket is NaN (insufficient
        invvol warmup) are dropped.
    """
    w_qld = _invvol_weights(
        {"QLD": qld_returns, "UPRO": upro_returns},
        window=invvol_window,
    )
    basket_qld = _basket_returns_from_weights(
        w_qld, {"QLD": qld_returns, "UPRO": upro_returns},
    )

    upg_lag = upgrade_gate.shift(1)
    upgrade_can_fire = bool((upg_lag.fillna(0.0) == 1.0).any())

    if not upgrade_can_fire:
        return basket_qld.dropna()

    w_tqqq = _invvol_weights(
        {"TQQQ": tqqq_returns, "UPRO": upro_returns},
        window=invvol_window,
    )
    basket_tqqq = _basket_returns_from_weights(
        w_tqqq, {"TQQQ": tqqq_returns, "UPRO": upro_returns},
    )

    aligned = pd.concat({
        "q": basket_qld,
        "t": basket_tqqq,
        "u": upg_lag,
    }, axis=1).dropna(subset=["q"])
    upg = aligned["u"].fillna(0.0)
    out = aligned["q"].copy()
    swap_mask = (upg == 1.0) & aligned["t"].notna()
    out[swap_mask] = aligned.loc[swap_mask, "t"]
    return out
