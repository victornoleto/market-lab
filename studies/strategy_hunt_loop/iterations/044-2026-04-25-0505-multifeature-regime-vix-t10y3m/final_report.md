# Iteration 044 — Final Report

## Verdict

🥈 **PROMISING (score 74/100, winner_conditions_met=False)** —
**regression vs iter 041 (84) by 10 points**, deeper than iter 042's
74 (compound asymmetry) and iter 043's 79 (hysteresis). The
hypothesis "richer information per bar via 2-feature composite
gate improves DSR" is **FALSIFIED** on the specific construction
tested here. Three pre-committed kills fired:

- **Kill A FIRED** — Sharpe regression vs iter 041 by ≥0.05 on **2/3
  datasets** (edu Δ −0.057, ndx Δ −0.067; spy −0.035 within band).
  Multi-feature gate destructively interferes with iter 041's binary
  VIX-20 gate.
- **Kill B FIRED** — DSR worst-p **0.2400** (educational) ≥ iter 041's
  0.168, and worse than iter 042 (0.216) and iter 043 (0.189). The
  "info per bar via T10Y3M" hypothesis is the **third independent
  attack** on iter 041's 84-ceiling that regresses DSR. The ceiling
  is now localised on **three orthogonal axes** (gate amplitude,
  gate frequency, gate input).
- **Kill D FIRED** — score **74** < iter 041's 84 (strict no-regression).

Kills C / E / F clean: MDD safe across all 3 datasets, G7 cross-lib
parity ≤ 0.13 pp, regime churn at ~9 RT/yr (within bounds).

Despite the regression, iter 044 is still PROMISING (not FAIL):
Sharpe edge cross-dataset preserved at 25/25 (3/3 beat benchmark by
≥+0.10), MDD ceiling 15/15, robustness 9/9 sub-windows positive,
6/7 gates per dataset. The composite mechanism IS informative
(stress conditional Sharpe +0.11-0.27 above calm) — it just doesn't
relieve the DSR variance penalty.

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen) | CAGR (vs 0.8×bench) | MDD (vs bench+5pp) | gates | DSR p |
|---|---|---|---|---|---|
| educational | **0.9698** (+0.290) | 12.57% (+3.39pp) ✅ | 29.89% (−30.25pp) ✅ | 6/7 | **0.2400** ❌ |
| spy_real    | **1.0959** (+0.196) | 13.31% (+1.33pp) ✅ | 29.89% (−8.81pp) ✅ | 6/7 | 0.2045 ❌ |
| ndx_real    | **1.0962** (+0.141) | 14.69% (−0.66pp) ❌ | 37.82% (−2.30pp) ✅ | 6/7 | 0.2288 ❌ |

vs **iter 041** (TOP-K #1, the prior STRONG-84 ceiling — same weights,
single-feature binary VIX gate at 20):

| dataset | iter 041 Sharpe | iter 044 Sharpe | Δ Sharpe | iter 041 MDD | iter 044 MDD | Δ MDD | iter 041 DSR | iter 044 DSR |
|---|---|---|---|---|---|---|---|---|
| educational | 1.027 | 0.970 | **−0.057** ❌ | 27.60% | 29.89% | +2.29pp | 0.168 | **0.240** ↑↑ |
| spy_real    | 1.131 | 1.096 | −0.035 | 24.65% | 29.89% | +5.24pp | 0.167 | **0.205** ↑ |
| ndx_real    | 1.164 | 1.096 | **−0.067** ❌ | 30.84% | 37.82% | +6.98pp | 0.156 | **0.229** ↑↑ |

Multi-feature composite gate **strictly worsens MDD on all 3
datasets** vs iter 041 (by 2.3-7.0 pp), Sharpe on 3/3, and DSR
worst-p on 3/3. The mechanism is the third independent
regression-via-perturbation of iter 041:

