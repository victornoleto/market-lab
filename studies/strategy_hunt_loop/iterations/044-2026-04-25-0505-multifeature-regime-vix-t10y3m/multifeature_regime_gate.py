"""Iter 044 — Multi-feature composite regime gate (VIX + T10Y3M).

Mechanism — generalises iter 041's single-feature VIX-level binary gate
to a TWO-feature standardised composite gate::

    z_VIX_t   = (VIX_t   - μ_VIX(window))   / σ_VIX(window)        # rolling
    z_neg_T_t = (-T_t    - μ_negT(window))  / σ_negT(window)       # rolling
    s_t       = w_VIX * z_VIX_t + w_negT * z_neg_T_t               # composite
    regime[t] = 1 (calm) if s_{t-1} <  τ
              = 0 (stress) if s_{t-1} >= τ

Same calm/stress weights as iter 041 (preserved verbatim) → only the
gate INPUT changes from "VIX_{t-1} vs 20" to "standardised composite
of (VIX, -T10Y3M)_{t-1} vs τ". The 1-bar lag is structural (no
look-ahead). Rolling z-score uses past `z_window` bars only — at
bar `t < z_window` the window expands from start.

Identity reduction: when `feature_weights["neg_t10y3m"] == 0` and the
composite threshold `τ` is set so the gate fires at the SAME flips
as iter 041's VIX-level gate at 20, this engine reproduces iter 041
exactly (see TDD spec `test_identity_reduction_when_only_vix_weight`).
The composite mechanism is a strict generalisation.

Citations
---------
* `[advances_fin_ml, ch.17-18]` — multi-feature regime detection.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day lag rule.
* `[risk_parity, ch.5]` — preserved 3-leg risk-parity stack.
* Estrella, A.; Hardouvelis, G.A. (1991), JF 46(2), 555-576,
  DOI 10.1111/j.1540-6261.1991.tb04617.x — term spread as recession
  leading indicator (T10Y3M canonical paper).
* Bauer-Mertens (2018), FRBSF Economic Letter 2018-07 — modern
  empirical confirmation of T10Y3M dominance for daily-frequency
  recession forecasts.
* Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098.
* Bekaert-Hoerova (2014), J Econometrics 183(2), SSRN 2294327.
* Hamilton (1989), Econometrica 57(2), DOI 10.2307/1912559.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd


def _validate_weights(name: str, w: Mapping[str, float]) -> None:
    for k in ("eq_w", "bd_w", "gld_w"):
        if k not in w:
            raise ValueError(f"{name} missing key {k!r}; got {dict(w)}")
        if w[k] < 0:
            raise ValueError(
                f"{name} weights must be non-negative; got {k}={w[k]}"
            )


def _validate_feature_weights(fw: Mapping[str, float]) -> None:
    for k in ("vix", "neg_t10y3m"):
        if k not in fw:
            raise ValueError(
                f"feature_weights missing key {k!r}; got {dict(fw)}"
            )


def rolling_zscore(s: pd.Series, window: int) -> pd.Series:
    """Causal rolling z-score with expanding warm-up.

    For t < window-1 the window expands from index 0 to t+1; for
    t >= window-1 the window is fixed at the most recent `window`
    bars. The returned series has the same index as `s`. Bars where
    the rolling std is zero (constant input) yield 0.0.
    """
    if window < 2:
        raise ValueError(f"window must be >= 2; got {window}")
    mu = s.rolling(window=window, min_periods=2).mean()
    sd = s.rolling(window=window, min_periods=2).std(ddof=0)
    z = (s - mu) / sd.where(sd > 0, other=np.nan)
    z = z.fillna(0.0)
    return z


def build_composite_regime(
    vix: pd.Series,
    term_spread: pd.Series,
    *,
    z_window: int = 252,
    feature_weights: Mapping[str, float] = None,
    stress_threshold: float = 0.0,
    lag_days: int = 1,
) -> tuple[pd.Series, pd.Series]:
    """Build the (regime, composite_score) pair from raw features.

    Parameters
    ----------
    vix, term_spread : pd.Series
        Daily VIX (level) and T10Y3M term spread (percent). Should be
        already aligned to the return index (ffilled and any
        pre-history bars filled). The function does NOT reindex.
    z_window : int
        Rolling z-score lookback (default 252 = 1y).
    feature_weights : mapping with keys "vix", "neg_t10y3m"
        Composite weights. Default {"vix": 0.5, "neg_t10y3m": 0.5}.
    stress_threshold : float
        Composite z-score above which the regime is stress (0).
    lag_days : int
        Lag applied to the composite before computing the regime
        label (default 1 — `regime[t]` uses `s[t-1]`).

    Returns
    -------
    (regime, composite_score)
        ``regime`` : pd.Series int 0/1 (1=calm, 0=stress).
        ``composite_score`` : pd.Series of the un-lagged composite
        score s_t (for diagnostics).
    """
    if feature_weights is None:
        feature_weights = {"vix": 0.5, "neg_t10y3m": 0.5}
    _validate_feature_weights(feature_weights)
    if not vix.index.equals(term_spread.index):
        raise ValueError(
            "vix and term_spread must share identical indices "
            f"(vix={len(vix)}, term_spread={len(term_spread)})"
        )

    z_vix = rolling_zscore(vix.astype(float), z_window)
    z_neg_t = rolling_zscore((-term_spread.astype(float)), z_window)
    s = (
        feature_weights["vix"] * z_vix
        + feature_weights["neg_t10y3m"] * z_neg_t
    )
    s.name = "composite"

    if lag_days > 0:
        s_lag = s.shift(lag_days)
        for i in range(min(lag_days, len(s_lag))):
            s_lag.iloc[i] = s.iloc[0]
    else:
        s_lag = s

    regime = (s_lag < stress_threshold).astype(int)
    regime.name = "regime"
    return regime, s


def apply_multifeature_regime_3leg(
    r_eq: pd.Series,
    r_bd: pd.Series,
    r_gld: pd.Series,
    vix: pd.Series,
    term_spread: pd.Series,
    *,
    calm_weights: Mapping[str, float],
    stress_weights: Mapping[str, float],
    z_window: int = 252,
    feature_weights: Mapping[str, float] = None,
    stress_threshold: float = 0.0,
    lag_days: int = 1,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[
    pd.Series, pd.DataFrame, pd.Series, pd.Series, pd.Series,
]:
    """Three-leg static stack with multi-feature composite regime gate.

    Returns
    -------
    (net, positions, scale, regime, composite_score)
    """
    _validate_weights("calm_weights", calm_weights)
    _validate_weights("stress_weights", stress_weights)
    if feature_weights is None:
        feature_weights = {"vix": 0.5, "neg_t10y3m": 0.5}

    if not (r_eq.index.equals(r_bd.index) and r_eq.index.equals(r_gld.index)):
        raise ValueError(
            "return streams must share identical indices "
            f"(eq={len(r_eq)}, bd={len(r_bd)}, gld={len(r_gld)})"
        )

    a = r_eq.astype(float)
    b = r_bd.astype(float)
    c = r_gld.astype(float)
    rmask = a.notna() & b.notna() & c.notna()
    a = a.loc[rmask]
    b = b.loc[rmask]
    c = c.loc[rmask]
    if len(a) == 0:
        raise ValueError("no overlapping non-NaN bars across return streams")

    vix_aligned = vix.reindex(a.index, method="ffill")
    if vix_aligned.isna().any():
        vix_aligned = vix_aligned.bfill().fillna(20.0)
    ts_aligned = term_spread.reindex(a.index, method="ffill")
    if ts_aligned.isna().any():
        ts_aligned = ts_aligned.bfill().fillna(0.0)

    regime, composite = build_composite_regime(
        vix_aligned,
        ts_aligned,
        z_window=z_window,
        feature_weights=feature_weights,
        stress_threshold=stress_threshold,
        lag_days=lag_days,
    )

    pos_eq = pd.Series(stress_weights["eq_w"], index=a.index, dtype=float)
    pos_bd = pd.Series(stress_weights["bd_w"], index=a.index, dtype=float)
    pos_gld = pd.Series(stress_weights["gld_w"], index=a.index, dtype=float)
    pos_eq.loc[regime == 1] = calm_weights["eq_w"]
    pos_bd.loc[regime == 1] = calm_weights["bd_w"]
    pos_gld.loc[regime == 1] = calm_weights["gld_w"]

    scale = pos_eq + pos_bd + pos_gld
    scale.name = "scale"

    gross = pos_eq * a + pos_bd * b + pos_gld * c

    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_bd = pos_bd.diff().abs().fillna(pos_bd.iloc[0])
    dpos_gld = pos_gld.diff().abs().fillna(pos_gld.iloc[0])
    cost = (dpos_eq + dpos_bd + dpos_gld) * cost_bps_per_leg

    net = (gross - cost).astype(float)
    net.name = "net"

    positions = pd.DataFrame(
        {"EQ": pos_eq, "BD": pos_bd, "GLD": pos_gld}, index=a.index,
    )
    return net, positions, scale, regime, composite
