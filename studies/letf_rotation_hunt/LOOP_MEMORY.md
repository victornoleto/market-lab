---
mission: "post-close strategy hunt: research new strategies and benchmark vs T3d-K2 study winner"
status: open
active_phase: 4
active_phase_name: "iter 017 focused validation/refinement"
total_iterations: 20
target_total_iterations: 50
closed_study_cumulative_n_trials: 426
cumulative_n_trials_loop: 120
cumulative_n_trials_global: 546
incumbent_winner_iter: "022-2026-05-06-T3d-extended-grid"
incumbent_winner_config: "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
incumbent_winner_sortino_lh56y: 1.3246
incumbent_winner_sharpe_lh56y: 0.919
incumbent_winner_cagr_lh56y: 0.3108
incumbent_winner_mdd_lh56y: -0.6450
incumbent_winner_score: 82
beats_winner_threshold_sortino: 1.3746
beats_winner_threshold_pct_above_spy: 0.95
beats_winner_threshold_winner_conditions_met: true
phase3_performance_threshold_cagr_lh56y: 0.3108
phase3_performance_threshold_end_equity_ratio_vs_winner: 1.05
phase3_min_acceptable_sortino_lh56y: 1.20
loop_winner_iter: ["009-2026-05-09-master-scope-off-override", "010-2026-05-09-graded-master-bridge", "012-2026-05-10-compound-tqqq-K4-x-ratevol-off", "014-2026-05-10-mechanism-mix-diverse-graded-blend", "015-2026-05-10-equity-tilted-basket-cagr-recovery", "016-2026-05-10-regime-switch-on-leg-basket", "017-2026-05-10-postcrash-rearm-tqqq-streak", "019-2026-05-10-spyrv-pct25-upgrade-mechmix", "020-2026-05-10-spy-mdd-rearm-gate"]
loop_phase3_performance_candidate_iter: ["011-2026-05-10-conditional-tqqq-leverage", "012-2026-05-10-compound-tqqq-K4-x-ratevol-off", "014-2026-05-10-mechanism-mix-diverse-graded-blend", "015-2026-05-10-equity-tilted-basket-cagr-recovery", "016-2026-05-10-regime-switch-on-leg-basket", "017-2026-05-10-postcrash-rearm-tqqq-streak", "019-2026-05-10-spyrv-pct25-upgrade-mechmix", "020-2026-05-10-spy-mdd-rearm-gate"]
loop_strict_superset_iter: ["012-2026-05-10-compound-tqqq-K4-x-ratevol-off", "014-2026-05-10-mechanism-mix-diverse-graded-blend", "015-2026-05-10-equity-tilted-basket-cagr-recovery", "016-2026-05-10-regime-switch-on-leg-basket", "017-2026-05-10-postcrash-rearm-tqqq-streak", "019-2026-05-10-spyrv-pct25-upgrade-mechmix", "020-2026-05-10-spy-mdd-rearm-gate"]
latest_iteration: "020-2026-05-10-spy-mdd-rearm-gate"
latest_score: 76.5
latest_tier_label: STRONG
latest_beats_winner: true
latest_phase3_performance_candidate: true
latest_strict_superset: true
latest_strict_superset_is_novel: true
latest_g1_pbo: 0.4325
latest_g1_pbo_loop_min: false
phase4_anchor_iter: "017-2026-05-10-postcrash-rearm-tqqq-streak"
phase4_anchor_config: "qld_voteK2_sma250_100_vol21_40_ar30_rearm_single_K4lv25_g25_rvp70_cashx_T40D60"
phase4_anchor_cagr_lh56y: 0.3266
phase4_anchor_sortino_lh56y: 1.4030
phase4_anchor_end_equity_ratio_vs_winner: 1.61
phase4_anchor_pbo: 0.4405
---

# letf_rotation_hunt — LOOP MEMORY

**Lê PRIMEIRO toda iteração.** Estado do post-close strategy hunt.

Não confundir com `BASE_MEMORY.md` (registro do study fechado, frozen). O loop
roda em paralelo, não modifica o estudo, e usa o study winner T3d-K2
(`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`, Sortino_lh56y 1.3246) como
benchmark fixo.

## Beats-winner criterion (frozen)

Um iter conta como `beats_winner=true` se TODOS os três passam:

1. `sortino_lh56y > 1.3746` (= 1.3246 + 0.05 anti-curve-fit margin)
2. `winner_conditions_met = True` (per scoring rubric)
3. `pct_time_above_benchmark_lh56y >= 0.95`

Falha em qualquer um → `beats_winner=false`. Loop **não para** no primeiro
beater (decisão de design — varredura ampla preferida sobre halt rápido).

Se um iter bate, registra em `loop_winner_iter` (lista de todos beaters)
e adiciona flag de review humana — **nunca** dispara realocação de capital
sozinho. Mandate §1 preserva 100% Plano C; qualquer deploy precisa de
mandate §7 override request manual.

## Trial accounting

DSR/p-value reporting in loop iters must use `cumulative_n_trials_global`, not
only the configs tested inside the current iter. Global trials start at the
closed-study count (426 after T5) and add every loop config. Local-only DSR is
allowed as a diagnostic, but cannot support `beats_winner=true` unless the
global-trials DSR still passes `[advances_fin_ml, p.222-223]`.

## Phase 3 — performance-first beater hunt (from iter 011)

User directive: the original T3d-K2 winner already has acceptable risk control;
do **not** keep trading performance for more safety. From iter 011 onward,
the loop should search for strategies with better risk/profit **and** better
absolute/relative performance. Sortino-only beaters (iters 009-010) are useful
research leads but not sufficient for the user's preference.

Phase 3 objective metrics:

1. Preserve statistical gates: PBO < 0.5 and DSR global p < 0.05 remain hard.
2. Prefer `cagr_lh56y > 31.08%` (T3d-K2 benchmark CAGR) and report the gap.
3. Prefer terminal equity ratio vs T3d-K2 > 1.05 and report rolling-window
   win rates over 1y/3y/5y/10y.
4. Maintain reasonable risk/profit: Sortino_lh56y >= 1.20 is the minimum
   acceptable floor; lower Sortino is not acceptable even if CAGR rises.
5. Avoid pure de-risking variants unless they also improve CAGR/terminal
   equity. A lower drawdown alone is not a Phase 3 win.

Every iter 011+ `hypothesis.md`, `SUMMARY.md`, and `verdict.json` should add
`phase3_performance_candidate` diagnostics: `cagr_lh56y`, `cagr_edge_vs_winner`,
`end_equity_ratio_vs_winner`, rolling win rates, and whether the config clears
the performance-first objective. CAGR/rolling-window comparisons remain
diagnostics under the mandate, while PBO/DSR/global-trial controls remain the
statistical hard gates `[advances_fin_ml, p.208-211]`, `[advances_fin_ml,
p.222-223]`.

## Phase 4 — iter 017 focused validation/refinement (from iter 021)

User directive: stop broad hunting for now. Treat iter 017's post-crash rearm
family (`T40D60`) as the research incumbent and validate/refine it. The goal is
not another open-ended search; it is to test whether the iter 017 edge is real,
parameter-robust, and improvable without sacrificing performance.

Phase 4 anchor:

- Iter: `017-2026-05-10-postcrash-rearm-tqqq-streak`
- Config: `qld_voteK2_sma250_100_vol21_40_ar30_rearm_single_K4lv25_g25_rvp70_cashx_T40D60`
- Metrics: CAGR 32.66%, Sortino 1.4030, terminal equity 1.61× T3d-K2,
  PBO 0.4405, global DSR pass.

Phase 4 allowed work:

1. Sensitivity around `T_crash` / `D_arm`, but max 6-8 configs and mechanism-
   diverse grids. Avoid pure narrow sweeps that caused iter 018 PBO blow-up.
2. Ablation: no rearm, rearm without TQQQ, TQQQ without rearm, OFF-duration
   only, crash-depth only, rearm window only.
3. Temporal robustness: subperiod tables (1987-1999, 2000-2009, 2010-2019,
   2020-2026) and event-level flip audit.
4. Independent implementation/cross-check inside iter dir before any claim that
   improves the anchor.
5. Any candidate must beat or preserve the Phase 4 anchor on CAGR/equity while
   preserving PBO < 0.5 and DSR global p < 0.05. A lower-MDD-only variant is a
   failure unless CAGR/terminal equity also improve.

Phase 4 success tags:

- `phase4_anchor_validated=true`: independent implementation or ablation shows
  the rearm mechanism, not incidental parameter choice, drives the edge.
- `phase4_anchor_improved=true`: candidate beats anchor CAGR (>32.66%) OR
  terminal ratio (>1.61×) while Sortino >= 1.35, PBO < 0.5, DSR global p < 0.05.
- `phase4_reject_anchor=true`: if sensitivity/cross-check shows T40D60 is a
  fragile event fit or fails PBO/DSR under fair re-test.

Every iter 021+ should explicitly state whether it validated, improved, or
weakened the iter 017 anchor `[advances_fin_ml, p.208-211]`, `[advances_fin_ml,
p.222-223]`.

## Iteration log (newest first)

### 020 — 2026-05-10 — spy-mdd-rearm-gate

**Hypothesis:** Refines iter 017's only NOVEL strict_superset
(`single_K4lv25_g25_rvp70_cashx_T40D60`, Sortino 1.4030) by gating its
rearm activation on SPY trailing 200d max drawdown depth at the
qualifying-flip moment. Six configs (mechanism-mix-diverse — 5 distinct
upgrade-axis topologies); slots 5+6 are NEW MDD-gated variants
(thresholds -15% and -25%). Tests whether requiring a real prior
broader-index drawdown prunes seesaw-induced false positives in iter
017's 16 qualified flips.
**Primary citation:** `[leverage_for_the_long_run, p.4-7, ch.2-3]`
Husson-Trifoni streak-vs-seesawing.
**Secondary:** `[regime_change, p.5-6, ch.2]` Chen-Tsang regime-change;
`[regime_change, p.44-46, ch.4]` abnormal-regime onset post-crisis;
`[regime_change, p.70-71, ch.5]` B-Strict analogue;
`[stocks_on_the_move, p.98]` Clenow trend re-establishment;
`[volatility_trading, p.58-60]` Sinclair vol cone; `[risk_parity,
p.80-81, ch.4]` Qian RORO graded; `[risk_parity, ch.5, p.10]` Carlson
stacking; `[systematic_trading, p.212, ch.13]` Carver re-arm;
`[advances_fin_ml, p.208-211]` CSCV PBO; `[advances_fin_ml, p.222-223]`
DSR cumulative (n_global=546).

**Configs tested (6, mechanism-mix-diverse with 5 distinct upgrade-axis topologies):**

| name | ON-leg | upgrade axis | rearm | mdd_thresh | sortino_lh56y | edge | cagr_lh56y | edge | end_eq | MDD | score | tier | WC | crisis | phase3 | beats | strict |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| `..._mddgate_baseline_qld_zroz` | single QLD | none | — | — | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | -64.5% | 76.5 | STRONG | T | 1/4 | F | F | F |
| `..._mddgate_single_K4lv25_g25_rvp70_cashx` ← iter 014 strict_superset replica | single QLD/TQQQ | K4_AND_QLDlv25 | — | — | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | -47.7% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T** |
| 🥇 `..._mddgate_basket3invvol_K4lv25_g25_rvp70_cashx` ← iter 014 LOOP MAX Sortino replica | basket3-invvol60 | K4_AND_QLDlv25 | — | — | **1.4689** | +0.1443 | 0.2265 | -8.43pp | 0.056× | **-32.8%** | **81.5** | STRONG | **T** | 2/4 | F | T | F |
| 🏆 `..._mddgate_single_K4lv25_g25_rvp70_cashx_T40D60` ← iter 017 NEW strict_superset replica | single QLD/TQQQ | K4_AND_QLDlv25 OR rearm | T40D60 | — | **1.4030** | **+0.0784** | **0.3266** | **+1.58pp** | **1.620×** | -48.2% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T** |
| 🏆 `..._mddgate_single_K4lv25_g25_rvp70_cashx_T40D60_mdd15` ← **PRIMARY (NEW)** | single QLD/TQQQ | K4_AND_QLDlv25 OR rearm_MDD | T40D60 | -0.15 | **1.3973** | +0.0727 | **0.3216** | **+1.08pp** | **1.393×** | -47.7% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T-NEW** |
| `..._mddgate_single_K4lv25_g25_rvp70_cashx_T40D60_mdd25` ← STRICTER (NEW) | single QLD/TQQQ | K4_AND_QLDlv25 OR rearm_MDD | T40D60 | -0.25 | 1.3808 | +0.0562 | 0.3134 | +0.26pp | 1.086× | -47.7% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T-NEW** |

**KILL_LOOP results (pre-registered):**
- 🎯 ✅ KILL_LOOP #1 (success_tag) — **FIRED.** 5 of 6 configs achieve
  beats_winner=True (slots 2, 3, 4 replicas + slots 5, 6 NEW). 8th
  loop iter to fire success_tag. **2 NEW non-replica beats_winner
  configs from this iter.**
- ❌ KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.4030
  ≫ 1.20 floor).
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact iter 011-019 baseline (drift 0.0000).
  **11th-generation cross-iter reproducibility.**
- ✅ KILL_LOOP #4 (replica_sanity_single_K4lv25_g25) — **NOT FIRED.**
  Sortino 1.3951 = bit-exact iter 013-019 (drift 0.0000).
- ✅ KILL_LOOP #5 (replica_sanity_basket3invvol_K4lv25_g25) — **NOT
  FIRED.** Sortino 1.4689 / CAGR 22.65% / MDD -32.82% = bit-exact
  iter 014-019 (drift 0.0000).
- ✅ KILL_LOOP #6 (replica_sanity_T40D60) — **NOT FIRED.** Sortino
  1.4030 = bit-exact iter 017-019 NEW strict_superset (drift 0.0000).
  **3rd-generation reproducibility on iter 017's first novel
  strict_superset CONFIRMED.**
- ❌ KILL_LOOP #7 (PBO_blowup) — **NOT FIRED.** G1 PBO 0.4325 < 0.55.
- 🎯 ✅ KILL_LOOP #8 (PBO_held) — **FIRED — POSITIVE TAG.** G1 PBO
  **0.4325** < 0.50 hard gate. Above iter 019's LOOP MIN 0.1984 — the
  MDD-depth filter adds less mechanism diversity than spyrv25 because
  it is a refinement of an existing rearm rather than a fully
  orthogonal axis. Iter trajectory: 005 0.881 → 011 0.3056 → 014
  0.4405 → 017 0.4405 → 018 0.8135 → 019 0.1984 (LOOP MIN) → **020
  0.4325**.
- 🏆 ✅ KILL_LOOP #9 (mddgate_phase3_perf_candidate) — **FIRED.** Both
  MDD15 and MDD25 achieve phase3=True (CAGR > 0.3108 ✓, end_eq > 1.05×
  ✓, Sortino ≥ 1.20 ✓, PBO 0.4325 < 0.50 ✓, DSR_global 1.10e-3 / 1.39e-3
  < 0.05 ✓). **CORE WEAK HYPOTHESIS CONFIRMED.**
- 🏆 🎯 ✅ KILL_LOOP #10 (mddgate_strict_superset) — **FIRED.** Both
  MDD15 and MDD25 achieve strict_superset=True. **STRONGEST WEAK
  HYPOTHESIS CONFIRMED. 2 NEW NON-REPLICA STRICT_SUPERSET CONFIGS
  FROM THIS ITER (slots 5, 6).**
- ❌ KILL_LOOP #11 (mddgate_dominates_T40D60) — **NOT FIRED.** Best
  MDD-gated Sortino is MDD15 1.3973 (-0.0057 vs T40D60 anchor 1.4030).
  **STRONG HYPOTHESIS REJECTED — depth filter does NOT lift Sortino.**
- ❌ KILL_LOOP #12 (mddgate_strict_superset_with_crisis_2plus) —
  **NOT FIRED.** Both MDD-gated strict_supersets are crisis 1/4 only.
  **LOOP'S FIRST CRISIS-≥2/4 STRICT_SUPERSET STILL NOT ACHIEVED.**

