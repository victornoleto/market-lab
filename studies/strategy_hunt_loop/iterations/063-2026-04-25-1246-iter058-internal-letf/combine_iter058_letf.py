"""Iter 063 — Composite combiner for iter 058 with LETF-substituted iter 041.

Builds:

    iter_046_LETF[t] = w_041 * iter_041_LETF[t] + w_039 * iter_039[t]
    iter_058_LETF[t] = w_046 * iter_046_LETF[t] + w_hyg * HYG_TSM[t]

with default weights matching iter 058 canonical: w_041 = w_039 = 0.5,
w_046 = 0.9, w_hyg = 0.1.

iter 039 stream is loaded from iter 046's saved subcomponent (matches
the basket VRP options primitive that doesn't admit linear LETF
substitution). HYG_TSM stream is loaded from iter 058's saved
subcomponent (preserves the credit-carry 3rd-stream verbatim).

Citations
---------
* `[risk_parity, ch.5]` — multi-leg risk-parity composition (iter 041
  base, regime tilts).
* `[volatility_trading, p.218]` — iter 039 cross-asset VRP basket
  preserved verbatim.
* Asvanunt-Richardson 2017 JPM 43(2) — HYG TSM credit risk premium
  preserved verbatim.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* Markowitz (1952), JoF 7(1) — convex combination of return streams.
"""

from __future__ import annotations

import pandas as pd


def combine_iter046_letf(
    r_041_letf: pd.Series,
    r_039: pd.Series,
    *,
    w_041: float = 0.5,
    w_039: float = 0.5,
) -> pd.Series:
    """Convex combo of LETF-substituted iter 041 + canonical iter 039.

    Inner-joins the two indexes; raises if <2 overlapping bars.
    """
    if w_041 < 0:
        raise ValueError(f"w_041 must be >= 0; got {w_041}")
    if w_039 < 0:
        raise ValueError(f"w_039 must be >= 0; got {w_039}")
    if (w_041 + w_039) <= 0:
        raise ValueError(
            f"w_041 + w_039 must be > 0; got {w_041 + w_039}"
        )
    common = r_041_letf.index.intersection(r_039.index)
    if len(common) < 2:
        raise ValueError(
            f"r_041_letf and r_039 have <2 overlapping bars "
            f"(041_letf={len(r_041_letf)}, 039={len(r_039)})"
        )
    a = r_041_letf.loc[common]
    b = r_039.loc[common]
    out = w_041 * a + w_039 * b
    out.name = "iter046_letf_combined"
    return out


def combine_iter058_letf(
    r_046_letf: pd.Series,
    r_hyg: pd.Series,
    *,
    w_046: float = 0.9,
    w_hyg: float = 0.1,
) -> pd.Series:
    """Convex combo of LETF-substituted iter 046 + HYG_TSM.

    Inner-joins the two indexes; raises if <2 overlapping bars.
    Mirrors `combine_046_plus_hyg` from iter 058 with w_046 / w_hyg
    defaults preserved.
    """
    if w_046 < 0:
        raise ValueError(f"w_046 must be >= 0; got {w_046}")
    if w_hyg < 0:
        raise ValueError(f"w_hyg must be >= 0; got {w_hyg}")
    if (w_046 + w_hyg) <= 0:
        raise ValueError(
            f"w_046 + w_hyg must be > 0; got {w_046 + w_hyg}"
        )
    common = r_046_letf.index.intersection(r_hyg.index)
    if len(common) < 2:
        raise ValueError(
            f"r_046_letf and r_hyg have <2 overlapping bars "
            f"(046_letf={len(r_046_letf)}, hyg={len(r_hyg)})"
        )
    a = r_046_letf.loc[common]
    b = r_hyg.loc[common]
    out = w_046 * a + w_hyg * b
    out.name = "iter058_letf_combined"
    return out
