# Iteration 042 — Combined regime modulation (leverage × weights) on iter 037 stack

## Hypothesis

Iter 041 broke the static-stack 79 ceiling at **STRONG 84** by modulating
*per-leg weights* across a VIX regime gate at near-constant total leverage
(1.50 calm vs 1.40 stress). Iter 038 had already shown that modulating
*total leverage* at fixed weights (1.7× calm vs 1.0× stress, on the same
0.6/0.45/0.45 base) preserves Sharpe and improves MDD. The two
mechanisms are **orthogonal axes** — one shifts composition, the other
shifts scale. **This iteration tests whether superposing them
compounds the DSR uplift**: keep iter 041's regime-conditional relative
composition (eq:bd:gld ratios calm vs stress) but rescale each regime's
weights so that total leverage matches iter 038's regime-differential
(1.7× calm vs 1.0× stress).

Concretely:

- **Calm (VIX_{t-1} < 20)**: iter 041's calm composition (0.70/0.40/0.40,
  total 1.50) rescaled by 1.7/1.5 ≈ 1.133 →
  **(0.79333, 0.45333, 0.45333)** total **1.700×**.
- **Stress (VIX_{t-1} ≥ 20)**: iter 041's stress composition
  (0.30/0.55/0.55, total 1.40) rescaled by 1.0/1.4 ≈ 0.714 →
  **(0.21429, 0.39286, 0.39286)** total **1.000×**.

Average leverage at the 65/35 calm/stress historical mix is
0.65·1.7 + 0.35·1.0 ≈ **1.455×**, statistically indistinguishable from
iter 041's 1.46-1.47×. So the *expected* exposure is preserved, but the
*conditional* exposure asymmetry is amplified: equity beta in calm
goes from 0.70 → 0.79 (+13%) and stress equity beta drops from
0.30 → 0.21 (−29%).

The economic prediction:

1. **Sharpe** — preserved or marginally up. Calm equity uplift adds
   bull-market return; stress equity reduction subtracts only a small
   amount because conditional Sharpe of equity is low/negative in
   stress regimes anyway (Bekaert-Hoerova 2014 §3).
