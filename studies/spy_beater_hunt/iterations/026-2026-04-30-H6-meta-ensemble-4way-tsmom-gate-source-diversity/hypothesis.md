# Iter 026 — H6 META-ENSEMBLE 4-WAY with E1 (TSMOM-gated TQQQ) as ALTERNATIVE 4TH CONSTITUENT — GATE-SOURCE-DIVERSITY TEST

**Date**: 2026-04-30
**Cumulative n_trials**: 96 (before iter 026) → **100** after this iter (4 configs added).
**Slug**: `H6-meta-ensemble-4way-tsmom-gate-source-diversity`
**Architectural axis**: meta-ensemble (10th iter on this axis after 018/019/020/021/025; iter 025 NEW PRINCIPLE map extension)
**Closest-to-winner UNCHANGED entering iter**: iter 019 H2 `h2_meta_3way_33a2_33g2_34f1` at score **71**.

---

## Hypothesis

**Primary claim (H6)**: iter 025 NEW PRINCIPLE established that the 4-way meta-axis 4th constituent's solo CAGR ≥ bar (11.21%) is the primary criterion for score lift (G1 IEF CAGR-fail 10.34% → 4-way score 67; G3 4040 CAGR-pass 15.79% → 4-way score 70). H6 tests this principle's **second-order extension** by introducing E1 (iter 014 `e1_tqqq_split_kmlm30_tlt10_tsmom6m`) as the 4th constituent — same CAGR-pass profile (E1 17.20% > G3 15.79%) but **DIFFERENT gate-source** (TSMOM 6m momentum vs SMA 200d).

**Secondary hypothesis (gate-source diversity)**: iter 019's H2 apex uses 3 gate-sources (QQQ-200d-SMA × SPY-200d-SMA × always-on-static). iter 025's H5.1 adds a 4th constituent G3 4040 sharing SPY-200d-SMA gate-source with G2 IEF (only sleeve composition differs). H6's E1 4th constituent uses TSMOM 6m on QQQ — **truly NEW gate-source**, expanding the meta-blend to 4 distinct gate-sources (QQQ-200d-SMA × SPY-200d-SMA × TSMOM-6m-QQQ × always-on-static).

