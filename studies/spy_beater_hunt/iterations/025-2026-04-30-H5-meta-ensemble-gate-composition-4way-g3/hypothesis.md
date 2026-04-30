# Iter 025 — H5 META-ENSEMBLE GATE-COMPOSITION 4-WAY (A2 + G2 IEF + F1 stack + G3 4040)

**Date**: 2026-04-30
**Cumulative n_trials**: 91 (before iter 025) → **96** after this iter (5 configs added).
**Slug**: `H5-meta-ensemble-gate-composition-4way-g3`
**Architectural axis**: meta-ensemble (9th iter on this axis after 018/019/020/021 + cross-product hybrid integration test)
**Closest-to-winner UNCHANGED entering iter**: iter 019 H2 `h2_meta_3way_33a2_33g2_34f1` at score **71**.

---

## Hypothesis

**Primary claim (H5)**: KILL #94's NEW PRINCIPLE — gate composition has TWO orthogonal effects on portfolio mechanics: (1) bear-avoidance switching (canonical Gayed); (2) **effective-leverage reduction via time-averaged exposure** — STACKS with meta-axis decorrelation (cross-strategy gate-source diversity from iter 019's H2 apex).

If true, replacing F1 stack always-on (CAGR-floor diversifier, score 61) or G2 IEF (LETF F1 with SPY gate, score 64) with G3 4040 (gated HFEA classical UPRO+TMF+KMLM at 300% notional with 2008/2022 bear-avoidance, score 66) within iter 019's 33/33/34 framework should lift the meta-ensemble score above 71.

**Mechanism predicted**:
- G3 4040 has higher **gross CAGR** (15.79%) than F1 stack (~13.5%) and matches G2 IEF (14.02%) → CAGR-axis lift expected on substitutions.
- G3 4040 has higher **MDD** (44.71%) than F1 stack (26.82%) and G2 IEF (33.72%) → MDD-axis penalty expected.
- The blend's decorrelation effect from triple gate-source diversity (QQQ × SPY-LETF × SPY-leveraged-duration) might yield Pareto-improvement vs iter 019.
- Per `[advances_fin_ml, ch.16, p.241-256]`, alpha-stream blends benefit when constituents have decorrelated drawdown timing — G3's 2008 path-dependent timing may not perfectly correlate with G2's LETF-decay path.

**Why this is genuinely new (not retread)**:
- iter 020 H3 tested 4-way with G1 IEF (best Sharpe 1.080, best MDD 18.57% but FAILS CAGR alone at 10.34%) — adding **CAGR-floor-failing** constituent → score 67 (−4 vs iter 019's 71). Lesson: 4-way dilution costs CAGR axis.
- iter 025 H5 tests 4-way with G3 4040 (CAGR 15.79% PASSES, MDD 44.71% PASSES, score 66) — adding **CAGR-floor-passing high-MDD** constituent → predicts MDD-axis penalty but CAGR-axis preservation.
- Test of NEW PRINCIPLE: does G3's gate-composition mechanism (effective-leverage reduction) replace F1 stack's natural diversification (no-leverage stack)?

**Citations**:
- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple alpha streams (4-way meta-ensemble at strategy-level)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking generalized to strategy-level
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate (A2 QQQ + G2 SPY + G3 SPY-with-HFEA-sleeve constituents — triple-gate-source meta-blend test)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in A2, G2, G3, F1 — universal MF presence)
- HFEA Bogleheads 2019 — leveraged barbell rationale (G3 sleeve)
- Bridgewater All-Weather (Dalio 1996) — F1 stack ON-state composition
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 96 (Bonferroni threshold ~5.21e-04)
- `[advances_fin_ml, p.208-211]` PBO grid-level N=5 stability
- `[advances_fin_ml, p.31-34]` factor framework — meta-ensemble axis 9th iter exploration

---

## Constituents (no infrastructure changes — all reuse 'blend' spec type)

### Constituent A (A2): iter 006 `a6_tqqq_split_kmlm30_tlt10`
- LRS QQQ-200d-SMA gate × 3× LETF (TQQQ + QLD) + KMLM crisis-alpha + TLT
- ON: 30% TQQQSIM + 30% QLDSIM + 30% KMLMSIM + 10% TLTSIM
- OFF: 100% IEFSIM
- Solo CAGR ~17.33% / MDD ~36% / Sharpe ~0.95 / score 67 (LRS-mono axis ceiling)

### Constituent B (G2 IEF): iter 017 `g2_f1_letf_2x_sma200_ief`
- LRS SPY-200d-SMA gate × 2.25× LETF F1 All-Weather (UPRO/TMF/IEF/UGL/KMLM)
- ON: 30% UPROSIM + 25% TMFSIM + 15% IEFSIM + 15% UGLSIM + 15% KMLMSIM
- OFF: 100% IEFSIM
- Solo CAGR ~14.02% / MDD ~33.72% / Sharpe ~0.97 / score 64

### Constituent C (F1 stack): iter 015 `f1_aw_stack_15x`
- Static always-on multi-asset stack 1.41× (no gate)
- 35% NTSXSIM + 30% GDESIM + 20% TLTSIM + 15% KMLMSIM
- Solo CAGR ~13.5% / MDD ~26.82% / Sharpe ~1.018 / score 61

