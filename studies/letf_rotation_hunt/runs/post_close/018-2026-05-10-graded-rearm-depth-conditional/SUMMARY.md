# 018-2026-05-10-graded-rearm-depth-conditional — SUMMARY

**Iter:** 018 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Graded rearm depth — D_arm linearly proportional to prior
OFF stretch length T_off. Refines iter 017's NEW (non-replica)
strict_superset (`single_K4lv25_g25_rvp70_cashx_T40D60`, Sortino 1.4030,
CAGR 32.66%, end_eq 1.62×, crisis 1/4) by making the rearm harvest window
length scale with the depth of the crash that preceded each qualifying
OFF→ON flip. Tests Husson-Trifoni's longer-below-MA → longer-above-MA
streak thesis at the per-event D_arm level.
**Primary citation:** `[leverage_for_the_long_run, p.4-7, ch.2-3]`
Husson-Trifoni — streaks-vs-seesawing asymmetry.
**Secondary citations:** `[leverage_for_the_long_run, p.7]` trend × streaks
× vol-regime decomposition; `[stocks_on_the_move, p.98]` Clenow trend
re-establishment; `[volatility_trading, p.58-60]` Sinclair vol cone;
`[risk_parity, p.80-81, ch.4]` Qian RORO graded; `[risk_parity, ch.5,
p.10]` Carlson stacking; `[systematic_trading, p.212, ch.13]` Carver re-arm
hysteresis; `[advances_fin_ml, p.208-211]` CSCV PBO mechanism-mix-diversity;
`[advances_fin_ml, p.222-223]` DSR cumulative (n_global=534).
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_018
**n_configs:** 6
**cumulative_n_trials_global:** 528 → **534**

## TL;DR

- ⚠️ **HYPOTHESIS REJECTED AT THE STATISTICAL LEVEL — G1 PBO BLOWUP**
  (KILL_LOOP #6 FIRED). G1 PBO **0.8135** (vs iter 017's 0.4405; +0.373pp
  jump in single iter — **largest single-iter PBO regression in the
  loop**). Cause: 5 of 6 configs share the iter 014 strict_superset
  base topology (`single/K4_AND_lv25/g=0.25/p70-cashx`), differing only
  in rearm specifics (none/fixed/graded × 3 coefficients). CSCV correctly
  penalises this parametric clustering — **identical lesson to iter 013**
  (4 of 6 in same K4_AND_lv25/p70-cashx family → PBO 0.5437). PBO ≥ 0.50
  hard gate fails for every config → `winner_conditions_met=False`
  universally → `beats_winner=false`, `phase3_performance_candidate=false`,
  `strict_superset=false` for ALL 6 configs.
- ✅ **All 3 calibration anchors PRESERVED bit-exact** (KILL_LOOP #3, #4,
  #5 ALL NOT FIRED):
  - `baseline_qld_zroz` Sortino 1.3240 = iter 011-017 baseline
    (drift 0.0000) — **9th-generation cross-iter reproducibility**.
  - `single_K4lv25_g25_rvp70_cashx` Sortino 1.3951 = iter 013-017
    strict_superset (drift 0.0000).
  - `single_K4lv25_g25_rvp70_cashx_T40D60` Sortino 1.4030 = iter 017
    LOOP MAX strict_superset (drift 0.0000) — **iter 017's NEW
    strict_superset confirmed reproducible.**
- 🤔 **MECHANISM-LEVEL FINDING: graded D_arm preserves but does NOT
  improve over fixed T40D60.** Best graded variant is slot 6
  `p100_clamp40_150` at Sortino 1.3997 (-0.0033 vs T40D60), CAGR 32.87%
  (+0.21pp vs T40D60), end_eq 1.731× (+0.11 vs T40D60). Slot 4 PRIMARY
  `p075_clamp30_120` Sortino 1.3946, CAGR 32.38% (-0.27pp). Slot 5
  shorter-clamp `p050_clamp30_90` Sortino 1.3920, CAGR 32.07% (-0.59pp).
  KILL_LOOP #10 (graded_dominates_T40D60) **NOT FIRED** — no graded
  config beats T40D60 on Sortino; the "deeper, fewer events" recipe iter
  017 surfaced is at or near the local optimum for D_arm.
- 📈 **CAGR/end_eq monotonicity in coefficient confirmed** — slot 5
  (coef 0.50) → slot 4 (coef 0.75) → slot 6 (coef 1.00) gives
  monotonically increasing CAGR (32.07% → 32.38% → 32.87%) and end_eq
  (1.36× → 1.49× → 1.73×). Longer mean D_arm per event (43.6 → 58.4 →
  76.0 days) maps directly to terminal-equity lift. **Slot 6's longer
  events do produce more compounding** — but Sortino plateaus near
  T40D60's 1.4030 and never breaches it. The graded variation does not
  unlock ADDITIONAL Sortino beyond what fixed T40D60 already extracts.
- ❌ **NO 2020 COVID rescue in any graded variant.** Crisis attribution
  identical to iter 017 (1/4 — only 2008 GFC) for all 6 configs. The
  graded D_arm doesn't address the V-recovery onset timing — same root
  cause iter 017 surfaced (`on_signal=OFF` during Feb-March 2020 V; the
  flip to ON came after SPY had already rebounded).
- ❌ **LOOP'S FIRST CRISIS-≥2/4 STRICT_SUPERSET STILL NOT ACHIEVED.**
  KILL_LOOP #12 NOT FIRED (no graded config achieves both
  strict_superset AND crisis ≥ 2/4 — and in this iter, no config achieves
  strict_superset at all because of the PBO blowup).
