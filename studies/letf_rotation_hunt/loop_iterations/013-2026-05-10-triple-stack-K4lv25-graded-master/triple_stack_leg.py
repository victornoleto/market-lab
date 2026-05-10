"""Triple stack: K4_AND_lv25 leverage upgrade × graded master ON-blend × ratevol-OFF.

Iter 013 helper. Composes three mechanically-orthogonal lifts onto the iter 022
winner architecture:

1. ON-leg leverage upgrade (iter 011/012 primitive): substitute TQQQSIM for
   QLDSIM when upgrade gate fires (K=4 of 4 vote, optionally AND lowvol25).
   Operates only on the ON state cell.
2. ON-blend graded master (iter 010 primitive): when ratevol gate fires AND
   on_signal=ON, the cell value is `gamma * alt_off + (1 - gamma) * on_leg`,
   where `on_leg` is either QLD or TQQQ depending on the upgrade gate.
3. OFF-leg ratevol override (iter 006/007 primitive): when on_signal=OFF AND
   ratevol gate fires, substitute alt-OFF (CASHX or IEFSIM) for ZROZSIM.

The three mechanisms operate on disjoint state cells (gated by K=2 entry +
ratevol), so they compose additively per `[risk_parity, ch.5, p.10]` Carlson
cap-efficient stacking. Graded blend cell (`[risk_parity, p.80-81, ch.4]`
Qian RORO) is the iter 010 primitive that adds 2022_rates rescue.

At gamma=0, this helper is bit-exactly equivalent to iter 012's
`build_compound_strategy_returns(use_off_override=True)` — the
strict-superset replica anchor (slot 2 calibration check).

At gamma=1, this helper is the iter 009 master-pure equivalent under the
new triple-stack ON-leg (full alt-off override during ratevol+ON cell).

For gamma in (0, 1), the on-blend cell is a linear blend providing a graded
RORO master-gate.

Citations
---------
- [risk_parity, p.80-81, ch.4]: Qian RORO graded master-gate (PRIMARY).
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking (PRIMARY).
- [volatility_trading, p.58-60]: Sinclair vol cone (ratevol gate).
- [stocks_on_the_move, p.98]: Clenow trend-strength (K=4 vote).
- [leverage_for_the_long_run, ch.4-5, p.40-60]: Husson-Trifoni LRS leverage.
- [advances_fin_ml, p.208-211]: PBO via CSCV (G1).
- [advances_fin_ml, p.222-223]: DSR cumulative n_trials (n_global=504).

This helper is iter-local (`loop_iterations/013-.../`). It does NOT modify
any study-shared module per LOOP_PROTOCOL §"Scope limits".
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_triple_stack_strategy_returns(
    on_signal: pd.Series,
    qld_returns: pd.Series,
    tqqq_returns: pd.Series,
    off_returns: pd.Series,
    alt_off_returns: pd.Series,
    upgrade_gate: pd.Series,
    ratevol_gate: pd.Series,
    gamma: float,
    use_off_override: bool,
) -> pd.Series:
    """Triple stack: leverage upgrade × graded master ON-blend × ratevol-OFF.

    Behavior matrix (all signals lagged 1 day — same convention as iter
    007/010/011/012):

      on_state=ON, ratevol=0:
          upgrade=1 → tqqq_returns
          upgrade=0 → qld_returns
      on_state=ON, ratevol=1 (graded ON-blend cell):
          upgrade=1 → gamma * alt_off + (1-gamma) * tqqq_returns
          upgrade=0 → gamma * alt_off + (1-gamma) * qld_returns
      on_state=OFF, use_off_override=True:
          ratevol=1 → alt_off_returns
          ratevol=0 → off_returns
      on_state=OFF, use_off_override=False:
          → off_returns (regardless of ratevol)

    NaN handling: ratevol NaN treated as ratevol=0 (warmup → no override,
    no blend); upgrade NaN treated as upgrade=0 (warmup → no upgrade).

    Reduces to:
      gamma=0, use_off_override=True   → iter 012 build_compound_strategy_returns
      gamma=1, use_off_override=True   → iter 009 build_master_scope (extended)
      gamma in (0,1)                   → iter 010 graded master (extended w/upgrade)

    Parameters
    ----------
    on_signal:
        K=2 entry gate (exact iter 022 winner replica).
    qld_returns, tqqq_returns:
        Daily simple returns of QLDSIM and TQQQSIM (the leverage choices).
    off_returns:
        Daily simple returns of OFF leg (typically ZROZSIM).
    alt_off_returns:
        Daily simple returns of alt-OFF asset (CASHX or IEFSIM).
    upgrade_gate:
        Binary {0, 1, NaN}; 1 = use TQQQ during ON state.
    ratevol_gate:
        Binary {0, 1, NaN}; 1 = ZROZ vol percentile > threshold.
    gamma:
        Coefficient in [0, 1] for the ON-blend cell. gamma=0 disables the
        ON-blend cell (iter 012 compound replica); gamma=1 enables full
        master-scope override (iter 009 master replica with upgrade-gated
        ON-leg).
    use_off_override:
        If False, OFF state always uses off_returns regardless of ratevol.
        Affects only the OFF state cell, not the ON-blend cell.

    Returns
    -------
    pd.Series
        Strategy daily returns. Index = aligned business days (rows where
        all required return streams + on_signal are non-NaN).
    """
    if not (0.0 <= gamma <= 1.0):
        raise ValueError(f"gamma must be in [0, 1], got {gamma}")

    aligned = pd.concat({
        "on_sig": on_signal.shift(1),
        "upg": upgrade_gate.shift(1),
        "rv": ratevol_gate.shift(1),
        "ret_qld": qld_returns,
        "ret_tqqq": tqqq_returns,
        "ret_off": off_returns,
        "ret_alt": alt_off_returns,
    }, axis=1).dropna(subset=["ret_qld", "ret_tqqq", "ret_off", "ret_alt"])

    on_state = aligned["on_sig"].fillna(0.0) == 1.0
    upg = aligned["upg"].fillna(0.0)
    rv = aligned["rv"].fillna(0.0)

    # Effective ON-leg return at each row (selects QLD or TQQQ based on upgrade).
    on_leg_ret = np.where(
        upg == 1.0, aligned["ret_tqqq"], aligned["ret_qld"]
    )
    on_leg_ret = pd.Series(on_leg_ret, index=aligned.index)

    out = pd.Series(0.0, index=aligned.index)

    # ON-state cells:
    on_clean = on_state & (rv != 1.0)
    on_blend = on_state & (rv == 1.0)
    out[on_clean] = on_leg_ret[on_clean]
    out[on_blend] = (
        gamma * aligned.loc[on_blend, "ret_alt"]
        + (1.0 - gamma) * on_leg_ret[on_blend]
    )

    # OFF-state cells:
    off_state = ~on_state
    if use_off_override:
        off_normal = off_state & (rv != 1.0)
        off_override = off_state & (rv == 1.0)
        out[off_normal] = aligned.loc[off_normal, "ret_off"]
        out[off_override] = aligned.loc[off_override, "ret_alt"]
    else:
        out[off_state] = aligned.loc[off_state, "ret_off"]

    return out


def triple_stack_turnover(
    on_signal: pd.Series,
    upgrade_gate: pd.Series,
    ratevol_gate: pd.Series,
    gamma: float,
    use_off_override: bool,
) -> float:
    """Annualised turnover from state transitions in the triple-stack machine.

    Categorical exposure state (5 states):
      0 = OFF (alt-off, when ratevol fired and use_off_override=True)
      1 = OFF (zroz, otherwise)
      2 = ON (qld-clean, ratevol=0, upgrade=0)
      3 = ON (tqqq-clean, ratevol=0, upgrade=1)
      4 = ON (blend, ratevol=1) — assigned regardless of upgrade because
          the cell is a fixed-weight blend that rebalances daily

    Each state change = 100% turnover. Approximation: ON-blend cell
    daily rebalancing internal turnover is not counted (consistent with
    iter 010's `graded_master_turnover` single-asset path; iter 012
    `compound_turnover` also counts only state transitions).
    """
    if not (0.0 <= gamma <= 1.0):
        raise ValueError(f"gamma must be in [0, 1], got {gamma}")

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
        state[off_state & rv_fired] = 0  # off-alt
    state[on_qld] = 2
    state[on_tqqq] = 3
    state[on_blend] = 4

    flips = (state.diff().abs() > 0).astype(int)
    n_years = len(state) / 252.0
    if n_years <= 0:
        return 0.0
    return float(flips.sum() / n_years)
