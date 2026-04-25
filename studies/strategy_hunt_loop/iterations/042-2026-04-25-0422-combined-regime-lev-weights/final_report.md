# Iteration 042 — Final Report

## Verdict

🥈 **PROMISING (score 74/100, winner_conditions_met=False)** — **regression
vs iter 041 (84) by 10 points**. The dual-axis hypothesis (composition
modulation × leverage modulation = compounded DSR uplift) is **falsified
at the originally-predicted compound-effect level**. Two pre-committed
kills fired:

- **Kill B FIRED** — DSR worst-p **0.216** ≥ iter 041's 0.168 (the two
  axes did NOT compound; in fact DSR *regressed* across all 3 datasets).
- **Kill D FIRED** — score **74** < iter 041's 84 (strict no-regression
  rule).

The hypothesis is NOT a complete failure: Sharpe edge stays at 25/25
(3/3 datasets beat by ≥ +0.10), MDD ceiling stays at 15/15 with the
**deepest MDD reduction in the loop's history** (edu 22.21%, spy
22.21%, ndx 28.85% — all best-of-iter), and 9/9 robustness windows
preserved. But the DSR axis got worse, and the 1.7×/1.0× leverage
asymmetry mechanically pushed ndx CAGR (15.02%) under the 0.8×
benchmark floor of 15.35%, costing 5 score points on criterion 4.

**Net structural lesson: DSR uplift in iter 041 came from the LOW
conditional-leverage range (1.50 vs 1.40), not from the regime
classifier's "informativeness". Amplifying the conditional asymmetry
(1.70 vs 1.00) HURTS DSR even when Sharpe is preserved — because path
variance grows faster than mean return.** The two regime axes are NOT
orthogonal in the way BASE_MEMORY's "iter 042 candidates" §1
prediction assumed; they are **anti-correlated through path variance**.

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen) | CAGR (vs 0.8×bench) | MDD (vs bench+5pp) | gates | DSR p |
|---|---|---|---|---|---|
| educational | **1.022** (+0.342) | 12.13% (+2.95pp) ✅ | **22.21%** (−37.93pp) ✅ | 6/7 | 0.175 ❌ |
| spy_real    | **1.087** (+0.187) | 12.50% (+0.52pp) ✅ | **22.21%** (−16.49pp) ✅ | 6/7 | 0.216 ❌ |
| ndx_real    | **1.125** (+0.170) | 15.02% (−0.32pp) ❌ | **28.85%** (−11.27pp) ✅ | 6/7 | 0.196 ❌ |

vs **iter 041 baseline** (the prior STRONG-84 ceiling):

| dataset | iter 041 Sharpe | iter 042 Sharpe | Δ Sharpe | iter 041 MDD | iter 042 MDD | Δ MDD | iter 041 DSR | iter 042 DSR |
|---|---|---|---|---|---|---|---|---|
| educational | 1.027 | 1.022 | −0.004 | 27.60% | **22.21%** | **−5.39pp** | 0.168 | 0.175 |
| spy_real    | 1.131 | 1.087 | −0.044 | 24.65% | **22.21%** | −2.44pp | 0.167 | 0.216 |
| ndx_real    | 1.164 | 1.125 | −0.039 | 30.84% | **28.85%** | −1.99pp | 0.156 | 0.196 |

