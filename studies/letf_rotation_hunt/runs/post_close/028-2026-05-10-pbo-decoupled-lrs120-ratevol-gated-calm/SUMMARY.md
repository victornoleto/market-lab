# Iter 028 — PBO-decoupled LRS1.20× ratevol-gated calm-only overlay

| Field | Value |
|---|---|
| **iter** | `028-2026-05-10-pbo-decoupled-lrs120-ratevol-gated-calm` |
| **tier** | `loop_iter` |
| **phase** | 4 — iter 017 focused validation/refinement |
| **slug** | `pbo-decoupled-lrs120-ratevol-gated-calm` |
| **hypothesis** | Iter 027 closed the LRS magnitude scan but slot 6 LRS1.20 unconditional's modern-era subperiod Sortino landed BELOW Phase 3 floor 1.20. This iter applies LRS1.20× ONLY when `ratevol_gate==0` (calm rate regime, ~70% of ON days at rvp70). Pre-registered KEY HYPOTHESIS: modern-era Sortino lift above 1.20 on at least one of {1990_2009, 2010_2026}. |
| **primary_citation** | `[advances_fin_ml, p.208-211]` CSCV PBO mechanism diversity |
| **datetime_utc** | 2026-05-10 13:18 UTC |
| **engine_version** | `loop_iter_028` |
| **n_configs** | 6 |
| **cumulative_n_trials_global (after)** | 594 |
| **cumulative_n_trials_loop (after)** | 168 |

## TL;DR

**Best config:** `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_rvgtdlrs120calm` (slot 6).

| Metric | Value | vs winner threshold | vs iter 017 anchor | vs iter 027 slot 6 LRS1.20 uncond |
|---|---:|---:|---:|---:|
| **Sortino_lh56y** | **1.3860** | +0.0114 (>1.3746) | -0.0170 (vs 1.4030) | **+0.0074** |
| **CAGR_lh56y** | **35.11%** | +4.03pp (>31.08%) | +2.45pp (>32.66%) | **-1.11pp** |
| **end_eq vs T3d-K2 baseline** | **3.385×** | n/a | +1.087× | -1.325× |
| **end_eq vs iter 017 anchor** | **2.090×** | n/a | +1.090× | **-0.818×** |
| **MDD** | -50.80% | n/a | -2.6pp worse | -2.6pp worse vs uncond |
| **PBO (G1)** | **0.4127** | <0.50 ✓ | identical to iter 026 | identical to iter 026 |
| **DSR_global p (G2 cumulative, n=594)** | 1.46e-03 | <0.05 ✓ | n/a | n/a |
| **score** | 76.5 | n/a | n/a | n/a |
| **tier_label** | STRONG | n/a | n/a | n/a |
| **winner_conditions_met** | True | n/a | n/a | n/a |
| **pct_time_above_benchmark_lh56y** | 1.000 | ≥0.95 ✓ | n/a | n/a |
| **beats_winner** | **True** | ✓ | n/a | n/a |
| **phase3_performance_candidate** | **True** | ✓ | n/a | n/a |
| **strict_superset** | **True** | ✓ | n/a | n/a |
| **phase4_anchor_improved** | **True** 🏆 | ✓ | ✓ (formal 5th) | n/a |

**KEY HYPOTHESIS RESULT:** **REJECTED** ❌. Slot 6 modern subperiod Sortino:
- 1990-2009: **1.139** (vs iter 027 unconditional 1.124, +0.015) — still BELOW 1.20 floor
- 2010-2026: **1.132** (vs iter 027 unconditional 1.144, -0.012) — still BELOW 1.20 floor

Regime-gating LRS to calm rate regimes does NOT lift modern-era Sortino above
the Phase 3 floor on either subperiod. **Modern-era softness is confirmed
structural to the rearm primitive itself**, not to LRS overlay magnitude or
unconditional application — iter 027's structural diagnosis is independently
falsified through this regime-conditioning probe.

## Configs tested

