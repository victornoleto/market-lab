"""Iter 053 — 70/30 convex combo of iter 037 (3-leg static stack) + iter 046 (TOP-K #1).

Loads BOTH iter 037 and iter 046 saved combined return streams from
their respective ``results.json`` files (no re-simulation), then
inner-joins on date and applies fixed-weight convex combination:

    r_combined[t] = 0.70 * r_037[t] + 0.30 * r_046[t]

Differs from iter 045 (50/50 iter 037 + iter 039, score 81) by:

1. Replaces iter 039 (3-asset VRP basket, edu Sharpe 1.14) with iter
   046 (50/50 iter 041 + iter 039, edu Sharpe 1.20) — iter 046 is the
   TOP-K #1 strategy. Higher standalone Sharpe is the structural
   claim.
2. Weight 70/30 (NOT 50/50). The 0.70 design point was chosen via
   Markowitz pre-screen on the saved streams as the score-Pareto-
   optimum (highest combined Sharpe within the 3/3 CAGR floor pass
   plateau).

Pre-screen finding: corr(iter 037, iter 046) = 0.93-0.96 across all
three datasets (Kill F threshold 0.85). The composition is
near-degenerate as a Markowitz combination because iter 046's
sub-component iter 041 shares the SPY+IEF+GLD asset basis with iter
037. Predicted total score 84 (tie iter 051 at TOP-K #2).

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen (2013) risk-parity
  stack (iter 037 base architecture).
* `[volatility_trading, p.218]` — Sinclair (2013) VRP harvest
  (iter 039 sub-component embedded in iter 046).
* Whaley (2009), JPM 35(3) 98-105 — VIX regime classifier (iter 041
  sub-component embedded in iter 046).
* Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe identity
  (validated to 4 decimals on 12/12 datasets across iter 049-052).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
"""

from __future__ import annotations

import pandas as pd


def combine_037_plus_046(
    r_037: pd.Series,
    r_046: pd.Series,
    *,
    w_037: float = 0.70,
    w_046: float = 0.30,
) -> pd.Series:
    """Convex combo of iter 037 stack + iter 046 TOP-K #1 streams.

    Parameters
    ----------
    r_037 : pd.Series
        Iter 037 daily net return stream (loaded from
        ``iterations/037-*/results.json`` ``returns_series``).
    r_046 : pd.Series
        Iter 046 daily net return stream (loaded from
        ``iterations/046-*/results.json`` ``returns_series``).
    w_037, w_046 : float, default 0.70 and 0.30
        Convex combination weights. Must each be ≥ 0 and sum > 0. For
        canonical iter 053: 0.70 / 0.30 (score-Pareto-optimum per
        Markowitz pre-screen). The function does not enforce sum=1 —
        caller may pass non-normalised weights.

    Returns
    -------
    pd.Series
        Combined daily net returns indexed on the inner-join of the
        two input series.

    Raises
    ------
    ValueError
        If ``w_037 < 0`` or ``w_046 < 0`` or both are 0, or the two
        streams have <2 overlapping bars.
    """
    if w_037 < 0:
        raise ValueError(f"w_037 must be >= 0; got {w_037}")
    if w_046 < 0:
        raise ValueError(f"w_046 must be >= 0; got {w_046}")
    if (w_037 + w_046) <= 0:
        raise ValueError(
            f"w_037 + w_046 must be > 0; got {w_037 + w_046}"
        )

    common = r_037.index.intersection(r_046.index)
    if len(common) < 2:
        raise ValueError(
            f"r_037 and r_046 have <2 overlapping bars "
            f"(037={len(r_037)}, 046={len(r_046)})"
        )
    a = r_037.loc[common]
    b = r_046.loc[common]
    combined = w_037 * a + w_046 * b
    combined.name = "combined_037_plus_046"
    return combined
