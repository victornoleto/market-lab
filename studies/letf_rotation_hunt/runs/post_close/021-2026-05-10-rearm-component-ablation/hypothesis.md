# Iter 021 — rearm-component-ablation

**Phase:** 4 — iter 017 focused validation/refinement
**Slug:** `rearm-component-ablation`
**n_configs:** 6 (mechanism-mix-diverse — 5 distinct upgrade-axis topologies)
**cumulative_n_trials_global before/after:** 546 → 552
**cumulative_n_trials_loop before/after:** 120 → 126

## Hypothesis

Iter 017's NEW non-replica strict_superset
`single_K4lv25_g25_rvp70_cashx_T40D60` (Sortino 1.4030, CAGR 32.66%,
end_eq 1.620×) **OR-combines** two upgrade-axis primitives:

- **K4_AND_QLDlv25 base** (state-domain): trend conviction (4-of-4 vote
  long) AND QLD 21d realised-vol percentile < 25th — fires ~7.1% of
  valid days in lh_56y.
- **T40D60 rearm overlay** (time-domain): MA-flip-on after ≥ 40-day OFF
  stretch, harvest TQQQ for 60 days — fires ~9.7% of valid days, 16
  qualified flips over 56 years.

Iter 020 (MDD-depth filter) demonstrated the rearm window survives
**refinement** but a depth-filter trims alpha (-0.006 Sortino vs
T40D60). What iters 017-020 have NOT yet established: which of the two
primitives **drives** the lift. The Husson-Trifoni MA-streak thesis
`[leverage_for_the_long_run, p.6-7, ch.3]` predicts that the time-domain
rearm overlay alone — operating on the empirical streak-window onset —
should produce a majority of the alpha; the K4_AND_lv25 base would then
be a state-domain refinement that adds incremental crisis-vol screening
during ranging markets.

This iter performs a clean **mechanism ablation** of the two upgrade-
axis primitives, tested under the iter 014 graded-blend frame:

- Slot 5 ⇒ rearm-window ALONE drives upgrade (K4_AND_lv25 base **removed**).
- Slot 6 ⇒ K4_AND_lv25 AND rearm intersection (BOTH must fire concurrently).

The pre-registered prediction tree:

| Slot 5 (rearm-only) outcome | Inference |
|---|---|
| Sortino 5 ≈ Sortino 4 (T40D60) | Rearm IS the dominant alpha; K4 base is incidental ⇒ **anchor partially invalidated** (overspecified). |
| Sortino 5 ≈ Sortino 2 (K4 only) | K4 base IS the dominant alpha; rearm only mirrors what K4 already captures ⇒ **anchor partially invalidated** (rearm overlay is decorative). |
| Sortino 5 ∈ (Sortino 2, Sortino 4) | Mechanisms are complementary ⇒ **anchor mechanism validated** — both axes contribute, OR-union is the right composition. |
| Sortino 5 ≈ Sortino 1 (baseline) | Rearm alone has no edge → ALL alpha attributable to K4 base ⇒ **rearm overlay rejected**. |

| Slot 6 (K4 AND rearm) outcome | Inference |
|---|---|
| Sortino 6 > Sortino 4 | Intersection more selective wins; OR is too permissive. |
| Sortino 6 ≈ Sortino 1 | Intersection fires too rarely; sets are nearly disjoint. |
| Sortino 6 ∈ (Sortino 1, Sortino 4) | Mild contribution; OR composition remains optimal. |

The expected outcome (mechanism prior) is **Sortino 5 ∈ (Sortino 2,
Sortino 4)** with Slot 6 falling near baseline (the rearm window
during MA-flip onset rarely coincides with the trend-conviction K4
state). This would constitute **`phase4_anchor_validated=true`**.

## Primary citation

`[leverage_for_the_long_run, p.6-7, ch.3]` — Husson-Trifoni:
"Above the moving average, autocorrelation is positive (streaks); below
the moving average, autocorrelation is negative (seesawing)." The MA
flip-on is the empirical streak-window onset — testable independently
of additional state-domain gating (K4 vote, vol percentiles).

## Secondary citations

