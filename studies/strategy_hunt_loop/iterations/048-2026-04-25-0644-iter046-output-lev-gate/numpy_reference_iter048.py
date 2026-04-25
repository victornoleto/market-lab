"""Pure-numpy reference for iter 048's output leverage gate (G7 parity).

Mirrors ``output_lev_gate.apply_output_lev_gate`` but operates on
``np.ndarray`` inputs. Used by the cross-lib G7 gate to ensure the
pandas engine and a hand-rolled numpy reference agree to ±3 pp CAGR
(the loop's standard cross-lib tolerance).

Citations
---------
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift; bar 0 lev
  uses combined[0]'s contemporaneous regime classification (bfill seed).
"""

from __future__ import annotations

import numpy as np


def apply_output_lev_gate_np(
    combined: np.ndarray,
    vix: np.ndarray,
    *,
    lev_calm: float = 1.4,
    lev_stress: float = 1.0,
    vix_threshold: float = 20.0,
) -> np.ndarray:
    """Pure-numpy mirror of ``apply_output_lev_gate``.

    Parameters
    ----------
    combined : np.ndarray
        Daily net returns, length n ≥ 2.
    vix : np.ndarray
        VIX values aligned to ``combined`` (same length).
    lev_calm, lev_stress, vix_threshold : float
        Same semantics as the pandas engine.

    Returns
    -------
    np.ndarray
        Re-scaled returns, same length as ``combined``.
    """
    combined = np.asarray(combined, dtype=float)
    vix = np.asarray(vix, dtype=float)
    if combined.shape != vix.shape:
        raise ValueError(
            f"combined and vix must have equal length; "
            f"got {combined.shape} vs {vix.shape}"
        )
    if combined.size < 2:
        raise ValueError(f"combined must have ≥ 2 bars; got {combined.size}")
    if lev_calm < 0 or lev_stress < 0 or vix_threshold < 0:
        raise ValueError(
            "lev_calm, lev_stress, vix_threshold must be ≥ 0"
        )

    # Replicate pandas .shift(1).bfill(): bar 0 reuses bar 0's vix value
    # (i.e. lev[0] is determined by vix[0]); bars 1..n-1 use vix[t-1].
    vix_lag = np.empty_like(vix)
    vix_lag[0] = vix[0]
    vix_lag[1:] = vix[:-1]

    is_stress = vix_lag >= vix_threshold
    lev = np.where(is_stress, lev_stress, lev_calm)
    return lev * combined
