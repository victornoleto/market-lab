"""Iter 074 — Pure-numpy reference implementation for G7 cross-lib parity.

Mirrors `iter074_ensemble.combine_iter016_iter064` operating on
already-aligned numpy arrays (caller responsible for inner-join).

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import numpy as np


def combine_iter016_iter064_np(
    r_016: np.ndarray,
    r_064: np.ndarray,
    *,
    w_016: float,
    w_064: float,
) -> np.ndarray:
    """Pure numpy reference for the convex weighted blend.

    Inputs must be already aligned (same length, same date order).
    """
    a = np.asarray(r_016, dtype=float)
    b = np.asarray(r_064, dtype=float)
    if a.shape != b.shape:
        raise ValueError(
            f"r_016 and r_064 must have same shape; got {a.shape}, {b.shape}"
        )
    if w_016 < 0 or w_064 < 0:
        raise ValueError(f"weights must be >= 0; got w_016={w_016}, w_064={w_064}")
    if (w_016 + w_064) <= 0:
        raise ValueError(
            f"w_016 + w_064 must be > 0; got {w_016 + w_064}"
        )
    return w_016 * a + w_064 * b
