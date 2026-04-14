"""Band-pass filter — [cycle_analytics, eq. 5-2, p.48, ch.5].

Ehlers's IIR band-pass is simultaneously a detrender and a smoother: its
DC response is zero (detrending) and its Nyquist response is near zero
(smoothing), with a resonant peak at a tunable center period.

Formula
-------

Let ``P`` be the center period (``= dcp · pct_of_dcp``), ``B`` the
bandwidth fraction (default 0.3 per [p.53, ch.5]):

    β = cos(2π / P)                       # center frequency
    γ = 1 / cos(2π · B / P)               # Q-dependent factor
    σ = γ - √(γ² - 1)                     # pole-radius parameter (eq. 5-1)
    λ = β                                 # eq. 5-2 uses same cos(2π/P)

    BP[t] = 0.5·(1 - σ)·(Input[t] - Input[t-2])
          + λ·(1 + σ)·BP[t-1]
          - σ·BP[t-2]

Tuning rule [cycle_analytics, p.152-153, ch.11]: set ``P = 0.9 · DCP`` to
obtain ~60° of phase lead. The strategy signal then becomes an early
indication of cycle turning points.

The ``dcp`` argument may be a scalar (fixed-tuning BPF) or a ``pd.Series``
of bar-by-bar dominant cycle estimates (adaptive BPF — the form used by
the Ehlers Band-Pass Swing strategy). When ``dcp`` is a series, the
coefficients ``(σ, λ)`` are recomputed every bar.
"""

from __future__ import annotations

import math
from typing import Union

import numpy as np
import pandas as pd

DCPInput = Union[float, int, pd.Series, np.ndarray]


def band_pass(
    series: pd.Series,
    dcp: DCPInput,
    pct_of_dcp: float = 0.90,
    bandwidth: float = 0.30,
) -> pd.Series:
    """Apply Ehlers's adaptive band-pass filter.

    Parameters
    ----------
    series : pd.Series
        Input (typically roofed price).
    dcp : float | pd.Series
        Dominant cycle period. Scalar → fixed-tuning. Series → adaptive.
    pct_of_dcp : float
        Tuning fraction. Default 0.90 per [p.152-153, ch.11] (60° lead).
        Must be > 0.
    bandwidth : float
        Fractional bandwidth. Default 0.30 per [p.53, ch.5]. Must be in
        (0, 1).

    Returns
    -------
    pd.Series
        Band-pass output, same length/index. Near zero-mean after warm-up.
    """
    if pct_of_dcp <= 0:
        raise ValueError(f"pct_of_dcp must be > 0, got {pct_of_dcp}")
    if not (0 < bandwidth < 1):
        raise ValueError(f"bandwidth must be in (0, 1), got {bandwidth}")

    values = series.to_numpy(dtype=float, copy=True)
    n = len(values)

    if isinstance(dcp, pd.Series):
        dcp_values = dcp.to_numpy(dtype=float, copy=True)
        if len(dcp_values) != n:
            raise ValueError(
                f"dcp series length ({len(dcp_values)}) must match "
                f"input length ({n})"
            )
    elif isinstance(dcp, np.ndarray):
        if len(dcp) != n:
            raise ValueError(f"dcp array length ({len(dcp)}) must match {n}")
        dcp_values = dcp.astype(float, copy=True)
    else:
        dcp_values = np.full(n, float(dcp))

    bp = np.zeros(n)
    two_pi = 2 * math.pi

    for t in range(2, n):
        period = dcp_values[t] * pct_of_dcp
        if period < 2:  # Nyquist floor — coeffs undefined below this
            bp[t] = bp[t - 1]
            continue

        beta = math.cos(two_pi / period)
        cos_bw = math.cos(two_pi * bandwidth / period)
        if abs(cos_bw) < 1e-12:
            bp[t] = bp[t - 1]
            continue
        gamma = 1.0 / cos_bw
        disc = gamma * gamma - 1.0
        if disc < 0:  # defensive — should never hit with bandwidth ∈ (0, 1)
            bp[t] = bp[t - 1]
            continue
        sigma = gamma - math.sqrt(disc)

        bp[t] = (
            0.5 * (1 - sigma) * (values[t] - values[t - 2])
            + beta * (1 + sigma) * bp[t - 1]
            - sigma * bp[t - 2]
        )

    return pd.Series(bp, index=series.index, name=series.name)
