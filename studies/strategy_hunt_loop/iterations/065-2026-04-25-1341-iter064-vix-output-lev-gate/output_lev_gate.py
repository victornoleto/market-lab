"""Iter 065 — VIX-conditional output leverage gate (1.5× calm / 1.0× stress) with futures-realistic borrow drag.

Mechanism
---------

Multiplies a daily net-return series by a regime-conditional scalar
derived from VIX[t-1], with an explicit borrow drag on the excess
leverage component::

    r_levered[t] = lev[t] * r_combined[t] - drag[t]
    lev[t]       = lev_calm   if VIX[t-1] <  vix_threshold
                   lev_stress if VIX[t-1] >= vix_threshold
    drag[t]      = (lev[t] - 1.0) * borrow_annual / 252

Default: ``lev_calm=1.5``, ``lev_stress=1.0``, ``vix_threshold=20``,
``borrow_annual=0.0225`` (= rf 0.02 + 25 bps futures basis).

The gate acts on the COMBINED OUTPUT (e.g., iter 064's saved combined
stream), preserving the inner regime dynamics of the iter 041 / iter 039 /
QQQ_TREND sub-components. No-lookahead: ``lev[t]`` uses ``vix.shift(1)``,
and the first bar's seed is filled via ``bfill`` (the pre-period regime
is unobservable).

Distinction vs prior iters
--------------------------

* iter 048 — VIX output gate on iter 046 (lev_calm=1.4, lev_stress=1.0,
  no explicit borrow drag). Score 83. This iter applies a higher lev
  on a higher-CAGR base AND models the borrow drag explicitly.
* iter 060 — Unconditional 1.5× external lev on iter 058 with
  futures borrow (drag 3/3). Score 79. This iter applies lev only
  during calm bars (~70%), reducing the average drag by ~30%.

Citations
---------

* `[leverage_for_the_long_run, ch.5]` — Hsiao & Williams 2017
  J. Index Investing. NTSX-style Treasury-futures financing.
* Whaley, R. E. (2009), JPM 35(3) 98-105,
  DOI 10.3905/JPM.2009.35.3.098 — VIX as ex-ante risk regime indicator.
* Bekaert, G. & Hoerova, M. (2014), J Econometrics 183(2) 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
* `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* `[risk_parity, ch.5]` — iter 046 base preserved via iter 064.
* Faber (2007) SSRN 962461 — QQQ_TREND component preserved via iter 064.
* Frazzini & Pedersen (2014), JFE 111(1) 1-25,
  DOI 10.1016/j.jfineco.2013.10.005 — borrow frictions on levered
  low-vol strategies.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_vix_lev_gate(
    combined: pd.Series,
    vix: pd.Series,
    *,
    lev_calm: float = 1.5,
    lev_stress: float = 1.0,
    vix_threshold: float = 20.0,
    borrow_annual: float = 0.0225,
    days_per_year: int = 252,
) -> pd.Series:
    """Apply VIX-regime output leverage gate with explicit borrow drag.

    Parameters
    ----------
    combined : pd.Series
        Daily net returns (e.g., iter 064's combined stream). Must have
        a DatetimeIndex with at least 2 bars.
    vix : pd.Series
        VIX series (DatetimeIndex). Reindexed to ``combined.index`` with
        ``ffill().bfill()``. Must overlap ``combined.index`` for at
        least one bar.
    lev_calm : float, default 1.5
        Multiplier applied when ``VIX[t-1] < vix_threshold``. Must be ≥ 0.
    lev_stress : float, default 1.0
        Multiplier applied when ``VIX[t-1] >= vix_threshold``. Must be ≥ 0.
    vix_threshold : float, default 20.0
        VIX threshold dividing calm from stress. Must be ≥ 0. Whaley 2009
        long-run median ≈ 20.
    borrow_annual : float, default 0.0225
        Annual borrow rate (futures-implied basis). Drag applied per bar:
        ``(lev[t] - 1.0) * borrow_annual / days_per_year``.
    days_per_year : int, default 252

    Returns
    -------
    pd.Series
        Levered daily-return series, same index as ``combined``,
        named ``iter065_vix_lev``.

    Raises
    ------
    ValueError
        If ``combined`` has fewer than 2 bars; ``vix`` does not overlap
        ``combined.index``; or any of ``lev_calm``, ``lev_stress``,
        ``vix_threshold``, or ``borrow_annual`` is negative.
    """
    if len(combined) < 2:
        raise ValueError(f"combined must have ≥ 2 bars; got {len(combined)}")
    if lev_calm < 0:
        raise ValueError(f"lev_calm must be ≥ 0; got {lev_calm}")
    if lev_stress < 0:
        raise ValueError(f"lev_stress must be ≥ 0; got {lev_stress}")
    if vix_threshold < 0:
        raise ValueError(f"vix_threshold must be ≥ 0; got {vix_threshold}")
    if borrow_annual < 0:
        raise ValueError(f"borrow_annual must be ≥ 0; got {borrow_annual}")

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
        raise ValueError("VIX alignment left NaN after ffill/bfill — likely no overlap")

    # No-lookahead: lev[t] uses vix[t-1]. shift(1) leaves bar 0 NaN; bfill
    # uses bar 0's own value as seed (pre-period regime is unobservable).
    vix_lag = vix_aligned.shift(1).bfill()

    is_stress = (vix_lag >= vix_threshold).to_numpy()
    lev = np.where(is_stress, lev_stress, lev_calm).astype(float)
    drag = (lev - 1.0) * borrow_annual / days_per_year
    out = lev * combined.to_numpy(dtype=float) - drag
    return pd.Series(out, index=combined.index, name="iter065_vix_lev")
