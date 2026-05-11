"""Mechanism-mix-diverse graded blend helper for iter 014.

Composes three orthogonal primitives onto the iter 022 winner architecture:

1. ON-leg type: single-asset (QLD or QLD/TQQQ swap on upgrade gate) OR
   multi-asset basket3 (invvol-weighted QLD/UPRO/UGL, with QLD↔TQQQ swap on
   upgrade gate).
2. Graded ON-blend cell (`[risk_parity, p.80-81, ch.4]` Qian RORO): when
   ratevol fires AND on_signal=ON, cell value is
   `gamma * alt_off + (1 - gamma) * on_leg`.
3. OFF-leg ratevol override (iter 006/007 primitive): when on_signal=OFF
   AND ratevol fires, route to alt-OFF (CASHX or IEFSIM); otherwise
   off_returns (ZROZ).

The three mechanisms operate on disjoint state cells per Carlson cap-
efficient stacking `[risk_parity, ch.5, p.10]`.

Calibration anchors at gamma=0:
- single-asset ON-leg with QLD only (no upgrade) ≡ iter 022 winner OFF=ZROZ
  baseline (Sortino 1.3240; iter 011-013 reference).
- single-asset ON-leg with K4_AND_lv25 upgrade + ratevol-OFF cashx
  ≡ iter 012 strict-superset (Sortino 1.3769).
- basket3 ON-leg (no upgrade) + ratevol-OFF cashx
  ≡ iter 007's `compound_basket3_x_ratevol_p70_cashx` (Sortino 1.4637 —
  4th-gen replica anchor across iters 007/008/009/010).

Citations
---------
- [risk_parity, p.80-81, ch.4]: Qian RORO graded master-gate (PRIMARY).
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking (PRIMARY).
- [stocks_on_the_move, p.98]: Clenow vol-parity sizing (basket invvol).
- [systematic_trading, ch.10]: Carver inverse-vol scalar.
- [volatility_trading, p.58-60]: Sinclair vol cone (ratevol gate).
- [leverage_for_the_long_run, ch.4-5, p.40-60]: Husson-Trifoni LRS leverage.
- [advances_fin_ml, p.208-211]: PBO via CSCV (mechanism-mix-diversity).
- [advances_fin_ml, p.222-223]: DSR cumulative n_trials.

Iter-local helper (`runs/post_close/014-.../`); does NOT modify shared modules.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_single_asset_on_leg(
    qld_returns: pd.Series,
    tqqq_returns: pd.Series,
    upgrade_gate: pd.Series,
) -> pd.Series:
    """Single-asset ON-leg with QLD↔TQQQ swap on upgrade gate.

    upgrade=1 → tqqq_returns ; upgrade=0 or NaN → qld_returns.
    Upgrade gate is lagged 1 day (computed t-1, applied at open of t —
    same convention as iter 011 conditional_leg).
    """
    upg_lag = upgrade_gate.shift(1)
    aligned = pd.concat({
        "q": qld_returns,
        "t": tqqq_returns,
        "u": upg_lag,
    }, axis=1).dropna(subset=["q", "t"])
    upg = aligned["u"].fillna(0.0)
    out = np.where(upg == 1.0, aligned["t"], aligned["q"])
    return pd.Series(out, index=aligned.index)


def _realised_vol(returns: pd.Series, window: int) -> pd.Series:
    return returns.rolling(window=window, min_periods=window).std() * np.sqrt(252.0)


def _invvol_weights(
    returns_by_asset: dict[str, pd.Series],
    window: int,
) -> pd.DataFrame:
    """Daily inverse-volatility weights (lagged 1 day on sigma).

    Mirrors `iter_005/basket_sizer.inverse_vol_weights` so basket3 g0
    reduces bit-exactly to iter 007 anchor.
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


