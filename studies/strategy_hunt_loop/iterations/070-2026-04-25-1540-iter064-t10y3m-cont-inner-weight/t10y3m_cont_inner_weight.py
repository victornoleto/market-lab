"""Iter 070 — Continuous T10Y3M z-score inner-weight blend on iter 064 streams.

Mechanism
---------

Combine two pre-computed daily net-return streams (iter 046 base
combined stream ``r_046`` and Faber 2007 QQQ-200d-trend stream
``r_qqqt``) using a *continuous* regime classifier built from the
**10Y minus 3M Treasury term spread (T10Y3M)**:

    z[t]      = (T10Y3M[t-1] - rolling_mean_5y[t-1]) / rolling_std_5y[t-1]
                (BOTH the spread and the rolling stats are taken at t-1
                — strict no-peek)
    f(z[t])   = clip(0.5 - alpha * z[t], 0, 1)
    w_qqqt[t] = w_min + (w_max - w_min) * f(z[t])
    w_046[t]  = 1.0 - w_qqqt[t]                  # total ≡ 1.0
    cost[t]   = cost_bps * 1e-4 * |w_qqqt[t] - w_qqqt[t-1]|
    r_070[t]  = w_046[t]*r_046[t] + w_qqqt[t]*r_qqqt[t] - cost[t]

Default canonical config: ``w_min=0.05``, ``w_max=0.20`` (matching
iter 069's envelope), ``alpha=0.25`` (±2σ z maps to ±0.5 swing in f),
``lookback_z=1260`` (≈ 5 trading years), ``cost_bps=5.0``.

Direction: low z (curve flat/inverted ⇒ recession risk) → high w_qqqt
(more trend-following). High z (curve steep ⇒ expansion) → low
w_qqqt. This matches iter 069's reverse direction empirically vindicated
on 3/3 datasets.

Distinction vs prior iters
--------------------------

* iter 048 — VIX × OUTPUT scalar on iter 046 (lev 1.4/1.0). 83.
* iter 065 — VIX × OUTPUT scalar on iter 064 (lev 1.5/1.0). 74.
* iter 067 — σ⁻² overlay × OUTPUT scalar on iter 064 (cap 1.0). 74.
* iter 068 — VIX **binary** INNER weight on iter 064 (calm 0.20 / stress 0.05). 79.
* iter 069 — VIX **binary** INNER weight REVERSED (calm 0.05 / stress 0.20). 90.
* **iter 070 — T10Y3M *continuous* INNER weight on iter 064**. Same
  structural axis as 068/069 but (a) different signal (yield curve vs
  equity vol) and (b) continuous regime gradient instead of binary.

Citations
---------

* `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching.
* `[regime_change, p.27, ch.3]` — continuous regime indicator construction.
* `[stocks_on_the_move, p.21-30]` — Clenow regime-conditional momentum.
* Faber (2007) SSRN 962461 — single-asset 200d SMA TAA primitive.
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk parity (iter 046).
* `[volatility_trading, p.218]` — Sinclair σ⁻² (preserved inside iter 046).
* Estrella & Mishkin (1998) RES 80(1):45-61, DOI 10.1162/003465398557320 —
  T10Y3M as recession-leading indicator (1-12 month horizon).
* Estrella & Trubin (2006) FRBNY Current Issues 12(5) — practical
  implementation guidance for T10Y3M.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on regime signal.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[systematic_trading, ch.11]` — Carver IDM ≤ 2.5 (we sit at 1.0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def combine_with_t10y3m_cont_inner_weight(
    r_046: pd.Series,
    r_qqqt: pd.Series,
    term_spread: pd.Series,
    *,
    w_min: float = 0.05,
    w_max: float = 0.20,
    alpha: float = 0.25,
    lookback_z: int = 1260,
    cost_bps: float = 5.0,
    return_diagnostics: bool = False,
) -> pd.Series:
    """Combine iter 046 + QQQ_TREND streams with continuous T10Y3M z-score regime.

    Parameters
    ----------
    r_046 : pd.Series
        Iter 046 daily net combined returns (loaded from
        ``iterations/046-*/results.json`` ``returns_series``).
    r_qqqt : pd.Series
        QQQ-200d-trend daily net returns. Computed via
        ``iter064.qqq_trend.compute_qqq_trend_returns``.
    term_spread : pd.Series
        T10Y3M term spread daily series (DatetimeIndex). Reindexed onto
        ``r_046 ∩ r_qqqt`` with ``ffill().bfill()`` so it never carries
        NaN into the rolling stats.
    w_min, w_max : float
        Inner-weight bounds for ``w_qqqt[t]``. Must satisfy
        ``0 ≤ w_min ≤ w_max ≤ 1``.
    alpha : float
        Z-score sensitivity. Must be ≥ 0. ``alpha=0`` disables the
        regime gate (constant ``w_qqqt = (w_min + w_max) / 2``).
    lookback_z : int
        Rolling window for z-score mean and std. Must be ≥ 1.
        Recommended ~ 5 trading years (1260) to absorb a full business
        cycle.
    cost_bps : float
        Bps charged per unit ``|Δw_qqqt|`` (per bar of the change).
    return_diagnostics : bool
        If True, attach intermediate arrays to ``out.attrs["diagnostics"]``.

    Returns
    -------
    pd.Series
        Daily net returns indexed on ``r_046.index ∩ r_qqqt.index``,
        named ``iter070_t10y3m_cont``.

    Raises
    ------
    ValueError
        On out-of-range parameters or insufficient overlap.
    """
    if not (0.0 <= w_min <= 1.0):
        raise ValueError(f"w_min must be in [0, 1]; got {w_min}")
    if not (0.0 <= w_max <= 1.0):
        raise ValueError(f"w_max must be in [0, 1]; got {w_max}")
    if w_min > w_max:
        raise ValueError(f"w_min ({w_min}) must not exceed w_max ({w_max})")
    if alpha < 0.0:
        raise ValueError(f"alpha must be >= 0; got {alpha}")
    if lookback_z < 1:
        raise ValueError(f"lookback_z must be >= 1; got {lookback_z}")
    if cost_bps < 0.0:
        raise ValueError(f"cost_bps must be >= 0; got {cost_bps}")

    common = r_046.index.intersection(r_qqqt.index)
    if len(common) < 2:
        raise ValueError(
            f"r_046 and r_qqqt must have ≥ 2 overlapping bars; got {len(common)}"
        )

    a = r_046.loc[common].astype(float)
    b = r_qqqt.loc[common].astype(float)

    # Align T10Y3M onto the common index — ffill (carry last known) then
    # bfill (seed any leading gap before T10Y3M coverage starts).
    spread_aligned = term_spread.reindex(common).ffill().bfill()
    if spread_aligned.isna().any():
        raise ValueError("term_spread alignment left NaN after ffill/bfill")

    # Strict no-peek: at bar t we use spread[t-1] AND rolling stats up to t-1.
    spread_lag = spread_aligned.shift(1).bfill()  # bar 0 seeded with bar 0's value

    # Rolling mean & std *of the lagged series* — both shift(1) → never use
    # the current bar's spread anywhere.
    rmean = spread_lag.rolling(lookback_z, min_periods=lookback_z).mean()
    rstd = spread_lag.rolling(lookback_z, min_periods=lookback_z).std(ddof=0)

    # During warmup (rolling stats undefined) and when std == 0, fall back
    # to z = 0 (midpoint weight). Never NaN.
    z_arr = np.where(
        (rmean.notna() & rstd.notna() & (rstd > 0)).to_numpy(),
        (spread_lag.to_numpy() - rmean.to_numpy()) / np.where(rstd.to_numpy() > 0, rstd.to_numpy(), 1.0),
        0.0,
    )
    z_arr = np.nan_to_num(z_arr, nan=0.0, posinf=0.0, neginf=0.0)

    # Continuous regime mapping: f(z) = clip(0.5 - alpha * z, 0, 1).
    # When alpha = 0, f(z) ≡ 0.5 → midpoint weight (gate disabled).
    f = np.clip(0.5 - alpha * z_arr, 0.0, 1.0)
    w_qqqt = w_min + (w_max - w_min) * f
    w_qqqt = np.clip(w_qqqt, w_min, w_max)  # numerical safety
    w_046 = 1.0 - w_qqqt

    # Flip cost on |Δw_qqqt|. Bar 0 has no prior weight; assume same as bar 0.
    w_qqqt_prev = np.concatenate([[w_qqqt[0]], w_qqqt[:-1]])
    delta_w = np.abs(w_qqqt - w_qqqt_prev)
    cost = (cost_bps * 1e-4) * delta_w

    out_arr = w_046 * a.to_numpy() + w_qqqt * b.to_numpy() - cost
    out = pd.Series(out_arr, index=common, name="iter070_t10y3m_cont")

    if return_diagnostics:
        out.attrs["diagnostics"] = {
            "z": z_arr,
            "f": f,
            "w_046": w_046,
            "w_qqqt": w_qqqt,
            "delta_w": delta_w,
            "cost": cost,
            "spread_lag": spread_lag.to_numpy(),
            "rmean": rmean.to_numpy(),
            "rstd": rstd.to_numpy(),
        }
    return out
