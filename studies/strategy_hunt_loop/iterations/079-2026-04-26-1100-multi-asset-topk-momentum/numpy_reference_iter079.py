"""Iter 079 — Numpy-pure reference for multi-asset top-K returns (G7 parity).

Mirrors `compute_topk_returns` in `multi_asset_topk_momentum.py` without
pandas. Used for the G7 ±3 pp CAGR check `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np


def compute_topk_returns_np(
    *,
    asset_returns: dict[str, np.ndarray],
    asset_order: Sequence[str],
    daily_dates: np.ndarray,      # numpy datetime64[ns] sorted ascending
    signal_dates: np.ndarray,     # numpy datetime64[ns] sorted ascending
    signal_weights: np.ndarray,   # shape (n_signals, n_sleeves) per asset_order
    trans_cost_bps: float,
) -> np.ndarray:
    """Pure-numpy implementation matching `compute_topk_returns`.

    Same T-1 lag rule (signal at signal_dates[k] applies to days
    strictly after signal_dates[k]). L1 turnover cost on rebalance.
    Day-0 prior allocation = zeros.
    """
    if trans_cost_bps < 0:
        raise ValueError(f"trans_cost_bps must be ≥ 0; got {trans_cost_bps}")

    n_days = daily_dates.shape[0]
    n_sleeves = len(asset_order)

    # Validate input shapes.
    for a in asset_order:
        if asset_returns[a].shape[0] != n_days:
            raise ValueError(
                f"asset_returns['{a}'].shape[0]={asset_returns[a].shape[0]} "
                f"≠ daily_dates.shape[0]={n_days}"
            )
    if signal_weights.shape[1] != n_sleeves:
        raise ValueError(
            f"signal_weights.shape[1]={signal_weights.shape[1]} ≠ n_sleeves={n_sleeves}"
        )
    if signal_dates.shape[0] != signal_weights.shape[0]:
        raise ValueError("signal_dates / signal_weights row count mismatch")

    w_mat = np.zeros((n_days, n_sleeves), dtype=float)
    if signal_dates.shape[0] > 0:
        # Sort signal by date ascending (defensive — caller should pass sorted).
        order = np.argsort(signal_dates, kind="stable")
        s_dates = signal_dates[order]
        s_weights = signal_weights[order]
        ins = np.searchsorted(s_dates, daily_dates, side="left")
        rebal_idx = ins - 1
        valid = rebal_idx >= 0
        w_mat[valid] = s_weights[rebal_idx[valid]]

    w_prev = np.vstack([np.zeros((1, n_sleeves)), w_mat[:-1]])
    turnover = np.abs(w_mat - w_prev).sum(axis=1)
    cost = turnover * (trans_cost_bps / 10000.0)

    ret_mat = np.column_stack([asset_returns[a] for a in asset_order])
    gross = (w_mat * ret_mat).sum(axis=1)
    return gross - cost
