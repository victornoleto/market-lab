"""Iter 051 — 80/20 convex combo of iter 037 (3-leg static stack) + iter 026 (single-asset SPY VRP).

Loads BOTH iter 037 and iter 026 saved combined return streams from
their respective ``results.json`` files (no re-simulation), then
inner-joins on date and applies fixed-weight convex combination:

    r_combined[t] = 0.80 * r_037[t] + 0.20 * r_026[t]

Differs from iter 045 (037+039 50/50, score 81) by:

1. Replaces iter 039 (3-asset basket VRP) with iter 026 (single-asset
   SPY VRP). iter 026 has tighter DSR (worst-p 0.083) and lower vol.
2. Asymmetric weights 80/20 (NOT 50/50). The 80/20 design point was
   chosen via Markowitz pre-screen on the saved streams as the
   **score-optimum** (3/3 CAGR floor pass + 3/3 Sharpe edge pass)
   rather than the **Sharpe-optimum** (which is w_037≈0.15).

The Markowitz formula was empirically validated to 4 decimals in
iter 050; this iteration relies on that validation as the basis for
the score-aware composition design.

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
  (iter 037 base architecture).
* `[volatility_trading, p.218]` — Sinclair (2013) single-asset VRP
  harvest (iter 026 base architecture).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe identity.
* Bondarenko (2014), QJF 4(3) 1450015 — empirical SPX VRP magnitude.
* Carr-Wu (2009), RFS 22(3) 1311-1341 — variance risk premia framework.
* Erb-Harvey (2006), FAJ 62(2) — gold's strategic role in iter 037.
"""

from __future__ import annotations

import pandas as pd


def combine_037_plus_026(
    r_037: pd.Series,
    r_026: pd.Series,
    *,
    w_037: float = 0.80,
    w_026: float = 0.20,
) -> pd.Series:
    """Convex combo of iter 037 stack + iter 026 VRP streams.

    Parameters
    ----------
    r_037 : pd.Series
        Iter 037 daily net return stream (loaded from
        ``iterations/037-*/results.json`` ``returns_series``).
    r_026 : pd.Series
        Iter 026 daily net return stream (loaded from
        ``iterations/026-*/results.json`` ``returns_series``).
    w_037, w_026 : float, default 0.80 and 0.20
        Convex combination weights. Must each be ≥ 0 and sum > 0.
        For canonical iter 051: 0.80 / 0.20 (score-Pareto-optimum
        per Markowitz pre-screen). The function does not enforce
        sum=1 — caller may pass non-normalised weights.

    Returns
    -------
    pd.Series
        Combined daily net returns indexed on the inner-join of the
        two input series.

    Raises
    ------
    ValueError
        If ``w_037 < 0`` or ``w_026 < 0`` or both are 0, or the two
        streams have <2 overlapping bars.
    """
    if w_037 < 0:
        raise ValueError(f"w_037 must be >= 0; got {w_037}")
    if w_026 < 0:
        raise ValueError(f"w_026 must be >= 0; got {w_026}")
    if (w_037 + w_026) <= 0:
        raise ValueError(
            f"w_037 + w_026 must be > 0; got {w_037 + w_026}"
        )

    common = r_037.index.intersection(r_026.index)
    if len(common) < 2:
        raise ValueError(
            f"r_037 and r_026 have <2 overlapping bars "
            f"(037={len(r_037)}, 026={len(r_026)})"
        )
    a = r_037.loc[common]
    b = r_026.loc[common]
    combined = w_037 * a + w_026 * b
    combined.name = "combined_037_plus_026"
    return combined