| # | name (suffix after `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_`) | upgrade | rearm | LRS mode | LRS factor | LRS gating | role |
|--:|---|---|---|---|--:|---|---|
| 1 | `baseline_qld_zroz` | none | NO | off | 1.00 | n/a | calibration anchor (19th-gen) |
| 2 | `single_K4lv25_g25_rvp70_cashx` | K4_AND_lv25 | NO | off | 1.00 | n/a | calibration anchor (16th-gen) |
| 3 | `single_K4lv25_g25_rvp70_cashx_unclrs105` | K4_AND_lv25 | NO | uncond_on | 1.05 | unconditional during ON | calibration anchor (5th-gen) |
| 4 | `single_K4lv25_g25_rvp70_cashx_T40D60` | K4_OR_rearm | YES (iter017) | off | 1.00 | n/a | iter 017 OR-anchor replica (11th-gen) |
| 5 | `single_rearmonly_g25_rvp70_cashx_T40D60` | rearmonly_indep | YES (INDEP) | off | 1.00 | n/a | iter 022 INDEP IMPL replica (8th-gen) |
| 6 | 🥇 `single_rearmonly_g25_rvp70_cashx_T40D60_rvgtdlrs120calm` (NEW) | rearmonly_indep | YES (INDEP) | rvgtdlrs120calm | **1.20** | when `ratevol_gate==0` (calm; ~50% of all bars active) | NEW probe |

## Results gross — per dataset (Sortino + Sharpe + CAGR + MDD)

| config | dataset | Sortino | Sharpe | CAGR | MDD | pct_above_bench |
|---|---|---:|---:|---:|---:|---:|
| baseline_qld_zroz | lh_56y | 1.3240 | 0.919 | 31.08% | -64.50% | 1.000 |
| baseline_qld_zroz | modern_1990 | 1.2217 | 0.855 | 28.05% | -64.50% | 0.998 |
| baseline_qld_zroz | spy_real | 1.0911 | 0.777 | 22.55% | -64.50% | 0.955 |
| baseline_qld_zroz | ndx_real | 1.2890 | 0.921 | 27.62% | -64.50% | 1.000 |
| single_K4lv25_g25 | lh_56y | 1.3951 | 0.968 | 31.47% | -47.69% | 1.000 |
| single_K4lv25_g25 | modern_1990 | 1.2905 | 0.905 | 28.48% | -47.69% | 0.998 |
| single_K4lv25_g25 | spy_real | 1.1592 | 0.834 | 22.97% | -33.77% | 0.839 |
| single_K4lv25_g25 | ndx_real | 1.4071 | 1.012 | 29.66% | -31.71% | 1.000 |
| single_K4lv25_g25_unclrs105 | lh_56y | 1.3842 | 0.962 | 32.42% | -49.27% | 1.000 |
| single_K4lv25_g25_unclrs105 | modern_1990 | 1.2833 | 0.900 | 29.40% | -49.27% | 0.998 |
| single_K4lv25_g25_unclrs105 | spy_real | 1.1544 | 0.831 | 23.77% | -35.09% | 0.845 |
| single_K4lv25_g25_unclrs105 | ndx_real | 1.4035 | 1.010 | 30.87% | -33.01% | 1.000 |
| single_K4lv25_g25_T40D60 (iter 017 OR) | lh_56y | 1.4030 | 0.974 | 32.66% | -48.18% | 1.000 |
| single_K4lv25_g25_T40D60 | modern_1990 | 1.3033 | 0.913 | 29.76% | -48.18% | 0.998 |
| single_K4lv25_g25_T40D60 | spy_real | 1.1707 | 0.841 | 23.91% | -36.73% | 0.839 |
| single_K4lv25_g25_T40D60 | ndx_real | 1.4187 | 1.019 | 30.74% | -36.36% | 0.997 |
| single_rearmonly_T40D60 (INDEP) | lh_56y | 1.4176 | 0.982 | 32.44% | -48.18% | 1.000 |
| single_rearmonly_T40D60 | modern_1990 | 1.3204 | 0.922 | 29.52% | -48.18% | 0.998 |
| single_rearmonly_T40D60 | spy_real | 1.2028 | 0.862 | 23.67% | -36.36% | 0.921 |
| single_rearmonly_T40D60 | ndx_real | 1.3910 | 1.001 | 28.70% | -36.36% | 0.999 |
| 🥇 **slot 6 rgtdlrs120calm** | **lh_56y** | **1.3860** | **0.961** | **35.11%** | **-50.80%** | **1.000** |
| slot 6 rgtdlrs120calm | modern_1990 | 1.3004 | 0.908 | 32.42% | -50.80% | 0.998 |
| slot 6 rgtdlrs120calm | spy_real | 1.1875 | 0.850 | 26.31% | -37.69% | 0.938 |
| slot 6 rgtdlrs120calm | ndx_real | 1.3680 | 0.985 | 32.16% | -36.36% | 0.998 |

