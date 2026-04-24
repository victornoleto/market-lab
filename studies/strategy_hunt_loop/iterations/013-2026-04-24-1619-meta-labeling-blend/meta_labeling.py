"""Iter 013 — Meta-labeling classifier (AFML ch.3) on iter 008 vol-managed blend.

Architecture (per-bar):

    primary  (iter 008 blend)  →  (s_t, w_spy_t, w_tlt_t)   un-gated positions
    features (compute_features) →  (ρ_60_t, vix_z_t)        orthogonal info
    secondary (LogReg, walk-fwd) →  p_hat_t  ∈ [0, 1]       learned from past
    gate_t = 1.0 if p_hat_t > τ else 0.0
    pos_spy_g_t = s_t · w_spy_t · gate_t
    pos_tlt_g_t = s_t · w_tlt_t · gate_t
    gross_t    = pos_spy_g_t · r_spy[t] + pos_tlt_g_t · r_tlt[t]
    cost_t     = (|Δpos_spy_g| + |Δpos_tlt_g|) · cost_bps_per_leg
    net_t      = gross_t − cost_t

Training protocol (walk-forward, no look-ahead):

    - At bar t ≥ warmup, the model in effect was last fit at the most
      recent retrain boundary ≤ t.
    - Each refit uses the PAST `train_window` bars up to (but NOT
      including) the boundary.
    - Labels and features are both shifted by 1 bar so the model never
      sees its own target.
    - First decision at t = warmup_bars. Before that, gate = 1.0
      (passive blend).

Citations
---------
* `[advances_fin_ml, ch.3, p.50-56]` — meta-labeling pipeline (López de
  Prado 2018): secondary ML model decides whether to act on primary.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag rule; features lagged.
* `[advances_fin_ml, ch.7, p.103-112]` — walk-forward CV for finance.
* `[regime_change, ch.2]` — correlation-regime feature rationale.
* `[systematic_trading, ch.12]` — VIX as sizing covariate.
* `[risk_parity, p.10-11, ch.1]` — base inverse-variance weighting.
* Moreira & Muir (2017), JoF 72(4) — variance-scaling form.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

ITER_DIR = Path(__file__).resolve().parent
ITER006_DIR = ITER_DIR.parent / "006-2026-04-24-1027-vol-managed-60-40"
sys.path.insert(0, str(ITER006_DIR))

from stock_bond_blend import apply_blend_variance_target  # noqa: E402


# ---------------------------------------------------------------------------
# Pre-committed meta-labeling configuration
# ---------------------------------------------------------------------------

META_CFG: dict = {
    "cfg_id": "meta_lr_rho60_vixz252_w1000_r252",
    "feature_rho_window": 60,
    "feature_vix_zscore_window": 252,
    "train_window": 1000,
    "retrain_cadence": 252,
    "warmup_bars": 1260,  # ≈ train_window + feature warmup
    "decision_threshold": 0.5,
    "classifier": "LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=1000)",
    "random_state": 42,
}

# First bar at which features are guaranteed NaN-free.
# = max(feature_rho_window, feature_vix_zscore_window) + 1 lag
FEATURE_WARMUP_BARS = max(
    META_CFG["feature_rho_window"], META_CFG["feature_vix_zscore_window"]
) + 1  # +1 for the feature lag


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------


def compute_features(
    r_spy: pd.Series,
    r_tlt: pd.Series,
    vix: pd.Series,
    *,
    rho_window: int = META_CFG["feature_rho_window"],
    vix_z_window: int = META_CFG["feature_vix_zscore_window"],
) -> pd.DataFrame:
    """Compute lagged meta-labeling features.

    Returns a DataFrame with columns ``rho_60`` and ``vix_z`` indexed
    on ``r_spy.index``. All values are computed from data strictly
    prior to each row's timestamp (no look-ahead).
    """
    if not r_spy.index.equals(r_tlt.index):
        raise ValueError("r_spy and r_tlt must share the same index")
    vix_aligned = vix.reindex(r_spy.index, method="ffill")

    # Rolling correlation (uses bars [t-W+1 .. t]), then lag by 1 so
    # the feature at bar t uses [t-W .. t-1].
    rho_raw = r_spy.rolling(rho_window, min_periods=rho_window).corr(r_tlt)
    rho_lagged = rho_raw.shift(1)

    # VIX z-score: rolling mean + std of VIX level, then lag by 1.
    vix_mean = vix_aligned.rolling(vix_z_window, min_periods=vix_z_window).mean()
    vix_std = vix_aligned.rolling(vix_z_window, min_periods=vix_z_window).std(ddof=0)
    # Avoid division by zero — if std is ~0, z-score collapses to 0.
    vix_z = (vix_aligned - vix_mean) / vix_std.replace(0.0, np.nan)
    vix_z_lagged = vix_z.shift(1)

    features = pd.DataFrame({
        "rho_60": rho_lagged,
        "vix_z": vix_z_lagged,
    })
    return features


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def apply_blend_with_meta(
    r_spy: pd.Series,
    r_tlt: pd.Series,
    vix: pd.Series,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    cost_bps_per_leg: float = 0.0002,
    train_window: int = META_CFG["train_window"],
    retrain_cadence: int = META_CFG["retrain_cadence"],
    warmup_bars: int = META_CFG["warmup_bars"],
    decision_threshold: float = META_CFG["decision_threshold"],
    random_state: int = META_CFG["random_state"],
    periods_per_year: int = 252,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.DataFrame]:
    """Run iter 008 blend with a meta-labeling gate on top.

    Returns (net, pos_spy_g, pos_tlt_g, scale, meta_frame).

    ``meta_frame`` holds per-bar meta diagnostics: rho_60, vix_z, p_act,
    gate, label_realized.
    """
    # 1. Un-gated blend (baseline positions).
    net_blend, pos_spy, pos_tlt, scale = apply_blend_variance_target(
        r_spy, r_tlt,
        target_vol=target_vol, lookback=lookback, max_leverage=max_leverage,
        periods_per_year=periods_per_year, cost_bps_per_leg=cost_bps_per_leg,
    )
    # Align returns to blend's valid index.
    r_spy_v = r_spy.loc[scale.index].astype(float)
    r_tlt_v = r_tlt.loc[scale.index].astype(float)

    # 2. Features on the BLEND's valid index.
    features = compute_features(r_spy, r_tlt, vix)
    features = features.loc[scale.index]

    # 3. Realized labels: 1 if the UN-GATED net blend return at bar t+1
    #    > 0, else 0. Label at bar t is the outcome of holding the blend
    #    FROM t to t+1 given features known at close of t-1.
    #    We align labels on the bar whose features we'll use to predict.
    #    So feature at bar t → predict net_blend at bar t (which uses
    #    positions sized from bar t-1 data). This is the canonical
    #    "is tomorrow's bet profitable?" label.
    y_all = (net_blend > 0).astype(int)  # label at bar t = profitable(bar t)

    # 4. Walk-forward training + prediction.
    p_act = pd.Series(np.nan, index=scale.index, dtype=float)
    p_act.iloc[:warmup_bars] = 1.0  # pre-warmup: no model → default to full take

    X_all = features.to_numpy()
    y_all_np = y_all.to_numpy()

    n = len(scale)
    # Build list of training boundaries (absolute positions inside scale
    # index). We refit AT each boundary using the past `train_window`
    # bars with full features + labels strictly prior to the boundary.
    # First boundary at warmup_bars; subsequent every retrain_cadence.
    boundaries = list(range(warmup_bars, n, retrain_cadence))
    # Add final boundary if not exactly aligned — ensures every post-
    # warmup bar has a model.
    if not boundaries or boundaries[-1] < n - 1:
        boundaries.append(min(n, boundaries[-1] + retrain_cadence) if boundaries else warmup_bars)

    current_model: LogisticRegression | None = None
    last_boundary = warmup_bars
    for b in boundaries:
        # Fit model on past [b - train_window : b] bars. This uses ONLY
        # data strictly before bar b (labels + features computed with
        # lagged inputs), so no look-ahead.
        train_start = max(0, b - train_window)
        X_train = X_all[train_start:b]
        y_train = y_all_np[train_start:b]

        # Drop NaN rows (feature warmup bars early in the series).
        mask = ~np.isnan(X_train).any(axis=1)
        X_train_clean = X_train[mask]
        y_train_clean = y_train[mask]

        if len(y_train_clean) < 50 or len(np.unique(y_train_clean)) < 2:
            # Not enough data or degenerate labels; skip refit.
            # Keep previous model (or None → default 1.0).
            pass
        else:
            model = LogisticRegression(
                C=1.0, penalty="l2", solver="lbfgs",
                max_iter=1000, random_state=random_state,
            )
            model.fit(X_train_clean, y_train_clean)
            current_model = model

        # Predict for bars [last_boundary : b] inclusive if first refit,
        # else [b : min(b+retrain_cadence, n)].
        pred_start = b
        pred_end = min(b + retrain_cadence, n)
        if current_model is None:
            p_act.iloc[pred_start:pred_end] = 1.0  # pass-through
        else:
            X_pred = X_all[pred_start:pred_end]
            # Any NaN in pred features → default to 1.0 (pass-through).
            pred_mask = ~np.isnan(X_pred).any(axis=1)
            probs = np.ones(pred_end - pred_start, dtype=float)
            if pred_mask.any():
                probs_valid = current_model.predict_proba(X_pred[pred_mask])[:, 1]
                probs[pred_mask] = probs_valid
            p_act.iloc[pred_start:pred_end] = probs
        last_boundary = b

    # 5. Gate decisions.
    gate = pd.Series(1.0, index=scale.index, dtype=float)
    gate.loc[p_act <= decision_threshold] = 0.0
    # Pre-warmup stays at 1.0 (already set above when p_act=1.0).

    # 6. Re-apply gate to positions and recompute net.
    pos_spy_g = pos_spy * gate
    pos_tlt_g = pos_tlt * gate

    gross = pos_spy_g * r_spy_v + pos_tlt_g * r_tlt_v
    dpos_spy = pos_spy_g.diff().abs().fillna(pos_spy_g.iloc[0])
    dpos_tlt = pos_tlt_g.diff().abs().fillna(pos_tlt_g.iloc[0])
    cost = (dpos_spy + dpos_tlt) * cost_bps_per_leg
    net = (gross - cost).astype(float)

    meta_frame = pd.DataFrame({
        "rho_60": features["rho_60"],
        "vix_z": features["vix_z"],
        "p_act": p_act,
        "gate": gate,
        "label_realized": y_all,
    })

    net.name = "net"
    pos_spy_g.name = "pos_spy_meta"
    pos_tlt_g.name = "pos_tlt_meta"
    return net, pos_spy_g, pos_tlt_g, scale, meta_frame
