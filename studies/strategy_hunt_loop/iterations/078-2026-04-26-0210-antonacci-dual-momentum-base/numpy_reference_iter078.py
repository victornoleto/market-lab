"""Iter 078 — Numpy-pure reference for GEM returns (G7 cross-lib parity).

Mirrors `compute_gem_returns` in `antonacci_dual_momentum.py` without
pandas. Used for the G7 ±3 pp CAGR check `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import numpy as np


def compute_gem_returns_np(
    *,
    spy_returns: np.ndarray,
    efa_returns: np.ndarray,
    agg_returns: np.ndarray,
    daily_dates: np.ndarray,      # numpy datetime64[ns] sorted ascending
    signal_dates: np.ndarray,     # numpy datetime64[ns] sorted ascending
    signal_choices: np.ndarray,   # array of "SPY" / "EFA" / "AGG" / None
    trans_cost_bps: float,
) -> np.ndarray:
    """Pure-numpy implementation of `compute_gem_returns`.

    Same T-1 lag rule (signal at signal_dates[k] applies to days
    strictly after signal_dates[k]). L1 turnover cost on rebalance.
    Day-0 prior allocation = (0, 0, 0).
    """
    if trans_cost_bps < 0:
        raise ValueError(f"trans_cost_bps must be ≥ 0; got {trans_cost_bps}")
    n = spy_returns.shape[0]
    if not (efa_returns.shape[0] == n and agg_returns.shape[0] == n
            and daily_dates.shape[0] == n):
        raise ValueError("input arrays must share length")

    w_spy = np.zeros(n, dtype=float)
    w_efa = np.zeros(n, dtype=float)
    w_agg = np.zeros(n, dtype=float)

    if signal_dates.shape[0] > 0:
        ins = np.searchsorted(signal_dates, daily_dates, side="left")
        rebal_idx = ins - 1
        for i in range(n):
            ridx = rebal_idx[i]
            if ridx < 0:
                continue
            sig_v = signal_choices[ridx]
            if sig_v is None:
                continue
            try:
                # numpy may pass strings as bytes after some round-trips
                sig_str = sig_v.decode() if isinstance(sig_v, bytes) else str(sig_v)
            except AttributeError:
                sig_str = str(sig_v)
            if sig_str == "SPY":
                w_spy[i] = 1.0
            elif sig_str == "EFA":
                w_efa[i] = 1.0
            elif sig_str == "AGG":
                w_agg[i] = 1.0
            elif sig_str in ("nan", "None", ""):
                continue

    w_mat = np.stack([w_spy, w_efa, w_agg], axis=1)
    w_prev = np.vstack([np.zeros((1, 3)), w_mat[:-1]])
    turnover = np.abs(w_mat - w_prev).sum(axis=1)
    cost = turnover * (trans_cost_bps / 10000.0)
    gross = w_spy * spy_returns + w_efa * efa_returns + w_agg * agg_returns
    return gross - cost