## Gates per config (G1 cross-config; G2-G7 per-config)

| config | G1 PBO | G2 DSR p_local | G2 DSR p_cumulative (n=594) | G3 above-bench wins | G4 OOS Sharpe | G5 fwd post-2020 Sharpe | G6 99% CI low | G7 xlib Δpp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_qld_zroz | 0.4127 ✓ | 3.29e-06 ✓ | 3.34e-03 ✓ | 6/8 ✓ | 0.823 ✓ | 0.708 ✓ | 0.547 ✓ | 0.000 ✓ |
| single_K4lv25_g25 | 0.4127 ✓ | 7.33e-07 ✓ | 1.25e-03 ✓ | 7/8 ✓ | 1.004 ✓ | 0.915 ✓ | 0.598 ✓ | 0.000 ✓ |
| single_K4lv25_g25_unclrs105 | 0.4127 ✓ | 9.08e-07 ✓ | 1.44e-03 ✓ | 7/8 ✓ | 1.000 ✓ | 0.913 ✓ | 0.590 ✓ | 0.000 ✓ |
| single_K4lv25_g25_T40D60 | 0.4127 ✓ | 6.20e-07 ✓ | 1.11e-03 ✓ | 7/8 ✓ | 1.017 ✓ | 0.934 ✓ | 0.608 ✓ | 0.000 ✓ |
| single_rearmonly_T40D60 | 0.4127 ✓ | 4.79e-07 ✓ | 9.44e-04 ✓ | 7/8 ✓ | 0.983 ✓ | 0.908 ✓ | 0.619 ✓ | 0.000 ✓ |
| 🥇 slot 6 rgtdlrs120calm | 0.4127 ✓ | 9.30e-07 ✓ | 1.46e-03 ✓ | 7/8 ✓ | 0.965 ✓ | 0.887 ✓ | 0.605 ✓ | 0.000 ✓ |

All 6 configs pass all 7 gates. PBO is identical across all configs (0.4127 =
iter 026's PBO) — **structural-not-magnitude diagnosis preserved on the
regime-conditioning axis**.

## Comparação vs winner (Phase 3 + Phase 4 diagnostics combined)

| config | sortino_lh | edge_vs_1.3246 | cagr_lh | edge_vs_31.08% | terminal_ratio_vs_T3d | WC | pct_above_lh | beats_winner | phase3_perf_candidate |
|---|---:|---:|---:|---:|---:|:--:|---:|:--:|:--:|
| baseline_qld_zroz | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | T | 1.000 | F | F |
| single_K4lv25_g25 | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | **T** | 1.000 | **T** | **T** |
| single_K4lv25_g25_unclrs105 | 1.3842 | +0.0596 | 0.3242 | +1.34pp | 1.507× | **T** | 1.000 | **T** | **T** |
| single_K4lv25_g25_T40D60 | 1.4030 | +0.0784 | 0.3266 | +1.58pp | 1.620× | **T** | 1.000 | **T** | **T** |
| single_rearmonly_T40D60 | 1.4176 | +0.0930 | 0.3244 | +1.36pp | 1.516× | **T** | 1.000 | **T** | **T** |
| 🥇 **slot 6 rgtdlrs120calm** | **1.3860** | **+0.0614** | **0.3511** | **+4.03pp** | **3.385×** | **T** | **1.000** | **🎯T** | **🎯T** |

**5 of 6 configs `beats_winner=True` and `phase3_performance_candidate=True`**
(slots 2-6). Slot 6 is the only `phase4_anchor_improved=True`.

## Phase 3 performance diagnostics

| metric | slot 6 rgtdlrs120calm | iter 027 slot 6 LRS1.20 uncond | iter 026 slot 6 LRS1.15 | iter 017 anchor T40D60 | T3d-K2 winner |
|---|---:|---:|---:|---:|---:|
| Sortino_lh56y | **1.3860** | 1.3786 | 1.3874 | 1.4030 | 1.3246 |
| CAGR_lh56y | **35.11%** | 36.22% | 35.32% | 32.66% | 31.08% |
| MDD_lh56y | -50.80% | -55.54% | -53.72% | -48.18% | -64.50% |
| end_eq vs T3d-K2 (lh_56y) | **3.385×** | 4.710× | 3.610× | 1.620× | 1.000× |
| end_eq vs iter 017 anchor | **2.090×** | 2.908× | 2.227× | 1.000× | 0.617× |
| modern_1990 Sortino | 1.300 | ≈ 1.124 | ≈ 1.134 | 1.303 | 1.222 |
| modern_1990 CAGR | 32.42% | ≈ 33.8% | ≈ 33.8% | 29.76% | 28.05% |
| 1990_2009 subperiod Sortino | **1.139** | 1.124 | 1.134 | n/a (proxied via modern_1990) | n/a |
| 2010_2026 subperiod Sortino | **1.132** | 1.144 | 1.148 | n/a | n/a |
| Rolling 1y win-rate vs T3d-K2 | 0.642 | 0.641 | 0.641 | n/a | n/a |
| Rolling 3y win-rate vs T3d-K2 | 0.668 | n/a | n/a | n/a | n/a |
| Rolling 5y win-rate vs T3d-K2 | 0.680 | 0.843 (LOOP MAX) | 0.808 | n/a | n/a |
| Rolling 10y win-rate vs T3d-K2 | 0.667 | 0.752 | 0.746 | n/a | n/a |

**Phase 3 verdict:** slot 6 rgtdlrs120calm IS a phase3_performance_candidate
(CAGR > 31.08%, end_eq > 1.05×, Sortino ≥ 1.20, PBO < 0.50, DSR < 0.05). It
adds +4.03pp CAGR vs T3d-K2 baseline at the cost of -0.4pp Sortino vs iter
027 slot 6's LRS1.20 unconditional, and trades end_eq dominance (3.385× vs
4.710×) for marginally better full-window Sortino (+0.0074).