- 🤔 **All configs tier_label = PROMISING** (score 72.5) instead of
  iter 017's STRONG (76.5) — the difference is the G1 PBO strict bar:
  iter 017 had PBO 0.4405 → contributes to `winner_conditions_met=True` →
  STRONG; iter 018 has PBO 0.8135 → `winner_conditions_met=False` → score
  drops 4 points (criterion 1 partial credit) → tier PROMISING.
- ✅ **Sortino edge over T3d-K2 winner preserved for slots 2-6**:
  +0.0705 to +0.0784 (vs benchmark 1.3246) — i.e. all 5 non-baseline
  configs would clear the +0.05 anti-curve-fit edge IF G1 PBO weren't
  blocking WC. The iter 014 strict_superset Sortino lift is mechanically
  intact; it's the multiple-testing penalty (CSCV PBO at 6-config
  parametric cluster) that kills statistical claims here.
- 📚 **Methodological lesson reinforced (3rd-time confirmation across
  iters 008/013/018):** "Mechanism diversity for CSCV is structural,
  not parametric." Iter 008 surfaced this with parameter-axis sweeps.
  Iter 013 surfaced this with K4_AND_lv25 gamma-clustered sweeps.
  Iter 018 now surfaces it with graded-D_arm coefficient sweeps. The
  recipe to break PBO < 0.50 in a 6-config grid REQUIRES at least 3-4
  qualitatively distinct ON-leg or OFF-mechanism topologies — coefficient
  variants alone don't count.

---

## Configs tested

| # | Name | Topology | Rearm rule | Role |
|---|---|---|---|---|
| 1 | `..._grearm_baseline_qld_zroz` | single/none/none | none | Calibration anchor |
| 2 | `..._grearm_single_K4lv25_g25_rvp70_cashx` | single/K4_AND_lv25/g=0.25/p70-cashx | none | Iter 014 strict_superset replica |
| 3 | `..._grearm_single_K4lv25_g25_rvp70_cashx_T40D60` | single/K4_AND_lv25_OR_rearm_fixed/g=0.25/p70-cashx | fixed T=40 D=60 | Iter 017 NEW strict_superset replica (LOOP MAX) |
| 4 | `..._grearm_single_K4lv25_g25_rvp70_cashx_p075_clamp30_120` ← **PRIMARY** | single/K4_AND_lv25_OR_rearm_graded/g=0.25/p70-cashx | D_arm = clamp(0.75 × T_off, 30, 120) | Graded depth-proportional (mean D=58.4) |
| 5 | `..._grearm_single_K4lv25_g25_rvp70_cashx_p050_clamp30_90` | single/K4_AND_lv25_OR_rearm_graded/g=0.25/p70-cashx | D_arm = clamp(0.50 × T_off, 30, 90) | Sensitivity (shorter, mean D=43.6) |
| 6 | `..._grearm_single_K4lv25_g25_rvp70_cashx_p100_clamp40_150` | single/K4_AND_lv25_OR_rearm_graded/g=0.25/p70-cashx | D_arm = clamp(1.00 × T_off, 40, 150) | Sensitivity (longer, mean D=76.0) |

