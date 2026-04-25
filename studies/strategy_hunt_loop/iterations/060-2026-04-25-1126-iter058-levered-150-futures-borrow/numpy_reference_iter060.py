"""Iter 060 — Pure-numpy reference for the levered iter 058 stream (G7 parity).

Since iter 058's combined stream is loaded from its saved JSON
(`returns_series` per dataset, frozen), the only engine call requiring
G7 parity is the leverage transform itself. ``apply_leverage_np`` is
already pure-numpy — this file just re-exports it under the iter 060
namespace for symmetric access.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ITER_DIR = Path(__file__).resolve().parent
if str(ITER_DIR) not in sys.path:
    sys.path.append(str(ITER_DIR))

from levered_iter058 import apply_leverage_np  # noqa: E402


def compute_levered_returns_np(
    r_058: np.ndarray,
    *,
    lev: float = 1.5,
    borrow_rate_annual: float = 0.025,
) -> np.ndarray:
    """Pure-numpy levered iter 058 reference.

    Parameters
    ----------
    r_058 : np.ndarray
        Daily simple net returns of iter 058's saved combined stream.
    lev : float, default 1.5
        Leverage multiplier.
    borrow_rate_annual : float, default 0.025
        Futures-implied financing rate (T-bill 2.0% + 0.5% roll cost).

    Returns
    -------
    np.ndarray
        Levered net returns (same length as input).
    """
    return apply_leverage_np(
        r_058, lev=lev, borrow_rate_annual=borrow_rate_annual,
    )


__all__ = ["compute_levered_returns_np"]