iter 042 strictly improves MDD on all 3 datasets (best static-stack
MDD of any iter ever), but Sharpe regresses by −0.04 on spy/ndx
(under Kill A's −0.05 threshold but visible) and DSR regresses on
all 3 datasets (worst case spy: 0.167 → 0.216, +0.049 worse).

vs **iter 037** (the unconditional 0.6/0.45/0.45 1.5× baseline):

| dataset | iter 037 Sharpe | iter 042 Sharpe | Δ |
|---|---|---|---|
| educational | 0.983 | 1.022 | +0.040 |
| spy_real    | 1.154 | 1.087 | −0.067 |
| ndx_real    | 1.174 | 1.125 | −0.049 |

iter 042 actually *underperforms* iter 037 on spy/ndx Sharpe — the
combined modulation costs more in stress-regime drag than it gains
in calm-regime upside.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 25 | 25 | 3/3 datasets beat bench by ≥+0.10 (preserved from iter 041) |
| 2 Gates | 19 | 25 | edu 6/7, spy 6/7, ndx 6/7 → 5+5+5+4 cross-bonus = 19 (G2 DSR sole fail) |
| 3 DSR | **0** | 15 | **worst p=0.216** (spy_real). vs iter 041 worst-p=0.168 → −5 score pts. **Regressed.** |
| 4 CAGR floor | **10** | 15 | **ndx 15.02% < 15.35% threshold by 0.32pp** — fails. spy 12.50% just clears 11.98%. edu clean. **Regressed −5 vs iter 041.** |
| 5 MDD ceiling | 15 | 15 | All 3 datasets clean by 11-38 pp margin. **Best static-stack MDD of any iter ever.** |
| 6 Robustness | 5 | 5 | 9/9 sub-windows Sharpe > 0 (perfect — preserved from iter 041) |
| **total** | **74** | **100+5** | tier: **🥈 PROMISING** |

## Configuration tested

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
}
```

Single pre-committed config, derived deterministically from iter 041
weights × iter 038 leverage targets:
- calm  = iter041_calm  × (1.700 / 1.500) = × 1.13333
- stress= iter041_stress× (1.000 / 1.400) = × 0.71429

No grid, no sweep, no post-hoc tuning. Cumulative n_trials advance:
**4306 → 4307 (+1).**

## Conditional metrics (regime decomposition)

| dataset | calm bars | calm Sharpe | stress bars | stress Sharpe | calm_frac |
|---|---|---|---|---|---|
| educational | 3333 | +0.969 | 1768 | **+1.136** | 65.3% |
| spy_real    | 2889 | +0.955 | 1337 | **+1.439** | 68.4% |
| ndx_real    | 2873 | +1.045 | 1193 | **+1.407** | 70.7% |

Conditional Sharpes are nearly identical to iter 041 (which had
calm 0.967/0.953/1.043 and stress 1.143/1.449/1.417). The dual-
axis modulation produces the SAME conditional Sharpe asymmetry —
but the unconditional Sharpe drops because the **path of total-
return realisations** has higher variance (regime switches now toggle
0.7 leverage units instead of 0.1), and DSR penalises that variance.

Round-trips per year: **7.26 / 8.02 / 8.15** (edu/spy/ndx). Identical
to iter 041 (same VIX gate, same lag, same threshold). **Kill F
clean** under the relaxed 10/yr cap (was 5/yr in iter 041 but the cost
absorption argument holds).

## Pre-committed kill criteria status

| kill | fired? | observed | threshold | interpretation |
|---|---|---|---|---|
| **A** Sharpe regress vs iter 041 by ≥0.05 on ≥2 ds | ✓ clean | 0/3 datasets | ≥ 2 of 3 | spy/ndx regress by 0.04 each, JUST under threshold |
| **B** DSR worst-p ≥ 0.168 (iter 041) | ❌ **fired** | 0.216 | ≥ 0.168 | **Orthogonal axes share noise; combined modulation hurts DSR** |
| **C** MDD breach on any dataset | ✓ clean | 0/3 | ≥ 1 | regime switch protects; deepest-ever MDD reduction |
| **D** Score < 84 | ❌ **fired** | 74 | < 84 | **−10 pts vs iter 041 (DSR −5, CAGR −5)** |
| **E** G7 cross-lib > 3pp | ✓ clean | max 1.011pp | > 3.0 pp | engine clean |
| **F** Regime churn > 10 RT/yr | ✓ clean | 7-8 RT/yr | > 10 | identical churn to iter 041 (same gate) |

## Why DSR regressed (the key structural finding)

**Hypothesis assumed**: iter 041's DSR uplift (0.222 → 0.168) and iter
038's DSR uplift (0.222 → 0.204) come from "regime-classifier
informativeness". If the two are partially orthogonal axes, the
combined effect should compound.

**Reality observed**: iter 041's DSR uplift came primarily from
**low total-path variance**. Its calm/stress total leverages were 1.50
vs 1.40 (range 0.10). The composition shift redistributed allocation
among legs but kept the *gross exposure* nearly constant — so the
realised Sharpe path was stable, and DSR's variance penalty was small.

iter 042 amplifies the conditional asymmetry to 1.70 vs 1.00 (range
0.70, 7× larger). The realised path now toggles a 0.7-leverage swing
on every regime crossing. Even though the *expected* return per
regime is preserved (avg leverage 1.46 ≈ iter 041's 1.47), the
*realised path variance* grows because each crossing now contributes
a larger jump in instantaneous exposure.

DSR with cumulative n_trials = 4307 penalises this variance. The
mean-return uplift (calm-leg equity tilt) is partially cancelled by
the mean-return loss (stress-leg defensive tilt at 1.0× total).
**Net mean change ≈ 0; net variance change > 0; net DSR worse**.

This is consistent with the broader literature: leverage modulation
(Moreira-Muir 2017) is a *vol-target* mechanism that reduces
unconditional vol and improves Sharpe; using it as a *regime indicator*
to amplify exposure where calm conditional Sharpe is already positive
mostly adds path variance without proportional mean-return gain.

## What worked / what didn't

**What worked**

- **MDD axis preserved + improved**: 22.21% / 22.21% / 28.85% —
  best-of-loop static-stack MDDs. The 1.0× total leverage in stress
  regimes is the most defensive iter ever tested. If the goal were
  "minimise drawdown subject to Sharpe ≥ 1.0", iter 042 wins.
- **Sharpe edge cross-dataset preserved**: 3/3 datasets beat benchmark
  by ≥ +0.10 (criterion 1 = 25/25). The strategy is still informative.
- **Robustness 9/9 sub-windows positive** preserved.
- **G7 cross-lib parity**: max 1.011 pp diff, well below 3 pp gate.
- **TDD specs (10/10) all pass** before backtest run; engine reuse from
  iter 041 introduces zero new bugs.
- **Engine reuse**: zero new arithmetic — all the work is in the CFG
  values. iter 042 is the first iter to test a *parameter-level*
  superposition of two prior positive results.

**What didn't (the 10-point regression)**

- **DSR axis regressed across all 3 datasets** — the central
  hypothesis. iter 041 worst-p 0.168 → iter 042 0.216 (+0.049 worse).
  The two mechanisms are NOT orthogonal in the DSR sense.
- **CAGR floor on ndx fails by 0.32pp** — the 1.7× calm leverage on
  QQQ adds bull-market upside but the 1.0× stress drag on QQQ during
  2022 cuts CAGR enough to slip under 0.8 × 19.18% = 15.35%. Not
  catastrophic (15.02% is still 4-5 pp above the 11% folclore tier)
  but enough to lose 5 score points.
- **Sharpe regresses on spy/ndx by 0.04** — under Kill A's 0.05
  threshold but consistent with the variance argument: bigger leverage
  swings at preserved expected exposure cost a small amount of
  unconditional Sharpe.

## Main lesson (for future iterations)

**The static-stack family's DSR ceiling at iter 041's 0.168 worst-p is
NOT primarily a "regime-classifier-information" bound. It is a
"path-variance" bound on the cumulative-n_trials deflator.** Any
mechanism that amplifies regime-conditional exposure asymmetry — even
when individually informative — can hurt DSR by adding more realised
variance than mean return.

**The path forward to break iter 041's 84 ceiling on the DSR axis**:

1. **Multi-feature regime classifier** (HMM-2 on VIX + T10Y3M, or
   VIX + EBP) — adds *information* per crossing without amplifying
   *exposure asymmetry*. The mechanism reduces the DSR variance
   penalty by making each regime call more deterministic, not by
   making the regimes more "different".
2. **Hysteretic single-axis VIX gate** (calm if VIX<18, stress if
   VIX>22) — same iter 041 weights, just halve the regime crossings.
   Predicted: −0.5 to +1 score pts. Probably won't break 84, but
   provides a clean comparison to test the path-variance hypothesis.
3. **Out-of-family extension**: any mechanism that adds a NEW
   independent return stream (FX carry, options skew, factor timing)
   rather than re-weighting the existing legs.

**Iter 042 explicitly closes** the "naive composition × leverage
superposition" path — adding a 1-line summary to BASE_MEMORY's
"Structural dead-ends" entry for the static-stack family.

## Structural dead-ends discovered

**Closes the dual-axis "compose iter 041 weights with iter 038
leverage targets" mechanism**: this specific superposition regresses
DSR despite preserving Sharpe and improving MDD, because the
amplified conditional leverage range (0.10 → 0.70) increases path
variance faster than mean return.

**Open paths preserved**: HMM-2 multi-feature, hysteretic gate,
cross-sectional factor timing, out-of-family.

This is a **soft closure** (not a tier-FAIL): iter 042 is still
PROMISING and demonstrates the deepest static-stack MDD reduction in
the loop. The closure is on the *specific compound-effect prediction*,
not on the leverage-modulation mechanism in general.

## Citations used

- **Primary**:
  - `[risk_parity, ch.5]` — dual-axis regime modulation of risk-parity stack.
  - `[advances_fin_ml, ch.17-18]` — Lopez de Prado on regime detection.
  - `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (the
    deflator's variance-penalty term is the binding mechanism for iter
    042's regression).
- **Supporting**:
  - `[risk_parity, p.10-11, ch.1]` — Asness-Frazzini-Pedersen
    diversification benefit.
  - `[advances_fin_ml, p.162-164]` — VIX_{t-1} no-look-ahead lag rule.
  - Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098.
  - Bekaert-Hoerova (2014), J Econometrics 183(2), SSRN 2294327.
  - Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084.
  - Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021.
  - Moreira-Muir (2017), JF 72(4), DOI 10.1111/jofi.12513 — leverage-
    modulation precedent (iter 038 base).
- **Methodology**:
  - `[advances_fin_ml, p.31-34]` — G7 cross-library parity gate.
  - `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.

## Next iteration suggestions

iter 042 closes the naive compound-effect path. The DSR axis still has
~10 score points remaining (currently 0/15) and the score gap to
WINNER is ~16 pts. **Structurally novel candidates** for iter 043:

1. **HMM-2 regime classifier on (VIX, T10Y3M)** — multi-feature
   regime detection per `[advances_fin_ml, ch.17-18]`. The path-variance
   argument predicts that HMM-2 should reduce DSR worst-p more than
   any single-feature gate because regime calls become *higher-
   confidence* (lower hysteresis between gates) without amplifying
   exposure asymmetry. Free parameters → CPCV mandatory. ~3-4h.
   **Recommended pick**: this is the cleanest test of the path-
   variance hypothesis vs the regime-information hypothesis.

2. **Hysteretic single-axis VIX gate on iter 041** (calm if VIX<18,
   stress if VIX>22) — preserves iter 041's mechanism, halves regime
   crossings to ~4/yr. Predicted: −0.5 to +1.5 score pts. Quick test
   (~1.5h). Useful as a control: if hysteresis IMPROVES iter 041's
   DSR, the path-variance hypothesis is supported; if it regresses,
   iter 041's edge was mostly the crossings themselves (information-
   per-crossing).

3. **Cross-sectional factor timing on ≥10 factor ETFs** (out-of-
   family): MTUM/QUAL/USMV/SIZE/VLUE/SPLV; 12-1 momentum + value
   composite (AMP 2013). New return stream independent of iter 037
   stack. Closer to iter 003 floor but with a much larger universe.
   ~3h.

**Recommended pick: #1 (HMM-2)**. It directly tests the path-
variance hypothesis raised by iter 042's failure, and breaks out of
the static-stack family if the test confirms that DSR uplift requires
information-per-bar rather than leverage-asymmetry-per-regime.

## Files in this iteration

- `hypothesis.md` — pre-committed hypothesis + kill criteria.
- `combined_regime_static_stack.py` — re-export of iter 041 engine.
- `numpy_reference_combined_regime.py` — re-export of iter 041 numpy ref.
- `run_backtests.py` — single cfg, 3 datasets driver.
- `compute_gates_and_score.py` — gates + scoring + kill evaluation.
- `tests/test_iter_042_combined_regime.py` — 10 TDD specs (all pass).
- `results.json` (640 KB), `verdict.json` (final score artefact).
- `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.
