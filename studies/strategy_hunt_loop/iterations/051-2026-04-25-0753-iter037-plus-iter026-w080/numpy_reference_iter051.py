"""Pure-numpy reference for iter 051 G7 cross-library parity.

The combination logic is element-wise weighted addition on already-
aligned arrays. The numpy reference does not perform inner-join; the
caller passes already-aligned slices.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity gate (G7).
"""

from __future__ import annotations

import numpy as np


def combine_037_plus_026_np(
    r_037: np.ndarray,
    r_026: np.ndarray,
    *,
    w_037: float = 0.80,
    w_026: float = 0.20,
) -> np.ndarray:
    """Convex combo via element-wise weighted addition.

    Parameters
    ----------
    r_037, r_026 : np.ndarray
        1-D float arrays of equal length representing already-aligned
        daily net returns.
    w_037, w_026 : float
        Convex combination weights (≥ 0; sum > 0; sum=1 not enforced).

    Returns
    -------
    np.ndarray
        Combined daily net returns array of identical shape.

    Raises
    ------
    ValueError
        If weights are negative / zero-sum, or arrays have unequal
        length.
    """
    if w_037 < 0:
        raise ValueError(f"w_037 must be >= 0; got {w_037}")
    if w_026 < 0:
        raise ValueError(f"w_026 must be >= 0; got {w_026}")
    if (w_037 + w_026) <= 0:
        raise ValueError(
            f"w_037 + w_026 must be > 0; got {w_037 + w_026}"
        )
    if r_037.shape != r_026.shape:
        raise ValueError(
            f"shape mismatch: r_037 {r_037.shape} vs r_026 {r_026.shape}"
        )
    return w_037 * r_037 + w_026 * r_026