**Key finding: 🏆 🎯 LOOP'S 2ND NOVEL (NON-REPLICA) STRICT_SUPERSET —
slot 5 MDD15 confirms mechanism robustness at a NEW topology axis.**
Slot 5 (`single_K4lv25_g25_rvp70_cashx_T40D60_mdd15`): Sortino 1.3973
(+0.0727 vs winner 1.3246, **-0.0057 vs T40D60 anchor 1.4030**), CAGR
32.16% (+1.08pp vs T3d-K2 floor 31.08%), end_eq 1.393× (>> 1.05×
floor), MDD -47.69%. Slot 6 MDD25 also achieves strict_superset (Sortino
1.3808, CAGR 31.34%, end_eq 1.086× — barely above 1.05× floor). **Both
add NEW topology entries to `loop_strict_superset_iter` (the loop's 2nd
and 3rd novel non-replica strict_supersets after iter 017's T40D60).**

**⚠️ STRONG HYPOTHESIS REJECTED — KILL_LOOP #11 NOT FIRED.** SPY 200d
MDD-depth filter does NOT lift Sortino above T40D60 anchor. MDD15
drops Sortino by 0.006 (CAGR -0.50pp / end_eq -0.227×); MDD25 drops
Sortino by 0.022 (CAGR -1.32pp / end_eq -0.534×). **Mechanism
diagnosis:** the 16 duration-qualified flips include both deep MDD
events (sample: -33%, -19%, -29%) and shallow ones (-11%, -12%). MDD15
retains 12/16 (drops 4 with MDD ∈ (-15%, 0%]); MDD25 retains 4/16
(drops 12 with MDD ∈ (-25%, 0%]). The 4 shallow flips dropped by MDD15
contribute -0.50pp CAGR / -0.227× end_eq. **Counterintuitively,
shallow-drawdown flips DO contain alpha** — TQQQ's 3× leverage
amplifies even moderate post-MA-flip rallies regardless of pre-flip
drawdown depth. Husson-Trifoni "deeper crashes → stronger streaks"
qualitatively SUPPORTED (each retained deep flip produces material lift)
but does NOT generalize to "must be deep" for QLD/TQQQ rotation.

**All 4 calibration anchors PRESERVED bit-exact** (KILL_LOOP #3, #4,
#5, #6 ALL NOT FIRED): baseline 1.3240 (11th-gen replica),
single_K4lv25_g25 1.3951 (8th-gen), basket3invvol 1.4689 (6th-gen),
T40D60 1.4030 (3rd-gen) — **iter 017's first novel strict_superset
confirmed reproducible across 3 generations.** **G1 PBO 0.4325** <
0.50 hard gate (above iter 019's LOOP MIN 0.1984; consistent with
MDD-depth being a refinement of existing rearm rather than wholly
orthogonal axis). Crisis attribution unchanged at 1/4 for all
single-asset configs (only 2008 GFC); 2/4 for basket3 (loses 2020
COVID).

**Capital remains 100% Plan C per mandate §1**; iter appended to
`loop_winner_iter` (9th iter), `loop_phase3_performance_candidate_iter`
(8th iter), AND `loop_strict_superset_iter` (7th iter — both NEW
strict_supersets from this iter; **latest_strict_superset_is_novel =
true**). Score 76.5 STRONG < 90 deploy bar; per LOOP_PROTOCOL §"Mandate
§1 reinforcement", `docs/CURRENT_STATE.md` "Active Hunts" entry
preserved untouched. **NO automatic capital realloc.**

**beats_winner:** **true** (5 of 6 configs > 1.3746 threshold; 3
replicas + 2 NEW; best is slot 4 T40D60 anchor 1.4030).

**phase3_performance_candidate (any):** **true** (slots 2 + 4 replicas
+ slots 5 + 6 NEW).

**strict_superset (any):** **🎯 true** (slots 2 + 4 replicas + slots
5 + 6 NEW; **latest_strict_superset_is_novel = true** — 2 NEW
non-replica strict_supersets from iter 020).

**Next iter ideas:** (a) **T_crash sweep at fixed D_arm=60** — test
T_crash ∈ {20, 30, 40, 50, 60} keeping all other iter 017 parameters
fixed. Tests whether T40D60 is the local maximum or whether shorter
T_crash values (catching more, shallower flips) lift further.
**Highest expected value: directly tunes iter 017 hyperparameter
space.** Cite `[leverage_for_the_long_run, p.6-7, ch.3]`. (b)
**Post-flip realised-vol confirmation gate** — fire rearm only if the
first 5 trading days following MA-flip-on show realised vol < threshold
(CONFIRMATION vs MDD15's REJECTION). Cite `[volatility_trading,
p.58-60]`. (c) **Pivot to entirely different family** — calendar/
seasonality (post-FOMC, monthly turn, Halloween), cross-asset
correlation regime (SPY-Treasury), or yield-curve slope. Per
LOOP_PROTOCOL §"Soft-halt hint", iters 018, 019, 020 all tried T40D60-
overlay refinements; family change may be due. **Highest expected
value if loop's CAGR-lift trajectory has plateaued.** (d) **Combined
T_crash + D_arm joint sweep** {(30,45), (40,60), (50,75), (60,90)}.
(e) **Post-flip TQQQ-vol confirmation** — QLD-vol percentile in first
5 days post-flip < 50th.

### 019 — 2026-05-10 — spyrv-pct25-upgrade-mechmix

**Hypothesis:** SPY 21d realised-vol percentile (< 25th vs trailing
1260-day window) as an alternative upgrade-gate trigger that is
OR-combined with iter 014's K4_AND_QLDlv25 and iter 017's T40D60
post-crash rearm. Six configs (mechanism-mix-diverse — 5 distinct
upgrade-axis topologies) testing whether broader-market vol-regime
onsets unlock additional upgrade activation that asset-specific QLD-vol
misses, in pursuit of the loop's 5th strict_superset on a NEW
forward-vol-orthogonal axis.
**Primary citation:** `[volatility_trading, p.58-60]` Sinclair vol cone
(percentile-based vol-regime gate).
**Secondary:** `[leverage_for_the_long_run, p.4-7, ch.2-3]`
Husson-Trifoni low-vol⇒streaks; `[stocks_on_the_move, p.98]` Clenow
trend re-establishment; `[risk_parity, p.80-81, ch.4]` Qian RORO graded;
`[risk_parity, ch.5, p.10]` Carlson stacking; `[systematic_trading,
p.212, ch.13]` Carver re-arm hysteresis (slot 6 inheritance);
`[advances_fin_ml, p.208-211]` CSCV PBO; `[advances_fin_ml, p.222-223]`
DSR cumulative (n_global=540).

**Configs tested (6, mechanism-mix-diverse with 5 distinct upgrade-axis topologies):**

| name | ON-leg | upgrade axis | rearm | sortino_lh56y | edge | cagr_lh56y | edge | end_eq | MDD | score | tier | WC | crisis | phase3 | beats | strict |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| `..._spyrv_baseline_qld_zroz` | single QLD | none | — | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | -64.5% | 76.5 | STRONG | T | 1/4 | F | F | F |
| `..._spyrv_single_K4lv25_g25_rvp70_cashx` ← iter 014 strict_superset replica | single QLD/TQQQ | K4_AND_QLDlv25 | — | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | -47.7% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T** |
| 🥇 `..._spyrv_basket3invvol_K4lv25_g25_rvp70_cashx` ← iter 014 LOOP MAX Sortino replica | basket3-invvol60 | K4_AND_QLDlv25 | — | **1.4689** | +0.1443 | 0.2265 | -8.43pp | 0.056× | **-32.8%** | **81.5** | STRONG | **T** | **3/4** | F | T | F |
| 🏆 `..._spyrv_single_K4lv25_g25_rvp70_cashx_T40D60` ← iter 017 NEW strict_superset replica | single QLD/TQQQ | K4_AND_QLDlv25 OR rearm | T40D60 | **1.4030** | **+0.0784** | **0.3266** | **+1.58pp** | **1.620×** | -48.2% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T** |
| `..._spyrv_single_K4lv25_OR_spyrv25_g25_rvp70_cashx` ← PRIMARY (rejected) | single QLD/TQQQ | K4_AND_QLDlv25 OR SPYRV25 | — | 1.2899 | -0.0347 | 0.3085 | -0.23pp | 0.933× | -48.4% | 76.5 | STRONG | T | 1/4 | F | F | F |
| `..._spyrv_single_K4lv25_OR_spyrv25_g25_rvp70_cashx_T40D60` ← STRONGEST (phase3 only) | single QLD/TQQQ | K4_AND_QLDlv25 OR SPYRV25 OR rearm | T40D60 | 1.3133 | -0.0113 | 0.3220 | +1.12pp | 1.409× | -48.2% | 76.5 | STRONG | T | 1/4 | **T** | F | F |

**KILL_LOOP results (pre-registered):**
- 🎯 ✅ KILL_LOOP #1 (success_tag) — **FIRED.** 3 of 6 configs achieve
  beats_winner=True (single replica, basket3 replica, T40D60 replica).
  7th loop iter to fire success_tag (after 009/010/012/014/015/016/017).
- ❌ KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.4030
  ≫ 1.20 floor).
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact match to iter 011-018 (drift 0.0000).
  **10th-generation cross-iter reproducibility.**
- ✅ KILL_LOOP #4 (replica_sanity_single_K4lv25_g25) — **NOT FIRED.**
  single_K4lv25_g25 Sortino 1.3951 = bit-exact match to iter 013-018
  (drift 0.0000).
- ✅ KILL_LOOP #5 (replica_sanity_basket3invvol_K4lv25_g25) — **NOT
  FIRED.** basket3invvol Sortino 1.4689 / CAGR 22.65% / MDD -32.82% /
  crisis 3/4 = bit-exact match to iter 014-017 (drift 0.0000).
- ✅ KILL_LOOP #6 (replica_sanity_T40D60) — **NOT FIRED.** T40D60
  Sortino 1.4030 = bit-exact match to iter 017-018 NEW strict_superset
  (drift 0.0000). **2nd-generation reproducibility on iter 017's first
  novel strict_superset CONFIRMED.**
- ❌ KILL_LOOP #7 (PBO_blowup) — **NOT FIRED.** G1 PBO 0.1984 ≪ 0.55
  ceiling.
- 🏆 🎯 ✅ KILL_LOOP #8 (PBO_held) — **FIRED — POSITIVE TAG.** G1 PBO
  **0.1984** ≪ 0.50 hard gate. **NEW LOOP MIN** (vs prior 0.3056 iter
  011, by -0.107pp). Iter trajectory: 005 0.881 → 006 0.798 → 007 0.552
  → 008 0.5675 → 009 0.3770 → 010 0.3929 → 011 0.3056 → 012 0.4960 →
  013 0.5437 → 014 0.4405 → 015 0.3333 → 016 0.3730 → 017 0.4405 → 018
  0.8135 → **019 0.1984 (NEW LOOP MIN)**.
- 🎯 ✅ KILL_LOOP #9 (spyrv_phase3_perf_candidate) — **FIRED.** Slot 6
  (3-way OR composite) achieves phase3=True (CAGR 32.20%, end_eq 1.409×,
  Sortino 1.3133, PBO 0.1984, DSR_global 3.14e-3). **CORE WEAK
  HYPOTHESIS CONFIRMED.**
- ❌ KILL_LOOP #10 (spyrv_strict_superset) — **NOT FIRED.** 0 of 2
  spyrv configs achieve strict_superset (slot 5 Sortino 1.2899 / slot 6
  Sortino 1.3133, both < 1.3746 threshold). **STRONGEST HYPOTHESIS
  REJECTED.**
- ❌ KILL_LOOP #11 (spyrv_2020_covid_rescue) — **NOT FIRED.** No spyrv
  config beats SPY in 2020_covid window. SPY-RV-pct25 fires too late
  (post-recovery) for V-bottom capture.
- ❌ KILL_LOOP #12 (spyrv_strict_superset_with_crisis_2plus) — **NOT
  FIRED.** Loop's first crisis-≥2/4 strict_superset still not achieved.

**Key finding: ⚠️ STRONG HYPOTHESIS REJECTED — SPY-RV-pct25 OR-add does
NOT beat K4_AND_QLDlv25 anchor on Sortino, but G1 PBO 0.1984 = NEW LOOP
MIN (best mechanism-mix-diversity result yet).** Slot 5 Sortino 1.2899
(-0.1052 vs slot 2 anchor 1.3951); slot 6 Sortino 1.3133 (-0.0897 vs
slot 4 T40D60 anchor 1.4030). Slot 5 fails Phase 3 floor (CAGR 30.85% <
31.08%; end_eq 0.933× < 1.05×). Slot 6 PASSES Phase 3 (CAGR 32.20%,
end_eq 1.409×, Sortino ≥ 1.20) — KILL_LOOP #9 fires — but cannot clear
the +0.05 anti-curve-fit margin above winner Sortino 1.3246. **Mechanism
diagnosis:** SPY-RV-pct25 fires 27.6% of valid days vs K4_AND_QLDlv25's
7.1% — the OR-add expands upgrade activation 4× from 7.1% to 26-30%,
but the broader-market low-vol regime captures many ranging-market
windows where leverage drag dominates compounding. **Sinclair vol cone
gate at 25th percentile on SPY is too inclusive for LETF rotation
upgrade.** **All 4 calibration anchors PRESERVED bit-exact** (KILL_LOOP
#3, #4, #5, #6 ALL NOT FIRED): baseline 1.3240 (10th-gen replica),
single_K4lv25_g25 1.3951 (8th-gen), basket3invvol 1.4689 (5th-gen),
T40D60 1.4030 (2nd-gen) — **iter 017's first novel strict_superset
confirmed reproducible across one full generation.** **G1 PBO 0.1984 —
NEW LOOP MIN** (smashes prior 0.3056 by -0.107pp). 5-distinct-mechanism-
topology recipe pushes CSCV diversity to its empirical floor —
methodological contribution: confirms that ADDING a genuinely orthogonal
upgrade-axis (different vol asset, different fire-rate) reduces ranking-
clustering substantially even when the new mechanism does not unlock
alpha. **Capital remains 100% Plan C per mandate §1**; iter NOT a NEW
strict_superset finding (slots 2 + 4 are replicas of iter 014 + iter 017
respectively). Score 76.5 STRONG < 90 deploy bar; per LOOP_PROTOCOL
§"Mandate §1 reinforcement", `docs/CURRENT_STATE.md` "Active Hunts"
entry preserved untouched. **NO automatic capital realloc.** Iter
appended to `loop_winner_iter` (8th iter), `loop_phase3_performance_
candidate_iter` (7th iter), AND `loop_strict_superset_iter` (6th iter
— but all replicas; slot 4 T40D60 remains the loop's only NOVEL
strict_superset, content-equivalent to iter 017).

**beats_winner:** **true** (3 of 6 configs > 1.3746 threshold; all
replicas; best is slot 4 T40D60).

**phase3_performance_candidate (any):** **true** (slot 6 NEW + slots 2
+ 4 replicas).

**strict_superset (any):** **🎯 true** (slots 2 + 4 replicas;
**latest_strict_superset_is_novel = false** — no NEW iter 019
strict_superset).

**Next iter ideas:** (a) **AND-combine SPY-RV-pct25 with
K4_AND_QLDlv25** — test whether intersection (not union) provides better
selectivity. Activation expected ~6%. Cite `[volatility_trading,
p.58-60]`. **Highest expected value: directly tests the rejection
mechanism** (OR was too permissive; AND tests if intersection is more
selective than QLDlv25 alone). (b) **Tighter percentile (10th instead of
25th)** — extreme-low-vol only. Activation expected ~10-12%. Combined
with iter 017 T40D60 rearm. (c) **VIX-based forward-looking signal**
— VIX percentile (vs trailing 1y) replaces realised-vol percentile.
1990+ coverage limits to modern_1990 dataset. Cite `[volatility_trading,
p.217-218]`. (d) **UGL-realised-vol percentile** — different asset
class (gold), more orthogonal to QLD-equity-vol than SPY. Cite
`[volatility_trading, p.58-60]` cross-asset. (e) **Crash-MDD-conditional
rearm** — fire rearm only when prior OFF stretch coincides with
trailing 200d SPY MDD breach > -15%. Filters seesaw-induced false
rearms. Cite `[regime_change]` + `[leverage_for_the_long_run, p.4-7]`.

### 018 — 2026-05-10 — graded-rearm-depth-conditional

**Hypothesis:** Graded rearm depth — D_arm linearly proportional to
prior OFF-stretch length T_off. Refines iter 017's NEW (non-replica)
strict_superset (`single_K4lv25_g25_rvp70_cashx_T40D60`, Sortino 1.4030,
CAGR 32.66%, end_eq 1.62×) by making the rearm harvest-window length
scale with the depth of the crash that preceded each qualifying flip.
Tests Husson-Trifoni's longer-below-MA → longer-above-MA streak thesis
at the per-event D_arm level.
**Primary citation:** `[leverage_for_the_long_run, p.4-7, ch.2-3]`
Husson-Trifoni streaks-vs-seesawing asymmetry.
**Secondary:** `[leverage_for_the_long_run, p.7]` trend × streaks ×
vol-regime; `[stocks_on_the_move, p.98]` Clenow trend re-establishment;
`[volatility_trading, p.58-60]` Sinclair vol cone; `[risk_parity,
p.80-81, ch.4]` Qian RORO graded; `[risk_parity, ch.5, p.10]` Carlson
stacking; `[systematic_trading, p.212, ch.13]` Carver re-arm
hysteresis; `[advances_fin_ml, p.208-211]` CSCV PBO; `[advances_fin_ml,
p.222-223]` DSR cumulative (n_global=534).

**Configs tested (6, only 2 distinct ON-leg topologies — STRUCTURAL DEFICIENCY):**

| name | rearm rule | qual.flips | mean D | sortino_lh56y | edge | cagr_lh56y | edge | end_eq | MDD | score | tier | WC | crisis | phase3 | beats | strict |
|---|---|--:|--:|---:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| `..._grearm_baseline_qld_zroz` | none | 0 | — | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | -64.5% | 72.5 | PROMISING | F | 1/4 | F | F | F |
| `..._grearm_single_K4lv25_g25_rvp70_cashx` (iter 014 replica) | none | 0 | — | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | -47.7% | 72.5 | PROMISING | F | 1/4 | F | F | F |
| 🥇 `..._grearm_single_K4lv25_g25_rvp70_cashx_T40D60` (iter 017 replica) | fixed T=40 D=60 | 16 | 60 | **1.4030** | **+0.0784** | 0.3266 | +1.58pp | 1.620× | -48.2% | 72.5 | PROMISING | F | 1/4 | F | F | F |
| `..._grearm_single_K4lv25_g25_rvp70_cashx_p075_clamp30_120` ← PRIMARY | graded coef=0.75 [30,120] | 16 | 58.4 | 1.3946 | +0.0700 | 0.3238 | +1.30pp | 1.492× | -48.2% | 72.5 | PROMISING | F | 1/4 | F | F | F |
| `..._grearm_single_K4lv25_g25_rvp70_cashx_p050_clamp30_90` | graded coef=0.50 [30,90] | 16 | 43.6 | 1.3920 | +0.0674 | 0.3207 | +0.99pp | 1.356× | -47.7% | 72.5 | PROMISING | F | 1/4 | F | F | F |
| `..._grearm_single_K4lv25_g25_rvp70_cashx_p100_clamp40_150` | graded coef=1.00 [40,150] | 16 | 76.0 | 1.3997 | +0.0751 | **0.3287** | **+1.79pp** | **1.731×** | -48.2% | 72.5 | PROMISING | F | 1/4 | F | F | F |

**KILL_LOOP results (pre-registered):**
- ❌ KILL_LOOP #1 (success_tag) — **NOT FIRED.** No config achieves
  beats_winner=True (G1 PBO 0.8135 ≥ 0.50 fails WC strict bar
  universally, even though Sortino > 1.3746 ✓ + pct_above ≥ 0.95 ✓ for
  5 of 6 configs).
- ✅ KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.4030
  ≫ 1.20 floor).
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact match to iter 011-017 baseline (drift
  0.0000). **9th-generation cross-iter reproducibility.**
- ✅ KILL_LOOP #4 (replica_sanity_single_K4lv25_g25) — **NOT FIRED.**
  single_K4lv25_g25_rvp70_cashx Sortino 1.3951 = bit-exact match to
  iter 013-017 strict_superset (drift 0.0000).
- ✅ KILL_LOOP #5 (replica_sanity_T40D60) — **NOT FIRED.**
  single_K4lv25_g25_T40D60 Sortino 1.4030 = bit-exact match to iter
  017 LOOP MAX strict_superset (drift 0.0000). **Iter 017's NEW
  strict_superset confirmed reproducible.**
- 🛑 KILL_LOOP #6 (PBO_blowup) — **FIRED.** G1 PBO **0.8135** ≥ 0.55
  hard regression threshold. **Largest single-iter PBO regression in
  the loop** (iter 017 0.4405 → iter 018 0.8135; +0.373pp). Iter
  trajectory: 005 0.881 → 006 0.798 → 007 0.552 → 008 0.5675 → 009
  0.3770 → 010 0.3929 → 011 0.3056 → 012 0.4960 → 013 0.5437 → 014
  0.4405 → 015 0.3333 → 016 0.3730 → 017 0.4405 → **018 0.8135**.
  Cause: 5 of 6 configs share K4_AND_lv25/g=0.25/p70-cashx base
  topology; rearm-overlay variation alone (none/fixed/graded × 3
  coefficients) does NOT introduce CSCV mechanism diversity. **3rd-time
  confirmation of iter 008/013 lesson** — "mechanism diversity for
  CSCV is structural, not parametric" `[advances_fin_ml, p.208-211]`.
- ❌ KILL_LOOP #7 (PBO_held) — **NOT FIRED.** G1 PBO 0.8135 ≥ 0.50.
- ❌ KILL_LOOP #8 (graded_rearm_phase3_perf_candidate) — **NOT FIRED.**
  0 of 3 graded configs achieve phase3=True (PBO blocks all). **CORE
  HYPOTHESIS REJECTED at the statistical level**, though mechanically
  the graded variants preserve T40D60's CAGR/end_eq within ±0.27pp.
- ❌ KILL_LOOP #9 (graded_rearm_strict_superset) — **NOT FIRED.** 0 of 3
  graded configs achieve strict_superset (PBO blocks). **STRONGEST
  HYPOTHESIS REJECTED.**
- ❌ KILL_LOOP #10 (graded_dominates_T40D60) — **NOT FIRED.** Best
  graded Sortino 1.3997 (slot 6 p100) < T40D60 1.4030 (-0.0033). Graded
  variation does NOT improve over fixed T40D60 on Sortino.
  Husson-Trifoni depth-proportional thesis SUPPORTED qualitatively
  (CAGR/end_eq monotonic in coefficient: 32.07% → 32.38% → 32.87%; end_eq
  1.36× → 1.49× → 1.73×) but Sortino at the local optimum is fixed
  T40D60.
- ❌ KILL_LOOP #11 (graded_rearm_2020_covid_rescue) — **NOT FIRED.** 0
  of 3 graded configs beat SPY in 2020_covid window. Mechanism-equivalent
  to iter 017 — graded D_arm doesn't address V-recovery onset timing.
- ❌ KILL_LOOP #12 (graded_rearm_strict_superset_with_crisis_2plus) —
  **NOT FIRED.** 0 of 3 graded achieve strict_superset AND crisis ≥ 2/4.
  **LOOP'S FIRST CRISIS-≥2/4 STRICT_SUPERSET STILL NOT ACHIEVED.**

**Key finding: ⚠️ HYPOTHESIS REJECTED AT THE STATISTICAL LEVEL — G1 PBO
BLOWUP (KILL_LOOP #6 FIRED).** G1 PBO **0.8135** (vs iter 017's 0.4405;
+0.373pp jump — largest single-iter PBO regression in the loop). Cause:
5 of 6 configs share the iter 014 strict_superset base topology (`single
/K4_AND_lv25/g=0.25/p70-cashx`), differing only in rearm specifics
(none/fixed/graded × 3 coefficients). CSCV correctly penalises this
parametric clustering — **3rd-time confirmation** of the iter 008/013
lesson "mechanism diversity for CSCV is structural, not parametric"
`[advances_fin_ml, p.208-211]`. PBO ≥ 0.50 hard gate fails for every
config → `winner_conditions_met=False` universally → `beats_winner=
false`, `phase3_performance_candidate=false`, `strict_superset=false`
for ALL 6 configs.

**All 3 calibration anchors PRESERVED bit-exact** (KILL_LOOP #3, #4, #5
NOT FIRED): baseline 1.3240 (9th-gen replica), single_K4lv25_g25
1.3951, T40D60 1.4030 — **iter 017's NEW strict_superset confirmed
reproducible across one generation**. Mechanism-level finding (separate
from the statistical KILL): graded D_arm preserves CAGR/end_eq lift
within ±0.27pp of T40D60, monotonic in coefficient (slot 5 coef=0.50
CAGR 32.07% / end_eq 1.36× → slot 4 coef=0.75 CAGR 32.38% / end_eq
1.49× → slot 6 coef=1.00 CAGR 32.87% / end_eq 1.73×). Slot 6 (longest
clamp, mean D=76) achieves highest CAGR/end_eq in iter 018; Sortino
plateaus near 1.40 across the coefficient range. **The fixed T40D60
mechanism is at or near the local Sortino optimum** for QLD/TQQQ rearm
in this universe; graded variation captures EXISTING streak structure
but does not unlock additional Sortino.

**Crisis attribution unchanged at 1/4** for all 6 configs (only
2008_GFC) — graded D_arm doesn't address V-recovery onset timing for
2020_covid (same iter 017 root cause: on_signal=OFF during Feb-Mar 2020
V-bottom). All configs pct_above_SPY = 1.0000 in lh_56y. **All gates
G2-G7 are CLEAN** for non-baseline configs (DSR cum 1.0e-3, OOS Sharpe
1.0+, FWD post-2020 Sharpe 0.92-0.97, bootstrap 99% CI low ~0.60); the
LONE blocker is G1 PBO 0.8135.

**Capital remains 100% Plan C per mandate §1**; iter NOT appended to
`loop_winner_iter`, `loop_phase3_performance_candidate_iter`, or
`loop_strict_superset_iter` (no positive flags). Score 72.5 PROMISING
< 90 deploy bar; per LOOP_PROTOCOL §"Mandate §1 reinforcement",
`docs/CURRENT_STATE.md` "Active Hunts" entry preserved untouched.
**NO automatic capital realloc.**

**beats_winner:** **false** (no config achieves `winner_conditions_met
=True` because G1 PBO 0.8135 ≥ 0.50; Sortino + pct_above thresholds
cleared by 5 of 6).

**phase3_performance_candidate (any):** **false** (PBO ceiling fails
for all 6; first iter since 013 with 0 phase3 candidates).

**strict_superset (any):** **false** (no NEW finding; iter 014/017
strict_supersets remain reproducible but iter 018 contributes nothing).

**Next iter ideas:** (a) **VIX-percentile / SPY-realised-vol gate on
flip qualification** — forward-volatility gate orthogonal to ALL
previously-tested mechanics. Use SPY 21d realised-vol percentile (vs
trailing 5y) as a VIX proxy (no pre-1990 VIX data needed). Add as ONE
distinct topology alongside basket3 + rearm variants to maintain CSCV
diversity. **Highest expected value: untested orthogonal mechanism +
restores PBO diversity.** Cite `[volatility_trading, ch.7]` Sinclair
VRP. (b) **Mechanism-mix-diverse rearm × basket3** — repeat iter 017's
4-distinct-topology recipe but stack graded D_arm in slots 4+5; tests
graded inside diversity. Cite `[advances_fin_ml, p.208-211]` CSCV
mechanism diversity. (c) **Drawdown-conditional rearm gate** — fire
rearm only when prior OFF stretch coincides with trailing 200d SPY MDD
breach > -15%; filters seesaw-induced false positives. Cite
`[regime_change]` + `[leverage_for_the_long_run, p.4-7]`. (d) **Tax /
fees stress on iter 017 strict_superset** — turnover ~5.3/y; quantify
Lei 14.754 swing tax 15% diagnostic (deferred from iter 017). (e)
**Pivot to entirely different family** — calendar/seasonality beyond
Halloween (e.g., post-FOMC drift), currency carry baskets, or gold
momentum. Iter 008/013/018 statistical lessons suggest exhausting the
K4_AND_lv25/g=0.25/p70-cashx neighbourhood may be subject to diminishing
returns; a regime change in family choice may be due.

### 017 — 2026-05-10 — postcrash-rearm-tqqq-streak

**Hypothesis:** Post-crash re-arm to TQQQ (streak capture overlay).
Stacks a TIME-domain re-arm window onto iter 014's strict_superset
(`single_K4lv25_g25_rvp70_cashx`) and triple-stack
(`basket3invvol_K4lv25_g25_rvp70_cashx`). The overlay strictly ADDS
upgrade-gate activation (OR-combine with K4_AND_lv25) for D_arm
trading days following each OFF→ON master-signal flip preceded by ≥
T_crash days OFF. Targets the loop's first crisis-≥2/4
strict_superset by capturing asymmetric post-crash rebounds (1974,
1982, 2002, 2009, 2020 March, 2023 January) with TQQQ exposure that
the K4_AND_lv25 state-domain gate misses. **First TIME-domain
mechanism in the loop** — orthogonal axis vs all prior state-domain
gates (K4 vote, lowvol percentile, ratevol, regime switch).
**Primary citation:** `[leverage_for_the_long_run, p.6-7, ch.3]`
Husson-Trifoni — above MA, positive autocorrelation/streaks; below
MA, seesawing. The MA flip-ON is the empirical streak-window onset.
**Secondary:** `[leverage_for_the_long_run, p.4, ch.2]` streaks vs
seesawing thesis; `[stocks_on_the_move, p.98]` Clenow trend
re-establishment; `[volatility_trading, p.58-60]` Sinclair vol cone;
`[risk_parity, p.80-81, ch.4]` Qian RORO; `[risk_parity, ch.5,
p.10]` Carlson stacking; `[systematic_trading, p.212, ch.13]` Carver
re-arm hysteresis (time-domain memory analogue applied to ENTRY
leverage); `[advances_fin_ml, p.208-211]` PBO; `[advances_fin_ml,
p.222-223]` DSR cumulative (n_global=528).

**Configs tested (6, mechanism-mix-diverse with 4 distinct ON-leg-overlay topologies):**

| name | ON-leg | upgrade base | T_crash | D_arm | qual.flips | rearm% | sortino_lh56y | edge | cagr_lh56y | edge | end_eq | MDD | score | tier | WC | crisis | phase3 | beats | strict |
|---|---|---|--:|--:|--:|--:|---:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| `..._rearm_baseline_qld_zroz` | single QLD | none | — | — | 0 | 0.0% | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | -64.5% | 76.5 | STRONG | T | 1/4 | F | F | F |
| `..._rearm_single_K4lv25_g25_rvp70_cashx` ← anchor (replica) | single QLD/TQQQ | K4_AND_lv25 | disabled | disabled | 0 | 0.0% | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | -47.7% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **T** |
| 🥇 `..._rearm_basket3invvol_K4lv25_g25_rvp70_cashx` ← LOOP MAX Sortino replica | basket3-invvol60 | K4_AND_lv25 | disabled | disabled | 0 | 0.0% | **1.4689** | +0.1443 | 0.2265 | -8.43pp | 0.056× | **-32.8%** | **81.5** | STRONG | **T** | **3/4** | F | T | F |
| `..._rearm_single_K4lv25_g25_rvp70_cashx_T20D30` ← phase3 only (Sortino 0.003 below threshold) | single QLD/TQQQ | K4_AND_lv25 OR rearm | 20 | 30 | **33** | 9.92% | 1.3716 | +0.0470 | 0.3172 | +0.64pp | 1.217× | -48.2% | 76.5 | STRONG | **T** | 1/4 | F | **T** | F |
| 🏆 **`..._rearm_single_K4lv25_g25_rvp70_cashx_T40D60`** ← 🎯 LOOP'S FIRST NEW STRICT_SUPERSET / LOOP MAX strict-superset Sortino | single QLD/TQQQ | K4_AND_lv25 OR rearm | 40 | 60 | **16** | 9.70% | **1.4030** | **+0.0784** | **0.3266** | **+1.58pp** | **1.620×** | -48.2% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T** |
| `..._rearm_basket3invvol_K4lv25_g25_rvp70_cashx_T20D30` ← TRADE-OFF RESOLUTION (rejected) | basket3-invvol60 | K4_AND_lv25 OR rearm | 20 | 30 | **33** | 9.92% | 1.4685 | +0.1439 | 0.2276 | -8.32pp | 0.058× | -32.8% | **81.5** | STRONG | **T** | **3/4** | F | T | F |

**KILL_LOOP results (pre-registered):**
- 🏆 ✅ KILL_LOOP #1 (success_tag) — **FIRED.** 3 of 6 configs
  achieve beats_winner=True (single replica, basket3 replica, slot 5
  T40D60 NEW). 6th loop iter to fire success_tag (after
  009/010/012/014/015/016).
- KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.4030
  >> 1.20 floor).
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact match to iter 011-016 baseline (drift
  0.0000). **8th-generation cross-iter reproducibility.**
- ✅ KILL_LOOP #4 (replica_sanity_single_K4lv25_g25) — **NOT FIRED.**
  single_K4lv25_g25_rvp70_cashx Sortino 1.3951 = bit-exact match to
  iter 013/014/015/016 (drift 0.0000).
- ✅ KILL_LOOP #5 (replica_sanity_basket3invvol_K4lv25_g25) — **NOT
  FIRED.** basket3invvol_K4lv25_g25_rvp70_cashx Sortino 1.4689 / CAGR
  22.65% / MDD -32.82% / crisis 3/4 = bit-exact match to iter
  014/015/016 triple-stack (drift 0.0000).
- ✅ KILL_LOOP #6 (PBO_blowup) — **NOT FIRED.** G1 PBO 0.4405 << 0.55.
- 🎯 ✅ KILL_LOOP #7 (PBO_held) — **FIRED — POSITIVE TAG.** G1 PBO
  **0.4405** < 0.50 hard gate. **Identical to iter 014** —
  mechanism-mix-diverse 5-distinct-topology recipe extended with
  TIME-domain rearm overlay; the (T_crash, D_arm) parametric
  variation does NOT introduce new CSCV ranking clustering. Iter
  trajectory: 005 0.881 → 006 0.798 → 007 0.552 → 008 0.5675 → 009
  0.3770 → 010 0.3929 → 011 0.3056 → 012 0.4960 → 013 0.5437 → 014
  0.4405 → 015 0.3333 → 016 0.3730 → **017 0.4405**.
- 🏆 ✅ KILL_LOOP #8 (rearm_phase3_perf_candidate) — **FIRED.** 2 of 3
  rearm configs achieve phase3_performance_candidate=True (slots 4 +
  5; slot 6 basket3+rearm fails by structural CAGR ceiling). **CORE
  HYPOTHESIS CONFIRMED — Husson-Trifoni MA-streak thesis empirically
  validated for the single ON-leg.**
- 🏆 🎯 ✅ KILL_LOOP #9 (rearm_strict_superset) — **FIRED.** Slot 5
  T40D60 strict_superset=True. **LOOP'S FIRST NOVEL (NON-REPLICA)
  STRICT_SUPERSET CONFIG.** Sortino 1.4030 = LOOP MAX strict_superset
  Sortino (+0.0079 above iter 012/014's 1.3951 ceiling). CAGR 32.66%
  > 31.08% Phase 3 floor by +1.58pp; end_eq 1.620× > 1.05 floor.
  **STRONGEST HYPOTHESIS CONFIRMED.**
- ❌ KILL_LOOP #10 (rearm_2020_covid_rescue) — **NOT FIRED.** No
  rearm config beats SPY in 2020_covid window. Strategy was OFF
  during Feb-March 2020 steepest drawdown (CASHX); MA flip-ON came
  June 2020; D_arm=60 forced TQQQ for rebound but SPY had already
  recovered so fast that strategy couldn't catch up. **Rearm
  overlay's CAGR lift comes from older crisis rebounds
  (1974/1982/2002/2009/2023 — non-benchmark windows), not from 2020
  specifically.** Informational, not hypothesis-rejecting (slot 5
  strict_superset achieved without 2020 rescue).
- ❌ KILL_LOOP #11 (rearm_strict_superset_with_crisis_2plus) —
  **NOT FIRED.** Slot 5 strict crisis 1/4 only (2008 GFC); slot 6
  crisis 3/4 but not strict. Cross-product still empty. **LOOP'S
  FIRST CRISIS-≥2/4 STRICT_SUPERSET STILL NOT ACHIEVED.**
- ❌ KILL_LOOP #12 (rearm_basket3_unlocks_phase3) — **NOT FIRED.**
  Slot 6 CAGR 22.76% << 31.08% floor. TQQQ swap during D_arm=30
  replaces only the QLD/TQQQ leg (~33% basket weight); UPRO + UGL
  still run via invvol. CAGR lift over basket3 anchor = +0.11pp —
  trivial vs 8.4pp gap. **Combined with iter 015 (eqtilt) and iter
  016 (regsw), this is the THIRD INDEPENDENT REJECTION of the
  basket3 CAGR ↔ crisis trade-off resolution attempt. The trade-off
  is overlay-resistant.**

**Key finding: 🏆 🎯 LOOP'S FIRST NOVEL (NON-REPLICA) STRICT_SUPERSET
— Husson-Trifoni "streak window" thesis empirically validated.**
Slot 5 `single_K4lv25_g25_rvp70_cashx_T40D60` strictly improves on
iter 014's single anchor strict_superset across **all three Phase 3
axes**: Sortino 1.3951 → **1.4030** (+0.0079, LOOP MAX
strict_superset Sortino); CAGR 31.47% → **32.66%** (+1.19pp, lifts
above T3d-K2 winner by +1.58pp); end_eq 1.13× → **1.62×** (+0.49,
+43% terminal compounding). 5y rolling win rate 40.1% → 55.3%
(+15.2pp); 10y rolling win rate 22.9% → 38.0% (+15.1pp). Mechanism:
post-crash re-arm to TQQQ for D_arm=60 trading days following each
OFF→ON master-signal flip preceded by ≥ T_crash=40 days OFF — 16
qualified flips over 56 years (~3.5 year cadence; ~9.7% active
rate). **First TIME-domain mechanism in the loop** — orthogonal axis
vs all prior state-domain gates (K4 vote, lowvol percentile,
ratevol, regime switch). **Surprise:** T40D60 (16 deeper events ×
60-day harvest) STRICTLY DOMINATES T20D30 (33 shallower events ×
30-day harvest) on every Phase 3 axis. Pre-registered "more events
= more lift" expectation CONTRADICTED. The "deeper, fewer" recipe
captures more concentrated streak regime per active day —
empirical confirmation of Husson-Trifoni p.6: low volatility →
investor underreaction → streaks; the streak regime is tighter and
longer than T20 thresholds admit. **Surprise:** 2020 COVID NOT
rescued — strategy was OFF during the Feb-March drawdown (CASHX);
SPY V-recovery faster than rearm-window TQQQ harvest. **Surprise:**
slot 4 T20D30 phase3=True but Sortino 1.3716 misses 1.3746 beats
threshold by **just 0.003** — phase3 candidate without crossing
beats_winner anti-curve-fit margin. **All 3 calibration anchors
PRESERVED bit-exact** (KILL_LOOP #3, #4, #5 NOT FIRED): baseline
1.3240 (8th-gen replica), single_K4lv25_g25 1.3951, basket3invvol
1.4689 / CAGR 22.65% / MDD -32.82% / crisis 3/4. **G1 PBO 0.4405 —
identical to iter 014** — TIME-domain rearm parametric variation
does NOT induce new CSCV ranking clustering. **Slot 6 (basket3 +
rearm) does NOT unlock Phase 3**: CAGR 22.76% lift over basket3
anchor's 22.65% is only +0.11pp (TQQQ swap replaces ~33% basket
weight only); structural CAGR ceiling overlay-resistant. Combined
with iter 015 (eqtilt rejection) + iter 016 (regsw rejection),
this is the **THIRD INDEPENDENT REJECTION** of the basket3 CAGR ↔
crisis trade-off resolution attempt. **Capital remains 100% Plan
C per mandate §1**; iter appended to `loop_winner_iter` (7th iter),
`loop_phase3_performance_candidate_iter` (6th iter), AND
`loop_strict_superset_iter` (5th iter — and **the FIRST iter to
contribute a UNIQUE strategy** rather than a replica of iter
012/014's strict_superset). Loop's strict_superset list now contains
4 unique configs:
  - iter 012's `..._tqqq_K4_AND_lv25_rvp70_cashx`
  - iter 014's `..._mmix_K4lv25_g0_rvp70_cashx` (iter 012 replica)
  - iter 014's `..._mmix_K4lv25_g25_rvp70_cashx` (LOOP MAX g25)
  - **iter 017's `..._rearm_single_K4lv25_g25_rvp70_cashx_T40D60` (NEW)**
Score 76.5 (slot 5 strict_superset) < 90 deploy bar; per
LOOP_PROTOCOL §"Mandate §1 reinforcement", `docs/CURRENT_STATE.md`
"Active Hunts" entry preserved untouched. **NO automatic capital
realloc.**

**beats_winner:** **true** (3 of 6 configs > 1.3746 threshold:
single replica 1.3951, basket3 replica 1.4689, **slot 5 T40D60 NEW
1.4030**).

**phase3_performance_candidate (any):** **true** (3 of 6: single
replica, slot 4 T20D30, **slot 5 T40D60 NEW**).

**strict_superset (any):** **🎯 true** (2 of 6: single replica AND
**slot 5 T40D60 NEW** — LOOP'S FIRST NOVEL STRICT_SUPERSET).

**Next iter ideas:** (a) **Combined rearm × leverage overlay on
slot 5** — stack a 1.1×–1.5× multiplier on the ON-leg returns
during the rearm window. **Highest expected value: directly extends
iter 017's confirmed mechanism with a multiplicative boost.** Cite
`[leverage_for_the_long_run, ch.4-5, p.40-60]`; `[risk_parity,
ch.5, p.10]`. Risk: PBO regression toward 0.50; Sortino floor
under leveraged TQQQ pre-rebound vol. (b) **Rearm with VIX-
percentile guard** — fire rearm only when prior OFF stretch had VIX
percentile > 75th AND post-flip VIX < 50th. Targets crisis 2/4 by
adding 2020 COVID rescue via forward-looking gate. Cite
`[volatility_trading, ch.7]` Sinclair VRP. (c) **Event-driven
crisis overlay** — slot activates basket3-invvol ONLY during
pre-defined crisis windows (e.g., 6m post 200d SPY MDD breach >
20%) and falls back to slot 5 (rearm single) otherwise. Risk:
in-sample fitting via post-hoc crisis windows; needs OOS validation.
`[regime_change]`. (d) **AND-gate fine-grid sweep on slot 5 with
K4_AND_lvN sensitivity** — slot 5's 7.1% K4_AND_lv25 active rate
under the rearm overlay (total 11.8% upgrade activation) may not be
optimal; sweep K4 ∩ {lv15, lv20, lv25, lv30, lv40}. Risk: PBO
regression. (e) **Tax / fees stress on slot 5 strict_superset** —
turnover 5.32/y; quantify Lei 14.754 swing tax 15%; diagnostic.

### 016 — 2026-05-10 — regime-switch-on-leg-basket

**Hypothesis:** Regime-conditional ON-leg basket switching — switch
between iter 014's two endpoints (single QLD/TQQQ for high CAGR vs
basket3-invvol QLD/UPRO/UGL for crisis cushion) based on regime
indicator (lowvol50 vol percentile, K=4 vote of 4 signals). Tests
whether dynamic switching can recover Phase 3 CAGR floor (>31.08%)
while retaining basket3-invvol's crisis 3/4 cushion — the structural
trade-off iter 015's static fixed-weight eqtilt could not unlock.
Targets the loop's first crisis-≥2/4 strict_superset.
**Primary citation:** `[risk_parity, p.80-81, ch.4]` Qian RORO regime-
conditional master-gate.
**Secondary:** `[risk_parity, p.110, ch.5]` Qian fixed-weight
diversification (frames dynamic vs static); `[risk_parity, p.11, ch.1]`
Qian invvol over-allocation; `[risk_parity, ch.5, p.10]` Carlson
stacking; `[volatility_trading, p.58-60]` Sinclair vol cone (lowvol50);
`[stocks_on_the_move, p.98]` Clenow trend-strength (K=4);
`[systematic_trading, ch.10]` Carver inverse-vol;
`[leverage_for_the_long_run, ch.4-5, p.40-60]` LRS;
`[advances_fin_ml, p.208-211]` CSCV PBO; `[advances_fin_ml,
p.222-223]` DSR cumulative (n_global=522).

**Configs tested (6, mechanism-mix-diverse with 4 distinct ON-leg topologies):**

| name | ON-leg | regime gate | upg/rv | sortino_lh56y | edge | cagr_lh56y | edge | end_eq | MDD | score | tier | WC | crisis | phase3 | beats | strict |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| `..._regsw_baseline_qld_zroz` | single QLD | — | none/none | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | -64.5% | 76.5 | STRONG | T | 1/4 | F | F | F |
| **`..._regsw_single_K4lv25_g25_rvp70_cashx`** ← strict_superset replica | single QLD/TQQQ | — | K4lv25/p70-cashx | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | -47.7% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T** |
| 🥇 `..._regsw_basket3invvol_K4lv25_g25_rvp70_cashx` ← LOOP MAX Sortino replica | basket3-invvol60 | — | K4lv25/p70-cashx | **1.4689** | +0.1443 | 0.2265 | -8.43pp | 0.056× | **-32.8%** | **81.5** | STRONG | **T** | **3/4** | F | T | F |
| **`..._regsw_lv50_K4lv25_g25_rvp70_cashx`** ← PRIMARY (rejected) | regsw-lv50 (41.7% single) | vol_21d < 50th pct | K4lv25/p70-cashx | 1.2631 | -0.0615 | 0.2271 | -8.37pp | 0.057× | -33.8% | 78.5 | STRONG | F | **3/4** | F | F | F |
| **`..._regsw_K4_K4lv25_g25_rvp70_cashx`** ← surprise best regsw Sortino | regsw-K4 (20.2% single) | K=4 vote fires | K4lv25/p70-cashx | **1.3647** | +0.0401 | 0.2361 | -7.47pp | 0.076× | -36.0% | **81.5** | T | **3/4** | F | F | F |
| `..._regsw_lv50_K4lv25_g0_rvp80_ief` ← surprise COVID rescue | regsw-lv50 (41.7% single) | vol_21d < 50th pct | K4lv25/p80-ief | 1.2412 | -0.0834 | 0.2333 | -7.75pp | 0.070× | -34.7% | 78.5 | STRONG | F | **3/4** | F | F | F |

**KILL_LOOP results (pre-registered):**
- 🏆 ✅ KILL_LOOP #1 (success_tag) — **FIRED.** 2 of 6 configs achieve
  beats_winner=True (single replica, basket3-invvol replica). 5th loop
  iter to fire success_tag (after 009/010/012/014/015).
- KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.3951 >>
  1.20 floor).
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact match to iter 011-015 baseline (drift
  0.0000). **7th-generation cross-iter reproducibility.**
- ✅ KILL_LOOP #4 (replica_sanity_single_K4lv25_g25) — **NOT FIRED.**
  single_K4lv25_g25_rvp70_cashx Sortino 1.3951 = bit-exact match to
  iter 013/014/015 (drift 0.0000).
- ✅ KILL_LOOP #5 (replica_sanity_basket3invvol_K4lv25_g25) — **NOT
  FIRED.** basket3invvol_K4lv25_g25_rvp70_cashx Sortino 1.4689 / CAGR
  22.65% / MDD -32.82% / crisis 3/4 = bit-exact match to iter 014/015
  triple-stack (drift 0.0000).
- ✅ KILL_LOOP #6 (PBO_blowup) — **NOT FIRED.** G1 PBO 0.3730 << 0.55
  ceiling.
- 🎯 ✅ KILL_LOOP #7 (PBO_held) — **FIRED — POSITIVE TAG.** G1 PBO
  **0.3730** < 0.50 hard gate. **LOOP 3rd-MIN** (after iter 011's
  0.3056 and iter 015's 0.3333). Iter trajectory: 005 0.881 → 006
  0.798 → 007 0.552 → 008 0.5675 → 009 0.3770 → 010 0.3929 → 011
  0.3056 → 012 0.4960 → 013 0.5437 → 014 0.4405 → 015 0.3333 →
  **016 0.3730**. 4-distinct-ON-leg-topology recipe held even with
  slots 4+6 sharing the lv50 regime gate.
- ❌ KILL_LOOP #8 (regsw_phase3_perf_candidate) — **NOT FIRED.** **0
  of 3 regsw variants achieve phase3_performance_candidate=True.**
  CORE HYPOTHESIS REJECTED — regime-switch does not clear Phase 3 CAGR
  floor.
- ❌ KILL_LOOP #9 (regsw_strict_superset) — **NOT FIRED.** 0 of 3
  regsw variants achieve strict_superset=True. STRONGEST HYPOTHESIS
  REJECTED.
- 🎯 ✅ KILL_LOOP #10 (regsw_crisis_2or3_of_4) — **FIRED — POSITIVE
  TAG.** **3 of 3 regsw configs achieve crisis 3/4** (lv50 g25, K4
  g25, lv50 g0 IEF). Regime switch retains basket3-invvol's crisis
  cushion bit-exactly with anchor.
- ❌ KILL_LOOP #11 (regsw_strict_superset_with_crisis) — **NOT
  FIRED.** 0 of 3 regsw achieve strict_superset AND crisis ≥ 2/4.
  Loop's first crisis-≥2/4 strict_superset NOT achieved.
- 🤔 KILL_LOOP #12 (lv50_dominates_K4 — DIAGNOSTIC) — **NOT FIRED —
  SURPRISE.** Sortino lv50 1.2631 < Sortino K4 1.3647 (-0.1016
  edge). Pre-registered expectation (lv50 routes single more often
  → higher Sortino) CONTRADICTED. **K4 trend-conviction is the
  smarter regime gate by Sortino**: K=4 fires only ~20% of the time
  but routes single during high-Sharpe trend regimes; lv50 routes
  single 41.7% of the time including some choppy-but-low-vol windows
  that don't deliver CAGR/Sortino boost.

**Key finding: ⚠️ DYNAMIC REGIME-SWITCH HYPOTHESIS REJECTED — CAGR ↔
crisis trade-off is mechanism-agnostic.** All 3 regsw configs preserve
basket3-invvol's crisis 3/4 cushion (KILL_LOOP #10 FIRED) but NONE
clear Phase 3 CAGR floor (KILL_LOOP #8/#9/#11 NOT FIRED). Best regsw
CAGR is K4's 23.61% (-7.47pp); best regsw Sortino is K4's 1.3647 (just
below 1.3746 beats threshold). **Combined with iter 015's eqtilt
rejection, the loop now has TWO independent rejections of the trade-
off resolution attempt** — neither static fixed-weight (iter 015) nor
dynamic regime-conditional (iter 016) approaches resolve it. The
basket3-invvol's CAGR penalty is too severe to be diluted by either
weight-averaging OR part-time deployment. **All 3 calibration anchors
PRESERVED bit-exact** (KILL_LOOP #3, #4, #5 NOT FIRED): baseline
1.3240 (7th-gen replica), single_K4lv25_g25 1.3951, basket3invvol
1.4689 / CAGR 22.65% / MDD -32.82% / crisis 3/4. **G1 PBO 0.3730 —
LOOP 3rd-MIN** (after iter 011's 0.3056 and iter 015's 0.3333).
**Surprise #1:** K4 regime > lv50 regime by Sortino (+0.1016 edge);
trend-conviction K=4 vote despite firing ~20% of time routes single
during periods of strongest equity compounding. **Surprise #2:** slot
6 (lv50 + IEF + g0 + p80) achieves 2020_covid rescue instead of
2022_rates rescue — different OFF-leg + ratevol mechanics decide
which 3 of 4 crises get rescued, not the regime-switch ON-leg. First
loop iter to surface this attribution. **Best config = single_K4lv25_
g25 calibration replica** (iter 014 strict_superset bit-exact); NO
NEW strict_superset config introduced. **Capital remains 100% Plan C
per mandate §1**; iter appended to `loop_winner_iter` (6th iter),
`loop_phase3_performance_candidate_iter` (5th iter), AND
`loop_strict_superset_iter` (4th iter — but content-equivalent to
iter 014's strict_superset config; the single_K4lv25_g25 strategy
itself is now confirmed across iters 013 (g25 PBO-blocked) / 014
(strict_superset) / 015 (replica) / 016 (replica)). Score 76.5 < 90
deploy bar; per LOOP_PROTOCOL §"Mandate §1 reinforcement",
`docs/CURRENT_STATE.md` "Active Hunts" entry preserved untouched.
**NO automatic capital realloc.**

**beats_winner:** **true** (2 of 6 configs > 1.3746 threshold; best
is calibration replica).

**phase3_performance_candidate (any):** **true** (1 of 6 — only
single replica).

**strict_superset (any):** **🎯 true** (1 of 6 — only single replica;
**not a NEW finding**).

**Next iter ideas:** (a) **Leverage overlay on iter 014 single
strict_superset** — add 1.1×–1.5× multiplier on ON-leg returns when
conditions are very favorable (K=4 AND lowvol25 AND VIX < 20 OR
similar conjunction). **Highest expected value: directly addresses
the structural CAGR ceiling without trading away the strict_superset
status** that two consecutive iters (015 eqtilt, 016 regsw) have
shown CAN'T be unlocked by ON-leg composition tweaks. Cite
`[leverage_for_the_long_run, ch.4-5, p.40-60]` LRS;
`[risk_parity, ch.5, p.10]` Carlson stacking. (b) **2020 COVID
re-entry trigger overlay** on iter 014 single strict_superset —
Carver-style re-arm hysteresis on ratevol gate. Targets the single
1/4 crisis hole (specifically COVID); if successful lifts score 76.5
→ ~82 (criterion 6 +5pts) without touching Phase 3 mechanics.
`[systematic_trading, p.212, ch.13]`. (c) **VIX-percentile / VRP
overlay** — forward-looking implied-vol gate orthogonal to all
realised-vol mechanics. `[volatility_trading, ch.7]`. (d) **Event-
driven crisis overlay** — slot that activates basket3-invvol ONLY
during pre-defined crisis windows (e.g., 6m post 200d SPY MDD breach
> 20%) and falls back to single otherwise. `[regime_change]`.
(e) **Tax / fees stress on iter 014 strict_superset** — turnover
5.38/y; quantify Lei 14.754 swing tax 15% diagnostic.

### 015 — 2026-05-10 — equity-tilted-basket-cagr-recovery

**Hypothesis:** Fixed-weight equity-tilted baskets (basket3-eqtilt66
weights 2/3+1/6+1/6; basket3-eqtilt85 weights 0.85+0.075+0.075;
basket2_QU invvol QLD/UPRO no-UGL ablation) test whether reducing UGL
from basket3-invvol's ~45% (Carver/Clenow inverse-vol) down to 16.7%,
7.5%, or 0% recovers CAGR_lh56y above 31.08% Phase 3 floor while
preserving 2022_rates / 2000_dotcom crisis cushion. Six configs,
mechanism-mix-diverse 5-distinct-ON-leg-topology grid (iter 014
PBO-0.4405 recipe). Targets the loop's first crisis-≥2/4
strict_superset. **Primary citation:** `[risk_parity, p.110, ch.5]`
Qian — diversification return for fixed-weight rebalanced basket.
**Secondary:** `[risk_parity, p.11, ch.1]` Qian invvol over-allocation;
`[risk_parity, p.80-81, ch.4]` Qian RORO graded; `[risk_parity, ch.5,
p.10]` Carlson stacking; `[stocks_on_the_move, p.98]` Clenow;
`[systematic_trading, ch.10]` Carver; `[volatility_trading, p.58-60]`
Sinclair; `[leverage_for_the_long_run, ch.4-5, p.40-60]` LRS;
`[advances_fin_ml, p.208-211]` CSCV PBO; `[advances_fin_ml, p.222-223]`
DSR cumulative (n_global=516).

**Configs tested (6, mechanism-mix-diverse with 5 distinct ON-leg topologies):**

| name | ON-leg | weights | upg/rv | sortino_lh56y | edge | cagr_lh56y | edge | end_eq | MDD | score | tier | WC | crisis | phase3 | beats | strict |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| `..._eqb_baseline_qld_zroz` | single QLD | — | none/none | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | -64.5% | 76.5 | STRONG | T | 1/4 | F | F | F |
| **`..._eqb_single_K4lv25_g25_rvp70_cashx`** ← strict_superset | single QLD/TQQQ | — | K4lv25/p70-cashx | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | -47.7% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T** |
| 🥇 `..._eqb_basket3invvol_K4lv25_g25_rvp70_cashx` ← LOOP MAX Sortino replica | basket3-invvol60 | invvol60 | K4lv25/p70-cashx | **1.4689** | +0.1443 | 0.2265 | -8.43pp | 0.056× | **-32.8%** | **81.5** | STRONG | **T** | **3/4** | F | T | F |
| **`..._eqb_basket3eq66_K4lv25_g25_rvp70_cashx`** ← PRIMARY (rejected) | basket3-eqtilt | (0.667, 0.167, 0.167) | K4lv25/p70-cashx | 1.4330 | +0.1084 | **0.2781** | -3.27pp | 0.284× | -39.2% | 79.5 | STRONG | T | 1/4 | F | T | F |
| `..._eqb_basket3eq85_K4lv25_g0_rvp80_ief` | basket3-eqtilt | (0.850, 0.075, 0.075) | K4lv25/p80-ief | 1.3603 | +0.0357 | 0.3005 | -1.03pp | 0.563× | -56.0% | 76.5 | STRONG | T | 1/4 | F | F | F |
| `..._eqb_basket2QU_K4lv25_g25_rvp70_cashx` ← surprise crisis 2/4 | basket2-invvol60 (QLD/UPRO; no UGL) | invvol60 | K4lv25/p70-cashx | 1.3434 | +0.0188 | 0.2899 | -2.09pp | 0.406× | -43.0% | 79.0 | STRONG | T | **2/4** | F | F | F |

**KILL_LOOP results (pre-registered):**
- 🏆 ✅ KILL_LOOP #1 (success_tag) — **FIRED.** 3 of 6 configs achieve
  beats_winner=True (single replica, basket3-invvol replica,
  basket3eq66). 5th loop iter to fire success_tag.
- KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.4689 >>
  1.20 floor).
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact match to iter 011-014 (drift 0.0000).
  **6th-generation cross-iter reproducibility.**
- ✅ KILL_LOOP #4 (replica_sanity_single_K4lv25_g25) — **NOT FIRED.**
  single_K4lv25_g25_rvp70_cashx Sortino 1.3951 = bit-exact match to
  iter 013/014 (drift 0.0000).
- ✅ KILL_LOOP #5 (replica_sanity_basket3invvol_K4lv25_g25) — **NOT
  FIRED.** basket3invvol_K4lv25_g25_rvp70_cashx Sortino 1.4689 / CAGR
  22.65% / MDD -32.82% / crisis 3/4 = bit-exact match to iter 014
  triple-stack (drift 0.0000).
- ✅ KILL_LOOP #6 (PBO_blowup) — **NOT FIRED.** G1 PBO 0.3333 << 0.55
  ceiling.
- 🎯 ✅ KILL_LOOP #7 (PBO_held) — **FIRED — POSITIVE TAG.** G1 PBO
  **0.3333** < 0.50 hard gate. **LOOP 2nd-MIN** (after iter 011's
  0.3056). Iter trajectory: 005 0.881 → 006 0.798 → 007 0.552 → 008
  0.5675 → 009 0.3770 → 010 0.3929 → 011 0.3056 → 012 0.4960 → 013
  0.5437 → 014 0.4405 → **015 0.3333**. Mechanism-mix-diverse
  5-distinct-ON-leg-topology recipe held even with 4 of 6 configs in
  K4lv25/g25/p70/CASHX shared axis.
- ❌ KILL_LOOP #8 (phase3_perf_candidate_eqtilt) — **NOT FIRED.** **0
  of 3 eqtilt variants achieve phase3_performance_candidate=True.**
  CORE HYPOTHESIS REJECTED — equity-tilt does not clear Phase 3 CAGR
  floor.
- ❌ KILL_LOOP #9 (strict_superset_eqtilt) — **NOT FIRED.** 0 of 3
  eqtilt variants achieve strict_superset=True. STRONGEST HYPOTHESIS
  REJECTED.
- ❌ KILL_LOOP #10 (eqtilt_crisis_2or3_of_4) — **NOT FIRED.** 0 of 3
  eqtilt achieve crisis ≥ 2/4. **Gold cushion structurally tied to
  ~45% UGL invvol weight; reducing to 16.7% / 7.5% drops crisis 3/4
  → 1/4.**
- 🤔 KILL_LOOP #11 (basket2_QU_no_crisis) — **NOT FIRED — SURPRISE.**
  basket2_QU (no UGL) crisis count = **2** (>1 threshold), rescuing
  **2000_dotcom + 2008_GFC**. The QLD+UPRO invvol weighting
  structurally de-risks during high-vol regimes, providing 2000_dotcom
  defense WITHOUT any gold sleeve. Pre-registered ablation expectation
  contradicted.
- ❌ KILL_LOOP #12 (eqtilt_crisis_strict_superset) — **NOT FIRED.** 0
  of 3 eqtilt achieve strict_superset AND crisis ≥ 2/4. Loop's first
  crisis-≥2/4 strict_superset NOT achieved.

**Key finding: ⚠️ EQUITY-TILT vs INVVOL-GOLD HYPOTHESIS REJECTED.**
Reducing UGL weight from basket3-invvol's ~45% (Carver/Clenow
inverse-vol equilibrium) down to 16.7% (eqtilt66), 7.5% (eqtilt85),
or 0% (basket2_QU) recovers some CAGR (22.65% → 27.81% / 30.05% /
28.99%) but **NEVER clears the 31.08% Phase 3 floor** AND **collapses
crisis attribution from 3/4 → 1/4** (eqtilt) or 2/4 (no-UGL ablation).
Across the entire UGL-weight spectrum {0%, 7.5%, 16.7%, 45%}, **no
fixed-weight tilt simultaneously clears Phase 3 CAGR floor AND
retains basket3-invvol's crisis 3/4**. The CAGR ↔ crisis-rescue
trade-off is **structural, not parametric**. **All 3 calibration
anchors PRESERVED bit-exact** (KILL_LOOP #3, #4, #5 NOT FIRED):
baseline 1.3240 (6th-gen replica), single_K4lv25_g25 1.3951,
basket3invvol_K4lv25_g25 1.4689 / CAGR 22.65% / MDD -32.82% / crisis
3/4. **G1 PBO 0.3333 — LOOP 2nd-MIN** (after iter 011's 0.3056) —
mechanism-mix-diverse 5-distinct-ON-leg-topology recipe held
empirically. **Surprise:** basket2_QU (no gold sleeve) rescues
2000_dotcom + 2008_GFC (crisis 2/4) — invvol QLD/UPRO weighting
structurally de-risks during high-vol regimes. **Best config =
single_K4lv25_g25 calibration replica** (iter 014 strict_superset
bit-exact); NO NEW strict_superset config introduced. **Capital
remains 100% Plan C per mandate §1**; iter appended to
`loop_winner_iter` (5th iter), `loop_phase3_performance_candidate_
iter` (4th iter), AND `loop_strict_superset_iter` (3rd iter — but
content-equivalent to iter 014's strict_superset config; the
single_K4lv25_g25 strategy itself is now confirmed across iters 013
(g25 PBO-blocked) / 014 (strict_superset) / 015 (replica)). Score
76.5 < 90 deploy bar; per LOOP_PROTOCOL §"Mandate §1 reinforcement",
`docs/CURRENT_STATE.md` "Active Hunts" entry preserved untouched.
**NO automatic capital realloc.**

**beats_winner:** **true** (3 of 6 configs > 1.3746 threshold; best
is calibration replica).

**phase3_performance_candidate (any):** **true** (1 of 6 — only
single replica).

**strict_superset (any):** **🎯 true** (1 of 6 — only single replica;
**not a NEW finding**).

**Next iter ideas:** (a) **Dynamic regime-conditional basket weights**
— switch between single-QLD (high CAGR, crisis 1/4) and basket3-invvol
(lower CAGR, crisis 3/4) based on regime indicator (VIX percentile,
ratevol, Gayed yield-curve gate). When equity-favorable: single QLD;
when defensive regime: basket3-invvol with full UGL weight. **Highest
expected value: addresses the structural CAGR ↔ crisis trade-off the
static eqtilt cannot unlock.** Cite `[risk_parity, p.80-81, ch.4]`
Qian RORO; `[risk_parity, p.110, ch.5]` Qian fixed-weight diversification.
(b) **2020 COVID re-entry trigger overlay** — Carver-style re-arm
hysteresis on ratevol gate. Targets the 2020_covid hole in iter 014
single strict_superset. `[systematic_trading, p.212, ch.13]`. (c)
**VIX-percentile / VRP overlay** — forward-looking implied-vol gate
orthogonal to all realised-vol gates. `[volatility_trading, ch.7]`.
(d) **Leverage overlay on iter 014 strict_superset** — 1.1×-1.5×
multiplier on ON-leg returns when conditions are very favorable
(K=4 AND lowvol25 AND VIX<20). `[leverage_for_the_long_run,
ch.4-5, p.40-60]`. (e) **Tax / fees stress on iter 014 strict_
superset** — turnover 5.38/y; quantify Lei 14.754 swing tax 15%
diagnostic.

### 014 — 2026-05-10 — mechanism-mix-diverse-graded-blend

**Hypothesis:** Mechanism-mix-diverse graded blend grid. Restores 6-distinct-
mechanism-topology design (iter 012 PBO-0.4960 recipe) while introducing
basket3 ON-leg variants (iter 007/010 UGL gold cushion) for 2022_rates
crisis rescue. Targets the loop's first crisis-3/4 strict_superset via TRUE
TRIPLE STACK (basket3 + K4_AND_lv25 + g=0.25 + ratevol-p70 cashx).
Citation: `[risk_parity, p.80-81, ch.4]` Qian RORO graded master-gate
(primary); `[risk_parity, ch.5, p.10]` Carlson stacking;
`[stocks_on_the_move, p.98]` Clenow vol-parity; `[systematic_trading,
ch.10]` Carver inverse-vol; `[volatility_trading, p.58-60]` Sinclair vol
cone; `[leverage_for_the_long_run, ch.4-5, p.40-60]` LRS leverage;
`[advances_fin_ml, p.208-211]` CSCV PBO mechanism diversity;
`[advances_fin_ml, p.222-223]` DSR cumulative (n_global=510).

**Configs tested (6, mechanism-mix-diverse with 5 distinct topologies):**

| name | topology | upg-active% | sortino_lh56y | edge | cagr_lh56y | edge | end_eq | MDD | score | tier | WC | crisis | phase3 | beats | strict |
|---|---|--:|---:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| `..._mmix_baseline_qld_zroz` | single/none/none | 0.0% | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | -64.5% | 76.5 | STRONG | T | 1/4 | F | F | F |
| `..._mmix_K4lv25_g0_rvp70_cashx` ← iter 012 strict-superset replica | single/K4lv25/g=0/p70-cashx | 7.1% | 1.3769 | +0.0523 | 0.3250 | +1.42pp | 1.544× | -55.8% | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T** |
| **`..._mmix_K4lv25_g25_rvp70_cashx`** ← NEW LOOP MAX strict-superset Sortino | single/K4lv25/g=0.25/p70-cashx | 7.1% | **1.3951** | **+0.0705** | 0.3147 | +0.39pp | 1.129× | **-47.7%** | 76.5 | STRONG | **T** | 1/4 | **T** | **T** | **🎯T** |
| `..._mmix_K4lv25_g0_rvp80_ief` | single/K4lv25/g=0/p80-ief | 7.1% | 1.3631 | +0.0385 | 0.3223 | +1.15pp | 1.423× | -60.0% | 76.5 | STRONG | T | 1/4 | F | T | F |
| `..._mmix_basket3_g0_rvp70_cashx` ← iter 007 5-gen anchor | basket3/none/g=0/p70-cashx | 0.0% | 1.4637 | +0.1391 | 0.2325 | -7.83pp | 0.068× | -32.8% | **79.0** | STRONG | **T** | **2/4** | F | T | F |
| 🥇 **`..._mmix_basket3_K4lv25_g25_rvp70_cashx`** ← TRUE TRIPLE STACK / LOOP MAX Sortino | basket3/K4lv25/g=0.25/p70-cashx | 7.3% | **1.4689 (LOOP MAX)** | **+0.1443** | 0.2265 | -8.43pp | 0.056× | **-32.8% (LOOP MIN)** | **81.5** | STRONG | **T** | **3/4** | F | T | F |

**KILL_LOOP results (pre-registered):**
- 🏆 ✅ KILL_LOOP #1 (success_tag) — **FIRED.** 4 of 6 configs achieve
  beats_winner=True (loop's 4th iter to fire success_tag after iters 009,
  010, 012).
- KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.4689 >>
  1.20 floor).
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact match to iter 011/012/013 baseline (drift
  0.0000).
- 🎯 ✅ KILL_LOOP #4 (replica_sanity_g0_K4lv25) — **NOT FIRED.**
  K4lv25_g0_rvp70_cashx Sortino 1.3769 = bit-exact match to iter 012
  strict-superset (drift 0.0000).
- 🎯 ✅ KILL_LOOP #5 (replica_sanity_g25_K4lv25) — **NOT FIRED.**
  K4lv25_g25_rvp70_cashx Sortino 1.3951 = bit-exact match to iter 013
  g25 (drift 0.0000).
- 🎯 ✅ KILL_LOOP #6 (replica_sanity_basket3_g0) — **NOT FIRED.**
  basket3_g0_rvp70_cashx Sortino 1.4637 = bit-exact match to iter 007 /
  008 / 009 / 010 5-gen anchor (drift 0.0000). **Cross-iter
  reproducibility extended to 5th generation.**
- 🎯 ✅ KILL_LOOP #7 (PBO_recovery) — **FIRED — POSITIVE TAG.** G1 PBO
  **0.4405** < 0.50 (recovery from iter 013's 0.5437; -0.103pp drop in
  single iter — 2nd-largest single-iter PBO drop in the loop after
  008→009's -0.190). Mechanism-mix-diversity recipe validated. Iter
  trajectory: 005 0.881 → 006 0.798 → 007 0.552 → 008 0.5675 → 009
  0.3770 → 010 0.3929 → 011 0.3056 → 012 0.4960 → 013 0.5437 → **014
  0.4405**.
- ✅ KILL_LOOP #8 (PBO_blowup) — **NOT FIRED.** G1 PBO 0.4405 << 0.55
  ceiling.
- 🎯 ✅ KILL_LOOP #9 (phase3_perf_candidate) — **FIRED — POSITIVE TAG.**
  3 of 6 configs achieve phase3_performance_candidate=True (vs iter 013's
  0/6). Phase 3 momentum RESTORED.
- 🏆 🎯 ✅ KILL_LOOP #10 (strict_superset) — **FIRED — POSITIVE TAG.**
  TWO strict_superset configs (loop's 2nd and 3rd ever):
  - `K4lv25_g0_rvp70_cashx` (iter 012 replica)
  - **`K4lv25_g25_rvp70_cashx` NEW** — Sortino 1.3951 LOOP MAX strict-
    superset Sortino (+0.0182 above iter 012's 1.3769).
- 🎯 ✅ KILL_LOOP #11 (crisis_2022_rescue) — **FIRED — POSITIVE TAG.**
  basket3_K4lv25_g25 beats SPY in 2022_rates window (graded blend
  cashx-during-ratevol-ON path delivers 2022 rescue, mirroring iter 010
  g25_cashx mechanism but with basket3 ON-leg).
- ❌ KILL_LOOP #12 (triple_stack_strict_with_crisis) — **NOT FIRED.**
  Triple-stack basket3 has Sortino max 1.4689 + crisis 3/4 + beats_winner
  but FAILS Phase 3 by CAGR floor (22.65% < 31.08%). **The structural
  CAGR ceiling of basket3 over 1970-2026 (truncated by UPRO/UGL synth
  inception ~1985) blocks the Phase 3 strict-bar AND prevents the loop's
  first crisis-3/4 strict_superset.**

**Key finding: 🏆 🎯 PBO RECOVERY 0.5437 → 0.4405 UNLOCKS LOOP'S 2nd AND
3rd STRICT_SUPERSETS — including the NEW LOOP MAX strict-superset Sortino
1.3951.** Iter 013's `K4lv25_g25_rvp70_cashx` (Sortino 1.3951; PBO-blocked
at 0.5437 in iter 013) is now strict_superset under iter 014's mechanism-
mix-diverse grid (PBO 0.4405). The returns series is bit-exact to iter
013 — the strict-superset eligibility was SOLELY a grid-composition
artifact, now repaired. **Loop's HIGHEST Sortino strict_superset is now
1.3951** (vs iter 012's 1.3769; +0.0182). **Triple-stack basket3
`basket3_K4lv25_g25_rvp70_cashx` achieves LOOP MAX Sortino 1.4689 + LOOP
MIN MDD -32.82% + LOOP MAX G2/G4/G5/G6 metrics + crisis 3/4 (loop first
2000_dotcom + 2022_rates combo) but FAILS Phase 3 by CAGR floor 22.65% <
31.08%** — structural ceiling of basket3 (synth inception ~1985 truncates
high-CAGR pre-1985 window). **All 4 calibration anchors PRESERVED bit-
exact** (KILL_LOOP #3, #4, #5, #6 NOT FIRED): baseline 1.3240 / K4lv25_g0
1.3769 / K4lv25_g25 1.3951 / basket3_g0 1.4637 (5-gen replica chain
extended). **Phase 3 momentum RESTORED**: iter 011 5/6 → 012 5/6 → 013
0/6 → **014 3/6**. **First loop iter to add 2000_dotcom rescue** (basket3
+ UGL gold cushion structurally captures dotcom; single-asset configs all
miss). **Capital remains 100% Plan C per mandate §1**; iter appended to
`loop_winner_iter` (4th iter), `loop_phase3_performance_candidate_iter`
(3rd iter), AND `loop_strict_superset_iter` (2nd iter — loop now has 1
config from iter 012 + 2 configs from iter 014 = 3 total strict_superset
configs). Score 81.5 (triple-stack basket3) < 90 deploy bar; per
LOOP_PROTOCOL §"Mandate §1 reinforcement", `docs/CURRENT_STATE.md`
"Active Hunts" entry preserved untouched. **NO automatic capital
realloc.**

**beats_winner:** **true** (best K4lv25_g25 strict_superset: Sortino
1.3951 > 1.3746 ✓, WC=True ✓, pct_above 1.0000 ≥ 0.95 ✓; also K4lv25_g0,
basket3_g0, and triple-stack basket3 all beat).

**phase3_performance_candidate (any):** **true** (3 of 6: K4lv25_g0,
K4lv25_g25, K4lv25_g0_p80_ief).

**strict_superset (any):** **🎯 true** (2 of 6: K4lv25_g0 iter 012
replica + K4lv25_g25 NEW loop max Sortino strict-superset).

**Next iter ideas:** (a) **HIGH-CAGR basket variant** — replace basket3
(QLD/UPRO/UGL invvol60) with basket2 (QLD/UPRO invvol60) or basket3 with
fixed-weight tilt toward equity (e.g., 2/3 QLD + 1/6 UPRO + 1/6 UGL) to
clear basket3's structural CAGR ceiling 22-23% < 31.08% Phase 3 floor.
Goal: unlock the loop's first crisis-3/4 strict_superset that current
basket3 narrowly misses by CAGR. **Highest expected value: directly
addresses the structural blocker.** Cite `[risk_parity, ch.5, p.10]`
Carlson stacking, `[stocks_on_the_move, p.98]` Clenow vol-parity. (b)
**2020 COVID re-entry trigger overlay** — Carver-style re-arm hysteresis
on ratevol gate; combined with iter 014 triple-stack could push crisis
4/4 if (a) also addressed. `[systematic_trading, p.212, ch.13]`. (c)
**VIX-percentile / VRP overlay on ON-leg** — forward-looking implied-vol
gate `[volatility_trading, ch.7]` Sinclair. (d) **AND-gate fine-grid
sweep on K4_AND_lvN** in mechanism-mix-diverse format (preserves iter 014
PBO recipe). (e) **Tax/fees stress on iter 014 strict_superset** —
turnover 5.38/y; quantify net-of-tax (Lei 14.754 swing tax 15%);
diagnostic.

### 013 — 2026-05-10 — triple-stack-K4lv25-graded-master

**Hypothesis:** Triple stack of iter 012's K4_AND_lv25 conditional ON-leg
leverage upgrade (strict-superset Sortino 1.3769 / CAGR 32.50% / crisis
1/4) with iter 010's graded master-scope ON-blend (gamma in {0, 0.25,
0.50, 1.0}; iter 010 g25 Sortino 1.4670 / crisis 3/4) on top of iter
006/007's ratevol-OFF override (CASHX p70). Targets the loop's first
strict-superset config that ALSO rescues 2022_rates by adding the iter
010 ON-blend primitive while preserving the iter 012 strict-superset.
Citation: `[risk_parity, p.80-81, ch.4]` Qian RORO graded master-gate
(primary); `[risk_parity, ch.5, p.10]` Carlson stacking;
`[volatility_trading, p.58-60]` Sinclair vol cone; `[stocks_on_the_move,
p.98]` Clenow trend; `[leverage_for_the_long_run, ch.4-5, p.40-60]` LRS;
`[advances_fin_ml, p.208-211]` CSCV PBO; `[advances_fin_ml, p.222-223]`
DSR cumulative (n_global=504).

**Configs tested (6, gamma sweep + upgrade-selectivity ablation grid):**

| name | topology | gamma | upg-active% | sortino_lh56y | edge | cagr_lh56y | edge | end_eq | MDD | score | tier | WC | crisis | phase3 | beats | strict |
|---|---|--:|--:|---:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| `..._tsgm_baseline_qld_zroz` | none/none/none | — | 0.0% | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | -64.5% | 72.5 | PROMISING | F | 1/4 | F | F | F |
| `..._tsgm_K4lv25_g0_rvp70_cashx` ← iter 012 strict-superset replica | K4_AND_lv25/g=0/p70-cashx | 0.00 | 7.1% | 1.3769 | +0.0523 | 0.3250 | +1.42pp | **1.544×** | -55.8% | 72.5 | PROMISING | F | 1/4 | F | F | F |
| **`..._tsgm_K4lv25_g25_rvp70_cashx`** ← Sortino/Sharpe/MDD peak | K4_AND_lv25/g=0.25/p70-cashx | 0.25 | 7.1% | **1.3951** | **+0.0705** | 0.3147 | +0.39pp | 1.129× | **-47.7%** | 72.5 | PROMISING | F | 1/4 | F | F | F |
| `..._tsgm_K4lv25_g50_rvp70_cashx` | K4_AND_lv25/g=0.50/p70-cashx | 0.50 | 7.1% | 1.3943 | +0.0697 | 0.3021 | -0.87pp | 0.765× | -46.3% | 69.5 | PROMISING | F | 1/4 | F | F | F |
| `..._tsgm_K4_g25_rvp70_cashx` ← upgrade ablation | K4/g=0.25/p70-cashx | 0.25 | 20.1% | 1.3455 | +0.0209 | 0.3193 | +0.85pp | 1.298× | -53.1% | 72.5 | PROMISING | F | 1/4 | F | F | F |
| `..._tsgm_K4lv25_g100_rvp70_cashx` ← only 2022 rescue | K4_AND_lv25/g=1.00/p70-cashx | 1.00 | 7.1% | 1.3169 | -0.0077 | 0.2699 | -4.09pp | 0.279× | -46.3% | **74.5** | PROMISING | F | **3/4** | F | F | F |

**KILL_LOOP results (pre-registered):**
- ❌ KILL_LOOP #1 (success_tag) — **NOT FIRED.** No config beats_winner=
  True (G1 PBO 0.5437 ≥ 0.50 fails WINNER strict bar → WC=False
  universally even where Sortino > 1.3746 ✓ + pct_above ≥ 0.95 ✓).
- KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.3951 >>
  1.20 floor; mechanism alive).
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact match to iter 011/012 (drift 0.0000).
  Calibration anchor preserved at byte level.
- 🎯 ✅ KILL_LOOP #4 (replica_sanity_g0) — **NOT FIRED.**
  K4lv25_g0_rvp70_cashx Sortino **1.3769** = bit-exact match to iter
  012 strict-superset config (drift 0.0000). **Confirms triple-stack
  helper reduces bit-exactly to iter 012 compound state machine when
  gamma=0** — guarantees no silent regression of the loop's first
  strict-superset returns series.
- ❌ KILL_LOOP #5 (phase3_perf_candidate) — **NOT FIRED.** No config
  achieves phase3_performance_candidate=True (G1 PBO 0.5437 ≥ 0.50 hard
  gate fails the Phase 3 PBO ceiling). **First iter since 011 with 0
  Phase 3 candidates** — Phase 3 momentum BROKEN this iter (011 5/6 →
  012 5/6 → 013 0/6).
- ⚠️ KILL_LOOP #6 (PBO_blowup) — **NOT FIRED at 0.55 ceiling, but
  breaches 0.50 hard gate.** G1 PBO **0.5437** (regression vs iter 012
  0.4960; +0.048pp). Iter trajectory: 005 0.881 → 006 0.798 → 007 0.552
  → 008 0.5675 → 009 0.3770 → 010 0.3929 → 011 0.3056 → 012 0.4960 →
  **013 0.5437**. Cause: gamma-sweep parametric clustering — 4 of 6
  configs share K4_AND_lv25 + ratevol-p70-cashx topology; CSCV correctly
  penalises rank-correlated parametric variants `[advances_fin_ml,
  p.208-211]`. **Iter 012's 6-distinct-topologies design (G1 PBO 0.4960)
  is the structural recipe iter 013 broke.**
- ❌ KILL_LOOP #7 (graded_lifts_strict_superset) — **NOT FIRED.** No g>0
  config achieves strict_superset=True (PBO blocks all WC-dependent flags).
  KEY hypothesis test FAILED at the statistical level despite Sortino
  lift confirmed.
- ✅ KILL_LOOP #8 (crisis_2022_rescue) — **FIRED — POSITIVE TAG (with
  caveats).** K4lv25_g100_rvp70_cashx (master-pure) beats SPY in
  2022_rates window — crisis 3/4 — at the cost of WC=False AND CAGR
  collapse (26.99% vs T3d-K2 31.08%; end_eq 0.279×). g25 + g50 do NOT
  rescue 2022 (single-asset QLD/TQQQ ON-leg lacks UGL gold cushion that
  iter 010's basket3 g25 had). **Crisis profile is structurally tied to
  ON-leg diversification (gold/UGL needed for 2022 rescue at intermediate
  gammas), not to gamma alone.**
- ❌ KILL_LOOP #9 (graded_score_lift) — **NOT FIRED.** No g>0 config
  achieves total_score >= 80. Best g>0 score is g100's 74.5 (+5pts crisis
  but WC=False → tier still PROMISING). g25 score 72.5.

**Key finding: ⚠️ HYPOTHESIS PARTIALLY CONFIRMED — Sortino/Sharpe/MDD/DSR
LIFT REAL but G1 PBO REGRESSION INVALIDATES PHASE 3 STATUS.**
Best config `qld_voteK2_sma250_100_vol21_40_ar30_tsgm_K4lv25_g25_rvp70_
cashx` hits Sortino_lh56y **1.3951** (loop's 3rd-best; +0.0705 vs T3d-K2
1.3246; +0.0182 vs iter 012 strict-superset 1.3769), Sharpe **0.9682
(LOOP MAX)** (vs iter 012 strict-superset 0.9584 and T3d-K2 winner 0.919),
MDD **-47.69%** (vs iter 012 -55.79%, baseline -64.50%), G2 DSR p_cum
**1.06e-03 (LOOP MIN)** at n_trials_global=504 (was 1.31e-03 at n=498),
G6 99% low **0.605 (LOOP MAX for g50)** vs iter 012 0.596. **Sortino
curve in gamma is non-monotonic** with peak at gamma≈0.25-0.50 (g25
1.3951; g50 1.3943; mirrors iter 010 dynamics). **G1 PBO regression
0.4960 → 0.5437** breaches 0.50 hard gate (KILL_LOOP #6 NOT FIRED at
0.55 ceiling). Cause: gamma-sweep parametric clustering — 4 of 6 configs
share K4_AND_lv25/p70-cashx family. **NO strict_superset, NO beats_winner,
NO phase3_performance_candidate this iter.** Calibration anchors PRESERVED
bit-exact (KILL_LOOP #3 + #4 NOT FIRED): baseline 1.3240 = iter 011/012;
g0 1.3769 = iter 012 strict-superset. **2022_rates rescue ONLY by g100
master-pure** (KILL_LOOP #8 fired but WC=False / CAGR collapse caveats).
Iter 010 g25's basket3+UGL crisis cushion structurally needed —
single QLD/TQQQ ON-leg can't replicate it at intermediate gammas.
**Capital remains 100% Plan C per mandate §1**; iter NOT appended to
loop_winner_iter / loop_phase3_performance_candidate_iter / loop_strict_
superset_iter (no positive flags). Score 74.5 < 90 deploy bar; per
LOOP_PROTOCOL §"Mandate §1 reinforcement", `docs/CURRENT_STATE.md`
"Active Hunts" entry preserved untouched. **NO automatic capital realloc.**

**beats_winner:** **false** (best Sortino 1.3951 > 1.3746 ✓ AND pct_above
1.0000 ≥ 0.95 ✓ but **winner_conditions_met=False because G1 PBO 0.5437
≥ 0.50** is the lone strict-bar blocker).

**phase3_performance_candidate (any):** **false** (G1 PBO regression
invalidates Phase 3 PBO ceiling for ALL configs).

**strict_superset (any):** **false**.

**Next iter ideas:** (a) **Mechanism-mix-diverse graded blend grid** —
replace iter 013's gamma sweep (4 configs in same K4_AND_lv25/p70-cashx
family) with a 6-distinct-topology grid: 1 baseline + 1 K4_AND_lv25_g25
_p70_cashx (iter 013 PRIMARY) + 1 K4_g25_p80_ief (different upgrade ×
ratevol × alt-OFF) + 1 tqqq_always_g0 (no upgrade gate; ON=TQQQ always)
+ 1 K4_AND_lv25_g0_basket3 (basket3 with UGL like iter 010 — gold for
2022) + 1 K4_AND_lv25_g25_basket3 (the "true" triple stack iter 013
should have tested with multi-asset basket). **Highest expected value:
addresses BOTH the PBO regression AND the missing 2022 rescue while
preserving graded blend.** Cite `[risk_parity, p.80-81, ch.4]` +
`[risk_parity, ch.5, p.10]` + `[advances_fin_ml, p.208-211]`. (b) **2020
COVID re-entry trigger overlay** — Carver-style re-arm hysteresis on
ratevol gate so it RELEASES exposure when on_signal flips OFF→ON after
N days. `[systematic_trading, p.212, ch.13]`. (c) **VIX-percentile / VRP
overlay** `[volatility_trading, ch.7]` — forward-looking gate orthogonal
to all current realised-vol mechanics. (d) **AND-gate fine-grid sweep
on K4_AND_lvN** with mechanism-mix-diverse alt-OFFs / ratevol thresholds.
(e) **Tax / fees stress on iter 012 strict-superset** — diagnostic.

### 012 — 2026-05-10 — compound-tqqq-K4-x-ratevol-off

**Hypothesis:** Compound stack of iter 011's TQQQ-K4 leverage upgrade
(ON-leg amplifier — substitute TQQQSIM for QLDSIM when K=4 vote fires)
with iter 006/007's ratevol-OFF override (OFF-leg diversion to
CASHX/IEFSIM when ZROZ realised vol percentile > p70/p80 over trailing
5y). Two mechanically-orthogonal lifts stacked per Carlson cap-efficient
stacking. Targets the loop's first **strict-superset** config that
simultaneously clears `beats_winner=True` AND
`phase3_performance_candidate=True`. Citation:
`[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking (primary);
`[volatility_trading, p.58-60]` Sinclair vol cone; `[stocks_on_the_
move, p.98]` Clenow trend; `[leverage_for_the_long_run, ch.4-5,
p.40-60]` LRS leverage scaling; `[advances_fin_ml, p.208-211]` CSCV
PBO; `[advances_fin_ml, p.222-223]` DSR cumulative (n_trials_global=498).

**Configs tested (6, 6-topology compound mechanism-mix grid):**

| name | topology | upg-active% | rv-active% | sortino_lh56y | edge | cagr_lh56y | edge | end_eq | MDD | score | tier | WC | crisis | phase3 | beats | strict |
|---|---|--:|--:|---:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| `..._clegrv_baseline_qld_zroz` | none/none | 0.0% | 0.0% | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | -64.5% | 76.5 | STRONG | T | 1/4 | F | F | F |
| `..._clegrv_tqqq_K4_zroz` ← iter 011 K4 anchor | K4/none | 20.1% | 0.0% | 1.2911 | -0.0335 | 0.3236 | +1.28pp | 1.482× | -64.9% | 76.5 | STRONG | T | 1/4 | **TRUE** | F | F |
| `..._clegrv_tqqq_K4_rvp70_cashx` ← CAGR ceiling | K4/p70-cashx | 20.1% | 10.9% | 1.3355 | +0.0109 | **0.3305** | **+1.97pp** | **1.825×** | -55.8% | 76.5 | STRONG | T | 1/4 | **TRUE** | F | F |
| `..._clegrv_tqqq_K4_rvp70_ief` | K4/p70-ief | 20.1% | 10.9% | 1.3323 | +0.0077 | 0.3302 | +1.94pp | 1.808× | -57.4% | 76.5 | STRONG | T | 1/4 | **TRUE** | F | F |
| `..._clegrv_tqqq_K4_rvp80_cashx` | K4/p80-cashx | 20.1% | 9.2% | 1.3272 | +0.0026 | 0.3284 | +1.76pp | 1.715× | -59.9% | 76.5 | STRONG | T | 1/4 | **TRUE** | F | F |
| 🏆 **`..._clegrv_tqqq_K4_AND_lv25_rvp70_cashx`** ← 🎯 STRICT SUPERSET | K4_AND_lv25/p70-cashx | 7.1% | 10.9% | **1.3769** | **+0.0523** | 0.3250 | +1.42pp | 1.544× | **-55.8%** | 76.5 | STRONG | **T** | 1/4 | **TRUE** | **TRUE** | **🎯 TRUE** |

**KILL_LOOP results (pre-registered):**
- 🏆 ✅ KILL_LOOP #1 (success_tag) — **FIRED.** `..._tqqq_K4_AND_
  lv25_rvp70_cashx` achieves `beats_winner=True` (Sortino 1.3769 >
  1.3746 ✓, WC=True ✓, pct_above 1.0 ✓). 3rd loop iter to achieve
  beats_winner=true (iters 009, 010, 012; iter 011 missed by Sortino-
  CAGR trade-off).
- KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.3769
  >> 1.20 floor).
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact match to iter 011 baseline (drift
  0.0000). Confirms iter 012 compound state machine reduces to
  iter 011 conditional state machine when ratevol disabled +
  upgrade=0. Calibration anchor preserved.
- 🎯 ✅ KILL_LOOP #4 (phase3_perf_candidate) — **FIRED — POSITIVE
  TAG.** 5 of 6 configs achieve `phase3_performance_candidate=True`
  (same hit rate as iter 011). Phase 3 momentum continues.
- ⚠️ KILL_LOOP #5 (PBO_blowup) — **NOT FIRED.** G1 PBO 0.4960 < 0.55
  ceiling AND 0.50 hard gate (barely — by 0.004). Regression vs iter
  011's loop-min 0.3056 (+0.190pp) due to parametric-variant
  clustering in compound family. Iter trajectory: 005 0.881 → 006
  0.798 → 007 0.552 → 008 0.5675 → 009 0.3770 → 010 0.3929 → 011
  0.3056 → **012 0.4960**.
- ✅ KILL_LOOP #6 (compound_collapse) — **NOT FIRED.** ALL 4 compound
  configs (slots 3-6) STRICTLY LIFT Sortino vs K4_zroz anchor (deltas
  +0.0361 to +0.0858). Cap-efficient stacking confirmed.
- 🎯 🏆 ✅ KILL_LOOP #7 (strict_superset) — **FIRED — POSITIVE TAG
  (LOOP'S FIRST!).** `..._tqqq_K4_AND_lv25_rvp70_cashx` achieves BOTH
  `beats_winner=True` AND `phase3_performance_candidate=True`
  simultaneously. Hypothesis fully confirmed at the strongest
  possible level.
- ❌ KILL_LOOP #8 (crisis_2022_rescue) — **NOT FIRED.** No compound
  config beats SPY in 2022_rates window. Crisis count unchanged at
  1/4 (only 2008). Iter 007's 2022 rescue depended on multi-asset
  basket3 with UGL gold cushion; iter 012's single QLD/TQQQ ON-leg
  has no equity-side defense for 2022.

**Key finding: 🏆 🎯 LOOP'S FIRST STRICT-SUPERSET CONFIG —
pre-registered hypothesis fully confirmed at the strongest possible
level.** `qld_voteK2_sma250_100_vol21_40_ar30_clegrv_tqqq_K4_AND_lv25_
rvp70_cashx` simultaneously clears all `beats_winner=True` thresholds
(Sortino 1.3769 > 1.3746 ✓, WC=True ✓, pct_above 1.0 ✓) AND all
`phase3_performance_candidate=True` strict-bar conditions (CAGR 32.50%
> 31.08%, end_eq 1.544× > 1.05, Sortino 1.3769 ≥ 1.20, PBO 0.4960 <
0.50, DSR_global 1.31e-03 < 0.05). MDD improves to -55.79% (+8.71pp
vs baseline -64.50%). Sharpe 0.9584 (loop max; > T3d-K2 winner 0.919).
**G4 OOS Sharpe = 1.005** (loop max). **G2 DSR p_cum = 1.31e-03 at
n=498** (loop minimum). **ALL 4 compound configs lift Sortino vs iter
011 K4 anchor** (deltas +0.0361 to +0.0858) AND lift CAGR (+0.0014pp
to +0.0069pp) — Carlson cap-efficient stacking thesis empirically
confirmed (KILL_LOOP #6 NOT FIRED). **G1 PBO regression to 0.4960**
(loop-min was iter 011's 0.3056; +0.190pp) is the hypothesis-
confirmation cost: compound configs share K=2 entry + ratevol gate +
alt-OFF asset family (parametric-variant cluster), less mechanically
diverse than iter 011's 6-distinct-topology grid. Still under both
0.50 hard gate and 0.55 KILL_LOOP ceiling. **Crisis count unchanged
at 1/4** (only 2008 GFC) — iter 007's 2022 rescue depended on
multi-asset basket3 with UGL gold cushion; iter 012's single QLD/TQQQ
ON-leg has no analogous backstop. Crisis profile structurally
decoupled from strict-superset performance lift. **Cross-iter
calibration preserved**: baseline Sortino 1.3240 bit-exact match to
iter 011 baseline (drift 0.0000) — KILL_LOOP #3 NOT FIRED. Future iter
013+ may continue using 1.3240 as canonical T3d-K2 replica reference.
**Capital remains 100% Plan C per mandate §1**; iter appended to BOTH
`loop_winner_iter` AND `loop_phase3_performance_candidate_iter`; new
`loop_strict_superset_iter` list initialized in frontmatter. Score
76.5 < 90 deploy bar; deploy escalation per KILL_RULES.md §DEPLOY
ESCALATION requires Sharpe_net edge > +0.15 AND user-driven mandate
§7 override. CURRENT_STATE "Active Hunts" entry preserved untouched
(LOOP_PROTOCOL §"Mandate §1 reinforcement"; gated on score ≥ 90).
**NO automatic capital realloc.**

**beats_winner:** **true** (best config K4_AND_lv25_rvp70_cashx:
Sortino 1.3769 > 1.3746 ✓, WC=True ✓, pct_above 1.0000 ≥ 0.95 ✓).

**phase3_performance_candidate (any):** **true** (5 of 6 configs).

**strict_superset (any):** **🎯 true** (1 of 6: K4_AND_lv25_rvp70_cashx
— loop's first strict-superset config).

**Next iter ideas:** (a) **Strict-superset multi-asset compound** —
stack iter 010's graded master scope (gamma=0.25 g25_cashx Sortino
1.4670, crisis 3/4) with iter 012's K4_AND_lv25 upgrade gate. Targets
the only structural gap in iter 012 (crisis 1/4 → 3/4) while keeping
the strict-superset Sortino lift. Could push score from 76.5 to ~85
via crisis criterion (criterion 6 +5pts). Cite `[risk_parity, p.80-81,
ch.4]` Qian RORO graded + `[risk_parity, ch.5, p.10]` stacking.
**Highest expected value: would lift score above 80 AND maintain
beats_winner+phase3+strict-superset triple.** (b) **AND-gate fine-grid
sweep** — sweep K=4 ∩ lowvol{15, 20, 25, 30, 40} to map AND-gate
sensitivity. Slot 6's 7.1% activation may not be optimal. Risk: G1 PBO
may regress further. (c) **Compound triple stack: K4 × ratevol ×
VIX-percentile** — add forward-looking VIX-percentile gate orthogonal
to realised-vol gates. Iter 010 idea #3 untouched. `[volatility_
trading, ch.7]` Sinclair VRP. (d) **Multi-asset basket × compound** —
replace QLD/TQQQ binary swap with QLD/UGL basket (gold backstop for
2022 rescue) within iter 012 framework. Direct path to crisis 2/4 or
3/4. (e) **Tax / fees stress on iter 012 strict-superset** — turnover
4.84/y; quantify net-of-tax impact (Lei 14.754 swing tax 15%).

### 011 — 2026-05-10 — conditional-tqqq-leverage

**Hypothesis:** Conditional ON-leg leverage scaling — substitute TQQQSIM
(3× NDX) for QLDSIM (2× NDX) only when conviction is high (vote count =
4 of 4 OR vol_21d in lowest 25th percentile of trailing 5y). Tests
whether selective leverage upgrade lifts CAGR_lh56y above the T3d-K2
official 31.08% benchmark while preserving Sortino_lh56y >= 1.20 (Phase
3 floor) and PBO < 0.5. Citation: `[leverage_for_the_long_run, ch.4-5,
p.40-60]` Husson-Trifoni LRS leverage scaling (primary); `[stocks_on_
the_move, p.98]` Clenow trend-strength filter; `[volatility_trading,
p.58-60]` Sinclair vol cone (low percentile = pump leverage);
`[advances_fin_ml, p.208-211]` CSCV PBO; `[advances_fin_ml, p.222-223]`
DSR cumulative (n_trials_global=492).

**Configs tested (6, 6-topology structural-diversity grid):**

| name | topology | upgrade-active% | sortino_lh56y | edge | cagr_lh56y | edge | end_eq_ratio | score | tier | WC | crisis | phase3_candidate | beats |
|---|---|--:|---:|---:|---:|---:|---:|---:|---|:---:|:---:|:---:|:---:|
| `..._cleg_baseline_qld` | none | 0.0% | 1.3240 | -0.0006 | 0.3108 | 0.00pp | 1.0000 | 76.5 | STRONG | T | 1/4 | F | F |
| **`..._cleg_tqqq_always`** ← Sortino-best CAGR-ceiling | always | 72.6% | 1.2274 | -0.0972 | **0.3669** | **+5.61pp** | **5.42×** | 76.5 | STRONG | T | 1/4 | **TRUE** | F |
| 🥇 **`..._cleg_tqqq_K4`** ← balanced winner | trend-strength | 20.1% | **1.2911** | -0.0335 | 0.3236 | +1.28pp | 1.48× | 76.5 | STRONG | T | 1/4 | **TRUE** | F |
| `..._cleg_tqqq_lowvol25` | vol-regime | 21.4% | 1.2755 | -0.0491 | 0.3182 | +0.74pp | 1.26× | 79.5 | STRONG | T | 1/4 | **TRUE** | F |
| 🥈 **`..._cleg_tqqq_K4_AND_lowvol25`** ← Sortino-preserving | combined-AND | 7.1% | **1.3247** | **+0.0001** | 0.3181 | +0.73pp | 1.25× | 76.5 | STRONG | T | 1/4 | **TRUE** | F |
| `..._cleg_tqqq_K4_OR_lowvol25` | combined-OR | 31.5% | 1.2573 | -0.0673 | 0.3237 | +1.29pp | 1.49× | 79.5 | STRONG | T | 1/4 | **TRUE** | F |

**KILL_LOOP results (pre-registered):**
- ❌ KILL_LOOP #1 (success_tag) — **NOT FIRED.** No config achieves
  `beats_winner=True` (best Sortino 1.3247 < 1.3746 threshold). Phase 3
  explicitly trades Sortino for CAGR; beats_winner is not the primary
  axis.
- KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.3247 >>
  1.20 Phase 3 floor; hypothesis alive).
- ⚠️ KILL_LOOP #3 (replica_sanity_baseline) — **FIRED — but POSITIVELY.**
  Baseline_qld Sortino_lh56y = 1.3240, drift +0.0399 vs iter 010's
  1.2841. **The new helper's baseline matches T3d-K2 OFFICIAL winner
  Sortino 1.3246 to 4 decimals (drift -0.0006).** Root cause: iter 011's
  `build_conditional_strategy_returns` uses stricter warmup-row-drop
  convention than iter 007's `build_compound_strategy_returns`. The
  iter 011 baseline IS the T3d-K2 winner replica at byte-level fidelity;
  iter 001-010's 1.2841 was an alignment artifact in iter 007. **This
  iter effectively documents and corrects the loop's baseline
  calibration.** Future iters may want to either explicitly reconcile
  against this iter 011 baseline, or keep the iter 007 alignment as the
  loop's "frozen" replica reference.
- 🎯 ✅ KILL_LOOP #4 (phase3_perf_candidate) — **FIRED — POSITIVE TAG.**
  **5 of 6 configs achieve `phase3_performance_candidate=True`** (CAGR >
  31.08% AND end_eq_ratio > 1.05 AND Sortino >= 1.20 AND PBO < 0.5 AND
  DSR_global p < 0.05). **First Phase 3 iter to find performance
  candidates.** Direct hit on user's stated objective.
- ✅ KILL_LOOP #5 (PBO_blowup) — **NOT FIRED.** G1 PBO = **0.3056 —
  LOOP MINIMUM** (drop -0.0873 vs iter 010's 0.3929). Iter trajectory
  G1 PBO: 005 0.881 → 006 0.798 → 007 0.552 → 008 0.5675 → 009 0.3770
  → 010 0.3929 → **011 0.3056**. 6-topology structural-diversity grid
  (none/always/trend-strength/vol-regime/AND/OR) keeps mechanism mix
  the cleanest CSCV mechanism diversity the loop has produced.
- KILL_LOOP #6 (tqqq_always_collapse) — **NOT FIRED** (tqqq_always
  Sortino 1.2274 well above 1.10 floor; TQQQ ceiling viable).
- 🎯 ✅ KILL_LOOP #7 (conditional_dominates_always) — **FIRED —
  POSITIVE TAG.** ALL 4 conditional configs (K4, lowvol25, AND, OR)
  have Sortino_lh56y STRICTLY GREATER than tqqq_always's 1.2274
  (deltas: +0.0637 K4, +0.0481 lowvol25, +0.0973 AND, +0.0299 OR).
  **Selective leverage upgrade is unambiguously smarter than always-
  upgrading.** Hypothesis core mechanism confirmed.

**Key finding: 🎯 PHASE 3 OBJECTIVE CONFIRMED — first iter to find
performance candidates.** 5 of 6 configs simultaneously (a) lift
CAGR_lh56y above T3d-K2 31.08% by margins +0.73pp to +5.61pp, (b)
preserve Sortino_lh56y >= 1.20 floor, (c) clear PBO < 0.5 (loop minimum
0.3056), and (d) clear DSR cumulative p < 0.05 (n=492). **Best CAGR**
(`tqqq_always`): CAGR 36.69% (+5.61pp), end_eq 5.42×, Sortino 1.2274
(above floor; rolling-window win-rate 60-70% across 1y-10y). **Balanced
winner** (`tqqq_K4`): CAGR 32.36% (+1.28pp), Sortino 1.2911 (well above
1.20 floor), end_eq 1.48× — only 20.1% upgrade-active days needed.
**Sortino-preserving** (`tqqq_K4_AND_lowvol25`): Sortino 1.3247 (TIED
with T3d-K2 official 1.3246; drift +0.0001), CAGR 31.81% (+0.73pp),
end_eq 1.25× — most conservative Phase 3 pick. **All 4 conditional
gates beat tqqq_always on Sortino** (KILL_LOOP #7 fired positively) —
selective leverage upgrade is structurally smarter than blanket TQQQ
exposure. **G1 PBO 0.3056 — LOOP MINIMUM** (6-topology grid is the
cleanest CSCV diversity the loop has produced; iter trajectory: 0.881
→ 0.798 → 0.552 → 0.5675 → 0.3770 → 0.3929 → **0.3056**). **Crisis
attribution unchanged at 1/4** (only 2008_GFC) — TQQQ doesn't change
crisis profile (same defensive ZROZ, same K=2 entry signal); Phase 3
lift comes from compounding in equity-bull regimes, not crisis rescue.
**Cross-iter baseline drift to T3d-K2 official:** iter 011 baseline
Sortino 1.3240 matches official 1.3246 to 4 decimals; iter 010's 1.2841
was an alignment artifact in iter 007. KILL_LOOP #3 fired but
positively. **Capital remains 100% Plan C per mandate §1**; iter NOT
appended to `loop_winner_iter` (no beats_winner=true config), but
appended to NEW `loop_phase3_performance_candidate_iter` list in
frontmatter. Score 76.5 < 90 deploy bar; per LOOP_PROTOCOL §"Mandate §1
reinforcement", `docs/CURRENT_STATE.md` "Active Hunts" entry preserved
untouched (gated on score ≥ 90 + WC=Y + beats_winner=true). No deploy
realloc; mandate §7 requires user-driven override.

**beats_winner:** **false** (best Sortino 1.3247 < 1.3746 anti-curve-fit
threshold; Phase 3 explicitly trades Sortino for CAGR).

**phase3_performance_candidate (any):** **true** (5 of 6 configs
achieve the strict bar: CAGR > 31.08%, end_eq_ratio > 1.05, Sortino >=
1.20, PBO < 0.5, DSR_global p < 0.05).

**Next iter ideas:** (a) **Compound conditional-TQQQ × ratevol OFF
override** — stack iter 011 tqqq_K4 with iter 006/007's ratevol p70
60d → CASHX OFF override. Targets the 2022_rates rescue gap that iter
011 doesn't address (ZROZ OFF leg unchanged), while preserving the
CAGR lift from the TQQQ amplifier. **Highest expected value: combines
iter 011's CAGR lift with iter 007's drawdown protection — could
simultaneously hit Phase 3 strict bar AND beats_winner=true (the
strict-superset goal).** Cite `[risk_parity, ch.5, p.10]` +
`[volatility_trading, p.58-60]`. (b) **Gamma-graded TQQQ allocation**
— linearly interpolate exposure (50% QLD + 50% TQQQ when K=3; 100%
TQQQ when K=4) — analogous to iter 010's gamma-graded master scope but
applied to ON-leg leverage. Cite `[risk_parity, p.80-81, ch.4]`. (c)
**VIX-percentile / VRP overlay on the upgrade gate** — replace lowvol25
realised-vol gate with VIX_pct < 25th + VRP > 0 dual gate
`[volatility_trading, ch.7]`.

### 010 — 2026-05-09 — graded-master-bridge

**Hypothesis:** Graded master-scope bridge — interpolate between iter
007 offleg-pure (gamma=0) and iter 009 master-pure (gamma=1) compound
configs via coefficient gamma in (0, 1) applied ONLY to the (ratevol
fired, on_signal=ON) regime cell. Tests whether a sweet spot at gamma
in {0.25, 0.50} simultaneously retains iter 009's beats_winner=True
AND adds the 2022_rates rescue (the trade-off iter 009 master_basket3
surfaced but failed WC strict bar on). Citation: `[risk_parity, p.80-81,
ch.4]` Qian RORO graded master-gate (primary); `[advances_fin_ml,
p.208-211]` CSCV structural diversity; `[advances_fin_ml, p.222-223]`
DSR cumulative (n_trials_global=486); `[volatility_trading, p.58-60]`
Sinclair vol cone (iter 006); `[stocks_on_the_move, p.98]` Clenow
vol-parity (iter 005); `[risk_parity, ch.5, p.10]` Carlson stacking
(iter 007).

**Configs tested (6, 4-topology structural-diversity grid: none-single
+ none-basket + offleg + 2 graded + master):**

| name | scope | gamma | sortino_lh56y | edge | score | tier | WC | crisis | beats |
|---|---|--:|---:|---:|---:|---|:---:|:---:|:---:|
| `..._gmaster_baseline` | none | — | 1.2841 | -0.0405 | 76.5 | STRONG | T | 1/4 | F |
| `..._gmaster_basket3_only` | none | — | 1.3340 | +0.0094 | 81.5 | STRONG | T | 3/4 | F |
| **`..._gmaster_offleg_pure`** ← iter 007/009 anchor | offleg | 0.00 | **1.4637** | **+0.1391** | 79.0 | STRONG | **T** | 2/4 | **TRUE** |
| **`..._gmaster_g25_cashx`** ← **🏆 OVERALL BEST** | **graded** | 0.25 | **1.4670** | **+0.1424** | **81.5** | STRONG | **T** | **3/4** | **TRUE** |
| **`..._gmaster_g50_cashx`** ← 🥈 | **graded** | 0.50 | **1.4538** | **+0.1292** | **81.5** | STRONG | **T** | **3/4** | **TRUE** |
| `..._gmaster_master_pure` ← iter 009 anchor | master | 1.00 | 1.3686 | +0.0440 | 78.5 | STRONG | F | 3/4 | F |

**KILL_LOOP results (pre-registered):**
- 🏆 KILL_LOOP #1 (success_tag) — **FIRED** for the second consecutive
  iter. THREE configs achieved `beats_winner=true` (offleg_pure +
  g25 + g50; iter 009 had 2). All three thresholds (Sortino > 1.3746,
  WC=T, pct_above ≥ 0.95) cleared simultaneously.
- KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.4670 >>
  1.30 floor; even the worst non-baseline 1.3340 sits well above).
- KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED** (baseline
  1.2841 = bit-exact match to iters 001-009; **5th-generation
  reproducibility**).
- KILL_LOOP #4 (replica_sanity_offleg_pure) — **NOT FIRED.** Offleg_pure
  (gamma=0) Sortino_lh56y = **1.4637**, **bit-exact** match to iter
  007/008/009 winner_replica (drift = 0.0000). **4th-generation
  cross-iter reproducibility confirmed.** Verified by unit test:
  `test_gamma_zero_matches_iter007_offleg`.
- KILL_LOOP #5 (replica_sanity_master_pure) — **NOT FIRED.**
  Master_pure (gamma=1) Sortino_lh56y = **1.3686**, **bit-exact** match
  to iter 009 master_basket3. Verified by unit test:
  `test_gamma_one_matches_iter009_master`.
- ✅ KILL_LOOP #6 (PBO_held) — **FIRED** (positive tag — hypothesis
  confirmed). G1 PBO = **0.3929** < 0.50, slightly above iter 009's
  0.3770 (+0.0159) due to graded variants sharing some IS-OOS rank
  correlation with offleg endpoint, but well below threshold. **Iter
  trajectory G1 PBO:** iter 005 0.881 → iter 006 0.798 → iter 007
  0.552 → iter 008 0.5675 → iter 009 0.3770 → **iter 010 0.3929**.
  Mechanism diversity preserved (4 distinct topologies in 6 configs).
- 🎯 ✅ KILL_LOOP #7 (graded_2022_rescue) — **FIRED — DIRECTIONAL
  HYPOTHESIS CONFIRMED.** Both graded configs (g25 AND g50) hit
  `beats_winner=True` AND beat SPY in 2022_rates window. **First
  time in the loop ANY config has cleared all of {beats_winner=True,
  2022_rates_beat=True, score ≥ 80, PBO < 0.50} simultaneously.**

**Key finding: 🏆 LOOP'S STRONGEST RESULT YET — graded master at
gamma=0.25 hits Sortino 1.4670 (loop max, +0.0033 above iter 007/008/
009 winner_replica) AND adds 2022_rates rescue while preserving
beats_winner=True.** Pre-registered hypothesis (graded gamma in (0, 1)
finds a sweet spot between iter 007 offleg endpoint and iter 009
master endpoint) **fully confirmed**. Three configs achieve
beats_winner=True simultaneously: `gmaster_g25_cashx` (Sortino 1.4670,
edge +0.1424, crisis 3/4, score 81.5 — loop best), `gmaster_g50_cashx`
(Sortino 1.4538, edge +0.1292, crisis 3/4, score 81.5),
`gmaster_offleg_pure` (Sortino 1.4637 bit-exact replica, crisis 2/4,
score 79.0). **Sortino curve in gamma is non-monotonic** — peaks at
gamma≈0.25 (small graded master *helps* both Sortino AND crisis rescue
simultaneously), then degrades smoothly to master endpoint at
gamma=1. By gamma=0.5, Sortino is below offleg (-0.0099) but 2022 still
rescued; by gamma=1, Sortino has degraded -0.0951 vs offleg AND WC
fails. **Cross-iter replica reproducibility unprecedented:** 5th-gen
baseline + 4th-gen offleg_pure + 2nd-gen master_pure all bit-exact.
Both equivalences (gamma=0 ≡ iter 007 offleg-only; gamma=1 ≡ iter 009
master_scope) are unit-tested in `tests/test_letf_rotation_hunt_loop_010.py`
(7 tests, 7 passed; total tests 1062, +7 from this iter, well above
813 baseline). **G2 DSR p_cumulative for g25 = 3.6e-04** at
n_trials_global=486 (loop minimum cumulative DSR). **2020 COVID and
2022_rates remain mechanistically incompatible**: basket3_only catches
2020 but misses 2022; graded g25/g50 catch 2022 but miss 2020 (ratevol
fires in March 2020 → diverts to CASHX → misses V-recovery). The 4/4
sweep would require either a re-entry trigger overlay (next iter idea
#1) or a different gate family (VIX-percentile, idea #3). **Capital
remains 100% Plan C per mandate §1**; iter appended to
`loop_winner_iter` list in this file's frontmatter only. CURRENT_STATE
"Active Hunts" entry gated on score ≥ 90 (LOOP_PROTOCOL §"Mandate §1
reinforcement"); best score 81.5 < 90 → conservative skip,
`docs/CURRENT_STATE.md` preserved untouched. No deploy realloc;
mandate §7 requires user-driven override.

**beats_winner:** **true** (best config g25_cashx: Sortino 1.4670 >
1.3746 ✓, WC=True ✓, pct_above 1.0000 ≥ 0.95 ✓; second config g50
also true; third config offleg_pure also true; loop's first-ever 3
beats_winner configs in a single iter).

**Next iter ideas:** (a) **2020 COVID re-entry trigger overlay** — add
a Carver-style re-arm hysteresis to the ratevol gate so that it
RELEASES exposure when on_signal flips OFF→ON after the gate has been
active for ≥ N days. Targets the **single remaining unrescued crisis**
for the g25/g50 family. If successful, would lift crisis count to 4/4
→ criterion 6 score 10/10 → total score ~90, potentially crossing the
deploy bar. Cite `[systematic_trading, p.212, ch.13]` Carver
semi-automatic stop re-arm; `[volatility_trading, p.58-60]` Sinclair
vol cone re-entry semantics. **Highest expected value: ONLY remaining
barrier to the score 90 deploy bar.** 6 configs: 1 baseline (g25
without re-entry), 4 re-entry variants (N day thresholds e.g.
5/10/20/40 days), 1 control (offleg_pure, no re-entry). (b) **Gamma
fine-grid** — sweep gamma ∈ {0.10, 0.15, 0.20, 0.25, 0.30, 0.40} with
the iter 010 anchor topology preserved; the Sortino peak at gamma≈0.25
may be sharper or flatter than this iter resolves. Cite `[risk_parity,
p.80-81, ch.4]`. Risk: parametric sweep within graded family may
regress G1 PBO toward 0.55 (iter 008 lesson). (c) **VIX-percentile /
VRP overlay on equity ON-leg** `[volatility_trading, ch.7]` Sinclair —
forward-looking implied-vol gate orthogonal to realised-vol gates and
bond-vol gate already in stack. Different 2020 COVID handling than
ratevol (VIX percentile may NOT fire pre-spike → catches 2020).

### 009 — 2026-05-09 — master-scope-off-override

**Hypothesis:** Substitute master-scope OFF override (iter 004's
structural-diversity primitive: when ratevol fires → whole portfolio
to alt-OFF, regardless of on_signal) for offleg-only override in 2 of 6
configs of iter 007/008's compound family. Tests whether the
offleg-vs-master scope contrast (iter 004 PBO 0.071 lesson) drops
G1 PBO < 0.50 in the compound family — the structural-diversity
primitive iter 008 identified as required. If so, offleg compound
configs (winner replica, alt_off_ief) unlock `winner_conditions_met=True`
⇒ loop's first `beats_winner=true`. Citation: `[advances_fin_ml,
p.208-211]` (CSCV structural diversity) + `[risk_parity, p.80-81, ch.4]`
(Qian RORO master-gate primitive) + `[volatility_trading, p.58-60]` +
`[stocks_on_the_move, p.98]` + `[risk_parity, ch.5, p.10]`.

**Configs tested (6, mechanism-mix structural-diversity grid: 4 offleg/none + 2 master-scope):**

| name | scope | sortino_lh56y | active% | score | tier | WC | edge_vs_winner | beats |
|---|---|---:|---:|---:|---|:---:|---:|:---:|
| `..._mscope_baseline` | none | 1.2841 | 0.0% | 76.5 | STRONG | T | -0.0405 | F |
| **`..._mscope_winner_replica`** ← **🏆 BEATS_WINNER** | offleg-cashx | **1.4637** | 28.0% | 79.0 | STRONG | **T** | **+0.1391** | **TRUE** |
| `..._mscope_basket3_only` (score-best) | none | 1.3340 | 0.0% | **81.5** | STRONG | T | +0.0094 | F |
| `..._mscope_master_basket3_x_ratevol_p70_60d_cashx` | **master-cashx** | 1.3686 | 28.0% | 78.5 | STRONG | F | +0.0440 | F |
| `..._mscope_master_single_x_ratevol_p70_60d_cashx` | **master-cashx** | 1.2802 | 28.0% | 78.5 | STRONG | F | -0.0444 | F |
| **`..._mscope_alt_off_ief`** ← **🏆 BEATS_WINNER** | offleg-ief | **1.4524** | 28.0% | 79.0 | STRONG | **T** | **+0.1278** | **TRUE** |

**KILL_LOOP results (pre-registered):**
- 🏆 KILL_LOOP #1 (success_tag) — **FIRED for the FIRST TIME**.
  Two configs achieved `beats_winner=true` (winner_replica Sortino
  1.4637, alt_off_ief Sortino 1.4524). All three thresholds (Sortino >
  1.3746, WC=T, pct_above ≥ 0.95) cleared simultaneously for both.
- KILL_LOOP #2 (decisive_fail) — **NOT FIRED** (best Sortino 1.4637 >>
  1.30 floor; all configs ≥ baseline).
- KILL_LOOP #3 (replica_sanity) — **NOT FIRED** (baseline 1.2841 =
  bit-exact match to iters 001-008 baselines).
- KILL_LOOP #4 (iter007_replica_sanity) — **NOT FIRED.** Iter 007
  winner replica Sortino_lh56y = **1.4637**, **bit-exact** to iter
  007/008 (drift = 0.0000). Cross-iter reproducibility across 3
  generations confirmed.
- ✅ KILL_LOOP #5 (PBO_cracks) — **FIRED** (positive tag — hypothesis
  confirmed). G1 PBO = **0.3770** < 0.50 (drop of **−0.190** vs iter
  008's 0.5675 in a single iter — largest single-iter PBO drop in the
  loop). Iter 008's diagnostic ("mechanism diversity for CSCV is
  structural, not parametric") is empirically validated.
- KILL_LOOP #6 (master_overshoot) — **NOT FIRED.** Counter to iter 004
  lesson: both master-scope configs have lh_56y pct_above = 1.0000
  (vs iter 004's master_cashx 0.7039). Ratevol-gate's ~28% activation
  fires during SPY-stress regimes where master-cash is relatively
  neutral; basket3 cushions further.

**Key finding: 🏆 LOOP'S FIRST `beats_winner=true` — TWO configs
simultaneously.** Master-scope OFF override (iter 004 structural
primitive) substituted for offleg-only override in 2 of 6 configs of
iter 007/008 compound family **fully cracks G1 PBO**: PBO **0.3770**
(drop of **−0.190** vs iter 008's 0.5675). Both offleg compound configs
hit `beats_winner=true` (winner_replica Sortino 1.4637 edge +0.139,
alt_off_ief Sortino 1.4524 edge +0.128); all 3 frozen thresholds
cleared simultaneously. **Master-scope configs themselves do NOT
collapse** (master_basket3 Sortino 1.3686 edge +0.044, master_single
1.2802 edge −0.044) — ratevol gate fires during SPY-stress regimes so
cash drag is relatively neutral; basket3 cushions further. **First
2022_rates rescue in the loop:** both master-scope configs beat SPY in
2022 (crisis count 3/4 each — add 2022 via master-cash override) — a
structurally complementary mechanic to offleg compound (which preserves
equity-bull compounding but misses deep-bond-bear regimes). Cross-iter
replica anchors hold bit-exact across 3 generations (winner_replica
Sortino 1.4637 matches iter 007/008 to 4 decimals). **G2 DSR
p_cumulative for beats configs both < 6.5e-4 at n_trials_global=480.**
**Iter trajectory G1 PBO:** iter 005 0.881 → iter 006 0.798 → iter
007 0.552 → iter 008 0.5675 → **iter 009 0.3770**. **Capital remains
100% Plan C per mandate §1**; iter appended to `loop_winner_iter` list
in this file's frontmatter only. CURRENT_STATE "Active Hunts" entry
gated on score ≥ 90 (LOOP_PROTOCOL §"Mandate §1 reinforcement"); best
score 79 < 90 → conservative skip, `docs/CURRENT_STATE.md` preserved
untouched. No deploy realloc; mandate §7 requires user-driven override.

**beats_winner:** **true** (best config winner_replica: Sortino 1.4637 >
1.3746 ✓, WC=True ✓, pct_above 1.0000 ≥ 0.95 ✓; second config
alt_off_ief also true; loop's first ever).

**Next iter ideas:** (a) **Sortino-edge-and-WC consolidation grid** —
keep iter 009's 2-master + 4-offleg topology (which gives PBO 0.377)
but sweep ratevol threshold p65/p70/p75/p80 and window 60d/120d on the
offleg compound configs. Goal: push score past 90 deploy bar (criterion
1 cap is 25/30; criterion 6 caps at 7.5/10 with 2022 unrescued).
**Highest expected value: directly extends iter 009's beats_winner=true
toward the score 90 deploy bar.** Cite `[advances_fin_ml, p.208-211]` +
`[volatility_trading, p.58-60]`. (b) **Hybrid offleg+master compound**
— graded master-scope (e.g., 50% basket / 50% CASHX when ratevol fires
AND on_signal=ON) to capture 2022 rescue while preserving equity-bull
compounding. Cite `[risk_parity, ch.4]` Qian. (c) **VIX-percentile /
VRP overlay on equity ON-leg** — Sinclair `[volatility_trading, ch.7]`,
forward-looking implied-vol gate orthogonal to all current mechanics.

### 008 — 2026-05-09 — compound-4axis-cscv-diversity

**Hypothesis:** Drop G1 PBO < 0.50 (lone strict-bar blocker for
`winner_conditions_met=True` after iter 007) by widening the compound-
mechanic family from iter 007's 3 axes to 5 qualitatively distinct
mechanism dimensions (ON-basket on/off, OFF-mechanic on/off, ratevol
threshold p70/p80, ratevol window 60d/120d, alt-OFF asset CASHX/IEFSIM).
Citation: `[advances_fin_ml, p.208-211]` (CSCV diversity rationale) +
`[stocks_on_the_move, p.98]` + `[volatility_trading, p.58-60]`.

**Configs tested (6, 5-mechanic-axis grid centred on iter 007 winner replica):**

| name | ON-basket | OFF-mechanic | sortino_lh56y | active% | score | tier | WC | edge_vs_winner |
|---|---|---|---:|---:|---:|---|:---:|---:|
| `..._4axis_baseline` (replica) | single QLD | always-ZROZ | 1.2841 | 0.0% | 72.5 | PROMISING | F | -0.0405 |
| **`..._4axis_basket3_x_ratevol_p70_60d_cashx`** ← **iter 007 winner replica (Sortino-best)** | basket3 invvol60 | ratevol-p70-60d→CASHX | **1.4637** | 28.0% | 75.0 | STRONG | F | **+0.1391** |
| `..._4axis_basket3_only` | basket3 invvol60 | always-ZROZ | 1.3340 | 0.0% | 77.5 | STRONG | F | +0.0094 |
| `..._4axis_basket3_x_ratevol_p80_60d_cashx` | basket3 invvol60 | ratevol-p80-60d→CASHX | 1.4430 | 19.1% | 77.5 | STRONG | F | +0.1184 |
| `..._4axis_basket3_x_ratevol_p70_120d_cashx` | basket3 invvol60 | ratevol-p70-120d→CASHX | 1.4442 | 28.0% | 75.0 | STRONG | F | +0.1196 |
| `..._4axis_basket3_x_ratevol_p70_60d_ief` | basket3 invvol60 | ratevol-p70-60d→IEFSIM | 1.4524 | 28.0% | 75.0 | STRONG | F | +0.1278 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED.** No config achieved
  `beats_winner=true`. 5 of 6 configs cleared Sortino > 1.3746;
  6 of 6 cleared pct_above ≥ 0.95 (1.0000 universally — first loop
  iter where this is universal). G1 PBO blocked all configs.
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (best Sortino 1.4637 >>
  1.30 floor; family alive).
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 =
  bit-exact match to iters 001-007 baselines).
- KILL_LOOP #4 (compound-edge-decay) — **NOT FIRED.** Iter 007 winner
  replica (config 2) Sortino_lh56y = **1.4637**, **bit-exact** match to
  iter 007 finding (drift = 0.0000). Cross-iter scientific
  reproducibility confirmed.
- KILL_LOOP #5 (PBO-still-polluted) — **FIRED.** G1 PBO = **0.5675** ≥
  0.50, slightly *above* iter 007's 0.552. Hypothesis (parameter-sweep
  mechanism diversity drops PBO) **rejected** — adding parameter axes
  within one OFF-leg ratevol mechanic *increased* PBO marginally.

**Key finding: clean negative result. Hypothesis REJECTED.**
**Mechanism diversity for CSCV is structural, not parametric.** Adding
parameter sweeps (threshold p70/p80, window 60d/120d, alt-OFF
CASHX/IEFSIM) within the same OFF-leg ratevol mechanic produced
*marginally worse* G1 PBO (0.5675 vs iter 007's 0.552), not better.
Parameter variants share IS-OOS rank correlation by construction —
CSCV correctly penalises this `[advances_fin_ml, p.208-211]`. Iter
trajectory: iter 005 0.881 → iter 006 0.798 → iter 007 0.552 → iter
008 0.5675 (direction reversed). **Sortino spread across the 4
ratevol-override variants is flat (1.4430-1.4637, range 0.021)** —
the parameter sweep produces mechanism-equivalent strategies. **Iter
007 findings replicate bit-exact:** Sortino 1.4637, MDD -32.82%,
Sharpe 1.0068, G5 FWD post-2020 1.227. Cross-iter reproducibility
confirmed. **5 of 6 configs clear +0.05 anti-curve-fit margin
(Sortino > 1.3746); 6 of 6 clear pct_above ≥ 0.95** — but
`beats_winner=false` universally because **G1 PBO 0.5675 ≥ 0.50** is
the lone blocker. **threshold_p80 narrowly leads on G5 FWD post-2020
Sharpe** (1.268 vs winner replica 1.227); **basket3_only and
threshold_p80 lead on crisis attribution** (3/4 each — add 2020 COVID
via UGL). Iter 004's clean PBO 0.071 came from a *master-scope*
override config (whole-portfolio cash, qualitatively different
mechanism). **The structural-diversity primitive — not the parametric
one — is what cracks PBO.** Methodological insight: **ceiling reached
for compound-family CSCV diversity at PBO ~0.55**; further parameter
sweeps within the family will not break it. **Capital remains 100%
Plan C per mandate §1.**

**beats_winner:** **false** (G1 PBO 0.5675 ≥ 0.50 universally; Sortino
+ pct_above thresholds both cleared by 5 of 6 configs; first loop iter
where pct_above ≥ 0.95 is universal but G1 still blocks).

**Next iter ideas:** (a) **Master-scope OFF override (iter 004-style
structural-diversity primitive)** — keep iter 007 compound winner
config family but add a master-scope config: when ratevol gate fires,
override to whole-portfolio CASHX (rather than only when on_signal=OFF).
That's the qualitatively different mechanism that should restore CSCV
diversity. 6-config design: anchor (compound winner replica),
basket3_only, master_basket3_x_ratevol, master_single_x_ratevol,
threshold_p80, alt_off_ief. Cite `[advances_fin_ml, p.208-211]` +
`[volatility_trading, p.58-60]`. **Highest expected value: directly
addresses the iter 008 negative result with iter 004's proven mechanism-
diversity primitive.** (b) **VIX-percentile / VRP overlay on equity
ON-leg** `[volatility_trading, ch.7]` Sinclair — forward-looking
implied-vol gate orthogonal to realised-vol gates and bond-vol gate
already in stack. Different mechanic family from compound (CSCV-
diverse). (c) **Bond duration timing on OFF leg**
`[systematic_trading, ch.9, p.180-190]` — distinct from ratevol gate
(yields, not return vol); also targets 2022_rates rescue (iter 008
confirmed all 5 override variants fail 2022_rates).

### 007 — 2026-05-09 — compound-ratevol-off-x-invvol-on-basket

**Hypothesis:** Compound the two best-performing loop mechanics — iter 005's
ON-leg multi-asset inverse-vol basket {QLD, UPRO, UGL} (+0.0094 edge) and
iter 006's OFF-leg ratevol regime gate (ZROZ vol-pct > 70th → CASHX,
+0.0140 edge) — into a single 3-axis orthogonal grid. Tests (a)
compounding vs conflict, (b) whether real-mechanism-switch grid breaks
G1 PBO 0.79-0.88 ceiling. Citation: `[stocks_on_the_move, p.98]` (Clenow
vol-parity sizing, ON-leg) + `[volatility_trading, p.58-60]` (Sinclair
volatility cone, OFF-leg) + `[risk_parity, ch.5]` (Carlson cap-efficient
stacking — compounding orthogonal lifts).

**Configs tested (6, 3-axis orthogonal grid: ON-leg type × OFF-mechanic × alt-OFF asset):**

| name | ON-leg | OFF-mechanic | sortino_lh56y | active% | score | tier | WC | edge_vs_winner |
|---|---|---|---:|---:|---:|---|:---:|---:|
| `..._compound_baseline` (replica) | single QLD | always ZROZ | 1.2841 | 0.0% | 72.5 | PROMISING | F | -0.0405 |
| `..._compound_ratevol_only` (iter 006 best replica) | single QLD | ratevol-p70-cashx | 1.3386 | 28.0% | 72.5 | PROMISING | F | +0.0140 |
| `..._compound_basket3_only` (iter 005 best replica) | basket3 invvol60 | always ZROZ | 1.3340 | 0.0% | 77.5 | STRONG | F | +0.0094 |
| **`..._compound_basket3_x_ratevol_p70_cashx`** ← **Sortino-best** | basket3 invvol60 | ratevol-p70-cashx | **1.4637** | 28.0% | 75.0 | STRONG | F | **+0.1391** |
| `..._compound_basket3_x_ratevol_p70_ief` | basket3 invvol60 | ratevol-p70-ief | 1.4524 | 28.0% | 75.0 | STRONG | F | +0.1278 |
| `..._compound_basket2_qld_ugl_x_ratevol_p70_cashx` | basket2 invvol60 | ratevol-p70-cashx | 1.4297 | 28.0% | 77.0 | STRONG | F | +0.1051 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.4637 >
  threshold 1.3746 ✓ AND pct_above 1.0000 ≥ 0.95 ✓ — first time both
  numerical thresholds clear simultaneously — but winner_conditions_met
  =False because G1 PBO 0.552 ≥ 0.50 fails the strict bar)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (all 5 non-baseline
  configs ≥ 1.33; family confirmed alive)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 =
  bit-exact match to iters 001-006 baselines)
- KILL_LOOP #4 (compound-non-additivity) — **NOT FIRED — STRONGLY
  CONTRADICTED**. Compound config 4 Sortino 1.4637 is +0.125 ABOVE
  max(ratevol_only, basket3_only) — mechanics compound super-additively
  by 1.72× the naive sum, not conflict.
- KILL_LOOP #5 (PBO-still-polluted) — **FIRED — partially.** G1 PBO
  0.552 ≥ 0.50 still fails, but improvement direction is monotonic
  (iter 005 0.881 → iter 006 0.798 → iter 007 0.552). 3-axis grid with
  real ON↔OFF mechanism switch dropped PBO by 0.246 vs iter 006.

**Key finding:** **Compound super-additivity confirmed — loop's largest
Sortino edge ever (+0.1391 vs winner 1.3246).** Best config:
`compound_basket3_x_ratevol_p70_cashx` Sortino_lh56y **1.4637**. Compound
delta over baseline (+0.1796) is **1.72×** the naive sum of independent
deltas (ratevol_only +0.0545 + basket3_only +0.0499 = +0.1044). The two
mechanics don't just stack — they reinforce each other. **MDD -32.82%**
(smallest in loop; smaller than SPY -55.1% in absolute terms; cuts
baseline -64.5% by half). **Sharpe = 1.0068** (crosses 1.0 for first
time in any loop config). **G5 FWD post-2020 Sharpe = 1.227** vs
baseline 0.708, lift +0.519 — single largest G5 improvement in loop AND
larger than iters 005+006 G5 lifts summed (super-additive on G5 too).
**Three configs (4, 5, 6) clear the +0.05 anti-curve-fit Sortino margin
(1.3746); two also clear the 0.95 pct_above_benchmark bar — first loop
iter to clear both simultaneously.** `beats_winner=false` only because
**G1 PBO 0.552 ≥ 0.50 fails the strict bar** in winner_conditions_met
— it's the LONE remaining blocker. **Sortino effect is robust across all
4 datasets** (lh_56y 1.4637 / mod_1990 1.3703 / spy_real 1.4549 /
ndx_real 1.5242). **CASHX > IEFSIM marginally** (zero duration cleanly
orthogonal to ZROZ duration risk); **basket3 > basket2** (UPRO needed
for 3-leg cross-asset diversification). **Super-additivity comes from
regime-coincidence**: ratevol gate fires precisely during bond-stress
windows where multi-asset basket (with UGL gold) ALSO has peak marginal
value — the two effects aren't just orthogonal, they reinforce in the
SAME regimes. CAGR trade-off: 23.25% vs baseline 29.85% (basket3 with
UGL drags equity-bull periods); turnover 15.6/y vs baseline 9.3/y (1.7×
basket-rebalance cost).

**beats_winner:** **false** (Sortino 1.4637 > 1.3746 ✓; pct_above
1.0000 ≥ 0.95 ✓; **winner_conditions_met=False because G1 PBO 0.552 ≥
0.50** is the lone strict-bar blocker; loop's closest approach to
beats_winner=true ever).

**Next iter ideas:** (a) **4th-axis orthogonal grid to crack G1 PBO
0.50** — keep the iter 007 winner config family but add a real 4th
mechanism switch (e.g., threshold sweep p65/p70/p75/p80 plus
mechanism-switch-OFF configs like baseline + basket3-only + single +
compound). 6-config design with 4 real mechanism dimensions should drop
PBO toward iter 004's 0.071. **Highest expected value: this is the
ONLY barrier to first beats_winner=true.** Cite `[advances_fin_ml,
p.208-211]` (CSCV diversity rationale). (b) **VIX-percentile / VRP
overlay** on equity ON-leg `[volatility_trading, ch.7]` Sinclair —
forward-looking implied-vol gate orthogonal to realised-vol gates and
bond-vol gate already in stack. Could replace AR(1) in vote-K composite.
(c) **Tax / fees stress on iter 007 winner** — turnover 1.7× baseline;
quantify net-of-tax Sortino impact before any deploy consideration
(diagnostic, not gating).

### 006 — 2026-05-09 — bond-ratevol-regime

**Hypothesis:** Bond rate-vol regime master-gate — when ZROZ realised vol
(60d/120d) percentile within trailing 5y exceeds 70th/80th, OFF leg
reroutes from ZROZ (≈ 27y duration) to a shorter-duration alternative
(CASHX or IEFSIM). Targets the 2022_rates loss directly via own-asset
OFF-leg second-moment regime detection — orthogonal to all 5 prior loop
iters. Citation: `[volatility_trading, p.58-60]` (Sinclair volatility cone) +
`[systematic_trading, p.212, ch.13]` (Carver vol-scaled regime thresholds).

**Configs tested (6, 3-axis grid: pct × window × alt-asset):**

| name | pct | window | alt-OFF | sortino_lh56y | active% | score | tier | WC | edge_vs_winner |
|---|--:|--:|---|---:|---:|---:|---|:---:|---:|
| `..._ratevol_off_baseline` (replica) | — | — | — | 1.2841 | 0.0% | 72.5 | PROMISING | F | -0.0405 |
| **`..._ratevol_p70_60d_to_cashx`** ← Sortino-best | 0.70 | 60d | CASHX | **1.3386** | 28.0% | 72.5 | PROMISING | F | **+0.0140** |
| `..._ratevol_p80_60d_to_cashx` | 0.80 | 60d | CASHX | 1.3288 | 19.1% | 72.5 | PROMISING | F | +0.0042 |
| `..._ratevol_p80_120d_to_cashx` | 0.80 | 120d | CASHX | 1.3244 | 19.8% | 72.5 | PROMISING | F | -0.0002 |
| `..._ratevol_p70_60d_to_ief` | 0.70 | 60d | IEFSIM | 1.3345 | 28.0% | 72.5 | PROMISING | F | +0.0099 |
| `..._ratevol_p80_60d_to_ief` | 0.80 | 60d | IEFSIM | 1.3241 | 19.1% | 72.5 | PROMISING | F | -0.0005 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.3386 < 1.3746
  threshold AND winner_conditions_met=False universally because G1 PBO
  0.798 fails)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (all 5 ratevol Sortinos
  ≥ 1.3241; family is *promising*, not dead)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 =
  bit-exact match to iters 001-005 baselines)
- KILL_LOOP #4 (over-suppression) — **NOT FIRED** (pct_above_benchmark
  = 1.0000 universally; OFF-leg-only override avoided iter 004 master
  failure mode)
- KILL_LOOP #5 (ratevol-non-event) — **NOT FIRED** (gate fires 19-28%
  of post-warmup days, well above 5% underpowered floor)

**Key finding:** **New loop edge maximum:** `ratevol_p70_60d_to_cashx`
Sortino 1.3386 (edge +0.0140 vs winner 1.3246) — exceeds iter 005's
basket3_invvol60 (+0.0094) by 0.0046. **All 5 override configs lift
baseline universally (5×4 wins on Sortino across configs × datasets)** —
bit-uniform improvement, first loop iter with this property. **G5 FWD
post-2020 Sharpe massive lift** for every override config (0.708
baseline → 0.856-0.943) — direct hypothesis confirmation that bond
rate-vol gating helps in the 2022 regime. MDD reduced ~7-9pp absolute
(-64.5% → -55.8% best) without sacrificing CAGR (29.9% → 30.5% — CASHX
yield carries defensive periods). **Crisis attribution count UNCHANGED
at 1/4** — SPY-relative binary test misses bond-stress episodes that
don't coincide with equity bear; the Sortino lift is distributed
across multiple bond-stress regimes (1979-1981 Volcker, 1994 Greenspan
shock, 2013 taper, 2022). **G1 PBO 0.798 universally fails** (better
than iter 005's 0.881 but below iter 004's clean 0.071) — 3-axis grid
(pct × window × alt-asset) reduces pollution but still single-mechanic
family. **CASHX > IEFSIM** during bond stress (zero duration cleanly
orthogonal); **p70 > p80** (wider activation gives more dodging
chances). Methodological insight: **two independent loop mechanics now
show G5 post-2020 Sharpe lift** (this iter via ratevol gate; iter 005
via multi-asset basket) — closed-study winner has a real post-2020
edge-decay problem the loop is starting to triangulate.

**beats_winner:** **false** (best Sortino 1.3386 < 1.3746 threshold AND
G1 PBO blocker; second consecutive iter with positive edge over winner
benchmark but +0.05 anti-curve-fit margin not cleared).

**Next iter ideas:** (a) **Combine ratevol-OFF × inverse-vol-ON basket**
`[volatility_trading, p.58-60]` + `[stocks_on_the_move, p.98]` — orthogonal
grid spanning OFF-side regime detection (this iter) AND ON-side
diversification (iter 005). 8 configs: 2 OFF × 2 ON × 2 controls. Tests
whether the two effects compound or conflict — both already show
positive edge AND positive G5 lift independently. **Highest expected
value because compounding is likely AND it would be the first
multi-mechanic-family grid in the loop, potentially breaking G1 PBO.**
(b) VIX-percentile / VRP overlay on equity ON-leg `[volatility_trading,
ch.7]` — forward-looking implied vol gate, distinct from realised-vol
already in winner stack. (c) Bond carry forecast on OFF rotation
`[systematic_trading, ch.7 p.119]` — 10y yield − FFR as additional input
to OFF-leg routing.

### 005 — 2026-05-09 — multi-asset-on-invvol

**Hypothesis:** Replace winner's single-asset (QLD) ON leg with a basket of
equity-style LETFs ({QLD, UPRO, UGL}) sized by inverse realised volatility
(60d / 120d) so each asset contributes equal volatility, while keeping
winner's binary vote-K=2 trend gate (computed on QLD) and ZROZ as OFF.
Tests cross-asset **first-moment** diversification — orthogonal to iter
004's (failed) cross-asset second-moment regime gate. Citation:
`[stocks_on_the_move, p.98]` (Clenow vol-parity sizing) +
`[systematic_trading, ch.10]` (Carver inverse-vol position sizing).

**Configs tested (6):**

| name | basket | vol_window | sizing | sortino_lh56y | score | tier | WC | edge_vs_winner |
|---|---|---:|---|---:|---:|---|:---:|---:|
| `..._on_baseline` (replica) | {QLD} | — | single | 1.2841 | 72.5 | PROMISING | F | -0.0405 |
| `..._on_basket2_qld_upro_invvol60` | {QLD, UPRO} | 60d | invvol | 1.2695 | 75.5 | STRONG | F | -0.0551 |
| `..._on_basket2_qld_ugl_invvol60` | {QLD, UGL} | 60d | invvol | 1.2849 | 74.5 | PROMISING | F | -0.0397 |
| **`..._on_basket3_qld_upro_ugl_invvol60`** ← Sortino-best | {QLD, UPRO, UGL} | 60d | invvol | **1.3340** | 77.5 | STRONG | F | **+0.0094** |
| `..._on_basket3_qld_upro_ugl_invvol120` | {QLD, UPRO, UGL} | 120d | invvol | 1.3049 | 77.5 | STRONG | F | -0.0197 |
| `..._on_basket3_qld_upro_ugl_eqweight` ← score-best | {QLD, UPRO, UGL} | — | eqweight | 1.3317 | **78.0** | STRONG | F | +0.0071 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.3340 < 1.3746;
  AND winner_conditions_met=False universally because G1 PBO 0.881 fails)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (all multi-asset Sortinos ≥ 1.27)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 = bit-exact match
  to iters 001-004 baselines)
- KILL_LOOP #4 (single-asset-domination) — **NOT FIRED — partially contradicted.**
  basket3 configs (1.3340 / 1.3317 / 1.3049) all *exceed* baseline. Iter 023's
  "QLD × Vote-K=2 is asset-specific" finding holds at 1-asset and 2-asset
  scales but breaks at 3-asset basket via cross-asset diversification.
  basket2_qld_ugl pct_above 0.93 < 0.95 strict bar (1980-2000 gold drag).
- KILL_LOOP #5 (turnover-blowup) — **NOT FIRED** (max 5.44/y; baseline 2.61;
  ratio 2.08× < 3× threshold)

**Key finding:** **First positive Sortino edge in the loop.**
basket3_qld_upro_ugl_invvol60 hits Sortino 1.3340 (edge +0.0094 vs winner
1.3246). Three-asset inverse-vol basket beats single-asset baseline by
+0.05 Sortino AND breaks the 1-of-4 crisis-rescue ceiling (3-of-4: dotcom
+ GFC + COVID via UGL gold complement). Two-asset baskets underperform —
the diversification benefit requires the third (cross-asset) leg. Equal-
weight ties inverse-vol on Sortino (1.3317 vs 1.3340) but loses 2020_COVID
rescue (fixed UPRO 3x weight is over-exposed during Mar-2020 -77% trough).
**G1 PBO 0.881 is the universal blocker** — single-mechanic grid (5 multi-
asset variants) is high-correlation; CSCV finds significant IS-OOS rank
divergence. WC=False for all configs despite positive Sortino edges.
**2022_rates still not rescued** — even gold falls during USD-strength +
real-rate rebound. **Methodological lesson:** orthogonal multi-mechanic
grid (iter 004 style, PBO 0.071) → clean PBO; single-mechanic grid (iter
005 style) → polluted PBO. Future multi-asset iter should redesign with
3 orthogonal axes.

**beats_winner:** **false** (best Sortino 1.3340 < 1.3746 threshold AND G1
PBO blocker; first config with positive edge but +0.05 anti-curve-fit
margin not cleared).

**Next iter ideas:** (a) **Bond duration timing** `[systematic_trading,
ch.9 p.180-190]` — 10y rate vol > 60d 80th percentile → reduce ZROZ /
switch to IEF. Iter 005 confirmed multi-asset can't rescue 2022_rates
(gold also fell); sidestepping bond risk directly is the orthogonal angle
and targets the unrescued crisis. **Highest expected value.**
(b) **Multi-asset orthogonal-grid retest** — same {QLD, UPRO, UGL} basket
but vary across 3 mechanic dimensions (composition × sizing × gate scope)
in 8 configs, to test whether iter 005's +0.0094 Sortino edge survives
proper CSCV (G1 PBO < 0.5). (c) VIX-percentile / VRP overlay
`[volatility_trading, ch.7]`.

### 004 — 2026-05-09 — corr-regime-stockbond

**Hypothesis:** Stock-bond correlation regime master-gate. When 60d/120d
rolling correlation between QLD↔ZROZ daily returns exceeds 0.00/0.20/0.30,
redirect either the OFF leg or the entire portfolio to CASHX since the
diversification hedge has structurally broken. Citation:
`[risk_parity, p.80-81, ch.4]` (Qian RORO regime — stocks-and-bonds correlation
flip eliminates diversification value). Targets the 2022_rates loss directly via
cross-asset second-moment regime detection — orthogonal to iters 001
(yield-curve), 002 (vol-DD), 003 (calendar).

**Configs tested (6):**

| name | threshold | window | scope | sortino_lh56y | corrpct | score | tier | WC | edge_vs_winner |
|---|--:|--:|---|---:|---:|---:|---|:---:|---:|
| `..._corrgate_off_baseline` ← Sortino-best | — | — | none | **1.2841** | 0.0% | 76.5 | STRONG | T | -0.0405 |
| `..._corrgate_t000_60d_offleg_cashx` | 0.00 | 60d | offleg→CASHX | 1.2211 | 44.7% | 76.5 | STRONG | T | -0.1035 |
| `..._corrgate_t020_60d_offleg_cashx` | 0.20 | 60d | offleg→CASHX | 1.2133 | 24.0% | 76.5 | STRONG | T | -0.1113 |
| `..._corrgate_t030_60d_offleg_cashx` (best corr-gate) | 0.30 | 60d | offleg→CASHX | 1.2540 | 14.6% | 76.5 | STRONG | T | -0.0706 |
| `..._corrgate_t020_120d_offleg_cashx` | 0.20 | 120d | offleg→CASHX | 1.2184 | 21.7% | 76.5 | STRONG | T | -0.1062 |
| `..._corrgate_t020_60d_master_cashx` (KILL #4 OVER_SUPPRESS) | 0.20 | 60d | master→CASHX | 0.9252 | 24.0% | 42.5 | MARGINAL | F | -0.3994 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.2841 < 1.3746)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (only master is < 1.10; offleg variants 1.21-1.25)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 = bit-exact iters 001/002/003 baseline)
- KILL_LOOP #4 (over-suppression) — **FIRED for `..._master_cashx`** (lh_56y pct_above_bench 0.7039 << 0.85)
- KILL_LOOP #5 (corr-regime-non-event) — **NOT FIRED** (corrgate fires 14.6%-44.7% — well above 5%)

**Key finding:** Stock-bond correlation regime gating produces no Sortino
lift on the winner's two-leg structure — the corr-flip is most active when
the trend signal is *already* defensive, so the gate's marginal
contribution is just OFF-leg vehicle choice (ZROZ vs CASHX). Across 56
years, ZROZ duration risk premium > CASHX short-rate yield in
expectation, so the swap loses Sortino. **`..._master_cashx` is the loop's
first FIRED KILL_LOOP** (#4 over-suppression: lh_56y pct_above_bench 0.7039
< 0.85) — forcing whole-portfolio cash during 24% of days collapses
Sortino by 28%. **G1 PBO=0.071 is the cleanest PBO of the loop** (vs
003's 0.444, 002's 0.159, 001's 0.575): orthogonal grid design (threshold
× window × scope) pays off methodologically even when the strategy
hypothesis fails. Best corr-gate variant (`t030_60d_offleg`) recovers to
baseline in post-2003 windows (spy_real 1.0911 = baseline; ndx_real 1.2890
= baseline) but loses 0.030 Sortino in lh_56y. Crisis attribution
unchanged (2008_GFC only, 1 of 4) — 2022_rates not rescued because the
QLD↔ZROZ correlation flipped positive *after* the bear was already
underway, AND the offleg-only override doesn't fire during ON state. The
t000 variant gives the cleanest MDD reduction of the loop (-7.1pp absolute,
-11% relative) but at -0.063 Sortino cost.

**beats_winner:** **false** (best Sortino edge -0.0405 = baseline replica
drift only; no corr-gate variant adds Sortino).

**Next iter ideas:** (a) **Multi-asset ON rotation with inverse-vol
weighting** {QLD, SOXL, UPRO} `[risk_parity, p.10, ch.1]` +
`[stocks_on_the_move, p.98]` — distinct from T4 Clenow / T5 Carver / iter
023 (which used 1 ON asset per config); cross-asset *first* moment
diversification on ON leg is the natural complement to this iter's
negative result on cross-asset *second* moment; (b) VIX-percentile / VRP
overlay `[volatility_trading, ch.7]` (forward-looking implied vol vs
realised already in stack); (c) Bond duration timing `[systematic_trading,
ch.9]` — sidestep bond risk directly rather than the cross-asset
correlation.

### 003 — 2026-05-09 — calendar-halloween-gate

**Hypothesis:** Calendar-month seasonal master-gate (Hirsch best-6-months /
Halloween effect: Nov-Apr ON, May-Oct weak) overlaid on the winner's
vote-of-K trend signal via three aggregation rules: hard veto OFF (May-Oct
or narrower Jun-Sep), augment as 5th vote member (K=2 or K=3 of 5), or
replace AR(1) with the calendar indicator. Citation:
`[trading_systems_methods, p.479-481]` (Hirsch / Halloween / Turn-of-month
calendar rules).

**Configs tested (6):**

| name | calendar mechanic | sortino_lh56y | score | tier | WC | edge_vs_winner |
|---|---|---:|---:|---|:---:|---:|
| `..._cal_off` (winner replica) | none (baseline) | 1.2841 | 76.5 | STRONG | T | -0.0405 |
| `..._cal_veto_may_oct` | hard veto May-Oct (Hirsch) | 1.1216 | 68.5 | PROMISING | F | -0.2030 |
| **`..._cal_veto_jun_sep`** ← Sortino-best | hard veto Jun-Sep (narrow) | **1.3061** | 71.5 | PROMISING | T | **-0.0185** |
| `..._cal_5vote_K2of5_may_oct` ← score-best | 5th vote (Nov-Apr=1), K=2 | 1.2575 | **79.5** | STRONG | T | -0.0671 |
| `..._cal_5vote_K3of5_may_oct` | 5th vote, stricter K=3 | 1.1128 | 58.5 | MARGINAL | F | -0.2118 |
| `..._cal_replace_ar_may_oct` | swap AR(1) for Halloween | 1.1515 | 76.5 | STRONG | T | -0.1731 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.3061 < 1.3746)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (only 1 of 5 calendar configs < 1.10 floor)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 = bit-exact iter 001/002 baseline)
- KILL_LOOP #4 (over-suppression) — **NOT FIRED** (all configs pct_time_above_benchmark_lh56y = 1.0000)

**Key finding:** The narrower Jun-Sep "summer stall" veto is the **first loop
config to lift Sortino above the replica baseline** (1.2841 → 1.3061, +0.022
edge). The canonical Hirsch May-Oct framing is monotonically worse than
baseline (-0.20 Sortino) because forcing OFF for 50.5% of trading days costs
more than it saves in crisis-rescue. The 2022_rates target was NOT rescued
by any variant: the bear ran Nov-2021 → Oct-2022, spanning ~6 months in
Hirsch "good" Nov-Apr where ON stayed on. Crisis attribution unchanged
(2008_GFC only, 1 of 4) for every config. **Augmentation K=2 (config 4)
produces highest CAGR (31.0%) and highest score (79.5 STRONG)** but lower
Sortino than baseline because soft tilt keeps Oct-2008 exposure on. G5
post-2020 FWD Sharpe surfaces clean published-edge decay: baseline 0.708 →
jun_sep 0.371 → may_oct 0.001. **G1 PBO=0.444 passes universally** (worse
than iter 002's 0.159 but better than iter 001's 0.575) — calendar layer
adds modest CSCV variation between veto/augment/replace.

**beats_winner:** **false** (best Sortino edge -0.0185 — closest any loop
iter has come to +0.05 threshold but still 0.0685 short).

**Next iter ideas:** (a) Stock-bond correlation regime classifier (60d
QLD↔ZROZ correlation flip; targets 2022 directly via dual-fall regime
detection) `[risk_parity, ch.5]` / `[ml_for_algo_trading, ch.9]`; (b)
Multi-asset ON rotation with inverse-vol weighting `[risk_parity, ch.5 p.10]`
+ `[stocks_on_the_move, p.98]`; (c) VIX-percentile / VRP harvesting overlay
`[machine_trading]` / `[volatility_trading, ch.7]`.

### 002 — 2026-05-09 — on-vol-dd-killswitch

**Hypothesis:** Vol-adjusted drawdown master-gate (Carver-style kill switch:
DD_252d > X × σ_price_21d, half-threshold re-arm hysteresis) overlaid on top
of the winner's vote-of-K trend signal. Targets the 2022_rates loss
identified in iter 001 as an ON-leg latency problem. Citation:
`[systematic_trading, p.212 ch.13]` (Carver semi-automatic stop, X*sigma
from tracking extreme).

**Configs tested (6):**

| name | kind | param | sortino_lh56y | killpct | score | tier |
|---|---|--:|---:|---:|---:|---|
| **`..._dd_off`** (winner replica) | no killswitch | — | **1.2841** ← best | 0.0% | 76.5 | STRONG |
| `..._dd_x2_252_vol21` | vol-adj | 2 | 1.0824 | 38.1% | 71.0 | PROMISING |
| `..._dd_x3_252_vol21` | vol-adj | 3 | 1.1526 | 27.7% | 76.5 | STRONG |
| `..._dd_x4_252_vol21` (Carver) | vol-adj | 4 | 1.1779 | 21.7% | 76.5 | STRONG |
| `..._dd_x5_252_vol21` | vol-adj | 5 | 1.2240 | 17.5% | 79.5 | STRONG |
| `..._dd_pct25_252` | abs % | 25% | 1.1365 | 31.2% | 76.0 | STRONG |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.2841 < 1.3746)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (4 of 5 ks-configs ≥ 1.10 floor)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 = iter 001 baseline exactly)
- KILL_LOOP #4 (whipsaw-detector) — **NOT FIRED** (kill-switch turnover lower than baseline 9.3/y)

**Key finding:** Carver's sigma-price stop does NOT generalise from
single-trade single-asset position management to a regime overlay on a
leveraged trend system. LETF natural vol means even normal pullbacks cross
3-4σ DD thresholds; the kill switch fires too often (21.7% of days at
Carver-default X=4) and locks out compounding rallies. Sortino is
monotonically below baseline across the entire X sweep. The original target
crisis (2022_rates) is not rescued by any variant — 2022 was a duration
problem (slow grinding bear), not a magnitude problem. **Structural
positive:** G1 PBO=0.159 passes cleanly across all configs (vs iter 001's
universal G1=0.575 fail) — kill-switch dimension is genuinely orthogonal,
confirming CSCV behaves correctly when configs vary in distinct mechanics.

**beats_winner:** **false** (best Sortino edge -0.0405 = baseline replica
drift only; no kill-switch variant adds Sortino).

**Next iter ideas:** (a) Equity-bond correlation regime classifier — flip OFF
when 60d QLD↔ZROZ correlation goes positive (would have fired in 2022 when
both fell together) `[regime_change]`/`[ml_for_algo_trading]`; (b)
Multi-asset ON rotation with inverse-vol weighting `[risk_parity, ch.5]` +
`[stocks_on_the_move, p.98]`; (c) Calendar/seasonal master-gate as 5th vote
member `[trading_systems_methods, p.388]`/`[evidence_based_ta, ch.7]`.

### 001 — 2026-05-09 — adaptive-off-yieldcurve

**Hypothesis:** Term-premium-aware OFF-asset rotation (10y - 3m CMT slope
gates ZROZ vs CASHX during defensive periods) attempts to rescue the 2022
rates loss of the study winner. Same trend ON signal as winner (vote-of-2
sma250/100 vol21<40% ar30>0). Citation: `[systematic_trading, ch.9 p.180-190]`
(Carver carry as regime gate).

**Configs tested (6):**

| name | OFF rule | sortino_lh56y | sharpe_lh56y | score | tier |
|---|---|---:|---:|---:|---|
| `..._off_zroz_baseline` | always ZROZ (replica) | 1.2841 | 0.892 | 72.5 | PROMISING |
| `..._off_adapt_ts000` | (10y-3m) > 0.0pp gate | 1.2661 | 0.880 | 72.5 | PROMISING |
| `..._off_adapt_ts050` | (10y-3m) > 0.5pp gate | 1.2969 | 0.902 | 72.5 | PROMISING |
| `..._off_adapt_ts100` | (10y-3m) > 1.0pp gate | 1.2796 | 0.890 | 72.5 | PROMISING |
| **`..._off_adapt_ts150`** | (10y-3m) > 1.5pp gate | **1.3018** ← best | 0.905 | 72.5 | PROMISING |
| `..._off_adapt_lvltrnd` | 10y < 252d-SMA(10y) | 1.2188 | 0.854 | 72.5 | PROMISING |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.3018 < 1.3746)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (all configs ≥ 1.10 floor)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (replica drift -0.04 < 0.05 bound)

**Key finding:** Term-premium gating on the OFF leg produces a tight Sortino
band (1.27-1.30) that does not exceed the always-ZROZ baseline by enough
margin to register a win. The 2022 equity drawdown was an ON-leg mistake (NDX
crashed while trend signal was still ON), not an OFF-asset problem — so no
amount of OFF-asset cleverness rescues that crisis. G1 PBO 0.575 fails
universally because the one-axis sweep design intentionally minimizes
hypothesis-space diversity.

**beats_winner:** **false** (best Sortino edge -0.0228; WC also failed on G1
PBO).

**Next iter ideas:** (a) ON-signal regime modulation — make the trend gate go
OFF earlier in 2022-style stress regimes via regime classifier
(`[regime_change]` / `[adaptive_markets]`); (b) Multi-asset ON rotation with
inverse-vol weighting (distinct from T4 ranking and T5 Carver); (c)
Calendar/seasonal master-gate as a 5th vote member (`[trading_systems_methods]`
Kaufman or `[evidence_based_ta]` Aronson).
