"""Iter 045 — Pure-numpy reference for the 50/50 convex combo (G7 parity).

Implements `compute_combined_returns_np` by composing the iter 037 numpy
reference (`apply_static_stack_3leg_np`) and the iter 039 numpy reference
(`compute_vrp_basket_returns_np`), then arithmetically averaging the two
streams on a pre-computed common index.

The numpy reference does NOT call into pandas — the whole point of G7 is
to detect engine bugs by computing through a different code path
(`[advances_fin_ml, p.31-34]`).

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_037_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "037-2026-04-25-0224-ntsx-3leg-preserved-lev"
ITER_039_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "039-2026-04-25-0313-vrp-basket-3etf"
for p in (ITER_037_DIR, ITER_039_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from numpy_reference_stacked_3leg import (  # noqa: E402
    apply_static_stack_3leg_np,
    cagr_np,
)
from numpy_reference_basket import (  # noqa: E402
    compute_vrp_basket_returns_np,
)


def compute_combined_returns_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    r_gld: np.ndarray,
    basket_prices: dict[str, np.ndarray],
    iv: np.ndarray,
    *,
    w_037: float = 0.5,
    w_039: float = 0.5,
    # iter 037 sub-strategy params
    eq_w: float = 0.60,
    bd_short_w: float = 0.45,
    bd_long_w: float = 0.45,
    cost_bps_per_leg: float = 0.0002,
    # iter 039 sub-strategy params
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    weights: dict[str, float] | None = None,
    iv_scales: dict[str, float] | None = None,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    cost_bps_per_roll: float = 5.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pure-numpy 50/50 combo of iter 037 and iter 039 net streams.

    All inputs are pre-aligned numpy arrays of identical length n. The
    iter 037 component receives RETURNS (already pct_change applied) and
    the iter 039 component receives PRICES (raw levels) — same as the
    pandas engines, just without index handling.

    Parameters
    ----------
    r_eq, r_bd, r_gld : np.ndarray (n,)
        Daily simple returns (post pct_change) for the 3-leg static
        stack. Must share length n.
    basket_prices : dict[str, np.ndarray (n,)]
        Per-ticker price LEVEL arrays for the iter 039 basket. Each
        must have length n+1 actually no — the iter 039 numpy ref
        consumes prices and computes returns internally; n must match
        r_eq's length AFTER pct_change is applied. The caller must
        align so that ``len(basket_prices[tk]) == len(r_eq) + 1``
        (one extra bar for the price level baseline). See test specs.
    iv : np.ndarray
        IV proxy aligned to basket_prices length. Same alignment rule.
    w_037, w_039 :
        Convex weights. ``w_037 + w_039`` must be > 0.
    Other params: same defaults as `combined_037_039.compute_combined_returns`.

    Returns
    -------
    (combined, r_037, r_039) : np.ndarray, np.ndarray, np.ndarray
        ``combined`` : daily net combined returns of length min(n_037,
        n_039) (the trim of overlapping bars).
        ``r_037``, ``r_039`` : per-strategy net streams trimmed to the
        same overlap.

    Notes
    -----
    The iter 037 component generates n_037 = len(r_eq) bars; iter 039
    generates n_039 = len(basket_prices[T]) - 1 bars (because the
    overlay needs a price-difference series internally). To inner-join,
    the function tail-trims iter 037 to match iter 039's length when
    iter 039 has a shorter post-warmup output.
    """
    if w_037 < 0:
        raise ValueError(f"w_037 must be >= 0; got {w_037}")
    if w_039 < 0:
        raise ValueError(f"w_039 must be >= 0; got {w_039}")
    if (w_037 + w_039) <= 0:
        raise ValueError(
            f"w_037 + w_039 must be > 0; got {w_037 + w_039}"
        )

    a = np.asarray(r_eq, dtype=float)
    b = np.asarray(r_bd, dtype=float)
    c = np.asarray(r_gld, dtype=float)
    if not (a.shape == b.shape == c.shape):
        raise ValueError(
            f"r_eq/r_bd/r_gld shape mismatch: {a.shape} vs {b.shape} vs {c.shape}"
        )

    net_037, _, _ = apply_static_stack_3leg_np(
        a, b, c,
        eq_w=eq_w, bd_short_w=bd_short_w, bd_long_w=bd_long_w,
        cost_bps_per_leg=cost_bps_per_leg,
    )

    arrs = {tk: np.asarray(p, dtype=float) for tk, p in basket_prices.items()}
    arr_v = np.asarray(iv, dtype=float)
    net_039 = compute_vrp_basket_returns_np(
        arrs, arr_v,
        rf=rf,
        harvest_notional=harvest_notional,
        weights=weights,
        iv_scales=iv_scales,
        k_long_pct=k_long_pct,
        k_short_pct=k_short_pct,
        dte_days=dte_days,
        cost_bps_per_roll=cost_bps_per_roll,
    )

    n_overlap = min(len(net_037), len(net_039))
    # tail-anchor: align both streams on their last n_overlap bars
    # (iter 037 starts at the second price bar; iter 039 starts at the
    # second price bar — they share the same anchor, so a tail-anchor
    # corresponds to the natural intersection of date indices).
    s037 = net_037[-n_overlap:]
    s039 = net_039[-n_overlap:]
    combined = w_037 * s037 + w_039 * s039
    return combined, s037, s039


__all__ = [
    "compute_combined_returns_np",
    "cagr_np",  # re-exported from iter 037 numpy ref
]
