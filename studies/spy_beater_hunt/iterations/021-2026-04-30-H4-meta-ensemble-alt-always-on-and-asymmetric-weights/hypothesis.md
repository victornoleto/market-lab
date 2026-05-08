# Iter 021 — Hypothesis (pre-commit)

**Slug**: `H4-meta-ensemble-alt-always-on-and-asymmetric-weights`

**Date**: 2026-04-30

**Cumulative n_trials**: 68 (prior iters 001-020) + 6 (this iter) = **74**

---

## Mission context

Following iter 020 (KILL #66 FIRED, 4-way 25/25/25/25 score 67 ≤ 71 → meta-axis
ceiling consolidated at 71 with diminishing returns at 4-way structure), the
meta-axis trajectory iter-018 → 019 → 020 (70 → 71 → 67) is **non-monotonic**.
3-way 33/33/34 (A2 + G2 IEF + F1 stack) at iter-019 retains as
closest-to-winner. Iter-020's "Suggested iter 021+" lesson explicitly recommends:

- (a) Test alternative always-on constituents in 3-way structure:
  - C₀ = F1 LETF 2.25× (G2 IEF sleeve standalone, no gate) at 34% weight
  - C₁ = pure NTSX 100% (highest CAGR runway, simplest concentrated equity)
  - C₂ = F1 stack 2× variant (NTSX 50% + GDE 30% + KMLM 20%, no TLT)
- (b) Asymmetric 3-way weights: 30/35/35 (F1-heavy), 35/30/35 (A2-and-F1-tilt),
  30/40/30 (G2-heavy) to map local optimum surface around 33/33/34.

**Pre-commit KILL** (per iter-020 lesson): if iter-021 max score ≤ 71, the
meta-axis ceiling is **DEFINITIVE at 71** within spy_beater rubric — no further
exploration value at meta-axis; user decision needed (declare hunt
EFFECTIVELY-CLOSED at 71 or pivot off meta-axis).

This iter executes (a) + (b) under a single 6-config sweep, maintaining N=6
PBO grid stability per iter-019 KILL #64 resolution.

---

## Hypothesis

**H₁ (alt always-on diversifier with higher CAGR runway lifts CAGR axis)**:
substituting F1 stack 1.41× (Sharpe 1.018, CAGR 11.95% standalone) with F1 LETF
2.25× (Sharpe 0.97, CAGR ~14% standalone — same composition as G2 IEF ON-state
but always-on no-gate) lifts the meta-blend CAGR aggregate by ~0.7-1.0pp via
runway lift, but may compress Sharpe by 0.02-0.05.

**H₂ (pure NTSX 100% as always-on Pareto-trades)**: replacing F1 stack with
pure NTSX 100% (50% S&P + 60% bonds via NTSX 90/60 stacking, ~1.5× notional,
standalone CAGR ~12-13% / Sharpe ~0.95 / MDD ~30%) provides simplest
concentrated-equity always-on. CAGR runway similar; Sharpe slightly lower;
MDD slightly higher than F1 stack.

**H₃ (F1 stack 2× variant — concentrated stack without TLT)**: using F1 stack
2× variant (NTSX 50% + GDE 30% + KMLM 20%, no TLT — equity-heavier vs F1
stack's NTSX 35% + GDE 30% + TLT 20% + KMLM 15%) tests if dropping TLT (a
2022-burdened duration asset) lifts CAGR floor without sacrificing Sharpe.

**H₄ (asymmetric 3-way weights at 30-40% granularity)**: weight perturbations
30/35/35, 35/30/35, 30/40/30 around iter-019's 33/33/34 map the local optimum
surface. If all 3 weight configs score ≤ 71, the weight-axis surface near apex
is FLAT — confirms 33/33/34 optimum is robust to ±5pp perturbations.

**H₅ (meta-axis ceiling DEFINITIVE at 71)**: trajectory iter-018 → 019 → 020
(70 → 71 → 67) shows non-monotonic ceiling at 71. If iter-021 max score ≤ 71
across 6 configs, the meta-axis Pareto frontier is empirically established at
71 with no further exploration value within spy_beater CAGR-anchored rubric.