def build_basket3_on_leg(
    qld_returns: pd.Series,
    tqqq_returns: pd.Series,
    upro_returns: pd.Series,
    ugl_returns: pd.Series,
    upgrade_gate: pd.Series,
    invvol_window: int = 60,
) -> pd.Series:
    """Multi-asset basket3 ON-leg with QLD↔TQQQ swap on upgrade gate.

    When upgrade_gate (lagged) == 1: basket = invvol(TQQQ, UPRO, UGL).
    Else:                            basket = invvol(QLD, UPRO, UGL).

    invvol weights are computed on each composition independently with
    `min_periods=invvol_window` (matches iter 005/007 anchor convention).
    Daily basket return = Σ w_i(t) × r_i(t) selected by upgrade gate.

    Window-alignment policy:
      - upgrade gate is constant 0 (`none`): TQQQ-basket is NEVER referenced;
        return = QLD-basket index (matches iter 007 basket3 anchor exactly,
        which has no TQQQ dependency).
      - upgrade gate can fire: TQQQ-basket is computed; for rows where
        TQQQ-basket is NaN (pre-TQQQ inception), QLD-basket is used
        regardless of upgrade gate value (graceful degradation; preserves
        the early window). On rows where both are valid AND upgrade=1,
        swap to TQQQ-basket.

    At upgrade gate constant 0 this reduces to iter 007's basket3 bit-exactly
    (KILL_LOOP #6 anchor: 1.4637).
    """
    w_qld = _invvol_weights(
        {"QLD": qld_returns, "UPRO": upro_returns, "UGL": ugl_returns},
        window=invvol_window,
    )
    basket_qld = _basket_returns_from_weights(
        w_qld,
        {"QLD": qld_returns, "UPRO": upro_returns, "UGL": ugl_returns},
    )

    upg_lag = upgrade_gate.shift(1)
    upgrade_can_fire = bool((upg_lag.fillna(0.0) == 1.0).any())

    if not upgrade_can_fire:
        return basket_qld.dropna()

    w_tqqq = _invvol_weights(
        {"TQQQ": tqqq_returns, "UPRO": upro_returns, "UGL": ugl_returns},
        window=invvol_window,
    )
    basket_tqqq = _basket_returns_from_weights(
        w_tqqq,
        {"TQQQ": tqqq_returns, "UPRO": upro_returns, "UGL": ugl_returns},
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


def build_mechanism_mix_strategy_returns(
    on_signal: pd.Series,
    on_leg_returns: pd.Series,
    off_returns: pd.Series,
    alt_off_returns: pd.Series,
    ratevol_gate: pd.Series,
    gamma: float,
    use_off_override: bool,
    drop_on_signal_warmup: bool = False,
) -> pd.Series:
    """Strategy assembler: graded ON-blend × ratevol-OFF override.

    `on_leg_returns` is precomputed (handles single vs basket and any
    upgrade swap externally — see `build_single_asset_on_leg` /
    `build_basket3_on_leg`).

    Behavior matrix (signals lagged 1 day):

      on_state=ON, ratevol=0:                        on_leg_returns
      on_state=ON, ratevol=1 (graded ON-blend cell): gamma * alt_off + (1-gamma) * on_leg
      on_state=OFF, use_off_override=True, rv=1:     alt_off_returns
      on_state=OFF, use_off_override=True, rv=0:     off_returns
      on_state=OFF, use_off_override=False:          off_returns

    NaN handling: ratevol NaN treated as ratevol=0 (warmup → no override,
    no blend).

    `drop_on_signal_warmup`:
      False (default; matches iter 011/012/013 single-asset convention) →
        on_sig NaN rows treated as OFF state (defensive baseline). Preserves
        bit-exact replica anchor for baseline_qld_zroz (Sortino 1.3240).
      True (matches iter 007 basket3 convention) → drop rows where
        on_sig is NaN (no output during K=2 warmup). Preserves bit-exact
        replica anchor for basket3 g0 (iter 007 Sortino 1.4637).

    Reduces to:
      gamma=0, use_off_override=True, drop_on_signal_warmup=False
        → iter 011/012 single-asset compound state machine
      gamma=0, use_off_override=True, drop_on_signal_warmup=True
        → iter 007 basket3 compound state machine
      gamma=1, use_off_override=True   → iter 009 master-pure equivalent
      gamma in (0,1)                   → iter 010 graded master (extended)
    """
    if not (0.0 <= gamma <= 1.0):
        raise ValueError(f"gamma must be in [0, 1], got {gamma}")

    aligned = pd.concat({
        "on_sig": on_signal.shift(1),
        "rv": ratevol_gate.shift(1),
        "ret_on": on_leg_returns,
        "ret_off": off_returns,
        "ret_alt": alt_off_returns,
    }, axis=1).dropna(subset=["ret_on", "ret_off", "ret_alt"])

    on_state = aligned["on_sig"].fillna(0.0) == 1.0
    rv = aligned["rv"].fillna(0.0)

    out = pd.Series(0.0, index=aligned.index)

    on_clean = on_state & (rv != 1.0)
    on_blend = on_state & (rv == 1.0)
    out[on_clean] = aligned.loc[on_clean, "ret_on"]
    out[on_blend] = (
        gamma * aligned.loc[on_blend, "ret_alt"]
        + (1.0 - gamma) * aligned.loc[on_blend, "ret_on"]
    )

    off_state = ~on_state
    if use_off_override:
        off_normal = off_state & (rv != 1.0)
        off_override = off_state & (rv == 1.0)
        out[off_normal] = aligned.loc[off_normal, "ret_off"]
        out[off_override] = aligned.loc[off_override, "ret_alt"]
    else:
        out[off_state] = aligned.loc[off_state, "ret_off"]

    if drop_on_signal_warmup:
        out = out[aligned["on_sig"].notna()]

    return out


def mechanism_mix_turnover(
    on_signal: pd.Series,
    upgrade_gate: pd.Series,
    ratevol_gate: pd.Series,
    use_basket: bool,
    use_off_override: bool,
) -> float:
    """Annualised turnover from categorical-state transitions.

    State categories (5):
      0 = OFF (alt-off, when ratevol fired and use_off_override=True)
      1 = OFF (zroz, otherwise)
      2 = ON (qld-clean / qld-basket3, ratevol=0, upgrade=0)
      3 = ON (tqqq-clean / tqqq-basket3, ratevol=0, upgrade=1)
      4 = ON (blend cell, ratevol=1)

    Approximation: basket3 daily invvol re-weighting turnover NOT counted
    (matches iter 007 `compound_turnover` and iter 010 `graded_master_turnover`
    single-asset path conventions). `use_basket` is recorded to make the
    function signature explicit but does not change state count under this
    approximation.
    """
    on_lag = on_signal.shift(1).fillna(0.0)
    upg_lag = upgrade_gate.shift(1).fillna(0.0)
    rv_lag = ratevol_gate.shift(1).fillna(0.0)

    on_state = on_lag == 1.0
    rv_fired = rv_lag == 1.0
    on_blend = on_state & rv_fired
    on_clean = on_state & ~rv_fired
    on_tqqq = on_clean & (upg_lag == 1.0)
    on_qld = on_clean & (upg_lag != 1.0)
    off_state = ~on_state

    state = pd.Series(1, index=on_lag.index)  # default off-zroz
    if use_off_override:
        state[off_state & rv_fired] = 0
    state[on_qld] = 2
    state[on_tqqq] = 3
    state[on_blend] = 4

    flips = (state.diff().abs() > 0).astype(int)
    n_years = len(state) / 252.0
    if n_years <= 0:
        return 0.0
    return float(flips.sum() / n_years)