| iter | perturbation type                         | DSR worst-p | Δ vs iter 041 | score |
|---|---|---|---|---|
| 041 | (baseline binary VIX-20 gate)             | 0.168       | —             | **84** |
| 042 | gate amplitude (compound asymmetry)       | 0.216       | +0.048        | 74 |
| 043 | gate frequency (Schmitt hysteresis)       | 0.189       | +0.021        | 79 |
| **044** | **gate input (2-feature composite)**  | **0.240**   | **+0.072** ↑ worst | **74** |

This iter is the **deepest DSR regression of the three** — adding a
second feature to the gate computation moves the worst-p further
from significance than either gate-timing perturbation. The
mechanism is structurally different (input enrichment vs timing
perturbation) but the result is qualitatively the same: any
modification of iter 041's instantaneous-binary-update construction
introduces variance that dominates the gain.

vs **iter 037** (the unconditional 0.6/0.45/0.45 1.5× baseline):

| dataset | iter 037 Sharpe | iter 044 Sharpe | Δ |
|---|---|---|---|
| educational | 0.983 | 0.970 | −0.013 |
| spy_real    | 1.154 | 1.096 | −0.058 |
| ndx_real    | 1.174 | 1.096 | −0.078 |

iter 044 underperforms even the *unconditional* baseline on spy/ndx —
the multi-feature gate is actively harmful on the post-2009 era. Only
educational gets a small lift from the 2008 stress regime detection.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 25 | 25 | 3/3 datasets beat bench by ≥+0.10 (preserved across 037→044) |
| 2 Gates | 19 | 25 | edu 6/7, spy 6/7, ndx 6/7 → 5+5+5+4 cross-bonus = 19 (G2 DSR sole fail) |
| 3 DSR | **0** | 15 | **worst p=0.2400** (educational) — falls in p≥0.20 band (0pts). **Worst of any iter on iter 041 weights.** |
| 4 CAGR floor | **10** | 15 | **ndx 14.69% < 15.35% threshold by 0.66pp** — fails. edu/spy clean. |
| 5 MDD ceiling | 15 | 15 | All 3 datasets clean (edu by 30pp, spy by 9pp, ndx by 2.3pp). |
| 6 Robustness | 5 | 5 | 9/9 sub-windows Sharpe > 0 (preserved from iter 041/043) |
| **total** | **74** | **100+5** | tier: **🥈 PROMISING** |

## Configuration tested

```python
CFG = {
    "cfg_id": "multifeature_vix_t10y3m_z252_eq_w_tau0_70_40_40_30_55_55",
    "z_window": 252,                              # 1y rolling lookback
    "feature_weights": {"vix": 0.5, "neg_t10y3m": 0.5},  # equal-weighted
    "stress_threshold": 0.0,                      # composite-z > 0 → stress
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},
    "feature_lag_days": 1,                        # iter 041 convention
    "rebalance": "daily",
    "cost_bps_per_leg": 0.0002,
    "funding_cost_modeled": False,
}
```

Single pre-committed config — no grid, no sweep, no post-hoc tuning.
All hyperparameters set to principled defaults: 252-day window
(standard FF regression length); 0.5/0.5 equal feature weights (no
preference for VIX over T10Y3M); threshold 0.0 (median split of
standardised composite). Cumulative n_trials advance:
**4308 → 4309 (+1)**.

## Regime / composite-score summary

| dataset | calm_frac | stress_frac | RT/yr | flips total | avg lev | composite μ | composite σ |
|---|---|---|---|---|---|---|---|
| educational | 52.3% | 47.7% | 8.97 | 363 | 1.452 | +0.010 | 0.962 |
| spy_real    | 52.4% | 47.6% | 8.80 | 295 | 1.452 | +0.022 | 0.998 |
| ndx_real    | 51.5% | 48.5% | 8.71 | 281 | 1.452 | +0.046 | 0.985 |

vs iter 041 (binary 20-gate, calm_frac ~63-68%, RT/yr ~7-8): the
2-feature composite **classifies far MORE bars as stress** (47-49%
vs 32-37%) because the threshold τ=0 splits the composite at its
median. The composite distribution is approximately N(0,1) as
expected (μ ≈ 0, σ ≈ 1.0).