---

## Constituents (specs frozen from prior iters + 3 NEW always-on variants)

### A2 — iter 006 `a6_tqqq_split_kmlm30_tlt10` (LRS QQQ-gated 3× LETF)
- score 67, mean CAGR 17.33%, MDD 49.73%, Sharpe 0.804
- ON: TQQQSIM 30% + QLDSIM 30% + KMLMSIM 30% + TLTSIM 10%; OFF: IEFSIM 100%
- Signal: QQQSIM 200d-SMA, lag 1d
- **Role**: highest-CAGR constituent — CAGR-floor anchor for meta-blends

### G2 IEF — iter 017 `g2_f1_letf_2x_sma200_ief` (LRS SPY-gated 2.25× F1 LETF)
- score 64, mean CAGR 14.02%, MDD 33.72%, Sharpe 0.970
- ON: UPROSIM 30% + TMFSIM 25% + IEFSIM 15% + UGLSIM 15% + KMLMSIM 15%;
  OFF: IEFSIM 100%
- Signal: SPYSIM 200d-SMA, lag 1d
- **Role**: mid-Sharpe + mid-CAGR moderate-decay LETF — bridge between G1 and A2

### F1 stack — iter 015 `f1_aw_stack_15x` (always-on multi-asset 1.41×) — BASELINE
- score 61, mean CAGR 11.95%, MDD 26.82%, Sharpe 1.018
- NTSXSIM 35% + GDESIM 30% + TLTSIM 20% + KMLMSIM 15% (always-on, no gate)
- **Role iter-019**: always-on structural diversifier — CAGR floor in
  bear-mode + permanent multi-asset decorrelation

### NEW: F1 LETF 2.25× always-on (substitutes F1 stack at H4.1)
- Composition same as G2 IEF ON-state but always-on (no SPY-200d-SMA gate):
  UPROSIM 30% + TMFSIM 25% + IEFSIM 15% + UGLSIM 15% + KMLMSIM 15%
- Standalone est: CAGR ~14% (G2 ON-state runs ~17% during bull regime;
  always-on captures less because of bear exposure ≈ -50% drawdown 2008/2022),
  Sharpe ~0.85-0.95, MDD ~50-55% (no gate buffer)
- **Role**: alternative always-on — higher CAGR runway than F1 stack but
  worse MDD profile. Tests CAGR-floor lift trade-off.

### NEW: pure NTSX 100% always-on (substitutes F1 stack at H4.2)
- NTSXSIM 1.0 (no gate)
- Standalone est: CAGR ~13-14% (NTSX = 90% S&P + 60% bonds, 1.5× notional),
  Sharpe ~0.85-0.90, MDD ~35-40%
- **Role**: simplest concentrated-equity always-on. Tests minimal-complexity
  alternative diversifier with similar runway.

### NEW: F1 stack 2× variant always-on (substitutes F1 stack at H4.3)
- NTSXSIM 50% + GDESIM 30% + KMLMSIM 20% (no TLT, no gate)
- Effective notional: 50%×1.5 + 30%×1.8 + 20%×1.0 = ~1.5× (similar to F1
  stack 1.41×)
- Standalone est: CAGR ~12-13% (similar runway to F1 stack), Sharpe ~0.95-1.00
  (slightly lower without TLT diversification), MDD ~30-35% (slightly higher
  without TLT cushion)
- **Role**: tests TLT contribution. If similar score → TLT marginal;
  if lower → TLT essential to F1 stack profile.

---

## Configs (6 — maintains N=6 PBO grid stability per iter-019 KILL #64)

### H4.1 — Alt always-on F1 LETF 2.25× at 33/33/34 (Group A — alternative diversifier)
**`h4_meta_3way_33a2_33g2_34f1letf2x`**
- 33% A2 + 33% G2 IEF + 34% F1 LETF 2.25× (always-on substitute)
- Linear-mean est: CAGR ~14.5%, MDD ~36-40%, Sharpe ~0.93
- Tests H₁: does higher-CAGR-runway always-on lift score above 71?