- `[leverage_for_the_long_run, p.4, ch.2]` Husson-Trifoni — "high
  volatility and seesawing action are the enemies of leverage; low
  volatility and streaks in performance are its friends." Frames the
  full upgrade rationale.
- `[stocks_on_the_move, p.98]` Clenow trend-strength filter — slot 2/3
  K4 base intuition.
- `[volatility_trading, p.58-60]` Sinclair vol cone — QLD-vol percentile
  component of K4_AND_lv25.
- `[risk_parity, p.80-81, ch.4]` Qian RORO graded master-gate.
- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking.
- `[systematic_trading, p.212, ch.13]` Carver re-arm hysteresis —
  conceptual basis for the time-domain memory of the rearm window.
- `[advances_fin_ml, p.208-211]` PBO via CSCV — mechanism diversity
  with 5 distinct upgrade-axis topologies (avoiding iter 018-style
  parametric clustering).
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials (n_global=552).
- `[advances_fin_ml, p.196-202]` Bootstrap CI / DSR.

## Configs tested (6 — mechanism-mix-diverse)

| # | Name (config) | ON-leg | Upgrade-axis | Rearm | Topology |
|--:|---|---|---|---|---|
| 1 | `..._ablate_baseline_qld_zroz` | QLD | none | — | single/none/none |
| 2 | `..._ablate_single_K4lv25_g25_rvp70_cashx` ← iter 014 strict_superset replica | QLD/TQQQ | K4_AND_QLDlv25 | — | single/K4_AND_QLDlv25 |
| 3 | `..._ablate_basket3invvol_K4lv25_g25_rvp70_cashx` ← iter 014 triple-stack replica | basket3-invvol60 | K4_AND_QLDlv25 | — | basket3/K4_AND_QLDlv25 |
| 4 | `..._ablate_single_K4lv25_g25_rvp70_cashx_T40D60` ← iter 017 NEW strict_superset replica | QLD/TQQQ | K4_AND_QLDlv25 OR rearm | T40D60 | single/K4_AND_QLDlv25_OR_rearm |
| 5 | `..._ablate_single_rearmonly_g25_rvp70_cashx_T40D60` ← **PRIMARY (NEW)** rearm-only ablation | QLD/TQQQ | rearm only | T40D60 | single/rearm_only |
| 6 | `..._ablate_single_K4lv25_AND_rearm_g25_rvp70_cashx_T40D60` ← **STRICTER (NEW)** intersection ablation | QLD/TQQQ | K4_AND_QLDlv25 AND rearm | T40D60 | single/K4_AND_QLDlv25_AND_rearm |

Datasets (per iter 020 convention, comparable to study iters 014/017):
`lh_56y` (1970-01 → 2026-04), `modern_1990` (1990-01 → 2026-04),
`spy_real` (2003-01 → 2026-04), `ndx_real` (2010-02 → 2026-04).

The five distinct upgrade-axis topologies (slots 1, 2, 3, 4, 5; slot 6
shares the rearm dimension with slot 4 but uses AND instead of OR — a
genuinely different set composition, not a parametric variant) preserve
the mechanism diversity that iter 020 used to clear PBO 0.4325 < 0.50.

## Pre-registered KILL_LOOP conditions

- **KILL_LOOP #1 (success_tag) — POSITIVE TAG.** FIRES if any config
  achieves `beats_winner=True`. Slots 2 + 4 (replicas) are pre-known
  to fire; slots 5 + 6 are the open question.
- **KILL_LOOP #2 (decisive_fail).** FIRES if best Sortino_lh56y < 1.20
  (Phase 3 floor). Not expected.
- **KILL_LOOP #3 (replica_sanity_baseline).** FIRES if baseline Sortino
  drifts from iter 011-020 baseline 1.3240 by > 0.005. **12th-generation
  cross-iter reproducibility test.**
- **KILL_LOOP #4 (replica_sanity_single_K4lv25_g25).** FIRES if
  drift > 0.005 from iter 014-020 anchor 1.3951.
- **KILL_LOOP #5 (replica_sanity_basket3invvol_K4lv25_g25).** FIRES if
  drift > 0.005 from iter 014-020 anchor 1.4689.
- **KILL_LOOP #6 (replica_sanity_T40D60).** FIRES if drift > 0.005 from
  iter 017-020 NEW strict_superset 1.4030. **4th-generation
  reproducibility test for iter 017's first novel strict_superset.**
