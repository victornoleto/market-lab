"""Iter 058 — Convex combo of iter 046 combined stream + HYG TSM.

iter 046's combined stream is loaded from its `results.json`
(`returns_series` per dataset), preserving its exact daily series.
HYG TSM is computed from HYG prices (same Tiingo window).

Citations
---------
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base
  preserved verbatim via its saved return stream.
* Asvanunt-Richardson 2017 JPM 43(2) DOI 10.3905/jpm.2017.43.2.090 —
  credit risk premium third stream rationale.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  combining streams compounds the deflated p-value when added Sharpe ≥
  base's noise floor.
"""

from __future__ import annotations

import pandas as pd


def combine_046_plus_hyg(
    r_046: pd.Series,
    r_hyg: pd.Series,
    *,
    w_046: float = 0.9,
    w_hyg: float = 0.1,
) -> pd.Series:
    """Convex combo of iter 046 stream and HYG TSM stream.

    Parameters
    ----------
    r_046 : pd.Series
        Iter 046 daily net combined returns (loaded from
        `iterations/046-*/results.json` `returns_series`).
    r_hyg : pd.Series
        HYG TSM daily net returns from
        `hyg_tsm.compute_hyg_tsm_returns`.
    w_046, w_hyg : float, default 0.9 / 0.1
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
        If w_046 < 0 or w_hyg < 0 or both are 0, or if the two
        return series have < 2 overlapping bars.
    """
    if w_046 < 0:
        raise ValueError(f"w_046 must be >= 0; got {w_046}")
    if w_hyg < 0:
        raise ValueError(f"w_hyg must be >= 0; got {w_hyg}")
    if (w_046 + w_hyg) <= 0:
        raise ValueError(
            f"w_046 + w_hyg must be > 0; got {w_046 + w_hyg}"
        )

    common = r_046.index.intersection(r_hyg.index)
    if len(common) < 2:
        raise ValueError(
            f"r_046 and r_hyg have <2 overlapping bars "
            f"(046={len(r_046)}, hyg={len(r_hyg)})"
        )
    a = r_046.loc[common]
    b = r_hyg.loc[common]
    combined = w_046 * a + w_hyg * b
    combined.name = "combined_046_plus_hyg"
    return combined
