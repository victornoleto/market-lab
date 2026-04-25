"""Iter 052 — 82/18 convex combo of iter 041 (regime-weighted stack) + iter 026 (single-asset SPY VRP).

Loads BOTH iter 041 and iter 026 saved combined return streams from
their respective ``results.json`` files (no re-simulation), then
inner-joins on date and applies fixed-weight convex combination:

    r_combined[t] = 0.82 * r_041[t] + 0.18 * r_026[t]

Differs from iter 051 (037+026 80/20, score 84) by:

1. Replaces iter 037 (3-leg static stack, edu Sharpe 0.98) with iter 041
   (regime-weighted stack with VIX-gated calm/stress weights, edu
   Sharpe 1.027). The +0.05 standalone Sharpe lift on the binding
   dataset is the structural claim.
2. Lower correlation: corr(041, 026) = 0.37/0.37/0.45 vs corr(037, 026)
   = 0.57/0.55/0.60 in iter 051 — better Markowitz diversification gain.
3. Weight 82/18 (NOT 80/20). The 0.82 design point was chosen via
   Markowitz pre-screen on the saved streams as the score-Pareto-
   optimum (highest combined Sharpe within the 2/3 CAGR floor pass
   plateau).

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen (2013) risk-parity
  stack (iter 041 base architecture, regime-modulated).
* Whaley, R.E. (2009), JPM 35(3) 98-105 — VIX regime classification.
* `[volatility_trading, p.218]` — Sinclair (2013) single-asset VRP
  harvest (iter 026 base architecture).
* Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe identity
  (validated to 4 decimals on 9/9 datasets across iter 049/050/051).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* Bondarenko (2014), QJF 4(3) 1450015 — empirical SPX VRP magnitude.
* Erb-Harvey (2006), FAJ 62(2) — gold's strategic role in iter 041 stack.
"""

from __future__ import annotations

import pandas as pd


def combine_041_plus_026(
    r_041: pd.Series,
    r_026: pd.Series,
    *,
    w_041: float = 0.82,
    w_026: float = 0.18,
) -> pd.Series:
    """Convex combo of iter 041 stack + iter 026 VRP streams.

    Parameters
    ----------
    r_041 : pd.Series
        Iter 041 daily net return stream (loaded from
        ``iterations/041-*/results.json`` ``returns_series``).
    r_026 : pd.Series
        Iter 026 daily net return stream (loaded from
        ``iterations/026-*/results.json`` ``returns_series``).
    w_041, w_026 : float, default 0.82 and 0.18
        Convex combination weights. Must each be ≥ 0 and sum > 0. For
        canonical iter 052: 0.82 / 0.18 (score-Pareto-optimum per
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
        If ``w_041 < 0`` or ``w_026 < 0`` or both are 0, or the two
        streams have <2 overlapping bars.
    """
    if w_041 < 0:
        raise ValueError(f"w_041 must be >= 0; got {w_041}")
    if w_026 < 0:
        raise ValueError(f"w_026 must be >= 0; got {w_026}")
    if (w_041 + w_026) <= 0:
        raise ValueError(
            f"w_041 + w_026 must be > 0; got {w_041 + w_026}"
        )

    common = r_041.index.intersection(r_026.index)
    if len(common) < 2:
        raise ValueError(
            f"r_041 and r_026 have <2 overlapping bars "
            f"(041={len(r_041)}, 026={len(r_026)})"
        )
    a = r_041.loc[common]
    b = r_026.loc[common]
    combined = w_041 * a + w_026 * b
    combined.name = "combined_041_plus_026"
    return combined
