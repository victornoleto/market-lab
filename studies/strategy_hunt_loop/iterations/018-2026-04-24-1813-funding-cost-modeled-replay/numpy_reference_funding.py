"""Iter 018 — Hand-rolled numpy reference for funding-cost subtraction (G7).

Independent numpy re-implementation of the iter 016 primitive PLUS
iter 018's funding-cost subtraction in a single pass. Compared against
the pandas wrapper in `compute_gates_and_score.py::g7_cross_lib`.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-lib parity discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_016_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / "016-2026-04-24-1729-static-stack-vm-hybrid"

sys.path.insert(0, str(ITER_016_DIR))
from numpy_reference_stack_vm import apply_static_stack_vm_np  # noqa: E402


def apply_static_stack_vm_funded_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    r_tbill: np.ndarray,
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Numpy reference for iter 018.

    Parameters
    ----------
    r_eq, r_bd, r_tbill : np.ndarray
        Same length (N,). `r_tbill` is the lagged-by-1 daily T-bill
        simple return (caller is responsible for the lag — mirrors
        pandas wrapper's call-site).
    All other params: pass through to iter 016's numpy primitive.

    Returns
    -------
    (net_post, pos_eq, pos_bd, scale, funding_cost)
        All arrays truncated to the valid-bar slice where scale is
        finite (first `lookback` bars dropped — matches iter 016 numpy
        reference). `net_post = gross - cost - funding_cost`.
    """
    net_gross, pos_eq, pos_bd, scale = apply_static_stack_vm_np(
        r_eq, r_bd,
        eq_weight=eq_weight, bd_weight=bd_weight,
        target_vol=target_vol, lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=cost_bps_per_leg,
    )
    n_full = len(r_eq)
    n_keep = len(scale)
    tail_start = n_full - n_keep
    r_tbill_valid = r_tbill[tail_start:]

    excess_lev = np.where(scale > 1.0, scale - 1.0, 0.0)
    funding_cost = excess_lev * r_tbill_valid
    net_post = net_gross - funding_cost
    return net_post, pos_eq, pos_bd, scale, funding_cost
