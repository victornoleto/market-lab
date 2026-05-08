"""Roofing filter — two-pole HP then SuperSmoother.

The roofing filter is Ehlers's **mandatory preprocessor** before any other
indicator computation: it produces a zero-mean, Spectral-Dilation-corrected
data stream where the passband is approximately between ``lp_period`` and
``hp_period`` bars [cycle_analytics, p.77 text example; p.81-82 Code Listing
7-3; p.88-89 rule, ch.7].

* Without the roofing filter, traditional indicators suffer from *Spectral
  Dilation*: market data's ``1/Fᵅ`` power density makes long-cycle amplitude
  swings dominate, producing erroneous overbought/oversold signals during
  trends [p.77-89, ch.7].
* The text example at [p.77, ch.7] uses ``hp_period=48`` and ``lp_period=10``
  for discussion. Code Listing 7-3 declares ``HPPeriod(80), LPPeriod(40)`` as
  the generalized defaults; the note at [p.82, ch.7] calls these "rather
  arbitrarily" chosen — callers pick per strategy.
"""

from __future__ import annotations

import pandas as pd

from .ehlers_hp import high_pass
from .ehlers_ss import super_smoother


def roofing_filter(
    series: pd.Series,
    hp_period: int,
    lp_period: int,
) -> pd.Series:
    """Apply roofing filter: high-pass followed by SuperSmoother.

    Parameters
    ----------
    series : pd.Series
        Raw price series (typically close).
    hp_period : int
        High-pass cutoff period. Cycles longer than this are suppressed.
    lp_period : int
        SuperSmoother cutoff. Cycles shorter than this are suppressed.

    Returns
    -------
    pd.Series
        Roofing-filtered output, same length/index. Zero-mean after warm-up.
    """
    hp = high_pass(series, period=hp_period)
    return super_smoother(hp, period=lp_period)
