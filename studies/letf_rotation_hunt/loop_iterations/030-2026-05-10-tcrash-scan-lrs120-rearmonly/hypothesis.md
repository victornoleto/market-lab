# Iter 030 — T_crash sensitivity scan at iter 027 slot 6 LRS1.20 unconditional ceiling

**Slug:** `tcrash-scan-lrs120-rearmonly`
**Phase:** 4 — iter 017 focused validation/refinement
**Date:** 2026-05-10 UTC

---

## Frontmatter

| field | value |
|---|---|
| n_configs | 6 |
| cumulative_n_trials_loop_before | 174 |
| cumulative_n_trials_loop_after | 180 |
| cumulative_n_trials_global_before | 600 |
| cumulative_n_trials_global_after | 606 |
| primary_citation | `[advances_fin_ml, p.208-211]` |
| secondary_citations | `[leverage_for_the_long_run, p.6-7, ch.3]`, `[stocks_on_the_move, p.98]`, `[advances_fin_ml, p.222-223]` |
| anchor_iter | `027-2026-05-10-pbo-decoupled-lrs120-ceiling-probe` (slot 6) |
| anchor_metrics | Sortino 1.3786, CAGR 36.22%, end_eq vs iter017 2.908×, PBO 0.3929 |

---

## Hypothesis

**PRIMARY (T_crash sensitivity at iter 027 LRS1.20 ceiling).** Iter 027 closed
the 5-point LRS magnitude scan (1.00, 1.05, 1.10, 1.15, 1.20×) and identified
slot 6 (rearm-only T40D60 + LRS1.20 unconditional) as the loop's strongest
formal Pareto frontier point on terminal compounding (CAGR 36.22%, end_eq vs
iter017 2.908×). Iter 028+029 closed the LRS regime-conditioning axis on both
calm and stress polarities — modern-era softness is structural to the rearm
primitive. **Open question (carryover from iter 029 next-iter idea (d)):** is
the iter 027 Pareto point a robust local optimum w.r.t. the crash-trigger
threshold T_crash, or is it a fragile event fit specific to T_crash=40?

This iter applies a 4-point T_crash sensitivity scan {35, 40, 45, 50} at the
iter 027 slot 6 base (rearm-only INDEP + LRS1.20 unconditional, D_arm=60
frozen). T_crash defines the minimum prior OFF-stretch length (in trading
days) required for an OFF→ON master-signal flip to qualify as a post-crash
re-arm event `[leverage_for_the_long_run, p.6-7, ch.3]`. Lower T_crash =
more inclusive (more events; shorter crashes count); higher T_crash = more
restrictive (only deep crashes count).

**KEY HYPOTHESIS (PRE-REGISTERED):** if the iter 027 Pareto point is robust,
T_crash sensitivity should be SMOOTH (monotonic-ish) and the central T40
should remain near the local optimum. If T_crash=40 is a fragile event fit,
either T35 or T50 will substantially exceed T40's metrics, falsifying the
T40 anchor.

**SECONDARY (Phase 4 anchor robustness diagnostic).** This is the FIRST
T_crash sensitivity probe at the LRS1.20 ceiling. Prior iters 017-029 all
fixed T_crash=40. The scan tests whether iter 017's choice was load-bearing
or accidental.

**TERTIARY (PBO mechanism diversity — anchor preservation).** Three calibration
anchors (slots 1-3) preserved bit-exact from iter 029. Slot 1 = baseline
(21st-gen target). Slot 2 = rearm-only T40D60 INDEP IMPL no LRS (10th-gen).
Slot 3 = rearm-only T40D60 + LRS1.20 unconditional = iter 027 slot 6
(2nd-gen). Slots 4-6 are NEW T_crash {35, 45, 50} variants with the same
LRS1.20 unconditional overlay.

---

## Citations

- **PRIMARY** `[advances_fin_ml, p.208-211]` — CSCV PBO mechanism-mix
  diversity. Anchor + 3 perturbation variants need to span sufficiently
  different return paths to avoid rank clustering. T_crash {35, 40, 45, 50}
  produces materially different rearm-event sets (different number of
  qualified flips per decade, different trigger dates), expected to inject
  enough mechanism diversity for PBO < 0.50.
- **SECONDARY** `[leverage_for_the_long_run, p.6-7, ch.3]` — Husson-Trifoni
  MA flip-on as empirical streak-window onset. T_crash defines the
  pre-flip OFF stretch threshold; sensitivity scan probes whether the
  streak-onset signal is robust to perturbations of the "how long below MA
  before flip" criterion.
- **SECONDARY** `[stocks_on_the_move, p.98]` — Clenow trend-strength /
  re-establishment after long OFF stretch. Provides theoretical grounding
  for varying T_crash: longer OFF stretches = stronger trend-reset signal,
  but fewer events.