**4 ON-leg-overlay topologies** (per hypothesis.md) but **5 of 6 configs
share K4_AND_lv25/g=0.25/p70-cashx base**, with only the rearm overlay
varying. This is the structural deficiency the PBO 0.8135 result reveals.

---

## Results gross + net per dataset (Sortino + Sharpe + CAGR + MDD)

### lh_56y (1970-01 → 2026-04)

| config | Sortino | Sharpe | CAGR | MDD | end_eq vs baseline | pct_above_SPY |
|---|---:|---:|---:|---:|---:|---:|
| baseline_qld_zroz | 1.3240 | 0.919 | 31.08% | -64.50% | 1.000× | 1.0000 |
| single_K4lv25_g25 (iter 014 replica) | 1.3951 | 0.968 | 31.47% | -47.69% | 1.129× | 1.0000 |
| single_K4lv25_g25_T40D60 (iter 017 replica) | **1.4030** | 0.974 | 32.66% | -48.18% | 1.620× | 1.0000 |
| graded p075_clamp30_120 (PRIMARY) | 1.3946 | 0.969 | 32.38% | -48.18% | 1.492× | 1.0000 |
| graded p050_clamp30_90 | 1.3920 | 0.967 | 32.07% | -47.69% | 1.356× | 1.0000 |
| graded p100_clamp40_150 | 1.3997 | 0.972 | **32.87%** | -48.18% | **1.731×** | 1.0000 |

### modern_1990 (1990+)

All non-baseline configs Sortino 1.290-1.303; CAGR 28.5-30.0%; MDD all -47.7% / -48.2%.

### spy_real (2003+)

Sortino 1.16-1.18; CAGR 23.0-24.6%; MDD -33.8% / -36.7%; pct_above_SPY 0.84-0.92 (graded p100 leads at 0.92).

### ndx_real (2010+)

Sortino 1.405-1.421; CAGR 29.7-30.7%; MDD -31.7% / -36.4%; pct_above_SPY 0.997-1.000.

**Net metrics** (after Lei 14.754 swing tax 15% + Inter Internacional fees):
not computed in this iter — `metrics_net = {}` per loop convention; tax/fees
stress is iter 017 idea (e), deferred to a future diagnostic-only iter.

---

## Gates per config (G1-G7)

| config | G1 PBO | G2 DSR p_loc | G2 p_cum | G3 win/8 | G4 OOS Sharpe | G5 FWD post-2020 | G6 99% CI low | G7 xlib delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_qld_zroz | **0.8135** ❌ | 3.29e-06 ✓ | 3.04e-03 ✓ | 6/8 ✓ | 0.822 ✓ | 0.708 ✓ | 0.547 ✓ | 0.000 ✓ |
| single_K4lv25_g25 | **0.8135** ❌ | 7.33e-07 ✓ | 1.13e-03 ✓ | 7/8 ✓ | 1.004 ✓ | 0.915 ✓ | 0.598 ✓ | 0.000 ✓ |
| T40D60 (iter 017 replica) | **0.8135** ❌ | 6.20e-07 ✓ | 1.00e-03 ✓ | 7/8 ✓ | 1.016 ✓ | 0.934 ✓ | 0.608 ✓ | 0.000 ✓ |
| graded p075 (PRIMARY) | **0.8135** ❌ | 7.32e-07 ✓ | 1.12e-03 ✓ | 7/8 ✓ | 1.025 ✓ | 0.931 ✓ | 0.604 ✓ | 0.000 ✓ |
| graded p050 | **0.8135** ❌ | 7.78e-07 ✓ | 1.17e-03 ✓ | 7/8 ✓ | 1.012 ✓ | 0.916 ✓ | 0.603 ✓ | 0.000 ✓ |
| graded p100 | **0.8135** ❌ | 6.69e-07 ✓ | 1.05e-03 ✓ | 7/8 ✓ | 1.011 ✓ | 0.966 ✓ | 0.604 ✓ | 0.000 ✓ |

**G1 fail dominates everything.** G2-G7 are all clean — DSR cumulative,
walk-forward, OOS, FWD, bootstrap CI, and cross-library all pass for every
non-baseline config. The lone PBO blocker is structural to the grid
design, not the underlying mechanism.

---

## Comparação vs winner

