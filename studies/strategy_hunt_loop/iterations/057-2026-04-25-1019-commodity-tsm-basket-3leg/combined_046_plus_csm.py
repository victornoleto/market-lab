"""Iter 057 — convex combo of iter 046 stream + commodity TSM basket.

iter 046's combined stream is loaded from its `results.json`
(`returns_series` per dataset), avoiding the need to re-run iter 046's
3-leg simulator. Commodity TSM basket is computed from
USO/UNG/SLV adjusted-close prices.

Citations
---------
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base
  preserved verbatim via its saved return stream.
* `[systematic_trading]` + Moskowitz-Ooi-Pedersen 2012 — commodity TSM.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  combining low-correlation streams compounds the deflated p-value.
"""

from __future__ import annotations

import pandas as pd


def combine_046_plus_csm(
    r_046: pd.Series,
    r_csm: pd.Series,
    *,
    w_046: float = 0.80,
    w_csm: float = 0.20,
) -> pd.Series:
    """Convex combo of iter 046 stream and commodity TSM basket.

    Parameters
    ----------
    r_046 : pd.Series
        Iter 046 daily net combined returns (loaded from
        ``iterations/046-*/results.json`` ``returns_series``).
    r_csm : pd.Series
        Commodity TSM basket daily net returns from
        ``commodity_tsm.compute_commodity_basket_tsm_returns``.
    w_046, w_csm : float, default 0.80 / 0.20
        Convex combination weights. Must each be ≥ 0; not normalised.

    Returns
    -------
    pd.Series
        Combined daily net returns indexed on the inner-join.

    Raises
    ------
    ValueError
        If w_046 < 0 or w_csm < 0 or both are 0, or inner-join < 2 bars.
    """
    if w_046 < 0:
        raise ValueError(f"w_046 must be >= 0; got {w_046}")
    if w_csm < 0:
        raise ValueError(f"w_csm must be >= 0; got {w_csm}")
    if (w_046 + w_csm) <= 0:
        raise ValueError(
            f"w_046 + w_csm must be > 0; got {w_046 + w_csm}"
        )

    common = r_046.index.intersection(r_csm.index)
    if len(common) < 2:
        raise ValueError(
            f"r_046 and r_csm have <2 overlapping bars "
            f"(046={len(r_046)}, csm={len(r_csm)})"
        )
    a = r_046.loc[common]
    b = r_csm.loc[common]
    combined = w_046 * a + w_csm * b
    combined.name = "combined_046_plus_csm"
    return combined