- **KILL_LOOP #7 (PBO_blowup).** FIRES if G1 PBO ≥ 0.55. The 5-distinct-
  topology recipe should hold; iter 018 demonstrated PBO blowup occurs
  with parametric clustering, NOT with structural ablation across
  different gate compositions.
- **KILL_LOOP #8 (PBO_held) — POSITIVE TAG.** FIRES if G1 PBO < 0.50.
- **KILL_LOOP #9 (ablate_phase3_perf_candidate) — CORE WEAK
  HYPOTHESIS.** FIRES if slot 5 OR slot 6 achieves
  `phase3_performance_candidate=True`. Tests whether either ablation
  variant retains Phase 3 performance candidacy independent of OR
  composition.
- **KILL_LOOP #10 (ablate_strict_superset) — STRONGEST WEAK HYPOTHESIS.**
  FIRES if slot 5 OR slot 6 achieves `strict_superset=True` (a NEW
  loop_strict_superset_iter contribution).
- **KILL_LOOP #11 (rearm_only_validates_anchor) — STRONG MECHANISM
  HYPOTHESIS.** FIRES if slot 5 Sortino_lh56y > slot 1 (baseline)
  + 0.04 AND slot 5 CAGR > slot 1 CAGR + 0.5pp. Indicates the rearm
  overlay contributes alpha INDEPENDENTLY of the K4_AND_lv25 base —
  necessary condition for `phase4_anchor_validated=true`.
- **KILL_LOOP #12 (ablate_strict_superset_with_crisis_2plus).** FIRES
  if slot 5 OR slot 6 achieves strict_superset=True AND crisis_count
  ≥ 2/4. Loop's first crisis-≥2/4 strict_superset still NOT achieved.

## Expected outcomes

**Sortino_lh56y range:**

- Slot 1 baseline: ~1.3240 (calibration anchor)
- Slot 2 K4 only: ~1.3951 (calibration anchor)
- Slot 3 basket3: ~1.4689 (calibration anchor)
- Slot 4 T40D60 anchor: ~1.4030 (calibration anchor — iter 017-020 replica)
- **Slot 5 rearm only: 1.32 – 1.42 (open) — most likely 1.36 – 1.39
  if mechanisms are complementary; ~1.40 if rearm dominates; ~1.32 if
  K4 dominates.**
- **Slot 6 K4 AND rearm: 1.30 – 1.36 (open) — most likely 1.32 – 1.33
  if intersection rarely fires; ~1.35+ if a small but high-signal
  intersection exists.**

**CAGR_lh56y expected:**

- Slot 1: 31.08%
- Slot 2: 31.47% (+0.39pp vs winner)
- Slot 3: 22.65% (-8.43pp vs winner — basket3 CAGR penalty)
- Slot 4: 32.66% (+1.58pp vs winner)
- **Slot 5: 31.5 – 32.5% (open)**
- **Slot 6: 31.0 – 31.6% (open) — limited by intersection rarity**

**Terminal end_equity_ratio_vs_baseline:**

- Slot 4: 1.620×
- **Slot 5: 1.10 – 1.55× (open)**
- **Slot 6: 1.00 – 1.10× (open)**

**Rolling 1y/3y/5y/10y win-rates vs baseline:** non-baseline configs
expected to clear ≥ 50%/50%/50%/30% baseline (slot 4 anchor:
50.5%/55.7%/55.3%/38.0% per iter 017 audit).

**`phase3_performance_candidate` vs slot 5+6:** ablation result
expected to retain Phase 3 candidacy (CAGR > 31.08%, end_eq > 1.05×)
for slot 5 if rearm contributes alpha. Slot 6 likely fails Phase 3
floor due to intersection rarity.

**`strict_superset` vs slot 5+6:** if slot 5 Sortino > 1.3746
threshold AND clears Phase 3 floors AND winner_conditions_met, slot 5
becomes a NEW novel non-replica strict_superset (the loop's 3rd novel
after iter 017's T40D60 and iter 020's MDD15). Slot 6 unlikely to
achieve strict_superset due to expected intersection rarity dropping
Sortino toward baseline.