| config | sortino_lh56y | edge_vs_1.3246 | cagr_lh56y | cagr_edge_vs_31.08% | terminal_ratio_vs_T3d-K2 | WC | pct_time_above_benchmark_lh56y | beats_winner | phase3_perf_candidate | strict_superset |
|---|---:|---:|---:|---:|---:|:---:|---:|:---:|:---:|:---:|
| baseline_qld_zroz | 1.3240 | -0.0006 | 31.08% | +0.00pp | 1.000× | F | 1.000 | F | F | F |
| single_K4lv25_g25 (iter 014 replica) | 1.3951 | +0.0705 | 31.47% | +0.39pp | 1.129× | **F** | 1.000 | F | F | F |
| T40D60 (iter 017 replica) | **1.4030** | **+0.0784** | **32.66%** | **+1.58pp** | **1.620×** | **F** | 1.000 | F | F | F |
| graded p075 (PRIMARY) | 1.3946 | +0.0700 | 32.38% | +1.30pp | 1.492× | F | 1.000 | F | F | F |
| graded p050 | 1.3920 | +0.0674 | 32.07% | +0.99pp | 1.356× | F | 1.000 | F | F | F |
| graded p100 | 1.3997 | +0.0751 | 32.87% | +1.79pp | 1.731× | F | 1.000 | F | F | F |

**WC=False universally because G1 PBO 0.8135 ≥ 0.50.** Sortino edge,
pct_above_SPY, and Phase 3 CAGR/end_eq metrics are all favourable for
slots 2-6, but the strict bar fails on G1.

---

## Phase 3 performance diagnostics

| config | CAGR_lh56y | gap vs T3d-K2 31.08% | end_eq_ratio | rolling_5y_win% | rolling_10y_win% | crisis | phase3_perf_candidate |
|---|---:|---:|---:|---:|---:|:---:|:---:|
| T40D60 (iter 017 replica) | 32.66% | +1.58pp | 1.620× | 55.3% | 38.0% | 1/4 | F (PBO blocked) |
| graded p075 (PRIMARY) | 32.38% | +1.30pp | 1.492× | 55.4% | 38.0% | 1/4 | F (PBO blocked) |
| graded p050 | 32.07% | +0.99pp | 1.356× | 55.4% | 38.0% | 1/4 | F (PBO blocked) |
| graded p100 | 32.87% | **+1.79pp** | **1.731×** | 55.4% | 38.0% | 1/4 | F (PBO blocked) |

**Honest read:** the graded mechanism preserves the rearm performance lift
within ±0.27pp CAGR vs T40D60 fixed window. Slot 6 (longest clamp,
mean D=76) achieves the highest CAGR/end_eq among all 6 configs (including
beating T40D60), but its Sortino 1.3997 is just 0.0033 below T40D60's
1.4030. The "deeper, fewer events" thesis (iter 017's surprise) **holds at
the local optimum** — graded variants concentrated around D=60 don't
significantly improve over the fixed window.

**Key insight:** the LRS streak harvest for QLD/TQQQ in this universe
plateaus around D_arm ≈ 60-90 days. Graded D_arm proportional to T_off
captures the EXISTING streak structure but does not unlock additional
streak capture beyond the fixed T40D60 mechanism. Husson-Trifoni's
qualitative thesis is supported (longer crashes do correlate with longer
recoveries), but the marginal lift is small in this universe.

---

## KILL_LOOP results (pre-registered)

- ❌ **KILL_LOOP #1 (success_tag) — NOT FIRED.** No config achieves
  `beats_winner=True` (G1 PBO 0.8135 ≥ 0.50 fails WC strict bar
  universally even though Sortino > 1.3746 ✓ + pct_above ≥ 0.95 ✓ for 5 of 6).
- ✅ **KILL_LOOP #2 (decisive_fail) — NOT FIRED.** Best Sortino 1.4030 ≫ 1.20 floor.
- ✅ **KILL_LOOP #3 (replica_sanity_baseline) — NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact match to iter 011-017 baseline (drift
  0.0000). **9th-generation cross-iter reproducibility.**
- ✅ **KILL_LOOP #4 (replica_sanity_single_K4lv25_g25) — NOT FIRED.**
  single_K4lv25_g25 Sortino 1.3951 = bit-exact match to iter 013-017
  strict_superset (drift 0.0000).
- ✅ **KILL_LOOP #5 (replica_sanity_T40D60) — NOT FIRED.**
  single_K4lv25_g25_T40D60 Sortino 1.4030 = bit-exact match to iter
  017 LOOP MAX strict_superset (drift 0.0000). **Iter 017's NEW
  strict_superset confirmed reproducible.**
