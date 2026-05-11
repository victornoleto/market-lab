# 018-2026-05-10-graded-rearm-depth-conditional — HYPOTHESIS

**Iter:** 018 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Slug:** `graded-rearm-depth-conditional`
**Datetime UTC pre-commit:** 2026-05-10 (loop session)
**Engine version:** loop_iter_018
**n_configs:** 6
**cumulative_n_trials_global before:** 528 (after iter 017)
**cumulative_n_trials_global after:** 534
**cumulative_n_trials_loop before:** 102
**cumulative_n_trials_loop after:** 108

---

## Hypothesis

**Graded rearm depth — D_arm linearly proportional to prior OFF stretch
length T_off.** Refines iter 017's empirically-validated FIXED-window
post-crash rearm (T40D60 → loop's first NEW (non-replica) strict_superset:
Sortino 1.4030, CAGR 32.66%, end_eq 1.62×, crisis 1/4) by making the
re-arm window length scale with the depth of the crash that preceded the
flip. Deeper crashes (longer OFF stretches) get proportionally longer
recovery windows — the streak-window-length-proportional-to-crash-depth
thesis suggested by `[leverage_for_the_long_run, p.4-7, ch.2-3]` (longer
below-MA stretches → stronger above-MA streaks per the seesaw-vs-streak
asymmetry).

Iter 017's "Surprise" finding was that T40D60 (deeper threshold + longer
harvest, 16 events × 60-day) STRICTLY DOMINATED T20D30 (shallower + shorter,
33 events × 30-day) on every Phase 3 axis, despite T20D30 having more
qualifying events. Pre-registered "more events = more lift" was contradicted.
That validated the **deeper, fewer** recipe — concentrated streak harvests
per active day.

**Iter 018 hypothesis:** if depth-thresholding (T_crash) and harvest-length
(D_arm) interact monotonically, then *graduating D_arm in proportion to the
specific OFF-stretch length actually observed* should outperform a
fixed-D_arm baseline. The graded rule reads "if T_off=40 was a 60-day
recovery, then T_off=80 deserves a 120-day recovery" — i.e. recovery time
scales with crash depth, not constant.

This is a NEW DIMENSION on iter 017's TIME-domain rearm primitive (graded
extension), preserving the Husson-Trifoni framework and not re-doing
iter 017's fixed (T_crash, D_arm) sweep.

**Primary citation:** `[leverage_for_the_long_run, p.4-7, ch.2-3]`
Husson-Trifoni — "Above its MA, the S&P 500 exhibits positive
autocorrelation (consecutive up-days more likely)... Below the MA,
alternating seesawing dominates. Behavioral explanation: low volatility →
investor underreaction → streaks; high volatility → overreaction → back-
and-forth."

**Secondary citations:**
- `[leverage_for_the_long_run, p.7]` "performance over time has nothing
  to do with time itself, but rather: 1) the behavior of the underlying
  asset in its overall trend, 2) the path of daily returns (streaks
  versus seesawing action), and 3) whether the regime under which leverage
  is utilized is high or low volatility" — direct support for graded
  depth-proportional harvest length.
- `[stocks_on_the_move, p.98]` Clenow trend-strength (post-crash trend
  re-establishment).
- `[volatility_trading, p.58-60]` Sinclair vol cone (low realised-vol
  regime onset post-crash).
- `[risk_parity, p.80-81, ch.4]` Qian RORO graded master-gate (gamma=0.25
  carries forward from iter 010/014).
- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking.
- `[systematic_trading, p.212, ch.13]` Carver semi-automatic stop re-arm
  (time-domain memory analogue).
- `[advances_fin_ml, p.208-211]` PBO via CSCV mechanism-mix-diversity.
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials (n_global=534).

---

## Configs (6, mechanism-mix-diverse with 4 distinct ON-leg-overlay topologies)

Naming convention: `qld_voteK2_sma250_100_vol21_40_ar30_grearm_<spec>`.
Slug abbreviates "graded-rearm".

