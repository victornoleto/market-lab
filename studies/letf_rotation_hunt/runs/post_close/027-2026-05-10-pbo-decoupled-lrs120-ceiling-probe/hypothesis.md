# Iter 027 — pbo-decoupled-lrs120-ceiling-probe — HYPOTHESIS

**Slug:** `027-2026-05-10-pbo-decoupled-lrs120-ceiling-probe`
**Phase:** 4 — iter 017 focused validation/refinement
**n_configs:** 6 (mechanism-mix-diverse, 3 NON-rearm + 3 rearm-scaffolded — identical structural layout to iter 024/025/026 except slot 6's LRS factor)

**Trial accounting:**
- `cumulative_n_trials_global` BEFORE this iter: **582** (post-iter-026)
- `cumulative_n_trials_global` AFTER this iter: **588**
- `cumulative_n_trials_loop` BEFORE: 156 → AFTER: 162

---

## Hypothesis

**PRIMARY (LRS magnitude structural test — sweet-spot ceiling probe).** Iter
024 cleared G1 PBO 0.4365 by decoupling the LRS axis from rearm scaffolding
(3 NON-rearm + 3 rearm balanced split). Iter 025 directly confirmed *"PBO
clustering is structural, NOT magnitude-related"* by raising slot 6's LRS
factor 1.05 → 1.10 within iter 024's exact mechanism-mix layout, observing
**bit-identical** G1 PBO 0.4365. Iter 026 advanced LRS1.10 → 1.15 within
the same layout and observed PBO 0.4127 (a small favorable structural
shift, no NEW PBO mode). This iter advances the magnitude axis one more
step (slot 6 LRS factor **1.15 → 1.20**) within the SAME mechanism-mix
layout. This is the **first LRS factor expected to potentially exceed the
Husson-Trifoni ann-vol-<40% sweet spot** on QLD on-leg (effective ~2.40×
of QQQ may push annual vol above 40% boundary in modern-era subperiods).
PRIMARY hypothesis: if iter 025/026's structural-not-magnitude diagnosis
holds, G1 PBO should remain < 0.50 with LRS1.20×.

**SECONDARY (Phase 4 magnitude monotonicity — beyond-sweet-spot probe).**
Linear extrapolation from the iter 024 → 025 → 026 trio (LRS lift per
+0.05 step on rearm base: -0.0108, -0.0100, -0.0094 Sortino; +0.99, +0.96,
+0.93pp CAGR — slowly decaying step) predicts slot 6 LRS1.20× delivers
Sortino ~**1.379** and CAGR ~**36.25%**. **Crucial test:** does the Sortino
stay above the Phase 4 improved floor (1.35), and does the LRS lift remain
linear (within ±0.025 monotonicity threshold), or has the strategy entered
the compounding-vol-drag asymmetry regime (`[leverage_for_the_long_run,
p.5-6]` ann-vol-≥40% danger zone) where Sortino degrades non-linearly? If
both hold, slot 6 LRS1.20× should preserve `phase4_anchor_improved=True`
AND deliver a strict Pareto improvement on CAGR + end_eq vs iter 017 over
iter 026 slot 6 LRS1.15.

**TERTIARY (5-point magnitude scan completion + Husson-Trifoni ceiling
identification).** Iter 026 closed the 4-point scan (1.00, 1.05, 1.10,
1.15) within the sweet spot; iter 027 LRS1.20× extends this to a 5-point
scan that crosses the predicted boundary. Two scientifically valuable
outcomes:
- If Sortino dip stays linear and PBO holds: sweet-spot boundary lies
  ABOVE LRS1.20 in this universe — formal claimable LRS ceiling extends.
- If Sortino dip becomes non-linear (KILL_LOOP #14) OR Sortino collapses
  below 1.35 floor (KILL_LOOP #13) OR PBO blows out (KILL_LOOP #8):
  sweet-spot ceiling is identified between LRS1.15 (formally claimable) and
  LRS1.20× — closes the LRS magnitude headroom for Phase 4 anchor
  improvement on this primitive.

## Primary citation

`[leverage_for_the_long_run, ch.4-5, p.40-60]` — Husson-Trifoni LRS
leverage scaling. LRS1.20× sits at the **boundary** of the ann-vol-<40%
sweet spot `[leverage_for_the_long_run, p.5-6]` on 2× QLD on-leg
(effective ~2.40× of QQQ — modern-era QLD ann vol ~28% × 1.20 = 33-34%
typical, but QQQ drawdown windows can push this above 40%).

## Secondary citations

- `[advances_fin_ml, p.208-211]` CSCV PBO mechanism-mix diversity —
  motivates preserving iter 024/025/026's PBO-clearing layout.
- `[leverage_for_the_long_run, p.13, ch.3]` canonical RISK_ON LRS rule
  (above-MA → leveraged S&P 500 daily; unconditional within RISK_ON).
- `[leverage_for_the_long_run, p.5-6]` ann vol < 40% sweet spot for daily
  leverage; danger zone above 40% (compounding-vol-drag asymmetry kicks in).
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials (n_global=588
  after this iter).
- `[advances_fin_ml, p.196-202]` bootstrap CI / DSR.
- `[risk_parity, ch.5, p.10]` Carlson stacking (LRS overlay composition).

## Strategy eligibility checklist

1. **Citable book/paper:** YES — `[leverage_for_the_long_run, ch.4-5, p.40-60]`
   primary, in `books/summaries/leverage_for_the_long_run.md`.
2. **Distinct from `runs/original/`:** YES — closed study (T1-T5) never tested
   LRS overlay × rearm × Vote-K=2 × ratevol composition.
3. **Distinct from `runs/post_close/`:** YES — iter 023 tested LRS1.15× but
   only on rearm-WINDOW (broken mechanism-mix → PBO 0.6548 blowup);
   iter 024 tested LRS1.05× unconditional on K4 + rearm bases; iter 025
   tested LRS1.10× unconditional on rearm base; iter 026 tested LRS1.15×
   unconditional on rearm base. NO prior iter tested LRS1.20× with the
   iter 024/025/026 mechanism-mix-diverse PBO-clearing layout.
4. **Data feasibility:** YES — same testfolio universe as iter 024/025/026
   (QLDSIM, TQQQSIM, ZROZSIM, IEFSIM, CASHX, SPYSIM); no new data needed.

## Configs tested (6 — single-axis variation from iter 024/025/026)

The layout is **identical to iter 024, 025, and 026** except slot 6's LRS
factor moves 1.15 → 1.20. Other slots are exact replicas (calibration
anchors). This isolates the LRS magnitude as the only varying dimension
across the 4-iter chain (024/025/026/027).

| # | name | upgrade gate | rearm | LRS mode | LRS factor | role |
|---|---|---|---|---|--:|---|
| 1 | `..._unclrs_baseline_qld_zroz` | none | NO | off | 1.00 | 18th-gen calibration anchor |
| 2 | `..._unclrs_single_K4lv25_g25_rvp70_cashx` | K4_AND_QLDlv25 | NO | off | 1.00 | 15th-gen calibration anchor |
| 3 | `..._unclrs_single_K4lv25_g25_rvp70_cashx_unclrs105` | K4_AND_QLDlv25 | NO | uncond_on | 1.05 | 4th-gen iter 024 K4 anchor |
| 4 | `..._unclrs_single_K4lv25_g25_rvp70_cashx_T40D60` | K4_AND_lv25 OR rearm | YES (iter017) | off | 1.00 | 10th-gen iter 017 OR-anchor |
| 5 | `..._unclrs_single_rearmonly_g25_rvp70_cashx_T40D60` | rearm only | YES (INDEPENDENT) | off | 1.00 | 7th-gen iter 022 INDEP IMPL |
| 6 | 🥇 🆕 `..._unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_unclrs120` | rearm only | YES (INDEPENDENT) | uncond_on | **1.20** | **NEW** rearm × LRS1.20× sweet-spot ceiling probe |

3 NON-rearm (slots 1, 2, 3) + 3 rearm-scaffolded (slots 4, 5, 6); LRS axis
on 2 of 6 slots distributed across 2 distinct base mechanism families
(K4 slot 3, rearm slot 6) — **4 effective CSCV groups identical to iter
024/025/026**.

## Datasets

`lh_56y` (1970-01 → 2026-04), `modern_1990` (1990-01 → 2026-04),
`spy_real` (2003-01 → 2026-04), `ndx_real` (2010-02 → 2026-04). Same as
iter 024/025/026 for direct comparability and bit-exact replica checks.

## Pre-registered KILL_LOOP conditions (anti-p-hacking)

- **KILL_LOOP #1 (success_tag — POSITIVE):** any config has
  `beats_winner=True`. Informational; does NOT block subsequent KILLs.
- **KILL_LOOP #2 (decisive_fail):** best Sortino_lh56y < 1.20. Trip ⇒
  iter unsuccessful regardless of any other tag.
- **KILL_LOOP #3 (replica baseline drift):** baseline (slot 1) Sortino_lh56y
  drift from iter 011-026 1.3240 > 0.005. Trip ⇒ universe data drift; abort
  comparisons.
- **KILL_LOOP #4 (replica single_K4lv25_g25 drift):** slot 2 Sortino_lh56y
  drift from iter 014-026 1.3951 > 0.005.
- **KILL_LOOP #5 (replica T40D60_OR_iter017 drift):** slot 4 Sortino_lh56y
  drift from iter 017-026 1.4030 > 0.005.
- **KILL_LOOP #6 (replica rearmonly_T40D60 drift):** slot 5 Sortino_lh56y
  drift from iter 021/022/023/024/025/026 1.4176 > 0.005.
- **KILL_LOOP #7 (replica K4_unclrs105 drift):** slot 3 Sortino_lh56y drift
  from iter 024/025/026 1.3842 > 0.005.
- **KILL_LOOP #8 (PBO_blowup):** G1 PBO ≥ 0.55. Trip ⇒ NEW PBO mode like
  iter 023's 0.6548 — magnitude-induced clustering would emerge here,
  FALSIFYING iter 025/026's structural-not-magnitude diagnosis at the
  beyond-sweet-spot boundary.
- **KILL_LOOP #9 (PBO_held — POSITIVE TAG, PRIMARY):** G1 PBO < 0.50
  (Phase 3 hard gate). Confirms iter 025/026's structural-not-magnitude
  diagnosis extends to LRS1.20×.
- **KILL_LOOP #10 (lrs120_phase4_anchor_improved — POSITIVE TAG, STRONG):**
  slot 6 (rearm + uncond LRS1.20) achieves `phase4_anchor_improved=True`
  (CAGR > 32.66% OR end_eq vs iter017 > 1.0; AND Sortino ≥ 1.35; AND
  PBO < 0.50; AND DSR_global < 0.05).
- **KILL_LOOP #11 (lrs120_strict_superset — POSITIVE TAG, STRONGEST):**
  slot 6 achieves `strict_superset=True` (beats_winner AND
  phase3_performance_candidate).
- **KILL_LOOP #12 (lrs120_magnitude_pareto_improvement — POSITIVE TAG):**
  slot 6 LRS1.20 strictly Pareto-dominates iter 026 slot 6 LRS1.15 on BOTH
  cagr_lh56y AND end_equity_ratio_vs_iter017.
- **KILL_LOOP #13 (lrs120_sortino_collapse):** slot 6 Sortino_lh56y < 1.35
  (Phase 4 improved floor — LRS1.20 too aggressive, breaks linearity).
  Trip ⇒ Husson-Trifoni sweet-spot ceiling identified between LRS1.15
  (claimable) and LRS1.20× (excessive).
- **KILL_LOOP #14 (lrs120_monotonicity_break):** |LRS1.15 → LRS1.20 Sortino
  delta - LRS1.10 → LRS1.15 Sortino delta| > 0.025. Trip ⇒ Sortino response
  to LRS magnitude is NON-linear at higher factors (compounding-vol-drag
  asymmetry kicks in earlier than predicted, consistent with the
  ann-vol-≥40% danger-zone hypothesis).

## Expected outcomes

**Primary path (iter 025/026 structural-not-magnitude diagnosis HOLDS,
sweet-spot ceiling NOT yet reached):**

| metric | iter 024 slot 6 LRS1.05 | iter 025 slot 6 LRS1.10 | iter 026 slot 6 LRS1.15 | iter 027 slot 6 LRS1.20 (predicted) |
|---|---:|---:|---:|---:|
| Sortino_lh56y | 1.4068 | 1.3968 | 1.3874 | ~**1.379** (linear extrap) |
| CAGR_lh56y | 33.43% | 34.39% | 35.32% | ~**36.25%** (linear extrap) |
| end_eq vs iter 017 | 1.264× | 1.687× | 2.227× | ~**2.85×** (linear extrap) |
| G1 PBO | 0.4365 | 0.4365 | 0.4127 | ~**0.41-0.44** (structural-not-magnitude) |
| Sortino vs 1.35 floor | +0.057 | +0.047 | +0.037 | ~+**0.029** (close but above) |

**Sortino edge vs winner (T3d-K2 1.3246):** ~+0.0544 (linear extrap)
**CAGR edge vs winner:** ~+5.17pp (linear extrap)
**Terminal ratio vs T3d-K2:** ~4.6× (LOOP MAX prediction)
**phase4_anchor_improved:** TRUE if Sortino ≥ 1.35 AND CAGR > 32.66%
AND PBO < 0.50 AND DSR_global < 0.05

**Comparison plan vs winner (T3d-K2):**
- For `beats_winner=True`: Sortino > 1.3746 AND winner_conditions_met AND
  pct_above_lh56y ≥ 0.95.
  Predicted: Sortino ~1.379 > 1.3746 → likely TRUE (margin shrinking).

**Phase 3 performance plan:**
- For `phase3_performance_candidate=True`: cagr_lh56y > 0.3108 AND
  end_equity_ratio_vs_winner > 1.05 AND sortino_lh56y ≥ 1.20 AND
  PBO < 0.5 AND DSR global p < 0.05.
  Predicted: ALL conditions met for slot 6.

**Phase 4 anchor plan:**
- For `phase4_anchor_improved=True`: cagr_lh56y > 0.3266 OR
  end_equity_ratio_vs_iter017 > 1.00, with Sortino ≥ 1.35, PBO < 0.5,
  DSR global p < 0.05.
  Predicted: TRUE if Sortino linear extrapolation holds and
  ann-vol-≥40% danger zone is not yet active.

**Pareto improvement vs iter 026 slot 6 LRS1.15:**
- For TRUE: cagr_lh56y > 35.32% AND end_eq_ratio_vs_iter017 > 2.227×.
  Predicted: TRUE if magnitude monotonicity holds.

**Alternative path A (KILL_LOOP #13 fires — Sortino collapses below 1.35):**
- Slot 6 Sortino < 1.35 ⇒ Husson-Trifoni sweet-spot ceiling identified at
  LRS1.15 → 1.20 transition; strategy enters compounding-vol-drag regime.
  Phase 4 improvement headroom on LRS magnitude axis is exhausted at LRS1.15.
  Negative result still scientifically valuable: maps the LRS ceiling and
  closes the LRS axis exploration on this primitive.

**Alternative path B (KILL_LOOP #14 fires — monotonicity breaks):**
- |LRS1.15→1.20 Sortino delta - LRS1.10→1.15 Sortino delta| > 0.025 ⇒
  non-linear Sortino response to LRS magnitude has emerged. The sweet-spot
  boundary is between LRS1.15 (linear) and LRS1.20× (non-linear). Even if
  Sortino stays above 1.35, the linear extrapolation framework ceases to
  apply beyond LRS1.15; future improvements need a different approach
  (regime-targeted LRS, basket extension, non-rearm pivot).

**Alternative path C (KILL_LOOP #8 fires — PBO blowup):**
- G1 PBO ≥ 0.55 ⇒ iter 025/026's structural-not-magnitude diagnosis FALSIFIED
  at LRS1.20×; magnitude DOES eventually induce CSCV rank clustering at
  high enough LRS factor. Reframes the LRS overlay's PBO behavior as
  magnitude-bounded structural rather than purely structural.

## INCOMPLETE flags / caveats

- **Synth caveat:** all results use testfolio synthetic series (QLDSIM,
  TQQQSIM, ZROZSIM, IEFSIM, CASHX, SPYSIM). Real ETF parity is checked at
  loop_001-010 level; this iter uses identical synth chain as iter 024/025/026.
- **DSR n_global = 588** — includes prior 426 closed-study trials + 156
  pre-iter-027 loop trials + 6 iter-027 configs.
- **Beyond-sweet-spot probe disclaimer:** LRS1.20× is the **first** factor
  expected to potentially exceed the Husson-Trifoni ann-vol-<40% sweet spot
  on QLD on-leg in modern-era subperiods. A negative outcome here (KILL_LOOP
  #13 or #14) is not a strategy failure but an empirical identification of
  the ceiling. The PBO-decoupled framework remains valid for LRS ≤ 1.15
  regardless.
- **Calibration drift policy:** any KILL_LOOP #3-#7 firing (drift > 0.005)
  ⇒ universe-level data integrity issue; this iter's claims are conditional
  on bit-exact replicas of all 5 prior calibration anchors.
- **No new helper modules introduced.** Reuses iter 024's
  `unconditional_lrs_overlay.py` bit-exactly (only the lrs_factor argument
  changes 1.15 → 1.20). Per LOOP_PROTOCOL §"Scope limits", no closed-study
  or cross-iter-shared module is modified.
- **Capital reallocation NOT triggered by this iter regardless of outcome.**
  Mandate §1 maintains 100% Plan C; any deploy escalation requires user
  mandate §7 override.

## Non-goals

- **Not** a broad hunt; Phase 4 focused on iter 017 anchor refinement.
- **Not** a parameter sweep on T_crash/D_arm (frozen at iter 017's 40/60).
- **Not** a basket extension or cross-base test (deferred to iter 026+ ideas
  list (d) — basket3-invvol60 + LRS).
- **Not** a non-rearm pivot (deferred to iter 026 ideas list (e)).
- **Not** a regime-targeted LRS test (deferred to iter 026 ideas list (c)).

## Methodology

1. Build the same 6-config grid as iter 024/025/026 with slot 6 LRS factor 1.20.
2. Run the standard 7-gate suite (G1 PBO, G2 DSR local + global, G3 walk-
   forward, G4 OOS 70/30, G5 fwd post-2020, G6 bootstrap CI, G7 cross-lib
   CAGR delta) on each config.
3. Compute the Phase 4 anchor diagnostics + magnitude monotonicity diagnostic
   vs iter 026 slot 6 LRS1.15.
4. Assess all 14 KILL_LOOP conditions.
5. Sort by (phase4_anchor_improved, strict_superset, phase3_performance_
   candidate, sortino, cagr, score) — same key as iter 024/025/026.
6. Generate plots/01-07 and tables (per_config_metrics.csv, gates_pass_fail.csv).
7. Validate verdict.json against `loop_verdict_schema.json`.
