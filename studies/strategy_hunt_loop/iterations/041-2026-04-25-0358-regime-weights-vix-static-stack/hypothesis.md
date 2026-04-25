# Iteration 041 — VIX-regime-conditional WEIGHTS on iter 037 static-stack base

## Hypothesis

Iter 037's three-leg static stack (0.6 SPY + 0.45 IEF + 0.45 GLD, 1.5×
total) hit the loop-record **STRONG 79** ceiling but is bottlenecked at
**DSR p=0.222** (criterion 3 = 0/15) and locked at maximal Sharpe edge
(criterion 1 = 25/25). Iter 038 already showed that VIX-regime-gated
LEVERAGE modulation on the same base preserves Sharpe (0.998/1.10/1.15)
while improving MDD (−4 to −8 pp) and slightly improving DSR (0.204).
**This iteration tests the structurally distinct alternative**:
modulate the *composition* of the portfolio rather than its total
leverage — keeping total leverage approximately constant at 1.5× while
shifting allocation between equity-tilted (calm regime) and bond/gold-
tilted (stressed regime) static stacks based on a lagged VIX
threshold.

The mechanism is two static stacks composed under a regime indicator,
not a leverage scaler. Calm regime keeps the equity beta high to
capture bull-market returns; stressed regime down-shifts equity in
favour of the diversifying legs whose realised conditional correlation
with equities goes more negative (bonds, flight-to-safety) or remains
near zero (gold). The economic prediction is twofold: (a) the DSR
deflator should decrease because the regime classifier introduces
*orthogonal explanatory power* over the unconditional stack, and
(b) the conditional MDD should shrink in 2008/2020-style stress
windows because equity exposure is reduced precisely when realised
correlations cluster.

This is structurally novel vs iter 038 (leverage modulation, not
weight modulation) and vs every prior VIX-gated VRP harvest iteration
(those gate on the harvest stream; here the gate sits on a static
stack base layer with NO VRP component).

## Primary citation

`[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity framework
explicitly contemplates *regime-conditional* weight tilts within a
constant total leverage budget when conditional correlations are
expected to differ from unconditional means.

## Additional citations

- `[risk_parity, p.10-11, ch.1]` — diversification benefit of bond/
  gold/equity stack at preserved leverage.
- `[advances_fin_ml, ch.17-18]` — Lopez de Prado on regime detection
  for portfolio construction; warns against in-sample regime fitting.
- `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (we use
  VIX_{t-1} → weight_t).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- Whaley, R. E. (2009). *Understanding the VIX*. Journal of
  Portfolio Management 35(3), 98-105 — VIX as ex-ante risk regime
  indicator. https://doi.org/10.3905/JPM.2009.35.3.098.
- Bekaert, G., & Hoerova, M. (2014). *The VIX, the variance premium
  and stock market volatility*. Journal of Econometrics 183(2),
  181-192. arXiv: SSRN 2294327. Decomposes VIX into risk-aversion
  and uncertainty components, justifying regime use as a state
  variable.
- Erb, C. B., & Harvey, C. R. (2006). *The strategic and tactical
  value of commodity futures*. Financial Analysts Journal 62(2),
  69-97. DOI: 10.2469/faj.v62.n2.4084 — gold strategic role.
- Asness, C., Moskowitz, T., & Pedersen, L. (2013). *Value and
  momentum everywhere*. Journal of Finance 68(3), 929-985. DOI:
  10.1111/jofi.12021 — orthogonality of asset-class returns.

## Edge source

SPY 1× buy-and-hold has a *constant* equity tilt across all market
regimes, so when realised conditional correlations spike upward in
stress (2008, 2020) every dollar is exposed to the systematic
drawdown. A regime-conditional weight switch reduces the realised
expected loss conditional on stress regime while preserving the
calm-regime equity tilt — the unconditional Sharpe rises if the
regime classifier is informative.

## Datasets

- **educational** (SPYSIM 21y, 2004-11-19 → 2026-04-15, GLD-aligned):
  spans GFC + COVID + 2022; only dataset with VIX history covering
  pre-2009. Weights tilt should be most distinguishable here.
