"""Iter 066 — Gated combine of iter 064 stream and meta-label predictions.

Construction
------------
At each bar t, the combined return is:

::

    r_066[t] = pred[t-1] * r_064[t]  -  cost_per_flip * |pred[t] - pred[t-1]|

Cost is applied on the BAR WHERE THE FLIP HAPPENS (t), reflecting an
end-of-day rebalance cost when the signal changes. ``pred[0]`` is treated
as the initial "cash" state (0) so the first non-cash bar costs.

The OOF predictions from purged k-fold CV are aligned to the iter 064
returns index by inner-join (warmup bars dropped where features were NaN
get zero exposure too — kept as cash, no return).

Citations
---------
* `[advances_fin_ml, ch.3]` — meta-label gating mechanics.
* `[advances_fin_ml, p.31-34]` — deterministic post-prediction transform
  (G7 cross-lib parity holds because given the same predictions, the
  combine is pure linear algebra).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def gate_iter064_with_meta(
    r_064: pd.Series, oof_pred: pd.Series, *,
    cost_per_flip: float = 5e-4,
) -> pd.Series:
    """Apply binary meta-label gate to iter 064 returns.

    Bars where ``oof_pred`` is NaN (warmup before first OOF prediction
    is generated, e.g., feature warmup) are treated as cash (pred=0).
    """
    common = r_064.index.intersection(oof_pred.index)
    r = r_064.loc[common].copy()
    p = oof_pred.loc[common].fillna(0).astype(int).copy()

    # signal[t-1] applies to ret[t]
    sig_lagged = p.shift(1).fillna(0).astype(int)
    flips = (p - p.shift(1).fillna(0)).abs().astype(int)
    gross = sig_lagged.values * r.values
    net = gross - cost_per_flip * flips.values
    out = pd.Series(net, index=common, name="r_066")
    return out


def gate_iter064_with_meta_np(
    r_064: np.ndarray, oof_pred: np.ndarray, *,
    cost_per_flip: float = 5e-4,
) -> np.ndarray:
    """Pure-numpy reference for G7 cross-lib parity.

    Inputs must be 1D arrays of equal length, same alignment as the
    pandas version. NaN predictions treated as cash (0).
    """
    if r_064.shape != oof_pred.shape:
        raise ValueError("r_064 and oof_pred must have same shape")
    p = np.where(np.isnan(oof_pred), 0, oof_pred).astype(np.int64)
    p_prev = np.empty_like(p)
    p_prev[0] = 0
    p_prev[1:] = p[:-1]
    flips = np.abs(p - p_prev).astype(np.float64)
    return p_prev * r_064 - cost_per_flip * flips
