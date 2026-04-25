"""Iter 048 — VIX-regime OUTPUT leverage gate on iter 046 combined stream.

Mechanism
---------

Multiplies iter 046's combined daily net-return series by a regime-conditional
scalar derived from VIX[t-1]::

    r_iter048[t] = lev[t] * r_iter046[t]
    lev[t]       = lev_calm   if VIX[t-1] <  vix_threshold
                   lev_stress if VIX[t-1] >= vix_threshold

The gate acts on the COMBINED OUTPUT, not on iter 046's inputs (the
iter 041 regime-gated stack and iter 039 VRP basket are computed verbatim
inside iter 046's engine; this file only re-scales the combined daily
net stream). This makes iter 048 structurally distinct from:

* iter 038 — VIX-gate on iter 037 (single static stack), not a composite.
* iter 041 / 043 / 044 — regime-conditional weights inside the stack
  (input-side modulation), not on the output stream.
* iter 047 — convex-weight sweep on iter 046, not a leverage modulation.

iter 047 closed weight asymmetry on iter 046; iter 048 tests the
distinct axis of OUTPUT-side leverage modulation. Single pre-committed
cfg (N=1) preserves Bonferroni budget per iter 047's lesson.

Citations
---------

* `[risk_parity, ch.5]` — base architecture (iter 041 + iter 039 50/50
  static scaffolding inside iter 046 — preserved verbatim).
* `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching;
  binary VIX gate is a degenerate 2-state HMM.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule; uses
  ``vix.shift(1)`` (with ``bfill`` to seed bar 0).
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline;
  numpy reference in ``numpy_reference_iter048.py``.
* Whaley (2009), JPM 35(3), 98-105, DOI 10.3905/JPM.2009.35.3.098 —
  VIX as ex-ante risk regime indicator; threshold 20 ≈ long-run median.
* Bekaert-Hoerova (2014), J Econometrics 183(2) 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
* Markowitz (1952), JoF 7(1) 77-91 — the COMBINED stream itself is
  Markowitz-style convex; this file does NOT alter that — only re-scales.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_output_lev_gate(
    combined: pd.Series,
    vix: pd.Series,
    *,
    lev_calm: float = 1.4,
    lev_stress: float = 1.0,
    vix_threshold: float = 20.0,
) -> pd.Series:
    """Apply VIX-regime output leverage gate on a daily-return series.

    Parameters
    ----------
    combined : pd.Series
        Daily net returns (e.g. iter 046's combined stream). Must have a
        DatetimeIndex with at least 2 bars.
    vix : pd.Series
        VIX series (DatetimeIndex). Reindexed to ``combined.index`` with
        ``ffill().bfill()`` if it does not already align. Must have at
        least one bar overlapping ``combined.index`` (otherwise raises).
    lev_calm : float, default 1.4
        Multiplier applied when ``vix[t-1] < vix_threshold``. Must be ≥ 0.
    lev_stress : float, default 1.0
        Multiplier applied when ``vix[t-1] >= vix_threshold``. Must be ≥ 0.
    vix_threshold : float, default 20.0
        Threshold dividing calm from stress. Must be ≥ 0.

    Returns
    -------
    pd.Series
        Re-scaled daily-return series, same index as ``combined``.

    Raises
    ------
    ValueError
        If ``combined`` has fewer than 2 bars; ``vix`` does not overlap
        ``combined.index``; or any of ``lev_calm``, ``lev_stress``,
        ``vix_threshold`` is negative.
    """
    if len(combined) < 2:
        raise ValueError(
            f"combined must have ≥ 2 bars; got {len(combined)}"
        )
    if lev_calm < 0:
        raise ValueError(f"lev_calm must be ≥ 0; got {lev_calm}")
    if lev_stress < 0:
        raise ValueError(f"lev_stress must be ≥ 0; got {lev_stress}")
    if vix_threshold < 0:
        raise ValueError(
            f"vix_threshold must be ≥ 0; got {vix_threshold}"
        )

    # Align VIX to combined.index — must overlap or fail.
    overlap = vix.index.intersection(combined.index)
    if len(overlap) == 0:
        raise ValueError(
            "vix index does not overlap combined.index "
            f"(combined={combined.index[0]}..{combined.index[-1]}; "
            f"vix={vix.index[0] if len(vix) else 'empty'}.."
            f"{vix.index[-1] if len(vix) else 'empty'})"
        )
    vix_aligned = vix.reindex(combined.index).ffill().bfill()
    if vix_aligned.isna().any():
        raise ValueError(
            "VIX alignment left NaN after ffill/bfill — likely no overlap"
        )

    # No-lookahead: lev[t] uses vix[t-1]. shift(1) leaves bar 0 NaN; bfill
    # uses bar 0's own value as the seed (the pre-period regime is unknown).
    vix_lag = vix_aligned.shift(1).bfill()

    is_stress = (vix_lag >= vix_threshold).to_numpy()
    lev = np.where(is_stress, lev_stress, lev_calm)
    out = lev * combined.to_numpy(float)
    return pd.Series(out, index=combined.index, name="iter048_output_lev")