### H4.2 — Alt always-on pure NTSX 100% at 33/33/34 (Group A)
**`h4_meta_3way_33a2_33g2_34ntsx100`**
- 33% A2 + 33% G2 IEF + 34% NTSX 100% (always-on substitute)
- Linear-mean est: CAGR ~14.0%, MDD ~35%, Sharpe ~0.90
- Tests H₂: does simplest concentrated-equity always-on Pareto-trade well?

### H4.3 — Alt always-on F1 stack 2× variant (no TLT) at 33/33/34 (Group A)
**`h4_meta_3way_33a2_33g2_34f1stack_no_tlt`**
- 33% A2 + 33% G2 IEF + 34% F1 stack variant (NTSX 50 + GDE 30 + KMLM 20)
- Linear-mean est: CAGR ~13.5%, MDD ~31%, Sharpe ~0.97
- Tests H₃: does TLT removal preserve score? Tests TLT marginal contribution.

### H4.4 — Asymmetric 30/35/35 F1-and-G2-heavy (Group B — weight perturbations)
**`h4_meta_3way_30a2_35g2_35f1`**
- 30% A2 + 35% G2 IEF + 35% F1 stack (original F1 stack 1.41×)
- Linear-mean: CAGR (0.30)(17.33) + (0.35)(14.02) + (0.35)(11.95) = 14.30%,
  MDD (0.30)(49.73) + (0.35)(33.72) + (0.35)(26.82) = 36.13%,
  Sharpe (0.30)(0.804) + (0.35)(0.970) + (0.35)(1.018) = 0.937
- Tests H₄: does reducing A2 weight (CAGR-anchor) by 3pp + lifting both G2
  and F1 by 1-2pp Pareto-improve via Sharpe lift?

### H4.5 — Asymmetric 35/30/35 A2-and-F1-tilted (Group B)
**`h4_meta_3way_35a2_30g2_35f1`**
- 35% A2 + 30% G2 IEF + 35% F1 stack
- Linear-mean: CAGR (0.35)(17.33) + (0.30)(14.02) + (0.35)(11.95) = 14.45%,
  MDD (0.35)(49.73) + (0.30)(33.72) + (0.35)(26.82) = 36.86%,
  Sharpe (0.35)(0.804) + (0.30)(0.970) + (0.35)(1.018) = 0.929
- Tests H₄: does shifting weight FROM G2 IEF TO A2 (CAGR-axis) preserve score?

### H4.6 — Asymmetric 30/40/30 G2-heavy (Group B)
**`h4_meta_3way_30a2_40g2_30f1`**
- 30% A2 + 40% G2 IEF + 30% F1 stack
- Linear-mean: CAGR (0.30)(17.33) + (0.40)(14.02) + (0.30)(11.95) = 14.40%,
  MDD (0.30)(49.73) + (0.40)(33.72) + (0.30)(26.82) = 36.42%,
  Sharpe (0.30)(0.804) + (0.40)(0.970) + (0.30)(1.018) = 0.934
- Tests H₄: does G2 IEF weight increase (best mid-Sharpe constituent) lift
  Sharpe enough to break 71 ceiling?

---

## Pre-committed KILL conditions

