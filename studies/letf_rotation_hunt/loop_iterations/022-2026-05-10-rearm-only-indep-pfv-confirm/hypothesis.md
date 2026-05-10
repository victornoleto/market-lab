# Iter 022 — rearm-only INDEPENDENT impl + PFV vol-confirm gate

**Phase:** 4 — iter 017 focused validation/refinement
**Slug:** `rearm-only-indep-pfv-confirm`
**Date:** 2026-05-10 UTC
**n_configs:** 6
**cumulative_n_trials_global:** 552 → **558**

## Hypothesis

**PRIMARY (validation):** An **independent reimplementation** of iter 021's
slot 5 rearm-only T40D60 gate — using a from-scratch explicit-loop algorithm
in `rearm_independent.py` (NO import of iter 017's `reentry_overlay.py`) —
must produce **bit-exact identical** strategy returns to the iter 017
module-based reference (slot 4 anchor for OR composition; rearm-only logic
re-derived in this iter). Validates that iter 021's loop-max single-leg
Sortino finding (1.4176 vs T3d-K2 winner 1.3246, +0.0930) is
implementation-independent and not an artefact of iter 017's helper
internals.

**SECONDARY (refinement):** A **post-flip realised-vol confirmation gate
(PFV20)** — fire rearm only if the first 5 trading days post-flip-on show
realised vol below trailing 5y 20th percentile of 5d realised vol — provides
a **quality-confirmation filter** topologically distinct from iter 020's
pre-flip MDD-rejection filter. Tests Husson-Trifoni's "low-vol regime ⇒
streaks" thesis at the PER-EVENT post-flip level: only flips that immediately
exhibit streak-quality (low vol persistence) earn rearm leverage. Expected
to tighten activation (~50-70% of slot 5's 5.8%) — positive expected on
Sortino, negative on CAGR (loses 5 first-day post-flip rebound days,
2020-style).

## Phase 4 mapping

- **Allowed work type:** "Independent implementation parity for T40D60
  returns" + "Small performance overlay during the rearm window only, if
  pre-registered and cited."
- **Anchor:** iter 017 `qld_voteK2_sma250_100_vol21_40_ar30_rearm_single_K4lv25_g25_rvp70_cashx_T40D60`
  (Sortino 1.4030, CAGR 32.66%, end_eq 1.620× T3d-K2, PBO 0.4405).
- **Iter 021 reference (rearm-only):** Sortino 1.4176, CAGR 32.44%, end_eq
  1.516×.

## Configs (6, mechanism-mix-diverse with 6 distinct upgrade-axis topologies)

| # | name | topology | upgrade axis | rearm impl | T_crash | D_arm | PFV |
|---|---|---|---|---|--:|--:|---|
| 1 | `..._indep_baseline_qld_zroz` | single/none/none | none | — | — | — | — |
| 2 | `..._indep_single_K4lv25_g25_rvp70_cashx` | single/K4_AND_QLDlv25/g=0.25/p70-cashx | K4_AND_lv25 | — | — | — | — |
| 3 | `..._indep_basket3invvol_K4lv25_g25_rvp70_cashx` | basket3/K4_AND_QLDlv25/g=0.25/p70-cashx | K4_AND_lv25 | — | — | — | — |
| 4 | `..._indep_single_K4lv25_g25_rvp70_cashx_T40D60` | single/K4_OR_rearm_iter017impl/g=0.25/p70-cashx | K4 OR rearm | iter017 module | 40 | 60 | — |
| 5 | `..._indep_single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl` (PRIMARY) | single/rearm_only_indepimpl/g=0.25/p70-cashx | rearm only | INDEPENDENT (rearm_independent.py) | 40 | 60 | — |
| 6 | `..._indep_single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl_pfv20` (NEW) | single/rearm_only_indepimpl_pfv20/g=0.25/p70-cashx | rearm only AND PFV20 | INDEPENDENT (rearm_independent.py) | 40 | 60 | 5d/1260d/p20 |

Note: slot 4 uses iter 017's `reentry_overlay.py` to provide the
calibration-anchor T40D60 OR-composition reproduction; slot 5 uses the
in-iter `rearm_independent.py` module to test the same algorithm via a
from-scratch explicit-loop implementation. Both target rearm-only/OR-anchor
behaviour with bit-exact-equivalent intermediate gates per the algorithm
specification in iter 017's docstring.

## KILL_LOOP pre-conditions

| # | rule | success-tag? |
|---|---|---|
| 1 | `success_tag` — any config achieves beats_winner=True | ✅ POSITIVE |
| 2 | `decisive_fail` — best Sortino_lh56y < 1.20 (Phase 3 floor) | ❌ NEGATIVE |
| 3 | `replica_baseline` — baseline Sortino drift > 0.005 vs 1.3240 | ❌ NEGATIVE |
| 4 | `replica_single_K4lv25_g25` — drift > 0.005 vs 1.3951 | ❌ NEGATIVE |
| 5 | `replica_basket3invvol_K4lv25_g25` — drift > 0.005 vs 1.4689 | ❌ NEGATIVE |
| 6 | `replica_T40D60` — drift > 0.005 vs 1.4030 (iter 017 OR-anchor) | ❌ NEGATIVE |
| 7 | `replica_rearmonly_T40D60` — slot 5 Sortino drift > 0.005 vs 1.4176 (iter 021 slot 5) | ❌ NEGATIVE |
| 8 | `parity_check_indep_impl` — max abs daily-return diff between independent rearm gate and iter 017 module gate (built from same on_signal/T_crash/D_arm) > 1e-12 | ❌ HARD MECHANISM FAIL |
| 9 | `PBO_blowup` — G1 PBO ≥ 0.55 | ❌ NEGATIVE |
| 10 | `PBO_held` — G1 PBO < 0.50 | ✅ POSITIVE |
| 11 | `pfv_phase3_perf_candidate` — slot 6 achieves phase3=True (CAGR>31.08%, end_eq>1.05×, Sortino≥1.20, PBO<0.50, DSR_global<0.05) | ✅ POSITIVE (CORE WEAK HYPOTHESIS) |
| 12 | `pfv_dominates_rearmonly` — slot 6 Sortino > 1.4176 (iter 021 slot 5) | ✅ POSITIVE (STRONG HYPOTHESIS — PFV improves rearm-only) |

## Expected outcomes

### Slot 5 (rearm-only INDEPENDENT IMPL — PRIMARY)

- **Sortino_lh56y:** 1.4176 (bit-exact match expected vs iter 021 slot 5)
- **CAGR_lh56y:** 0.3244 (32.44%)
- **end_eq vs T3d-K2 baseline:** 1.516×
- **end_eq vs iter 017 anchor:** 0.936×
- **PBO:** 0.40-0.55 (slots 4-6 share T40D60 fingerprint; mechanism diversity from PFV in slot 6 mitigates)
- **rolling_win_rates_vs_winner (1y/3y/5y/10y):** ~0.51 / 0.46 / 0.45 / 0.36
- **rolling_win_rates_vs_iter017 (1y/3y/5y/10y):** ~0.45 / 0.40 / 0.40 / 0.40

### Slot 6 (rearm-only + PFV20 — SECONDARY)

- **Sortino_lh56y:** 1.40-1.43 (PFV may help by removing seesaw-context flips, or hurt by losing 2020 V-bottom rebound)
- **CAGR_lh56y:** 0.27-0.31 (likely lower; PFV tightens activation 30-50%, sacrificing some post-flip explosive moves)
- **end_eq vs T3d-K2 baseline:** 0.8-1.3×
- **end_eq vs iter 017 anchor:** 0.5-0.8×
- **rearm activation%:** 1.5-3% (vs slot 5's 5.8%; PFV-quality filter tightens)
- **`phase3_performance_candidate`:** plausible if PFV preserves Sortino while CAGR remains > 31.08% — uncertain
- **`phase4_anchor_improved`:** unlikely (CAGR likely lower than 32.66%)

### Comparison vs winner

For **beats_winner=True** a config needs:
- `sortino_lh56y > 1.3746` (= 1.3246 + 0.05 anti-curve-fit margin)
- `winner_conditions_met = True` (per scoring rubric strict bars)
- `pct_time_above_benchmark_lh56y >= 0.95`

For **phase3_performance_candidate** (Phase 3 perf-first floor):
- `cagr_lh56y > 0.3108`
- `end_equity_ratio_vs_winner > 1.05`
- `sortino_lh56y >= 1.20`
- `g1_pbo < 0.50` AND `g2_dsr_p_cumulative < 0.05`

For **phase4_anchor_improved** (Phase 4 strict improvement vs iter 017):
- `(cagr_lh56y > 0.3266 OR end_eq_ratio_vs_iter017 > 1.0)`
- `sortino_lh56y >= 1.35`
- `g1_pbo < 0.50` AND `g2_dsr_p_cumulative < 0.05`

For **phase4_anchor_validated**:
- Slot 5 INDEPENDENT IMPL parity check passes (KILL_LOOP #8 NOT FIRED)
- AND slot 5 Sortino drift vs 1.4176 < 0.005 (KILL_LOOP #7 NOT FIRED)

## INCOMPLETE flags

- **PFV percentile sensitivity:** only p20 tested in slot 6; p10/p25 not pre-registered (avoid PBO blowup risk per iter 018 lesson).
- **PFV reference asset:** uses QLD 5d realised vol (asset-specific, mirroring iter 014's K4_AND_QLDlv25 pattern); SPY/QQQ alternatives not tested.
- **Subperiod robustness:** reported in SUMMARY.md (1970-1989 / 1990-2009 / 2010-2026) for slot 5 only; slot 6 subperiod left as next-iter follow-up if PFV fires.
- **Independent impl validation depth:** parity check covers `build_postcrash_rearm_gate` only; not the full upstream `entry_signal_K2` / `upgrade_signal_K4` / `upgrade_signal_lowvol25` chain (those are calibration-anchor checked via slots 1-3).

## Trial accounting

- `closed_study_cumulative_n_trials`: 426
- `cumulative_n_trials_loop` BEFORE iter 022: 126
- `cumulative_n_trials_global` BEFORE iter 022: 552
- LOCAL `n_configs` this iter: 6
- `cumulative_n_trials_loop` AFTER iter 022: 132
- `cumulative_n_trials_global` AFTER iter 022: **558**

## Citations

- **PRIMARY:** `[advances_fin_ml, p.222-223]` Bailey-Lopez-de-Prado DSR with
  cumulative n_trials — independent reimplementation reduces single-impl
  risk in DSR claims.
- `[advances_fin_ml, p.208-211]` PBO via CSCV — mechanism-mix diversity.
- `[leverage_for_the_long_run, p.6-7, ch.3]` Husson-Trifoni MA flip-on as
  empirical streak-window onset (motivates rearm primitive).
- `[leverage_for_the_long_run, p.4, ch.2]` streaks-vs-seesawing thesis
  (motivates PFV: streak quality = low post-flip vol).
- `[volatility_trading, p.58-60]` Sinclair vol cone (PFV percentile-based
  vol-regime gate).
- `[stocks_on_the_move, p.98]` Clenow trend-strength (K4 base intuition).
- `[risk_parity, p.80-81, ch.4]` Qian RORO graded master gate.
- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking.
- `[systematic_trading, p.212, ch.13]` Carver re-arm hysteresis.
- `[advances_fin_ml, p.196-202]` bootstrap CI / DSR.

## Eligibility checklist (LOOP_PROTOCOL §"Strategy eligibility")

1. ✅ **Citable:** primary `[advances_fin_ml, p.222-223]` (DSR cumulative).
2. ✅ **Distinct from `iterations/`:** independent reimplementation of a
   loop-iter primitive is not in T1-T5 closed study.
3. ✅ **Distinct from `loop_iterations/`:** iter 021 used iter 017's module
   to build the rearm-only ablation; iter 022 uses an INDEPENDENT impl in
   a fresh module + adds the never-tested PFV20 gate.
4. ✅ **Data feasibility:** all required series (QLDSIM, TQQQSIM, UPROSIM,
   UGLSIM, ZROZSIM, IEFSIM, CASHX, SPYSIM) already in
   `data/testfolio/` and used by iters 011-021.

## Mandate §1 reminder

Capital remains 100% Plano C. Even if `phase4_anchor_improved=true` or
`beats_winner=true` fires, this iter records only — no realloc.
LOOP_PROTOCOL §"Mandate §1 reinforcement".