The higher stress fraction means the strategy spends more time at
the defensive 1.40× tilt — and on the post-GFC era this *under-
exposure* costs more than it saves: the post-2009 era had a high
unconditional equity Sharpe (~0.90-0.96) that the composite gate
mistakes for stress 47% of the time.

## Conditional metrics (regime decomposition)

| dataset | calm bars | calm Sharpe | stress bars | stress Sharpe |
|---|---|---|---|---|
| educational | 2670 | +1.016 | 2431 | +0.921 |
| spy_real    | 2216 | +1.020 | 2010 | +1.182 |
| ndx_real    | 2094 | +0.980 | 1972 | +1.244 |

Stress conditional Sharpe is higher than calm on spy/ndx (consistent
with the iter 041 pattern), but the **edge is much smaller than iter
041's**: iter 041 stress Sharpe was 1.14/1.45/1.42 vs calm 0.97/0.95/
1.04 (Δ +0.17/+0.50/+0.38). Iter 044 stress Sharpe is 0.92/1.18/1.24
vs calm 1.02/1.02/0.98 (Δ −0.10/+0.16/+0.26). On educational the
ranking REVERSES — calm now outperforms stress by 0.10. The
classifier IS less informative than iter 041's binary VIX-20 gate.

## Pre-committed kill criteria status

| kill | fired? | observed | threshold | interpretation |
|---|---|---|---|---|
| **A** Sharpe regress vs iter 041 by ≥0.05 on ≥2 ds | ❌ **fired** | 2/3 (edu Δ−0.057, ndx Δ−0.067) | ≥ 2 of 3 | Multi-feature gate destructively interferes with iter 041 |
| **B** DSR worst-p ≥ iter 041's 0.168 | ❌ **fired** | 0.2400 (edu) | ≥ 0.168 | "Info per bar" hypothesis FALSIFIED — composite gate adds variance, not signal |
| **C** MDD breach on any dataset | ✓ clean | 0/3 | ≥ 1 | Composite gate preserves tail protection (smaller margin than iter 041) |
| **D** Score < 84 | ❌ **fired** | 74 | < 84 | **−10 pts vs iter 041 (deepest regression of any 041-perturbation iter)** |
| **E** G7 cross-lib > 3pp | ✓ clean | max 0.123pp | > 3.0 pp | engine clean (full-pipeline numpy ref agrees with pandas) |
| **F** Excessive churn | ✓ clean | max 8.97 RT/yr | > 12 | Composite gate churn is comparable to iter 041's ~7-8 |

## Why DSR worsened (the structural finding)

**Hypothesis assumed**: adding T10Y3M as a 2nd orthogonal feature
(corr(ΔVIX, ΔT) = −0.15 to −0.22 across datasets) to the gate
computation should add information density per bar without changing
the instantaneous-update property — the iter 042/043 lesson was
"don't perturb gate timing", and a multi-feature instantaneous gate
honors that.

**Reality observed**: the composite gate fires at the median of a
DIFFERENT distribution than iter 041's (composite z-score at 0 vs
VIX level at 20). On the post-GFC era specifically:

1. **Median-split semantics differ from level-threshold semantics.**
   iter 041's "VIX < 20" classifies ~63-68% of bars as calm. The
   composite-z < 0 classifies only ~52% as calm. This means iter 044
   assigns **defensive (1.40×) tilt to ~13-16% MORE bars** than iter
   041, including bars where the realised return belongs to the
   high-Sharpe post-GFC distribution. The under-exposure costs Sharpe.

2. **T10Y3M innovation noise dominates its signal at daily frequency.**
   T10Y3M moves slowly month-to-month (recession indicator on
   year-scale), but the 252-day rolling z-score amplifies daily Δ
   into a high-frequency stress signal. A 5bp daily move in T10Y3M
   that normalises to z = +1.5 will flip the composite to stress
   despite zero change in the underlying recession risk.

