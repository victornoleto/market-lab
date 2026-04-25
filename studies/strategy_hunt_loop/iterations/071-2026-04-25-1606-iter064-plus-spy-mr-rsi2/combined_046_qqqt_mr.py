"""Iter 071 — 3-leg convex combiner for iter 046 + QQQ_TREND + SPY MR.

Generalises iter 064's 2-leg `combined_046_plus_qqqt.combine_046_plus_qqqt`
to a 3-leg form, with the third stream being SPY short-term mean-
reversion (Connors-Alvarez RSI(2) + Chan p.95 momentum gate).

Citations
---------
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base
  preserved verbatim.
* Faber (2007) SSRN 962461 — single-asset 200-day SMA TAA primitive
  (preserved verbatim from iter 064).
* `[algo_trading_chan, p.95, p.153-154]` — momentum-gated mean-
  reversion as a complementary stream.
"""

from __future__ import annotations

import pandas as pd


def combine_046_qqqt_mr(
    r_046: pd.Series,
    r_qqqt: pd.Series,
    r_mr: pd.Series,
    *,
    w_046: float,
    w_qqqt: float,
    w_mr: float,
) -> pd.Series:
    """3-leg convex combo on inner-joined daily index.

    Parameters
    ----------
    r_046, r_qqqt, r_mr : pd.Series
        Daily net returns of the 3 streams.
    w_046, w_qqqt, w_mr : float
        Convex weights. Each must be ≥ 0 and the sum must be > 0.
        Sum-to-1 is NOT enforced (caller may pass non-normalised weights
        for sensitivity sweeps), but in practice the iter 071 sweep
        always uses (1-w_mr)·0.90, (1-w_mr)·0.10, w_mr.

    Returns
    -------
    pd.Series
        Combined daily net returns, indexed on the inner-join of
        all 3 input series.

    Raises
    ------
    ValueError
        If any weight is negative, all are zero, or the inner-join
        has < 2 bars.
    """
    if w_046 < 0:
        raise ValueError(f"w_046 must be >= 0; got {w_046}")
    if w_qqqt < 0:
        raise ValueError(f"w_qqqt must be >= 0; got {w_qqqt}")
    if w_mr < 0:
        raise ValueError(f"w_mr must be >= 0; got {w_mr}")
    if (w_046 + w_qqqt + w_mr) <= 0:
        raise ValueError(
            f"sum of weights must be > 0; got {w_046 + w_qqqt + w_mr}"
        )
    common = r_046.index.intersection(r_qqqt.index).intersection(r_mr.index)
    if len(common) < 2:
        raise ValueError(
            f"inner-join has < 2 bars (046={len(r_046)}, "
            f"qqqt={len(r_qqqt)}, mr={len(r_mr)}, common={len(common)})"
        )
    combined = (
        w_046 * r_046.loc[common]
        + w_qqqt * r_qqqt.loc[common]
        + w_mr * r_mr.loc[common]
    )
    combined.name = "combined_046_qqqt_mr"
    return combined
