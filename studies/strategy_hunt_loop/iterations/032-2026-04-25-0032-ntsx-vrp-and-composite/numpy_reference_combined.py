"""Iter 032 — Pure-numpy reference for NTSX + AND-composite VRP overlay (G7 parity).

Composes iter 015's `apply_static_stack_np` with iter 031's
`compute_vrp_and_composite_returns_np`. This is hand-rolled numpy
composition — no pandas, no engine code reuse beyond the two existing
numpy primitives.

Aligns inputs by length (caller is responsible for pre-aligning the
4 series); computes pct_change for equity and bond legs, then sums the
NTSX leg with `(vrp_full - rf_daily)` on the post-pct_change index
(NTSX layer drops bar 0; harvest layer keeps bar 0; output = harvest
length minus 1).

Citations
---------
* `[risk_parity, p.5, p.10-11, ch.1]` — NTSX risk-parity base.
* `[volatility_trading, p.217-218]` — Sinclair short-vol-writer regime.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_015_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "015-2026-04-24-1704-return-stacked-static-ntsx"
ITER_031_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "031-2026-04-24-2322-vix-and-composite-vrp-primary"
for p in (ITER_015_DIR, ITER_031_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from numpy_reference_stacked import apply_static_stack_np  # noqa: E402
from numpy_reference_and_composite import (  # noqa: E402
    compute_vrp_and_composite_returns_np,
)


def compute_ntsx_vrp_combined_returns_np(
    eq_prices: np.ndarray,
    bd_prices: np.ndarray,
    iv_raw: np.ndarray,
    vix_zscore: np.ndarray,
    *,
    eq_w: float = 0.9,
    bd_w: float = 0.6,
    cost_bps_per_leg: float = 0.0002,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    iv_scale: float = 1.0,
    cost_bps_per_roll: float = 5.0,
    vix_threshold: float = 35.0,
    persistence_days: int = 3,
    z_threshold: float = 2.0,
) -> np.ndarray:
    """Pure-numpy combined NTSX + AND-composite VRP returns.

    Parameters
    ----------
    eq_prices, bd_prices, iv_raw, vix_zscore : np.ndarray
        Pre-aligned 1-D arrays of equal length. The caller is
        responsible for inner-joining and dropping NaN on price/iv
        before passing.

    Returns
    -------
    np.ndarray of length ``n - 1`` — the NTSX layer drops bar 0 (no
    prior bar for pct_change); the harvest layer keeps bar 0 but is
    aligned via tail-slicing.
    """
    if eq_w < 0:
        raise ValueError(f"eq_w must be >= 0; got {eq_w}")
    if bd_w < 0:
        raise ValueError(f"bd_w must be >= 0; got {bd_w}")
    if harvest_notional < 0:
        raise ValueError(
            f"harvest_notional must be >= 0; got {harvest_notional}"
        )

    n = len(eq_prices)
    if not (n == len(bd_prices) == len(iv_raw) == len(vix_zscore)):
        raise ValueError(
            "eq_prices, bd_prices, iv_raw, vix_zscore must share length; "
            f"got {n}, {len(bd_prices)}, {len(iv_raw)}, {len(vix_zscore)}"
        )
    if n < 2:
        raise ValueError(f"need >= 2 bars, got {n}")

    eq = np.asarray(eq_prices, dtype=float)
    bd = np.asarray(bd_prices, dtype=float)

    r_eq = (eq[1:] - eq[:-1]) / eq[:-1]
    r_bd = (bd[1:] - bd[:-1]) / bd[:-1]

    ntsx_net, _, _ = apply_static_stack_np(
        r_eq, r_bd, eq_w=eq_w, bd_w=bd_w, cost_bps_per_leg=cost_bps_per_leg,
    )

    vrp_full = compute_vrp_and_composite_returns_np(
        eq, iv_raw, vix_zscore,
        rf=rf,
        harvest_notional=harvest_notional,
        k_long_pct=k_long_pct,
        k_short_pct=k_short_pct,
        dte_days=dte_days,
        iv_scale=iv_scale,
        cost_bps_per_roll=cost_bps_per_roll,
        vix_threshold=vix_threshold,
        persistence_days=persistence_days,
        z_threshold=z_threshold,
    )
    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    harvest = vrp_full - rf_daily

    # NTSX has length n-1 (post-pct_change), harvest has length n.
    # Align by taking harvest[1:] (drop bar 0).
    return ntsx_net + harvest[1:]