## Phase 4 anchor diagnostics

| metric | slot 6 rgtdlrs120calm | iter 017 anchor T40D60 | edge | iter 027 slot 6 LRS1.20 uncond | edge |
|---|---:|---:|---:|---:|---:|
| Sortino_lh56y | **1.3860** | 1.4030 | -0.0170 | 1.3786 | **+0.0074** |
| CAGR_lh56y | **35.11%** | 32.66% | **+2.45pp** | 36.22% | -1.11pp |
| end_eq_ratio vs iter 017 | **2.090×** | 1.000× | **+1.090×** | 2.908× | -0.818× |
| MDD_lh56y | -50.80% | -48.18% | -2.62pp worse | -55.54% | +4.74pp better |
| PBO (G1) | 0.4127 | n/a | identical to iter 024-027 | 0.3929 | +0.0198 worse |
| `phase4_anchor_improved` | **True** | n/a | n/a | True | n/a |
| `phase4_anchor_pareto_improved` (vs iter 027 slot 6) | **False** | n/a | n/a | n/a | CAGR + end_eq both regress |

**Phase 4 verdict:**
- Slot 6 is the loop's **5th formal `phase4_anchor_improved=True`** iter (after
  iter 024, 025, 026, 027).
- Slot 6 is **NOT a Pareto improvement over iter 027 slot 6**: it loses 1.11pp
  CAGR and 0.818× terminal compounding for +0.0074 Sortino lift. Iter 027's
  unconditional LRS1.20 remains the formal Pareto frontier point on the rearm
  base.
- PBO 0.4127 = identical to iter 026 (and slightly worse than iter 027's
  0.3929) — regime-conditioning preserves the PBO-decoupled framework but
  does not improve PBO.
- Modern-era Sortino: 1.139 / 1.132 vs iter 027 unconditional 1.124 / 1.144
  — marginal mixed shifts (+0.015 / -0.012); regime-gating's pruning of
  high-rate-vol days produces a small net lift in 1990-2009 but a small
  regression in 2010-2026. **Neither subperiod reaches the Phase 3 floor 1.20.**

## KILL_LOOP results (pre-registered)

- 🎯 ✅ **KILL_LOOP #1 (success_tag) — FIRED.** 5 of 6 configs achieve
  `beats_winner=True` (slots 2-6). 14th loop iter to fire success_tag.
- ✅ **KILL_LOOP #2 (decisive_fail) — NOT FIRED.** Best Sortino 1.4176
  (slot 5) ≫ 1.20.
- ✅ **KILL_LOOP #3 (replica_baseline) — NOT FIRED.** Slot 1 Sortino 1.3240 =
  bit-exact iter 011-027 baseline (drift 0.0000). **19th-gen** reproducibility.
- ✅ **KILL_LOOP #4 (replica_single_K4lv25_g25) — NOT FIRED.** Slot 2 Sortino
  1.3951 = bit-exact iter 014-027 (drift 0.0000). **16th-gen.**
