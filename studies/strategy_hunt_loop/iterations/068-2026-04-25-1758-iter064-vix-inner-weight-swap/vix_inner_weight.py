"""Iter 068 — VIX-conditional INNER weight swap on iter 046 + QQQ_TREND streams.

Mechanism
---------

Combine two pre-computed daily net-return streams (iter 046 base
combined stream `r_046` and Faber 2007 QQQ-200d-trend stream `r_qqqt`)
with a binary VIX-regime-conditional convex weight:

    w_qqqt[t] = w_qqqt_calm   if VIX[t-1] <  vix_threshold
                w_qqqt_stress if VIX[t-1] >= vix_threshold
    w_046[t]  = 1.0 - w_qqqt[t]              # total exposure ≡ 1.0
    cost[t]   = cost_bps * 1e-4 * |w_qqqt[t] - w_qqqt[t-1]|
    r_068[t]  = w_046[t] * r_046[t] + w_qqqt[t] * r_qqqt[t] - cost[t]

Default canonical config: ``w_qqqt_calm=0.20``, ``w_qqqt_stress=0.05``,
``vix_threshold=20.0`` (Whaley 2009 long-run median), ``cost_bps=5.0``
per |Δw_qqqt|.

Distinction vs prior iters
--------------------------

* iter 048 — VIX gate × OUTPUT scalar on iter 046 (lev 1.4 / 1.0).
  Score 83. Total exposure 1.0-1.4 (varies).
* iter 065 — VIX gate × OUTPUT scalar on iter 064 (lev 1.5 / 1.0).
  Score 74. Total exposure 1.0-1.5.
* iter 067 — σ⁻² overlay × OUTPUT scalar on iter 064 (cap 1.0).
  Score 74. Total exposure 0.1-1.0.
* iter 068 — VIX gate × INNER MARKOWITZ WEIGHT between r_046 and
  r_qqqt. Total exposure strictly 1.0 every bar. Mechanism is
  qualitatively distinct: it does NOT scale total leverage, it
  reallocates BETWEEN sub-streams based on regime.

Citations
---------

* `[stocks_on_the_move, p.21-30]` — Clenow (2015), 200d SMA filter as
  regime gate inside a momentum portfolio.
* Faber (2007) SSRN 962461 — single-asset 200d SMA TAA primitive.
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk parity.
* `[volatility_trading, p.218]` — Sinclair σ⁻² scaling (preserved
  inside iter 046).
* Whaley (2009) JPM 35(3), DOI 10.3905/JPM.2009.35.3.098 — VIX
  ex-ante regime; threshold = 20 long-run median.
* Bekaert & Hoerova (2014) J Econometrics 183(2): 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
* Moskowitz, Ooi & Pedersen (2012) JFE 104(2),
  DOI 10.1016/j.jfineco.2011.11.003 — TSM regime conditionality.
* `[advances_fin_ml, ch.17-18]` — regime detection.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[systematic_trading, ch.11]` — Carver IDM ≤ 2.5 (we sit at 1.0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def combine_with_vix_inner_weight(
    r_046: pd.Series,
    r_qqqt: pd.Series,
    vix: pd.Series,
    *,
    w_qqqt_calm: float = 0.20,
    w_qqqt_stress: float = 0.05,
    vix_threshold: float = 20.0,
    cost_bps: float = 5.0,
    return_diagnostics: bool = False,
) -> pd.Series:
    """Combine iter 046 + QQQ_TREND streams with VIX-conditional inner weight.

    Parameters
    ----------
    r_046 : pd.Series
        Iter 046 daily net combined returns (e.g., loaded from
        ``iterations/046-*/results.json`` ``returns_series``).
    r_qqqt : pd.Series
        QQQ-200d-trend daily net returns (Faber 2007). Computed via
        ``iter064.qqq_trend.compute_qqq_trend_returns``.
    vix : pd.Series
        VIX series (DatetimeIndex). Reindexed to combined.index with
        ``ffill().bfill()``. Must overlap by ≥ 1 bar.
    w_qqqt_calm : float, default 0.20
        QQQ_TREND weight when VIX[t-1] < vix_threshold. Must be in [0, 1].
    w_qqqt_stress : float, default 0.05
        QQQ_TREND weight when VIX[t-1] >= vix_threshold. Must be in [0, 1].
    vix_threshold : float, default 20.0
        Whaley 2009 long-run median.
    cost_bps : float, default 5.0
        Bps per unit |Δw_qqqt| (charged on the bar of the flip only).
    return_diagnostics : bool, default False
        If True, attach intermediate arrays in ``out.attrs["diagnostics"]``
        — useful for tests and per-bar inspection.

    Returns
    -------
    pd.Series
        Daily net returns indexed on the inner-join of ``r_046`` and
        ``r_qqqt``, named ``iter068_vix_inner``.

    Raises
    ------
    ValueError
        On out-of-range weights, negative cost / threshold, < 2 overlapping
        bars, no VIX overlap.
    """
    if not (0.0 <= w_qqqt_calm <= 1.0):
        raise ValueError(f"w_qqqt_calm must be in [0, 1]; got {w_qqqt_calm}")
    if not (0.0 <= w_qqqt_stress <= 1.0):
        raise ValueError(f"w_qqqt_stress must be in [0, 1]; got {w_qqqt_stress}")
    if vix_threshold < 0:
        raise ValueError(f"vix_threshold must be >= 0; got {vix_threshold}")
    if cost_bps < 0:
        raise ValueError(f"cost_bps must be >= 0; got {cost_bps}")

    common = r_046.index.intersection(r_qqqt.index)
    if len(common) < 2:
        raise ValueError(
            f"r_046 and r_qqqt must have ≥ 2 overlapping bars; "
            f"got {len(common)}"
        )

    a = r_046.loc[common].astype(float)
    b = r_qqqt.loc[common].astype(float)

    overlap = vix.index.intersection(common)
    if len(overlap) == 0:
        raise ValueError(
            "vix index does not overlap r_046 ∩ r_qqqt"
        )
    vix_aligned = vix.reindex(common).ffill().bfill()
    if vix_aligned.isna().any():
        raise ValueError("VIX alignment left NaN after ffill/bfill")

    # Strict no-lookahead: weight at t uses VIX[t-1]. shift(1) leaves
    # bar 0 NaN; bfill seeds it with bar 0's own value (pre-period
    # regime is unobservable). Same convention as iter 048/065.
    vix_lag = vix_aligned.shift(1).bfill()

    is_stress = (vix_lag.to_numpy() >= vix_threshold)
    w_qqqt = np.where(is_stress, w_qqqt_stress, w_qqqt_calm).astype(float)
    w_046 = 1.0 - w_qqqt

    w_qqqt_prev = np.concatenate([[w_qqqt[0]], w_qqqt[:-1]])  # bar 0 has no prior; assume same regime
    delta_w = np.abs(w_qqqt - w_qqqt_prev)
    cost = (cost_bps * 1e-4) * delta_w

    out_arr = w_046 * a.to_numpy() + w_qqqt * b.to_numpy() - cost
    out = pd.Series(out_arr, index=common, name="iter068_vix_inner")

    if return_diagnostics:
        out.attrs["diagnostics"] = {
            "w_046": w_046,
            "w_qqqt": w_qqqt,
            "is_stress": is_stress,
            "delta_w": delta_w,
            "cost": cost,
            "vix_lag": vix_lag.to_numpy(),
        }
    return out