- 🛑 **KILL_LOOP #6 (PBO_blowup) — FIRED.** G1 PBO **0.8135** ≥ 0.55
  hard regression threshold. **Largest single-iter PBO regression in the
  loop** (iter 017 0.4405 → iter 018 0.8135; +0.373pp). Iter trajectory:
  005 0.881 → 006 0.798 → 007 0.552 → 008 0.5675 → 009 0.3770 → 010
  0.3929 → 011 0.3056 → 012 0.4960 → 013 0.5437 → 014 0.4405 → 015
  0.3333 → 016 0.3730 → 017 0.4405 → **018 0.8135**. Cause: 5 of 6 configs
  share K4_AND_lv25/g=0.25/p70-cashx base topology; rearm-overlay
  variation alone (none/fixed/graded × 3 coefficients) does NOT introduce
  enough CSCV mechanism diversity. **Identical lesson to iter 013** which
  had 4 of 6 in same family (PBO 0.5437); iter 018's 5-of-6 clustering
  amplifies the effect.
- ❌ **KILL_LOOP #7 (PBO_held) — NOT FIRED.** G1 PBO 0.8135 ≥ 0.50 hard
  gate.
- ❌ **KILL_LOOP #8 (graded_rearm_phase3_perf_candidate) — NOT FIRED.**
  0 of 3 graded configs achieve phase3=True (PBO blocks all). **CORE
  HYPOTHESIS REJECTED at the statistical level**, though mechanically the
  graded variants preserve T40D60's CAGR/end_eq within ±0.27pp.
- ❌ **KILL_LOOP #9 (graded_rearm_strict_superset) — NOT FIRED.** 0 of 3
  graded configs achieve strict_superset (PBO blocks all). **STRONGEST
  HYPOTHESIS REJECTED.**
- ❌ **KILL_LOOP #10 (graded_dominates_T40D60) — NOT FIRED.** Best graded
  Sortino 1.3997 (slot 6) < T40D60 1.4030 (-0.0033 edge). Graded
  variation does NOT improve over fixed T40D60 on Sortino. Husson-Trifoni
  depth-proportional thesis SUPPORTED qualitatively (CAGR/end_eq
  monotonic in coefficient) but Sortino at the local optimum is fixed
  T40D60.
- ❌ **KILL_LOOP #11 (graded_rearm_2020_covid_rescue) — NOT FIRED.** 0 of
  3 graded configs beat SPY in 2020_covid window. Mechanism-equivalent to
  iter 017 — graded D_arm doesn't address V-recovery onset timing.
- ❌ **KILL_LOOP #12 (graded_rearm_strict_superset_with_crisis_2plus) —
  NOT FIRED.** 0 of 3 graded configs achieve strict_superset AND crisis
  ≥ 2/4. **LOOP'S FIRST CRISIS-≥2/4 STRICT_SUPERSET STILL NOT
  ACHIEVED.**

---

## Plots

- `plots/01_equity_curves.png` — log-scale equity (lh_56y); baseline + 5
  overlay variants + SPY 1× b&h.
- `plots/02_drawdown_curves.png` — drawdowns; all overlay configs hit
  ~-47.7% / -48.2% (uniform across rearm variants).
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe (lh_56y).
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR (lh_56y).
- `plots/05_regime_attribution.png` — % time in equity (vote-K=2 ON state).
- `plots/06_pct_beat_spy.png` — cumulative % of 3y windows beating SPY.
- `plots/07_crisis_attribution.png` — crisis MDD vs SPY across 4 windows.

## Tables

- `tables/per_config_metrics.csv` — gross metrics per (config, dataset).
- `tables/gates_pass_fail.csv` — per-config gate outcomes + activation %s
  + turnover.

## Verdict + KILL status + Conclusion

- **Verdict:** PROMISING (best score 72.5; tier downgraded from STRONG to
  PROMISING because G1 PBO failure removes WC=True for all configs). Best
  config = `single_K4lv25_g25_rvp70_cashx_T40D60` (iter 017 strict_superset
  replica) — iter 018 contributes NO new strict_superset and surfaces a
  **statistical KILL** of the graded-D_arm hypothesis at the CSCV level.
- **KILL_LOOP fired summary:** #6 (PBO_blowup) fired (negative). #3, #4,
  #5 NOT fired (replica anchors preserved bit-exact — clean reproducibility
  + iter 017's NEW strict_superset confirmed). #7-#12 ALL NOT FIRED
  (PBO blowup blocks every WC-dependent positive flag).