- ✅ **KILL_LOOP #5 (replica_T40D60_OR_iter017) — NOT FIRED.** Slot 4 Sortino
  1.4030 = bit-exact iter 017-027 (drift 0.0000). **11th-gen.**
- ✅ **KILL_LOOP #6 (replica_rearmonly_T40D60) — NOT FIRED.** Slot 5 Sortino
  1.4176 = bit-exact iter 021-027 INDEP IMPL (drift 0.0000). **8th-gen.**
- ✅ **KILL_LOOP #7 (replica_K4_unclrs105) — NOT FIRED.** Slot 3 Sortino
  1.3842 = bit-exact iter 024-027 K4 + LRS1.05 anchor (drift 0.0000). **5th-gen.**
- ✅ **KILL_LOOP #8 (PBO_blowup) — NOT FIRED.** G1 PBO 0.4127 < 0.55. The
  bond-vol regime gate did NOT re-introduce iter 023's PBO clustering pattern.
- 🏆 ✅ **KILL_LOOP #9 (PBO_held) — FIRED — POSITIVE TAG. STRUCTURAL
  PBO-DECOUPLED FRAMEWORK PRESERVED ON REGIME-CONDITIONING AXIS.** G1 PBO
  **0.4127** < 0.50 hard gate; identical to iter 026 (also 0.4127) — the
  bond-vol regime gate is mechanically orthogonal to equity-rearm and does
  NOT cluster CSCV ranks.
- 🏆 ✅ **KILL_LOOP #10 (rgtdlrs120calm_phase4_anchor_improved) — FIRED —
  POSITIVE TAG. FIFTH FORMAL PHASE 4 IMPROVEMENT.** Slot 6 satisfies CAGR
  35.11% > 32.66% iter 017 anchor ✓; end_eq vs iter017 2.090× > 1.0× ✓;
  Sortino 1.3860 ≥ 1.35 ✓; PBO 0.4127 < 0.50 ✓; DSR_global 1.46e-03 < 0.05 ✓.
- 🏆 ✅ **KILL_LOOP #11 (rgtdlrs120calm_strict_superset) — FIRED.** Slot 6
  strict_superset=True (Sortino 1.3860 > 1.3746, CAGR 35.11% > 31.08%, end_eq
  3.385× > 1.05×, PBO 0.4127 < 0.50, DSR_global 1.46e-03 < 0.05).
- ❌ **KILL_LOOP #12 (rgtdlrs120calm_modern_sortino_lift) — NOT FIRED.
  KEY HYPOTHESIS REJECTED.** Slot 6 modern subperiod Sortino: 1990_2009 =
  1.139 (vs iter 027 uncond 1.124, +0.015 — small lift but still BELOW 1.20
  floor); 2010_2026 = 1.132 (vs iter 027 uncond 1.144, -0.012 — small
  regression). Neither subperiod reaches the Phase 3 floor 1.20.
  **REGIME-CONDITIONING ON RATEVOL DOES NOT SOLVE MODERN-ERA SOFTNESS.**
- 🏆 ✅ **KILL_LOOP #13 (rgtdlrs120calm_partial_lift) — FIRED.** Slot 6 CAGR
  35.11% > 33.43% iter 024 LRS1.05 baseline. Regime gating preserves enough
  LRS exposure (50.91% of all bars active) to deliver substantial CAGR lift —
  the overlay is not washed out.
- ✅ **KILL_LOOP #14 (rgtdlrs120calm_sortino_collapse) — NOT FIRED.** Slot 6
  Sortino 1.3860 ≥ 1.35 floor (+0.036 above floor).

## Key finding: 🎯 ❌ MODERN-ERA SOFTNESS CONFIRMED STRUCTURAL TO REARM PRIMITIVE — REGIME-GATING DOES NOT REPAIR IT

**This iter formally falsifies a regime-conditioning thesis for resolving
the modern-era Sortino softness identified in iter 022-027.** Slot 6
ratevol-gated LRS1.20 calm-only:

1. **DELIVERS** formal Phase 4 improvement (5th in loop history): CAGR 35.11%
   > 32.66% anchor; end_eq vs iter 017 = 2.090×; Sortino 1.386 ≥ 1.35.
2. **DELIVERS** beats_winner=True and strict_superset=True with PBO 0.4127
   identical to iter 026 — regime-gating preserves PBO-decoupled framework.