| # | Name | Topology | Rearm rule | Role |
|---|---|---|---|---|
| 1 | `..._grearm_baseline_qld_zroz` | single/none/none | none | Calibration anchor (KILL_LOOP #3 baseline replica = 1.3240) |
| 2 | `..._grearm_single_K4lv25_g25_rvp70_cashx` | single/K4_AND_lv25/g=0.25/p70-cashx | none | Iter 014 strict_superset replica (KILL_LOOP #4 = 1.3951) |
| 3 | `..._grearm_single_K4lv25_g25_rvp70_cashx_T40D60` | single/K4_AND_lv25_OR_rearm_fixed/g=0.25/p70-cashx | fixed T=40 D=60 | Iter 017 NEW strict_superset replica (KILL_LOOP #5 = 1.4030) |
| 4 | **`..._grearm_single_K4lv25_g25_rvp70_cashx_p075_clamp30_120`** ← **PRIMARY** | single/K4_AND_lv25_OR_rearm_graded/g=0.25/p70-cashx | **D_arm = clamp(0.75 × T_off, 30, 120)** | Graded depth-proportional (PRIMARY) |
| 5 | `..._grearm_single_K4lv25_g25_rvp70_cashx_p050_clamp30_90` | single/K4_AND_lv25_OR_rearm_graded/g=0.25/p70-cashx | D_arm = clamp(0.50 × T_off, 30, 90) | Sensitivity (shallower / shorter clamp) |
| 6 | `..._grearm_single_K4lv25_g25_rvp70_cashx_p100_clamp40_150` | single/K4_AND_lv25_OR_rearm_graded/g=0.25/p70-cashx | D_arm = clamp(1.00 × T_off, 40, 150) | Sensitivity (deeper / longer clamp) |

**4 distinct ON-leg-overlay topologies** (mechanism-mix-diverse recipe):
- Slot 1: single/none — calibration anchor.
- Slot 2: single/K4_AND_lv25 — iter 014 strict_superset replica.
- Slot 3: single/K4_AND_lv25 OR fixed-T40D60 rearm — iter 017 NEW strict_superset replica.
- Slots 4-6: single/K4_AND_lv25 OR **graded** rearm — NEW topology family
  (graded D_arm ∝ T_off with clamp). Slots 4, 5, 6 share the graded
  family but parametrise differently (coefficient and clamp range).

**Datasets:** `lh_56y` (1970-01 → 2026-04), `modern_1990` (1990+), `spy_real` (2003+), `ndx_real` (2010+).
Same datasets as iter 017 for cross-iter comparability.

---

## Pre-registered KILL_LOOP conditions

| # | Tag | Rule | Type |
|---|---|---|---|
| 1 | `success_tag` | Any config has `beats_winner=True` (Sortino > 1.3746 AND winner_conditions_met=True AND pct_above_lh56y ≥ 0.95). | Positive (informational) |
| 2 | `decisive_fail` | Best Sortino_lh56y < 1.20 (Phase 3 floor — strategy mechanism dead). | Negative |
| 3 | `replica_sanity_baseline` | Baseline Sortino_lh56y deviates from iter 011-017 baseline 1.3240 by > 0.005. **9th-generation cross-iter reproducibility check.** | Sanity |
| 4 | `replica_sanity_single_K4lv25_g25` | `single_K4lv25_g25_rvp70_cashx` Sortino_lh56y deviates from iter 013-017 strict_superset 1.3951 by > 0.005. | Sanity |
| 5 | `replica_sanity_T40D60` | `single_K4lv25_g25_rvp70_cashx_T40D60` Sortino_lh56y deviates from iter 017 LOOP MAX strict_superset 1.4030 by > 0.005. **Cross-iter reproducibility for iter 017 NEW strict_superset.** | Sanity |
| 6 | `PBO_blowup` | G1 PBO ≥ 0.55 (hard regression threshold). | Negative |
| 7 | `PBO_held` | G1 PBO < 0.50 (Phase 3 hard gate). | Positive |
| 8 | `graded_rearm_phase3_perf_candidate` | Any graded-rearm config (slots 4/5/6) achieves `phase3_performance_candidate=True`. **CORE HYPOTHESIS TEST.** | Positive |
| 9 | `graded_rearm_strict_superset` | Any graded-rearm config (slots 4/5/6) achieves `strict_superset=True`. **STRONGEST HYPOTHESIS TEST.** | Positive |
| 10 | `graded_dominates_T40D60` | Any graded-rearm config has Sortino_lh56y > 1.4030 (iter 017 LOOP MAX strict_superset Sortino). **Direct dominance test for graded vs fixed.** | Positive |
| 11 | `graded_rearm_2020_covid_rescue` | Any graded-rearm config beats SPY in 2020_covid window. Iter 017 fixed T40D60 missed this; graded depth-proportional rearm may capture it via shorter D_arm during shallower flips. | Diagnostic |
| 12 | `graded_rearm_strict_superset_with_crisis_2plus` | Any graded-rearm config achieves `strict_superset=True` AND crisis count ≥ 2/4. **LOOP'S FIRST CRISIS-≥2/4 STRICT_SUPERSET** target. | Positive (diagnostic) |

---

## Expected outcomes (pre-registered)

### Sortino_lh56y range (per config, lh_56y)

| config | expected range | rationale |
|---|---|---|
| Slot 1 baseline | 1.3240 ± 0.005 | Replica anchor (KILL_LOOP #3) |
| Slot 2 single_K4lv25_g25 anchor | 1.3951 ± 0.005 | Replica anchor (KILL_LOOP #4) |
| Slot 3 T40D60 anchor | 1.4030 ± 0.005 | Replica anchor (KILL_LOOP #5) |
| Slot 4 graded p075 (PRIMARY) | 1.36 - 1.42 | Centered on iter 017 T40D60 (1.4030); graded mechanism may concentrate or dilute depending on regime mix |
| Slot 5 graded p050 (shorter) | 1.34 - 1.40 | Shorter clamp may dilute streak captures |
| Slot 6 graded p100 (longer) | 1.36 - 1.42 | Longer clamp may capture more streak per event but with more whipsaw exposure |

### CAGR_lh56y range (per config, lh_56y)

| config | expected range | gap vs T3d-K2 31.08% |
|---|---|---|
| Slot 1 baseline | 31.08% ± 0.0pp | Replica anchor |
| Slot 2 anchor | 31.47% ± 0.0pp | Replica anchor |
| Slot 3 T40D60 anchor | 32.66% ± 0.0pp | Replica anchor |
| Slot 4 graded p075 | 32-34% | Could exceed T40D60 if depth-proportional captures more concentrated streak harvest |
| Slot 5 graded p050 | 31-33% | Shorter clamp may dilute lift |
| Slot 6 graded p100 | 32-35% | Longer clamp captures more streak but with whipsaw cost |

### Phase 3 performance plan

For a graded-rearm slot to qualify as `phase3_performance_candidate`:
- `cagr_lh56y > 0.3108` (T3d-K2 floor)
- `end_eq_ratio_vs_baseline > 1.05`
- `sortino_lh56y >= 1.20` (Phase 3 floor)
- `g1_pbo < 0.50` (CSCV hard gate)
- `g2_dsr_p_cumulative < 0.05` (n_global=534)

For `beats_winner=true`:
- `sortino_lh56y > 1.3746`
- `winner_conditions_met = True`
- `pct_time_above_benchmark_lh56y >= 0.95`

`strict_superset = beats_winner AND phase3_performance_candidate`.

**Probability assessment** (subjective, pre-registered):
- KILL_LOOP #1 (success_tag) FIRES: 85% (slots 2, 3 are replicas of iter 014/017 strict_superset; graded slots may also clear)
- KILL_LOOP #6 (PBO_blowup) FIRES: 15% (4 distinct topologies preserved; mechanism-mix-diverse recipe expected to hold ~0.4405 ceiling like iter 017)
- KILL_LOOP #7 (PBO_held) FIRES (positive): 75%
- KILL_LOOP #8 (graded_phase3) FIRES: 60% (graded extension of validated mechanism)
- KILL_LOOP #9 (graded_strict_superset) FIRES: 45% (graded must beat both Sortino threshold AND CAGR floor under graded coefficient sensitivity)
- KILL_LOOP #10 (graded_dominates_T40D60) FIRES: 30% (graded may concentrate harvests better OR dilute; not strongly directional ex-ante)
- KILL_LOOP #11 (graded_2020_covid_rescue) FIRES: 20% (mechanism unchanged from iter 017 — flip-conditional only; graded D_arm doesn't address V-recovery onset timing)
- KILL_LOOP #12 (graded_strict_superset_with_crisis_2plus) FIRES: 12% (combined condition; LOOP'S FIRST target remains hard)

### Comparison plan vs T3d-K2 winner

For best graded-rearm config, report:
- `sortino_edge_vs_winner = sortino_lh56y - 1.3246`
- `cagr_edge_vs_winner = cagr_lh56y - 0.3108`
- `end_equity_ratio_vs_winner = candidate_end_equity / winner_end_equity` (computed against iter 017 single anchor baseline equity proxy)
- Rolling-window win rates: 1y/3y/5y/10y vs iter 014 single anchor.
- `beats_winner` (frozen criterion per LOOP_PROTOCOL).
- `phase3_performance_candidate` (Phase 3 strict bar).
- `strict_superset` (intersection).

---

## INCOMPLETE flags (pre-registered caveats)

- **Synth caveat (UPRO/UGL pre-1985):** UPRO synth inception ~1985; UGL synth calibrated 2008-2026 then extrapolated. Per study `synths.py` documentation, pre-1985 synths inherit calibration. Slots 1-6 use single ON-leg (no UPRO/UGL); UPRO/UGL not on critical path for this iter. **Marginal data risk.**
- **CASHX FFR proxy:** OFF-leg uses CASHX = `data/testfolio/cashx.json` FFR proxy. iter 014/017 used same.
- **Graded D_arm clamp arbitrariness:** the 30/90/120/150 clamp values are pre-registered (not optimised post-hoc). Slot 4's clamp(30, 120) brackets iter 017's fixed D=60. Slots 5-6 stress upper/lower bounds. Anti-curve-fit per `[advances_fin_ml, p.208-211]` — coefficient and clamp pre-committed before run.
- **Mechanism-mix-diverse PBO ceiling:** iter 013 lesson — parametric clusters within same family inflate PBO. Mitigation: 4 distinct topologies (slot 1 baseline, slot 2 anchor, slot 3 fixed rearm, slots 4-6 graded rearm) — same diversity recipe as iter 017's 0.4405 PBO.
- **Tax / fees stress NOT included** in this iter (diagnostic-only per next-iter idea (e) from iter 017). Reported gross of Lei 14.754 swing tax 15%.
- **No cross-asset leverage** in this iter (idea (a) from iter 017's "next iter ideas" list — deferred to a future iter to keep this one focused on the graded-D_arm thesis).

---

## File checklist (PASSO 6)

- [ ] hypothesis.md (this file) — pre-commit
- [ ] backtest.py — main entrypoint
- [ ] graded_reentry_overlay.py — iter-local helper (extends iter 017's reentry_overlay.py)
- [ ] verdict.json (validates against `studies/letf_rotation_hunt/loop_verdict_schema.json`)
- [ ] SUMMARY.md (mirrors iter 017)
- [ ] plots/01_equity_curves.png … 07_crisis_attribution.png
- [ ] tables/per_config_metrics.csv
- [ ] tables/gates_pass_fail.csv