- **Conclusion (lesson-learned):** the loop now has **3 independent
  confirmations** (iters 008, 013, 018) that "mechanism diversity for
  CSCV is structural, not parametric" `[advances_fin_ml, p.208-211]`.
  The graded D_arm coefficient sweep is the THIRD instance of a parametric
  cluster blowing PBO above 0.50. The loop's robust mechanism for
  6-config grids requires ≥3-4 qualitatively distinct topologies — iter
  017 had 4 (single/none, single/fixed-rearm, basket3/none, basket3/rearm
  via slot 6), iter 014 had 5 (1 baseline + 4 ON-leg topologies + 1
  basket3 triple-stack), both held PBO < 0.50. Iter 018 has only 2
  qualitatively distinct topologies (1 baseline + 5 single ON-leg).
  **Cohorts of graded coefficient variants cannot substitute for
  topological diversity.**
- **Mechanism-level finding (separate from the statistical KILL):** the
  graded D_arm preserves CAGR/end_eq lift within ±0.27pp of T40D60,
  monotonic in coefficient. Slot 6 (longest clamp) wins on CAGR + end_eq;
  slot 5 (shortest) loses. Sortino plateaus near 1.40 across the
  coefficient range. **The fixed T40D60 mechanism is at or near the local
  Sortino optimum** for the QLD/TQQQ rearm window in this universe.
- **Next iter direction:** restore CSCV diversity. Either (a) widen
  topologies (mix in basket3 or alt-OFF), (b) test ORTHOGONAL forward-vol
  gate (VIX-percentile / SPY-realised-vol on flip qualification — still
  un-tested in 18 iters), or (c) drop the graded experiment entirely
  and pivot to a fundamentally different family (currency carry,
  cross-asset trend, calendar/seasonality outside Halloween). VIX/SPY-vol
  gate has been on the ideas list since iter 010 but never executed —
  highest expected value.

**beats_winner:** **false** (no config achieves `winner_conditions_met=
True` because G1 PBO 0.8135 ≥ 0.50; Sortino + pct_above thresholds are
cleared by 5 of 6 but WC strict bar fails).

**phase3_performance_candidate (any):** **false** (PBO ceiling fails for
all 6 configs; Phase 3 momentum BROKEN this iter — first iter since 013
with 0 phase3 candidates).

**strict_superset (any):** **false** (no NEW finding; iter 014/017
strict_supersets remain reproducible but iter 018 does not contribute).

**Next iter ideas:**
(a) **VIX-percentile / SPY-realised-vol gate on flip qualification** —
forward-volatility gate orthogonal to ALL previously-tested mechanics.
Use SPY 21d realised-vol percentile (vs trailing 5y) as a VIX proxy
(no pre-1990 VIX data needed). Add this as ONE distinct topology
alongside basket3 + rearm variants to maintain CSCV diversity.
**Highest expected value: untested orthogonal mechanism + restores PBO
diversity.** Cite `[volatility_trading, ch.7]` Sinclair VRP.
(b) **Mechanism-mix-diverse rearm × basket3** — repeat iter 017's
4-distinct-topology recipe (1 baseline, 1 single anchor, 1 basket3
anchor, 1 single + rearm, 1 basket3 + rearm, 1 alt-OFF) but stack
graded D_arm in slots 4+5. Maintains 4 topologies + tests graded inside
diversity. Cite `[advances_fin_ml, p.208-211]` CSCV mechanism diversity.
(c) **Drawdown-conditional rearm gate** — fire rearm only when prior
OFF stretch coincides with trailing 200d SPY MDD breach > -15%, rather
than just T_off ≥ 40 days. Filters seesaw-induced false positives.
Cite `[regime_change]` + `[leverage_for_the_long_run, p.4-7]`.
(d) **Tax / fees stress on iter 017 strict_superset** — turnover ~5.3/y;
quantify Lei 14.754 swing tax 15% diagnostic (deferred from iter 017).
(e) **Pivot to entirely different family** — calendar/seasonality
beyond Halloween (e.g., post-FOMC drift), currency carry baskets, or
gold momentum. Iter 008/013/018 statistical lessons suggest exhausting
the K4_AND_lv25/g=0.25/p70-cashx neighbourhood may be subject to
diminishing returns; a regime change in family choice may be due.