2. **MDD** — meaningful improvement. Stress regime at 1.0× total with
   only 21% equity is the most defensive iter-stack ever tested
   (deeper than iter 041's stress 1.40× at 21% equity).
3. **DSR** — predicted worst-p in 0.13-0.17 range. iter 041 alone
   moved 0.222 → 0.168 (−0.054). iter 038 alone moved 0.222 → 0.204
   (−0.018). If the two axes are even partially orthogonal, the
   combined effect could push worst-p toward
   0.222 − 0.054 − 0.018 ≈ **0.150** (additive lower bound), or as low
   as 0.13 if multiplicative variance reduction stacks favourably.
4. **Score** — predicted **84-92**, most-likely **88**. Path to WINNER
   (≥ 90 + all 5 strict conditions) requires DSR worst-p to drop into
   the 0.10-0.13 zone (10/15 score on criterion 3) and all other
   criteria to stay perfect — possible but tight.

This is structurally novel vs iter 041 (constant-leverage weight
modulation) AND vs iter 038 (constant-weight leverage modulation).
The mechanism is **dual-axis regime modulation**: composition AND
scale both gated on the same lagged-VIX signal.

## Primary citation

`[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity framework
explicitly contemplates dual modulation (allocation + leverage) of a
multi-leg static stack across regimes when conditional risk-return
trade-offs differ across states.

## Additional citations

- `[risk_parity, p.10-11, ch.1]` — diversification benefit of bond/gold/
  equity stack at preserved expected leverage budget.
- `[advances_fin_ml, ch.17-18, p.162-164]` — Lopez de Prado on regime
  detection / Markov-switching with VIX_{t-1} no-lookahead lag.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- Whaley, R. E. (2009). *Understanding the VIX*. Journal of Portfolio
  Management 35(3), 98-105. DOI: 10.3905/JPM.2009.35.3.098.
- Bekaert, G., & Hoerova, M. (2014). *The VIX, the variance premium and
  stock market volatility*. Journal of Econometrics 183(2), 181-192.
  SSRN 2294327.
- Erb, C. B., & Harvey, C. R. (2006). *The strategic and tactical value
  of commodity futures*. FAJ 62(2), 69-97. DOI: 10.2469/faj.v62.n2.4084.
- Asness, C., Moskowitz, T., & Pedersen, L. (2013). *Value and momentum
  everywhere*. Journal of Finance 68(3), 929-985. DOI:
  10.1111/jofi.12021.
- Moreira, A., & Muir, T. (2017). *Volatility-managed portfolios*.
  Journal of Finance 72(4), 1611-1644. DOI: 10.1111/jofi.12513 — for
  the iter 038 leverage-modulation precedent that this iter combines.

## Edge source

SPY 1× buy-and-hold has constant leverage AND constant composition
across regimes. Iter 041 changed composition only; iter 038 changed
leverage only. iter 042 changes BOTH simultaneously, exploiting the
fact that calm and stress regimes have qualitatively different
conditional risk-return profiles — calm rewards equity tilt, stress
punishes any equity exposure. By scaling UP equity in calm AND
scaling DOWN total exposure in stress, the strategy captures more of
calm-regime upside while sacrificing less to stress-regime drawdowns
than either parent alone.

## Datasets

- **educational** (SPY+IEF+GLD 21y, 2004-11-19 → 2026-04-15, GLD-aligned):
  spans GFC + COVID + 2022; richest regime variation. The 1.0× stress
  setting should sharply reduce the 2008 GFC drawdown vs iter 041's
  1.40× stress.
- **spy_real** (SPY+IEF+GLD 17y, 2009-06-25 → 2026-04-15): post-GFC,
  fewer regime breaks. Tests whether the dual modulation works outside
  a single training crisis.
- **ndx_real** (QQQ+IEF+GLD 16y, 2010-02-12 → 2026-04-15): tech-heavy.
  The 1.7× calm leverage on QQQ adds aggressive bull exposure; the
  1.0× stress on QQQ during 2022 should help significantly.

## Kill criteria (pre-committed)

The hypothesis is FALSIFIED if **ANY** of the following:

- **Kill A — Sharpe regression vs iter 041**: Sharpe drops by ≥ 0.05
  vs iter 041 on ≥ 2 datasets (combined modulation hurts pure Sharpe
  vs the weight-only mechanism).
- **Kill B — DSR no-improvement vs iter 041**: worst-p ≥ 0.168
  (combined adds zero explanatory power on top of weight-only).
- **Kill C — MDD breach**: MDD breaches `benchmark + 5pp` on any
  dataset (the 1.7× calm leverage punishes a missed regime call).
- **Kill D — score regression vs iter 041**: total score < 84 (the
  current top — strict no-regression rule).
- **Kill E — G7 parity break**: cross-library |ΔCAGR| > 3 pp on any
  dataset.
- **Kill F — excessive churn**: realised regime-switch turnover
  > 10 round-trips/year on any dataset (relaxed from iter 041's 5
  cap because dual modulation mechanically adds turnover; the
  relevant test is whether costs eat the alpha, not whether the gate
  flips often).

## Expected budget

- Configs to test: **1** (single pre-committed cfg
  `combined_regime_vix_lt20_lev17_w70_40_40_ge20_lev10_w30_55_55`).
- Wall-time: ~30-45 min (data load + 3 runs + cross-lib parity + gates
  + score). Engine reused from iter 041 (no new mechanism), only CFG
  values change.
- Files to create:
  - `combined_regime_static_stack.py` — thin module wrapping iter 041's
    `apply_regime_weights_3leg` with the new CFG (no new arithmetic).
  - `numpy_reference_combined_regime.py` — alias to iter 041's numpy
    reference for G7 parity (same arithmetic, different params).
  - `run_backtests.py` — single-cfg, 3 datasets driver.
  - `compute_gates_and_score.py` — gates + scoring + kill evaluation.
  - `tests/test_iter_042_combined_regime.py` — TDD specs (≥ 6).
  - `results.json`, `verdict.json`, `final_report.md`, plots.

## Implementation plan

1. **TDD specs first** (`tests/test_iter_042_combined_regime.py`):
   1. CFG total leverage check — `sum(calm_weights.values())` ≈ 1.700
      and `sum(stress_weights.values())` ≈ 1.000 to 4 decimals.
   2. Composition ratios match iter 041 — calm `(eq/bd, eq/gld)` =
      iter 041 calm `(0.70/0.40, 0.70/0.40)` = (1.75, 1.75); stress
      ratios match iter 041 stress.
   3. Identity reduction — when calm and stress weights are equal,
      output reduces exactly to a single-static-stack.
   4. Cross-lib parity — pandas vs numpy reference yield identical
      net returns to floating-point precision (≤ 1e-12 absolute,
      same as iter 041 spec).
   5. Asymmetry test — calm-only output is identical to iter 041
      `apply_regime_weights_3leg` with calm weights both arms;
      stress-only analogously. (Confirms reuse of iter 041 engine
      doesn't introduce new bugs.)
   6. Determinism — same inputs yield same outputs idempotently.

2. **Engine module** (`combined_regime_static_stack.py`): thin re-export
   of iter 041's `apply_regime_weights_3leg`. The "combined" name
   denotes the *cfg* (lev × weights), not new arithmetic.

3. **Numpy reference** (`numpy_reference_combined_regime.py`): import
   iter 041's `apply_regime_weights_3leg_np` for G7 parity. Same
   reasoning — no new arithmetic.

4. **Run backtests** (`run_backtests.py`): single CFG, 3 datasets,
   verbatim same VIX path / dataset windows as iter 037/038/041.
   `regime_summary` dict reports regime fraction, switch count,
   turnover, conditional Sharpe / MDD per regime.

5. **Compute gates** (`compute_gates_and_score.py`):
   - G1 PBO — N=1 → vacuous PASS (single pre-committed config; same
     spec convention as iter 037-041).
   - G2 DSR with cumulative n_trials = 4306 + 1 = 4307.
   - G3 walk-forward 6/8 windows + per-window MDD < 25%.
   - G4 OOS 70/30 Sharpe > 0.
   - G5 FWD post-2020 stress Sharpe > 0.
   - G6 bootstrap 99.9% CI low > 0 with 5000 draws.
   - G7 cross-lib parity from numpy reference.
   - Kill A-F evaluation against iter 041 baseline metrics (since iter
     041 is the new ceiling-holder).
   - Score via `studies/strategy_hunt_loop/scoring.py`.

6. **Final report + verdict.json + plots** (Stage 5 of PROMPT.md).

## Pre-committed configuration

```python
CFG = {
    "cfg_id": "combined_regime_vix_lt20_lev17_w70_40_40_ge20_lev10_w30_55_55",
    "vix_threshold": 20.0,
    "calm_weights":   {"eq_w": 0.79333, "bd_w": 0.45333, "gld_w": 0.45333},  # total 1.700×
    "stress_weights": {"eq_w": 0.21429, "bd_w": 0.39286, "gld_w": 0.39286},  # total 1.000×
    "vix_lag_days": 1,
    "rebalance": "daily",
    "cost_bps_per_leg": 0.0002,
    "funding_cost_modeled": False,
    # Provenance: derived deterministically from iter 041 CFG by
    # rescaling each regime's weights to iter 038's leverage targets:
    #   calm  = iter041_calm  × (1.700 / sum(iter041_calm))  = × 1.13333
    #   stress= iter041_stress× (1.000 / sum(iter041_stress))= × 0.71429
    # No grid search, no sweep, no post-hoc tuning. Single config.
}
```

## Why structural novelty

vs iter 041: iter 041 modulates per-leg weights at near-constant total
leverage (1.50 vs 1.40, range 0.10). iter 042 modulates BOTH per-leg
weights AND total leverage simultaneously (1.70 vs 1.00, range 0.70).
The differential leverage range is **7× larger** than iter 041's; the
conditional asymmetry between calm and stress is qualitatively
amplified. The relative composition within each regime is preserved
(same eq:bd:gld ratios as iter 041), so the new mechanism is purely
*dual-axis* rather than a triple shift.

vs iter 038: iter 038 modulates total leverage at fixed relative
weights (0.6/0.45/0.45 base proportional). iter 042 modulates total
leverage at *regime-conditional* relative weights — calm uses iter
041's eq-tilted ratios, stress uses iter 041's defensive ratios. The
two mechanisms compose along orthogonal axes.

vs iter 037: iter 037 is the unconditional baseline (constant weights,
constant leverage). iter 042 differs on BOTH axes simultaneously.

vs iter 028-031: those gate VRP harvest streams; iter 042 has zero VRP
component — pure static stack with regime indicator on both
composition and leverage.

vs iter 040: iter 040 wraps σ⁻² vol-target on a basket; iter 042 stays
in the unconditional-volatility static-stack family.

This is the cleanest in-family attempt at breaking iter 041's STRONG
84 ceiling by attacking the DSR axis (criterion 3 = 5/15 currently)
through orthogonal-axis stacking. The structural prediction is +5 to
+10 score points on the DSR axis with no regression on the other 5
criteria; the realised result will tell us whether the two mechanisms
are independently informative or share the same regime signal noise
floor.

## Predicted outcome

- **Sharpe**: roughly equal to iter 041 (Δ ±0.03 across datasets).
  Calm leverage uplift compensates stress leverage reduction in
  expectation.
- **MDD**: improvement of 1-3 pp on edu (covers 2008), 0-1 pp on spy/
  ndx (post-GFC has fewer stress clusters). The 1.0× stress is the
  defensive end of every iter ever tested in the static-stack family.
- **DSR**: target worst-p **0.13-0.17**. If achieved, criterion 3
  jumps from 5 → 5 (worst-p > 0.10) or 5 → 10 (worst-p ∈ [0.05, 0.10)).
- **CAGR**: roughly equal to iter 041's 13.0/13.5/15.7%.
- **Score**: predicted **84-92 STRONG** (with non-trivial probability
  of WINNER status if DSR clears 0.05).

If the prediction holds, the result is either (a) a strict iter-041
improvement at 86-89 STRONG → break to a new ceiling, or (b) a
WINNER at 90+ if DSR collapses below 0.05. The most likely scenario
is (a) — DSR axes typically don't compound multiplicatively even
when individually informative.

If neither effect compounds, Kill B fires (worst-p ≥ 0.168) and the
result is a STRONG 79-84 with the lesson that the two regime axes
share too much information to be considered orthogonal.
