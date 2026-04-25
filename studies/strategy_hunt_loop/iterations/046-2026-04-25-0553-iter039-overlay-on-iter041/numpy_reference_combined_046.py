"""Iter 046 — Pure-numpy reference for the 50/50 convex combo (G7 parity).

Composes iter 041's `apply_regime_weights_3leg_np` (which consumes a
pre-computed integer regime array) and iter 039's
`compute_vrp_basket_returns_np` (which consumes price levels + IV
proxy), then arithmetically averages the two streams on a tail-anchored
slice. Mirrors iter 045's pattern with iter 037's numpy ref replaced by
iter 041's.

The regime array is pre-built **externally** with the 1-day VIX lag
(VIX[t-1] < threshold → regime=1 calm; else 0 stress; the first bar
falls back to VIX[0]) so this numpy reference is purely a pricing
kernel without lookahead-leakage logic of its own. The pandas engine's
`apply_regime_weights_3leg` does the lag internally; the numpy ref
expects the lag to have already happened.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

import numpy as np

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_039_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "039-2026-04-25-0313-vrp-basket-3etf"
ITER_041_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "041-2026-04-25-0358-regime-weights-vix-static-stack"
for p in (ITER_039_DIR, ITER_041_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from numpy_reference_regime_weights import (  # noqa: E402
    apply_regime_weights_3leg_np,
    cagr_np,
)
from numpy_reference_basket import (  # noqa: E402
    compute_vrp_basket_returns_np,
)


def build_regime_array(
    vix: np.ndarray,
    *,
    vix_threshold: float = 20.0,
) -> np.ndarray:
    """Build the 1-day-lagged binary regime array.

    Convention identical to iter 041's pandas engine:
    ``regime[t] = 1 if VIX[t-1] < threshold else 0``. Bar 0 falls back
    to ``VIX[0]`` (no "yesterday"), matching iter 041's bootstrap rule.

    Parameters
    ----------
    vix : (n,) np.ndarray
        VIX levels aligned to the **return** index (one element per
        return bar; same length as the returns the regime modulates).
    vix_threshold : float
        Calm/stress cutoff. Default 20.0.

    Returns
    -------
    regime : (n,) ndarray int
        1 = calm, 0 = stress.
    """
    v = np.asarray(vix, dtype=float)
    n = len(v)
    if n == 0:
        return np.zeros(0, dtype=int)
    lagged = np.empty(n, dtype=float)
    lagged[0] = v[0]
    if n > 1:
        lagged[1:] = v[:-1]
    return (lagged < vix_threshold).astype(int)


def compute_combined_returns_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    r_gld: np.ndarray,
    vix_for_regime: np.ndarray,
    basket_prices: dict[str, np.ndarray],
    iv: np.ndarray,
    *,
    w_041: float = 0.5,
    w_039: float = 0.5,
    # iter 041 sub-strategy params
    calm_weights: Mapping[str, float] | None = None,
    stress_weights: Mapping[str, float] | None = None,
    vix_threshold: float = 20.0,
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
    """Pure-numpy 50/50 combo of iter 041 and iter 039 net streams.

    Parameters
    ----------
    r_eq, r_bd, r_gld : np.ndarray (n,)
        Daily simple returns (post pct_change) for the 3-leg regime
        stack. Must share length n.
    vix_for_regime : np.ndarray (n,)
        VIX levels aligned to the **return** index (length n, NOT the
        price index n+1). The 1-day lag is applied internally.
    basket_prices : dict[str, np.ndarray (n+1,)]
        Per-ticker price LEVEL arrays for the iter 039 basket.
    iv : np.ndarray (n+1,)
        IV proxy for the iter 039 basket (BS pricing).
    w_041, w_039 : float
        Convex weights. ``w_041 + w_039 > 0``.
    calm_weights, stress_weights : Mapping[str, float] | None
        iter 041 regime weights. None defaults match iter 041's TOP-K
        ({0.70/0.40/0.40} calm; {0.30/0.55/0.55} stress).
    Other params: same defaults as `combined_041_039.compute_combined_returns`.

    Returns
    -------
    (combined, r_041, r_039) : np.ndarray, np.ndarray, np.ndarray
        ``combined`` : daily net combined returns of length min(n_041,
        n_039) tail-trimmed to overlap.
        ``r_041``, ``r_039`` : per-strategy net streams trimmed to the
        same overlap.
    """
    if w_041 < 0:
        raise ValueError(f"w_041 must be >= 0; got {w_041}")
    if w_039 < 0:
        raise ValueError(f"w_039 must be >= 0; got {w_039}")
    if (w_041 + w_039) <= 0:
        raise ValueError(
            f"w_041 + w_039 must be > 0; got {w_041 + w_039}"
        )

    a = np.asarray(r_eq, dtype=float)
    b = np.asarray(r_bd, dtype=float)
    c = np.asarray(r_gld, dtype=float)
    if not (a.shape == b.shape == c.shape):
        raise ValueError(
            f"r_eq/r_bd/r_gld shape mismatch: {a.shape} vs {b.shape} vs {c.shape}"
        )

    cw = dict(calm_weights) if calm_weights is not None else {
        "eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40,
    }
    sw = dict(stress_weights) if stress_weights is not None else {
        "eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55,
    }

    # iter 041 leg: build regime from VIX (1-day lag), call np ref
    regime = build_regime_array(vix_for_regime, vix_threshold=vix_threshold)
    if regime.shape != a.shape:
        raise ValueError(
            f"regime length {regime.shape} != returns length {a.shape}; "
            f"caller must align vix_for_regime to the returns index"
        )
    net_041, _, _ = apply_regime_weights_3leg_np(
        a, b, c, regime,
        calm_weights=cw, stress_weights=sw,
        cost_bps_per_leg=cost_bps_per_leg,
    )

    # iter 039 leg: prices + IV → returns
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

    n_overlap = min(len(net_041), len(net_039))
    s041 = net_041[-n_overlap:]
    s039 = net_039[-n_overlap:]
    combined = w_041 * s041 + w_039 * s039
    return combined, s041, s039


__all__ = [
    "compute_combined_returns_np",
    "build_regime_array",
    "cagr_np",
]