3. **Composite threshold-crossings happen on a DIFFERENT trigger
   distribution than VIX-20.** iter 041's gate fires on actual VIX
   spikes (real risk events). iter 044's gate fires on either VIX or
   T10Y3M z-score crossings — and the OR-like nature of the additive
   composite means **either feature can drag the gate into stress**
   even when the other is benign. This is a more PERMISSIVE
   classifier (more stress bars), not a more PRECISE one.

DSR penalises the residual variance at the path level. iter 041's
binary gate at VIX=20 has very few false positives because VIX-20
has a strong empirical recession-risk signal. iter 044's composite
has many false positives because the equal-weight aggregation
pollutes the precise VIX signal with noisy T10Y3M innovations on
non-recession days.

In short: **iter 041's binary VIX-20 gate is also a local optimum on
the GATE-INPUT axis.** The "richer information per bar via more
features" intuition fails when the additional feature has a worse
signal-to-noise ratio at the relevant frequency. The path forward to
break the 84 ceiling on the DSR axis must NOT add daily-frequency
features that dilute VIX's already-strong recession signal.

This jointly with iter 042 (gate amplitude perturbation) and iter
043 (gate frequency perturbation) localises iter 041's 84-ceiling on
**three independent structural axes**:

- gate amplitude (iter 042: 1.7×/1.0× swing) → DSR 0.216
- gate frequency (iter 043: hysteresis [18, 22]) → DSR 0.189
- gate input (iter 044: 2-feature composite) → DSR 0.240

The 84-ceiling is not just narrow on one perturbation type — it is a
**plateau** in the local neighbourhood across three perturbation
directions. Any naive enrichment of iter 041 fails.

## What worked / what didn't

**What worked**

- **Sharpe edge cross-dataset preserved** (25/25): 3/3 datasets
  beat benchmark by ≥+0.10. The composite mechanism is still
  generating equity premium.
- **MDD axis clean** (15/15): no breaches, all 3 datasets within
  +5pp of benchmark MDD.
- **Robustness 9/9** sub-windows positive across all 3 datasets.
- **G7 cross-lib parity** max 0.123 pp, well below 3 pp threshold.
- **Engine TDD** (13/13 specs pass): the full pipeline (rolling
  z-score, composite construction, lag application, weight
  switching, cost accounting) is verified before backtest.
- **Feature orthogonality confirmed**: corr(ΔVIX, ΔT10Y3M) =
  −0.15 to −0.22 across datasets, validating the orthogonality
  premise of the hypothesis.

**What didn't (the 10-point regression)**

- **DSR axis regressed deepest of any iter** on iter 041's weights.
  Worst-p moved from 0.168 → 0.240 (+0.072), worse than iter 042
  (0.216) or iter 043 (0.189). The "info per bar" hypothesis FAILS
  on this multi-feature axis.
- **Sharpe regress on edu + ndx by 0.057-0.067**: composite gate
  classifies more stress bars than iter 041's binary gate, and the
  extra defensive bars cost premium on the post-2009 high-Sharpe
  equity distribution.
- **CAGR floor on ndx fails by 0.66pp**: ndx_real CAGR 14.69% slips
  under the 15.35% threshold. The same under-exposure mechanism that
  costs Sharpe also costs CAGR on tech-heavy QQQ.
- **MDD weakens vs iter 041** by 2.3-7.0 pp (still within +5pp gate
  except spy +5.24pp marginal). Composite gate's larger calm/stress
  swings during 2009/2020/2022 produced more retracement.

## Main lesson (for future iterations)

**iter 041's 84-ceiling is robust across three structurally distinct
perturbation axes:**

| axis | iter | direction | DSR worst-p | score |
|---|---|---|---|---|
| (baseline) | 041 | binary VIX-20 single feature | 0.168 | 84 |
| amplitude  | 042 | compound 1.7×/1.0× × weight tilt | 0.216 | 74 |
| frequency  | 043 | hysteresis [18, 22] | 0.189 | 79 |
| input      | 044 | 2-feature composite (VIX + T10Y3M) | 0.240 | 74 |

