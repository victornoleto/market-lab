"""Iter 065 — pure-numpy reference for VIX-conditional output leverage gate.

Reproduces the exact logic of ``output_lev_gate.apply_vix_lev_gate`` in
pure numpy (no pandas) so we can run the G7 cross-lib parity check.
The two inputs (``combined_returns`` and ``vix_aligned``) must already
be aligned to the same index by the caller; the numpy reference does
NOT do reindex/ffill/bfill.

Citations
---------

* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline;
  the numpy reference must match the pandas implementation to floating-
  point exactness.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule;
  reproduces ``vix.shift(1).bfill()`` as ``vix_aligned[max(0, t-1)]``.
"""

from __future__ import annotations

import numpy as np


def apply_vix_lev_gate_np(
    combined_returns: np.ndarray,
    vix_aligned: np.ndarray,
    *,
    lev_calm: float = 1.5,
    lev_stress: float = 1.0,
    vix_threshold: float = 20.0,
    borrow_annual: float = 0.0225,
    days_per_year: int = 252,
) -> np.ndarray:
    """Numpy reference for ``output_lev_gate.apply_vix_lev_gate``.

    Inputs must already be aligned to the same length / index (the
    pandas caller applies ``reindex/ffill/bfill`` before calling this
    via the parity wrapper).

    Parameters
    ----------
    combined_returns : np.ndarray
        Daily net returns, shape (n,).
    vix_aligned : np.ndarray
        VIX values aligned to ``combined_returns.index``, shape (n,).
    lev_calm, lev_stress, vix_threshold, borrow_annual, days_per_year :
        Same as ``output_lev_gate.apply_vix_lev_gate``.

    Returns
    -------
    np.ndarray
        Levered returns, shape (n,).
    """
    if combined_returns.shape != vix_aligned.shape:
        raise ValueError(
            f"shapes must match: combined={combined_returns.shape}, "
            f"vix={vix_aligned.shape}"
        )
    if len(combined_returns) < 2:
        raise ValueError(f"len must be ≥ 2; got {len(combined_returns)}")
    if lev_calm < 0:
        raise ValueError(f"lev_calm must be ≥ 0; got {lev_calm}")
    if lev_stress < 0:
        raise ValueError(f"lev_stress must be ≥ 0; got {lev_stress}")
    if vix_threshold < 0:
        raise ValueError(f"vix_threshold must be ≥ 0; got {vix_threshold}")
    if borrow_annual < 0:
        raise ValueError(f"borrow_annual must be ≥ 0; got {borrow_annual}")

    # vix.shift(1).bfill(): seed bar 0 with vix_aligned[0] (the bfill of
    # the NaN at index 0 takes the next non-NaN, which is vix_aligned[0]).
    n = len(vix_aligned)
    vix_lag = np.empty(n, dtype=float)
    vix_lag[0] = float(vix_aligned[0])
    vix_lag[1:] = vix_aligned[:-1].astype(float)

    is_stress = vix_lag >= vix_threshold
    lev = np.where(is_stress, lev_stress, lev_calm).astype(float)
    drag = (lev - 1.0) * borrow_annual / days_per_year
    return lev * combined_returns.astype(float) - drag
