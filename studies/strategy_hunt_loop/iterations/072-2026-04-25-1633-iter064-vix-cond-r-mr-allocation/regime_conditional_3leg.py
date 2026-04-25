"""Iter 072 — VIX-conditional 3-leg combiner: r_046 + r_qqqt + regime-cond r_mr.

Mechanism
---------

Combine three pre-computed daily net-return streams (iter 046 base
combined stream `r_046`, Faber 2007 200d-SMA QQQ-trend `r_qqqt`, and
Connors-Alvarez RSI(2) SPY mean-reversion `r_mr` from iter 071) with a
VIX-binary regime-conditional weight on the 3rd stream:

    w_mr[t]    = w_mr_calm   if VIX[t-1] <  threshold
                 w_mr_stress if VIX[t-1] >= threshold
    w_046[t]   = (1 - w_mr[t]) * 0.90        # preserve iter 064 9:1 ratio
    w_qqqt[t]  = (1 - w_mr[t]) * 0.10
    cost[t]    = cost_bps * 1e-4 * |w_mr[t] - w_mr[t-1]|
    r_072[t]   = w_046[t]·r_046[t]
                 + w_qqqt[t]·r_qqqt[t]
                 + w_mr[t]·r_mr[t] - cost[t]

Total exposure is strictly 1.0 every bar (Σw ≡ 1). Flip cost is charged
once per regime transition (5 bps default per |Δw_mr|).

Distinction vs prior iters
--------------------------

* iter 064 — STATIC 2-stream (90% r_046 + 10% r_qqqt), no regime.
* iter 068/069 — VIX-conditional INNER weight BETWEEN r_046 ↔ r_qqqt
  (within iter 064). w_mr does not exist.
* iter 070 — Continuous T10Y3M z-score INNER weight on iter 064.
* iter 071 — STATIC 3-stream blend (proportional 9:1 base + static w_mr).
* **iter 072 — Regime-conditional weight on the 3rd STREAM (r_mr).**
  Composes iter 069's binary-VIX classifier with iter 071's validated
  calm-aggressive r_mr stream — hierarchical regime allocation.

Citations
---------

* `[algo_trading_chan, p.95, p.153-154]` — Chan: momentum filter on MR
  + MR/momentum complementarity in regime-based portfolio allocation.
* Whaley, R. E. (2009). "Understanding the VIX." JPM 35(3): 98-105.
  DOI 10.3905/JPM.2009.35.3.098 — VIX threshold = 20 long-run median.
* Bekaert, G., & Hoerova, M. (2014). J Econometrics 183(2): 181-192.
  SSRN 2294327 — VIX as risk-aversion + uncertainty proxy.
* Connors, L., & Alvarez, C. (2009). *Short Term Trading Strategies
  That Work*. ISBN 978-0-9755513-2-7. Connors-Alvarez VIX timing rule.
* Lo, A. W., & MacKinlay, A. C. (1988). RFS 1(1): 41-66.
  DOI 10.1093/rfs/1.1.41 — short-horizon equity mean-reversion.
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base.
* Faber (2007), SSRN 962461 + `[stocks_on_the_move, p.21-30]` — iter 064.
* `[advances_fin_ml, ch.17-18]` — regime detection / structural breaks.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX (no peek).
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* `[systematic_trading, ch.11]` — Carver IDM ≤ 2.5 (sit at 1.0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def combine_regime_cond_3leg(
    r_046: pd.Series,
    r_qqqt: pd.Series,
    r_mr: pd.Series,
    vix: pd.Series,
    *,
    w_mr_calm: float,
    w_mr_stress: float,
    vix_threshold: float = 20.0,
    cost_bps: float = 5.0,
    return_diagnostics: bool = False,
) -> pd.Series:
    """3-leg blend with VIX-conditional weight on the 3rd stream (r_mr).

    Parameters
    ----------
    r_046 : pd.Series
        Iter 046 daily net combined returns (saved verbatim).
    r_qqqt : pd.Series
        Faber 2007 200d-SMA QQQ-trend daily net returns.
    r_mr : pd.Series
        Iter 071 SPY short-term mean-reversion daily net returns
        (Connors-Alvarez RSI(2) + Chan p.95 momentum gate).
    vix : pd.Series
        VIX series (DatetimeIndex). Reindexed to combined.index with
        ``ffill().bfill()``. Must overlap by ≥ 1 bar.
    w_mr_calm : float
        r_mr weight when VIX[t-1] < ``vix_threshold`` (calm regime).
        Must be in [0, 1].
    w_mr_stress : float
        r_mr weight when VIX[t-1] >= ``vix_threshold`` (stress regime).
        Must be in [0, 1].
    vix_threshold : float, default 20.0
        Whaley 2009 long-run median.
    cost_bps : float, default 5.0
        Bps per unit |Δw_mr| (charged once per regime transition).
    return_diagnostics : bool, default False
        If True, attach intermediate arrays in ``out.attrs["diagnostics"]``.

    Returns
    -------
    pd.Series
        Daily net returns indexed on the inner-join of r_046, r_qqqt, r_mr,
        named ``iter072_regime_cond_3leg``.

    Raises
    ------
    ValueError
        On out-of-range weights, negative cost / threshold, < 2 overlapping
        bars, or no VIX overlap.
    """
    if not (0.0 <= w_mr_calm <= 1.0):
        raise ValueError(f"w_mr_calm must be in [0, 1]; got {w_mr_calm}")
    if not (0.0 <= w_mr_stress <= 1.0):
        raise ValueError(f"w_mr_stress must be in [0, 1]; got {w_mr_stress}")
    if vix_threshold < 0:
        raise ValueError(f"vix_threshold must be >= 0; got {vix_threshold}")
    if cost_bps < 0:
        raise ValueError(f"cost_bps must be >= 0; got {cost_bps}")

    common = r_046.index.intersection(r_qqqt.index).intersection(r_mr.index)
    if len(common) < 2:
        raise ValueError(
            f"r_046 ∩ r_qqqt ∩ r_mr must have ≥ 2 overlapping bars; "
            f"got {len(common)}"
        )

    a = r_046.loc[common].astype(float)
    b = r_qqqt.loc[common].astype(float)
    c = r_mr.loc[common].astype(float)

    overlap = vix.index.intersection(common)
    if len(overlap) == 0:
        raise ValueError("vix index does not overlap r_046 ∩ r_qqqt ∩ r_mr")
    vix_aligned = vix.reindex(common).ffill().bfill()
    if vix_aligned.isna().any():
        raise ValueError("VIX alignment left NaN after ffill/bfill")

    # Strict no-lookahead: weight at t uses VIX[t-1]. shift(1) leaves bar 0
    # NaN; bfill seeds with bar 0's own value (pre-period regime
    # unobservable) — same convention as iter 048/065/068/069.
    vix_lag = vix_aligned.shift(1).bfill()

    is_stress = (vix_lag.to_numpy() >= vix_threshold)
    w_mr = np.where(is_stress, w_mr_stress, w_mr_calm).astype(float)
    w_base = 1.0 - w_mr
    # Preserve iter 064 9:1 ratio between r_046 and r_qqqt within base.
    w_046 = w_base * 0.90
    w_qqqt = w_base * 0.10

    w_mr_prev = np.concatenate([[w_mr[0]], w_mr[:-1]])
    delta_w_mr = np.abs(w_mr - w_mr_prev)
    cost = (cost_bps * 1e-4) * delta_w_mr

    out_arr = (
        w_046 * a.to_numpy()
        + w_qqqt * b.to_numpy()
        + w_mr * c.to_numpy()
        - cost
    )
    out = pd.Series(out_arr, index=common, name="iter072_regime_cond_3leg")

    if return_diagnostics:
        out.attrs["diagnostics"] = {
            "w_046": w_046,
            "w_qqqt": w_qqqt,
            "w_mr": w_mr,
            "is_stress": is_stress,
            "delta_w_mr": delta_w_mr,
            "cost": cost,
            "vix_lag": vix_lag.to_numpy(),
        }
    return out