The pattern: **any structural enrichment of iter 041's gate
introduces variance that dominates the precision gain**. The
"instantaneous Bayesian update at VIX=20" property of iter 041 is
simultaneously the source of its 84-ceiling AND of its narrowness —
the gate is precisely tuned to VIX's recession-risk signal at the
point where the signal-to-noise ratio peaks (level 20), and any
modification (different threshold via composite, lagged response via
hysteresis, amplified swings via leverage compound) blunts the
signal more than it sharpens.

**Three failed enrichment directions imply the path forward is
out-of-family**, not in-family refinement:

1. **Out-of-family return-stream addition**: instead of modifying
   iter 041's gate, add a SEPARATE return source (factor-timing
   overlay, cross-sectional momentum, options skew, FX carry) to
   iter 041's net returns. New DSR-positive contribution, not a
   gate refinement.
2. **Different base-stack family**: abandon the 3-leg static stack
   and try a different architecture (long-short factor portfolio,
   convex/option-based payoff, term-structure carry). The 84-ceiling
   may be specific to the 3-leg-with-VIX-gate family.
3. **Different gate ASSET class**: instead of VIX (equity vol),
   try CDS spreads, GOLD/COPPER ratio, or USD index — a regime
   indicator from a DIFFERENT market.

**Iter 044 explicitly closes the multi-feature instantaneous-gate
direction on iter 041 weights.** Combined with iter 042 (amplitude)
and iter 043 (frequency), the 3-axis closure leaves the
**out-of-family return-stream addition** as the cleanest open
direction.

## Structural dead-ends discovered

