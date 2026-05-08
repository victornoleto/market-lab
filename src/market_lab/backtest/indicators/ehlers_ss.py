"""SuperSmoother — two-pole Butterworth with Nyquist zero.

Formula (eq. 3-3, [cycle_analytics, p.33, ch.3])::

    a  = exp(-√2·π / period)
    b  = 2·a·cos(√2·π / period)
    c2 = b
    c3 = -a²
    c1 = 1 - c2 - c3
    Output[t] = c1·(Input[t] + Input[t-1])/2
              + c2·Output[t-1]
              + c3·Output[t-2]

Properties (cited verbatim from [cycle_analytics, p.32-36, ch.3]):

* Attenuates aliasing noise at **12 dB per octave**.
* Places a transfer-function zero at the Nyquist frequency via the
  ``(Input + Input[-1])/2`` numerator — Nyquist oscillation is annihilated.
* For cutoff = 10 bars, maximum group delay ≈ 1.5 bars.
* Unity DC gain (``c1 + c2 + c3 = 1``) — constants pass through unchanged.

Warm-up: the recursion needs two previous Output samples. We seed
``Output[0]`` and ``Output[1]`` with the input itself (the standard Ehlers
EasyLanguage convention where series are retroactively padded by the value
at index 0). This gives a short transient, not a hard zero, so tests with
constant inputs see unity output from t=0.
"""

from __future__ import annotations

import math

import pandas as pd


def super_smoother(series: pd.Series, period: int) -> pd.Series:
    """Apply Ehlers's two-pole SuperSmoother to ``series``.

    Parameters
    ----------
    series : pd.Series
        Input signal. NaNs are not handled — caller must pass a clean series.
    period : int
        Cutoff period in bars. Must be ≥ 2 (Nyquist lower bound).

    Returns
    -------
    pd.Series
        Filtered output, same length and index as ``series``.
    """
    if period < 2:
        raise ValueError(f"SuperSmoother period must be ≥ 2, got {period}")

    a = math.exp(-math.sqrt(2) * math.pi / period)
    b = 2 * a * math.cos(math.sqrt(2) * math.pi / period)
    c2 = b
    c3 = -a * a
    c1 = 1 - c2 - c3

    values = series.to_numpy(dtype=float, copy=True)
    n = len(values)
    out = values.copy()  # seed first two bars with the input (warm-up pad)

    for t in range(2, n):
        out[t] = (
            c1 * (values[t] + values[t - 1]) / 2
            + c2 * out[t - 1]
            + c3 * out[t - 2]
        )

    return pd.Series(out, index=series.index, name=series.name)
