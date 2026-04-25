"""Iter 064 — Convex combo of iter 046 combined stream + QQQ trend stream.

iter 046's combined stream is loaded from its `results.json`
(`returns_series` per dataset), preserving its exact daily series.
QQQ_TREND is computed from QQQ prices (same Tiingo window).

Citations
---------
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base
  preserved verbatim via its saved return stream.
* Faber (2007) SSRN 962461 — single-asset 200-day SMA TAA primitive.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  combining streams compounds the deflated p-value when added Sharpe ≥
  base's noise floor.
"""

from __future__ import annotations

import pandas as pd


def combine_046_plus_qqqt(
    r_046: pd.Series,
    r_qqqt: pd.Series,
    *,
    w_046: float = 0.9,
    w_qqqt: float = 0.1,
) -> pd.Series:
    """Convex combo of iter 046 stream and QQQ trend stream.

    Parameters
    ----------
    r_046 : pd.Series
        Iter 046 daily net combined returns (loaded from
        `iterations/046-*/results.json` `returns_series`).
    r_qqqt : pd.Series
        QQQ trend daily net returns from
        `qqq_trend.compute_qqq_trend_returns`.
    w_046, w_qqqt : float, default 0.9 / 0.1
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
        If w_046 < 0 or w_qqqt < 0 or both are 0, or if the two
        return series have < 2 overlapping bars.
    """
    if w_046 < 0:
        raise ValueError(f"w_046 must be >= 0; got {w_046}")
    if w_qqqt < 0:
        raise ValueError(f"w_qqqt must be >= 0; got {w_qqqt}")
    if (w_046 + w_qqqt) <= 0:
        raise ValueError(
            f"w_046 + w_qqqt must be > 0; got {w_046 + w_qqqt}"
        )

    common = r_046.index.intersection(r_qqqt.index)
    if len(common) < 2:
        raise ValueError(
            f"r_046 and r_qqqt have <2 overlapping bars "
            f"(046={len(r_046)}, qqqt={len(r_qqqt)})"
        )
    a = r_046.loc[common]
    b = r_qqqt.loc[common]
    combined = w_046 * a + w_qqqt * b
    combined.name = "combined_046_plus_qqqt"
    return combined