- **spy_real** (SPY+IEF+GLD 17y, 2009-06-25 → 2026-04-15): post-GFC,
  fewer regime breaks; tests whether the modulation works *outside* a
  single training crisis (2008).
- **ndx_real** (QQQ+IEF+GLD 16y, 2010-02-12 → 2026-04-15): tech-heavy
  benchmark; regime classifier may behave differently because QQQ has
  higher conditional vol than SPY in tech sell-offs (2022).

## Kill criteria (pre-committed)

The hypothesis is FALSIFIED if **ANY** of the following occurs:

- **Kill A — Sharpe regression**: Sharpe drops by ≥ 0.05 vs iter 037
  on ≥ 2 datasets (regime modulation hurts pure performance).
- **Kill B — DSR no-improvement**: worst-p ≥ 0.222 across the 3
  datasets (regime classifier adds zero explanatory power vs
  unconditional iter 037).
- **Kill C — MDD breach**: MDD breaches `benchmark + 5pp` on any
  dataset (regime switch fails to protect during 2008/2020 stress).
- **Kill D — score regression**: total score < 79 (no improvement vs
  iter 037 ceiling — strict regression).
- **Kill E — G7 parity break**: cross-library |ΔCAGR| > 3 pp on any
  dataset (engine bug).
- **Kill F — excessive churn**: realised regime-switch turnover
  > 5 round-trips/year on any dataset (in-sample regime fitting risk).

## Expected budget

- Configs to test: **1** (single pre-committed cfg
  `regime_weights_vix_lt20_70_40_40_ge20_30_55_55`).
- Wall-time: ~30-45 min (data load + 3 runs + cross-lib parity + gates
  + score).
- Files to create:
  - `regime_weights_static_stack.py` — pandas engine.
  - `numpy_reference_regime_weights.py` — numpy reference for G7.
  - `run_backtests.py` — single-cfg, 3 datasets driver.
  - `compute_gates_and_score.py` — gates + scoring + kill evaluation.
  - `tests/test_iter_041_regime_weights.py` — TDD specs (≥ 5).
  - `results.json`, `verdict.json`, `final_report.md`, plots.

## Implementation plan

1. **TDD specs first** (`tests/test_iter_041_regime_weights.py`):
   1. Identity reduction — when calm/stress weights are equal,
      regime modulation reduces exactly to iter 037's
      `apply_static_stack_3leg`.
   2. No look-ahead — using VIX_t (not VIX_{t-1}) yields *different*
      first-bar weights vs the lagged version (negative test).
   3. Regime determinism — given a fixed VIX series, regime
      assignment is deterministic and idempotent.
   4. Cross-lib parity — pandas engine vs pure-numpy reference yields
      identical net returns to floating-point precision.
   5. Calm-only fallback — when VIX[:] < threshold, output equals
      single-static-stack at calm weights only.
   6. Stressed-only fallback — analogous for VIX[:] ≥ threshold.
   7. Param-domain errors — negative weights, out-of-range threshold.

2. **Engine module** (`regime_weights_static_stack.py`):
   - Function `apply_regime_weights_3leg(r_eq, r_bd, r_gld, vix,
     calm_weights, stress_weights, vix_threshold, cost_bps_per_leg,
     turnover_round_trip_factor)`.
   - Resolve weights per bar from `vix.shift(1) < threshold` (lagged).
   - Daily rebalance: each bar's positions are
     `weights_regime[t] · 1`; cost is `(|Δpos_eq| + |Δpos_bd| +
     |Δpos_gld|) × cost_bps_per_leg` so regime switches incur a real
     cost (the only non-trivial turnover in the model).
   - Return `(net, positions, scale, regime_label)`.

3. **Numpy reference** (`numpy_reference_regime_weights.py`): mirror
   the same arithmetic on pure ndarray inputs — used by both the G7
   gate and TDD spec #4.

