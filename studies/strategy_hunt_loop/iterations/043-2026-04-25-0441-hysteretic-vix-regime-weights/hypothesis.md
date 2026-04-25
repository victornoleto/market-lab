# Iteration 043 — Hysteretic single-axis VIX gate on iter 041 weight stack

## Hypothesis

Iter 041 (🥇 STRONG, score **84/100**) is the loop-record. Its DSR
worst-p (0.168) lifted to criterion 3 = 5/15 (vs iter 037's 0/15) by
*adding a regime classifier* over iter 037's static stack — but not
high enough to escape the deflated-Sharpe band (p < 0.10 needed for
+5 score → 89). Iter 042 attempted to compound iter 041's weight
modulation with iter 038's leverage modulation; this **regressed
DSR to 0.216** (criterion 3 dropped back to 0/15) and the score fell
to 74. The iter 042 final report identified the mechanism: amplifying
*conditional exposure asymmetry* adds path variance faster than mean
return, so the deflator (which penalises path variance via its
cumulative-`n_trials` term) gets *worse*.

**This iteration tests the converse prediction**: if iter 041's
DSR uplift is path-variance-bound rather than regime-information-
bound, then *halving the regime crossings* (without changing the
weights) should **reduce path variance and improve DSR**. The cleanest
way to halve crossings without changing the binary `VIX < 20` rule's
*economic* state is to introduce **hysteresis** — a Schmitt trigger
with a low entry threshold (calm if VIX < 18) and a high exit
threshold (stress if VIX > 22). Inside the [18, 22] band the regime
*persists* in its prior state.

Mechanism::

    state[t] = state[t-1]                                        # default
    if state[t-1] == calm and VIX[t-1] >= high_threshold:        # exit calm
        state[t] = stress
    if state[t-1] == stress and VIX[t-1] <  low_threshold:       # enter calm
        state[t] = calm

    pos_eq[t] = calm_weights["eq_w"]   if state[t]=='calm' else stress_weights["eq_w"]
    pos_bd[t] = calm_weights["bd_w"]   if state[t]=='calm' else stress_weights["bd_w"]
    pos_gld[t]= calm_weights["gld_w"]  if state[t]=='calm' else stress_weights["gld_w"]

    gross[t] = pos_eq*r_eq + pos_bd*r_bd + pos_gld*r_gld
    cost[t]  = (|∆pos_eq| + |∆pos_bd| + |∆pos_gld|) * cost_bps_per_leg
    net[t]   = gross - cost

VIX[t-1] is the lagged level (no look-ahead). Bootstrap state at bar 0
from VIX[0] vs the **mid-band** (calm if VIX[0] < 20 else stress) so
that `low_threshold = high_threshold = 20` reduces exactly to iter 041
— a TDD spec enforces this identity reduction.

## Primary citation

`[advances_fin_ml, ch.17-18]` — Lopez de Prado on regime detection
and the explicit warning that *whipsaw* (frequent regime crossings on
noise) is a primary cost mechanism for state-dependent strategies;
hysteresis is the standard remedy. The path-variance argument from
iter 042 is itself a corollary of the deflator definition in
`[advances_fin_ml, p.222-223]`.

## Additional citations

- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
  with regime-conditional weight tilts (same mechanism as iter 041; we
  only change the gate construction).
- `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (VIX_{t-1}).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials; the
  deflator's variance penalty term is the binding mechanism that
  iter 042 identified and this iteration tries to relieve.
- Hamilton, J. D. (1989). *A new approach to the economic analysis of
  nonstationary time series and the business cycle*. Econometrica
  57(2), 357-384. DOI: 10.2307/1912559 — Markov regime-switching with
  state persistence (the canonical reference for hysteretic state
  classifiers in macro-finance).
- Whaley, R. E. (2009). *Understanding the VIX*. JPM 35(3), 98-105.
  DOI: 10.3905/JPM.2009.35.3.098 — VIX as ex-ante risk regime
  indicator (carries over from iter 041).
- Bekaert, G., & Hoerova, M. (2014). *The VIX, the variance premium
  and stock market volatility*. J Econometrics 183(2), 181-192.
  SSRN 2294327 — VIX uncertainty / risk-aversion decomposition.
- Krishnamurthy, A. (2010). *Amplification mechanisms in liquidity
  crises*. AER 100(3), 1-25 — the macro literature's path-dependence
  argument for hysteretic risk-state machines.

## Edge source

SPY 1× buy-and-hold has *constant* equity tilt regardless of
regime. iter 041 reduces equity exposure precisely when realised
correlations cluster upward (stress) — but pays a *crossings cost*:
each whipsaw between VIX 19/21 trades the legs back and forth at 2bps
× 0.40 ≈ 8bps × 7-8 round-trips/year ≈ −56-65bps/year of fixed cost
PLUS path variance. Hysteresis discards the whipsaw without losing
the regime detection at the long horizon. The economic prediction
is **same conditional Sharpe per regime, fewer crossings, lower path
variance, lower DSR worst-p** — precisely what the iter 042 final
report's "path-variance hypothesis" identified as the binding axis.

## Datasets

- **educational** (SPY+IEF+GLD 21y, 2004-11-19 → 2026-04-15,
  GLD-aligned): same window as iter 041 for apples-to-apples
  comparison; spans GFC + COVID + 2022.
- **spy_real** (SPY+IEF+GLD 17y, 2009-06-25 → 2026-04-15): post-GFC
  era; tests hysteresis on a calmer-on-average regime distribution.
- **ndx_real** (QQQ+IEF+GLD 16y, 2010-02-12 → 2026-04-15): tech-heavy
  benchmark; the 2022 stress cluster is a stress test for hysteretic
  regime persistence.

## Kill criteria (pre-committed)

The hypothesis is FALSIFIED if **ANY** of the following occurs:

- **Kill A — Sharpe regression**: Sharpe drops by ≥ 0.05 vs iter 041
  on ≥ 2 datasets (hysteresis sacrifices too much regime
  responsiveness for path-variance reduction).
- **Kill B — DSR no-improvement**: worst-p ≥ 0.168 (iter 041's
  worst-p) — the path-variance hypothesis is FALSIFIED; iter 041's
  DSR uplift came from regime *information*, not low path variance.
- **Kill C — MDD breach**: MDD breaches `benchmark + 5pp` on any
  dataset (hysteresis delays exit from calm into stress, and the
  resulting drawdown breaches budget).
- **Kill D — score regression**: total score < 84 (iter 041
  ceiling — strict no-regression rule, same convention as iter 042).
- **Kill E — G7 parity break**: cross-library |ΔCAGR| > 3 pp on any
  dataset (engine bug introduced by the new state-machine logic).
- **Kill F — wrong direction on churn**: regime round-trips/year is
  NOT halved vs iter 041 on ≥ 2 datasets (iter 041 avg ~7-8 RT/yr;
  iter 043 target ~3-4 RT/yr; if observed > iter 041, the Schmitt
  trigger is broken).

If Kill B fires (worst-p ≥ 0.168) — the **PRIMARY** falsification —
the structural lesson is: iter 041's edge was specifically the
crossings *themselves* (each crossing is a high-info update of the
regime label), and hysteresis loses the information without
recovering DSR. iter 044 must then attack DSR via *information per
bar* (HMM-2 multi-feature, ML meta-label) rather than *bars per
crossing*.

## Expected budget

- Configs to test: **1** (single pre-committed cfg
  `hysteretic_vix_low18_high22_w70_40_40_30_55_55`).
- Wall-time: ~30-45 min (data load + 3 runs + cross-lib parity + gates
  + score; identical to iter 041 cost profile, plus a small constant
  for state-machine vs vectorised binary gate).
- Files to create:
  - `regime_weights_hysteretic.py` — pandas engine with Schmitt
    trigger.
  - `numpy_reference_hysteretic.py` — pure-numpy reference for G7
    parity.
  - `run_backtests.py` — single-cfg, 3 datasets driver.
  - `compute_gates_and_score.py` — gates + scoring + kill evaluation.
  - `tests/test_iter_043_hysteretic.py` — TDD specs (≥ 8).
  - `results.json`, `verdict.json`, `final_report.md`, plots.

## Implementation plan

1. **TDD specs first** (`tests/test_iter_043_hysteretic.py`):
   1. **Identity reduction** — when `low_threshold = high_threshold =
      20`, the hysteretic engine reduces *exactly* to iter 041's
      `apply_regime_weights_3leg` on the same inputs (numerical
      tolerance 1e-12).
   2. **Hysteresis halves crossings** — given the same VIX series,
      the count of regime flips with `(low=18, high=22)` is strictly
      `≤` the count with `(low=high=20)` (often half or less).
   3. **State persistence in band** — when VIX stays in [18, 22] for
      a stretch, the regime label does not flip (idempotent inside
      the band).
   4. **Calm-to-stress only via high threshold** — a calm → stress
      transition occurs only when VIX_{t-1} ≥ high_threshold (never
      while in [low, high)).
   5. **Stress-to-calm only via low threshold** — symmetric: stress
      → calm only when VIX_{t-1} < low_threshold.
   6. **No look-ahead** — using VIX_t (not VIX_{t-1}) yields different
      first-bar state vs the lagged version (negative test).
   7. **Cross-lib parity** — pandas engine vs pure-numpy reference
      yields identical net returns to floating-point precision.
   8. **Threshold ordering** — `low_threshold > high_threshold`
      raises `ValueError`.
   9. **Calm-only fallback** — when VIX series stays below
      low_threshold throughout, the run reduces to a single static
      stack at calm weights only.
   10. **Stressed-only fallback** — analogous for VIX above
       high_threshold throughout.

2. **Engine module** (`regime_weights_hysteretic.py`):
   - Function `apply_regime_weights_hysteretic_3leg(r_eq, r_bd, r_gld,
     vix, *, calm_weights, stress_weights, low_threshold,
     high_threshold, cost_bps_per_leg)`.
   - Build VIX_lag = VIX.shift(1) with first-bar bootstrap from VIX[0].
   - Iterate per bar to update state via Schmitt trigger; vectorise
     where possible (numpy/Numba-friendly inner loop).
   - Daily rebalance: each bar's positions are
     `weights_state[t] · 1`; cost is `(|Δpos_eq| + |Δpos_bd| +
     |Δpos_gld|) × cost_bps_per_leg`.
   - Return `(net, positions, scale, regime_label)`.

3. **Numpy reference** (`numpy_reference_hysteretic.py`): mirror the
   same arithmetic on pure ndarray inputs — used by both the G7
   gate and TDD spec #7.

4. **Run backtests** (`run_backtests.py`): single CFG, 3 datasets,
   with the same VIX path / dataset windows as iter 041 for apples-
   to-apples comparison. Add `regime_summary` dict per dataset
   reporting regime fraction, switch count, turnover, conditional
   Sharpe / MDD per regime, **and the band-occupancy fraction**
   (i.e. fraction of bars where 18 ≤ VIX < 22 — the "hysteresis-
   active" zone).

5. **Compute gates** (`compute_gates_and_score.py`):
   - G1 PBO via CSCV (1-cfg → degenerate; report `pbo_pass=True` with
     the standard note from iter 041).
   - G2 DSR with cumulative n_trials = 4307 + 1 = 4308.
   - G3 walk-forward 6/8 windows + per-window MDD < 25%.
   - G4 OOS 70/30 Sharpe > 0.
   - G5 FWD post-2020 stress Sharpe > 0.
   - G6 bootstrap 99.9% CI low > 0 with 5000 draws.
   - G7 cross-lib parity from numpy reference.
   - Kill A-F evaluation against iter 041 baseline metrics.
   - Score via `studies/strategy_hunt_loop/scoring.py`.

6. **Final report + verdict.json + plots** (Stage 5 of PROMPT.md).

## Pre-committed configuration

```python
CFG = {
    "cfg_id": "hysteretic_vix_low18_high22_w70_40_40_30_55_55",
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},  # total 1.50×
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},  # total 1.40×
    "low_threshold": 18.0,    # enter calm if VIX_{t-1} < 18
    "high_threshold": 22.0,   # enter stress if VIX_{t-1} >= 22
    "vix_lag_days": 1,        # VIX_{t-1} → state_t (no look-ahead)
    "rebalance": "daily",
    "cost_bps_per_leg": 0.0002,
    "funding_cost_modeled": False,
}
```

Single pre-committed config — no grid, no sweep, no post-hoc tuning.
The thresholds are a symmetric ±2 around iter 041's binary 20 mark
(matching the natural one-σ band of the VIX 1y rolling distribution
for the 2010-2024 window and explicitly listed in iter 042's "Next
iteration suggestions" §2 with an [18, 22] band proposal).

## Why structural novelty

vs **iter 041**: identical weights, identical assets, identical
total-leverage budget — but the regime gate is hysteretic instead of
binary. A binary gate is a degenerate special case (low = high =
20), which the identity-reduction TDD spec enforces.

vs **iter 038**: iter 038 modulates leverage scalar, not weights;
iter 043 modulates weights with a *different* gate structure
(hysteretic vs binary). Cleanly orthogonal axes.

vs **iter 028/029/030/031**: those gated VRP-harvest streams (with
VIX levels / persistence / z-scores). iter 043 has no VRP component
— it gates a static stack like iter 041, with a state-persistence
modification.

vs **iter 042**: iter 042 amplifies the conditional asymmetry by
compounding iter 041's weights with iter 038's leverage targets.
iter 043 does the *opposite* — preserve the asymmetry, halve the
crossings. The two are direct alternatives that disambiguate the
"path-variance vs regime-information" question raised by iter 042's
final report.

This is the cleanest in-family attempt at *understanding* iter 041's
edge mechanism. If iter 043 improves DSR, the path-variance
hypothesis is supported and a refined hysteretic regime gate is the
natural next direction. If iter 043 regresses DSR, iter 041's edge is
information-per-crossing and iter 044 must attack DSR via richer
regime classifiers (HMM-2 on (VIX, T10Y3M)) instead of fewer
crossings.

## Predicted outcome

- **Sharpe**: roughly equal to iter 041 (path-variance reduction is
  small relative to the overall vol; expected −0.01 to +0.02 across
  the three datasets).
- **MDD**: slightly worse on edu/spy if hysteresis delays exit into
  stress (e.g. 2008Q3 VIX briefly between 22 and 30); slightly
  better on ndx if it avoids the 2022 whipsaw cluster. Net
  expectation: ±0-3 pp from iter 041.
- **DSR**: **worst-p target 0.10-0.14** — corresponding to criterion
  3 = 10/15 (vs iter 041's 5/15). +5 score points → **89/100 STRONG**.
  This is the central prediction.
- **CAGR**: stays at 12-17% across datasets (criterion 4 stays
  15/15).
- **Score**: predicted **84-89 STRONG**, with most-likely value 87.

If the prediction holds (DSR worst-p improves), the iter 042
"path-variance" lesson is *confirmed* and the path forward is to
refine the regime classifier (HMM-2 / hysteretic+ML) without
amplifying the conditional asymmetry. If the prediction is wrong
(Kill B fires, DSR worst-p ≥ 0.168), the lesson is the opposite —
iter 041's edge is information-rich crossings, and iter 044 must
attack DSR via *more* (better-calibrated) crossings, not fewer.

Either outcome is informative. The hysteretic single-axis gate is
the cheapest disambiguation experiment in the loop's path forward.