3. **FAILS** the KEY HYPOTHESIS — modern subperiod Sortino remains 1.139 /
   1.132, both BELOW Phase 3 floor 1.20 by -0.061 / -0.068. The pruning of
   ~30% of LRS-active bars (high rate-vol regimes) produces a marginal lift
   in 1990-2009 (+0.015) but a marginal regression in 2010-2026 (-0.012),
   net mixed.
4. **IS NOT A PARETO IMPROVEMENT** over iter 027 slot 6 LRS1.20 unconditional:
   trades -1.11pp CAGR + -0.818× terminal compounding for +0.0074 Sortino.
   Iter 027's unconditional LRS1.20 remains the loop's strongest formal
   Phase 4 candidate by terminal compounding.

**Mechanism diagnosis:** the modern-era softness is structural to the rearm
primitive (T40D60 post-crash signal) interacting with the modern-era 2× QLD
on-leg vol cluster, NOT to LRS overlay magnitude OR application gating.
This independent falsification through a mechanically-orthogonal regime
overlay (bond-vol percentile, low correlation with equity-rearm signal)
strengthens iter 027's structural diagnosis: "modern-era softness is
structural to the rearm primitive, NOT the LRS overlay magnitude" extends
to "NOT the LRS application regime gating either."

**Mechanism vs iter 023 PBO blowup:** iter 023 used a leverage overlay GATED
TO THE REARM WINDOW — the gate signal was correlated with the rearm signal
(both equity-side), causing CSCV rank clustering and PBO 0.6548. Iter 028
uses a regime gate ORTHOGONAL to rearm (bond-vol percentile vs equity-crash)
— PBO held at 0.4127 = iter 026's value. **PBO-decoupled framework
generalizes to mechanically-orthogonal regime gates.**

## Subperiod robustness (slot 6 rgtdlrs120calm — 3 sub-windows)

| subperiod | n_obs | Sortino | CAGR | MDD | SPY CAGR | strategy CAGR vs SPY |
|---|---:|---:|---:|---:|---:|---:|
| 1970-1989 | 1010 | **2.255** | 60.43% | -27.32% | 17.73% | **+42.70pp** |
| 1990-2009 | 5043 | 1.139 | 33.94% | -50.80% | 8.15% | **+25.79pp** |
| 2010-2026 | 4097 | 1.132 | 30.85% | -36.36% | 14.20% | **+16.65pp** |

All 3 subperiods beat SPY CAGR by **17-43pp**. 1970-1989 Sortino 2.255
exceptional (small-n sample bias likely). Modern-era Sortino 1.13-1.14 BELOW
Phase 3 floor 1.20 — **same caveat as iter 022-027**, NOT improved by
regime-conditioning.

## Rolling-window win rates

vs T3d-K2 baseline (slot 6 rgtdlrs120calm):
- 1y: 0.642
- 3y: 0.668
- 5y: 0.680
- 10y: 0.667

vs iter 017 anchor (slot 6 rgtdlrs120calm):
- 1y: 0.640
- 3y: 0.762
- 5y: 0.787
- 10y: 0.737

Comparable to iter 026/027 LRS1.15/1.20 unconditional rolling win rates
against T3d-K2 (0.641 / 0.808 / 0.746 etc.). Regime-gating does not produce
distinctively stronger temporal alpha distribution than unconditional LRS.

## LRS active stats (slot 6)

| diagnostic | value | interpretation |
|---|---:|---|
| `lrs_active_pct` (all bars) | **0.5091** | LRS factor 1.20× applied on 50.9% of all trading bars |
| `on_active_pct` (all bars) | 0.7258 | 72.6% of all bars in RISK_ON state |
| `calm_within_on_pct` | 0.7014 | 70.1% of ON bars are in calm rate regime — matches the rvp70 threshold construction |
| `rv_warmup_pct` | 0.1300 | 13.0% of bars in pre-1975 ratevol gate warmup; LRS conservatively OFF |

The regime gate behaves as designed: ~70% of ON bars are calm (LRS active),
~30% of ON bars are stress (LRS off). The pruning ratio matches the
70th-percentile threshold construction exactly.

## Crisis attribution (slot 6 rgtdlrs120calm)

| crisis | beats SPY? |
|---|:--:|
| 2000-02 dot-com | ❌ |
| 2008 GFC | ✓ |
| 2020 COVID | ❌ |
| 2022 rates | ❌ |