4. **Run backtests** (`run_backtests.py`): single CFG, 3 datasets,
   with the same VIX path / dataset windows used by iter 037 for
   apples-to-apples comparison. Add `regime_summary` dict per dataset
   reporting regime fraction, switch count, turnover, conditional
   Sharpe / MDD per regime.

5. **Compute gates** (`compute_gates_and_score.py`):
   - G1 PBO via CSCV (1-cfg → degenerate; report `pbo_pass=True` with
     a note that with a single pre-committed config there is no
     in-sample/out-of-sample split to overfit, equivalent to
     spec §0 default).
   - G2 DSR with cumulative n_trials = 4305 + 1 = 4306.
   - G3 walk-forward 6/8 windows + per-window MDD < 25%.
   - G4 OOS 70/30 Sharpe > 0.
   - G5 FWD post-2020 stress Sharpe > 0.
   - G6 bootstrap 99.9% CI low > 0 with 5000 draws.
   - G7 cross-lib parity from numpy reference.
   - Kill A-F evaluation against iter 037 baseline metrics.
   - Score via `studies/strategy_hunt_loop/scoring.py`.

6. **Final report + verdict.json + plots** (Stage 5 of PROMPT.md).

## Pre-committed configuration

```python
CFG = {
    "cfg_id": "regime_weights_vix_lt20_70_40_40_ge20_30_55_55",
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},  # total 1.50×
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},  # total 1.40×
    "vix_threshold": 20.0,                # absolute VIX level
    "vix_lag_days": 1,                    # use VIX_{t-1} → weight_t (no look-ahead)
    "rebalance": "daily",
    "cost_bps_per_leg": 0.0002,           # 2 bps per unit per-leg ∆position
    "funding_cost_modeled": False,
}
```

Single pre-committed config — no grid, no sweep, no post-hoc tuning.
The thresholds and weights are taken **verbatim** from BASE_MEMORY.md
"Iter 041 candidates" section #4 to keep the iteration pre-committed
on a path that has been on the candidates list since iter 040 closed.

## Why structural novelty

vs iter 037: identical base assets and total-leverage budget but
weights are now *time-varying* — a new mechanism, not a parameter
tweak.

vs iter 038: iter 038 modulated total leverage (1.7× ↔ 1.0×) at fixed
relative weights. iter 041 keeps total leverage at 1.40-1.50× but
shifts allocation across legs — this modulates *composition*, not
*scale*. The two are orthogonal mechanisms.

vs iter 028/029/030/031: all four gated a VRP-harvest stream with VIX
levels / persistence / z-scores / AND-composites. iter 041 has no
VRP component — it gates a static stack.

vs iter 032/040: those compose a static stack with a put-spread or
vol-managed wrapper; iter 041 stays in the static-stack family with
a regime indicator.

This is the cleanest in-family attempt at breaking the iter 037/038
ceiling of 79 STRONG by attacking the DSR axis (criterion 3 = 0/15
currently) without inheriting any iter 038 leverage-modulation
mechanism or any iter 040 σ⁻²-absorption mechanism.

## Predicted outcome

- **Sharpe**: roughly equal to iter 037 (regime classifier is at
  best slightly informative; 21y VIX history has only ~2-3 large
  stress clusters which is thin).
- **MDD**: improvement of 2-6 pp on edu (covers 2008 + 2020), 1-3 pp
  on spy/ndx (covers 2020 + 2022).
- **DSR**: improvement of 0.05-0.15 in worst-p (target 0.07-0.18) —
  if achieved, criterion 3 jumps from 0 → 5 or 0 → 10 → score 84-89.
- **CAGR**: stays at 12-17% across datasets (criterion 4 stays 15/15).
- **Score**: predicted **80-87 STRONG**, with most-likely value 84.

If the prediction holds, the result is a "STRONG → STRONG-stretch"
update on the static-stack family, matching BASE_MEMORY's predicted
81-83. If the regime classifier is a coin-flip on this VIX history,
the result will be Kill B (DSR no-improvement) → ❌ FAIL with score
≤ 79.