(numbered after iter-020's KILL #70 — new KILLs start at #71)

### KILL #71 (iter-021 max score ≤ 71 → meta-axis ceiling DEFINITIVE at 71)
**Trigger**: max iter-021 score across 6 configs ≤ 71 AND iter-019's 71 retains.
**Implication**: meta-axis Pareto frontier within spy_beater CAGR-anchored
rubric is empirically established DEFINITIVELY at 71. No further exploration
value at meta-axis. iter-022+ should pivot off meta-axis OR declare hunt
EFFECTIVELY-CLOSED at 71 (user decision per mandate §1 + §7).

### KILL #72 (best iter-021 score ≥ 75 → STRONG tier reachable at meta-axis)
**Trigger**: ANY iter-021 config with score ≥ 75 AND winner_conditions_met=True.
**Implication**: tier STRONG empirically reached at meta-axis; ceiling lifts
above 75. Hunt status REOPENED stronger; iter-022+ targets ≥80 via further
weight optimization OR alternative constituent substitution.

### KILL #73 (alt always-on F1 LETF 2.25× Pareto-dominates F1 stack at H4.1)
**Trigger**: H4.1 score > 71 AND mean CAGR > 15.04% (iter-019 baseline).
**Implication**: higher-CAGR-runway always-on diversifier (F1 LETF 2.25×)
Pareto-dominates lower-CAGR no-decay stack (F1 stack 1.41×) at meta-axis.
Reframes the always-on constituent recommendation; iter-022+ should adopt
F1 LETF 2.25× always-on as new baseline.

### KILL #74 (pure NTSX 100% always-on FAILS or scores < 65 at H4.2)
**Trigger**: H4.2 fails CAGR bar OR score < 65.
**Implication**: pure concentrated-equity always-on insufficient as
diversifier; multi-asset stack (TLT/KMLM/GDE) is essential. Confirms
diversification value beyond pure equity stacking.

### KILL #75 (F1 stack 2× variant Pareto-matches F1 stack at H4.3)
**Trigger**: H4.3 score ≥ 70 AND mean Sharpe ≥ 1.020.
**Implication**: TLT contribution to F1 stack is marginal; no-TLT variant
matches with-TLT variant within rubric noise. Simplifies always-on
recommendation. Strengthens 2022 stress-period robustness narrative
(no-TLT avoids 2022 duration loss).

### KILL #76 (asymmetric weights all ≤ 71 across H4.4-H4.6 — weight surface flat)
**Trigger**: H4.4 + H4.5 + H4.6 all score ≤ 71.
**Implication**: weight-axis surface near apex (33/33/34) is FLAT for ±5pp
perturbations. Confirms 33/33/34 optimum is robust; weight-axis exploration
exhausted at this granularity.

---

## Expected outcomes

**Pessimistic (no breakthrough; KILL #71 fires)**: all 6 configs score 65-71,
iter-019's 71 retains as ceiling. KILL #71 + #76 fire; meta-axis ceiling
DEFINITIVE at 71. User declares hunt EFFECTIVELY-CLOSED.

**Realistic (incremental improvement)**: H4.1 (F1 LETF 2.25× always-on) scores
70-73 via CAGR lift +0.5-1.0pp. Asymmetric weights H4.4-H4.6 score 69-71.
Meta-axis ceiling lifts to 72-73 but STRONG tier (≥75) NOT reached.

**Optimistic (breakthrough; KILL #72 fires)**: H4.1 or H4.6 scores 75-77 via
super-linear decorrelation gain at higher-CAGR-runway always-on substitution.
KILL #72 fires; tier STRONG reached; iter-022+ targets 80+.

**Most likely outcome based on iter-020 mechanism analysis**: H4.1 scores
69-72 (CAGR lift +0.5pp gives +1pt; Sharpe drop −0.04 gives 0pts; net +0-1pt
vs iter-019's 71). H4.2 scores 64-68 (NTSX-only loses MDD/Sharpe diversity;
KILL #74 likely fires). H4.3 scores 68-71 (TLT removal marginal). Asymmetric
H4.4-H4.6 score 69-71 (weight-axis flat near apex). KILL #71 + #76 likely
fire; KILL #72 unlikely. Meta-axis ceiling EMPIRICALLY DEFINITIVE at 71.

---

## INCOMPLETE flags

- **Synth caveats inherited from prior iters**: SPYSIM/QQQSIM/TQQQSIM/QLDSIM/
  UPROSIM/TMFSIM/IEFSIM/KMLMSIM/TLTSIM/UGLSIM/NTSXSIM/GDESIM all DIRECT in
  testfolio cache; no new synth needed. NTSX 100% standalone tested in iter
  015 baseline (F1 stack contains NTSX 35%); pure NTSX 100% extends weight
  to 100% — no new infra.
- **Cumulative n_trials = 74**: DSR worst-p threshold tightens. Worst case
  bound `q_value ≈ 0.05/74 = 6.76e-04`. Should comfortably pass with
  iter-020's worst p = 9.28e-05 baseline given similar architectural family.
- **Meta-ensemble combinatorial dimensions** (which 3 of 68 prior configs
  + 3 new always-on variants × what weights) NOT counted in DSR n_trials.
  Honest n_trials likely larger; DSR margin remains conservative-loose.
- **lh_56y rolling = 0 windows**: rolling_metrics computes only on spy_real
  overlap; pass-rates from spy_real only (n=18/13/8/3 windows for 5/10/15/20y).
- **G3 walk-forward MDD bar at 25%**: STILL FAILS by 0.4-3.5pp on both
  datasets in all prior meta-axis iters. Adding higher-leverage always-on
  (F1 LETF 2.25× at 34%) likely WORSENS wf_mdd (no gate buffer).
- **PBO N=6 stability**: maintained per iter-019 KILL #64 resolution.
- **All assets DIRECT in testfolio cache** — no new synth, no new infra.
  Reuses "blend" + "lrs" + "static" spec types from iter 018-020. 771 tests
  baseline preserved.

---

## Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple
  alpha streams — alternative always-on constituent substitution at 3-way
  meta-ensemble axis; tests whether higher-CAGR-runway diversifier
  Pareto-dominates lower-CAGR no-decay stack.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking generalized:
  F1 LETF 2.25× always-on as 3rd constituent tests if higher-leverage
  multi-asset stack lifts blend CAGR without sacrificing decorrelation gain.
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate at
  meta-ensemble: gates remain on QQQ + SPY signals; tests if always-on
  diversifier composition matters more than gate decorrelation.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM) — present in
  all 3 always-on variants (15-20%); F1 stack baseline 15%, F1 LETF 2.25×
  15%, NTSX 100% 0% (concentrated equity), F1 stack 2× variant 20%.
- Bridgewater All-Weather (Dalio 1996) — F1 stack ON-state composition vs
  always-on substitution variants; tests if All-Weather thesis holds without
  TLT (H4.3) or with concentrated equity (H4.2) or with leveraged variant
  (H4.1).
- `[advances_fin_ml, p.31-34]` factor framework — meta-ensemble axis weight
  + always-on substitution adds to architectural taxonomy.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 74; worst p ≤ 0.05
  threshold tightens; iter-020 baseline p = 9.28e-05 << 0.05 expected to hold.
- `[advances_fin_ml, p.208-211]` PBO grid-level — N=6 stability MAINTAINED per
  iter-019 KILL #64 resolution.
- `[advances_fin_ml, p.196-202]` bootstrap CI — G6 expected to pass on both
  datasets with comfortable margin per iter-020 baseline.

---

## Pre-iter mandate compliance

This iter remains under mandate §1 MAINTENANCE MODE (2026-04-23). Score 71 from
iter-019 < 90 WINNER threshold; no winner candidate trips mandate §7 override
request. F1+SPLIT incumbent fallback retains deploy-ready status. iter-021
exploration is **RESEARCH ONLY**.

If KILL #71 fires (max ≤ 71), the meta-axis ceiling is DEFINITIVE at 71 →
user decision needed: (a) declare hunt EFFECTIVELY-CLOSED at 71, document
IMPOSSIBILITY_RESULT-light per iter-011 template, F1+SPLIT confirmed deploy
fallback; OR (b) pivot off meta-axis to constituent-level architectural
changes (require new families beyond 8 fam + 3 hybrid + 3-axis meta surface).

If KILL #72 fires (≥ 75), the meta-axis trajectory continues upward; iter-022+
research authorized within mandate §1 MAINTENANCE MODE.
