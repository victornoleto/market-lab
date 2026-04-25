"""Iter 056 — Pure-numpy reference for the 1.3× levered iter 046 (G7 parity).

Composes iter 046's `compute_combined_returns_np` and applies the
identical leverage transform from ``levered_iter046.apply_leverage_np``.
G7 verifies the levered pandas/numpy CAGR Δ ≤ 3 pp.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

import numpy as np

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
for p in (ITER_046_DIR, ITER_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from numpy_reference_combined_046 import compute_combined_returns_np  # noqa: E402

from levered_iter046 import apply_leverage_np  # noqa: E402


def compute_levered_returns_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    r_gld: np.ndarray,
    vix_for_regime: np.ndarray,
    basket_prices: dict[str, np.ndarray],
    iv: np.ndarray,
    *,
    lev: float = 1.3,
    borrow_rate_annual: float = 0.035,
    w_041: float = 0.5,
    w_039: float = 0.5,
    calm_weights: Mapping[str, float] | None = None,
    stress_weights: Mapping[str, float] | None = None,
    vix_threshold: float = 20.0,
    cost_bps_per_leg: float = 0.0002,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    weights: dict[str, float] | None = None,
    iv_scales: dict[str, float] | None = None,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    cost_bps_per_roll: float = 5.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Pure-numpy levered iter 046 reference.

    Returns
    -------
    (r_levered, r_046) : (np.ndarray, np.ndarray)
    """
    r_046, _, _ = compute_combined_returns_np(
        r_eq, r_bd, r_gld, vix_for_regime,
        basket_prices, iv,
        w_041=w_041, w_039=w_039,
        calm_weights=calm_weights, stress_weights=stress_weights,
        vix_threshold=vix_threshold,
        cost_bps_per_leg=cost_bps_per_leg,
        rf=rf, harvest_notional=harvest_notional,
        weights=weights, iv_scales=iv_scales,
        k_long_pct=k_long_pct, k_short_pct=k_short_pct,
        dte_days=dte_days, cost_bps_per_roll=cost_bps_per_roll,
    )
    r_levered = apply_leverage_np(
        r_046, lev=lev, borrow_rate_annual=borrow_rate_annual,
    )
    return r_levered, r_046


__all__ = ["compute_levered_returns_np"]
