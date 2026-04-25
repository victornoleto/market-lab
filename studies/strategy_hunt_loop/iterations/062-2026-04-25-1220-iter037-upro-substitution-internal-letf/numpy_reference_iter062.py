"""Pure-numpy reference for iter 062 (G7 cross-lib parity check).

Two operations replicated:

1. **Synth LETF formula**: ``r_synth[t] = leverage·r_spy[t] - expense/252``.
2. **3-leg static stack**: ``net[t] = w_eq·r_eq[t] + w_s·r_s[t] +
   w_l·r_l[t] - turnover_cost[t]`` where turnover is zero for t > 0
   under static weights, and t=0 turnover equals the sum of weights.

Citations
---------
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
  (vacuous for static weights and prior-day-only synth formula).
"""

from __future__ import annotations

import numpy as np


def synth_upro_returns_np(
    r_spy: np.ndarray,
    *,
    leverage: float = 3.0,
    expense_ratio: float = 0.0091,
) -> np.ndarray:
    """Pure-numpy reference for synth-UPRO formula."""
    if leverage <= 0:
        raise ValueError(f"leverage must be > 0; got {leverage}")
    if expense_ratio < 0:
        raise ValueError(f"expense_ratio must be ≥ 0; got {expense_ratio}")
    daily_expense = expense_ratio / 252.0
    return leverage * np.asarray(r_spy, dtype=float) - daily_expense


def apply_static_stack_3leg_np(
    r_eq: np.ndarray,
    r_bd_short: np.ndarray,
    r_bd_long: np.ndarray,
    *,
    eq_w: float = 0.20,
    bd_short_w: float = 0.65,
    bd_long_w: float = 0.65,
    cost_bps_per_leg: float = 0.0002,
) -> np.ndarray:
    """Pure-numpy reference for the 3-leg static stack net returns."""
    a = np.asarray(r_eq, dtype=float)
    b = np.asarray(r_bd_short, dtype=float)
    c = np.asarray(r_bd_long, dtype=float)
    if not (a.shape == b.shape == c.shape):
        raise ValueError(
            f"shape mismatch: eq={a.shape} bd_s={b.shape} bd_l={c.shape}"
        )

    n = len(a)
    gross = eq_w * a + bd_short_w * b + bd_long_w * c
    cost = np.zeros(n, dtype=float)
    # t=0: |Δ| from zero = w (one-time setup); t>0: |Δ| = 0 for static weights.
    cost[0] = (eq_w + bd_short_w + bd_long_w) * cost_bps_per_leg
    return gross - cost
