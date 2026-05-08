# Iter 020 — Hypothesis (pre-commit)

**Slug**: `H3-meta-ensemble-4way-and-alt-3way-g1-ief`

**Date**: 2026-04-30

**Cumulative n_trials**: 62 (prior iters 001-019) + 6 (this iter) = **68**

---

## Mission context

Following iter 018 (KILL #59 fired, score 70 broke 67-cap via 2-way meta-ensemble) and
iter 019 (KILL #65 fired, score 71 broke 70-cap via 3-way 33/33/34 equal-weight blend
of A2 + G2 IEF + F1 stack), the meta-ensemble axis has shown **two consecutive
incremental improvements** (67 → 70 → 71). Iter 019's "Suggested iter 020+" lesson
explicitly recommends:

- (a) **Different 3-way combinations** — replace G2 IEF (mid-Sharpe 0.97) with G1 IEF
  (best Sharpe 1.080, best MDD 18.57%, but FAILS CAGR alone at 10.34%) to test if
  Sharpe-anchored constituent lifts the meta-blend.
- (b) **4-way blends** — A2 + G1 IEF + G2 IEF + F1 stack at 25/25/25/25 to test if
  adding 4th decorrelation source breaks 71-cap.
- (c) **Asymmetric 3-way weights** — to map the Pareto frontier finer.

Pre-commit KILL: if iter 020 ≤ 71 → meta-axis ceiling at 71 with diminishing returns;
if ≥ 75 → STRONG tier empirically reachable.

This iter executes (a) + (b) + a small slice of (c) under a single 6-config sweep,
maintaining N=6 PBO grid stability (vs iter-018 N=3 instability artifact resolved
by iter-019).

---

## Hypothesis

**H₁ (4-way Pareto-improves over 3-way)**: a 4-way blend (A2 + G1 IEF + G2 IEF +
F1 stack) at appropriate weights breaks iter-019's 71-cap by adding a 4th
decorrelation source (G1 IEF's no-decay 1.41× stack with SPY-200d-SMA gate).
G1 IEF's best-in-hunt Sharpe 1.080 + best-in-hunt MDD 18.57% should lift the
blend's Sharpe + MDD axes; A2 weight reduction (50% → 25-30%) trades CAGR floor
for diversification.

**H₂ (alt 3-way with G1 IEF Pareto-dominates iter-019 with G2 IEF)**: replacing
G2 IEF with G1 IEF in the 3-way structure (A2 + G1 IEF + F1 stack at 33/33/34)
lifts Sharpe + MDD via better constituent profile, but may compress CAGR floor
(linear-mean 13.13% vs iter-019's 14.43%).

**H₃ (F1 stack is essential — drop F1 → CAGR fails OR score drops)**: a 3-way
all-gated blend (A2 + G1 IEF + G2 IEF) without F1 stack always-on may pass
CAGR bar (linear-mean 13.90%) but loses the structural diversification gain
that delivered iter-019's Sharpe lift +0.094 above linear.

**H₄ (meta-axis ceiling consolidates between 71-75)**: trajectory iter-018 → 019
shows +1pt per layer; if iter-020 4-way adds another +1-2pts (72-73), the
trend continues; if 4-way matches 3-way (71) or drops, the meta-axis ceiling
is at 71 with diminishing returns from additional structural complexity.

---

## Constituents (specs frozen from prior iters)

### A2 — iter 006 `a6_tqqq_split_kmlm30_tlt10` (LRS QQQ-gated 3× LETF)
- score 67, mean CAGR 17.33%, MDD 49.73%, Sharpe 0.804
- ON: TQQQSIM 30% + QLDSIM 30% + KMLMSIM 30% + TLTSIM 10%; OFF: IEFSIM 100%
- Signal: QQQSIM 200d-SMA, lag 1d
- **Role**: highest-CAGR constituent (17.33%) — CAGR-floor anchor for meta-blends

### G1 IEF — iter 016 `g1_f1_stack_sma200_ief` (LRS SPY-gated 1.41× F1 stack)
- score 61, mean CAGR 10.34% (FAILS CAGR alone), MDD 18.57% (BEST OVERALL),
  Sharpe 1.080 (BEST OVERALL)
- ON: NTSXSIM 35% + GDESIM 30% + TLTSIM 20% + KMLMSIM 15%; OFF: IEFSIM 100%
- Signal: SPYSIM 200d-SMA, lag 1d
- **Role**: best-Sharpe + best-MDD constituent — Sharpe/MDD-axis anchor

### G2 IEF — iter 017 `g2_f1_letf_2x_sma200_ief` (LRS SPY-gated 2.25× F1 LETF)
- score 64, mean CAGR 14.02%, MDD 33.72%, Sharpe 0.970
- ON: UPROSIM 30% + TMFSIM 25% + IEFSIM 15% + UGLSIM 15% + KMLMSIM 15%;
  OFF: IEFSIM 100%
- Signal: SPYSIM 200d-SMA, lag 1d
- **Role**: mid-Sharpe + mid-CAGR moderate-decay LETF — bridge between G1 and A2

### F1 stack — iter 015 `f1_aw_stack_15x` (always-on multi-asset 1.41×)
- score 61, mean CAGR 11.95%, MDD 26.82%, Sharpe 1.018
- NTSXSIM 35% + GDESIM 30% + TLTSIM 20% + KMLMSIM 15% (always-on, no gate)
- **Role**: always-on structural diversifier — CAGR floor in bear-mode +
  permanent multi-asset decorrelation

---

## Configs (6 — maintains N=6 PBO grid stability per iter-019 KILL #64)

### H3.1 — 4-way equal-weight (CORE TEST)
**`h3_meta_4way_25a2_25g1_25g2_25f1`**
- 25% A2 + 25% G1 IEF + 25% G2 IEF + 25% F1 stack
- Linear-mean: CAGR 13.41%, MDD 32.21%, Sharpe 0.968
- Tests H₁: does 4-way break 71-cap?

### H3.2 — 4-way A2-tilted (CAGR-preserving)
**`h3_meta_4way_30a2_20g1_25g2_25f1`**
- 30% A2 + 20% G1 IEF + 25% G2 IEF + 25% F1 stack
- Linear-mean: CAGR 13.79%, MDD 33.05%, Sharpe 0.952
- Tests H₁ with mild A2 tilt (preserves CAGR floor)

### H3.3 — Alt 3-way: G1 IEF replaces G2 IEF
**`h3_meta_3way_33a2_33g1_34f1`**
- 33% A2 + 33% G1 IEF + 34% F1 stack (mirrors iter-019 winning weights)
- Linear-mean: CAGR 13.13%, MDD 31.66%, Sharpe 0.968
- Tests H₂: does Sharpe-anchored G1 IEF (best in hunt) Pareto-dominate iter-019?

### H3.4 — Alt 3-way A2-heavy with G1 IEF
**`h3_meta_3way_50a2_25g1_25f1`**
- 50% A2 + 25% G1 IEF + 25% F1 stack
- Linear-mean: CAGR 14.24%, MDD 36.21%, Sharpe 0.929
- Tests H₂ with CAGR-preserving tilt; analog of iter-019 50/25/25 structure

### H3.5 — All-gated 3-way (no F1 stack)
**`h3_meta_3way_33a2_33g1_34g2`**
- 33% A2 + 33% G1 IEF + 34% G2 IEF (drops F1 stack always-on)
- Linear-mean: CAGR 13.90%, MDD 34.01%, Sharpe 0.951
- Tests H₃: does dual-gate + LETF substitution work without F1 stack?

### H3.6 — 4-way moderate A2-tilt
**`h3_meta_4way_35a2_15g1_25g2_25f1`**
- 35% A2 + 15% G1 IEF + 25% G2 IEF + 25% F1 stack
- Linear-mean: CAGR 14.04%, MDD 33.51%, Sharpe 0.940
- Tests H₁ with stronger A2-tilt + smaller G1 IEF dose

---

## Pre-committed KILL conditions

(numbered after iter-019's KILL #65 — new KILLs start at #66)

### KILL #66 (4-way ≤ 71 → meta-axis ceiling consolidates at 71, diminishing returns)
**Trigger**: max iter-020 4-way config score ≤ 71 AND no alt-3-way config exceeds 71.
**Implication**: meta-axis ceiling effectively at 71; adding 4th constituent does
not break 3-way 33/33/34 ceiling. Iter-021+ should explore weight-axis optimization
within 3-way structure or pivot off meta-axis.

### KILL #67 (best iter-020 score ≥ 75 → STRONG tier reachable)
**Trigger**: ANY iter-020 config with score ≥ 75 AND winner_conditions_met=True.
**Implication**: tier STRONG empirically reached; meta-axis trajectory continues
upward. Hunt status REOPENED stronger; iter-021+ may target ≥80 via further
weight optimization.

### KILL #68 (alt 3-way with G1 IEF Pareto-dominates iter-019 with G2 IEF)
**Trigger**: `h3_meta_3way_33a2_33g1_34f1` (H3.3) score > 71 AND mean Sharpe > 1.025.
**Implication**: G1 IEF (best Sharpe 1.080 + best MDD 18.57% but FAILS CAGR alone)
is the better Sharpe-anchored constituent for meta-blends; iter-019's G2 IEF
choice is suboptimal at meta-axis. Reframes the architectural recommendation.

### KILL #69 (drop F1 stack → CAGR fails OR score drops below 70)
**Trigger**: `h3_meta_3way_33a2_33g1_34g2` (H3.5) fails CAGR bar OR scores < 70.
**Implication**: F1 stack always-on is essential for meta-blend score; dual-gate
substitution insufficient for Pareto-improvement at meta-axis. Confirms iter-019's
mechanism analysis (always-on diversifier provides structural CAGR floor +
decorrelation gain ABOVE pure gate-axis decorrelation).

### KILL #70 (4-way Sharpe ≥ 1.05 — Pareto-improves on 3-way)
**Trigger**: max 4-way Sharpe ≥ 1.05.
**Implication**: adding G1 IEF (best Sharpe 1.080) as 4th constituent lifts Sharpe
above iter-019's 1.025 — even if score doesn't break 71, Sharpe-axis Pareto
frontier expands. Strengthens rubric-revision review case.

---

## Expected outcomes

**Pessimistic (no breakthrough)**: 4-way scores 67-71, all 3-way alt configs
score 64-71, no STRONG tier reached. KILL #66 fires; meta-axis ceiling at 71.

**Realistic (incremental improvement)**: 4-way scores 70-73, alt 3-way with G1 IEF
scores 70-72, weight optimization yields 1-2pt lift. KILL #67 may NOT fire;
meta-axis ceiling 72-73. Score lift modest but trajectory continues.

**Optimistic (breakthrough)**: best 4-way scores 75-78 via super-linear
decorrelation gain at 4-way structure (4 decorrelated streams > 3 streams).
KILL #67 fires; tier STRONG reached; iter-021+ targets 80+.

**Most likely outcome based on iter-019 mechanism analysis**: 4-way scores 69-72
(close to 3-way 71 with diminishing returns); alt 3-way with G1 IEF scores 70-72
(close to iter-019 71 with Sharpe lift but CAGR drag); all-gated 3-way (no F1)
scores 65-69 (CAGR may fail or score drops, KILL #69 fires).

---

## INCOMPLETE flags

- **Synth caveats inherited from prior iters**: SPYSIM/QQQSIM/TQQQSIM/QLDSIM/UPROSIM/
  TMFSIM/IEFSIM/KMLMSIM/TLTSIM/UGLSIM/NTSXSIM/GDESIM all DIRECT in testfolio cache;
  no new synth needed. Synth fidelity caveats from `studies/long_term_portfolio/synths.py`
  apply as in iter-019.
- **lh_56y rolling = 0 windows**: rolling_metrics computes only on spy_real overlap;
  pass-rates from spy_real only (n=18/13/8/3 windows for 5/10/15/20y respectively).
  Same as iter-019.
- **Cumulative n_trials = 68**: DSR worst-p threshold tightens. Worst case bound
  `q_value ≈ 0.05/68 = 7.4e-04`. Should comfortably pass with iter-019's worst
  p = 1.55e-04 baseline given similar architectural family.
- **Meta-ensemble combinatorial dimensions**: which 4 of 62 prior configs × what
  weights NOT counted in DSR n_trials. Honest n_trials likely larger; DSR margin
  remains conservative-loose. Same caveat as iter 018/019.
- **G3 walk-forward MDD bar at 25%**: STILL FAILS by ~3-7pp on both datasets in
  all prior iters at this leverage level (1.4-2.5× effective). 4-way with G1 IEF
  (no-decay 1.41× stack) at 25% weight may marginally improve wf_mdd toward 25%
  threshold but unlikely to fully clear.
- **PBO N=6 stability**: maintained per iter-019 KILL #64 resolution.

---

## Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple alpha
  streams — 4-way meta-ensemble axis depth probe; Markowitz mean-variance
  optimization at strategy-level with 4 constituents.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking generalized to
  4-way strategy-level: blending two regime-gated LETFs (A2 + G2) + one regime-
  gated stack (G1 IEF) + one always-on multi-asset (F1 stack) tests if 4
  decorrelated streams Pareto-improve over 3 streams.
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate at
  meta-ensemble: gates on QQQ vs SPY signals + dual SPY-gated decorrelation
  (G1 IEF + G2 IEF) tests gate-correlation hierarchy.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM) — present in all
  4 constituents (A2 30% ON, G1 IEF 15% ON, G2 IEF 15% ON, F1 stack 15%).
- Bridgewater All-Weather (Dalio 1996) — F1 stack ON-state composition repeated
  in G1 IEF ON, G2 IEF echoes via TMF/IEF/UGL/KMLM.
- `[advances_fin_ml, p.31-34]` factor framework — meta-ensemble axis 4-way
  structure adds to architectural taxonomy.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 68; worst p ≤ 0.05
  threshold tightens; iter-019 baseline p = 1.55e-04 << 0.05 expected to hold.
- `[advances_fin_ml, p.208-211]` PBO grid-level — N=6 stability MAINTAINED per
  iter-019 KILL #64 resolution.
- `[advances_fin_ml, p.196-202]` bootstrap CI — G6 expected to pass on both
  datasets with comfortable margin per iter-019 baseline.

---

## Pre-iter mandate compliance

This iter remains under mandate §1 MAINTENANCE MODE (2026-04-23). Score 71 from
iter-019 < 90 WINNER threshold; no winner candidate trips mandate §7 override
request. F1+SPLIT incumbent fallback retains deploy-ready status. iter-020
exploration is **RESEARCH ONLY**.