- **SECONDARY** `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials
  (n_global=606 after iter 030).
- **SECONDARY** `[leverage_for_the_long_run, p.13, ch.3]` — canonical
  RISK_ON LRS rule preserved (LRS1.20× applied unconditionally on every ON
  day; iter 028+029 falsified regime-conditioning, so unconditional remains
  the strongest ceiling form).
- **SECONDARY** `[risk_parity, ch.5, p.10]` — Carlson stacking (LRS overlay
  composition).

---

## Configs tested (6)

| slot | name | upgrade_mode | rearm | T_crash | D_arm | LRS mode | LRS factor | role |
|---:|---|---|:---:|---:|---:|---|---:|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_baseline_qld_zroz` | none | F | 0 | 0 | off | 1.00 | calibration (21st-gen baseline) |
| 2 | `..._unclrs_single_rearmonly_g25_rvp70_cashx_T40D60` | rearmonly_indep | T | 40 | 60 | off | 1.00 | calibration (10th-gen iter 022 INDEP) |
| 3 | `..._unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_unclrs120` | rearmonly_indep | T | 40 | 60 | unclrs120 | 1.20 | calibration (2nd-gen iter 027 slot 6 Pareto anchor) |
| 4 | `..._unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120` | rearmonly_indep | T | 35 | 60 | unclrs120 | 1.20 | **NEW** — T_crash DOWN |
| 5 | `..._unclrs_single_rearmonly_g25_rvp70_cashx_T45D60_unclrs120` | rearmonly_indep | T | 45 | 60 | unclrs120 | 1.20 | **NEW** — T_crash UP |
| 6 | `..._unclrs_single_rearmonly_g25_rvp70_cashx_T50D60_unclrs120` | rearmonly_indep | T | 50 | 60 | unclrs120 | 1.20 | **NEW** — T_crash UP further |

D_arm=60 frozen for all rearm slots (matches iter 017 anchor).
LRS_factor=1.20 unconditional on every ON day for slots 3-6 (matches iter
027 slot 6 ceiling).
gamma=0.25, ratevol p70 cashx for all slots ≥ 2 (matches iter 022-029
INDEP IMPL framework).

---

## Datasets

| dataset | window | bottleneck |
|---|---|---|
| lh_56y | 1970-01..2026-04 | SPYSIM |
| modern_1990 | 1990-01..2026-04 | (subperiod-equivalent) |
| spy_real | 2003-01..2026-04 | Tiingo SPY |
| ndx_real | 2010-02..2026-04 | Tiingo QQQ |

Same as study + prior loop iters for comparability. Modern subperiod
diagnostic is computed from lh_56y returns (1990-2009 + 2010-2026 cuts).

---

## Pre-registered KILL_LOOP conditions

| # | name | rule | direction |
|---:|---|---|---|
| 1 | success_tag | any config has beats_winner=True | informational |
| 2 | decisive_fail | best Sortino_lh56y < 1.20 (Phase 3 floor) | informational |
| 3 | replica_baseline | slot 1 Sortino diverges from iter 011-029 baseline 1.3240 by > 0.005 | regression-fail |
| 4 | replica_rearmonly_T40D60 | slot 2 Sortino diverges from iter 021-029 INDEP IMPL 1.4176 by > 0.005 | regression-fail |
| 5 | replica_rearmonly_T40D60_LRS120 | slot 3 Sortino diverges from iter 027 slot 6 1.3786 by > 0.005 | regression-fail |
| 6 | PBO_blowup | G1 PBO ≥ 0.55 (NEW PBO mode like iter 023) | hard-fail |
| 7 | PBO_held | G1 PBO < 0.50 (Phase 3 hard gate) | positive_tag |
| 8 | tcrash_phase4_anchor_improved | ANY of slots 3-6 achieves phase4_anchor_improved=True | positive_tag |
| 9 | tcrash_modern_sortino_lift | ANY T_crash variant lifts modern subperiod Sortino ≥ 1.20 on at least one of {1990_2009, 2010_2026} | KEY HYPOTHESIS |
| 10 | tcrash_monotonicity | metrics (CAGR, Sortino, end_eq) vary smoothly/monotonically across T_crash {35, 40, 45, 50} (no decision-boundary cliffs) | positive_tag |
| 11 | tcrash_anchor_robustness | iter 027 T40 remains the local Pareto optimum (no T35/T45/T50 strictly dominates T40 on (CAGR, Sortino, end_eq)) | positive_tag |
| 12 | tcrash_anchor_falsified | EITHER T35 OR T45 OR T50 strictly Pareto-dominates T40 on (CAGR, Sortino, end_eq) AND beats_winner=True AND PBO < 0.50 | falsification |

---

## Expected outcomes

**Sortino_lh56y range (slots 3-6):** 1.30 – 1.45.
T35 expected slightly higher CAGR (more events) but possibly lower Sortino
(more event noise); T45/T50 expected lower CAGR (fewer events) but possibly
higher Sortino (events are deeper crashes → cleaner streak signature).

**CAGR_lh56y range (slots 3-6):** 30 – 40%.
- Slot 3 (T40 anchor): 36.22% (calibration target).
- Slot 4 (T35): expect 35-40% (more events, more LRS active days).
- Slot 5 (T45): expect 32-37% (fewer events, less LRS active during recoveries).
- Slot 6 (T50): expect 30-35% (only major crashes trigger; less compounding).