### Constituent D (G3 4040 — NEW for iter 025): iter 024 `g3_gated_hfea_4040`
- LRS SPY-200d-SMA gate × HFEA leveraged-barbell 300% notional + KMLM crisis-alpha
- ON: 40% UPROSIM + 40% TMFSIM + 20% KMLMSIM
- OFF: 100% IEFSIM
- Solo CAGR 15.79% / MDD 44.71% / Sharpe 0.895 / score 66 (cross-product hybrid family ceiling)

**Triple gate-source diversity**: A2 (QQQ-200d) × G2 (SPY-200d on LETF F1) × G3 (SPY-200d on HFEA classical) — same SPY signal source for G2/G3 but **different sleeve composition** (2.25× LETF F1 with UGL gold vs 300% HFEA leverage-barbell with leveraged duration TMF).

---

## Configs (5)

### H5.1 — equal-weight 4-way (CORE TEST adding G3 to iter-019's 3-way)
**Naming**: `h5_meta_4way_25a2_25g2_25f1_25g3`
**Spec**: 25% A2 + 25% G2 IEF + 25% F1 stack + 25% G3 4040
**Linear-mean estimate**: CAGR 15.16% / MDD 35.31% / Sharpe 0.958
**Tests**: does adding CAGR-passing G3 lift over G1 IEF 4-way iter 020 (score 67)?

### H5.2 — 3-way substitute F1 with G3 (gate-composition replaces always-on diversifier)
**Naming**: `h5_meta_3way_33a2_33g2_34g3`
**Spec**: 33% A2 + 33% G2 IEF + 34% G3 4040
**Linear-mean estimate**: CAGR 15.72% / MDD 38.21% / Sharpe 0.938
**Tests**: KILL #97 — does G3 outperform F1 stack as 3rd constituent of iter 019's 33/33/34 framework?

### H5.3 — 3-way substitute G2 with G3 (replace LETF gate with leveraged-duration gate)
**Naming**: `h5_meta_3way_33a2_33g3_34f1`
**Spec**: 33% A2 + 33% G3 4040 + 34% F1 stack
**Linear-mean estimate**: CAGR 15.52% / MDD 35.75% / Sharpe 0.955
**Tests**: KILL #98 — is SPY-200d gate on HFEA-classical sleeve a substitute for SPY-200d gate on LETF F1 sleeve within meta-ensemble?

### H5.4 — asymmetric 4-way preserving A2 tilt + minor G3 dose
**Naming**: `h5_meta_4way_30a2_25g2_25f1_20g3`
**Spec**: 30% A2 + 25% G2 IEF + 25% F1 stack + 20% G3 4040
**Linear-mean estimate**: CAGR 15.25% / MDD 34.88% / Sharpe 0.961
**Tests**: lower G3 dose (20%) → less MDD-axis dilution, preserves CAGR via A2 tilt.

### H5.5 — 3-way A2+G3+F1 with F1 dominance (replace G2 with G3, boost F1 to compensate G3's MDD)
**Naming**: `h5_meta_3way_30a2_30g3_40f1`
**Spec**: 30% A2 + 30% G3 4040 + 40% F1 stack
**Linear-mean estimate**: CAGR 15.34% / MDD 34.94% / Sharpe 0.961
**Tests**: F1 dominance compensates G3's MDD penalty; tests whether G3 substitution preserves Pareto frontier when F1 carries diversification load.

---

## Pre-committed KILL conditions

KILL #1-#94 from prior iters retained (KILL #6 not fired since iter 005; KILL #94 NEW from iter 024).

### NEW for iter 025

- **KILL #95** (axis-ceiling): max H5 score ≤ 71 → meta-axis ceiling NOT broken via gate-composition stacking; **9th meta-axis confirmation point** since iter 018; meta-axis ceiling at 71 holds DEFINITIVE across cross-product-hybrid integration test.
- **KILL #96** (4-way dilution generalization): h5_meta_4way_25a2_25g2_25f1_25g3 ≤ iter-020 H3 4-way score 67 → 4-way meta-axis structure caps below 3-way regardless of 4th constituent's CAGR profile (G3 4040 vs G1 IEF). Validates iter-020 lesson generalizes beyond the specific G1 IEF identity.
- **KILL #97** (G3 outperforms F1 stack as always-on within meta-ensemble): h5_meta_3way_33a2_33g2_34g3 score ≥ 71 → G3 4040 (gated HFEA, MDD 44.71%) Pareto-dominates F1 stack (always-on, MDD 26.82%) within iter 019's framework via gate-composition mechanism. **Would BREAK closest-to-winner gap if fires HARD** (≥ 75 score = STRONG tier).
- **KILL #98** (SPY-LETF gate not substitutable for SPY-HFEA gate within meta): h5_meta_3way_33a2_33g3_34f1 score ≤ iter-019's 71 by ≥ 2pts → SPY-200d gate on LETF F1 sleeve (G2 IEF) is NOT replaceable by SPY-200d gate on HFEA classical sleeve (G3 4040) within meta-ensemble — gate-source diversity (signal × sleeve) matters more than just signal-side decorrelation.
- **KILL #99** (architectural-ceiling-invalidation safeguard): max H5 score ≥ 75 → STRONG tier reached → 8-axis architectural ceiling claim INVALIDATED → reopen hunt with hypothesis that gate-composition + meta-axis is a NEW 9th axis exceeding prior taxonomy. Requires escalation to user per mandate §1 + §7.
- **KILL #100** (Sharpe-axis Pareto improvement test, NOT firing strictly): max H5 mean Sharpe ≥ 1.05 → Sharpe-axis Pareto frontier extends beyond iter 020's 1.058 (current best mean Sharpe among CAGR-passers). New empirical finding (no score consequence per rubric saturation, but documents Sharpe-frontier).

