"""Iter 059 — Convex combo of iter 037 3-leg stream + HYG TSM.

iter 037's combined stream is loaded from its `results.json`
(`returns_series` per dataset, cfg `ntsx_3leg_preserved_60_45_45_spy_ief_gld`),
preserving its exact daily series. HYG TSM is computed from HYG prices
(same Tiingo window) via the engine vendored from iter 058.

The convex combiner is structurally identical to iter 058's
`combine_046_plus_hyg` — only the variable names change (037 vs 046).

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 multi-leg
  risk-parity decomposition (iter 037 base).
* Asvanunt-Richardson 2017 JPM 43(2) DOI 10.3905/jpm.2017.43.2.090 —
  credit risk premium third stream rationale.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  combining streams compounds the deflated p-value when added Sharpe ≥
  base's noise floor.
"""

from __future__ import annotations

import pandas as pd


def combine_037_plus_hyg(
    r_037: pd.Series,
    r_hyg: pd.Series,
    *,
    w_037: float = 0.9,
    w_hyg: float = 0.1,
) -> pd.Series:
    """Convex combo of iter 037 stream and HYG TSM stream.

    Parameters
    ----------
    r_037 : pd.Series
        Iter 037 daily net combined returns (loaded from
        `iterations/037-*/results.json` `returns_series` for cfg
        `ntsx_3leg_preserved_60_45_45_spy_ief_gld`).
    r_hyg : pd.Series
        HYG TSM daily net returns from
        `hyg_tsm.compute_hyg_tsm_returns`.
    w_037, w_hyg : float, default 0.9 / 0.1
        Convex combination weights. Must each be ≥ 0; not enforced
        sum=1 (caller may pass non-normalised weights for sensitivity
        runs).

    Returns
    -------
    pd.Series
        Combined daily net returns indexed on the inner-join of the
        two input series.

    Raises
    ------
    ValueError
        If w_037 < 0 or w_hyg < 0 or both are 0, or if the two
        return series have < 2 overlapping bars.
    """
    if w_037 < 0:
        raise ValueError(f"w_037 must be >= 0; got {w_037}")
    if w_hyg < 0:
        raise ValueError(f"w_hyg must be >= 0; got {w_hyg}")
    if (w_037 + w_hyg) <= 0:
        raise ValueError(
            f"w_037 + w_hyg must be > 0; got {w_037 + w_hyg}"
        )

    common = r_037.index.intersection(r_hyg.index)
    if len(common) < 2:
        raise ValueError(
            f"r_037 and r_hyg have <2 overlapping bars "
            f"(037={len(r_037)}, hyg={len(r_hyg)})"
        )
    a = r_037.loc[common]
    b = r_hyg.loc[common]
    combined = w_037 * a + w_hyg * b
    combined.name = "combined_037_plus_hyg"
    return combined