**Gap vs T3d-K2 CAGR 31.08%:** all 4 LRS-on slots expected positive (+1pp to +9pp).

**Terminal equity ratio vs T3d-K2:** all 4 LRS-on slots expected > 1.05×.

**Terminal equity ratio vs iter 017 anchor:** slot 3 = 2.908× target; slots 4-6
should land in [1.0×, 4.0×] depending on T_crash direction.

**Rolling-window win-rate vs T3d-K2 (1y/3y/5y/10y):** all 4 LRS-on slots
expected > 0.55 / 0.60 / 0.65 / 0.55 (similar to iter 027 slot 6 profile).

**KEY HYPOTHESIS expectation (modern_sortino_lift):** EXPECTED FALSE per
iter 027/028/029 structural diagnosis. T_crash perturbation alone cannot
lift modern subperiod Sortino ≥ 1.20 — modern softness is structural to
the rearm primitive's interaction with 2× QLD on-leg vol cluster, not to
the specific T_crash threshold. If KEY HYPOTHESIS fires (T35 or T50 lifts
modern Sortino above 1.20), it falsifies the structural diagnosis and
opens a new T_crash-conditional research direction.

**Tcrash_anchor_robustness expectation (KILL_LOOP #11):** EXPECTED TRUE.
Iter 027 selected T40 by inheritance from iter 017, not by sensitivity
scan; the perturbation test should confirm T40 is at or near a local
optimum. If FALSIFIED (#12 fires), iter 017's T40 choice was a fragile
local fit and the loop should re-tune to the dominant T_crash value.

**Comparison plan vs winner (T3d-K2):**
- beats_winner = (sortino_lh56y > 1.3746 AND winner_conditions_met AND pct_above ≥ 0.95)
- Expected: 4 of 4 LRS-on slots (3-6) probably beats_winner = True.

**Phase 3 performance plan:**
- phase3_performance_candidate = (cagr_lh56y > 0.3108 AND end_eq_ratio_vs_winner > 1.05 AND sortino_lh56y >= 1.20 AND PBO < 0.5 AND DSR_global p < 0.05)
- Expected: 4 of 4 LRS-on slots probably phase3_performance_candidate = True.

**Phase 4 anchor plan (iter 017 T40D60 anchor):**
- phase4_anchor_improved = ((cagr_lh56y > 0.3266 OR end_eq_ratio_vs_iter017 > 1.00) AND sortino_lh56y >= 1.35 AND PBO < 0.5 AND DSR_global p < 0.05)
- Expected: at least 1 of slots 3-6 probably phase4_anchor_improved = True.

---

## INCOMPLETE flags / caveats

1. **LRS gross-return approximation.** The iter 024 `apply_unconditional_lrs_overlay`
   helper applies a multiplicative scalar without modeling daily-rebalance
   compounding-vol-drag asymmetry. At LRS1.20× over multi-decade horizons
   this approximation is reasonable but optimistic. (Documented in
   iter 024's helper docstring; preserved for cross-iter calibration.)
2. **Synth-only series.** lh_56y window uses QLDSIM (Testfolio synth Gayed
   methodology). Real ETF (post-inception 2006-) parity is only verified
   on spy_real / ndx_real subsets.
3. **D_arm=60 frozen.** This iter does NOT scan D_arm; sensitivity is
   T_crash only. A future iter could complete the (T_crash, D_arm) joint
   scan if T_crash anchor robustness fails.
4. **n_global=606 DSR denominator.** All beats_winner claims use cumulative
   n_trials = closed-study 426 + loop 180. Local-only DSR reported as
   diagnostic.
5. **Mechanism diversity is 1-axis (T_crash) for slots 3-6.** The 2 prior
   anchors (slots 1-2) provide structural mechanism diversity. If PBO
   blows up despite this (KILL_LOOP #6 fires), it indicates 1-axis sweeps
   on the rearm primitive are not viable even at the LRS1.20 ceiling and
   the loop must pivot to non-rearm Phase 4 family for further T_crash
   exploration. The 4 ON-day rearm gates (slots 3-6) span sufficiently
   different event sets that they should not cluster ranks the way iter
   018's narrow grid did.
6. **Phase 4 anchor reference is iter 017 T40D60 (CAGR 32.66%).** Improvement
   is measured against this. Iter 027 slot 6 raised the de-facto research
   ceiling (CAGR 36.22%) but the formal anchor remains iter 017 per
   LOOP_PROTOCOL §"Phase 4 objective".

---

## Guardrails

- Capital remains 100% Plano C per mandate §1. No realloc regardless of `beats_winner`.
- No modifications to BASE_MEMORY.md, gates.py, scoring.py, plot_helper.py,
  data_loader.py, signals.py, signals_carry.py, synths.py, tax_layer.py,
  kill_rules.py, run_iter*.py, configs/, iterations/, verdict_schema.json.
- New helpers (none required for this iter — reuses iter 022 INDEP gate +
  iter 024 unconditional LRS overlay) live inside iter dir if added.
- No push to remote; commit only.
- STOP after PASSO 10.