---

## Expected outcomes

**Most likely (per iter 020 lesson + iter 024 G3 MDD-axis penalty)**:
- All 5 configs PASS bars 3/3 (5/5 sweep — fifth 100% bar-pass sweep ever).
- Score range: 64-72.
- KILL #95 FIRED — score ≤ 71.
- KILL #96 FIRED OR NOT — depends on H5.1 4-way score vs 67.
- KILL #97 NOT FIRED — H5.2 substitution score < 71 (MDD axis penalty propagates).
- KILL #98 FIRED — H5.3 substitution score < 71 by ≥ 2pts.
- KILL #99 NOT FIRED — score < 75.

**If KILL #97 FIRES HARD (H5.2 ≥ 71)**:
- This would be the **first** sub-iter to break the 71 ceiling within meta-axis.
- Mechanism: G3's higher CAGR (15.79%) lifts the blend's CAGR axis; G3's MDD penalty (44.71%) is partially absorbed by A2 + G2 IEF in 33/33/34 weighting.
- Triggers 9-axis architectural taxonomy update + new closest-to-winner.

**If KILL #99 FIRES (max ≥ 75)**:
- Architectural ceiling claim INVALIDATED.
- Required: pause hunt, escalate to user per mandate §1, write detailed post-mortem on why iter 020 H3 (4-way at 25/25/25/25) scored 67 but iter 025 H5 (4-way at 25/25/25/25 substituting G3 for G1) scored ≥ 75 — what mechanism caused +8pts lift?

---

## INCOMPLETE flags

- **Constituent G3 4040 spec**: includes KMLMSIM 20% within ON state — KILL #94 NEW PRINCIPLE finding uses 'kmlm15' variant (50/35/15) but iter 025 uses '4040' variant (40/40/20). Both PASS bars 3/3; '4040' was iter 024's selected_config (highest score). Choice matches iter 024's selected best.
- **PBO grid stability**: N=5 configs may exhibit similar instability as iter-018's N=3 → check vs iter-020 N=6 baseline. If PBO lh > 0.5 strict → flag.
- **Tax classification (drag estimate)**: iter 024 G3 'lrs' = annual_realize → drag 1.87-2.12pp. Meta-blend with G3 component will have **mixed tax classification** — current `tax_layer.py` treats blend as conservative (max-drag of constituents) → estimated drag 1.9-2.1pp similar to iter 019 H2 (1.91pp).
- **Cross-strategy correlation**: triple-gate-source decorrelation (QQQ × SPY-LETF × SPY-HFEA) is asymmetric (G2 + G3 share SPY signal but differ sleeve composition). Empirical decorrelation may be lower than iter-019's QQQ × SPY × always-on triplet.

---

## Reproducibility checks

- Run with `datasets_to_test=("lh_56y", "spy_real")` (default since iter 015).
- DSR cumulative_n_trials = 96 (Bonferroni threshold 5.21e-04). Worst-case G3 4040 had p=1.90e-03 in iter 024 (passes single-comparison <0.05; passes Bonferroni <5.49e-04 only marginally). Iter 025 blends should have tighter (better) DSR p-values via decorrelation Sharpe lift.
- 771 tests baseline preserved (no new infra).
- Reuses 'blend' spec type from iter 018 + 'lrs' spec type from iter 024 + 'static' spec type from iter 015.

---

## Strategic context

This iter 025 directly tests the iter 024 final report's **Option C** ("test gate-composition meta-ensemble") as the natural next step after iter 024's KILL #94 NEW PRINCIPLE finding.

**If KILL #95 FIRES** (most likely, score ≤ 71): hunt EFFECTIVELY-CLOSED reaffirmed. 9-axis architectural taxonomy validated. F1+SPLIT confirmed deploy fallback. iter 026+ would pivot to Option B (CAPE-timing, low-credibility) or Option D (rubric-revision request).

**If KILL #95 NOT FIRED** (score > 71): meta-axis ceiling REVISED upward. Closest-to-winner UPDATED. Hunt reopens with NEW best architectural axis (gate-composition meta-ensemble), strengthening the path-to-WINNER (≥ 90 score) at +4pts above prior ceiling.

**Mandate compliance**: §1 100% Plano C UNCHANGED — research only. Mandate §7 review case at 9th iter (8 prior + iter 025 if rubric-suboptimal selected) regardless of score.
