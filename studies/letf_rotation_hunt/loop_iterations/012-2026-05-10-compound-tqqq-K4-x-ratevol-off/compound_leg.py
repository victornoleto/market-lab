"""Compound TQQQ-K4 leverage upgrade × ratevol OFF override — iter 012 helper.

Stacks two mechanically-orthogonal lifts onto the iter 022 winner architecture:

1. ON-leg leverage upgrade (iter 011 primitive): substitute TQQQSIM (3× NDX)
   for QLDSIM (2× NDX) when an upgrade gate fires (K=4 of 4 vote, optionally
   AND lowvol25). Operates only on the ON state cell.
2. OFF-leg ratevol override (iter 006/007 primitive): substitute alt-OFF
   asset (CASHX or IEFSIM) for ZROZSIM when ZROZ realised-vol percentile
   exceeds threshold. Operates only on the OFF state cell.

The two state cells are disjoint (gated by K=2 entry signal), so the lifts
compose additively per `[risk_parity, ch.5, p.10]` Carlson cap-efficient
stacking. K=2 entry signal and OFF=ZROZ default unchanged from iter 022
winner architecture.

Citations
---------
- [risk_parity, ch.5, p.10]: Carlson cap-efficient stacking — independent
  orthogonal lifts compound additively when their information content is
  uncorrelated (primary).
- [volatility_trading, p.58-60]: Sinclair vol cone — applied to bond
  ratevol gate (high percentile = retreat from duration).
- [stocks_on_the_move, p.98]: Clenow trend-strength filter (K=4 vote =
  high conviction risk-on for the leverage upgrade).
- [leverage_for_the_long_run, ch.4-5, p.40-60]: Husson-Trifoni LRS
  leverage scaling.

This helper is iter-local (`loop_iterations/012-.../`). It does NOT modify
any study-shared module per LOOP_PROTOCOL §"Scope limits".
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_compound_strategy_returns(
    on_signal: pd.Series,
    qld_returns: pd.Series,
    tqqq_returns: pd.Series,
    off_returns: pd.Series,
    alt_off_returns: pd.Series,
    upgrade_gate: pd.Series,
    ratevol_gate: pd.Series,
    use_off_override: bool,
) -> pd.Series:
    """Compound: ON-leg leverage upgrade × OFF-leg ratevol override.

    Behavior (all signals lagged 1 day — same convention as iter 007/011):
      on_signal = 1 AND upgrade = 1                         → tqqq_returns
      on_signal = 1 AND upgrade = 0 (or NaN)                → qld_returns
      on_signal = 0 AND use_off_override AND ratevol = 1    → alt_off_returns
      on_signal = 0 AND use_off_override AND ratevol = 0    → off_returns
      on_signal = 0 AND use_off_override AND ratevol NaN    → off_returns
      on_signal = 0 AND not use_off_override                → off_returns

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
        Binary {0, 1, NaN}; 1 = ZROZ vol percentile > threshold (high-vol
        regime — divert OFF leg).
    use_off_override:
        If False, OFF state always uses off_returns regardless of ratevol.

    Returns
    -------
    pd.Series
        Strategy daily returns. Index = aligned business days (rows where
        all required return streams + on_signal are non-NaN).
    """
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

    on_qld = on_state & (upg != 1.0)
    on_tqqq = on_state & (upg == 1.0)

    out = pd.Series(0.0, index=aligned.index)
    out[on_qld] = aligned.loc[on_qld, "ret_qld"]
    out[on_tqqq] = aligned.loc[on_tqqq, "ret_tqqq"]

    off_state = ~on_state
    if use_off_override:
        off_normal = off_state & (rv != 1.0)
        off_override = off_state & (rv == 1.0)
        out[off_normal] = aligned.loc[off_normal, "ret_off"]
        out[off_override] = aligned.loc[off_override, "ret_alt"]
    else:
        out[off_state] = aligned.loc[off_state, "ret_off"]

    return out


def compound_turnover(
    on_signal: pd.Series,
    upgrade_gate: pd.Series,
    ratevol_gate: pd.Series,
    use_off_override: bool,
) -> float:
    """Annualised turnover from ON↔OFF flips + QLD↔TQQQ flips + ZROZ↔alt flips.

    Categorical exposure state:
      0 = OFF (alt-off, when ratevol fired and override active)
      1 = OFF (zroz, when ratevol not fired or override inactive)
      2 = ON  (qld, when on_state=1 and upgrade=0)
      3 = ON  (tqqq, when on_state=1 and upgrade=1)

    Each state change = 100% turnover.
    """
    on_lag = on_signal.shift(1).fillna(0.0)
    upg_lag = upgrade_gate.shift(1).fillna(0.0)
    rv_lag = ratevol_gate.shift(1).fillna(0.0)

    on_state = on_lag == 1.0
    on_tqqq = on_state & (upg_lag == 1.0)
    on_qld = on_state & (upg_lag != 1.0)
    off_state = ~on_state

    state = pd.Series(1, index=on_lag.index)  # default off-zroz
    if use_off_override:
        state[off_state & (rv_lag == 1.0)] = 0  # off-alt
    state[on_qld] = 2
    state[on_tqqq] = 3

    flips = (state.diff().abs() > 0).astype(int)
    n_years = len(state) / 252.0
    if n_years <= 0:
        return 0.0
    return float(flips.sum() / n_years)