1 of 4 crisis windows beat SPY — same as iter 026/027 slot 6 (LRS overlays
historically lag SPY in dot-com / COVID / 2022 due to vol-drag asymmetry on
leveraged equity exposure during reversal V-bottoms).

## All 5 prior calibration anchors PRESERVED bit-exact (KILL_LOOPs #3-#7 NOT FIRED)

| slot | anchor | sortino_lh56y | gen | drift |
|---|---|---:|---|---:|
| 1 | iter 011-027 baseline | 1.3240 | **19th-gen** | 0.0000 |
| 2 | iter 014-027 single_K4lv25_g25 | 1.3951 | **16th-gen** | 0.0000 |
| 3 | iter 024-027 K4 + LRS1.05 | 1.3842 | **5th-gen** | 0.0000 |
| 4 | iter 017-027 T40D60 OR-anchor | 1.4030 | **11th-gen** | 0.0000 |
| 5 | iter 021-027 rearm-only INDEP IMPL | 1.4176 | **8th-gen** | 0.0000 |

**Cross-impl parity check (iter 017 vs iter 022 INDEP IMPL):** max abs diff
= 0.000e+00, n_diff_days = 0. Iter 022 INDEP IMPL parity preserved across
8 iters.

**NEW slot 6 calibration anchor seeded:** rearm-only + ratevol-gated LRS1.20
calm-only Sortino 1.3860 / CAGR 35.11% / end_eq vs iter017 2.090× /
PBO 0.4127 (1st-gen — established by iter 028).

## Capital remains 100% Plan C per mandate §1

- `loop_winner_iter` += `028-2026-05-10-...` (15th iter to beat winner)
- `loop_phase3_performance_candidate_iter` += `028-...` (14th iter)
- `loop_strict_superset_iter` += `028-...` (13th iter; slot 6 is NEW non-replica
  strict_superset — `latest_strict_superset_is_novel=true`)
- `loop_phase4_anchor_qualitatively_improved_iter` += `028-...` (6th iter)
- `loop_phase4_anchor_improved_iter` += `028-...` (5th iter — 5th formal
  Phase 4 improvement; iter 027 was 4th)
- `loop_phase4_anchor_pareto_improved_iter` UNCHANGED (slot 6 NOT a Pareto
  improvement over iter 027 slot 6; loses CAGR + end_eq for marginal Sortino lift)

Score 76.5 STRONG < 90 deploy bar; per LOOP_PROTOCOL §"Mandate §1
reinforcement", `docs/CURRENT_STATE.md` "Active Hunts" entry preserved
untouched. **NO automatic capital realloc.**

## Plot / table refs

- `plots/01_equity_curves.png` — log equity curves lh_56y
- `plots/02_drawdown_curves.png` — drawdowns lh_56y
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR
- `plots/05_regime_attribution.png` — % time in equity (vote-K=2 ON state)
- `plots/06_pct_beat_spy.png` — cumulative % of 3y windows beating SPY
- `plots/07_crisis_attribution.png` — crisis MDD vs SPY
- `tables/per_config_metrics.csv` — full metrics per config × dataset
- `tables/gates_pass_fail.csv` — G1-G7 pass/fail per config
- `verdict.json` — full machine-readable verdict (validates against `loop_verdict_schema.json`)
- `regime_gated_lrs_overlay.py` — NEW iter-local helper (`apply_ratevol_gated_lrs_overlay`)

## Verdict + KILL status + Conclusion

| flag | value |
|---|---|
| `beats_winner` (best) | **True** |
| `phase3_performance_candidate` (best) | **True** |
| `strict_superset` (best) | **True** |
| `phase4_anchor_improved` (best) | **True** 🏆 (5th formal) |
| `phase4_anchor_pareto_improved` (vs iter 027 slot 6) | **False** ❌ |
| `phase4_anchor_validated` | **True** (5/5 anchors bit-exact + INDEP parity = 0) |
| `modern_sortino_lift_fired` | **False** ❌ KEY HYPOTHESIS REJECTED |
| `monotonicity_break` | n/a (no magnitude scan in this iter) |
| `latest_score` | 76.5 |
| `latest_tier_label` | STRONG |
| `latest_g1_pbo` | 0.4127 (= iter 026; +0.0198 vs iter 027) |
| `latest_strict_superset` | True |
| `latest_strict_superset_is_novel` | True |

### Conclusion