**Mechanism predicted**:
- E1's higher solo CAGR (17.20% > G3's 15.79%) → CAGR-axis lift +0.5pp on 25/25/25/25 blend mean.
- E1's higher solo MDD (47.48% > G3's 44.71%) → MDD-axis penalty similar to G3 (anchor [0.7, 0.15] saturation at 40-45% range).
- E1's lower solo Sharpe (0.75 < G3's 0.895) → Sharpe-axis penalty.
- TSMOM 6m gate-source diversity from SMA-only gates → potential super-linear decorrelation lift IF gate-source diversity is a 2nd-order Pareto-improvement axis NOT yet rubric-saturated.
- Per `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple alpha streams, decorrelation across gate-sources should yield non-linear Sharpe lift; iter 019's H2 already exhibited super-linear MDD relief (−7.50pp vs linear 36.0%) at 3 gate-sources.

**Why this is genuinely new (not retread)**:
- iter 025 H5 used G3 (SPY-200d-SMA gate, same source as G2) → 4-way 25/25/25/25 score 70.
- iter 020 H3 used G1 (SPY-200d-SMA gate, same source as G2) → 4-way 25/25/25/25 score 67.
- iter 026 H6 uses E1 (TSMOM-6m-QQQ gate, DIFFERENT source from all 3 prior 3-way constituents) → first test of gate-source-diversity-as-4th-axis within meta-ensemble.

**Citations**:
- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple alpha streams (4-way meta-ensemble at strategy-level with gate-source-diversity test)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking generalized to 4 distinct gate-sources
- Moskowitz, Ooi, Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 — TSMOM 6m gate rationale (E1 constituent)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate (A2 QQQ-track + G2 SPY-track LETF F1 constituents — SMA gate-source)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in A2, G2, E1 ON-state; F1 stack always-on)
- Bridgewater All-Weather (Dalio 1996) — F1 stack ON-state composition (always-on multi-asset stack)
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 100 (Bonferroni threshold ~5.00e-04)
- `[advances_fin_ml, p.208-211]` PBO grid-level N=4 stability

---

## Constituents (no infrastructure changes — all reuse 'blend' + 'lrs' + 'static' spec types)

### Constituent A (A2): iter 006 `a6_tqqq_split_kmlm30_tlt10`
- LRS QQQ-200d-SMA gate × 3× LETF (TQQQ + QLD) + KMLM crisis-alpha + TLT
- ON: 30% TQQQSIM + 30% QLDSIM + 30% KMLMSIM + 10% TLTSIM
- OFF: 100% IEFSIM
- Solo CAGR ~17.33% / MDD ~36% / Sharpe ~0.95 / score 67 (LRS-mono axis ceiling)
- **Gate-source**: QQQ-200d-SMA

### Constituent B (G2 IEF): iter 017 `g2_f1_letf_2x_sma200_ief`
- LRS SPY-200d-SMA gate × 2.25× LETF F1 All-Weather (UPRO/TMF/IEF/UGL/KMLM)
- ON: 30% UPROSIM + 25% TMFSIM + 15% IEFSIM + 15% UGLSIM + 15% KMLMSIM
- OFF: 100% IEFSIM
- Solo CAGR ~14.02% / MDD ~33.72% / Sharpe ~0.97 / score 64
- **Gate-source**: SPY-200d-SMA

### Constituent C (F1 stack): iter 015 `f1_aw_stack_15x`
- Static always-on multi-asset stack 1.41× (NO gate)
- 35% NTSXSIM + 30% GDESIM + 20% TLTSIM + 15% KMLMSIM
- Solo CAGR ~13.5% / MDD ~26.82% / Sharpe ~1.018 / score 61
- **Gate-source**: always-on (no gate)

### Constituent D (E1 — NEW for iter 026): iter 014 `e1_tqqq_split_kmlm30_tlt10_tsmom6m`
- LRS TSMOM 6m (~126d) gate × 3× LETF (TQQQ + QLD) + KMLM crisis-alpha + TLT
- ON: 30% TQQQSIM + 30% QLDSIM + 30% KMLMSIM + 10% TLTSIM
- OFF: 100% IEFSIM
- Filter: `momentum`, lookback_days: 126
- Solo CAGR 17.20% / MDD 47.48% / Sharpe 0.75 / score 65 (cross-product hybrid family member)
- **Gate-source**: TSMOM-6m-QQQ — **DIFFERENT from all 3 prior constituents**

**Quadruple gate-source diversity**: A2 (QQQ-200d-SMA) × G2 (SPY-200d-SMA) × F1 (always-on) × **E1 (TSMOM-6m-QQQ — NEW)**. ON-sleeve composition is identical between A2 and E1 (same TQQQ split + KMLM30 + TLT10), isolating the gate-source-diversity effect.

---

## Configs (4)

### H6.1 — equal-weight 4-way (CORE TEST: G3 → E1 substitution at iter 025's 4-way)
**Naming**: `h6_meta_4way_25a2_25g2_25f1_25e1`
**Spec**: 25% A2 + 25% G2 IEF + 25% F1 stack + 25% E1
**Linear-mean estimate**: CAGR ~15.51% / MDD ~36.06% / Sharpe ~0.945
**Tests**: KILL #102 — does E1 (higher solo CAGR + DIFFERENT gate-source) lift over iter 025 H5.1 score 70 (G3 4040 same SPY-SMA source as G2)?

### H6.2 — 3-way substitute F1 stack with E1 (TSMOM-axis replaces always-on)
**Naming**: `h6_meta_3way_33a2_33g2_34e1`
**Spec**: 33% A2 + 33% G2 IEF + 34% E1
**Linear-mean estimate**: CAGR ~16.18% / MDD ~39.06% / Sharpe ~0.890
**Tests**: KILL #104 — does E1 outperform F1 stack as 3rd constituent of iter 019's 33/33/34 framework? Parallels iter 025 KILL #97 (G3 vs F1) but swaps gate-source diversity for sleeve diversity.

### H6.3 — 3-way substitute G2 IEF with E1 (replace SPY-LETF gate with TSMOM-TQQQ gate)
**Naming**: `h6_meta_3way_33a2_33e1_34f1`
**Spec**: 33% A2 + 33% E1 + 34% F1 stack
**Linear-mean estimate**: CAGR ~15.94% / MDD ~36.74% / Sharpe ~0.918
**Tests**: KILL #105 — is TSMOM-6m-QQQ gate substitutable for SPY-200d-LETF gate within meta-ensemble? Parallels iter 025 KILL #98 (G3 vs G2) but with truly NEW gate-source.

### H6.4 — asymmetric 4-way preserving A2 tilt + minor E1 dose
**Naming**: `h6_meta_4way_30a2_25g2_25f1_20e1`
**Spec**: 30% A2 + 25% G2 IEF + 25% F1 stack + 20% E1
**Linear-mean estimate**: CAGR ~15.59% / MDD ~35.59% / Sharpe ~0.953
**Tests**: lower E1 dose (20%) → less MDD-axis dilution from E1's 47.48% solo MDD, preserves CAGR via A2 tilt. Parallel to iter 025 H5.4.

---

## Pre-committed KILL conditions

KILL #1-#100 from prior iters retained. KILL #95 (meta-axis ceiling at 71 DEFINITIVE) is the REGENT KILL for this iter.

### NEW for iter 026

- **KILL #101** (axis-ceiling reaffirm — 10th meta-axis confirmation): max H6 score ≤ 71 → meta-axis ceiling at 71 DEFINITIVE confirmed across cross-product-hybrid integration AND TSMOM-axis integration; **10th meta-axis confirmation point** since iter 018 (after 018/019/020/021/025 prior). Strengthens KILL #95 to 10-point evidence base.
- **KILL #102** (E1 vs G3 as 4th constituent — gate-source-diversity HYPOTHESIS): H6.1 (4-way 25/25/25/25 with E1) score ≥ iter 025 H5.1 score 70 → E1's higher solo CAGR (17.20% > 15.79%) AND/OR TSMOM gate-source diversity translates to higher 4-way score within rubric. Tests if iter 025 NEW PRINCIPLE (4th-constituent CAGR ≥ bar) compounds with gate-source-diversity bonus.
- **KILL #103** (gate-source-diversity HARD test): H6.1 score ≥ 72 → TSMOM gate-source ADDS DECORRELATION beyond SMA-only gates → 4-way constituent selection principle EXTENDED to include gate-source-diversity criterion (would update iter 025 NEW PRINCIPLE: "4th constituent's solo CAGR ≥ bar AND distinct gate-source from existing constituents").
- **KILL #104** (E1 substitution for F1 always-on at 3-way): H6.2 (substitute F1 with E1) score ≥ iter 019 H2 71 → E1 outperforms F1 stack as 3rd constituent within iter 019 framework. Parallels iter 025 KILL #97 (G3 vs F1, NOT FIRED). **Would BREAK closest-to-winner gap if fires HARD** (≥ 75 score = STRONG tier).
- **KILL #105** (TSMOM gate substitutable for SPY-LETF gate within meta): H6.3 score ≤ iter-019's 71 by ≥ 2pts → TSMOM-6m-QQQ gate is NOT replaceable for SPY-200d-LETF gate within meta-ensemble. If H6.3 score ∈ [69, 73], gate-source signals are approximately substitutable.

---

## Expected outcomes

**Most likely (per iter 025 NEW PRINCIPLE + iter 014 E1 absolute baseline)**:
- All 4 configs PASS bars 3/3 (4/4 sweep — sixth 100% bar-pass sweep ever).
- Score range: 65-71.
- KILL #101 FIRED — score ≤ 71.
- KILL #102 FIRES OR NOT — depends on H6.1 4-way score vs 70.
- KILL #103 NOT FIRED — score < 72 (rubric-saturated for Sharpe + MDD axes).
- KILL #104 NOT FIRED — H6.2 score < 71 (F1 stack's natural-diversification advantage maintained as 3rd constituent).

**If KILL #103 FIRES (H6.1 ≥ 72)**:
- Gate-source-diversity is a NEW 2nd-order Pareto axis — first iter to demonstrate principle.
- 4-way ceiling REVISED upward via gate-source-diversity bonus (was 70 with G1/G3 SMA-only; could be ≥ 72 with TSMOM addition).
- Triggers updated 4-way constituent selection rule: requires distinct gate-source from existing constituents.

**If KILL #104 FIRES HARD (H6.2 ≥ 75)**:
- This would be the **first** sub-iter to break the 71 ceiling within meta-axis.
- Mechanism: E1's higher solo CAGR (17.20%) lifts blend's CAGR axis; E1's MDD penalty (47.48%) absorbed by A2 + G2 IEF in 33/33/34 weighting; TSMOM gate-source decorrelation adds Sharpe axis lift that breaks rubric saturation.
- Triggers 9-axis architectural taxonomy update + new closest-to-winner.

---

## INCOMPLETE flags

- **E1 constituent gate-source vs A2 constituent gate-source**: A2 uses QQQ-200d-SMA; E1 uses TSMOM-6m-QQQ. Both signals derived from QQQ — partial signal-source overlap (fundamental QQQ price action) but distinct timing-mechanism (slow SMA vs faster momentum). Decorrelation may be less than fully-orthogonal gate-sources.
- **DSR Bonferroni at n_trials=100**: threshold 5.00e-04. Worst per-config DSR p in iter 014 was 6.71e-04 for E1 (fails Bonferroni 4.27e-04 at then-n_trials=58). Blends should have tighter (lower) DSR p via decorrelation Sharpe lift, but E1's standalone DSR was the worst in spy_beater hunt; meta-blend may inherit some tightness.
- **Tax classification (drag estimate)**: meta-blend with E1 component (LRS spec type) → annual_realize. Estimated drag 1.9-2.1pp similar to iter 025 H5.1 (1.91pp).
- **PBO grid stability**: N=4 configs may exhibit reduced stability vs iter-020 N=6 baseline. If PBO lh_56y > 0.5 strict → flag (analogous to iter 025 spy_real PBO 0.786 strict-fail).

---

## Reproducibility checks

- Run with `datasets_to_test=("lh_56y", "spy_real")` (default since iter 015).
- DSR cumulative_n_trials = 100 (Bonferroni threshold 5.00e-04).
- 771 tests baseline preserved (no new infra — 'lrs' + 'momentum' filter already supported in run_iter via iter 014).
- Reuses 'blend' spec type from iter 018-025 + 'lrs' (sma + momentum filters) spec type from iter 014/024 + 'static' spec type from iter 015.

---

## Strategic context

This iter 026 directly tests iter 025 NEW PRINCIPLE generalization to gate-source-diversity dimension. iter 025 mapped 4th-constituent CAGR-axis (G1 IEF FAIL → G3 4040 PASS); iter 026 maps gate-source-axis (G3 same-as-G2 SPY-SMA → E1 NEW TSMOM-6m-QQQ).

**If KILL #101 FIRES** (most likely, score ≤ 71): hunt EFFECTIVELY-CLOSED reaffirmed at 10-point meta-axis evidence. iter 027+ would pivot to Option B (CAPE-timing, low-credibility) or Option D (rubric-revision request). Recommendation: declare hunt closed at iter 026.

**If KILL #103 FIRES** (gate-source-diversity bonus, H6.1 ≥ 72): meta-axis ceiling REVISED upward via gate-source-diversity finding. Closest-to-winner UPDATED. Hunt extends to map gate-source-diversity 5-way (add B2 HFEA static or C1 vol-target as 5th constituent for further gate-source-axis exploration).

**If KILL #104 FIRES HARD** (H6.2 ≥ 75 STRONG tier): architectural ceiling claim INVALIDATED. Required: pause hunt, escalate to user per mandate §1, write detailed post-mortem on why E1 (TSMOM gate, lower Sharpe) substitution for F1 stack (always-on, higher Sharpe) yielded score lift — what mechanism caused +4pts over iter 019?

**Mandate compliance**: §1 100% Plano C UNCHANGED — research only. Mandate §7 review case at 10th iter (9 prior + iter 026 if rubric-suboptimal selected) regardless of score.