**Comparison plan:**

- **Beats-winner (per best_config):** requires
  `sortino_lh56y > 1.3746 AND winner_conditions_met=True AND
  pct_time_above_benchmark_lh56y >= 0.95`. Slots 2 + 4 expected to fire
  (calibration anchors); slots 5 + 6 are the open test.
- **Phase 3 performance candidate:** requires `cagr_lh56y > 0.3108
  AND end_equity_ratio_vs_baseline > 1.05 AND sortino_lh56y >= 1.20
  AND PBO < 0.5 AND DSR_global p < 0.05`. Slot 4 expected to fire
  (anchor); slots 5 + 6 are the open test.
- **Phase 4 anchor improved:** requires `(cagr_lh56y > 0.3266 OR
  end_equity_ratio_vs_iter017 > 1.00) AND sortino_lh56y >= 1.35
  AND PBO < 0.5 AND DSR_global p < 0.05`. **Not the primary objective
  of this iter — ablation does not pursue improvement.** Falls true
  only if a slot accidentally improves on T40D60 (highly unlikely
  given the ablation framing).
- **Phase 4 anchor validated:** new boolean. TRUE if slot 5 (rearm-
  only) Sortino_lh56y > slot 1 (baseline) + 0.04 AND slot 5 CAGR_lh56y
  > slot 1 CAGR + 0.5pp AND PBO < 0.5 AND DSR_global p < 0.05.
  Indicates rearm contributes ALPHA INDEPENDENTLY of K4 base — the
  mechanism is real, not an artifact of K4 + parametric tuning.

## INCOMPLETE flags

- **Synth caveat:** lh_56y uses SPYSIM/QLDSIM/TQQQSIM/UPROSIM/UGLSIM
  via testfolio cache (Husson-Trifoni LRS methodology, FFR-aware).
  Pre-1985 TQQQ synth is the standard `synthetic_letf` reconstruction
  via QLD/borrow-cost; documented `[advances_fin_ml, p.208-211]` PBO
  remains the dominant control regardless of synth assumptions because
  CSCV operates on rank-stability, not absolute returns.
- **Tax/fees not applied** at this stage (gross metrics primary,
  consistent with iter 020). Lei 14.754 swing tax 15% diagnostic
  deferred — turnover ~5/y for slot 4 anchor is the baseline.
- **G7 cross-library CAGR delta** uses `numpy + pandas` only; no
  cross-implementation parity beyond bit-exact replica anchors. The
  KILL_LOOP #3-#6 replicas serve as parity controls for slots 1-4.
- **Slot 5 NaN handling:** `combine_OR(zero_series, rearm_gate)` ≡
  `rearm_gate` (no NaN propagation, since zero_series has no NaN).
  Slot 5's gate is therefore strictly the rearm output.
- **Slot 6 NaN handling:** `combine_AND(K4_AND_QLDlv25, rearm_gate)`
  propagates NaN from K4_AND_QLDlv25 (which has NaN during its 1260-day
  vol-percentile warmup). During warmup, slot 6 upgrade=NaN → treated
  as 0 by `build_single_asset_on_leg` → on-leg = QLD. This matches
  slot 2's behavior during warmup (no upgrade activity).
- **Mechanism-diversity claim:** PBO blowup risk is structurally
  different from iter 018. Iter 018 had 5/6 configs sharing the K4_AND_
  lv25_OR_rearm topology with parametric variation (rearm coefficient
  sweep). This iter 021's slot 5 has a topologically distinct gate
  (NO K4 base; rearm alone), and slot 6 has a topologically distinct
  intersection (AND not OR). The CSCV ranking matrix sees 5 different
  active-day patterns across slots 1, 2, 3, 4, 5 (slot 6 may be
  near-zero activity → similar to slot 1 baseline by ranking, but
  still distinct in expectation).
- **Phase 4 success-tag interpretation:** an ablation iter is
  expected to PRODUCE NEGATIVE OR DIAGNOSTIC RESULTS, not improve the
  anchor. The success criteria are reversed: confirming that mechanisms
  are complementary (slot 5 contributes alpha but does not dominate)
  validates the iter 017 anchor; failing to find a complementary
  contribution rejects it.
