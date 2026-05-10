"""Master-scope OFF override helper for iter 009.

Mirrors iter 004's `master_cashx` override semantics applied to the
compound multi-asset basket (iter 007's `build_compound_strategy_returns`
analogue with master scope).

Citation: `[risk_parity, p.80-81, ch.4]` (Qian RORO master-gate);
`[advances_fin_ml, p.208-211]` (CSCV structural diversity primitive).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_master_scope_strategy_returns(
    on_signal: pd.Series,
    on_basket_returns: pd.Series,
    off_returns: pd.Series,
    alt_off_returns: pd.Series,
    ratevol_gate: pd.Series,
) -> pd.Series:
    """Apply trend signal with **master-scope** OFF override.

    Master-scope: when ratevol gate fires (=1), route the WHOLE portfolio
    to alt_off, regardless of on_signal state. This is qualitatively
    different from iter 007's offleg-only override (which only routes to
    alt_off when on_signal=OFF AND ratevol=1).

    Behavior:
      ratevol fired (=1)         → alt_off_returns (whole portfolio, master)
      ratevol not fired (=0):
          on_signal=ON           → on_basket_returns
          on_signal=OFF          → off_returns (ZROZ)
      ratevol NaN (warmup)       → fallback to non-override behaviour
                                   (on_signal=ON → on_basket; else → off)

    All signals lagged 1 day (computed at close of t-1, applied at open
    of t) — same convention as iter 004 / 007.
    """
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
    on_active = on_state & (~gate_fired)
    off_active = (~on_state) & (~gate_fired)

    out[on_active] = aligned.loc[on_active, "ret_on"]
    out[off_active] = aligned.loc[off_active, "ret_off"]
    out[gate_fired] = aligned.loc[gate_fired, "ret_alt"]

    out = out[aligned["on_sig"].notna()]
    return out


def master_scope_turnover(
    weights: pd.DataFrame | None,
    on_signal: pd.Series,
    ratevol_gate: pd.Series,
) -> float:
    """Annualised turnover for master-scope OFF override compound.

    Categorical exposure {0=alt-off, 1=on, 2=off-zroz} where master-scope
    forces 0 whenever ratevol=1, regardless of on_signal. For multi-asset
    basket: includes 0.5 × Σ |Δw| within ON state.
    """
    on_lag = on_signal.shift(1)
    rv_lag = ratevol_gate.shift(1)

    if weights is None:
        idx = on_lag.dropna().index
        rv_lag_filled = rv_lag.reindex(idx).fillna(0.0)
        on_lag_idx = on_lag.reindex(idx)
        exposure = pd.Series(0, index=idx)
        # Master-scope: ratevol=1 → 0 regardless of on_signal
        exposure[(rv_lag_filled != 1) & (on_lag_idx == 1)] = 1
        exposure[(rv_lag_filled != 1) & (on_lag_idx != 1)] = 2
        exposure[(rv_lag_filled == 1)] = 0
        changes = (exposure != exposure.shift(1)).sum()
        n_years = len(exposure) / 252.0
        return float(changes / max(n_years, 1e-9))

    idx = weights.index
    on_lag_idx = on_lag.reindex(idx).fillna(0.0)
    rv_lag_filled = rv_lag.reindex(idx).fillna(0.0)

    # Basket weight delta only counts when on (and not master-suppressed)
    in_on_active = ((on_lag_idx == 1) & (rv_lag_filled != 1)).astype(float)
    w_eff = weights.fillna(0.0).mul(in_on_active, axis=0)
    w_diff = (w_eff - w_eff.shift(1)).abs().sum(axis=1).fillna(0.0)
    basket_turnover = 0.5 * w_diff.sum()

    exposure = pd.Series(2, index=idx)
    exposure[(rv_lag_filled != 1) & (on_lag_idx == 1)] = 1
    exposure[(rv_lag_filled != 1) & (on_lag_idx != 1)] = 2
    exposure[(rv_lag_filled == 1)] = 0
    state_changes = (exposure != exposure.shift(1)).sum()

    n_years = len(idx) / 252.0
    total = basket_turnover + state_changes
    return float(total / max(n_years, 1e-9))
