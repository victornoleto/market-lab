"""Iter 029 — Inverse ratevol-gated LRS overlay helper (slot 6 only).

Phase 4 — iter 017 focused validation/refinement. Iter-local helper that
applies a multiplicative leverage scalar to on-leg returns ONLY on bars
where (a) the strategy is in RISK_ON state (on_signal lagged 1d == 1) AND
(b) the bond rate-vol regime gate reports STRESS (ratevol_gate lagged 1d ==
1). NaN gate values are treated as conservative no-LRS (matches iter 028's
warmup policy bit-exactly).

Distinct from iter 028's `apply_ratevol_gated_lrs_overlay`:
- iter 028: LRS applied when ratevol_gate==0 (calm regime, ~70% of ON
  days at rvp70 threshold; ~51% of all bars active by construction).
- iter 029: LRS applied when ratevol_gate==1 (STRESS regime, complementary
  ~30% of ON days; ~22% of all bars active by construction).

The two helpers are mathematical inverses on the binary regime split. Iter
029 is the symmetry diagnostic for iter 028: if iter 028 (calm-only) failed
to lift modern-era subperiod Sortino above Phase 3 floor 1.20, iter 029
tests the complementary regime subset to see whether stress-period LRS
exposure asymmetrically captures the missing alpha — or whether modern-era
softness is structural to the rearm primitive across BOTH regime subsets.

Iter-local helper (`loop_iterations/029-.../`); does NOT modify shared
modules per LOOP_PROTOCOL §"Scope limits".

Citations
---------
- [advances_fin_ml, p.208-211]: PRIMARY CSCV PBO mechanism-mix diversity —
  inverse regime gate uses the SAME mechanically-orthogonal bond-vol signal
  as iter 028, so PBO behaviour should match (~0.41 regime).
- [volatility_trading, p.58-60]: Sinclair on volatility cones — symmetry
  diagnostic on percentile-regime classification.
- [systematic_trading, ch.13, p.212]: Carver on vol-scaled regime
  thresholds — this iter inverts the polarity (LRS during stress) to
  attribute alpha by regime subset.
- [leverage_for_the_long_run, p.13, ch.3]: PRIMARY canonical RISK_ON LRS
  rule preserved; gating remains within-RISK_ON conditional.
- [leverage_for_the_long_run, p.5-6]: ann-vol-<40% sweet spot — note this
  helper INTENTIONALLY applies LRS during the high-realised-vol bars
  excluded by iter 028; expected vol drag is substantially higher per
  active LRS bar.
"""
from __future__ import annotations

import pandas as pd


def apply_inverse_ratevol_gated_lrs_overlay(
    on_leg_returns: pd.Series,
    on_signal: pd.Series,
    ratevol_gate: pd.Series,
    lrs_factor: float,
) -> pd.Series:
    """Scale on-leg returns by lrs_factor on STRESS-regime ON days only.

    On day t, the scaler is:
        scaler[t] = 1.0 + (lrs_factor - 1.0) * (on_lag[t] == 1) * (rv_lag[t] == 1)

    where on_lag = on_signal.shift(1) and rv_lag = ratevol_gate.shift(1).
    rv_lag == NaN is treated as no-LRS (conservative — strict OFF until
    pct_window warmup completes). on_lag == NaN is treated as 0 (no
    RISK_ON state, no LRS).

    For lrs_factor == 1.0 this reduces to on_leg_returns unchanged
    (calibration anchor sanity).

    The lag matches iter 014's `build_single_asset_on_leg` shift convention
    and iter 006's `ratevol_regime_gate` lag convention bit-exactly: signals
    computed on day t-1's information are applied at the open of day t.

    Mathematically the binary inverse of iter 028's
    `apply_ratevol_gated_lrs_overlay` on the ratevol_gate==0/1 split: if
    iter 028 multiplied returns by `1 + (k-1)*on*(rv==0)`, this helper
    multiplies by `1 + (k-1)*on*(rv==1)`. NaN bars receive scaler = 1.0
    in BOTH iter 028 and iter 029 — the warmup policy is identical.

    Parameters
    ----------
    on_leg_returns : pd.Series
        Daily on-leg returns from `build_single_asset_on_leg`.
    on_signal : pd.Series
        0/1 daily series marking RISK_ON state (vote-K=2 entry signal).
    ratevol_gate : pd.Series
        {0, 1, NaN} daily gate from `ratevol_regime_gate`. 1 = high
        bond-rate-vol regime (STRESS); 0 = calm; NaN = warmup (treated as
        no-LRS conservatively to match iter 028).
    lrs_factor : float
        Multiplicative leverage scalar applied on stress-regime ON days
        only. 1.0 = no overlay. >1.0 = boost. Iter 029 uses 1.20× (matches
        iter 027/028 magnitude — only the gating polarity flips).

    Returns
    -------
    pd.Series
        Aligned to on_leg_returns.index. Values: r_t * scaler[t].
    """
    if lrs_factor == 1.0:
        return on_leg_returns

    on_lag = on_signal.shift(1).reindex(on_leg_returns.index).fillna(0.0)
    rv_lag = ratevol_gate.shift(1).reindex(on_leg_returns.index)

    # Stress regime: gate == 1; NaN treated as conservative no-LRS (matches
    # iter 028's warmup policy bit-exactly).
    stress = (rv_lag == 1.0).astype(float)
    on_active = (on_lag == 1.0).astype(float)
    scaler = 1.0 + (lrs_factor - 1.0) * on_active * stress
    return on_leg_returns * scaler


def diagnose_inverse_lrs_active_pct(
    on_signal: pd.Series,
    ratevol_gate: pd.Series,
    on_leg_index: pd.Index,
) -> dict[str, float]:
    """Diagnostic: fraction of bars where the inverse LRS overlay is active.

    Returns:
        - lrs_active_pct: fraction of all bars where on_lag==1 AND rv_lag==1
        - on_active_pct: fraction of all bars where on_lag==1
        - stress_within_on_pct: fraction of ON bars where rv_lag==1
        - rv_warmup_pct: fraction of all bars where rv_lag is NaN

    Naming convention mirrors iter 028's `diagnose_lrs_active_pct` with
    `calm_within_on_pct` → `stress_within_on_pct` to flag the polarity
    flip. Verdict.json carries both fields under the same `lrs_diag` key
    so SUMMARY tables and dashboards can read them uniformly with
    iter 028.
    """
    on_lag = on_signal.shift(1).reindex(on_leg_index).fillna(0.0)
    rv_lag = ratevol_gate.shift(1).reindex(on_leg_index)

    on_active = (on_lag == 1.0)
    stress = (rv_lag == 1.0)
    rv_nan = rv_lag.isna()

    lrs_active = on_active & stress
    n_total = len(on_leg_index)

    lrs_active_pct = float(lrs_active.mean()) if n_total > 0 else 0.0
    on_active_pct = float(on_active.mean()) if n_total > 0 else 0.0
    rv_warmup_pct = float(rv_nan.mean()) if n_total > 0 else 0.0
    on_n = int(on_active.sum())
    stress_within_on_pct = (
        float((on_active & stress).sum() / on_n) if on_n > 0 else 0.0
    )

    return {
        "lrs_active_pct": lrs_active_pct,
        "on_active_pct": on_active_pct,
        "stress_within_on_pct": stress_within_on_pct,
        "rv_warmup_pct": rv_warmup_pct,
    }