**Closes "multi-feature composite instantaneous gate (VIX + T10Y3M
equal-weighted)" on iter 041 weights**: a 2-feature standardised
composite with median split classifies more bars as stress (52% vs
iter 041's 64-67%), under-exposes during the post-GFC equity
recovery, regresses Sharpe on edu + ndx by 0.06, and worsens DSR
worst-p from 0.168 to 0.240 — the deepest DSR regression of any iter
on iter 041's weight architecture.

**Joint closure** with iter 042 + iter 043: any gate enrichment
direction on iter 041 — amplitude (042), frequency (043), or input
(044) — regresses DSR by 4-7pp. The 84-ceiling is a **plateau**
across the local neighbourhood, not a narrow ridge along one axis.

**Open paths preserved**: out-of-family return-stream addition
(factor timing, cross-sectional momentum, options overlay, FX
carry); different gate ASSET class (CDS, gold/copper ratio, DXY);
different base-stack family (long-short factor, convex payoff,
term-structure carry).

This is a **PROMISING-tier closure** (74/100, not FAIL): the
mechanism is still informative (Sharpe edge preserved cross-dataset,
MDD clean, robustness 9/9). The closure is on the *specific
multi-feature gate construction*, not on multi-feature regime
detection in general. A different feature weighting (e.g., 0.8 VIX +
0.2 neg-T10Y3M, downweighting T10Y3M's noise contribution) might
recover some of the lost edge — but iter 044 was pre-committed to
equal weights to avoid post-hoc tuning.

## Citations used

- **Primary**:
  - `[advances_fin_ml, ch.17-18]` — López de Prado on multi-feature
    regime detection. The 2-feature composite is a 1-feature
    generalisation; the result that it does NOT improve DSR worst-p
    is a refinement of the textbook claim that "more features =
    higher posterior precision". Precision gain only obtains when
    feature SNR matches the decision frequency.
  - `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity
    stack with regime-conditional weights (preserved from iter 041).
- **Supporting**:
  - `[advances_fin_ml, p.162-164]` — VIX_{t-1} no-look-ahead lag
    (preserved from iter 041; rolling z-score uses past 252 only).
  - `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
    the deflator's variance term is the binding mechanism (and the
    one that iter 042+043+044 jointly localise to a plateau).
  - Estrella-Hardouvelis (1991), JF 46(2), 555-576, DOI
    10.1111/j.1540-6261.1991.tb04617.x — T10Y3M as canonical
    recession leading indicator (the feature added in iter 044).
  - Bauer-Mertens (2018), FRBSF Economic Letter 2018-07 — modern
    empirical evidence that T10Y3M outperforms T10Y2Y for recession
    forecasting; supports daily-frequency use.
  - Whaley (2009), JPM 35(3), 98-105, DOI 10.3905/JPM.2009.35.3.098.
  - Bekaert-Hoerova (2014), J Econometrics 183(2), SSRN 2294327.
  - Hamilton (1989), Econometrica 57(2), DOI 10.2307/1912559.
  - Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084.
  - Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021.
- **Methodology**:
  - `[advances_fin_ml, p.31-34]` — G7 cross-library parity gate.
  - `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.

## Next iteration suggestions

iter 044 + iter 042 + iter 043 jointly localise iter 041's 84-ceiling
to a **plateau across 3 structural axes** (amplitude / frequency /
input). The remaining open directions are STRUCTURALLY out-of-family:

1. **Out-of-family return-stream addition** *(STRONGLY RECOMMENDED)* —
   add a SEPARATE DSR-positive return source to iter 041's net
   returns instead of refining its gate. Specifically:
   - **iter 039 VRP basket overlay on iter 037**: the iter 039 basket
     achieves DSR worst-p = 0.075 (vs iter 041's 0.168) on a *different*
     return mechanism. Layering iter 039's net (1/3 SPY + 1/3 QQQ +
     1/3 IWM short put-spread VRP) on top of iter 041's net stack
     could compound DSR if the cross-correlation is low. The
     iter 032 attempt at composing 015 + 031 failed by MDD breach;
     iter 039 has lower per-leg DD than iter 031, so the composition
     risk is lower. ~3h.
   - **Cross-sectional factor timing on ≥10 factor ETFs**: completely
     separate return stream, AMP 2013-style 12-1 momentum + value
     composite on MTUM/QUAL/USMV/SIZE/VLUE/SPLV. Bypasses the static-
     stack ceiling entirely. ~3h.

2. **Different gate ASSET class on iter 041 weights** — try a
   regime indicator from a DIFFERENT market (CDS HY-IG spread,
   GLD/CPER ratio, DXY level z-score). The hypothesis: VIX's
   instantaneous-update precision is asset-specific; a non-equity-vol
   regime indicator may have its own local optimum at a different
   threshold without dragging in T10Y3M's noise. ~3h.

3. **ML meta-label on iter 041 base** (`[advances_fin_ml, ch.3]`) —
   binary open/skip classifier on iter 041's signals using
   (VIX, VXN, RVX, VVIX, T10Y3M, EBP, skew). Walk-forward fitted.
   This is fundamentally different from iter 044: instead of *modifying
   the gate input*, it learns a meta-classifier on top of iter 041's
   raw output. The iter 044 result suggests the additive composite
   is the wrong functional form — a learned non-linear meta-classifier
   may extract value where the linear composite failed. ~4h.

**Recommended pick: #1a (iter 039 basket overlay on iter 037)**.
Iter 044's closure on multi-feature gate enrichment makes the
"out-of-family return-stream addition" the cleanest path: it
sidesteps the 3-axis 84-plateau by going DSR-positive via a
DIFFERENT mechanism rather than refining the gate. Iter 032 risk
re-trigger is mitigated because iter 039's per-leg DD is lower than
iter 031's.

## Files in this iteration

- `hypothesis.md` — pre-committed hypothesis + kill criteria.
- `multifeature_regime_gate.py` — pandas engine (rolling z-score,
  composite gate, weight switching).
- `numpy_reference_multifeature.py` — full-pipeline numpy reference
  (G7 gate detects bugs in BOTH composite construction AND weight
  switching).
- `run_backtests.py` — single cfg, 3 datasets driver.
- `compute_gates_and_score.py` — gates + scoring + kill evaluation.
- `tests/test_iter_044_multifeature.py` — 13 TDD specs (all pass).
- `results.json` (~640 KB), `verdict.json` (final score artefact).
- `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.
