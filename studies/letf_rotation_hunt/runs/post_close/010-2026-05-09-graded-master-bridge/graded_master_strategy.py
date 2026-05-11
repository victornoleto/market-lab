"""Graded master-scope OFF override helper for iter 010.

Interpolates between iter 007's offleg-only OFF override (gamma=0) and
iter 009's full master-scope OFF override (gamma=1) using a coefficient
gamma in [0, 1] that applies ONLY in the (ratevol fired, on_signal=ON)
regime — the single cell where iter 007 and iter 009 disagree.

At gamma=0, this helper is bit-exactly equivalent to iter 007's
`build_compound_strategy_returns(use_off_override=True)`.
At gamma=1, this helper is bit-exactly equivalent to iter 009's
`build_master_scope_strategy_returns`.
For gamma in (0, 1), the cell value is a linear blend
gamma * alt_off_returns + (1 - gamma) * on_basket_returns, providing a
graded RORO master-gate per `[risk_parity, p.80-81, ch.4]` (Qian).

Citations
---------
- [risk_parity, p.80-81, ch.4]: Qian RORO graded master-gate (canonical
  reference for partial weights between full risk-on and full risk-off).
- [advances_fin_ml, p.208-211]: CSCV / PBO via combinatorial 50/50 splits;
  structural mechanism diversity (preserves iter 009 PBO 0.377).
- [volatility_trading, p.58-60]: Sinclair volatility cone (ratevol gate,
  iter 006 module re-imported).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_graded_master_strategy_returns(
    on_signal: pd.Series,
    on_basket_returns: pd.Series,
    off_returns: pd.Series,
    alt_off_returns: pd.Series,
    ratevol_gate: pd.Series,
    gamma: float,
) -> pd.Series:
    """Apply trend signal with **graded master-scope** OFF override.

    Behaviour matrix:

      ratevol fired (=1):
          on_signal=ON  → gamma * alt_off_returns + (1 - gamma) * on_basket_returns
          on_signal=OFF → alt_off_returns                       (same as offleg AND master)
      ratevol not fired (=0):
          on_signal=ON  → on_basket_returns
          on_signal=OFF → off_returns (ZROZ)
      ratevol NaN (warmup) → fallback baseline
          on_signal=ON  → on_basket_returns
          else          → off_returns

    All signals lagged 1 day (computed at close of t-1, applied at open
    of t) — same convention as iters 005/006/007/009.

    Parameters
    ----------
    gamma:
        Coefficient in [0, 1]. gamma=0 ≡ iter 007 offleg-only override
        (no override during ratevol+ON); gamma=1 ≡ iter 009 full master
        (full alt_off override during ratevol+ON).
    """
    if not (0.0 <= gamma <= 1.0):
        raise ValueError(f"gamma must be in [0, 1], got {gamma}")

    aligned = pd.concat({
        "on_sig": on_signal.shift(1),
        "rv": ratevol_gate.shift(1),
        "ret_on": on_basket_returns,
        "ret_off": off_returns,
        "ret_alt": alt_off_returns,
    }, axis=1).dropna(subset=["ret_on", "ret_off", "ret_alt"])

    rv_filled = aligned["rv"].fillna(0.0)
    on_state = (aligned["on_sig"] == 1)
    gate_fired = (rv_filled == 1)

    out = pd.Series(0.0, index=aligned.index)
    on_clean = on_state & (~gate_fired)
    off_clean = (~on_state) & (~gate_fired)
    on_blend = on_state & gate_fired
    off_override = (~on_state) & gate_fired

    out[on_clean] = aligned.loc[on_clean, "ret_on"]
    out[off_clean] = aligned.loc[off_clean, "ret_off"]
    out[on_blend] = (
        gamma * aligned.loc[on_blend, "ret_alt"]
        + (1.0 - gamma) * aligned.loc[on_blend, "ret_on"]
    )
    out[off_override] = aligned.loc[off_override, "ret_alt"]

    out = out[aligned["on_sig"].notna()]
    return out


def graded_master_turnover(
    weights: pd.DataFrame | None,
    on_signal: pd.Series,
    ratevol_gate: pd.Series,
    gamma: float,
) -> float:
    """Annualised turnover for graded master compound.

    State categories: {0=alt-off, 1=on-clean, 2=off-zroz, 3=on-blend}.
    Basket weight delta is scaled by the effective basket weight
    (1 in on-clean, 1-gamma in on-blend, 0 elsewhere).

    For a single-asset ON config (weights=None), turnover counts only
    state transitions.
    """
    if not (0.0 <= gamma <= 1.0):
        raise ValueError(f"gamma must be in [0, 1], got {gamma}")

    on_lag = on_signal.shift(1)
    rv_lag = ratevol_gate.shift(1) if ratevol_gate is not None else None

    if weights is None:
        idx = on_lag.dropna().index
        if rv_lag is not None:
            rv_lag_filled = rv_lag.reindex(idx).fillna(0.0)
        else:
            rv_lag_filled = pd.Series(0.0, index=idx)
        on_lag_idx = on_lag.reindex(idx)
        exposure = pd.Series(0, index=idx)
        exposure[(rv_lag_filled != 1) & (on_lag_idx == 1)] = 1
        exposure[(rv_lag_filled != 1) & (on_lag_idx != 1)] = 2
        exposure[(rv_lag_filled == 1) & (on_lag_idx == 1)] = 3
        exposure[(rv_lag_filled == 1) & (on_lag_idx != 1)] = 0
        changes = (exposure != exposure.shift(1)).sum()
        n_years = len(exposure) / 252.0
        return float(changes / max(n_years, 1e-9))

    idx = weights.index
    on_lag_idx = on_lag.reindex(idx).fillna(0.0)
    if rv_lag is not None:
        rv_lag_filled = rv_lag.reindex(idx).fillna(0.0)
    else:
        rv_lag_filled = pd.Series(0.0, index=idx)

    on_clean_mask = ((on_lag_idx == 1) & (rv_lag_filled != 1)).astype(float)
    on_blend_mask = ((on_lag_idx == 1) & (rv_lag_filled == 1)).astype(float)
    eff_factor = on_clean_mask + (1.0 - gamma) * on_blend_mask
    w_eff = weights.fillna(0.0).mul(eff_factor, axis=0)
    w_diff = (w_eff - w_eff.shift(1)).abs().sum(axis=1).fillna(0.0)
    basket_turnover = 0.5 * w_diff.sum()

    exposure = pd.Series(2, index=idx)
    exposure[(rv_lag_filled != 1) & (on_lag_idx == 1)] = 1
    exposure[(rv_lag_filled != 1) & (on_lag_idx != 1)] = 2
    exposure[(rv_lag_filled == 1) & (on_lag_idx == 1)] = 3
    exposure[(rv_lag_filled == 1) & (on_lag_idx != 1)] = 0
    state_changes = (exposure != exposure.shift(1)).sum()

    n_years = len(idx) / 252.0
    total = basket_turnover + state_changes
    return float(total / max(n_years, 1e-9))
