"""Iter 028 — Ratevol-gated LRS overlay helper (slot 6 only).

Phase 4 — iter 017 focused validation/refinement. Iter-local helper that
applies a multiplicative leverage scalar to on-leg returns ONLY on bars
where (a) the strategy is in RISK_ON state (on_signal lagged 1d == 1) AND
(b) the bond rate-vol regime gate reports calm (ratevol_gate lagged 1d == 0
or NaN-as-conservative-OFF).

Distinct from iter 024's `apply_unconditional_lrs_overlay`:
- iter 024-027: LRS factor applied on every ON day unconditionally (~70-80%
  of trading days).
- iter 028: LRS factor applied on ON days where ratevol_gate==0 (calm rate
  regime, ~70% of ON days at rvp70 threshold by construction; high rate-vol
  bars get bare 2× exposure with no overlay).

Mechanism rationale: iter 027 closed the LRS magnitude scan and observed
modern-era subperiod Sortino (1.124-1.144) lands BELOW the Phase 3 floor
1.20 — modern-era softness identified as structural to the rearm primitive.
This iter's hypothesis: gating LRS to calm-rate regimes prunes LRS exposure
during bond-vol stress windows (1980s Volcker, 1994 rate shock, 2008 GFC,
2020 COVID, 2022 hike cycle) which historically cluster with equity-vol
spikes that amplify daily-rebalance vol-drag asymmetry on the LRS overlay.

Iter-local helper (`runs/post_close/028-.../`); does NOT modify shared
modules per LOOP_PROTOCOL §"Scope limits".

Citations
---------
- [advances_fin_ml, p.208-211]: PRIMARY CSCV PBO mechanism-mix diversity —
  bond-vol regime gate is mechanically orthogonal to equity-rearm signal,
  preserves PBO-decoupled framework established in iter 024.
- [volatility_trading, p.58-60]: Sinclair on volatility cones — current
  realised vol placed against historical percentile distribution as
  regime-detection primitive (iter 006 ratevol gate is direct
  implementation).
- [systematic_trading, ch.13, p.212]: Carver on vol-scaled regime
  thresholds — supports gating leverage application to calm regimes.
- [leverage_for_the_long_run, p.13, ch.3]: PRIMARY canonical RISK_ON LRS
  rule — preserves "leverage only when above MA daily" convention; regime
  gating is a within-RISK_ON conditional refinement, not a replacement.
- [leverage_for_the_long_run, p.5-6]: ann-vol-<40% sweet spot motivation
  for vol-regime gating of LRS overlays.
"""
from __future__ import annotations

import pandas as pd


def apply_ratevol_gated_lrs_overlay(
    on_leg_returns: pd.Series,
    on_signal: pd.Series,
    ratevol_gate: pd.Series,
    lrs_factor: float,
) -> pd.Series:
    """Scale on-leg returns by lrs_factor on calm-rate-regime ON days only.

    On day t, the scaler is:
        scaler[t] = 1.0 + (lrs_factor - 1.0) * (on_lag[t] == 1) * (rv_lag[t] == 0)

    where on_lag = on_signal.shift(1) and rv_lag = ratevol_gate.shift(1).
    rv_lag == NaN is treated as no-LRS (conservative — strict OFF until
    pct_window warmup completes). on_lag == NaN is treated as 0 (no
    RISK_ON state, no LRS).

    For lrs_factor == 1.0 this reduces to on_leg_returns unchanged
    (calibration anchor sanity).

    The lag matches iter 014's `build_single_asset_on_leg` shift convention
    and iter 006's `ratevol_regime_gate` lag convention: signals computed
    on day t-1's information are applied at open of day t.

    Parameters
    ----------
    on_leg_returns : pd.Series
        Daily on-leg returns from `build_single_asset_on_leg`.
    on_signal : pd.Series
        0/1 daily series marking RISK_ON state (vote-K=2 entry signal).
    ratevol_gate : pd.Series
        {0, 1, NaN} daily gate from `ratevol_regime_gate`. 1 = high
        bond-rate-vol regime; 0 = calm; NaN = warmup (treated as no-LRS
        conservatively).
    lrs_factor : float
        Multiplicative leverage scalar applied on calm-rate ON days only.
        1.0 = no overlay. >1.0 = boost. Iter 028 uses 1.20× (matches iter
        027 slot 6's magnitude — only the gating dimension changes).

    Returns
    -------
    pd.Series
        Aligned to on_leg_returns.index. Values: r_t * scaler[t].
    """
    if lrs_factor == 1.0:
        return on_leg_returns

    on_lag = on_signal.shift(1).reindex(on_leg_returns.index).fillna(0.0)
    rv_lag = ratevol_gate.shift(1).reindex(on_leg_returns.index)

    # Calm regime: gate == 0; NaN treated as conservative no-LRS (matches
    # the iter 024-027 ratevol-off-leg policy of "default to safe asset
    # during warmup").
    calm = (rv_lag == 0.0).astype(float)
    on_active = (on_lag == 1.0).astype(float)
    scaler = 1.0 + (lrs_factor - 1.0) * on_active * calm
    return on_leg_returns * scaler


def diagnose_lrs_active_pct(
    on_signal: pd.Series,
    ratevol_gate: pd.Series,
    on_leg_index: pd.Index,
) -> dict[str, float]:
    """Diagnostic: fraction of bars where the LRS overlay is active.

    Returns:
        - lrs_active_pct: fraction of all bars where on_lag==1 AND rv_lag==0
        - on_active_pct: fraction of all bars where on_lag==1
        - calm_within_on_pct: fraction of ON bars where rv_lag==0 (regime
          gating efficiency)
        - rv_warmup_pct: fraction of all bars where rv_lag is NaN
    """
    on_lag = on_signal.shift(1).reindex(on_leg_index).fillna(0.0)
    rv_lag = ratevol_gate.shift(1).reindex(on_leg_index)

    on_active = (on_lag == 1.0)
    calm = (rv_lag == 0.0)
    rv_nan = rv_lag.isna()

    lrs_active = on_active & calm
    n_total = len(on_leg_index)

    lrs_active_pct = float(lrs_active.mean()) if n_total > 0 else 0.0
    on_active_pct = float(on_active.mean()) if n_total > 0 else 0.0
    rv_warmup_pct = float(rv_nan.mean()) if n_total > 0 else 0.0
    on_n = int(on_active.sum())
    calm_within_on_pct = (
        float((on_active & calm).sum() / on_n) if on_n > 0 else 0.0
    )

    return {
        "lrs_active_pct": lrs_active_pct,
        "on_active_pct": on_active_pct,
        "calm_within_on_pct": calm_within_on_pct,
        "rv_warmup_pct": rv_warmup_pct,
    }
