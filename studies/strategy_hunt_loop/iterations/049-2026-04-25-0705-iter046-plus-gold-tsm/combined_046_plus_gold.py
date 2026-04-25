"""Iter 049 — 50/50 convex combo of iter 046 combined stream + gold TSM.

iter 046's combined stream is loaded from its `results.json`
(`returns_series` per dataset), avoiding the need to re-run iter 046's
3-leg simulator. Gold TSM is computed from GLD prices (same Tiingo
window as iter 046).

Citations
---------
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base
  preserved verbatim via its saved return stream.
* `[systematic_trading]` — Carver TSM single-asset rule (gold TSM).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  combining low-correlation streams compounds the deflated p-value.
"""

from __future__ import annotations

import pandas as pd


def combine_046_plus_gold(
    r_046: pd.Series,
    r_gold: pd.Series,
    *,
    w_046: float = 0.5,
    w_gold: float = 0.5,
) -> pd.Series:
    """Convex combo of iter 046 stream and gold TSM stream.

    Parameters
    ----------
    r_046 : pd.Series
        Iter 046 daily net combined returns (loaded from
        `iterations/046-*/results.json` `returns_series`).
    r_gold : pd.Series
        Gold TSM daily net returns from `gold_tsm.compute_gold_tsm_returns`.
    w_046, w_gold : float, default 0.5 each
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
        If w_046 < 0 or w_gold < 0 or both are 0.
    """
    if w_046 < 0:
        raise ValueError(f"w_046 must be >= 0; got {w_046}")
    if w_gold < 0:
        raise ValueError(f"w_gold must be >= 0; got {w_gold}")
    if (w_046 + w_gold) <= 0:
        raise ValueError(
            f"w_046 + w_gold must be > 0; got {w_046 + w_gold}"
        )

    common = r_046.index.intersection(r_gold.index)
    if len(common) < 2:
        raise ValueError(
            f"r_046 and r_gold have <2 overlapping bars "
            f"(046={len(r_046)}, gold={len(r_gold)})"
        )
    a = r_046.loc[common]
    b = r_gold.loc[common]
    combined = w_046 * a + w_gold * b
    combined.name = "combined_046_plus_gold"
    return combined