Iter 028 ratevol-gated LRS1.20 calm-only delivers a **5th formal
`phase4_anchor_improved=True` for the loop** with PBO held at 0.4127 (=
iter 026's value, structural framework preserved). However, it formally
**falsifies the regime-conditioning thesis** for resolving modern-era
Sortino softness: pruning ~30% of LRS-active bars to high rate-vol regimes
produces a +0.015 lift in 1990-2009 modern Sortino and a -0.012 regression
in 2010-2026, both still BELOW Phase 3 floor 1.20.

**Independent confirmation** of iter 027's structural diagnosis: modern-era
softness is structural to the rearm primitive itself, not to LRS overlay
magnitude OR application regime gating. Iter 027 slot 6 LRS1.20
unconditional remains the loop's strongest formal Phase 4 candidate by
terminal compounding (4.710× vs T3d-K2 baseline; 2.908× vs iter 017
anchor; iter 028 slot 6 = 3.385× / 2.090× respectively).

**Mechanically-orthogonal regime gate (bond-vol percentile) preserves
PBO-decoupled framework** — does NOT cluster CSCV ranks like iter 023's
rearm-window-gated LRS overlay (PBO 0.6548). This validates that orthogonal
regime gates can be added to the iter 024-027 framework without re-introducing
the iter 023 PBO mode.

### Next iter ideas

(a) **PIVOT to non-rearm Phase 4 family.** Iters 017-028 are all variants
of T40D60 + K4 + ratevol scaffolding. Two independent regime-conditioning
falsifications (iter 023 rearm-window-only LRS PBO blowup; iter 028 calm-only
LRS modern Sortino lift fail) plus the 5-point LRS magnitude scan completion
in iter 027 indicate the rearm primitive's improvement headroom on
LRS/regime axes is **conclusively mapped**. Loop count 28/50 leaves ~22
iters for family pivots — strong inflection point. Candidate non-rearm
Phase 4 families: calendar/seasonality (e.g., turn-of-month, sell-in-may);
cross-asset trend (e.g., gold + bond + equity Clenow ranking); VIX regime
overlay on entry signal; Sinclair vol-cone on equity (parallel to iter 006
on bonds). Cite `[volatility_trading, p.58-60]`,
`[trend_following_factor, ch.4]`, `[clenow_chapter_3]`.

(b) **Inverse regime gate test (LRS1.20 ONLY when ratevol fires) — symmetry
diagnostic.** Apply LRS1.20 EXCLUSIVELY during high-rate-vol regimes (~30%
of bars). Tests whether the modern-era softness comes from the calm regimes
(then inverse gate would help) or the stress regimes (then unconditional or
no-gate is best). 4-config sensitivity across rvp50/60/70/80 thresholds.
Expected: if calm regime is the structural softness driver, this iter's
inverse should show worse modern Sortino still. If stress regime is the
driver, this could pivot the diagnosis. Cite `[volatility_trading, p.58-60]`.

(c) **Equity-vol regime gate (replaces ratevol) on slot 6 LRS overlay.**
Same mechanism as iter 028 but use 21d realised vol percentile of QLD
returns instead of bond returns. Tests an EQUITY-side regime gate; expected
to be more correlated with rearm signal — risk of PBO clustering similar to
iter 023. Pre-register PBO blowup (KILL_LOOP) at 0.55. Cite
`[volatility_trading, p.58-60]`, `[advances_fin_ml, p.208-211]`.

(d) **Combined T_crash sensitivity at the iter 027 slot 6 LRS1.20 magnitude
ceiling.** Vary T_crash within {35, 40, 45, 50} on the iter 027 slot 6 +
LRS1.20 unconditional; tests whether the rearm-base modern softness can be
shifted by adjusting the crash trigger threshold without changing the LRS
overlay. Cite `[advances_fin_ml, p.208-211]`. Risk: iter 018-style PBO
clustering if grid is too narrow — pre-register mechanism diversity.

**Recommendation:** prioritize (a) pivot to non-rearm Phase 4 family. After
iter 028, the rearm primitive's LRS magnitude axis (5-point scan complete)
AND its LRS regime-conditioning axis (calm-only falsified) are both
exhausted on the modern-Sortino-lift dimension. Continued probing of the
rearm family on these axes would burn iters with diminishing informational
returns. A family pivot reopens the search space within Phase 4 spirit
(ablation: "what if we remove the rearm scaffolding entirely?") and aligns
with iter 027's own next-iter idea (d).
